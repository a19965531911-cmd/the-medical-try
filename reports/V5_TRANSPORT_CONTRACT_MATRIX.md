# V5 Transport Contract Matrix

| criterion | resourceType | profile | minimum fields | numeric | referenceRange | relation | generic insufficient | selected source |
|---|---|---|---|---:|---:|---:|---:|---|
| 485 | Observation | http://localhost:3456/api/terminology/Profile/cnwqk485-popq-assessment | status, subject, code, valueCodeableConcept | false | false | false | false | V2.4.3 |
| 615 | Observation | http://localhost:3456/api/terminology/Profile/cnwqk615-pathological-t-stage-observation | status, subject, code | true | false | false | true | V2.4.3 |
| 265 | Observation | http://localhost:3456/api/terminology/Profile/cnwqk265-serum-cardiac-troponin-observation | status, subject, code, effectiveDateTime, valueQuantity | true | false | false | true | V2.4.3 |
| 635 | Observation | http://localhost:3456/api/terminology/Profile/cnwqk635-LaboratoryExaminationProfile | status, subject, code, valueQuantity, referenceRange | true | true | false | true | V2.4.3 |
| 675 | Condition | http://localhost:3456/api/terminology/Profile/cnwqk675-head-facial-herpes-zoster-condition | subject, clinicalStatus, verificationStatus, code, bodySite | false | false | false | false | V4 |
| 735 | Condition | http://localhost:3456/api/terminology/StructureDefinition/cnwqk735-nonneoplasm-disease-stage | subject, code, clinicalStatus | false | false | false | false | V2.4.3 |
| 745 | Procedure | http://localhost:3456/api/terminology/Profile/cnwqk745-postop-mechanical-ventilation | status, subject, code, performedDateTime, partOf | false | false | true | true | V4 |
| 755 | Procedure | http://localhost:3456/api/terminology/Profile/cnwqk755-MechanicalVentilationProcedure | status, subject, code, performedPeriod | true | false | false | true | V2.4.3 |
| 855 | Observation | http://localhost:3456/api/terminology/Profile/cnwqk855-serum-creatinine-observation | status, subject, code, valueQuantity | true | true | false | true | V2.4.3 |
| 835 | Observation | http://localhost:3456/api/terminology/Profile/cnwqk835-OrganOrTissueStatus | status, subject, code, valueCodeableConcept | false | false | false | false | V2.4.3 |
| 875 | Observation | http://localhost:3456/api/terminology/Profile/cnwqk875-intracranialhypertension-profile | status, subject, code, effectiveDateTime, valueCodeableConcept | false | false | false | false | V4 |
| 805 | Observation | http://localhost:3456/api/terminology/Profile/cnwqk805-SmokingStatusObservation | status, subject, code, valueCodeableConcept | true | false | false | true | V2.4.3 |
| 565 | Observation | http://localhost:3456/api/terminology/Profile/cnwqk565-symptomobservation | status, subject, code, extension | false | false | false | false | V2.4.3 |
| 555 | Procedure | http://localhost:3456/api/terminology/Profile/cnwqk555-SurgeryHistoryProfile | status, subject, code, performedDateTime | false | false | false | false | V2.4.3 |
| 185 | MedicationAdministration | http://localhost:3456/api/terminology/Profile/cnwqk185-chemotherapy-administration | status, subject, medicationCodeableConcept, effectiveDateTime, dosage, extension | false | false | false | false | V4 |
| 165 | Procedure | http://localhost:3456/api/terminology/Profile/cnwqk165-chemotherapy-history | status, subject, code, extension | false | false | false | false | V2.4.3 |

| criterion | status |
|---|---|
| 485 | audited |
| 615 | audited |
| 265 | audited |
| 635 | audited |
| 675 | audited |
| 735 | audited |
| 745 | audited |
| 755 | audited |
| 855 | audited |
| 835 | audited |
| 875 | audited |
| 805 | audited |
| 565 | audited |
| 555 | audited |
| 185 | audited |
| 165 | audited |
