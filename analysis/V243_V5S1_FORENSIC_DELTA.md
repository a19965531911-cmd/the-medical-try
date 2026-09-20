# V2.4.3 vs V5S.1 FORENSIC DELTA

Date: 2026-09-19  
Repository: `CHIP2026_CP2_A_baseline_v4_3_mvp`  
V5S.1 commit: `c7341927d0f7ba74f848a90890004eb680d6a70d`  
Scope: read-only production/candidate analysis. No candidate rebuilt and no Tianchi submission performed.

## 1. Artifact confidence

**V2.4.3 artifact state: EXACT.** The preserved snapshot contains the exact candidate `submission/a_test_message_bundle_v2_4_3.json`, exact Base64-embedded Python for all 16 Libraries, `src/library_factory.py`, criterion FHIR service implementations under `evidence/`, analysis matrices, and the preserved successful online ingestion log `evidence/online_a1_run.log`.

V2.4.3 candidate: 149,376 bytes; SHA256 `dbda76bf126c55f0176c2067f033a16d68838eb800df0d7f745cb25d4704e173`.  
V5S.1 candidate: 360,724 bytes; SHA256 `4ea0165cdae6a5c665bc1afafd920e32430b5867998c642eccc832f54eb829b9` (matches frozen expected value).

No missing historical component needed reconstruction. Production patient inputs and hidden labels were not recovered or inferred.

## 2. Online evidence

| Version | Macro F1 | Micro precision | Micro recall | Micro F1 |
|---|---:|---:|---:|---:|
| V2.4.3 | about 0.14375 | about 0.6923 | 0.10 | not supplied |
| V5S.1 | 0.0625 | 0.50 | 0.0222222222 | 0.0425531915 |

These aggregates establish V2.4.3 as the stronger online baseline, but do not expose criterion-level or patient-level gold labels.

## 3. Top-level Bundle differences

There is **no meaningful submission-shell difference**:

- Both are `resourceType=Bundle`, `type=message`, with exactly 17 entries: one MessageHeader and 16 Libraries.
- MessageHeader JSON is identical, including ID, `eventCoding`, source name/software/version, and `challenge_id=train_set`.
- Entry order and all Library IDs, names, titles, identifiers, and `contentType=text/x-python` are identical.
- Both use valid padded Base64. Replacing every `content.data` with a placeholder makes the full Bundles equal.
- The size delta is entirely embedded Python. It does not support a platform-ingestion explanation.

## 4. Runtime architecture differences

V2.4.3 embeds criterion-specific deterministic Python. Each report is normalized and evaluated independently; a satisfying report directly builds resources. There is no LLM request or output parser.

V5S.1 embeds a shared runtime plus criterion specification. It sentence-splits reports, performs alias-group retrieval, then uses deterministic rules for 265, 485, 555, 615, 635, 755, 805, and 855. The other eight criteria use one local-model YES/NO request. A MATCH may still be revoked by payload gates for 265, 635, and 855.

V5S.1 therefore adds two decision failure surfaces absent from V2.4.3: evidence-window exclusion and conservative model rejection. It also adds useful precision controls and cross-report fusion.

## 5. Retrieval differences

V2.4.3 evaluates each complete report. It has no eight-window cap, anchor requirement, fallback sentence, or cross-report fusion. Context outside keyword-local sentences remains visible, but all required concepts must occur in one report.

V5S.1 splits on punctuation/newlines, retrieves by alias group, reserves at least one window per hit group, deduplicates, and applies a global maximum of eight windows. It can fuse evidence across reports. If no group hits, it falls back to the first sentence.

This can improve precision while excluding relation, negation, timing, or qualifier context available to V2.4.3. Dispersed four-analyte evidence can compete for the budget. Conversely, 675 and 745 gain cross-report positive paths unavailable to V2.4.3.

## 6. Prompt differences

V2.4.3 has **no prompt**: all 16 decisions are deterministic predicates.

For eight V5S.1 semantic criteria, the actual Chinese prompt contains the criterion rule and only retrieved windows, requires `YES` or `NO`, and ends with wording equivalent to “evidence sufficient => YES; otherwise => NO.” There is no `UNKNOWN`. This is systematically conservative under missing or fragmented evidence.

V2.4.3 did not send broader text to a model; it avoided the model. Its context advantage comes from deterministic predicates scanning the full report.

## 7. Rule/semantic strictness differences

V5S.1 is stricter for LLM-routed criteria because insufficient evidence is forced to NO. It is additionally stricter at the structured payload boundary for 265, 635, and especially 855. It is not uniformly stricter: cross-report fusion broadens 675 and 745, and 485/615/755/805 remain close to V2.4.3.

Key shifts:

