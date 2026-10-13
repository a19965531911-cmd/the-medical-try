B7_STATUS = OFFLINE_RESEARCH_ACCEPTANCE; PLATFORM_BLOCKED
REGRESSION = 1116 passed in207.90s; exit0
LIBRARIES_VERIFIED = 16/16 fresh-process positive+empty execution; Service PASS
HTTP_WORKER_LIMIT = 2 per namespace;32 across16; no unbounded worker creation
HTTP_RESOURCE_LEAKS = slots reclaimed in delay checks; indefinite trickle can occupy slots, cannot cancel server work
TIMEOUT_MATRIX = 640 virtual combinations +3 actual delay checks
SCHEMA_VALIDATION = 17 checks passed
POSITIVE_RESCUE_CASES = 7 targeted profiles plus attacks/incomplete
RESCUED_TRUE_POSITIVES = 5
INTRODUCED_FALSE_POSITIVES = 0
FHIR_SERVICE_SUCCESSFUL_RESCUES = 5
B6H_SYNTHETIC_F1 = 1.0
B7H_SYNTHETIC_F1 = 1.0
B6H_SYNTHETIC_RECALL = 1.0
B7H_SYNTHETIC_RECALL = 1.0
PLATFORM_LIVE_INFERENCE_VERIFIED = NO
B7_OFFLINE_CANDIDATE = B7H research artifact
B_OFFLINE_BEST = B2E retained; no stable B7-specific clinical improvement
B_BOARD_READY = NO
REMAINING_BLOCKERS = platform time quota/live model;2/3 identities;MessageHeader;18 FSH conflicts;official checker; actual token-quality study


SYNTHETIC local HTTP fixture metrics: {"trigger_rate": 0.5813953488372093, "http_rate": 1.0, "json_rate": 0.72, "grounding_rate": 0.72, "accepted_facts": 8, "unproductive": 20, "service_rate": 1.0, "p95_synthetic_http": 0.02912100008688867}
Grounding rate uses inherited schema+literal gate; semantic acceptance separately counted. No real Qwen/token success claim. Virtual matrix is a schedule model, not direct transport measurement for all faults. Worker lifetime cancellation and slow-trickle Session closure are not proven.
