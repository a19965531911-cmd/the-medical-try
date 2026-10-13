# B3 Remaining FSH Cases

The 18 original B2E cases are enumerated below with exact inputs and emitted resources. Cases with multiple constraints count once. B3 retains 18 cases with existing local FSH subset violations. Full SUSHI/IG/profile validation remains unavailable.

12 cases: 85/205 fixed status=planned, which is not an R4 ProcedureStatus. 5 cases: 295 requires two components but evidence supports one. 1 case: 225 ongoing in-progress conflicts with completed and lacks an evidenced performed date. No 625 case has a violation detected by the existing subset checker; its clinical/Service logic disagreement remains separate.

No remaining case can be made fully compliant by a verified constructor-only change without changing evidence or the official constraints. For 225, adding the report timestamp as a completed-treatment time is unsupported. For 295, missing intent/quantity cannot be synthesized. For 85/205, using planned is invalid R4 and using completed for planned procedures falsifies status.

## 85_positive_0

Profile: 85; known contract conflict: YES; safely fully repairable: NO.

Input evidence:
```json
[
  {
    "text": "拟择期行胸腔镜肺叶切除术",
    "timestamp": "2026-10-09T12:00:00+08:00",
    "topic": "手术记录"
  }
]
```

Actual B2E FHIR:
```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "resource": {
        "resourceType": "Procedure",
        "id": "85a6788b-a485-4e9c-a084-cf2f1b8deb00",
        "meta": {
          "profile": [
            "http://localhost:3456/api/terminology/Profile/cnwqk85-lung-resection"
          ]
        },
        "subject": {
          "reference": "Patient/p1"
        },
        "code": {
          "coding": [
            {
              "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk85-procedure-codes",
              "code": "pulmonary-lobectomy"
            }
          ]
        },
        "status": "preparation",
        "extension": [
          {
            "url": "http://localhost:3456/api/terminology/StructureDefinition/cnwqk85-procedure-priority",
            "valueCodeableConcept": {
              "coding": [
                {
                  "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk85-priority-codes",
                  "code": "elective"
                }
              ]
            }
          },
          {
            "url": "http://localhost:3456/api/terminology/StructureDefinition/cnwqk85-surgical-approach",
            "valueCodeableConcept": {
              "coding": [
                {
                  "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk85-approach-codes",
                  "code": "thoracoscopic"
                }
              ]
            }
          }
        ],
        "text": {
          "status": "generated",
          "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">拟择期行胸腔镜肺叶切除术。拟择期行胸腔镜肺叶切除术。拟择期行胸腔镜肺叶切除术</div>"
        },
        "category": {
          "coding": [
            {
              "system": "http://terminology.hl7.org/CodeSystem/procedure-category",
              "code": "surgery"
            }
          ]
        }
      },
      "request": {
        "method": "POST",
        "url": "Procedure"
      }
    }
  ]
}
```

Original FSH constraints:
```fsh
* status = #planned (exactly)
```

Detected violations:
- cnwqk85-lung-resection: status fixed=planned, actual=preparation

## 85_positive_1

Profile: 85; known contract conflict: YES; safely fully repairable: NO.

Input evidence:
```json
[
  {
    "text": "计划VATS肺段切除术",
    "timestamp": "2026-10-09T12:00:00+08:00",
    "topic": "手术记录"
  }
]
```

Actual B2E FHIR:
```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "resource": {
        "resourceType": "Procedure",
        "id": "608a17b4-031b-46a7-89de-b9c86a6bdf4b",
        "meta": {
          "profile": [
            "http://localhost:3456/api/terminology/Profile/cnwqk85-lung-resection"
          ]
        },
        "subject": {
          "reference": "Patient/p1"
        },
        "code": {
          "coding": [
            {
              "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk85-procedure-codes",
              "code": "pulmonary-lobectomy"
            }
          ]
        },
        "status": "preparation",
        "extension": [
          {
            "url": "http://localhost:3456/api/terminology/StructureDefinition/cnwqk85-procedure-priority",
            "valueCodeableConcept": {
              "coding": [
                {
                  "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk85-priority-codes",
                  "code": "elective"
                }
              ]
            }
          },
          {
            "url": "http://localhost:3456/api/terminology/StructureDefinition/cnwqk85-surgical-approach",
            "valueCodeableConcept": {
              "coding": [
                {
                  "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk85-approach-codes",
                  "code": "thoracoscopic"
                }
              ]
            }
          }
        ],
        "text": {
          "status": "generated",
          "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">计划VATS肺段切除术。计划VATS肺段切除术。计划VATS肺段切除术</div>"
        },
        "category": {
          "coding": [
            {
              "system": "http://terminology.hl7.org/CodeSystem/procedure-category",
              "code": "surgery"
            }
          ]
        }
      },
      "request": {
        "method": "POST",
        "url": "Procedure"
      }
    }
  ]
}
```

