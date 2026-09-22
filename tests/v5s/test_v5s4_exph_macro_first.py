import base64
import hashlib
import io
import json
from contextlib import redirect_stdout
from pathlib import Path

from scripts.build_v5s2_expe_aggressive_submission import build_source as build_e
from scripts.build_v5s4_exph_macro_first_submission import build_source as build_h
from src.v43.fhir.contracts import contract_for_criterion
from src.v43.fhir.service_replay import replay_service

ROOT = Path(__file__).resolve().parents[2]
E = ROOT / "submission/a_test_message_bundle_v5s2_expe_aggressive_candidate.json"
H = ROOT / "submission/a_test_message_bundle_v5s4_exph_macro_first_candidate.json"


def _run(source, text):
    namespace = {}
    exec(compile(source, "485", "exec"), namespace)
    generator = namespace["FHIRResourceBundleGenerator"]("http://localhost:3456")
    output = io.StringIO()
    with redirect_stdout(output):
        bundle = generator.parse_clinical_text_to_fhir_bundle("p1", [{"text": text}])
    metrics = next(line for line in output.getvalue().splitlines() if "V5S4H_METRICS|" in line or "V5S2E_METRICS|" in line)
    return dict(field.split("=", 1) for field in metrics.split("|")[1:]), bundle


def test_485_high_stage_is_local_and_scorer_visible():
    for text in ("POP-Q III", "POP-Q Ⅲ", "盆腔器官脱垂III度", "子宫脱垂III度"):
        metrics, bundle = _run(build_h("485", "485", {}), text)
        resources = tuple(entry["resource"] for entry in bundle["entry"])
        assert metrics["final_decision"] == "MATCH"
        assert metrics["rescue_reason"] == "EXPLICIT_STAGE"
        assert len(resources) == 1
        assert replay_service(resources, contract_for_criterion("485").service, "fixture://fhir", {"p1": "case-1"}).status == "SERVICE_HIT"


def test_485_unbound_or_low_stage_is_blocked():
    for text in ("POP-Q II", "乳腺癌III期，另有子宫脱垂", "CKD IV期，子宫脱垂", "子宫脱垂", "III期"):
        metrics, bundle = _run(build_h("485", "485", {}), text)
        assert metrics["final_decision"] == "NO_MATCH"
        assert not bundle["entry"]


def test_frozen_criteria_are_byte_for_byte_equal_to_experiment_e():
    e_bundle = json.loads(E.read_text(encoding="utf-8"))
    h_bundle = json.loads(H.read_text(encoding="utf-8"))
    e_sources = {str(x["resource"]["content"][0]["title"]): base64.b64decode(x["resource"]["content"][0]["data"]).decode() for x in e_bundle["entry"] if x["resource"].get("resourceType") == "Library"}
    h_sources = {str(x["resource"]["content"][0]["title"]): base64.b64decode(x["resource"]["content"][0]["data"]).decode() for x in h_bundle["entry"] if x["resource"].get("resourceType") == "Library"}
    for cid in e_sources:
        if cid != "485":
            assert h_sources[cid] == e_sources[cid]


def test_experiment_e_artifact_hash_is_unchanged():
    assert hashlib.sha256(E.read_bytes()).hexdigest() == "831385ec9deab93d19e54c8319027978eee4b6843c32ddbc5714795b50ad27e8"
