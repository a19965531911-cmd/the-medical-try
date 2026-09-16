from importlib import import_module

from v43.clinical.store import ClinicalStore
from v43.constraints.values import EligibilityResult
from v43.fhir.compiler import compile_fhir
from v43.fhir.contracts import contract_for_criterion
from v43.fhir.service_replay import replay_service
from v43.fhir.validator import validate_fhir
from v43.ir.loader import load_criterion_ir
from v43.references import frozen_reference_paths
from v43.retrieval.retriever import retrieve
from v43.runtime import RuntimeServices, evaluate_criterion


def _reports(texts):
    if isinstance(texts, str):
        texts = (texts,)
    return [{"text": text, "timestamp": "2026-01-01", "fixture_source": "regression"}
            for text in texts]


def _run(text):
    return evaluate_criterion("635", "p1", _reports(text), RuntimeServices(None, 1.0))


def _store(text):
    ir = load_criterion_ir(frozen_reference_paths()["criterion_ir_draft"], ("635",))["635"]
    packet = retrieve(ir, _reports(text))
    store = ClinicalStore.from_packet(packet)
    facts, events, relations = import_module("v43.criteria.c635").extract(packet)
    for item in facts:
        store.add_fact(item)
    for item in events:
        store.add_event(item)
    for item in relations:
        store.add_relation(item)
    return store


def test_635_is_inclusion_requiring_all_four_labs_at_or_below_twice_uln():
    eligible = ("AST 30 U/L上限40", "ALT 50 U/L上限40", "BUN 12 mmol/L上限9", "Cr 180 umol/L上限100")
    above_limit = (*eligible[:-1], "Cr 201 umol/L上限100")
    missing_ast = eligible[1:]

    assert _run(eligible).decision_trace.eligibility_result is EligibilityResult.SATISFIED
    assert _run(above_limit).decision_trace.eligibility_result is not EligibilityResult.SATISFIED
    assert _run(missing_ast).decision_trace.eligibility_result is not EligibilityResult.SATISFIED


def test_635_transport_emits_four_observations_and_matches_official_service_aggregation():
    text = ("AST 30 U/L上限40", "ALT 50 U/L上限40", "BUN 12 mmol/L上限9", "Cr 180 umol/L上限100")
    run = _run(text)
    contract = contract_for_criterion("635")
    validated = validate_fhir(compile_fhir(run.decision_trace, _store(text), contract, "Patient/p1"), contract)

    assert validated.structural_status == "VALID"
    assert len(validated.resources) == 4
    assert {r["code"]["coding"][0]["code"] for r in validated.resources} == {"AST", "ALT", "BUN", "Cr"}
    assert replay_service(validated.resources, contract.service, "fixture://fhir", {"p1": "doc"}).status == "SERVICE_HIT"
    assert replay_service(validated.resources[:-1], contract.service, "fixture://fhir", {"p1": "doc"}).status == "SERVICE_MISS"
