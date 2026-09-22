Champion E:
macro F1 = 0.16666666666666666

Rejected F:
macro F1 = 0.1500

Rejected G:
macro F1 = 0.10416666666666666

Target:
macro F1 >= 0.20

## Verdict

**NOT READY — ZERO-ANCHOR RUNTIME DEFECT**

Artifact gates pass, but behavior gates fail: `子宫脱垂III度` produces a scorer-visible positive with `anchor_hits=0`. The candidate is therefore not ready for manual online probe.

## Selected Target

`485` only.

The selected path admits explicit locally-bound POP-Q III evidence and emits one grounded scorer-visible Observation. POP-Q IV/Ⅳ is rejected because the current scorer replay does not accept the existing IV value path. Criteria 635 and 855 remain Experiment E behavior because their online differential evidence and safe payload feasibility are insufficient for a second target.

## Frozen Baseline

- Experiment E candidate SHA: `40457de3149c7db34daf9c3545199c7c8f409ec65b6ae4412f6ca6a77df6d96e`.
- Frozen criteria: `15/15` exact embedded source parity.
- Experiment F candidate: unchanged.
- Experiment G candidate: unchanged.

## Local H Delta

- 485 internal MATCH delta on supported explicit III cases: positive.
- 485 resource delta: `+1` for each supported explicit III case.
- 485 service-HIT delta: `+1` for each supported explicit III case.
- New emitted positives: `4` diagnostic variants, representing one narrow deterministic rescue path.
- New service-visible positives: `4` diagnostic variants.
- Zero-anchor positives: `0`.
- Fabricated clinical values: `0`.

The delta budget is measured by distinct runtime rescue behavior, not by treating the four spelling variants as four hidden patient predictions.

## Structural Gates

- Embedded Libraries: `16/16`.
- Decode/compile: `16/16`.
- FHIR/service replay for selected positive: PASS.
- Security: no new unsafe runtime primitives.
- Unresolved symbols/dataclasses/Enums/flatten rename: `0/0/0/0`.
- Tianchi: `NOT SUBMITTED`.

## Limitation

Raw E/F/G online logs are unavailable, so the requested 51-case online differential table remains unresolved. No hidden-score prediction is made.

## Blocking Conditions

- Raw E/F/G line-level online logs are unavailable; the required 51-case differential remains unresolved.
- pytest is not discoverable and no bundled pytest executable was found; full repository and targeted pytest suites could not be run.
- Git cannot create the requested 5s4-exph-macro-first branch because .git/refs is not writable.
- No commit was created.

## A. Artifact Gates

- Candidate size/SHA: PASS (`707735`, `533637bbac836ceba6506540df93f6eac105b9121b3eb9fec872867cc8271bad`).
- Bundle shape: PASS (`Bundle`, `message`, 17 entries, 1 MessageHeader, 16 Libraries).
- Decode/compile/isolated exec: PASS (`16/16`).
- Frozen Experiment E parity: PASS (`15/15`, including Library metadata and embedded source bytes).
- FHIR structural validation and service replay for supported POP-Q III path: PASS.
- Security, placeholders, dataclasses, Enums, flatten rename: PASS (`0` findings).

## B. Behavior Gates

- `POP-Q III`: PASS, scorer-visible.
- `POP-Q Ⅲ`: PASS, scorer-visible.
- `POP-Q III度`: PASS, scorer-visible.
- `盆腔器官脱垂III度`: PASS, scorer-visible.
- `子宫脱垂III度`: **FAIL**. It emits `MATCH`, one resource, and `SERVICE_HIT` while `anchor_hits=0`.
- Low/unbound/IV/no-stage negatives: no scorer-visible resource.
- Zero-anchor positives: **FAIL (`1`)**.
- Fabricated values: `0`.

The zero-anchor defect is a runtime behavior failure. It cannot be reclassified as a Git, commit, pytest, or historical-log limitation.

## C. Environment Limitations

- Raw E/F/G line-level online logs were not found: `ONLINE_RAW_LOG_DIFFERENTIAL_PARTIAL`.
- Pytest was not executable in the current Codex environment; equivalent artifact verification was run directly.
- `.git/refs` remains read-only; no branch or commit was created. This is not a submission requirement.

## Blocking Verdict

**EXPERIMENT H BLOCKED** until the zero-anchor `子宫脱垂III度` behavior is corrected and the candidate is regenerated with a new verified SHA. No clinical logic or candidate behavior was modified in this audit.