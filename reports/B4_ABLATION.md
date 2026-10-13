# B4 Ablation

SCORING_FORMULA_UNVERIFIED. Actual 16-Library packages executed with NO stub; disabled libraries are silent diagnostic probes.
Generated resources, FSH-invalid outputs, Service hits and unknown patient labels are recorded separately in ablations/*.results.json.
No official scoring formula or denominator is inferred from silence or differences; no uploads were made.
```json
{
  "All16": {
    "enabled": [
      "2",
      "3",
      "85",
      "205",
      "225",
      "255",
      "295",
      "465",
      "475",
      "495",
      "525",
      "585",
      "625",
      "695",
      "715",
      "765"
    ],
    "cases": 182,
    "generated": 71,
    "invalid": 18,
    "hits": 71
  },
  "Only3": {
    "enabled": [
      "3"
    ],
    "cases": 182,
    "generated": 4,
    "invalid": 0,
    "hits": 4
  },
  "Only295": {
    "enabled": [
      "295"
    ],
    "cases": 182,
    "generated": 7,
    "invalid": 5,
    "hits": 7
  },
  "Half-fire": {
    "enabled": [
      "2",
      "3",
      "85",
      "205",
      "225",
      "255",
      "295",
      "465"
    ],
    "cases": 182,
    "generated": 38,
    "invalid": 18,
    "hits": 38
  },
  "Complementary Half-fire": {
    "enabled": [
      "475",
      "495",
      "525",
      "585",
      "625",
      "695",
      "715",
      "765"
    ],
    "cases": 182,
    "generated": 33,
    "invalid": 0,
    "hits": 33
  }
}
```
