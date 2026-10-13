# B4 Semantic Comparison

All cases are synthetic; no real Precision/Recall/Macro F1/Micro F1 can be computed.
R: B2E deterministic rules. L: LLM-first closed structured Bare Prompt, UNKNOWN fails closed. H: rules plus categorical UNKNOWN supplementation. I: one missing atom per call. S: H with OR-only single-profile policy. F: H engineering candidate.
B4-R intentionally disables historical semantic fallback for a pure-rule control. Numeric/date/causal/vessel facts are protected and require existing deterministic extraction; no semantic-only numeric recall claim.
Existing builders already emit one representation for the eligible S profiles, so S has no resource-count change on this corpus; AND profiles 3/465/625/715 retain every resource.

|Variant|Cases|MATCH|Service hits|R4 invalid|FSH invalid|Stub calls|Semantic fixture errors|
|---|---:|---:|---:|---:|---:|---:|---:|
|B4R|182|71|71|0|18|0|3|
|B4L|182|3|3|0|0|131|0|
|B4H|182|74|74|0|18|60|0|
|B4I|182|74|74|0|18|114|0|
|B4S|182|74|74|0|18|60|0|
|B4F|182|74|74|0|18|60|0|

Three explicit paraphrase groups and subject/negative/uncertain/planned counterfactuals use specified stub responses. They verify plumbing and guards; they do not establish model understanding or generalization.
No regex synonym expansion is claimed across the 16 criteria. Existing 167 per-criterion boundary/negative cases are replayed alongside 15 new semantic fixtures.
I explicitly asks for missing TBIL/ALT/AST, upper limits and encounter identity, and for smoking context, quantity, 90-day window and cessation guarantee. These diagnostic responses cannot bypass deterministic original-value validation; semantic numeric extraction remains a limitation.
F is selected as a reviewable H implementation with conservative fallback and fewer calls than item mode; the proven offline recommendation remains B2E until live/gold validation. L cannot be recommended from NO-stub results.
