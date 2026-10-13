# B2 Final Verdict

```text
A_CHAMPION = V5S.2 Experiment E (frozen)
B1 = b1-evidence (frozen)
B_CHAMPION = UNVERIFIED
BEST_OFFLINE_CANDIDATE = B2E
B_BOARD_READY = NO
```

B2E is selected for correcting reproduced event, provenance and OR/time bugs, not for maximizing synthetic hits. Official-compatible 625 B2B remains comparison-only; synthetic hit counts cannot determine a leaderboard champion.

## Candidate policy

submission/b2_candidate.json NOT GENERATED: all necessary confirmed profile/identity checks did not pass. An executable review artifact exists at experiment/b2-official-contract/B2E.json. submission/b2_candidate.manifest.json records this status and exact hashes. 16/16 Libraries passed isolated processes and original-service offline positive replay; package strict reload/sanity passed. Formal publication gate remains blocked.

## Unresolved

2/3 identity and MessageHeader contract NOT resolved. 225 ongoing/completed, 295 OR/cardinality and 625 clinical/service conflict are explicitly tested but not officially resolved. 85/205 planned invalid R4 fixed values additionally prevent claims of complete FSH compliance. No official checker, gold patient labels or live semantic endpoint available.

## Changes

src/b_board/b2_runtime.py adds scoped strategies, event/hospital/date binding, 90-day observation filtering, correct OR refusal handling, original-value FHIR construction and 85 category. scripts/b2_experiments.py freezes no existing files, builds six isolated versions, replays official code, performs R4/available-FSH subset checks and writes reports. tests/b_board adds reproduced failures and boundaries. Frozen runtime/builders/packages are hash-verified unchanged.

## Official validation recommendation

Do not perform a blind official verification submission with guessed identifiers. First obtain official mapping/header evidence and checker or equivalent official confirmation. Then a limited hashed validation upload may be useful; no automatic Tianchi submission was performed.

## Results

All variants use 167 identical synthetic cases. These counts are behavior measurements, not accuracy or leaderboard scores.

|Variant|Matches|Offline Service hits|Decision/Service differences|Cases with known FSH violations|
|---|---:|---:|---:|---:|
|B1|74|73|1|20|
|B2A|74|73|1|20|
|B2B|76|75|1|20|
|B2C|74|74|0|18|
|B2D|74|73|1|20|
|B2E|71|71|0|18|

B2E changes 11 decisions relative to B1: 4 NO_MATCH to MATCH and 7 MATCH to NO_MATCH. All existing positive fixtures are retained. The changes address the refusal OR veto, stale smoking evidence, hospital-scoped lab panels, cross-event false combinations and independent elective/emergency procedures. Selected strict-panel serialization agrees with Service on emitted resources; this does not resolve the disagreement when Service evaluates all original source measurements.

Final review fixed two reproduced 295 regressions: distributed current-smoking/quantity context now remains within linked recent records and keeps quantity provenance; explicit evaluation dates take priority over unrelated report timestamps. The local FSH checker now uses the original explicit canonical URL, removing false missing-profile warnings for 475/525/715. Frozen A/B1 files remain unchanged.

### Acceptance Evidence

- Focused suite: 200 passed in 4.55 seconds.
- Final full repository regression: 908 passed in 111.90 seconds, exit 0; evidence in `analysis/B2_PYTEST_RESULTS.xml`.
- Reloaded B2E: 16/16 Libraries ran in fresh isolated Python processes, including positive and empty-input executions; positive resources hit the original offline Service.
- Six-variant matrix: 1,002 executions, no observed exceptions or timeouts; B2E total execution time 0.341 seconds with NO model stub (not production latency).
- Local R4 subset: no violations in matrix outputs. Available FSH subset still finds violations in 18 B2E cases; full validator is unavailable.
- Strict JSON serialization/reload, duplicate-key and NaN/Infinity rejection, XHTML escaping and deterministic semantic veto checks passed in the focused suite.
- Publication gate on the actual B2E file exited 1 with `official tbd/null routing contract unverified`, as required.
- Live model request failed with WinError 10061; actual model schema/latency/token adequacy remain unverified.

Commands: `python -m pytest tests/b_board -q`, `python -m pytest -q --junitxml=analysis/B2_PYTEST_RESULTS.xml`, and `python scripts/b2_experiments.py`. Use the existing bundled Python executable if it is not resolved by the current shell. Detailed inputs, FHIR outputs and hashes are in `experiment/b2-official-contract/results.json` and `submission/b2_candidate.manifest.json`.
