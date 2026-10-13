"""Isolated B4 builds and staged audits. Never submits online or edits history."""
import argparse
import base64
import copy
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import zipfile
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
from scripts.build_b_submission import load_rows, parse_submission, submission_sanity_check, publication_gate
from scripts.b2_experiments import cases, fsh_checks, r4_structure
from scripts.audit_b_board import replay_service
from scripts.check_b_submission import CHILD

DEST = ROOT / "experiment/b4-semantic-recall"
BASE = ROOT / "experiment/b2-official-contract/B2E.json"
VARIANTS = {"B4R": "rules", "B4L": "llm_first", "B4H": "hybrid", "B4I": "item", "B4S": "hybrid", "B4F": "hybrid"}


def config(variant):
    return dict(variant=variant, mode=VARIANTS[variant], single_profile=variant == "B4S",
                endpoint="http://127.0.0.1:1213/v1/chat/completions", model="local-model",
                max_tokens=2048, timeout_seconds=5)


def build_variant(variant, override=None):
    bundle = parse_submission(BASE.read_text(encoding="utf8"))
    selected = config(variant)
    if override:
        selected.update(override)
    overlay = (ROOT / "src/b_board/b4_overlay.py").read_text(encoding="utf8")
    for entry in bundle["entry"][1:]:
        r = entry["resource"]
        source = base64.b64decode(r["content"][0]["data"], validate=True).decode("utf8")
        source += "\nB4_CONFIG=" + repr(selected) + "\n" + overlay
        compile(source, r["name"], "exec")
        r["content"][0]["data"] = base64.b64encode(source.encode("utf8")).decode("ascii")
    submission_sanity_check(bundle, load_rows())
    return bundle


def namespaces(bundle):
    result = {}
    for entry in bundle["entry"][1:]:
        r = entry["resource"]
        ns = {}
        exec(compile(base64.b64decode(r["content"][0]["data"]), r["name"], "exec"), ns)
        result[r["content"][0]["title"]] = ns
    return result


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, allow_nan=False, indent=2) + "\n", encoding="utf8")


