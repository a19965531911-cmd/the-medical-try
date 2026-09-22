# V5A Pragmatic Matcher Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and verify one recall-first V5A production candidate with tolerant local-model decisions and scorer-visible deterministic FHIR.

**Architecture:** Generate compact criterion specifications from frozen V4 IR, resolve high-confidence cases deterministically, and send every unresolved non-empty patient to one bounded patient-level semantic matcher. Parse simple decisions tolerantly, apply small contradiction guards, extract only scorer-required source values, and reuse proven FHIR/service contracts.

**Tech Stack:** Python 3.12 standard library, PyYAML build dependency, pytest, FHIR R4 JSON, local OpenAI-compatible HTTP endpoint.

**Spec:** `docs/superpowers/specs/2026-09-17-v5-pragmatic-matcher-design.md`

## Global Constraints

- Work only on `v5-pragmatic`; do not modify, merge into, or overwrite the frozen V4 branch/artifacts.
- Single controller, single checkout, sequential execution; no subagents or parallel agents.
- Use RED then GREEN for every behavior change and commit small verified stages.
- Build only `submission/a_test_message_bundle_v5a_candidate.json`.
- Do not push, upload Tianchi, infer hidden labels, or fabricate clinical measurements.
- Endpoint is `http://127.0.0.1:1213/v1/chat/completions`, model is `local-model`, temperature is `0`, max tokens starts at `128`.
- V5 production may reuse V4 FHIR infrastructure but V4 strict typed semantic graph is not a decision authority.

---

### Task 1: Official Runtime and Transport Evidence

**Files:**
- Create: `scripts/audit_v5_sources.py`
- Create: `reports/V5_OFFICIAL_RUNTIME_AUDIT.md`
- Create: `reports/V5_TRANSPORT_CONTRACT_MATRIX.md`
- Create: `reports/V5_TRANSPORT_SELECTION.md`
- Create: `reports/V5_635_POLARITY_AUDIT.md`
- Test: `tests/v5/test_source_audits.py`

**Interfaces:**
- Consumes: V2.4.3 official train Bundle, its 16 service-code files, V4 criterion IR/contracts, and V4 service replay.
- Produces: `load_official_libraries() -> dict[str, OfficialLibraryAudit]`, `transport_matrix() -> dict[str, TransportContractAudit]`, and four evidence-backed Markdown reports.

- [ ] Write tests asserting 16 exact IDs/titles, Base64 decode/compile, architecture classification, endpoint/model/parser/retry extraction, complete transport fields, and a resolved 635 record.
- [ ] Run `python -m pytest tests/v5/test_source_audits.py -q` and observe RED because audit APIs/reports do not exist.
- [ ] Implement source decoding with Python AST/text inspection and derive transport requirements from official service code plus V4 contracts; do not infer unsupported facts.
- [ ] Generate all four reports with criterion-by-criterion evidence and explicit source paths.
- [ ] Run the audit test and `python scripts/audit_v5_sources.py`; require 16/16 records and no unresolved 635 semantics.
- [ ] Commit with `docs(v5): audit official runtime and transport contracts`.

### Task 2: Criterion Specifications, Retrieval, Prompt, and Parser

**Files:**
- Create: `src/v5/__init__.py`
- Create: `src/v5/models.py`
- Create: `src/v5/criterion_specs.py`
- Create: `src/v5/retrieval.py`
- Create: `src/v5/prompt.py`
- Create: `src/v5/response_parser.py`
- Create: `tests/v5/test_criterion_specs.py`
- Create: `tests/v5/test_retrieval_prompt.py`
- Create: `tests/v5/test_response_parser.py`

**Interfaces:**
- Produces: `Decision(str Enum)`, `ParseMethod(str Enum)`, `ParsedDecision`, `CriterionSpec`, `EvidenceSegment`; `load_criterion_specs() -> Mapping[str, CriterionSpec]`; `select_evidence(spec, reports, max_segments=6, max_chars=1200) -> tuple[EvidenceSegment, ...]`; `build_prompt(spec, segments) -> str`; `parse_response(value) -> ParsedDecision`.

- [ ] Write parser RED cases for sentinels, explanations, fences, JSON decision, boolean match, Chinese equivalents, whitespace, harmless fields, ambiguous prose, malformed data, and invalid values.
- [ ] Run parser tests and observe import/behavior failures.
- [ ] Implement the priority parser without broad schema rejection; verify GREEN and commit `feat(v5): add tolerant decision parser`.
- [ ] Write RED tests that all 16 generated specs contain original text, polarity, thresholds/blockers, aliases, and prompt protocol; retrieval must retain cross-report evidence and fallback without keywords while enforcing bounds.
- [ ] Implement compact spec generation from verified IR, bounded three-tier retrieval, and concise prompts; verify all Task 2 tests.
- [ ] Commit `feat(v5): add compact specs and bounded retrieval`.

