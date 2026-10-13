# B3 Live Model Diagnosis

MODEL_ENDPOINT_STATUS = UNAVAILABLE

Project and sibling configuration/startup scans found endpoint consumers and historical runtime-contract documents, but no defined trusted model-service launcher, model path, weights or deployment configuration for port 1213. No service was invented or downloaded. Normal process inventory identified no model server; privileged process command-line inventory was denied. This does not claim model software is uninstalled.

Actual localhost model-list request and status:
```json
{
  "endpoint": "http://127.0.0.1:1213/v1/chat/completions",
  "startup": "NO_PROJECT_DEFINED_TRUSTED_STARTUP_FOUND",
  "downloads": false,
  "external_paid_calls": false,
  "patient_data_sent": false,
  "tests": [
    {
      "case": "NO_MATCH",
      "status": "NOT_RUN_ENDPOINT_UNAVAILABLE",
      "real_model": false
    },
    {
      "case": "POSITIVE",
      "status": "NOT_RUN_ENDPOINT_UNAVAILABLE",
      "real_model": false
    },
    {
      "case": "NEGATION_UNCERTAINTY",
      "status": "NOT_RUN_ENDPOINT_UNAVAILABLE",
      "real_model": false
    },
    {
      "case": "PARTIAL_JSON_RESCUE",
      "status": "NOT_RUN_ENDPOINT_UNAVAILABLE",
      "real_model": false
    }
  ],
  "status": "UNAVAILABLE",
  "availability_error": "URLError: <urlopen error [WinError 10061] 由于目标计算机积极拒绝，无法连接。>",
  "availability_seconds": 2.196015600115061,
  "fault_tests": "Controlled malformed JSON and timeout tests are offline tests, not real model results"
}
```

Reproduce availability with the bundled Python: urllib.request.urlopen('http://127.0.0.1:1213/v1/models', timeout=5). When a trusted project service is supplied, rerun this audit; the four synthetic real probes run only after availability succeeds. No genuine patient text is used.

Offline fault-injection tests verify malformed/duplicate/nonfinite JSON, extra fields, nonliteral evidence and TimeoutError degradation. They are explicitly not live-model tests. Production request timeout remains 30 seconds (socket timeout, not a guaranteed end-to-end deadline), no retry, max_tokens=1024. B3 records transport errors/duration instead of silently concealing failure. Token adequacy and real multi-patient model throughput remain unverified.
