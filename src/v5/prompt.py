from .models import CriterionSpec, EvidenceSegment


def build_prompt(spec: CriterionSpec, segments: tuple[EvidenceSegment, ...]) -> str:
    evidence = "\n".join(f"[REPORT {item.report_index}] {item.text}" for item in segments) or "[NO NON-EMPTY REPORT]"
    conditions = "; ".join(spec.positive_conditions)
    blockers = "; ".join(spec.blocking_conditions) or "none explicitly documented"
    thresholds = "\n".join(spec.thresholds) or "none"
    return (
        "You are deciding whether supplied patient clinical text satisfies ONE trial criterion.\n"
        "Use only supplied text. Equivalent clinical wording is allowed. Do not assume missing facts.\n"
        "Missing evidence means UNKNOWN, not NO_MATCH. Explicit contradiction may mean NO_MATCH.\n\n"
        f"Criterion ID: {spec.criterion_id}\n"
        f"Original criterion: {spec.original_text}\n"
        f"Interpretation: {spec.plain_summary}\n"
        f"Polarity: {spec.polarity}\n"
        f"Positive conditions: {conditions}\n"
        f"Blocking conditions: {blockers}\n"
        f"Thresholds: {thresholds}\n"
        f"Temporal requirement: {spec.temporal_requirement}\n\n"
        f"Patient evidence:\n{evidence}\n\n"
        "Output first line: MATCH / NO_MATCH / UNKNOWN\n"
        "Optional next lines: EVIDENCE_REPORTS and concise EVIDENCE. Do not provide chain-of-thought."
    )
