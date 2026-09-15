from typing import Any

from .trace import DecisionTrace
from .values import TruthValue, to_eligibility_result


def execute(ir: Any, store: Any) -> DecisionTrace:
    """Map an already evaluated typed root to the immutable public trace contract."""
    root = getattr(ir, "root_truth", TruthValue.UNKNOWN)
    if not isinstance(root, TruthValue):
        root = TruthValue(root)
    criterion_id = getattr(ir, "criterion_id", "unknown")
    return DecisionTrace(criterion_id, (), (), (), (() if root is not TruthValue.UNKNOWN else ("root",)),
                         root, to_eligibility_result(root), f"ROOT_{root.value}")
