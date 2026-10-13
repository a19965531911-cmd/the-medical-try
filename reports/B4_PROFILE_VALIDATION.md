# B4 Profile Validation

Local R4 and FSH checks are existing partial validators, not a complete FHIR validator or official checker.
FSH conflicts cannot be removed by changing plans to completed or inventing missing OR components. No such repair was applied.
Profile 85/205 FSH fixes Procedure.status=planned, absent from R4 ProcedureStatus. 225 ongoing conflicts with completed plus performedDateTime. 295 requires both components although criterion is OR.
Original B2E 18 cases remain visible. Detailed B4F evidence/resources and Service replay follow. All reported 'not safely repairable' cases require contract clarification.

## 85_positive_0

Profile ID: 85
Safely fully repairable: NO with the currently available evidence/contract; no invented facts or status changes.
Actual Service hit with preserved resource: True
Violations: cnwqk85-lung-resection: status fixed=planned, actual=preparation
```json
{
  "original_evidence": [
    {
      "text": "拟择期行胸腔镜肺叶切除术",
      "timestamp": "2026-10-09T12:00:00+08:00",
      "topic": "手术记录"
    }
  ],
  "actual_resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Procedure",
          "id": "bfdca1d7-c50b-4c0c-b488-e4d311f02a05",
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
}
```

## 85_positive_1

Profile ID: 85
Safely fully repairable: NO with the currently available evidence/contract; no invented facts or status changes.
Actual Service hit with preserved resource: True
Violations: cnwqk85-lung-resection: status fixed=planned, actual=preparation
```json
{
  "original_evidence": [
    {
      "text": "计划VATS肺段切除术",
      "timestamp": "2026-10-09T12:00:00+08:00",
      "topic": "手术记录"
    }
  ],
  "actual_resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Procedure",
          "id": "5a87db62-8c4d-4551-ad0e-e851bec1face",
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
}
```

## 85_positive_2

Profile ID: 85
Safely fully repairable: NO with the currently available evidence/contract; no invented facts or status changes.
Actual Service hit with preserved resource: True
Violations: cnwqk85-lung-resection: status fixed=planned, actual=preparation
```json
{
  "original_evidence": [
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
  ],
  "actual_resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Procedure",
          "id": "1f1f9f65-3cc6-427b-a3c8-d6c6fe39f612",
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
}
```

## 205_positive_0

Profile ID: 205
Safely fully repairable: NO with the currently available evidence/contract; no invented facts or status changes.
Actual Service hit with preserved resource: True
Violations: cnwqk205-thoracic-surgery: status fixed=planned, actual=preparation
```json
{
  "original_evidence": [
    {
      "text": "拟择期全麻下胸部手术",
      "timestamp": "2026-10-09T12:00:00+08:00",
      "topic": "手术记录"
    }
  ],
  "actual_resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Procedure",
          "id": "6315df5a-f0ff-4015-a974-c88c03c55c35",
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
}
```

## 205_positive_1

Profile ID: 205
Safely fully repairable: NO with the currently available evidence/contract; no invented facts or status changes.
Actual Service hit with preserved resource: True
Violations: cnwqk205-thoracic-surgery: status fixed=planned, actual=preparation
```json
{
  "original_evidence": [
    {
      "text": "计划全身麻醉下肺叶切除术",
      "timestamp": "2026-10-09T12:00:00+08:00",
      "topic": "手术记录"
    }
  ],
  "actual_resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Procedure",
          "id": "ac18ae07-e221-4af7-90c0-8e49f45cac69",
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
}
```

## 205_positive_2

Profile ID: 205
Safely fully repairable: NO with the currently available evidence/contract; no invented facts or status changes.
Actual Service hit with preserved resource: True
Violations: cnwqk205-thoracic-surgery: status fixed=planned, actual=completed
```json
{
  "original_evidence": [
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
  ],
  "actual_resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Procedure",
          "id": "db77b07f-b56d-4b77-ac06-e912856b53b4",
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
}
```

## 295_positive_0

Profile ID: 295
Safely fully repairable: NO with the currently available evidence/contract; no invented facts or status changes.
Actual Service hit with preserved resource: True
Violations: cnwqk295-smokingstatus: required component; 295 required slice smoking-cessation-guarantee
```json
{
  "original_evidence": [
    {
      "text": "目前每天吸烟20支",
      "timestamp": "2026-10-09T12:00:00+08:00",
      "topic": "个人史"
    }
  ],
  "actual_resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Observation",
          "id": "1aa9a9bc-a9b9-4784-a59a-271a3135a8a7",
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
}
```

## 295_positive_1

Profile ID: 295
Safely fully repairable: NO with the currently available evidence/contract; no invented facts or status changes.
Actual Service hit with preserved resource: True
Violations: cnwqk295-smokingstatus: required component; 295 required slice smoking-cessation-guarantee
```json
{
  "original_evidence": [
    {
      "text": "现吸烟1包/日",
      "timestamp": "2026-10-09T12:00:00+08:00",
      "topic": "个人史"
    }
  ],
  "actual_resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Observation",
          "id": "bf4ff3e4-9978-4935-a48c-d50fcdb73aee",
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
}
```

## 295_positive_2

