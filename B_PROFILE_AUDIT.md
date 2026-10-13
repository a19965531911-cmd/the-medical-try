# B Profile Audit

## Provenance and Pipeline

A_CHAMPION = Experiment E (V5S.2); reported online macro F1 0.16666666666666666.
B_CANDIDATE = b1-evidence; no B leaderboard validation.

Builder -> message Bundle -> Library base64 Python -> E normalization/retrieval -> B atoms/state -> deterministic constraints -> structured semantic rescue for unknown categorical facts -> grounded FHIR transaction -> official service.

E fallback = localhost:1213 local-model, errors return NO. B retains endpoint, increases response budget from 32 to 1024 for JSON facts. No real model was used in offline verification.

All B profile IDs are absent from E's actual executable libraries. None would automatically use a B-specific generic semantic route. No E-to-B patient predictions can be compared without adding B routes first.

## Criterion Matrix

|profile_id|criterion|required_facts|boolean_logic|temporal_logic|negation_logic|numeric_logic|current_handler|official_FHIR_behavior|risk|proposed_change|confidence|
|---|---|---|---|---|---|---|---|---|---|---|---|
|2|有呼吸系统的症状如咳嗽、胸闷、气短等|respiratory|OR within atom|current evidence|local state; unknown not positive|none|E: missing B route|Service OR over four respiratory codes; NLP also maps chest pain to chest tightness and restricts topics. Candidate excludes isolated chest pain and supports symptom paraphrases.|MEDIUM|ADD_RULE / B-only adaptation|medium; no real labels|
|3|接受根治性（R0）手术切除且病理证实为肝细胞癌患者；|hcc, pathology, resection, r0|AND|history/event|local state; unknown not positive|none|E: missing B route|Service intersects HCC Condition profile with Procedure outcome R0. NLP requires pathology-topic R0 and separate surgical record. Candidate composes grounded HCC, pathology, completed resection and R0 across records.|HIGH|ADD_RULE / B-only adaptation|medium; no real labels|
|85| 3. 择期行胸腔镜肺切除术；|elective, thoracoscopy, lung_resection|AND|planned or completed elective|local state; unknown not positive|none|E: missing B route|Service planned status filter commented out. FSH/NLP use completed surgery; service checks pulmonary-lobectomy, elective, thoracoscopic. Candidate admits planned or completed elective surgery, preserves FHIR preparation status for plans.|HIGH|ADD_RULE / B-only adaptation|medium; no real labels|
|205|1. 择期全麻下胸部手术的病人|elective, thoracic_surgery, general_anesthesia|AND|planned or completed elective|local state; unknown not positive|none|E: missing B route|Service checks thoracic code and GA method/depth; neither elective nor planned status enforced. Candidate requires explicit elective/planned evidence, supports cross-record GA.|HIGH|ADD_RULE / B-only adaptation|medium; no real labels|
|225| 8.接受放疗的患者。|radiotherapy|atomic|history/event|local state; unknown not positive|none|E: missing B route|Service profile only; FSH fixes completed status. Candidate excludes plans but preserves in-progress for ongoing radiotherapy. Full FSH conformity for ongoing cases remains unresolved.|MEDIUM|ADD_RULE / B-only adaptation|medium; no real labels|
|255|1.符合1999年WHO制定的2型糖尿病诊断标准；|t2dm|atomic|current evidence|local state; unknown not positive|none|E: missing B route|Service Condition profile only. FSH permits E11, does not require literal WHO1999 or lab values for existing diagnosis; NLP demands glucose/symptom evidence. Candidate accepts explicit T2DM without inventing glucose observations.|MEDIUM|ADD_RULE / B-only adaptation|medium; no real labels|
|295| 3)既往三个月内每天吸烟大于5支，或不能保证试验期间停止吸烟者；|smoking_eligible|OR within atom|recent/current|local state; unknown not positive|>5/day|E: missing B route|Service start within 90 days AND (daily cigarettes >5 OR cannot-guarantee). FSH requires both components, but OR often supports only one. Candidate emits only evidenced components; full FSH conformity unresolved. Record timestamp is observation time, not smoking start.|HIGH|ADD_RULE / B-only adaptation|medium; no real labels|
|465| 3.      肾活检提示为原发性膜性肾病、ANCA相关血管炎、狼疮性肾炎、IgA肾病等自身免疫相关的肾病。|renal_biopsy, autoimmune_renal|AND|current evidence|local state; unknown not positive|none|E: missing B route|Service renal biopsy Procedure AND autoimmune Condition same subject. FSH explicitly extends disease list far beyond initial examples. Candidate covers selected explicit FSH diseases, requires biopsy and grounded diagnosis.|HIGH|ADD_RULE / B-only adaptation|medium; no real labels|
|475| 2.符合脊柱源性慢性疼痛诊断标准：疼痛引起原因为脊柱病变，疼痛持续时间≥3个月。|pain, spinal_cause, pain_relation, duration|AND|current evidence|local state; unknown not positive|>=3 months|E: missing B route|Service requires spinal cause extension and more_than_3_months; FSH label explicitly >=3. Candidate requires linked spinal pain plus >=3 months; unrelated causality cannot complete atom.|HIGH|ADD_RULE / B-only adaptation|medium; no real labels|
|495|1) 病理诊断符合弥漫大B细胞淋巴瘤；|dlbcl, pathology|AND|current evidence|local state; unknown not positive|none|E: missing B route|Service accepts C83.3 OR 9680/3 in Observation value. Candidate requires pathology and DLBCL, adds method and correct value code.|MEDIUM|ADD_RULE / B-only adaptation|medium; no real labels|
|525|1.术前诊断中下段食管癌|esophageal, middle_lower, preoperative|AND|preoperative|local state; unknown not positive|none|E: missing B route|Service profile only. FSH accepts C15.2/C15.5 (middle/lower Chinese labels conflict with conventional ICD mapping). Candidate follows provided codes; requires preop context and location, does not infer location from unvalidated incisor distance.|MEDIUM|ADD_RULE / B-only adaptation|medium; no real labels|
|585|（1）腰痛持续3个月以上；|low_back_pain, duration|AND|current evidence|local state; unknown not positive|>=3 months|E: missing B route|Service value>=3 and exact unit 月. FSH minValue 3 mo. Candidate emits months with inclusive boundary; supports years/half-year and distributed pain duration.|MEDIUM|ADD_RULE / B-only adaptation|medium; no real labels|
|625| 某次就医期间总胆红素在正常范围上限1.5倍以内，丙氨酸氨基转移酶（ALT）和天冬氨酸氨基转移酶（AST）在正常范围上限3倍以内的患者。|labs|atomic|encounter/date grouped|local state; unknown not positive|TBIL<=1.5ULN AND ALT/AST<=3ULN|E: missing B route|CRITICAL: service does NOT require all three tests and pools all patient dates, rejecting on any outlier. Candidate obeys requested complete TBIL<=1.5 AND ALT<=3 AND AST<=3 per encounter/date, existential over encounters. Different from executable official service for mixed dates/partial panels.|HIGH|ADD_RULE / B-only adaptation|medium; no real labels|
|695| 3.证实有远处转移；|distant|atomic|current evidence|local state; unknown not positive|none|E: missing B route|Service profile AND with_distant_metastasis value. Candidate excludes uncertainty/M0/regional nodes; accepts M1 and explicit organ metastases, with possible primary-site ambiguity remaining.|MEDIUM|ADD_RULE / B-only adaptation|medium; no real labels|
|715| 3. 病变未侵及下腔静脉、门静脉；|ivc_clear, portal_clear|AND|current evidence|local state; unknown not positive|none|E: missing B route|Service requires both inferior_vena_cava and portal_vein components code=no. Candidate parses explicit vessel-specific negation, rejects invasion or uncertainty and does not infer from unscoped vascular-negative language.|HIGH|ADD_RULE / B-only adaptation|medium; no real labels|
|765| 3.有窒息缺氧史|history_hypoxia|OR within atom|history/event|local state; unknown not positive|none|E: missing B route|Service Condition history profile only; FSH allows suffocation OR hypoxia. Candidate requires history/event context rather than current low oxygen measurements.|MEDIUM|ADD_RULE / B-only adaptation|medium; no real labels|

