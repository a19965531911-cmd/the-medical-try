import json
from urllib.error import HTTPError, URLError

import pytest

from v5.models import Decision, ParseMethod
from v5.transport import LocalModelTransport, TransportStatus


class SequenceRequest:
    def __init__(self, *items):
        self.items = list(items)
        self.calls = []

    def __call__(self, payload, timeout):
        self.calls.append((payload, timeout))
        item = self.items.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item


def test_transport_sends_competition_payload():
    request = SequenceRequest({"choices": [{"message": {"content": "MATCH"}}]})
    result = LocalModelTransport(request_fn=request, sleep_fn=lambda _: None).decide("prompt")
    payload, timeout = request.calls[0]
    assert payload == {"model": "local-model", "temperature": 0, "max_tokens": 128, "messages": [{"role": "user", "content": "prompt"}]}
    assert timeout == 30.0
    assert result.status is TransportStatus.OK
    assert result.parsed.decision is Decision.MATCH
    assert result.parsed.method is ParseMethod.PARSED_SENTINEL
    assert result.attempts == 1


@pytest.mark.parametrize("error,status,retry", (
    (URLError("refused"), TransportStatus.CONNECT_ERROR, True),
    (TimeoutError("slow"), TransportStatus.TIMEOUT, True),
    (HTTPError("u", 500, "bad", {}, None), TransportStatus.HTTP_5XX, True),
    (HTTPError("u", 400, "bad", {}, None), TransportStatus.HTTP_4XX, False),
))
def test_retry_policy_is_bounded_by_failure_class(error, status, retry):
    items = (error, {"choices": [{"message": {"content": "NO_MATCH"}}]}) if retry else (error,)
    request = SequenceRequest(*items)
    result = LocalModelTransport(request_fn=request, sleep_fn=lambda _: None).decide("p")
    assert len(request.calls) == (2 if retry else 1)
    if retry:
        assert result.status is TransportStatus.OK and result.parsed.decision is Decision.NO_MATCH
    else:
        assert result.status is status and result.parsed.decision is Decision.UNKNOWN


def test_two_retryable_failures_return_unknown_without_crash():
    request = SequenceRequest(TimeoutError("a"), TimeoutError("b"))
    result = LocalModelTransport(request_fn=request, sleep_fn=lambda _: None).decide("p")
    assert result.status is TransportStatus.TIMEOUT
    assert result.parsed.decision is Decision.UNKNOWN
    assert result.attempts == 2


@pytest.mark.parametrize("response,status", (
    ({"choices": []}, TransportStatus.EMPTY_RESPONSE),
    ({"bad": 1}, TransportStatus.INVALID_RESPONSE),
    ({"choices": [{"message": {"content": ""}}]}, TransportStatus.EMPTY_RESPONSE),
))
def test_invalid_or_empty_envelopes_do_not_retry(response, status):
    request = SequenceRequest(response)
    result = LocalModelTransport(request_fn=request, sleep_fn=lambda _: None).decide("p")
    assert result.status is status
    assert result.parsed.decision is Decision.UNKNOWN
    assert len(request.calls) == 1


def test_parse_unknown_is_valid_response_and_not_retried():
    request = SequenceRequest({"choices": [{"message": {"content": "explanation only"}}]})
    result = LocalModelTransport(request_fn=request, sleep_fn=lambda _: None).decide("p")
    assert result.status is TransportStatus.PARSE_UNKNOWN
    assert result.parsed.decision is Decision.UNKNOWN
    assert result.attempts == 1
