import re
from typing import Any

from .models import CriterionSpec, EvidenceSegment


def _text(report: Any) -> str:
    return str(report.get("text", "")).strip() if isinstance(report, dict) else ""


def select_evidence(spec: CriterionSpec, reports: list[dict], max_segments: int = 6, max_chars: int = 1200) -> tuple[EvidenceSegment, ...]:
    candidates = []
    for index, report in enumerate(reports or []):
        text = _text(report)
        if not text:
            continue
        hits = sum(1 for alias in spec.aliases if alias and str(alias).lower() in text.lower())
        numeric = len(re.findall(r"\d+(?:\.\d+)?", text))
        tier = "A" if hits else ("B" if numeric else "C")
        score = hits * 100.0 + numeric * 5.0 + min(len(text), 200) / 200.0
        candidates.append(EvidenceSegment(index, text, score, tier))
    candidates.sort(key=lambda item: (-item.score, item.report_index))
    selected = []
    remaining = max_chars
    for item in candidates[:max_segments]:
        if remaining <= 0:
            break
        text = item.text[:remaining]
        if text:
            selected.append(EvidenceSegment(item.report_index, text, item.score, item.tier))
            remaining -= len(text)
    selected.sort(key=lambda item: item.report_index)
    return tuple(selected)