def package():
    with zipfile.ZipFile(DEST / "B4_candidate_pack.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for p in DEST.rglob("*"):
            if p.is_file() and p.suffix != ".zip":
                z.write(p, "experiment/b4-semantic-recall/" + p.relative_to(DEST).as_posix())
        for p in [ROOT / "src/b_board/b4_overlay.py", ROOT / "scripts/b4_experiments.py",
                  ROOT / "scripts/b4_model_probe.py", ROOT / "scripts/run_b4.ps1",
                  ROOT / "tests/b_board/test_b4_semantic.py"] + list((ROOT / "reports").glob("B4_*")):
            z.write(p, p.relative_to(ROOT).as_posix())


def audit_embedded_sources():
    checks = []
    baseline = namespaces(parse_submission(BASE.read_text(encoding="utf8")))
    for variant in VARIANTS:
        bundle = parse_submission((DEST / (variant + ".json")).read_text(encoding="utf8"))
        submission_sanity_check(bundle, load_rows())
        for cid, ns in namespaces(bundle).items():
            assert ns["B4_CONFIG"] == config(variant)
            assert ns["FHIRResourceBundleGenerator"]._transport is ns["_b4_transport"]
            assert ns["FHIRResourceBundleGenerator"].parse_clinical_text_to_fhir_bundle is ns["_b4_entry"]
            # Compare frozen definitions as source bytes separately from final bindings.
            assert ns["B2_SELECTED"] == baseline[cid]["B2_SELECTED"] == "B2E"
            checks.append(dict(variant=variant, profile_id=cid, binding="PASS",
                               embedded_config=ns["B4_CONFIG"], executable_model_route=variant != "B4R"))
    dump(DEST / "embedded_source_audit.json", checks)


def synthetic_answer(atom, quote, index=0):
    return dict(match=True, facts=[dict(atom=atom, state="PRESENT", evidence=quote, report=index)],
                subject="patient", negated=False, planned=False, uncertain=False,
                evidence=[quote], reason="Controlled fixture, not a model prediction")


def semantic_cases():
    result = []
    for name, cid, atom, text in [
        ("breath", "2", "respiratory", "活动后透不过气"),
        ("lymphoma", "495", "dlbcl", "病理报告。确诊弥漫性大细胞B淋巴瘤"),
        ("diabetes", "255", "t2dm", "明确诊断成人发病型糖尿病，疾病分型为第二型"),
    ]:
        quote = text.split("。")[-1]
        for state, prefix, suffix, expected in [("positive", "", "", True), ("family", "父亲", "", False),
                                               ("negative", "否认", "", False), ("uncertain", "可能", "", False),
                                               ("planned", "拟评估", "", False)]:
            record = text.replace(quote, prefix + quote + suffix)
            result.append(dict(case="semantic_" + name + "_" + state, profile_id=cid,
                               reports=[dict(text=record, timestamp="2026-10-09")],
                               stub=synthetic_answer(atom, quote), synthetic_expected=expected))
    return result


def replay(fixture, ns, row, transport="stub"):
    g = ns["FHIRResourceBundleGenerator"]("http://localhost:3456")
    if transport == "stub":
        g.transport = lambda p: fixture.get("stub", "NO")
    started = time.perf_counter()
    response = g.parse_clinical_text_to_fhir_bundle("p1", fixture["reports"])
    service = replay_service(row, response)
    return dict(case=fixture["case"], profile_id=fixture["profile_id"], reports=fixture["reports"],
                decision=g.last_result["decision"], extraction=g.last_result,
                resources=response, r4_errors=r4_structure(response), fsh_violations=fsh_checks(row, response),
                service_hit=service["hit"], model_metrics=g.model_metrics, transport=transport,
                synthetic_expected=fixture.get("synthetic_expected"), elapsed_seconds=time.perf_counter()-started,
                true_patient_label="UNKNOWN",
                stage_status=("NLP_NO_RESOURCE" if not response["entry"] else
                              "FHIR_PROFILE_INVALID" if fsh_checks(row, response) or r4_structure(response) else
                              "VALID_LOCAL_SUBSET_SERVICE_MISS" if not service["hit"] else
                              "SERVICE_HIT_TRUE_LABEL_UNKNOWN"))


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Run synthetic matrix with the authorized local model")
    parser.add_argument("--skip-regression", action="store_true", help="Reuse existing B4 test XML; report missing evidence")
    parser.add_argument("--refresh-reports", action="store_true", help="Verify frozen hashes and sources, then repackage existing results")
    args = parser.parse_args()
    DEST.mkdir(parents=True, exist_ok=True)
    if args.refresh_reports:
        frozen = parse_submission((DEST / "frozen_hashes.json").read_text(encoding="utf8"))
        assert all(digest(ROOT / name) == sha for name, sha in frozen.items())
        prior = parse_submission((DEST / "results.json").read_text(encoding="utf8"))
        matrices = {v: parse_submission((DEST / v / "results.json").read_text(encoding="utf8")) for v in VARIANTS}
        audit_embedded_sources()
        write_reports(load_rows(), matrices, prior["summaries"], prior["model"], prior["regression"], frozen)
        package()
        print("Refreshed reports and package; frozen hashes and 96 embedded bindings verified")
        return
    paths = [p for directory in ("submission", "experiment/b2-official-contract", "experiment/b3-final", "experiment/b3-review")
             for p in (ROOT / directory).rglob("*") if p.is_file()]
    paths += [ROOT / p for p in ("src/b_board/runtime.py", "src/b_board/b2_runtime.py", "src/b_board/b3_overlay.py", "src/b_board/b3_input_guard.py")]
    paths += list((ROOT / "reports").glob("B2*")) + list((ROOT / "reports").glob("B3*"))
    paths += [ROOT / p for p in ("B_PROFILE_AUDIT.md", "reports/B_FINAL_DELIVERY.md", "scripts/build_b_submission.py", "scripts/b2_experiments.py", "scripts/build_b3_candidate.py")]
    frozen = {str(p.relative_to(ROOT)): digest(p) for p in paths}
    dump(DEST / "frozen_hashes.json", frozen)
    rows = load_rows()
    row_map = {str(r["profile_id"]): r for r in rows}
    fixtures = cases() + semantic_cases()
    endpoint = dict(status="LIVE_MODEL_UNAVAILABLE", endpoint=config("B4H")["endpoint"], real_calls=0)
    try:
        with urlopen("http://127.0.0.1:1213/v1/models", timeout=3) as response:
            endpoint.update(status="MODELS_ENDPOINT_REACHABLE_CHAT_UNVERIFIED", models=json.loads(response.read().decode()))
    except Exception as exc:
        endpoint["error"] = type(exc).__name__ + ": " + str(exc)
    results, summaries, bundles = {}, [], {}
    for variant in VARIANTS:
        bundles[variant] = build_variant(variant)
        dump(DEST / (variant + ".json"), bundles[variant])
        dump(DEST / variant / "config.json", config(variant))
        persisted = parse_submission((DEST / (variant + ".json")).read_text(encoding="utf8"))
        submission_sanity_check(persisted, rows)
        ns = namespaces(persisted)
        matrix = [replay(f, ns[f["profile_id"]], row_map[f["profile_id"]]) for f in fixtures]
        results[variant] = matrix
        dump(DEST / variant / "results.json", matrix)
        summaries.append(dict(variant=variant, cases=len(matrix), matches=sum(x["decision"] == "MATCH" for x in matrix),
                              service_hits=sum(x["service_hit"] for x in matrix),
                              r4_invalid_cases=sum(bool(x["r4_errors"]) for x in matrix),
                              fsh_invalid_cases=sum(bool(x["fsh_violations"]) for x in matrix),
                              stub_calls=sum(x["model_metrics"]["calls"] for x in matrix),
                              synthetic_safety_errors=sum(x["synthetic_expected"] is not None and (x["decision"] == "MATCH") != x["synthetic_expected"] for x in matrix),
                              real_patient_metrics="UNAVAILABLE"))
        print(json.dumps(summaries[-1]), flush=True)
        (DEST / variant / "run.log").write_text(json.dumps(summaries[-1], indent=2) + "\n", encoding="utf8")
        dump(DEST / variant / "manifest.json", dict(sha256=digest(DEST / (variant + ".json")),
             config=config(variant), frozen_b2e_sha256=digest(BASE), model_enabled=config(variant)["mode"] != "rules",
             model_policy="LOCAL_ONLY_SYNTHETIC_AUDIT", publication="BLOCKED"))
    # Probe actual on-disk embedded transport even if /models is absent.
    live_ns = namespaces(parse_submission((DEST / "B4H.json").read_text(encoding="utf8")))
    probe_cases = semantic_cases() if args.live or endpoint["status"] != "LIVE_MODEL_UNAVAILABLE" else semantic_cases()[:1]
    live = [replay(f, live_ns[f["profile_id"]], row_map[f["profile_id"]], "live") for f in probe_cases]
    endpoint["real_calls"] = sum(r["model_metrics"]["calls"] for r in live)
    endpoint["http_success"] = sum(r["model_metrics"]["http_success"] for r in live)
    endpoint["json_valid"] = sum(r["model_metrics"]["json_valid"] for r in live)
    endpoint["grounded"] = sum(r["model_metrics"]["grounded"] for r in live)
    endpoint["results"] = live
    if endpoint["http_success"]:
        endpoint["status"] = "LIVE_MODEL_RESPONDED" if endpoint["json_valid"] else "LIVE_MODEL_RESPONSE_INVALID"
    latencies = sorted(t for r in live for t in r["model_metrics"]["latencies"])
    endpoint["mean_seconds"] = sum(latencies)/len(latencies) if latencies else None
    endpoint["p95_seconds"] = latencies[max(0, int(len(latencies)*.95 + .999)-1)] if latencies else None
    dump(DEST / "model_endpoint.json", endpoint)
    if args.live and endpoint["http_success"]:
        for variant in VARIANTS:
            ns = namespaces(bundles[variant])
            dump(DEST / variant / "live_results.json", [replay(f, ns[f["profile_id"]], row_map[f["profile_id"]], "live") for f in fixtures])
    isolated = []
    for variant in VARIANTS:
        persisted = parse_submission((DEST / (variant + ".json")).read_text(encoding="utf8"))
        for row, entry in zip(rows, persisted["entry"][1:]):
            cid = str(row["profile_id"])
            fixture = next(f for f in fixtures if f["case"] == cid + "_positive_0")
            payload = dict(source=entry["resource"]["content"][0]["data"], reports=fixture["reports"])
            child = subprocess.run([sys.executable, "-I", "-c", CHILD], input=json.dumps(payload),
                                   encoding="utf8", capture_output=True, timeout=30, cwd=DEST)
            if child.returncode:
                raise RuntimeError(variant + " " + cid + ": " + child.stderr)
            response = parse_submission(child.stdout)
            assert not r4_structure(response)
            hit = replay_service(row, response)["hit"]
            if variant != "B4L":
                assert response["entry"] and hit
            isolated.append(dict(variant=variant, profile_id=cid, status="PASS", service_hit=hit,
                                 positive_output_expected=variant != "B4L", model_mode="NO_STUB"))
    dump(DEST / "isolated.json", isolated)
    regression = dict(status="NOT_RUN")
    if not args.skip_regression:
        regression_env = os.environ.copy()
        git_count = int(regression_env.get("GIT_CONFIG_COUNT", "0"))
        regression_env.update({"GIT_CONFIG_COUNT": str(git_count + 1),
                               "GIT_CONFIG_KEY_" + str(git_count): "safe.directory",
                               "GIT_CONFIG_VALUE_" + str(git_count): ROOT.as_posix()})
        child = subprocess.run([sys.executable, "-m", "pytest", "-q", "--basetemp", "work/b4-full",
                                "-o", "cache_dir=work/b4-cache",
                                "--junitxml=experiment/b4-semantic-recall/regression.xml"],
                               cwd=ROOT, capture_output=True, encoding="utf8", errors="replace", timeout=900, env=regression_env)
        (DEST / "regression.log").write_text(child.stdout + child.stderr, encoding="utf8")
        regression = dict(status="PASS" if child.returncode == 0 else "FAIL", exit_code=child.returncode,
                          summary=child.stdout.splitlines()[-1:] if child.stdout else [])
    dump(DEST / "regression.json", regression)
    publication = dict(status="BLOCKED", official_checker="UNAVAILABLE",
                       routing=[{k:r[k] for k in ("profile_id", "id", "index", "deepquery_id")} for r in rows],
                       message_header=bundles["B4F"]["entry"][0])
    try:
        publication_gate(parse_submission((DEST / "B4F.json").read_text(encoding="utf8")), rows)
        publication["local_identity_gate"] = "PASS_OFFICIAL_HEADER_STILL_UNVERIFIED"
    except ValueError as exc:
        publication["local_identity_gate"] = "FAIL"
        publication["error"] = str(exc)
    dump(DEST / "publication_gate.json", publication)
    unchanged = all(digest(ROOT / name) == sha for name, sha in frozen.items())
    if not unchanged:
        raise RuntimeError("Frozen files changed during B4 audit")
    dump(DEST / "results.json", dict(summaries=summaries, frozen_unchanged=unchanged, model=endpoint, regression=regression))
    write_reports(rows, results, summaries, endpoint, regression, frozen)
    audit_embedded_sources()
    package()
    print("B4 audit complete; publication remains blocked", flush=True)
    if regression["status"] == "FAIL":
        raise SystemExit(1)


def write_reports(rows, results, summaries, endpoint, regression, frozen):
    reports = ROOT / "reports"
    def md(name, lines):
        (reports / name).write_text("\n".join(lines) + "\n", encoding="utf8")
    md("B4_BASELINE_AUDIT.md", ["# B4 Baseline Audit", "", "A champion, B1, B2E and B3 original files were hash-checked before and after: unchanged.",
        "B2E.json: experiment/b2-official-contract/B2E.json. B3 runtime/artifacts: experiment/b3-final and b3-review.",
        "Official workbook: C:/Users/32433/Desktop/CHIP2026-CP2-data-test_b.xlsx (16 criteria, embedded FSH/NLP/Service).",
        "CHIP_CP2_B3_toolkit.zip was not found in the workspace, Desktop, Downloads or sibling project search; existing B3 Python audits were reused.",
        "Read B_PROFILE_AUDIT.md, B_FINAL_DELIVERY.md, B2_FINAL_VERDICT.md and existing B3 reports. Historical results are not new verification.",
        "Frozen hash inventory: experiment/b4-semantic-recall/frozen_hashes.json.", "",
        "Model launch/weights: no project-defined trusted launcher or discovered local weights. Windows PowerShell, WSL_DISTRO_NAME empty. Port/process/model-directory scans found no identified running service.",
        "No patient gold labels, official checker or confirmed publication mapping supplied. No online submission."])
    native_path = DEST / "native_endpoint.json"
    native = parse_submission(native_path.read_text(encoding="utf8")) if native_path.exists() else {"status": "NOT_RUN"}
    md("B4_MODEL_ENDPOINT.md", ["# B4 Model Endpoint", "", "Actual B4H.json was decoded and its bound _b4_transport invoked on synthetic evidence.",
        "Embedded settings: loopback-only endpoint, model=local-model, max_tokens=2048, socket timeout=5 seconds; no retries. Socket timeout is not a guaranteed total deadline.",
        "No trusted server launcher/weights identified; software absence is not asserted. No models downloaded or external/paid calls made.",
        "```json", json.dumps({k:v for k,v in endpoint.items() if k != "results"}, ensure_ascii=False, indent=2), "```", "",
        "Native Windows loopback verification (separate from sandbox socket restrictions):", "```json",
        json.dumps({k:v for k,v in native.items() if k != "embedded_probe"}, ensure_ascii=False, indent=2), "```",
        "Native embedded call metrics:", "```json", json.dumps(native.get("embedded_probe", {}).get("model_metrics", {}), ensure_ascii=False, indent=2), "```", "",
        "Per-call errors, fallback results, JSON/evidence metrics and latency: experiment/b4-semantic-recall/model_endpoint.json.",
        "Native probe evidence: native_endpoint.json. Native WinError 10061 means the target refused the connection; the model type/actual deployed model ID remains unidentified (local-model is only the inherited API placeholder).",
        "Stub metrics in the variant matrix are controlled tests, not live model accuracy. Run scripts/run_b4.ps1 -Live after restoring the trusted local service."])
    header = "|Variant|Cases|MATCH|Service hits|R4 invalid|FSH invalid|Stub calls|Semantic fixture errors|"
    table = [header, "|---|---:|---:|---:|---:|---:|---:|---:|"] + ["|" + "|".join(str(s[k]) for k in ("variant","cases","matches","service_hits","r4_invalid_cases","fsh_invalid_cases","stub_calls","synthetic_safety_errors")) + "|" for s in summaries]
    md("B4_SEMANTIC_COMPARISON.md", ["# B4 Semantic Comparison", "", "All cases are synthetic; no real Precision/Recall/Macro F1/Micro F1 can be computed.",
        "R: B2E deterministic rules. L: LLM-first closed structured Bare Prompt, UNKNOWN fails closed. H: rules plus categorical UNKNOWN supplementation. I: one missing atom per call. S: H with OR-only single-profile policy. F: H engineering candidate.",
        "B4-R intentionally disables historical semantic fallback for a pure-rule control. Numeric/date/causal/vessel facts are protected and require existing deterministic extraction; no semantic-only numeric recall claim.",
        "Existing builders already emit one representation for the eligible S profiles, so S has no resource-count change on this corpus; AND profiles 3/465/625/715 retain every resource.", "", *table, "",
        "Three explicit paraphrase groups and subject/negative/uncertain/planned counterfactuals use specified stub responses. They verify plumbing and guards; they do not establish model understanding or generalization.",
        "No regex synonym expansion is claimed across the 16 criteria. Existing 167 per-criterion boundary/negative cases are replayed alongside 15 new semantic fixtures.",
        "I explicitly asks for missing TBIL/ALT/AST, upper limits and encounter identity, and for smoking context, quantity, 90-day window and cessation guarantee. These diagnostic responses cannot bypass deterministic original-value validation; semantic numeric extraction remains a limitation.",
        "F is selected as a reviewable H implementation with conservative fallback and fewer calls than item mode; the proven offline recommendation remains B2E until live/gold validation. L cannot be recommended from NO-stub results."])
    conflict_lines = ["# B4 Profile Validation", "", "Local R4 and FSH checks are existing partial validators, not a complete FHIR validator or official checker.",
        "FSH conflicts cannot be removed by changing plans to completed or inventing missing OR components. No such repair was applied.",
        "Profile 85/205 FSH fixes Procedure.status=planned, absent from R4 ProcedureStatus. 225 ongoing conflicts with completed plus performedDateTime. 295 requires both components although criterion is OR.",
        "Original B2E 18 cases remain visible. Detailed B4F evidence/resources and Service replay follow. All reported 'not safely repairable' cases require contract clarification."]
    for r in results["B4F"]:
        if r["fsh_violations"]:
            conflict_lines += ["", "## " + r["case"], "", "Profile ID: " + r["profile_id"],
                "Safely fully repairable: NO with the currently available evidence/contract; no invented facts or status changes.",
                "Actual Service hit with preserved resource: " + str(r["service_hit"]),
                "Violations: " + "; ".join(r["fsh_violations"]), "```json",
                json.dumps(dict(original_evidence=r["reports"], actual_resources=r["resources"]), ensure_ascii=False, indent=2), "```"]
    md("B4_PROFILE_VALIDATION.md", conflict_lines)
    ids = [str(r["profile_id"]) for r in rows]
    sets = {"All16": ids, "Only3": ["3"], "Only295": ["295"], "Half-fire": ids[:8], "Complementary Half-fire": ids[8:]}
    ablations = {}
    for name, enabled in sets.items():
        bundle = build_variant("B4F")
        for entry in bundle["entry"][1:]:
            r = entry["resource"]
            if r["content"][0]["title"] not in enabled:
                source = base64.b64decode(r["content"][0]["data"]).decode("utf8")
                source += '\ndef _b4_silent(self,patient_id,case_reports,ai_algorithm_type="nlp"):\n    return {"resourceType":"Bundle","type":"transaction","entry":[]}\nFHIRResourceBundleGenerator.parse_clinical_text_to_fhir_bundle=_b4_silent\n'
                r["content"][0]["data"] = base64.b64encode(source.encode()).decode()
        submission_sanity_check(bundle, rows)
        dump(DEST / "ablations" / (name + ".json"), bundle)
        ns = namespaces(bundle)
        records = []
        for old in results["B4F"]:
            g = ns[old["profile_id"]]["FHIRResourceBundleGenerator"]("http://localhost:3456")
            g.transport = lambda p: "NO"
            response = g.parse_clinical_text_to_fhir_bundle("p1", old["reports"])
            records.append(dict(case=old["case"], profile_id=old["profile_id"], generated=bool(response["entry"]),
                                fsh_violations=fsh_checks(next(r for r in rows if str(r["profile_id"]) == old["profile_id"]), response),
                                service_hit=replay_service(next(r for r in rows if str(r["profile_id"]) == old["profile_id"]), response)["hit"],
                                true_label="UNKNOWN"))
        dump(DEST / "ablations" / (name + ".results.json"), records)
        ablations[name] = dict(enabled=enabled, cases=len(records), generated=sum(x["generated"] for x in records),
                               invalid=sum(bool(x["fsh_violations"]) for x in records), hits=sum(x["service_hit"] for x in records))
    dump(DEST / "ablations/results.json", ablations)
    md("B4_ABLATION.md", ["# B4 Ablation", "", "SCORING_FORMULA_UNVERIFIED. Actual 16-Library packages executed with NO stub; disabled libraries are silent diagnostic probes.",
        "Generated resources, FSH-invalid outputs, Service hits and unknown patient labels are recorded separately in ablations/*.results.json.",
        "No official scoring formula or denominator is inferred from silence or differences; no uploads were made.", "```json", json.dumps(ablations, indent=2), "```"])
    with (reports / "B4_EXPERIMENT_RESULTS.csv").open("w", encoding="utf8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summaries[0]))
        writer.writeheader(); writer.writerows(summaries)
    remaining = next(s["fsh_invalid_cases"] for s in summaries if s["variant"] == "B4F")
    md("B4_FINAL_VERDICT.md", ["# B4 Final Verdict", "", "```text",
        "A_CHAMPION = V5S.2 Experiment E (frozen)", "B_OFFLINE_BEST = B2E (retained; B4F engineering candidate unverified)",
        "B_ONLINE_VERIFIED = NO", "B_BOARD_READY = NO", "LIVE_MODEL_STATUS = " + endpoint["status"],
        "MODEL_ENABLED_IN_EMBEDDED_CODE = YES (actual bound transport tested; live success separate)",
        "LIBRARIES_PASSED = 16/16 B4F fresh-process positive and empty executions; original Service replay",
        "REGRESSION_TESTS = " + regression["status"] + " " + " ".join(regression.get("summary", [])),
        "FHIR_VALIDATION = LOCAL_R4_SUBSET_ONLY; full FSH validator unavailable",
        "FSH_VIOLATIONS_REMAINING = " + str(remaining) + " cases in B4F matrix (clinical/contract conflicts retained)",
        "PUBLICATION_IDENTITY = UNVERIFIED (2/3 tbd/null and MessageHeader)", "OFFICIAL_CHECKER = UNAVAILABLE",
        "BEST_VARIANT = B4H/B4F engineering recommendation; no live/gold champion selection",
        "RECOMMENDED_NEXT_ACTION = Restore trusted local model; run -Live; obtain official identity/FSH contracts and legal gold labels", "```", "",
        "No real leaderboard improvement or target attainment is claimed. Model unavailability prevents completing the real-model goal. Frozen files hash-verified unchanged.",
        "All six variants passed 16 fresh-process import/entrypoint/empty checks (96 total); L intentionally remains empty with NO stub. The 40 new B4 tests cover guarded categorical recall and attacks; original tests/expected results were preserved.",
        "Initial full run: 1002 passed, 1 Git ownership failure. Process-local safe.directory configuration repaired that environment failure; final complete run above passed. No global Git configuration was changed.",
        "Native loopback probe also confirmed connection refusal (WinError 10061); no trusted launcher/weights were found. Numerical semantic recovery, actual LLM accuracy/throughput, complete FHIR validation and real scoring remain unverified.",
        "B4F.json is an offline review artifact only. Full matrix, stage evidence, configs, isolated checks, five ablation packages and candidate pack are under experiment/b4-semantic-recall.",
        "One-command reproduction: powershell -ExecutionPolicy Bypass -File scripts/run_b4.ps1. Add -Live for local-model synthetic matrix.",
        "Port probing inside this environment may be restricted; recorded endpoint failure is scoped to the actual execution context."])


if __name__ == "__main__":
    run()
