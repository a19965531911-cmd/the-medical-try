from enum import Enum


class TruthValue(str, Enum):
    TRUE = "TRUE"
    FALSE = "FALSE"
    UNKNOWN = "UNKNOWN"


class EligibilityResult(str, Enum):
    SATISFIED = "SATISFIED"
    NOT_SATISFIED = "NOT_SATISFIED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


def to_eligibility_result(value: TruthValue) -> EligibilityResult:
    return {
        TruthValue.TRUE: EligibilityResult.SATISFIED,
        TruthValue.FALSE: EligibilityResult.NOT_SATISFIED,
        TruthValue.UNKNOWN: EligibilityResult.INSUFFICIENT_EVIDENCE,
    }[value]
