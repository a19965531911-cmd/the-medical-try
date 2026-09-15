from dataclasses import replace
from typing import Any

from v43.ir.models import CriterionIR

from .bm25 import rank_tier2
from .fallback import rank_fallback
from .lexical import rank_tier1
from .models import EvidencePacket, EvidenceSpan, RetrievalTrace
from .segmenter import segment_reports


def _merge_primary(
    tier1: list[EvidenceSpan], tier2: list[EvidenceSpan]
) -> list[EvidenceSpan]:
    merged = {span.span_id: span for span in tier2}
    for span in tier1:
        tier2_span = merged.get(span.span_id)
        if tier2_span is not None:
            span = replace(span, bm25_score=tier2_span.bm25_score)
        merged[span.span_id] = span
    return sorted(
        merged.values(),
        key=lambda span: (
            span.retrieval_tier or 99,
            -(span.lexical_score + span.bm25_score + span.metadata_boost),
            span.report_index,
            span.start_offset,
        ),
    )


def retrieve(ir: CriterionIR, reports: list[dict[str, Any]]) -> EvidencePacket:
    spans = segment_reports(reports)
    if not spans:
        return EvidencePacket(spans=(), retrieval_reason="NO_EVIDENCE")

    tier1 = rank_tier1(ir, spans)
    tier2 = rank_tier2(ir, spans)
    primary = _merge_primary(tier1, tier2)
    if primary:
        ranked = tuple(
            replace(span, final_rank=index)
            for index, span in enumerate(primary, start=1)
        )
        return EvidencePacket(
            spans=ranked,
            retrieval_reason="PRIMARY_RETRIEVAL",
            trace=RetrievalTrace(
                tier1_count=len(tier1),
                tier2_count=len(tier2),
            ),
        )

    fallback = tuple(rank_fallback(spans, k=ir.retrieval_policy.fallback_k))
    return EvidencePacket(
        spans=fallback,
        retrieval_reason="RETRIEVAL_FALLBACK_USED",
        trace=RetrievalTrace(
            tier3_count=len(fallback),
            fallback_used=True,
        ),
    )
