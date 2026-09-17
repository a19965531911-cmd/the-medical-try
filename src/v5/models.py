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


@dataclass(frozen=True, slots=True)
class CriterionSpec:
    criterion_id: str
    original_text: str
    plain_summary: str
    positive_conditions: tuple[str, ...]
    blocking_conditions: tuple[str, ...]
    transport_requirements: tuple[str, ...]
    aliases: tuple[str, ...]
    thresholds: tuple[str, ...]
    temporal_requirement: str
    polarity: str


@dataclass(frozen=True, slots=True)
class EvidenceSegment:
    report_index: int
    text: str
    score: float
    tier: str
