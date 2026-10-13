# B4 Reproduction

Run from this repository in native Windows PowerShell:

```powershell
& ./scripts/run_b4.ps1
# Synthetic records only; invokes the authorized local model when restored:
& ./scripts/run_b4.ps1 -Live
```

The launcher uses the existing bundled Python by absolute path. Test dependencies
are in `work/b4-python-deps` (pytest 9.1.1, PyYAML 6.0.3); the existing runtime supplies
openpyxl. A clean checkout needs the repository's requirements and requirements-dev
installed in its existing chosen environment. No interpreter or model reinstall is
required. Adjust the launcher interpreter path for another host.

Variants are independently executable 16-Library message bundles: B4R (rules),
B4L (LLM-first), B4H (hybrid), B4I (item fallback), B4S (OR-only single profile),
and B4F (engineering candidate using H). Each has its own config, manifest,
run log and evidence matrix. Reload the desired JSON to switch or roll back;
no original B2E/B3/A artifact is overwritten.

The local model configuration is embedded in the actual Python source. To build
with the documented identity of a restored trusted local model, call
`build_variant("B4H", {"model": "actual-local-model-id"})` and save the result to
a new path. External endpoints are rejected. B4R deliberately makes no model
calls; B4L fails closed when the model returns UNKNOWN or cannot be reached.

`regression.xml`, `isolated.json`, `model_endpoint.json`, `publication_gate.json`
and each variant's `results.json` are the verification evidence. Five ablation
packages and their actual execution results are in `ablations/`.

All test cases are synthetic. Stub semantic positive responses are explicitly
specified fixtures, never a proxy for live model performance. Every output retains
an unknown real patient label. The local FSH/R4 validators are incomplete; 18 known
contract conflicts remain. B4F is an offline review artifact and cannot be treated
as an approved submission. Official identity/header/checker and scoring formula
remain unverified. No online submission is performed by these scripts.
