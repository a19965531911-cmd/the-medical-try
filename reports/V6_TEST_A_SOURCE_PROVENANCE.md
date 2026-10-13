# V6.0.1 Test-A Source Provenance

## Result

**TEST_A_TEXT_NOT_FOUND**

The accessible workspace contains multiple identical copies of `CHIP2026-CP2-data-test_a.xlsx` (size `38857`, SHA256 `5e90d8fc...`). Structural inspection shows one sheet, `criterions`, with `17` rows and `10` columns:

`Dataset, index, json, id, label, question, deepquery_id, profile_id, FHIR_FSH, FHIR_SERVICE_CODE`

This is a criterion-definition workbook, not the unlabeled 51-patient case-report corpus. No patient text was loaded, no labels/gold values were read, and no hidden-label evaluation was performed.

The V6 patient-level coverage audit is therefore `NOT_AVAILABLE_NOT_CHECKED`. This does not by itself reject the architecture, but it blocks any claim about Test-A evidence coverage.
