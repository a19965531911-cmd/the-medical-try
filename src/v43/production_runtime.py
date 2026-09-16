"""Self-contained production entrypoint backed by the verified V4.3 core."""
from importlib import import_module
from types import SimpleNamespace

from v43.clinical.store import ClinicalStore
from v43.constraints.executor import execute
from v43.fhir.compiler import compile_fhir
from v43.fhir.contracts import contract_for_criterion
from v43.retrieval.models import EvidencePacket
from v43.retrieval.segmenter import segment_reports

REVIEW_REQUIRED = "REVIEW_REQUIRED"
PRODUCTION_TEMPORAL_POLICY_875 = "EVER_PRESENT"

def evaluate_and_compile(criterion_id, patient_id, reports, temporal_policy_875=PRODUCTION_TEMPORAL_POLICY_875):
    criterion_id = str(criterion_id)
    spans = segment_reports([report for report in (reports or []) if isinstance(report, dict)])
    packet = EvidencePacket(spans=spans, retrieval_reason="PRODUCTION_ALL_SPANS")
    plugin = import_module("v43.criteria.c" + criterion_id)
    constraints = plugin.build_constraints(SimpleNamespace(criterion_id=criterion_id, raw={}))
    store = ClinicalStore.from_packet(packet)
    facts, events, relations = plugin.extract(packet)
    for fact in facts: store.add_fact(fact)
    for event in events: store.add_event(event)
    for relation in relations: store.add_relation(relation)
    trace = execute(SimpleNamespace(criterion_id=criterion_id, raw={}, constraints=constraints, root_constraint_id="root"), store)
    if criterion_id == "875" and temporal_policy_875 == REVIEW_REQUIRED:
        return trace, store, ()
    if criterion_id == "875" and temporal_policy_875 not in {"EVER_PRESENT", "CURRENT_ACTIVE"}:
        raise ValueError("unsupported 875 production policy: " + str(temporal_policy_875))
    compiled = compile_fhir(trace, store, contract_for_criterion(criterion_id), "Patient/" + str(patient_id))
    return trace, store, compiled.resources
