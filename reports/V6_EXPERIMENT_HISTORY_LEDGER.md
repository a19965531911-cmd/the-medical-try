# V6 Experiment History Ledger

## Frozen baseline

| Experiment | Result | Engineering lesson |
|---|---|---|
| E | champion, macro F1 `0.16666666666666666` | rollback baseline; preserve proven scorer contract |
| F | `0.15` | transport over-recovery increased false positives |
| G | `0.10416666666666666` | broad admission expansion failed online despite valid local replay |
| H/H1 | same as E | narrow rescue produced no useful online coverage |
| I | blocked | no safe scorer-surface gap was proven |
| J | blocked | no safe new decision path for 635/855 |

## V6 constraints

1. Improve evidence completeness without lowering admission thresholds.
2. Treat local `MATCH + FHIR VALID + SERVICE_HIT` as transport evidence, not correctness evidence.
3. Never fabricate a payload or infer a missing criterion component.
4. Keep scorer mappings from E/C/I unchanged until a contract mismatch is proven.
5. Return `UNKNOWN` for missing or unresolved required evidence; `UNKNOWN` emits no resource.
6. Keep Experiment E as the rollback baseline. This prototype is not connected to a candidate builder.

Production candidate: **NOT GENERATED**. Tianchi: **NOT SUBMITTED**.
