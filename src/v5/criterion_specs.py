from functools import lru_cache
import json

from v43.fhir.contracts import contract_for_criterion
from v43.ir.loader import load_criterion_ir
from v43.references import CRITERION_IDS as _V43_IDS, frozen_reference_paths

from .models import CriterionSpec


CRITERION_IDS = tuple(_V43_IDS)


@lru_cache(maxsize=1)
def load_criterion_specs() -> dict[str, CriterionSpec]:
    reviewed = load_criterion_ir(frozen_reference_paths()["criterion_ir_draft"], CRITERION_IDS)
    result = {}
    for criterion in CRITERION_IDS:
        ir = reviewed[criterion]
        raw = ir.raw
        retrieval = raw["retrieval_policy"]
        aliases = tuple(dict.fromkeys((
            *retrieval.get("primary_aliases", ()),
            *retrieval.get("expanded_terms", ()),
            *retrieval.get("bm25_query", ()),
        )))
        semantics = raw["constraint_semantics"]
        positive = tuple(str(item) for item in raw.get("required_facts", ())) or (str(raw["logical_expression"]),)
        blockers = tuple(str(item) for item in raw.get("prohibited_facts", ()))
        thresholds = tuple(json.dumps(item, ensure_ascii=False, sort_keys=True) for item in raw.get("numeric_constraints", ()))
        temporal = "EVER_PRESENT" if criterion == "875" else str(raw.get("temporal_scope", "documented"))
        contract = contract_for_criterion(criterion)
        result[criterion] = CriterionSpec(
            criterion_id=criterion,
            original_text=ir.original_text,
            plain_summary=ir.title,
            positive_conditions=positive + (str(raw["logical_expression"]),),
            blocking_conditions=blockers + tuple(str(x) for x in semantics.get("blocking_if_present", ())),
            transport_requirements=tuple(contract.required_fields),
            aliases=aliases,
            thresholds=thresholds,
            temporal_requirement=temporal,
            polarity=ir.criterion_type.value,
        )
    return result