- **165:** V2.4.3 directly matches external-location + received/completed chemotherapy in one report. V5S.1 requires retrieved concept coverage and conservative semantic YES.
- **265:** both require threshold-positive troponin; V5S.1 revokes MATCH when analyte and numeric value cannot be bound.
- **555:** V2.4.3 parses relative months and computes an event date. V5S.1 can decide recent surgery yet serialize 1970 when no explicit date is extracted.
- **635:** both require all four value/ULN pairs. V5S.1 adds an explicit post-MATCH completeness gate and bounded retrieval. V2.4.3 does not use default ULNs; its exact rule uses reported value/high pairs.
- **745:** V2.4.3 requires postoperative and invasive-ventilation relation in the same report/clause. V5S.1 can fuse reports and ask the model to infer relation, creating both new positive paths and new context-loss paths.
- **855:** V2.4.3 accepts numeric Scr/BUN plus qualitative ALT/AST “not elevated.” V5S.1 requires all four numeric components before resources are allowed.

See `analysis/V243_V5S1_STRICTNESS_DELTA.csv`.

## 8. Payload differences

V2.4.3 directly constructs scorer-oriented payloads inside criterion builders. V5S.1 separates decision, extraction, and resource construction. This avoids fabricated structured values but creates MATCH-to-resource dropouts.

High-impact differences:

- 265: V5S.1 omits the preoperative extension and scorer-specific troponin coding.
- 555: V5S.1 may use a 1970 fallback instead of deriving a relative event date.
- 755: V2.4.3 emits normal `performedPeriod.start/end`; V5S.1 emits nonstandard `duration_hours` inside the period.
- 805: V2.4.3 emits a cessation-duration Observation; V5S.1 does not.
- 855: V2.4.3 can emit four profile-specific Observations; V5S.1 emits only serum creatinine after requiring four lab inputs.

## 9. FHIR/service-query differences

Preserved services search by profile and then inspect criterion-specific codes, values, extensions, dates, references, and `Patient/` subject references. Local replay proves literal compatibility only, not production equivalence.

Highest-confidence classifications:

- **V243_MORE_VISIBLE:** 265, 555, 805, 855.
- **V5S1_MORE_VISIBLE:** 675 and 745 because V2.4.3 used legacy profile spellings while V5S.1 uses strings queried by preserved service code.
- **IDENTICAL/equivalent when emitted:** 165, 185, 485, 565, 635, 835, 875.
- **UNRESOLVED:** 615, 735, 755 because changes pull in opposite directions or production normalization is unproven.

Both emit transaction entries with `request.method=POST` and `request.url=<resourceType>`. See `analysis/V243_V5S1_FHIR_DELTA.csv`.

## 10. Subject/patient identity comparison

Literal construction is identical:

`{"subject":{"reference":"Patient/" + str(patient)}}`

Preserved services accept subjects beginning with `Patient/`; 745 also follows `partOf` to the parent Procedure. Neither runtime has an obvious local subject-format advantage.

The Tianchi executor's patient argument mapping and production identity normalization remain **UNRESOLVED**. Synthetic replay cannot prove them.

## 11. Criterion-by-criterion delta table

