from .models import CriterionIR


def validate_criterion_ir(ir: CriterionIR) -> None:
    if not ir.criterion_id:
        raise ValueError("criterion_id is required")
    if not ir.retrieval_policy.primary_aliases:
        raise ValueError("retrieval_policy.primary_aliases is required")
    if not ir.fhir_contract.resource_type:
        raise ValueError("FHIR_contract.resource_type is required")
    if not ir.service_query_contract.queried_resource_type:
        raise ValueError("service_query_contract.queried_resource_type is required")
