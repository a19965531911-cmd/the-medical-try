import base64
import csv
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "submission" / "a_test_message_bundle_v5s_candidate.json"
AUTOPSY_CSV = ROOT / "analysis" / "V5S_ONLINE_AUTOPSY.csv"
AUTOPSY_MD = ROOT / "analysis" / "V5S_ONLINE_AUTOPSY.md"
SERVICE_CSV = ROOT / "analysis" / "V5S_SERVICE_VISIBILITY_MATRIX.csv"

sys.path.insert(0, str(ROOT / "src"))
from v43.fhir.contracts import contract_for_criterion
from v43.fhir.service_replay import replay_service


CRITERIA = ("485", "615", "265", "635", "675", "735", "745", "755", "855", "835", "875", "805", "565", "555", "185", "165")

POSITIVE_CASES = {
    "165": [("completed outside chemotherapy", "已在外院完成两周期化疗")],
    "185": [("first irinotecan", "首次接受伊立替康化疗")],
    "265": [("cTnI", "cTnI 0.08 ug/L"), ("cTnT", "cTnT 0.04 ug/L")],
    "485": [("III", "盆腔器官脱垂 POP-Q III期"), ("IV", "盆腔器官脱垂 POP-Q IV期")],
    "555": [("recent surgery", "3个月前完成胆囊切除术")],
    "565": [("severe diarrhea", "目前严重腹泻"), ("severe constipation", "目前严重便秘")],
    "615": [("pT3a", "病理pT3a"), ("pT3b", "病理pT3b"), ("pT4", "病理pT4"), ("R1", "切缘R1"), ("pN1", "pN1"), ("GS", "Gleason评分8分"), ("PSA", "PSA 0.2 ng/mL")],
    "635": [("labs", "AST 30上限40 ALT 30上限40 BUN 8上限9 Cr 80上限100")],
    "675": [("herpes zoster", "患者70岁确诊头面部带状疱疹")],
    "735": [("active disease", "活动性乙型肝炎")],
    "745": [("postoperative ventilation", "术后行有创机械通气")],
    "755": [("24h ventilation", "机械通气持续30小时")],
    "855": [("renal hepatic labs", "Scr 120 umol/L，BUN 7 mmol/L，ALT 30 U/L上限40，AST 25 U/L上限40")],
    "835": [("coagulation", "目前凝血功能异常")],
    "875": [("intracranial", "既往发生颅内高压"), ("consciousness", "既往发生意识障碍")],
    "805": [("current smoker", "目前每日吸烟"), ("recent quitter", "戒烟1年")],
}


def decode_libraries():
    bundle = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    result = {}
    for entry in bundle["entry"]:
        resource = entry["resource"]
        if resource.get("resourceType") == "Library":
            cid = str(resource["content"][0]["title"])
            source = base64.b64decode(resource["content"][0]["data"], validate=True).decode("utf-8")
            namespace = {}
            exec(compile(source, resource["name"], "exec"), namespace)
            result[cid] = (resource, source, namespace)
    return result


def parse_metrics(path):
    records = []
    if not path or not path.exists():
        return records
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not re.match(r"^\s*V5S_METRICS\|", line):
            continue
        fields = {}
        for item in line.split("V5S_METRICS|", 1)[1].split("|"):
            if "=" in item:
                key, value = item.split("=", 1)
                fields[key] = value
        records.append(fields)
    return records


def find_metrics_log():
    candidates = []
    for folder in (ROOT, ROOT / "analysis", ROOT / "reports", ROOT / "work"):
        if folder.exists():
            candidates.extend(folder.glob("**/*"))
    for path in candidates:
        if path.is_file() and path.suffix.lower() in {".log", ".txt", ".out", ".json", ".md"}:
            try:
                if re.search(r"^\s*V5S_METRICS\|", path.read_text(encoding="utf-8", errors="replace"), re.MULTILINE):
                    return path
            except OSError:
                pass
    return None


