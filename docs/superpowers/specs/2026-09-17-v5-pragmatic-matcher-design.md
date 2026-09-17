# V5A Pragmatic Matcher Design

## Objective

V5A optimizes robust competition execution and hidden-set recall, not maximal ontology completeness. It replaces V4's strict typed semantic graph as the primary decision path with a compact patient-level matcher while preserving the proven Bundle shell, Library identity sequence, FHIR transport mappings, and service-query compatibility.

V4 remains frozen on `v43-mvp`. V5A is developed on `v5-pragmatic`, produces only `submission/a_test_message_bundle_v5a_candidate.json`, and is never uploaded, pushed, or merged automatically.

## Evidence Authorities

The implementation uses three independently auditable authorities:

1. Official runtime: V2.4.3 `data/train_set_message_bundle.json`, decoded Library sources, and the matching `evidence/a_*_FHIR_SERVICE_CODE.py` files.
2. Proven transport: V2.4.3 Library/FHIR behavior and V4 service contracts, validators, replay evidence, profiles, identifiers, and Bundle shell.
3. Clinical criterion meaning: frozen V4 `A16_CRITERION_IR_DRAFT.yaml`, converted at build time into compact V5 criterion specifications.

Official runtime behavior and scorer-visible transport requirements are documented before matcher implementation. Criterion 635 receives a separate polarity and AND/OR audit. Transport selection prioritizes online-proven behavior, official scorer compatibility, local service evidence, then clinical elegance.

## Runtime Architecture

Each Library exposes the unchanged `FHIRResourceBundleGenerator.parse_clinical_text_to_fhir_bundle(patient_id, case_reports, ai_algorithm_type="nlp")` API.

The V5A flow is:

1. Normalize non-empty patient reports.
2. Select a bounded, criterion-aware evidence set using aliases, lexical relevance, and high-information fallback. Retrieval never gates eligibility and preserves cross-report diversity.
3. Run a small high-confidence deterministic matcher. Explicit positive and explicit contradictory evidence may resolve the decision; absence of a regex hit remains `UNKNOWN`.
4. For every unresolved criterion, make one patient-by-criterion model decision request. All 16 criteria are semantic-capable.
5. Parse the response into `MATCH`, `NO_MATCH`, or `UNKNOWN` using a tolerant deterministic parser.
6. Apply only explicit criterion-specific contradiction guards.
7. When the final decision is `MATCH`, extract the minimum concrete transport payload required by the selected scorer contract. Missing required values produce no fabricated FHIR and an explicit drop reason.
8. Build deterministic FHIR through selected proven adapters, validate it, and expose privacy-safe metrics.

V4 `ClinicalFact`, `ClinicalEvent`, `ClinicalRelation`, `ClinicalEpisode`, strict grounding graph, and three-valued constraint graph are not V5A decision authorities.

## Components

`src/v5/criterion_specs.py` generates compact immutable `CriterionSpec` records from the reviewed V4 IR. Each contains the criterion ID, original Chinese text, plain summary, positive conditions, blockers, aliases, thresholds, temporal requirements, and transport requirements. There is no independently hand-maintained clinical truth table.

`src/v5/retrieval.py` implements bounded Tier A alias selection, Tier B lexical scoring, and Tier C high-information fallback. It caps selected segments and segment length, retains distinct reports where possible, records prompt character length, and always returns semantic input for non-empty patients when fallback is needed.

`src/v5/prompt.py` creates concise prompts containing one criterion, its polarity and key conditions, selected evidence with report indices, and the required first-line response protocol. It explicitly distinguishes absent evidence (`UNKNOWN`) from contradictory evidence (`NO_MATCH`) and never requests chain-of-thought.

`src/v5/response_parser.py` strips harmless markdown fences and whitespace, then applies this priority: canonical first-line sentinel, explicit JSON decision or boolean match field, isolated unambiguous Chinese equivalent, otherwise `UNKNOWN`. Arbitrary prose containing the word `match` is not accepted.

`src/v5/transport.py` sends sequential OpenAI-compatible requests to `http://127.0.0.1:1213/v1/chat/completions` with `model="local-model"`, `temperature=0`, and `max_tokens=128`. It classifies connect, 4xx, 5xx, timeout, empty, invalid, and parse-unknown outcomes. It retries at most once only for connect errors, 5xx, and timeout, with a short bounded delay.

`src/v5/deterministic.py` contains only high-confidence decisions and concrete numeric extraction. Weak or missing evidence returns `UNKNOWN` and permits semantic fallback.

`src/v5/guards.py` vetoes a semantic `MATCH` only for explicit contradictions, including planned-only first irinotecan, explicitly short ventilation duration, never smoking, or surgery clearly beyond six months. It does not recreate the V4 graph.

`src/v5/payload_extractors.py` extracts scorer-required concrete values from source reports. Semantic eligibility and transport completeness are distinct states. Required numeric values, reference ranges, or relations are never invented.

`src/v5/fhir_adapter.py` selects and calls the proven per-criterion FHIR construction path established by the transport audit. It preserves profiles, codes, references, and service-visible fields.

`src/v5/matcher.py` composes retrieval, deterministic resolution, model matching, parsing, guards, and transport payload extraction. `src/v5/runtime.py` exposes the production API. `src/v5/metrics.py` formats privacy-safe metrics without raw report text.

## Decision and Parsing Protocol

The model's first line should be exactly `MATCH`, `NO_MATCH`, or `UNKNOWN`. Optional lines may contain `EVIDENCE_REPORTS` and a short `EVIDENCE` statement.

