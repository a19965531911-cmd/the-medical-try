# V4.3 Production Readiness Audit

## Evidence and method

All 16 rows were reconciled against the `criterions` sheet in `CHIP2026-CP2-data-test_a.xlsx`, the corrected A16 CriterionIR, the V2.4.3 and V4.2.2 `FHIR_SERVICE_CODE` evidence, decoded legacy Libraries, the V4.2.2 bundle builder, and the current V4.3 extractor/constraint/compiler paths. The detailed result is `analysis/V43_PRODUCTION_CRITERION_MATRIX.csv`.

Audit gate: 16/16 checked. Statuses are 14 PASS, 1 FIXED (635), and 1 REVIEW_REQUIRED (875 policy). There are no unchecked rows.

## Criterion 635 ruling and correction

The exact source text is `5)或AST、ALT、BUN、Cr不超过正常值一倍者；`; the source English gloss says `not more than twice the normal value`. Both legacy service files implement `value <= 2 * high_value` and require AST, ALT, BUN, and Cr all to meet the condition before returning a patient. This is an inclusion criterion.

Therefore the authoritative logic is:

`AST <= 2xULN AND ALT <= 2xULN AND BUN <= 2xULN AND Cr <= 2xULN`

The former V4.3 expression `ANY(...): value > reference_high` had reversed polarity, the wrong threshold, and the wrong aggregator. A regression was observed RED, then the IR, deterministic facts, typed constraint root, four-resource compiler, and service aggregation were corrected. The focused audit/expansion suite passed after the correction.

## Clinical semantics and transport types

Clinical objects and scorer-facing FHIR transport are intentionally separate layers:

- 165 keeps a chemotherapy MedicationAdministration clinical event and compiles a service-compatible Procedure using `cnwqk165-chemotherapy-history`.
- 485 keeps prolapse plus POP-Q assessment semantics and compiles a service-compatible Observation carrying grade III/IV.
- 565 keeps severe current symptom/Condition semantics and compiles a service-compatible Observation with symptom code and severity extension.

Dedicated production tests must assert unchanged clinical decisions, exact transport resource types, and service hits.

## Criterion 875 policy

The exact criterion and both legacy service matchers provide no evidence for CURRENT_ACTIVE, EVER_PRESENT, or an episode window. They query either observation profile plus the `present` value concept. `REVIEW_REQUIRED` therefore remains the semantic audit status. Production packaging must expose and record the selected policy rather than changing a default silently. The local candidate will use an explicit `EVER_PRESENT` transport policy for literal documented positive evidence; this is a packaging choice, not a claim that the source resolved temporal semantics.

## Criterion 555

The test_a text is `半年内手术史`. Legacy service code applies a 180-day window relative to a reference date. V4.3 accepts explicit relative months and rejects bare surgery history. Date-based inference is permitted only when both surgery date and a usable index/report date exist; otherwise the result remains insufficient evidence.

## Criterion 855

The clinical rule and official service both require all four components. Scr and BUN use the stated fixed thresholds; ALT and AST must not be elevated. V4.3 retains the four-item clinical hard requirement. The transport layer emits/query-observes the four corresponding profiles; service visibility does not weaken the clinical decision rule.

## Audit gate conclusion

The semantic audit gate is open for production embedding. Criterion 635 is corrected and regression protected. Criterion 875 remains explicitly review-required at the semantic layer, with the candidate policy required in configuration and reports.

