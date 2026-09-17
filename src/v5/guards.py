from dataclasses import dataclass
import re

from .models import CriterionSpec, Decision


@dataclass(frozen=True, slots=True)
class GuardResult:
    decision: Decision
    reason_code: str | None = None


def _text(reports: list[dict]) -> str:
    return "\n".join(str(report.get("text", "")) for report in reports if isinstance(report, dict))


def apply_guard(spec: CriterionSpec, reports: list[dict], decision: Decision) -> GuardResult:
    if decision is not Decision.MATCH:
        return GuardResult(decision)
    text = _text(reports)
    patterns = {
        "185": (
            (r"(?:拟|计划|尚未).{0,12}(?:伊立替康|给药)|(?:伊立替康).{0,12}(?:尚未给药|计划)", "PLANNED_ONLY"),
            (r"(?:既往|此前).{0,8}(?:多次|反复).{0,8}(?:伊立替康|CPT-?11)", "PRIOR_MULTIPLE_USE"),
        ),
        "555": ((r"(?:距今|术后)\s*(?:7|8|9|1\d)\s*个?月|(?:一|两|二|三)年", "OUTSIDE_SIX_MONTHS"),),
        "675": ((r"(?:躯干|胸部|腹部|腰部|四肢).{0,8}带状疱疹|带状疱疹.{0,8}(?:非|不在)头面部", "NON_HEAD_FACE_SITE"),),
        "745": (
            (r"(?:拟|计划|尚未).{0,12}(?:插管|机械通气)|(?:插管|机械通气).{0,12}(?:拟行|尚未)", "PLANNED_ONLY"),
            (r"(?:仅|只).{0,4}无创通气|无创通气.{0,8}(?:未|无).{0,4}(?:插管|有创)", "NON_INVASIVE_ONLY"),
        ),
        "755": ((r"(?:持续|病程|症状仅)\s*(?:[0-6]|一|二|两|三|四|五|六)\s*(?:天|日)", "DURATION_TOO_SHORT"),),
        "805": (
            (r"(?:从不|从未|无).{0,4}吸烟", "NEVER_SMOKER"),
            (r"戒烟\s*(?:2|[3-9]|\d{2,}|两|二|三|四|五|六|七|八|九)\s*年", "CESSATION_AT_LEAST_TWO_YEARS"),
        ),
    }
    for pattern, reason in patterns.get(spec.criterion_id, ()):
        if re.search(pattern, text, re.I):
            return GuardResult(Decision.NO_MATCH, reason)
    return GuardResult(decision)

