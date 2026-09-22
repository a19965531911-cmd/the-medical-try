# V5S.5 Scorer Contract Matrix

## Evidence basis

The matrix is reconstructed from `src/v43/fhir/contracts.py`, `src/v43/fhir/service_replay.py`, `analysis/V5S_SERVICE_VISIBILITY_MATRIX.csv`, `analysis/EXPC_SCORER_REPLAY.csv`, `analysis/V243_V5S1_FHIR_DELTA.csv`, the V2.4.3 legacy `evidence/a_*_FHIR_SERVICE_CODE.py` sources, and the integration replay tests. It distinguishes local deterministic replay from claims about the external online scorer.

The complete machine-readable matrix is in [analysis/V5S5_SCORER_CONTRACT_MATRIX.json](../analysis/V5S5_SCORER_CONTRACT_MATRIX.json).

## Result

| Criterion | Expected scorer surface | Required distinguishing fields | Existing E evidence | Experiment I status |
|---|---|---|---|---|
| 165 | Procedure | external-treatment extension | local HIT | frozen; no online gap proof |
| 185 | MedicationAdministration | irinotecan code plus first-use extension | local HIT | frozen; no online gap proof |
| 265 | Observation | preoperative profile/extension, analyte code, threshold | EXPC control HIT | control; do not redesign |
| 485 | Observation | POP-Q grade III/IV value | local HIT; H1 had no online coverage | frozen; not target |
| 555 | Procedure | completed surgery and bounded performedDateTime | EXPC control HIT when date grounded | control; resource-zero cases lack safe payload |
| 565 | Observation | symptom code plus severe extension | local HIT | frozen; no online gap proof |
| 615 | Observation | one of five branch profiles and branch value/code | local HIT for tested branches | high priority reviewed; no gap |
| 635 | Observation x4 | four analytes, values and referenceRange.high | local HIT when complete | no online MATCH; not target |
| 675 | Condition | B02.9 plus head/face bodySite | local HIT | frozen; no gap |
| 735 | Condition | official profile, active status and disease code | local HIT | partial-confidence; frozen |
| 745 | Procedure parent + child | invasive code and resolvable `partOf` surgery | local HIT | high priority reviewed; no gap |
| 755 | Procedure | valid ISO performedPeriod >=24h | EXPC control HIT; F rejected extra recovery | control and frozen |
| 805 | Observation plus cessation relation | current status or former status plus duration | EXPC control HIT | control; frozen |
| 835 | Observation | coagulation code plus abnormal value | local HIT | complete groups but no proven gap |
| 855 | Observation up to x4 | four profile-specific lab resources | EXPC control HIT when complete | control; no online MATCH |
| 875 | Observation branch | branch profile plus presence value | intracranial branch local HIT | partial-confidence; frozen |

## Organizer, V2.4.3 and E comparison

The legacy and V2.4.3 implementations establish scorer-facing resource shapes. Experiment C already repaired the known control transport differences for `265`, `555`, `755`, `805`, and `855`. Experiment E includes those control paths and its existing high-priority positives replay as service hits in the checked local contract.

The most relevant non-control candidates were `615` and `745`. Both already emit the branch-specific or relational resource shapes required by the local scorer-equivalent query, and both have `SERVICE_HIT` replay evidence. Therefore neither satisfies the required E-MISS to safe-legacy-HIT gate.

## Limitations

No raw H1 `V5S2E_METRICS` line log was found locally. The 51-row online surface counts supplied in the task are therefore classified as `EXTERNAL_ONLINE_OBSERVATION`, not independently parsed raw logs. The local matrix does not claim to reproduce hidden online labels or the external service implementation.
