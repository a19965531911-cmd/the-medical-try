import pytest

from v43.constraints.values import EligibilityResult
from v43.runtime import RuntimeServices, evaluate_criterion


def run(criterion, *texts):
    reports = [
        {"text": text, "topic": "note", "timestamp": f"2026-01-{index + 1:02d}", "fixture_source": "synthetic"}
        for index, text in enumerate(texts)
    ]
    return evaluate_criterion(criterion, "phase2-case", reports, RuntimeServices(None, 1.0))


def assert_sat(criterion, text):
    assert run(criterion, text).decision_trace.eligibility_result is EligibilityResult.SATISFIED


def assert_not_sat(criterion, text):
    assert run(criterion, text).decision_trace.eligibility_result is not EligibilityResult.SATISFIED


def test_block_a_numeric_and_temporal_criteria():
    assert_sat("265", "术前cTnI 0.08 μg/L")
    assert_not_sat("265", "术后cTnI 0.08 μg/L")
    for positive in ("病理pT3a", "切缘R1", "pN1", "Gleason评分8分", "PSA 0.2 ng/mL"):
        assert_sat("615", positive)
    assert_not_sat("615", "Gleason评分7分，PSA 0.1 ng/mL")
    assert_sat("635", "AST 30 U/L上限40，ALT 50 U/L上限40，BUN 12 mmol/L上限9，Cr 180 umol/L上限100")
    assert_not_sat("635", "AST 30 U/L上限40，ALT 50 U/L上限40，BUN 12 mmol/L上限9，Cr 201 umol/L上限100")
    assert_not_sat("635", "AST 30 U/L上限40")
    assert_sat("755", "机械通气持续30小时")
    assert_not_sat("755", "机械通气持续12小时")
    assert_sat("855", "Scr 120 μmol/L，BUN 7 mmol/L，ALT 30 U/L上限40，AST 25 U/L上限40")
    assert_not_sat("855", "Scr 190 μmol/L，BUN 7 mmol/L，ALT 30 U/L上限40，AST 25 U/L上限40")
    assert_sat("805", "目前每日吸烟")
    assert_sat("805", "戒烟1年")
    assert_not_sat("805", "戒烟3年")
    assert_not_sat("805", "从不吸烟")
    assert_sat("555", "3个月前行胆囊切除术")
    assert_not_sat("555", "8个月前行胆囊切除术")
    assert_not_sat("555", "既往有手术史")


def test_block_b_diagnosis_state_and_symptom_criteria():
    assert_sat("485", "盆腔器官脱垂，POP-Q III期")
    assert_not_sat("485", "盆腔器官脱垂，POP-Q II期")
    assert_sat("735", "活动性乙型肝炎")
    assert_not_sat("735", "乙型肝炎已稳定")
    assert_sat("835", "目前凝血功能异常")
    assert_not_sat("835", "凝血功能正常")
    assert_sat("565", "目前严重腹泻")
    assert_sat("565", "目前严重便秘")
    assert_not_sat("565", "轻度腹泻")


def test_block_c_outside_hospital_chemotherapy():
    assert_sat("165", "转入我院前于当地医院完成2周期化疗")
    assert_not_sat("165", "拟于外院接受化疗")
    assert_not_sat("165", "母亲曾在外院接受化疗")


def test_structured_phase2_criteria_do_not_call_semantic_transport():
    class FailingTransport:
        def post(self, payload, timeout):
            raise AssertionError("structured criterion must not call semantic transport")

    for criterion, text in (("265", "术前cTnI 0.08 μg/L"), ("615", "病理pT3a"),
                            ("635", "AST 50 U/L，参考上限40 U/L"), ("755", "机械通气30小时"),
                            ("855", "Scr 120 μmol/L，BUN 7 mmol/L，ALT 30 U/L上限40，AST 25 U/L上限40"),
                            ("805", "目前吸烟"), ("555", "3个月前手术")):
        reports = [{"text": text, "timestamp": "2026-01-01", "fixture_source": "synthetic"}]
        evaluate_criterion(criterion, "no-llm", reports, RuntimeServices(FailingTransport(), 1.0))


@pytest.mark.parametrize("criterion, paraphrase, negatives", [
    ("265", "术前检查cTnT 0.04 ug/L", ("术后cTnT 0.04 ug/L", "术前cTnT 0.02 ug/L")),
    ("615", "术后病理提示pN1", ("pN0，Gleason评分7分", "PSA 0.05 ng/mL")),
    ("635", "AST 30 U/L上限40，ALT 50 U/L上限40，BUN 12 mmol/L上限9，Cr 180 umol/L上限100", ("AST 30 U/L上限40，ALT 50 U/L上限40，BUN 12 mmol/L上限9，Cr 201 umol/L上限100", "ALT 50 U/L上限40")),
    ("755", "机械通气25h", ("机械通气20小时", "仅记录机械通气")),
    ("855", "Scr 100 umol/L，BUN 6 mmol/L，ALT 20 U/L上限40，AST 20 U/L上限40", ("Scr 180 μmol/L，BUN 6 mmol/L，ALT 20 U/L上限40，AST 20 U/L上限40", "Scr 100 μmol/L")),
    ("805", "当前吸烟", ("戒烟2年", "从未吸烟")),
    ("555", "5个月前接受手术", ("7个月前接受手术", "患者母亲3个月前手术")),
    ("485", "子宫脱垂，POP-Q IV度", ("POP-Q评估完成但未记录分期", "盆腔器官脱垂POP-Q II期")),
    ("735", "乙肝活动期", ("既往乙肝已稳定", "家族有活动性乙肝")),
    ("835", "现有凝血功能障碍", ("凝血功能正常", "曾有凝血异常，目前正常")),
    ("565", "现为重度便秘", ("轻度便秘", "严重腹泻已缓解")),
    ("165", "在外院已行三周期化疗", ("计划在外院化疗", "父亲在当地医院完成化疗")),
])
def test_expanded_paraphrase_hard_negatives_and_missing_evidence(criterion, paraphrase, negatives):
    assert_sat(criterion, paraphrase)
    for text in negatives:
        assert_not_sat(criterion, text)
    assert_not_sat(criterion, "资料未提供相关信息")
