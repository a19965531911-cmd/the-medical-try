import importlib
import importlib.util
import io
import json
from contextlib import redirect_stdout

import pytest

from scripts.audit_v5s1_expc import NEGATIVE_CASES, POSITIVE_CASES, replay_scorer
from scripts.build_v5s2_expe_aggressive_submission import build_source as build_expe_source


STAMP = "2020-01-01T00:00:00Z"
DECISION_FIELDS = (
    "anchor_hits",
    "groups_hit",
    "groups_required",
    "fallback_used",
    "model_decision",
    "hard_contradiction",
    "admission_mode",
    "final_decision",
    "reason",
)


def _builder():
    return importlib.import_module(
        "scripts.build_v5s2_expf_resource_recovery_submission"
    )


def _metrics(output, prefix):
    line = next(line for line in output.splitlines() if line.startswith(prefix))
    return dict(field.split("=", 1) for field in line.split("|")[1:])


def _run(source, cid, text, timestamp=STAMP, answer="YES"):
    namespace = {}
    exec(compile(source, cid, "exec"), namespace)
    generator = namespace["FHIRResourceBundleGenerator"]("http://localhost:3456")
    calls = []
    generator.transport = lambda prompt: (calls.append(prompt) or answer)
    report = {"text": text}
    if timestamp is not None:
        report["timestamp"] = timestamp
    output = io.StringIO()
    with redirect_stdout(output):
        bundle = generator.parse_clinical_text_to_fhir_bundle("p1", [report])
    return bundle, calls, output.getvalue(), namespace


def _resources(bundle):
    return [entry["resource"] for entry in bundle["entry"]]


def _evidence(namespace, text, timestamp=STAMP):
    report = {"text": text}
    if timestamp is not None:
        report["timestamp"] = timestamp
    reports = namespace["normalize_reports"]([report])
    windows = namespace["retrieve_evidence"](reports, namespace["SPEC"])
    return json.dumps(list(windows), ensure_ascii=False, sort_keys=True)


def test_expf_builder_module_exists():
    assert importlib.util.find_spec(
        "scripts.build_v5s2_expf_resource_recovery_submission"
    ) is not None


def test_expf_audit_module_exists():
    assert importlib.util.find_spec("scripts.audit_v5s2_expf") is not None


def test_expf_candidate_audit_hard_gates(tmp_path):
    audit = importlib.import_module("scripts.audit_v5s2_expf")
    result = audit.audit_experiment(output_dir=tmp_path, build_candidate=True)
    assert result["hard_gates"] == {
        "decode": 16,
        "compile": 16,
        "exec": 16,
        "embedded_positive": 16,
        "embedded_negative": 16,
        "fhir": 16,
        "service": 16,
        "security": 16,
    }
    assert result["decision_deltas"] == 0
    assert result["retrieval_deltas"] == 0
    assert result["prompt_deltas"] == 0
    assert result["llm_call_deltas"] == 0
    assert result["existing_resource_deltas"] == 0
    assert result["recovery"] == {
        "265": {"recovered": 0, "total": 1, "status": "BLOCKED_NO_SAFE_PAYLOAD"},
        "555": {"recovered": 0, "total": 2, "status": "BLOCKED_NO_SAFE_PAYLOAD"},
        "755": {"recovered": 2, "total": 2, "status": "GROUNDED_METADATA_REUSE"},
    }
    assert result["counts"] == {
        "dataclasses": 0,
        "enums": 0,
        "flatten_rename": 0,
        "unresolved_symbols": 0,
    }
    assert (tmp_path / "V5S2F_AUDIT.json").is_file()
    assert (tmp_path / "V5S2_EXPERIMENT_F_DECISION_PARITY.md").is_file()
    assert (tmp_path / "V5S2_EXPERIMENT_F_READINESS.md").is_file()


@pytest.mark.parametrize(
    ("text", "hours"),
    [
        ("MV持续24h", 24),
        ("气管插管持续30 h", 30),
        ("MV持续48h", 48),
        ("气管插管持续1天", 24),
        ("MV持续2天", 48),
    ],
)
def test_755_reuses_rule_grounded_duration_and_hits_scorer(text, hours):
    builder = _builder()
    old_bundle, _, old_output, _ = _run(build_expe_source("755", "755", {}), "755", text)
    new_bundle, _, new_output, _ = _run(builder.build_source("755", "755", {}), "755", text)
    assert _metrics(old_output, "V5S2E_METRICS|")["final_decision"] == "MATCH"
    assert _resources(old_bundle) == []
    assert _metrics(new_output, "V5S2E_METRICS|")["final_decision"] == "MATCH"
    assert len(_resources(new_bundle)) == 1
    assert replay_scorer("755", _resources(new_bundle))
    period = _resources(new_bundle)[0]["performedPeriod"]
    assert period["start"] != period["end"]
    assert _metrics(new_output, "V5S2F_METRICS|") == {
        "criterion": "755",
        "final_decision": "MATCH",
        "resource_compile": "RECOVERED",
        "resources": "1",
        "recovery_mode": "GROUNDED_METADATA_REUSE",
    }
    assert hours >= 24


