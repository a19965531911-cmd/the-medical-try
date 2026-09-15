from pathlib import Path
from typing import Iterable
import yaml

from .models import CriterionIR, FHIRContract, RetrievalPolicy, ServiceQueryContract
from .validation import validate_criterion_ir


def _tuple(value, default=()):
    if value is None:
        return tuple(default)
    if isinstance(value, str):
        return (value,)
    return tuple(value)


def _criterion(raw: dict) -> CriterionIR:
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
    contract = FHIRContract(str(fc.get("resource_type", "")), _tuple(fc.get("profiles") or fc.get("profile")), _tuple(fc.get("required_fields")), _tuple(fc.get("optional_fields")), _tuple(fc.get("coding_systems")), _tuple(fc.get("coding_codes")), _tuple(fc.get("value_types") or fc.get("value_type")), dict(fc))
    service = ServiceQueryContract(str(sc.get("queried_resource_type") or sc.get("query_resource") or ""), sc.get("required_profile_match"), _tuple(sc.get("query_parameters")), dict(sc))
    result = CriterionIR(str(raw["criterion_id"]), str(raw.get("title", "")), str(raw.get("original_text", "")), str(raw.get("criterion_type", "")), str(raw.get("clinical_domain", "")), policy, contract, service, str(raw.get("temporal_scope", "")), dict(raw))
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
