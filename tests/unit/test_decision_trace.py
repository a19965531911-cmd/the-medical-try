from dataclasses import FrozenInstanceError
from types import SimpleNamespace

import pytest

from v43.clinical.models import AssertionState, ClinicalEvent, ClinicalFact, ClinicalRelation
from v43.clinical.store import ClinicalStore
from v43.constraints.executor import execute
from v43.constraints.trace import DecisionTrace, TraceNode
from v43.constraints.values import EligibilityResult, TruthValue, to_eligibility_result
from v43.ir.loader import load_criterion_ir
from v43.references import frozen_reference_paths


def test_root_truth_maps_to_eligibility_result():
    assert to_eligibility_result(TruthValue.TRUE) is EligibilityResult.SATISFIED
    assert to_eligibility_result(TruthValue.FALSE) is EligibilityResult.NOT_SATISFIED
    assert to_eligibility_result(TruthValue.UNKNOWN) is EligibilityResult.INSUFFICIENT_EVIDENCE


def test_decision_trace_is_immutable_and_classifies_nodes():
    support = TraceNode("age", "numeric", (), (), (), (), "52 >= 50", TruthValue.TRUE, "NUMERIC_PASS")
    unknown = TraceNode("relation", "relation_required", (), (), (), (), "missing", TruthValue.UNKNOWN, "RELATION_MISSING")
    trace = DecisionTrace(
        criterion_id="675",
        nodes=(support, unknown),
        supporting_node_ids=("age",),
        blocking_node_ids=(),
        unknown_node_ids=("relation",),
        root_result=TruthValue.UNKNOWN,
        eligibility_result=EligibilityResult.INSUFFICIENT_EVIDENCE,
        reason_code="ROOT_UNKNOWN",
    )
    assert trace.supporting_node_ids == ("age",)
    assert trace.result is TruthValue.UNKNOWN
    with pytest.raises(FrozenInstanceError):
        trace.reason_code = "changed"


def test_executor_derives_unknown_from_missing_constraint_not_external_root_truth():
    ir = SimpleNamespace(criterion_id="675", constraints=("missing",), root_truth=TruthValue.TRUE)
    trace = execute(ir, ClinicalStore(frozenset()))
    assert trace.root_result is TruthValue.UNKNOWN
    assert trace.eligibility_result is EligibilityResult.INSUFFICIENT_EVIDENCE
    assert trace.supporting_node_ids == ()
    assert trace.unknown_node_ids == ("missing",)
    assert tuple(node.constraint_id for node in trace.nodes) == ("missing", "root")


def test_executor_recursively_evaluates_typed_leaves_and_boolean_nodes():
    store = ClinicalStore(frozenset({"s1"}))
    store.add_fact(ClinicalFact("f1", "assertion", "diagnosis", None, None,
                               AssertionState.PRESENT, "patient", "current", "2026-01-01",
                               "s1", 0, 1.0, "test"))
    ir = SimpleNamespace(
        criterion_id="test",
        constraints=(
            {"constraint_id": "diagnosis", "operator": "required_present", "concept": "diagnosis"},
            {"constraint_id": "subject", "operator": "patient_subject", "subject": "patient"},
            {"constraint_id": "missing", "operator": "required_present", "concept": "missing"},
            {"constraint_id": "choice", "operator": "OR", "input_node_ids": ("subject", "missing")},
            {"constraint_id": "root", "operator": "AND", "input_node_ids": ("diagnosis", "choice")},
        ), root_constraint_id="root", root_truth=TruthValue.FALSE)
    trace = execute(ir, store)
    assert trace.root_result is TruthValue.TRUE
    assert trace.eligibility_result is EligibilityResult.SATISFIED
    assert trace.supporting_node_ids == ("diagnosis", "subject", "choice", "root")
    assert trace.blocking_node_ids == ()
    assert trace.unknown_node_ids == ("missing",)
    assert len(trace.nodes) == 5
    with pytest.raises(FrozenInstanceError):
        trace.nodes[-1].reason_code = "changed"