@pytest.mark.parametrize("text", ["MV持续23h", "气管插管持续12小时", "MV持续6h"])
def test_755_explicit_short_duration_remains_negative(text):
    builder = _builder()
    bundle, calls, output, _ = _run(builder.build_source("755", "755", {}), "755", text)
    assert _metrics(output, "V5S2E_METRICS|")["final_decision"] == "NO_MATCH"
    assert _resources(bundle) == []
    assert calls == []


def test_755_missing_timestamp_is_blocked_without_fabrication():
    builder = _builder()
    bundle, _, output, _ = _run(
        builder.build_source("755", "755", {}), "755", "MV持续30h", timestamp=None
    )
    assert _metrics(output, "V5S2E_METRICS|")["final_decision"] == "MATCH"
    assert _resources(bundle) == []
    assert "1970-01-01" not in json.dumps(bundle)
    assert _metrics(output, "V5S2F_METRICS|")["recovery_mode"] == "BLOCKED_NO_SAFE_PAYLOAD"


def test_555_grounded_relative_date_is_preserved_and_qualitative_match_is_blocked():
    builder = _builder()
    for text, emitted, recovery_mode in (
        ("3个月前完成胆囊切除手术", True, "NONE"),
        ("已完成胆囊切除手术", False, "BLOCKED_NO_SAFE_PAYLOAD"),
    ):
        old_bundle, _, old_output, _ = _run(build_expe_source("555", "555", {}), "555", text)
        new_bundle, _, new_output, _ = _run(builder.build_source("555", "555", {}), "555", text)
        assert _metrics(old_output, "V5S2E_METRICS|")["final_decision"] == "MATCH"
        assert _metrics(new_output, "V5S2E_METRICS|")["final_decision"] == "MATCH"
        assert _resources(new_bundle) == _resources(old_bundle)
        assert bool(_resources(new_bundle)) is emitted
        assert replay_scorer("555", _resources(new_bundle)) is emitted
        assert _metrics(new_output, "V5S2F_METRICS|")["recovery_mode"] == recovery_mode


@pytest.mark.parametrize("text", ["cTnI 0.08 ug/L", "cTnT 0.04 ug/L"])
def test_265_grounded_numeric_measurement_is_preserved_and_hits_scorer(text):
    builder = _builder()
    old_bundle, _, _, _ = _run(build_expe_source("265", "265", {}), "265", text)
    new_bundle, _, output, _ = _run(builder.build_source("265", "265", {}), "265", text)
    assert _resources(new_bundle) == _resources(old_bundle)
    assert replay_scorer("265", _resources(new_bundle))
    assert _metrics(output, "V5S2F_METRICS|")["recovery_mode"] == "NONE"


def test_265_qualitative_match_is_blocked_without_inventing_measurement():
    builder = _builder()
    bundle, _, output, _ = _run(
        builder.build_source("265", "265", {}), "265", "肌钙蛋白升高"
    )
    assert _metrics(output, "V5S2E_METRICS|")["final_decision"] == "MATCH"
    assert _resources(bundle) == []
    assert _metrics(output, "V5S2F_METRICS|")["recovery_mode"] == "BLOCKED_NO_SAFE_PAYLOAD"


@pytest.mark.parametrize(
    ("cid", "text", "answer"),
    [
        *[(cid, text, "YES") for cid, text in POSITIVE_CASES.items()],
        *[(cid, text, "NO") for cid, text in NEGATIVE_CASES.items()],
        ("265", "肌钙蛋白升高", "YES"),
        ("555", "已完成手术", "YES"),
        ("755", "机械通气", "YES"),
        ("755", "MV持续30h", "YES"),
    ],
)
def test_experiment_e_decisions_retrieval_prompts_and_existing_resources_are_frozen(
    cid, text, answer
):
    builder = _builder()
    old_bundle, old_calls, old_output, old_namespace = _run(
        build_expe_source(cid, cid, {}), cid, text, answer=answer
    )
    new_bundle, new_calls, new_output, new_namespace = _run(
        builder.build_source(cid, cid, {}), cid, text, answer=answer
    )
    old_metrics = _metrics(old_output, "V5S2E_METRICS|")
    new_metrics = _metrics(new_output, "V5S2E_METRICS|")
    assert {field: old_metrics[field] for field in DECISION_FIELDS} == {
        field: new_metrics[field] for field in DECISION_FIELDS
    }
    assert old_calls == new_calls
    assert _evidence(old_namespace, text) == _evidence(new_namespace, text)
    if _resources(old_bundle):
        assert _resources(new_bundle) == _resources(old_bundle)
    elif cid == "755" and text == "MV持续30h":
        assert len(_resources(new_bundle)) == 1
    else:
        assert _resources(new_bundle) == []