Original FSH constraints:
```fsh
* status = #planned (exactly)
```

Detected violations:
- cnwqk85-lung-resection: status fixed=planned, actual=preparation

## 85_positive_2

Profile: 85; known contract conflict: YES; safely fully repairable: NO.

Input evidence:
```json
[
  {
    "text": "拟择期手术。",
    "timestamp": "2026-10-09T12:00:00+08:00",
    "topic": "手术记录"
  },
  {
    "text": "胸腔镜入路。",
    "timestamp": "2026-10-09T12:00:00+08:00",
    "topic": "手术记录"
  },
  {
    "text": "肺叶切除术",
    "timestamp": "2026-10-09T12:00:00+08:00",
    "topic": "手术记录"
  }
]
```

Actual B2E FHIR:
```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "resource": {
        "resourceType": "Procedure",
        "id": "5301392e-9878-4d47-b516-59dfdce5fd23",
        "meta": {
          "profile": [
            "http://localhost:3456/api/terminology/Profile/cnwqk85-lung-resection"
          ]
        },
        "subject": {
          "reference": "Patient/p1"
        },
        "code": {
          "coding": [
            {
              "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk85-procedure-codes",
              "code": "pulmonary-lobectomy"
            }
          ]
        },
        "status": "preparation",
        "extension": [
          {
            "url": "http://localhost:3456/api/terminology/StructureDefinition/cnwqk85-procedure-priority",
            "valueCodeableConcept": {
              "coding": [
                {
                  "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk85-priority-codes",
                  "code": "elective"
                }
              ]
            }
          },
          {
            "url": "http://localhost:3456/api/terminology/StructureDefinition/cnwqk85-surgical-approach",
            "valueCodeableConcept": {
              "coding": [
                {
                  "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk85-approach-codes",
                  "code": "thoracoscopic"
                }
              ]
            }
          }
        ],
        "text": {
          "status": "generated",
          "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">拟择期手术。。胸腔镜入路。。肺叶切除术</div>"
        },
        "category": {
          "coding": [
            {
              "system": "http://terminology.hl7.org/CodeSystem/procedure-category",
              "code": "surgery"
            }
          ]
        }
      },
      "request": {
        "method": "POST",
        "url": "Procedure"
      }
    }
  ]
}
```

Original FSH constraints:
```fsh
* status = #planned (exactly)
```

Detected violations:
- cnwqk85-lung-resection: status fixed=planned, actual=preparation

## 205_positive_0

Profile: 205; known contract conflict: YES; safely fully repairable: NO.

Input evidence:
```json
[
  {
    "text": "拟择期全麻下胸部手术",
    "timestamp": "2026-10-09T12:00:00+08:00",
    "topic": "手术记录"
  }
]
```

Actual B2E FHIR:
```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "resource": {
        "resourceType": "Procedure",
        "id": "bd2adb47-8788-4446-9a5a-28b2973365f3",
        "meta": {
          "profile": [
            "http://localhost:3456/api/terminology/Profile/cnwqk205-thoracic-surgery"
          ]
        },
        "subject": {
          "reference": "Patient/p1"
        },
        "code": {
          "coding": [
            {
              "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk205-thoracic-surgery-cs",
              "code": "pulmonary"
            }
          ]
        },
        "status": "preparation",
        "extension": [
          {
            "url": "http://localhost:3456/api/terminology/StructureDefinition/anesthesia-method",
            "valueCodeableConcept": {
              "coding": [
                {
                  "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk205-anesthesia-method-cs",
                  "code": "GA"
                }
              ]
            }
          },
          {
            "url": "http://localhost:3456/api/terminology/StructureDefinition/anesthesia-depth",
            "valueCodeableConcept": {
              "coding": [
                {
                  "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk205-anesthesia-depth-cs",
                  "code": "GA"
                }
              ]
            }
          }
        ],
        "text": {
          "status": "generated",
          "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">拟择期全麻下胸部手术。拟择期全麻下胸部手术。拟择期全麻下胸部手术</div>"
        }
      },
      "request": {
        "method": "POST",
        "url": "Procedure"
      }
    }
  ]
}
```

Original FSH constraints:
```fsh
* status = #planned (exactly)  // 择期手术状态
```

Detected violations:
- cnwqk205-thoracic-surgery: status fixed=planned, actual=preparation

## 205_positive_1

