"""Audit Experiment C decision parity and preserved scorer visibility."""

from __future__ import annotations

import base64
import csv
import io
import json
import sys
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import build_v5s1_expc_submission as expc_builder


V243_ROOT = ROOT.parent / "CHIP2026_CP2_A_baseline_v2_4_3"
FROZEN_CANDIDATE = ROOT / "submission/a_test_message_bundle_v5s1_candidate.json"
V243_CANDIDATE = V243_ROOT / "submission/a_test_message_bundle_v2_4_3.json"

TARGETS = {"265", "555", "755", "805", "855"}
REPORT_NAMES = (
    "EXPC_LEGACY_TRANSPORT_CONTRACT.csv",
    "EXPC_DECISION_PARITY.csv",
    "EXPC_SCORER_REPLAY.csv",
)

POSITIVE_CASES = {
    "165": "已在外院完成两周期化疗",
    "185": "首次接受伊立替康化疗",
    "265": "cTnI 0.08 ug/L",
    "485": "盆腔器官脱垂 POP-Q III期",
    "555": "3个月前完成胆囊切除术",
    "565": "目前严重腹泻",
    "615": "术后病理 pN1",
    "635": "AST 30上限40 ALT 30上限40 BUN 8上限9 Cr 180上限100",
    "675": "患者70岁确诊头面部带状疱疹",
    "735": "活动性乙型肝炎",
    "745": "术后行有创机械通气",
    "755": "机械通气持续30小时",
    "805": "目前每日吸烟",
    "835": "目前凝血功能异常",
    "855": "Scr 120 umol/L，BUN 7 mmol/L，ALT 30 U/L上限40，AST 25 U/L上限40",
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
    "635": "AST 30上限40 ALT 30上限40 BUN 8上限9 Cr 250上限100",
    "675": "躯干部带状疱疹，非头面部",
    "735": "乙肝病情稳定",
    "745": "术后仅无创通气",
    "755": "机械通气持续12小时",
    "805": "从不吸烟",
    "835": "凝血功能正常",
    "855": "Scr 120 umol/L，BUN 7 mmol/L，ALT 50 U/L上限40，AST 25 U/L上限40",
    "875": "否认颅内高压且意识清楚",
}

SCORER_CASES = (
    {"criterion": "265", "branch": "265_ctni", "text": "术前 cTnI 0.08 ug/L", "timestamp": "2020-01-01T00:00:00Z", "expected_hits": ("MISS", "HIT", "HIT")},
    {"criterion": "265", "branch": "265_ctnt", "text": "术前 cTnT 0.04 ug/L", "timestamp": "2020-01-01T00:00:00Z", "expected_hits": ("MISS", "HIT", "HIT")},
    {"criterion": "555", "branch": "555_three_months", "text": "3个月前完成胆囊切除手术", "timestamp": "2020-01-01T00:00:00Z", "expected_hits": ("MISS", "HIT", "HIT")},
    {"criterion": "755", "branch": "755_thirty_hours", "text": "机械通气持续30小时", "timestamp": "2020-01-01T00:00:00Z", "expected_hits": ("MISS", "HIT", "HIT")},
    {"criterion": "805", "branch": "805_current", "text": "目前每日吸烟", "timestamp": "2020-01-01T00:00:00Z", "expected_hits": ("HIT", "HIT", "HIT")},
    {"criterion": "805", "branch": "805_former_one_year", "text": "戒烟1年", "timestamp": "2020-01-01T00:00:00Z", "expected_hits": ("MISS", "HIT", "HIT")},
    {"criterion": "855", "branch": "855_normal", "text": "Scr 120 umol/L，BUN 7 mmol/L，ALT 30 U/L上限50正常，AST 25 U/L上限40正常", "timestamp": "2020-01-01T00:00:00Z", "expected_hits": ("MISS", "HIT", "HIT")},
    {"criterion": "855", "branch": "855_alt_45_uln_50", "text": "Scr 120 umol/L，BUN 7 mmol/L，ALT 45 U/L上限50正常，AST 25 U/L上限40正常", "timestamp": "2020-01-01T00:00:00Z", "expected_hits": ("MISS", "MISS", "MISS")},
)


def _candidate_sources(path: Path) -> dict[str, str]:
    bundle = json.loads(path.read_text(encoding="utf-8"))
    return {
        str(resource["content"][0]["title"]): base64.b64decode(
            resource["content"][0]["data"]
        ).decode("utf-8")
        for entry in bundle["entry"]
        if (resource := entry["resource"]).get("resourceType") == "Library"
    }


