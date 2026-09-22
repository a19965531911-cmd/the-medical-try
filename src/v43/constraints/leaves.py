import operator
from typing import Any

from v43.clinical.models import AssertionState
from v43.clinical.store import ClinicalStore

from .values import TruthValue


def evaluate_required_present(state: AssertionState) -> TruthValue:
    return {AssertionState.PRESENT: TruthValue.TRUE, AssertionState.ABSENT: TruthValue.FALSE,
            AssertionState.UNKNOWN: TruthValue.UNKNOWN}[state]


def evaluate_blocking_if_present(state: AssertionState) -> TruthValue:
    return TruthValue.FALSE if state is AssertionState.PRESENT else TruthValue.TRUE


def evaluate_must_be_absent(state: AssertionState) -> TruthValue:
    return {AssertionState.PRESENT: TruthValue.FALSE, AssertionState.ABSENT: TruthValue.TRUE,
            AssertionState.UNKNOWN: TruthValue.UNKNOWN}[state]


def evaluate_explicit_absence(state: AssertionState | None) -> TruthValue:
    if state is None:
        return TruthValue.UNKNOWN
    return {AssertionState.PRESENT: TruthValue.FALSE, AssertionState.ABSENT: TruthValue.TRUE,
            AssertionState.UNKNOWN: TruthValue.UNKNOWN}[state]


_OPERATORS = {">=": operator.ge, ">": operator.gt, "<=": operator.le, "<": operator.lt,
              "==": operator.eq, "!=": operator.ne}
_NUMERIC_UNITS = {"year", "years", "yr", "y", "month", "h", "ug/L", "ng/mL",
                  "umol/L", "mmol/L", "U/L", "ratio", "score", "mg", "g", "kg", "mmHg", "%"}


def evaluate_numeric(value: Any, op: str, threshold: Any, unit: str | None) -> TruthValue:
    if value is None or threshold is None or unit not in _NUMERIC_UNITS or op not in _OPERATORS:
        return TruthValue.UNKNOWN
    try:
        return TruthValue.TRUE if _OPERATORS[op](float(value), float(threshold)) else TruthValue.FALSE
    except (TypeError, ValueError):
        return TruthValue.UNKNOWN


def evaluate_subject(subject: str | None) -> TruthValue:
    if subject is None or subject.lower() == "unknown":
        return TruthValue.UNKNOWN
    return TruthValue.TRUE if subject.lower() == "patient" else TruthValue.FALSE


def evaluate_temporal(within_scope: bool | None) -> TruthValue:
    if within_scope is None:
        return TruthValue.UNKNOWN
    return TruthValue.TRUE if within_scope else TruthValue.FALSE


def evaluate_relation(store: ClinicalStore, a: str, b: str, relation_type: str,
                      *, closed_world: bool = False) -> TruthValue:
    matching = store.find_relations(source_node=a, target_node=b, relation_type=relation_type)
    if matching:
        states = {relation.state for relation in matching}
        if AssertionState.PRESENT in states:
            return TruthValue.TRUE
        if AssertionState.UNKNOWN in states:
            return TruthValue.UNKNOWN
        return TruthValue.FALSE
    between_nodes = store.find_relations(source_node=a, target_node=b)
    if any(r.state is AssertionState.PRESENT for r in between_nodes):
        return TruthValue.FALSE
    return TruthValue.FALSE if closed_world else TruthValue.UNKNOWN
