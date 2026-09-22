# V5S implementation plan

1. Audit official train shell, V2.4.3 Libraries, and V5A probe-fixed Libraries. Record endpoint/model, aggregation, prompts, retrieval, FHIR shape, retries, and the 675/875/555/165 visibility comparison in `reports/`.
2. Freeze written interpretations for 635 and 855 in dedicated audit reports.
3. Add RED tests for sentence/window retrieval at beginning, late offsets, report boundaries, cross-report coverage, and no-anchor fallback.
4. Implement `src/v5s/runtime_template.py` with plain-function retrieval, parser, bounded local transport, criterion rules, payload extraction, proven FHIR adapter, and metrics. Add criterion literals in `criterion_data.py`.
5. Add RED rule tests, then implement 265, 485, 615, 755, 805, 555, 635, and 855 rules with explicit local numeric binding and no fabricated values.
6. Add RED prompt/parser and semantic fixture tests, then implement the short Chinese YES/NO prompt, parser tolerance, one-call transport, and minimal guards. Reach at least 96 fixture cases.
7. Build `scripts/build_v5s_submission.py` from the single template plus safe literals, preserving the A16 shell and never flattening modules.
8. Add decoded artifact tests for compile, exec, symbol audit, complexity, security, 32 runtime calls, FHIR structure, and service replay.
9. Run all V5S tests, rebuild the single candidate, perform fresh decode/compile/exec/security/size/SHA256 verification, and report READY or BLOCKED with evidence.

Self-review: no placeholders or TBD markers; all 16 criteria and hard gates are named; the plan does not alter V4/V5A files; production and development share the template source; model endpoint and shell are preserved; online submission is excluded.
