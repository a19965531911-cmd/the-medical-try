import json

import pytest

from v43.clinical.models import AssertionState, ClinicalEvent, ClinicalFact, ClinicalRelation
from v43.clinical.store import ClinicalStore
from v43.constraints.trace import DecisionTrace
from v43.constraints.values import EligibilityResult, TruthValue
from v43.fhir.compiler import compile_fhir
from v43.fhir.contracts import LEGACY_SOURCE_PATHS, contract_for_criterion
from v43.fhir.validator import validate_fhir


def _trace(criterion, result=EligibilityResult.SATISFIED):
    truth = TruthValue.TRUE if result is EligibilityResult.SATISFIED else TruthValue.FALSE
    return DecisionTrace(criterion, (), (), (), (), truth, result, "ROOT_TRUE")


def _store(criterion):
    store = ClinicalStore(frozenset({"s1", "s2"}))
    if criterion == "185":
        store.add_event(ClinicalEvent("med", "MedicationAdministration", "irinotecan", "occurred",
            {"first_use": AssertionState.PRESENT}, "patient", "2026-01-01T00:00:00Z", None,
            "CURRENT", "e1", ("s1",), (0,), 1.0, "deterministic"))
    elif criterion == "675":
        store.add_event(ClinicalEvent("dx", "Diagnosis", "herpes_zoster", "active", {}, "patient",
            "2026-01-01T00:00:00Z", None, "CURRENT", "e1", ("s1",), (0,), 1.0, "deterministic"))
        store.add_fact(ClinicalFact("site", "AnatomicalSite", "head_face_site", "face", None,
            AssertionState.PRESENT, "patient", "CURRENT", None, "s2", 0, 1.0, "deterministic"))
        store.add_relation(ClinicalRelation("loc", "dx", "site", "LOCATED_AT", AssertionState.PRESENT,
            ("s1", "s2"), (0,), 1.0, "deterministic"))
    elif criterion == "745":
        store.add_event(ClinicalEvent("surgery", "Surgery", "surgery", "occurred", {}, "patient",
            "2026-01-01T00:00:00Z", None, "CURRENT", "e1", ("s1",), (0,), 1.0, "deterministic"))
        store.add_event(ClinicalEvent("vent", "MechanicalVentilation", "mechanical_ventilation", "occurred",
            {"invasive": AssertionState.PRESENT}, "patient", "2026-01-01T01:00:00Z", None,
            "CURRENT", "e1", ("s2",), (0,), 1.0, "deterministic"))
        store.add_relation(ClinicalRelation("post", "vent", "surgery", "POSTOPERATIVE_TO",
            AssertionState.PRESENT, ("s1", "s2"), (0,), 1.0, "deterministic"))
    else:
        store.add_fact(ClinicalFact("icp", "Assertion", "intracranial_hypertension", True, None,
            AssertionState.PRESENT, "patient", "CURRENT", "2026-01-01T00:00:00Z", "s1", 0, 1.0,
            "deterministic"))
    return store


@pytest.mark.parametrize("criterion", ["185", "675", "745", "875"])
def test_compiler_only_emits_for_satisfied_trace_and_never_carries_raw_text(criterion):
    contract = contract_for_criterion(criterion)
    blocked = compile_fhir(_trace(criterion, EligibilityResult.NOT_SATISFIED), _store(criterion), contract, "Patient/p1")
    assert blocked.status == "NOT_COMPILED"
    assert blocked.resources == ()

    result = compile_fhir(_trace(criterion), _store(criterion), contract, "Patient/p1")
    assert result.status == "COMPILED"
    assert "raw_text" not in json.dumps(result.resources)
    assert validate_fhir(result, contract).structural_status == "VALID"


def test_legacy_contract_provenance_records_both_read_only_baselines_and_frozen_ir():
    assert any("baseline_v2_4_3" in path for path in LEGACY_SOURCE_PATHS)
    assert any("baseline_v4_2_2" in path for path in LEGACY_SOURCE_PATHS)
    assert any("A16_CRITERION_IR_DRAFT.yaml" in path for path in LEGACY_SOURCE_PATHS)


def test_structural_validator_rejects_wrong_subject_reference_independently():
    contract = contract_for_criterion("185")
    result = compile_fhir(_trace("185"), _store("185"), contract, "not-a-patient")
    validated = validate_fhir(result, contract)
    assert validated.structural_status == "INVALID"
    assert validated.reason_code == "FHIR_INVALID"

