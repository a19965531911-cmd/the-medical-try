from dataclasses import replace

from v43.ir.models import CriterionIR

from .models import EvidenceSpan


def rank_tier1(ir: CriterionIR, spans: tuple[EvidenceSpan, ...]) -> list[EvidenceSpan]:
    aliases = tuple(alias.casefold() for alias in ir.retrieval_policy.primary_aliases if alias)
    ranked: list[EvidenceSpan] = []
    for span in spans:
        text = span.text.casefold()
        score = float(sum(alias in text for alias in aliases))
        if score:
            ranked.append(replace(span, retrieval_tier=1, lexical_score=score))
    return sorted(ranked, key=lambda span: -span.lexical_score)
