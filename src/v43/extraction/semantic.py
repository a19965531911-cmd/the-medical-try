from dataclasses import asdict
import json

from v43.clinical.models import AssertionState, ClinicalEvent, ClinicalFact, ClinicalRelation
from .grounding import validate_grounding


class SemanticExtractionError(ValueError):
    def __init__(self, reason_code: str, message: str):
        super().__init__(message)
        self.reason_code = reason_code


class CallGuard:
    def __init__(self):
        self._cache = {}

    def get(self, key):
        return self._cache.get(key)

    def put(self, key, value):
        self._cache[key] = value

    def reserve(self, key):
        if key in self._cache:
            return False
        self._cache[key] = RuntimeError("semantic call already in progress")
        return True


_FORBIDDEN = {"eligible", "match", "qualified", "final_decision"}


def _contains_forbidden(value):
    if isinstance(value, dict):
        return bool(_FORBIDDEN.intersection(value)) or any(_contains_forbidden(v) for v in value.values())
    if isinstance(value, list):
        return any(_contains_forbidden(v) for v in value)
    return False


def _content(response):
    if "choices" not in response:
        return response
    try:
        value = response["choices"][0]["message"]["content"]
        return json.loads(value) if isinstance(value, str) else value
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise SemanticExtractionError("SCHEMA_REJECT", "invalid semantic response envelope") from exc


def _parse(data):
    if not isinstance(data, dict) or set(data) != {"facts", "events", "relations"} or _contains_forbidden(data):
        raise SemanticExtractionError("SCHEMA_REJECT", "semantic output violates allowed schema")
    try:
        facts = tuple(ClinicalFact(**{**item, "state": AssertionState(item["state"]), "source": "semantic"}) for item in data["facts"])
        events = tuple(ClinicalEvent(**{**item, "evidence_span_ids": tuple(item["evidence_span_ids"]),
                                       "report_indices": tuple(item["report_indices"]), "source": "semantic"}) for item in data["events"])
        relations = tuple(ClinicalRelation(**{**item, "state": AssertionState(item["state"]),
                                              "evidence_span_ids": tuple(item["evidence_span_ids"]),
                                              "report_indices": tuple(item["report_indices"]), "source": "semantic"}) for item in data["relations"])
    except (KeyError, TypeError, ValueError) as exc:
        raise SemanticExtractionError("SCHEMA_REJECT", "invalid typed semantic object") from exc
    return facts, events, relations


def extract_semantic(ir, packet, transport, call_guard, *, patient_id: str, timeout: float = 30.0):
    key = (patient_id, ir.criterion_id)
    cached = call_guard.get(key)
    if cached is not None:
        if isinstance(cached, BaseException):
            raise cached
        return cached
    call_guard.reserve(key)
    prompt = {
        "criterion_ir": ir.raw,
        "criterion_summary": {"title": ir.title, "original_text": ir.original_text},
        "evidence_packet": [asdict(span) for span in packet.spans],
        "allowed_output": {"facts": "ClinicalFact[]", "events": "ClinicalEvent[]", "relations": "ClinicalRelation[]"},
        "forbidden_keys": sorted(_FORBIDDEN),
    }
    payload = {"model": "local-model", "temperature": 0,
               "messages": [{"role": "user", "content": json.dumps(prompt, ensure_ascii=False)}]}
    try:
        result = _parse(_content(transport.post(payload, timeout)))
        validate_grounding((*result[0], *result[1], *result[2]), packet)
    except SemanticExtractionError as exc:
        call_guard.put(key, exc)
        raise
    except ValueError as exc:
        error = SemanticExtractionError("GROUNDING_REJECT", str(exc))
        call_guard.put(key, error)
        raise error from exc
    except BaseException as exc:
        call_guard.put(key, exc)
        raise
    call_guard.put(key, result)
    return result
