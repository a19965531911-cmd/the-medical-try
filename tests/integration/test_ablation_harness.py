from v43.shadow.evaluator import run_ablation


def test_ablation_harness_reports_each_retrieval_mode_without_changing_decisions():
    cases = ({"case_id": "a", "critical_span_id": "s1",
              "retrieved": {"tier1": (), "tier1_bm25": ("s1",), "tier1_bm25_fallback": ("s1",)}},)
    result = run_ablation(cases, ("tier1", "tier1_bm25", "tier1_bm25_fallback"))
    assert result == {
        "tier1": {"cases": 1, "critical_hits": 0, "recall_at_k": 0.0},
        "tier1_bm25": {"cases": 1, "critical_hits": 1, "recall_at_k": 1.0},
        "tier1_bm25_fallback": {"cases": 1, "critical_hits": 1, "recall_at_k": 1.0},
    }
