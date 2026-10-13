"""B5 package, corpus and deployment-budget safety."""
import base64
import json

import pytest


def ns(variant="B5H", cid="2", **config):
    from scripts.b5_experiments import build_variant
    bundle = build_variant(variant, config)
    library = next(e["resource"] for e in bundle["entry"][1:] if e["resource"]["content"][0]["title"] == cid)
    scope = {}
    exec(base64.b64decode(library["content"][0]["data"]), scope)
    return scope


def test_corpus_has_exact_five_balanced_groups_and_all_profiles():
    from scripts.b5_experiments import corpus
    from collections import Counter
    items = corpus()
    assert len(items) == 100
    assert set(Counter(x["group"] for x in items).values()) == {20}
    assert len({x["profile_id"] for x in items}) == 16
    assert len({x["case"] for x in items}) == 100
    assert all(type(x["expected"]) is bool and x["label_rationale"] for x in items)


def test_rule_mode_matches_frozen_b2e_and_never_requests_model():
    scope = ns("B5R")
    reports = [{"text": "患者咳嗽"}]
    generator = scope["FHIRResourceBundleGenerator"]("http://localhost:3456")
    generator.transport = lambda prompt: pytest.fail("rule mode called model")
    bundle = generator.parse_clinical_text_to_fhir_bundle("p1", reports)
    assert bundle["entry"]
    assert generator.last_result["match"] == scope["evaluate_b2"]("2", reports, "B2E")["match"]


def test_llm_connection_failure_retains_rules_and_traces_fallback():
    scope = ns("B5L")
    generator = scope["FHIRResourceBundleGenerator"]("http://localhost:3456")
    def fail(prompt):
        generator.transport_error = "connection refused"
        generator.transport_error_kind = "CONNECTION_FAILED"
        return None
    generator.transport = fail
    assert generator.parse_clinical_text_to_fhir_bundle("p1", [{"text": "咳嗽"}])["entry"]
    assert generator.b5_trace["fallback"] == "RULES_AFTER_MODEL_FAILURE"


def test_call_limit_is_global_across_event_groups():
    scope = ns("B5H", "495", max_calls=1)
    generator = scope["FHIRResourceBundleGenerator"]("http://localhost:3456")
    prompts = []
    generator.transport = lambda p: (prompts.append(p) or "NO")
    reports = [{"text": "病理报告。未知淋巴瘤", "event_id": "A"},
               {"text": "病理报告。另一未知淋巴瘤", "event_id": "B"}]
    assert not generator.parse_clinical_text_to_fhir_bundle("p1", reports)["entry"]
    assert len(prompts) <= 1


def test_model_transport_total_timeout_is_enforced(monkeypatch):
    scope = ns("B5H")
    seen = []
    def timeout(*args, **kwargs):
        seen.append(kwargs["timeout"])
        raise scope["_b5_subprocess"].TimeoutExpired("controlled", kwargs["timeout"])
    monkeypatch.setattr(scope["_b5_subprocess"], "run", timeout)
    generator = scope["FHIRResourceBundleGenerator"]("http://localhost:3456")
    assert not generator.parse_clinical_text_to_fhir_bundle("p1", [{"text": "活动后透不过气"}])["entry"]
    assert 0 < seen[0] <= 4
    assert generator.model_metrics["errors"][0]["kind"] == "TOTAL_BUDGET_TIMEOUT"


def test_no_external_endpoint_can_be_embedded():
    with pytest.raises(ValueError, match="loopback"):
        ns(endpoint="https://example.com/v1/chat/completions")


@pytest.mark.parametrize("variant", ["B5H", "B5L"])
@pytest.mark.parametrize("cid,reports", [
    ("715", [{"text": "父亲下腔静脉、门静脉均未受侵"}]),
    ("525", [{"text": "术前食管癌", "event_id": "A"}, {"text": "肿瘤中下段", "event_id": "B"}]),
])
def test_subject_and_event_cannot_complete_patient_facts(variant, cid, reports):
    scope = ns(variant, cid)
    generator = scope["FHIRResourceBundleGenerator"]("http://localhost:3456")
    generator.transport = lambda prompt: "NO"
    assert not generator.parse_clinical_text_to_fhir_bundle("p1", reports)["entry"]
