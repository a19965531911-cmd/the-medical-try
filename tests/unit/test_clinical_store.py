from dataclasses import FrozenInstanceError

import pytest

from v43.clinical.models import (
    AssertionState,
    ClinicalEpisode,
    ClinicalEvent,
    ClinicalFact,
    ClinicalRelation,
)
from v43.clinical.store import ClinicalStore
from v43.retrieval.models import EvidencePacket, EvidenceSpan


def span(span_id: str = "s1") -> EvidenceSpan:
    return EvidenceSpan(span_id, "evidence", 0, None, "2026-01-01", 0, 8, "hash")


def fact(fact_id: str, state: AssertionState, when: str, span_id: str) -> ClinicalFact:
    return ClinicalFact(
        fact_id=fact_id,
        fact_type="assertion",
        concept="impairment",
        value=None,
        unit=None,
        state=state,
        subject="patient",
        temporality="current",
        clinical_time=when,
        evidence_span_id=span_id,
        report_index=0,
        confidence=1.0,
        source="deterministic",
    )


def test_store_from_packet_validates_provenance_and_models_have_no_raw_text():
    store = ClinicalStore.from_packet(EvidencePacket((span(),)))
    item = fact("f1", AssertionState.PRESENT, "2026-01-01", "s1")
    store.add_fact(item)
    assert store.get_fact("f1") == item
    assert "text" not in item.__dataclass_fields__
    with pytest.raises(FrozenInstanceError):
        item.concept = "changed"
    with pytest.raises(ValueError, match="unknown evidence span"):
        store.add_fact(fact("f2", AssertionState.PRESENT, "2026-01-02", "missing"))


def test_store_retains_present_and_absent_assertions_at_different_times():
    store = ClinicalStore(frozenset({"s1", "s2"}))
    earlier = fact("f1", AssertionState.PRESENT, "2026-01-01", "s1")
    later = fact("f2", AssertionState.ABSENT, "2026-02-01", "s2")
    store.add_fact(earlier)
    store.add_fact(later)
    assert store.find_facts(concept="impairment", subject="patient") == (earlier, later)


def test_store_rejects_duplicate_identity_time_and_never_overwrites_ids():
    store = ClinicalStore(frozenset({"s1"}))
    item = fact("f1", AssertionState.PRESENT, "2026-01-01", "s1")
    store.add_fact(item)
    with pytest.raises(ValueError, match="duplicate"):
        store.add_fact(fact("f2", AssertionState.PRESENT, "2026-01-01", "s1"))
    with pytest.raises(ValueError, match="already exists"):
        store.add_fact(fact("f1", AssertionState.ABSENT, "2026-02-01", "s1"))
    assert store.get_fact("f1") == item


def test_store_owns_events_relations_and_episodes_with_all_provenance_checked():
    store = ClinicalStore(frozenset({"s1", "s2"}))
    event = ClinicalEvent("e1", "procedure", "surgery", "occurred", (), "patient", "2026-01-01", None, "past", "ep1", ("s1",), (0,), 1.0, "parser")
    relation = ClinicalRelation("r1", "e2", "e1", "POSTOPERATIVE_TO", AssertionState.PRESENT, ("s2",), (1,), 0.9, "parser")
    episode = ClinicalEpisode("ep1", "perioperative", "2026-01-01", "2026-01-02", (0, 1), ("s1", "s2"), 0.8)
    store.add_event(event)
    store.add_relation(relation)
    store.add_episode(episode)
    assert store.get_event("e1") == event
    assert store.find_relations(source_node="e2", relation_type="POSTOPERATIVE_TO") == (relation,)
    assert store.get_episode("ep1") == episode

