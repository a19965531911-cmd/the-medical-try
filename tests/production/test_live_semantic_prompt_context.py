import base64
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
from urllib.error import HTTPError

import pytest

from v43.runtime import RuntimeServices, evaluate_criterion


ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = ROOT / "submission" / "a_test_message_bundle_v4_3_candidate_v4.json"
EXPECTED = {
    "185": "根据NCCN指南，首次应用包含伊立替康的化疗方案治疗",
    "675": "年龄50岁以上并确诊头面部带状疱疹",
    "745": "术后需要有创机械通气",
    "875": "颅内高压或意识不清",
}
UNKNOWN_TEXT = {
    "185": "患者已完成该拓扑异构酶抑制剂的首剂治疗",
    "675": "患者年逾五旬，颜面出现水痘病毒再激活性皮疹",
    "745": "麻醉苏醒阶段经人工气道接受正压呼吸支持",
    "875": "患者当前神志障碍，不能清楚应答",
}
SEMANTIC_FIELDS = {
    "criterion_id", "original_text", "criterion_type", "clinical_domain", "entities",
    "constraint_semantics", "fact_schema", "event_schema", "relation_schema", "relations",
    "logical_expression",
}


class RecordingTransport:
    def __init__(self):
        self.calls = []

    def post(self, payload, timeout):
        self.calls.append((payload, timeout))
        return {"facts": [], "events": [], "relations": []}


def _prompt(transport):
    return json.loads(transport.calls[0][0]["messages"][0]["content"])


def _namespaces(candidate):
    bundle = json.loads(candidate.read_text(encoding="utf-8"))
    result = {}
    for entry in bundle["entry"]:
        resource = entry["resource"]
        if resource.get("resourceType") != "Library":
            continue
        criterion = str(resource["content"][0]["title"])
        if criterion not in EXPECTED:
            continue
        source = base64.b64decode(resource["content"][0]["data"], validate=True).decode("utf-8")
        namespace = {}
        exec(compile(source, resource["name"], "exec"), namespace)
        result[criterion] = namespace
    return result


def assert_live_prompt_context(candidate):
    for criterion, namespace in _namespaces(candidate).items():
        transport = RecordingTransport()
        namespace["evaluate_and_compile"](
            criterion, "p1", [{"text": UNKNOWN_TEXT[criterion], "timestamp": "2026-01-01"}],
            "EVER_PRESENT", transport, namespace["CallGuard"](),
        )
        assert len(transport.calls) == 1
        payload, timeout = transport.calls[0]
        prompt = json.loads(payload["messages"][0]["content"])
        assert timeout == 30.0
        assert prompt["criterion_ir"] and SEMANTIC_FIELDS <= set(prompt["criterion_ir"])
        assert prompt["criterion_ir"]["criterion_id"] == criterion
        assert prompt["criterion_ir"]["original_text"] == EXPECTED[criterion]
        assert prompt["criterion_summary"]["original_text"] == EXPECTED[criterion]
        assert prompt["criterion_summary"]["title"] != criterion
        assert prompt["criterion_ir"]["entities"]
        assert prompt["criterion_ir"]["constraint_semantics"]
        assert prompt["criterion_ir"]["event_schema"] or prompt["criterion_ir"]["fact_schema"]
        assert prompt["allowed_output"] == {
            "facts": "ClinicalFact[]", "events": "ClinicalEvent[]", "relations": "ClinicalRelation[]"
        }


def test_live_semantic_prompt_contains_reviewed_context():
    assert_live_prompt_context(CANDIDATE)


def test_development_and_production_prompt_semantics_match():
    for criterion, namespace in _namespaces(CANDIDATE).items():
        reports = [{"text": UNKNOWN_TEXT[criterion], "timestamp": "2026-01-01"}]
        development_transport = RecordingTransport()
        evaluate_criterion(criterion, "p1", reports, RuntimeServices(development_transport, 30.0, "EVER_PRESENT"))
        production_transport = RecordingTransport()
        namespace["evaluate_and_compile"](
            criterion, "p1", reports, "EVER_PRESENT", production_transport, namespace["CallGuard"](),
        )
        development = _prompt(development_transport)
        production = _prompt(production_transport)
        assert {field: development["criterion_ir"][field] for field in SEMANTIC_FIELDS} == {
            field: production["criterion_ir"][field] for field in SEMANTIC_FIELDS
        }
        assert development["criterion_summary"] == production["criterion_summary"]
        assert development["allowed_output"] == production["allowed_output"]


