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
from v43.retrieval.bm25 import rank_tier2, tokenize_zh
from v43.retrieval.segmenter import segment_reports


CASES = json.loads(
    (Path(__file__).parents[1] / "fixtures" / "retrieval_cases.json").read_text(
        encoding="utf-8"
    )
)


def _ir(case: dict) -> CriterionIR:
    return CriterionIR(
        criterion_id=case["criterion_id"],
        title="test",
        original_text="test",
        criterion_type=CriterionType.eligibility,
        clinical_domain="test",
        retrieval_policy=RetrievalPolicy((), (), tuple(case["query"]), True, 3, False),
        fhir_contract=FHIRContract("Observation", (), (), (), (), (), (), {}),
        service_query_contract=ServiceQueryContract("Observation", False, (), {}),
        temporal_scope="CURRENT",
        raw={},
    )


def test_tokenize_zh_combines_chinese_bigrams_ascii_numbers_and_units():
    assert tokenize_zh("CPT-11 伊立替康 38.5mg 50岁") == [
        "cpt",
        "11",
        "伊立",
        "立替",
        "替康",
        "38.5mg",
        "50岁",
    ]


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["criterion_id"])
def test_tier2_ranks_critical_paraphrase_above_unrelated_report(case: dict):
    ranked = rank_tier2(_ir(case), segment_reports(case["reports"]))

    assert ranked
    assert ranked[0].report_index == case["critical_report_index"]
    assert ranked[0].retrieval_tier == 2
    assert ranked[0].bm25_score > 0