Profile: 205; known contract conflict: YES; safely fully repairable: NO.

Input evidence:
```json
[
  {
    "text": "计划全身麻醉下肺叶切除术",
    "timestamp": "2026-10-09T12:00:00+08:00",
    "topic": "手术记录"
  }
]
```

Actual B2E FHIR:
```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "resource": {
        "resourceType": "Procedure",
        "id": "9b9178ad-7aee-4712-b045-e0a3ee7fb498",
        "meta": {
          "profile": [
            "http://localhost:3456/api/terminology/Profile/cnwqk205-thoracic-surgery"
          ]
        },
        "subject": {
          "reference": "Patient/p1"
        },
        "code": {
          "coding": [
            {
              "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk205-thoracic-surgery-cs",
              "code": "pulmonary"
            }
          ]
        },
        "status": "preparation",
        "extension": [
          {
            "url": "http://localhost:3456/api/terminology/StructureDefinition/anesthesia-method",
            "valueCodeableConcept": {
              "coding": [
                {
                  "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk205-anesthesia-method-cs",
                  "code": "GA"
                }
              ]
            }
          },
          {
            "url": "http://localhost:3456/api/terminology/StructureDefinition/anesthesia-depth",
            "valueCodeableConcept": {
              "coding": [
                {
                  "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk205-anesthesia-depth-cs",
                  "code": "GA"
                }
              ]
            }
          }
        ],
        "text": {
          "status": "generated",
          "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">计划全身麻醉下肺叶切除术。计划全身麻醉下肺叶切除术。计划全身麻醉下肺叶切除术</div>"
        }
      },
      "request": {
        "method": "POST",
        "url": "Procedure"
      }
    }
  ]
}
```

Original FSH constraints:
```fsh
* status = #planned (exactly)  // 择期手术状态
```

Detected violations:
- cnwqk205-thoracic-surgery: status fixed=planned, actual=preparation

## 205_positive_2

Profile: 205; known contract conflict: YES; safely fully repairable: NO.

Input evidence:
```json
[
  {
    "text": "择期肺切除手术。",
    "timestamp": "2026-10-09T12:00:00+08:00",
    "topic": "手术记录"
  },
  {
    "text": "麻醉方式为全麻",
    "timestamp": "2026-10-09T12:00:00+08:00",
    "topic": "手术记录"
  }
]
```

Actual B2E FHIR:
```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "resource": {
        "resourceType": "Procedure",
        "id": "1e7ee9c6-c613-4481-89e4-be9565448814",
        "meta": {
          "profile": [
            "http://localhost:3456/api/terminology/Profile/cnwqk205-thoracic-surgery"
          ]
        },
        "subject": {
          "reference": "Patient/p1"
        },
        "code": {
          "coding": [
            {
              "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk205-thoracic-surgery-cs",
              "code": "pulmonary"
            }
          ]
        },
        "status": "completed",
        "extension": [
          {
            "url": "http://localhost:3456/api/terminology/StructureDefinition/anesthesia-method",
            "valueCodeableConcept": {
              "coding": [
                {
                  "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk205-anesthesia-method-cs",
                  "code": "GA"
                }
              ]
            }
          },
          {
            "url": "http://localhost:3456/api/terminology/StructureDefinition/anesthesia-depth",
            "valueCodeableConcept": {
              "coding": [
                {
                  "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk205-anesthesia-depth-cs",
                  "code": "GA"
                }
              ]
            }
          }
        ],
        "performedDateTime": "2026-10-09T12:00:00+08:00",
        "text": {
          "status": "generated",
          "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">择期肺切除手术。。择期肺切除手术。。麻醉方式为全麻</div>"
        }
      },
      "request": {
        "method": "POST",
        "url": "Procedure"
      }
    }
  ]
}
```

Original FSH constraints:
```fsh
* status = #planned (exactly)  // 择期手术状态
```

Detected violations:
- cnwqk205-thoracic-surgery: status fixed=planned, actual=completed

## 295_positive_0

Profile: 295; known contract conflict: YES; safely fully repairable: NO.

Input evidence:
```json
[
  {
    "text": "目前每天吸烟20支",
    "timestamp": "2026-10-09T12:00:00+08:00",
    "topic": "个人史"
  }
]
```

