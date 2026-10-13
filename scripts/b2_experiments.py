"""Isolated B2 experiment matrix and contract evidence; never submits to a platform."""
import ast
import base64
import copy
import csv
import hashlib
import io
import json
import re
import sys
import time
import subprocess
import contextlib
from pathlib import Path
from urllib.request import Request,urlopen
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/"src"))
from scripts.build_b_submission import load_rows,submission_sanity_check,parse_submission,publication_gate
from scripts.audit_b_board import replay_service,fixture_reports
from scripts.check_b_submission import CHILD
from b_board.b2_runtime import evaluate_b2,build_b2_resources,B2_VARIANTS,labs_b2,smoking_b2
from b_board.runtime import evaluate,build_b_resources

EXPERIMENT=ROOT/"experiment/b2-official-contract"
FROZEN=EXPERIMENT/"frozen"


def case(name,cid,data):
    return {"case":name,"profile_id":cid,"reports":data}


def report(text,day="2026-10-09",**extra):
    return dict(text=text,timestamp=day,**extra)


def cases():
    import importlib.util
    spec=importlib.util.spec_from_file_location("b1cases",ROOT/"tests/b_board/test_b_board.py")
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    result=[case(cid+("_positive_" if expected else "_negative_")+str(i),cid,fixture_reports(cid,text)) for cid,(pos,neg) in mod.CASES.items() for expected,texts in ((True,pos),(False,neg)) for i,text in enumerate(texts)]
    labs=[
        ("full_normal",[report("TBIL 1 ULN ALT 2 ULN AST 2 ULN")]),
        ("partial",[report("TBIL 1 ULN ALT 2 ULN")]),
        ("good_then_bad",[report("TBIL 1 ULN ALT 2 ULN AST 2 ULN","2026-10-08",encounter_id="a"),report("ALT 4 ULN","2026-10-09",encounter_id="b")]),
        ("different_dates",[report("TBIL 1 ULN","2026-10-08"),report("ALT 2 ULN AST 2 ULN","2026-10-09")]),
        ("alt_equal",[report("TBIL 1 ULN ALT 3 ULN AST 2 ULN")]),
        ("tbil_equal",[report("TBIL 1.5 ULN ALT 2 ULN AST 2 ULN")]),
        ("hospital_ranges",[report("TBIL 30上限20 ALT 90上限30 AST 90上限30",hospital_id="a",encounter_id="1"),report("ALT 90上限20",hospital_id="b",encounter_id="1")]),
        ("no_ranges",[report("TBIL 20 ALT 40 AST 40")]),
        ("same_encounter_conflict",[report("TBIL 1 ULN ALT 2 ULN AST 2 ULN",encounter_id="a"),report("ALT 4 ULN",encounter_id="a")]),
        ("bad_then_good",[report("ALT 4 ULN","2026-10-09",encounter_id="b"),report("TBIL 1 ULN ALT 2 ULN AST 2 ULN","2026-10-08",encounter_id="a")]),
        ("encounter_outranks_date",[report("TBIL 1 ULN","2026-10-08",encounter_id="a"),report("ALT 2 ULN AST 2 ULN","2026-10-09",encounter_id="a")]),
        ("same_day_different_encounter",[report("TBIL 1 ULN",encounter_id="a"),report("ALT 2 ULN AST 2 ULN",encounter_id="b")]),
    ]
    result += [case("625_"+n,"625",data) for n,data in labs]
    smoke=[("quantity_only","目前每天吸烟20支"),("refusal_only","不能保证试验期间停止吸烟"),("both","目前每天吸烟20支，不能保证停止吸烟"),("neither","目前每天吸烟5支，能保证停止吸烟"),("or_veto","目前每天吸烟5支，不能保证停止吸烟")]
    result += [case("295_"+n,"295",[report(text)]) for n,text in smoke]
    result += [case("295_old","295",[report("每天吸烟20支","2026-01-01"),report("当前评估")])]
    for cid in ("85","205"):
        positive="择期已完成胸腔镜肺叶切除术" if cid=="85" else "择期已完成全麻下胸部手术"
        planned="拟择期胸腔镜肺叶切除术" if cid=="85" else "拟择期全麻下胸部手术"
        first="择期手术"; second="胸腔镜肺叶切除术" if cid=="85" else "全麻下胸部手术"
        result += [case(cid+"_completed",cid,[report(positive)]),case(cid+"_planned",cid,[report(planned)]),case(cid+"_cross_event",cid,[report(first,event_id="a"),report(second,event_id="b")]),case(cid+"_good_and_emergency",cid,[report(positive,event_id="a"),report("急诊开胸肺切除术全麻",event_id="b")])]
    result += [case("225_"+n,"225",[report(t)]) for n,t in (("ongoing","正在接受放疗"),("completed","放疗已完成"),("planned","拟行放疗"),("recommended","建议放疗"),("denied","否认放疗"))]
    for cid,left,right in (("3","病理证实肝细胞癌","已行肝切除R0"),("465","肾活检已完成","IgA肾病"),("495","病理报告","DLBCL"),("475","腰椎间盘突出导致疼痛","疼痛持续半年")):
        result += [case(cid+"_cross_event",cid,[report(left,event_id="a"),report(right,event_id="b")]),case(cid+"_same_event",cid,[report(left,event_id="a"),report(right,event_id="a")])]
    return result


