from dataclasses import dataclass
from itertools import product
import re
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


@dataclass(frozen=True)
class _ExecutableNode:
    constraint_id: str
    operator: str
    input_node_ids: tuple[str, ...] = ()
    concept: str = ""
    op: str = ""
    value: Any = None
    unit: str | None = None
    source_node: str = ""
    target_node: str = ""
    relation_type: str = ""
    event_type: str = ""
    event_alias: str = ""
    event_attribute: str = ""


def _split_expression(expression: str, operator: str) -> tuple[str, ...]:
    depth = 0
    start = 0
    parts: list[str] = []
    marker = f" {operator} "
    index = 0
    while index < len(expression):
        char = expression[index]
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif depth == 0 and expression.startswith(marker, index):
            parts.append(expression[start:index].strip())
            index += len(marker)
            start = index
            continue
        index += 1
    if parts:
        parts.append(expression[start:].strip())
    return tuple(parts)


def _strip_group(expression: str) -> str:
    expression = expression.strip()
    while expression.startswith("(") and expression.endswith(")"):
        depth = 0
        closes_at_end = False
        for index, char in enumerate(expression):
            depth += char == "("
            depth -= char == ")"
            if depth == 0:
                closes_at_end = index == len(expression) - 1
                break
        if not closes_at_end:
            break
        expression = expression[1:-1].strip()
    return expression


def _nodes_from_raw(raw: dict[str, Any]) -> tuple[tuple[_ExecutableNode, ...], str | None]:
    expression = str(raw.get("logical_expression", "")).strip()
    if not expression:
        return (), None
    numeric_names = tuple((raw.get("constraint_semantics") or {}).get("numeric_compare", ()))
    numeric_by_name = dict(zip(numeric_names, raw.get("numeric_constraints") or ()))
    nodes: list[_ExecutableNode] = []

    def parse(fragment: str) -> str:
        fragment = _strip_group(fragment)
        for boolean_operator in ("OR", "AND"):
            parts = _split_expression(fragment, boolean_operator)
            if parts:
                inputs = tuple(parse(part) for part in parts)
                node_id = f"boolean_{len(nodes) + 1}"
                nodes.append(_ExecutableNode(node_id, boolean_operator, inputs))
                return node_id
        match = re.fullmatch(r"([A-Za-z_]+)\((.*)\)", fragment)
        if match is None:
            node_id = f"constraint_{len(nodes) + 1}"
            nodes.append(_ExecutableNode(node_id, "unknown"))
            return node_id
        operator, arguments_text = match.groups()
        arguments = tuple(item.strip() for item in arguments_text.split(","))
        node_id = f"constraint_{len(nodes) + 1}"
        if operator == "numeric_compare":
            numeric = numeric_by_name.get(arguments[0], {})
            nodes.append(_ExecutableNode(
                node_id, operator, concept=str(numeric.get("fact", arguments[0])),
                op=str(numeric.get("op", "")), value=numeric.get("value"),
                unit=numeric.get("unit"),
            ))
        elif operator == "relation_required" and len(arguments) == 3:
            nodes.append(_ExecutableNode(
                node_id, operator, source_node=arguments[0], target_node=arguments[1],
                relation_type=arguments[2],
            ))
        else:
            concept = arguments[0] if arguments else ""
            declaration = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)\s+([A-Za-z_][A-Za-z0-9_]*)", concept)
            attribute = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)", concept)
            nodes.append(_ExecutableNode(
                node_id, operator, concept=concept,
                event_type=declaration.group(1) if declaration else "",
                event_alias=declaration.group(2) if declaration else (attribute.group(1) if attribute else ""),
                event_attribute=attribute.group(2) if attribute else "",
            ))
        return node_id

    root_id = parse(expression)
    return tuple(nodes), root_id


def _execution_nodes(ir: Any) -> tuple[tuple[Any, ...], str | None]:
    constraints = tuple(_get(ir, "constraints", ()) or ())
    if constraints:
        return constraints, _get(ir, "root_constraint_id")
    raw = _get(ir, "raw")
    if isinstance(raw, dict):
        return _nodes_from_raw(raw)
    return (), None


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


