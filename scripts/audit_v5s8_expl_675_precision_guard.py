from __future__ import annotations

import ast
import base64
import hashlib
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts import build_v5s2_expe_aggressive_submission as e_builder
from scripts import build_v5s8_expl_675_precision_guard_submission as l_builder
from scripts.v6_baseline_gate import E_COMMIT, E_RELATIVE, _candidate_sources, _git_bytes
from src.v43.fhir.contracts import contract_for_criterion
from src.v43.fhir.service_replay import replay_service

TARGET = "675"
CRITERIA = ("485", "615", "265", "635", "675", "735", "745", "755", "855", "835", "875", "805", "565", "555", "185", "165")
NON_TARGETS = tuple(cid for cid in CRITERIA if cid != TARGET)
FIXTURE_CASES = [
    ("core_missing_site", "患者56岁，诊断带状疱疹。"),
    ("valid_head_face", "患者70岁确诊头面部带状疱疹"),
    ("valid_face", "63岁，面部带状疱疹。"),
    ("valid_ophthalmic", "70岁，眼周带状疱疹。"),
    ("age_below_threshold", "49岁，头面部带状疱疹"),
    ("diagnosis_missing", "56岁，面部皮疹"),
    ("site_missing_trunk", "56岁，胸背部带状疱疹"),
    ("site_missing_lower_limb", "56岁，下肢带状疱疹"),
    ("age_missing", "头面部带状疱疹"),
    ("explicit_negation", "56岁，否认带状疱疹"),
    ("unrelated_face_pain", "56岁，既往躯干部带状疱疹，本次面部疼痛。"),
    ("unrelated_face_rash", "56岁，胸背部带状疱疹，面部无皮疹。"),
    ("cross_report_complete", [{"text": "患者56岁"}, {"text": "确诊头面部带状疱疹"}]),
]


def _run(source, reports, prefix):
    namespace = {}
    exec(compile(source, TARGET, "exec"), namespace)
    generator = namespace["FHIRResourceBundleGenerator"]("http://localhost:3456")
    output = io.StringIO()
    with redirect_stdout(output):
        bundle = generator.parse_clinical_text_to_fhir_bundle("p1", reports if isinstance(reports, list) else [{"text": reports, "timestamp": "2026-01-31T12:34:56+08:00"}])
    lines = output.getvalue().splitlines()
    line = next((x for x in reversed(lines) if x.startswith(prefix)), None)
    if line is None:
        line = next(x for x in reversed(lines) if "METRICS|" in x)
    metrics = dict(field.split("=", 1) for field in line.split("|")[1:])
    return metrics, bundle


def _resources(bundle):
    return tuple(entry["resource"] for entry in bundle.get("entry", ()))


def _fixture_text(case):
    return case if isinstance(case, str) else "。".join(item["text"] for item in case)


def _delta_type(e_decision, l_decision):
    if e_decision == "MATCH" and l_decision == "NO_MATCH":
        return "MATCH_TO_NO_MATCH"
    if e_decision == "MATCH" and l_decision == "UNKNOWN":
        return "MATCH_TO_UNKNOWN"
    if e_decision in {"NO_MATCH", "UNKNOWN"} and l_decision == "MATCH":
        return "FORBIDDEN_NEW_POSITIVE"
    if e_decision == l_decision == "NO_MATCH":
        return "NO_MATCH_TO_NO_MATCH"
    return "NO_CHANGE"


def audit():
    e_sources = _candidate_sources(_git_bytes(f"{E_COMMIT}:{E_RELATIVE}"))
    l_sources = {cid: l_builder.build_source(cid, cid, {}) for cid in CRITERIA}
    rows = []
    for name, case in FIXTURE_CASES:
        e_metrics, e_bundle = _run(e_sources[TARGET], case, "V5S2E_METRICS|")
        l_metrics, l_bundle = _run(l_sources[TARGET], case, "V5S8L_METRICS|")
        e_decision, l_decision = e_metrics["final_decision"], l_metrics["final_decision"]
        delta = _delta_type(e_decision, l_decision)
        rows.append({
            "case": name,
            "input_hash": hashlib.sha256(json.dumps(case, ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
            "e_decision": e_decision,
            "l_decision": l_decision,
            "e_resources": len(_resources(e_bundle)),
            "l_resources": len(_resources(l_bundle)),
            "e_reason": e_metrics.get("reason"),
            "l_reason": l_metrics.get("reason"),
            "age_found": l_metrics.get("age_found"),
            "zoster_found": l_metrics.get("zoster_found"),
            "site_found": l_metrics.get("site_found"),
            "delta_type": delta,
            "semantic_stub": False,
            "retained_payload_equal": (_resources(e_bundle) == _resources(l_bundle)) if e_decision == l_decision == "MATCH" else None,
        })
    fixture_json = ROOT / "tests/fixtures/v5_matcher_cases.json"
    if fixture_json.exists():
        corpus = json.loads(fixture_json.read_text(encoding="utf-8"))
        seen = {row["input_hash"] for row in rows}
        for item in corpus:
            if str(item.get("criterion")) != TARGET:
                continue
            case = item.get("reports") or [{"text": item.get("text", "")}]
            h = hashlib.sha256(json.dumps(case, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
            if h in seen:
                continue
            seen.add(h)
            e_metrics, e_bundle = _run(e_sources[TARGET], case, "V5S2E_METRICS|")
            l_metrics, l_bundle = _run(l_sources[TARGET], case, "V5S8L_METRICS|")
            rows.append({"case": item.get("case_id", "fixture"), "input_hash": h, "e_decision": e_metrics["final_decision"], "l_decision": l_metrics["final_decision"], "e_resources": len(_resources(e_bundle)), "l_resources": len(_resources(l_bundle)), "e_reason": e_metrics.get("reason"), "l_reason": l_metrics.get("reason"), "age_found": l_metrics.get("age_found"), "zoster_found": l_metrics.get("zoster_found"), "site_found": l_metrics.get("site_found"), "delta_type": _delta_type(e_metrics["final_decision"], l_metrics["final_decision"]), "semantic_stub": False, "retained_payload_equal": (_resources(e_bundle) == _resources(l_bundle)) if e_metrics["final_decision"] == l_metrics["final_decision"] == "MATCH" else None})
    non_target_parity = {cid: l_sources[cid] == e_sources[cid] for cid in NON_TARGETS}
    retained = [row for row in rows if row["l_decision"] == "MATCH"]
    valid_retained = sum(row["case"].startswith("valid_") or row["case"] == "cross_report_complete" for row in retained)
    retained_rows = [row for row in rows if row["retained_payload_equal"] is not None]
    return {"criterion": TARGET, "rows": rows, "new_positives": sum(row["delta_type"] == "FORBIDDEN_NEW_POSITIVE" for row in rows), "non_target_source_parity": non_target_parity, "non_target_parity_count": sum(non_target_parity.values()), "retained_positive_cases": len(retained), "valid_retained_positive_cases": valid_retained, "retained_payload_equal": all(row["retained_payload_equal"] for row in retained_rows), "retained_payload_cases": len(retained_rows), "frozen_e_source_matches_builder": e_sources[TARGET] == e_builder.build_source(TARGET, TARGET, {})}


if __name__ == "__main__":
    result = audit()
    (ROOT / "analysis/V5S8L_675_DELTA.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
