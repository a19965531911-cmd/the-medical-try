import io
import importlib
import json
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from src.v43.fhir.contracts import contract_for_criterion
from src.v43.fhir.service_replay import replay_service


TARGETS = {"485", "635", "855", "675", "735", "745"}
NON_TARGETS = {"615", "265", "755", "805", "555", "565", "835", "875", "185", "165"}
ROOT = Path(__file__).resolve().parents[2]


def _builder():
    return importlib.import_module("scripts.build_v5s3_expg_criterion_recall_submission")


def _run(criterion, text, answer="YES"):
    namespace = {}
    source = _builder().build_source(criterion, criterion, {})
    exec(compile(source, criterion, "exec"), namespace)
    generator = namespace["FHIRResourceBundleGenerator"]("http://localhost:3456")
    prompts = []
    generator.transport = lambda prompt: (prompts.append(prompt) or answer)
    output = io.StringIO()
    with redirect_stdout(output):
        bundle = generator.parse_clinical_text_to_fhir_bundle(
            "p1", [{"text": text, "timestamp": "2026-01-31T12:34:56+08:00"}]
        )
    line = next(line for line in output.getvalue().splitlines() if line.startswith("V5S3G_METRICS|"))
    metrics = dict(field.split("=", 1) for field in line.split("|")[1:])
    return metrics, bundle, prompts, namespace


@pytest.mark.parametrize("text", ["POP-Q III", "POP-Q Ⅳ", "子宫脱垂III度", "盆腔器官脱垂四期"])
def test_485_locally_bound_high_stage_is_a_rule_positive(text):
    metrics, bundle, _, _ = _run("485", text)
    assert metrics["final_decision"] == "MATCH"
    assert metrics["expansion_reason"] in {"ALIAS_RECOVERY", "RULE_DIRECT"}
    assert len(bundle["entry"]) == 1


@pytest.mark.parametrize("text", ["乳腺癌III期，另有子宫脱垂", "POP-Q II期"])
def test_485_unbound_or_low_stage_is_not_admitted(text):
    metrics, bundle, _, _ = _run("485", text)
    assert metrics["final_decision"] == "NO_MATCH"
    assert not bundle["entry"]


@pytest.mark.parametrize("text", ["肝肾功能正常", "ALT正常，AST正常", "BUN正常", "Cr正常"])
def test_635_qualitative_or_partial_labs_allow_semantic_match_without_fabrication(text):
    metrics, bundle, _, _ = _run("635", text)
    assert metrics["final_decision"] == "MATCH"
    assert metrics["expansion_reason"] in {"QUALITATIVE_LAB_NORMAL", "PARTIAL_LAB_SUPPORTED"}
    assert not bundle["entry"]


def test_635_explicit_threshold_violation_blocks_llm_yes():
    metrics, bundle, _, _ = _run("635", "ALT 100 U/L 上限40")
    assert metrics["final_decision"] == "NO_MATCH"
    assert metrics["hard_contradiction"] == "EXPLICIT_THRESHOLD_VIOLATION"
    assert not bundle["entry"]


@pytest.mark.parametrize("text", ["Scr 100 umol/L", "BUN 6 mmol/L", "肝肾功能无明显异常"])
def test_855_partial_or_qualitative_labs_allow_match_without_invented_resources(text):
    metrics, bundle, _, _ = _run("855", text)
    assert metrics["final_decision"] == "MATCH"
    assert metrics["expansion_reason"] in {"QUALITATIVE_LAB_NORMAL", "PARTIAL_LAB_SUPPORTED"}
    assert not bundle["entry"]


@pytest.mark.parametrize("text", ["Scr 200 umol/L", "BUN 12 mmol/L", "ALT 50 U/L 上限40"])
def test_855_any_explicit_violation_blocks_match(text):
    metrics, bundle, _, _ = _run("855", text)
    assert metrics["final_decision"] == "NO_MATCH"
    assert metrics["hard_contradiction"] == "EXPLICIT_THRESHOLD_VIOLATION"
    assert not bundle["entry"]


@pytest.mark.parametrize("text", ["头面部带状疱疹", "65岁患者确诊带状疱疹"])
def test_675_zoster_with_site_or_age_is_positive(text):
    metrics, bundle, _, _ = _run("675", text)
    assert metrics["final_decision"] == "MATCH"
    assert bundle["entry"]


@pytest.mark.parametrize("text", ["患者65岁", "面部疼痛"])
def test_675_age_only_or_face_only_is_negative(text):
    metrics, bundle, _, _ = _run("675", text)
    assert metrics["final_decision"] == "NO_MATCH"
    assert not bundle["entry"]


@pytest.mark.parametrize("text", ["乙肝正在治疗", "结核，抗结核治疗中", "现患HIV，currently treated"])
def test_735_current_or_treated_target_disease_is_positive(text):
    metrics, bundle, _, _ = _run("735", text)
    assert metrics["final_decision"] == "MATCH"
    assert bundle["entry"]


@pytest.mark.parametrize("text", ["既往HBV感染史", "结核已治愈", "inactive hepatitis B"])
def test_735_resolved_or_history_only_is_negative(text):
    metrics, bundle, _, _ = _run("735", text)
    assert metrics["final_decision"] == "NO_MATCH"
    assert not bundle["entry"]


