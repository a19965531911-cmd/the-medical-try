from v43.fhir.contracts import BASE, contract_for_criterion

from .payload_extractors import PayloadResult


def _concept(system, code): return {"coding": [{"system": system, "code": code}]}
def _base(kind, profile, patient): return {"resourceType":kind,"meta":{"profile":[profile]},"subject":{"reference":"Patient/"+patient}}


def build_resources(criterion_id: str, patient_id: str, payload: PayloadResult) -> tuple[dict, ...]:
    if payload.status != "READY": return ()
    cid=str(criterion_id); contract=contract_for_criterion(cid); profile=contract.profiles[0]; t=payload.values.get("time","2026-01-01T00:00:00Z")
    r=_base(contract.resource_type,profile,patient_id)
    if contract.resource_type == "Observation": r["status"]="final"
    elif contract.resource_type in {"Procedure","MedicationAdministration"}: r["status"]="completed"
    if cid == "185":
        r.update({"medicationCodeableConcept":_concept(BASE+"CodeSystem/cnwqk185-custom-cs","cnwqk185-drug-irinotecan"),"effectiveDateTime":t,"dosage":{"text":"first irinotecan administration"},"extension":[{"url":BASE+"Extension/cnwqk185-application-order","valueCode":"cnwqk185-application-first"}]})
    elif cid == "675":
        r.update({"clinicalStatus":_concept("http://terminology.hl7.org/CodeSystem/condition-clinical","active"),"verificationStatus":_concept("http://terminology.hl7.org/CodeSystem/condition-ver-status","confirmed"),"code":_concept(BASE+"CodeSystem/icd10","B02.9"),"bodySite":[_concept(BASE+"CodeSystem/cnwqk675-head-facial-body-site-cs",payload.values["site"])]})
    elif cid == "745":
        parent=_base("Procedure","",patient_id); parent.pop("meta"); parent.update({"id":"surgery-1","status":"completed","code":{"text":"surgery"},"performedDateTime":t})
        r.update({"code":_concept(BASE+"CodeSystem/cnwqk745-procedure-type-cs","invasive_mechanical_ventilation"),"performedDateTime":t,"partOf":[{"reference":"Procedure/surgery-1"}]})
        return (parent,r)
    elif cid == "875":
        code="intracranial-hypertension" if payload.values["condition"] == "intracranial" else "unconsciousness"
        system=BASE+("CodeSystem/cnwqk875-intracranialhypertension-cs" if payload.values["condition"] == "intracranial" else "CodeSystem/cnwqk875-unconsciousness-cs")
        r.update({"code":_concept(system,code),"effectiveDateTime":t,"valueCodeableConcept":_concept(BASE+"CodeSystem/cnwqk875-presence-cs","present")})
    elif cid == "635":
        out=[]
        for lab,(value,high) in payload.values["labs"].items():
            item=_base("Observation",profile,patient_id); item.update({"status":"final","code":_concept(BASE+"CodeSystem/cnwqk635-LaboratoryTestsCS",lab),"effectiveDateTime":t,"valueQuantity":{"value":value,"unit":"unit"},"referenceRange":[{"high":{"value":high,"unit":"unit"}}]}); out.append(item)
        return tuple(out)
    else:
        r["code"]=_concept(BASE+f"CodeSystem/cnwqk{cid}-codes",cid)
        if cid == "165": r["extension"]=[{"url":BASE+"StructureDefinition/cnwqk165-treatment-location","valueCode":"external"}]
        elif cid in {"265","855"}: r.update({"effectiveDateTime":t,"valueQuantity":{"value":payload.values.get("number",1),"unit":"score"}})
        elif cid == "485": r["valueCodeableConcept"]=_concept(BASE+"CodeSystem/cnwqk485-popq-grade-cs","III")
        elif cid == "555": r["performedDateTime"]=t
        elif cid == "565": r["extension"]=[{"url":BASE+"Extension/cnwqk565-observation-severity-ext","valueCodeableConcept":_concept(BASE+"CodeSystem/cnwqk565-symptomseverity-cs","severe")}]
        elif cid == "615":
            index={"pT":0,"R1":1,"pN1":2,"GS":3,"PSA":4}[payload.values["branch"]]; r["meta"]["profile"]=[contract.profiles[index]]; r["valueQuantity"]={"value":payload.values.get("number",1),"unit":"score"}
        elif cid == "735": r["clinicalStatus"]=_concept("http://terminology.hl7.org/CodeSystem/condition-clinical","active")
        elif cid == "755": r["performedPeriod"]={"start":t,"end":t}
        elif cid == "805": r["valueCodeableConcept"]=_concept(BASE+"CodeSystem/cnwqk805-SmokingStatusCS",payload.values["smoking"])
        elif cid == "835": r["valueCodeableConcept"]=_concept(BASE+"CodeSystem/cnwqk835-AbnormalityStatusCS","abnormal")
    return (r,)

