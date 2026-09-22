import base64
import hashlib
import io
import json
from contextlib import redirect_stdout
from pathlib import Path

from scripts.build_v5s4_exph_macro_first_submission import build_source as build_h
from scripts.build_v5s4_exph1_anchorfix_submission import build_source as build_h1
from src.v43.fhir.contracts import contract_for_criterion
from src.v43.fhir.service_replay import replay_service

ROOT = Path(__file__).resolve().parents[2]
H = ROOT / "submission/a_test_message_bundle_v5s4_exph_macro_first_candidate.json"
H1 = ROOT / "submission/a_test_message_bundle_v5s4_exph1_anchorfix_candidate.json"


def _run(source, text):
    namespace = {}
    exec(compile(source, "485", "exec"), namespace)
    reports = namespace["normalize_reports"]([{"text": text}])
    windows = namespace["retrieve_evidence"](reports, namespace["SPEC"])
    generator = namespace["FHIRResourceBundleGenerator"]("http://localhost:3456")
    output = io.StringIO()
    with redirect_stdout(output):
        bundle = generator.parse_clinical_text_to_fhir_bundle("p1", [{"text": text}])
    line = next(line for line in output.getvalue().splitlines() if "METRICS|" in line)
    metrics = dict(field.split("=", 1) for field in line.split("|")[1:])
    resources = tuple(entry["resource"] for entry in bundle["entry"])
    service = replay_service(resources, contract_for_criterion("485").service, "fixture://fhir", {"p1": "case-1"}).status
    return windows.metrics, metrics, resources, service


def test_h1_aligns_real_uterine_prolapse_anchor():
    windows, metrics, resources, service = _run(build_h1("485", "485", {}), "患者诊断为子宫脱垂III度。")
    assert windows.metrics["true_anchor_hits"] >= 1
    assert metrics["final_decision"] == "MATCH"
    assert len(resources) == 1
    assert service == "SERVICE_HIT"


def test_h1_positive_regression_set_is_visible():
    for text in ("子宫脱垂III度", "盆腔器官脱垂III度", "POP-Q III", "POP-Q Ⅲ"):
        windows, metrics, resources, service = _run(build_h1("485", "485", {}), text)
        assert windows.metrics["true_anchor_hits"] >= 1
        assert metrics["final_decision"] == "MATCH"
        assert len(resources) == 1
        assert service == "SERVICE_HIT"


def test_h1_negative_binding_set_stays_blocked():
    for text in ("POP-Q I", "POP-Q II", "子宫脱垂II度", "盆腔器官脱垂II度", "乳腺癌III期，伴子宫脱垂", "CKD IV期，另有子宫脱垂", "子宫脱垂", "III期", "明确否认子宫脱垂"):
        _windows, metrics, resources, service = _run(build_h1("485", "485", {}), text)
        assert metrics["final_decision"] == "NO_MATCH"
        assert not resources
        assert service == "SERVICE_MISS"


def test_h1_preserves_h_decision_resource_and_service_on_existing_cases():
    cases = ("POP-Q III", "POP-Q Ⅲ", "盆腔器官脱垂III度", "子宫脱垂III度", "POP-Q I", "POP-Q II", "POP-Q IV", "子宫脱垂")
    for text in cases:
        h_windows, h_metrics, h_resources, h_service = _run(build_h("485", "485", {}), text)
        h1_windows, h1_metrics, h1_resources, h1_service = _run(build_h1("485", "485", {}), text)
        assert h1_metrics["final_decision"] == h_metrics.get("final_decision", h_metrics.get("decision"))
        assert len(h1_resources) == len(h_resources)
        assert h1_service == h_service
        assert h1_windows.metrics["true_anchor_hits"] >= h_windows.metrics.get("anchor_hits", 0) if h1_windows.metrics.get("true_anchor_hits") is not None else True


def test_h1_preserves_frozen_h_and_e_sources_for_non_485():
    h_bundle = json.loads(H.read_text(encoding="utf-8"))
    h1_bundle = json.loads(H1.read_text(encoding="utf-8"))
    hs = {str(x["resource"]["content"][0]["title"]): base64.b64decode(x["resource"]["content"][0]["data"]).decode() for x in h_bundle["entry"] if x["resource"].get("resourceType") == "Library"}
    h1s = {str(x["resource"]["content"][0]["title"]): base64.b64decode(x["resource"]["content"][0]["data"]).decode() for x in h1_bundle["entry"] if x["resource"].get("resourceType") == "Library"}
    for cid in hs:
        if cid != "485":
            assert h1s[cid] == hs[cid]


def test_frozen_h_and_e_hashes_unchanged():
    assert hashlib.sha256(H.read_bytes()).hexdigest() == "05ea1171d41fe84f0330f20e28b2deacc76f59b819363e211880eca0ee7cad5d"