def _attribute_state(value: Any) -> Any:
    from v43.clinical.models import AssertionState
    if isinstance(value, AssertionState):
        return value
    if value is True or (isinstance(value, str) and value.upper() == "PRESENT"):
        return AssertionState.PRESENT
    if value is False or (isinstance(value, str) and value.upper() == "ABSENT"):
        return AssertionState.ABSENT
    return AssertionState.UNKNOWN


def _event_bindings(ir: Any, constraints: tuple[Any, ...],
                    store: Any) -> tuple[dict[str, str | None], ...]:
    declarations: dict[str, str] = {}
    raw = _get(ir, "raw", {})
    for node in constraints:
        alias = str(_get(node, "event_alias", ""))
        event_type = str(_get(node, "event_type", ""))
        if alias and event_type:
            declarations[alias] = event_type
    referenced = {
        str(value) for node in constraints
        for value in (_get(node, "source_node", ""), _get(node, "target_node", ""),
                      _get(node, "event_alias", "")) if value
    }
    for entity in raw.get("entities", ()) if isinstance(raw, dict) else ():
        alias = str(entity.get("id", ""))
        event_type = str(entity.get("type", ""))
        if alias in referenced and event_type:
            declarations[alias] = event_type
    if not declarations:
        return ({},)
    required_subject = None
    if isinstance(raw, dict):
        required_subject = (raw.get("subject_constraints") or {}).get("subject")
    aliases = tuple(declarations)
    candidates = tuple(
        tuple(event.event_id for event in store.events
              if event.event_type == declarations[alias]
              and (required_subject is None or event.subject == required_subject)) or (None,)
        for alias in aliases
    )
    environments = []
    for values in product(*candidates):
        events = tuple(store.get_event(event_id) for event_id in values if event_id is not None)
        subjects = {event.subject for event in events if event.subject is not None}
        if len(subjects) <= 1:
            environments.append(dict(zip(aliases, values)))
    return tuple(environments) or ({alias: None for alias in aliases},)


def _bound_relation(store: Any, bindings: dict[str, str | None], source: str,
                    target: str, relation_type: str, closed_world: bool) -> TruthValue:
    a = bindings.get(source, source)
    b = bindings.get(target, target)
    if a is None or b is None:
        return TruthValue.FALSE if closed_world else TruthValue.UNKNOWN
    return evaluate_relation(store, a, b, relation_type, closed_world=closed_world)


def _leaf(node: Any, store: Any,
          bindings: dict[str, str | None]) -> tuple[TruthValue, str]:
    operator = str(_get(node, "operator", "unknown")).lower()
    state = _fact_state(store, str(_get(node, "concept", _get(node, "fact", ""))))
    if operator == "required_present":
        alias = str(_get(node, "event_alias", ""))
        event_type = str(_get(node, "event_type", ""))
        attribute = str(_get(node, "event_attribute", ""))
        if event_type:
            return ((TruthValue.TRUE, "REQUIRED_EVENT_PRESENT") if bindings.get(alias) is not None
                    else (TruthValue.UNKNOWN, "REQUIRED_EVENT_MISSING"))
        if alias and attribute:
            event_id = bindings.get(alias)
            event = store.get_event(event_id) if event_id is not None else None
            if event is None:
                return TruthValue.UNKNOWN, "REQUIRED_EVENT_MISSING"
            result = evaluate_required_present(_attribute_state(
                event.attributes.get(attribute) if isinstance(event.attributes, dict) else None
            ))
            return result, "REQUIRED_EVENT_ATTRIBUTE_EVALUATED"
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
        return _bound_relation(
            store, bindings, str(_get(node, "source_node", _get(node, "a", ""))),
            str(_get(node, "target_node", _get(node, "b", ""))),
            str(_get(node, "relation_type")), bool(_get(node, "closed_world", False)),
        ), "RELATION_EVALUATED"
    return TruthValue.UNKNOWN, "UNSUPPORTED_CONSTRAINT"


