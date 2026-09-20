import io
from contextlib import redirect_stdout

import pytest

from scripts.build_v5s2_expe_aggressive_submission import build_source


def run_case(criterion, text, answer="YES"):
    namespace = {}
    exec(compile(build_source(criterion, criterion, {}), criterion, "exec"), namespace)
    generator = namespace["FHIRResourceBundleGenerator"]("http://localhost:3456")
    generator.transport = lambda _prompt: answer
    output = io.StringIO()
    with redirect_stdout(output):
        bundle = generator.parse_clinical_text_to_fhir_bundle(
            "p1", [{"text": text, "timestamp": "2026-01-31T12:34:56+08:00"}]
        )
    metrics_line = next(
        line for line in output.getvalue().splitlines()
        if line.startswith("V5S2E_METRICS|")
    )
    metrics = dict(field.split("=", 1) for field in metrics_line.split("|")[1:])
    return metrics, bundle


@pytest.mark.parametrize(
    ("criterion", "text"),
    [
        ("675", "确诊带状疱疹"),
        ("745", "已完成手术治疗"),
        ("165", "已完成化疗"),
        ("165", "已在外院完成治疗"),
    ],
)
def test_single_real_anchor_plus_llm_match_is_admitted(criterion, text):
    metrics, _bundle = run_case(criterion, text)
    assert metrics["final_decision"] == "MATCH"
    assert metrics["admission_mode"] == "PARTIAL_GROUNDED"


def test_age_only_is_not_a_zoster_positive():
    metrics, bundle = run_case("675", "患者年龄70岁")
    assert metrics["final_decision"] == "NO_MATCH"
    assert not bundle["entry"]


@pytest.mark.parametrize("text", ["计划外院化疗", "拟转外院化疗，尚未开始"])
def test_165_planned_only_is_blocked(text):
    metrics, bundle = run_case("165", text)
    assert metrics["final_decision"] == "NO_MATCH"
    assert metrics["hard_contradiction"] == "PLANNED_ONLY"
    assert not bundle["entry"]


@pytest.mark.parametrize(
    ("criterion", "text", "expected"),
    [
        ("485", "盆腔器官脱垂", "MATCH"),
        ("485", "盆腔器官脱垂 POP-Q III期", "MATCH"),
        ("485", "POP-Q II期", "NO_MATCH"),
        ("735", "乙型肝炎", "MATCH"),
        ("735", "乙型肝炎已治愈", "NO_MATCH"),
        ("745", "机械通气", "MATCH"),
        ("745", "计划无创通气 NIV", "NO_MATCH"),
        ("755", "机械通气", "MATCH"),
        ("755", "机械通气持续23小时", "NO_MATCH"),
        ("755", "机械通气持续24小时", "MATCH"),
        ("265", "肌钙蛋白升高", "MATCH"),
        ("265", "cTnI 0.03 ug/L", "NO_MATCH"),
        ("635", "AST 90 上限40", "NO_MATCH"),
        ("615", "术后病理 pN1", "MATCH"),
        ("555", "已完成手术", "MATCH"),
        ("555", "7个月前完成手术", "NO_MATCH"),
        ("565", "目前腹泻", "MATCH"),
        ("565", "腹泻已解决", "NO_MATCH"),
        ("185", "已使用伊立替康", "MATCH"),
        ("185", "计划使用伊立替康", "NO_MATCH"),
        ("855", "BUN 12 mmol/L", "NO_MATCH"),
        ("875", "否认颅内高压", "NO_MATCH"),
    ],
)
def test_relaxed_admission_and_hard_contradictions(criterion, text, expected):
    metrics, bundle = run_case(criterion, text)
    assert metrics["final_decision"] == expected
    if expected == "NO_MATCH":
        assert not bundle["entry"]


def test_zero_anchor_fallback_match_is_blocked():
    metrics, bundle = run_case("615", "一般情况稳定")
    assert metrics["final_decision"] == "NO_MATCH"
    assert metrics["admission_mode"] == "FALLBACK_BLOCK"
    assert not bundle["entry"]
