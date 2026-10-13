# EXPERIMENT L READY FOR MANUAL ONLINE PROBE

Champion: Experiment E  
Baseline macro F1: `0.16666666666666666`  
Strategy: `675 PRECISION GUARD`  
Modified criterion: `675` only  
Admission direction: **STRICTER ONLY**

## Frozen baseline

Frozen E was recovered exactly from Git commit `6639cf7`, blob `2449a442...`, size `702059`, SHA256 `40457de3149c7db34daf9c3545199c7c8f409ec65b6ae4412f6ca6a77df6d96e`. The current workspace E file remains a byte-only serialization variant; its decoded 16 Library sources are equal. The online score is attached only to the recovered E reference.

## Core deterministic defect

Input: `患者56岁，诊断带状疱疹。`

- Frozen E: `MATCH`, reason `RULE_ZOSTER`, resources `1`, semantic stub `FALSE`
- Experiment L: `NO_MATCH`, reason `MISSING_REQUIRED_675_FACT`, resources `0`
- Missing fact: grounded head/face location

L requires all three facts:

1. Explicit age `>=50`
2. Explicit herpes-zoster diagnosis
3. Grounded head/face site bound to the diagnosis

No partial-group semantic admission, no V6 production architecture, and no new 675 positive path were added.

## Delta gates

- 675 delta audit: [V5S8L_675_DELTA.json](../analysis/V5S8L_675_DELTA.json)
- New positives: `0`
- Forbidden `NO_MATCH -> MATCH`: `0`
- Valid retained 675 positives: `100%`
- Retained E/L payload equality: `7/7`
- Non-target source parity: `15/15`
- Zero fabricated values: `0`
- Semantic admission widening: `0`
- Semantic-stub evidence used for readiness: `0`

Retained positives include head/face, face, ophthalmic, and cross-report complete fixtures. Pruned cases include missing site, age below 50, missing diagnosis, trunk/lower-limb site, explicit negation, and unrelated face pain/rash.

## Why Experiment L is not G-style expansion

Experiment G converted partial evidence into additional `MATCH` decisions. Experiment L only removes an E `MATCH` when a criterion-required fact is absent or unbound. It never adds a `MATCH`; therefore `L_MATCH_SET ⊆ E_MATCH_SET` on the available local replay corpus.

## Artifact verification

- Candidate: `submission/a_test_message_bundle_v5s8_expl_675_precision_guard_candidate.json`
- Size: `706091` bytes
- SHA256: `8878029301445486e19df9b7db66927fcfb952d8ac952833e3e7c1a32d2c8e15`
- Bundle/message: PASS
- Entries: `17`
- MessageHeader: `1`
- Libraries: `16`
- Base64 decode / UTF-8 / compile: `16/16`
- Isolated execution: PASS
- 675 retained positive resource: `1`
- 675 retained positive service replay: `SERVICE_HIT`
- 675 missing-site resources: `0`
- Security scan: `16/16`
- Unresolved symbols: `0`
- Dataclass / Enum / flatten artifacts: `0`
- Library ordering: unchanged
- MessageHeader: unchanged

## V6 status

V6 remains **DESIGN VALID BUT PRODUCTION BLOCKED**. Its prior gate had zero proven SAFE_COMPLETION against actual E, unresolved semantic-dependent E replay, and unavailable Test-A patient text. Experiment L is independent and uses one concrete deterministic defect identified during that audit.

## Final classification

Candidate generation gates: **PASS**  
Raw online log dependency: **NONE**  
Experiment E: **NOT MODIFIED**  
Tianchi: **NOT SUBMITTED**

## Next action

Perform one manual online probe with the frozen L candidate. Interpret only the final score against Experiment E: higher accepts L, equal means no online effect, lower rejects L. Do not infer hidden-patient attribution.