### Task 3: Reliable Semantic Transport

**Files:**
- Create: `src/v5/transport.py`
- Create: `tests/v5/test_transport.py`
- Create: `tests/v5/test_online_failure_regressions.py`

**Interfaces:**
- Produces: `TransportStatus`, `TransportResult`, `LocalModelTransport.decide(prompt: str) -> TransportResult`; consumes `parse_response` and performs no more than two sequential attempts.

- [ ] Write RED tests for exact endpoint/model/temperature/max_tokens, success, empty/invalid response, connect/timeout/4xx/5xx classification, retry eligibility, one retry success, exhausted retry, and no retry on parsed decisions/4xx.
- [ ] Run tests and observe RED.
- [ ] Implement stdlib HTTP transport with one bounded retry only for connect, timeout, and 5xx; never log prompt text.
- [ ] Encode V4 online failure response shapes and verify they parse without `SCHEMA_REJECT`.
- [ ] Run Task 3 tests and commit `feat(v5): add bounded local model transport`.

### Task 4: Matcher, Deterministic Fast Paths, Guards, and Metrics

**Files:**
- Create: `src/v5/deterministic.py`
- Create: `src/v5/guards.py`
- Create: `src/v5/metrics.py`
- Create: `src/v5/matcher.py`
- Create: `tests/v5/test_matcher.py`
- Create: `tests/v5/test_guards.py`
- Create: `tests/v5/test_metrics.py`

**Interfaces:**
- Produces: `DeterministicResult`, `GuardResult`, `MatchResult`; `deterministic_match(spec, reports)`, `apply_guard(spec, reports, decision)`, and `match_patient(spec, reports, transport)`. `MatchResult` separately records deterministic, model, guarded, and final decisions plus attempts/status/parse/prompt length.

- [ ] Write RED tests for high-confidence deterministic match/no-match, weak evidence remaining unknown, all 16 unknown paths invoking semantic fallback, cross-report fusion, model recovery, model failure safety, and one patient-level call.
- [ ] Implement minimum high-confidence deterministic paths and matcher orchestration; verify GREEN.
- [ ] Write RED guard tests for 185 planned/prior use, 555 beyond six months, 675 explicit non-head location, 745 non-invasive/preoperative/planned, 755 explicit short duration, and 805 never-smoker/two-plus years.
- [ ] Implement small explicit guards and privacy-safe `V5_METRICS` formatting with no patient text or identifiers.
- [ ] Run Task 4 tests and commit `feat(v5): add pragmatic patient matcher`.

### Task 5: Transport Payloads, FHIR Adapter, and Runtime

**Files:**
- Create: `src/v5/payload_extractors.py`
- Create: `src/v5/fhir_adapter.py`
- Create: `src/v5/runtime.py`
- Create: `tests/v5/test_payload_extractors.py`
- Create: `tests/v5/test_fhir_adapter.py`
- Create: `tests/v5/test_runtime.py`

**Interfaces:**
- Produces: `PayloadResult`, `RuntimeResult`; `extract_payload(spec, reports, final_decision)`, `build_resources(criterion_id, patient_id, payload)`, and `evaluate_and_compile(criterion_id, patient_id, reports, transport)`. Drop reasons are explicit and resources are never produced from invented values.

- [ ] Write RED tests for all 16 payloads, required real numbers/reference ranges, 615 five branches, 805 two positive branches and three negative/unknown states, 745 resolvable relation, missing required value, and no silent semantic-match drop.
- [ ] Implement source-backed payload extractors according to the audited matrix.
- [ ] Write RED FHIR tests for exact selected profiles/codes/fields, V4 structural validator, service replay, 615 5/5, 805 2/2, and 745 relation resolution.
- [ ] Implement adapters by reusing proven V4 compiler/contracts where selected and dedicated minimal builders only where the transport report selects official/V2.4.3.
- [ ] Implement runtime composition and verify Task 5 tests plus existing V4 production tests.
- [ ] Commit `feat(v5): connect scorer-visible fhir transport`.

### Task 6: Fixture Corpus, Real Probes, Ablation, and Decision Delta

**Files:**
- Create: `tests/fixtures/v5_matcher_cases.json`
- Create: `scripts/probe_v5_local_model.py`
- Create: `scripts/evaluate_v5_fixtures.py`
- Create: `scripts/compare_v5_decisions.py`
- Create: `reports/V5_REAL_MODEL_PROBE.md`
- Create: `reports/V5A_DECISION_DELTA.md`
- Test: `tests/v5/test_fixture_corpus.py`
- Test: `tests/v5/test_real_probe_reporting.py`

