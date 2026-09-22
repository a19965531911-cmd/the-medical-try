# V5S.4 Pytest Environment Exception

Status: `pytest suite = NOT EXECUTABLE IN CURRENT CODEX ENVIRONMENT`

Checks performed on September 21, 2026:

- Codex Python runtime: Python 3.12.14.
- `python -m pytest --version`: unavailable in the Codex runtime.
- System `py.exe` resolves to Windows Store Python 3.13, but direct process creation failed in this environment.
- An existing historical dependency directory contains pytest files, but access is denied from the current sandbox and external read-only approval did not complete.
- No package was installed and no candidate was rebuilt.

Equivalent artifact-level verification was executed directly:

- JSON and Bundle shape: PASS.
- Base64/UTF-8 decode: `16/16`.
- Compile: `16/16`.
- Isolated exec: `16/16`.
- Frozen E parity: `15/15`.
- Candidate SHA/size: PASS.
- FHIR and service replay for the supported 485 III path: PASS.
- Security and unresolved-symbol scan: PASS.

This is an environment limitation, not evidence of candidate corruption.