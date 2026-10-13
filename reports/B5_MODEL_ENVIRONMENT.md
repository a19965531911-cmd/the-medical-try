# B5 Model Environment

B4F actual embedded request: HTTP POST /v1/chat/completions, application/json, model=local-model, temperature=0, max_tokens=2048, messages[{role:user,content:criterion+records+schema}], response choices[0].message.content. It is OpenAI-compatible, not a custom port-inferred protocol.
Native Windows PowerShell 7.6.5; Python 3.12.14 validated by absolute path. WSL_DISTRO_NAME empty.
Normal resolution/Get-Command/where did not find Ollama/lms/llama-server. PATH inspected; scoped common installation and D:/DeepTutor/D:/AI_Agent_Toolkit/D:/tools searches discovered trusted D:/DeepTutor/ollama/ollama.exe. Absolute --version validated 0.32.14; PATH was not overwritten.
Existing Start-DeepTutor.cmd defines OLLAMA_MODELS=D:/DeepTutor/ollama-models and local port 11434. Service started with existing weights, loopback binding and OLLAMA_NO_CLOUD=1. No models downloaded, cloud/paid calls or real patient texts sent.
The temporary audit Ollama service (owned PID 5548) was stopped after capability verification. Reproduce startup with scripts/start_b5_existing_ollama.ps1; it uses existing weights, hidden process, loopback, cloud disabled and no pruning/download.
Only registered weight is bge-m3:latest (BERT 566.70M F16). /api/show declares embedding capability; chat returns 400 does not support chat. Actual /api/embed returned one 1024-dimensional vector. This proves local inference, not clinical JSON generation.
LM Studio/llama.cpp standalone/medical chat weights were not discovered in scoped common directories or existing environments. Bundled Python lacks torch/transformers/llama_cpp; existing model cache directories and project launchers were checked. Software absence beyond the inspected scope is not asserted.
Proxy-bypassed native requests: 1213 WinError10061 connection refusal; 11434 HTTP200. Therefore sandbox/socket/proxy problems alone do not explain 1213. The installed model is capability-incompatible with the existing generation client.
Firewall changes were unnecessary: actual loopback 11434 inference succeeded. Platform 1213 service contract remains undocumented.
```json
{
  "os": "Windows-11-10.0.26200-SP0",
  "python": "C:\\Users\\32433\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe",
  "python_version": "3.12.14 (main, Aug 25 2026, 14:01:42) [MSC v.1944 64 bit (AMD64)]",
  "wsl": null,
  "model_found": true,
  "usable_chat_model": false,
  "installation_paths": [
    {
      "path": "D:\\DeepTutor\\ollama\\ollama.exe",
      "exists": true
    },
    {
      "path": "D:\\DeepTutor\\ollama-models",
      "exists": true
    },
    {
      "path": "C:\\Users\\32433\\.ollama\\models",
      "exists": false
    },
    {
      "path": "C:\\Users\\32433\\.lmstudio\\models",
      "exists": false
    },
    {
      "path": "C:\\Users\\32433\\.cache\\huggingface\\hub",
      "exists": false
    },
    {
      "path": "D:\\models",
      "exists": false
    }
  ],
  "local_env": {
    "OLLAMA_MODELS": null,
    "OLLAMA_HOST": null,
    "HF_HOME": null
  },
  "downloads": false,
  "external_calls": false,
  "patient_data_sent": false,
  "ollama_version": {
    "exit_code": 0,
    "output": "ollama version is 0.32.14\n"
  },
  "local_manifests": [
    {
      "path": "D:\\DeepTutor\\ollama-models\\manifests\\registry.ollama.ai\\library\\bge-m3\\latest",
      "manifest": {
        "schemaVersion": 2,
        "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
        "config": {
          "mediaType": "application/vnd.docker.container.image.v1+json",
          "digest": "sha256:0c4c9c2a325fb1cdafec606e6809cb745f1cb26a6d919994400d27372303e276",
          "size": 337
        },
        "layers": [
          {
            "mediaType": "application/vnd.ollama.image.model",
            "digest": "sha256:daec91ffb5dd0c27411bd71f29932917c49cf529a641d0168496c3a501e3062c",
            "size": 1157671200
          },
          {
            "mediaType": "application/vnd.ollama.image.license",
            "digest": "sha256:a406579cd136771c705c521db86ca7d60a6f3de7c9b5460e6193a2df27861bde",
            "size": 1068
          }
        ]
      }
    }
  ],
  "status": "MODEL_ENVIRONMENT_BLOCKED"
}
```
Full requests, /api/show version/digest/capabilities, error response and embedding hash: experiment/b5/model_environment.json.
MODEL_ENVIRONMENT_BLOCKED means no discovered usable chat model. Ollama installation itself is verified, not missing.
