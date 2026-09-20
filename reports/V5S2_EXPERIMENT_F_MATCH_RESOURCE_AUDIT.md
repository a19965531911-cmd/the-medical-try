# V5S.2 Experiment F MATCH to Resource Audit

## Scope and Evidence

This audit covers only the five online Experiment E rows reported as `final_decision=MATCH` with zero emitted resources: criterion 265 x1, 555 x2, and 755 x2. It compares the frozen Experiment E source, Experiment C transport overlay, V2.4.3 Library builders, and preserved scorer queries. No hidden labels are used.

The frozen Experiment E candidate is `submission/a_test_message_bundle_v5s2_expe_aggressive_candidate.json`, size 702059 bytes, SHA256 `40457de3149c7db34daf9c3545199c7c8f409ec65b6ae4412f6ca6a77df6d96e`.

## Data Flow

Experiment E computes the final decision first, then calls `_expe_payload`, `derive_transport_meta`, and `build_expc_resources` only for selected transport criteria. This preserves a MATCH even when the compiler returns an empty resource list. The loss therefore occurs after decision admission and does not imply a decision-policy failure.

## Criterion 755 x2

The frozen `rule_decide` accepts ventilation text followed by a numeric duration in hours or days and returns `RULE_DURATION`. `_expe_payload` then performs a second, narrower extraction: it omits the `gas tube intubation` and `MV` aliases accepted by the rule. Any row admitted through one of those unmatched prefixes can retain `MATCH` while losing `duration_hours` before transport.

`derive_transport_meta` merely copies `values["duration_hours"]`; it does not recover the duration from the successful rule path. `build_expc_resources` additionally requires a report timestamp so it can create the scorer-required ISO `performedPeriod.start/end`. The preserved 755 scorer query filters the mechanical-ventilation profile and validates a period of at least 86400 seconds.

Classification: **E - regex recognizes narrower wording**, followed by **C - transport-meta mismatch**. Recovery is safe when both the already-grounded duration and report timestamp exist. If the timestamp is absent, the row remains `BLOCKED_NO_SAFE_PAYLOAD`; inventing a period endpoint is prohibited.

## Criterion 555 x2

Experiment E admits `surgery anchor + semantic MATCH + no explicit >6 month contradiction` without requiring an exact relative date. `_expe_payload` therefore may contain no surgery interval. `derive_transport_meta` only recognizes an explicit `N months ago` phrase. `build_expc_resources` requires both that interval and a report timestamp before calculating `performedDateTime`.

The preserved scorer query requests the 555 Procedure profile with a date lower bound representing the six-month window. Resource existence or profile alone is insufficient. V2.4.3 calculated the date only after its rule extracted a relative interval. The older V5S.1 1970 fallback is outside the scorer window and is not a scorer-visible positive representation.

Classification: **A - payload extraction missing** and **F - required scorer field genuinely unavailable**. The two supplied online patterns are not safely recoverable without a grounded surgery date or interval and must remain `BLOCKED_NO_SAFE_PAYLOAD`.

## Criterion 265 x1

Experiment E admits `troponin anchor + semantic MATCH + no explicit below-threshold contradiction` without requiring a measurement. The frozen payload extractor and Experiment C builder require an analyte-bound numeric value. The 265 scorer query checks the serum/preoperative profiles, the cTnI/cTnT coding, the preoperative extension, and a numeric `valueQuantity` against the analyte threshold.

The criterion threshold is not a patient measurement and cannot be copied into `valueQuantity`. Neither V2.4.3 nor Experiment C contains a non-numeric generic marker that satisfies the preserved scorer query.

Classification: **A - payload extraction missing** and **F - required scorer field genuinely unavailable**. The supplied qualitative online row must remain `BLOCKED_NO_SAFE_PAYLOAD` unless its selected evidence actually contains a grounded analyte-bound number missed by extraction.

## Recovery Decision

| Criterion | Lost online rows | Safe compiler recovery | Required grounded facts | Result |
|---|---:|---:|---|---|
| 265 | 1 | 0 | analyte and patient measurement | `BLOCKED_NO_SAFE_PAYLOAD` |
| 555 | 2 | 0 | surgery date or relative interval plus report timestamp | `BLOCKED_NO_SAFE_PAYLOAD` |
| 755 | 2 | 2 conditional | ventilation duration plus report timestamp | `GROUNDED_METADATA_REUSE` |

Experiment F must not force 5/5. Its legal target is two 755 recoveries, with 265 and 555 explicitly blocked when scorer-required facts are absent.
