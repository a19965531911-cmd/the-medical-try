# V5S.3 Experiment G Readiness

## Baseline

- Champion Experiment E macro F1: `0.1666666666666667`
- Failed Experiment F macro F1: `0.1500`
- Experiment F lowered precision without increasing recall, so Experiment G branches from Experiment E.
- No hidden-F1 estimate is made.

## Offline Decision Matrix

Counts below are from the public synthetic diagnostic matrix in `scripts/audit_v5s3_expg.py`, not online patient counts.

| Criterion | Experiment E MATCH | Experiment G MATCH | Delta |
|---|---:|---:|---:|
| 485 | 3 | 4 | 1 |
| 615 | 1 | 1 | 0 |
| 265 | 1 | 1 | 0 |
| 635 | 3 | 4 | 1 |
| 675 | 2 | 2 | 0 |
| 735 | 2 | 2 | 0 |
| 745 | 1 | 1 | 0 |
| 755 | 1 | 1 | 0 |
| 855 | 0 | 3 | 3 |
| 835 | 1 | 1 | 0 |
| 875 | 1 | 1 | 0 |
| 805 | 1 | 1 | 0 |
| 565 | 1 | 1 | 0 |
| 555 | 1 | 1 | 0 |
| 185 | 1 | 1 | 0 |
| 165 | 1 | 1 | 0 |

## Target Detail

### 485

- Aliases added: POPQ/POP Q; uterine and vaginal prolapse; Roman, Unicode, Arabic, and Chinese stage forms
- Rule positives added: locally bound stage III/IV
- Semantic positives added: prolapse anchor plus bound high stage
- Contradiction blocks: POP-Q I/II, denial, unrelated staging
- Scorer-visible resource count in safe replay fixture: `1`
- Replay HIT count: `1`

### 635

- Aliases added: hepatic/renal function and qualitative normal language
- Rule positives added: complete four-analyte rule preserved
- Semantic positives added: qualitative normal or partial analyte with LLM YES
- Contradiction blocks: any value above 2x analyte ULN
- Scorer-visible resource count in safe replay fixture: `4`
- Replay HIT count: `1`

### 855

- Aliases added: hepatic/renal function and qualitative normal language
- Rule positives added: complete four-analyte rule preserved
- Semantic positives added: qualitative normal or partial analyte with LLM YES
- Contradiction blocks: Scr>=178, BUN>=9, ALT/AST above ULN
- Scorer-visible resource count in safe replay fixture: `4`
- Replay HIT count: `1`

### 675

- Aliases added: VZV reactivation, facial/ophthalmic/V1 sites, English age forms
- Rule positives added: zoster plus site or age>=50
- Semantic positives added: same bounded combinations
- Contradiction blocks: explicit zoster denial
- Scorer-visible resource count in safe replay fixture: `1`
- Replay HIT count: `1`

### 735

- Aliases added: current, ongoing, treated, persistent states
- Rule positives added: target disease plus current/treatment state
- Semantic positives added: disease plus LLM YES with no resolved blocker
- Contradiction blocks: history, cured, resolved, inactive
- Scorer-visible resource count in safe replay fixture: `1`
- Replay HIT count: `1`

### 745

- Aliases added: post-op ventilation, remained intubated, respiratory support
- Rule positives added: same or adjacent sentence postoperative invasive relation
- Semantic positives added: bounded relation plus LLM YES
- Contradiction blocks: pre-op only, NIV-only, planned-only
- Scorer-visible resource count in safe replay fixture: `2`
- Replay HIT count: `1`

## Gates

- Non-target decision parity: `10/10`
- Non-target MATCH delta: `0`
- Zero-anchor fallback positives: `0`
- Embedded decode/compile/exec/positive/negative: `16/16`, `16/16`, `16/16`, `16/16`, `16/16`
- FHIR/service/security: `16/16`, `16/16`, `16/16`
- Complexity: dataclasses `0`, Enums `0`, flatten rename `0`, unresolved globals `0`
- Experiment E artifact: unchanged
- Tianchi: not submitted