Actual B2E FHIR:
```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "resource": {
        "resourceType": "Observation",
        "id": "ef6cdc26-4708-47e3-80c4-989a66bc72c8",
        "meta": {
          "profile": [
            "http://localhost:3456/api/terminology/Profile/cnwqk295-smokingstatus"
          ]
        },
        "subject": {
          "reference": "Patient/p1"
        },
        "code": {
          "coding": [
            {
              "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk295-smokingcs",
              "code": "smoking-status-detail"
            }
          ]
        },
        "status": "final",
        "component": [
          {
            "code": {
              "coding": [
                {
                  "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk295-smokingcs",
                  "code": "number-of-cigarettes-per-day"
                }
              ]
            },
            "valueQuantity": {
              "value": 20.0,
              "unit": "支/日"
            }
          }
        ],
        "effectivePeriod": {
          "start": "2026-10-09"
        },
        "text": {
          "status": "generated",
          "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">目前每天吸烟20支</div>"
        }
      },
      "request": {
        "method": "POST",
        "url": "Observation"
      }
    }
  ]
}
```

Original FSH constraints:
```fsh
* component 2..*
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #open
* component ^slicing.ordered = false
* component contains
* component[cigarettesPerDay].code = CNWQK295SmokingCS#number-of-cigarettes-per-day "每天吸烟支数"
* component[cigarettesPerDay].valueQuantity 1..1
* component[cessationGuarantee].code = CNWQK295SmokingCS#smoking-cessation-guarantee "戒烟保证"
* component[cessationGuarantee].valueCodeableConcept 1..1
* component[cessationGuarantee].valueCodeableConcept from CNWQK295GuaranteeVS
```

Detected violations:
- cnwqk295-smokingstatus: required component
- 295 required slice smoking-cessation-guarantee

## 295_positive_1

Profile: 295; known contract conflict: YES; safely fully repairable: NO.

Input evidence:
```json
[
  {
    "text": "现吸烟1包/日",
    "timestamp": "2026-10-09T12:00:00+08:00",
    "topic": "个人史"
  }
]
```

Actual B2E FHIR:
```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "resource": {
        "resourceType": "Observation",
        "id": "38760bf9-d405-4173-ad49-256575516e3a",
        "meta": {
          "profile": [
            "http://localhost:3456/api/terminology/Profile/cnwqk295-smokingstatus"
          ]
        },
        "subject": {
          "reference": "Patient/p1"
        },
        "code": {
          "coding": [
            {
              "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk295-smokingcs",
              "code": "smoking-status-detail"
            }
          ]
        },
        "status": "final",
        "component": [
          {
            "code": {
              "coding": [
                {
                  "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk295-smokingcs",
                  "code": "number-of-cigarettes-per-day"
                }
              ]
            },
            "valueQuantity": {
              "value": 20.0,
              "unit": "支/日"
            }
          }
        ],
        "effectivePeriod": {
          "start": "2026-10-09"
        },
        "text": {
          "status": "generated",
          "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">现吸烟1包/日</div>"
        }
      },
      "request": {
        "method": "POST",
        "url": "Observation"
      }
    }
  ]
}
```

Original FSH constraints:
```fsh
* component 2..*
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #open
* component ^slicing.ordered = false
* component contains
* component[cigarettesPerDay].code = CNWQK295SmokingCS#number-of-cigarettes-per-day "每天吸烟支数"
* component[cigarettesPerDay].valueQuantity 1..1
* component[cessationGuarantee].code = CNWQK295SmokingCS#smoking-cessation-guarantee "戒烟保证"
* component[cessationGuarantee].valueCodeableConcept 1..1
* component[cessationGuarantee].valueCodeableConcept from CNWQK295GuaranteeVS
```

Detected violations:
- cnwqk295-smokingstatus: required component
- 295 required slice smoking-cessation-guarantee

## 295_positive_2

Profile: 295; known contract conflict: YES; safely fully repairable: NO.

Input evidence:
```json
[
  {
    "text": "目前吸烟。",
    "timestamp": "2026-10-09T12:00:00+08:00",
    "topic": "个人史"
  },
  {
    "text": "每日20支",
    "timestamp": "2026-10-09T12:00:00+08:00",
    "topic": "个人史"
  }
]
```

Actual B2E FHIR:
```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "resource": {
        "resourceType": "Observation",
        "id": "6fdc432f-ef58-4eb7-a6fb-baee4ae067e6",
        "meta": {
          "profile": [
            "http://localhost:3456/api/terminology/Profile/cnwqk295-smokingstatus"
          ]
        },
        "subject": {
          "reference": "Patient/p1"
        },
        "code": {
          "coding": [
            {
              "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk295-smokingcs",
              "code": "smoking-status-detail"
            }
          ]
        },
        "status": "final",
        "component": [
          {
            "code": {
              "coding": [
                {
                  "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk295-smokingcs",
                  "code": "number-of-cigarettes-per-day"
                }
              ]
            },
            "valueQuantity": {
              "value": 20.0,
              "unit": "支/日"
            }
          }
        ],
        "effectivePeriod": {
          "start": "2026-10-09"
        },
        "text": {
          "status": "generated",
          "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">每日20支</div>"
        }
      },
      "request": {
        "method": "POST",
        "url": "Observation"
      }
    }
  ]
}
```

