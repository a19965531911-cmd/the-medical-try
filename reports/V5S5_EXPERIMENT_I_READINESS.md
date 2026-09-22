# V5S.5 Experiment I Readiness

Champion E:
macro F1 = 0.16666666666666666

H/H1:
same score — NO ONLINE COVERAGE FOR 485

Experiment I objective:
recover high-confidence existing E predictions that are currently invisible to scorer.

## Verdict

========================================
**EXPERIMENT I BLOCKED**
========================================

**NO SAFE HIGH-CONFIDENCE SCORER-SURFACE GAP FOUND**

No Experiment I candidate was generated.

## Online surface evidence

The supplied online summary is classified as `EXTERNAL_ONLINE_OBSERVATION` because no raw H1 `V5S2E_METRICS|...` log was found in the workspace. Independent summation gives:

- Internal final MATCH rows: `29`
- Resource-positive rows: `24`
- MATCH/resources=0 rows: `5`

The five resource-zero rows are distributed as one `265` row, two `755` rows, and two `555` rows. They do not by themselves prove a safe scorer transport repair: the missing payload fields include analyte/temporal facts that may not be safely reconstructed from the emitted evidence.

## Aggregate metric consistency

Using the exact reported aggregate values:

- E/H1 precision `0.75`, recall `0.06666666666666667` imply `TP=6`, predicted positives `=8`, `FP=2` when the common gold-positive denominator is `90`.
- F precision `0.60`, recall `0.06666666666666667` imply `TP=6`, predicted positives `=10`, `FP=4`.
- G precision `0.5714285714285714`, recall `0.044444444444444446` imply `TP=4`, predicted positives `=7`, `FP=3`.

The smallest common integer solution is therefore `gold positives=90`. These aggregate counts are consistency evidence only, not hidden labels per patient. If the displayed decimals were rounded rather than exact, larger integer ambiguities would be possible; under the reported exact values, the solution above is unique at the smallest denominator.

This confirms that `24` internal resource-positive rows are not equivalent to `24` scorer-visible predicted-positive rows, but it does not identify a safe E transport delta by itself.

## Contract and candidate review

The complete contract matrix is in [analysis/V5S5_SCORER_CONTRACT_MATRIX.json](../analysis/V5S5_SCORER_CONTRACT_MATRIX.json), with narrative explanation in [reports/V5S5_SCORER_CONTRACT_MATRIX.md](V5S5_SCORER_CONTRACT_MATRIX.md).

The before/after surface table is in [reports/V5S5_SCORER_SURFACE_BEFORE_AFTER.md](V5S5_SCORER_SURFACE_BEFORE_AFTER.md).

Priority non-control candidates were checked:

- `615`: existing branch-specific E resource replays `SERVICE_HIT`; no E-MISS to legacy-HIT gap.
- `745`: existing parent/child `partOf` representation replays `SERVICE_HIT`; no transport repair is justified.
- `835`: existing abnormal-coagulation representation replays `SERVICE_HIT`.
- `165`, `185`, `565`, `675`, `735`, `875`: existing checked positive paths replay as service hits or are lower-confidence semantic paths; no safe delta demonstrated.
- `555`, `755`: resource-zero paths lack a safe grounded temporal payload; inventing dates or duration is prohibited.
- `265`, `855`: controls already have Experiment C transport evidence; no redesign is allowed. `855` also has no online MATCH in the supplied summary.
- `485`: no online coverage; H/H1 is excluded from this experiment.
- `635`: no online MATCH; requires a future decision experiment, not transport repair.

Experiment F's negative 755 result is preserved. No 755 recovery is attempted.

## Required gate result

Candidate generation requires at least one existing high-confidence E MATCH proven to be scorer-contract `MISS`, plus a safe legacy/official representation proven to `HIT` without changing clinical facts. The checked evidence produced:

- Existing E positive paths checked: yes.
- Proven E scorer-invisible high-confidence paths: `0`.
- Safe legacy/official E-MISS → I-HIT paths: `0`.
- Clinical decision delta: `0`.
- Internal MATCH delta: `0`.
- Candidate generated: `NO`.
- E/H1/F/G candidates modified: `NO`.
- Tianchi submitted: `NO`.

No code, fixture, candidate, or clinical logic was changed in this round. Only the requested audit artifacts were created.

## Next action

Do not create or upload Experiment I. Preserve Experiment E as champion and wait for a trustworthy raw online metrics log or new scorer-contract evidence before opening another transport experiment.
