# Criterion 855 frozen interpretation

The V5S interpretation follows the existing V4.3 production audit: criterion 855 requires complete renal/hepatic lab evidence. Scr and BUN use fixed thresholds, while ALT and AST must each be locally bound to an explicit matching upper limit and must not exceed that upper limit.

Required grounded evidence:

- Scr < 178 umol/L
- BUN < 9 mmol/L
- ALT <= its local upper limit of normal
- AST <= its local upper limit of normal

All four components are required for a deterministic positive decision. Missing values or missing ALT/AST upper limits are insufficient evidence. The scorer-facing FHIR payload preserves the proven serum-creatinine Observation contract and emits only grounded values.
