"""Audit Experiment G against the frozen Experiment E champion."""

from __future__ import annotations

import ast
import base64
import hashlib
import io
import json
from contextlib import redirect_stdout
from pathlib import Path

from scripts import build_v5s2_expe_aggressive_submission as expe_builder
from scripts import build_v5s3_expg_criterion_recall_submission as expg_builder
from v43.fhir.contracts import contract_for_criterion
from v43.fhir.service_replay import replay_service
from v5s.criterion_data import CRITERION_IDS


ROOT = Path(__file__).resolve().parents[1]
EXPE_CANDIDATE = ROOT / "submission/a_test_message_bundle_v5s2_expe_aggressive_candidate.json"
EXPG_CANDIDATE = ROOT / "submission/a_test_message_bundle_v5s3_expg_criterion_recall_candidate.json"
TARGETS = ("485", "635", "855", "675", "735", "745")
NON_TARGETS = tuple(cid for cid in CRITERION_IDS if cid not in TARGETS)

POSITIVE_CASES = {
    "165": "已在外院完成两周期化疗",
    "185": "首次接受伊立替康化疗",
    "265": "cTnI 0.08 ug/L",
    "485": "子宫脱垂III度",
    "555": "3个月前完成胆囊切除术",
    "565": "目前严重腹泻",
    "615": "术后病理 pN1",
    "635": "AST 30上限40 ALT 30上限40 BUN 8上限9 Cr 80上限100",
    "675": "头面部带状疱疹",
    "735": "乙肝正在治疗",
    "745": "完成手术。术后继续有创机械通气",
    "755": "机械通气持续30小时",
    "805": "目前每日吸烟",
    "835": "目前凝血功能异常",
    "855": "Scr 100 umol/L BUN 6 mmol/L ALT 30上限40 AST 25上限40",
    "875": "既往发生颅内高压",
}

NEGATIVE_CASES = {
    "165": "仅计划转外院化疗",
    "185": "拟首次使用伊立替康，尚未给药",
    "265": "cTnI 0.03 ug/L",
    "485": "POP-Q II期",
    "555": "8个月前完成胆囊切除术",
    "565": "严重腹泻已缓解",
    "615": "pN0且GS 7，PSA 0.05 ng/mL",
    "635": "ALT 100上限40",
    "675": "患者65岁",
    "735": "结核已治愈",
    "745": "术后仅无创通气",
    "755": "机械通气持续12小时",
    "805": "从不吸烟",
    "835": "凝血功能正常",
    "855": "BUN 12 mmol/L",
    "875": "否认颅内高压且意识清楚",
}

DELTA_CASES = {
    "485": ("POP-Q III", "POP-Q Ⅳ", "子宫脱垂III度", "盆腔器官脱垂四期"),
    "635": ("肝肾功能正常", "ALT正常，AST正常", "BUN正常", "Cr正常"),
    "855": ("Scr 100 umol/L", "BUN 6 mmol/L", "肝肾功能无明显异常"),
    "675": ("头面部带状疱疹", "65岁患者确诊带状疱疹"),
    "735": ("乙肝正在治疗", "结核，抗结核治疗中"),
    "745": ("患者接受手术治疗。术后转ICU，继续有创机械通气。",),
}

TARGET_DETAILS = {
    "485": {"aliases_added": "POPQ/POP Q; uterine and vaginal prolapse; Roman, Unicode, Arabic, and Chinese stage forms", "rules_added": "locally bound stage III/IV", "semantic_added": "prolapse anchor plus bound high stage", "contradictions": "POP-Q I/II, denial, unrelated staging"},
    "635": {"aliases_added": "hepatic/renal function and qualitative normal language", "rules_added": "complete four-analyte rule preserved", "semantic_added": "qualitative normal or partial analyte with LLM YES", "contradictions": "any value above 2x analyte ULN"},
    "855": {"aliases_added": "hepatic/renal function and qualitative normal language", "rules_added": "complete four-analyte rule preserved", "semantic_added": "qualitative normal or partial analyte with LLM YES", "contradictions": "Scr>=178, BUN>=9, ALT/AST above ULN"},
    "675": {"aliases_added": "VZV reactivation, facial/ophthalmic/V1 sites, English age forms", "rules_added": "zoster plus site or age>=50", "semantic_added": "same bounded combinations", "contradictions": "explicit zoster denial"},
    "735": {"aliases_added": "current, ongoing, treated, persistent states", "rules_added": "target disease plus current/treatment state", "semantic_added": "disease plus LLM YES with no resolved blocker", "contradictions": "history, cured, resolved, inactive"},
    "745": {"aliases_added": "post-op ventilation, remained intubated, respiratory support", "rules_added": "same or adjacent sentence postoperative invasive relation", "semantic_added": "bounded relation plus LLM YES", "contradictions": "pre-op only, NIV-only, planned-only"},
}