def test_745_adjacent_sentence_postoperative_invasive_ventilation_is_positive():
    metrics, bundle, _, _ = _run("745", "患者接受手术治疗。术后转ICU，继续有创机械通气。")
    assert metrics["final_decision"] == "MATCH"
    assert metrics["expansion_reason"] == "CROSS_SENTENCE_RELATION"
    assert len(bundle["entry"]) == 2


@pytest.mark.parametrize("text", ["术前因呼吸衰竭机械通气，后行手术", "术后仅NIV无创通气", "计划术后机械通气"])
def test_745_preop_niv_or_planned_ventilation_is_negative(text):
    metrics, bundle, _, _ = _run("745", text)
    assert metrics["final_decision"] == "NO_MATCH"
    assert not bundle["entry"]


def test_target_prompts_explain_partial_admission_and_hard_blockers():
    expected = {
        "485": ("脱垂", "III"), "635": ("肝肾功能正常", "四项"),
        "855": ("肝肾功能正常", "无需"), "675": ("带状疱疹", "50"),
        "735": ("正在治疗", "既往史"), "745": ("相邻句子", "无创通气"),
    }
    texts = {"485": "子宫脱垂", "635": "AST正常", "855": "BUN正常", "675": "确诊带状疱疹", "735": "乙肝", "745": "手术治疗，呼吸机支持"}
    for criterion, tokens in expected.items():
        _, _, prompts, _ = _run(criterion, texts[criterion], "NO")
        assert prompts and all(token in prompts[0] for token in tokens)


def test_target_retrieval_is_group_balanced_and_capped_at_16():
    text = "。".join([f"AST正常记录{i}" for i in range(20)] + ["BUN正常", "Cr正常", "ALT正常"])
    metrics, _, _, namespace = _run("635", text)
    reports = namespace["normalize_reports"]([{"text": text}])
    windows = namespace["retrieve_evidence"](reports, namespace["SPEC"])
    assert len(windows) <= 16
    assert windows.metrics["groups_hit"] == 4
    assert metrics["groups_hit"] == "4"


def test_non_target_sources_are_exact_experiment_e_sources():
    expg = _builder()
    expe = importlib.import_module("scripts.build_v5s2_expe_aggressive_submission")
    for criterion in NON_TARGETS:
        assert expg.build_source(criterion, criterion, {}) == expe.build_source(criterion, criterion, {})


def test_zero_anchor_llm_yes_is_always_blocked_for_targets():
    for criterion in TARGETS:
        metrics, bundle, _, _ = _run(criterion, "一般情况稳定")
        assert metrics["anchor_hits"] == "0"
        assert metrics["final_decision"] == "NO_MATCH"
        assert metrics["admission_mode"] == "FALLBACK_BLOCK"
        assert not bundle["entry"]


@pytest.mark.parametrize(
    ("criterion", "text", "expected_resources"),
    [
        ("485", "子宫脱垂III度", 1),
        ("635", "AST 30上限40 ALT 30上限40 BUN 8上限9 Cr 80上限100", 4),
        ("855", "Scr 100 umol/L BUN 6 mmol/L ALT 30上限40 AST 25上限40", 4),
        ("675", "头面部带状疱疹", 1),
        ("735", "乙肝正在治疗", 1),
        ("745", "完成手术。术后继续有创机械通气", 2),
    ],
)
def test_target_safe_resource_paths_are_visible_to_service_replay(criterion, text, expected_resources):
    _, bundle, _, _ = _run(criterion, text)
    resources = tuple(entry["resource"] for entry in bundle["entry"])
    assert len(resources) == expected_resources
    result = replay_service(
        resources,
        contract_for_criterion(criterion).service,
        "http://localhost:3456/api/terminology/",
        {"p1": "case-1"},
    )
    assert result.status == "SERVICE_HIT"


def test_builder_script_generates_the_only_experiment_g_candidate():
    result = subprocess.run(
        [sys.executable, "scripts/build_v5s3_expg_criterion_recall_submission.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    candidates = list((ROOT / "submission").glob("*v5s3_expg*candidate.json"))
    assert [path.name for path in candidates] == ["a_test_message_bundle_v5s3_expg_criterion_recall_candidate.json"]


def test_experiment_g_audit_reports_all_hard_gates(tmp_path):
    audit = importlib.import_module("scripts.audit_v5s3_expg")
    result = audit.audit_experiment(output_dir=tmp_path)
    assert result["experiment_e_sha256"] == "831385ec9deab93d19e54c8319027978eee4b6843c32ddbc5714795b50ad27e8"
    assert result["non_target_parity"] == 10
    assert result["non_target_match_delta"] == 0
    assert result["zero_anchor_fallback_positives"] == 0
    assert result["counts"] == {
        "decode": 16,
        "compile": 16,
        "exec": 16,
        "embedded_positive": 16,
        "embedded_negative": 16,
        "fhir": 16,
        "service": 16,
        "security": 16,
        "dataclasses": 0,
        "enums": 0,
        "flatten_rename": 0,
        "unresolved_symbols": 0,
    }
    written = json.loads((tmp_path / "V5S3G_AUDIT.json").read_text(encoding="utf-8"))
    assert written["counts"] == result["counts"]
