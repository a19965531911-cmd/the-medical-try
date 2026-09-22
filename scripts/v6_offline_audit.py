"""Run the bounded, deterministic V6 offline feasibility audit."""

from __future__ import annotations

import hashlib
import json
import py_compile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.v6_offline_prototype import MVP_CRITERIA, evaluate_patient, replay

BASELINE = ROOT / "submission/a_test_message_bundle_v5s2_expe_aggressive_candidate.json"
EXPECTED_BASELINE_SHA = "40457de3149c7db34daf9c3545199c7c8f409ec65b6ae4412f6ca6a77df6d96e"
TRAIN_BUNDLE = ROOT.parent / "CHIP2026_CP2_A_baseline_v2_4_3/data/train_set_message_bundle.json"
TEST_XLSX = ROOT.parent / "CHIP2026_CP2_A_baseline_v2_4_3/data/CHIP2026-CP2-data-test_a.xlsx"

POSITIVE = {
    "555": [{"text": "患者于2026-06-01完成胆囊切除术", "timestamp": "2026-06-01"},
            {"text": "本次评估", "timestamp": "2026-09-01"}],
    "565": [{"text": "目前严重腹泻", "timestamp": "2026-09-01"}],
    "615": [{"text": "复查PSA 0.2 ng/mL", "timestamp": "2026-09-01"}],
    "675": [{"text": "患者65岁", "timestamp": "2026-09-01"},
            {"text": "确诊头面部带状疱疹", "timestamp": "2026-09-01"}],
    "735": [{"text": "目前乙型肝炎处于活动期", "timestamp": "2026-09-01"}],
    "745": [{"text": "患者于2026-08-01完成手术", "timestamp": "2026-08-01"},
            {"text": "术后于2026-08-01行气管插管有创机械通气", "timestamp": "2026-08-01"}],
}

NEGATIVE = [
    ("555", [{"text": "患者于2025-12-01完成手术", "timestamp": "2026-09-01"}], "NO_MATCH"),
    ("555", [{"text": "既往有手术史", "timestamp": "2026-09-01"}], "UNKNOWN"),
    ("565", [{"text": "严重腹泻已缓解"}], "NO_MATCH"),
    ("615", [{"text": "Gleason评分7分，PSA 0.1 ng/mL"}], "UNKNOWN"),
    ("675", [{"text": "患者65岁"}, {"text": "确诊躯干部带状疱疹"}], "UNKNOWN"),
    ("675", [{"text": "患者65岁，否认头面部带状疱疹"}], "NO_MATCH"),
    ("735", [{"text": "乙型肝炎已治愈"}], "NO_MATCH"),
    ("735", [{"text": "既往乙肝病史"}], "UNKNOWN"),
    ("745", [{"text": "术后仅无创机械通气"}], "NO_MATCH"),
    ("745", [{"text": "完成手术"}, {"text": "气管插管有创机械通气"}], "UNKNOWN"),
]

STABILITY_CASES = [
    ("745_complete_cross_report", "745", POSITIVE["745"], "MATCH", True),
    ("745_missing_relation", "745", [{"text": "完成手术"}, {"text": "气管插管有创机械通气"}], "UNKNOWN", False),
    ("675_complete_facts", "675", POSITIVE["675"], "MATCH", True),
    ("675_missing_site", "675", [{"text": "患者65岁"}, {"text": "确诊躯干部带状疱疹"}], "UNKNOWN", False),
    ("735_current_state", "735", POSITIVE["735"], "MATCH", True),
    ("735_history_only", "735", [{"text": "既往乙肝病史"}], "UNKNOWN", False),
    ("565_missing_severity", "565", [{"text": "目前腹泻"}], "UNKNOWN", False),
    ("615_non_satisfying_branch", "615", [{"text": "Gleason评分7分，PSA 0.1 ng/mL"}], "UNKNOWN", False),
]


