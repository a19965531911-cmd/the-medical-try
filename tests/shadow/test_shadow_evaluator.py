from dataclasses import asdict
from types import SimpleNamespace

import pytest

from v43.constraints.values import EligibilityResult, TruthValue
from v43.fhir.service_replay import ServiceValidationResult
from v43.shadow.adapters import LegacyAdapter
from v43.shadow.evaluator import ShadowDecisionRecord, V43ShadowInput, compare_case


def _adapter(version, resources=(), service="SERVICE_MISS"):
    return LegacyAdapter(version, lambda criterion, patient, reports: resources,
                         lambda resources, criterion: service)


def _resource(profile, patient="p1"):
    return {"resourceType": "Observation", "meta": {"profile": [profile]},
            "subject": {"reference": "Patient/" + patient}}


def _v43(decision="SATISFIED", count=1, service="SERVICE_HIT", reason="ROOT_TRUE"):
    trace = SimpleNamespace(eligibility_result=EligibilityResult(decision), root_result=TruthValue.TRUE,
                            reason_code=reason, nodes=(), supporting_node_ids=(), blocking_node_ids=(),
                            unknown_node_ids=())
    run = SimpleNamespace(criterion_id="875", patient_run_id="private-patient", decision_trace=trace,
                          evidence_packet=SimpleNamespace(spans=(1, 2)), fact_count=1, event_count=0,
                          relation_count=0)
    return V43ShadowInput(run, count, service)


def test_legacy_decision_requires_criterion_matching_resources_and_does_not_mutate_inputs():
    reports = [{"text": "private"}]
    profile = "http://localhost:3456/api/terminology/Profile/cnwqk875-intracranialhypertension-profile"
    adapter = _adapter("2.4.3", (_resource(profile),))
    observed = adapter.observe("875", "p1", reports)
    assert observed.decision == "SATISFIED"
    assert observed.resource_count == 1
    assert observed.service_hit == "SERVICE_MISS"
    assert reports == [{"text": "private"}]
    assert not hasattr(observed, "decision_trace")


@pytest.mark.parametrize("old,new,count,service,expected", [
    ("SATISFIED", "SATISFIED", 1, "SERVICE_HIT", "UNCHANGED_POSITIVE"),
    ("NOT_SATISFIED", "NOT_SATISFIED", 0, "SERVICE_MISS", "UNCHANGED_NEGATIVE"),
    ("NOT_SATISFIED", "SATISFIED", 1, "SERVICE_HIT", "RECOVERY"),
    ("SATISFIED", "INSUFFICIENT_EVIDENCE", 0, "SERVICE_MISS", "REGRESSION"),
    ("SATISFIED", "SATISFIED", 2, "SERVICE_HIT", "FHIR_DELTA"),
    ("SATISFIED", "SATISFIED", 1, "SERVICE_MISS", "SERVICE_DELTA"),
])
def test_shadow_classifies_all_frozen_delta_types(old, new, count, service, expected):
    profile = "http://localhost:3456/api/terminology/Profile/cnwqk875-intracranialhypertension-profile"
    resources = (_resource(profile),) if old == "SATISFIED" else ()
    a243 = _adapter("2.4.3", resources, "SERVICE_HIT" if resources else "SERVICE_MISS")
    a422 = _adapter("4.2.2", resources, "SERVICE_HIT" if resources else "SERVICE_MISS")
    record = compare_case(a243, a422, _v43(new, count, service), reports=[])
    assert record.delta_type == expected
    assert record.reason_code
    assert set(asdict(record)) == set(ShadowDecisionRecord.__dataclass_fields__)
    assert "private-patient" not in str(asdict(record))


def test_adapter_is_observer_only_and_cannot_ensemble_a_legacy_positive_into_v43():
    profile = "http://localhost:3456/api/terminology/Profile/cnwqk875-intracranialhypertension-profile"
    old = _adapter("2.4.3", (_resource(profile),), "SERVICE_HIT")
    record = compare_case(old, old, _v43("INSUFFICIENT_EVIDENCE", 0, "SERVICE_MISS"), reports=[])
    assert record.v43_decision == "INSUFFICIENT_EVIDENCE"
    assert record.delta_type == "REGRESSION"


def test_shadow_case_id_is_anonymized_and_reproducible_for_same_run():
    adapter = _adapter("legacy")
    first = compare_case(adapter, adapter, _v43(), reports=[])
    second = compare_case(adapter, adapter, _v43(), reports=[])
    assert first.anonymized_case_id == second.anonymized_case_id
    assert "private-patient" not in first.anonymized_case_id
