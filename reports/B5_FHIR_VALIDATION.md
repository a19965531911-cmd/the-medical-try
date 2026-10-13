# B5 FHIR Validation

Same existing R4/FSH subset validators and unmodified workbook Service replay; complete FHIR/FSH validator unavailable. Full profiles and official checker remain unverified.
167 legacy cases replayed using B5-R: known FSH-invalid case count=18. No incompatible status or invented components were added to pass profiles.
85/205 FSH status planned is outside R4 ProcedureStatus; preparation/completed reflects evidence. 225 ongoing cannot be relabelled completed or assigned invented completion time. 295 OR cannot fill both required component slices when only one exists. 625 retains complete same-encounter panel and original numeric/ULN evidence; Service's looser pooled semantics do not certify truth.

## 85_positive_0
Profile 85; Service hit=True; safely fully repairable=NO without new source evidence/official contract.
Violation: cnwqk85-lung-resection: status fixed=planned, actual=preparation
```json
{
  "reports": [
    {
      "text": "拟择期行胸腔镜肺叶切除术",
      "timestamp": "2026-10-09T12:00:00+08:00",
      "topic": "手术记录"
    }
  ],
  "resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Procedure",
          "id": "608892d4-1905-40d5-9634-0a14a61093f1",
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
Profile 85; Service hit=True; safely fully repairable=NO without new source evidence/official contract.
Violation: cnwqk85-lung-resection: status fixed=planned, actual=preparation
```json
{
  "reports": [
    {
      "text": "计划VATS肺段切除术",
      "timestamp": "2026-10-09T12:00:00+08:00",
      "topic": "手术记录"
    }
  ],
  "resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Procedure",
          "id": "770dc859-fc8b-48a0-85e9-42e94258298a",
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
Profile 85; Service hit=True; safely fully repairable=NO without new source evidence/official contract.
Violation: cnwqk85-lung-resection: status fixed=planned, actual=preparation
```json
{
  "reports": [
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
  "resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Procedure",
          "id": "163e82e5-eef5-4b6d-bd0c-a61277e33ef2",
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
Profile 205; Service hit=True; safely fully repairable=NO without new source evidence/official contract.
Violation: cnwqk205-thoracic-surgery: status fixed=planned, actual=preparation
```json
{
  "reports": [
    {
      "text": "拟择期全麻下胸部手术",
      "timestamp": "2026-10-09T12:00:00+08:00",
      "topic": "手术记录"
    }
  ],
  "resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Procedure",
          "id": "204344a0-9ea8-4f68-a140-00e75c7b4274",
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
Profile 205; Service hit=True; safely fully repairable=NO without new source evidence/official contract.
Violation: cnwqk205-thoracic-surgery: status fixed=planned, actual=preparation
```json
{
  "reports": [
    {
      "text": "计划全身麻醉下肺叶切除术",
      "timestamp": "2026-10-09T12:00:00+08:00",
      "topic": "手术记录"
    }
  ],
  "resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Procedure",
          "id": "36f9f2e2-8ff4-4aba-a047-32da09768310",
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
Profile 205; Service hit=True; safely fully repairable=NO without new source evidence/official contract.
Violation: cnwqk205-thoracic-surgery: status fixed=planned, actual=completed
```json
{
  "reports": [
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
  "resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Procedure",
          "id": "0ed063cf-c119-412d-b1e2-582567d2a5c3",
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
Profile 295; Service hit=True; safely fully repairable=NO without new source evidence/official contract.
Violation: cnwqk295-smokingstatus: required component; 295 required slice smoking-cessation-guarantee
```json
{
  "reports": [
    {
      "text": "目前每天吸烟20支",
      "timestamp": "2026-10-09T12:00:00+08:00",
      "topic": "个人史"
    }
  ],
  "resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Observation",
          "id": "71f66657-7678-4ad9-a2b3-f555bd346c45",
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
Profile 295; Service hit=True; safely fully repairable=NO without new source evidence/official contract.
Violation: cnwqk295-smokingstatus: required component; 295 required slice smoking-cessation-guarantee
```json
{
  "reports": [
    {
      "text": "现吸烟1包/日",
      "timestamp": "2026-10-09T12:00:00+08:00",
      "topic": "个人史"
    }
  ],
  "resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Observation",
          "id": "3ec0bf0d-c01f-4a75-aa38-4f6acc571903",
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
Profile 295; Service hit=True; safely fully repairable=NO without new source evidence/official contract.
Violation: cnwqk295-smokingstatus: required component; 295 required slice smoking-cessation-guarantee
```json
{
  "reports": [
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
  "resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Observation",
          "id": "0a0e86ff-6e2d-4301-a3f3-e116973c206e",
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
Profile 295; Service hit=True; safely fully repairable=NO without new source evidence/official contract.
Violation: cnwqk295-smokingstatus: required component; 295 required slice smoking-cessation-guarantee
```json
{
  "reports": [
    {
      "text": "目前每天吸烟20支",
      "timestamp": "2026-10-09"
    }
  ],
  "resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Observation",
          "id": "f81825f9-5950-45e2-a135-2f6f909a7267",
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
Profile 295; Service hit=True; safely fully repairable=NO without new source evidence/official contract.
Violation: cnwqk295-smokingstatus: required component; 295 required slice number-of-cigarettes-per-day
```json
{
  "reports": [
    {
      "text": "不能保证试验期间停止吸烟",
      "timestamp": "2026-10-09"
    }
  ],
  "resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Observation",
          "id": "337c8ce5-6e46-4eb6-a4aa-8bebf5446d14",
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
Profile 85; Service hit=True; safely fully repairable=NO without new source evidence/official contract.
Violation: cnwqk85-lung-resection: status fixed=planned, actual=completed
```json
{
  "reports": [
    {
      "text": "择期已完成胸腔镜肺叶切除术",
      "timestamp": "2026-10-09"
    }
  ],
  "resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Procedure",
          "id": "8f3b1829-be4d-4d6f-97e9-d04bed758f2a",
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
Profile 85; Service hit=True; safely fully repairable=NO without new source evidence/official contract.
Violation: cnwqk85-lung-resection: status fixed=planned, actual=preparation
```json
{
  "reports": [
    {
      "text": "拟择期胸腔镜肺叶切除术",
      "timestamp": "2026-10-09"
    }
  ],
  "resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Procedure",
          "id": "3ae9293c-af0b-4ee7-ad70-c2b7b549af42",
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
Profile 85; Service hit=True; safely fully repairable=NO without new source evidence/official contract.
Violation: cnwqk85-lung-resection: status fixed=planned, actual=completed
```json
{
  "reports": [
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
  "resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Procedure",
          "id": "3351de74-dac5-4d0e-a3cd-66ffeb7a5986",
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
Profile 205; Service hit=True; safely fully repairable=NO without new source evidence/official contract.
Violation: cnwqk205-thoracic-surgery: status fixed=planned, actual=completed
```json
{
  "reports": [
    {
      "text": "择期已完成全麻下胸部手术",
      "timestamp": "2026-10-09"
    }
  ],
  "resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Procedure",
          "id": "685fb337-38b7-412b-8b36-72016c03c8b1",
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
Profile 205; Service hit=True; safely fully repairable=NO without new source evidence/official contract.
Violation: cnwqk205-thoracic-surgery: status fixed=planned, actual=preparation
```json
{
  "reports": [
    {
      "text": "拟择期全麻下胸部手术",
      "timestamp": "2026-10-09"
    }
  ],
  "resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Procedure",
          "id": "cd9d64f2-9c3e-46ee-ae95-99661346ebdb",
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
Profile 205; Service hit=True; safely fully repairable=NO without new source evidence/official contract.
Violation: cnwqk205-thoracic-surgery: status fixed=planned, actual=completed
```json
{
  "reports": [
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
  "resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Procedure",
          "id": "6f297260-6b6f-412c-b89b-8690b2490b46",
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
Profile 225; Service hit=True; safely fully repairable=NO without new source evidence/official contract.
Violation: cnwqk225-radiotherapy-procedure: required performedDateTime; cnwqk225-radiotherapy-procedure: status fixed=completed, actual=in-progress
```json
{
  "reports": [
    {
      "text": "正在接受放疗",
      "timestamp": "2026-10-09"
    }
  ],
  "resources": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Procedure",
          "id": "217dd0ca-754c-482b-83c3-4fb16f43e725",
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