Original FSH constraints:
```fsh
* component 2..*
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #open
* component ^slicing.ordered = false
* component contains
* component[cigarettesPerDay].code = CNWQK295SmokingCS#number-of-cigarettes-per-day "每天吸烟支数"
* component[cigarettesPerDay].valueQuantity 1..1
* component[cessationGuarantee].code = CNWQK295SmokingCS#smoking-cessation-guarantee "戒烟保证"
* component[cessationGuarantee].valueCodeableConcept 1..1
* component[cessationGuarantee].valueCodeableConcept from CNWQK295GuaranteeVS
```

Detected violations:
- cnwqk295-smokingstatus: required component
- 295 required slice smoking-cessation-guarantee

## 295_quantity_only

Profile: 295; known contract conflict: YES; safely fully repairable: NO.

Input evidence:
```json
[
  {
    "text": "目前每天吸烟20支",
    "timestamp": "2026-10-09"
  }
]
```

Actual B2E FHIR:
```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "resource": {
        "resourceType": "Observation",
        "id": "614dc99a-7e2f-4c9d-bf3c-ccd52659b1df",
        "meta": {
          "profile": [
            "http://localhost:3456/api/terminology/Profile/cnwqk295-smokingstatus"
          ]
        },
        "subject": {
          "reference": "Patient/p1"
        },
        "code": {
          "coding": [
            {
              "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk295-smokingcs",
              "code": "smoking-status-detail"
            }
          ]
        },
        "status": "final",
        "component": [
          {
            "code": {
              "coding": [
                {
                  "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk295-smokingcs",
                  "code": "number-of-cigarettes-per-day"
                }
              ]
            },
            "valueQuantity": {
              "value": 20.0,
              "unit": "支/日"
            }
          }
        ],
        "effectivePeriod": {
          "start": "2026-10-09"
        },
        "text": {
          "status": "generated",
          "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">目前每天吸烟20支</div>"
        }
      },
      "request": {
        "method": "POST",
        "url": "Observation"
      }
    }
  ]
}
```

Original FSH constraints:
```fsh
* component 2..*
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #open
* component ^slicing.ordered = false
* component contains
* component[cigarettesPerDay].code = CNWQK295SmokingCS#number-of-cigarettes-per-day "每天吸烟支数"
* component[cigarettesPerDay].valueQuantity 1..1
* component[cessationGuarantee].code = CNWQK295SmokingCS#smoking-cessation-guarantee "戒烟保证"
* component[cessationGuarantee].valueCodeableConcept 1..1
* component[cessationGuarantee].valueCodeableConcept from CNWQK295GuaranteeVS
```

Detected violations:
- cnwqk295-smokingstatus: required component
- 295 required slice smoking-cessation-guarantee

## 295_refusal_only

Profile: 295; known contract conflict: YES; safely fully repairable: NO.

Input evidence:
```json
[
  {
    "text": "不能保证试验期间停止吸烟",
    "timestamp": "2026-10-09"
  }
]
```

Actual B2E FHIR:
```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "resource": {
        "resourceType": "Observation",
        "id": "1414d33e-d1ca-4427-9496-48d253ed7c13",
        "meta": {
          "profile": [
            "http://localhost:3456/api/terminology/Profile/cnwqk295-smokingstatus"
          ]
        },
        "subject": {
          "reference": "Patient/p1"
        },
        "code": {
          "coding": [
            {
              "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk295-smokingcs",
              "code": "smoking-status-detail"
            }
          ]
        },
        "status": "final",
        "component": [
          {
            "code": {
              "coding": [
                {
                  "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk295-smokingcs",
                  "code": "smoking-cessation-guarantee"
                }
              ]
            },
            "valueCodeableConcept": {
              "coding": [
                {
                  "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk295-guaranteecs",
                  "code": "cannot-guarantee"
                }
              ]
            }
          }
        ],
        "effectivePeriod": {
          "start": "2026-10-09"
        },
        "text": {
          "status": "generated",
          "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">不能保证试验期间停止吸烟</div>"
        }
      },
      "request": {
        "method": "POST",
        "url": "Observation"
      }
    }
  ]
}
```

