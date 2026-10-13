"""Native loopback probe of the actual B4H artifact; synthetic text only."""
import json
import sys
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
from scripts.b4_experiments import DEST, dump, namespaces, parse_submission, replay, load_rows, semantic_cases


def main():
    bundle = parse_submission((DEST / "B4H.json").read_text(encoding="utf8"))
    ns = namespaces(bundle)
    rows = {str(r["profile_id"]): r for r in load_rows()}
    result = dict(execution_context="NATIVE_WINDOWS_LOOPBACK", status="LIVE_MODEL_UNAVAILABLE",
                  synthetic_only=True, endpoint="http://127.0.0.1:1213/v1/chat/completions")
    try:
        with urlopen("http://127.0.0.1:1213/v1/models", timeout=3) as response:
            result["models"] = json.loads(response.read().decode())
    except Exception as exc:
        result["models_error"] = type(exc).__name__ + ": " + str(exc)
    fixture = semantic_cases()[0]
    result["embedded_probe"] = replay(fixture, ns[fixture["profile_id"]], rows[fixture["profile_id"]], "live")
    metrics = result["embedded_probe"]["model_metrics"]
    if metrics["http_success"]:
        result["status"] = "LIVE_MODEL_RESPONDED" if metrics["json_valid"] else "LIVE_MODEL_RESPONSE_INVALID"
    dump(DEST / "native_endpoint.json", result)
    print(json.dumps({k: v for k, v in result.items() if k != "embedded_probe"}, ensure_ascii=True))
    print(json.dumps(metrics, ensure_ascii=True))


if __name__ == "__main__":
    main()