def r4_structure(bundle):
    """Local R4 constraints used by these resources; not an official full validator."""
    errors=[]
    try:
        json.dumps(bundle,allow_nan=False)
    except (TypeError,ValueError):
        errors.append("JSON serialization")
    if bundle.get("resourceType")!="Bundle" or bundle.get("type")!="transaction":
        errors.append("transaction Bundle")
    for entry in bundle.get("entry",[]):
        r=entry["resource"];kind=r.get("resourceType")
        if not re.fullmatch(r"[A-Za-z0-9\-.]{1,64}",r.get("id","")):
            errors.append("resource id")
        if entry.get("request")!={"method":"POST","url":kind}:
            errors.append("request")
        if not r.get("subject",{}).get("reference","").startswith("Patient/"):
            errors.append("subject")
        if not isinstance(r.get("meta",{}).get("profile"),list):
            errors.append("profile type")
        if kind=="Procedure" and r.get("status") not in {"preparation","in-progress","not-done","on-hold","stopped","completed","entered-in-error","unknown"}:
            errors.append("Procedure.status R4")
        if kind=="Observation" and r.get("status") not in {"registered","preliminary","final","amended","corrected","cancelled","entered-in-error","unknown"}:
            errors.append("Observation.status")
        if kind=="Condition" and not r.get("clinicalStatus"):
            errors.append("Condition clinicalStatus")
        for field in ("effectiveDateTime","performedDateTime"):
            if field in r and not re.fullmatch(r"\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2}))?",r[field]):
                errors.append("invalid "+field)
        if r.get("text"):
            try:
                root=ET.fromstring(r["text"]["div"])
                if root.tag!="{http://www.w3.org/1999/xhtml}div" or any(n.tag.endswith("script") for n in root.iter()):
                    errors.append("XHTML unsafe")
            except ET.ParseError:
                errors.append("XHTML invalid")
    return errors


def fsh_checks(row,bundle):
    """Check available explicit profile minima/fixed statuses; report unsupported coverage."""
    violations=[]
    sections=re.split(r"(?m)^(?=(?:Profile|CodeSystem|ValueSet|Extension):)",row["FHIR_FSH"])
    for entry in bundle.get("entry",[]):
        r=entry["resource"]
        canonical=r["meta"]["profile"][0]
        profile=canonical.rsplit("/",1)[-1]
        section=next((s for s in sections if s.startswith("Profile:") and (
            re.search(r'(?m)^\* \^url = "'+re.escape(canonical)+r'"\s*$',s)
            or not re.search(r'(?m)^\* \^url = ',s) and re.search(r"(?m)^Id:\s*"+re.escape(profile)+r"\s*$",s)
        )),None)
        if section is None:
            violations.append("No matching FSH profile "+profile);continue
        for path,count in re.findall(r"(?m)^\* ([A-Za-z]+)\s+(\d+)\.\.",section):
            if int(count)>0:
                value=r.get(path)
                if value is None or isinstance(value,list) and len(value)<int(count):
                    violations.append(profile+": required "+path)
        fixed=re.search(r"\* status = #(\S+) \(exactly\)",section)
        if fixed and r.get("status")!=fixed[1]:
            violations.append(profile+": status fixed="+fixed[1]+", actual="+r.get("status",""))
        if str(row["profile_id"])=="295":
            codes={c["code"]["coding"][0]["code"] for c in r.get("component",[])}
            for c in ("number-of-cigarettes-per-day","smoking-cessation-guarantee"):
                if c not in codes:
                    violations.append("295 required slice "+c)
    return violations