Original FSH constraints:
```fsh
* component 2..*
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #open
* component ^slicing.ordered = false
* component contains
* component[cigarettesPerDay].code = CNWQK295SmokingCS#number-of-cigarettes-per-day "每天吸烟支数"
* component[cigarettesPerDay].valueQuantity 1..1
* component[cessationGuarantee].code = CNWQK295SmokingCS#smoking-cessation-guarantee "戒烟保证"
* component[cessationGuarantee].valueCodeableConcept 1..1
* component[cessationGuarantee].valueCodeableConcept from CNWQK295GuaranteeVS
```

Detected violations:
- cnwqk295-smokingstatus: required component
- 295 required slice number-of-cigarettes-per-day

## 85_completed

Profile: 85; known contract conflict: YES; safely fully repairable: NO.

Input evidence:
```json
[
  {
    "text": "择期已完成胸腔镜肺叶切除术",
    "timestamp": "2026-10-09"
  }
]
```

Actual B2E FHIR:
```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "resource": {
        "resourceType": "Procedure",
        "id": "43e3b61c-a282-474f-8567-d594667188fe",
        "meta": {
          "profile": [
            "http://localhost:3456/api/terminology/Profile/cnwqk85-lung-resection"
          ]
        },
        "subject": {
          "reference": "Patient/p1"
        },
        "code": {
          "coding": [
            {
              "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk85-procedure-codes",
              "code": "pulmonary-lobectomy"
            }
          ]
        },
        "status": "completed",
        "extension": [
          {
            "url": "http://localhost:3456/api/terminology/StructureDefinition/cnwqk85-procedure-priority",
            "valueCodeableConcept": {
              "coding": [
                {
                  "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk85-priority-codes",
                  "code": "elective"
                }
              ]
            }
          },
          {
            "url": "http://localhost:3456/api/terminology/StructureDefinition/cnwqk85-surgical-approach",
            "valueCodeableConcept": {
              "coding": [
                {
                  "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk85-approach-codes",
                  "code": "thoracoscopic"
                }
              ]
            }
          }
        ],
        "performedDateTime": "2026-10-09",
        "text": {
          "status": "generated",
          "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">择期已完成胸腔镜肺叶切除术。择期已完成胸腔镜肺叶切除术。择期已完成胸腔镜肺叶切除术</div>"
        },
        "category": {
          "coding": [
            {
              "system": "http://terminology.hl7.org/CodeSystem/procedure-category",
              "code": "surgery"
            }
          ]
        }
      },
      "request": {
        "method": "POST",
        "url": "Procedure"
      }
    }
  ]
}
```

Original FSH constraints:
```fsh
* status = #planned (exactly)
```

Detected violations:
- cnwqk85-lung-resection: status fixed=planned, actual=completed

## 85_planned

Profile: 85; known contract conflict: YES; safely fully repairable: NO.

Input evidence:
```json
[
  {
    "text": "拟择期胸腔镜肺叶切除术",
    "timestamp": "2026-10-09"
  }
]
```

Actual B2E FHIR:
```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "resource": {
        "resourceType": "Procedure",
        "id": "72d63ef0-a042-4f67-9bf4-fcf28b657835",
        "meta": {
          "profile": [
            "http://localhost:3456/api/terminology/Profile/cnwqk85-lung-resection"
          ]
        },
        "subject": {
          "reference": "Patient/p1"
        },
        "code": {
          "coding": [
            {
              "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk85-procedure-codes",
              "code": "pulmonary-lobectomy"
            }
          ]
        },
        "status": "preparation",
        "extension": [
          {
            "url": "http://localhost:3456/api/terminology/StructureDefinition/cnwqk85-procedure-priority",
            "valueCodeableConcept": {
              "coding": [
                {
                  "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk85-priority-codes",
                  "code": "elective"
                }
              ]
            }
          },
          {
            "url": "http://localhost:3456/api/terminology/StructureDefinition/cnwqk85-surgical-approach",
            "valueCodeableConcept": {
              "coding": [
                {
                  "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk85-approach-codes",
                  "code": "thoracoscopic"
                }
              ]
            }
          }
        ],
        "text": {
          "status": "generated",
          "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">拟择期胸腔镜肺叶切除术。拟择期胸腔镜肺叶切除术。拟择期胸腔镜肺叶切除术</div>"
        },
        "category": {
          "coding": [
            {
              "system": "http://terminology.hl7.org/CodeSystem/procedure-category",
              "code": "surgery"
            }
          ]
        }
      },
      "request": {
        "method": "POST",
        "url": "Procedure"
      }
    }
  ]
}
```

Original FSH constraints:
```fsh
* status = #planned (exactly)
```

Detected violations:
- cnwqk85-lung-resection: status fixed=planned, actual=preparation

