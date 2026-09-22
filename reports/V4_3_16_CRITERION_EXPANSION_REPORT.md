# V4.3 16-Criterion Expansion Report

## Scope and outcome

V4.3 now executes all 16 frozen CHIP2026 CP2 criteria through the shared criterion-centric pipeline. The verified four-criterion core was retained; Phase 2 added criterion plugins, deterministic extraction, typed constraints, FHIR mappings, service replay fixtures, and three-version shadow coverage for the remaining 12 criteria.

No production Bundle was generated. No Tianchi submission, push, pull request, merge, or leaderboard prediction was performed.

## Criterion status

| Criterion | Status | Primary extraction path | Key accepted behavior |
| --- | --- | --- | --- |
| 185 | PASS | deterministic first; optional grounded semantic fallback | actual first irinotecan administration |
| 675 | PASS | deterministic first; optional grounded semantic fallback | age plus linked head/face herpes-zoster diagnosis |
| 745 | PASS | deterministic first; optional grounded semantic fallback | postoperative invasive ventilation relation |
| 875 | PASS | deterministic first; optional grounded semantic fallback | explicit injectable temporal policy; default remains review-required |
| 165 | PASS | deterministic | completed chemotherapy at an outside hospital; planned/family mentions blocked |
| 265 | PASS | deterministic | preoperative cTnI/cTnT threshold with unit normalization |
| 485 | PASS | deterministic | POP-Q III/IV tied to pelvic-organ prolapse |
| 555 | PASS | deterministic | completed surgery within six months; missing time is unknown |
| 565 | PASS | deterministic | current severe diarrhea or constipation; resolved/history cues blocked |
| 615 | PASS | deterministic typed OR | pT3a-4, R1, pN1, GS >= 8, or PSA > 0.1 ng/mL |
| 635 | PASS | deterministic | any AST/ALT/BUN/Cr value above an explicit matching reference high |
| 735 | PASS | deterministic | target disease and active state in the same current context |
| 755 | PASS | deterministic | mechanical-ventilation duration >= 24 hours |
| 805 | PASS | deterministic | current smoking or cessation under two years |
| 835 | PASS | deterministic | explicit current coagulation abnormality; no invented lab threshold |
| 855 | PASS | deterministic | complete renal/hepatic lab evidence satisfying all frozen limits |

The seven structured criteria 265, 555, 615, 635, 755, 805, and 855 are explicitly tested with a transport that raises on any semantic call; observed semantic calls are zero. The four original criteria retain the bounded semantic path, exact span grounding, and persistent one-call ceiling. The Phase 2 diagnosis/state criteria currently use deterministic extraction; unsupported paraphrases remain insufficient evidence rather than triggering an unbounded semantic call.

## IR and constraint rulings

- Frozen CriterionIR loading and validation succeeds for 16/16 criteria.
- Criterion plugins import and execute for 16/16 criteria through the shared runtime.
- Criterion 635 follows the authoritative frozen expression `ANY(AST,ALT,BUN,Cr): value>reference_high`. A value without an explicit reference high does not satisfy the criterion. No `REVIEW_REQUIRED` item remains for this criterion.
- Criterion 615 uses a typed OR; no branch requires the other branches.
- Criterion 875 retains its previously frozen temporal ruling: production-like default is `REVIEW_REQUIRED`; the positive verification fixture explicitly uses `EVER_PRESENT`.

## FHIR and service replay

FHIR compilation and independent structural validation pass for 16/16 criteria. Each criterion has both a service-hit fixture and a structurally valid identity-mismatch service-miss fixture. Service replay passes 16/16.

Clinical semantics are governed by the frozen IR, while transport must match the audited legacy service queries. The compact IR draft and audited transport differ in resource type for 165 (`MedicationAdministration` versus `Procedure`), 485 (`Condition` versus `Observation`), and 565 (`Condition` versus `Observation`). V4.3 uses the audited service-compatible resource types for transport and records these discrepancies for production-integration review; it does not alter the clinical decision rules.

The 875 official-style SQLite JSON1 regression passes profile and value-concept matching using valid JSON, and malformed JSON is rejected. The 745 service replay resolves the ventilation `partOf` reference against the complete emitted bundle.

## Shadow evaluation

All 16 criteria run through read-only V2.4.3 observer, V4.2.2 observer, and V4.3 comparison paths. V4.3 remains the sole decision authority; no ensemble or legacy vote is applied.

- Decision delta: 16/16 synthetic positive fixtures remain positive across the three observed paths.
- Service delta: none in the 16 positive fixtures.
- FHIR delta: criterion 745 records the expected `FHIR_DELTA` because V4.3 includes the referenced parent surgery resource while the legacy criterion-matching count is one.
- The legacy observations are contract-shaped proxy observations, not reconstructed legacy EligibilityResult objects.

## Verification record

- Expanded criterion/scaffold focused regression: `31 passed`.
- Full shadow plus FHIR/service focused regression: `44 passed`.
- Final fresh suite, `pytest tests/unit tests/integration tests/shadow -q`: `204 passed in 18.08s`.
- Python `compileall` for `src/v43`: PASS, exit code 0.
- Raw-text observability boundary: PASS.
- Frozen reason-code registry: PASS.
- Semantic one-call ceiling, including terminal failures: PASS.
- Structured criteria unnecessary semantic calls: 0.
- 875 SQLite JSON1 execution and malformed-JSON rejection: PASS.

## Known limitations and next-phase checks

- Phase 2 language coverage is deliberately bounded to tested deterministic patterns. Unrecognized clinical paraphrases resolve conservatively to insufficient evidence.
- The compact-IR/legacy-transport discrepancies for 165, 485, and 565 must be explicitly resolved or preserved during production embedding; runtime guessing is forbidden.
- Criterion 555 requires an explicit relative interval in the current deterministic path; a bare surgery history remains unknown.
- Criterion 855 requires all four relevant lab components and explicit ALT/AST reference highs; missing values never imply normality.
- Shadow results are deterministic synthetic/proxy acceptance results, not hidden-gold or leaderboard evidence.

## Verdict

`V4.3 16-CRITERION ENGINE VERIFIED`

`READY FOR PRODUCTION INTEGRATION PHASE`
