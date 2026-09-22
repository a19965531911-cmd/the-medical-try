from v43.clinical.models import AssertionState, ClinicalFact
from v43.clinical.store import ClinicalStore
from v43.temporal.models import TemporalView
from v43.temporal.reconcile import reconcile


def make_fact(fact_id, state, when, span_id):
    return ClinicalFact(fact_id, "assertion", "impairment", None, None, state, "patient",
                        None, when, span_id, 0, 1.0, "test")


def test_reconcile_derives_current_and_historical_without_changing_source_assertions():
    store = ClinicalStore(frozenset({"s1", "s2"}))
    store.add_fact(make_fact("f1", AssertionState.PRESENT, "2026-01-01", "s1"))
    store.add_fact(make_fact("f2", AssertionState.ABSENT, "2026-02-01", "s2"))
    views = reconcile(store, "impairment", "patient")
    assert views[TemporalView.CURRENT] == ("f2",)
    assert views[TemporalView.HISTORICAL] == ("f1",)
    assert views[TemporalView.RESOLVED] == ("f1",)
    assert [fact.state for fact in store.facts] == [AssertionState.PRESENT, AssertionState.ABSENT]


def test_same_time_opposing_assertions_are_conflict():
    store = ClinicalStore(frozenset({"s1", "s2"}))
    store.add_fact(make_fact("f1", AssertionState.PRESENT, "2026-01-01", "s1"))
    store.add_fact(make_fact("f2", AssertionState.ABSENT, "2026-01-01", "s2"))
    views = reconcile(store, "impairment", "patient")
    assert views[TemporalView.CONFLICT] == ("f1", "f2")
    assert views[TemporalView.CURRENT] == ()


def test_missing_or_unparseable_time_is_unknown():
    store = ClinicalStore(frozenset({"s1"}))
    store.add_fact(make_fact("f1", AssertionState.PRESENT, None, "s1"))
    assert reconcile(store, "impairment", "patient")[TemporalView.UNKNOWN] == ("f1",)

