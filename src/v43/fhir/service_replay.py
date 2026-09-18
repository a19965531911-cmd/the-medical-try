from dataclasses import dataclass
from typing import Mapping

from .contracts import ServiceContract


@dataclass(frozen=True, slots=True)
class ServiceValidationResult:
    status: str
    matched_patient_ids: tuple[str, ...]
    reason_code: str | None = None


def _codings(resource: dict, path: str) -> list[dict]:
    value = resource
    for part in path.split("."):
        value = value.get(part, {}) if isinstance(value, dict) else {}
    return value if isinstance(value, list) else []


def replay_service(resources: tuple[dict, ...], contract: ServiceContract, base_url: str,
                   identity: Mapping[str, str]) -> ServiceValidationResult:
    if any(profile.endswith("cnwqk635-LaboratoryExaminationProfile") for profile in contract.profiles):
        patient_labs: dict[str, set[str]] = {}
        for resource in resources:
            if resource.get("resourceType") != "Observation":
                continue
            if not set(resource.get("meta", {}).get("profile", ())) & set(contract.profiles):
                continue
            patient = resource.get("subject", {}).get("reference", "").removeprefix("Patient/")
            code = next((coding.get("code") for coding in _codings(resource, "code.coding")), None)
            value = resource.get("valueQuantity", {}).get("value")
            high = (resource.get("referenceRange") or [{}])[0].get("high", {}).get("value")
            try:
                qualifies = float(value) <= 2 * float(high) and float(high) > 0
            except (TypeError, ValueError):
                qualifies = False
            if patient in identity and code in {"AST", "ALT", "BUN", "Cr"} and qualifies:
                patient_labs.setdefault(patient, set()).add(code)
        matches = tuple(patient for patient, labs in patient_labs.items()
                        if labs == {"AST", "ALT", "BUN", "Cr"})
        return ServiceValidationResult("SERVICE_HIT" if matches else "SERVICE_MISS", matches,
                                       None if matches else "SERVICE_MISS")
    matches = []
    procedure_ids = {
        "Procedure/" + str(resource["id"])
        for resource in resources
        if resource.get("resourceType") == "Procedure" and resource.get("id")
    }
    for resource in resources:
        if resource.get("resourceType") != contract.resource_type:
            continue
        if not set(resource.get("meta", {}).get("profile", ())) & set(contract.profiles):
            continue
        if contract.code and not any(c.get("system") == contract.code_system and c.get("code") == contract.code
                                     for c in _codings(resource, "medicationCodeableConcept.coding")
                                     + _codings(resource, "code.coding")):
            continue
        allowed_value_codes = set(contract.value_code.split(",")) if contract.value_code else set()
        if allowed_value_codes and not any(c.get("system") == contract.value_system and c.get("code") in allowed_value_codes
                                           for c in _codings(resource, "valueCodeableConcept.coding")):
            continue
        if contract.resource_type == "MedicationAdministration" and not any(
            e.get("url", "").endswith("cnwqk185-application-order") and e.get("valueCode") == "cnwqk185-application-first"
            for e in resource.get("extension", ())):
            continue
        if contract.resource_type == "Procedure" and contract.code == "invasive_mechanical_ventilation":
            parent_refs = {item.get("reference") for item in resource.get("partOf", ())}
            if not parent_refs & procedure_ids:
                continue
        patient = resource.get("subject", {}).get("reference", "").removeprefix("Patient/")
        if patient in identity:
            matches.append(patient)
    status = "SERVICE_HIT" if matches else "SERVICE_MISS"
    return ServiceValidationResult(status, tuple(dict.fromkeys(matches)), None if matches else "SERVICE_MISS")


def official_875_sql() -> str:
    """Official-style profile + value-concept JSON1 query; malformed rows must raise."""
    return """
    SELECT EXISTS (
      SELECT 1 FROM observation AS o
      JOIN json_each(o.resource, '$.meta.profile') AS p
      JOIN json_each(o.resource, '$.valueCodeableConcept.coding') AS c
      WHERE p.value = ?
        AND json_extract(c.value, '$.system') = ?
        AND json_extract(c.value, '$.code') = ?
    )
    """
