from pathlib import Path
from typing import Iterable
import yaml

from .models import CriterionIR, FHIRContract, RetrievalPolicy, ServiceQueryContract, CriterionType
from .validation import validate_criterion_ir


def _tuple(value, default=()):
    if value is None:
        return tuple(default)
    if isinstance(value, str):
        return (value,)
    return tuple(value)


def _criterion(raw: dict) -> CriterionIR:
    required = ("constraint_semantics", "entities", "numeric_constraints", "temporal_constraints", "subject_constraints", "fact_schema", "event_schema", "relation_schema", "episode_policy", "logical_expression")
    for key in required:
        if key not in raw:
            raise ValueError(f"missing {key}")
    rp = raw.get("retrieval_policy")
    if not rp:
        raise ValueError(f"criterion {raw.get('criterion_id')} missing retrieval_policy")
    fc = raw.get("FHIR_contract")
    if not fc:
        raise ValueError(f"criterion {raw.get('criterion_id')} missing FHIR_contract")
    sc = raw.get("service_query_contract")
    if not sc:
        raise ValueError(f"criterion {raw.get('criterion_id')} missing service_query_contract")
    fallback = rp.get("fallback") or {}
    policy = RetrievalPolicy(_tuple(rp.get("primary_aliases")), _tuple(rp.get("expanded_terms")), _tuple(rp.get("bm25_query")), bool(fallback.get("enabled", True)), int(fallback.get("k", 3)), bool(rp.get("hard_gate", False)))
    profiles = _tuple(fc.get("profiles") or fc.get("profile"))
    if not profiles: raise ValueError("FHIR_contract.profiles is required")
    for key in ("required_fields", "coding_systems", "coding_codes", "value_types", "cardinality"):
        if key not in fc and not (key == "value_types" and "value_type" in fc): raise ValueError(f"FHIR_contract.{key} is required")
    contract = FHIRContract(str(fc.get("resource_type", "")), profiles, _tuple(fc.get("required_fields")), _tuple(fc.get("optional_fields")), _tuple(fc.get("coding_systems")), _tuple(fc.get("coding_codes")), _tuple(fc.get("value_types") or fc.get("value_type")), dict(fc))
    if "coding_paths" not in sc and "query_resource" not in sc: raise ValueError("service_query_contract.coding_paths is required")
    service = ServiceQueryContract(str(sc.get("queried_resource_type") or sc.get("query_resource") or ""), sc.get("required_profile_match"), _tuple(sc.get("query_parameters")), dict(sc))
    try: ctype = CriterionType(raw.get("criterion_type"))
    except ValueError as exc: raise ValueError("criterion_type invalid") from exc
    result = CriterionIR(str(raw["criterion_id"]), str(raw.get("title", "")), str(raw.get("original_text", "")), ctype, str(raw.get("clinical_domain", "")), policy, contract, service, str(raw.get("temporal_scope", "")), dict(raw))
    validate_criterion_ir(result)
    return result


def load_criterion_ir(path: str | Path, ids: Iterable[str]) -> dict[str, CriterionIR]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if data.get("criterion_ir_schema_version") != "v4.3-draft2":
        raise ValueError("unsupported schema version")
    wanted = tuple(str(i) for i in ids)
    by_id = {str(item.get("criterion_id")): item for item in data.get("criteria", [])}
    missing = [i for i in wanted if i not in by_id]
    if missing:
        raise ValueError(f"missing criterion IDs: {missing}")
    return {i: _criterion(by_id[i]) for i in wanted}
