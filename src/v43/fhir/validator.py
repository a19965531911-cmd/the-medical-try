import json
from dataclasses import replace

from .compiler import FHIRCompileResult
from .contracts import CompiledContract


def validate_fhir(result: FHIRCompileResult, contract: CompiledContract) -> FHIRCompileResult:
    if result.status != "COMPILED":
        return replace(result, structural_status="NOT_RUN")
    candidates = [
        r for r in result.resources
        if r.get("resourceType") == contract.resource_type
        and set(r.get("meta", {}).get("profile", ())) & set(contract.profiles)
    ]
    valid = bool(candidates)
    for resource in candidates:
        try:
            json.loads(json.dumps(resource, allow_nan=False))
        except (TypeError, ValueError):
            valid = False
        valid &= resource.get("meta", {}).get("profile", [None])[0] in contract.profiles
        valid &= resource.get("subject", {}).get("reference", "").startswith("Patient/")
        valid &= all(field in resource for field in contract.required_fields)
        if contract.criterion_id == "745":
            parent_ref = resource.get("partOf", [{}])[0].get("reference", "")
            valid &= parent_ref.startswith("Procedure/")
            valid &= any(
                other.get("resourceType") == "Procedure"
                and "Procedure/" + other.get("id", "") == parent_ref
                for other in result.resources
            )
    return replace(result, structural_status="VALID" if valid else "INVALID",
                   reason_code=result.reason_code if valid else "FHIR_INVALID")
