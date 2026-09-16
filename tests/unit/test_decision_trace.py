from dataclasses import FrozenInstanceError
from types import SimpleNamespace

import pytest

from v43.clinical.models import AssertionState, ClinicalFact
from v43.clinical.store import ClinicalStore
from v43.constraints.executor import execute
from v43.constraints.trace import DecisionTrace, TraceNode
from v43.constraints.values import EligibilityResult, TruthValue, to_eligibility_result


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
