from collections import Counter

from .models import Decision
from .transport import TransportStatus


class MatcherMetrics:
    def __init__(self):
        self._counts = Counter()

    def record(self, criterion_id: str, semantic: Decision, final: Decision, status: TransportStatus, reason_code: str | None):
        self._counts[(criterion_id, "calls")] += 1
        self._counts[(criterion_id, f"semantic_{semantic.value.lower()}")] += 1
        self._counts[(criterion_id, f"final_{final.value.lower()}")] += 1
        self._counts[(criterion_id, f"status_{status.value.lower()}")] += 1
        if semantic is Decision.MATCH and final is not Decision.MATCH:
            self._counts[(criterion_id, "guarded_drop")] += 1
        if reason_code:
            self._counts[(criterion_id, f"reason_{reason_code.lower()}")] += 1

    def format_line(self) -> str:
        parts = []
        for (criterion, key), value in sorted(self._counts.items()):
            parts.append(f"criterion={criterion} {key}={value}")
        return "V5_METRICS " + " ".join(parts)

