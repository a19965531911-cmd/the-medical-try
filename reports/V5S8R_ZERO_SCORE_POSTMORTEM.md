# EXPERIMENT L ZERO-SCORE POSTMORTEM

## Result

**EXPERIMENT L ZERO-SCORE UNRESOLVED**

Reported online score: `0.0000`.

The local frozen artifact passes artifact, import, constructor, public-entrypoint, JSON, Bundle, and deterministic 675 control-flow checks. No local evidence identifies a runtime exception, invalid no-match return, serializer corruption, ordering change, resource-path change, or fallback change outside the intended 675 overlay.

## Artifact identity

- Candidate: `submission/a_test_message_bundle_v5s8_expl_675_precision_guard_candidate.json`
- Size: `706091` bytes
- SHA256: `8878029301445486e19df9b7db66927fcfb952d8ac952833e3e7c1a32d2c8e15`
- Local identity: PASS
- Current HEAD: `88e72cfc1f3a903c7de8ab87c0c041d71ae56ab4`
- Current branch: `codex/v5s3-expg-criterion-recall-main-based`
- Candidate tracked by current Git HEAD: NO; it is an existing untracked workspace artifact
- Server-side uploaded file identity and submission mapping: UNVERIFIED

The local hash proves only the workspace file. It does not prove that the file selected by the online submission UI was this exact byte sequence.

## Differential evidence

The exact frozen E reference is Git commit `6639cf7`, SHA256 `40457de3149c7db34daf9c3545199c7c8f409ec65b6ae4412f6ca6a77df6d96e`. Parsed E and L shells have the same message type, 17 entries, one MessageHeader, 16 Libraries, and identical Library ordering. MessageHeader, Library metadata, security fields, and URLs are unchanged. Embedded source is byte-identical for 15/16 Libraries; only 675 differs and contains the L overlay.

Evidence file: `analysis/V5S8R_E_L_ARTIFACT_DIFF.json`.

## Runtime chain

`artifact bytes -> Bundle shell -> base64 decode -> Python import -> class definition -> constructor -> public entrypoint -> transaction Bundle`

Fresh-process evidence is in `analysis/V5S8R_LIBRARY_RUNTIME_MATRIX.json`:

- E: 16/16 import, constructor, entrypoint, and Bundle-contract passes
- L: 16/16 import, constructor, entrypoint, and Bundle-contract passes
- L/675 control cases: 5/5 pass, including complete positive and all tested rejection controls

The public signature remains `(self, patient_id, case_reports, ai_algorithm_type='nlp')`. No external model or network service was used in this postmortem.

## Root-cause classification

- A runtime exception: **not proven; local fresh-process gate passes**
- B invalid no-match return: **not proven; rejection path is a valid transaction Bundle**
- C artifact serialization delta: **not supported; only intended 675 embedded source differs**
- D compatibility failure: **not proven; all embedded sources parse/import under the available Python runtime**
- E wrong upload/submission identity: **plausible but unproven; server-side identity is unavailable**
- F local runtime pass, platform failure unresolved: **current classification**
- G other proven cause: **none**

This is not classified as a clinical-strategy failure because local replay shows the intended strict 675 behavior and retained payload parity; the online zero cannot be attributed to clinical quality from the available evidence.

## Structural and packaging checks

- MessageHeader: PASS; unchanged from exact E reference
- Libraries: PASS; 16, unchanged order
- FHIR Bundle shell: PASS; message Bundle with 17 entries
- Base64/UTF-8/compile: PASS for all 16 embedded sources
- JSON serializability and transaction Bundle return: PASS in fresh processes
- Security fields and URL metadata: unchanged
- Unresolved-symbol scan: `0` in the prior deterministic artifact audit
- Candidate/runtime mismatch: local candidate decodes to the audited L source; server-side mapping remains unknown

## Final verdict

`NOT_READY`

This verdict means the reported zero-score incident is not locally explained well enough to justify another blind online probe. It does not mean the local L artifact is proven invalid.

## Minimal next action

Obtain or record the online platform's selected filename/hash and execution/error status for the zero-score submission, then compare it to `V5S8R_SUBMISSION_IDENTITY.json` before any resubmission.