def execute(ir: Any, store: Any) -> DecisionTrace:
    """Evaluate typed constraint nodes against the clinical store and emit an immutable trace."""
    constraints, normalized_root = _execution_nodes(ir)
    environments = _event_bindings(ir, constraints, store)
    nodes_by_id = {_get(node, "constraint_id", str(node)): node for node in constraints}

    synthetic_root = False
    if constraints:
        requested_root = _get(ir, "root_constraint_id", normalized_root)
        if requested_root is None or requested_root not in nodes_by_id:
            requested_root = "root"
            synthetic_root = True
            nodes_by_id[requested_root] = {"constraint_id": requested_root, "operator": "AND",
                                           "input_node_ids": tuple(nodes_by_id)}
    else:
        requested_root = "root"

    traces_by_environment: list[dict[str, TraceNode]] = []
    for bindings in environments:
        trace_by_id: dict[str, TraceNode] = {}

        def evaluate(node_id: str) -> TraceNode:
            if node_id in trace_by_id:
                return trace_by_id[node_id]
            node = nodes_by_id.get(node_id, {"constraint_id": node_id, "operator": "unknown"})
            operator = str(_get(node, "operator", "unknown"))
            inputs = tuple(_get(node, "input_node_ids", _get(node, "inputs", ())) or ())
            if operator.upper() in {"AND", "OR"}:
                children = tuple(evaluate(str(item)) for item in inputs)
                result = (evaluate_all(child.result for child in children)
                          if operator.upper() == "AND"
                          else evaluate_any(child.result for child in children))
                reason = f"BOOLEAN_{operator.upper()}_{result.value}"
            else:
                children = ()
                result, reason = _leaf(node, store, bindings)
            supporting = tuple(child.constraint_id for child in children
                               if child.result is TruthValue.TRUE)
            blocking = tuple(child.constraint_id for child in children
                             if child.result is TruthValue.FALSE)
            unknown = tuple(child.constraint_id for child in children
                            if child.result is TruthValue.UNKNOWN)
            trace = TraceNode(str(node_id), operator, inputs, supporting, blocking, unknown,
                              f"{operator}({','.join(inputs)})", result, reason)
            trace_by_id[node_id] = trace
            return trace

        evaluate(str(requested_root))
        traces_by_environment.append(trace_by_id)

    trace_by_id: dict[str, TraceNode] = {}

    def aggregate(node_id: str) -> TraceNode:
        if node_id in trace_by_id:
            return trace_by_id[node_id]
        candidates = tuple(trace[node_id] for trace in traces_by_environment if node_id in trace)
        if not candidates:
            raise KeyError(node_id)
        exemplar = candidates[0]
        result = evaluate_any(candidate.result for candidate in candidates)
        inputs = exemplar.input_node_ids
        supporting = tuple(item for item in inputs
                           if aggregate(item).result is TruthValue.TRUE)
        blocking = tuple(item for item in inputs
                         if aggregate(item).result is TruthValue.FALSE)
        unknown = tuple(item for item in inputs
                        if aggregate(item).result is TruthValue.UNKNOWN)
        reason = (f"BOOLEAN_{exemplar.operator.upper()}_{result.value}"
                  if exemplar.operator.upper() in {"AND", "OR"} else exemplar.reason_code)
        trace_by_id[node_id] = TraceNode(
            exemplar.constraint_id, exemplar.operator, inputs, supporting, blocking, unknown,
            exemplar.normalized_calculation, result, reason,
        )
        return trace_by_id[node_id]

    root_node = aggregate(str(requested_root))
    ordered = tuple(trace_by_id[node_id] for node_id in nodes_by_id if node_id in trace_by_id)
    classified = tuple(node for node in ordered
                       if not (synthetic_root and node.constraint_id == root_node.constraint_id))
    supporting = tuple(node.constraint_id for node in classified if node.result is TruthValue.TRUE)
    blocking = tuple(node.constraint_id for node in classified if node.result is TruthValue.FALSE)
    unknown = tuple(node.constraint_id for node in classified if node.result is TruthValue.UNKNOWN)
    root = root_node.result
    return DecisionTrace(str(_get(ir, "criterion_id", "unknown")), ordered, supporting, blocking,
                         unknown, root, to_eligibility_result(root), f"ROOT_{root.value}")
