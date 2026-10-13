"""Offline workbook audit and same-input replay, with network disabled."""
import ast
import base64
import builtins
import contextlib
import copy
import datetime
import io
import json
from pathlib import Path
import sys
import types
from urllib.parse import parse_qs,urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"src"))
from scripts.build_b_submission import load_rows,build_bundle,submission_sanity_check
from b_board.runtime import REQUIRED,PROFILE_NAMES,PATTERNS


class OfflineResponse:
    status_code = 200
    def __init__(self,data,url):
        self.data,self.url = data,url
    def json(self):
        return copy.deepcopy(self.data)
    def raise_for_status(self):
        return None


def _coding_match(concept,token):
    system,sep,code = token.partition("|")
    if not sep:
        code,system = system,None
    return any(x.get("code")==code and (system is None or x.get("system")==system) for x in concept.get("coding",[]))


class OfflineRequests:
    RequestException = RuntimeError
    exceptions = types.SimpleNamespace(RequestException=RuntimeError)
    def __init__(self,resources):
        self.resources = resources
        self.calls = []
    def get(self,url,params=None,**kwargs):
        parsed = urlparse(url)
        if parsed.hostname not in ("localhost","127.0.0.1"):
            raise RuntimeError("External network disabled in replay")
        query = {k:v[-1] for k,v in parse_qs(parsed.query).items()}
        query.update(params or {})
        self.calls.append({"path":parsed.path,"params":query})
        if "/empi/mapping" in parsed.path:
            return OfflineResponse({"targetId":"synthetic-paperless-p1"},url)
        kind = parsed.path.rstrip("/").split("/")[-1]
        if kind == "metadata":
            return OfflineResponse({"resourceType":"CapabilityStatement"},url)
        patient = {"resourceType":"Patient","id":"p1","name":[{"family":"Synthetic","given":["Patient"],"text":"Synthetic Patient"}],"gender":"unknown","birthDate":"1970-01-01"}
        if kind == "p1":
            return OfflineResponse(patient,url)
        candidates = [patient] if kind == "Patient" else [r for r in self.resources if r.get("resourceType")==kind]
        for key,value in query.items():
            if key == "_profile":
                candidates = [r for r in candidates if value in r.get("meta",{}).get("profile",[])]
            elif key == "code":
                candidates = [r for r in candidates if _coding_match(r.get("code",{}),value)]
            elif key == "value-concept":
                candidates = [r for r in candidates if _coding_match(r.get("valueCodeableConcept",{}),value)]
            elif key == "subject":
                candidates = [r for r in candidates if r.get("subject",{}).get("reference")==value]
            elif key == "_id":
                candidates = [r for r in candidates if r.get("id") in value.split(",")]
            elif key == "status":
                candidates = [r for r in candidates if r.get("status")==value]
            elif not key.startswith("_"):
                raise RuntimeError("Unimplemented official query parameter: " + key)
        return OfflineResponse({"resourceType":"Bundle","type":"searchset","entry":[{"resource":r} for r in candidates]},url)


def offline_namespace(source, resources=()):
    """Execute inspected definitions only, with imports restricted and requests replaced."""
    tree = ast.parse(source)
    allowed = {"re","uuid","datetime","typing","json","requests","collections","math","calendar"}
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            if any(alias.name.split(".")[0] not in allowed for alias in node.names):
                raise RuntimeError("Unsupported workbook import")
        elif isinstance(node,ast.ImportFrom) and node.module.split(".")[0] not in allowed:
            raise RuntimeError("Unsupported workbook import")
    tree.body = [n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef,ast.ClassDef,ast.Assign,ast.AnnAssign))]
    requests = OfflineRequests(resources)
    frozen_time = types.ModuleType("datetime")
    frozen_time.__dict__.update(vars(datetime))
    class ReplayDatetime(datetime.datetime):
        @classmethod
        def now(cls,tz=None):
            value = cls(2026,10,9,12,0,0)
            return value.replace(tzinfo=tz) if tz else value
        @classmethod
        def utcnow(cls):
            return cls(2026,10,9,4,0,0)
    frozen_time.datetime = ReplayDatetime
    original_import = builtins.__import__
    def local_import(name,*args,**kwargs):
        if name == "requests":
            return requests
        if name == "datetime":
            return frozen_time
        return original_import(name,*args,**kwargs)
    safe_builtins = dict(vars(builtins),__import__=local_import)
    namespace = {"__name__":"offline_workbook","__builtins__":safe_builtins}
    exec(compile(tree,"workbook-offline","exec"),namespace)
    return namespace,requests


