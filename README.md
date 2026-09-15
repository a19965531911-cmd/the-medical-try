# CHIP2026 CP2 Clinical Eligibility Engine

## Overview

This repository preserves sanitized research code for transforming Chinese clinical text into eligibility-criterion decisions, FHIR R4 resources, and service-query validation inputs.

The core pipeline evolved from rule-based matching toward criterion-aware evidence extraction and deterministic constraint execution:

`Chinese clinical text -> criterion matching -> typed FHIR R4 resources -> service-query validation`

## Competition Context

The project was developed for the CHIP2026 CP2 clinical NLP task. It is an independent research and competition project and does not imply endorsement by or partnership with the competition organizers.

Official competition datasets and generated submission artifacts are not included.

## Architecture Evolution

- **V2.4.3:** best proven legacy rule-based baseline, retained as a sanitized source snapshot.
- **V3.x:** introduced grounded semantic rescue with subject, negation, planning, uncertainty, and evidence checks.
- **V4.2.x:** introduced patient-level `EvidenceLedger`, criterion specifications, semantic atom extraction, deterministic compilation, and typed builder boundaries.
- **V4.3:** criterion-centric architecture research based on typed criterion IR, retrieval, fact/event/relation modeling, temporal reasoning, deterministic constraints, FHIR compilation, and service validation.

## V4.3 Architecture

```text
Natural Criterion
  -> Criterion IR
  -> Criterion-aware Retrieval
  -> Fact / Event / Relation
  -> Temporal / Episode Reasoning
  -> Constraint Executor
  -> FHIR Compiler
  -> Service Validation
```

V4.3 is represented by design documentation only; this repository does not claim that the full V4.3 runtime has been implemented.

## Repository Structure

```text
docs/                     Architecture, history, and release audit
examples/synthetic/       Synthetic-only demonstration input
legacy/v2_4_3/src/        Sanitized V2.4.3 rule-based snapshot
scripts/                  Metadata-only release auditing tool
src/v3_engine/            Grounded semantic safety layer
src/v4_engine/            V4.2 evidence and constraint components
tests/                    Synthetic-only unit tests
```

## Installation

Python 3.10 or newer is required.

```bash
python -m venv .venv
python -m pip install -r requirements-dev.txt
```

The retained runtime modules use the Python standard library. `pytest` is required only for tests.

## Testing

From the repository root:

```bash
python -m pytest -q
```

All repository tests use synthetic inputs and do not require competition datasets or network services.

## Data

Official competition datasets, official test inputs, patient records, and generated submission bundles are **not included**. The example under `examples/synthetic/` was written specifically for this repository and is marked synthetic.

## Privacy

This repository excludes patient-level clinical data. Historical files that might contain patient identifiers, full case text, or competition inputs were excluded rather than assumed to be anonymized.

## Status

Research and competition project. Historical snapshots were curated into Git after development; the Git history does not claim to reproduce the original development timeline.

## Disclaimer

For research and competition purposes only. Not for clinical decision-making.

## License

No open-source license has been selected. See [LICENSE_POLICY.md](LICENSE_POLICY.md).
