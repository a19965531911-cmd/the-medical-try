# V5S ONLINE AUTOPSY

Frozen candidate commit: `67d48f9`.
Metrics log: **MISSING**. No readable file containing `V5S_METRICS|` was found.

## 1. Proven Online Funnel

The user-provided aggregate result is proven: macro F1 `0.05654761904761904`; micro precision `0.26666666666666666`; micro recall `0.044444444444444446`; micro F1 `0.0761904761904762`.
Raw metric records parsed: `0`.
Per-criterion funnel totals are **UNRESOLVED** because the complete online log is absent.
Expected benchmark cardinality is 816 evaluations (51 patients x 16 criteria).

## 2. Scorer Confusion Matrix Reconstruction

PROVEN from the supplied aggregate metrics: predicted positives = 15 and TP = 4 are consistent with precision 4/15; gold positives = 90 and FN = 86 are consistent with recall 4/90.
INFERRED: FP = 11, FN = 86, and predicted positives = 15 follow arithmetically from those values.
UNRESOLVED: individual patient/criterion labels, which resources correspond to TP/FP, and any hidden-label mapping. No individual labels were inferred.

## 3. Service Visibility

See `analysis/V5S_SERVICE_VISIBILITY_MATRIX.csv`. Structural validity and service retrieval are reported as separate gates.

## 4. MATCH -> resources=0

The raw log is unavailable, so the online count and exact patient cases are UNRESOLVED. Static candidate analysis identifies two grounded-payload failure modes: 265 can receive a semantic MATCH without an analyte-bound numeric payload; 635 can receive a semantic MATCH without all four value/ULN pairs. The frozen runtime correctly emits no positive FHIR resources in those cases rather than fabricating values.
Reproduction with a fake YES transport: 265 text `肌钙蛋白升高，符合标准但数值未记录` produced `decision=MATCH|resources=0`; 635 text `肝肾功能化验符合标准，但AST ALT BUN Cr具体数值及上限未记录` produced `decision=MATCH|resources=0`. Both were LLM route, transport OK, parse OK.

## 5. Prompt-Semantic Drift

The final embedded SPEC rules are keyword-oriented descriptions. They do not fully encode approved thresholds, temporal/state constraints, or OR/AND semantics. This is a HARD SEMANTIC REGRESSION for semantic fallback prompts, even though deterministic routes cover some criteria.

## 6. Retrieval Group Coverage

The current retrieval implementation caps the combined evidence list with `out[:8]`. Adversarial fixtures show that repeated early-group hits can consume the entire cap before later required groups are returned. `len(windows)` is not a valid anchor-hit count; the exact group audit is recorded in this report's service/autopsy companion data where available.

## 7. V2.4.3 Regression Comparison

Compared with V2.4.3, the strongest evidence-supported regressions are SERVICE_QUERY visibility mismatches, PAYLOAD drops for MATCH decisions lacking grounded numbers, RETRIEVAL group truncation, and SEMANTIC_PROMPT drift. Exact online per-criterion attribution remains UNRESOLVED without the raw log.

## 8. Top Root Causes

1. SERVICE_QUERY: generated resources do not match all fixed scorer variants (notably POP-Q IV and impaired-consciousness 875 branch).
2. RETRIEVAL: global eight-window cap can drop later required groups.
3. SEMANTIC_PROMPT: embedded criterion rules have degraded to keyword lists.
4. PAYLOAD: semantic MATCH may not contain the numeric payload required for 265/635 FHIR emission.
5. FHIR/PAYLOAD boundary: structural validity does not establish scorer visibility or complete scorer fields.

## 9. Smallest Proposed V5S.1 Repair Set

1. Repair service-visible profile/value/code branches with exhaustive replay tests before any prompt change.
2. Replace the global retrieval cap with per-group coverage plus a bounded total budget.
3. Restore full short Chinese criterion semantics in embedded SPEC rules.
4. Keep MATCH-to-resource emission gated by grounded payload completeness; do not fabricate clinical values.
5. Re-run the online probe only after the raw-log audit and service replay gates are green.

No production behavior was modified in this autopsy.

## Service Replay Variant Details

