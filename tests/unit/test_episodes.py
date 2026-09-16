import pytest

from v43.clinical.models import AssertionState, ClinicalEvent, ClinicalRelation
from v43.episodes.linker import link_episode


def event(event_id, concept, when, report, span):
    return ClinicalEvent(event_id, "procedure", concept, "occurred", (), "patient", when,
                         None, None, None, (span,), (report,), 1.0, "test")


def relation(relation_id, source, target, kind, state=AssertionState.PRESENT):
    return ClinicalRelation(relation_id, source, target, kind, state,
                            ("sr",), (1,), 1.0, "test")


def test_745_rejects_patient_cooccurrence_for_old_surgery_and_current_ventilation():
    surgery = event("surgery", "Surgery", "2016-01-01", 0, "s1")
    ventilation = event("vent", "MechanicalVentilation", "2026-01-01", 1, "s2")
    episodes = link_episode((surgery, ventilation), (), "745")
    assert len(episodes) == 2
    assert all(len(episode.report_indices) == 1 for episode in episodes)


def test_745_links_postoperative_to_relation():
    surgery = event("surgery", "Surgery", "2026-01-01", 0, "s1")
    ventilation = event("vent", "MechanicalVentilation", "2026-01-02", 1, "s2")
    episodes = link_episode((surgery, ventilation),
                            (relation("r1", "vent", "surgery", "POSTOPERATIVE_TO"),), "745")
    assert len(episodes) == 1
    assert episodes[0].evidence_span_ids == ("s1", "s2", "sr")


def test_745_requires_after_and_same_episode_together():
    events = (event("surgery", "Surgery", "2026-01-01", 0, "s1"),
              event("vent", "MechanicalVentilation", "2026-01-02", 1, "s2"))
    after_only = link_episode(events, (relation("r1", "vent", "surgery", "AFTER"),), "745")
    both = link_episode(events, (relation("r1", "vent", "surgery", "AFTER"),
                                 relation("r2", "vent", "surgery", "SAME_EPISODE")), "745")
    assert len(after_only) == 2
    assert len(both) == 1


@pytest.mark.parametrize("relations", [
    (relation("r1", "surgery", "vent", "POSTOPERATIVE_TO"),),
    (relation("r1", "vent", "surgery", "BEFORE"),),
    (relation("r1", "vent", "surgery", "POSTOPERATIVE_TO", AssertionState.ABSENT),),
    (relation("r1", "other", "surgery", "POSTOPERATIVE_TO"),),
])
def test_745_rejects_reverse_unrelated_wrong_type_and_nonpresent_relations(relations):
    events = (event("surgery", "Surgery", "2026-01-01", 0, "s1"),
              event("vent", "MechanicalVentilation", "2026-01-02", 1, "s2"))
    assert len(link_episode(events, relations, "745")) == 2


def test_745_rejects_cross_patient_postoperative_relation():
    surgery = event("surgery", "Surgery", "2026-01-01", 0, "s1")
    ventilation = ClinicalEvent("vent", "procedure", "MechanicalVentilation", "occurred", (),
                                "different-patient", "2026-01-02", None, None, None,
                                ("s2",), (1,), 1.0, "test")
    assert len(link_episode((surgery, ventilation),
                            (relation("r1", "vent", "surgery", "POSTOPERATIVE_TO"),), "745")) == 2


def test_745_allows_same_episode_in_reverse_only_with_directed_after():
    events = (event("surgery", "Surgery", "2026-01-01", 0, "s1"),
              event("vent", "MechanicalVentilation", "2026-01-02", 1, "s2"))
    relations = (relation("r1", "vent", "surgery", "AFTER"),
                 relation("r2", "surgery", "vent", "SAME_EPISODE"))
    assert len(link_episode(events, relations, "745")) == 1