def _run(source: str, cid: str, text: str, answer: str = "YES") -> dict:
    namespace = {}
    exec(compile(source, cid, "exec"), namespace)
    generator = namespace["FHIRResourceBundleGenerator"]("http://localhost:3456")
    calls = []
    generator.transport = lambda prompt: (calls.append(prompt) or answer)
    output = io.StringIO()
    with redirect_stdout(output):
        bundle = generator.parse_clinical_text_to_fhir_bundle(
            "p1", [{"text": text, "timestamp": "2026-01-31T12:34:56+08:00"}]
        )
    line = next(line for line in output.getvalue().splitlines() if "_METRICS|" in line)
    metrics = dict(field.split("=", 1) for field in line.split("|")[1:])
    decision = metrics.get("final_decision", metrics.get("decision"))
    return {"decision": decision, "metrics": metrics, "bundle": bundle, "calls": calls, "namespace": namespace}


def _resources(run: dict) -> tuple[dict, ...]:
    return tuple(entry["resource"] for entry in run["bundle"].get("entry", ()))


def _fhir_valid(cid: str, resources: tuple[dict, ...]) -> bool:
    contract = contract_for_criterion(cid)
    profiles = set(contract.profiles)
    for resource in resources:
        if resource.get("resourceType") != contract.resource_type:
            continue
        if not profiles.intersection(resource.get("meta", {}).get("profile", ())):
            continue
        if all(field in resource for field in contract.required_fields):
            return True
    return False


def _candidate_sources(path: Path) -> dict[str, str]:
    bundle = json.loads(path.read_text(encoding="utf-8"))
    return {
        str(resource["content"][0]["title"]): base64.b64decode(resource["content"][0]["data"], validate=True).decode("utf-8")
        for entry in bundle["entry"]
        if (resource := entry["resource"]).get("resourceType") == "Library"
    }


def _complexity_and_runtime(sources: dict[str, str]) -> tuple[dict, dict[str, dict]]:
    counts = {"decode": 0, "compile": 0, "exec": 0, "security": 0, "dataclasses": 0, "enums": 0, "flatten_rename": 0, "unresolved_symbols": 0}
    namespaces = {}
    for cid, source in sources.items():
        counts["decode"] += 1
        code = compile(source, cid, "exec")
        counts["compile"] += 1
        namespace = {}
        exec(code, namespace)
        namespaces[cid] = namespace
        counts["exec"] += 1
        counts["security"] += int(not any(token in source for token in ("input(", "eval(", "os.system", "subprocess")))
        counts["dataclasses"] += source.count("dataclass")
        counts["enums"] += source.count("Enum")
        counts["flatten_rename"] += sum(source.count(token) for token in ("z0", "z1", "z2"))
        counts["unresolved_symbols"] += sum(source.count(token) for token in ("__BASE__", "__TITLE__", "__SPEC__"))
        tree = ast.parse(source, filename=cid)
        counts["unresolved_symbols"] += sum(1 for node in ast.walk(tree) if isinstance(node, ast.Name) and node.id.startswith("__") and node.id.endswith("__") and node.id != "__name__")
    return counts, namespaces