def test_executor_normalizes_loaded_frozen_ir_sections_into_executable_nodes():
    ir = load_criterion_ir(frozen_reference_paths()["criterion_ir_draft"], ("675",))["675"]
    ir.raw["root_truth"] = TruthValue.FALSE
    store = ClinicalStore(frozenset({"age-span", "diagnosis-span", "relation-span"}))
    store.add_fact(ClinicalFact(
        "age", "measurement", "patient_age", 52, "year", AssertionState.PRESENT,
        "patient", "current", "2026-01-01", "age-span", 0, 1.0, "test",
    ))
    store.add_fact(ClinicalFact(
        "diagnosis", "assertion", "herpes_zoster_diagnosis", None, None,
        AssertionState.PRESENT, "patient", "current", "2026-01-01",
        "diagnosis-span", 0, 1.0, "test",
    ))
    store.add_relation(ClinicalRelation(
        "location", "zoster_event", "head_face_site", "LOCATED_AT",
        AssertionState.PRESENT, ("relation-span",), (0,), 1.0, "test",
    ))

    trace = execute(ir, store)

    assert trace.root_result is TruthValue.TRUE
    assert trace.eligibility_result is EligibilityResult.SATISFIED
    assert trace.unknown_node_ids == ()


def _criterion_745_store(*, invasive=AssertionState.PRESENT,
                         relations=(("ventilation", "surgery", "POSTOPERATIVE_TO"),)):
    span_ids = {"surgery-span", "ventilation-span"}
    span_ids.update(f"relation-{index}" for index, _ in enumerate(relations))
    store = ClinicalStore(frozenset(span_ids))
    store.add_event(ClinicalEvent(
        "surgery", "Surgery", "completed_surgery", "completed", {}, "patient",
        "2026-01-01", None, "past", "perioperative-1", ("surgery-span",),
        (0,), 1.0, "test",
    ))
    store.add_event(ClinicalEvent(
        "ventilation", "MechanicalVentilation", "mechanical_ventilation", "active",
        {"invasive": invasive}, "patient", "2026-01-02", None, "current",
        "perioperative-1", ("ventilation-span",), (1,), 1.0, "test",
    ))
    for index, (source, target, relation_type) in enumerate(relations):
        store.add_relation(ClinicalRelation(
            f"relation-{index}", source, target, relation_type, AssertionState.PRESENT,
            (f"relation-{index}",), (1,), 1.0, "test",
        ))
    return store


@pytest.mark.parametrize("relations", [
    (("ventilation", "surgery", "POSTOPERATIVE_TO"),),
    (("ventilation", "surgery", "AFTER"),
     ("ventilation", "surgery", "SAME_EPISODE")),
])
def test_loaded_criterion_745_binds_typed_event_aliases_and_relations(relations):
    ir = load_criterion_ir(frozen_reference_paths()["criterion_ir_draft"], ("745",))["745"]

    trace = execute(ir, _criterion_745_store(relations=relations))

    assert trace.root_result is TruthValue.TRUE
    assert trace.eligibility_result is EligibilityResult.SATISFIED


@pytest.mark.parametrize(("invasive", "relations", "expected"), [
    (AssertionState.ABSENT, (("ventilation", "surgery", "POSTOPERATIVE_TO"),),
     EligibilityResult.NOT_SATISFIED),
    (AssertionState.PRESENT, (("surgery", "ventilation", "POSTOPERATIVE_TO"),),
     EligibilityResult.INSUFFICIENT_EVIDENCE),
    (AssertionState.PRESENT, (("unrelated", "surgery", "POSTOPERATIVE_TO"),),
     EligibilityResult.INSUFFICIENT_EVIDENCE),
])
def test_loaded_criterion_745_rejects_noninvasive_or_unbound_relations(
        invasive, relations, expected):
    ir = load_criterion_ir(frozen_reference_paths()["criterion_ir_draft"], ("745",))["745"]

    trace = execute(ir, _criterion_745_store(invasive=invasive, relations=relations))

    assert trace.eligibility_result is expected


def test_loaded_criterion_745_does_not_split_alias_binding_across_events():
    ir = load_criterion_ir(frozen_reference_paths()["criterion_ir_draft"], ("745",))["745"]
    store = _criterion_745_store(relations=(
        ("ventilation-2", "surgery", "POSTOPERATIVE_TO"),
    ))
    store.add_event(ClinicalEvent(
        "ventilation-2", "MechanicalVentilation", "mechanical_ventilation", "active",
        {"invasive": AssertionState.ABSENT}, "patient", "2026-01-03", None, "current",
        "perioperative-1", ("ventilation-span",), (1,), 1.0, "test",
    ))

    trace = execute(ir, store)

    assert trace.root_result is TruthValue.UNKNOWN
    assert trace.eligibility_result is EligibilityResult.INSUFFICIENT_EVIDENCE
