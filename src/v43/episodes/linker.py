from collections import defaultdict
from typing import Any

from v43.clinical.models import AssertionState, ClinicalEpisode, ClinicalEvent, ClinicalRelation


def _policy_name(policy: Any) -> str:
    if isinstance(policy, str):
        return policy
    if isinstance(policy, dict):
        return str(policy.get("criterion_id", policy.get("name", "")))
    return str(getattr(policy, "criterion_id", ""))


def link_episode(events: tuple[ClinicalEvent, ...], relations: tuple[ClinicalRelation, ...],
                 policy: Any) -> tuple[ClinicalEpisode, ...]:
    by_id = {event.event_id: event for event in events}
    parent = {event_id: event_id for event_id in by_id}

    def find(node: str) -> str:
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    def union(left: str, right: str) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    present = [r for r in relations if r.state is AssertionState.PRESENT
               and r.source_node in by_id and r.target_node in by_id]
    qualifying: list[ClinicalRelation] = []
    if _policy_name(policy) == "745":
        kinds_by_pair: dict[frozenset[str], set[str]] = defaultdict(set)
        for relation in present:
            kinds_by_pair[frozenset((relation.source_node, relation.target_node))].add(relation.relation_type)
        for relation in present:
            kinds = kinds_by_pair[frozenset((relation.source_node, relation.target_node))]
            if relation.relation_type == "POSTOPERATIVE_TO" or {"AFTER", "SAME_EPISODE"} <= kinds:
                union(relation.source_node, relation.target_node)
                qualifying.append(relation)
    else:
        for relation in present:
            if relation.relation_type in {"POSTOPERATIVE_TO", "SAME_EPISODE"}:
                union(relation.source_node, relation.target_node)
                qualifying.append(relation)

    components: dict[str, list[ClinicalEvent]] = defaultdict(list)
    for event in events:
        components[find(event.event_id)].append(event)

    episodes = []
    ordered = sorted(components.values(), key=lambda group: min(event.event_id for event in group))
    for index, group in enumerate(ordered, start=1):
        ids = {event.event_id for event in group}
        used_relations = [r for r in qualifying if r.source_node in ids and r.target_node in ids]
        reports = tuple(sorted({i for event in group for i in event.report_indices}
                               | {i for relation in used_relations for i in relation.report_indices}))
        spans = tuple(dict.fromkeys(
            [span for event in group for span in event.evidence_span_ids]
            + [span for relation in used_relations for span in relation.evidence_span_ids]
        ))
        starts = [event.start_time for event in group if event.start_time is not None]
        ends = [event.end_time for event in group if event.end_time is not None]
        concepts = {event.concept for event in group}
        episode_type = "perioperative" if {"Surgery", "MechanicalVentilation"} <= concepts else "clinical"
        confidence = min([event.confidence for event in group]
                         + [relation.confidence for relation in used_relations])
        episodes.append(ClinicalEpisode(f"episode-{index:03d}", episode_type,
                                        min(starts) if starts else None, max(ends) if ends else None,
                                        reports, spans, confidence))
    return tuple(episodes)
