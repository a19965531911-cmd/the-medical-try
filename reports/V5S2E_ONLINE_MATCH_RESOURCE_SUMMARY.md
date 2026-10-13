# V5S.2 Experiment E Online MATCH Resource Summary

## Source

The complete raw online log is not stored in this repository. This snapshot records the aggregate and row-pattern counts supplied with the Experiment F contract; it does not infer hidden labels or patient outcomes.

## Totals

- Evaluations: `51 x 16 = 816`
- Final MATCH: `29`
- MATCH with resources > 0: `24`
- MATCH with resources = 0: `5`
- Lost distribution: 265 x1, 555 x2, 755 x2
- Experiment E online macro F1: `0.1666666667`
- Historical previous best: `0.14375`

## Lost MATCH Rows

| Criterion | Total decisions | MATCH | MATCH/resources > 0 | MATCH/resources = 0 | RULE MATCH among lost | PARTIAL_GROUNDED MATCH among lost |
|---|---:|---:|---:|---:|---:|---:|
| 265 | not present in supplied aggregate | not present in supplied aggregate | not present in supplied aggregate | 1 | 0 | 1 |
| 555 | not present in supplied aggregate | not present in supplied aggregate | not present in supplied aggregate | 2 | 0 | 2 |
| 755 | not present in supplied aggregate | not present in supplied aggregate | not present in supplied aggregate | 2 | 2 | 0 |
| All criteria | 816 | 29 | 24 | 5 | 2 | 3 |

For 265, the lost row had two anchor/group hits and a semantic MATCH. For 555, both lost rows had one anchor/group hit and semantic MATCH. For 755, both lost rows had two anchor/group hits, no model decision, and deterministic `RULE_DURATION` MATCH.

These counts establish the compiler-recovery motivation only. They do not establish which rows are true positives.
