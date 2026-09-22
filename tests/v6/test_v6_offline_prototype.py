import pytest

from scripts.v6_offline_prototype import MVP_CRITERIA, evaluate_patient, replay


POSITIVE_CASES = {
    "555": [
        {"text": "患者于2026-06-01完成胆囊切除术", "timestamp": "2026-06-01"},
        {"text": "本次评估", "timestamp": "2026-09-01"},
    ],
    "565": [{"text": "目前严重腹泻", "timestamp": "2026-09-01"}],
    "615": [{"text": "复查PSA 0.2 ng/mL", "timestamp": "2026-09-01"}],
    "675": [
        {"text": "患者65岁", "timestamp": "2026-09-01"},
        {"text": "确诊头面部带状疱疹", "timestamp": "2026-09-01"},
    ],
    "735": [{"text": "目前乙型肝炎处于活动期", "timestamp": "2026-09-01"}],
    "745": [
        {"text": "患者于2026-08-01完成手术", "timestamp": "2026-08-01"},
        {"text": "术后于2026-08-01行气管插管有创机械通气", "timestamp": "2026-08-01"},
    ],
}


@pytest.mark.parametrize("criterion", MVP_CRITERIA)
def test_positive_mvp_cases_are_payload_and_service_ready(criterion):
    store, decisions = evaluate_patient(POSITIVE_CASES[criterion], (criterion,))
    result = decisions[criterion]
    replayed = replay("p1", result)

    assert store["semantic_calls"] == 0
    assert result["decision"] == "MATCH"
    assert result["payload_ready"] is True
    assert result["scorer_contract_ready"] is True
    assert replayed["service_status"] == "SERVICE_HIT"


@pytest.mark.parametrize(
    ("criterion", "reports", "decision", "reason"),
    [
        ("555", [{"text": "患者于2025-12-01完成手术", "timestamp": "2026-09-01"}], "NO_MATCH", "SURGERY_OVER_6_MONTHS"),
        ("555", [{"text": "既往有手术史", "timestamp": "2026-09-01"}], "UNKNOWN", "MISSING_GROUNDED_TIME"),
        ("555", [{"text": "计划于2026-08-01手术", "timestamp": "2026-09-01"}], "UNKNOWN", "NO_COMPLETED_SURGERY"),
        ("565", [{"text": "严重腹泻已缓解"}], "NO_MATCH", "SYMPTOM_RESOLVED"),
        ("565", [{"text": "目前轻度腹泻"}], "UNKNOWN", "SEVERITY_OR_CURRENT_STATE_MISSING"),
        ("565", [{"text": "否认腹泻"}], "UNKNOWN", "NO_SYMPTOM_FACT"),
        ("615", [{"text": "Gleason评分7分，PSA 0.1 ng/mL"}], "UNKNOWN", "NO_SATISFYING_ONCOLOGY_BRANCH"),
        ("615", [{"text": "母亲PSA 2.0 ng/mL"}], "UNKNOWN", "NO_SATISFYING_ONCOLOGY_BRANCH"),
        ("675", [{"text": "患者65岁"}, {"text": "确诊躯干部带状疱疹"}], "UNKNOWN", "MISSING_AGE_DIAGNOSIS_OR_SITE"),
        ("675", [{"text": "患者65岁，否认头面部带状疱疹"}], "NO_MATCH", "EXPLICIT_ZOSTER_NEGATION"),
        ("675", [{"text": "患者45岁"}, {"text": "确诊头面部带状疱疹"}], "NO_MATCH", "AGE_UNDER_50"),
        ("735", [{"text": "乙型肝炎已治愈"}], "NO_MATCH", "TARGET_DISEASE_RESOLVED"),
        ("735", [{"text": "既往乙肝病史"}], "UNKNOWN", "ACTIVITY_STATE_MISSING"),
        ("735", [{"text": "父亲患活动性乙肝"}], "UNKNOWN", "NO_TARGET_DISEASE"),
        ("745", [{"text": "术后仅无创机械通气"}], "NO_MATCH", "NONINVASIVE_ONLY"),
        ("745", [{"text": "计划术后行有创机械通气"}], "UNKNOWN", "MISSING_SURGERY_OR_INVASIVE_VENTILATION"),
        ("745", [{"text": "完成手术"}, {"text": "气管插管有创机械通气"}], "UNKNOWN", "POSTOPERATIVE_RELATION_UNRESOLVED"),
    ],
)
def test_precision_guards_preserve_no_match_or_unknown(criterion, reports, decision, reason):
    _, decisions = evaluate_patient(reports, (criterion,))
    result = decisions[criterion]

    assert result["decision"] == decision
    assert result["reason_code"] == reason
    assert replay("p1", result)["service_status"] == "SERVICE_MISS"


def test_local_scope_does_not_merge_conflicting_zoster_episodes():
    reports = [
        {"text": "既往否认带状疱疹", "timestamp": "2025-01-01"},
        {"text": "患者65岁，现确诊头面部带状疱疹", "timestamp": "2026-09-01"},
    ]
    _, decisions = evaluate_patient(reports, ("675",))

    assert decisions["675"]["decision"] == "NO_MATCH"


def test_match_without_required_time_is_not_emitted():
    reports = [{"text": "完成手术"}, {"text": "术后行气管插管有创机械通气"}]
    _, decisions = evaluate_patient(reports, ("745",))
    result = decisions["745"]

    assert result["decision"] == "MATCH"
    assert result["payload_ready"] is False
    assert result["scorer_contract_ready"] is False
    assert replay("p1", result)["resources"] == ()

