# B5 Native Evaluation

```powershell
& ./scripts/run_b5.ps1
```

This executes 100 authored synthetic labelled cases per variant in fresh isolated
Python processes: B5R, B5H, B5L and the original B4F JSON (400 evaluations). No
transport stub is used. Actual model requests require native loopback access;
sandbox-only socket denials must be reported separately from native failures.

The existing bundled Python is used by absolute path with dependencies already
available in `work/b4-python-deps` and its runtime. The official criterion workbook
is read from `C:/Users/32433/Desktop/CHIP2026-CP2-data-test_b.xlsx`.

Current environment: trusted Ollama 0.32.14 at `D:/DeepTutor/ollama/ollama.exe`,
existing weights in `D:/DeepTutor/ollama-models`, bge-m3:latest only. Its embedding
API works, but its chat API rejects the model as unsupported. No generation model
was downloaded. Port 1213 has no discovered server.

The audit's temporary Ollama process was stopped at completion. To restart the
existing local service without downloads, use `scripts/start_b5_existing_ollama.ps1`.
It refuses to start over an existing listener and disables cloud access/pruning.

Run the separate capability audit against an already running local server:

```powershell
& 'C:/Users/32433/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' scripts/b5_model_environment.py
```

After an authorized generative model is available, use its verified model ID and
OpenAI-compatible loopback endpoint:

```powershell
& ./scripts/run_b5.ps1 -Endpoint http://127.0.0.1:11434/v1/chat/completions -Model ACTUAL_LOCAL_CHAT_MODEL
```

The evaluator embeds the same endpoint and model configuration into H and L.
One model request is allowed per Library/record set with a four-second total
generation budget. This budget may be insufficient for a large local model; it
is an explicit deployment constraint, not a performance claim. JSON/evidence
validation is inherited from frozen B4F, while the B5 layer retains detailed raw
request/error traces and enforces a killable HTTP subprocess deadline.

`live_traces.json` contains original evidence, authored expected labels/rationales,
actual Library output and official Service replay. `evaluation.json` includes
per-profile confusion matrices. `model_environment.json` includes native version,
model capabilities/digest, chat rejection and embedding verification.

The runner does not select a semantic winner automatically even when an endpoint
responds. Current `B5_candidate.json` is created only after successful code checks
and is the rule-equivalent engineering fallback. It is not officially publishable.
No Tianchi upload is performed. The 18 known FSH conflicts, 2/3 identity and
MessageHeader contract require official clarification.
