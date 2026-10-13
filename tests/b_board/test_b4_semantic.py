"""B4 evidence safety and executable-package behavior; synthetic only."""
import base64
import json
from functools import lru_cache

import pytest


@lru_cache(maxsize=None)
def namespace(cid="2", variant="B4H"):
    from scripts.b4_experiments import build_variant
    bundle = build_variant(variant)
    entry = next(e["resource"] for e in bundle["entry"][1:]
                 if e["resource"]["content"][0]["title"] == cid)
    ns = {}
    exec(base64.b64decode(entry["content"][0]["data"]), ns)
    return ns


def answer(atom="respiratory", quote="活动后透不过气", index=0, **extra):
    return dict(match=True, facts=[dict(atom=atom, state="PRESENT", evidence=quote, report=index)],
                subject="patient", negated=False, planned=False, uncertain=False,
                evidence=[quote], reason="literal patient evidence", **extra)


def run(cid, reports, raw, variant="B4H"):
    ns = namespace(cid, variant)
    g = ns["FHIRResourceBundleGenerator"]("http://localhost:3456")
    g.transport = lambda prompt: raw
    bundle = g.parse_clinical_text_to_fhir_bundle("p1", reports)
    return g, bundle


def test_semantic_recall_without_rule_keyword():
    g, bundle = run("2", [{"text": "活动后透不过气"}], answer())
    assert bundle["entry"]
    assert g.last_result["facts"]["respiratory"]["source"] == "semantic"
    assert g.model_metrics["calls"] == 1


@pytest.mark.parametrize("text", ["父亲活动后透不过气", "否认活动后透不过气", "可能活动后透不过气",
                                  "拟评估活动后透不过气", "活动后透不过气已完全消失"])
def test_quote_cannot_hide_subject_negation_or_state(text):
    _, bundle = run("2", [{"text": text}], answer())
    assert not bundle["entry"]


@pytest.mark.parametrize("raw", ["YES", '{"match":true,"match":false}', '{"facts":NaN}',
                                  answer(quote="编造的症状"), answer(index=True),
                                  dict(answer(), subject="family"), dict(answer(), planned=True),
                                  dict(answer(), extra="not allowed")])
def test_invalid_response_is_closed_and_falls_back(raw):
    g, bundle = run("2", [{"text": "活动后透不过气"}], raw)
    assert not bundle["entry"]
    assert g.model_metrics["errors"]


def test_model_cannot_override_deterministic_negative():
    _, bundle = run("2", [{"text": "无咳嗽。活动后透不过气"}], answer())
    assert not bundle["entry"]


def test_repeated_quote_cannot_select_only_safe_occurrence():
    _, bundle = run("2", [{"text": "活动后透不过气。否认活动后透不过气"}], answer())
    assert not bundle["entry"]


def test_unknown_is_valid_and_never_emits_resources():
    raw = dict(answer(), match=None, facts=[], evidence=[])
    g, bundle = run("2", [{"text": "活动后透不过气"}], raw)
    assert not bundle["entry"]
    assert g.model_metrics["json_valid"] == 1


@pytest.mark.parametrize("cid,items", [("625", ["TBIL", "ALT", "AST", "reference_upper_limits", "encounter_identity"]),
                                      ("295", ["current_or_recent", "daily_quantity", "ninety_day_window", "cessation_guarantee"])])
def test_numeric_item_prompts_expose_independent_constraints(cid, items):
    ns = namespace(cid, "B4I")
    g = ns["FHIRResourceBundleGenerator"]("http://localhost:3456")
    prompts = []
    g.transport = lambda p: (prompts.append(json.loads(p)) or "NO")
    assert not g.parse_clinical_text_to_fhir_bundle("p1", [{"text": "就诊记录，无相关检查内容"}])["entry"]
    assert [p["requested_items"] for p in prompts] == [[item] for item in items]


def test_overall_yes_cannot_complete_labs_or_vessels():
    for cid, atom, text in [("625", "labs", "TBIL 1 ULN"), ("715", "ivc_clear", "下腔静脉未受侵")]:
        _, bundle = run(cid, [{"text": text}], answer(atom, text))
        assert not bundle["entry"]


def test_cross_event_rescue_does_not_join_pathology():
    reports = [{"text": "病理报告", "event_id": "A"},
               {"text": "确诊弥漫性大细胞B淋巴瘤", "event_id": "B"}]
    _, bundle = run("495", reports, answer("dlbcl", reports[1]["text"], 1))
    assert not bundle["entry"]


def test_single_profile_preserves_and_resources():
    _, bundle = run("3", [{"text": "病理证实肝细胞癌，已行肝癌根治性切除R0"}], "NO", "B4S")
    assert {e["resource"]["resourceType"] for e in bundle["entry"]} == {"Procedure", "Condition"}


def test_item_fallback_targets_only_missing_atoms():
    ns = namespace("495", "B4I")
    g = ns["FHIRResourceBundleGenerator"]("http://localhost:3456")
    prompts = []
    def transport(prompt):
        prompts.append(json.loads(prompt))
        return answer("dlbcl", "确诊弥漫性大细胞B淋巴瘤")
    g.transport = transport
    assert g.parse_clinical_text_to_fhir_bundle("p1", [{"text": "病理报告。确诊弥漫性大细胞B淋巴瘤"}])["entry"]
    assert [p["requested_atoms"] for p in prompts] == [["dlbcl"]]


def test_embedded_transport_config_and_timeout(monkeypatch):
    ns = namespace()
    seen = []
    def timeout(request, timeout):
        seen.append((request.full_url, timeout, json.loads(request.data)))
        raise TimeoutError("controlled")
    monkeypatch.setitem(ns, "urlopen", timeout)
    g = ns["FHIRResourceBundleGenerator"]("http://localhost:3456")
    assert not g.parse_clinical_text_to_fhir_bundle("p1", [{"text": "活动后透不过气"}])["entry"]
    assert seen[0][0] == "http://127.0.0.1:1213/v1/chat/completions"
    assert seen[0][2]["max_tokens"] == 2048
    assert g.model_metrics["errors"][0]["kind"] == "TIMEOUT"


@pytest.mark.parametrize("cid", ["2","3","85","205","225","255","295","465","475","495","525","585","625","695","715","765"])
def test_empty_input_never_calls_model(cid):
    g, bundle = run(cid, [], answer())
    assert not bundle["entry"]
    assert g.model_metrics["calls"] == 0