**Interfaces:**
- Corpus records contain criterion, case ID, class, reports, and expected decision; at least 112 cases and seven per criterion. Probe report records sanitized status, latency, output shape, first-line category, parse method, and decision only.

- [ ] Write RED corpus tests requiring 16 criteria, three diverse positives, three relevant negatives, one ambiguous case each, and zero raw hidden/test data.
- [ ] Build the 112+ synthetic corpus and run matcher evaluation; require each criterion has a recovered positive and record semantic/guard/FHIR/service funnel counts.
- [ ] Probe 1213 first with 20 cases across 185/675/745/875, then 12 across 265/615/755/805, diagnose observed HTTP/format failures, and minimally adjust tested parser/transport behavior if evidence requires.
- [ ] Run at least 64 real cases, four per criterion; calculate transport and parseability rates, latency percentiles, retries, status counts, and per-criterion output counts without raw text.
- [ ] Compare bounded selected evidence against full-report prompts and select bounded retrieval only when decision agreement is preserved.
- [ ] Run the same available corpus through V2.4.3, V4, and V5A adapters and report decision counts/deltas, especially V4 unknown to V5 match.
- [ ] Verify Task 6 tests and commit `test(v5): add matcher corpus and real model probes`.

### Task 7: Actual Local FHIR Service Visibility

**Files:**
- Create: `scripts/verify_v5_service_visibility.py`
- Create: `tests/v5/test_service_visibility.py`

**Interfaces:**
- Produces one isolated positive transaction per criterion, submits it to the configured local FHIR endpoint, executes the exact scorer-style query from the transport matrix, and returns a criterion-by-criterion visibility result.

- [ ] Write a RED integration test that requires actual POST plus scorer-style query, not static replay.
- [ ] Detect/start the repository-supported local FHIR service without changing competition code; isolate synthetic patient IDs.
- [ ] Implement sequential submit/query verification and exact 16/16 assertion, including 615 branches, 805 branches, and 745 references.
- [ ] Run the service gate fresh and commit `test(v5): verify end-to-end service visibility`.

### Task 8: Production Builder and Release Verification

**Files:**
- Create: `scripts/build_v5_submission.py`
- Create: `scripts/verify_v5_candidate.py`
- Create: `tests/v5/test_production_candidate.py`
- Create: `submission/a_test_message_bundle_v5a_candidate.json`
- Create: `reports/V5A_PRODUCTION_READINESS_REPORT.md`

**Interfaces:**
- Builder consumes the exact V2.4.3 shell and embeds a scanner-safe stdlib-only V5 runtime into 16 Libraries. Verifier reports shell, IDs/titles, decode/compile, runtime markers, absence of V4 semantic authority, security, FHIR, service, fixture, probe, and funnel gates.

- [ ] Write RED production tests for exact shell/header/sequence/signature, 16 decode/compile, all semantic-capable, compact specs, parser/transport/retry/matcher presence, no dynamic dotted registries, no external hosts/input, and absence of V4 strict semantic decision authority.
- [ ] Implement the flattened V5 builder without overwriting any prior candidate.
- [ ] Build V5A and run decoded runtime fixtures, structural validation, security scan, and production source audit.
- [ ] Run fresh complete pytest, 112+ fixtures, 64+ real probe, service visibility, branch gates, decode/compile, and SHA256 commands; record exact counts and exit codes.
- [ ] Generate the readiness report. Declare READY only if every spec hard gate passes; otherwise declare BLOCKED with evidence and the smallest next fix.
- [ ] Commit `feat(v5): build pragmatic production candidate` without push, merge, or Tianchi upload.

## Self-Review Record

- Spec coverage: Tasks 1-8 cover official audit, transport authority, 635, tolerant protocol, all-criterion semantics, retrieval, real HTTP reliability, guards, payload separation, FHIR visibility, fixtures, deltas, production security, and readiness reporting.
- Placeholder scan: no deferred implementation markers or unspecified test steps remain.
- Type/interface consistency: `CriterionSpec`, `ParsedDecision`, `TransportResult`, `MatchResult`, `PayloadResult`, and `RuntimeResult` flow in one direction from Task 2 through Task 8.
- Hard gate coverage: Task 6 owns 112+/64+/95%/positive-recovery gates; Task 7 owns actual 16/16 service visibility; Task 8 owns shell, FHIR, security, decode/compile, branches, production authority, and final artifact identity.
