"""Read-only observer adapters for legacy resource emitters.

Proxy semantics are intentionally narrow: legacy_decision is SATISFIED iff the
legacy emitter returned at least one resource matching the requested criterion's
official resource type/profile. No legacy DecisionTrace is invented.
"""

from copy import deepcopy
from dataclasses import dataclass
from typing import Callable, Sequence

from v43.fhir.contracts import contract_for_criterion


@dataclass(frozen=True, slots=True)
class LegacyObservation:
    version: str
    decision: str
    resource_count: int
    service_hit: str


class LegacyAdapter:
    def __init__(self, version: str, emit_resources: Callable, replay_service: Callable):
        self.version = version
        self._emit_resources = emit_resources
        self._replay_service = replay_service

    def observe(self, criterion: str, patient_id: str, reports: Sequence[dict]) -> LegacyObservation:
        emitted = tuple(deepcopy(self._emit_resources(criterion, patient_id, deepcopy(reports))))
        contract = contract_for_criterion(criterion)
        matching = tuple(r for r in emitted
                         if r.get("resourceType") == contract.resource_type
                         and set(r.get("meta", {}).get("profile", ())) & set(contract.profiles))
        decision = "SATISFIED" if matching else "NOT_SATISFIED"
        service = str(self._replay_service(deepcopy(emitted), criterion)) if matching else "SERVICE_MISS"
        return LegacyObservation(self.version, decision, len(matching), service)
