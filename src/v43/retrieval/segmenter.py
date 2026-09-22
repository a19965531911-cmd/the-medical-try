from hashlib import sha256
import re
from typing import Any

from .models import EvidenceSpan


_SENTENCE_ENDINGS = frozenset("。！？；")
_WHITESPACE = re.compile(r"\s+")


def _normalized_text(text: str) -> str:
    return _WHITESPACE.sub(" ", text).strip()


def _append_span(
    spans: list[EvidenceSpan],
    text: str,
    report_index: int,
    topic: str | None,
    timestamp: str | None,
    start: int,
    end: int,
) -> None:
    while start < end and text[start].isspace():
        start += 1
    while end > start and text[end - 1].isspace():
        end -= 1
    if start == end:
        return

    source_text = text[start:end]
    normalized_hash = sha256(_normalized_text(source_text).encode("utf-8")).hexdigest()
    identity = f"{report_index}:{start}:{end}:{normalized_hash}"
    span_id = f"span-{sha256(identity.encode('utf-8')).hexdigest()}"
    spans.append(
        EvidenceSpan(
            span_id=span_id,
            text=source_text,
            report_index=report_index,
            topic=topic,
            timestamp=timestamp,
            start_offset=start,
            end_offset=end,
            normalized_hash=normalized_hash,
        )
    )


def segment_reports(reports: list[dict[str, Any]]) -> tuple[EvidenceSpan, ...]:
    spans: list[EvidenceSpan] = []
    for report_index, report in enumerate(reports):
        text = report.get("text")
        if not isinstance(text, str) or not text.strip():
            continue

        start = 0
        for index, character in enumerate(text):
            if character in _SENTENCE_ENDINGS:
                _append_span(
                    spans,
                    text,
                    report_index,
                    report.get("topic"),
                    report.get("timestamp"),
                    start,
                    index + 1,
                )
                start = index + 1
            elif character in "\r\n":
                _append_span(
                    spans,
                    text,
                    report_index,
                    report.get("topic"),
                    report.get("timestamp"),
                    start,
                    index,
                )
                start = index + 1

        _append_span(
            spans,
            text,
            report_index,
            report.get("topic"),
            report.get("timestamp"),
            start,
            len(text),
        )
    return tuple(spans)
