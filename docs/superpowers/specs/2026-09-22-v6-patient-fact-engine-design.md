# V6 Patient-Level Fact Engine Design

## Decision

V6 is an isolated, non-production patient-level fact engine. It addresses the failure demonstrated by G: broader local matches and valid service replay do not establish hidden-set correctness. The objective is grounded evidence completeness, not more `MATCH` labels.

## Architecture

`reports -> normalization -> deterministic facts -> optional grounded semantic residuals -> patient fact store -> explicit fusion -> criterion evaluator -> MATCH/NO_MATCH/UNKNOWN -> payload gate -> reused scorer FHIR`

There is no global classifier and no final LLM voter. Evaluators receive facts, not raw model confidence.

## Fact contract

The store uses plain dictionaries and lists. A fact has `id`, `type`, `concept`, `value`, `unit`, `status`, `negated`, `planned`, `historical`, `source_report`, `sentence_index`, and `evidence_text`. Relations carry source/target fact IDs and grounded evidence. Only fields required by the criteria are admitted.

The prototype extracts demographics, laboratory values, staging, procedures, treatments, smoking, diagnoses, symptoms, coagulation status, and consciousness/intracranial-hypertension mentions. It does not interpret eligibility during extraction.

## Negation, status, and time

Negation is sentence-local. `无吸烟史，但术后需要气管插管有创机械通气` negates smoking only. Historical negation does not become a patient-global block against a later current positive. `计划/拟/将` produces planned facts; `已/目前/活动期/正在治疗` produces performed/current status; `既往/曾` remains historical. Explicit resolved states are retained and evaluated as such.

## Fusion

Facts from multiple reports may be combined when each fact retains source and time. A relation is fused only when chronology and local evidence support it. For 745, surgery plus ventilation without a grounded postoperative relation remains `UNKNOWN`; a later report containing an explicit postoperative relation can complete the criterion. Conflicts resolve only with grounded temporal specificity. Otherwise the evaluator returns `UNKNOWN`.

## Optional semantic residual

The semantic component, when later enabled, gets zero or one patient-level call, extracts facts only, and returns no decision field. Every returned evidence string must be an exact substring of the input. Malformed JSON, extra prose, hallucinated facts, unsupported negation, and unsupported relations are dropped. The prototype uses zero calls and is therefore deterministic.

## Evaluator contract

`evaluate(facts) -> {decision, reason_code, supporting_fact_ids, payload_ready, scorer_contract_ready}`.

`MATCH` requires every fact and relation required by the criterion. Explicit violations produce `NO_MATCH`. Missing or unresolved facts produce `UNKNOWN`. `UNKNOWN` never emits a resource.

## G negative-control constraints

V6 does not import G's partial/qualitative admission paths for 635 or 855, does not convert 2/3 evidence into a 675 match, does not infer activity from disease history, and does not infer postoperative ventilation from unrelated reports. More evidence can complete a criterion; it cannot lower its threshold.

## Scorer integration

V6 reuses E/C/I scorer contracts and payload builders. A payload is emitted only after `MATCH`, complete grounded values/relations, and a proven contract. No new FHIR mapping is invented in the MVP.

## Runtime and rollback

Preferred extraction mode is deterministic extraction plus one grounded residual semantic call. Target budget is <=2 calls per patient average and hard maximum 4. The MVP remains an isolated `scripts/v6_offline_prototype.py`; rollback is deleting the integration branch and retaining E unchanged.

## Approval gate

Proceed to production only if at least four criteria show architecture-level evidence gain, `UNSAFE_RELAXATION=0`, payload reuse is proven, and implementation complexity remains below the V4 architecture. No score prediction is made.
