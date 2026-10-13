import base64
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from scripts import build_v5s2_expe_aggressive_submission as e_builder
from scripts import build_v5s8_expl_675_precision_guard_submission as l_builder
from scripts.v6_baseline_gate import E_COMMIT, E_RELATIVE, _candidate_sources, _git_bytes
from src.v43.fhir.contracts import contract_for_criterion
from src.v43.fhir.service_replay import replay_service

ROOT = Path(__file__).resolve().parents[2]
TARGET = "675"
NON_TARGETS = {"165", "185", "265", "485", "555", "565", "615", "635", "735", "745", "755", "805", "835", "855", "875"}


def _run(source, text):
    namespace = {}
    exec(compile(source, "675", "exec"), namespace)
    generator = namespace["FHIRResourceBundleGenerator"]("http://localhost:3456")
    output = io.StringIO()
    with redirect_stdout(output):
        bundle = generator.parse_clinical_text_to_fhir_bundle("p1", [{"text": text, "timestamp": "2026-01-31T12:34:56+08:00"}])
    lines = output.getvalue().splitlines()
    metric = next((line for line in reversed(lines) if line.startswith("V5S8L_METRICS|")), None)
    if metric is None:
        metric = next(line for line in lines if line.startswith("V5S2E_METRICS|"))
    values = dict(field.split("=", 1) for field in metric.split("|")[1:])
    return values, bundle


def test_missing_site_is_pruned_without_resources():
    e, e_bundle = _run(e_builder.build_source(TARGET, TARGET, {}), "患者56岁，诊断带状疱疹。")
    l, l_bundle = _run(l_builder.build_source(TARGET, TARGET, {}), "患者56岁，诊断带状疱疹。")
    assert e["final_decision"] == "MATCH"
    assert l["final_decision"] == "NO_MATCH"
    assert e["reason"] == "RULE_ZOSTER"
    assert not l_bundle["entry"]


@pytest.mark.parametrize("text", [
    "56岁，诊断头面部带状疱疹。",
    "63岁，面部带状疱疹。",
    "70岁，眼周带状疱疹。",
])
def test_complete_675_positive_is_retained_and_service_visible(text):
    metrics, bundle = _run(l_builder.build_source(TARGET, TARGET, {}), text)
    assert metrics["final_decision"] == "MATCH"
    resources = tuple(entry["resource"] for entry in bundle["entry"])
    assert resources
    assert replay_service(resources, contract_for_criterion(TARGET).service, "fixture://fhir", {"p1": "case"}).status == "SERVICE_HIT"


@pytest.mark.parametrize("text", [
    "49岁，头面部带状疱疹",
    "56岁，带状疱疹",
    "56岁，胸背部带状疱疹",
    "56岁，下肢带状疱疹",
    "头面部带状疱疹",
    "56岁，面部皮疹",
    "56岁，否认带状疱疹",
    "56岁，胸背部带状疱疹，面部无皮疹。",
    "56岁，既往躯干部带状疱疹，本次面部疼痛。",
])
def test_incomplete_or_unrelated_675_facts_emit_nothing(text):
    metrics, bundle = _run(l_builder.build_source(TARGET, TARGET, {}), text)
    assert metrics["final_decision"] == "NO_MATCH"
    assert not bundle["entry"]


def test_l_match_set_is_subset_of_e_on_local_675_cases():
    cases = [
        "56岁，诊断头面部带状疱疹。", "63岁，面部带状疱疹。", "70岁，眼周带状疱疹。",
        "患者56岁，诊断带状疱疹。", "49岁，头面部带状疱疹", "56岁，胸背部带状疱疹",
        "患者65岁", "否认带状疱疹",
    ]
    e_source = e_builder.build_source(TARGET, TARGET, {})
    l_source = l_builder.build_source(TARGET, TARGET, {})
    for text in cases:
        e, _ = _run(e_source, text)
        l, _ = _run(l_source, text)
        assert l["final_decision"] != "MATCH" or e["final_decision"] == "MATCH", text


def test_non_target_sources_are_exact_experiment_e_sources():
    for criterion in NON_TARGETS:
        assert l_builder.build_source(criterion, criterion, {}) == e_builder.build_source(criterion, criterion, {})


def test_frozen_e_source_semantics_are_the_replay_baseline():
    sources = _candidate_sources(_git_bytes(f"{E_COMMIT}:{E_RELATIVE}"))
    assert sources[TARGET] == e_builder.build_source(TARGET, TARGET, {})
