from src.v3_engine.core import safe_rescue


def result(**overrides):
    payload = {
        "match": True,
        "confidence": "high",
        "subject": "patient",
        "negated": False,
        "planned": False,
        "uncertain": False,
        "evidence": ["活动性乙肝"],
        "facts": {},
        "reason": "grounded synthetic example",
    }
    payload.update(overrides)
    return payload


def test_grounded_synthetic_result_can_be_rescued():
    assert safe_rescue(result(), "患者目前活动性乙肝")


def test_family_or_planned_result_cannot_be_rescued():
    text = "患者目前活动性乙肝"
    assert not safe_rescue(result(subject="family"), text)
    assert not safe_rescue(result(planned=True), text)


def test_evidence_must_be_grounded_in_source():
    assert not safe_rescue(result(evidence=["不存在的证据"]), "患者目前活动性乙肝")
