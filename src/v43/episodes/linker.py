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
        same_episode_pairs = {
            frozenset((relation.source_node, relation.target_node))
            for relation in present if relation.relation_type == "SAME_EPISODE"
        }
        for ventilation in events:
            if ventilation.concept != "MechanicalVentilation":
                continue
            for surgery in events:
                if (surgery.concept != "Surgery" or ventilation.subject is None
                        or ventilation.subject != surgery.subject):
                    continue
                directed = [relation for relation in present
                            if relation.source_node == ventilation.event_id
                            and relation.target_node == surgery.event_id]
                postoperative = [relation for relation in directed
                                 if relation.relation_type == "POSTOPERATIVE_TO"]
                after = [relation for relation in directed if relation.relation_type == "AFTER"]
                same_pair = frozenset((ventilation.event_id, surgery.event_id))
                same = [relation for relation in present
                        if relation.relation_type == "SAME_EPISODE"
                        and frozenset((relation.source_node, relation.target_node)) == same_pair]
                matched = postoperative or (after + same if after and same_pair in same_episode_pairs else [])
                if matched:
                    union(ventilation.event_id, surgery.event_id)
                    qualifying.extend(matched)
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
