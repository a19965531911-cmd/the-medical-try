"""Dependency-free production gates for the V4.3 flattened candidate."""
from __future__ import annotations

import base64
from copy import deepcopy
import dataclasses
import hashlib
import inspect
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from v43.fhir.compiler import FHIRCompileResult
from v43.fhir.contracts import contract_for_criterion
from v43.fhir.service_replay import replay_service
from v43.fhir.validator import validate_fhir
from v43.extraction.semantic import CallGuard
from v43.production_runtime import evaluate_and_compile as evaluate_development


CANDIDATE = ROOT / "submission" / "a_test_message_bundle_v4_3_candidate_v3.json"
SHELL = ROOT.parent / "CHIP2026_CP2_A_baseline_v2_4_3" / "submission" / "a_test_message_bundle_v2_4_3.json"
CRITERIA = ("485", "615", "265", "635", "675", "735", "745", "755", "855", "835", "875", "805", "565", "555", "185", "165")
SEMANTIC = {"185", "675", "745", "875"}
POSITIVE = {
    "485": "盆腔器官脱垂，POP-Q III期", "615": "术后病理pN1", "265": "术前cTnI 0.08 μg/L",
    "635": "AST 30 U/L上限40，ALT 30 U/L上限40，BUN 8 mmol/L上限9，Cr 80 umol/L上限100",
    "675": "患者70岁，确诊头面部带状疱疹", "735": "活动性乙型肝炎", "745": "术后行有创机械通气",
    "755": "机械通气持续30小时", "855": "Scr 120 μmol/L，BUN 7 mmol/L，ALT 30 U/L上限40，AST 25 U/L上限40",
    "835": "目前凝血功能异常", "875": "目前意识不清", "805": "目前每日吸烟", "565": "目前严重腹泻",
    "555": "3个月前行胆囊切除术", "185": "首次接受伊立替康化疗", "165": "转入我院前于当地医院完成2周期化疗",
}
PARAPHRASES = {
    "185": ("患者已完成该拓扑异构酶抑制剂的首剂治疗", "记录显示这是此抗肿瘤方案的首次实际实施"),
    "675": ("患者年逾五旬，颜面出现水痘病毒再激活性皮疹", "高龄患者此次成簇疱性皮损沿面部神经分布"),
    "745": ("麻醉苏醒阶段经人工气道接受正压呼吸支持", "术毕患者进入人工气道辅助呼吸阶段"),
    "875": ("患者当前神志障碍，不能清楚应答", "查房时发现患者处于意识障碍状态"),
}
BRANCHES = {
    "615": ("病理分期pT3a", "切缘R1", "术后病理pN1", "Gleason评分8分", "PSA 0.2 ng/mL"),
    "805": ("目前每日吸烟", "戒烟1年"),
}
HOST_LIKE = re.compile(r"['\"]([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})['\"]")


def load_libraries():
    bundle = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    libraries = {}
    for entry in bundle["entry"]:
        resource = entry["resource"]
        if resource.get("resourceType") != "Library":
            continue
        criterion = str(resource["content"][0]["title"])
        source = base64.b64decode(resource["content"][0]["data"], validate=True).decode("utf-8")
        namespace = {}
        exec(compile(source, resource["name"], "exec"), namespace)
        libraries[criterion] = (resource, source, namespace)
    assert tuple(libraries) == CRITERIA
    return bundle, libraries


def semantic_objects(namespace, criterion, span_id):
    state = namespace["AssertionState"]
    fact = lambda fid, concept, value=True, unit=None: namespace["ClinicalFact"](fid, "assertion", concept, value, unit, state.PRESENT, "patient", "current", None, span_id, 0, 1.0, "semantic")
    event = lambda eid, kind, concept, attrs={}: namespace["ClinicalEvent"](eid, kind, concept, "occurred", attrs, "patient", "2026-01-01", None, "current", None, (span_id,), (0,), 1.0, "semantic")
    relation = lambda rid, source, target, kind: namespace["ClinicalRelation"](rid, source, target, kind, state.PRESENT, (span_id,), (0,), 1.0, "semantic")
    if criterion == "185":
        return (), (event("admin", "MedicationAdministration", "irinotecan", {"first_use": "PRESENT", "planned_only": "ABSENT", "previous_multiple_use": "ABSENT"}),), ()
    if criterion == "675":
        return (fact("age", "patient_age", 60, "year"), fact("site", "head_face_site", "head_face")), (event("dx", "Diagnosis", "herpes_zoster"),), (relation("loc", "dx", "site", "LOCATED_AT"),)
    if criterion == "745":
        return (), (event("s", "Surgery", "Surgery"), event("v", "MechanicalVentilation", "MechanicalVentilation", {"invasive": "PRESENT"})), (relation("post", "v", "s", "POSTOPERATIVE_TO"),)
    return (fact("ci", "consciousness_impairment"),), (), ()


def serialize(value):
    result = dataclasses.asdict(value)
    if "state" in result:
        result["state"] = result["state"].value
    return result