class PromptAwareTransport(RecordingTransport):
    def post(self, payload, timeout):
        self.calls.append((payload, timeout))
        prompt = json.loads(payload["messages"][0]["content"])
        raw = prompt["criterion_ir"]
        assert SEMANTIC_FIELDS <= set(raw)
        assert raw["original_text"] in EXPECTED.values()
        assert raw["entities"] and raw["constraint_semantics"]
        evidence = prompt["evidence_packet"]
        assert evidence and evidence[0]["text"]
        span = evidence[0]["span_id"]
        common_fact = {
            "fact_type": "assertion", "unit": None, "state": "PRESENT", "subject": "patient",
            "temporality": "current", "clinical_time": None, "evidence_span_id": span,
            "report_index": 0, "confidence": 1.0,
        }
        common_event = {
            "status": "occurred", "subject": "patient", "start_time": "2026-01-01",
            "end_time": None, "temporality": "current", "episode_id": None,
            "evidence_span_ids": [span], "report_indices": [0], "confidence": 1.0,
        }
        common_relation = {
            "state": "PRESENT", "evidence_span_ids": [span], "report_indices": [0], "confidence": 1.0,
        }
        original = raw["original_text"]
        if "伊立替康" in original:
            return {"facts": [], "events": [{**common_event, "event_id": "admin", "event_type": "MedicationAdministration", "concept": "irinotecan", "attributes": {"first_use": "PRESENT", "planned_only": "ABSENT", "previous_multiple_use": "ABSENT"}}], "relations": []}
        if "带状疱疹" in original:
            facts = [
                {**common_fact, "fact_id": "age", "concept": "patient_age", "value": 60, "unit": "year"},
                {**common_fact, "fact_id": "site", "concept": "head_face_site", "value": "head_face"},
            ]
            event = {**common_event, "event_id": "dx", "event_type": "Diagnosis", "concept": "herpes_zoster", "attributes": {}}
            relation = {**common_relation, "relation_id": "loc", "source_node": "dx", "target_node": "site", "relation_type": "LOCATED_AT"}
            return {"facts": facts, "events": [event], "relations": [relation]}
        if "机械通气" in original:
            events = [
                {**common_event, "event_id": "s", "event_type": "Surgery", "concept": "Surgery", "attributes": {}},
                {**common_event, "event_id": "v", "event_type": "MechanicalVentilation", "concept": "MechanicalVentilation", "attributes": {"invasive": "PRESENT"}},
            ]
            relation = {**common_relation, "relation_id": "post", "source_node": "v", "target_node": "s", "relation_type": "POSTOPERATIVE_TO"}
            return {"facts": [], "events": events, "relations": [relation]}
        fact = {**common_fact, "fact_id": "ci", "concept": "consciousness_impairment", "value": True}
        return {"facts": [fact], "events": [], "relations": []}


def test_prompt_aware_semantic_smoke_satisfies_all_four():
    for criterion, namespace in _namespaces(CANDIDATE).items():
        transport = PromptAwareTransport()
        output = io.StringIO()
        with redirect_stdout(output):
            trace, _, resources = namespace["evaluate_and_compile"](
                criterion, "p1", [{"text": UNKNOWN_TEXT[criterion], "timestamp": "2026-01-01"}],
                "EVER_PRESENT", transport, namespace["CallGuard"](),
            )
        assert len(transport.calls) == 1
        assert trace.eligibility_result.value == "SATISFIED" and resources
        assert "semantic_called=1|semantic_success=1|semantic_reason=SUCCESS" in output.getvalue()


@pytest.mark.parametrize("failure,reason", (
    (TimeoutError("offline"), "TIMEOUT"),
    (HTTPError("http://127.0.0.1", 503, "offline", {}, None), "HTTP_ERROR"),
    (json.JSONDecodeError("bad", "x", 0), "INVALID_JSON"),
))
def test_semantic_transport_failures_are_observable_and_fail_safe(failure, reason):
    namespace = _namespaces(CANDIDATE)["875"]

    class FailingTransport:
        def post(self, payload, timeout):
            raise failure

    output = io.StringIO()
    with redirect_stdout(output):
        trace, _, resources = namespace["evaluate_and_compile"](
            "875", "p1", [{"text": UNKNOWN_TEXT["875"], "timestamp": "2026-01-01"}],
            "EVER_PRESENT", FailingTransport(), namespace["CallGuard"](),
        )
    assert trace.eligibility_result.value == "INSUFFICIENT_EVIDENCE" and not resources
    assert "semantic_called=1|semantic_success=0|semantic_reason=" + reason in output.getvalue()


@pytest.mark.parametrize("response,reason", (
    ({"unexpected": []}, "SCHEMA_REJECT"),
    ({"facts": [{
        "fact_id": "bad", "fact_type": "assertion", "concept": "consciousness_impairment",
        "value": True, "unit": None, "state": "PRESENT", "subject": "patient",
        "temporality": "current", "clinical_time": None, "evidence_span_id": "unknown-span",
        "report_index": 0, "confidence": 1.0,
    }], "events": [], "relations": []}, "GROUNDING_REJECT"),
))
def test_semantic_rejections_are_observable_and_fail_safe(response, reason):
    namespace = _namespaces(CANDIDATE)["875"]

    class ResponseTransport:
        def post(self, payload, timeout): return response

    output = io.StringIO()
    with redirect_stdout(output):
        trace, _, resources = namespace["evaluate_and_compile"](
            "875", "p1", [{"text": UNKNOWN_TEXT["875"], "timestamp": "2026-01-01"}],
            "EVER_PRESENT", ResponseTransport(), namespace["CallGuard"](),
        )
    assert trace.eligibility_result.value == "INSUFFICIENT_EVIDENCE" and not resources
    assert "semantic_called=1|semantic_success=0|semantic_reason=" + reason in output.getvalue()
