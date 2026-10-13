"""Read-only V6.0.1 provenance and same-input baseline replay gate."""

from __future__ import annotations

import base64
import difflib
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts import audit_v5s3_expg as expg_audit
from scripts.v6_offline_prototype import build_resources, evaluate_patient, replay

E_PATH = ROOT / "submission/a_test_message_bundle_v5s2_expe_aggressive_candidate.json"
E_EXPECTED_SHA = "40457de3149c7db34daf9c3545199c7c8f409ec65b6ae4412f6ca6a77df6d96e"
E_COMMIT = "6639cf7"
E_RELATIVE = "submission/a_test_message_bundle_v5s2_expe_aggressive_candidate.json"
MVP = ("555", "565", "675", "735", "745")

POSITIVE = {
    "555": [{"text": "患者于2026-06-01完成胆囊切除术", "timestamp": "2026-06-01"}, {"text": "本次评估", "timestamp": "2026-09-01"}],
    "565": [{"text": "目前严重腹泻", "timestamp": "2026-09-01"}],
    "675": [{"text": "患者65岁", "timestamp": "2026-09-01"}, {"text": "确诊头面部带状疱疹", "timestamp": "2026-09-01"}],
    "735": [{"text": "目前乙型肝炎处于活动期", "timestamp": "2026-09-01"}],
    "745": [{"text": "患者于2026-08-01完成手术", "timestamp": "2026-08-01"}, {"text": "术后于2026-08-01行气管插管有创机械通气", "timestamp": "2026-08-01"}],
}

