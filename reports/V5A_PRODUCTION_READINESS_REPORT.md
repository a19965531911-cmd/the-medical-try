# V5A Production Readiness Report

## Verdict

**V5A BLOCKED**

The candidate is built and passes all available offline production gates, but two mandatory real-service gates cannot run because neither required local endpoint is listening. Offline replay is not counted as a substitute.

## Artifact

- Candidate: `submission/a_test_message_bundle_v5a_candidate.json`
- Size: 810688 bytes
- SHA256: `afaf280db4afb8d8e66c9962f4d42faa22d5c186351ea7ac2449fe54635c287f`
- Tianchi: NOT SUBMITTED

## Verified Gates

- V5 tests: 109/109 PASS (fresh)
- Frozen integration criterion tests: 16/16 PASS (fresh)
- Synthetic matcher corpus: 112 cases, 16 criteria, 3 positive + 3 negative + 1 ambiguous per criterion
- Offline FHIR structural validation: 16/16 PASS
- Offline service-contract replay: 16/16 PASS
- 615 offline branch replay: 5/5 PASS
- 805 offline branch replay: 2/2 PASS
- Candidate Base64 decode: 16/16 PASS
- Candidate Python compile: 16/16 PASS
- Tianchi security preflight: 16/16 PASS
- Internal `v43.*`/`v5.*` hostname-like registry hits: 0
- Unauthorized external hosts: 0
- `input()`: 0
- Allowed local endpoints remain embedded: `127.0.0.1:1213`, `localhost:3456`
- Production contains `model="local-model"`, tolerant parser, retry transport, pragmatic matcher, guards, and FHIR adapter.
- Production declares `V5_MATCHER_AUTHORITY=True` and `V4_TYPED_SEMANTIC_GRAPH_AUTHORITY=False`.
- Criterion 635 polarity: resolved as inclusion, all AST/ALT/BUN/Cr values <= 2x matching ULN.
- Criterion 875 policy: `EVER_PRESENT`.

## Blocked Gates

- Real local-model transport: 0/64 (0.0%), required >=95%.
- Real response parseability: 0/64 (0.0%), required >=95%.
- Observed model status: `CONNECT_ERROR` 64/64; no listener on `127.0.0.1:1213`.
- Actual scorer-style FHIR service visibility: 0/16 executed; no listener on port 3456.
- Semantic MATCH: 0 under observed endpoint-unavailable run.
- Guarded MATCH: 0 under observed endpoint-unavailable run.
- FHIR emitted: 3/112 from deterministic 615 fast paths under the observed run.
- Actual service-visible: 0/16 because the service is unavailable.
- Per-criterion real positive recovery and semantic-drop funnel cannot be accepted without model responses.

## Decision Delta

- V4 totals on 112-case synthetic corpus: SATISFIED 42, INSUFFICIENT_EVIDENCE 70.
- V5 totals with the observed unavailable endpoint: MATCH 3, UNKNOWN 109.
- V4 UNKNOWN -> V5 MATCH: 0 (real semantic recovery unavailable).

## Smallest Next Fix

Start or restore the approved local model at `127.0.0.1:1213` and the repository-compatible FHIR service at port 3456, then rerun `scripts/probe_v5_local_model.py`, actual POST/query service visibility, and the final readiness verifier. No architecture or 16-criterion semantic change is indicated by the current evidence.
