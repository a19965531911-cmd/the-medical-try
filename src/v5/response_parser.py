import json
import re
from typing import Any

from .models import Decision, ParsedDecision, ParseMethod


_SENTINELS = {item.value: item for item in Decision}
_CHINESE = {"符合": Decision.MATCH, "不符合": Decision.NO_MATCH, "无法判断": Decision.UNKNOWN}


def _unfence(text: str) -> str:
    stripped = text.strip()
    match = re.fullmatch(r"```(?:json|text)?\s*\n?(.*?)\n?```", stripped, re.I | re.S)
    return match.group(1).strip() if match else stripped


def _json_decision(value: Any) -> Decision | None:
    data = value
    if isinstance(value, str):
        try:
            data = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return None
    if not isinstance(data, dict):
        return None
    decision = data.get("decision")
    if isinstance(decision, str) and decision.strip().upper() in _SENTINELS:
        return _SENTINELS[decision.strip().upper()]
    match = data.get("match")
    if isinstance(match, bool):
        return Decision.MATCH if match else Decision.NO_MATCH
    return None


def parse_response(value: Any) -> ParsedDecision:
    if isinstance(value, dict):
        decision = _json_decision(value)
        return ParsedDecision(decision or Decision.UNKNOWN, ParseMethod.PARSED_JSON if decision else ParseMethod.PARSE_UNKNOWN)
    if not isinstance(value, str) or not value.strip():
        return ParsedDecision(Decision.UNKNOWN, ParseMethod.PARSE_UNKNOWN)
    text = _unfence(value)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    sentinel_lines = [line.upper() for line in lines if line.upper() in _SENTINELS]
    if len(set(sentinel_lines)) == 1:
        return ParsedDecision(_SENTINELS[sentinel_lines[0]], ParseMethod.PARSED_SENTINEL)
    decision = _json_decision(text)
    if decision is not None:
        return ParsedDecision(decision, ParseMethod.PARSED_JSON)
    chinese_hits = {decision for phrase, decision in _CHINESE.items() if re.fullmatch(re.escape(phrase) + r"(?:[。；;，,：:].*)?", text, re.S)}
    if len(chinese_hits) == 1:
        return ParsedDecision(next(iter(chinese_hits)), ParseMethod.PARSED_CHINESE)
    return ParsedDecision(Decision.UNKNOWN, ParseMethod.PARSE_UNKNOWN)
