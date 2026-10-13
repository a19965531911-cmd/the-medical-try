"""Probe installed local services without downloads, proxies or external calls."""
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from urllib.request import Request, build_opener, ProxyHandler
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "experiment/b5"


def request(url, payload=None, timeout=20):
    started = time.perf_counter()
    result = {"url": url, "method": "POST" if payload is not None else "GET", "request": payload}
    try:
        req = Request(url, data=json.dumps(payload).encode() if payload is not None else None,
                      headers={"Content-Type": "application/json"})
        with build_opener(ProxyHandler({})).open(req, timeout=timeout) as response:
            result.update(http_status=response.status, response=json.loads(response.read().decode()))
    except HTTPError as exc:
        result.update(http_status=exc.code, error_body=exc.read().decode(), error=type(exc).__name__)
    except Exception as exc:
        result["error"] = type(exc).__name__ + ": " + str(exc)
    result["seconds"] = time.perf_counter() - started
    return result


def main():
    paths = [Path(p) for p in ("D:/DeepTutor/ollama/ollama.exe", "D:/DeepTutor/ollama-models",
                               "C:/Users/32433/.ollama/models", "C:/Users/32433/.lmstudio/models",
                               "C:/Users/32433/.cache/huggingface/hub", "D:/models")]
    result = dict(os=platform.platform(), python=sys.executable, python_version=sys.version,
                  wsl=os.environ.get("WSL_DISTRO_NAME"), model_found=False, usable_chat_model=False,
                  installation_paths=[dict(path=str(p), exists=p.exists()) for p in paths],
                  local_env={k:os.environ.get(k) for k in ("OLLAMA_MODELS", "OLLAMA_HOST", "HF_HOME")},
                  downloads=False, external_calls=False, patient_data_sent=False)
    exe = paths[0]
    if exe.exists():
        completed = subprocess.run([str(exe), "--version"], capture_output=True, text=True, timeout=10)
        result["ollama_version"] = dict(exit_code=completed.returncode, output=completed.stdout + completed.stderr)
    model_root = paths[1]
    result["local_manifests"] = [{"path": str(p), "manifest": json.loads(p.read_text())}
                                  for p in (model_root / "manifests").rglob("*") if p.is_file()]
    result["probes"] = [request("http://127.0.0.1:1213/v1/models", timeout=3),
                         request("http://127.0.0.1:11434/api/version"),
                         request("http://127.0.0.1:11434/api/tags")]
    tags = result["probes"][-1].get("response", {}).get("models", [])
    result["model_found"] = bool(tags)
    for model in tags:
        name = model["name"]
        show = request("http://127.0.0.1:11434/api/show", {"model": name})
        result["probes"].append(show)
        capabilities = show.get("response", {}).get("capabilities", [])
        if "completion" in capabilities and not name.endswith(":cloud"):
            result["usable_chat_model"] = True
            result["chat_model"] = name
    if any(m["name"] == "bge-m3:latest" for m in tags):
        result["probes"].append(request("http://127.0.0.1:11434/v1/chat/completions",
            {"model": "bge-m3:latest", "messages": [{"role": "user", "content": "仅输出JSON: {\"match\":false,\"facts\":[]}"}], "max_tokens": 32}))
        embedding = request("http://127.0.0.1:11434/api/embed", {"model": "bge-m3:latest", "input": ["患者活动后气短"]}, timeout=60)
        vectors = embedding.get("response", {}).pop("embeddings", None)
        if vectors is not None:
            embedding["actual_embedding"] = dict(count=len(vectors), dimensions=[len(v) for v in vectors],
                response_vectors_sha256=hashlib.sha256(json.dumps(vectors).encode()).hexdigest())
        result["probes"].append(embedding)
    result["status"] = "CHAT_MODEL_AVAILABLE" if result["usable_chat_model"] else "MODEL_ENVIRONMENT_BLOCKED"
    DEST.mkdir(parents=True, exist_ok=True)
    (DEST / "model_environment.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf8")
    print(json.dumps({k:result[k] for k in ("status", "model_found", "usable_chat_model", "ollama_version")}, ensure_ascii=True))
    print(json.dumps([{k:p.get(k) for k in ("url", "http_status", "error", "error_body", "seconds", "actual_embedding")} for p in result["probes"]], ensure_ascii=True))


if __name__ == "__main__":
    main()
