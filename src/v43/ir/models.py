from dataclasses import dataclass
from typing import Any
from enum import Enum

class CriterionType(str, Enum):
    eligibility = "eligibility"
    exclusion = "exclusion"
    inclusion = "inclusion"


@dataclass(frozen=True)
class RetrievalPolicy:
    primary_aliases: tuple[str, ...]
    expanded_terms: tuple[str, ...]
    bm25_query: tuple[str, ...]
    fallback_enabled: bool
    fallback_k: int
    hard_gate: bool


@dataclass(frozen=True)
class FHIRContract:
    resource_type: str
    profiles: tuple[str, ...]
    required_fields: tuple[str, ...]
    optional_fields: tuple[str, ...]
    coding_systems: tuple[str, ...]
    coding_codes: tuple[str, ...]
    value_types: tuple[str, ...]
    raw: dict[str, Any]


@dataclass(frozen=True)
class ServiceQueryContract:
    queried_resource_type: str
    required_profile_match: bool | None
    query_parameters: tuple[str, ...]
    raw: dict[str, Any]


@dataclass(frozen=True)
class CriterionIR:
    criterion_id: str
    title: str
    original_text: str
    criterion_type: CriterionType
    clinical_domain: str
    retrieval_policy: RetrievalPolicy
    fhir_contract: FHIRContract
    service_query_contract: ServiceQueryContract
    temporal_scope: str
    raw: dict[str, Any]
