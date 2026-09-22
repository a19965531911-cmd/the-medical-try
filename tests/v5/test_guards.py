import pytest

from v5.criterion_specs import load_criterion_specs
from v5.guards import apply_guard
from v5.models import Decision


@pytest.mark.parametrize(("criterion", "text", "reason"), [
    ("185", "拟首次使用伊立替康，尚未给药", "PLANNED_ONLY"),
    ("185", "既往已多次接受伊立替康", "PRIOR_MULTIPLE_USE"),
    ("555", "手术距今8个月", "OUTSIDE_SIX_MONTHS"),
    ("675", "躯干部带状疱疹，非头面部", "NON_HEAD_FACE_SITE"),
    ("745", "拟术后插管，尚未实施", "PLANNED_ONLY"),
    ("745", "术后仅无创通气", "NON_INVASIVE_ONLY"),
    ("755", "症状仅持续3天", "DURATION_TOO_SHORT"),
    ("805", "从不吸烟", "NEVER_SMOKER"),
    ("805", "已戒烟3年", "CESSATION_AT_LEAST_TWO_YEARS"),
])
def test_explicit_contradiction_downgrades_model_match(criterion, text, reason):
    result = apply_guard(load_criterion_specs()[criterion], [{"text": text}], Decision.MATCH)
    assert result.decision is Decision.NO_MATCH
    assert result.reason_code == reason


def test_guard_does_not_invent_a_contradiction():
    result = apply_guard(load_criterion_specs()["805"], [{"text": "既往吸烟，戒烟时间不详"}], Decision.MATCH)
    assert result.decision is Decision.MATCH
    assert result.reason_code is None

