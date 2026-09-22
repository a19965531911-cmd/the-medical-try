from collections import Counter
from dataclasses import replace
from math import log
import re

from v43.ir.models import CriterionIR

from .models import EvidenceSpan


_TOKEN_PATTERN = re.compile(
    r"\d+(?:\.\d+)?(?:mg|g|kg|ml|l|mmhg|cm|mm|岁|天|日|小时|℃)?|[A-Za-z]+|[\u3400-\u9fff]+",
    re.IGNORECASE,
)


def tokenize_zh(text: str) -> list[str]:
    tokens: list[str] = []
    for match in _TOKEN_PATTERN.finditer(text):
        token = match.group(0)
        if "\u3400" <= token[0] <= "\u9fff":
            if len(token) == 1:
                tokens.append(token)
            else:
                tokens.extend(token[index : index + 2] for index in range(len(token) - 1))
        else:
            tokens.append(token.casefold())
    return tokens


def rank_tier2(ir: CriterionIR, spans: tuple[EvidenceSpan, ...]) -> list[EvidenceSpan]:
    if not spans:
        return []
    query_tokens = [
        token
        for query_part in ir.retrieval_policy.bm25_query
        for token in tokenize_zh(query_part)
    ]
    if not query_tokens:
        return []

    document_tokens = [tokenize_zh(span.text) for span in spans]
    average_length = sum(map(len, document_tokens)) / len(document_tokens) or 1.0
    document_frequency = Counter(
        token for tokens in document_tokens for token in set(tokens)
    )
    document_count = len(spans)
    scored: list[EvidenceSpan] = []
    for span, tokens in zip(spans, document_tokens):
        frequencies = Counter(tokens)
        length_ratio = len(tokens) / average_length
        score = 0.0
        for token in query_tokens:
            frequency = frequencies[token]
            if not frequency:
                continue
            inverse_document_frequency = log(
                1.0
                + (document_count - document_frequency[token] + 0.5)
                / (document_frequency[token] + 0.5)
            )
            score += inverse_document_frequency * (
                frequency * 2.2
                / (frequency + 1.2 * (0.25 + 0.75 * length_ratio))
            )
        if score > 0:
            scored.append(replace(span, retrieval_tier=2, bm25_score=score))
    return sorted(scored, key=lambda span: (-span.bm25_score, span.report_index, span.start_offset))