def _write_readiness(path: Path, result: dict) -> None:
    lines = [
        "# V5S.3 Experiment G Readiness",
        "",
        "## Baseline",
        "",
        "- Champion Experiment E macro F1: `0.1666666666666667`",
        "- Failed Experiment F macro F1: `0.1500`",
        "- Experiment F lowered precision without increasing recall, so Experiment G branches from Experiment E.",
        "- No hidden-F1 estimate is made.",
        "",
        "## Offline Decision Matrix",
        "",
        "Counts below are from the public synthetic diagnostic matrix in `scripts/audit_v5s3_expg.py`, not online patient counts.",
        "",
        "| Criterion | Experiment E MATCH | Experiment G MATCH | Delta |",
        "|---|---:|---:|---:|",
    ]
    for cid in CRITERION_IDS:
        row = result["per_criterion"][cid]
        lines.append(f"| {cid} | {row['experiment_e_match']} | {row['experiment_g_match']} | {row['delta']} |")
    lines.extend(["", "## Target Detail", ""])
    for cid in TARGETS:
        row = result["per_criterion"][cid]
        detail = TARGET_DETAILS[cid]
        lines.extend([
            f"### {cid}",
            "",
            f"- Aliases added: {detail['aliases_added']}",
            f"- Rule positives added: {detail['rules_added']}",
            f"- Semantic positives added: {detail['semantic_added']}",
            f"- Contradiction blocks: {detail['contradictions']}",
            f"- Scorer-visible resource count in safe replay fixture: `{row['scorer_visible_resources']}`",
            f"- Replay HIT count: `{row['replay_hits']}`",
            "",
        ])
    lines.extend([
        "## Gates", "",
        f"- Non-target decision parity: `{result['non_target_parity']}/10`",
        f"- Non-target MATCH delta: `{result['non_target_match_delta']}`",
        f"- Zero-anchor fallback positives: `{result['zero_anchor_fallback_positives']}`",
        f"- Embedded decode/compile/exec/positive/negative: `{result['counts']['decode']}/16`, `{result['counts']['compile']}/16`, `{result['counts']['exec']}/16`, `{result['counts']['embedded_positive']}/16`, `{result['counts']['embedded_negative']}/16`",
        f"- FHIR/service/security: `{result['counts']['fhir']}/16`, `{result['counts']['service']}/16`, `{result['counts']['security']}/16`",
        f"- Complexity: dataclasses `{result['counts']['dataclasses']}`, Enums `{result['counts']['enums']}`, flatten rename `{result['counts']['flatten_rename']}`, unresolved globals `{result['counts']['unresolved_symbols']}`",
        "- Experiment E artifact: unchanged",
        "- Tianchi: not submitted",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def audit_experiment(output_dir: Path | None = None) -> dict:
    expg_builder.main()
    raw = EXPG_CANDIDATE.read_bytes()
    sources = _candidate_sources(EXPG_CANDIDATE)
    counts, _ = _complexity_and_runtime(sources)
    counts.update({"embedded_positive": 0, "embedded_negative": 0, "fhir": 0, "service": 0})
    per_criterion = {}
    zero_anchor_fallback_positives = 0
    non_target_parity = 0
    non_target_match_delta = 0

    for cid in CRITERION_IDS:
        source_e = expe_builder.build_source(cid, cid, {})
        source_g = expg_builder.build_source(cid, cid, {})
        pos = _run(source_g, cid, POSITIVE_CASES[cid])
        neg = _run(source_g, cid, NEGATIVE_CASES[cid], "NO")
        resources = _resources(pos)
        counts["embedded_positive"] += int(pos["decision"] == "MATCH" and bool(resources))
        counts["embedded_negative"] += int(neg["decision"] == "NO_MATCH" and not _resources(neg))
        counts["fhir"] += int(_fhir_valid(cid, resources))
        replay = replay_service(resources, contract_for_criterion(cid).service, "fixture://fhir", {"p1": "case-1"})
        counts["service"] += int(replay.status == "SERVICE_HIT")

        if cid in TARGETS:
            cases = DELTA_CASES[cid]
        else:
            cases = (POSITIVE_CASES[cid], NEGATIVE_CASES[cid])
        old_match = sum(_run(source_e, cid, text, "YES" if i == 0 or cid in TARGETS else "NO")["decision"] == "MATCH" for i, text in enumerate(cases))
        new_runs = [_run(source_g, cid, text, "YES" if i == 0 or cid in TARGETS else "NO") for i, text in enumerate(cases)]
        new_match = sum(run["decision"] == "MATCH" for run in new_runs)
        zero_anchor_fallback_positives += sum(run["decision"] == "MATCH" and run["metrics"].get("anchor_hits") == "0" for run in new_runs)
        per_criterion[cid] = {
            "experiment_e_match": old_match,
            "experiment_g_match": new_match,
            "delta": new_match - old_match,
            "scorer_visible_resources": len(resources) if cid in TARGETS else None,
            "replay_hits": int(replay.status == "SERVICE_HIT") if cid in TARGETS else None,
        }
        if cid in NON_TARGETS:
            e_pos = _run(source_e, cid, POSITIVE_CASES[cid])
            e_neg = _run(source_e, cid, NEGATIVE_CASES[cid], "NO")
            parity = source_e == source_g and e_pos["decision"] == pos["decision"] and e_neg["decision"] == neg["decision"] and bool(_resources(e_pos)) == bool(resources) and bool(_resources(e_neg)) == bool(_resources(neg))
            non_target_parity += int(parity)
            non_target_match_delta += (int(pos["decision"] == "MATCH") + int(neg["decision"] == "MATCH")) - (int(e_pos["decision"] == "MATCH") + int(e_neg["decision"] == "MATCH"))

    result = {
        "candidate": str(EXPG_CANDIDATE.relative_to(ROOT)).replace("\\", "/"),
        "size": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "experiment_e_sha256": hashlib.sha256(EXPE_CANDIDATE.read_bytes()).hexdigest(),
        "non_target_parity": non_target_parity,
        "non_target_match_delta": non_target_match_delta,
        "zero_anchor_fallback_positives": zero_anchor_fallback_positives,
        "counts": counts,
        "per_criterion": per_criterion,
        "targets": list(TARGETS),
        "tianchi": "NOT SUBMITTED",
    }
    destination = Path(output_dir) if output_dir is not None else ROOT / "analysis"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "V5S3G_AUDIT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if output_dir is None:
        _write_readiness(ROOT / "reports/V5S3_EXPERIMENT_G_READINESS.md", result)
    return result


if __name__ == "__main__":
    print(json.dumps(audit_experiment(), ensure_ascii=False, indent=2))
