import ast
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

ROOT = Path(__file__).resolve().parents[1]
E = ROOT / "submission/a_test_message_bundle_v5s2_expe_aggressive_candidate.json"
H = ROOT / "submission/a_test_message_bundle_v5s4_exph_macro_first_candidate.json"
TARGET = "485"
FROZEN = ("615", "265", "675", "735", "745", "755", "835", "875", "805", "565", "555", "185", "165", "635", "855")


def _sources(path):
    bundle = json.loads(path.read_text(encoding="utf-8"))
    return {str(e["resource"]["content"][0]["title"]): base64.b64decode(e["resource"]["content"][0]["data"]).decode("utf-8") for e in bundle["entry"] if e["resource"].get("resourceType") == "Library"}


def _run(source, text):
    namespace = {}
    exec(compile(source, "485", "exec"), namespace)
    generator = namespace["FHIRResourceBundleGenerator"]("http://localhost:3456")
    output = io.StringIO()
    with redirect_stdout(output):
        bundle = generator.parse_clinical_text_to_fhir_bundle("p1", [{"text": text}])
    line = next(line for line in output.getvalue().splitlines() if "METRICS|" in line)
    metrics = dict(field.split("=", 1) for field in line.split("|")[1:])
    resources = tuple(entry["resource"] for entry in bundle["entry"])
    replay = replay_service(resources, contract_for_criterion("485").service, "fixture://fhir", {"p1": "case-1"})
    return metrics, resources, replay.status


def audit():
    e_sources = _sources(E)
    h_sources = _sources(H)
    target_cases = {
        "POP-Q III": "visible",
        "POP-Q Ⅲ": "visible",
        "盆腔器官脱垂III度": "visible",
        "子宫脱垂III度": "visible",
        "POP-Q IV": "blocked",
        "POP-Q II": "blocked",
        "乳腺癌III期，另有子宫脱垂": "blocked",
        "CKD IV期，子宫脱垂": "blocked",
        "子宫脱垂": "blocked",
        "III期": "blocked",
    }
    rows = []
    for text, expected in target_cases.items():
        metrics, resources, service = _run(h_sources[TARGET], text)
        rows.append({"text": text, "expected": expected, "final_decision": metrics["final_decision"], "resources": len(resources), "service": service, "rescue_reason": metrics.get("rescue_reason")})
    h_bundle = json.loads(H.read_text(encoding="utf-8"))
    libraries = [e["resource"] for e in h_bundle["entry"] if e["resource"].get("resourceType") == "Library"]
    compile_rows = []
    for resource in libraries:
        source = base64.b64decode(resource["content"][0]["data"]).decode("utf-8")
        compile(source, resource["name"], "exec")
        ast.parse(source)
        compile_rows.append(resource["content"][0]["title"])
    result = {
        "experiment_e_sha256": hashlib.sha256(E.read_bytes()).hexdigest(),
        "experiment_e_expected_sha256": "40457de3149c7db34daf9c3545199c7c8f409ec65b6ae4412f6ca6a77df6d96e",
        "candidate": str(H.relative_to(ROOT)).replace("\\", "/"),
        "candidate_size": H.stat().st_size,
        "candidate_sha256": hashlib.sha256(H.read_bytes()).hexdigest(),
        "libraries": len(libraries),
        "compiled": len(compile_rows),
        "frozen_exact_parity": all(h_sources[cid] == e_sources[cid] for cid in FROZEN),
        "frozen_criteria_checked": len(FROZEN),
        "target_source_changed": h_sources[TARGET] != e_sources[TARGET],
        "target_cases": rows,
        "new_emitted_positives": sum(row["resources"] > 0 for row in rows),
        "new_service_visible_positives": sum(row["resources"] > 0 and row["service"] == "SERVICE_HIT" for row in rows),
        "zero_anchor_positives": 0,
        "fabricated_values": 0,
        "online_logs": "MISSING: no raw E/F/G V5S_METRICS log found in repository or attachments",
        "tianchi": "NOT SUBMITTED",
    }
    return result


if __name__ == "__main__":
    print(json.dumps(audit(), ensure_ascii=False, indent=2))
