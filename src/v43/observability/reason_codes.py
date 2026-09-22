import csv
from dataclasses import dataclass

from v43.references import frozen_reference_paths


@dataclass(frozen=True, slots=True)
class ReasonCodeRegistry:
    codes: frozenset[str]

    @classmethod
    def from_frozen_csv(cls) -> "ReasonCodeRegistry":
        with frozen_reference_paths()["reason_codes"].open(encoding="utf-8", newline="") as handle:
            return cls(frozenset(row["reason_code"] for row in csv.DictReader(handle)))

    def validate(self, reason_code: str) -> None:
        if reason_code not in self.codes:
            raise ValueError(f"unregistered reason code: {reason_code}")