## 85_good_and_emergency

Profile: 85; known contract conflict: YES; safely fully repairable: NO.

Input evidence:
```json
[
  {
    "text": "择期已完成胸腔镜肺叶切除术",
    "timestamp": "2026-10-09",
    "event_id": "a"
  },
  {
    "text": "急诊开胸肺切除术全麻",
    "timestamp": "2026-10-09",
    "event_id": "b"
  }
]
```

Actual B2E FHIR:
```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "resource": {
        "resourceType": "Procedure",
        "id": "a958c120-2991-4b6d-833c-00e764359ea5",
        "meta": {
          "profile": [
            "http://localhost:3456/api/terminology/Profile/cnwqk85-lung-resection"
          ]
        },
        "subject": {
          "reference": "Patient/p1"
        },
        "code": {
          "coding": [
            {
              "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk85-procedure-codes",
              "code": "pulmonary-lobectomy"
            }
          ]
        },
        "status": "completed",
        "extension": [
          {
            "url": "http://localhost:3456/api/terminology/StructureDefinition/cnwqk85-procedure-priority",
            "valueCodeableConcept": {
              "coding": [
                {
                  "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk85-priority-codes",
                  "code": "elective"
                }
              ]
            }
          },
          {
            "url": "http://localhost:3456/api/terminology/StructureDefinition/cnwqk85-surgical-approach",
            "valueCodeableConcept": {
              "coding": [
                {
                  "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk85-approach-codes",
                  "code": "thoracoscopic"
                }
              ]
            }
          }
        ],
        "performedDateTime": "2026-10-09",
        "text": {
          "status": "generated",
          "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">择期已完成胸腔镜肺叶切除术。择期已完成胸腔镜肺叶切除术。择期已完成胸腔镜肺叶切除术</div>"
        },
        "category": {
          "coding": [
            {
              "system": "http://terminology.hl7.org/CodeSystem/procedure-category",
              "code": "surgery"
            }
          ]
        }
      },
      "request": {
        "method": "POST",
        "url": "Procedure"
      }
    }
  ]
}
```

Original FSH constraints:
```fsh
* status = #planned (exactly)
```

Detected violations:
- cnwqk85-lung-resection: status fixed=planned, actual=completed

## 205_completed

Profile: 205; known contract conflict: YES; safely fully repairable: NO.

Input evidence:
```json
[
  {
    "text": "择期已完成全麻下胸部手术",
    "timestamp": "2026-10-09"
  }
]
```

Actual B2E FHIR:
```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "resource": {
        "resourceType": "Procedure",
        "id": "1fb8a33a-3fb9-4cc1-bf4f-eeecbdd07696",
        "meta": {
          "profile": [
            "http://localhost:3456/api/terminology/Profile/cnwqk205-thoracic-surgery"
          ]
        },
        "subject": {
          "reference": "Patient/p1"
        },
        "code": {
          "coding": [
            {
              "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk205-thoracic-surgery-cs",
              "code": "pulmonary"
            }
          ]
        },
        "status": "completed",
        "extension": [
          {
            "url": "http://localhost:3456/api/terminology/StructureDefinition/anesthesia-method",
            "valueCodeableConcept": {
              "coding": [
                {
                  "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk205-anesthesia-method-cs",
                  "code": "GA"
                }
              ]
            }
          },
          {
            "url": "http://localhost:3456/api/terminology/StructureDefinition/anesthesia-depth",
            "valueCodeableConcept": {
              "coding": [
                {
                  "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk205-anesthesia-depth-cs",
                  "code": "GA"
                }
              ]
            }
          }
        ],
        "performedDateTime": "2026-10-09",
        "text": {
          "status": "generated",
          "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">择期已完成全麻下胸部手术。择期已完成全麻下胸部手术。择期已完成全麻下胸部手术</div>"
        }
      },
      "request": {
        "method": "POST",
        "url": "Procedure"
      }
    }
  ]
}
```

Original FSH constraints:
```fsh
* status = #planned (exactly)  // 择期手术状态
```

Detected violations:
- cnwqk205-thoracic-surgery: status fixed=planned, actual=completed

## 205_planned

Profile: 205; known contract conflict: YES; safely fully repairable: NO.

Input evidence:
```json
[
  {
    "text": "拟择期全麻下胸部手术",
    "timestamp": "2026-10-09"
  }
]
```