def _namespace(source: str, cid: str) -> dict:
    namespace: dict = {}
    exec(compile(source, cid, "exec"), namespace)
    return namespace


def _parse_metrics(output: str) -> dict[str, str]:
    line = next(
        (line for line in output.splitlines() if line.startswith("V5S_METRICS|")),
        "",
    )
    if not line:
        return {}
    return dict(field.split("=", 1) for field in line.split("|")[1:])


def _run_source(source: str, cid: str, text: str, timestamp: str | None, answer: str):
    namespace = _namespace(source, cid)
    generator = namespace["FHIRResourceBundleGenerator"]("http://localhost:3456")
    calls: list[str] = []
    if hasattr(generator, "transport"):
        generator.transport = lambda prompt: (calls.append(prompt) or answer)
    report = {"text": text}
    if timestamp is not None:
        report["timestamp"] = timestamp
    output = io.StringIO()
    with redirect_stdout(output):
        bundle = generator.parse_clinical_text_to_fhir_bundle("p1", [report])
    resources = [entry["resource"] for entry in bundle.get("entry", [])]
    return resources, calls, _parse_metrics(output.getvalue()), namespace


def _evidence_snapshot(namespace: dict, text: str, timestamp: str | None) -> str:
    report = {"text": text}
    if timestamp is not None:
        report["timestamp"] = timestamp
    reports = namespace["normalize_reports"]([report])
    windows = namespace["retrieve_evidence"](reports, namespace["SPEC"])
    return json.dumps(list(windows), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _profiles(resource: dict) -> tuple[str, ...]:
    return tuple(resource.get("meta", {}).get("profile", ()))


def _patient(resource: dict) -> str | None:
    reference = resource.get("subject", {}).get("reference", "")
    return reference.split("/", 1)[1] if reference.startswith("Patient/") else None


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def replay_scorer(cid: str, resources: list[dict]) -> bool:
    """Faithful local replay of the five preserved V2.4.3 service queries."""
    base = "http://localhost:3456/api/terminology/"
    if cid == "265":
        profile = base + "Profile/cnwqk265-serum-cardiac-troponin-observation"
        extension = base + "Extension/cnwqk265-preoperative-extension"
        system = base + "CodeSystem/cnwqk265-cardiac-troponin-tests"
        for resource in resources:
            if profile not in _profiles(resource) or _patient(resource) is None:
                continue
            if not any(item.get("url") == extension and item.get("valueBoolean") is True for item in resource.get("extension", ())):
                continue
            code = next((item.get("code") for item in resource.get("code", {}).get("coding", ()) if item.get("system") == system), None)
            quantity = resource.get("valueQuantity", {})
            value = quantity.get("value")
            if quantity.get("unit") == "ug/L" and value is not None and ((code == "cTnI" and value >= 0.06) or (code == "cTnT" and value >= 0.03)):
                return True
        return False
    if cid == "555":
        profile = base + "Profile/cnwqk555-SurgeryHistoryProfile"
        reference = datetime(2020, 1, 1)
        for resource in resources:
            if profile not in _profiles(resource) or resource.get("status") != "completed" or _patient(resource) is None:
                continue
            value = resource.get("performedDateTime")
            if not value:
                continue
            try:
                procedure = _parse_datetime(value).replace(tzinfo=None)
            except (TypeError, ValueError):
                continue
            if 0 <= (reference - procedure).days <= 180:
                return True
        return False
    if cid == "755":
        profile = base + "Profile/cnwqk755-MechanicalVentilationProcedure"
        for resource in resources:
            period = resource.get("performedPeriod", {})
            if profile not in _profiles(resource) or not period.get("start") or not period.get("end"):
                continue
            try:
                if (_parse_datetime(period["end"]) - _parse_datetime(period["start"])).total_seconds() >= 86400:
                    return True
            except (TypeError, ValueError):
                continue
        return False
    if cid == "805":
        status_profile = base + "Profile/cnwqk805-SmokingStatusObservation"
        cessation_profile = base + "Profile/cnwqk805-SmokingCessationDurationObservation"
        statuses: dict[str, str] = {}
        durations: dict[str, float] = {}
        for resource in resources:
            patient = _patient(resource)
            if patient is None:
                continue
            if status_profile in _profiles(resource):
                coding = resource.get("valueCodeableConcept", {}).get("coding", ())
                if coding:
                    statuses.setdefault(patient, coding[0].get("code"))
            if cessation_profile in _profiles(resource):
                value = resource.get("valueQuantity", {}).get("value")
                if value is not None:
                    durations[patient] = value
        return any(status == "current-smoker" or (status == "former-smoker" and patient in durations and durations[patient] < 2) for patient, status in statuses.items())
    if cid == "855":
        profiles = {
            "scr": base + "Profile/cnwqk855-serum-creatinine-observation",
            "bun": base + "Profile/cnwqk855-blood-urea-nitrogen-observation",
            "alt": base + "Profile/cnwqk855-alanine-aminotransferase-observation",
            "ast": base + "Profile/cnwqk855-aspartate-aminotransferase-observation",
        }
        grouped: dict[str, dict[str, dict]] = {}
        for resource in resources:
            patient = _patient(resource)
            if patient is None:
                continue
            kind = next((name for name, profile in profiles.items() if profile in _profiles(resource)), None)
            value = resource.get("valueQuantity", {}).get("value")
            if kind is None or value is None:
                continue
            current = grouped.setdefault(patient, {}).get(kind)
            if current is None or (resource.get("effectiveDateTime", "") and current.get("effectiveDateTime", "") < resource.get("effectiveDateTime", "")):
                grouped[patient][kind] = resource
        return any(
            set(values) == set(profiles)
            and values["scr"]["valueQuantity"]["value"] < 178
            and values["bun"]["valueQuantity"]["value"] < 9
            and values["alt"]["valueQuantity"]["value"] < 40
            and values["ast"]["valueQuantity"]["value"] < 35
            for values in grouped.values()
        )
    raise ValueError(f"unsupported scorer criterion: {cid}")


def _contract_rows() -> list[dict[str, str]]:
    source = "exact V2.4.3 candidate Library + preserved evidence/a_*_FHIR_SERVICE_CODE.py"
    return [
        {"criterion": "265", "v5s1_shape": "generic troponin Observation", "v243_shape": "serum/preoperative profiles + analyte coding + extension", "scorer_query_requirement": "serum profile; preoperative=true; cTnI/cTnT code; ug/L threshold", "planned_expc_shape": "exact legacy-visible troponin fields from grounded analyte/value", "transport_only_change": "YES", "decision_impact": "NONE", "evidence_source": source},
        {"criterion": "555", "v5s1_shape": "Procedure with 1970 fallback", "v243_shape": "completed Procedure with relative performedDateTime", "scorer_query_requirement": "completed procedure within 0..180 days before 2020-01-01", "planned_expc_shape": "legacy relative date only when report timestamp and interval exist", "transport_only_change": "YES", "decision_impact": "NONE", "evidence_source": source},
        {"criterion": "755", "v5s1_shape": "performedPeriod.duration_hours", "v243_shape": "performedPeriod.start/end", "scorer_query_requirement": "valid ISO period lasting at least 86400 seconds", "planned_expc_shape": "legacy start/end derived from grounded duration and report timestamp", "transport_only_change": "YES", "decision_impact": "NONE", "evidence_source": source},
        {"criterion": "805", "v5s1_shape": "smoking status only", "v243_shape": "status plus cessation-duration Observation", "scorer_query_requirement": "current smoker or former smoker with duration <2", "planned_expc_shape": "legacy status and grounded cessation resource", "transport_only_change": "YES", "decision_impact": "NONE", "evidence_source": source},
        {"criterion": "855", "v5s1_shape": "single creatinine Observation", "v243_shape": "four profile-specific lab Observations", "scorer_query_requirement": "latest Scr/BUN/ALT/AST all present and below fixed thresholds", "planned_expc_shape": "four observations from already-grounded V5S.1 values", "transport_only_change": "YES", "decision_impact": "NONE", "evidence_source": source},
    ]


def _write_csv(path: Path, rows: list[dict], fields: tuple[str, ...]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def audit_experiment(output_dir: Path | None = None, cases=None) -> dict:
    frozen = _candidate_sources(FROZEN_CANDIDATE)
    v243 = _candidate_sources(V243_CANDIDATE)
    expc = {cid: expc_builder.build_source(cid, cid, {}) for cid in frozen}
    non_target_source_deltas = sum(frozen[cid] != expc[cid] for cid in frozen if cid not in TARGETS)
    target_prefix_deltas = sum(not expc[cid].startswith(frozen[cid]) for cid in TARGETS)

    parity_rows = []
    decision_deltas = 0
    timestamp = "2026-01-31T12:34:56+08:00"
    for cid in frozen:
        for case_class, text, answer in (("POS", POSITIVE_CASES[cid], "YES"), ("NEG", NEGATIVE_CASES[cid], "NO")):
            old_resources, old_calls, old_metrics, old_ns = _run_source(frozen[cid], cid, text, timestamp, answer)
            new_resources, new_calls, new_metrics, new_ns = _run_source(expc[cid], cid, text, timestamp, answer)
            old_evidence = _evidence_snapshot(old_ns, text, timestamp)
            new_evidence = _evidence_snapshot(new_ns, text, timestamp)
            fields = tuple(key for key in old_metrics if key != "resources")
            equal = (
                {key: old_metrics.get(key) for key in fields} == {key: new_metrics.get(key) for key in fields}
                and old_calls == new_calls
                and old_evidence == new_evidence
                and bool(old_resources) == bool(new_resources)
            )
            decision_deltas += int(not equal)
            parity_rows.append({
                "criterion": cid,
                "case": case_class,
                "decision_equal": "YES" if old_metrics.get("decision") == new_metrics.get("decision") else "NO",
                "reason_equal": "YES" if old_metrics.get("reason") == new_metrics.get("reason") else "NO",
                "route_equal": "YES" if old_metrics.get("route") == new_metrics.get("route") else "NO",
                "llm_calls_equal": "YES" if old_calls == new_calls else "NO",
                "evidence_equal": "YES" if old_evidence == new_evidence else "NO",
                "positive_set_equal": "YES" if bool(old_resources) == bool(new_resources) else "NO",
                "all_decision_fields_equal": "YES" if equal else "NO",
            })

    scorer_rows = []
    for case in cases or SCORER_CASES:
        cid = case["criterion"]
        text = case["text"]
        timestamp = case.get("timestamp")
        old_resources, _, old_metrics, _ = _run_source(frozen[cid], cid, text, timestamp, "YES")
        new_resources, _, new_metrics, _ = _run_source(expc[cid], cid, text, timestamp, "YES")
        legacy_resources, _, _, _ = _run_source(v243[cid], cid, text, timestamp, "YES")
        row = {
            "criterion": cid,
            "branch": case["branch"],
            "V5S1_SERVICE_HIT": "HIT" if replay_scorer(cid, old_resources) else "MISS",
            "EXPC_SERVICE_HIT": "HIT" if replay_scorer(cid, new_resources) else "MISS",
            "V243_SERVICE_HIT": "HIT" if replay_scorer(cid, legacy_resources) else "MISS",
            "shape_delta": f"{len(old_resources)}->{len(new_resources)};legacy={len(legacy_resources)}",
            "decision": new_metrics.get("decision", "MATCH" if new_resources else "NO_MATCH"),
            "V5S1_resources": old_resources,
            "EXPC_resources": new_resources,
            "V243_resources": legacy_resources,
        }
        scorer_rows.append(row)

    contract_rows = _contract_rows()
    if output_dir is not None:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        _write_csv(output_dir / REPORT_NAMES[0], contract_rows, ("criterion", "v5s1_shape", "v243_shape", "scorer_query_requirement", "planned_expc_shape", "transport_only_change", "decision_impact", "evidence_source"))
        _write_csv(output_dir / REPORT_NAMES[1], parity_rows, ("criterion", "case", "decision_equal", "reason_equal", "route_equal", "llm_calls_equal", "evidence_equal", "positive_set_equal", "all_decision_fields_equal"))
        _write_csv(output_dir / REPORT_NAMES[2], scorer_rows, ("criterion", "branch", "V5S1_SERVICE_HIT", "EXPC_SERVICE_HIT", "V243_SERVICE_HIT", "shape_delta"))
    return {
        "decision_deltas": decision_deltas,
        "non_target_source_deltas": non_target_source_deltas,
        "target_prefix_deltas": target_prefix_deltas,
        "contract_rows": contract_rows,
        "parity_rows": parity_rows,
        "scorer_rows": scorer_rows,
    }


if __name__ == "__main__":
    result = audit_experiment(ROOT / "analysis")
    print(json.dumps({key: result[key] for key in ("decision_deltas", "non_target_source_deltas", "target_prefix_deltas")}, indent=2))
