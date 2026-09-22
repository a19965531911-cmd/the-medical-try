from dataclasses import dataclass
from enum import Enum
from typing import Any


class AssertionState(str, Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class ClinicalFact:
    fact_id: str
    fact_type: str
    concept: str
    value: Any
    unit: str | None
    state: AssertionState
    subject: str | None
    temporality: str | None
    clinical_time: str | None
    evidence_span_id: str
    report_index: int
    confidence: float
    source: str


@dataclass(frozen=True, slots=True)
class ClinicalEvent:
    event_id: str
    event_type: str
    concept: str
    status: str
    attributes: Any
    subject: str | None
    start_time: str | None
    end_time: str | None
    temporality: str | None
    episode_id: str | None
    evidence_span_ids: tuple[str, ...]
    report_indices: tuple[int, ...]
    confidence: float
    source: str


@dataclass(frozen=True, slots=True)
class ClinicalRelation:
    relation_id: str
    source_node: str
    target_node: str
    relation_type: str
    state: AssertionState
    evidence_span_ids: tuple[str, ...]
    report_indices: tuple[int, ...]
    confidence: float
    source: str


@dataclass(frozen=True, slots=True)
class ClinicalEpisode:
    episode_id: str
    episode_type: str
    start_time: str | None
    end_time: str | None
    report_indices: tuple[int, ...]
    evidence_span_ids: tuple[str, ...]
    confidence: float