Accepted unambiguous variants include fenced sentinel output, `{"decision":"MATCH"}`, `{"match":true}`, and isolated Chinese equivalents `符合`, `不符合`, and `无法判断`. Harmless extra JSON fields are accepted. Leading explanations are accepted only when a distinct canonical sentinel or explicit structured decision remains unambiguous.

`MATCH` authorizes eligibility but not fabricated transport. `NO_MATCH` and `UNKNOWN` emit no positive FHIR. A semantic match with incomplete transport records `MISSING_REQUIRED_VALUE` rather than silently dropping or inventing data.

## Retrieval and Prompt Bounds

Retrieval selects a small fixed number of report segments, favors criterion anchors without requiring them, preserves multiple report indices for cross-report fusion, and includes fallback high-information text when lexical matching is empty. Long segments are truncated at safe character boundaries. Full-report and selected-segment modes are compared using decision agreement, parseability, latency, and prompt length; selected mode is adopted only if it preserves fixture decisions.

## Reliability and Observability

No internal model concurrency is permitted. One Library invocation issues at most two sequential HTTP attempts for one patient-by-criterion decision. The initial timeout is inherited from verified competition-compatible evidence and is changed only from observed local probe results.

Metrics record criterion, deterministic decision, LLM call/attempt counts, transport classification, parser method, model decision, guard result, final decision, transport completeness, resource count, prompt length, retries, and explicit drop reason. Raw reports, quotes, patient identifiers, and model prose are not logged.

Allowed parser metrics are `PARSED_SENTINEL`, `PARSED_JSON`, `PARSED_CHINESE`, and `PARSE_UNKNOWN`. Transport failures are `CONNECT_ERROR`, `HTTP_4XX`, `HTTP_5XX`, `TIMEOUT`, `EMPTY_RESPONSE`, and `INVALID_RESPONSE`. Positive drops use `GUARD_VETO`, `MISSING_REQUIRED_VALUE`, `FHIR_BUILD_ERROR`, `FHIR_VALIDATION_ERROR`, or `SERVICE_VISIBILITY_FAIL`.

## Criterion-Specific Constraints

All 16 criteria support semantic fallback. High-confidence numeric extraction remains preferred for 265, 615, 635, 755, 805, and 855. Criteria 185, 555, 565, 675, 735, 745, 805, and 875 retain small explicit temporal or contradiction guards. Criterion 675 permits cross-report fusion. Criterion 745 requires scorer-visible surgery/ventilation linkage. Criterion 875 uses `EVER_PRESENT` unless the official audit proves another competition policy. Criterion 635 is not implemented until its official text, code, service query, polarity, conjunction, and threshold meaning are reconciled in the dedicated audit.

## Testing Strategy

Every implementation change follows RED then GREEN. Unit tests cover tolerant parsing, retry classification and limits, prompt semantics for all 16 criteria, bounded retrieval with fallback, deterministic resolution, contradiction vetoes, payload extraction, and metrics privacy. The online-failure regression corpus includes extra JSON fields, fenced JSON, leading explanation plus sentinel, Chinese decisions, HTTP 500 then success, and two exhausted failures.

The matcher fixture corpus contains at least seven cases per criterion: literal, synonym, and narrative positives; explicit negation, history/competing context, and planned/unrelated negatives; and one ambiguous case. No criterion may have zero recovered positives. Fixtures separately count semantic match, guarded match, FHIR emission, and service visibility.

Real local-model acceptance uses at least 64 synthetic cases, at least four per criterion, with transport success and parseability both at least 95 percent and no criterion with zero parseable responses. Probe output stores only status, latency, shape, first-line category, parse method, and canonical decision.

End-to-end visibility requires each positive fixture to pass actual V5 runtime, transaction Bundle generation, local FHIR submission, and exact scorer-style query with the patient ID returned. This gate must pass 16 of 16. Criterion 615 independently covers all five OR branches; 805 covers current and recent-former smokers; 745 validates the relation.

## Audits and Deliverables

Before matcher implementation, produce:

- `reports/V5_OFFICIAL_RUNTIME_AUDIT.md`
- `reports/V5_TRANSPORT_CONTRACT_MATRIX.md`
- `reports/V5_TRANSPORT_SELECTION.md`
- `reports/V5_635_POLARITY_AUDIT.md`

After implementation, produce:

- `reports/V5_REAL_MODEL_PROBE.md`
- `reports/V5A_DECISION_DELTA.md`
- `reports/V5A_PRODUCTION_READINESS_REPORT.md`
- `scripts/build_v5_submission.py`
- `submission/a_test_message_bundle_v5a_candidate.json`

The builder preserves the exact V2.4.3 shell, MessageHeader, 16 Library IDs and titles, scanner-safe flattened source, allowed local endpoint, and absence of external hosts or `input()`.

## Release Gates

V5A is ready only when the official audit and transport documents are complete; the real model success and parseability rates are each at least 95 percent over at least 64 cases; all 16 criteria are semantic-capable; at least 112 matcher fixtures run; deterministic unknown-to-model recovery is demonstrated 16 of 16; retries and fail-safe behavior pass; service visibility, FHIR structure, security, decode, and compile pass 16 of 16; 615 passes 5 of 5; 805 passes 2 of 2; the 635 audit passes; 875 is explicitly `EVER_PRESENT`; and no criterion has zero positive recovery.

If any hard gate fails, the outcome is `V5A BLOCKED`, with the failing gate, observed evidence, and smallest next fix. Tianchi remains not submitted.