## Submission Contract

The repository champion uses a message Bundle with one MessageHeader and 16 Python Libraries, identifier[0]=A index, content.title=profile ID. B construction preserves this shell and original B IDs where known; rows 2/3 use unique cnwqk2/cnwqk3 resource IDs and profile-2/profile-3 fallback identifiers. Original tbd/null values remain in the manifest. Deepquery IDs are preserved as explicitly scoped identifiers. These fallback index mappings are NOT an official contract and require platform validation. MessageHeader challenge_id=train_set is inherited from the online E reference; correct B platform setting is unverified.

Strict local checker checks count, order, unique IDs/identifiers, deepquery identity, base64, UTF-8, syntax, embedded route, JSON roundtrip, NaN rejection. It is not a formal platform checker or complete FSH validator. Missing evidence is never replaced with invented components, dates, or lab values. This means 295 one-branch records and 225 ongoing radiotherapy can conflict with stricter FSH cardinality/status constraints.

## Differential

Source: analysis/B_DIFFERENTIAL.json. All inputs synthetic and identical between official NLP reference and candidate; E has no B libraries. The reference uses real-shaped topics, with duplicated pathology/surgery topic records for profile 3 for both systems. Model transport is a NO stub; semantic-dependent behavior is unverified. No score or F1 improvement is inferred.

