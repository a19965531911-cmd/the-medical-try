from dataclasses import dataclass, field, replace
from importlib import import_module
from types import MappingProxyType, SimpleNamespace
from typing import Any, Mapping

from v43.clinical.store import ClinicalStore
from v43.constraints.executor import execute
from v43.constraints.trace import DecisionTrace
from v43.constraints.values import EligibilityResult, TruthValue
from v43.episodes.linker import link_episode
from v43.extraction.semantic import CallGuard, SemanticExtractionError, extract_semantic
from v43.ir.loader import load_criterion_ir
from v43.references import CRITERION_IDS, frozen_reference_paths
from v43.retrieval.models import EvidencePacket
from v43.retrieval.retriever import retrieve
from v43.temporal.reconcile import reconcile


@dataclass(frozen=True, slots=True)
class RuntimeServices:
    semantic_transport: object | None
    timeout_seconds: float
    temporal_policy: str = "REVIEW_REQUIRED"
    _semantic_guard: CallGuard = field(
        default_factory=CallGuard,
        init=False,
        repr=False,
        compare=False,
    )


@dataclass(frozen=True, slots=True)
class CriterionRun:
    criterion_id: str
    patient_run_id: str
    evidence_packet: EvidencePacket
    fact_count: int
    event_count: int
    relation_count: int
    episode_count: int
    temporal_views: Mapping[str, Mapping[str, tuple[str, ...]]]
    decision_trace: DecisionTrace
    extraction_status: str
    reason_codes: tuple[str, ...]


def _add_objects(store: ClinicalStore, objects: tuple[tuple[Any, ...], ...]) -> None:
    for fact in objects[0]:
        store.add_fact(fact)
    for event in objects[1]:
        store.add_event(event)
    for relation in objects[2]:
        store.add_relation(relation)


def _temporal_views(store: ClinicalStore) -> Mapping[str, Mapping[str, tuple[str, ...]]]:
    concepts = tuple(dict.fromkeys(fact.concept for fact in store.facts))
    result = {
        concept: MappingProxyType({view.value: ids for view, ids in reconcile(store, concept, "patient").items()})
        for concept in concepts
    }
    return MappingProxyType(result)


def _resolved_temporal_ir(ir: Any) -> Any:
    raw = dict(ir.raw)
    raw["logical_expression"] = str(raw["logical_expression"]).replace("@REVIEW_REQUIRED", "")
    return replace(ir, raw=raw)


def _review_required(trace: DecisionTrace) -> DecisionTrace:
    return replace(
        trace,
        root_result=TruthValue.UNKNOWN,
        eligibility_result=EligibilityResult.INSUFFICIENT_EVIDENCE,
        reason_code="TEMPORAL_SCOPE_REVIEW_REQUIRED",
    )


def _current_875_store(
    store: ClinicalStore,
    valid_span_ids: frozenset[str],
    temporal_views: Mapping[str, Mapping[str, tuple[str, ...]]],
) -> ClinicalStore:
    current_ids = {
        fact_id
        for concept in ("intracranial_hypertension", "consciousness_impairment")
        for fact_id in temporal_views.get(concept, {}).get("CURRENT", ())
    }
    current = ClinicalStore(valid_span_ids)
    for fact in store.facts:
        if fact.fact_id in current_ids:
            current.add_fact(fact)
    return current


def evaluate_criterion(
    criterion_id: str,
    patient_id: str,
    reports: list[dict[str, Any]],
    services: RuntimeServices,
) -> CriterionRun:
    criterion_id = str(criterion_id)
    if criterion_id not in CRITERION_IDS:
        raise ValueError(f"unsupported criterion ID: {criterion_id}")
    ir = load_criterion_ir(frozen_reference_paths()["criterion_ir_draft"], (criterion_id,))[criterion_id]
    packet = retrieve(ir, reports)
    plugin = import_module(f"v43.criteria.c{criterion_id}")
    constraints = plugin.build_constraints(ir)

    store = ClinicalStore.from_packet(packet)
    _add_objects(store, plugin.extract(packet))
    reason_codes: list[str] = []
    extraction_status = "DETERMINISTIC"
    if services.semantic_transport is not None and criterion_id in {"185", "675", "745", "875"}:
        try:
            semantic = extract_semantic(
                ir,
                packet,
                services.semantic_transport,
                services._semantic_guard,
                patient_id=patient_id,
                timeout=services.timeout_seconds,
            )
            _add_objects(store, semantic)
            extraction_status = "DETERMINISTIC_AND_SEMANTIC"
        except SemanticExtractionError as exc:
            extraction_status = "SEMANTIC_REJECTED"
            reason_codes.append(exc.reason_code)

    for episode in link_episode(store.events, store.relations, ir.raw.get("episode_policy", {})):
        store.add_episode(episode)
    temporal_views = _temporal_views(store)

    execution_ir = _resolved_temporal_ir(ir) if criterion_id == "875" else ir
    execution_ir = SimpleNamespace(
        criterion_id=execution_ir.criterion_id,
        raw=execution_ir.raw,
        constraints=constraints,
        root_constraint_id="root",
    )
    execution_store = (
        _current_875_store(store, store.valid_span_ids, temporal_views)
        if criterion_id == "875" and services.temporal_policy == "CURRENT_ACTIVE"
        else store
    )
    trace = execute(execution_ir, execution_store)
    if criterion_id == "875" and services.temporal_policy == "REVIEW_REQUIRED":
        trace = _review_required(trace)
        reason_codes.append("TEMPORAL_SCOPE_REVIEW_REQUIRED")
    elif criterion_id == "875" and services.temporal_policy not in {"CURRENT_ACTIVE", "EVER_PRESENT"}:
        raise ValueError(f"unsupported 875 temporal policy: {services.temporal_policy}")

    return CriterionRun(
        criterion_id,
        patient_id,
        packet,
        len(store.facts),
        len(store.events),
        len(store.relations),
        len(store.episodes),
        temporal_views,
        trace,
        extraction_status,
        tuple(reason_codes),
    )