def build_variant(variant):
    bundle=parse_submission((FROZEN/"b_test_message_bundle_b1_candidate.json").read_text(encoding="utf8"))
    overlay=(ROOT/"src/b_board/b2_runtime.py").read_text(encoding="utf8")
    overlay_tree=ast.parse(overlay)
    # All frozen definitions already exist: remove fallback package imports from embedded code.
    overlay_tree.body=[n for n in overlay_tree.body if not isinstance(n,ast.Try)]
    overlay=ast.unparse(overlay_tree)
    for entry in bundle["entry"][1:]:
        r=entry["resource"]
        source=base64.b64decode(r["content"][0]["data"]).decode("utf8")
        if variant!="B1":
            source+="\n_B1_EVALUATE=evaluate\n_B1_BUILD=build_b_resources\n_B1_SMOKING=_smoking\n"+overlay
            source+="\nB2_SELECTED="+repr(variant)+"\n"
            source+='\ndef evaluate(cid,reports):\n    return evaluate_b2(cid,reports,B2_SELECTED)\n'
            source+='\ndef build_b_resources(cid,patient,reports,result):\n    return build_b2_resources(cid,patient,reports,result,B2_SELECTED)\n'
        compile(source,r["name"],"exec")
        r["content"][0]["data"]=base64.b64encode(source.encode()).decode()
    submission_sanity_check(bundle,load_rows())
    return bundle


def llm_probe():
    started=time.perf_counter()
    status={"endpoint":"http://127.0.0.1:1213/v1/chat/completions","real_model":False,"token_budget":1024,"timeout_seconds":30,"probe_timeout_seconds":5}
    try:
        payload={"model":"local-model","temperature":0,"max_tokens":1024,"messages":[{"role":"user","content":"从原文无咳嗽提取JSON：{facts:{respiratory:{state,evidence,report}}}，仅JSON。"}]}
        request=Request(status["endpoint"],json.dumps(payload).encode(),{"Content-Type":"application/json"})
        with urlopen(request,timeout=5) as response:
            data=json.loads(response.read().decode())
        status.update(real_model=True,response=data)
    except Exception as exc:
        status.update(status="UNAVAILABLE",error=type(exc).__name__+": "+str(exc))
    status["elapsed_seconds"]=time.perf_counter()-started
    return status


