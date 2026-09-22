# V6 MVP DESIGN READY FOR APPROVAL

## Decision

V6 demonstrates an architecture-level evidence-completeness path without lowering admission thresholds in the bounded offline prototype. This is a design approval result only. It is not production readiness and makes no leaderboard prediction.

Champion: Experiment E  
Champion macro F1: `0.16666666666666666`  
Architecture: `PATIENT-LEVEL FACT ENGINE`  
Primary improvement: `EVIDENCE COMPLETENESS`

## Offline evidence

- Prototype: `scripts/v6_offline_prototype.py`
- MVP criteria: `555, 565, 675, 735, 745`
- Focused tests: `25 passed`
- Positive MVP cases: `5/5 MATCH`, payload-ready, scorer replay `SERVICE_HIT`
- Negative, missing, planned, history-only, contradiction, incomplete-relation cases: covered
- Admission stability: `analysis/V6_ADMISSION_STABILITY.json`
- `UNSAFE_RELAXATION`: `0`
- Semantic calls in prototype: `0`
- Test-A patient text: unavailable; fact coverage is `NOT_AVAILABLE_NOT_CHECKED`

## Safeguards

- G negative-control safeguards: **PASS**
- Local negation: **PASS**
- Temporal/status handling: **PASS**
- Cross-report fusion: **PASS** for grounded 745 relation; unresolved relation remains `UNKNOWN`
- Semantic residual grounding: **DESIGN PASS / IMPLEMENTATION DEFERRED**; prototype is deterministic
- UNKNOWN emits no resources: **PASS**
- No qualitative or partial-lab admission paths imported from G: **PASS**

## Scorer payload reuse

**PARTIAL**. The prototype reuses the existing `contract_for_criterion` and service replay contracts for its five MVP examples. The current E file has SHA256 `831385ec9deab93d19e54c8319027978eee4b6843c32ddbc5714795b50ad27e8`, while the requested frozen E reference is `40457de3149c7db34daf9c3545199c7c8f409ec65b6ae4412f6ca6a77df6d96e`; this identity mismatch is recorded and is not repaired in this run.

## Deliverables

- Design: `docs/superpowers/specs/2026-09-22-v6-patient-fact-engine-design.md`
- Plan: `docs/superpowers/plans/2026-09-22-v6-patient-fact-engine.md`
- Criterion matrix: `reports/V6_CRITERION_ARCHITECTURE_MATRIX.md`
- History ledger: `reports/V6_EXPERIMENT_HISTORY_LEDGER.md`
- Stability evidence: `analysis/V6_ADMISSION_STABILITY.json`
- Benchmark evidence: `analysis/V6_OFFLINE_BENCHMARK.json`

## Boundary

Production candidate: **NOT GENERATED**  
Experiment E: **NOT MODIFIED**  
Tianchi: **NOT SUBMITTED**  
Test-A unlabeled patient audit: **NOT CHECKED**, because the patient text is unavailable in this workspace.

## Next action

Review and approve the design, then separately resolve the E frozen-artifact provenance and obtain the unlabeled Test-A text before any production MVP integration.