```json
{
  "comparison": "Offline official B NLP/service vs candidate; E has no B routes",
  "synthetic_only": true,
  "cases": 151,
  "new_positives": [
    "3_positive_0",
    "85_positive_2",
    "205_positive_0",
    "205_positive_2",
    "225_positive_1",
    "255_positive_0",
    "255_positive_1",
    "255_positive_2",
    "295_positive_1",
    "295_positive_2",
    "295_positive_attack_14",
    "295_positive_attack_17",
    "475_positive_1",
    "475_positive_2",
    "585_positive_0",
    "585_positive_1",
    "585_positive_2",
    "585_positive_attack_9",
    "585_positive_attack_10",
    "585_positive_attack_11",
    "625_positive_0",
    "625_positive_1",
    "625_positive_2",
    "625_positive_attack_18",
    "625_positive_boundary_ALT_3",
    "625_positive_boundary_AST_3",
    "695_positive_1",
    "695_positive_2",
    "715_positive_0",
    "715_positive_attack_13"
  ],
  "lost_positives": [
    "2_negative_2",
    "2_negative_3",
    "2_negative_4",
    "2_negative_attack_5",
    "85_negative_1",
    "85_negative_3",
    "225_negative_3",
    "225_negative_4",
    "465_negative_1",
    "465_negative_3",
    "465_negative_4",
    "475_negative_1",
    "495_negative_1",
    "495_negative_3",
    "495_negative_4",
    "495_negative_attack_4",
    "525_negative_2",
    "525_negative_3",
    "525_negative_4",
    "715_negative_0",
    "715_negative_1",
    "715_negative_3",
    "715_negative_4",
    "715_negative_attack_12",
    "765_negative_1",
    "765_negative_3",
    "765_negative_4"
  ],
  "unchanged_positives": [
    "2_positive_0",
    "2_positive_1",
    "2_positive_2",
    "3_positive_1",
    "3_positive_2",
    "85_positive_0",
    "85_positive_1",
    "205_positive_1",
    "225_positive_0",
    "225_positive_2",
    "465_positive_0",
    "465_positive_1",
    "465_positive_2",
    "475_positive_0",
    "495_positive_0",
    "495_positive_1",
    "495_positive_2",
    "525_positive_0",
    "525_positive_1",
    "525_positive_2",
    "695_positive_0",
    "715_positive_1",
    "715_positive_2",
    "765_positive_0",
    "765_positive_1",
    "765_positive_2"
  ],
  "new_negatives": [
    "2_negative_2",
    "2_negative_3",
    "2_negative_4",
    "2_negative_attack_5",
    "85_negative_1",
    "85_negative_3",
    "225_negative_3",
    "225_negative_4",
    "465_negative_1",
    "465_negative_3",
    "465_negative_4",
    "475_negative_1",
    "495_negative_1",
    "495_negative_3",
    "495_negative_4",
    "495_negative_attack_4",
    "525_negative_2",
    "525_negative_3",
    "525_negative_4",
    "715_negative_0",
    "715_negative_1",
    "715_negative_3",
    "715_negative_4",
    "715_negative_attack_12",
    "765_negative_1",
    "765_negative_3",
    "765_negative_4"
  ],
  "unresolved": [
    "295_positive_0",
    "295_positive_attack_15"
  ],
  "service_mismatches": [],
  "candidate_logic_failures": [],
  "real_patient_differential": "NOT_AVAILABLE",
  "local_schema": {
    "libraries": 16,
    "unique_ids": 16,
    "deepquery_ids": 16,
    "local_schema": "PASS",
    "platform_mapping": "UNVERIFIED_FOR_TBD"
  },
  "baseline_match_set": [
    "2_positive_0",
    "2_positive_1",
    "2_positive_2",
    "2_negative_2",
    "2_negative_3",
    "2_negative_4",
    "2_negative_attack_5",
    "3_positive_1",
    "3_positive_2",
    "85_positive_0",
    "85_positive_1",
    "85_negative_1",
    "85_negative_3",
    "205_positive_1",
    "225_positive_0",
    "225_positive_2",
    "225_negative_3",
    "225_negative_4",
    "465_positive_0",
    "465_positive_1",
    "465_positive_2",
    "465_negative_1",
    "465_negative_3",
    "465_negative_4",
    "475_positive_0",
    "475_negative_1",
    "495_positive_0",
    "495_positive_1",
    "495_positive_2",
    "495_negative_1",
    "495_negative_3",
    "495_negative_4",
    "495_negative_attack_4",
    "525_positive_0",
    "525_positive_1",
    "525_positive_2",
    "525_negative_2",
    "525_negative_3",
    "525_negative_4",
    "695_positive_0",
    "715_positive_1",
    "715_positive_2",
    "715_negative_0",
    "715_negative_1",
    "715_negative_3",
    "715_negative_4",
    "715_negative_attack_12",
    "765_positive_0",
    "765_positive_1",
    "765_positive_2",
    "765_negative_1",
    "765_negative_3",
    "765_negative_4"
  ],
  "new_match_set": [
    "2_positive_0",
    "2_positive_1",
    "2_positive_2",
    "3_positive_0",
    "3_positive_1",
    "3_positive_2",
    "85_positive_0",
    "85_positive_1",
    "85_positive_2",
    "205_positive_0",
    "205_positive_1",
    "205_positive_2",
    "225_positive_0",
    "225_positive_1",
    "225_positive_2",
    "255_positive_0",
    "255_positive_1",
    "255_positive_2",
    "295_positive_0",
    "295_positive_1",
    "295_positive_2",
    "295_positive_attack_14",
    "295_positive_attack_15",
    "295_positive_attack_17",
    "465_positive_0",
    "465_positive_1",
    "465_positive_2",
    "475_positive_0",
    "475_positive_1",
    "475_positive_2",
    "495_positive_0",
    "495_positive_1",
    "495_positive_2",
    "525_positive_0",
    "525_positive_1",
    "525_positive_2",
    "585_positive_0",
    "585_positive_1",
    "585_positive_2",
    "585_positive_attack_9",
    "585_positive_attack_10",
    "585_positive_attack_11",
    "625_positive_0",
    "625_positive_1",
    "625_positive_2",
    "625_positive_attack_18",
    "625_positive_boundary_ALT_3",
    "625_positive_boundary_AST_3",
    "695_positive_0",
    "695_positive_1",
    "695_positive_2",
    "715_positive_0",
    "715_positive_1",
    "715_positive_2",
    "715_positive_attack_13",
    "765_positive_0",
    "765_positive_1",
    "765_positive_2"
  ]
}
```