def run():
    EXPERIMENT.mkdir(parents=True,exist_ok=True)
    rows=load_rows();row_by_id={str(r["profile_id"]):r for r in rows}
    matrix=[];summaries=[];bundles={}
    fixtures=cases()
    for variant in B2_VARIANTS:
        bundle=build_variant(variant);bundles[variant]=bundle
        (EXPERIMENT/(variant+".json")).write_text(json.dumps(bundle,ensure_ascii=False,allow_nan=False,indent=2),encoding="utf8")
        generators={}
        for entry in bundle["entry"][1:]:
            r=entry["resource"];namespace={}
            exec(compile(base64.b64decode(r["content"][0]["data"]),r["name"],"exec"),namespace)
            generators[r["content"][0]["title"]]=namespace["FHIRResourceBundleGenerator"]
        for fixture in fixtures:
            cid=fixture["profile_id"];generator=generators[cid]("http://localhost:3456")
            calls=[];generator.transport=lambda p:(calls.append(p) or "NO")
            started=time.perf_counter();error=None;service_error=None;response={"resourceType":"Bundle","type":"transaction","entry":[]}
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    response=generator.parse_clinical_text_to_fhir_bundle("p1",fixture["reports"])
                decision=generator.last_result["decision"]
                try:
                    hit=replay_service(row_by_id[cid],response)["hit"]
                except Exception as exc:
                    hit=None;service_error=type(exc).__name__+": "+str(exc)
            except Exception as exc:
                decision="ERROR";hit=None;error=type(exc).__name__+": "+str(exc)
            matrix.append(dict(fixture,variant=variant,decision=decision,service_hit=hit,service_error=service_error,error=error,resources=response,r4_errors=r4_structure(response),fsh_violations=fsh_checks(row_by_id[cid],response),model_calls=len(calls),elapsed_seconds=time.perf_counter()-started))
        subset=[r for r in matrix if r["variant"]==variant]
        summaries.append({"variant":variant,"synthetic_cases":len(subset),"match_count":sum(r["decision"]=="MATCH" for r in subset),"service_hit_count":sum(r["service_hit"] is True for r in subset),"service_differences":sum(r["service_hit"]!=(r["decision"]=="MATCH") for r in subset),"r4_invalid_cases":sum(bool(r["r4_errors"]) for r in subset),"fsh_violating_cases":sum(bool(r["fsh_violations"]) for r in subset),"model_calls_stub":sum(r["model_calls"] for r in subset),"elapsed_seconds":sum(r["elapsed_seconds"] for r in subset),"exceptions":sum(bool(r["error"] or r["service_error"]) for r in subset),"timeouts":0,"full_fsh_validation":"UNAVAILABLE","macro_f1":"NO_GOLD_LABELS"})
    # Three 625 strategies, same evidence and actual constructed FHIR.
    strategies=[]
    for f in [f for f in fixtures if f["case"].startswith("625_") and not any(t in f["case"] for t in ("positive","negative"))]:
        for strategy in ("CURRENT_B1","CLINICAL_STRICT","OFFICIAL_COMPATIBLE"):
            result=evaluate("625",f["reports"]) if strategy=="CURRENT_B1" else labs_b2(f["reports"],strategy)
            resources=build_b_resources("625","p1",f["reports"],result) if strategy=="CURRENT_B1" else build_b2_resources("625","p1",f["reports"],result)
            response={"resourceType":"Bundle","type":"transaction","entry":[{"resource":r,"request":{"method":"POST","url":r["resourceType"]}} for r in resources]}
            strategies.append(dict(f,strategy=strategy,decision=result["decision"],resources=response,service_hit=replay_service(row_by_id["625"],response)["hit"]))
    smoke=[]
    for f in [f for f in fixtures if f["case"] in ("295_quantity_only","295_refusal_only","295_both","295_neither","295_or_veto","295_old")]:
        for strategy in ("SERVICE_GROUNDED","PROFILE_COMPLETE"):
            result=smoking_b2(f["reports"],strategy)
            resources=build_b2_resources("295","p1",f["reports"],result)
            response={"resourceType":"Bundle","type":"transaction","entry":[{"resource":r,"request":{"method":"POST","url":r["resourceType"]}} for r in resources]}
            smoke.append(dict(f,strategy=strategy,decision=result["decision"],resources=response,service_hit=replay_service(row_by_id["295"],response)["hit"],fsh_violations=fsh_checks(row_by_id["295"],response)))
    # Actual on-disk reloaded B2E, each Library in an isolated process.
    actual=parse_submission((EXPERIMENT/"B2E.json").read_text(encoding="utf8"));isolated=[]
    for row,entry in zip(rows,actual["entry"][1:]):
        cid=str(row["profile_id"])
        fixture=next(f for f in fixtures if f["case"]==cid+"_positive_0")
        payload={"source":entry["resource"]["content"][0]["data"],"reports":fixture["reports"]}
        child=subprocess.run([sys.executable,"-I","-c",CHILD],input=json.dumps(payload),capture_output=True,text=True,timeout=30,cwd=EXPERIMENT)
        if child.returncode:
            raise RuntimeError(cid+": "+child.stderr)
        response=parse_submission(child.stdout)
        if not response["entry"] or r4_structure(response) or not replay_service(row,response)["hit"]:
            raise ValueError("Isolated deployment check failed "+cid)
        isolated.append({"profile_id":cid,"isolated":"PASS","service_hit":True,"fsh_violations":fsh_checks(row,response)})
    baseline={r["case"]:r for r in matrix if r["variant"]=="B1"}
    deltas=[{"case":r["case"],"variant":r["variant"],"before":baseline[r["case"]]["decision"],"after":r["decision"],"reason":"event/temporal or strategy difference; see full reports/resources"} for r in matrix if r["variant"]!="B1" and r["decision"]!=baseline[r["case"]]["decision"]]
    probe=llm_probe()
    manifest={"selected":"B2E","candidate_generated":False,"official_ready":False,"reason":"Known unresolved identity and fixed-status/cardinality FSH contract conflicts; required checks not all pass","experimental_artifact":str(EXPERIMENT/"B2E.json"),"sha256":hashlib.sha256((EXPERIMENT/"B2E.json").read_bytes()).hexdigest(),"frozen_sources":json.loads((FROZEN/"freeze_manifest.json").read_text()),"isolated":isolated,"model":probe}
    for item in manifest["frozen_sources"]:
        if hashlib.sha256((ROOT/item["source"]).read_bytes()).hexdigest()!=item["sha256"]:
            raise ValueError("Frozen source changed: "+item["source"])
    try:
        publication_gate(actual,rows)
    except ValueError as exc:
        manifest["publication_gate"]="BLOCKED";manifest["publication_error"]=str(exc)
    if any(r["error"] for r in matrix):
        raise ValueError("Experiment runtime failures")
    data={"summary":summaries,"deltas":deltas,"matrix":matrix,"625_strategies":strategies,"295_strategies":smoke,"manifest":manifest}
    (EXPERIMENT/"results.json").write_text(json.dumps(data,ensure_ascii=False,allow_nan=False,indent=2),encoding="utf8")
    (ROOT/"submission/b2_candidate.manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf8")
    with (ROOT/"reports/B2_EXPERIMENT_RESULTS.csv").open("w",encoding="utf-8-sig",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(summaries[0]));writer.writeheader();writer.writerows(summaries)
    write_reports(rows,data)
    print(json.dumps({"summary":summaries,"deltas":len(deltas),"isolated":len(isolated),"model":probe,"candidate_generated":False},ensure_ascii=False,indent=2))


