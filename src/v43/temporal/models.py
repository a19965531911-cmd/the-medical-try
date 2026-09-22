from enum import Enum


class TemporalView(str, Enum):
    CURRENT = "CURRENT"
    HISTORICAL = "HISTORICAL"
    RESOLVED = "RESOLVED"
    CONFLICT = "CONFLICT"
    UNKNOWN = "UNKNOWN"
