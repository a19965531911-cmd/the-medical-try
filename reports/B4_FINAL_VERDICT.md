# B4 Final Verdict

```text
A_CHAMPION = V5S.2 Experiment E (frozen)
B_OFFLINE_BEST = B2E (retained; B4F engineering candidate unverified)
B_ONLINE_VERIFIED = NO
B_BOARD_READY = NO
LIVE_MODEL_STATUS = LIVE_MODEL_UNAVAILABLE
MODEL_ENABLED_IN_EMBEDDED_CODE = YES (actual bound transport tested; live success separate)
LIBRARIES_PASSED = 16/16 B4F fresh-process positive and empty executions; original Service replay
REGRESSION_TESTS = PASS 1007 passed in 130.23s (0:02:10)
FHIR_VALIDATION = LOCAL_R4_SUBSET_ONLY; full FSH validator unavailable
FSH_VIOLATIONS_REMAINING = 18 cases in B4F matrix (clinical/contract conflicts retained)
PUBLICATION_IDENTITY = UNVERIFIED (2/3 tbd/null and MessageHeader)
OFFICIAL_CHECKER = UNAVAILABLE
BEST_VARIANT = B4H/B4F engineering recommendation; no live/gold champion selection
RECOMMENDED_NEXT_ACTION = Restore trusted local model; run -Live; obtain official identity/FSH contracts and legal gold labels
```

No real leaderboard improvement or target attainment is claimed. Model unavailability prevents completing the real-model goal. Frozen files hash-verified unchanged.
All six variants passed 16 fresh-process import/entrypoint/empty checks (96 total); L intentionally remains empty with NO stub. The 40 new B4 tests cover guarded categorical recall and attacks; original tests/expected results were preserved.
Initial full run: 1002 passed, 1 Git ownership failure. Process-local safe.directory configuration repaired that environment failure; final complete run above passed. No global Git configuration was changed.
Native loopback probe also confirmed connection refusal (WinError 10061); no trusted launcher/weights were found. Numerical semantic recovery, actual LLM accuracy/throughput, complete FHIR validation and real scoring remain unverified.
B4F.json is an offline review artifact only. Full matrix, stage evidence, configs, isolated checks, five ablation packages and candidate pack are under experiment/b4-semantic-recall.
One-command reproduction: powershell -ExecutionPolicy Bypass -File scripts/run_b4.ps1. Add -Live for local-model synthetic matrix.
Port probing inside this environment may be restricted; recorded endpoint failure is scoped to the actual execution context.
