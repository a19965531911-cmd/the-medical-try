import base64
import json
from dataclasses import replace
from pathlib import Path

from v43.fhir.compiler import FHIRCompileResult
from v43.fhir.contracts import contract_for_criterion
from v43.fhir.service_replay import replay_service
from v43.fhir.validator import validate_fhir
import v5s.runtime_template as runtime
from v5s.runtime_template import extract_payload, retrieve_evidence

ROOT = Path(__file__).resolve().parents[2]


def test_group_aware_retrieval_reserves_late_required_group_and_reports_metrics():
    spec = {"aliases": ["early", "decisive"], "groups": [["early"], ["decisive"]]}
    reports = [{"index": 0, "text": "early. " * 20 + "decisive."}]
    windows = retrieve_evidence(reports, spec)
    assert len(windows) <= 8
    assert any("decisive" in item["text"] for item in windows)
    assert windows.metrics["groups_required"] == 2
    assert windows.metrics["groups_hit"] == 2
    assert windows.metrics["group_ids_hit"] == [0, 1]
    assert windows.metrics["fallback_used"] is False
    assert windows.metrics["true_anchor_hits"] >= 2


def test_485_stage_iv_is_visible_to_the_stage_iv_scorer_contract():
    payload = extract_payload("485", [], "MATCH", [{"text": "POP-Q IV"}])
    old, old_profile = runtime.BASE, runtime.PROFILE
    runtime.BASE = "http://localhost:3456/api/terminology/"
    runtime.PROFILE = contract_for_criterion("485").profiles[0]
    try:
        resources = runtime.build_resources("485", "p1", payload)
    finally:
        runtime.BASE, runtime.PROFILE = old, old_profile
    service = contract_for_criterion("485").service
    assert replay_service(tuple(resources), service, "fixture://fhir", {"p1": "p1"}).status == "SERVICE_HIT"


def test_875_consciousness_uses_the_consciousness_profile_and_code():
    payload = extract_payload("875", [], "MATCH", [{"text": "consciousness impairment"}])
    old_base, old_profile, old_profiles = runtime.BASE, runtime.PROFILE, runtime.PROFILES
    contract = contract_for_criterion("875")
    runtime.BASE = "http://localhost:3456/api/terminology/"
    runtime.PROFILE = contract.profiles[0]
    runtime.PROFILES = {"intracranial": contract.profiles[0], "consciousness": contract.profiles[1]}
    try:
        resources = runtime.build_resources("875", "p1", payload)
    finally:
        runtime.BASE, runtime.PROFILE, runtime.PROFILES = old_base, old_profile, old_profiles
    resource = resources[0]
    assert resource["meta"]["profile"] == [contract.profiles[1]]
    assert resource["code"]["coding"][0]["system"].endswith("cnwqk875-unconsciousness-cs")
    assert replay_service(tuple(resources), replace(contract.service, profiles=(contract.service.profiles[1],)), "fixture://fhir", {"p1": "p1"}).status == "SERVICE_HIT"


def test_embedded_rules_are_criterion_specific_and_not_keyword_only():
    candidate = ROOT / "submission/a_test_message_bundle_v5s1_candidate.json"
    bundle = json.loads(candidate.read_text(encoding="utf-8"))
    rules = {}
    for entry in bundle["entry"]:
        resource = entry["resource"]
        if resource.get("resourceType") != "Library":
            continue
        source = base64.b64decode(resource["content"][0]["data"]).decode("utf-8")
        namespace = {}
        exec(compile(source, resource["name"], "exec"), namespace)
        rules[str(resource["content"][0]["title"])] = namespace["SPEC"]["rule"]
    assert "cTnI >= 0.06" in rules["265"] and "cTnT >= 0.03" in rules["265"]
    assert "POP-Q stage III OR IV" in rules["485"]
    assert "AST" in rules["635"] and "ULN" in rules["635"] and "AND" in rules["635"]
    assert "intracranial hypertension" in rules["875"] and "impaired consciousness" in rules["875"]
    assert all("keyword-only" not in rule for rule in rules.values())


def _embedded(cid):
    bundle = json.loads((ROOT / "submission/a_test_message_bundle_v5s1_candidate.json").read_text(encoding="utf-8"))
    for entry in bundle["entry"]:
        resource = entry["resource"]
        if resource.get("resourceType") == "Library" and str(resource["content"][0]["title"]) == cid:
            source = base64.b64decode(resource["content"][0]["data"]).decode("utf-8")
            namespace = {}
            exec(compile(source, resource["name"], "exec"), namespace)
            return namespace
    raise AssertionError(cid)


def _run(cid, text, answer="YES"):
    namespace = _embedded(cid)
    generator = namespace["FHIRResourceBundleGenerator"]("http://localhost:3456")
    generator.transport = lambda prompt: answer
    import io
    from contextlib import redirect_stdout
    output = io.StringIO()
    with redirect_stdout(output):
        bundle = generator.parse_clinical_text_to_fhir_bundle("p1", [{"text": text}])
    return tuple(entry["resource"] for entry in bundle["entry"]), output.getvalue()


