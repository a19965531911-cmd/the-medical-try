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
    "165": CompiledContract("165", "Procedure", (_profile("cnwqk165-chemotherapy-history"),),
        ("status", "subject", "code", "extension"), ServiceContract("Procedure", (_profile("cnwqk165-chemotherapy-history"),))),
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
    "265": CompiledContract("265", "Observation", (_profile("cnwqk265-serum-cardiac-troponin-observation"),),
        ("status", "subject", "code", "effectiveDateTime", "valueQuantity"), ServiceContract("Observation", (_profile("cnwqk265-serum-cardiac-troponin-observation"),))),
    "485": CompiledContract("485", "Observation", (_profile("cnwqk485-popq-assessment"),),
        ("status", "subject", "code", "valueCodeableConcept"), ServiceContract("Observation", (_profile("cnwqk485-popq-assessment"),), value_system=BASE+"CodeSystem/cnwqk485-popq-grade-cs", value_code="III")),
    "555": CompiledContract("555", "Procedure", (_profile("cnwqk555-SurgeryHistoryProfile"),),
        ("status", "subject", "code", "performedDateTime"), ServiceContract("Procedure", (_profile("cnwqk555-SurgeryHistoryProfile"),))),
    "565": CompiledContract("565", "Observation", (_profile("cnwqk565-symptomobservation"),),
        ("status", "subject", "code", "extension"), ServiceContract("Observation", (_profile("cnwqk565-symptomobservation"),))),
    "615": CompiledContract("615", "Observation", (
        _profile("cnwqk615-pathological-t-stage-observation"),
        _profile("cnwqk615-resection-margin-status-observation"),
        _profile("cnwqk615-pathological-n-stage-observation"),
        _profile("cnwqk615-gleason-score-observation"),
        _profile("cnwqk615-psa-observation")),
        ("status", "subject", "code"), ServiceContract("Observation", (
            _profile("cnwqk615-pathological-t-stage-observation"),
            _profile("cnwqk615-resection-margin-status-observation"),
            _profile("cnwqk615-pathological-n-stage-observation"),
            _profile("cnwqk615-gleason-score-observation"),
            _profile("cnwqk615-psa-observation")))),
    "635": CompiledContract("635", "Observation", (_profile("cnwqk635-LaboratoryExaminationProfile"),),
        ("status", "subject", "code", "valueQuantity", "referenceRange"), ServiceContract("Observation", (_profile("cnwqk635-LaboratoryExaminationProfile"),))),
    "735": CompiledContract("735", "Condition", (BASE+"StructureDefinition/cnwqk735-nonneoplasm-disease-stage",),
        ("subject", "code", "clinicalStatus"), ServiceContract("Condition", (BASE+"StructureDefinition/cnwqk735-nonneoplasm-disease-stage",))),
    "755": CompiledContract("755", "Procedure", (_profile("cnwqk755-MechanicalVentilationProcedure"),),
        ("status", "subject", "code", "performedPeriod"), ServiceContract("Procedure", (_profile("cnwqk755-MechanicalVentilationProcedure"),))),
    "805": CompiledContract("805", "Observation", (_profile("cnwqk805-SmokingStatusObservation"),),
        ("status", "subject", "code", "valueCodeableConcept"), ServiceContract("Observation", (_profile("cnwqk805-SmokingStatusObservation"),))),
    "835": CompiledContract("835", "Observation", (_profile("cnwqk835-OrganOrTissueStatus"),),
        ("status", "subject", "code", "valueCodeableConcept"), ServiceContract("Observation", (_profile("cnwqk835-OrganOrTissueStatus"),))),
    "855": CompiledContract("855", "Observation", (_profile("cnwqk855-serum-creatinine-observation"),),
        ("status", "subject", "code", "valueQuantity"), ServiceContract("Observation", (_profile("cnwqk855-serum-creatinine-observation"),))),
}


def contract_for_criterion(criterion_id: str) -> CompiledContract:
    return CONTRACTS[str(criterion_id)]
