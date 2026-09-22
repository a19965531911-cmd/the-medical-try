import pytest

from v5.models import Decision, ParseMethod
from v5.response_parser import parse_response


@pytest.mark.parametrize("value,decision", (
    ("MATCH", Decision.MATCH),
    (" MATCH\nEVIDENCE: supported ", Decision.MATCH),
    ("NO_MATCH\nEVIDENCE_REPORTS: 0", Decision.NO_MATCH),
    ("UNKNOWN", Decision.UNKNOWN),
    ("```text\nMATCH\nEVIDENCE: x\n```", Decision.MATCH),
))
def test_parses_canonical_first_line(value, decision):
    result = parse_response(value)
    assert result.decision is decision
    assert result.method is ParseMethod.PARSED_SENTINEL


@pytest.mark.parametrize("value,decision", (
    ('{"decision":"MATCH","extra":"harmless"}', Decision.MATCH),
    ('```json\n{"decision":"NO_MATCH","evidence":"x"}\n```', Decision.NO_MATCH),
    ({"decision": "UNKNOWN", "other": 1}, Decision.UNKNOWN),
    ({"match": True}, Decision.MATCH),
    ({"match": False}, Decision.NO_MATCH),
))
def test_parses_explicit_json_decisions(value, decision):
    result = parse_response(value)
    assert result.decision is decision
    assert result.method is ParseMethod.PARSED_JSON


@pytest.mark.parametrize("value,decision", (
    ("符合", Decision.MATCH),
    ("符合。依据：病历明确支持。", Decision.MATCH),
    ("不符合", Decision.NO_MATCH),
    ("无法判断", Decision.UNKNOWN),
))
def test_parses_unambiguous_chinese(value, decision):
    result = parse_response(value)
    assert result.decision is decision
    assert result.method is ParseMethod.PARSED_CHINESE


@pytest.mark.parametrize("value", (
    "the text may match in another context",
    "MATCH and NO_MATCH",
    "无法判断是否符合",
    "explanation only",
    "{bad json",
    "",
    None,
    {"decision": "YES"},
    {"match": "true"},
))
def test_ambiguous_or_malformed_values_become_unknown(value):
    result = parse_response(value)
    assert result.decision is Decision.UNKNOWN
    assert result.method is ParseMethod.PARSE_UNKNOWN


def test_leading_explanation_accepts_only_distinct_sentinel_line():
    result = parse_response("简要结论如下：\nMATCH\nEVIDENCE: x")
    assert result.decision is Decision.MATCH
    assert result.method is ParseMethod.PARSED_SENTINEL
