"""Locations of frozen, read-only design artifacts."""

from pathlib import Path

CRITERION_IDS = ("185", "675", "745", "875")
REFERENCE_ROOT = Path(__file__).resolve().parents[3] / "CHIP2026_CP2_A_architecture_research_v4_3"


def frozen_reference_paths() -> dict[str, Path]:
    """Return required frozen references without copying or mutating them."""
    return {
        "criterion_ir_schema": REFERENCE_ROOT / "analysis" / "V43_IR_SCHEMA_REFERENCE.yaml",
        "criterion_ir_draft": REFERENCE_ROOT / "analysis" / "A16_CRITERION_IR_DRAFT.yaml",
        "shadow_schema": REFERENCE_ROOT / "analysis" / "V43_SHADOW_EVALUATOR_SCHEMA.json",
        "reason_codes": REFERENCE_ROOT / "analysis" / "V43_FAILURE_REASON_CODES.csv",
        "constraint_logic": REFERENCE_ROOT / "docs" / "V43_CONSTRAINT_LOGIC.md",
    }
