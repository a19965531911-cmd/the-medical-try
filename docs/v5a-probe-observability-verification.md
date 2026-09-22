# V5A observability patch verification

Only the production generator metrics statements changed. The probe builder reads
the existing transportfix artifact, preserves the flattened engine verbatim, and
replaces the generator boot block. AST comparison verifies that evaluation and
FHIR return statements and all other definitions are unchanged.

Candidate: submission/a_test_message_bundle_v5a_probe_candidate.json

Size: 870832 bytes

SHA256: 5585d22d26302208488545722bca476a44091d3cc945a932af21b989fc4b110c

Transportfix source SHA256 remains:
3821c901e1a7b789203f158f2f42bd2cf8d70bb34b202c9cf09dbbea21afb833

Fresh verification:
- Full tests/v5 and tests/integration: 216 passed, 16 failed.
- Subsequently added artifact static audit and metrics tests: 46 passed.
- Decode, compile, security, expanded metrics, endpoint/model: 16/16 each.
- Metrics status/parse combinations: 45/45; no clinical content logged.
- Frozen V4 and previous candidates: unchanged.
- Tianchi: NOT SUBMITTED.

The 16 prediction/FHIR equality tests cannot reach prediction in the old artifact:
`z11_load_criterion_specs` raises `NameError: name 'CriterionSpec' is not defined`.
The flattened definition is `z1_CriterionSpec`, but the generated spec factory
uses the unqualified name. The builder's special criterion_specs source does not
declare the import needed for its name mapping. This predates the observability
patch and the identical engine prefix is preserved in the probe artifact.

The minimal next fix is a separate build-time binding correction, followed by
fresh embedded execution parity tests. It is deliberately not included because
this request allows metrics changes only.

OBSERVABILITY PATCH ONLY: YES

PREDICTION BEHAVIOR CHANGED: NO (engine and prediction statements unchanged;
successful runtime/FHIR equality remains unverified due to the existing error).

VERDICT: BLOCKED — cannot claim READY FOR ONLINE ENVIRONMENT PROBE.