class Transport:
    def __init__(self, namespace, criterion, grounded=True):
        self.namespace, self.criterion, self.grounded, self.calls = namespace, criterion, grounded, 0

    def post(self, payload, timeout):
        self.calls += 1
        prompt = json.loads(payload["messages"][0]["content"])
        assert payload["model"] == "local-model" and payload["temperature"] == 0
        span_id = prompt["evidence_packet"][0]["span_id"] if self.grounded else "unknown-span"
        facts, events, relations = semantic_objects(self.namespace, self.criterion, span_id)
        return {"facts": [serialize(x) for x in facts], "events": [serialize(x) for x in events], "relations": [serialize(x) for x in relations]}


def resources(namespace, criterion, text, transport=None, guard=None):
    return namespace["evaluate_and_compile"](criterion, "p1", [{"text": text, "timestamp": "2026-01-01"}], "EVER_PRESENT", transport, guard)


def normalize_shell(bundle):
    result = deepcopy(bundle)
    for entry in result["entry"]:
        if entry["resource"].get("resourceType") == "Library":
            entry["resource"]["content"][0]["data"] = "<library-source>"
    return result


def main():
    bundle, libraries = load_libraries()
    assert normalize_shell(bundle) == normalize_shell(json.loads(SHELL.read_text(encoding="utf-8")))
    print("SHELL_PARITY 16/16 PASS")

    for criterion, (_, source, namespace) in libraries.items():
        assert tuple(inspect.signature(namespace["FHIRResourceBundleGenerator"].parse_clinical_text_to_fhir_bundle).parameters) == ("self", "patient_id", "case_reports", "ai_algorithm_type")
        assert not any(token in source for token in ("VERIFIED_MODULE_SOURCES", "VERIFIED_PACKAGES", "_VerifiedCoreLoader", "input("))
        hits = HOST_LIKE.findall(source)
        assert not [hit for hit in hits if hit.startswith("v43.") or hit not in {"127.0.0.1", "localhost"}]
        assert "http://127.0.0.1:1213/v1/chat/completions" in source
        assert re.search(r"['\"]model['\"]\s*:\s*['\"]local-model['\"]", source)
        trace, _, compiled = resources(namespace, criterion, POSITIVE[criterion], Transport(namespace, criterion))
        assert trace.eligibility_result.value == "SATISFIED" and compiled, (criterion, trace.eligibility_result.value, len(compiled))
        contract = contract_for_criterion(criterion)
        assert validate_fhir(FHIRCompileResult("SATISFIED", "COMPILED", compiled), contract).structural_status == "VALID"
        assert replay_service(compiled, contract.service, "fixture://fhir", {"p1": "doc"}).status == "SERVICE_HIT"
    print("SECURITY_PREFLIGHT 16/16 PASS")
    print("FHIR_STRUCTURAL 16/16 PASS")
    print("SERVICE_REPLAY 16/16 PASS")

    for criterion in set(CRITERIA) - SEMANTIC:
        namespace = libraries[criterion][2]
        transport = Transport(namespace, criterion)
        resources(namespace, criterion, "证据待补充", transport, namespace["CallGuard"]())
        assert transport.calls == 0
    print("STRUCTURED_ZERO_SEMANTIC_CALLS 12/12 PASS")

    semantic_count = 0
    parity_count = 0
    for criterion, fixtures in PARAPHRASES.items():
        namespace = libraries[criterion][2]
        for text in fixtures:
            reports = [{"text": text, "timestamp": "2026-01-01"}]
            transport = Transport(namespace, criterion)
            trace, _, compiled = namespace["evaluate_and_compile"](criterion, "p1", reports, "EVER_PRESENT", transport, namespace["CallGuard"]())
            assert transport.calls == 1 and trace.eligibility_result.value == "SATISFIED" and compiled, (criterion, text, transport.calls, trace.eligibility_result.value, len(compiled))
            development_transport = Transport(namespace, criterion)
            development, _, _ = evaluate_development(criterion, "p1", reports, semantic_transport=development_transport, call_guard=CallGuard())
            assert development_transport.calls == 1
            assert development.eligibility_result.value == trace.eligibility_result.value
            semantic_count += 1
            parity_count += 1
    print(f"SEMANTIC_PARAPHRASE {semantic_count}/8 PASS")
    print(f"DEVELOPMENT_PRODUCTION_PARITY {parity_count}/8 PASS")

    namespace = libraries["875"][2]
    transport = Transport(namespace, "875", grounded=False)
    guard = namespace["CallGuard"]()
    for _ in range(2):
        trace, _, compiled = resources(namespace, "875", PARAPHRASES["875"][0], transport, guard)
        assert trace.eligibility_result.value == "INSUFFICIENT_EVIDENCE" and not compiled
    assert transport.calls == 1
    print("GROUNDING_AND_ONE_CALL PASS")

    for criterion, fixtures in BRANCHES.items():
        namespace = libraries[criterion][2]
        contract = contract_for_criterion(criterion)
        for text in fixtures:
            trace, _, compiled = resources(namespace, criterion, text)
            assert trace.eligibility_result.value == "SATISFIED"
            assert replay_service(compiled, contract.service, "fixture://fhir", {"p1": "doc"}).status == "SERVICE_HIT"
        print(f"BRANCH_SERVICE_{criterion} {len(fixtures)}/{len(fixtures)} PASS")

    digest = hashlib.sha256(CANDIDATE.read_bytes()).hexdigest().upper()
    print(f"CANDIDATE_BYTES {CANDIDATE.stat().st_size}")
    print(f"CANDIDATE_SHA256 {digest}")


if __name__ == "__main__":
    main()