| Criterion | V2.4.3 decision | V5S.1 decision | Major delta | Direction classification |
|---|---|---|---|---|
| 165 | external-location chemotherapy completion in one report; reject negated/planned | semantic LLM requires external prior chemotherapy and completed/received semantics | whole-report deterministic match -> bounded evidence plus conservative LLM | LIKELY_RECALL_INCREASING for V2.4.3 |
| 185 | first/initial irinotecan regimen; reject prior use | semantic LLM must support first irinotecan-containing regimen | deterministic same-report rule -> conservative LLM; date fallback changed | LIKELY_RECALL_INCREASING for V2.4.3 |
| 265 | cTnI>=0.06 OR cTnT>=0.03 ug/L with analyte/unit parsing | same threshold; MATCH revoked unless analyte-bound numeric payload exists | grounded-payload gate plus loss of scorer-specific coding/extension/time | LIKELY_PRECISION_INCREASING; HIGH visibility risk |
| 485 | POP-Q III or IV; reject negation | deterministic POP-Q III/IV; V5S.1 emits exact branch | decision near-equivalent; top-level code less scorer-specific | NEUTRAL decision; MEDIUM transport risk |
| 555 | event_months(surgery)<=6; reject negated/planned | deterministic recent-surgery rule on selected windows | relative timing serialization weakened; bounded windows may split event/time | LIKELY_RECALL_INCREASING for V2.4.3 |
| 565 | severe diarrhea OR constipation; reject negated/resolved/history-only | conservative semantic LLM over symptom/severity windows | deterministic phrase rule -> conservative model | LIKELY_RECALL_INCREASING for V2.4.3 |
| 615 | OR pT3a/b/4, R1, pN1, GS>=8, PSA>0.1 | deterministic OR over same branches on selected windows | thresholds similar; retrieval and emitted code/time differ | UNKNOWN decision; MEDIUM transport risk |
| 635 | all four value/high pairs and every value<=high | same rule plus post-MATCH all-four grounded gate | similar semantic rule; extra gate and 8-window competition | LIKELY_PRECISION_INCREASING; possible retrieval recall cost |
| 675 | age>=50 AND zoster AND head/face relation; reject family/negated | semantic LLM over group windows; cross-report fusion allowed | cross-report fusion and corrected profile, but conservative prompt | MIXED |
| 735 | listed disease AND active; reject stable/resolved/cured/history | semantic LLM over disease/activity windows | profile corrected; branch code simplified; deterministic -> LLM | UNKNOWN |
| 745 | postoperative marker + needs/receives invasive ventilation; reject noninvasive/preop/no-need | semantic LLM may fuse reports and infer postoperative relation | cross-report positive paths but context-loss/model-rejection paths | MIXED |
| 755 | ventilation_hours>=24; reject planned/negated | same threshold on selected windows | decision similar; FHIR time representation changed | NEUTRAL decision; HIGH transport risk |
| 805 | current smoking OR quit<24 months; reject never/family/unknown | same deterministic rule on selected windows | cessation resource/time and scorer-specific coding removed | LIKELY_RECALL_INCREASING for V2.4.3 transport |
| 835 | explicit coagulation abnormality; reject normal/no-abnormal | semantic LLM requires explicit abnormality | deterministic phrase -> conservative LLM; code/time simplified | LIKELY_RECALL_INCREASING for V2.4.3 |
| 855 | Scr<178, BUN<9, qualitative ALT/AST not elevated | MATCH revoked unless all four numeric components grounded | qualitative path removed; four-resource contract collapsed to one | LIKELY_PRECISION_INCREASING; VERY HIGH recall/visibility cost |
| 875 | deterministic OR; reject clear-conscious/negated | semantic LLM OR; exact branch resource | deterministic OR -> conservative LLM; FHIR branch retained | LIKELY_RECALL_INCREASING for V2.4.3 |

Full pipeline table: `analysis/V243_V5S1_RUNTIME_DELTA.csv`.

## 12. Available-input shadow decision deltas

**UNAVAILABLE.** No legitimate preserved patient input corpus was found that can be safely and exactly replayed through both versions. Hidden inputs and labels were not reconstructed, so no patient-level decision table was generated.

## 13. Top 5 evidence-backed explanations for why V2.4.3 scores higher

Ranked by direct code evidence and plausible impact, without claiming hidden-gold causality:

1. **Scorer-visible payload regression (strongest evidence, high impact).** Exact comparison shows loss of 265 preoperative/code fields, 555 derived date, 755 valid period, 805 cessation resource, and three of four 855 resources. An internal MATCH can become an online false negative.
2. **Conservative decision path (strong evidence, high impact).** Eight criteria moved from deterministic full-report predicates to a prompt that maps insufficient evidence to NO. The recall drop is consistent with, but does not prove, this mechanism.
3. **Grounded payload gates (strong evidence, criterion-limited high impact).** 265, 635, and 855 can revoke MATCH. The 855 change removes a concrete qualitative ALT/AST path.
4. **Bounded sentence retrieval (strong code evidence, medium/high impact).** Eight windows and alias hits improve focus but can omit qualifiers and relations, especially for 165, 555, 635, 745, and 855.
5. **Temporal representation changes (strong evidence, medium impact).** V2.4.3 derives dates from report timestamps and relative intervals; V5S.1 often omits time or falls back to 1970, which can fail date-filtered queries.

## 14. What should NOT be copied from V2.4.3

- Do not fabricate missing numeric values. V2.4.3's 855 decision may be positive without enough numeric material for all four scorer resources.
- Do not copy `datetime.now()` as an evidence date; it is nondeterministic and ungrounded.
- Do not copy legacy profile spellings for 675, 735, 745, 755, or 805 without proving production aliases.
- Do not remove negation, planned-event, history-only, or relation checks merely to increase recall.
- Do not infer hidden labels from aggregate scores.
- Do not copy whole-report matching without controls for unrelated context and cross-entity contamination.

## 15. Smallest possible future experiments

No experiment was implemented. Controlled manual A/B candidates should change one dimension only:

- **A:** V2.4.3 decision/resource code + V5S.1 retrieval, isolating retrieval.
- **B:** V2.4.3 + one criterion rule change, beginning with 855 grounding.
- **C:** V5S.1 decisions + exact V2.4.3 FHIR transport for 265/555/755/805/855, isolating visibility.
- **D:** V5S.1 windows + V2.4.3 deterministic predicates, isolating model conservatism.
- **E:** V5S.1 with only the eight-window cap varied, holding aliases, rules, payloads, and FHIR fixed.

Each future experiment must preserve the frozen V5S.1 artifact and separate internal decisions from scorer-visible resources.
