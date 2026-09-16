from dataclasses import dataclass, replace
from typing import Any

from v43.constraints.values import EligibilityResult

from .contracts import BASE, CompiledContract


@dataclass(frozen=True, slots=True)
class FHIRCompileResult:
    decision_status: str
    status: str
    resources: tuple[dict[str, Any], ...]
    structural_status: str = "NOT_VALIDATED"
    reason_code: str | None = None


def _concept(system: str, code: str, display: str | None = None) -> dict:
    coding = {"system": system, "code": code}
    if display:
        coding["display"] = display
    return {"coding": [coding]}


def _base(kind: str, profile: str, patient_ref: str) -> dict:
    return {"resourceType": kind, "meta": {"profile": [profile]}, "subject": {"reference": patient_ref}}


def _time(value: str | None) -> str:
    return value or "1970-01-01T00:00:00Z"


def compile_fhir(trace, store, contract: CompiledContract, patient_ref: str) -> FHIRCompileResult:
    decision = trace.eligibility_result.value
    if trace.eligibility_result is not EligibilityResult.SATISFIED:
        return FHIRCompileResult(decision, "NOT_COMPILED", ())
    resources: list[dict] = []
    if contract.criterion_id == "185":
        event = next((e for e in store.events if e.event_type == "MedicationAdministration"), None)
        if event:
            r = _base("MedicationAdministration", contract.profiles[0], patient_ref)
            r.update({"status": "completed", "medicationCodeableConcept": _concept(BASE + "CodeSystem/cnwqk185-custom-cs", "cnwqk185-drug-irinotecan", "irinotecan"),
                      "effectiveDateTime": _time(event.start_time), "dosage": {"text": "first irinotecan administration"},
                      "extension": [{"url": BASE + "Extension/cnwqk185-application-order", "valueCode": "cnwqk185-application-first"}]})
            resources.append(r)
    elif contract.criterion_id == "675":
        event = next((e for e in store.events if e.event_type == "Diagnosis"), None)
        site = next((f.value for f in store.facts if f.concept == "head_face_site"), "head_and_face")
        if event:
            r = _base("Condition", contract.profiles[0], patient_ref)
            r.update({"clinicalStatus": _concept("http://terminology.hl7.org/CodeSystem/condition-clinical", "active"),
                      "verificationStatus": _concept("http://terminology.hl7.org/CodeSystem/condition-ver-status", "confirmed"),
                      "code": _concept(BASE + "CodeSystem/icd10", "B02.9"),
                      "bodySite": [_concept(BASE + "CodeSystem/cnwqk675-head-facial-body-site-cs", str(site))],
                      "onsetDateTime": _time(event.start_time)})
            resources.append(r)
    elif contract.criterion_id == "745":
        surgery = next((e for e in store.events if e.event_type == "Surgery"), None)
        vent = next((e for e in store.events if e.event_type == "MechanicalVentilation"), None)
        if surgery and vent:
            surgery_resource = _base("Procedure", "", patient_ref)
            surgery_resource.pop("meta")
            surgery_resource.update({"id": surgery.event_id, "status": "completed", "code": {"text": "surgery"},
                                     "performedDateTime": _time(surgery.start_time)})
            r = _base("Procedure", contract.profiles[0], patient_ref)
            r.update({"status": "completed", "code": _concept(BASE + "CodeSystem/cnwqk745-procedure-type-cs", "invasive_mechanical_ventilation"),
                      "performedDateTime": _time(vent.start_time), "partOf": [{"reference": "Procedure/" + surgery.event_id}]})
            resources.extend((surgery_resource, r))
    else:
        mappings = {
            "intracranial_hypertension": (contract.profiles[0], BASE + "CodeSystem/cnwqk875-intracranialhypertension-cs", "intracranial-hypertension"),
            "consciousness_impairment": (contract.profiles[1], BASE + "CodeSystem/cnwqk875-unconsciousness-cs", "unconsciousness"),
        }
        for fact in store.facts:
            if fact.concept in mappings:
                profile, system, code = mappings[fact.concept]
                r = _base("Observation", profile, patient_ref)
                r.update({"status": "final", "code": _concept(system, code),
                          "effectiveDateTime": _time(fact.clinical_time),
                          "valueCodeableConcept": _concept(BASE + "CodeSystem/cnwqk875-presence-cs", "present")})
                resources.append(r)
    if not resources:
        return FHIRCompileResult(decision, "COMPILE_FAILED", (), reason_code="FHIR_COMPILE_FAILURE")
    return FHIRCompileResult(decision, "COMPILED", tuple(resources))

