# V4.3 Semantic Production Parity Report

Date: 2026-09-17

Artifact: `submission/a_test_message_bundle_v4_3_candidate_v3.json`

## Verdict

`SEMANTIC_PRODUCTION_GAP NOT REPRODUCED`

`READY FOR MANUAL ONLINE PROBE`

Tianchi submission was not performed.

## Only-one-question audit

The decoded production Library source contains the verified semantic parser, the local endpoint `http://127.0.0.1:1213/v1/chat/completions`, and `model="local-model"`. Semantic extraction is reached only after the deterministic constraint root remains `UNKNOWN`; a shared `CallGuard` limits calls per patient and criterion, and exact `span_id` grounding is validated before semantic objects enter the store. The other 12 criteria cannot enter this path and made zero semantic calls.

| criterion | fixture | development decision | production decision | semantic called? | result |
|---|---|---|---|---:|---|
| 185 | topoisomerase-inhibitor first treatment | SATISFIED | SATISFIED | 1 | PARITY |
| 185 | first actual execution of antitumor regimen | SATISFIED | SATISFIED | 1 | PARITY |
| 675 | facial varicella-virus reactivation rash, age paraphrase | SATISFIED | SATISFIED | 1 | PARITY |
| 675 | facial dermatomal clustered vesicles, age paraphrase | SATISFIED | SATISFIED | 1 | PARITY |
| 745 | positive-pressure support through artificial airway after anesthesia | SATISFIED | SATISFIED | 1 | PARITY |
| 745 | postoperative artificial-airway assisted breathing | SATISFIED | SATISFIED | 1 | PARITY |
| 875 | impaired mentation and inability to answer clearly | SATISFIED | SATISFIED | 1 | PARITY |
| 875 | impaired consciousness on rounds | SATISFIED | SATISFIED | 1 | PARITY |

All semantic fixtures deliberately avoid the current deterministic extractor patterns. The comparison ran the unflattened verified source modules and each decoded flattened production Library with the same grounded semantic response.

## Production gates

| Gate | Result |
|---|---|
| Bundle shell normalized parity | 16/16 PASS |
| Decoded Library compile/runtime | 16/16 PASS |
| Internal `v43.*` hostname-like hits | 0 PASS |
| Unauthorized external host hits | 0 PASS |
| `input()` hits | 0 PASS |
| Registry/loader markers | 0 PASS |
| Local semantic endpoint and model | 16/16 PASS |
| Structured criteria semantic calls | 0 across 12/12 PASS |
| Semantic paraphrase fixtures | 8/8 PASS |
| Development-production semantic parity | 8/8 PASS |
| Unknown `span_id` rejection | PASS |
| One call per patient and criterion | PASS |
| FHIR structural validation | 16/16 PASS |
| Service replay | 16/16 PASS |
| Criterion 615 branch replay | 5/5 PASS |
| Criterion 805 branch replay | 2/2 PASS |

The 615 branches were pT, R1, pN1, GS >= 8, and PSA > 0.1. The 805 branches were current smoker and former smoker with cessation under two years.

## Build design

The V3 builder flattens the required verified modules at build time into one self-contained Python source per Library. It does not embed `VERIFIED_MODULE_SOURCES`, `VERIFIED_PACKAGES`, or `_VerifiedCoreLoader`; the 16 clinical rules, FHIR compiler/contracts, and outer Bundle shell remain unchanged.

## Verification environment

The dependency-free production gate was executed with Python 3.12.14. The accessible interpreter does not contain pytest or PyYAML, so the complete pytest suite was not claimed as run. Equivalent production gates were executed directly by `scripts/verify_v43_candidate_v3.py`; pytest regression files were added for execution in the normal project test environment.

## Artifact identity

- Size: 1,572,696 bytes
- SHA256: `1B988B4F274420AB41FFD4D949DFFDE9C10EE4CC1E326F6FCB16235EA4B36436`
