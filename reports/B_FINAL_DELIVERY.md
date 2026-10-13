# B Board Delivery

Date: 2026-10-09 (Asia/Shanghai)

```text
A_CHAMPION = V5S.2 Experiment E
B_CHAMPION = UNVERIFIED
B_CANDIDATE = b1-evidence
B_BOARD_READY = NO
```

## Outcome

An executable, locally checked B candidate has been generated. It is not cleared
for official publication and is not evidence of a leaderboard improvement.
The frozen online A reference has no B profile routes. B therefore adds a scoped
adapter, reusing E normalization, retrieval, local endpoint and message shell.
No existing engine, A builder or champion artifact was manually changed.

Input workbook: Desktop/CHIP2026-CP2-data-test_b.xlsx, 16 criteria, no patient rows.
Scoped input inventory found this workbook on Desktop and only a synthetic
patient_example.json under examples/synthetic. The repository README and historical
provenance audit likewise document absent official patient records.

## Files

- `src/b_board/runtime.py`: required atomic facts, explicit state extraction,
  duration/smoking/lab/vessel constraints, structured semantic rescue, FHIR builders.
- `src/b_board/__init__.py`: B package boundary.
- `scripts/build_b_submission.py`: workbook loading, E primitive extraction,
  independent B Library routing, strict JSON/package checker, publication gate.
- `scripts/audit_b_board.py`: question/FSH/NLP/service audit, network-free official
  NLP/service replay, frozen replay clock, complete synthetic differential.
- `scripts/check_b_submission.py`: actual on-disk artifact loading and isolated
  Python `-I` process per Library, official service replay, failed publication gate.
- `tests/b_board/test_b_board.py`: 169 focused regressions including all 16 profiles,
  numerical boundaries, temporal/negation traps, disease/pathology binding,
  distributed facts, tbd/null, JSON duplicates, grounding and embedded entrypoints.
- `docs/B_IMPLEMENTATION_PLAN.md`: completed execution checklist.
- `B_PROFILE_AUDIT.md`: all 16 audit rows, official behavior conflicts and every delta.
- `analysis/B_PROFILE_SOURCE_AUDIT.json`: full inspected official source columns and IDs.
- `analysis/B_DIFFERENTIAL.json`: baseline/new match sets and every changed decision.
- `analysis/B_SUBMISSION_DRY_RUN.json`: isolated runtime results and blockers.
- `analysis/B_PYTEST_RESULTS.xml`: final full-suite evidence.
- `submission/b_test_message_bundle_b1_candidate.json`: offline candidate.
- `submission/b_test_message_bundle_b1_candidate.manifest.json`: input/artifact hashes and routing.

The generated submission files are ignored by the existing Git policy; they are
present on disk. This task did not commit, push or submit to Tianchi.

## Verdicts

```text
2   ADD_RULE
3   ADD_RULE
85  ADD_RULE
205 ADD_RULE
225 ADD_RULE
255 ADD_RULE
295 ADD_RULE
465 ADD_RULE
475 ADD_RULE
495 ADD_RULE
525 ADD_RULE
585 ADD_RULE
625 ADD_RULE
695 ADD_RULE
715 ADD_RULE
765 ADD_RULE
```

ADD_RULE reflects absent B handlers in E, not a claim that each profile's existing
generic algorithm was defective. The B adapter handles atom states rather than
admitting cases from disease keywords alone. The code uses PRESENT, ABSENT,
NEGATED, PLANNED, HISTORICAL, UNCERTAIN and UNKNOWN explicitly.

## Verification

```text
baseline before B changes: 708 passed
focused:                  169 passed
regression, full:         877 passed, 0 failures, 0 errors
original regressions:     708 passed within final full run
integration:              54 passed
production:               139 passed
unit:                     130 passed
V5:                       179 passed
V5S:                      147 passed
V6:                       25 passed
shadow:                   25 passed
legacy/V3/V4:             9 passed
golden/red/cross:          no separate suites with these names;
                          fixture, adversarial, integration, grounding and
                          production equivalents included in the full run
schema, package:          PASS: 17 entries, 16 Libraries, unique IDs,
                          deepquery mapping, base64/UTF-8, syntax, JSON;
                          duplicate keys and nonfinite constants rejected
schema, complete FSH:     NOT VERIFIED; known 225/295 conflicts
submission, isolated:     16/16 actual embedded Libraries passed
submission, service:      16/16 strong positives hit unmodified official
                          service code with local mocked FHIR responses
publication gate:         FAILED AS EXPECTED, exits nonzero
formal platform checker:  UNAVAILABLE
real-model rescue:        UNVERIFIED; NO stub/structured response fixtures only
```

