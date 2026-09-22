from v43.ir.models import (
    CriterionIR,
    CriterionType,
    FHIRContract,
    RetrievalPolicy,
    ServiceQueryContract,
)
from v43.retrieval.lexical import rank_tier1
from v43.retrieval.segmenter import segment_reports


def _ir(*aliases: str) -> CriterionIR:
    return CriterionIR(
        criterion_id="test",
        title="test",
        original_text="test",
        criterion_type=CriterionType.eligibility,
        clinical_domain="test",
        retrieval_policy=RetrievalPolicy(aliases, (), (), True, 3, False),
        fhir_contract=FHIRContract("Observation", (), (), (), (), (), (), {}),
        service_query_contract=ServiceQueryContract("Observation", False, (), {}),
        temporal_scope="CURRENT",
        raw={},
    )


def test_tier1_aliases_come_from_the_supplied_ir():
    spans = segment_reports([{"text": "记录含有定制锚点。另有伊立替康。"}])

    ranked = rank_tier1(_ir("定制锚点"), spans)

    assert [span.text for span in ranked] == ["记录含有定制锚点。"]
    assert ranked[0].retrieval_tier == 1
    assert ranked[0].lexical_score == 1.0


def test_tier1_ranks_mentions_without_claiming_family_or_negation_is_positive():
    spans = segment_reports([{"text": "家属曾使用伊立替康。患者未使用伊立替康。"}])

    ranked = rank_tier1(_ir("伊立替康"), spans)

    assert len(ranked) == 2
    assert all(span.lexical_score == 1.0 for span in ranked)
    assert all(not hasattr(span, "eligible") for span in ranked)
    assert all(not hasattr(span, "match") for span in ranked)


def test_tier1_anchor_miss_is_an_empty_ranking_not_a_no_evidence_decision():
    spans = segment_reports([{"text": "呼之能应，神志朦胧。"}])

    ranked = rank_tier1(_ir("意识不清"), spans)

    assert ranked == []