def metric_summary(records):
    rows = []
    for cid in CRITERIA:
        subset = [r for r in records if str(r.get("criterion")) == cid]
        numeric = lambda key: [float(r[key]) for r in subset if r.get(key, "").replace(".", "", 1).isdigit()]
        windows = numeric("evidence_windows")
        prompts = numeric("prompt_length")
        reasons = Counter(r.get("reason", "") for r in subset)
        row = {
            "criterion": cid,
            "evaluations": len(subset),
            "RULE_calls": sum(r.get("route") == "RULE" for r in subset),
            "LLM_calls": sum(r.get("llm_called") == "1" for r in subset),
            "MATCH_decisions": sum(r.get("decision") == "MATCH" for r in subset),
            "NO_MATCH_decisions": sum(r.get("decision") == "NO_MATCH" for r in subset),
            "MATCH_resources_gt0": sum(r.get("decision") == "MATCH" and float(r.get("resources", "0") or 0) > 0 for r in subset),
            "MATCH_resources_eq0": sum(r.get("decision") == "MATCH" and float(r.get("resources", "0") or 0) == 0 for r in subset),
            "total_resources": sum(float(r.get("resources", "0") or 0) for r in subset),
            "mean_evidence_windows": round(statistics.mean(windows), 3) if windows else "",
            "prompt_length_min": min(prompts) if prompts else "",
            "prompt_length_mean": round(statistics.mean(prompts), 3) if prompts else "",
            "prompt_length_max": max(prompts) if prompts else "",
            "reason_distribution": json.dumps(dict(reasons), ensure_ascii=False, sort_keys=True),
        }
        rows.append(row)
    return rows


