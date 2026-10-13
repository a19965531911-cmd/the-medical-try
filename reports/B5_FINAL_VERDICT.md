# B5 Final Verdict

```makefile
A_CHAMPION = V5S.2 Experiment E (frozen)
B_OFFLINE_BASELINE = B2E (frozen)
B5_BEST_CANDIDATE = B5R (rule-equivalent engineering artifact; no semantic gain proven)
B_ONLINE_VERIFIED = NO
B_BOARD_READY = NO
MODEL_FOUND = YES (trusted Ollama with embedding-only bge-m3)
MODEL_NAME = bge-m3:latest; generative model NOT_FOUND_IN_INSPECTED_SCOPE
MODEL_ENDPOINT = 11434 embedding works; required 1213 chat refuses connection
LIVE_REQUEST_SUCCESS = embedding YES; clinical structured generation NO
EMBEDDED_LLM_EXECUTION = actual attempts verified; zero successful generative responses
MODEL_DEPLOYABILITY_VERDICT = UNVERIFIED_AND_BLOCKED
SYNTHETIC_PRECISION = live LLM UNAVAILABLE; B5R 0.9523809523809523; B5H guarded fallback 1.0
SYNTHETIC_RECALL = live LLM UNAVAILABLE; B5R 0.851063829787234; B5H guarded fallback 0.851063829787234
SYNTHETIC_F1 = live LLM UNAVAILABLE; B5R 0.898876404494382; B5H guarded fallback 0.9195402298850575
LATENCY_P95 = successful live LLM UNAVAILABLE; measured failure/fallback latency in analysis/B5_LATENCY.json
FHIR_VALIDATION = LOCAL_SUBSET_ONLY
FSH_VIOLATIONS_REMAINING = 18 legacy cases
PUBLICATION_IDENTITY = 2/3 tbd/null and MessageHeader UNVERIFIED
OFFICIAL_CHECKER = UNAVAILABLE
RECOMMENDED_NEXT_ACTION = Provide an authorized existing generative model or explicitly authorize a trusted model download; verify platform model/runtime contract; rerun actual corpus
```

MODEL_ENVIRONMENT_BLOCKED: installed model cannot generate the required JSON. Real semantic improvement goal remains unmet; embedding success is not substituted.
Regression: {"status": "PASS", "exit_code": 0, "summary": ["1017 passed in 182.74s (0:03:02)"]}. Frozen files hash-verified unchanged. No online upload.
Reproduce: scripts/run_b5.ps1. For an authorized verified local chat model: scripts/run_b5.ps1 -Endpoint http://127.0.0.1:PORT/v1/chat/completions -Model MODEL_ID.