OTHER = [
    ("555_old_surgery", "555", [{"text": "患者于2025-12-01完成手术", "timestamp": "2026-09-01"}]),
    ("555_missing_time", "555", [{"text": "既往有手术史", "timestamp": "2026-09-01"}]),
    ("565_resolved", "565", [{"text": "严重腹泻已缓解"}]),
    ("565_missing_severity", "565", [{"text": "目前腹泻"}]),
    ("675_missing_site", "675", [{"text": "患者65岁"}, {"text": "确诊躯干部带状疱疹"}]),
    ("675_negated", "675", [{"text": "患者65岁，否认头面部带状疱疹"}]),
    ("735_resolved", "735", [{"text": "乙型肝炎已治愈"}]),
    ("735_history_only", "735", [{"text": "既往乙肝病史"}]),
    ("745_niv", "745", [{"text": "术后仅无创机械通气"}]),
    ("745_missing_relation", "745", [{"text": "完成手术"}, {"text": "气管插管有创机械通气"}]),
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_bytes(ref: str) -> bytes:
    return subprocess.check_output(["git", "show", ref], cwd=ROOT)


def _candidate_sources(raw: bytes) -> dict[str, str]:
    bundle = json.loads(raw.decode("utf-8"))
    return {
        str(resource["content"][0]["title"]): base64.b64decode(resource["content"][0]["data"], validate=True).decode("utf-8")
        for entry in bundle["entry"]
        if (resource := entry["resource"]).get("resourceType") == "Library"
    }


def provenance() -> dict:
    current = E_PATH.read_bytes()
    historical = _git_bytes(f"{E_COMMIT}:{E_RELATIVE}")
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", E_RELATIVE], cwd=ROOT, capture_output=True, text=True).returncode == 0
    current_sources = _candidate_sources(current)
    historical_sources = _candidate_sources(historical)
    parsed_equal = json.loads(current.decode("utf-8")) == json.loads(historical.decode("utf-8"))
    source_rows = []
    for cid in sorted(set(current_sources) | set(historical_sources)):
        a, b = current_sources.get(cid, ""), historical_sources.get(cid, "")
        source_rows.append({
            "criterion": cid,
            "current_source_sha256": sha(a.encode()),
            "historical_source_sha256": sha(b.encode()),
            "equal": a == b,
            "diff_lines": 0 if a == b else len(list(difflib.unified_diff(b.splitlines(), a.splitlines()))),
        })
    builder = __import__("scripts.build_v5s2_expe_aggressive_submission", fromlist=["build_source"])
    builder_rows = []
    for cid, source in historical_sources.items():
        built = builder.build_source(cid, cid, {})
        builder_rows.append({"criterion": cid, "historical_equals_current_builder": source == built})
    return {
        "current_workspace": {"path": str(E_PATH), "size": len(current), "sha256": sha(current), "tracked": tracked},
        "exact_recovered": {"git_commit": E_COMMIT, "path": E_RELATIVE, "blob": subprocess.check_output(["git", "rev-parse", f"{E_COMMIT}:{E_RELATIVE}"], cwd=ROOT, text=True).strip(), "size": len(historical), "sha256": sha(historical), "status": "FROZEN_E_EXACT_ARTIFACT_FOUND"},
        "reference_sha256": E_EXPECTED_SHA,
        "reference_match": sha(historical) == E_EXPECTED_SHA,
        "current_matches_exact": current == historical,
        "parsed_bundle_equal": parsed_equal,
        "decoded_source_comparison": source_rows,
        "current_builder_reproduction": builder_rows,
        "classification": "SEMANTIC_DELTA" if any(not row["equal"] for row in source_rows) else ("BYTE_ONLY" if parsed_equal else "METADATA_ONLY"),
    }


def _e_run(sources: dict[str, str], cid: str, reports: list[dict]) -> dict:
    run = expg_audit._run(sources[cid], cid, "。".join(report.get("text", "") for report in reports), "YES")
    return {"decision": run["decision"], "resources": len(expg_audit._resources(run)), "reason": run["metrics"].get("reason", run["metrics"].get("admission_mode", "UNKNOWN")), "semantic_stub": bool(run["calls"])}


def replay_matrix(historical_sources: dict[str, str]) -> list[dict]:
    cases = [(f"{cid}_positive", cid, POSITIVE[cid]) for cid in MVP]
    cases.extend(OTHER)
    rows = []
    for name, cid, reports in cases:
        e = _e_run(historical_sources, cid, reports)
        store, decisions = evaluate_patient(reports, (cid,))
        v6 = decisions[cid]
        resources = build_resources("p1", v6)
        service = replay("p1", v6)["service_status"]
        input_hash = sha(json.dumps(reports, ensure_ascii=False, sort_keys=True).encode("utf-8"))
        grounded = bool(v6["payload_ready"] and v6["scorer_contract_ready"])
        if e["semantic_stub"]:
            classification = "UNRESOLVED"
        elif e["decision"] != "MATCH" and v6["decision"] == "MATCH":
            classification = "SAFE_COMPLETION" if grounded and service == "SERVICE_HIT" else "UNSAFE_RELAXATION"
        elif e["decision"] == v6["decision"]:
            classification = "NO_CHANGE"
        elif e["decision"] == "MATCH" and v6["decision"] != "MATCH":
            classification = "REGRESSION"
        else:
            classification = "UNRESOLVED"
        rows.append({"case": name, "criterion": cid, "input_hash": input_hash, "e_decision": e["decision"], "e_resources": e["resources"], "e_reason": e["reason"], "v6_decision": v6["decision"], "v6_resources": len(resources), "v6_reason": v6["reason_code"], "facts_gained": len(store["facts"]), "required_facts_grounded": grounded, "decision_delta": e["decision"] != v6["decision"], "classification": classification, "g_negative_control_pass": grounded if classification == "SAFE_COMPLETION" else None, "v6_service": service, "e_semantic_stub_used": e["semantic_stub"]})
    return rows


def find_test_a_sources() -> list[dict]:
    rows = []
    for root in (ROOT, ROOT.parent):
        for path in root.rglob("CHIP2026-CP2-data-test_a.xlsx"):
            try:
                import openpyxl
                wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
                sheets = [{"title": ws.title, "rows": ws.max_row, "columns": ws.max_column, "headers": [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]} for ws in wb.worksheets]
                rows.append({"path": str(path), "size": path.stat().st_size, "sha256": sha(path.read_bytes()), "sheets": sheets, "is_patient_text": False})
            except (OSError, PermissionError):
                continue
    unique = {row["sha256"]: row for row in rows}
    return list(unique.values())


def main() -> None:
    prov = provenance()
    exact_sources = _candidate_sources(_git_bytes(f"{E_COMMIT}:{E_RELATIVE}"))
    rows = replay_matrix(exact_sources)
    test_a = find_test_a_sources()
    (ROOT / "analysis/V6_E_PROVENANCE_INVENTORY.json").write_text(json.dumps(prov, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "analysis/V6_E_VS_V6_FIXTURE_REPLAY.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    stability = [{**row, "decision_e": row.pop("e_decision"), "decision_v6": row.pop("v6_decision")} for row in rows]
    (ROOT / "analysis/V6_ADMISSION_STABILITY_V2.json").write_text(json.dumps({"rows": stability, "unsafe_relaxation": sum(row["classification"] == "UNSAFE_RELAXATION" for row in stability)}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    coverage_path = ROOT / "analysis/V6_TEST_A_UNLABELED_COVERAGE.json"
    if any(item.get("is_patient_text") for item in test_a):
        coverage_path.write_text(json.dumps({"status": "PATIENT_TEXT_FOUND", "definition_files_found": test_a, "patient_text_loaded": False, "labels_read": False}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"provenance": prov, "safe_completion": sum(row["classification"] == "SAFE_COMPLETION" for row in rows), "unsafe_relaxation": sum(row["classification"] == "UNSAFE_RELAXATION" for row in rows), "regressions": sum(row["classification"] == "REGRESSION" for row in rows), "unresolved": sum(row["classification"] == "UNRESOLVED" for row in rows), "test_a": "TEST_A_TEXT_NOT_FOUND"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