def test_retrieval_group_budget_same_report_cross_report_dedup_and_missing_group():
    spec = {"groups": [["g0"], ["g1"], ["g2"]], "aliases": ["g0", "g1", "g2"]}
    same = retrieve_evidence([{"index": 0, "text": "g0。" * 12 + "g1。g2。"}], spec)
    assert same.metrics["group_ids_hit"] == [0, 1, 2]
    assert len(same) <= 8
    split = retrieve_evidence([
        {"index": 0, "text": "g0。" * 12},
        {"index": 1, "text": "g1。"},
        {"index": 2, "text": "g2。"},
    ], spec)
    assert split.metrics["group_ids_hit"] == [0, 1, 2]
    assert {item["report"] for item in split} == {0, 1, 2}
    keys = [(item["report"], item["text"]) for item in split]
    assert len(keys) == len(set(keys))
    missing = retrieve_evidence([{"index": 0, "text": "g0。g2。"}], spec)
    assert missing.metrics["groups_required"] == 3
    assert missing.metrics["groups_hit"] == 2
    assert missing.metrics["group_ids_hit"] == [0, 2]


def test_635_fuses_complete_grounded_labs_across_windows_and_reports():
    windows = retrieve_evidence([
        {"index": 0, "text": "AST 30上限40。ALT 35上限40。"},
        {"index": 1, "text": "BUN 8上限9。Cr 180上限100。"},
    ], {"groups": [["AST"], ["ALT"], ["BUN"], ["Cr"]]})
    payload = extract_payload("635", [], "MATCH", windows)
    assert payload["labs"] == {"AST": (30.0, 40.0), "ALT": (35.0, 40.0), "BUN": (8.0, 9.0), "Cr": (180.0, 100.0)}


def test_numeric_semantic_yes_without_grounded_payload_is_explicitly_downgraded():
    for cid, text in (("265", "肌钙蛋白升高但未记录数值"), ("635", "四项化验符合但未记录数值及ULN")):
        resources, metrics = _run(cid, text, "YES")
        assert resources == ()
        assert "decision=NO_MATCH" in metrics
        assert "resources=0" in metrics
        assert "reason=MISSING_GROUNDED_PAYLOAD" in metrics


def test_all_positive_production_branches_are_structural_and_service_visible():
    cases = {
        "165": ["已在外院完成两周期化疗"],
        "185": ["首次接受伊立替康化疗"],
        "265": ["cTnI 0.08 ug/L", "cTnT 0.04 ug/L"],
        "485": ["POP-Q III期", "POP-Q IV期"],
        "555": ["3个月前完成胆囊切除术"],
        "565": ["目前严重腹泻", "目前严重便秘"],
        "615": ["pT3a", "pT3b", "pT4", "R1", "pN1", "GS 8", "PSA 0.2 ng/mL"],
        "635": ["AST 30上限40 ALT 35上限40 BUN 8上限9 Cr 180上限100"],
        "675": ["患者70岁确诊头面部带状疱疹"],
        "735": ["活动性乙型肝炎"],
        "745": ["术后行有创机械通气"],
        "755": ["机械通气持续30小时", "机械通气持续2天"],
        "805": ["目前每日吸烟", "戒烟1年"],
        "835": ["目前凝血功能异常"],
        "855": ["Scr 120 umol/L，BUN 7 mmol/L，ALT 30 U/L上限40，AST 25 U/L上限40"],
        "875": ["既往发生颅内高压", "既往发生意识障碍"],
    }
    for cid, texts in cases.items():
        contract = contract_for_criterion(cid)
        for text in texts:
            resources, metrics = _run(cid, text, "YES")
            assert resources, (cid, text, metrics)
            compiled = FHIRCompileResult("MATCH", "COMPILED", resources)
            assert validate_fhir(compiled, contract).structural_status == "VALID", (cid, text, resources)
            assert replay_service(resources, contract.service, "fixture://fhir", {"p1": "p1"}).status == "SERVICE_HIT", (cid, text, resources)
            assert "decision=MATCH" in metrics and "resources=0" not in metrics


def test_reserved_group_windows_are_the_actual_anchor_sentences_at_full_budget():
    groups = [[f"anchor-{index}"] for index in range(8)]
    reports = [{"index": index, "text": f"context-{index}。anchor-{index}。tail-{index}"} for index in range(8)]
    windows = retrieve_evidence(reports, {"groups": groups})
    assert len(windows) == 8
    for group_id, aliases in enumerate(groups):
        assert any(group_id in item.get("groups", []) and aliases[0] in item["text"] for item in windows)


def test_all_16_embedded_rules_preserve_required_semantic_fragments():
    required = {
        "165": ("外院", "完成"),
        "185": ("首次", "CPT-11", "给药"),
        "265": ("cTnI >= 0.06", "cTnT >= 0.03", "绑定"),
        "485": ("POP-Q stage III OR IV",),
        "555": ("6个月", "手术"),
        "565": ("严重腹泻", "严重便秘", "当前"),
        "615": ("pT3a", "pT3b", "pT4", "R1", "pN1", "GS >=8", "PSA >0.1"),
        "635": ("AST AND ALT AND BUN AND Cr", "ULN", "2*ULN", "完整"),
        "675": ("age >=50", "AND", "头面部"),
        "735": ("活动性", "历史", "不活动"),
        "745": ("术后", "有创机械通气", "关系"),
        "755": (">=24小时", "小时/天", "属于机械通气"),
        "805": ("当前吸烟", "戒烟未满2年"),
        "835": ("凝血功能障碍", "不设通用数值阈值"),
        "855": ("Scr <178", "BUN <9", "ALT <= ULN", "AST <= ULN", "绑定"),
        "875": ("intracranial hypertension", "impaired consciousness", "EVER_PRESENT"),
    }
    for cid, fragments in required.items():
        rule = _embedded(cid)["SPEC"]["rule"]
        assert all(fragment in rule for fragment in fragments), (cid, rule, fragments)