def write_reports(rows,data):
    dest=ROOT/"reports"
    identity=["# B2 Identity Contract","","B_BOARD_READY = NO","","## Verified evidence","","The original B workbook has 16 rows. Profiles 2/3 have id=tbd and index=null, but distinct profile_id and deepquery_id. This proves missing assignments in the file, not a platform routing rule. Their FSH and Service code never inspect Library id/identifier/content.title/deepquery_id.","","Frozen online A E package has one MessageHeader plus 16 Libraries, content.title=A profile, identifier[0]=A index, challenge_id=train_set. This is A historical evidence only. No official B publication instructions, routing implementation, announcement or formal checker were found in scoped local docs/reports/scripts or supplied workbook.","","## Not verified","","profile-2/profile-3 acceptance; routing key; deepquery identifier system; train_set for B; reuse of A shell. These are hypotheses inherited from B1, not official facts. Publication gate remains blocked. No alternate IDs were uploaded.","","## Confirmation steps","","1. Obtain official B release instructions and exact Library routing schema from organizer/platform documentation.","2. Request assigned index/id for profile 2 and 3 and confirm how deepquery IDs are used.","3. Confirm challenge_id and one-header/16-Library count explicitly for B.","4. Run official checker on the exact hashed experimental artifact after confirmed mappings are applied.","5. Save original evidence, URL/date and checker output; only then consider a limited official verification submission.","","## Isolation","","Git creation was denied in the sandbox; escalated Git encountered dubious ownership. No global safe.directory was changed. Requested isolation achieved by experiment/b2-official-contract; A and B1 package/source hashes frozen and verified unchanged.","","|profile|id|index|deepquery|","|---|---|---|---|"]
    identity += ["|"+"|".join(str(r[k]) for k in ("profile_id","id","index","deepquery_id"))+"|" for r in rows]
    (dest/"B2_IDENTITY_CONTRACT.md").write_text("\n".join(identity)+"\n",encoding="utf8")
    conflicts=["# B2 Service / FSH Conflicts","","## Critical correction to B1 audit","","85 and 205 original FSH both fix status=planned, NOT completed. planned is not a FHIR R4 ProcedureStatus code. NLP returns completed; service ignores status. B2 preserves preparation for planned and completed for completed events. No status falsification. 85 category (FSH 1..1) is now emitted from the surgical evidence.","","## Categories","","NLP extraction: B1 drops unknown-ULN values and cross-hospital provenance. B2 retains each measurement with its own explicit reference range; ratios are dimensionless unit 1. Unknown reference ranges produce no fabricated normal result.","","Clinical Boolean: strict 625 requires complete three-test panel, all supported results within thresholds in one encounter; an eligible encounter exists. Official-compatible accepts supported partial panels but vetoes any observed outlier across dates. B1 implicitly pools undated reports and hospital-colliding IDs. B2 explicit encounter outranks date and hospital namespaces IDs; unlinked undated reports cannot complete each other.","","FHIR construction: strict strategy emits the selected eligible panel's actual observations; compatible emits all supported observations. Thus service can hit selected strict resources even when evaluating all source observations would reject. Outputs in results.json permit review; no new labs, ULNs or encounters are synthesized.","","Service implementation: 625 loops over all observations, accepts partial panels, rejects at first outlier. Order of normal/abnormal results is immaterial when all observations are retained; B1 successful-panel serialization could change the selected panel/order. Official service pools across dates. Clinical-strict is selected for B2E; compatible B2B is a comparison only.","","FSH constraints: 295 requires both cigarettes and cessation components; actual service uses quantity>5 OR cannot-guarantee after recent-date filter. SERVICE_GROUNDED emits only supported components, PROFILE_COMPLETE requires both values in the evidence. Neither missing quantity nor unknown intent is filled. Both strategies remain available; full conflict is not solved.","","295 date: use recorded observation date only for documented recent/current behavior. It is not smoking onset. Anchor priority is supplied evaluation_timestamp, else latest report date; absent evaluation context remains uncertain against real platform wall-clock. Official Service additionally evaluates against current wall-clock; replay clock fixed to 2026-10-09 is documented.","","225 ongoing remains in-progress; FSH fixed completed rejects it while service accepts profile only. It is never rewritten completed. Completed treatment passes known status rule; plan/recommendation/denial do not emit.","","## 625 same-input output/service matrix","","|case|strategy|decision|service hit|resources|","|---|---|---|---|---|"]
    conflicts += [f'|{r["case"]}|{r["strategy"]}|{r["decision"]}|{r["service_hit"]}|{len(r["resources"]["entry"])}|' for r in data["625_strategies"]]
    conflicts += ["","## 295 same-input OR/cardinality matrix","","|case|strategy|decision|service hit|FSH violations|","|---|---|---|---|---|"]
    conflicts += [f'|{r["case"]}|{r["strategy"]}|{r["decision"]}|{r["service_hit"]}|{", ".join(r["fsh_violations"])}|' for r in data["295_strategies"]]
    conflicts += ["","## Validation coverage","","Local typed R4 subset checks resource enums, IDs, Bundle request/subject, profile arrays, JSON and safe XHTML. Available FSH checks use ORIGINAL profile blocks for direct mandatory fields, fixed status and the known required 295 slices. No SUSHI snapshots/official IG or complete FHIR validator was provided. Unsupported bindings/slicing are not declared valid. Original service Python is run unchanged with offline mock FHIR responses, not a deployed official server."]
    conflicts += ["", "Profile lookup honors original explicit ^url, which can differ from Id (475/525/715). The earlier Id-only local checker produced false missing-profile warnings; those have been removed. This correction improves the audit, not clinical predictions."]
    (dest/"B2_SERVICE_FSH_CONFLICTS.md").write_text("\n".join(conflicts)+"\n",encoding="utf8")
    deltas=["# B2 Criterion Deltas","","No gold labels: no F1/precision/recall scores reported. E has no B routes. Frozen B1 is the actual comparison baseline. All original inputs and real FHIR outputs are in experiment/b2-official-contract/results.json.","","B2A adds 85 category; B2B adds official-compatible 625; B2C adds safe 295 OR/time handling and preserves truthful 225 status; B2D adds 85/205 event constraints; B2E combines clinical-strict 625, safe 295 and event constraints also for 3/465/475/495. Untargeted profiles retain B1 behavior.","","Explicit event/procedure ID outranks encounter, hospital namespaces ID, differing dates separate unlinked records. With no event information, same-day/implicit records can still combine: real-event binding cannot be guaranteed from absent metadata. No invented encounter references.","","|case|variant|B1|new|","|---|---|---|---|"]
    deltas += [f'|{r["case"]}|{r["variant"]}|{r["before"]}|{r["after"]}|' for r in data["deltas"]]
    (dest/"B2_CRITERION_DELTAS.md").write_text("\n".join(deltas)+"\n",encoding="utf8")
    probe=data["manifest"]["model"]
    llm=["# B2 LLM Rescue Validation","","Actual localhost:1213 chat-completions request attempted; no stub substituted for endpoint availability.","","```json",json.dumps(probe,ensure_ascii=False,indent=2),"```","","Endpoint unavailable: real schema adherence, extra fields, Chinese negation/history/plans/uncertainty, token adequacy, multi-patient latency and timeout behavior remain UNVERIFIED. 1024 tokens and inherited 30 second timeout unchanged. Experimental matrix transport uses NO stub and explicitly counts stub calls; it is not model performance.","","B1 categorical unknown-only rescue and evidence grounding are retained. It cannot change deterministic negative/absent/planned/uncertain facts or fill numeric profiles. Event-veto is UNCERTAIN and cannot be rescued. Tests cover JSON malformed responses, extra facts, missing grounding, planned/negative states and XHTML injection. Patient text is data; generated XHTML escapes it. More complex prompt injection and model interpretation cannot be certified without a live endpoint."]
    llm += ["", "Offline tests establish that unrecognized facts/top-level match flags cannot create accepted facts and that deterministic veto states bypass the model. The inherited parser ignores extra keys; it does not enforce a closed JSON schema. Grounding uses normalized substring comparison, not literal byte-for-byte matching. These limitations remain documented, and no live model reliability claim is made. The availability probe uses a 5-second network timeout; the inherited production transport uses 30 seconds."]
    (dest/"B2_LLM_RESCUE_VALIDATION.md").write_text("\n".join(llm)+"\n",encoding="utf8")
    verdict=["# B2 Final Verdict","","```text","A_CHAMPION = V5S.2 Experiment E (frozen)","B1 = b1-evidence (frozen)","B_CHAMPION = UNVERIFIED","BEST_OFFLINE_CANDIDATE = B2E","B_BOARD_READY = NO","```","","B2E is selected for correcting reproduced event, provenance and OR/time bugs, not for maximizing synthetic hits. Official-compatible 625 B2B remains comparison-only; synthetic hit counts cannot determine a leaderboard champion.","","## Candidate policy","","submission/b2_candidate.json NOT GENERATED: all necessary confirmed profile/identity checks did not pass. An executable review artifact exists at experiment/b2-official-contract/B2E.json. submission/b2_candidate.manifest.json records this status and exact hashes. 16/16 Libraries passed isolated processes and original-service offline positive replay; package strict reload/sanity passed. Formal publication gate remains blocked.","","## Unresolved","","2/3 identity and MessageHeader contract NOT resolved. 225 ongoing/completed, 295 OR/cardinality and 625 clinical/service conflict are explicitly tested but not officially resolved. 85/205 planned invalid R4 fixed values additionally prevent claims of complete FSH compliance. No official checker, gold patient labels or live semantic endpoint available.","","## Changes","","src/b_board/b2_runtime.py adds scoped strategies, event/hospital/date binding, 90-day observation filtering, correct OR refusal handling, original-value FHIR construction and 85 category. scripts/b2_experiments.py freezes no existing files, builds six isolated versions, replays official code, performs R4/available-FSH subset checks and writes reports. tests/b_board adds reproduced failures and boundaries. Frozen runtime/builders/packages are hash-verified unchanged.","","## Official validation recommendation","","Do not perform a blind official verification submission with guessed identifiers. First obtain official mapping/header evidence and checker or equivalent official confirmation. Then a limited hashed validation upload may be useful; no automatic Tianchi submission was performed.","","## Results","","See B2_EXPERIMENT_RESULTS.csv and results.json for predictions, service behavior, known FSH violations, model-call stub counts, durations and exception counts. Full regression evidence will be recorded separately after final code execution."]
    (dest/"B2_FINAL_VERDICT.md").write_text("\n".join(verdict)+"\n",encoding="utf8")


if __name__=="__main__":
    run()
