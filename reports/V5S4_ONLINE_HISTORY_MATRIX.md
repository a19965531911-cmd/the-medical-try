# V5S.4 Online History Matrix

| Version | Macro P | Macro R | Macro F1 | Micro P | Micro R | Micro F1 | Runtime pattern | Transport | Decision architecture |
|---|---:|---:|---:|---:|---:|---:|---|---|---|
| V2.4.3 | unresolved | unresolved | 0.14375 | unresolved | unresolved | unresolved | legacy scorer-visible resources | legacy FHIR transport | deterministic/legacy |
| V4.2.1 | unresolved | unresolved | 0.13313 | 1.0 | unresolved | unresolved | high precision, low recall | legacy transport | conservative |
| Experiment E | 0.21875 | 0.140625 | 0.16666666666666666 | 0.75 | 0.06666666666666667 | 0.12244897959183675 | champion baseline | preserved legacy transport | aggressive but payload-gated |
| Experiment F | unresolved | unresolved | 0.1500 | unresolved | unresolved | unresolved | rejected 755 additions | changed resource recovery | rejected |
| Experiment G | 0.15625 | 0.078125 | 0.10416666666666666 | 0.5714285714285714 | 0.044444444444444446 | 0.08247422680412372 | resource-zero and broad semantic drift | G overlay | rejected |

Individual hidden patient labels are not inferred.
