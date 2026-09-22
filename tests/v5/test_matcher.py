import pytest

from v5.criterion_specs import CRITERION_IDS, load_criterion_specs
from v5.matcher import match_patient
from v5.models import Decision
from v5.transport import TransportResult, TransportStatus
from v5.models import ParsedDecision, ParseMethod


class FakeTransport:
    def __init__(self, decision=Decision.MATCH, status=TransportStatus.OK):
        self.calls = []
        self.result = TransportResult(status, ParsedDecision(decision, ParseMethod.PARSED_SENTINEL), 1, 0.01, "choices")

    def decide(self, prompt):
        self.calls.append(prompt)
        return self.result


@pytest.mark.parametrize("criterion", CRITERION_IDS)
def test_all_criteria_use_one_semantic_call_when_fast_path_is_unresolved(criterion):
    transport = FakeTransport()
    result = match_patient(load_criterion_specs()[criterion], [{"text": "患者有相关临床记录，但使用了同义改写。"}], transport)
    assert result.final_decision is Decision.MATCH
    assert result.model_decision is Decision.MATCH
    assert len(transport.calls) == 1


def test_empty_patient_evidence_is_unknown_without_model_call():
    transport = FakeTransport()
    result = match_patient(load_criterion_specs()["675"], [{"text": "  "}], transport)
    assert result.final_decision is Decision.UNKNOWN
    assert transport.calls == []


def test_high_confidence_fast_path_skips_model():
    transport = FakeTransport()
    result = match_patient(load_criterion_specs()["615"], [{"text": "术后病理 pT3a。"}], transport)
    assert result.final_decision is Decision.MATCH
    assert result.deterministic_decision is Decision.MATCH
    assert transport.calls == []


def test_cross_report_evidence_is_in_single_patient_call():
    transport = FakeTransport()
    reports = [{"text": "患者56岁。"}, {"text": "颜面部疱疹已确诊。"}]
    result = match_patient(load_criterion_specs()["675"], reports, transport)
    assert result.final_decision is Decision.MATCH
    assert len(transport.calls) == 1
    assert "56岁" in transport.calls[0] and "颜面部疱疹" in transport.calls[0]


def test_transport_failure_stays_unknown():
    transport = FakeTransport(Decision.UNKNOWN, TransportStatus.CONNECT_ERROR)
    result = match_patient(load_criterion_specs()["675"], [{"text": "同义临床描述"}], transport)
    assert result.final_decision is Decision.UNKNOWN
    assert result.transport_status is TransportStatus.CONNECT_ERROR

