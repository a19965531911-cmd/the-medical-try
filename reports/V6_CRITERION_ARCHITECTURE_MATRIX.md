# V6 Criterion Architecture Matrix

This is an offline architecture ranking, not a correctness or leaderboard claim.

| criterion | required facts | current E bottleneck | cross-report benefit | relation benefit | temporal benefit | semantic extraction benefit | safe scorer payload | G-style over-admission risk | V6 category | recommended for MVP |
|---|---|---|---|---|---|---|---|---|---|---|
| 745 | performed surgery + performed invasive ventilation + postoperative relation | relation can be split across reports | high | high | high | residual relation only | proven two-Procedure contract | high; UNKNOWN required | GAIN_LIKELY | YES |
| 165 | performed chemotherapy + explicit outside-hospital relation | relation/context fragmentation | medium | high | medium | useful for residual relation | existing Procedure contract | medium | GAIN_LIKELY | YES |
| 185 | irinotecan + explicit first use | first-use wording may be distant | medium | medium | high | useful for explicit status only | existing treatment contract | medium | GAIN_POSSIBLE | YES |
| 675 | age >=50 + zoster + head/face site | evidence groups may be separated | high | medium | medium | residual diagnosis/site binding | existing Condition contract | high; 2/3 is UNKNOWN | GAIN_POSSIBLE | YES |
| 735 | listed disease + active state | history/current wording separation | medium | medium | high | residual activity state | existing Condition contract | high; history is not active | GAIN_POSSIBLE | YES |
| 565 | diarrhea/constipation + explicit severity | generic symptom text lacks severity | low | low | medium | severity phrase extraction | existing severity extension | medium | GAIN_POSSIBLE | YES |
| 855 | four labs + thresholds | payload completeness, not safe admission expansion | medium | low | medium | numeric extraction only | proven four Observation contract | very high | RISKY | NO |
| 635 | four labs + explicit reference highs | scorer contract and polarity already constrained | medium | low | medium | numeric extraction only | proven four Observation contract | very high | RISKY | NO |
| 485 | prolapse + stage III/IV bound | lexical aliases, not patient fusion | low | low | low | limited | existing Observation contract | high | NEUTRAL | NO |
| 615 | one satisfying oncology branch | mostly branch-specific parsing | low | low | medium | limited | existing branch contract | medium | NEUTRAL | NO |
| 755 | ventilation duration >=24h | duration/payload representation | low | low | high | limited | legacy period contract | medium | NEUTRAL | NO |
| 805 | current/former smoking + duration | status and duration payload | low | low | medium | limited | legacy two-resource contract | medium | NEUTRAL | NO |
| 835 | explicit coagulation abnormality | mostly direct extraction | low | low | low | limited | existing Observation contract | medium | NEUTRAL | NO |
| 555 | completed surgery + date window | time/source may be split | medium | low | high | useful for explicit date only | existing Procedure contract | low | GAIN_POSSIBLE | NO |
| 875 | intracranial hypertension OR impaired consciousness | context disambiguation | low | medium | medium | residual context | existing branch contract | medium | GAIN_POSSIBLE | NO |

MVP selection is deliberately conservative: `555, 565, 675, 735, 745`. These five criteria benefit from time/status/relation completeness while retaining explicit admission thresholds. The gate requires at least four criteria with evidence gain, zero unsafe relaxation, and reusable payloads before production work.
