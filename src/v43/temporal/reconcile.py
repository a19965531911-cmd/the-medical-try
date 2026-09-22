from datetime import datetime

from v43.clinical.models import AssertionState, ClinicalFact
from v43.clinical.store import ClinicalStore

from .models import TemporalView


def _parsed_time(fact: ClinicalFact) -> datetime | None:
    if fact.clinical_time is None:
        return None
    try:
        return datetime.fromisoformat(fact.clinical_time.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def reconcile(store: ClinicalStore, concept: str, subject: str) -> dict[TemporalView, tuple[str, ...]]:
    result: dict[TemporalView, tuple[str, ...]] = {view: () for view in TemporalView}
    facts = store.find_facts(concept=concept, subject=subject)
    timed = [(fact, _parsed_time(fact)) for fact in facts]
    unknown = tuple(fact.fact_id for fact, when in timed if when is None)
    result[TemporalView.UNKNOWN] = unknown
    comparable = [(fact, when) for fact, when in timed if when is not None]
    if not comparable:
        return result

    latest_time = max(when for _, when in comparable)
    latest = tuple(fact for fact, when in comparable if when == latest_time)
    known_latest_states = {fact.state for fact in latest if fact.state is not AssertionState.UNKNOWN}
    if len(known_latest_states) > 1:
        result[TemporalView.CONFLICT] = tuple(fact.fact_id for fact in latest)
        return result

    result[TemporalView.CURRENT] = tuple(fact.fact_id for fact in latest)
    historical = tuple(fact for fact, when in comparable if when < latest_time)
    result[TemporalView.HISTORICAL] = tuple(fact.fact_id for fact in historical)
    if known_latest_states == {AssertionState.ABSENT}:
        result[TemporalView.RESOLVED] = tuple(
            fact.fact_id for fact in historical if fact.state is AssertionState.PRESENT
        )
    return result