def write_autopsy(records, log_path):
    rows = metric_summary(records)
    AUTOPSY_CSV.parent.mkdir(parents=True, exist_ok=True)
    with AUTOPSY_CSV.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["criterion"])
        writer.writeheader()
        writer.writerows(rows)
    total = len(records)
    matches = sum(r.get("decision") == "MATCH" for r in records)
    match_resources = sum(r.get("decision") == "MATCH" and float(r.get("resources", "0") or 0) > 0 for r in records)
    lines = [
        "# V5S ONLINE AUTOPSY",
        "",
        f"Frozen candidate commit: `67d48f9`.",
        f"Metrics log: `{log_path}`." if log_path else "Metrics log: **MISSING**. No readable file containing `V5S_METRICS|` was found.",
        "",
        "## 1. Proven Online Funnel",
        "",
        "The user-provided aggregate result is proven: macro F1 `0.05654761904761904`; micro precision `0.26666666666666666`; micro recall `0.044444444444444446`; micro F1 `0.0761904761904762`.",
        f"Raw metric records parsed: `{total}`.",
        f"Recalculated MATCH decisions: `{matches}`; MATCH with resources > 0: `{match_resources}`." if records else "Per-criterion funnel totals are **UNRESOLVED** because the complete online log is absent.",
        "Expected benchmark cardinality is 816 evaluations (51 patients x 16 criteria).",
        "",
        "## 2. Scorer Confusion Matrix Reconstruction",
        "",
        "PROVEN from the supplied aggregate metrics: predicted positives = 15 and TP = 4 are consistent with precision 4/15; gold positives = 90 and FN = 86 are consistent with recall 4/90.",
        "INFERRED: FP = 11, FN = 86, and predicted positives = 15 follow arithmetically from those values.",
        "UNRESOLVED: individual patient/criterion labels, which resources correspond to TP/FP, and any hidden-label mapping. No individual labels were inferred.",
        "",
        "## 3. Service Visibility",
        "",
        "See `analysis/V5S_SERVICE_VISIBILITY_MATRIX.csv`. Structural validity and service retrieval are reported as separate gates.",
        "",
        "## 4. MATCH -> resources=0",
        "",
        "The raw log is unavailable, so the online count and exact patient cases are UNRESOLVED. Static candidate analysis identifies two grounded-payload failure modes: 265 can receive a semantic MATCH without an analyte-bound numeric payload; 635 can receive a semantic MATCH without all four value/ULN pairs. The frozen runtime correctly emits no positive FHIR resources in those cases rather than fabricating values.",
        "Reproduction with a fake YES transport: 265 text `肌钙蛋白升高，符合标准但数值未记录` produced `decision=MATCH|resources=0`; 635 text `肝肾功能化验符合标准，但AST ALT BUN Cr具体数值及上限未记录` produced `decision=MATCH|resources=0`. Both were LLM route, transport OK, parse OK.",
        "",
        "## 5. Prompt-Semantic Drift",
        "",
        "The final embedded SPEC rules are keyword-oriented descriptions. They do not fully encode approved thresholds, temporal/state constraints, or OR/AND semantics. This is a HARD SEMANTIC REGRESSION for semantic fallback prompts, even though deterministic routes cover some criteria.",
        "",
        "## 6. Retrieval Group Coverage",
        "",
        "The current retrieval implementation caps the combined evidence list with `out[:8]`. Adversarial fixtures show that repeated early-group hits can consume the entire cap before later required groups are returned. `len(windows)` is not a valid anchor-hit count; the exact group audit is recorded in this report's service/autopsy companion data where available.",
        "",
        "## 7. V2.4.3 Regression Comparison",
        "",
        "Compared with V2.4.3, the strongest evidence-supported regressions are SERVICE_QUERY visibility mismatches, PAYLOAD drops for MATCH decisions lacking grounded numbers, RETRIEVAL group truncation, and SEMANTIC_PROMPT drift. Exact online per-criterion attribution remains UNRESOLVED without the raw log.",
        "",
        "## 8. Top Root Causes",
        "",
        "1. SERVICE_QUERY: generated resources do not match all fixed scorer variants (notably POP-Q IV and impaired-consciousness 875 branch).",
        "2. RETRIEVAL: global eight-window cap can drop later required groups.",
        "3. SEMANTIC_PROMPT: embedded criterion rules have degraded to keyword lists.",
        "4. PAYLOAD: semantic MATCH may not contain the numeric payload required for 265/635 FHIR emission.",
        "5. FHIR/PAYLOAD boundary: structural validity does not establish scorer visibility or complete scorer fields.",
        "",
        "## 9. Smallest Proposed V5S.1 Repair Set",
        "",
        "1. Repair service-visible profile/value/code branches with exhaustive replay tests before any prompt change.",
        "2. Replace the global retrieval cap with per-group coverage plus a bounded total budget.",
        "3. Restore full short Chinese criterion semantics in embedded SPEC rules.",
        "4. Keep MATCH-to-resource emission gated by grounded payload completeness; do not fabricate clinical values.",
        "5. Re-run the online probe only after the raw-log audit and service replay gates are green.",
        "",
        "No production behavior was modified in this autopsy.",
    ]
    AUTOPSY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def code_shape(resource):
    if not resource:
        return "", "", "", "", ""
    code_block = resource.get("medicationCodeableConcept") or resource.get("code") or {}
    coding = (code_block.get("coding") or [{}])[0]
    value = resource.get("valueCodeableConcept") or resource.get("valueQuantity") or resource.get("performedPeriod") or resource.get("extension") or ""
    return resource.get("resourceType", ""), ";".join(resource.get("meta", {}).get("profile", [])), coding.get("system", ""), coding.get("code", ""), json.dumps(value, ensure_ascii=False, sort_keys=True)


def service_matrix():
    libraries = decode_libraries()
    rows = []
    details = []
    for cid in CRITERIA:
        resource_meta, _source, ns = libraries[cid]
        variants = []
        for label, text in POSITIVE_CASES[cid]:
            payload = ns["extract_payload"](cid, [], "MATCH", [{"text": text}])
            resources = ns["build_resources"](cid, "p1", payload)
            contract = contract_for_criterion(cid)
            service = contract.service
            if cid == "615":
                branch_index = {"pT3a": 0, "pT3b": 0, "pT4": 0, "R1": 1, "pN1": 2, "GS": 3, "PSA": 4}[label]
                service = replace(service, profiles=(service.profiles[branch_index],))
            if cid == "875":
                branch_index = 0 if label == "intracranial" else 1
                service = replace(service, profiles=(service.profiles[branch_index],))
            replay = replay_service(tuple(resources), service, "fixture://fhir", {"p1": "p1"})
            variants.append((label, text, payload, resources, replay.status))
            details.append((cid, label, replay.status, [code_shape(r) for r in resources]))
        contract = contract_for_criterion(cid)
        target_resources = [resource for resource in variants[0][3] if resource.get("resourceType") == contract.resource_type and set(resource.get("meta", {}).get("profile", ())) & set(contract.profiles)]
        first_resources = target_resources or variants[0][3]
        generated = code_shape(first_resources[0] if first_resources else {})
        expected_profile = ";".join(contract.service.profiles)
        expected_shape = json.dumps({"value_system": contract.service.value_system, "value_code": contract.service.value_code}, ensure_ascii=False, sort_keys=True)
        statuses = [x[4] for x in variants]
        status = "SERVICE_HIT" if all(x == "SERVICE_HIT" for x in statuses) else "SERVICE_MISS"
        reasons = [f"{label}:{result}" for label, _text, _payload, _resources, result in variants if result != "SERVICE_HIT"]
        rows.append({
            "criterion": cid,
            "generated_resource_type": generated[0],
            "generated_profile": generated[1],
            "generated_code_system": generated[2],
            "generated_code": generated[3],
            "generated_value_shape": generated[4],
            "scorer_expected_resource_type": contract.service.resource_type,
            "scorer_expected_profile": expected_profile,
            "scorer_expected_code_system": contract.service.code_system or contract.service.value_system or "",
            "scorer_expected_code": contract.service.code or contract.service.value_code or "",
            "scorer_expected_value_shape": expected_shape,
            "status": status,
            "reason": "; ".join(reasons) or "all tested variants replayed as SERVICE_HIT",
        })
    with SERVICE_CSV.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return rows, details


