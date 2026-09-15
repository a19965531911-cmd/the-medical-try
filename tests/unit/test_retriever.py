import json
from pathlib import Path

import pytest

from v43.ir.models import (
    CriterionIR,
    CriterionType,
    FHIRContract,
    RetrievalPolicy,
    ServiceQueryContract,
)
from v43.retrieval.fallback import rank_fallback
from v43.retrieval.retriever import retrieve
from v43.retrieval.segmenter import segment_reports


CASES = json.loads(
    (Path(__file__).parents[1] / "fixtures" / "retrieval_cases.json").read_text(
        encoding="utf-8"
    )
)


def _ir(
    *, aliases: tuple[str, ...] = (), query: tuple[str, ...] = (), fallback_k: int = 3
) -> CriterionIR:
    return CriterionIR(
        criterion_id="test",
        title="test",
        original_text="test",
        criterion_type=CriterionType.eligibility,
        clinical_domain="test",
        retrieval_policy=RetrievalPolicy(aliases, (), query, True, fallback_k, False),
        fhir_contract=FHIRContract("Observation", (), (), (), (), (), (), {}),
        service_query_contract=ServiceQueryContract("Observation", False, (), {}),
        temporal_scope="CURRENT",
        raw={},
    )


def test_empty_reports_are_the_only_no_evidence_packet():
    packet = retrieve(_ir(), [{"text": "  "}, {}])

    assert packet.spans == ()
    assert packet.retrieval_reason == "NO_EVIDENCE"
    assert packet.trace.tier1_count == 0
    assert packet.trace.tier2_count == 0
    assert packet.trace.tier3_count == 0
    assert packet.trace.fallback_used is False


def test_anchor_miss_uses_nonempty_diverse_fallback_capped_at_three():
    reports = [
        {"text": "普通记录。体温38.5℃，今日给予治疗。", "topic": "病程"},
        {"text": "昨日复查血压120mmHg。", "topic": "护理"},
        {"text": "患者目前否认疼痛。", "topic": "查房"},
        {"text": "计划明日复诊。", "topic": "随访"},
    ]

    packet = retrieve(_ir(aliases=("不存在的锚点",)), reports)

    assert 1 <= len(packet.spans) <= 3
    assert len({span.report_index for span in packet.spans}) == len(packet.spans)
    assert packet.retrieval_reason == "RETRIEVAL_FALLBACK_USED"
    assert packet.trace.fallback_used is True
    assert packet.trace.tier3_count == len(packet.spans)
    assert all(span.retrieval_tier == 3 for span in packet.spans)
    assert [span.final_rank for span in packet.spans] == list(range(1, len(packet.spans) + 1))


def test_fallback_selects_at_most_one_span_per_report():
    spans = segment_reports(
        [
            {"text": "体温39℃。给予抗感染治疗。"},
            {"text": "血压90mmHg。"},
        ]
    )

    ranked = rank_fallback(spans, k=3)

    assert len(ranked) == 2
    assert {span.report_index for span in ranked} == {0, 1}


def test_primary_tiers_deduplicate_spans_and_preserve_all_score_metadata():
    packet = retrieve(
        _ir(aliases=("神志",), query=("神志",)),
        [{"text": "神志朦胧。"}],
    )

    assert len(packet.spans) == 1
    span = packet.spans[0]
    assert span.retrieval_tier == 1
    assert span.lexical_score > 0
    assert span.bm25_score > 0
    assert span.metadata_boost == 0
    assert span.final_rank == 1
    assert packet.retrieval_reason == "PRIMARY_RETRIEVAL"
    assert packet.trace.tier1_count == 1
    assert packet.trace.tier2_count == 1
    assert packet.trace.fallback_used is False


def test_incomplete_primary_is_supplemented_when_distractor_hides_critical_span():
    packet = retrieve(
        _ir(aliases=("伊立替康",), query=("伊立替康",)),
        [
            {"text": "家属未使用伊立替康。", "topic": "家族史"},
            {"text": "呼之能应，神志朦胧。", "topic": "查房"},
        ],
    )

    assert {span.report_index for span in packet.spans} == {0, 1}
    distractor = next(span for span in packet.spans if span.report_index == 0)
    critical = next(span for span in packet.spans if span.report_index == 1)
    assert distractor.retrieval_tier == 1
    assert distractor.lexical_score > 0
    assert distractor.bm25_score > 0
    assert critical.retrieval_tier == 3
    assert packet.retrieval_reason == "PRIMARY_WITH_FALLBACK"
    assert packet.trace.fallback_used is True
    assert packet.trace.tier3_count == 1
    assert [span.final_rank for span in packet.spans] == list(
        range(1, len(packet.spans) + 1)
    )


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["criterion_id"])
def test_critical_evidence_recall_at_k_fixture(case: dict):
    packet = retrieve(_ir(query=tuple(case["query"])), case["reports"])

    assert case["critical_report_index"] in {span.report_index for span in packet.spans}
