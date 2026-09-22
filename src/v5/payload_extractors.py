from dataclasses import dataclass
import re

from .models import CriterionSpec, Decision

@dataclass(frozen=True, slots=True)
class PayloadResult:
    status: str
    values: dict
    source_text: str
    reason_code: str | None = None

def _number_unit(pattern, text):
    m = re.search(pattern, text, re.I)
    return (float(m.group(1)), m.group(2) if m.lastindex and m.lastindex >= 2 else None) if m else None

def extract_payload(spec: CriterionSpec, reports: list[dict], final_decision: Decision) -> PayloadResult:
    text = "\n".join(str(x.get("text", "")) for x in reports if isinstance(x, dict))
    if final_decision is not Decision.MATCH:
        return PayloadResult("NOT_MATCHED", {}, text, "DECISION_NOT_MATCH")
    values = {}
    timestamps = [str(x.get("timestamp")) for x in reports if isinstance(x, dict) and x.get("timestamp")]
    if timestamps:
        values["time"] = timestamps[0]
    cid = spec.criterion_id
    if cid == "265":
        found = _number_unit(r"(?:cTnI|cTnT|肌钙蛋白[IT]?)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*([A-Za-zµμ/]+)", text)
        if found: values["number"], values["unit"] = found
    elif cid == "855":
        found = _number_unit(r"(?:Scr|肌酐|creatinine)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*([A-Za-zµμ/]+)", text)
        if found: values["number"], values["unit"] = found
    elif cid == "615":
        branch = None
        if re.search(r"\bPSA\b", text, re.I):
            branch = "PSA"; found = _number_unit(r"\bPSA\b\s*[:=]?\s*(\d+(?:\.\d+)?)\s*([A-Za-zµμ/]+)?", text)
        elif re.search(r"\b(?:GS|Gleason)\b", text, re.I):
            branch = "GS"; found = _number_unit(r"\b(?:GS|Gleason)\b\s*[:=]?\s*(\d+(?:\.\d+)?)", text)
        elif re.search(r"\bpT(?:3a|3b|4)\b", text, re.I): branch, found = "pT", None
        elif re.search(r"\bR1\b", text, re.I): branch, found = "R1", None
        elif re.search(r"\bpN1\b", text, re.I): branch, found = "pN1", None
        else: found = None
        if branch: values["branch"] = branch
        if found:
            values["number"], values["unit"] = found
    elif cid == "635":
        labs = {}
        for lab in ("AST", "ALT", "BUN", "Cr"):
            match = re.search(lab + r"\s*[:=]?\s*(\d+(?:\.\d+)?).*?(?:上限|ULN|high)\s*[:=]?\s*(\d+(?:\.\d+)?)", text, re.I)
            if match: labs[lab] = (float(match.group(1)), float(match.group(2)))
        if len(labs) != 4:
            return PayloadResult("DROP", values, text, "MISSING_REQUIRED_LAB_VALUES")
        values["labs"] = labs
    elif cid == "805":
        lower = text.lower()
        if re.search(r"从不|从未|never", text, re.I): values["smoking"] = "never-smoker"
        elif re.search(r"戒烟|quit|former", text, re.I): values["smoking"] = "former-smoker"
        elif re.search(r"目前|每日|current", text, re.I): values["smoking"] = "current-smoker"
    elif cid == "755":
        m = re.search(r"(?:持续|duration|通气)\s*(\d+(?:\.\d+)?)\s*(小时|h|hours)", text, re.I)
        if m: values["duration_hours"] = float(m.group(1))
    elif cid == "555":
        m = re.search(r"(\d{4}-\d{2}-\d{2})", text)
        if m: values["surgery_date"] = m.group(1)
    if cid == "675": values["site"] = "face" if re.search(r"面", text) else "head"
    if cid == "875": values["condition"] = "intracranial" if "颅内高压" in text else "consciousness"
    return PayloadResult("READY", values, text)
