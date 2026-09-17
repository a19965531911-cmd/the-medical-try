from dataclasses import dataclass
from enum import Enum


class Decision(str, Enum):
    MATCH = "MATCH"
    NO_MATCH = "NO_MATCH"
    UNKNOWN = "UNKNOWN"


class ParseMethod(str, Enum):
    PARSED_SENTINEL = "PARSED_SENTINEL"
    PARSED_JSON = "PARSED_JSON"
    PARSED_CHINESE = "PARSED_CHINESE"
    PARSE_UNKNOWN = "PARSE_UNKNOWN"


@dataclass(frozen=True, slots=True)
class ParsedDecision:
    decision: Decision
    method: ParseMethod
