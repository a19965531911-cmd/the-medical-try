# V5S.2 Experiment E Aggressive Recall Readiness Report

## Verdict

**READY FOR MANUAL ONLINE PROBE**

The V5S.2 Experiment E candidate is frozen. The full repository suite is green, all offline hard gates pass, and no local zero-score regression was found. No Tianchi submission was made in this run.

## Artifact

- Candidate: `submission/a_test_message_bundle_v5s2_expe_aggressive_candidate.json`
- Size: `702059` bytes
- SHA256: `40457de3149c7db34daf9c3545199c7c8f409ec65b6ae4412f6ca6a77df6d96e`
- Base reference: V5S.1 SHA256 `4ea0165cdae6a5c665bc1afafd920e32430b5867998c642eccc832f54eb829b9`
- Branch: `v5s1-expc-legacy-transport`
- Base commit: `c734192`
- Tianchi: **NOT SUBMITTED**

## Recall Recovery

- Experiment C MATCH: `12`
- Experiment E MATCH: `15`
- MATCH delta: `+3`
- Partial-grounded MATCH count: `15`
- One-anchor semantic positives: `11`
- Zero-anchor fallback positives: `0`
- Fallback-only blocks: `16`

| Criterion | Experiment C | Experiment E | Delta |
|---|---:|---:|---:|
| 485 | NO_MATCH | MATCH | +1 |
| 615 | MATCH | MATCH | 0 |
| 265 | NO_MATCH | MATCH | +1 |
| 635 | NO_MATCH | MATCH | +1 |
| All remaining criteria | unchanged | unchanged | 0 |

The recovery logic admits partially grounded evidence while retaining explicit contradiction blockers. `NO_MATCH` does not emit generic false FHIR resources, and zero-anchor fallback remains blocked.

## Embedded Verification

- Base64 decode: `16/16`
- UTF-8 decode: `16/16`
- Python compile: `16/16`
- Isolated execution: `16/16`
- Embedded positive cases: `16/16`
- Embedded negative cases: `16/16`
- FHIR structural validation: `16/16`
- Service replay: `16/16`
- Security checks: `16/16`
- Experiment C transport parity: `16/16`
- Dataclass artifacts: `0`
- Enum artifacts: `0`
- Flatten-rename artifacts: `0`
- Unresolved symbols: `0`

## Test Status

- Focused V5S.2 suite: `78 passed`
- Full repository suite: `605 passed`
- Hard-gate regression: **none found**

## Transport and Submission Risk

Experiment C transport behavior remains unchanged: decision deltas, non-target source deltas, and target-prefix deltas are all zero. The candidate passes the offline packaging and embedded-runtime checks. The prior V5S.1 `/tctmp/tccfile` failure remains classified as an external Tianchi upload or file-mount failure because it occurred before FHIR submission and before embedded Library execution; this candidate has not been resubmitted online.

## Final Classification

- Candidate code: **PASS**
- Candidate file: **PASS**
- Embedded runtime: **PASS**
- Transport parity: **PASS**
- Local packaging: **PASS**
- Tianchi online runtime: **NOT TESTED IN THIS RUN**

## Next Action

Perform one **manual online probe** with the frozen candidate. Do not modify the candidate before that probe. Record the Tianchi result separately from the offline readiness evidence.
