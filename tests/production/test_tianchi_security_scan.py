import base64
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = ROOT / "submission" / "a_test_message_bundle_v4_3_candidate_v3.json"
HOST_LIKE = re.compile(r"['\"]([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})['\"]")
ALLOWED_LOCAL = ("127.0.0.1", "localhost")


def _sources():
    bundle = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    for entry in bundle["entry"]:
        resource = entry["resource"]
        if resource.get("resourceType") == "Library":
            yield base64.b64decode(resource["content"][0]["data"], validate=True).decode("utf-8")


def test_all_decoded_libraries_pass_tianchi_security_preflight():
    sources = tuple(_sources())
    assert len(sources) == 16
    for source in sources:
        compile(source, "decoded-library", "exec")
        assert "VERIFIED_MODULE_SOURCES" not in source
        assert "VERIFIED_PACKAGES" not in source
        assert "_VerifiedCoreLoader" not in source
        assert "input(" not in source
        hits = HOST_LIKE.findall(source)
        assert not [hit for hit in hits if hit.startswith("v43.")]
        assert not [hit for hit in hits if hit not in ALLOWED_LOCAL]


def test_local_semantic_endpoint_remains_embedded_and_whitelisted():
    for source in _sources():
        assert "http://127.0.0.1:1213/v1/chat/completions" in source
        assert re.search(r"['\"]model['\"]\s*:\s*['\"]local-model['\"]", source)
