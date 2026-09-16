from typing import Any

from .boolean import evaluate_all, evaluate_any
from .leaves import (evaluate_blocking_if_present, evaluate_explicit_absence,
                     evaluate_must_be_absent, evaluate_numeric, evaluate_relation,
                     evaluate_required_present, evaluate_subject, evaluate_temporal)
from .trace import DecisionTrace
from .trace import TraceNode
from .values import TruthValue, to_eligibility_result


def _get(value: Any, name: str, default: Any = None) -> Any:
    return value.get(name, default) if isinstance(value, dict) else getattr(value, name, default)


def _fact_state(store: Any, concept: str) -> Any:
    facts = store.find_facts(concept=concept)
    if not facts:
        return None
    states = {fact.state for fact in facts}
    from v43.clinical.models import AssertionState
    if AssertionState.PRESENT in states:
        return AssertionState.PRESENT
    if AssertionState.UNKNOWN in states:
        return AssertionState.UNKNOWN
    return AssertionState.ABSENT


def _leaf(node: Any, store: Any) -> tuple[TruthValue, str]:
    operator = str(_get(node, "operator", "unknown")).lower()
    state = _fact_state(store, str(_get(node, "concept", _get(node, "fact", ""))))
    if operator == "required_present":
        return ((TruthValue.UNKNOWN, "REQUIRED_MISSING") if state is None
                else (evaluate_required_present(state), "REQUIRED_EVALUATED"))
    if operator == "blocking_if_present":
        return ((TruthValue.TRUE, "BLOCKER_NOT_PROVEN") if state is None
                else (evaluate_blocking_if_present(state), "BLOCKER_EVALUATED"))
    if operator == "must_be_absent":
        return ((TruthValue.UNKNOWN, "ABSENCE_NOT_PROVEN") if state is None
                else (evaluate_must_be_absent(state), "ABSENCE_EVALUATED"))
    if operator == "explicit_absence_fact":
        return evaluate_explicit_absence(state), "EXPLICIT_ABSENCE_EVALUATED"
    if operator == "numeric_compare":
        facts = store.find_facts(concept=str(_get(node, "concept", _get(node, "fact", ""))))
        if not facts:
            return TruthValue.UNKNOWN, "NUMERIC_MISSING"
        results = [evaluate_numeric(fact.value, str(_get(node, "op")), _get(node, "value"),
                                    _get(node, "unit", fact.unit)) for fact in facts]
        return evaluate_any(results), "NUMERIC_EVALUATED"
    if operator == "patient_subject":
        return evaluate_subject(_get(node, "subject")), "SUBJECT_EVALUATED"
    if operator == "temporal_required":
        return evaluate_temporal(_get(node, "within_scope")), "TEMPORAL_EVALUATED"
    if operator == "relation_required":
        return evaluate_relation(store, str(_get(node, "source_node", _get(node, "a", ""))),
                                 str(_get(node, "target_node", _get(node, "b", ""))),
                                 str(_get(node, "relation_type")),
                                 closed_world=bool(_get(node, "closed_world", False))), "RELATION_EVALUATED"
    return TruthValue.UNKNOWN, "UNSUPPORTED_CONSTRAINT"


def execute(ir: Any, store: Any) -> DecisionTrace:
    """Evaluate typed constraint nodes against the clinical store and emit an immutable trace."""
    constraints = tuple(_get(ir, "constraints", ()) or ())
    nodes_by_id = {_get(node, "constraint_id", str(node)): node for node in constraints}
    trace_by_id: dict[str, TraceNode] = {}

    def evaluate(node_id: str) -> TraceNode:
        if node_id in trace_by_id:
            return trace_by_id[node_id]
        node = nodes_by_id.get(node_id, {"constraint_id": node_id, "operator": "unknown"})
        operator = str(_get(node, "operator", "unknown"))
        inputs = tuple(_get(node, "input_node_ids", _get(node, "inputs", ())) or ())
        if operator.upper() in {"AND", "OR"}:
            children = tuple(evaluate(str(item)) for item in inputs)
            result = (evaluate_all(child.result for child in children) if operator.upper() == "AND"
                      else evaluate_any(child.result for child in children))
            reason = f"BOOLEAN_{operator.upper()}_{result.value}"
        else:
            children = ()
            result, reason = _leaf(node, store)
        supporting = tuple(child.constraint_id for child in children if child.result is TruthValue.TRUE)
        blocking = tuple(child.constraint_id for child in children if child.result is TruthValue.FALSE)
        unknown = tuple(child.constraint_id for child in children if child.result is TruthValue.UNKNOWN)
        trace = TraceNode(str(node_id), operator, inputs, supporting, blocking, unknown,
                          f"{operator}({','.join(inputs)})", result, reason)
        trace_by_id[node_id] = trace
        return trace

    synthetic_root = False
    if constraints:
        requested_root = _get(ir, "root_constraint_id")
        if requested_root is None or requested_root not in nodes_by_id:
            requested_root = "root"
            synthetic_root = True
            nodes_by_id[requested_root] = {"constraint_id": requested_root, "operator": "AND",
                                           "input_node_ids": tuple(nodes_by_id)}
        root_node = evaluate(str(requested_root))
    else:
        root_node = evaluate("root")
    ordered = tuple(trace_by_id[node_id] for node_id in nodes_by_id if node_id in trace_by_id)
    classified = tuple(node for node in ordered
                       if not (synthetic_root and node.constraint_id == root_node.constraint_id))
    supporting = tuple(node.constraint_id for node in classified if node.result is TruthValue.TRUE)
    blocking = tuple(node.constraint_id for node in classified if node.result is TruthValue.FALSE)
    unknown = tuple(node.constraint_id for node in classified if node.result is TruthValue.UNKNOWN)
    root = root_node.result
    return DecisionTrace(str(_get(ir, "criterion_id", "unknown")), ordered, supporting, blocking,
                         unknown, root, to_eligibility_result(root), f"ROOT_{root.value}")
