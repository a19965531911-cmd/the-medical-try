# B2 Service / FSH Conflicts

## Critical correction to B1 audit

85 and 205 original FSH both fix status=planned, NOT completed. planned is not a FHIR R4 ProcedureStatus code. NLP returns completed; service ignores status. B2 preserves preparation for planned and completed for completed events. No status falsification. 85 category (FSH 1..1) is now emitted from the surgical evidence.

## Categories

NLP extraction: B1 drops unknown-ULN values and cross-hospital provenance. B2 retains each measurement with its own explicit reference range; ratios are dimensionless unit 1. Unknown reference ranges produce no fabricated normal result.

Clinical Boolean: strict 625 requires complete three-test panel, all supported results within thresholds in one encounter; an eligible encounter exists. Official-compatible accepts supported partial panels but vetoes any observed outlier across dates. B1 implicitly pools undated reports and hospital-colliding IDs. B2 explicit encounter outranks date and hospital namespaces IDs; unlinked undated reports cannot complete each other.

FHIR construction: strict strategy emits the selected eligible panel's actual observations; compatible emits all supported observations. Thus service can hit selected strict resources even when evaluating all source observations would reject. Outputs in results.json permit review; no new labs, ULNs or encounters are synthesized.

Service implementation: 625 loops over all observations, accepts partial panels, rejects at first outlier. Order of normal/abnormal results is immaterial when all observations are retained; B1 successful-panel serialization could change the selected panel/order. Official service pools across dates. Clinical-strict is selected for B2E; compatible B2B is a comparison only.

FSH constraints: 295 requires both cigarettes and cessation components; actual service uses quantity>5 OR cannot-guarantee after recent-date filter. SERVICE_GROUNDED emits only supported components, PROFILE_COMPLETE requires both values in the evidence. Neither missing quantity nor unknown intent is filled. Both strategies remain available; full conflict is not solved.

295 date: use recorded observation date only for documented recent/current behavior. It is not smoking onset. Anchor priority is supplied evaluation_timestamp, else latest report date; absent evaluation context remains uncertain against real platform wall-clock. Official Service additionally evaluates against current wall-clock; replay clock fixed to 2026-10-09 is documented.

225 ongoing remains in-progress; FSH fixed completed rejects it while service accepts profile only. It is never rewritten completed. Completed treatment passes known status rule; plan/recommendation/denial do not emit.

## 625 same-input output/service matrix

|case|strategy|decision|service hit|resources|
|---|---|---|---|---|
|625_full_normal|CURRENT_B1|MATCH|True|3|
|625_full_normal|CLINICAL_STRICT|MATCH|True|3|
|625_full_normal|OFFICIAL_COMPATIBLE|MATCH|True|3|
|625_partial|CURRENT_B1|NO_MATCH|False|0|
|625_partial|CLINICAL_STRICT|NO_MATCH|False|0|
|625_partial|OFFICIAL_COMPATIBLE|MATCH|True|2|
|625_good_then_bad|CURRENT_B1|MATCH|True|3|
|625_good_then_bad|CLINICAL_STRICT|MATCH|True|3|
|625_good_then_bad|OFFICIAL_COMPATIBLE|NO_MATCH|False|0|
|625_different_dates|CURRENT_B1|NO_MATCH|False|0|
|625_different_dates|CLINICAL_STRICT|NO_MATCH|False|0|
|625_different_dates|OFFICIAL_COMPATIBLE|MATCH|True|3|
|625_alt_equal|CURRENT_B1|MATCH|True|3|
|625_alt_equal|CLINICAL_STRICT|MATCH|True|3|
|625_alt_equal|OFFICIAL_COMPATIBLE|MATCH|True|3|
|625_tbil_equal|CURRENT_B1|MATCH|True|3|
|625_tbil_equal|CLINICAL_STRICT|MATCH|True|3|
|625_tbil_equal|OFFICIAL_COMPATIBLE|MATCH|True|3|
|625_hospital_ranges|CURRENT_B1|NO_MATCH|False|0|
|625_hospital_ranges|CLINICAL_STRICT|MATCH|True|3|
|625_hospital_ranges|OFFICIAL_COMPATIBLE|NO_MATCH|False|0|
|625_no_ranges|CURRENT_B1|NO_MATCH|False|0|
|625_no_ranges|CLINICAL_STRICT|NO_MATCH|False|0|
|625_no_ranges|OFFICIAL_COMPATIBLE|NO_MATCH|False|0|
|625_same_encounter_conflict|CURRENT_B1|NO_MATCH|False|0|
|625_same_encounter_conflict|CLINICAL_STRICT|NO_MATCH|False|0|
|625_same_encounter_conflict|OFFICIAL_COMPATIBLE|NO_MATCH|False|0|
|625_bad_then_good|CURRENT_B1|MATCH|True|3|
|625_bad_then_good|CLINICAL_STRICT|MATCH|True|3|
|625_bad_then_good|OFFICIAL_COMPATIBLE|NO_MATCH|False|0|
|625_encounter_outranks_date|CURRENT_B1|MATCH|True|3|
|625_encounter_outranks_date|CLINICAL_STRICT|MATCH|True|3|
|625_encounter_outranks_date|OFFICIAL_COMPATIBLE|MATCH|True|3|
|625_same_day_different_encounter|CURRENT_B1|NO_MATCH|False|0|
|625_same_day_different_encounter|CLINICAL_STRICT|NO_MATCH|False|0|
|625_same_day_different_encounter|OFFICIAL_COMPATIBLE|MATCH|True|3|

## 295 same-input OR/cardinality matrix

|case|strategy|decision|service hit|FSH violations|
|---|---|---|---|---|
|295_quantity_only|SERVICE_GROUNDED|MATCH|True|cnwqk295-smokingstatus: required component, 295 required slice smoking-cessation-guarantee|
|295_quantity_only|PROFILE_COMPLETE|NO_MATCH|False||
|295_refusal_only|SERVICE_GROUNDED|MATCH|True|cnwqk295-smokingstatus: required component, 295 required slice number-of-cigarettes-per-day|
|295_refusal_only|PROFILE_COMPLETE|NO_MATCH|False||
|295_both|SERVICE_GROUNDED|MATCH|True||
|295_both|PROFILE_COMPLETE|MATCH|True||
|295_neither|SERVICE_GROUNDED|NO_MATCH|False||
|295_neither|PROFILE_COMPLETE|NO_MATCH|False||
|295_or_veto|SERVICE_GROUNDED|MATCH|True||
|295_or_veto|PROFILE_COMPLETE|MATCH|True||
|295_old|SERVICE_GROUNDED|NO_MATCH|False||
|295_old|PROFILE_COMPLETE|NO_MATCH|False||

## Validation coverage

Local typed R4 subset checks resource enums, IDs, Bundle request/subject, profile arrays, JSON and safe XHTML. Available FSH checks use ORIGINAL profile blocks for direct mandatory fields, fixed status and the known required 295 slices. No SUSHI snapshots/official IG or complete FHIR validator was provided. Unsupported bindings/slicing are not declared valid. Original service Python is run unchanged with offline mock FHIR responses, not a deployed official server.

Profile lookup honors original explicit ^url, which can differ from Id (475/525/715). The earlier Id-only local checker produced false missing-profile warnings; those have been removed. This correction improves the audit, not clinical predictions.
