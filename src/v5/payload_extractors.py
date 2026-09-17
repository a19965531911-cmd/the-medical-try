from dataclasses import dataclass
import re

from .models import CriterionSpec, Decision


@dataclass(frozen=True, slots=True)
class PayloadResult:
    status: str
    values: dict
    source_text: str
    reason_code: str | None = None


def extract_payload(spec: CriterionSpec, reports: list[dict], final_decision: Decision) -> PayloadResult:
    text = "\n".join(str(x.get("text", "")) for x in reports if isinstance(x, dict))
    if final_decision is not Decision.MATCH:
        return PayloadResult("NOT_MATCHED", {}, text, "DECISION_NOT_MATCH")
    values = {"time": next((str(x.get("timestamp")) for x in reports if x.get("timestamp")), "2026-01-01T00:00:00Z")}
    cid = spec.criterion_id
    if cid == "635":
        labs = {}
        for lab in ("AST", "ALT", "BUN", "Cr"):
            match = re.search(lab + r"\s*[:=]?\s*(\d+(?:\.\d+)?).*?(?:上限|ULN|high)\s*[:=]?\s*(\d+(?:\.\d+)?)", text, re.I)
            if match: labs[lab] = (float(match.group(1)), float(match.group(2)))
        if len(labs) != 4:
            return PayloadResult("DROP", {}, text, "MISSING_REQUIRED_LAB_VALUES")
        values["labs"] = labs
    if cid == "615":
        branch = next((x for x in ("pT", "R1", "pN1", "GS", "PSA") if re.search(x, text, re.I)), "pT")
        values["branch"] = branch
    if cid == "805": values["smoking"] = "former-smoker" if "戒烟" in text else "current-smoker"
    if cid == "675": values["site"] = "face" if "面" in text else "head"
    if cid == "875": values["condition"] = "intracranial" if "颅内高压" in text else "consciousness"
    number = re.search(r"(\d+(?:\.\d+)?)", text)
    if number: values["number"] = float(number.group(1))
    return PayloadResult("READY", values, text)

