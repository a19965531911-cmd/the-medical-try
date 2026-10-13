"""Same labelled synthetic corpus, isolated actual Libraries, no stub metrics."""
import argparse
import ast
import base64
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.parse import urlparse
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "src"))
from scripts.build_b_submission import load_rows, parse_submission, submission_sanity_check, publication_gate
from scripts.audit_b_board import replay_service, fixture_reports
from scripts.b2_experiments import fsh_checks, r4_structure, cases

DEST = ROOT / "experiment/b5"
B4 = ROOT / "experiment/b4-semantic-recall/B4F.json"
B2 = ROOT / "experiment/b2-official-contract/B2E.json"
MODES = {"B5R": "rules", "B5H": "hybrid", "B5L": "llm_first"}


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, allow_nan=False, indent=2) + "\n", encoding="utf8")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_variant(variant, override=None):
    cfg = dict(variant=variant, endpoint="http://127.0.0.1:1213/v1/chat/completions", model="local-model",
               max_tokens=2048, request_timeout_seconds=4, total_model_budget_seconds=4, max_calls=1)
    cfg.update(override or {})
    parts = urlparse(cfg["endpoint"])
    if parts.scheme != "http" or parts.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("authorized loopback HTTP endpoint required")
    if not 0 < cfg["request_timeout_seconds"] <= cfg["total_model_budget_seconds"] <= 30 or cfg["max_calls"] != 1:
        raise ValueError("B5 requires one request and a <=30 second bounded total budget")
    bundle = parse_submission(B4.read_text(encoding="utf8"))
    overlay = (ROOT / "src/b_board/b5_overlay.py").read_text(encoding="utf8")
    for entry in bundle["entry"][1:]:
        library = entry["resource"]
        source = base64.b64decode(library["content"][0]["data"]).decode("utf8")
        source += "\nB5_CONFIG=" + repr(cfg) + "\nB4_CONFIG.update(mode=" + repr(MODES[variant]) + ",variant=" + repr(variant) + ")\n" + overlay
        compile(source, library["name"], "exec")
        library["content"][0]["data"] = base64.b64encode(source.encode()).decode()
    submission_sanity_check(bundle, load_rows())
    return bundle