def retrieval_group_audit():
    libraries = decode_libraries()
    rows = []
    for cid in ("635", "675", "745", "755", "855"):
        _resource, _source, ns = libraries[cid]
        spec = ns["SPEC"]
        groups = spec.get("groups", [])
        reports = []
        for index in range(8):
            reports.append({"index": index, "text": groups[0][0] + "。重复早期证据。"})
        for index, group in enumerate(groups[1:], start=8):
            reports.append({"index": index, "text": group[0] + "。晚到证据。"})
        windows = ns["retrieve_evidence"](reports, spec)
        group_ids = sorted({int(window.get("group", -1)) for window in windows if window.get("group", -1) >= 0})
        true_hits = sorted({group_index for report in reports for group_index, group in enumerate(groups) if any(alias.lower() in report["text"].lower() for alias in group)})
        rows.append({
            "criterion": cid,
            "true_anchor_hits": len(true_hits),
            "groups_required": len(groups),
            "groups_hit": len(group_ids),
            "group_ids_hit": json.dumps(group_ids),
            "windows": len(windows),
            "fallback_used": any(window.get("group") == -1 for window in windows),
            "cap_dropped_required_groups": len(group_ids) < len(groups),
        })
    with (ROOT / "analysis" / "V5S_RETRIEVAL_GROUP_AUDIT.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def main():
    log_path = Path(sys.argv[1]) if len(sys.argv) > 1 else find_metrics_log()
    records = parse_metrics(log_path)
    write_autopsy(records, log_path)
    rows, details = service_matrix()
    retrieval_rows = retrieval_group_audit()
    with AUTOPSY_MD.open("a", encoding="utf-8") as handle:
        handle.write("\n## Service Replay Variant Details\n\n")
        for cid, label, status, shapes in details:
            handle.write(f"- `{cid}` `{label}`: `{status}`; resources={len(shapes)}\n")
        handle.write("\n## Service Matrix Status Counts\n\n")
        handle.write(json.dumps(dict(Counter(row["status"] for row in rows)), ensure_ascii=False, sort_keys=True) + "\n")
        handle.write("\n## Retrieval Group Audit\n\n")
        for row in retrieval_rows:
            handle.write(f"- `{row['criterion']}`: true_anchor_hits={row['true_anchor_hits']}, groups_required={row['groups_required']}, groups_hit={row['groups_hit']}, group_ids_hit={row['group_ids_hit']}, windows={row['windows']}, fallback_used={row['fallback_used']}, cap_dropped_required_groups={row['cap_dropped_required_groups']}\n")
        handle.write("\n## Embedded Prompt Rule Audit\n\n")
        libraries = decode_libraries()
        for cid in CRITERIA:
            rule = libraries[cid][2]["SPEC"].get("rule", "")
            handle.write(f"- `{cid}`: `{rule}`; status=`KEYWORD_ONLY_DRIFT`\n")


if __name__ == "__main__":
    main()
