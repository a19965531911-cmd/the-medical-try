# V4.3 Criterion-Centric Architecture

## Objective

V4.3 reframes clinical eligibility matching around the meaning of each criterion rather than a global keyword registry or final model-generated label. Retrieval gathers bounded evidence; deterministic constraints retain final decision authority.

## Pipeline

```text
Natural Criterion
  -> Criterion IR
  -> Criterion-aware Retrieval
  -> Clinical Facts / Events / Relations
  -> Temporal and Episode Reconciliation
  -> Three-valued Constraint Executor
  -> FHIR Compiler
  -> Service-query Validation
```

## Criterion IR

Each fixed criterion is compiled offline into a typed representation containing definitions, concept aliases, value and unit rules, subject constraints, temporal scope, relation requirements, FHIR output contracts, and independent scorer-query contracts. Runtime components consume this shared representation instead of maintaining separate keyword registries.

## Retrieval

Retrieval ranks evidence but never decides eligibility. Reviewed lexical aliases form the first tier, BM25-like ranking over patient spans forms the second, and a bounded high-information fallback prevents missing aliases from becoming a hard recall gate. Evidence packets retain report, span, tier, score, and timestamp provenance.

## Clinical Model

- `ClinicalFact` represents demographics, measurements, and simple assertions.
- `ClinicalEvent` represents occurrences such as surgery or medication administration.
- `ClinicalRelation` links facts and events using typed relations.
- `ClinicalEpisode` is a lightweight reconciliation container rather than a second source of truth.

Qualifiers belong to their event. Conflict is a reconciliation result over comparable observations, not a raw extraction state.

## Constraint Execution

Every leaf and Boolean node evaluates to `TRUE`, `FALSE`, or `UNKNOWN`. The root maps these values to `SATISFIED`, `NOT_SATISFIED`, or `INSUFFICIENT_EVIDENCE`. Conservative three-valued logic distinguishes missing evidence from proven absence, and every node emits a decision trace with supporting, blocking, and unknown object identifiers.

Relation constraints are explicit. For example, surgery and invasive ventilation must be linked to the same postoperative episode; patient-level co-occurrence is insufficient.

## FHIR and Service Validation

Criterion evaluation and FHIR compilation are separate stages. A FHIR contract controls resource generation, while an independent service-query contract checks scorer parameters, coding paths, references, identity handling, and JSON assumptions. Decision success, structural validity, and service hits are recorded separately.

## Migration Strategy

The design proposed an initial four-criterion MVP, followed by shadow comparison with V2.4.3 and V4.2.2 and then domain-by-domain expansion. The architecture documentation is retained here as research; implementation status must not be inferred from this design.