## Every Changed Decision

|case|baseline -> candidate|reason|
|---|---|---|
|2_negative_2|MATCH -> NO_MATCH|respiratory=UNKNOWN|
|2_negative_3|MATCH -> NO_MATCH|respiratory=UNCERTAIN|
|2_negative_4|MATCH -> NO_MATCH|respiratory=ABSENT|
|2_negative_attack_5|MATCH -> NO_MATCH|respiratory=ABSENT|
|3_positive_0|NO_MATCH -> MATCH|hcc=PRESENT; pathology=PRESENT; resection=HISTORICAL; r0=HISTORICAL|
|85_positive_2|NO_MATCH -> MATCH|elective=HISTORICAL; thoracoscopy=HISTORICAL; lung_resection=HISTORICAL|
|85_negative_1|MATCH -> NO_MATCH|elective=UNKNOWN; thoracoscopy=NEGATED; lung_resection=NEGATED|
|85_negative_3|MATCH -> NO_MATCH|elective=UNKNOWN; thoracoscopy=UNCERTAIN; lung_resection=UNCERTAIN|
|205_positive_0|NO_MATCH -> MATCH|elective=HISTORICAL; thoracic_surgery=PRESENT; general_anesthesia=PRESENT|
|205_positive_2|NO_MATCH -> MATCH|elective=HISTORICAL; thoracic_surgery=HISTORICAL; general_anesthesia=HISTORICAL|
|225_positive_1|NO_MATCH -> MATCH|radiotherapy=HISTORICAL|
|225_negative_3|MATCH -> NO_MATCH|radiotherapy=UNCERTAIN|
|225_negative_4|MATCH -> NO_MATCH|radiotherapy=PLANNED|
|255_positive_0|NO_MATCH -> MATCH|t2dm=PRESENT|
|255_positive_1|NO_MATCH -> MATCH|t2dm=PRESENT|
|255_positive_2|NO_MATCH -> MATCH|t2dm=PRESENT|
|295_positive_0|UNRESOLVED -> MATCH|smoking_eligible=PRESENT|
|295_positive_1|NO_MATCH -> MATCH|smoking_eligible=PRESENT|
|295_positive_2|NO_MATCH -> MATCH|smoking_eligible=PRESENT|
|295_positive_attack_14|NO_MATCH -> MATCH|smoking_eligible=PRESENT|
|295_positive_attack_15|UNRESOLVED -> MATCH|smoking_eligible=PRESENT|
|295_positive_attack_17|NO_MATCH -> MATCH|smoking_eligible=PRESENT|
|465_negative_1|MATCH -> NO_MATCH|renal_biopsy=PRESENT; autoimmune_renal=NEGATED|
|465_negative_3|MATCH -> NO_MATCH|renal_biopsy=PRESENT; autoimmune_renal=UNCERTAIN|
|465_negative_4|MATCH -> NO_MATCH|renal_biopsy=PLANNED; autoimmune_renal=PRESENT|
|475_positive_1|NO_MATCH -> MATCH|pain=PRESENT; spinal_cause=PRESENT; pain_relation=PRESENT; duration=PRESENT|
|475_positive_2|NO_MATCH -> MATCH|pain=PRESENT; spinal_cause=PRESENT; pain_relation=PRESENT; duration=PRESENT|
|475_negative_1|MATCH -> NO_MATCH|pain=NEGATED; spinal_cause=PRESENT; pain_relation=UNKNOWN; duration=PRESENT|
|495_negative_1|MATCH -> NO_MATCH|dlbcl=NEGATED; pathology=PRESENT|
|495_negative_3|MATCH -> NO_MATCH|dlbcl=UNCERTAIN; pathology=PRESENT|
|495_negative_4|MATCH -> NO_MATCH|dlbcl=PLANNED; pathology=UNKNOWN|
|495_negative_attack_4|MATCH -> NO_MATCH|dlbcl=PRESENT; pathology=UNCERTAIN|
|525_negative_2|MATCH -> NO_MATCH|esophageal=PRESENT; middle_lower=UNKNOWN; preoperative=PRESENT|
|525_negative_3|MATCH -> NO_MATCH|esophageal=UNCERTAIN; middle_lower=UNCERTAIN; preoperative=PRESENT|
|525_negative_4|MATCH -> NO_MATCH|esophageal=HISTORICAL; middle_lower=HISTORICAL; preoperative=UNKNOWN|
|585_positive_0|NO_MATCH -> MATCH|low_back_pain=PRESENT; duration=PRESENT|
|585_positive_1|NO_MATCH -> MATCH|low_back_pain=PRESENT; duration=PRESENT|
|585_positive_2|NO_MATCH -> MATCH|low_back_pain=PRESENT; duration=PRESENT|
|585_positive_attack_9|NO_MATCH -> MATCH|low_back_pain=PRESENT; duration=PRESENT|
|585_positive_attack_10|NO_MATCH -> MATCH|low_back_pain=PRESENT; duration=PRESENT|
|585_positive_attack_11|NO_MATCH -> MATCH|low_back_pain=PRESENT; duration=PRESENT|
|625_positive_0|NO_MATCH -> MATCH|labs=PRESENT|
|625_positive_1|NO_MATCH -> MATCH|labs=PRESENT|
|625_positive_2|NO_MATCH -> MATCH|labs=PRESENT|
|625_positive_attack_18|NO_MATCH -> MATCH|labs=PRESENT|
|625_positive_boundary_ALT_3|NO_MATCH -> MATCH|labs=PRESENT|
|625_positive_boundary_AST_3|NO_MATCH -> MATCH|labs=PRESENT|
|695_positive_1|NO_MATCH -> MATCH|distant=PRESENT|
|695_positive_2|NO_MATCH -> MATCH|distant=PRESENT|
|715_positive_0|NO_MATCH -> MATCH|ivc_clear=PRESENT; portal_clear=PRESENT|
|715_negative_0|MATCH -> NO_MATCH|ivc_clear=PRESENT; portal_clear=NEGATED|
|715_negative_1|MATCH -> NO_MATCH|ivc_clear=NEGATED; portal_clear=PRESENT|
|715_negative_3|MATCH -> NO_MATCH|ivc_clear=PRESENT; portal_clear=UNCERTAIN|
|715_negative_4|MATCH -> NO_MATCH|ivc_clear=PRESENT; portal_clear=NEGATED|
|715_negative_attack_12|MATCH -> NO_MATCH|ivc_clear=PRESENT; portal_clear=NEGATED|
|715_positive_attack_13|NO_MATCH -> MATCH|ivc_clear=PRESENT; portal_clear=PRESENT|
|765_negative_1|MATCH -> NO_MATCH|history_hypoxia=NEGATED|
|765_negative_3|MATCH -> NO_MATCH|history_hypoxia=UNCERTAIN|
|765_negative_4|MATCH -> NO_MATCH|history_hypoxia=UNKNOWN|

## Readiness

B_BOARD_READY = NO

Blockers: actual B patient/query corpus unavailable; official publication contract for tbd/null and deepquery mapping unavailable; formal platform checker unavailable; local-model JSON semantic rescue not validated against real endpoint; known FSH/service conflicts for 225/295/625. Generated artifact is an offline candidate, not a proven upload-ready champion.