The final full run completed in 159.47 seconds. The offline mock implements only
the observed FHIR search parameters; it is not a full FHIR server or platform emulator.
The official 295 naive/aware datetime exception remains in the reference replay;
candidate date-only FHIR dateTime serialization avoids that exception without
inventing a smoking start date.

## Differential

151 identical synthetic cases, official B Excel NLP plus official service vs candidate:

```text
BASELINE MATCH SET:       53 cases
NEW MATCH SET:            58 cases
NO_MATCH -> MATCH:        30
MATCH -> NO_MATCH:        27
unchanged positives:      26
unresolved reference:      2 (295 datetime exception)
candidate logic failures:  0
candidate/service mismatch:0
```

The 58-case new set includes two cases whose reference failed, hence the delta
counts do not reduce to a simple difference in total positives. Every change is
listed in B_PROFILE_AUDIT.md with required-atom states; JSON additionally includes
the original text, selected fact evidence, emitted resources and baseline errors.
Typical recovered positives concern synonyms, fragmented evidence, inclusive
duration boundaries and T2DM diagnoses. Removed positives concern plans,
uncertainty, family history, unsupported pathology and mixed vessel invasion.

This is NOT a same-patient comparison with the online E champion: E lacks B routes,
real B patient/query records are absent, and model-dependent E outputs cannot be
reproduced here. Synthetic labels prove logical consistency only, never F1 gain.

## Risks and Blockers

1. **2/3 publication identity:** supplied IDs are both `tbd`, indexes both null.
   Candidate uses distinct `cnwqk2`/`cnwqk3` resource IDs and `profile-2`/`profile-3`
   fallback identifiers while preserving exact deepquery IDs. The official index
   mapping is undocumented. MessageHeader challenge_id=train_set is inherited
   from E; its B platform meaning is also unverified. Publication is blocked.
2. **625:** official service accepts incomplete panels and pools all dates. Requested
   semantics require all three tests in an encounter with inclusive limits. Candidate
   follows the user's requested AND/encounter semantics. Official scoring may differ.
3. **295:** OR evidence can support only one of the two FSH-required components.
   Candidate emits only supported data. Full profile validity requires resolution;
   no cigarette counts or cessation promises were fabricated.
4. **225:** ongoing radiotherapy is valid clinical evidence but FSH fixes completed
   status. Candidate preserves in-progress, so strict profile validation may fail.
5. **85/205:** official queries do not enforce planned/elective as stated. Candidate
   requires elective/planned evidence and retains completed elective history when
   supported. Query behavior and intended temporal labels remain ambiguous.
6. **3/465/475/715:** pathology, biopsy, causality and distributed negation are
   clinically demanding. Synthetic attacks cover concrete defects; real-record
   performance and complex event resolution remain unmeasured.
7. **Semantic rescue:** the local model's ability to return grounded JSON has not
   been exercised. E's error-to-NO fallback remains; real model evaluation is needed.

No true patient-level MATCH/NO_MATCH prediction file was fabricated. The message
Bundle is executable algorithm packaging, not a set of patient predictions.

## Reproduce

Python exists at the bundled absolute path but is not resolved by the current PATH.
Active shell is native Windows PowerShell; WSL_DISTRO_NAME is empty. The interpreter
was invoked successfully by absolute path (Python 3.12.14, openpyxl and pytest usable).

```powershell
$bPython = 'C:\Users\32433\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $bPython scripts/build_b_submission.py
& $bPython scripts/audit_b_board.py
& $bPython -m pytest -q --basetemp work/pytest-b-recheck
& $bPython scripts/check_b_submission.py
& $bPython scripts/check_b_submission.py --publication
```

The last command intentionally fails until the publication contract is resolved.
Candidate SHA256:
`f7470f0e97d8348b10ab44f88515807e2b207d5369ad5506edc154bcdf0909a3`.

```text
B_BOARD_READY = NO
```
