import ast
import base64
import hashlib
import importlib
import importlib.util
import io
import json
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from scripts.audit_v5s1_expc import (
    REPORT_NAMES,
    SCORER_CASES,
    audit_experiment,
    replay_scorer,
)


ROOT = Path(__file__).resolve().parents[2]
TARGETS = {"265", "555", "755", "805", "855"}
NON_TARGETS = {"165", "185", "485", "565", "615", "635", "675", "735", "745", "835", "875"}
CORE_FUNCTIONS = {
    "normalize_reports",
    "retrieve_evidence",
    "rule_decide",
    "llm_decide",
    "parse_decision",
    "extract_payload",
}


def test_expc_builder_module_exists():
    assert importlib.util.find_spec("scripts.build_v5s1_expc_submission") is not None


def test_expc_builder_runs_as_a_script():
    result = subprocess.run(
        [sys.executable, "scripts/build_v5s1_expc_submission.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert (
        ROOT / "submission/a_test_message_bundle_v5s1_expc_candidate.json"
    ).is_file()


def test_expc_audit_runs_as_a_script():
    result = subprocess.run(
        [sys.executable, "scripts/audit_v5s1_expc.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    summary = json.loads(result.stdout)
    assert summary == {
        "decision_deltas": 0,
        "non_target_source_deltas": 0,
        "target_prefix_deltas": 0,
    }


def _builder():
    return importlib.import_module("scripts.build_v5s1_expc_submission")


def _candidate_sources(path):
    bundle = json.loads(path.read_text(encoding="utf-8"))
    return {
        str(entry["resource"]["content"][0]["title"]): base64.b64decode(
            entry["resource"]["content"][0]["data"]
        ).decode("utf-8")
        for entry in bundle["entry"]
        if entry["resource"].get("resourceType") == "Library"
    }


def _namespace(source, cid):
    namespace = {}
    exec(compile(source, cid, "exec"), namespace)
    return namespace


def _run(source, cid, text, timestamp=None, answer="YES"):
    namespace = _namespace(source, cid)
    generator = namespace["FHIRResourceBundleGenerator"]("http://localhost:3456")
    calls = []
    generator.transport = lambda prompt: (calls.append(prompt) or answer)
    report = {"text": text}
    if timestamp is not None:
        report["timestamp"] = timestamp
    output = io.StringIO()
    with redirect_stdout(output):
        bundle = generator.parse_clinical_text_to_fhir_bundle("p1", [report])
    return bundle, calls, output.getvalue()


def _resources(bundle):
    return [entry["resource"] for entry in bundle["entry"]]


def test_frozen_candidate_hashes_and_sizes_are_unchanged():
    paths = (
        (
            ROOT / "submission/a_test_message_bundle_v5s1_candidate.json",
            360724,
            "4ea0165cdae6a5c665bc1afafd920e32430b5867998c642eccc832f54eb829b9",
        ),
        (
            ROOT.parent / "CHIP2026_CP2_A_baseline_v2_4_3/submission/a_test_message_bundle_v2_4_3.json",
            149376,
            "dbda76bf126c55f0176c2067f033a16d68838eb800df0d7f745cb25d4704e173",
        ),
    )
    for path, size, digest in paths:
        payload = path.read_bytes()
        assert len(payload) == size
        assert hashlib.sha256(payload).hexdigest() == digest


def test_exact_legacy_datetime_algorithms():
    builder = _builder()
    value = "2026-01-31T12:34:56+08:00"
    assert builder.canonical_datetime(value) == "2026-01-31T04:34:56Z"
    assert builder.months_before(value, 3) == "2025-10-31T04:34:56Z"
    assert builder.hours_before(value, 30) == "2026-01-29T22:34:56Z"


def test_non_target_sources_are_byte_for_byte_frozen_and_core_functions_are_not_redefined():
    frozen = _candidate_sources(ROOT / "submission/a_test_message_bundle_v5s1_candidate.json")
    builder = _builder()
    for cid in NON_TARGETS:
        assert builder.build_source(cid, "test", {}) == frozen[cid]
    for cid in TARGETS:
        source = builder.build_source(cid, "test", {})
        definitions = [
            node.name
            for node in ast.parse(source).body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        assert all(definitions.count(name) == 1 for name in CORE_FUNCTIONS)
        assert source.index("MISSING_GROUNDED_PAYLOAD") < source.index("derive_transport_meta")


def test_target_transport_shapes_match_legacy_contracts():
    builder = _builder()
    stamp = "2026-01-31T12:34:56+08:00"
    cases = {
        "265": ("cTnI 0.08 ug/L", 1),
        "555": ("3\u4e2a\u6708\u524d\u5b8c\u6210\u80c6\u56ca\u5207\u9664\u672f", 1),
        "755": ("\u673a\u68b0\u901a\u6c14\u6301\u7eed30\u5c0f\u65f6", 1),
        "805": ("\u6212\u70df1\u5e74", 2),
        "855": ("Scr 120 umol/L, BUN 7 mmol/L, ALT 30 U/L\u4e0a\u965040, AST 25 U/L\u4e0a\u965040", 4),
    }
    outputs = {}
    for cid, (text, count) in cases.items():
        bundle, _, metrics = _run(builder.build_source(cid, "test", {}), cid, text, stamp)
        outputs[cid] = _resources(bundle)
        assert len(outputs[cid]) == count, (cid, metrics, outputs[cid])
        assert all(entry["request"] == {"method": "POST", "url": entry["resource"]["resourceType"]} for entry in bundle["entry"])

    troponin = outputs["265"][0]
    assert troponin["meta"]["profile"][-1].endswith("cnwqk265-preoperative-cardiac-troponin-observation")
    assert [coding["code"] for coding in troponin["code"]["coding"]] == ["cTnI", "10839-9"]
    assert troponin["extension"][0]["valueBoolean"] is True
    assert troponin["valueQuantity"]["system"] == "http://unitsofmeasure.org"
    assert troponin["effectiveDateTime"] == "2026-01-31T04:34:56Z"

    surgery = outputs["555"][0]
    assert surgery["code"]["coding"][0]["code"] == "surgery"
    assert surgery["performedDateTime"] == "2025-10-31T04:34:56Z"

    ventilation = outputs["755"][0]
    assert ventilation["performedPeriod"] == {
        "start": "2026-01-29T22:34:56Z",
        "end": "2026-01-31T04:34:56Z",
    }
    assert "duration_hours" not in ventilation["performedPeriod"]

    smoking, cessation = outputs["805"]
    assert smoking["code"]["coding"][0]["code"] == "72166-2"
    assert cessation["code"]["coding"][0]["code"] == "63586-4"
    assert cessation["valueQuantity"] == {
        "value": 1.0,
        "unit": "\u5e74",
        "system": "http://unitsofmeasure.org",
        "code": "a",
    }

    labs = outputs["855"]
    assert [resource["code"]["coding"][0]["code"] for resource in labs] == ["2160-0", "3094-0", "1742-6", "1920-8"]
    assert [resource["valueQuantity"]["value"] for resource in labs] == [120.0, 7.0, 30.0, 25.0]


def test_current_smoker_is_one_resource_and_missing_timestamps_are_not_fabricated():
    builder = _builder()
    current, _, _ = _run(builder.build_source("805", "test", {}), "805", "\u76ee\u524d\u6bcf\u65e5\u5438\u70df")
    assert len(current["entry"]) == 1
    assert "effectiveDateTime" not in current["entry"][0]["resource"]
    for cid, text in (("555", "3\u4e2a\u6708\u524d\u5b8c\u6210\u80c6\u56ca\u5207\u9664\u672f"), ("755", "\u673a\u68b0\u901a\u6c14\u6301\u7eed30\u5c0f\u65f6")):
        bundle, _, _ = _run(builder.build_source(cid, "test", {}), cid, text)
        assert bundle["entry"] == []
        assert "1970-01-01" not in json.dumps(bundle)


def test_decision_reason_route_evidence_and_llm_calls_match_frozen_v5s1():
    frozen = _candidate_sources(ROOT / "submission/a_test_message_bundle_v5s1_candidate.json")
    builder = _builder()
    cases = {
        "265": "cTnT 0.04 ug/L",
        "555": "3\u4e2a\u6708\u524d\u5b8c\u6210\u80c6\u56ca\u5207\u9664\u672f",
        "755": "\u673a\u68b0\u901a\u6c14\u6301\u7eed30\u5c0f\u65f6",
        "805": "\u6212\u70df1\u5e74",
        "855": "Scr 120 umol/L, BUN 7 mmol/L, ALT 30 U/L\u4e0a\u965040, AST 25 U/L\u4e0a\u965040",
    }
    keys = ("route", "evidence_windows", "groups_hit", "llm_called", "decision", "reason", "prompt_length")
    for cid, text in cases.items():
        old_bundle, old_calls, old_metrics = _run(frozen[cid], cid, text, "2026-01-31T12:34:56+08:00")
        new_bundle, new_calls, new_metrics = _run(builder.build_source(cid, "test", {}), cid, text, "2026-01-31T12:34:56+08:00")
        old_fields = dict(field.split("=", 1) for field in old_metrics.strip().split("|")[1:])
        new_fields = dict(field.split("=", 1) for field in new_metrics.strip().split("|")[1:])
        assert {key: old_fields[key] for key in keys} == {key: new_fields[key] for key in keys}
        assert old_calls == new_calls
        assert bool(old_bundle["entry"]) == bool(new_bundle["entry"])


def test_negative_cases_never_gain_resources():
    builder = _builder()
    negatives = {
        "265": "cTnI 0.03 ug/L",
        "555": "8\u4e2a\u6708\u524d\u5b8c\u6210\u80c6\u56ca\u5207\u9664\u672f",
        "755": "\u673a\u68b0\u901a\u6c14\u6301\u7eed12\u5c0f\u65f6",
        "805": "\u4ece\u4e0d\u5438\u70df",
        "855": "Scr 190 umol/L, BUN 7 mmol/L, ALT 30 U/L\u4e0a\u965040, AST 25 U/L\u4e0a\u965040",
    }
    for cid, text in negatives.items():
        bundle, _, metrics = _run(builder.build_source(cid, "test", {}), cid, text, "2026-01-31T12:34:56+08:00", "NO")
        assert bundle["entry"] == [], (cid, metrics)


@pytest.mark.parametrize("case", SCORER_CASES, ids=lambda case: case["branch"])
def test_exact_preserved_scorer_replay_matrix(case):
    result = audit_experiment(cases=[case])["scorer_rows"][0]
    assert replay_scorer(case["criterion"], result["EXPC_resources"]) == (
        case["expected_hits"][1] == "HIT"
    )
    assert (
        result["V5S1_SERVICE_HIT"],
        result["EXPC_SERVICE_HIT"],
        result["V243_SERVICE_HIT"],
    ) == case["expected_hits"]


def test_expc_audit_writes_contract_parity_and_scorer_reports(tmp_path):
    result = audit_experiment(output_dir=tmp_path)
    assert result["decision_deltas"] == 0
    assert result["non_target_source_deltas"] == 0
    assert result["target_prefix_deltas"] == 0
    assert {path.name for path in tmp_path.iterdir()} == set(REPORT_NAMES)
    assert len(result["contract_rows"]) == 5
    assert {row["decision_impact"] for row in result["contract_rows"]} == {"NONE"}
    assert len(result["scorer_rows"]) == len(SCORER_CASES)
    assert any(
        row["criterion"] == "855"
        and row["branch"] == "855_alt_45_uln_50"
        and row["decision"] == "MATCH"
        and row["EXPC_SERVICE_HIT"] == "MISS"
        for row in result["scorer_rows"]
    )
