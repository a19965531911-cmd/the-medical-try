"""Frozen FHIR/service mappings audited from the two legacy baselines."""

from dataclasses import dataclass


BASE = "http://localhost:3456/api/terminology/"

# These paths are deliberately recorded in production code and exercised by tests.
LEGACY_SOURCE_PATHS = (
    "CHIP2026_CP2_A_baseline_v2_4_3/evidence/a_49_FHIR_SERVICE_CODE.py",
    "CHIP2026_CP2_A_baseline_v2_4_3/evidence/a_24_FHIR_SERVICE_CODE.py",
    "CHIP2026_CP2_A_baseline_v2_4_3/evidence/a_31_FHIR_SERVICE_CODE.py",
    "CHIP2026_CP2_A_baseline_v2_4_3/evidence/a_37_FHIR_SERVICE_CODE.py",
    "CHIP2026_CP2_A_baseline_v2_4_3/src/library_factory.py",
    "CHIP2026_CP2_A_baseline_v2_4_3/analysis/fhir_forensic_raw.json",
    "CHIP2026_CP2_A_baseline_v4_2_2/evidence/a_49_FHIR_SERVICE_CODE.py",
    "CHIP2026_CP2_A_baseline_v4_2_2/evidence/a_24_FHIR_SERVICE_CODE.py",
    "CHIP2026_CP2_A_baseline_v4_2_2/evidence/a_31_FHIR_SERVICE_CODE.py",
    "CHIP2026_CP2_A_baseline_v4_2_2/evidence/a_37_FHIR_SERVICE_CODE.py",
    "CHIP2026_CP2_A_baseline_v4_2_2/src/library_factory.py",
    "CHIP2026_CP2_A_baseline_v4_2_2/analysis/fhir_forensic_raw.json",
    "CHIP2026_CP2_A_architecture_research_v4_3/analysis/A16_CRITERION_IR_DRAFT.yaml",
)


@dataclass(frozen=True, slots=True)
class ServiceContract:
    resource_type: str
    profiles: tuple[str, ...]
    code_system: str | None = None
    code: str | None = None
    value_system: str | None = None
    value_code: str | None = None


@dataclass(frozen=True, slots=True)
class CompiledContract:
    criterion_id: str
    resource_type: str
    profiles: tuple[str, ...]
    required_fields: tuple[str, ...]
    service: ServiceContract


def _profile(name: str) -> str:
    return BASE + "Profile/" + name


CONTRACTS = {
    "185": CompiledContract("185", "MedicationAdministration", (_profile("cnwqk185-chemotherapy-administration"),),
        ("status", "subject", "medicationCodeableConcept", "effectiveDateTime", "dosage", "extension"),
        ServiceContract("MedicationAdministration", (_profile("cnwqk185-chemotherapy-administration"),),
                        BASE + "CodeSystem/cnwqk185-custom-cs", "cnwqk185-drug-irinotecan")),
    "675": CompiledContract("675", "Condition", (_profile("cnwqk675-head-facial-herpes-zoster-condition"),),
        ("subject", "clinicalStatus", "verificationStatus", "code", "bodySite"),
        ServiceContract("Condition", (_profile("cnwqk675-head-facial-herpes-zoster-condition"),),
                        BASE + "CodeSystem/icd10", "B02.9")),
    "745": CompiledContract("745", "Procedure", (_profile("cnwqk745-postop-mechanical-ventilation"),),
        ("status", "subject", "code", "performedDateTime", "partOf"),
        ServiceContract("Procedure", (_profile("cnwqk745-postop-mechanical-ventilation"),),
                        BASE + "CodeSystem/cnwqk745-procedure-type-cs", "invasive_mechanical_ventilation")),
    "875": CompiledContract("875", "Observation", (
        _profile("cnwqk875-intracranialhypertension-profile"),
        _profile("cnwqk875-unconsciousness-profile")),
        ("status", "subject", "code", "effectiveDateTime", "valueCodeableConcept"),
        ServiceContract("Observation", (
            _profile("cnwqk875-intracranialhypertension-profile"),
            _profile("cnwqk875-unconsciousness-profile")),
            value_system=BASE + "CodeSystem/cnwqk875-presence-cs", value_code="present")),
}


def contract_for_criterion(criterion_id: str) -> CompiledContract:
    return CONTRACTS[str(criterion_id)]

