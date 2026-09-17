from dataclasses import dataclass
from enum import Enum
import json
import time
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .models import Decision, ParsedDecision, ParseMethod
from .response_parser import parse_response


class TransportStatus(str, Enum):
    OK = "OK"
    CONNECT_ERROR = "CONNECT_ERROR"
    HTTP_4XX = "HTTP_4XX"
    HTTP_5XX = "HTTP_5XX"
    TIMEOUT = "TIMEOUT"
    EMPTY_RESPONSE = "EMPTY_RESPONSE"
    INVALID_RESPONSE = "INVALID_RESPONSE"
    PARSE_UNKNOWN = "PARSE_UNKNOWN"


@dataclass(frozen=True, slots=True)
class TransportResult:
    status: TransportStatus
    parsed: ParsedDecision
    attempts: int
    latency_seconds: float
    output_shape: str


def _unknown() -> ParsedDecision:
    return ParsedDecision(Decision.UNKNOWN, ParseMethod.PARSE_UNKNOWN)


class LocalModelTransport:
    endpoint = "http://127.0.0.1:1213/v1/chat/completions"

    def __init__(self, request_fn: Callable | None = None, sleep_fn: Callable[[float], None] = time.sleep, timeout: float = 30.0):
        self.request_fn = request_fn or self._http_request
        self.sleep_fn = sleep_fn
        self.timeout = timeout

    def _http_request(self, payload: dict, timeout: float):
        request = Request(self.endpoint, json.dumps(payload, ensure_ascii=False).encode("utf-8"), {"Content-Type": "application/json"}, method="POST")
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def decide(self, prompt: str) -> TransportResult:
        payload = {"model": "local-model", "temperature": 0, "max_tokens": 128, "messages": [{"role": "user", "content": prompt}]}
        started = time.perf_counter()
        for attempt in (1, 2):
            retryable = False
            try:
                response = self.request_fn(payload, self.timeout)
                if not isinstance(response, dict):
                    return TransportResult(TransportStatus.INVALID_RESPONSE, _unknown(), attempt, time.perf_counter() - started, type(response).__name__)
                choices = response.get("choices")
                if not isinstance(choices, list) or not choices:
                    status = TransportStatus.EMPTY_RESPONSE if choices == [] else TransportStatus.INVALID_RESPONSE
                    return TransportResult(status, _unknown(), attempt, time.perf_counter() - started, "dict")
                try:
                    content = choices[0]["message"]["content"]
                except (KeyError, IndexError, TypeError):
                    return TransportResult(TransportStatus.INVALID_RESPONSE, _unknown(), attempt, time.perf_counter() - started, "dict")
                if content is None or (isinstance(content, str) and not content.strip()):
                    return TransportResult(TransportStatus.EMPTY_RESPONSE, _unknown(), attempt, time.perf_counter() - started, "choices")
                parsed = parse_response(content)
                status = TransportStatus.PARSE_UNKNOWN if parsed.method is ParseMethod.PARSE_UNKNOWN else TransportStatus.OK
                return TransportResult(status, parsed, attempt, time.perf_counter() - started, "choices")
            except HTTPError as exc:
                status = TransportStatus.HTTP_5XX if 500 <= exc.code < 600 else TransportStatus.HTTP_4XX
                retryable = status is TransportStatus.HTTP_5XX
            except TimeoutError:
                status = TransportStatus.TIMEOUT
                retryable = True
            except URLError:
                status = TransportStatus.CONNECT_ERROR
                retryable = True
            except (json.JSONDecodeError, UnicodeDecodeError, TypeError, ValueError):
                return TransportResult(TransportStatus.INVALID_RESPONSE, _unknown(), attempt, time.perf_counter() - started, "invalid")
            if retryable and attempt == 1:
                self.sleep_fn(0.05)
                continue
            return TransportResult(status, _unknown(), attempt, time.perf_counter() - started, "error")
        raise AssertionError("unreachable")
