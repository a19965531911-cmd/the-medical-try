# V5S.6 Experiment J - Criterion 855 Feasibility

Audit date: 2026-09-22

## Criterion

`Scr <178 μmol/L, BUN <9 mmol/L, ALT/AST within normal range`

Criterion 855 was evaluated automatically after criterion 635 failed its payload feasibility gate.

## Proposed rescue

The proposed safe rescue was deterministic patient-level fusion of grounded Scr, BUN, ALT, and AST values across separate reports, without inventing missing values or relying on a generic qualitative statement.

## Frozen E behavior

Deterministic replay shows that Experiment E already implements this path:

| Case | E decision | Resources | Service |
|---|---|---:|---|
| All four values in one report | MATCH | 4 | SERVICE_HIT |
| Scr, BUN, ALT, AST split across four reports | MATCH | 4 | SERVICE_HIT |
| AST missing | NO_MATCH | 0 | SERVICE_MISS |
| Scr = 180 μmol/L | NO_MATCH | 0 | SERVICE_MISS |
| BUN = 9 mmol/L | NO_MATCH | 0 | SERVICE_MISS |
| ALT above ULN | NO_MATCH | 0 | SERVICE_MISS |
| Numeric Scr/BUN plus only `肝功能正常` | NO_MATCH | 0 | SERVICE_MISS |

The complete cross-report case had `groups_hit=4/4`, emitted the four official profile-specific Observations, and passed the Experiment C exact scorer replay.

## Replay sensitivity

The complete cross-report resource set returned `HIT`. Replacing one required lab profile with `wrong-profile` changed the exact control scorer replay to `MISS`. The test therefore exercises the scorer contract rather than generic FHIR validity.

## Safety analysis

- No safe missing-analyte completion exists without fabricating patient values.
- Generic `肝肾功能正常` cannot replace numeric Scr/BUN thresholds.
- Qualitative liver normality cannot produce the required ALT/AST scorer resources without real values under the proven contract.
- Multiple conflicting values without reliable chronology require conservative rejection; changing that policy would not be a bounded positive rescue.

## Verdict

**855 FEASIBILITY: FAIL FOR EXPERIMENT J**

The scorer-compatible cross-report numeric fusion is safe, but it is already present in frozen Experiment E. Therefore it creates no new decision, resource-positive, or service-visible delta. Missing-information cases remain unsafe.

No eligible E `NO_MATCH -> J MATCH` path was found.