def corpus():
    tree = ast.parse((ROOT / "tests/b_board/test_b_board.py").read_text(encoding="utf8"))
    original = ast.literal_eval(next(n.value for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "CASES" for t in n.targets)))
    items = []
    def add(group, cid, text=None, expected=False, reason="", records=None):
        items.append(dict(case=group + "_" + str(sum(x["group"] == group for x in items)).zfill(2), group=group,
                          profile_id=cid, reports=records if records is not None else fixture_reports(cid, text),
                          expected=expected, label_rationale=reason, label_source="AUTHORED_CRITERION_LOGIC_SYNTHETIC_NOT_PATIENT_GOLD"))
    for cid, (positive, negative) in original.items():
        add("clear_positive", cid, positive[0], True, "Explicit evidence satisfies the criterion's required conjunction/threshold.")
        add("clear_negative", cid, negative[0], False, "Required criterion evidence is absent or belongs to an excluded alternative.")
    for cid in ("2", "255", "495", "625"):
        add("clear_positive", cid, original[cid][0][1], True, "Explicit corroborated second positive expression; original numeric limits retained.")
        add("clear_negative", cid, original[cid][1][2], False, "Near-miss alternative or threshold violation does not meet the criterion.")
    synonyms = [
        ("2", "活动后透不过气", True), ("2", "走几步就觉得呼吸费力", True),
        ("2", "持续干咳", True), ("2", "感觉胸口憋得慌", True),
        ("3", "组织学证实HCC，已行hepatectomy，negative margins，R0", True),
        ("85", "拟择期VATS肺段切除术", True), ("205", "择期肺切除，全身麻醉", True),
        ("225", "外照射疗程已经结束", True), ("255", "明确诊断成人发病型糖尿病，疾病分型为第二型", True),
        ("295", "现吸烟1包/日", True), ("465", "renal biopsy证实IgA nephropathy", True),
        ("475", "腰椎间盘突出所致腰背痛持续半年", True),
        ("495", "病理报告。确诊弥漫性大细胞B淋巴瘤", True),
        ("525", "术前诊断下段食道癌", True), ("585", "下背痛半年余", True),
        ("625", "总胆红素30上限20，谷丙转氨酶90上限30，谷草转氨酶90上限30", True),
        ("695", "肺癌患者影像证实骨转移", True), ("715", "下腔静脉未受侵。门静脉未受侵", True),
        ("765", "出生时发生窒息", True), ("695", "仅区域淋巴结转移，M0", False),
    ]
    for cid, text, expected in synonyms:
        add("complex_synonym", cid, text, expected, "Authored synonym preserves clinical meaning; regional nodes without distant spread remain negative.")
    states = [
        ("2", "否认活动后透不过气", False), ("2", "活动后透不过气已完全消失", False),
        ("3", "病理疑似HCC，拟肝切除R0", False), ("85", "拟择期胸腔镜肺叶切除术", True),
        ("205", "拟择期全麻下胸部手术", True), ("225", "拟行放疗", False),
        ("225", "正在接受放疗", True), ("225", "放疗已完成", True),
        ("255", "疑似第二型糖尿病，尚未确诊", False), ("295", "曾每天20支，戒烟5年", False),
        ("465", "拟肾活检，诊断IgA肾病", False), ("475", "疑似脊柱源性疼痛半年", False),
        ("495", "病理疑似DLBCL", False), ("525", "术后病理中段食管癌", False),
        ("585", "腰痛已消失，曾持续半年", False), ("625", "拟查TBIL ALT AST", False),
        ("695", "不排除远处转移", False), ("715", "考虑门静脉侵犯，下腔静脉未侵", False),
        ("765", "曾发生窒息", True), ("765", "可能有窒息史", False),
    ]
    for cid, text, expected in states:
        add("state_scope", cid, text, expected, "Criterion-specific plan/history policy: elective plans and occurred hypoxia permitted; unsupported/uncertain facts excluded.")
    def r(text, **kwargs):
        return dict(text=text, timestamp="2026-10-09", **kwargs)
    cross = [
        ("3", [r("病理证实肝细胞癌", event_id="A"), r("已行肝切除R0", event_id="B")], False),
        ("3", [r("病理证实肝细胞癌", event_id="A"), r("已行肝切除R0", event_id="A")], True),
        ("85", [r("择期手术", event_id="A"), r("胸腔镜肺叶切除术", event_id="B")], False),
        ("205", [r("择期手术", event_id="A"), r("全麻下胸部手术", event_id="B")], False),
        ("465", [r("肾活检已完成", event_id="A"), r("IgA肾病", event_id="B")], False),
        ("495", [r("病理报告", event_id="A"), r("DLBCL", event_id="B")], False),
        ("495", [r("病理报告", event_id="A"), r("DLBCL", event_id="A")], True),
        ("475", [r("腰椎间盘突出导致疼痛", event_id="A"), r("疼痛持续半年", event_id="B")], False),
        ("625", [dict(text="TBIL 1 ULN", timestamp="2026-10-08"), r("ALT 2 ULN AST 2 ULN")], False),
        ("625", [r("TBIL 1 ULN", encounter_id="A"), r("ALT 2 ULN AST 2 ULN", encounter_id="B")], False),
        ("625", [r("TBIL 1 ULN", encounter_id="A"), r("ALT 2 ULN AST 2 ULN", encounter_id="A")], True),
        ("295", [dict(text="每天吸烟20支", timestamp="2026-01-01"), r("当前评估", evaluation_timestamp="2026-10-09")], False),
        ("2", [r("父亲活动后透不过气")], False), ("255", [r("母亲确诊2型糖尿病")], False),
        ("495", [r("家族病理确诊DLBCL")], False), ("225", [r("父亲放疗已完成")], False),
        ("695", [r("母亲证实远处转移")], False), ("765", [r("父亲有窒息缺氧史")], False),
        ("715", [r("父亲下腔静脉、门静脉均未受侵")], False),
        ("525", [r("术前食管癌", event_id="A"), r("肿瘤中下段", event_id="B")], False),
    ]
    for cid, records, expected in cross:
        add("cross_scope", cid, expected=expected, reason="Required facts must share patient/event/encounter; stale smoking and relatives are not patient evidence.", records=records)
    assert len(items) == 100 and all(v == 20 for v in Counter(x["group"] for x in items).values())
    return items


