Same paired perturbations and fixed response policies: {
  "B7_1H": {
    "metrics": {
      "n": 158,
      "tp": 50,
      "fp": 0,
      "fn": 7,
      "tn": 101,
      "precision": 1.0,
      "recall": 0.8771929824561403,
      "f1": 0.9345794392523364
    },
    "calls": 68,
    "rescues": 8,
    "productive_rate": 0.11764705882352941,
    "accepted_facts": 14,
    "facts_per_call": 0.20588235294117646,
    "calls_per_rescue": 8.5,
    "robust_metrics": {
      "n": 29,
      "tp": 23,
      "fp": 0,
      "fn": 0,
      "tn": 6,
      "precision": 1.0,
      "recall": 1.0,
      "f1": 1.0
    }
  },
  "B7_2H": {
    "metrics": {
      "n": 158,
      "tp": 50,
      "fp": 0,
      "fn": 7,
      "tn": 101,
      "precision": 1.0,
      "recall": 0.8771929824561403,
      "f1": 0.9345794392523364
    },
    "calls": 60,
    "rescues": 8,
    "productive_rate": 0.13333333333333333,
    "accepted_facts": 14,
    "facts_per_call": 0.23333333333333334,
    "calls_per_rescue": 7.5,
    "robust_metrics": {
      "n": 29,
      "tp": 22,
      "fp": 0,
      "fn": 1,
      "tn": 6,
      "precision": 1.0,
      "recall": 0.9565217391304348,
      "f1": 0.9777777777777777
    }
  }
}
Ambiguous source preserves true clinical label but should abstain; resulting FN is intentionally counted. Report-order changes carry the same quote with correct legacy index. Fact-changing negation/plans explicitly use negative labels. Response quotes are rewritten along with source: measures deterministic plumbing robustness, not model language generalization. Same-event four-atom evidence distributed over three records tested in both report orders; conservative pathology UNKNOWN/UNCERTAIN gate can still prevent rescue. These failures are counted, not relabelled.
