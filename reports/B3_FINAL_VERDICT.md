# B3 Final Verdict

```text
A_CHAMPION = V5S.2 Experiment E (unchanged)
B_OFFLINE_BEST = B3 (B2E plus reproduced runtime guards)
B_ONLINE_VERIFIED = NO
B_BOARD_READY = NO
FSH_VIOLATIONS_REMAINING = 18 cases (existing subset validator)
MODEL_ENDPOINT_STATUS = UNAVAILABLE
PUBLICATION_IDENTITY_STATUS = UNRESOLVED
```

The manual-review candidate is experiment/b3-final/B3.json. Build/compile/reload checks pass, but it is not cleared for publication and is not an online champion. No Tianchi submission was performed.

## Verified Changes

B3 appends guards to the complete frozen B2E source. Three tests first reproduced: extra model JSON fields were accepted; categorical rescue could merge separate events; the actual embedded entrypoint retained pathology provenance from another event. B3 validates a closed facts schema, rejects duplicate/nonfinite JSON and requires literal source quotes, then recomputes facts in one linked event using the same single model response. Event guards preserve a genuine eligible event and cannot create numerical facts or override deterministic vetoes. Local transport now exposes its error/duration while preserving endpoint, token budget, timeout and deterministic NO fallback.

## Actual Package Evidence

```json
{
  "synthetic_cases": 167,
  "matches": 71,
  "service_hits": 71,
  "service_differences": 0,
  "b2e_deterministic_decision_deltas": 0,
  "fsh_violating_cases": 18,
  "local_r4_subset_violations": 0,
  "isolated_libraries": 16,
  "concurrent_processes_passed": 16,
  "concurrent_workers": 4,
  "offline_model_stub_calls": 7,
  "matrix_seconds": 0.3868923985864967,
  "publication_gate": "BLOCKED: Publication blocked: official tbd/null routing contract unverified",
  "formal_profile_validator": "UNAVAILABLE",
  "gold_labels": "UNAVAILABLE"
}
```

All 16 final wrappers reach evaluate_b2 and build_b2_resources; frozen _B1 aliases intentionally provide underlying extraction/building, not a fallback to a previous submitted package. Duplicate definitions are recorded in results.json and their final bindings verified. Each final source keeps the exact B2E prefix; no later packaging/template pass overwrites it. 16/16 Libraries pass Python -I positive/empty execution and original unchanged offline Service queries. Concurrent entrypoint checks use distinct generator instances; last_result is per instance and a shared instance is not guaranteed to retain per-request diagnostics.

Strict serialized-file reload and local R4 subset pass; known FSH conflicts remain. Original Service code is replayed with offline FHIR mocks/frozen date, not a live official FHIR deployment. NO model stubs are used only for offline deterministic replay and counted. No gold labels: no precision/recall/F1 claim. The B2 six-strategy experiment was not repeated.

## External Dependencies and Stop Condition

Official profile 2/3 mapping, B MessageHeader contract and official checker/IG remain external dependencies. The 18 FSH cases are official specification/evidence conflicts, not a reason to invent values. Model startup requires a trusted project-defined service configuration. All available local checks have a finite stopping point; further ungrounded rule changes or blind validation uploads are not recommended.

## Final Regression Evidence

- B focused tests: 227 passed in 4.97 seconds, exit 0; `analysis/B3_FOCUSED_RESULTS.xml`.
- Full repository regression: 935 passed in 127.21 seconds, exit 0; `analysis/B3_PYTEST_RESULTS.xml`.
- Actual-file publication gate: exited 1 with `official tbd/null routing contract unverified`; blocked as required.
- Final frozen A/B1/B2E source/artifact hashes and B3 candidate hash verified after all executions.
- B3 SHA256: `ee39e779f48927b2a01b976d15b2c6eab32370d21ceae43a0f82cc4da4818119`.

Reproduce with the existing bundled Python executable at `C:/Users/32433/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`:

```powershell
python scripts/audit_b3_final.py
python -m pytest tests/b_board -q --junitxml=analysis/B3_FOCUSED_RESULTS.xml
python -m pytest -q --junitxml=analysis/B3_PYTEST_RESULTS.xml
```

Online update: the user confirmed a final score of 0.0000 for B3.json on the
2026-10-09 21:27:07 submission, correcting an earlier B2E filename attribution.
This is a user-confirmed score, not successful online validation. Server-side
artifact hash, execution and scoring logs remain unavailable. See B3_ZERO_SCORE.md.

All available local acceptance checks have completed. Complete official publication validation and live-model testing remain unavailable for the external reasons documented above; tests do not override these gates.
