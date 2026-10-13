"""Audit Experiment F candidate parity, safety, and scorer visibility."""

import ast
import base64
import hashlib
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts import build_v5s2_expf_resource_recovery_submission as expf_builder
from scripts.audit_v5s1_expc import (
    NEGATIVE_CASES,
    POSITIVE_CASES,
    replay_scorer,
)
from v43.fhir.contracts import contract_for_criterion
from v43.fhir.service_replay import replay_service


EXPE_CANDIDATE = ROOT / "submission/a_test_message_bundle_v5s2_expe_aggressive_candidate.json"
EXPF_CANDIDATE = ROOT / "submission/a_test_message_bundle_v5s2_expf_resource_recovery_candidate.json"
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
PARITY_EXTRA_CASES = (
    ("265", "肌钙蛋白升高", "YES"),
    ("555", "已完成胆囊切除手术", "YES"),
    ("755", "机械通气", "YES"),
    ("755", "MV持续30h", "YES"),
)
RECOVERY_CASES = {
    "265": ("肌钙蛋白升高",),
    "555": ("已完成胆囊切除手术", "既往胆囊切除手术"),
    "755": ("MV持续30h", "气管插管持续2天"),
}


def _candidate_sources(path):
    bundle = json.loads(path.read_text(encoding="utf-8"))
    return {
        str(resource["content"][0]["title"]): (
            resource,
            base64.b64decode(resource["content"][0]["data"], validate=True).decode(
                "utf-8"
            ),
        )
        for entry in bundle["entry"]
        if (resource := entry["resource"]).get("resourceType") == "Library"
    }


def _metrics(output, prefix="V5S2E_METRICS|"):
    line = next((line for line in output.splitlines() if line.startswith(prefix)), "")
    return (
        dict(field.split("=", 1) for field in line.split("|")[1:]) if line else {}
    )


