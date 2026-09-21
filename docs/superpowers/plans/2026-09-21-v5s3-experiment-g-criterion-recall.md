# Experiment G Criterion Recall Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add criterion-specific rescue for 485, 635, 855, 675, 735, and 745 while preserving Experiment E behavior for the other ten criteria.

**Architecture:** Build G from each frozen Experiment E Library source. Append a target-only overlay for retrieval, prompts, contradictions, decisions, payloads, and metrics; return the unmodified E source for non-target criteria. Add an offline audit that generates the sole candidate and proves runtime, FHIR, service, security, parity, and complexity gates.

**Tech Stack:** Python 3.12, embedded Python source, pytest, existing FHIR contracts and service replay.

**Spec:** `C:/Users/32433/.codex/attachments/26d08d54-19cd-4896-a80f-30dd8c470973/已粘贴的文本.txt`

## Global Constraints

- Baseline is Experiment E commit `6639cf7`; do not inherit Experiment F behavior.
- Change only `485`, `635`, `855`, `675`, `735`, and `745`.
- Preserve `615`, `265`, `755`, `805`, `555`, `565`, `835`, `875`, `185`, and `165` exactly.
- Keep transport, MessageHeader, Library IDs, scorer profiles, and Experiment C transport frozen.
- Do not fabricate lab values; qualitative or partial lab decisions may emit zero resources.
- No new dependencies, dataclasses, Enums, flatten rename, namespace prefix, or unresolved globals.
- Produce exactly one G candidate; do not push, merge, or submit Tianchi.

## Review Focus

- Bind prolapse stages locally so cancer and unrelated staging do not leak.
- Bind lab values and ULNs by analyte; any explicit violation blocks admission.
- Require zoster plus head/face site or age at least 50.
- Let resolved/history language override active disease admission.
- Allow adjacent-sentence postoperative invasive ventilation while blocking pre-op, NIV-only, and planned-only cases.

### Task 1: Executable Behavior Contract

**Files:** Create `tests/v5s/test_v5s3_expg_criterion_recall.py`.

- [ ] Write target behavior, prompt, retrieval, resource, parity, and zero-anchor tests.
- [ ] Run the focused file and confirm failure because the G builder is absent.

### Task 2: Target-Only Embedded Overlay

**Files:** Create `src/v5s/expg_overlay.py` and `scripts/build_v5s3_expg_criterion_recall_submission.py`.

- [ ] Implement local 485 stage binding and payload extraction.
- [ ] Implement 635/855 qualitative and partial admission with violation blockers.
- [ ] Implement bounded 675, 735, and 745 rules.
- [ ] Implement target prompts, group-balanced retrieval up to 16 windows, and `V5S3G_METRICS`.
- [ ] Run focused tests to green.

### Task 3: Audit and Candidate

**Files:** Create `scripts/audit_v5s3_expg.py`, `analysis/V5S3G_AUDIT.json`, both required reports, and the G candidate.

- [ ] Record online-log unavailability without inventing criterion counts.
- [ ] Audit decode, compile, exec, positive, negative, FHIR, service, and security for all 16 criteria.
- [ ] Verify ten non-target sources and decisions are identical, zero-anchor positives are zero, and E SHA is unchanged.
- [ ] Write machine-readable audit and readiness results.

### Task 4: Verification and Commit

- [ ] Run focused and full repository tests.
- [ ] Run builder and audit scripts fresh; verify hashes, candidate count, and git diff.
- [ ] Commit only intended files, excluding caches and `tmp.patch`.
