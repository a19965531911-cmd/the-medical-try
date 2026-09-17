import pytest

from v5.models import Decision
from v5.response_parser import parse_response


@pytest.mark.parametrize("value", (
    '{"decision":"MATCH","extra":"harmless"}',
    '```json\n{"decision":"MATCH","evidence":"x"}\n```',
    'Clinical summary:\nMATCH\nEVIDENCE: x',
    ' MATCH\nEvidence: x ',
    '符合。依据：支持。',
))
def test_v4_online_response_shapes_recover_match(value):
    assert parse_response(value).decision is Decision.MATCH