Profile ID: 295
Safely fully repairable: NO with the currently available evidence/contract; no invented facts or status changes.
Actual Service hit with preserved resource: True
Violations: cnwqk295-smokingstatus: required component; 295 required slice smoking-cessation-guarantee
```json
{
  "original_evidence": [
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
  ],
  "actual_resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Observation",
          "id": "6ef3e5b1-8d45-43ab-ab5c-97a7e72c762e",
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
}
```

## 295_quantity_only

Profile ID: 295
Safely fully repairable: NO with the currently available evidence/contract; no invented facts or status changes.
Actual Service hit with preserved resource: True
Violations: cnwqk295-smokingstatus: required component; 295 required slice smoking-cessation-guarantee
```json
{
  "original_evidence": [
    {
      "text": "目前每天吸烟20支",
      "timestamp": "2026-10-09"
    }
  ],
  "actual_resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Observation",
          "id": "c97b0955-6d39-42ca-8109-fb5c3da8e5c9",
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
}
```

## 295_refusal_only

Profile ID: 295
Safely fully repairable: NO with the currently available evidence/contract; no invented facts or status changes.
Actual Service hit with preserved resource: True
Violations: cnwqk295-smokingstatus: required component; 295 required slice number-of-cigarettes-per-day
```json
{
  "original_evidence": [
    {
      "text": "不能保证试验期间停止吸烟",
      "timestamp": "2026-10-09"
    }
  ],
  "actual_resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Observation",
          "id": "8649c72a-7b1d-4bf3-b20c-6a03db7b7e21",
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
}
```

## 85_completed

Profile ID: 85
Safely fully repairable: NO with the currently available evidence/contract; no invented facts or status changes.
Actual Service hit with preserved resource: True
Violations: cnwqk85-lung-resection: status fixed=planned, actual=completed
```json
{
  "original_evidence": [
    {
      "text": "择期已完成胸腔镜肺叶切除术",
      "timestamp": "2026-10-09"
    }
  ],
  "actual_resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Procedure",
          "id": "08b8fba1-faf5-4aed-8a2a-870a116aecba",
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
}
```

## 85_planned

Profile ID: 85
Safely fully repairable: NO with the currently available evidence/contract; no invented facts or status changes.
Actual Service hit with preserved resource: True
Violations: cnwqk85-lung-resection: status fixed=planned, actual=preparation
```json
{
  "original_evidence": [
    {
      "text": "拟择期胸腔镜肺叶切除术",
      "timestamp": "2026-10-09"
    }
  ],
  "actual_resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Procedure",
          "id": "a99455a7-affc-4fe7-b30e-4f90e0f47828",
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
}
```

## 85_good_and_emergency

Profile ID: 85
Safely fully repairable: NO with the currently available evidence/contract; no invented facts or status changes.
Actual Service hit with preserved resource: True
Violations: cnwqk85-lung-resection: status fixed=planned, actual=completed
```json
{
  "original_evidence": [
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
  ],
  "actual_resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Procedure",
          "id": "6e6d2233-5be2-47fc-b32a-8547e2c97218",
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
}
```

## 205_completed

Profile ID: 205
Safely fully repairable: NO with the currently available evidence/contract; no invented facts or status changes.
Actual Service hit with preserved resource: True
Violations: cnwqk205-thoracic-surgery: status fixed=planned, actual=completed
```json
{
  "original_evidence": [
    {
      "text": "择期已完成全麻下胸部手术",
      "timestamp": "2026-10-09"
    }
  ],
  "actual_resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Procedure",
          "id": "73d83355-d04d-4244-b69b-4a524c0f76bb",
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
}
```

## 205_planned

Profile ID: 205
Safely fully repairable: NO with the currently available evidence/contract; no invented facts or status changes.
Actual Service hit with preserved resource: True
Violations: cnwqk205-thoracic-surgery: status fixed=planned, actual=preparation
```json
{
  "original_evidence": [
    {
      "text": "拟择期全麻下胸部手术",
      "timestamp": "2026-10-09"
    }
  ],
  "actual_resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Procedure",
          "id": "b8316794-797d-4a35-bfd5-df712361d0b3",
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
}
```

## 205_good_and_emergency

Profile ID: 205
Safely fully repairable: NO with the currently available evidence/contract; no invented facts or status changes.
Actual Service hit with preserved resource: True
Violations: cnwqk205-thoracic-surgery: status fixed=planned, actual=completed
```json
{
  "original_evidence": [
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
  ],
  "actual_resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Procedure",
          "id": "72dcdcfa-609a-4bc0-ae42-7f259b2839d4",
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
}
```

## 225_ongoing

Profile ID: 225
Safely fully repairable: NO with the currently available evidence/contract; no invented facts or status changes.
Actual Service hit with preserved resource: True
Violations: cnwqk225-radiotherapy-procedure: required performedDateTime; cnwqk225-radiotherapy-procedure: status fixed=completed, actual=in-progress
```json
{
  "original_evidence": [
    {
      "text": "正在接受放疗",
      "timestamp": "2026-10-09"
    }
  ],
  "actual_resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Procedure",
          "id": "ca5b6c23-b16d-4c78-a8a5-52b1019605a9",
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
}
```
