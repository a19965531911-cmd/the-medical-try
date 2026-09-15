# Architecture History

This document records architecture evolution, not a reconstructed Git timeline. The historical versions were imported as sanitized snapshots after their development.

## V2.4.3

V2.4.3 is the retained legacy baseline. It used deterministic, rule-first matching and directly generated FHIR transaction resources. The design was compact and inspectable, but matching and FHIR construction were closely coupled and evidence was primarily evaluated report by report.

## V3.x

V3 introduced a guarded semantic rescue path. Model output had to satisfy a schema and preserve patient subject, negation, planning, uncertainty, and source-grounded evidence constraints. This improved the boundary around semantic inference but did not yet provide a patient-level evidence model.

Intermediate V2.5, V3.0, and V3.1 directories are not copied as full snapshots. Their distinct architectural contribution is represented by the small retained `src/v3_engine/` compatibility layer; other code was superseded or duplicated by V4.2.2.

## V4.0 through V4.2

V4 separated extraction from decision authority. `EvidenceLedger` collected criterion-specific evidence across reports, expressions described criterion logic, and `CriterionCompiler` made deterministic decisions. Semantic extraction returned atom states rather than a final eligibility label, while typed builders defined the FHIR construction boundary.

V4.0, V4.1, V4.2, and V4.2.1 are summarized rather than copied mechanically. V4.2.2 contains the latest pre-V4.3 form of the same source layout and is the retained representative implementation.

## V4.3

V4.3 research identified limits in report-centric retrieval, atom-bag evidence, global contradiction handling, and non-executable temporal metadata. The selected direction is a criterion-centric pipeline with:

- offline compilation of natural criteria into typed criterion IR;
- bounded criterion-aware retrieval across longitudinal reports;
- distinct clinical facts, events, relations, and episodes;
- three-valued deterministic constraint evaluation with decision traces;
- separate FHIR compilation and service-query validation;
- shadow evaluation against retained V2.4.3 and V4.2.2 behavior.

The full V4.3 runtime was not implemented in the historical material curated here. Its status is architecture research/design.
