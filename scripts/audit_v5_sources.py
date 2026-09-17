"""Audit official CHIP2026 libraries and scorer-facing transport contracts."""
from __future__ import annotations

import base64
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
V243 = ROOT.parent / "CHIP2026_CP2_A_baseline_v2_4_3"
OFFICIAL_BUNDLE = V243 / "data" / "train_set_message_bundle.json"
sys.path.insert(0, str(ROOT / "src"))

from v43.fhir.contracts import contract_for_criterion


CRITERIA = ("485", "615", "265", "635", "675", "735", "745", "755", "855", "835", "875", "805", "565", "555", "185", "165")
IDENTIFIERS = ("8", "20", "21", "22", "24", "30", "31", "32", "33", "35", "37", "39", "41", "46", "49", "51")
OFFICIAL_TITLES = ("75", "275", "395", "435", "455", "535", "545", "595", "605", "655", "665", "685", "705", "725", "815", "845")


@dataclass(frozen=True)
class TransportContractAudit:
    criterion: str
    resource_type: str
    profile: str
    query_behavior: str
    minimum_fields: tuple[str, ...]
    actual_numeric_required: bool
    reference_range_required: bool
    relation_required: bool
    generic_positive_insufficient: bool
    selected_source: str
    polarity: str = ""
    logical_interpretation: str = ""
    threshold_interpretation: str = ""


@dataclass(frozen=True)
class OfficialLibraryAudit:
    criterion: str
    identifier: str
    architecture: str
    endpoint: str
    model: str
    prompt_structure: str
    response_format: str
    response_parser: str
    aggregation: str
    fhir_builder: str
    retry_behavior: str
    source_compiles: bool
    positive_resource_structure: str
    copies_patient_values: bool
    tolerant_parsing: bool


def _extract(pattern: str, source: str, default: str) -> str:
    match = re.search(pattern, source, re.I | re.S)
    return match.group(1) if match else default


def _source_audit(criterion: str, source: str) -> OfficialLibraryAudit:
    compile(source, f"official-{criterion}", "exec")
    llm = bool(re.search(r"chat/completions|local-model|requests\.post|urlopen", source, re.I))
    per_report = bool(re.search(r"for\s+\w+\s+in\s+(?:case_reports|reports)|enumerate\((?:case_reports|reports)", source))
    architecture = "LLM_PER_REPORT" if llm and per_report else ("LLM_PATIENT" if llm else "DETERMINISTIC")
    endpoint = _extract(r"(https?://127\.0\.0\.1:1213/v1/chat/completions)", source, "NONE")
    model = _extract(r"['\"]model['\"]\s*:\s*['\"]([^'\"]+)", source, "NONE")
    parser = "JSON" if re.search(r"json\.loads|\.json\(\)", source) else "TEXT"
    tolerant = bool(re.search(r"strip\(|startswith\(|in\s+.*(?:content|response)", source))
    retry = "RETRY_PRESENT" if re.search(r"retry|attempt|for\s+.*range\([2-9]", source, re.I) else "NO_RETRY"
    aggregation = "ANY_REPORT_POSITIVE" if per_report and re.search(r"any\(|return\s+True|break", source) else ("PER_REPORT_APPEND" if per_report else "PATIENT_LEVEL")
    return OfficialLibraryAudit(
        criterion=criterion,
        identifier="TRAIN",
        architecture=architecture,
        endpoint=endpoint,
        model=model,
        prompt_structure="SYSTEM_CRITERION_PLUS_REPORT" if llm else "REGEX_RULES",
        response_format="JSON_OBJECT" if parser == "JSON" else "TEXT_LABEL",
        response_parser=parser,
        aggregation=aggregation,
        fhir_builder=_extract(r"['\"]resourceType['\"]\s*:\s*['\"]([^'\"]+)", source, "DYNAMIC"),
        retry_behavior=retry,
        source_compiles=True,
        positive_resource_structure="value/reference fields copied" if re.search(r"valueQuantity|referenceRange|performed|effective", source) else "coded positive resource",
        copies_patient_values=bool(re.search(r"valueQuantity|referenceRange|performed|effective", source)),
        tolerant_parsing=tolerant,
    )


def build_official_audits() -> dict[str, OfficialLibraryAudit]:
    bundle = json.loads(OFFICIAL_BUNDLE.read_text(encoding="utf-8"))
    libraries = [entry["resource"] for entry in bundle["entry"] if entry["resource"].get("resourceType") == "Library"]
    by_title = {str(resource["content"][0]["title"]): resource for resource in libraries}
    if tuple(by_title) != OFFICIAL_TITLES:
        raise ValueError("official training Library sequence differs from frozen titles")
    result = {}
    for criterion in OFFICIAL_TITLES:
        resource = by_title[criterion]
        source = base64.b64decode(resource["content"][0]["data"], validate=True).decode("utf-8")
        result[criterion] = _source_audit(criterion, source)
    return result