def replay_service(row, bundle):
    resources = [entry["resource"] for entry in bundle.get("entry",[])]
    namespace,requests = offline_namespace(row["FHIR_SERVICE_CODE"],resources)
    with contextlib.redirect_stdout(io.StringIO()):
        patients = namespace["get_data_from_fhir_database"]("http://localhost:3456/api/fhir/baseDstu4")
    if patients is None:
        raise RuntimeError("Official service returned error sentinel")
    return {"hit":bool(patients),"requests":requests.calls}


TOPICS = {"2":"主诉","3":"辅助检查 病理","85":"手术记录","205":"手术记录","225":"放射治疗","255":"医学诊断","295":"个人史","465":"辅助检查 病理","475":"医学诊断","495":"辅助检查 病理","525":"术前诊断","585":"主诉","625":"实验室检查","695":"医学诊断","715":"辅助检查","765":"既往史"}


def fixture_reports(cid,text):
    reports = [{"text":part,"timestamp":"2026-10-09T12:00:00+08:00","topic":TOPICS[cid]} for part in text.split("\n")]
    # For 3 provide a separate real-shaped surgical record, with identical source text.
    # This is fixture construction, applied equally to reference and candidate.
    if cid == "3":
        reports += [dict(r,topic="手术记录") for r in reports]
    return reports


NOTES = {
    "2":"Service OR over four respiratory codes; NLP also maps chest pain to chest tightness and restricts topics. Candidate excludes isolated chest pain and supports symptom paraphrases.",
    "3":"Service intersects HCC Condition profile with Procedure outcome R0. NLP requires pathology-topic R0 and separate surgical record. Candidate composes grounded HCC, pathology, completed resection and R0 across records.",
    "85":"Service planned status filter commented out. FSH/NLP use completed surgery; service checks pulmonary-lobectomy, elective, thoracoscopic. Candidate admits planned or completed elective surgery, preserves FHIR preparation status for plans.",
    "205":"Service checks thoracic code and GA method/depth; neither elective nor planned status enforced. Candidate requires explicit elective/planned evidence, supports cross-record GA.",
    "225":"Service profile only; FSH fixes completed status. Candidate excludes plans but preserves in-progress for ongoing radiotherapy. Full FSH conformity for ongoing cases remains unresolved.",
    "255":"Service Condition profile only. FSH permits E11, does not require literal WHO1999 or lab values for existing diagnosis; NLP demands glucose/symptom evidence. Candidate accepts explicit T2DM without inventing glucose observations.",
    "295":"Service start within 90 days AND (daily cigarettes >5 OR cannot-guarantee). FSH requires both components, but OR often supports only one. Candidate emits only evidenced components; full FSH conformity unresolved. Record timestamp is observation time, not smoking start.",
    "465":"Service renal biopsy Procedure AND autoimmune Condition same subject. FSH explicitly extends disease list far beyond initial examples. Candidate covers selected explicit FSH diseases, requires biopsy and grounded diagnosis.",
    "475":"Service requires spinal cause extension and more_than_3_months; FSH label explicitly >=3. Candidate requires linked spinal pain plus >=3 months; unrelated causality cannot complete atom.",
    "495":"Service accepts C83.3 OR 9680/3 in Observation value. Candidate requires pathology and DLBCL, adds method and correct value code.",
    "525":"Service profile only. FSH accepts C15.2/C15.5 (middle/lower Chinese labels conflict with conventional ICD mapping). Candidate follows provided codes; requires preop context and location, does not infer location from unvalidated incisor distance.",
    "585":"Service value>=3 and exact unit 月. FSH minValue 3 mo. Candidate emits months with inclusive boundary; supports years/half-year and distributed pain duration.",
    "625":"CRITICAL: service does NOT require all three tests and pools all patient dates, rejecting on any outlier. Candidate obeys requested complete TBIL<=1.5 AND ALT<=3 AND AST<=3 per encounter/date, existential over encounters. Different from executable official service for mixed dates/partial panels.",
    "695":"Service profile AND with_distant_metastasis value. Candidate excludes uncertainty/M0/regional nodes; accepts M1 and explicit organ metastases, with possible primary-site ambiguity remaining.",
    "715":"Service requires both inferior_vena_cava and portal_vein components code=no. Candidate parses explicit vessel-specific negation, rejects invasion or uncertainty and does not infer from unscoped vascular-negative language.",
    "765":"Service Condition history profile only; FSH allows suffocation OR hypoxia. Candidate requires history/event context rather than current low oxygen measurements.",
}


