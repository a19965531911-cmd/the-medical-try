# B2 LLM Rescue Validation

Actual localhost:1213 chat-completions request attempted; no stub substituted for endpoint availability.

```json
{
  "endpoint": "http://127.0.0.1:1213/v1/chat/completions",
  "real_model": false,
  "token_budget": 1024,
  "timeout_seconds": 30,
  "probe_timeout_seconds": 5,
  "status": "UNAVAILABLE",
  "error": "URLError: <urlopen error [WinError 10061] 由于目标计算机积极拒绝，无法连接。>",
  "elapsed_seconds": 2.1274377000518143
}
```

Endpoint unavailable: real schema adherence, extra fields, Chinese negation/history/plans/uncertainty, token adequacy, multi-patient latency and timeout behavior remain UNVERIFIED. 1024 tokens and inherited 30 second timeout unchanged. Experimental matrix transport uses NO stub and explicitly counts stub calls; it is not model performance.

B1 categorical unknown-only rescue and evidence grounding are retained. It cannot change deterministic negative/absent/planned/uncertain facts or fill numeric profiles. Event-veto is UNCERTAIN and cannot be rescued. Tests cover JSON malformed responses, extra facts, missing grounding, planned/negative states and XHTML injection. Patient text is data; generated XHTML escapes it. More complex prompt injection and model interpretation cannot be certified without a live endpoint.

Offline tests establish that unrecognized facts/top-level match flags cannot create accepted facts and that deterministic veto states bypass the model. The inherited parser ignores extra keys; it does not enforce a closed JSON schema. Grounding uses normalized substring comparison, not literal byte-for-byte matching. These limitations remain documented, and no live model reliability claim is made. The availability probe uses a 5-second network timeout; the inherited production transport uses 30 seconds.