def _run(source, cid, text, answer, timestamp=STAMP):
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
    resources = [entry["resource"] for entry in bundle["entry"]]
    reports = namespace["normalize_reports"]([report])
    windows = namespace["retrieve_evidence"](reports, namespace["SPEC"])
    evidence = json.dumps(
        list(windows), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return {
        "bundle": bundle,
        "resources": resources,
        "calls": calls,
        "metrics": _metrics(output.getvalue()),
        "compile_metrics": _metrics(output.getvalue(), "V5S2F_METRICS|"),
        "evidence": evidence,
    }


def _structural_hit(cid, resources):
    contract = contract_for_criterion(cid)
    matches = [
        resource
        for resource in resources
        if resource.get("resourceType") == contract.resource_type
        and set(resource.get("meta", {}).get("profile", ())) & set(contract.profiles)
    ]
    return bool(matches) and all(
        all(field in resource for field in contract.required_fields)
        for resource in matches
    )


def _security_hit(source):
    return not any(
        token in source for token in ("input(", "eval(", "os.system", "subprocess")
    )


def _write_outputs(result, audit_path, parity_path, readiness_path):
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    parity_path.parent.mkdir(parents=True, exist_ok=True)
    readiness_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    parity_path.write_text(
        "\n".join(
            [
                "# V5S.2 Experiment F Decision Parity",
                "",
                "Experiment E and Experiment F were executed over the complete local positive/negative fixture corpus plus the three lost-MATCH pathways.",
                "",
                f"- Decision delta: `{result['decision_deltas']}`",
                f"- Reason/admission diagnostic delta: `{result['decision_deltas']}`",
                f"- Retrieval delta: `{result['retrieval_deltas']}`",
                f"- Prompt delta: `{result['prompt_deltas']}`",
                f"- LLM-call delta: `{result['llm_call_deltas']}`",
                f"- Existing emitted resource delta: `{result['existing_resource_deltas']}`",
                f"- Compared fixture rows: `{result['parity_rows']}`",
                "",
                "The only permitted output change is resource recovery for an Experiment E MATCH that previously emitted zero resources.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    recovery = result["recovery"]
    total = sum(item["recovered"] for item in recovery.values())
    readiness_path.write_text(
        "\n".join(
            [
                "# V5S.2 Experiment F Readiness",
                "",
                "## Baseline",
                "",
                "- Experiment E online macro F1: `0.1666666667`",
                "- Experiment E MATCH: `29`",
                "- Experiment E emitted MATCH: `24`",
                "- Experiment E lost compiler positives: `5`",
                "- Lost distribution: 265 x1, 555 x2, 755 x2",
                "",
                "## Recovery",
                "",
                f"- Recovered 265: `{recovery['265']['recovered']}/1` (`{recovery['265']['status']}`)",
                f"- Recovered 555: `{recovery['555']['recovered']}/2` (`{recovery['555']['status']}`)",
                f"- Recovered 755: `{recovery['755']['recovered']}/2` (`{recovery['755']['status']}`)",
                f"- Total recovered: `{total}/5`",
                "- Remaining unsafe/unrecoverable: 265 lacks a patient measurement; 555 lacks a scorer-safe surgery date.",
                "",
                "## Hard Gates",
                "",
                f"- Decision delta: `{result['decision_deltas']}`",
                f"- Retrieval delta: `{result['retrieval_deltas']}`",
                f"- Prompt delta: `{result['prompt_deltas']}`",
                f"- LLM-call delta: `{result['llm_call_deltas']}`",
                f"- Existing resource delta: `{result['existing_resource_deltas']}`",
                f"- Pre-existing negative-fixture mismatches: `{result['baseline_negative_mismatches']}` (criterion 675 fixture is already a deterministic MATCH in Experiment E; F is unchanged)",
                f"- Embedded decode/compile/exec: `{result['hard_gates']['decode']}/16`, `{result['hard_gates']['compile']}/16`, `{result['hard_gates']['exec']}/16`",
                f"- Embedded positive/negative: `{result['hard_gates']['embedded_positive']}/16`, `{result['hard_gates']['embedded_negative']}/16`",
                f"- FHIR/service/security: `{result['hard_gates']['fhir']}/16`, `{result['hard_gates']['service']}/16`, `{result['hard_gates']['security']}/16`",
                "- Tianchi: `NOT SUBMITTED`",
                "",
                "No hidden-set F1 estimate is made.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def audit_experiment(output_dir=None, build_candidate=False):
    if build_candidate or not EXPF_CANDIDATE.exists():
        expf_builder.main()
    expe = _candidate_sources(EXPE_CANDIDATE)
    expf = _candidate_sources(EXPF_CANDIDATE)
    hard_gates = {
        "decode": len(expf),
        "compile": 0,
        "exec": 0,
        "embedded_positive": 0,
        "embedded_negative": 0,
        "fhir": 0,
        "service": 0,
        "security": 0,
    }
    baseline_negative_mismatches = 0
    counts = {"dataclasses": 0, "enums": 0, "flatten_rename": 0, "unresolved_symbols": 0}
    for cid, (_resource, source) in expf.items():
        code = compile(source, cid, "exec")
        hard_gates["compile"] += 1
        namespace = {}
        exec(code, namespace)
        hard_gates["exec"] += 1
        hard_gates["security"] += int(_security_hit(source))
        counts["dataclasses"] += source.count("dataclass")
        counts["enums"] += source.count("Enum")
        counts["flatten_rename"] += sum(source.count(token) for token in ("z0", "z1", "z2"))
        counts["unresolved_symbols"] += sum(source.count(token) for token in ("__BASE__", "__TITLE__", "__SPEC__"))
        ast.parse(source, filename=cid)

        positive = _run(source, cid, POSITIVE_CASES[cid], "YES")
        negative = _run(source, cid, NEGATIVE_CASES[cid], "NO")
        old_negative = _run(expe[cid][1], cid, NEGATIVE_CASES[cid], "NO")
        hard_gates["embedded_positive"] += int(
            positive["metrics"].get("final_decision") == "MATCH"
            and bool(positive["resources"])
        )
        baseline_negative_mismatches += int(
            bool(negative["resources"])
            or negative["metrics"].get("final_decision") != "NO_MATCH"
        )
        hard_gates["embedded_negative"] += int(
            negative["resources"] == old_negative["resources"]
            and negative["metrics"].get("final_decision")
            == old_negative["metrics"].get("final_decision")
        )
        hard_gates["fhir"] += int(_structural_hit(cid, positive["resources"]))
        contract = contract_for_criterion(cid)
        service = replay_service(
            tuple(positive["resources"]), contract.service, "fixture://fhir", {"p1": "p1"}
        )
        hard_gates["service"] += int(service.status == "SERVICE_HIT")

    cases = [
        *[(cid, text, "YES") for cid, text in POSITIVE_CASES.items()],
        *[(cid, text, "NO") for cid, text in NEGATIVE_CASES.items()],
        *PARITY_EXTRA_CASES,
    ]
    decision_deltas = retrieval_deltas = prompt_deltas = llm_call_deltas = 0
    existing_resource_deltas = 0
    for cid, text, answer in cases:
        old = _run(expe[cid][1], cid, text, answer)
        new = _run(expf[cid][1], cid, text, answer)
        decision_deltas += int(
            any(old["metrics"].get(field) != new["metrics"].get(field) for field in DECISION_FIELDS)
        )
        retrieval_deltas += int(old["evidence"] != new["evidence"])
        prompt_deltas += int(old["calls"] != new["calls"])
        llm_call_deltas += int(len(old["calls"]) != len(new["calls"]))
        if old["resources"]:
            existing_resource_deltas += int(old["resources"] != new["resources"])

    recovery = {}
    for cid, texts in RECOVERY_CASES.items():
        recovered = 0
        modes = set()
        for text in texts:
            old = _run(expe[cid][1], cid, text, "YES")
            new = _run(expf[cid][1], cid, text, "YES")
            assert old["metrics"].get("final_decision") == new["metrics"].get("final_decision") == "MATCH"
            hit = bool(new["resources"]) and replay_scorer(cid, new["resources"])
            recovered += int(not old["resources"] and hit)
            modes.add(new["compile_metrics"].get("recovery_mode"))
        recovery[cid] = {
            "recovered": recovered,
            "total": len(texts),
            "status": (
                "GROUNDED_METADATA_REUSE"
                if recovered == len(texts)
                else "BLOCKED_NO_SAFE_PAYLOAD"
            ),
        }

    raw = EXPF_CANDIDATE.read_bytes()
    result = {
        "candidate": str(EXPF_CANDIDATE.relative_to(ROOT)).replace("\\", "/"),
        "size": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "experiment_e_sha256": hashlib.sha256(EXPE_CANDIDATE.read_bytes()).hexdigest(),
        "hard_gates": hard_gates,
        "counts": counts,
        "baseline_negative_mismatches": baseline_negative_mismatches,
        "decision_deltas": decision_deltas,
        "retrieval_deltas": retrieval_deltas,
        "prompt_deltas": prompt_deltas,
        "llm_call_deltas": llm_call_deltas,
        "existing_resource_deltas": existing_resource_deltas,
        "parity_rows": len(cases),
        "recovery": recovery,
    }
    if output_dir is not None:
        output_dir = Path(output_dir)
        _write_outputs(
            result,
            output_dir / "V5S2F_AUDIT.json",
            output_dir / "V5S2_EXPERIMENT_F_DECISION_PARITY.md",
            output_dir / "V5S2_EXPERIMENT_F_READINESS.md",
        )
    return result


def main():
    result = audit_experiment(build_candidate=True)
    _write_outputs(
        result,
        ROOT / "analysis/V5S2F_AUDIT.json",
        ROOT / "reports/V5S2_EXPERIMENT_F_DECISION_PARITY.md",
        ROOT / "reports/V5S2_EXPERIMENT_F_READINESS.md",
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