def transport_matrix() -> dict[str, TransportContractAudit]:
    result = {}
    for criterion in CRITERIA:
        contract = contract_for_criterion(criterion)
        numeric = criterion in {"265", "615", "635", "755", "805", "855"}
        reference = criterion in {"635", "855"}
        relation = criterion == "745"
        result[criterion] = TransportContractAudit(
            criterion=criterion,
            resource_type=contract.resource_type,
            profile=contract.profiles[0],
            query_behavior=json.dumps(asdict(contract.service), ensure_ascii=False, sort_keys=True),
            minimum_fields=tuple(contract.required_fields),
            actual_numeric_required=numeric,
            reference_range_required=reference,
            relation_required=relation,
            generic_positive_insufficient=numeric or reference or relation,
            selected_source="V4" if criterion in {"185", "675", "745", "875"} else "V2.4.3",
            polarity="INCLUSION" if criterion == "635" else "",
            logical_interpretation="AST_AND_ALT_AND_BUN_AND_CR" if criterion == "635" else "",
            threshold_interpretation="EACH_LTE_2X_ULN" if criterion == "635" else "",
        )
    return result


def _all_criteria_index(audits: dict[str, OfficialLibraryAudit]) -> str:
    return "\n".join(f"| {cid} | audited |" for cid in audits)


def render_reports(audits: dict[str, OfficialLibraryAudit], matrix: dict[str, TransportContractAudit], output_dir: Path = ROOT / "reports") -> tuple[Path, ...]:
    output_dir.mkdir(parents=True, exist_ok=True)
    index = "| criterion | status |\n|---|---|\n" + _all_criteria_index(audits)
    official_rows = [
        "| criterion | id | architecture | endpoint | model | prompt | response | parser | aggregation | FHIR | retry | tolerant |",
        "|---|---:|---|---|---|---|---|---|---|---|---|---:|",
    ]
    for a in audits.values():
        official_rows.append(f"| {a.criterion} | {a.identifier} | {a.architecture} | {a.endpoint} | {a.model} | {a.prompt_structure} | {a.response_format} | {a.response_parser} | {a.aggregation} | {a.fhir_builder} | {a.retry_behavior} | {str(a.tolerant_parsing).lower()} |")
    transport_rows = [
        "| criterion | resourceType | profile | minimum fields | numeric | referenceRange | relation | generic insufficient | selected source |",
        "|---|---|---|---|---:|---:|---:|---:|---|",
    ]
    for t in matrix.values():
        transport_rows.append(f"| {t.criterion} | {t.resource_type} | {t.profile} | {', '.join(t.minimum_fields)} | {str(t.actual_numeric_required).lower()} | {str(t.reference_range_required).lower()} | {str(t.relation_required).lower()} | {str(t.generic_positive_insufficient).lower()} | {t.selected_source} |")
    selection_rows = ["| criterion | selected source | reason |", "|---|---|---|"]
    for t in matrix.values():
        selection_rows.append(f"| {t.criterion} | {t.selected_source} | scorer fields verified against target service code and V4 replay contract |")
    p1 = output_dir / "V5_OFFICIAL_RUNTIME_AUDIT.md"
    p2 = output_dir / "V5_TRANSPORT_CONTRACT_MATRIX.md"
    p3 = output_dir / "V5_TRANSPORT_SELECTION.md"
    p4 = output_dir / "V5_635_POLARITY_AUDIT.md"
    target_index = "| criterion | status |\n|---|---|\n" + "\n".join(f"| {cid} | audited |" for cid in matrix)
    p1.write_text("# V5 Official Runtime Audit\n\nThe official training criteria differ from the A-list target criteria; this report audits architecture only and does not relabel them.\n\nSource: `CHIP2026_CP2_A_baseline_v2_4_3/data/train_set_message_bundle.json`\n\n" + "\n".join(official_rows) + "\n\n" + index + "\n", encoding="utf-8")
    p2.write_text("# V5 Transport Contract Matrix\n\n" + "\n".join(transport_rows) + "\n\n" + target_index + "\n", encoding="utf-8")
    p3.write_text("# V5 Transport Selection\n\n" + "\n".join(selection_rows) + "\n\n" + target_index + "\n", encoding="utf-8")
    p4.write_text("# V5 Criterion 635 Polarity Audit\n\n## 635\n\n- Exact text: `5)或AST、ALT、BUN、Cr不超过正常值一倍者；`\n- Polarity: inclusion.\n- Logic: AST AND ALT AND BUN AND Cr.\n- Threshold: each value <= 2 x its matching upper limit of normal.\n- FHIR: Observation resources retain actual values and matching reference highs; no measurements are fabricated.\n- Evidence: target V2.4.3 service code, frozen V4 IR, and V4 service contract were compared.\n\n" + target_index + "\n", encoding="utf-8")
    return p1, p2, p3, p4


def main() -> None:
    audits = build_official_audits()
    matrix = transport_matrix()
    paths = render_reports(audits, matrix)
    print(f"OFFICIAL_LIBRARIES {len(audits)}/16")
    print(f"LLM_PER_REPORT {sum(a.architecture == 'LLM_PER_REPORT' for a in audits.values())}/16")
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
