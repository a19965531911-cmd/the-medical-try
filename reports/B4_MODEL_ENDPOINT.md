# B4 Model Endpoint

Actual B4H.json was decoded and its bound _b4_transport invoked on synthetic evidence.
Embedded settings: loopback-only endpoint, model=local-model, max_tokens=2048, socket timeout=5 seconds; no retries. Socket timeout is not a guaranteed total deadline.
No trusted server launcher/weights identified; software absence is not asserted. No models downloaded or external/paid calls made.
```json
{
  "status": "LIVE_MODEL_UNAVAILABLE",
  "endpoint": "http://127.0.0.1:1213/v1/chat/completions",
  "real_calls": 1,
  "error": "URLError: <urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>",
  "http_success": 0,
  "json_valid": 0,
  "grounded": 0,
  "mean_seconds": 0.0009445999749004841,
  "p95_seconds": 0.0009445999749004841
}
```

Native Windows loopback verification (separate from sandbox socket restrictions):
```json
{
  "execution_context": "NATIVE_WINDOWS_LOOPBACK",
  "status": "LIVE_MODEL_UNAVAILABLE",
  "synthetic_only": true,
  "endpoint": "http://127.0.0.1:1213/v1/chat/completions",
  "models_error": "URLError: <urlopen error [WinError 10061] 由于目标计算机积极拒绝，无法连接。>"
}
```
Native embedded call metrics:
```json
{
  "calls": 1,
  "http_success": 0,
  "responses": 0,
  "json_valid": 0,
  "grounded": 0,
  "fact_rejections": 0,
  "errors": [
    {
      "kind": "CONNECTION_FAILED",
      "message": "URLError: <urlopen error [WinError 10061] 由于目标计算机积极拒绝，无法连接。>"
    }
  ],
  "latencies": [
    2.042098500067368
  ]
}
```

Per-call errors, fallback results, JSON/evidence metrics and latency: experiment/b4-semantic-recall/model_endpoint.json.
Native probe evidence: native_endpoint.json. Native WinError 10061 means the target refused the connection; the model type/actual deployed model ID remains unidentified (local-model is only the inherited API placeholder).
Stub metrics in the variant matrix are controlled tests, not live model accuracy. Run scripts/run_b4.ps1 -Live after restoring the trusted local service.
