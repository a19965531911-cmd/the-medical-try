from dataclasses import dataclass

from .values import EligibilityResult, TruthValue


@dataclass(frozen=True, slots=True)
class TraceNode:
    constraint_id: str
    operator: str
    input_node_ids: tuple[str, ...]
    supporting_node_ids: tuple[str, ...]
    blocking_node_ids: tuple[str, ...]
    unknown_node_ids: tuple[str, ...]
    normalized_calculation: str
    result: TruthValue
    reason_code: str


@dataclass(frozen=True, slots=True)
class DecisionTrace:
    criterion_id: str
    nodes: tuple[TraceNode, ...]
    supporting_node_ids: tuple[str, ...]
    blocking_node_ids: tuple[str, ...]
    unknown_node_ids: tuple[str, ...]
    root_result: TruthValue
    eligibility_result: EligibilityResult
    reason_code: str

    @property
    def result(self) -> TruthValue:
        return self.root_result
