from dataclasses import FrozenInstanceError
from inspect import signature

import pytest

from v43.constraints.values import EligibilityResult
from v43.runtime import RuntimeServices, evaluate_criterion


def run(cid, *texts, policy="REVIEW_REQUIRED"):
    reports=[{"text":t,"topic":"note","timestamp":f"2026-01-{i+1:02d}"} for i,t in enumerate(texts)]
    return evaluate_criterion(cid, "p1", reports, RuntimeServices(None, 1.0, policy))


def test_185_hard_positives_and_negatives():
    result = run("185", "患者首次接受伊立替康静脉给药")
    assert result.decision_trace.eligibility_result is EligibilityResult.SATISFIED
    assert result.event_count == 1 and result.evidence_packet.spans
    for text in ("计划首次使用伊立替康", "拟首次接受伊立替康给药", "既往多次使用伊立替康", "母亲曾使用伊立替康", "方案中提及伊立替康"):
        assert run("185", text).decision_trace.eligibility_result is not EligibilityResult.SATISFIED
    assert run("185", "未接受伊立替康给药").decision_trace.eligibility_result is not EligibilityResult.SATISFIED


def test_675_correspondence():
    assert run("675", "患者55岁", "确诊头面部带状疱疹").decision_trace.eligibility_result is EligibilityResult.SATISFIED
    assert run("675", "患者55岁，确诊躯干部带状疱疹", "面部另有皮损").decision_trace.eligibility_result is not EligibilityResult.SATISFIED
    assert run("675", "患者55岁，未确诊头面部带状疱疹").decision_trace.eligibility_result is not EligibilityResult.SATISFIED


def test_745_postoperative_not_unrelated_or_noninvasive():
    assert run("745", "术后自主呼吸欠佳，继续气管插管有创机械通气").decision_trace.eligibility_result is EligibilityResult.SATISFIED
    for texts in (("10年前胆囊切除术", "此次肺炎机械通气"), ("术前拟行有创机械通气",), ("术后无创机械通气",), ("术后未行气管插管有创机械通气",)):
        assert run("745", *texts).decision_trace.eligibility_result is not EligibilityResult.SATISFIED


def test_875_review_and_injectable_policies():
    reviewed=run("875", "呼之能应，神志朦胧")
    assert reviewed.decision_trace.eligibility_result is EligibilityResult.INSUFFICIENT_EVIDENCE
    assert reviewed.decision_trace.reason_code == "TEMPORAL_SCOPE_REVIEW_REQUIRED"
    assert run("875", "颅内高压", policy="EVER_PRESENT").decision_trace.eligibility_result is EligibilityResult.SATISFIED
    assert run("875", "目前意识不清", policy="CURRENT_ACTIVE").decision_trace.eligibility_result is EligibilityResult.SATISFIED
    for text in ("否认颅内高压", "已排除颅内高压"):
        assert run("875", text, policy="EVER_PRESENT").decision_trace.eligibility_result is not EligibilityResult.SATISFIED


def test_875_current_active_uses_latest_state_but_ever_present_preserves_history():
    texts = ("曾有颅内高压", "目前无颅内高压")
    assert run("875", *texts, policy="CURRENT_ACTIVE").decision_trace.eligibility_result is not EligibilityResult.SATISFIED
    assert run("875", *texts, policy="EVER_PRESENT").decision_trace.eligibility_result is EligibilityResult.SATISFIED


def test_runtime_contracts_are_locked_and_expose_composed_pipeline_state():
    assert tuple(signature(RuntimeServices).parameters) == ("semantic_transport", "timeout_seconds", "temporal_policy")
    assert RuntimeServices(None, 1.0).temporal_policy == "REVIEW_REQUIRED"
    services = RuntimeServices(None, 1.0, "CURRENT_ACTIVE")
    with pytest.raises(FrozenInstanceError):
        services.temporal_policy = "EVER_PRESENT"
    result = run("675", "患者55岁", "确诊头面部带状疱疹")
    assert result.fact_count == 2
    assert result.event_count == 1
    assert result.relation_count == 1
    assert result.episode_count >= 1
    assert result.temporal_views
    with pytest.raises(FrozenInstanceError):
        result.fact_count = 0


class SemanticTransport:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = 0

    def post(self, payload, timeout):
        self.calls += 1
        if self.error is not None:
            raise self.error
        return self.response


def _semantic_response(span_id=None):
    facts = [] if span_id is None else [{
        "fact_id": "semantic-f1", "fact_type": "assertion", "concept": "first_use",
        "value": None, "unit": None, "state": "PRESENT", "subject": "patient",
        "temporality": "current", "clinical_time": None, "evidence_span_id": span_id,
        "report_index": 0, "confidence": 1.0,
    }]
    return {"facts": facts, "events": [], "relations": []}


@pytest.mark.parametrize("transport, expected_reason, raises", [
    (SemanticTransport(_semantic_response()), None, None),
    (SemanticTransport({"eligible": True, "facts": [], "events": [], "relations": []}), "SEMANTIC_SCHEMA_REJECT", None),
    (SemanticTransport(_semantic_response("missing")), "GROUNDING_REJECT", None),
    (SemanticTransport(error=TimeoutError("offline")), None, TimeoutError),
])
def test_runtime_services_share_terminal_semantic_guard_across_runs(transport, expected_reason, raises):
    services = RuntimeServices(transport, 1.0)
    reports = [{"text": "患者首次接受伊立替康静脉给药", "timestamp": "2026-01-01"}]
    for _ in range(2):
        if raises is not None:
            with pytest.raises(raises, match="offline"):
                evaluate_criterion("185", "p-cache", reports, services)
        else:
            result = evaluate_criterion("185", "p-cache", reports, services)
            if expected_reason is not None:
                assert expected_reason in result.reason_codes
    assert transport.calls == 1


def test_current_875_post_extraction_boundary_receives_only_span_ids(monkeypatch):
    import v43.runtime as runtime

    original = runtime._current_875_store

    def checked(store, valid_span_ids, temporal_views):
        assert isinstance(valid_span_ids, frozenset)
        return original(store, valid_span_ids, temporal_views)

    monkeypatch.setattr(runtime, "_current_875_store", checked)
    assert run("875", "目前意识不清", policy="CURRENT_ACTIVE").decision_trace.eligibility_result is EligibilityResult.SATISFIED
