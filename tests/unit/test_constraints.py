import itertools

import pytest

from v43.clinical.models import AssertionState
from v43.clinical.store import ClinicalStore
from v43.constraints.boolean import evaluate_and, evaluate_or
from v43.constraints.leaves import (
    evaluate_blocking_if_present,
    evaluate_must_be_absent,
    evaluate_numeric,
    evaluate_relation,
    evaluate_required_present,
    evaluate_subject,
    evaluate_temporal,
)
from v43.constraints.values import TruthValue


VALUES = (TruthValue.TRUE, TruthValue.FALSE, TruthValue.UNKNOWN)
AND = {
    (TruthValue.TRUE, TruthValue.TRUE): TruthValue.TRUE,
    (TruthValue.TRUE, TruthValue.FALSE): TruthValue.FALSE,
    (TruthValue.TRUE, TruthValue.UNKNOWN): TruthValue.UNKNOWN,
    (TruthValue.FALSE, TruthValue.TRUE): TruthValue.FALSE,
    (TruthValue.FALSE, TruthValue.FALSE): TruthValue.FALSE,
    (TruthValue.FALSE, TruthValue.UNKNOWN): TruthValue.FALSE,
    (TruthValue.UNKNOWN, TruthValue.TRUE): TruthValue.UNKNOWN,
    (TruthValue.UNKNOWN, TruthValue.FALSE): TruthValue.FALSE,
    (TruthValue.UNKNOWN, TruthValue.UNKNOWN): TruthValue.UNKNOWN,
}
OR = {
    (TruthValue.TRUE, TruthValue.TRUE): TruthValue.TRUE,
    (TruthValue.TRUE, TruthValue.FALSE): TruthValue.TRUE,
    (TruthValue.TRUE, TruthValue.UNKNOWN): TruthValue.TRUE,
    (TruthValue.FALSE, TruthValue.TRUE): TruthValue.TRUE,
    (TruthValue.FALSE, TruthValue.FALSE): TruthValue.FALSE,
    (TruthValue.FALSE, TruthValue.UNKNOWN): TruthValue.UNKNOWN,
    (TruthValue.UNKNOWN, TruthValue.TRUE): TruthValue.TRUE,
    (TruthValue.UNKNOWN, TruthValue.FALSE): TruthValue.UNKNOWN,
    (TruthValue.UNKNOWN, TruthValue.UNKNOWN): TruthValue.UNKNOWN,
}


@pytest.mark.parametrize("left,right", tuple(itertools.product(VALUES, repeat=2)))
def test_complete_kleene_and_table(left, right):
    assert evaluate_and(left, right) is AND[left, right]


@pytest.mark.parametrize("left,right", tuple(itertools.product(VALUES, repeat=2)))
def test_complete_kleene_or_table(left, right):
    assert evaluate_or(left, right) is OR[left, right]


@pytest.mark.parametrize(
    "state,required,blocking,absent",
    [
        (AssertionState.PRESENT, TruthValue.TRUE, TruthValue.FALSE, TruthValue.FALSE),
        (AssertionState.ABSENT, TruthValue.FALSE, TruthValue.TRUE, TruthValue.TRUE),
        (AssertionState.UNKNOWN, TruthValue.UNKNOWN, TruthValue.TRUE, TruthValue.UNKNOWN),
    ],
)
def test_presence_leaf_tables(state, required, blocking, absent):
    assert evaluate_required_present(state) is required
    assert evaluate_blocking_if_present(state) is blocking
    assert evaluate_must_be_absent(state) is absent


def test_numeric_missing_and_incompatible_unit_are_unknown():
    assert evaluate_numeric(None, ">=", 50, "years") is TruthValue.UNKNOWN
    assert evaluate_numeric(50, ">=", 50, "bananas") is TruthValue.UNKNOWN
    assert evaluate_numeric(50, ">=", 50, "years") is TruthValue.TRUE


def test_subject_relation_and_temporal_unknowns_are_conservative():
    store = ClinicalStore(frozenset())
    assert evaluate_subject(None) is TruthValue.UNKNOWN
    assert evaluate_subject("family") is TruthValue.FALSE
    assert evaluate_relation(store, "a", "b", "LOCATED_AT") is TruthValue.UNKNOWN
    assert evaluate_temporal(None) is TruthValue.UNKNOWN


def test_generic_negation_evaluator_is_not_exposed():
    import v43.constraints.boolean as boolean

    assert not hasattr(boolean, "evaluate_not")
