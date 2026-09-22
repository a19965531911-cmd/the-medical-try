# V5S.6 Experiment J - Criterion 635 Feasibility

Audit date: 2026-09-22

## Criterion

`AST、ALT、BUN、Cr不超过正常值一倍者`

The numeric interpretation used by the frozen Experiment E runtime and scorer replay is that each of AST, ALT, BUN, and Cr must be no greater than `2 x ULN`.

## Feasibility questions

### Q1. Can explicit qualitative normality be clinically relevant evidence?

**YES, with qualifications.** Explicit statements such as `肝肾功能正常` or `AST、ALT、BUN、Cr均正常` are clinically relevant evidence that the named laboratory domain was considered normal. Generic statements such as `检查正常` are not sufficiently bound to criterion 635.

This semantic answer alone is insufficient for Experiment J because a positive must also produce a scorer-compatible, non-fabricated payload.

### Q2. Can qualitative evidence be represented for the scorer without inventing numeric values?

**NO.** The actual local scorer-equivalent contract in `src/v43/fhir/service_replay.py` requires four `Observation` resources with:

- profile `cnwqk635-LaboratoryExaminationProfile`
- codes `AST`, `ALT`, `BUN`, and `Cr`
- numeric `valueQuantity.value`
- numeric `referenceRange[0].high.value`
- `value <= 2 * high` for every analyte

There is no documented alternative qualitative status resource in the official/legacy evidence, V2.4.3 representation, Experiment C transport, or service replay contract.

### Q3. Can exact service replay prove HIT for a qualitative representation?

**NO.** Frozen E deterministic replay produced:

| Input | E decision | Resources | Service |
|---|---|---:|---|
| `肝肾功能正常` | NO_MATCH | 0 | SERVICE_MISS |
| `肝肾功能未见明显异常` | NO_MATCH | 0 | SERVICE_MISS |
| `AST、ALT、BUN、Cr均在正常范围` | MATCH | 0 | SERVICE_MISS |
| `AST、ALT正常，BUN、Cr正常` | MATCH | 0 | SERVICE_MISS |
| `检查正常` | NO_MATCH | 0 | SERVICE_MISS |

The two analyte-bound qualitative examples demonstrate the exact failure relevant to this experiment: an internal semantic MATCH cannot become scorer-visible without four real numeric values and four real ULNs.

The replay was also sensitivity-checked. A complete grounded four-resource numeric payload returned `SERVICE_HIT`; removing the required Cr `referenceRange` changed it to `SERVICE_MISS`. This proves that the numeric fields are actually exercised by the replay.

## Contradiction finding

`肝肾功能正常，但Cr 220 μmol/L` can reach an internal semantic MATCH in Experiment E but emits no resources and remains `SERVICE_MISS`. It cannot be repaired by transport without inventing a Cr ULN, and the explicit abnormal value must not be overridden by qualitative normality.

## Verdict

**635 FEASIBILITY: FAIL**

Reason: qualitative normality may be clinically meaningful, but the proven scorer contract is numeric and complete. A qualitative positive cannot be made scorer-visible without fabricating AST/ALT/BUN/Cr values or reference highs.

Classification: `BLOCKED_NO_SAFE_SCORER_PAYLOAD`.
