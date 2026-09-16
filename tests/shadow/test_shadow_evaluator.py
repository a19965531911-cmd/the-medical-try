from dataclasses import asdict
from importlib import import_module
from types import SimpleNamespace

import pytest

from v43.constraints.values import EligibilityResult, TruthValue
from v43.clinical.store import ClinicalStore
from v43.fhir.compiler import compile_fhir
from v43.fhir.contracts import contract_for_criterion
from v43.fhir.service_replay import ServiceValidationResult
from v43.fhir.service_replay import replay_service
from v43.fhir.validator import validate_fhir
from v43.ir.loader import load_criterion_ir
from v43.references import CRITERION_IDS, frozen_reference_paths
from v43.retrieval.retriever import retrieve
from v43.runtime import RuntimeServices, evaluate_criterion
from v43.shadow.adapters import LegacyAdapter
from v43.shadow.evaluator import ShadowDecisionRecord, V43ShadowInput, compare_case


ALL_CASES = {
    "165": "转入我院前于当地医院完成2周期化疗",
    "185": "首次接受伊立替康化疗",
    "265": "术前cTnI 0.08 μg/L",
    "485": "盆腔器官脱垂，POP-Q III期",
    "555": "3个月前行胆囊切除术",
    "565": "目前严重腹泻",
    "615": "Gleason评分8分",
    "635": "AST 30 U/L上限40，ALT 50 U/L上限40，BUN 12 mmol/L上限9，Cr 180 umol/L上限100",
    "675": "患者70岁，确诊头面部带状疱疹",
    "735": "活动性乙型肝炎",
    "745": "术后行有创机械通气",
    "755": "机械通气持续30小时",
    "805": "目前每日吸烟",
    "835": "目前凝血功能异常",
    "855": "Scr 120 μmol/L，BUN 7 mmol/L，ALT 30 U/L上限40，AST 25 U/L上限40",
    "875": "目前意识不清",
}


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


@pytest.mark.parametrize("criterion", CRITERION_IDS)
def test_all_sixteen_criteria_run_three_version_shadow_without_ensemble(criterion):
    text = ALL_CASES[criterion]
    reports = [{"text": text, "timestamp": "2026-01-01", "fixture_source": "synthetic"}]
    temporal_policy = "EVER_PRESENT" if criterion == "875" else "REVIEW_REQUIRED"
    run = evaluate_criterion(criterion, "p1", reports, RuntimeServices(None, 1.0, temporal_policy))

    ir = load_criterion_ir(frozen_reference_paths()["criterion_ir_draft"], (criterion,))[criterion]
    packet = retrieve(ir, reports)
    store = ClinicalStore.from_packet(packet)
    facts, events, relations = import_module(f"v43.criteria.c{criterion}").extract(packet)
    for item in facts:
        store.add_fact(item)
    for item in events:
        store.add_event(item)
    for item in relations:
        store.add_relation(item)

    contract = contract_for_criterion(criterion)
    validated = validate_fhir(compile_fhir(run.decision_trace, store, contract, "Patient/p1"), contract)
    service = replay_service(validated.resources, contract.service, "fixture://fhir", {"p1": "doc"})

    def legacy(version):
        return LegacyAdapter(version, lambda *_: validated.resources,
                             lambda resources, requested: replay_service(
                                 tuple(resources), contract_for_criterion(requested).service,
                                 "fixture://fhir", {"p1": "doc"}).status)

    record = compare_case(legacy("2.4.3"), legacy("4.2.2"),
                          V43ShadowInput(run, len(validated.resources), service.status), reports)
    assert record.criterion == criterion
    assert record.v243_decision == "SATISFIED"
    assert record.v422_decision == "SATISFIED"
    assert record.v43_decision == "SATISFIED"
    assert record.v243_service_hit == "SERVICE_HIT"
    assert record.v422_service_hit == "SERVICE_HIT"
    assert record.v43_service_hit == "SERVICE_HIT"
    expected_delta = "FHIR_DELTA" if criterion == "745" else "UNCHANGED_POSITIVE"
    assert record.delta_type == expected_delta