CHILD = r'''import json,sys,base64,time,io,contextlib
p=json.load(sys.stdin);ns={};exec(compile(base64.b64decode(p['source']),'actual_library','exec'),ns)
g=ns['FHIRResourceBundleGenerator']('http://localhost:3456')
started=time.perf_counter()
with contextlib.redirect_stdout(io.StringIO()):
    bundle=g.parse_clinical_text_to_fhir_bundle('p1',p['reports'])
json.dump({'resources':bundle,'extraction':g.last_result,'model_metrics':getattr(g,'model_metrics',{}),
           'trace':getattr(g,'b5_trace',{'retrieval_policy':'B4_ALL_RECORDS_EVENT_GROUPS','selected_record_indices':list(range(len(p['reports']))),'requests':'B4_DOES_NOT_RETAIN_RAW_REQUEST_RESPONSE'}),
           'elapsed_seconds':time.perf_counter()-started},sys.stdout,allow_nan=False)
'''


def execute(task):
    variant, fixture, source, row = task
    started = time.perf_counter()
    try:
        child = subprocess.run([sys.executable, "-I", "-c", CHILD],
            input=json.dumps(dict(source=source, reports=fixture["reports"])), capture_output=True,
            encoding="utf8", errors="replace", cwd=DEST, timeout=15)
        if child.returncode:
            raise RuntimeError(child.stderr[:2000])
        record = parse_submission(child.stdout)
        resources = record["resources"]
        record.update(variant=variant, **fixture, exception=None,
            predicted=record["extraction"]["match"], service_hit=replay_service(row, resources)["hit"],
            r4_errors=r4_structure(resources), fsh_violations=fsh_checks(row, resources))
    except Exception as exc:
        record = dict(variant=variant, **fixture, exception=type(exc).__name__ + ": " + str(exc),
                      predicted=False, service_hit=False, r4_errors=[], fsh_violations=[], model_metrics={},
                      trace={}, resources=None, elapsed_seconds=time.perf_counter()-started)
    return record


def metrics(records):
    tp = sum(r["predicted"] and r["expected"] for r in records)
    fp = sum(r["predicted"] and not r["expected"] for r in records)
    fn = sum(not r["predicted"] and r["expected"] for r in records)
    tn = sum(not r["predicted"] and not r["expected"] for r in records)
    return dict(n=len(records), tp=tp, fp=fp, fn=fn, tn=tn,
                precision=tp/(tp+fp) if tp+fp else 0, recall=tp/(tp+fn) if tp+fn else 0,
                f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0)


def summarize(records):
    summary = {}
    for variant in dict.fromkeys(r["variant"] for r in records):
        subset = [r for r in records if r["variant"] == variant]
        summary[variant] = dict(overall=metrics(subset),
            service_pipeline=metrics([dict(r, predicted=r["service_hit"]) for r in subset]),
            stages=dict(no_resource=sum(not bool(r["resources"]["entry"]) for r in subset if r["resources"] is not None),
                profile_invalid=sum(bool(r["fsh_violations"] or r["r4_errors"]) for r in subset),
                generated_service_miss=sum(bool(r["resources"]["entry"]) and not r["service_hit"] for r in subset if r["resources"] is not None)),
            profiles={cid:metrics([r for r in subset if r["profile_id"] == cid]) for cid in dict.fromkeys(r["profile_id"] for r in subset)},
            groups={group:metrics([r for r in subset if r["group"] == group]) for group in dict.fromkeys(r["group"] for r in subset)})
    return summary


