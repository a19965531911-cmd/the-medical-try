# V4.3 Four-Criterion MVP Implementation Report

## Scope and architecture

This local MVP implements criteria 185, 675, 745, and 875 on branch `v43-mvp` in a standalone repository. The pipeline is criterion-centric: segmentation and non-gating three-tier retrieval feed grounded deterministic/semantic extraction, typed clinical storage, episode/temporal reconciliation, three-valued constraint execution, FHIR compilation, structural validation, service replay, and observation-only shadow comparison.

Raw report text is restricted to segmentation, retrieval, and extraction. Clinical reasoning, FHIR, service replay, and shadow evaluation consume typed objects or provenance identifiers. No production Bundle was generated.

## Git mode and milestones

- Git mode: standalone repository because the parent repository had no commit usable as a worktree base.
- Tasks 1-2: scaffold and frozen CriterionIR loading/validation.
- Milestone A, Tasks 3-6: commits `6a0b0e6`, `6f655d9`, `0c35f42`.
- Milestone B, Tasks 7-9: commits `deb3bb3`, `af1fb4e`, `22201ca`, `f00f239`, `fa6680e`, `7f8fd7c`, `410d439`.
- Milestone C, Tasks 10-12: commits `94d6279`, `3ee3304`, `ac73da1`, `d1d1197`.
- Milestone D checkpoint, Tasks 13-14: commit `f62be09`; final corrections follow it.

## Criterion behavior

- 185 distinguishes actual first irinotecan administration from planning, prior multiple administrations, family-subject mentions, explicit negation, and mere discussion.
- 675 permits cross-report age fusion but requires the head/face location to be linked to the herpes-zoster diagnosis rather than an unrelated lesion.
- 745 requires invasive mechanical ventilation and a directional `POSTOPERATIVE_TO(V,S)` relation or `AFTER(V,S) AND SAME_EPISODE(V,S)` under a consistent event binding. Patient-level co-occurrence, preoperative, remote surgery, planned ventilation, and noninvasive ventilation do not satisfy it.
- 875 defaults to `REVIEW_REQUIRED`. `CURRENT_ACTIVE` and `EVER_PRESENT` are injectable ablation policies. When unresolved scope controls the result, the production-like default returns insufficient evidence with `TEMPORAL_SCOPE_REVIEW_REQUIRED`.

## Retrieval and extraction

Tier 1 uses frozen IR terms, Tier 2 uses Chinese character bigrams plus ASCII/number/unit tokens, and Tier 3 supplies a diverse fallback capped at three spans. Retrieval is a ranker, never an eligibility gate. Deterministic fixture ablation records recall@K of 0.0 for Tier 1 alone and 1.0 after BM25 and after the full three-tier retriever for the explicit critical-span fixture. Semantic extraction uses exact `span_id` grounding and a persistent one-call ceiling per patient and criterion, including terminal failure paths.

## FHIR and service replay

Contracts were audited against both read-only legacy baselines and the frozen IR. The MVP compiles MedicationAdministration (185), Condition (675), Procedure with resolved surgery `partOf` (745), and Observation presence coding (875). Structural validity and service retrievability are evaluated independently. The 875 regression executes SQLite JSON1 `json_valid`, `json_each`, and `json_extract` through the official-style profile plus `value-concept` query; malformed JSON is rejected.

## Shadow evaluation

V2.4.3 and V4.2.2 adapters are read-only observers. Their proxy decision is explicitly defined as whether a criterion-matching FHIR resource was emitted; the adapters also record resource count and service hit and do not fabricate legacy DecisionTrace objects. V4.3 remains the sole decision authority. Supported deltas are `UNCHANGED_POSITIVE`, `UNCHANGED_NEGATIVE`, `RECOVERY`, `REGRESSION`, `FHIR_DELTA`, and `SERVICE_DELTA`.

## Verification record

- Task 2 frozen IR regression: 33 passed.
- Milestone A retrieval regression: 20 passed.
- Milestone A+B integration: 67 passed.
- Milestone C unit and criterion integration: 134 passed.
- Milestone D harvested focused suite: 23 passed; post-audit FHIR/shadow focused suite: 22 passed.
- Final fresh full-suite and compile/import counts are recorded in the final ledger entry after this report is generated.

## Limitations and rulings

- Criterion 875 temporal scope remains unresolved by official evidence; `REVIEW_REQUIRED` is retained rather than silently selecting current or ever-present semantics.
- Legacy decisions are proxy observations based on matching resource emission, not historical EligibilityResult objects.
- Semantic extraction is transport-configurable but tests use fake transports; no live local model call is required for acceptance.
- Retrieval recall figures are deterministic-fixture results, not leaderboard estimates.
- No hidden-label inference, submission probing, leaderboard prediction, production Bundle, Tianchi submission, push, PR, or merge was performed.