def audit():
    import importlib.util
    spec = importlib.util.spec_from_file_location("b_cases",ROOT/"tests/b_board/test_b_board.py")
    cases_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cases_module)
    rows = load_rows()
    bundle = build_bundle(rows)
    results,source_audit = [],[]
    for row,entry in zip(rows,bundle["entry"][1:]):
        cid = str(row["profile_id"])
        reference,_ = offline_namespace(row["NLP_CODE"])
        candidate = {}
        source = base64.b64decode(entry["resource"]["content"][0]["data"]).decode("utf-8")
        exec(compile(source,cid,"exec"),candidate)
        profile_cases = [(expected,str(index),text) for expected,texts in zip((True,False),cases_module.CASES[cid]) for index,text in enumerate(texts)]
        attacks = cases_module.test_additional_attacks.pytestmark[0].args[1]
        profile_cases += [(expected,"attack_"+str(index),text) for index,(profile,text,expected) in enumerate(attacks) if profile==cid]
        if cid == "625":
            profile_cases += [(value<=3,"boundary_"+lab+"_"+str(value),"TBIL 1.5 ULN ALT 3 ULN AST 3 ULN".replace(lab+" 3",lab+" "+str(value))) for lab in ("ALT","AST") for value in (3,3.01)]
        for expected,index,text in profile_cases:
                reports = fixture_reports(cid,text)
                baseline_error = None
                with contextlib.redirect_stdout(io.StringIO()):
                    try:
                        old = reference["FHIRResourceBundleGenerator"]("http://localhost:3456/api/terminology").parse_clinical_text_to_fhir_bundle("p1",reports)
                        old_hit = replay_service(row,old)["hit"]
                    except Exception as exc:
                        baseline_error = type(exc).__name__+": "+str(exc)
                        old,old_hit = {},None
                    generator = candidate["FHIRResourceBundleGenerator"]("http://localhost:3456/api/fhir/baseDstu4")
                    calls = []
                    generator.transport = lambda prompt:(calls.append(prompt) or "NO")
                    new = generator.parse_clinical_text_to_fhir_bundle("p1",reports)
                    try:
                        service = replay_service(row,new)
                    except Exception as exc:
                        service = {"hit":None,"error":type(exc).__name__+": "+str(exc)}
                old_decision = "UNRESOLVED" if old_hit is None else "MATCH" if old_hit else "NO_MATCH"
                new_decision = generator.last_result["decision"]
                delta = old_decision+" -> "+new_decision if old_decision != new_decision else "UNCHANGED"
                results.append({"case":cid+("_positive_" if expected else "_negative_")+str(index),"profile_id":cid,"text":text,"synthetic_expected":expected,"baseline_kind":"OFFICIAL_EXCEL_NLP_AND_SERVICE","baseline_decision":old_decision,"baseline_error":baseline_error,"candidate_decision":new_decision,"candidate_service_hit":service["hit"],"candidate_service_error":service.get("error"),"semantic_calls":len(calls),"delta":delta,"reason":generator.last_result["reason"],"facts":generator.last_result["facts"],"baseline_resources":len(old.get("entry",[])),"candidate_resources":len(new.get("entry",[]))})
        source_audit.append({"profile_id":cid,"question":row["question"],"id":row["id"],"index":row["index"],"deepquery_id":row["deepquery_id"],"required_facts":REQUIRED[cid],"FHIR_FSH":row["FHIR_FSH"],"NLP_CODE":row["NLP_CODE"],"FHIR_SERVICE_CODE":row["FHIR_SERVICE_CODE"],"official_behavior":NOTES[cid],"verdict":"ADD_RULE","current_champion_handler":"MISSING_B_LIBRARY","candidate_handler":"b_board.runtime / evidence atoms"})
    target = ROOT/"analysis"
    target.mkdir(exist_ok=True)
    summary = {"comparison":"Offline official B NLP/service vs candidate; E has no B routes","synthetic_only":True,"cases":len(results),"new_positives":[r["case"] for r in results if r["delta"]=="NO_MATCH -> MATCH"],"lost_positives":[r["case"] for r in results if r["delta"]=="MATCH -> NO_MATCH"],"unchanged_positives":[r["case"] for r in results if r["baseline_decision"]==r["candidate_decision"]=="MATCH"],"new_negatives":[r["case"] for r in results if r["delta"]=="MATCH -> NO_MATCH"],"unresolved":[r["case"] for r in results if r["baseline_error"]],"service_mismatches":[r["case"] for r in results if r["candidate_service_hit"]!=(r["candidate_decision"]=="MATCH")],"candidate_logic_failures":[r["case"] for r in results if (r["candidate_decision"]=="MATCH")!=r["synthetic_expected"]],"real_patient_differential":"NOT_AVAILABLE","local_schema":submission_sanity_check(bundle,rows)}
    summary["baseline_match_set"] = [r["case"] for r in results if r["baseline_decision"]=="MATCH"]
    summary["new_match_set"] = [r["case"] for r in results if r["candidate_decision"]=="MATCH"]
    (target/"B_DIFFERENTIAL.json").write_text(json.dumps({"summary":summary,"rows":results},ensure_ascii=False,allow_nan=False,indent=2)+"\n",encoding="utf-8")
    (target/"B_PROFILE_SOURCE_AUDIT.json").write_text(json.dumps(source_audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines = ["# B Profile Audit", "", "## Provenance and Pipeline", "", "A_CHAMPION = Experiment E (V5S.2); reported online macro F1 0.16666666666666666.", "B_CANDIDATE = b1-evidence; no B leaderboard validation.", "", "Builder -> message Bundle -> Library base64 Python -> E normalization/retrieval -> B atoms/state -> deterministic constraints -> structured semantic rescue for unknown categorical facts -> grounded FHIR transaction -> official service.", "", "E fallback = localhost:1213 local-model, errors return NO. B retains endpoint, increases response budget from 32 to 1024 for JSON facts. No real model was used in offline verification.", "", "All B profile IDs are absent from E's actual executable libraries. None would automatically use a B-specific generic semantic route. No E-to-B patient predictions can be compared without adding B routes first.", "", "## Criterion Matrix", "", "|profile_id|criterion|required_facts|boolean_logic|temporal_logic|negation_logic|numeric_logic|current_handler|official_FHIR_behavior|risk|proposed_change|confidence|", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for row in source_audit:
        cid = row["profile_id"]
        temporal = "planned or completed elective" if cid in ("85","205") else "history/event" if cid in ("3","225","765") else "recent/current" if cid=="295" else "encounter/date grouped" if cid=="625" else "preoperative" if cid=="525" else "current evidence"
        numeric = ">5/day" if cid=="295" else ">=3 months" if cid in ("475","585") else "TBIL<=1.5ULN AND ALT/AST<=3ULN" if cid=="625" else "none"
        risk = "HIGH" if cid in ("3","85","205","295","465","475","625","715") else "MEDIUM"
        lines.append("|"+"|".join((cid,row["question"].replace("|","/"),", ".join(row["required_facts"]),"AND" if len(row["required_facts"])>1 else "OR within atom" if cid in ("2","295","765") else "atomic",temporal,"local state; unknown not positive",numeric,"E: missing B route",NOTES[cid].replace("|","/"),risk,"ADD_RULE / B-only adaptation","medium; no real labels"))+"|")
    lines += ["", "## Submission Contract", "", "The repository champion uses a message Bundle with one MessageHeader and 16 Python Libraries, identifier[0]=A index, content.title=profile ID. B construction preserves this shell and original B IDs where known; rows 2/3 use unique cnwqk2/cnwqk3 resource IDs and profile-2/profile-3 fallback identifiers. Original tbd/null values remain in the manifest. Deepquery IDs are preserved as explicitly scoped identifiers. These fallback index mappings are NOT an official contract and require platform validation. MessageHeader challenge_id=train_set is inherited from the online E reference; correct B platform setting is unverified.", "", "Strict local checker checks count, order, unique IDs/identifiers, deepquery identity, base64, UTF-8, syntax, embedded route, JSON roundtrip, NaN rejection. It is not a formal platform checker or complete FSH validator. Missing evidence is never replaced with invented components, dates, or lab values. This means 295 one-branch records and 225 ongoing radiotherapy can conflict with stricter FSH cardinality/status constraints.", "", "## Differential", "", "Source: analysis/B_DIFFERENTIAL.json. All inputs synthetic and identical between official NLP reference and candidate; E has no B libraries. The reference uses real-shaped topics, with duplicated pathology/surgery topic records for profile 3 for both systems. Model transport is a NO stub; semantic-dependent behavior is unverified. No score or F1 improvement is inferred.", "", "```json",json.dumps(summary,ensure_ascii=False,indent=2),"```", "", "## Every Changed Decision", "", "|case|baseline -> candidate|reason|", "|---|---|---|"]
    for r in results:
        if r["delta"]!="UNCHANGED":
            atoms = "; ".join(a+"="+f["state"] for a,f in r["facts"].items())
            lines.append("|"+r["case"]+"|"+r["delta"]+"|"+atoms+"|")
    lines += ["", "## Readiness", "", "B_BOARD_READY = NO", "", "Blockers: actual B patient/query corpus unavailable; official publication contract for tbd/null and deepquery mapping unavailable; formal platform checker unavailable; local-model JSON semantic rescue not validated against real endpoint; known FSH/service conflicts for 225/295/625. Generated artifact is an offline candidate, not a proven upload-ready champion."]
    (ROOT/"B_PROFILE_AUDIT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    audit()
