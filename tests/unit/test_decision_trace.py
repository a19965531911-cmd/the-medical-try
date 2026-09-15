from dataclasses import FrozenInstanceError

import pytest

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