def main():
    py_compile.compile(str(ROOT / "scripts/v6_offline_prototype.py"), doraise=True)
    py_compile.compile(str(ROOT / "tests/v6/test_v6_offline_prototype.py"), doraise=True)
    positive_rows = []
    for criterion in MVP_CRITERIA:
        store, decisions = evaluate_patient(POSITIVE[criterion], (criterion,))
        result = decisions[criterion]
        replayed = replay("p1", result)
        assert result["decision"] == "MATCH", (criterion, result)
        assert result["payload_ready"] and result["scorer_contract_ready"], (criterion, result)
        assert replayed["service_status"] == "SERVICE_HIT", (criterion, replayed)
        positive_rows.append({"criterion": criterion, "facts": len(store["facts"]),
                              "decision": result["decision"], "resources": len(replayed["resources"]),
                              "service": replayed["service_status"]})

    negative_rows = []
    for criterion, reports, expected in NEGATIVE:
        _, decisions = evaluate_patient(reports, (criterion,))
        result = decisions[criterion]
        replayed = replay("p1", result)
        assert result["decision"] == expected, (criterion, result)
        assert replayed["service_status"] == "SERVICE_MISS", (criterion, replayed)
        negative_rows.append({"criterion": criterion, "decision": result["decision"],
                              "reason": result["reason_code"], "service": replayed["service_status"]})

    stability_rows = []
    unsafe = 0
    for name, criterion, reports, expected, complete in STABILITY_CASES:
        store, decisions = evaluate_patient(reports, (criterion,))
        decision = decisions[criterion]
        if decision["decision"] == "MATCH" and not complete:
            classification = "UNSAFE_RELAXATION"
            unsafe += 1
        elif decision["decision"] == "MATCH" and complete:
            classification = "SAFE_COMPLETION"
        else:
            classification = "NO_CHANGE"
        stability_rows.append({
            "case": name,
            "criterion": criterion,
            "facts_gained": len(store["facts"]),
            "decision_e": "NOT_REPLAYED",
            "decision_v6": decision["decision"],
            "reason": decision["reason_code"],
            "required_facts_grounded": complete,
            "classification": classification,
        })

    baseline_sha = hashlib.sha256(BASELINE.read_bytes()).hexdigest()
    train_entries = json.loads(TRAIN_BUNDLE.read_text(encoding="utf-8"))["entry"]
    library_count = sum(entry["resource"].get("resourceType") == "Library" for entry in train_entries)
    result = {
        "prototype": "scripts/v6_offline_prototype.py",
        "mvp_criteria": list(MVP_CRITERIA),
        "positive": positive_rows,
        "negative": negative_rows,
        "admission_stability": stability_rows,
        "unsafe_relaxation": unsafe,
        "compile": "PASS",
        "semantic_calls": 0,
        "service_replay": "PASS",
        "train_official_library_count": library_count,
        "test_a_criterion_definition_file": str(TEST_XLSX),
        "test_a_patient_text_available": False,
        "test_a_fact_coverage": "NOT_AVAILABLE_NOT_CHECKED",
        "experiment_e_sha256": baseline_sha,
        "expected_experiment_e_sha256": EXPECTED_BASELINE_SHA,
        "experiment_e_artifact_match": baseline_sha == EXPECTED_BASELINE_SHA,
        "candidate_generated": False,
        "tianchi": "NOT_SUBMITTED",
    }
    out = ROOT / "analysis/V6_OFFLINE_BENCHMARK.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    stability = {
        "scope": "synthetic_and_existing_fixture_only",
        "online_labels_used": False,
        "test_a_patient_text_available": False,
        "rows": stability_rows,
        "unsafe_relaxation": unsafe,
        "verdict": "PASS" if unsafe == 0 else "FAIL",
    }
    (ROOT / "analysis/V6_ADMISSION_STABILITY.json").write_text(
        json.dumps(stability, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
