# V5S.2 Experiment F Readiness

## Baseline

- Experiment E online macro F1: `0.1666666667`
- Experiment E MATCH: `29`
- Experiment E emitted MATCH: `24`
- Experiment E lost compiler positives: `5`
- Lost distribution: 265 x1, 555 x2, 755 x2

## Recovery

- Recovered 265: `0/1` (`BLOCKED_NO_SAFE_PAYLOAD`)
- Recovered 555: `0/2` (`BLOCKED_NO_SAFE_PAYLOAD`)
- Recovered 755: `2/2` (`GROUNDED_METADATA_REUSE`)
- Total recovered: `2/5`
- Remaining unsafe/unrecoverable: 265 lacks a patient measurement; 555 lacks a scorer-safe surgery date.

## Hard Gates

- Decision delta: `0`
- Retrieval delta: `0`
- Prompt delta: `0`
- LLM-call delta: `0`
- Existing resource delta: `0`
- Pre-existing negative-fixture mismatches: `1` (criterion 675 fixture is already a deterministic MATCH in Experiment E; F is unchanged)
- Embedded decode/compile/exec: `16/16`, `16/16`, `16/16`
- Embedded positive/negative: `16/16`, `16/16`
- FHIR/service/security: `16/16`, `16/16`, `16/16`
- Tianchi: `NOT SUBMITTED`

No hidden-set F1 estimate is made.
