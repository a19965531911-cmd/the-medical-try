from dataclasses import dataclass
import re

from .models import CriterionSpec, Decision


@dataclass(frozen=True, slots=True)
class DeterministicResult:
    decision: Decision
    reason_code: str | None = None


def _joined(reports: list[dict]) -> str:
    return "\n".join(str(report.get("text", "")) for report in reports if isinstance(report, dict))


def deterministic_match(spec: CriterionSpec, reports: list[dict]) -> DeterministicResult:
    text = _joined(reports)
    if not text.strip():
        return DeterministicResult(Decision.UNKNOWN, "NO_PATIENT_TEXT")
    if spec.criterion_id == "615":
        if re.search(r"\bpT(?:3a|3b|4)\b|\bR1\b|\bpN1\b", text, re.I):
            return DeterministicResult(Decision.MATCH, "EXPLICIT_615_BRANCH")
        gs = re.search(r"(?:GS|Gleason(?:\s*score)?)\s*[:=]?\s*(\d+(?:\.\d+)?)", text, re.I)
        psa = re.search(r"PSA\s*[:=]?\s*(\d+(?:\.\d+)?)", text, re.I)
        if (gs and float(gs.group(1)) >= 8) or (psa and float(psa.group(1)) > 0.1):
            return DeterministicResult(Decision.MATCH, "EXPLICIT_615_THRESHOLD")
    return DeterministicResult(Decision.UNKNOWN)

