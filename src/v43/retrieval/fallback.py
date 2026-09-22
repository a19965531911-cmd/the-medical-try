from dataclasses import replace
import re

from .models import EvidenceSpan


_NUMBER_OR_UNIT = re.compile(r"\d+(?:\.\d+)?\s*(?:mg|g|kg|ml|mmhg|cm|mm|岁|天|小时|℃)?", re.I)
_CLINICAL_CUES = (
    "诊断",
    "治疗",
    "给予",
    "使用",
    "复查",
    "手术",
    "意识",
    "神志",
    "疼痛",
    "发热",
)
_TEMPORAL_CUES = ("今日", "昨日", "目前", "既往", "术后", "计划", "明日")
_NEGATION_CUES = ("无", "未", "否认", "排除")


def _information_score(span: EvidenceSpan) -> tuple[float, float]:
    metadata_boost = 0.25 if span.topic else 0.0
    score = min(len(span.text.strip()), 80) / 80
    score += len(_NUMBER_OR_UNIT.findall(span.text))
    score += sum(cue in span.text for cue in _CLINICAL_CUES)
    score += 0.5 * sum(cue in span.text for cue in _TEMPORAL_CUES)
    score += 0.5 * sum(cue in span.text for cue in _NEGATION_CUES)
    return score + metadata_boost, metadata_boost


def rank_fallback(spans: tuple[EvidenceSpan, ...], k: int = 3) -> list[EvidenceSpan]:
    if k <= 0:
        return []
    best_by_report: dict[int, tuple[float, EvidenceSpan, float]] = {}
    for span in spans:
        score, metadata_boost = _information_score(span)
        candidate = (score, span, metadata_boost)
        current = best_by_report.get(span.report_index)
        if current is None or (score, -span.start_offset) > (
            current[0],
            -current[1].start_offset,
        ):
            best_by_report[span.report_index] = candidate

    selected = sorted(
        best_by_report.values(),
        key=lambda item: (-item[0], item[1].report_index, item[1].start_offset),
    )[:k]
    return [
        replace(span, retrieval_tier=3, metadata_boost=boost, final_rank=index)
        for index, (_, span, boost) in enumerate(selected, start=1)
    ]