def package():
    with zipfile.ZipFile(DEST/"B5_delivery.zip","w",zipfile.ZIP_DEFLATED) as z:
        for p in DEST.rglob("*"):
            if p.is_file() and p.suffix != ".zip": z.write(p,"experiment/b5/"+p.relative_to(DEST).as_posix())
        for p in list((ROOT/"reports").glob("B5_*"))+[ROOT/"analysis/B5_PREDICTIONS.csv",ROOT/"analysis/B5_LATENCY.json",ROOT/"src/b_board/b5_overlay.py",ROOT/"scripts/b5_experiments.py",ROOT/"scripts/b5_model_environment.py",ROOT/"scripts/run_b5.ps1",ROOT/"scripts/start_b5_existing_ollama.ps1",ROOT/"tests/b_board/test_b5_execution.py"]:
            z.write(p,p.relative_to(ROOT).as_posix())


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default="http://127.0.0.1:1213/v1/chat/completions")
    parser.add_argument("--model", default="local-model")
    parser.add_argument("--skip-regression", action="store_true")
    parser.add_argument("--refresh-reports", action="store_true", help="Validate persisted evidence and refresh reports without model calls")
    args = parser.parse_args()
    DEST.mkdir(parents=True, exist_ok=True)
    if args.refresh_reports:
        frozen = parse_submission((DEST/"frozen_hashes.json").read_text(encoding="utf8"))
        assert all(digest(ROOT/name)==sha for name,sha in frozen.items())
        records = parse_submission((DEST/"live_traces.json").read_text(encoding="utf8"))
        assert len(records)==400
        summary = summarize(records)
        dump(DEST/"evaluation.json",summary)
        latency = parse_submission((ROOT/"analysis/B5_LATENCY.json").read_text(encoding="utf8"))
        fsh = parse_submission((DEST/"legacy_fsh_replay.json").read_text(encoding="utf8"))
        final = parse_submission((DEST/"results.json").read_text(encoding="utf8"))
        write_reports(records,summary,latency,fsh,final)
        package()
        print("Persisted 400-case evidence and frozen hashes verified; reports/pack refreshed")
        return
    frozen_paths = [p for folder in ("submission", "experiment/b2-official-contract", "experiment/b3-final", "experiment/b3-review", "experiment/b4-semantic-recall")
                    for p in (ROOT / folder).rglob("*") if p.is_file()]
    frozen_paths += [p for p in (ROOT / "reports").glob("B[234]*")]
    frozen_paths += [ROOT / "src/b_board" / name for name in ("runtime.py", "b2_runtime.py", "b3_overlay.py", "b4_overlay.py")]
    frozen = {str(p.relative_to(ROOT)): digest(p) for p in frozen_paths}
    dump(DEST / "frozen_hashes.json", frozen)
    samples = corpus(); dump(DEST / "corpus.json", samples)
    rows = load_rows(); row_map = {str(r["profile_id"]):r for r in rows}
    bundles = {v:build_variant(v, dict(endpoint=args.endpoint, model=args.model)) for v in MODES}
    for v, b in bundles.items():
        dump(DEST / (v + ".json"), b)
        dump(DEST / (v + ".manifest.json"), dict(variant=v, sha256=digest(DEST/(v+".json")),
            mode=MODES[v], endpoint=args.endpoint, model=args.model, total_model_budget_seconds=4,
            max_calls=1, baseline_source_sha256=digest(B4), publication="BLOCKED"))
    # On-disk B4F is loaded without transport substitution in the same isolated harness.
    bundles["B4F_REFERENCE"] = parse_submission(B4.read_text(encoding="utf8"))
    tasks = []
    for variant, bundle in bundles.items():
        sources = {e["resource"]["content"][0]["title"]:e["resource"]["content"][0]["data"] for e in bundle["entry"][1:]}
        tasks += [(variant, f, sources[f["profile_id"]], row_map[f["profile_id"]]) for f in samples]
    with ThreadPoolExecutor(max_workers=4) as pool:
        records = []
        for i, record in enumerate(pool.map(execute, tasks)):
            records.append(record)
            if (i+1) % 25 == 0:
                print("Isolated actual-library evaluations: " + str(i+1) + "/400", flush=True)
    dump(DEST / "live_traces.json", records)
    summary = summarize(records)
    dump(DEST / "evaluation.json", summary)
    fields = ["variant","case","group","profile_id","expected","predicted","service_hit","calls","http_success","json_valid","grounded","fallback","elapsed_seconds","fsh_violations","exception","label_rationale"]
    with (ROOT / "analysis/B5_PREDICTIONS.csv").open("w", encoding="utf8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields); writer.writeheader()
        for r in records:
            output = {k:r.get(k) for k in fields}
            output.update({k:r["model_metrics"].get(k, 0) for k in ("calls","http_success","json_valid","grounded")})
            output["fallback"] = r["trace"].get("fallback", "B4_OR_RULES")
            output["fsh_violations"] = ";".join(r["fsh_violations"])
            writer.writerow(output)
    latency = {}
    for v in bundles:
        subset = [r for r in records if r["variant"] == v]
        values = sorted(r["elapsed_seconds"] for r in subset)
        calls = sum(r["model_metrics"].get("calls",0) for r in subset)
        success = sum(r["model_metrics"].get("http_success",0) for r in subset)
        parsed = sum(r["model_metrics"].get("json_valid",0) for r in subset)
        grounded = sum(r["model_metrics"].get("grounded",0) for r in subset)
        latency[v] = dict(cases=len(subset), calls=calls, http_success=success, json_valid=parsed, grounded=grounded,
            request_success_rate=success/calls if calls else None, json_success_rate=parsed/calls if calls else None,
            grounding_success_rate=grounded/calls if calls else None,
            pipeline_mean_seconds=sum(values)/len(values), pipeline_p95_seconds=values[math.ceil(.95*len(values))-1],
            successful_model_latency_p95=None, fallback_cases=sum(r["trace"].get("fallback")=="RULES_AFTER_MODEL_FAILURE" for r in subset),
            exceptions=sum(r["exception"] is not None for r in subset),
            error_kinds=dict(Counter(e["kind"] for r in subset for e in r["model_metrics"].get("errors",[]))))
        successful = sorted(t for r in subset if r["model_metrics"].get("responses",0) for t in r["model_metrics"].get("latencies",[]))
        if successful:
            latency[v]["successful_model_latency_p95"] = successful[math.ceil(.95*len(successful))-1]
    dump(ROOT / "analysis/B5_LATENCY.json", latency)
    # Replay all 167 legacy cases separately for FSH conflicts and rule parity.
    fsh_records = []
    scope_by_id = {}
    for entry in bundles["B5R"]["entry"][1:]:
        cid = entry["resource"]["content"][0]["title"]; scope={}
        exec(base64.b64decode(entry["resource"]["content"][0]["data"]),scope)
        scope_by_id[cid] = scope
    for f in cases():
        g = scope_by_id[f["profile_id"]]["FHIRResourceBundleGenerator"]("http://localhost:3456")
        output = g.parse_clinical_text_to_fhir_bundle("p1", f["reports"])
        fsh_records.append(dict(**f, resources=output, fsh_violations=fsh_checks(row_map[f["profile_id"]], output),
                               r4_errors=r4_structure(output), service_hit=replay_service(row_map[f["profile_id"]],output)["hit"]))
    dump(DEST / "legacy_fsh_replay.json", fsh_records)
    original = parse_submission(B2.read_text(encoding="utf8"))
    original_scopes = {}
    for entry in original["entry"][1:]:
        scope = {}; exec(base64.b64decode(entry["resource"]["content"][0]["data"]), scope)
        original_scopes[entry["resource"]["content"][0]["title"]] = scope
    parity = []
    for fixture in cases():
        cid = fixture["profile_id"]
        old = original_scopes[cid]["evaluate"](cid, fixture["reports"])
        new = scope_by_id[cid]["evaluate_b2"](cid, fixture["reports"], "B2E")
        assert old == new
        parity.append(dict(case=fixture["case"], result_exactly_equal=True, decision=new["decision"]))
    dump(DEST / "rule_parity.json", parity)
    regression = {"status":"NOT_RUN"}
    if not args.skip_regression:
        env = os.environ.copy(); count=int(env.get("GIT_CONFIG_COUNT","0"))
        env.update({"GIT_CONFIG_COUNT":str(count+1),"GIT_CONFIG_KEY_"+str(count):"safe.directory","GIT_CONFIG_VALUE_"+str(count):ROOT.as_posix()})
        child = subprocess.run([sys.executable,"-m","pytest","-q","-o","cache_dir=work/b5-cache","--basetemp","work/b5-full","--junitxml=experiment/b5/regression.xml"],
            env=env, cwd=ROOT,capture_output=True,encoding="utf8",errors="replace",timeout=900)
        (DEST/"regression.log").write_text(child.stdout+child.stderr,encoding="utf8")
        regression=dict(status="PASS" if child.returncode==0 else "FAIL",exit_code=child.returncode,summary=child.stdout.splitlines()[-1:])
    dump(DEST/"regression.json",regression)
    live_success=any(x["http_success"] for x in latency.values())
    # Without successful model evidence, build only the proven rule-equivalent candidate.
    chosen="B5R" if not live_success else "UNSELECTED_REQUIRES_REVIEW"
    if chosen=="B5R" and not any(r["exception"] for r in records if r["variant"]=="B5R") and regression["status"]=="PASS":
        dump(DEST/"B5_candidate.json",bundles["B5R"])
        candidate = parse_submission((DEST/"B5_candidate.json").read_text(encoding="utf8"))
        submission_sanity_check(candidate, rows)
        dump(DEST/"B5_candidate.manifest.json",dict(sha256=digest(DEST/"B5_candidate.json"),
             selected_strategy="B5R", semantic_gain="NOT_PROVEN", rule_parity_cases=len(parity), publication="BLOCKED"))
    publication={"status":"BLOCKED","official_checker":"UNAVAILABLE"}
    try: publication_gate(bundles["B5R"],rows)
    except ValueError as exc: publication["identity_error"]=str(exc)
    publication["header"] = bundles["B5R"]["entry"][0]
    dump(DEST/"publication_gate.json",publication)
    assert all(digest(ROOT/name)==sha for name,sha in frozen.items())
    final=dict(candidate=chosen, regression=regression, frozen_unchanged=True, model_success=live_success)
    dump(DEST/"results.json",final)
    write_reports(records,summary,latency,fsh_records,final)
    package()
    print(json.dumps(final),flush=True)
    if regression["status"]=="FAIL": raise SystemExit(1)


def write_reports(records,summary,latency,fsh_records,final):
    envpath=DEST/"model_environment.json"
    environment=parse_submission(envpath.read_text(encoding="utf8")) if envpath.exists() else {"status":"ENVIRONMENT_NOT_VERIFIED"}
    def report(name, lines):
        (ROOT/"reports"/name).write_text("\n".join(lines)+"\n",encoding="utf8")
    report("B5_MODEL_ENVIRONMENT.md",["# B5 Model Environment","",
        "B4F actual embedded request: HTTP POST /v1/chat/completions, application/json, model=local-model, temperature=0, max_tokens=2048, messages[{role:user,content:criterion+records+schema}], response choices[0].message.content. It is OpenAI-compatible, not a custom port-inferred protocol.",
        "Native Windows PowerShell 7.6.5; Python 3.12.14 validated by absolute path. WSL_DISTRO_NAME empty.",
        "Normal resolution/Get-Command/where did not find Ollama/lms/llama-server. PATH inspected; scoped common installation and D:/DeepTutor/D:/AI_Agent_Toolkit/D:/tools searches discovered trusted D:/DeepTutor/ollama/ollama.exe. Absolute --version validated 0.32.14; PATH was not overwritten.",
        "Existing Start-DeepTutor.cmd defines OLLAMA_MODELS=D:/DeepTutor/ollama-models and local port 11434. Service started with existing weights, loopback binding and OLLAMA_NO_CLOUD=1. No models downloaded, cloud/paid calls or real patient texts sent.",
        "The temporary audit Ollama service (owned PID 5548) was stopped after capability verification. Reproduce startup with scripts/start_b5_existing_ollama.ps1; it uses existing weights, hidden process, loopback, cloud disabled and no pruning/download.",
        "Only registered weight is bge-m3:latest (BERT 566.70M F16). /api/show declares embedding capability; chat returns 400 does not support chat. Actual /api/embed returned one 1024-dimensional vector. This proves local inference, not clinical JSON generation.",
        "LM Studio/llama.cpp standalone/medical chat weights were not discovered in scoped common directories or existing environments. Bundled Python lacks torch/transformers/llama_cpp; existing model cache directories and project launchers were checked. Software absence beyond the inspected scope is not asserted.",
        "Proxy-bypassed native requests: 1213 WinError10061 connection refusal; 11434 HTTP200. Therefore sandbox/socket/proxy problems alone do not explain 1213. The installed model is capability-incompatible with the existing generation client.",
        "Firewall changes were unnecessary: actual loopback 11434 inference succeeded. Platform 1213 service contract remains undocumented.","```json",
        json.dumps({k:v for k,v in environment.items() if k!='probes'},ensure_ascii=False,indent=2),"```",
        "Full requests, /api/show version/digest/capabilities, error response and embedding hash: experiment/b5/model_environment.json.",
        "MODEL_ENVIRONMENT_BLOCKED means no discovered usable chat model. Ollama installation itself is verified, not missing."])
    report("B5_LIVE_CALL_TRACE.md",["# B5 Live Call Trace","",
        "400 fresh isolated-process executions: 100 identical authored labelled synthetic cases for B5-R/H/L plus original B4F. Sources were decoded from actual JSON Libraries; transport was never replaced by stub in this evaluation.",
        "100-case corpus has exactly 20 clear-positive, 20 clear-negative, 20 complex-synonym, 20 state-scope, 20 cross-scope cases. Labels/rationales were authored from criterion logic before evaluation; they are not patient gold.",
        "B5 traces: original record indices (broad retrieval preserves paraphrases), request payload, actual raw response/error, JSON/literal grounding validation, extracted facts, built Bundle and original Service replay. B4F predates raw-response tracing; it records actual transport counters/errors and extraction.",
        "No successful generative response exists in the current environment. Complete text-to-LLM-to-grounded-FHIR success is BLOCKED; rule-to-FHIR-to-Service execution is separately verified.",
        "Actual per-case evidence: experiment/b5/live_traces.json. Prediction table: analysis/B5_PREDICTIONS.csv. Actual bge-m3 chat incompatibility and successful embedding are separate capability probes.","```json",json.dumps(latency,indent=2),"```"])
    lines=["# B5 Semantic Evaluation","",
        "All metrics below describe labelled synthetic PIPELINE behavior, including deterministic rules and connection-failure fallback. They are not live model performance or leaderboard scores.",
        "B5-R uses B2E deterministic evaluate/build without changing facts; B5-H fills only grounded UNKNOWN categorical atoms; B5-L attempts structured model judgment then uses deterministic Builder. Transport failures fall back to B2E; valid UNKNOWN remains UNKNOWN.",
        "B5-H/L additionally exclude ambiguous family-only records and prevent cross-event 525 conjunctions. B5-R remains unchanged. These are deterministic safety repairs, not LLM recall gains. The original 100 labels are retained; family 715 and cross-event 525 failures were first reproduced in new tests.",
        "No model-quality metrics can be estimated with zero successful generative calls. No champion selection by MATCH counts. B5-R remains the offline engineering candidate until real model evidence exists.",
        "Numeric/date/event treatment remains deterministic. Item/categorical model assertions cannot fabricate a lab panel, surgery or missing treatment history.",
        "Per-profile synthetic precision/recall/F1 and confusion matrices (zero_division=0; defined corpus denominator, not official Macro F1):","```json",json.dumps(summary,indent=2),"```"]
    report("B5_SEMANTIC_EVALUATION.md",lines)
    report("B5_DEPLOYABILITY.md",["# B5 Deployability","",
        "MODEL_DEPLOYABILITY_VERDICT = UNVERIFIED_AND_BLOCKED",
        "Local Ollama 11434 is user-host-specific and provides only embedding. No evidence confirms Tianchi permits outbound/local model requests or supplies localhost:1213; inheriting E's client string cannot establish the execution contract.",
        "B5-H/L can embed a verified local OpenAI-compatible model endpoint/name via CLI; no automatic cloud route or model downloads. /api/show must establish generation capability and the corpus must pass real end-to-end evaluation before selecting a semantic candidate.",
        "Actual embedded B5 transport enforces loopback HTTP, disables proxies, max_calls=1 per Library/record set, total generation budget=4 seconds, subprocess kill/wait on total timeout and no retries. Process startup/cleanup and deterministic work add overhead; it is not a whole-Library hard deadline. Parent isolation timeout=15 seconds.",
        "16 Libraries do not share process-local caches. Worst configured model wait is 16*4=64 seconds per patient if all are separately invoked, plus startup/rule/FHIR overhead. No claim this satisfies an unknown platform quota. Cross-Library deduplication requires platform support and remains unresolved.",
        "Connection/invalid-response failures explicitly fall back to rules; fallback success is not model success. L's valid UNKNOWN does not force YES. B5-R never calls a model.",
        "Official 2/3 identity, MessageHeader, runtime subprocess permission, available Python/network behavior, server model/version and total time allowance require official confirmation. No submission or gate removal performed."])
    violations=[r for r in fsh_records if r['fsh_violations']]
    lines=["# B5 FHIR Validation","",
        "Same existing R4/FSH subset validators and unmodified workbook Service replay; complete FHIR/FSH validator unavailable. Full profiles and official checker remain unverified.",
        "167 legacy cases replayed using B5-R: known FSH-invalid case count="+str(len(violations))+". No incompatible status or invented components were added to pass profiles.",
        "85/205 FSH status planned is outside R4 ProcedureStatus; preparation/completed reflects evidence. 225 ongoing cannot be relabelled completed or assigned invented completion time. 295 OR cannot fill both required component slices when only one exists. 625 retains complete same-encounter panel and original numeric/ULN evidence; Service's looser pooled semantics do not certify truth."]
    for r in violations:
        lines += ["","## "+r['case'],"Profile "+r['profile_id']+"; Service hit="+str(r['service_hit'])+"; safely fully repairable=NO without new source evidence/official contract.",
                  "Violation: "+"; ".join(r['fsh_violations']),"```json",json.dumps(dict(reports=r['reports'],resources=r['resources']),ensure_ascii=False,indent=2),"```"]
    report("B5_FHIR_VALIDATION.md",lines)
    overall=summary['B5R']['overall']
    hybrid=summary['B5H']['overall']
    report("B5_FINAL_VERDICT.md",["# B5 Final Verdict","","```makefile",
        "A_CHAMPION = V5S.2 Experiment E (frozen)","B_OFFLINE_BASELINE = B2E (frozen)",
        "B5_BEST_CANDIDATE = "+final['candidate']+" (rule-equivalent engineering artifact; no semantic gain proven)",
        "B_ONLINE_VERIFIED = NO","B_BOARD_READY = NO",
        "MODEL_FOUND = YES (trusted Ollama with embedding-only bge-m3)","MODEL_NAME = bge-m3:latest; generative model NOT_FOUND_IN_INSPECTED_SCOPE",
        "MODEL_ENDPOINT = 11434 embedding works; required 1213 chat refuses connection",
        "LIVE_REQUEST_SUCCESS = embedding YES; clinical structured generation NO",
        "EMBEDDED_LLM_EXECUTION = actual attempts verified; zero successful generative responses",
        "MODEL_DEPLOYABILITY_VERDICT = UNVERIFIED_AND_BLOCKED",
        "SYNTHETIC_PRECISION = live LLM UNAVAILABLE; B5R "+str(overall['precision'])+"; B5H guarded fallback "+str(hybrid['precision']),
        "SYNTHETIC_RECALL = live LLM UNAVAILABLE; B5R "+str(overall['recall'])+"; B5H guarded fallback "+str(hybrid['recall']),
        "SYNTHETIC_F1 = live LLM UNAVAILABLE; B5R "+str(overall['f1'])+"; B5H guarded fallback "+str(hybrid['f1']),
        "LATENCY_P95 = successful live LLM UNAVAILABLE; measured failure/fallback latency in analysis/B5_LATENCY.json",
        "FHIR_VALIDATION = LOCAL_SUBSET_ONLY","FSH_VIOLATIONS_REMAINING = "+str(len(violations))+" legacy cases",
        "PUBLICATION_IDENTITY = 2/3 tbd/null and MessageHeader UNVERIFIED","OFFICIAL_CHECKER = UNAVAILABLE",
        "RECOMMENDED_NEXT_ACTION = Provide an authorized existing generative model or explicitly authorize a trusted model download; verify platform model/runtime contract; rerun actual corpus",
        "```","","MODEL_ENVIRONMENT_BLOCKED: installed model cannot generate the required JSON. Real semantic improvement goal remains unmet; embedding success is not substituted.",
        "Regression: "+json.dumps(final['regression'])+". Frozen files hash-verified unchanged. No online upload.",
        "Reproduce: scripts/run_b5.ps1. For an authorized verified local chat model: scripts/run_b5.ps1 -Endpoint http://127.0.0.1:PORT/v1/chat/completions -Model MODEL_ID."])


if __name__ == "__main__": run()
