# V5S.4 Target Feasibility

## Online Evidence

Raw Experiment E/F/G line-level online metrics logs are unavailable in the repository and supplied attachments. Criterion-level 51-case funnel counts therefore remain unresolved and are not fabricated.

## Selection

Selected target: `485` only.

Reason: explicit POP-Q III evidence can produce a grounded `Observation` with an existing scorer-compatible profile and `valueCodeableConcept`, and the local service replay returns `SERVICE_HIT`.

Rejected targets:

- `635`: complete numeric labs can be visible, but the requested online differential cannot be audited from raw logs; no change is admitted.
- `855`: same payload/online uncertainty; qualitative or partial labs are rejected.

The H candidate does not inherit the G overlays for `635`, `855`, `675`, `735`, or `745`.

## Grade

485: `A` for the supported `POP-Q III` scorer path.

`POP-Q IV/Ⅳ` is intentionally not admitted because the current local scorer contract accepts the `III` value path only. No fabricated IV representation is introduced.
