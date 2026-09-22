from typing import Any, Mapping

from .reason_codes import ReasonCodeRegistry


_ALLOWED = frozenset({
    "run_id", "stage", "criterion", "retrieval_tier", "span_count", "fallback_used",
    "parser_status", "fact_count", "event_count", "relation_count", "episode_count",
    "temporal_status", "constraint_result", "resource_count", "structural_status",
    "service_status", "reason_code",
})


def emit_trace(event: Mapping[str, Any], sink=None) -> dict[str, Any]:
    sanitized = {key: value for key, value in event.items() if key in _ALLOWED}
    if "reason_code" in sanitized:
        ReasonCodeRegistry.from_frozen_csv().validate(str(sanitized["reason_code"]))
    if sink is not None:
        sink(dict(sanitized))
    return sanitized

