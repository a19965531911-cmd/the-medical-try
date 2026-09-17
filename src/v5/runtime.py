from dataclasses import dataclass

from .criterion_specs import load_criterion_specs
from .fhir_adapter import build_resources
from .matcher import MatchResult, match_patient
from .payload_extractors import extract_payload


@dataclass(frozen=True, slots=True)
class RuntimeResult:
    match: MatchResult
    resources: tuple[dict, ...]
    reason_code: str | None


def evaluate_and_compile(criterion_id, patient_id, reports, transport):
    spec=load_criterion_specs()[str(criterion_id)]
    match=match_patient(spec,reports,transport)
    payload=extract_payload(spec,reports,match.final_decision)
    resources=build_resources(str(criterion_id),str(patient_id),payload)
    reason=payload.reason_code if match.final_decision.value == "MATCH" and not resources else match.reason_code
    return RuntimeResult(match,resources,reason)
