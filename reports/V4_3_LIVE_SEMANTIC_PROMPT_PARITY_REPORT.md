# V4.3 Live Semantic Prompt Parity Report

Date: 2026-09-17

Candidate: `submission/a_test_message_bundle_v4_3_candidate_v4.json`

## Defect and correction

The V3 defect was confirmed from decoded source. Its live semantic prompt used an empty `criterion_ir`, and both summary fields contained only the criterion number. This allowed typed-result parity tests to pass without proving that a live model could see the criterion semantics.

V4 build-time loads the frozen authoritative `A16_CRITERION_IR_DRAFT.yaml` through the verified `load_criterion_ir()` implementation. It extracts the semantic-required subset only for 185, 675, 745, and 875 and embeds it as a standalone Python constant. No second clinical definition is maintained by hand.

## Prompt parity

| Criterion | Authoritative original text present | Entities/events/relations present | Constraint semantics present | Development-production parity |
|---|---:|---:|---:|---:|
| 185 | PASS | PASS | PASS | PASS |
| 675 | PASS | PASS | PASS | PASS |
| 745 | PASS | PASS | PASS | PASS |
| 875 | PASS | PASS | PASS | PASS |

The parity comparison covers `criterion_id`, `original_text`, `criterion_type`, `clinical_domain`, entities, fact/event/relation schemas, relations, logical expression, and constraint semantics. Serialization order and nonclinical metadata are not compared.

## Runtime policy

- Production semantic timeout: 30.0 seconds
- Verified `extract_semantic` default timeout: 30.0 seconds
- Match: YES
- Semantic call condition: deterministic root is `UNKNOWN`
- One-call guard: unchanged, patient ID by criterion ID
- Structured criteria: semantic path unavailable; observed calls 0 across 12 criteria
- Failure behavior: deterministic result is retained and the Library does not crash

## Privacy-safe observability

Each evaluation emits criterion ID and only these semantic fields: `semantic_called`, `semantic_success`, and `semantic_reason`. No report text or patient content is printed. Verified reasons are `SUCCESS`, `TIMEOUT`, `HTTP_ERROR`, `INVALID_JSON`, `SCHEMA_REJECT`, `GROUNDING_REJECT`, and `NOT_NEEDED`.

## Gates

| Gate | Result |
|---|---:|
| Prompt context and parity | 4/4 PASS |
| Prompt-aware semantic smoke | 4/4 PASS |
| Semantic result parity | 8/8 PASS |
| Grounding | PASS |
| One-call guard | PASS |
| Structured semantic calls | 0 across 12/12 PASS |
| Security preflight | 16/16 PASS |
| FHIR structural validation | 16/16 PASS |
| Service replay | 16/16 PASS |
| Criterion 615 branch replay | 5/5 PASS |
| Criterion 805 branch replay | 2/2 PASS |
| Bundle shell | UNCHANGED |
| Base64 decode and compile | 16/16 PASS |
| Production pytest suite | 139 passed, 0 failed, 0 errors |

## Artifact

- Size: 1,742,104 bytes
- SHA256: `E6FA4214D761997479328B816F8B11640CC9342CA835856B13EC6613F09F5BEE`
- Tianchi: NOT SUBMITTED
- Verdict: READY FOR MANUAL ONLINE PROBE
