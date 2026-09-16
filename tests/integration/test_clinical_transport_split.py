from importlib import import_module

import pytest

from v43.clinical.store import ClinicalStore
from v43.fhir.compiler import compile_fhir
from v43.fhir.contracts import contract_for_criterion
from v43.fhir.service_replay import replay_service
from v43.fhir.validator import validate_fhir
from v43.ir.loader import load_criterion_ir
from v43.references import frozen_reference_paths
from v43.retrieval.retriever import retrieve
from v43.runtime import RuntimeServices, evaluate_criterion


CASES = {
    "165": ("转入我院前于当地医院完成2周期化疗", "MedicationAdministration", "Procedure"),
    "485": ("盆腔器官脱垂，POP-Q III期", "pelvic_organ_prolapse", "Observation"),
    "565": ("目前严重腹泻", "severe_diarrhea", "Observation"),
}


@pytest.mark.parametrize("criterion", CASES)
def test_clinical_semantics_remain_typed_while_transport_matches_legacy_service(criterion):
    text, clinical_type, transport_type = CASES[criterion]
    reports = [{"text": text, "timestamp": "2026-01-01", "fixture_source": "regression"}]
    ir = load_criterion_ir(frozen_reference_paths()["criterion_ir_draft"], (criterion,))[criterion]
    packet = retrieve(ir, reports)
    store = ClinicalStore.from_packet(packet)
    facts, events, relations = import_module(f"v43.criteria.c{criterion}").extract(packet)
    for item in facts:
        store.add_fact(item)
    for item in events:
        store.add_event(item)
    for item in relations:
        store.add_relation(item)

    if criterion == "165":
        assert any(event.event_type == clinical_type for event in store.events)
    else:
        assert any(fact.concept == clinical_type for fact in store.facts)

    run = evaluate_criterion(criterion, "p1", reports, RuntimeServices(None, 1.0))
    contract = contract_for_criterion(criterion)
    result = validate_fhir(compile_fhir(run.decision_trace, store, contract, "Patient/p1"), contract)
    assert result.structural_status == "VALID"
    assert {resource["resourceType"] for resource in result.resources} == {transport_type}
    assert replay_service(result.resources, contract.service, "fixture://fhir", {"p1": "doc"}).status == "SERVICE_HIT"

