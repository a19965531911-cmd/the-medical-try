import json

import pytest

from v43.extraction.semantic import CallGuard, SemanticExtractionError, extract_semantic
from v43.ir.models import CriterionIR, CriterionType, FHIRContract, RetrievalPolicy, ServiceQueryContract
from v43.retrieval.models import EvidencePacket, EvidenceSpan


class FakeTransport:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def post(self, payload, timeout):
        self.calls.append((payload, timeout))
        return self.response


def ir():
    raw = {"criterion_id": "185", "constraint_semantics": {"op": "AND"}, "fact_schema": {}, "event_schema": {}, "relation_schema": {}}
    return CriterionIR("185", "first irinotecan", "reviewed summary", CriterionType.eligibility, "oncology",
                       RetrievalPolicy(("irinotecan",), (), (), True, 3, False),
                       FHIRContract("MedicationAdministration", (), (), (), (), (), (), {}),
                       ServiceQueryContract("MedicationAdministration", None, (), {}), "CURRENT", raw)


def packet():
    return EvidencePacket((EvidenceSpan("s1", "伊立替康首次实际给药", 2, "treatment", "2026-01-01", 0, 10, "h"),))


def valid_response(span_id="s1"):
    return {"facts": [{"fact_id": "f1", "fact_type": "assertion", "concept": "first_use", "value": None,
                       "unit": None, "state": "PRESENT", "subject": "patient", "temporality": "current",
                       "clinical_time": None, "evidence_span_id": span_id, "report_index": 2, "confidence": 1.0}],
            "events": [], "relations": []}


def test_semantic_prompt_contains_full_ir_packet_and_allowed_schema():
    transport = FakeTransport(valid_response())
    extract_semantic(ir(), packet(), transport, CallGuard(), patient_id="p1", timeout=4.5)
    payload, timeout = transport.calls[0]
    prompt = json.loads(payload["messages"][0]["content"])
    assert prompt["criterion_ir"] == ir().raw
    assert prompt["evidence_packet"][0]["span_id"] == "s1"
    assert prompt["allowed_output"] == {"facts": "ClinicalFact[]", "events": "ClinicalEvent[]", "relations": "ClinicalRelation[]"}
    assert payload["model"] == "local-model" and payload["temperature"] == 0
    assert timeout == 4.5


def test_semantic_calls_transport_at_most_once_per_patient_criterion():
    transport = FakeTransport(valid_response())
    guard = CallGuard()
    first = extract_semantic(ir(), packet(), transport, guard, patient_id="p1")
    second = extract_semantic(ir(), packet(), transport, guard, patient_id="p1")
    assert first == second
    assert len(transport.calls) == 1


@pytest.mark.parametrize("response", [
    {"eligible": True, "facts": [], "events": [], "relations": []},
    {"facts": [{"concept": "x", "attributes": {"match": True}}], "events": [], "relations": []},
    {"facts": [], "events": [], "relations": [], "meta": {"qualified": True}},
    {"facts": [], "events": [], "relations": [{"final_decision": "yes"}]},
])
def test_semantic_rejects_forbidden_decision_keys_anywhere(response):
    with pytest.raises(SemanticExtractionError) as exc:
        extract_semantic(ir(), packet(), FakeTransport(response), CallGuard(), patient_id="p1")
    assert exc.value.reason_code == "SCHEMA_REJECT"


def test_semantic_rejects_unknown_span_without_fuzzy_substitution():
    with pytest.raises(SemanticExtractionError) as exc:
        extract_semantic(ir(), packet(), FakeTransport(valid_response("S1")), CallGuard(), patient_id="p1")
    assert exc.value.reason_code == "GROUNDING_REJECT"


@pytest.mark.parametrize("response", [
    {"eligible": True, "facts": [], "events": [], "relations": []},
    valid_response("missing"),
])
def test_semantic_rejection_is_terminal_without_second_post(response):
    transport = FakeTransport(response)
    guard = CallGuard()
    for _ in range(2):
        with pytest.raises(SemanticExtractionError):
            extract_semantic(ir(), packet(), transport, guard, patient_id="p1")
    assert len(transport.calls) == 1


def test_semantic_transport_failure_is_terminal_without_second_post():
    class FailingTransport(FakeTransport):
        def post(self, payload, timeout):
            self.calls.append((payload, timeout))
            raise TimeoutError("offline")

    transport = FailingTransport(None)
    guard = CallGuard()
    for _ in range(2):
        with pytest.raises(TimeoutError, match="offline"):
            extract_semantic(ir(), packet(), transport, guard, patient_id="p1")
    assert len(transport.calls) == 1