Actual B2E FHIR:
```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "resource": {
        "resourceType": "Procedure",
        "id": "b3023a8e-888c-4c8c-86aa-8db6fb1d64ae",
        "meta": {
          "profile": [
            "http://localhost:3456/api/terminology/Profile/cnwqk205-thoracic-surgery"
          ]
        },
        "subject": {
          "reference": "Patient/p1"
        },
        "code": {
          "coding": [
            {
              "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk205-thoracic-surgery-cs",
              "code": "pulmonary"
            }
          ]
        },
        "status": "preparation",
        "extension": [
          {
            "url": "http://localhost:3456/api/terminology/StructureDefinition/anesthesia-method",
            "valueCodeableConcept": {
              "coding": [
                {
                  "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk205-anesthesia-method-cs",
                  "code": "GA"
                }
              ]
            }
          },
          {
            "url": "http://localhost:3456/api/terminology/StructureDefinition/anesthesia-depth",
            "valueCodeableConcept": {
              "coding": [
                {
                  "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk205-anesthesia-depth-cs",
                  "code": "GA"
                }
              ]
            }
          }
        ],
        "text": {
          "status": "generated",
          "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">拟择期全麻下胸部手术。拟择期全麻下胸部手术。拟择期全麻下胸部手术</div>"
        }
      },
      "request": {
        "method": "POST",
        "url": "Procedure"
      }
    }
  ]
}
```

Original FSH constraints:
```fsh
* status = #planned (exactly)  // 择期手术状态
```

Detected violations:
- cnwqk205-thoracic-surgery: status fixed=planned, actual=preparation

## 205_good_and_emergency

Profile: 205; known contract conflict: YES; safely fully repairable: NO.

Input evidence:
```json
[
  {
    "text": "择期已完成全麻下胸部手术",
    "timestamp": "2026-10-09",
    "event_id": "a"
  },
  {
    "text": "急诊开胸肺切除术全麻",
    "timestamp": "2026-10-09",
    "event_id": "b"
  }
]
```

Actual B2E FHIR:
```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "resource": {
        "resourceType": "Procedure",
        "id": "0e99a335-e139-4614-8916-964ad04912e6",
        "meta": {
          "profile": [
            "http://localhost:3456/api/terminology/Profile/cnwqk205-thoracic-surgery"
          ]
        },
        "subject": {
          "reference": "Patient/p1"
        },
        "code": {
          "coding": [
            {
              "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk205-thoracic-surgery-cs",
              "code": "pulmonary"
            }
          ]
        },
        "status": "completed",
        "extension": [
          {
            "url": "http://localhost:3456/api/terminology/StructureDefinition/anesthesia-method",
            "valueCodeableConcept": {
              "coding": [
                {
                  "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk205-anesthesia-method-cs",
                  "code": "GA"
                }
              ]
            }
          },
          {
            "url": "http://localhost:3456/api/terminology/StructureDefinition/anesthesia-depth",
            "valueCodeableConcept": {
              "coding": [
                {
                  "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk205-anesthesia-depth-cs",
                  "code": "GA"
                }
              ]
            }
          }
        ],
        "performedDateTime": "2026-10-09",
        "text": {
          "status": "generated",
          "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">择期已完成全麻下胸部手术。择期已完成全麻下胸部手术。择期已完成全麻下胸部手术</div>"
        }
      },
      "request": {
        "method": "POST",
        "url": "Procedure"
      }
    }
  ]
}
```

Original FSH constraints:
```fsh
* status = #planned (exactly)  // 择期手术状态
```

Detected violations:
- cnwqk205-thoracic-surgery: status fixed=planned, actual=completed

## 225_ongoing

Profile: 225; known contract conflict: YES; safely fully repairable: NO.

Input evidence:
```json
[
  {
    "text": "正在接受放疗",
    "timestamp": "2026-10-09"
  }
]
```

Actual B2E FHIR:
```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "resource": {
        "resourceType": "Procedure",
        "id": "99f03e59-a595-47ea-bb27-4c5896656570",
        "meta": {
          "profile": [
            "http://localhost:3456/api/terminology/Profile/cnwqk225-radiotherapy-procedure"
          ]
        },
        "subject": {
          "reference": "Patient/p1"
        },
        "code": {
          "coding": [
            {
              "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk225-radiotherapy-cs",
              "code": "radiotherapy"
            }
          ]
        },
        "status": "in-progress",
        "text": {
          "status": "generated",
          "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">正在接受放疗</div>"
        }
      },
      "request": {
        "method": "POST",
        "url": "Procedure"
      }
    }
  ]
}
```

Original FSH constraints:
```fsh
* status = #completed (exactly)
* performedDateTime 1..1
```

Detected violations:
- cnwqk225-radiotherapy-procedure: required performedDateTime
- cnwqk225-radiotherapy-procedure: status fixed=completed, actual=in-progress
