# V5S.3 Experiment G Online Audit

## Evidence Availability

The repository and supplied attachments do not contain raw Experiment E or Experiment F line-level online logs. Therefore the requested per-criterion totals, `anchor_hits` histograms, `groups_hit` histograms, rule/LLM positive counts, final MATCH counts, resource counts, contradiction counts, fallback-only counts, and LLM-NO counts cannot be reconstructed reliably. This report does not invent those values.

Known aggregate online results supplied for this task:

- Experiment E macro F1: `0.1666666666666667`
- Experiment F macro F1: `0.1500`
- Experiment F added two scorer-visible 755 outputs without improving recall and reduced precision.

## Supplied Qualitative Observations

| Criterion | Available observation | Conservative bottleneck tested by G |
|---|---|---|
| 485 | Many cases had zero anchors, fallback, and final NO_MATCH. | Missing prolapse/stage aliases and local stage binding. |
| 635 | Many cases had one or two of four groups but remained NO_MATCH. | Four-analyte all-or-nothing semantic admission. |
| 855 | Many cases had one anchor or fallback and almost no positives. | Complete-panel dependency despite partial or qualitative normal evidence. |
| 675 | Experiment E improved this criterion; some two-of-three group cases remained NO_MATCH. | Zoster plus site or age relation coverage. |
| 735 | Disease anchors often received LLM NO_MATCH without literal activity wording. | Current-state and ongoing-treatment vocabulary. |
| 745 | Many one-group and some two-group cases remained NO_MATCH. | Same-sentence postoperative ventilation relation requirement. |

## Interpretation Boundary

No hidden labels, patient IDs, or criterion-level online counts are inferred. Experiment G uses public synthetic fixtures to test the specified bottlenecks and reports those offline counts separately in `V5S3_EXPERIMENT_G_READINESS.md`.
