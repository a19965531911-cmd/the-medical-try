# B5 Semantic Evaluation

All metrics below describe labelled synthetic PIPELINE behavior, including deterministic rules and connection-failure fallback. They are not live model performance or leaderboard scores.
B5-R uses B2E deterministic evaluate/build without changing facts; B5-H fills only grounded UNKNOWN categorical atoms; B5-L attempts structured model judgment then uses deterministic Builder. Transport failures fall back to B2E; valid UNKNOWN remains UNKNOWN.
B5-H/L additionally exclude ambiguous family-only records and prevent cross-event 525 conjunctions. B5-R remains unchanged. These are deterministic safety repairs, not LLM recall gains. The original 100 labels are retained; family 715 and cross-event 525 failures were first reproduced in new tests.
No model-quality metrics can be estimated with zero successful generative calls. No champion selection by MATCH counts. B5-R remains the offline engineering candidate until real model evidence exists.
Numeric/date/event treatment remains deterministic. Item/categorical model assertions cannot fabricate a lab panel, surgery or missing treatment history.
Per-profile synthetic precision/recall/F1 and confusion matrices (zero_division=0; defined corpus denominator, not official Macro F1):
```json
{
  "B5R": {
    "overall": {
      "n": 100,
      "tp": 40,
      "fp": 2,
      "fn": 7,
      "tn": 51,
      "precision": 0.9523809523809523,
      "recall": 0.851063829787234,
      "f1": 0.898876404494382
    },
    "service_pipeline": {
      "n": 100,
      "tp": 40,
      "fp": 2,
      "fn": 7,
      "tn": 51,
      "precision": 0.9523809523809523,
      "recall": 0.851063829787234,
      "f1": 0.898876404494382
    },
    "stages": {
      "no_resource": 58,
      "profile_invalid": 9,
      "generated_service_miss": 0
    },
    "profiles": {
      "2": {
        "n": 11,
        "tp": 2,
        "fp": 0,
        "fn": 4,
        "tn": 5,
        "precision": 1.0,
        "recall": 0.3333333333333333,
        "f1": 0.5
      },
      "3": {
        "n": 6,
        "tp": 3,
        "fp": 0,
        "fn": 0,
        "tn": 3,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "85": {
        "n": 5,
        "tp": 3,
        "fp": 0,
        "fn": 0,
        "tn": 2,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "205": {
        "n": 5,
        "tp": 3,
        "fp": 0,
        "fn": 0,
        "tn": 2,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "225": {
        "n": 7,
        "tp": 3,
        "fp": 0,
        "fn": 1,
        "tn": 3,
        "precision": 1.0,
        "recall": 0.75,
        "f1": 0.8571428571428571
      },
      "255": {
        "n": 7,
        "tp": 2,
        "fp": 0,
        "fn": 1,
        "tn": 4,
        "precision": 1.0,
        "recall": 0.6666666666666666,
        "f1": 0.8
      },
      "295": {
        "n": 5,
        "tp": 2,
        "fp": 0,
        "fn": 0,
        "tn": 3,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "465": {
        "n": 5,
        "tp": 2,
        "fp": 0,
        "fn": 0,
        "tn": 3,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "475": {
        "n": 5,
        "tp": 2,
        "fp": 0,
        "fn": 0,
        "tn": 3,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "495": {
        "n": 9,
        "tp": 3,
        "fp": 0,
        "fn": 1,
        "tn": 5,
        "precision": 1.0,
        "recall": 0.75,
        "f1": 0.8571428571428571
      },
      "525": {
        "n": 5,
        "tp": 2,
        "fp": 1,
        "fn": 0,
        "tn": 2,
        "precision": 0.6666666666666666,
        "recall": 1.0,
        "f1": 0.8
      },
      "585": {
        "n": 4,
        "tp": 2,
        "fp": 0,
        "fn": 0,
        "tn": 2,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "625": {
        "n": 9,
        "tp": 4,
        "fp": 0,
        "fn": 0,
        "tn": 5,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "695": {
        "n": 6,
        "tp": 2,
        "fp": 0,
        "fn": 0,
        "tn": 4,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "715": {
        "n": 5,
        "tp": 2,
        "fp": 1,
        "fn": 0,
        "tn": 2,
        "precision": 0.6666666666666666,
        "recall": 1.0,
        "f1": 0.8
      },
      "765": {
        "n": 6,
        "tp": 3,
        "fp": 0,
        "fn": 0,
        "tn": 3,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      }
    },
    "groups": {
      "clear_positive": {
        "n": 20,
        "tp": 20,
        "fp": 0,
        "fn": 0,
        "tn": 0,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "clear_negative": {
        "n": 20,
        "tp": 0,
        "fp": 0,
        "fn": 0,
        "tn": 20,
        "precision": 0,
        "recall": 0,
        "f1": 0
      },
      "complex_synonym": {
        "n": 20,
        "tp": 12,
        "fp": 0,
        "fn": 7,
        "tn": 1,
        "precision": 1.0,
        "recall": 0.631578947368421,
        "f1": 0.7741935483870968
      },
      "state_scope": {
        "n": 20,
        "tp": 5,
        "fp": 0,
        "fn": 0,
        "tn": 15,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "cross_scope": {
        "n": 20,
        "tp": 3,
        "fp": 2,
        "fn": 0,
        "tn": 15,
        "precision": 0.6,
        "recall": 1.0,
        "f1": 0.75
      }
    }
  },
  "B5H": {
    "overall": {
      "n": 100,
      "tp": 40,
      "fp": 0,
      "fn": 7,
      "tn": 53,
      "precision": 1.0,
      "recall": 0.851063829787234,
      "f1": 0.9195402298850575
    },
    "service_pipeline": {
      "n": 100,
      "tp": 40,
      "fp": 0,
      "fn": 7,
      "tn": 53,
      "precision": 1.0,
      "recall": 0.851063829787234,
      "f1": 0.9195402298850575
    },
    "stages": {
      "no_resource": 60,
      "profile_invalid": 9,
      "generated_service_miss": 0
    },
    "profiles": {
      "2": {
        "n": 11,
        "tp": 2,
        "fp": 0,
        "fn": 4,
        "tn": 5,
        "precision": 1.0,
        "recall": 0.3333333333333333,
        "f1": 0.5
      },
      "3": {
        "n": 6,
        "tp": 3,
        "fp": 0,
        "fn": 0,
        "tn": 3,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "85": {
        "n": 5,
        "tp": 3,
        "fp": 0,
        "fn": 0,
        "tn": 2,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "205": {
        "n": 5,
        "tp": 3,
        "fp": 0,
        "fn": 0,
        "tn": 2,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "225": {
        "n": 7,
        "tp": 3,
        "fp": 0,
        "fn": 1,
        "tn": 3,
        "precision": 1.0,
        "recall": 0.75,
        "f1": 0.8571428571428571
      },
      "255": {
        "n": 7,
        "tp": 2,
        "fp": 0,
        "fn": 1,
        "tn": 4,
        "precision": 1.0,
        "recall": 0.6666666666666666,
        "f1": 0.8
      },
      "295": {
        "n": 5,
        "tp": 2,
        "fp": 0,
        "fn": 0,
        "tn": 3,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "465": {
        "n": 5,
        "tp": 2,
        "fp": 0,
        "fn": 0,
        "tn": 3,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "475": {
        "n": 5,
        "tp": 2,
        "fp": 0,
        "fn": 0,
        "tn": 3,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "495": {
        "n": 9,
        "tp": 3,
        "fp": 0,
        "fn": 1,
        "tn": 5,
        "precision": 1.0,
        "recall": 0.75,
        "f1": 0.8571428571428571
      },
      "525": {
        "n": 5,
        "tp": 2,
        "fp": 0,
        "fn": 0,
        "tn": 3,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "585": {
        "n": 4,
        "tp": 2,
        "fp": 0,
        "fn": 0,
        "tn": 2,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "625": {
        "n": 9,
        "tp": 4,
        "fp": 0,
        "fn": 0,
        "tn": 5,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "695": {
        "n": 6,
        "tp": 2,
        "fp": 0,
        "fn": 0,
        "tn": 4,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "715": {
        "n": 5,
        "tp": 2,
        "fp": 0,
        "fn": 0,
        "tn": 3,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "765": {
        "n": 6,
        "tp": 3,
        "fp": 0,
        "fn": 0,
        "tn": 3,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      }
    },
    "groups": {
      "clear_positive": {
        "n": 20,
        "tp": 20,
        "fp": 0,
        "fn": 0,
        "tn": 0,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "clear_negative": {
        "n": 20,
        "tp": 0,
        "fp": 0,
        "fn": 0,
        "tn": 20,
        "precision": 0,
        "recall": 0,
        "f1": 0
      },
      "complex_synonym": {
        "n": 20,
        "tp": 12,
        "fp": 0,
        "fn": 7,
        "tn": 1,
        "precision": 1.0,
        "recall": 0.631578947368421,
        "f1": 0.7741935483870968
      },
      "state_scope": {
        "n": 20,
        "tp": 5,
        "fp": 0,
        "fn": 0,
        "tn": 15,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "cross_scope": {
        "n": 20,
        "tp": 3,
        "fp": 0,
        "fn": 0,
        "tn": 17,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      }
    }
  },
  "B5L": {
    "overall": {
      "n": 100,
      "tp": 40,
      "fp": 0,
      "fn": 7,
      "tn": 53,
      "precision": 1.0,
      "recall": 0.851063829787234,
      "f1": 0.9195402298850575
    },
    "service_pipeline": {
      "n": 100,
      "tp": 40,
      "fp": 0,
      "fn": 7,
      "tn": 53,
      "precision": 1.0,
      "recall": 0.851063829787234,
      "f1": 0.9195402298850575
    },
    "stages": {
      "no_resource": 60,
      "profile_invalid": 9,
      "generated_service_miss": 0
    },
    "profiles": {
      "2": {
        "n": 11,
        "tp": 2,
        "fp": 0,
        "fn": 4,
        "tn": 5,
        "precision": 1.0,
        "recall": 0.3333333333333333,
        "f1": 0.5
      },
      "3": {
        "n": 6,
        "tp": 3,
        "fp": 0,
        "fn": 0,
        "tn": 3,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "85": {
        "n": 5,
        "tp": 3,
        "fp": 0,
        "fn": 0,
        "tn": 2,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "205": {
        "n": 5,
        "tp": 3,
        "fp": 0,
        "fn": 0,
        "tn": 2,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "225": {
        "n": 7,
        "tp": 3,
        "fp": 0,
        "fn": 1,
        "tn": 3,
        "precision": 1.0,
        "recall": 0.75,
        "f1": 0.8571428571428571
      },
      "255": {
        "n": 7,
        "tp": 2,
        "fp": 0,
        "fn": 1,
        "tn": 4,
        "precision": 1.0,
        "recall": 0.6666666666666666,
        "f1": 0.8
      },
      "295": {
        "n": 5,
        "tp": 2,
        "fp": 0,
        "fn": 0,
        "tn": 3,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "465": {
        "n": 5,
        "tp": 2,
        "fp": 0,
        "fn": 0,
        "tn": 3,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "475": {
        "n": 5,
        "tp": 2,
        "fp": 0,
        "fn": 0,
        "tn": 3,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "495": {
        "n": 9,
        "tp": 3,
        "fp": 0,
        "fn": 1,
        "tn": 5,
        "precision": 1.0,
        "recall": 0.75,
        "f1": 0.8571428571428571
      },
      "525": {
        "n": 5,
        "tp": 2,
        "fp": 0,
        "fn": 0,
        "tn": 3,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "585": {
        "n": 4,
        "tp": 2,
        "fp": 0,
        "fn": 0,
        "tn": 2,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "625": {
        "n": 9,
        "tp": 4,
        "fp": 0,
        "fn": 0,
        "tn": 5,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "695": {
        "n": 6,
        "tp": 2,
        "fp": 0,
        "fn": 0,
        "tn": 4,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "715": {
        "n": 5,
        "tp": 2,
        "fp": 0,
        "fn": 0,
        "tn": 3,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "765": {
        "n": 6,
        "tp": 3,
        "fp": 0,
        "fn": 0,
        "tn": 3,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      }
    },
    "groups": {
      "clear_positive": {
        "n": 20,
        "tp": 20,
        "fp": 0,
        "fn": 0,
        "tn": 0,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "clear_negative": {
        "n": 20,
        "tp": 0,
        "fp": 0,
        "fn": 0,
        "tn": 20,
        "precision": 0,
        "recall": 0,
        "f1": 0
      },
      "complex_synonym": {
        "n": 20,
        "tp": 12,
        "fp": 0,
        "fn": 7,
        "tn": 1,
        "precision": 1.0,
        "recall": 0.631578947368421,
        "f1": 0.7741935483870968
      },
      "state_scope": {
        "n": 20,
        "tp": 5,
        "fp": 0,
        "fn": 0,
        "tn": 15,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "cross_scope": {
        "n": 20,
        "tp": 3,
        "fp": 0,
        "fn": 0,
        "tn": 17,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      }
    }
  },
  "B4F_REFERENCE": {
    "overall": {
      "n": 100,
      "tp": 40,
      "fp": 2,
      "fn": 7,
      "tn": 51,
      "precision": 0.9523809523809523,
      "recall": 0.851063829787234,
      "f1": 0.898876404494382
    },
    "service_pipeline": {
      "n": 100,
      "tp": 40,
      "fp": 2,
      "fn": 7,
      "tn": 51,
      "precision": 0.9523809523809523,
      "recall": 0.851063829787234,
      "f1": 0.898876404494382
    },
    "stages": {
      "no_resource": 58,
      "profile_invalid": 9,
      "generated_service_miss": 0
    },
    "profiles": {
      "2": {
        "n": 11,
        "tp": 2,
        "fp": 0,
        "fn": 4,
        "tn": 5,
        "precision": 1.0,
        "recall": 0.3333333333333333,
        "f1": 0.5
      },
      "3": {
        "n": 6,
        "tp": 3,
        "fp": 0,
        "fn": 0,
        "tn": 3,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "85": {
        "n": 5,
        "tp": 3,
        "fp": 0,
        "fn": 0,
        "tn": 2,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "205": {
        "n": 5,
        "tp": 3,
        "fp": 0,
        "fn": 0,
        "tn": 2,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "225": {
        "n": 7,
        "tp": 3,
        "fp": 0,
        "fn": 1,
        "tn": 3,
        "precision": 1.0,
        "recall": 0.75,
        "f1": 0.8571428571428571
      },
      "255": {
        "n": 7,
        "tp": 2,
        "fp": 0,
        "fn": 1,
        "tn": 4,
        "precision": 1.0,
        "recall": 0.6666666666666666,
        "f1": 0.8
      },
      "295": {
        "n": 5,
        "tp": 2,
        "fp": 0,
        "fn": 0,
        "tn": 3,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "465": {
        "n": 5,
        "tp": 2,
        "fp": 0,
        "fn": 0,
        "tn": 3,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "475": {
        "n": 5,
        "tp": 2,
        "fp": 0,
        "fn": 0,
        "tn": 3,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "495": {
        "n": 9,
        "tp": 3,
        "fp": 0,
        "fn": 1,
        "tn": 5,
        "precision": 1.0,
        "recall": 0.75,
        "f1": 0.8571428571428571
      },
      "525": {
        "n": 5,
        "tp": 2,
        "fp": 1,
        "fn": 0,
        "tn": 2,
        "precision": 0.6666666666666666,
        "recall": 1.0,
        "f1": 0.8
      },
      "585": {
        "n": 4,
        "tp": 2,
        "fp": 0,
        "fn": 0,
        "tn": 2,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "625": {
        "n": 9,
        "tp": 4,
        "fp": 0,
        "fn": 0,
        "tn": 5,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "695": {
        "n": 6,
        "tp": 2,
        "fp": 0,
        "fn": 0,
        "tn": 4,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "715": {
        "n": 5,
        "tp": 2,
        "fp": 1,
        "fn": 0,
        "tn": 2,
        "precision": 0.6666666666666666,
        "recall": 1.0,
        "f1": 0.8
      },
      "765": {
        "n": 6,
        "tp": 3,
        "fp": 0,
        "fn": 0,
        "tn": 3,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      }
    },
    "groups": {
      "clear_positive": {
        "n": 20,
        "tp": 20,
        "fp": 0,
        "fn": 0,
        "tn": 0,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "clear_negative": {
        "n": 20,
        "tp": 0,
        "fp": 0,
        "fn": 0,
        "tn": 20,
        "precision": 0,
        "recall": 0,
        "f1": 0
      },
      "complex_synonym": {
        "n": 20,
        "tp": 12,
        "fp": 0,
        "fn": 7,
        "tn": 1,
        "precision": 1.0,
        "recall": 0.631578947368421,
        "f1": 0.7741935483870968
      },
      "state_scope": {
        "n": 20,
        "tp": 5,
        "fp": 0,
        "fn": 0,
        "tn": 15,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0
      },
      "cross_scope": {
        "n": 20,
        "tp": 3,
        "fp": 2,
        "fn": 0,
        "tn": 15,
        "precision": 0.6,
        "recall": 1.0,
        "f1": 0.75
      }
    }
  }
}
```
