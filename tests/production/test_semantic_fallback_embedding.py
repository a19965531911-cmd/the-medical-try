import base64
import dataclasses
import json
from pathlib import Path

import pytest

from v43.extraction.semantic import CallGuard
from v43.production_runtime import evaluate_and_compile as evaluate_development


ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = ROOT / "submission" / "a_test_message_bundle_v4_3_candidate_v3.json"
PARAPHRASES = {
    "185": ("患者已完成该拓扑异构酶抑制剂的首剂治疗", "记录显示这是此抗肿瘤方案的首次实际实施"),
    "675": ("患者年逾五旬，颜面出现水痘病毒再激活性皮疹", "高龄患者此次成簇疱性皮损沿面部神经分布"),
    "745": ("麻醉苏醒阶段经人工气道接受正压呼吸支持", "术毕患者进入人工气道辅助呼吸阶段"),
    "875": ("患者当前神志障碍，不能清楚应答", "查房时发现患者处于意识障碍状态"),
}


def _namespace(criterion):
    bundle = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    resource = next(e["resource"] for e in bundle["entry"] if e["resource"].get("resourceType") == "Library" and str(e["resource"]["content"][0]["title"]) == criterion)
    source = base64.b64decode(resource["content"][0]["data"], validate=True).decode("utf-8")
    namespace = {}
    exec(compile(source, resource["name"], "exec"), namespace)
    return source, namespace


def _objects(namespace, criterion, span_id):
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


def _serialize(value):
    result = dataclasses.asdict(value)
    if "state" in result:
        result["state"] = result["state"].value
    return result


class _Transport:
    def __init__(self, namespace, criterion, grounded=True):
        self.namespace = namespace
        self.criterion = criterion
        self.grounded = grounded
        self.calls = 0

    def post(self, payload, timeout):
        self.calls += 1
        prompt = json.loads(payload["messages"][0]["content"])
        span_id = prompt["evidence_packet"][0]["span_id"] if self.grounded else "unknown-span"
        facts, events, relations = _objects(self.namespace, self.criterion, span_id)
        return {"facts": [_serialize(x) for x in facts], "events": [_serialize(x) for x in events], "relations": [_serialize(x) for x in relations]}


@pytest.mark.parametrize("criterion", ("185", "675", "745", "875"))
def test_semantic_paraphrases_are_grounded_and_called_once(criterion):
    source, namespace = _namespace(criterion)
    assert "CallGuard" in source and "validate_grounding" in source
    for text in PARAPHRASES[criterion]:
        transport = _Transport(namespace, criterion)
        trace, _, resources = namespace["evaluate_and_compile"](criterion, "p1", [{"text": text, "timestamp": "2026-01-01"}], "EVER_PRESENT", transport, namespace["CallGuard"]())
        assert transport.calls == 1
        assert trace.eligibility_result.value == "SATISFIED"
        assert resources


@pytest.mark.parametrize("criterion", ("185", "675", "745", "875"))
def test_development_and_flattened_production_semantic_parity(criterion):
    _, namespace = _namespace(criterion)
    for text in PARAPHRASES[criterion]:
        reports = [{"text": text, "timestamp": "2026-01-01"}]
        development_transport = _Transport(namespace, criterion)
        development, _, _ = evaluate_development(criterion, "p1", reports, semantic_transport=development_transport, call_guard=CallGuard())
        production_transport = _Transport(namespace, criterion)
        production, _, _ = namespace["evaluate_and_compile"](criterion, "p1", reports, "EVER_PRESENT", production_transport, namespace["CallGuard"]())
        assert development_transport.calls == production_transport.calls == 1
        assert development.eligibility_result.value == production.eligibility_result.value == "SATISFIED"


def test_unknown_span_is_rejected_and_cached_by_call_guard():
    _, namespace = _namespace("875")
    transport = _Transport(namespace, "875", grounded=False)
    guard = namespace["CallGuard"]()
    reports = [{"text": PARAPHRASES["875"][0], "timestamp": "2026-01-01"}]
    for _ in range(2):
        trace, _, resources = namespace["evaluate_and_compile"]("875", "p1", reports, "EVER_PRESENT", transport, guard)
        assert trace.eligibility_result.value == "INSUFFICIENT_EVIDENCE"
        assert not resources
    assert transport.calls == 1


@pytest.mark.parametrize("criterion", ("165", "265", "485", "555", "565", "615", "635", "735", "755", "805", "835", "855"))
def test_structured_criteria_never_call_semantic_transport(criterion):
    _, namespace = _namespace(criterion)
    transport = _Transport(namespace, criterion)
    namespace["evaluate_and_compile"](criterion, "p1", [{"text": "证据待补充", "timestamp": "2026-01-01"}], "EVER_PRESENT", transport, namespace["CallGuard"]())
    assert transport.calls == 0
