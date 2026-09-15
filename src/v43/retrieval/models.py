from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EvidenceSpan:
    span_id: str
    text: str
    report_index: int
    topic: str | None
    timestamp: str | None
    start_offset: int
    end_offset: int
    normalized_hash: str
    retrieval_tier: int | None = None
    lexical_score: float = 0.0
    bm25_score: float = 0.0
    metadata_boost: float = 0.0
    final_rank: int | None = None


@dataclass(frozen=True, slots=True)
class RetrievalTrace:
    tier1_count: int = 0
    tier2_count: int = 0
    tier3_count: int = 0
    fallback_used: bool = False


@dataclass(frozen=True, slots=True)
class EvidencePacket:
    spans: tuple[EvidenceSpan, ...]
    retrieval_reason: str | None = None
    trace: RetrievalTrace = RetrievalTrace()
