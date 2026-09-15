from pathlib import Path
import pytest
import yaml

from v43.ir.loader import load_criterion_ir
from v43.references import frozen_reference_paths


def test_loads_four_mvp_criteria_with_typed_contracts():
    items = load_criterion_ir(frozen_reference_paths()["criterion_ir_draft"], ("185", "675", "745", "875"))
    assert tuple(items) == ("185", "675", "745", "875")
    assert all(item.fhir_contract.resource_type for item in items.values())
    assert all(item.service_query_contract.queried_resource_type for item in items.values())
    assert all(item.retrieval_policy.hard_gate is False for item in items.values())
    assert items["875"].temporal_scope == "REVIEW_REQUIRED"


def test_rejects_wrong_schema_version(tmp_path: Path):
    source = yaml.safe_load(frozen_reference_paths()["criterion_ir_draft"].read_text(encoding="utf-8"))
    source["criterion_ir_schema_version"] = "v4.2"
    path = tmp_path / "bad.yaml"
    path.write_text(yaml.safe_dump(source, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ValueError, match="schema version"):
        load_criterion_ir(path, ("185",))


def test_requires_contracts_and_retrieval_policy(tmp_path: Path):
    source = yaml.safe_load(frozen_reference_paths()["criterion_ir_draft"].read_text(encoding="utf-8"))
    source["criteria"][0].pop("FHIR_contract")
    path = tmp_path / "bad.yaml"
    path.write_text(yaml.safe_dump(source, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ValueError, match="FHIR_contract"):
        load_criterion_ir(path, ("165",))

    source["criteria"][0]["FHIR_contract"] = {"resource_type": "X"}
    source["criteria"][0].pop("retrieval_policy")
    path.write_text(yaml.safe_dump(source, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ValueError, match="retrieval_policy"):
        load_criterion_ir(path, ("165",))


@pytest.mark.parametrize("section", [
    "constraint_semantics", "entities", "numeric_constraints", "temporal_constraints",
    "subject_constraints", "fact_schema", "event_schema", "relation_schema",
    "episode_policy", "logical_expression",
])
def test_rejects_missing_required_ir_sections(tmp_path: Path, section: str):
    source = yaml.safe_load(frozen_reference_paths()["criterion_ir_draft"].read_text(encoding="utf-8"))
    criterion = next(item for item in source["criteria"] if item["criterion_id"] == "185")
    criterion.pop(section)
    path = tmp_path / "bad.yaml"
    path.write_text(yaml.safe_dump(source, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ValueError, match=section):
        load_criterion_ir(path, ("185",))


def test_converts_enums_and_rejects_invalid_values(tmp_path: Path):
    items = load_criterion_ir(frozen_reference_paths()["criterion_ir_draft"], ("185",))
    assert items["185"].criterion_type.value == "eligibility"

    source = yaml.safe_load(frozen_reference_paths()["criterion_ir_draft"].read_text(encoding="utf-8"))
    criterion = next(item for item in source["criteria"] if item["criterion_id"] == "185")
    criterion["criterion_type"] = "maybe"
    path = tmp_path / "bad.yaml"
    path.write_text(yaml.safe_dump(source, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ValueError, match="criterion_type"):
        load_criterion_ir(path, ("185",))


def test_rejects_incomplete_contract_fields(tmp_path: Path):
    source = yaml.safe_load(frozen_reference_paths()["criterion_ir_draft"].read_text(encoding="utf-8"))
    criterion = next(item for item in source["criteria"] if item["criterion_id"] == "185")
    criterion["FHIR_contract"].pop("profiles")
    path = tmp_path / "bad.yaml"
    path.write_text(yaml.safe_dump(source, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ValueError, match="FHIR_contract.profiles"):
        load_criterion_ir(path, ("185",))

    criterion["FHIR_contract"]["profiles"] = ["restored"]
    criterion["service_query_contract"].pop("coding_paths")
    path.write_text(yaml.safe_dump(source, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ValueError, match="service_query_contract.coding_paths"):
        load_criterion_ir(path, ("185",))
