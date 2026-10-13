# V6 Patient Fact Engine Implementation Plan

1. Keep the fact store as plain dictionaries/lists and define stable evidence IDs.
2. Add deterministic extractors for labs, staging, procedures, treatments, diagnoses, symptoms, smoking, and status markers.
3. Add sentence-local negation, planned/performed/current/historical status, and explicit timestamps.
4. Add guarded cross-report fusion for facts and relations; unresolved links return `UNKNOWN`.
5. Add an optional grounded semantic residual parser with a strict JSON/evidence-substring validator.
6. Implement 4-6 criterion evaluators with the `MATCH/NO_MATCH/UNKNOWN` contract.
7. Reuse proven E/C/I scorer payload adapters; keep payload gates separate from clinical decisions.
8. Run synthetic and existing fixture regression, including missing-one, negated, planned, history-only, contradiction, complete/incomplete cross-report, and unrelated evidence cases.
9. Run admission-stability analysis and require `UNSAFE_RELAXATION=0`.
10. Only after approval, design an E fallback integration. Do not build a candidate in this phase.
