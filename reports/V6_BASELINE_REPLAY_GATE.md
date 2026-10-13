# V6 BASELINE GATE BLOCKED

## Online champion reference

Experiment E, macro F1 `0.16666666666666666`.

The exact historical E artifact was recovered from Git and matches the frozen SHA. The current workspace E file is byte-different but semantically equivalent after Bundle parsing and 16/16 decoded-source comparison.

## Same-input replay

Replay artifact: `analysis/V6_E_VS_V6_FIXTURE_REPLAY.json`  
Stability artifact: `analysis/V6_ADMISSION_STABILITY_V2.json`

The same V6 fixtures were executed through the exact recovered E Library runtime and the V6 prototype. E semantic-dependent rows used a deterministic `YES` transport stub because the historical local model endpoint is unavailable. Those rows are marked `UNRESOLVED`, not treated as E ground truth.

Summary:

- exact E provenance: **PASS**
- V6 execution: **PASS**
- semantic-independent E rows: executed
- safe E -> V6 completion: `0`
- unsafe relaxation: `0`
- deterministic regression: `1` (`675_missing_site`, E accepted partial evidence while V6 correctly returned UNKNOWN)
- semantic-dependent unresolved rows: `11`
- Test-A unlabeled patient text: **NOT_FOUND**

The positive fixtures mostly produce `MATCH` in both systems, so they are `NO_CHANGE` or `UNRESOLVED`, not architectural gains. No case satisfies the strict SAFE_COMPLETION definition with an actual reproducible E semantic decision and a demonstrated V6-only gain.

## Gate decision

**V6 BASELINE GATE BLOCKED**

The gate requires at least three actual architecture-level safe gains, or two including 745. The current evidence establishes no such gain. `UNSAFE_RELAXATION=0` is necessary but insufficient.

Production candidate: **NOT GENERATED**  
Experiment E: **NOT OVERWRITTEN**  
Tianchi: **NOT SUBMITTED**

## Reason

V6 prototype behavior is internally coherent, but superiority over the actual E runtime is not demonstrated on the available fixtures. The remaining uncertainty is the unavailable semantic E transport and the absent unlabeled Test-A patient corpus. Do not proceed to production V6 integration.
