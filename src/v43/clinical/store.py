from collections.abc import Iterable

from v43.retrieval.models import EvidencePacket

from .models import ClinicalEpisode, ClinicalEvent, ClinicalFact, ClinicalRelation


class ClinicalStore:
    def __init__(self, valid_span_ids: frozenset[str]):
        self.valid_span_ids = valid_span_ids
        self._facts: dict[str, ClinicalFact] = {}
        self._events: dict[str, ClinicalEvent] = {}
        self._relations: dict[str, ClinicalRelation] = {}
        self._episodes: dict[str, ClinicalEpisode] = {}
        self._fact_identities: set[tuple[object, ...]] = set()

    @classmethod
    def from_packet(cls, packet: EvidencePacket) -> "ClinicalStore":
        return cls(frozenset(span.span_id for span in packet.spans))

    def _validate_spans(self, span_ids: Iterable[str]) -> None:
        unknown = set(span_ids) - self.valid_span_ids
        if unknown:
            raise ValueError(f"unknown evidence span ID(s): {sorted(unknown)}")

    @staticmethod
    def _add_by_id(collection: dict[str, object], object_id: str, item: object) -> None:
        if object_id in collection:
            raise ValueError(f"ID already exists: {object_id}")
        collection[object_id] = item

    def add_fact(self, fact: ClinicalFact) -> None:
        self._validate_spans((fact.evidence_span_id,))
        identity = ("fact", fact.concept, fact.subject, fact.clinical_time, fact.evidence_span_id)
        if identity in self._fact_identities:
            raise ValueError(f"duplicate clinical identity: {identity}")
        self._add_by_id(self._facts, fact.fact_id, fact)
        self._fact_identities.add(identity)

    def add_event(self, event: ClinicalEvent) -> None:
        self._validate_spans(event.evidence_span_ids)
        self._add_by_id(self._events, event.event_id, event)

    def add_relation(self, relation: ClinicalRelation) -> None:
        self._validate_spans(relation.evidence_span_ids)
        self._add_by_id(self._relations, relation.relation_id, relation)

    def add_episode(self, episode: ClinicalEpisode) -> None:
        self._validate_spans(episode.evidence_span_ids)
        self._add_by_id(self._episodes, episode.episode_id, episode)

    def get_fact(self, fact_id: str) -> ClinicalFact | None:
        return self._facts.get(fact_id)

    def get_event(self, event_id: str) -> ClinicalEvent | None:
        return self._events.get(event_id)

    def get_relation(self, relation_id: str) -> ClinicalRelation | None:
        return self._relations.get(relation_id)

    def get_episode(self, episode_id: str) -> ClinicalEpisode | None:
        return self._episodes.get(episode_id)

    def find_facts(self, *, concept: str | None = None, subject: str | None = None,
                   clinical_time: str | None = None) -> tuple[ClinicalFact, ...]:
        return tuple(f for f in self._facts.values()
                     if (concept is None or f.concept == concept)
                     and (subject is None or f.subject == subject)
                     and (clinical_time is None or f.clinical_time == clinical_time))

    def find_events(self, *, concept: str | None = None, subject: str | None = None,
                    clinical_time: str | None = None) -> tuple[ClinicalEvent, ...]:
        return tuple(e for e in self._events.values()
                     if (concept is None or e.concept == concept)
                     and (subject is None or e.subject == subject)
                     and (clinical_time is None or e.start_time == clinical_time))

    def find_relations(self, *, source_node: str | None = None, target_node: str | None = None,
                       relation_type: str | None = None) -> tuple[ClinicalRelation, ...]:
        return tuple(r for r in self._relations.values()
                     if (source_node is None or r.source_node == source_node)
                     and (target_node is None or r.target_node == target_node)
                     and (relation_type is None or r.relation_type == relation_type))

    @property
    def facts(self) -> tuple[ClinicalFact, ...]:
        return tuple(self._facts.values())

    @property
    def events(self) -> tuple[ClinicalEvent, ...]:
        return tuple(self._events.values())

    @property
    def relations(self) -> tuple[ClinicalRelation, ...]:
        return tuple(self._relations.values())

    @property
    def episodes(self) -> tuple[ClinicalEpisode, ...]:
        return tuple(self._episodes.values())
