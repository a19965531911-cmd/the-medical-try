# B5 Live Call Trace

400 fresh isolated-process executions: 100 identical authored labelled synthetic cases for B5-R/H/L plus original B4F. Sources were decoded from actual JSON Libraries; transport was never replaced by stub in this evaluation.
100-case corpus has exactly 20 clear-positive, 20 clear-negative, 20 complex-synonym, 20 state-scope, 20 cross-scope cases. Labels/rationales were authored from criterion logic before evaluation; they are not patient gold.
B5 traces: original record indices (broad retrieval preserves paraphrases), request payload, actual raw response/error, JSON/literal grounding validation, extracted facts, built Bundle and original Service replay. B4F predates raw-response tracing; it records actual transport counters/errors and extraction.
No successful generative response exists in the current environment. Complete text-to-LLM-to-grounded-FHIR success is BLOCKED; rule-to-FHIR-to-Service execution is separately verified.
Actual per-case evidence: experiment/b5/live_traces.json. Prediction table: analysis/B5_PREDICTIONS.csv. Actual bge-m3 chat incompatibility and successful embedding are separate capability probes.
```json
{
  "B5R": {
    "cases": 100,
    "calls": 0,
    "http_success": 0,
    "json_valid": 0,
    "grounded": 0,
    "request_success_rate": null,
    "json_success_rate": null,
    "grounding_success_rate": null,
    "pipeline_mean_seconds": 0.0014800949930213391,
    "pipeline_p95_seconds": 0.0035610999912023544,
    "successful_model_latency_p95": null,
    "fallback_cases": 0,
    "exceptions": 0,
    "error_kinds": {}
  },
  "B5H": {
    "cases": 100,
    "calls": 34,
    "http_success": 0,
    "json_valid": 0,
    "grounded": 0,
    "request_success_rate": 0.0,
    "json_success_rate": 0.0,
    "grounding_success_rate": 0.0,
    "pipeline_mean_seconds": 0.7884013810078614,
    "pipeline_p95_seconds": 2.332667399896309,
    "successful_model_latency_p95": null,
    "fallback_cases": 34,
    "exceptions": 0,
    "error_kinds": {
      "CONNECTION_FAILED": 34
    }
  },
  "B5L": {
    "cases": 100,
    "calls": 74,
    "http_success": 0,
    "json_valid": 0,
    "grounded": 0,
    "request_success_rate": 0.0,
    "json_success_rate": 0.0,
    "grounding_success_rate": 0.0,
    "pipeline_mean_seconds": 1.7070746259973384,
    "pipeline_p95_seconds": 2.338137699989602,
    "successful_model_latency_p95": null,
    "fallback_cases": 74,
    "exceptions": 0,
    "error_kinds": {
      "CONNECTION_FAILED": 74
    }
  },
  "B4F_REFERENCE": {
    "cases": 100,
    "calls": 34,
    "http_success": 0,
    "json_valid": 0,
    "grounded": 0,
    "request_success_rate": 0.0,
    "json_success_rate": 0.0,
    "grounding_success_rate": 0.0,
    "pipeline_mean_seconds": 0.7160262819984928,
    "pipeline_p95_seconds": 2.1146685001440346,
    "successful_model_latency_p95": null,
    "fallback_cases": 0,
    "exceptions": 0,
    "error_kinds": {
      "CONNECTION_FAILED": 34
    }
  }
}
```
