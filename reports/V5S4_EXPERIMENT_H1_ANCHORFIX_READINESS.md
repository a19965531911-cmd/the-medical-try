# V5S.4 Experiment H1 Anchor-Fix Readiness

Audit date: 2026-09-21

## Final verdict

**EXPERIMENT H1 READY FOR MANUAL ONLINE PROBE**

This verdict means that the frozen H1 artifact is locally complete and its observable delta is explained. It does not claim that H1 will outperform Experiment E online.

## Scope and root cause

H1 is a retrieval-only correction for criterion `485`. The H clinical matcher already accepted the relevant prolapse vocabulary, but H retrieval aliases and groups did not contain those terms. Consequently, `子宫脱垂III度` reached the H clinical decision path as `MATCH` with one resource and `SERVICE_HIT`, while retrieval reported zero true anchors.

H1 aligns retrieval with the already-supported matcher vocabulary for `485` only:

- `子宫脱垂`
- `盆底器官脱垂`
- `阴道前壁脱垂`
- `阴道后壁脱垂`
- `阴道穹隆脱垂`

No H clinical decision rule, stage policy, FHIR payload construction, scorer transport, or other criterion was changed.

## Artifact integrity

- H baseline: `submission/a_test_message_bundle_v5s4_exph_macro_first_candidate.json`
- H baseline size/SHA256: `707735` / `533637bbac836ceba6506540df93f6eac105b9121b3eb9fec872867cc8271bad`
- H1 candidate: `submission/a_test_message_bundle_v5s4_exph1_anchorfix_candidate.json`
- H1 candidate size/SHA256: `708799` / `0d5fe4d6b2e403f02189f3797503c3c30ad98d2a67551fdb3f6863fdc0a489a2`
- H baseline SHA remained unchanged during this audit.
- Current repository branch: `v5s3-expg-criterion-recall`
- Current HEAD: `0e2c6c8428018b2b4e864f0dfcb0ed797f1e2374`
- No commit or branch switch was performed. Git ref creation remains unavailable because `.git/refs` is read-only.

## H to H1 behavior delta

Deterministic replay over the criterion-485 positive and negative fixture set found:

- Decision delta: `0`
- Resource-count delta: `0`
- Service-status delta: `0`
- H1 positive zero-anchor cases: `0`

The confirmed case changes only in retrieval metrics:

| Case | H | H1 | Clinical output |
|---|---|---|---|
| `子宫脱垂III度` | `MATCH`, resource `1`, `SERVICE_HIT`, anchor `0` | `MATCH`, resource `1`, `SERVICE_HIT`, anchor `1` | unchanged |

The additional aligned vocabulary cases also remained clinically unchanged while gaining an anchor:

- `阴道前壁脱垂III度`
- `阴道后壁脱垂III度`
- `阴道穹隆脱垂III度`

Existing `POP-Q` and `盆腔器官脱垂` positives remained `MATCH` with one resource and `SERVICE_HIT`. Low-stage, unbound-stage, denial, unrelated-stage, and unsupported-IV cases remained `NO_MATCH`, resource `0`, and `SERVICE_MISS`.

## Candidate visibility chain

The expected path is complete:

`source logic` -> `runtime` -> `serializer` -> `frozen candidate`

- H1 source overlay is present only for criterion `485`.
- H1 runtime replay reaches the aligned aliases and reports true anchors.
- H1 candidate contains `16/16` Libraries and the decoded embedded source exactly matches the deterministic H1 builder output for `16/16` Libraries.
- The H1 target Library differs from H; all `15/15` non-target H Libraries are byte-identical to H.
- The H1 non-target sources remain exact-parity with Experiment E: `15/15`.
- The Bundle shell and non-Library entries are unchanged between H and H1.

Visibility chain: **PASS**.

## Structural and packaging audit

- Bundle shell: PASS (`Bundle`, `message`)
- Entries: PASS (`17`)
- MessageHeader: PASS (`1`)
- Libraries: PASS (`16`)
- Base64/UTF-8 decode: PASS (`16/16`)
- Python compile: PASS (`16/16`)
- AST parse: PASS (`16/16`)
- Isolated runtime execution: PASS (`16/16`)
- FHIR structural validation: PASS (`16/16`)
- Service replay: PASS (`16/16`)
- Security preflight: PASS (`16/16`)
- Unresolved symbols: `0`
- Dataclass findings: `0`
- Enum findings: `0`
- Flatten-rename findings: `0`
- Placeholder findings: `0`
- Interactive/dangerous runtime primitives (`input`, `eval`, `os.system`, `subprocess`, socket/request escape paths): `0`

## Collateral-delta audit

No hidden collateral delta was found in the checked scope.

- No decision delta.
- No resource delta.
- No service/fallback delta.
- No non-target source or serializer delta.
- No ordering or Bundle-shell delta.
- No FHIR/security/schema compatibility delta.
- No candidate/runtime mismatch.

Raw E/F/G online line-level logs remain unavailable, so this audit does not claim a reconstructed online 51-case differential. That is an evidence limitation, not a local H1 artifact failure.

## Test environment note

The project pytest suite was not executable in the current Codex runtime. The status is `PYTEST_ENVIRONMENT_UNAVAILABLE`; no dependency was installed and no candidate was rebuilt for that reason. The deterministic artifact, replay, packaging, and security gates above were run directly.

Tianchi status: **NOT SUBMITTED**.

## Next action

Perform one manual online probe using the frozen H1 candidate and record the returned leaderboard result separately from this local readiness audit.