- `485` `III`: `SERVICE_HIT`; resources=1
- `485` `IV`: `SERVICE_MISS`; resources=1
- `615` `pT3a`: `SERVICE_HIT`; resources=1
- `615` `pT3b`: `SERVICE_HIT`; resources=1
- `615` `pT4`: `SERVICE_HIT`; resources=1
- `615` `R1`: `SERVICE_HIT`; resources=1
- `615` `pN1`: `SERVICE_HIT`; resources=1
- `615` `GS`: `SERVICE_HIT`; resources=1
- `615` `PSA`: `SERVICE_HIT`; resources=1
- `265` `cTnI`: `SERVICE_HIT`; resources=1
- `265` `cTnT`: `SERVICE_HIT`; resources=1
- `635` `labs`: `SERVICE_HIT`; resources=4
- `675` `herpes zoster`: `SERVICE_HIT`; resources=1
- `735` `active disease`: `SERVICE_HIT`; resources=1
- `745` `postoperative ventilation`: `SERVICE_HIT`; resources=2
- `755` `24h ventilation`: `SERVICE_HIT`; resources=1
- `855` `renal hepatic labs`: `SERVICE_HIT`; resources=1
- `835` `coagulation`: `SERVICE_HIT`; resources=1
- `875` `intracranial`: `SERVICE_HIT`; resources=1
- `875` `consciousness`: `SERVICE_MISS`; resources=1
- `805` `current smoker`: `SERVICE_HIT`; resources=1
- `805` `recent quitter`: `SERVICE_HIT`; resources=1
- `565` `severe diarrhea`: `SERVICE_HIT`; resources=1
- `565` `severe constipation`: `SERVICE_HIT`; resources=1
- `555` `recent surgery`: `SERVICE_HIT`; resources=1
- `185` `first irinotecan`: `SERVICE_HIT`; resources=1
- `165` `completed outside chemotherapy`: `SERVICE_HIT`; resources=1

## Service Matrix Status Counts

{"SERVICE_HIT": 14, "SERVICE_MISS": 2}

## Retrieval Group Audit

- `635`: true_anchor_hits=4, groups_required=4, groups_hit=1, group_ids_hit=[0], windows=8, fallback_used=False, cap_dropped_required_groups=True
- `675`: true_anchor_hits=3, groups_required=3, groups_hit=1, group_ids_hit=[0], windows=8, fallback_used=False, cap_dropped_required_groups=True
- `745`: true_anchor_hits=2, groups_required=2, groups_hit=1, group_ids_hit=[0], windows=8, fallback_used=False, cap_dropped_required_groups=True
- `755`: true_anchor_hits=2, groups_required=2, groups_hit=1, group_ids_hit=[0], windows=8, fallback_used=False, cap_dropped_required_groups=True
- `855`: true_anchor_hits=4, groups_required=4, groups_hit=1, group_ids_hit=[0], windows=8, fallback_used=False, cap_dropped_required_groups=True

## Embedded Prompt Rule Audit

- `485`: `患者相关证据是否明确满足标准：POP-Q,盆腔器官脱垂`; status=`KEYWORD_ONLY_DRIFT`
- `615`: `患者相关证据是否明确满足标准：pT,R1,pN1,GS,Gleason,PSA`; status=`KEYWORD_ONLY_DRIFT`
- `265`: `患者相关证据是否明确满足标准：cTnI,cTnT,肌钙蛋白`; status=`KEYWORD_ONLY_DRIFT`
- `635`: `患者相关证据是否明确满足标准：AST,ALT,BUN,Cr,肌酐,尿素氮`; status=`KEYWORD_ONLY_DRIFT`
- `675`: `患者相关证据是否明确满足标准：年龄,带状疱疹,头面部`; status=`KEYWORD_ONLY_DRIFT`
- `735`: `患者相关证据是否明确满足标准：乙型肝炎,HIV,结核,结缔组织`; status=`KEYWORD_ONLY_DRIFT`
- `745`: `患者相关证据是否明确满足标准：手术,术后,机械通气,有创`; status=`KEYWORD_ONLY_DRIFT`
- `755`: `患者相关证据是否明确满足标准：机械通气,持续,小时,天`; status=`KEYWORD_ONLY_DRIFT`
- `855`: `患者相关证据是否明确满足标准：Scr,肌酐,BUN,ALT,AST`; status=`KEYWORD_ONLY_DRIFT`
- `835`: `患者相关证据是否明确满足标准：凝血,PT,APTT,INR`; status=`KEYWORD_ONLY_DRIFT`
- `875`: `患者相关证据是否明确满足标准：颅内高压,意识障碍,昏迷`; status=`KEYWORD_ONLY_DRIFT`
- `805`: `患者相关证据是否明确满足标准：吸烟,戒烟`; status=`KEYWORD_ONLY_DRIFT`
- `565`: `患者相关证据是否明确满足标准：腹泻,便秘,严重`; status=`KEYWORD_ONLY_DRIFT`
- `555`: `患者相关证据是否明确满足标准：手术,切除,个月前`; status=`KEYWORD_ONLY_DRIFT`
- `185`: `患者相关证据是否明确满足标准：伊立替康,irinotecan,CPT-11,首次,初次`; status=`KEYWORD_ONLY_DRIFT`
- `165`: `患者相关证据是否明确满足标准：化疗,外院,外部医院`; status=`KEYWORD_ONLY_DRIFT`
