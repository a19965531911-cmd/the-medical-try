from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Iterable, Mapping
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class V43ShadowInput:
    run: Any
    resource_count: int
    service_hit: str


@dataclass(frozen=True, slots=True)
class ShadowDecisionRecord:
    criterion: str
    anonymized_case_id: str
    v243_decision: str
    v422_decision: str
    v43_decision: str
    v243_resource_count: int
    v422_resource_count: int
    v43_resource_count: int
    v243_service_hit: str
    v422_service_hit: str
    v43_service_hit: str
    retrieved_span_count: int
    fact_count: int
    event_count: int
    relation_count: int
    v43_constraint_result: str
    v43_decision_trace: dict
    delta_type: str
    reason_code: str


def _value(value: Any) -> Any:
    return value.value if isinstance(value, Enum) else value


def _trace_dict(trace: Any) -> dict:
    def normalize(value: Any) -> Any:
        if isinstance(value, Enum):
            return value.value
        if hasattr(value, "__dataclass_fields__"):
            return {key: normalize(val) for key, val in asdict(value).items()}
        if isinstance(value, (tuple, list)):
            return [normalize(item) for item in value]
        return value
    if hasattr(trace, "__dataclass_fields__"):
        return normalize(trace)
    return {
        "eligibility_result": _value(trace.eligibility_result),
        "root_result": _value(trace.root_result),
        "reason_code": trace.reason_code,
        "nodes": normalize(trace.nodes),
        "supporting_node_ids": list(trace.supporting_node_ids),
        "blocking_node_ids": list(trace.blocking_node_ids),
        "unknown_node_ids": list(trace.unknown_node_ids),
    }


def _delta(old, new_decision: str, new_count: int, new_service: str) -> str:
    old_positive = old.decision == "SATISFIED"
    new_positive = new_decision == "SATISFIED"
    if old_positive and not new_positive:
        return "REGRESSION"
    if not old_positive and new_positive:
        return "RECOVERY"
    if old.resource_count != new_count:
        return "FHIR_DELTA"
    if old.service_hit != new_service:
        return "SERVICE_DELTA"
    return "UNCHANGED_POSITIVE" if new_positive else "UNCHANGED_NEGATIVE"


def compare_case(adapter243, adapter422, v43_run: V43ShadowInput, reports: list[dict]) -> ShadowDecisionRecord:
    run = v43_run.run
    old243 = adapter243.observe(run.criterion_id, run.patient_run_id, reports)
    old422 = adapter422.observe(run.criterion_id, run.patient_run_id, reports)
    decision = _value(run.decision_trace.eligibility_result)
    delta = _delta(old243, decision, v43_run.resource_count, v43_run.service_hit)
    return ShadowDecisionRecord(
        run.criterion_id, "case-" + uuid4().hex, old243.decision, old422.decision, decision,
        old243.resource_count, old422.resource_count, v43_run.resource_count,
        old243.service_hit, old422.service_hit, v43_run.service_hit,
        len(run.evidence_packet.spans), run.fact_count, run.event_count, run.relation_count,
        _value(run.decision_trace.root_result), _trace_dict(run.decision_trace), delta,
        str(run.decision_trace.reason_code),
    )


def run_ablation(case_set: Iterable[Mapping[str, Any]], modes: Iterable[str]) -> dict:
    cases = tuple(case_set)
    result = {}
    for mode in modes:
        hits = sum(case["critical_span_id"] in case["retrieved"].get(mode, ()) for case in cases)
        result[mode] = {"cases": len(cases), "critical_hits": hits,
                        "recall_at_k": hits / len(cases) if cases else 0.0}
    return result

