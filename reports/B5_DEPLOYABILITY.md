# B5 Deployability

MODEL_DEPLOYABILITY_VERDICT = UNVERIFIED_AND_BLOCKED
Local Ollama 11434 is user-host-specific and provides only embedding. No evidence confirms Tianchi permits outbound/local model requests or supplies localhost:1213; inheriting E's client string cannot establish the execution contract.
B5-H/L can embed a verified local OpenAI-compatible model endpoint/name via CLI; no automatic cloud route or model downloads. /api/show must establish generation capability and the corpus must pass real end-to-end evaluation before selecting a semantic candidate.
Actual embedded B5 transport enforces loopback HTTP, disables proxies, max_calls=1 per Library/record set, total generation budget=4 seconds, subprocess kill/wait on total timeout and no retries. Process startup/cleanup and deterministic work add overhead; it is not a whole-Library hard deadline. Parent isolation timeout=15 seconds.
16 Libraries do not share process-local caches. Worst configured model wait is 16*4=64 seconds per patient if all are separately invoked, plus startup/rule/FHIR overhead. No claim this satisfies an unknown platform quota. Cross-Library deduplication requires platform support and remains unresolved.
Connection/invalid-response failures explicitly fall back to rules; fallback success is not model success. L's valid UNKNOWN does not force YES. B5-R never calls a model.
Official 2/3 identity, MessageHeader, runtime subprocess permission, available Python/network behavior, server model/version and total time allowance require official confirmation. No submission or gate removal performed.
