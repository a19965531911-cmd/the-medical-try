# V5S.2 Experiment F Resource Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Recover scorer-visible resources for already-positive Experiment E decisions without changing retrieval, prompts, model calls, clinical rules, or decision policy.

**Architecture:** Freeze Experiment E as the input artifact, then build Experiment F by appending a transport-only overlay to the exact Experiment E Library source. The overlay delegates to the frozen resource builder first, preserves every existing emitted resource byte-for-structure, and only retries criterion 755 with duration metadata extracted from the same grounded text pattern accepted by the frozen rule. Criteria 265 and 555 remain blocked when their scorer-required numeric or temporal facts are absent.

**Tech Stack:** Python 3.12 embedded Library source, FHIR R4 JSON bundles, pytest, local scorer/service replay.

**Spec:** User-provided V5S.2 Experiment F MATCH to resource recovery contract dated 2026-09-20.

## Global Constraints

- Experiment E candidate SHA256 remains `40457de3149c7db34daf9c3545199c7c8f409ec65b6ae4412f6ca6a77df6d96e`.
- Decision, reason, admission mode, contradictions, rule/model results, retrieval, prompts, LLM calls, and fallback behavior must have zero deltas.
- Existing Experiment E emitted resources must be deeply equal in Experiment F.
- No fabricated numeric measurement, date, duration, unit, stage, or other patient fact.
- Do not modify zero-positive criteria or submit to Tianchi.
- Production embedded source must contain zero dataclasses, Enums, flatten renames, namespace prefixes, or unresolved globals.

## Review Focus

- Criterion 755 duration spellings (`24h`, `30 h`, `48h`, `1 day`, `2 days`, Chinese hours/days) must reuse grounded values without changing the frozen rule result.
- Criterion 755 with no report timestamp must remain blocked rather than inventing a period endpoint.
- Criterion 555 semantic MATCH without a surgery date must remain blocked because the scorer date window cannot be satisfied safely.
- Criterion 265 semantic MATCH without analyte-bound numeric measurement must remain blocked because the scorer threshold cannot be satisfied safely.
- Existing emitted resources for all 16 criteria must remain structurally identical.

---

### Task 1: Freeze and Audit Experiment E

**Files:**
- Create: `reports/V5S2_EXPERIMENT_F_MATCH_RESOURCE_AUDIT.md`
- Create: `reports/V5S2E_ONLINE_MATCH_RESOURCE_SUMMARY.md`

**Interfaces:**
- Consumes: Experiment E candidate, V2.4.3 builder/query evidence, Experiment C transport audit, user-supplied online totals.
- Produces: Evidence-backed recovery classification for criteria 265, 555, and 755.

- [x] Verify the Experiment E candidate hash and focused baseline tests.
- [x] Trace `rule_decide -> _expe_payload -> derive_transport_meta -> build_expc_resources`.
- [x] Compare each lost criterion with the preserved scorer query.
- [x] Classify safe recovery versus `BLOCKED_NO_SAFE_PAYLOAD`.

### Task 2: Add Experiment F Red Tests

**Files:**
- Create: `tests/v5s/test_v5s2_expf_resource_recovery.py`

**Interfaces:**
- Consumes: `scripts.build_v5s2_expf_resource_recovery_submission.build_source`.
- Produces: Regression gates for decision parity, resource parity, recovery, blocked payloads, and scorer replay.

- [ ] Add parameterized 755 positive duration tests and verify they fail because the F builder does not exist.
- [ ] Add 755 negative duration and missing timestamp tests.
- [ ] Add 265 and 555 safe/blocked payload tests.
- [ ] Add all-fixture Experiment E decision and existing-resource deep equality tests.

### Task 3: Implement Transport-Only Recovery

**Files:**
- Create: `src/v5s/expf_overlay.py`
- Create: `scripts/build_v5s2_expf_resource_recovery_submission.py`

**Interfaces:**
- Consumes: Exact Experiment E source from `build_v5s2_expe_aggressive_submission.build_source`.
- Produces: `EXPF_OVERLAY_SOURCE` and `build_source(cid, title, identifier)`.

- [ ] Add a grounded duration extractor covering the frozen rule's accepted ventilation forms.
- [ ] Delegate to the frozen metadata/resource builders before attempting recovery.
- [ ] Recover only criterion 755 when grounded duration and timestamp are both present.
- [ ] Mark unsafe 265/555/755 compiler paths as `BLOCKED_NO_SAFE_PAYLOAD` and emit PHI-free `V5S2F_METRICS`.
- [ ] Run the focused Experiment F suite and verify green.

### Task 4: Build, Audit, and Report Candidate

**Files:**
- Create: `scripts/audit_v5s2_expf.py`
- Create: `analysis/V5S2F_AUDIT.json`
- Create: `reports/V5S2_EXPERIMENT_F_DECISION_PARITY.md`
- Create: `reports/V5S2_EXPERIMENT_F_READINESS.md`
- Create: `submission/a_test_message_bundle_v5s2_expf_resource_recovery_candidate.json`

**Interfaces:**
- Consumes: Experiment E and F candidates plus local fixture corpus.
- Produces: Hard-gate counts, parity evidence, recovery evidence, and the sole Experiment F candidate.

- [ ] Build the candidate and verify 16 Library entries decode, compile, and execute.
- [ ] Compare decision diagnostics and model-call counts across the complete local fixture corpus.
- [ ] Deep-compare every previously emitted Experiment E resource.
- [ ] Replay recovered and existing resources against criterion-specific scorer contracts.
- [ ] Write audit JSON and readiness/parity reports from measured results.

### Task 5: Final Verification and Commit

**Files:**
- Modify only generated audit/report files if fresh verification changes measured counts.

**Interfaces:**
- Consumes: Entire repository and final candidate.
- Produces: Final Git commit and verifiable readiness summary.

- [ ] Run focused Experiment F tests.
- [ ] Run the full repository suite with the existing local pytest dependencies.
- [ ] Run the candidate audit and SHA256 verification.
- [ ] Recheck Experiment E SHA256 and Git diff.
- [ ] Commit all Experiment F files without push, merge, or Tianchi submission.
