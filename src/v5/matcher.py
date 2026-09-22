from dataclasses import dataclass

from .deterministic import deterministic_match
from .guards import apply_guard
from .models import CriterionSpec, Decision, ParseMethod
from .prompt import build_prompt
from .retrieval import select_evidence
from .transport import TransportStatus


@dataclass(frozen=True, slots=True)
class MatchResult:
    deterministic_decision: Decision
    model_decision: Decision
    guarded_decision: Decision
    final_decision: Decision
    reason_code: str | None
    attempts: int
    transport_status: TransportStatus | None
    parse_method: ParseMethod | None
    prompt_length: int


def match_patient(spec: CriterionSpec, reports: list[dict], transport) -> MatchResult:
    deterministic = deterministic_match(spec, reports)
    if deterministic.decision is not Decision.UNKNOWN or deterministic.reason_code == "NO_PATIENT_TEXT":
        return MatchResult(deterministic.decision, Decision.UNKNOWN, deterministic.decision, deterministic.decision,
                           deterministic.reason_code, 0, None, None, 0)
    segments = select_evidence(spec, reports)
    if not segments:
        return MatchResult(Decision.UNKNOWN, Decision.UNKNOWN, Decision.UNKNOWN, Decision.UNKNOWN,
                           "NO_PATIENT_TEXT", 0, None, None, 0)
    prompt = build_prompt(spec, segments)
    response = transport.decide(prompt)
    model = response.parsed.decision
    guarded = apply_guard(spec, reports, model)
    return MatchResult(Decision.UNKNOWN, model, guarded.decision, guarded.decision, guarded.reason_code,
                       response.attempts, response.status, response.parsed.method, len(prompt))
