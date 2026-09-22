from collections.abc import Iterable

from .values import TruthValue


def evaluate_and(left: TruthValue, right: TruthValue) -> TruthValue:
    if TruthValue.FALSE in (left, right):
        return TruthValue.FALSE
    if TruthValue.UNKNOWN in (left, right):
        return TruthValue.UNKNOWN
    return TruthValue.TRUE


def evaluate_or(left: TruthValue, right: TruthValue) -> TruthValue:
    if TruthValue.TRUE in (left, right):
        return TruthValue.TRUE
    if TruthValue.UNKNOWN in (left, right):
        return TruthValue.UNKNOWN
    return TruthValue.FALSE


def evaluate_all(values: Iterable[TruthValue]) -> TruthValue:
    result = TruthValue.TRUE
    for value in values:
        result = evaluate_and(result, value)
    return result


def evaluate_any(values: Iterable[TruthValue]) -> TruthValue:
    result = TruthValue.FALSE
    for value in values:
        result = evaluate_or(result, value)
    return result
