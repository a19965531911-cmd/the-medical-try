"""Read-only cross-version shadow evaluation."""
from .adapters import LegacyAdapter, LegacyObservation
from .evaluator import ShadowDecisionRecord, V43ShadowInput, compare_case, run_ablation

__all__ = ["LegacyAdapter", "LegacyObservation", "ShadowDecisionRecord", "V43ShadowInput",
           "compare_case", "run_ablation"]
