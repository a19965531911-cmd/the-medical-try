# V5S.6 Experiment J Target Selection

Audit date: 2026-09-22

## Baseline

- Champion: Experiment E
- Macro F1: `0.16666666666666666`
- Candidate: `submission/a_test_message_bundle_v5s2_expe_aggressive_candidate.json`
- SHA256: `40457de3149c7db34daf9c3545199c7c8f409ec65b6ae4412f6ca6a77df6d96e`

## Selection sequence

### Primary target: 635

**FAIL**

- Clinical qualitative normality can be relevant.
- The proven scorer surface requires four real numeric values and four real reference highs.
- Qualitative-only paths cannot emit a safe scorer-compatible payload.
- Fabricating numeric values or ULNs is prohibited.

### Automatic pivot: 855

**FAIL FOR NEW RESCUE**

- Complete grounded values split across reports are safe.
- Frozen Experiment E already fuses those reports, emits four resources, and returns `SERVICE_HIT`.
- Missing analytes or qualitative-only liver evidence cannot be safely completed.

## Selected target

**NONE**

Neither criterion satisfies all selection requirements:

1. scorer-visible safe representation exists;
2. new positive path is grounded;
3. no fabricated patient value;
4. binding is clinically defensible;
5. service replay returns HIT;
6. the path is not already positive in Experiment E.

## Delta budget

- New internal MATCH paths: `0`
- New resource-positive paths: `0`
- New service-visible paths: `0`
- Non-target modifications: `0`
- Candidate generated: `NO`

Creating a candidate with zero behavior delta would be meaningless. Creating a qualitative 635 or incomplete 855 candidate would violate the no-fabrication and scorer-visibility gates.
