# V5 Official Runtime Audit

The official training criteria differ from the A-list target criteria; this report audits architecture only and does not relabel them.

Source: `CHIP2026_CP2_A_baseline_v2_4_3/data/train_set_message_bundle.json`

| criterion | id | architecture | endpoint | model | prompt | response | parser | aggregation | FHIR | retry | tolerant |
|---|---:|---|---|---|---|---|---|---|---|---|---:|
| 75 | TRAIN | LLM_PER_REPORT | http://127.0.0.1:1213/v1/chat/completions | local-model | SYSTEM_CRITERION_PLUS_REPORT | JSON_OBJECT | JSON | ANY_REPORT_POSITIVE | Procedure | NO_RETRY | true |
| 275 | TRAIN | LLM_PER_REPORT | http://127.0.0.1:1213/v1/chat/completions | local-model | SYSTEM_CRITERION_PLUS_REPORT | JSON_OBJECT | JSON | PER_REPORT_APPEND | Observation | RETRY_PRESENT | true |
| 395 | TRAIN | LLM_PER_REPORT | http://127.0.0.1:1213/v1/chat/completions | local-model | SYSTEM_CRITERION_PLUS_REPORT | JSON_OBJECT | JSON | ANY_REPORT_POSITIVE | Consent | NO_RETRY | true |
| 435 | TRAIN | DETERMINISTIC | NONE | NONE | REGEX_RULES | TEXT_LABEL | TEXT | ANY_REPORT_POSITIVE | Observation | NO_RETRY | true |
| 455 | TRAIN | LLM_PER_REPORT | http://127.0.0.1:1213/v1/chat/completions | local-model | SYSTEM_CRITERION_PLUS_REPORT | JSON_OBJECT | JSON | PER_REPORT_APPEND | Procedure | NO_RETRY | true |
| 535 | TRAIN | LLM_PER_REPORT | http://127.0.0.1:1213/v1/chat/completions | local-model | SYSTEM_CRITERION_PLUS_REPORT | JSON_OBJECT | JSON | PER_REPORT_APPEND | Bundle | NO_RETRY | true |
| 545 | TRAIN | LLM_PER_REPORT | http://127.0.0.1:1213/v1/chat/completions | NONE | SYSTEM_CRITERION_PLUS_REPORT | JSON_OBJECT | JSON | ANY_REPORT_POSITIVE | Bundle | NO_RETRY | true |
| 595 | TRAIN | LLM_PER_REPORT | http://127.0.0.1:1213/v1/chat/completions | local-model | SYSTEM_CRITERION_PLUS_REPORT | JSON_OBJECT | JSON | PER_REPORT_APPEND | Observation | NO_RETRY | true |
| 605 | TRAIN | LLM_PER_REPORT | http://127.0.0.1:1213/v1/chat/completions | NONE | SYSTEM_CRITERION_PLUS_REPORT | JSON_OBJECT | JSON | ANY_REPORT_POSITIVE | Procedure | NO_RETRY | true |
| 655 | TRAIN | LLM_PER_REPORT | http://127.0.0.1:1213/v1/chat/completions | local-model | SYSTEM_CRITERION_PLUS_REPORT | JSON_OBJECT | JSON | PER_REPORT_APPEND | Bundle | NO_RETRY | true |
| 665 | TRAIN | LLM_PER_REPORT | http://127.0.0.1:1213/v1/chat/completions | local-model | SYSTEM_CRITERION_PLUS_REPORT | JSON_OBJECT | JSON | ANY_REPORT_POSITIVE | Observation | NO_RETRY | true |
| 685 | TRAIN | LLM_PER_REPORT | http://127.0.0.1:1213/v1/chat/completions | local-model | SYSTEM_CRITERION_PLUS_REPORT | JSON_OBJECT | JSON | PER_REPORT_APPEND | Observation | NO_RETRY | true |
| 705 | TRAIN | LLM_PER_REPORT | http://127.0.0.1:1213/v1/chat/completions | local-model | SYSTEM_CRITERION_PLUS_REPORT | JSON_OBJECT | JSON | PER_REPORT_APPEND | Observation | NO_RETRY | true |
| 725 | TRAIN | LLM_PER_REPORT | http://127.0.0.1:1213/v1/chat/completions | local-model | SYSTEM_CRITERION_PLUS_REPORT | JSON_OBJECT | JSON | PER_REPORT_APPEND | Condition | NO_RETRY | true |
| 815 | TRAIN | LLM_PER_REPORT | http://127.0.0.1:1213/v1/chat/completions | local-model | SYSTEM_CRITERION_PLUS_REPORT | JSON_OBJECT | JSON | PER_REPORT_APPEND | Observation | NO_RETRY | true |
| 845 | TRAIN | LLM_PER_REPORT | http://127.0.0.1:1213/v1/chat/completions | local-model | SYSTEM_CRITERION_PLUS_REPORT | JSON_OBJECT | JSON | PER_REPORT_APPEND | Observation | NO_RETRY | true |

| criterion | status |
|---|---|
| 75 | audited |
| 275 | audited |
| 395 | audited |
| 435 | audited |
| 455 | audited |
| 535 | audited |
| 545 | audited |
| 595 | audited |
| 605 | audited |
| 655 | audited |
| 665 | audited |
| 685 | audited |
| 705 | audited |
| 725 | audited |
| 815 | audited |
| 845 | audited |
