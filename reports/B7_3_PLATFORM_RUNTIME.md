# B7.3 Platform Runtime

|Item|SAMPLE_SUPPORTED|OFFICIAL_DOCUMENTED (B runtime)|PLATFORM_LIVE_VERIFIED|
|---|---|---|---|
|1213 chat/completions/local-model|YES|UNVERIFIED beyond supplied sample|NO|
|requests usable|Sample import/call YES|Image/dependency manifest not supplied|NO|
|30s request timeout/one retry|Code observation YES|Not a server quota declaration|NO|
|Task time/call/concurrency quota|NO|UNVERIFIED|NO|
|Timeout causes whole evaluation failure|NO|UNVERIFIED|NO|
|Model/error logs visible|NO|UNVERIFIED|NO|

Exact sample decoded lines:
```json
[
  {
    "entry": 1,
    "lines": [
      {
        "line": 23,
        "text": "        self.llm_url = \"http://127.0.0.1:1213/v1/chat/completions\""
      },
      {
        "line": 24,
        "text": "        self.llm_timeout = 30"
      },
      {
        "line": 25,
        "text": "        self.llm_max_tokens = 256"
      },
      {
        "line": 26,
        "text": "        self.llm_temperature = 0.0"
      },
      {
        "line": 68,
        "text": "            \"model\": \"local-model\","
      },
      {
        "line": 73,
        "text": "            \"temperature\": self.llm_temperature,"
      },
      {
        "line": 74,
        "text": "            \"max_tokens\": self.llm_max_tokens,"
      },
      {
        "line": 78,
        "text": "        for _ in range(retry + 1):"
      },
      {
        "line": 80,
        "text": "                resp = requests.post(self.llm_url, json=payload, timeout=self.llm_timeout)"
      },
      {
        "line": 82,
        "text": "                content = resp.json()[\"choices\"][0][\"message\"][\"content\"]"
      }
    ]
  }
]
```
Sample path C:\Users\32433\xwechat_files\wxid_4r7tcofyke6922_c386\msg\file\2026-10\tccfile-one hash ac320362548e20089566de8b18e53a01a781f2576911163232b1f596b374e20d. A485 test_a is protocol evidence, not B release contract. Final B7.3 uses max_tokens2048 and8s caller budget, one call, no retries; not the sample256/30s policy. Actual transport requests timeout limits inactivity; caller thread timeout does not cancel server request.2slots per namespace/32 across16; slow trickle can retain slots. Sessions exit when request ends; no hard lifecycle guarantee. Local Windows failure says nothing about platform provisioning. No LIVE inference response obtained.
