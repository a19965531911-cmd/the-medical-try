# V5S.5 Scorer Surface Before/After

Experiment I was required to preserve all E clinical decisions and change only selected scorer-facing transport paths. No transport candidate was generated because the selection gate failed.

## Online surface reconstruction

The supplied H1 online observation, independently summed, is:

- Internal final `MATCH`: `29`
- Rows with `resources>0`: `24`
- `MATCH/resources=0`: `5`

Per-criterion counts:

| Criterion | Final MATCH | Resources >0 | MATCH/resources=0 |
|---|---:|---:|---:|
| 485 | 0 | 0 | 0 |
| 615 | 3 | 3 | 0 |
| 265 | 3 | 2 | 1 |
| 635 | 0 | 0 | 0 |
| 675 | 1 | 1 | 0 |
| 735 | 2 | 2 | 0 |
| 745 | 2 | 2 | 0 |
| 755 | 3 | 1 | 2 |
| 855 | 0 | 0 | 0 |
| 835 | 1 | 1 | 0 |
| 875 | 2 | 2 | 0 |
| 805 | 3 | 3 | 0 |
| 565 | 1 | 1 | 0 |
| 555 | 3 | 1 | 2 |
| 185 | 1 | 1 | 0 |
| 165 | 4 | 4 | 0 |
| **TOTAL** | **29** | **24** | **5** |

This is labeled `EXTERNAL_ONLINE_OBSERVATION`; raw H1 line logs were not found locally.

## Before/after matrix

| Criterion | Decision source | Groups | E decision | E resources | E scorer-contract-compatible | E replay | I resources | I compatible | I replay | Transport delta | Selected |
|---|---|---:|---|---:|---|---|---:|---|---|---|---|
| 165 | semantic, 3/3 | 3/3 | MATCH | 1 | yes | HIT | unchanged | yes | HIT | none | no |
| 185 | semantic, 3/3 | 3/3 | MATCH | 1 | yes | HIT | unchanged | yes | HIT | none | no |
| 265 | deterministic rule | 1/3 | MATCH | 1 | yes | HIT | unchanged | yes | HIT | none | no |
| 485 | deterministic rule | 1/1 | MATCH | 1 | yes | HIT | unchanged | yes | HIT | none | no |
| 555 | deterministic rule | 2/2 | MATCH | 0 on resource-zero path | blocked by absent grounded payload | MISS on that path | unchanged | unchanged | unchanged | no |
| 565 | semantic, 3/3 | 3/3 | MATCH | 1 | yes | HIT | unchanged | yes | HIT | none | no |
| 615 | deterministic RULE_BRANCH | 1/1 | MATCH | 1 | yes | HIT | unchanged | yes | HIT | none | no |
| 635 | deterministic rule | 4/4 | MATCH | 4 | yes | HIT | unchanged | yes | HIT | none | no |
| 675 | deterministic rule | 3/3 | MATCH | 1 | yes | HIT | unchanged | yes | HIT | none | no |
| 735 | semantic, 2/2 | 2/2 | MATCH | 1 | yes | HIT | unchanged | yes | HIT | none | no |
| 745 | semantic relation | 2/2 | MATCH | 2 | yes | HIT | unchanged | yes | HIT | none | no |
| 755 | deterministic rule | 2/2 | MATCH | 0 on resource-zero path | blocked by absent grounded payload | MISS on that path | unchanged | unchanged | unchanged | no |
| 805 | deterministic rule | 1/2 | MATCH | 1 | yes | HIT | unchanged | yes | HIT | none | no |
| 835 | semantic, 2/2 | 2/2 | MATCH | 1 | yes | HIT | unchanged | yes | HIT | none | no |
| 855 | deterministic rule | 1/4 in checked partial case; complete path is control | existing complete path is contract-compatible | HIT when complete | unchanged | unchanged | unchanged | none | no |
| 875 | semantic, 1/2 | 1/2 | MATCH | 1 | yes for intracranial branch | HIT | unchanged | yes | HIT | none | no |

`I` columns are intentionally unchanged because no safe transport gap was proven.

## Selection result

- Existing E positive paths checked: yes.
- Existing E `SERVICE_HIT` paths preserved: yes.
- Proven scorer-invisible high-confidence E paths with safe legacy replacement: `0`.
- Safe invisible paths: `0`.
- Unsafe/incomplete paths: resource-zero `555` and `755` cases without grounded temporal payload; the `265` resource-zero online row is a payload/visibility observation without a safe new fact source.
- Selected criteria: none.
- Candidate generation: blocked.
