from v5.criterion_specs import load_criterion_specs
from v5.prompt import build_prompt
from v5.retrieval import select_evidence


def test_retrieval_retains_cross_report_alias_evidence():
    spec = load_criterion_specs()["675"]
    reports = [{"text": "患者62岁"}, {"text": "一般情况稳定"}, {"text": "确诊颜面部带状疱疹"}]
    selected = select_evidence(spec, reports, max_segments=3, max_chars=200)
    assert {0, 2} <= {item.report_index for item in selected}


def test_no_keyword_still_returns_high_information_fallback():
    spec = load_criterion_specs()["185"]
    reports = [{"text": "该方案为患者此前未曾接受的拓扑异构酶抑制治疗。"}]
    selected = select_evidence(spec, reports, max_segments=2, max_chars=100)
    assert len(selected) == 1
    assert selected[0].tier == "C"


def test_retrieval_enforces_segment_and_character_bounds():
    spec = load_criterion_specs()["735"]
    reports = [{"text": "活动性乙型肝炎" * 300}, {"text": "结核活动期" * 300}, {"text": "其他" * 300}]
    selected = select_evidence(spec, reports, max_segments=2, max_chars=80)
    assert len(selected) <= 2
    assert sum(len(item.text) for item in selected) <= 80


def test_prompt_contains_semantic_critical_fields_and_protocol():
    for spec in load_criterion_specs().values():
        prompt = build_prompt(spec, select_evidence(spec, [{"text": "待判断的临床叙述"}]))
        assert spec.original_text in prompt
        assert spec.plain_summary in prompt
        assert "MATCH / NO_MATCH / UNKNOWN" in prompt
        assert "missing" in prompt.lower() or "缺失" in prompt
        for threshold in spec.thresholds:
            assert threshold in prompt
