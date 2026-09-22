"""Transport-only overlay appended to frozen V5S.1 target libraries."""


OVERLAY_SOURCE = r'''

# Experiment C: legacy scorer transport. Frozen decision functions above remain authoritative.
from datetime import datetime,timezone,timedelta

_frozen_build_resources=build_resources
_FrozenGenerator=FHIRResourceBundleGenerator

def parse_datetime(value):
    return datetime.fromisoformat(str(value).replace("Z","+00:00"))

def canonical_datetime(value):
    return parse_datetime(value).astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z")

def hours_before(value,hours):
    return (parse_datetime(value)-timedelta(hours=hours)).astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z")

def months_before(value,months):
    dt=parse_datetime(value);whole=int(months);month_index=dt.year*12+dt.month-1-whole;year,month=divmod(month_index,12);month+=1
    leap=year%4==0 and (year%100!=0 or year%400==0);days=[31,29 if leap else 28,31,30,31,30,31,31,30,31,30,31]
    shifted=dt.replace(year=year,month=month,day=min(dt.day,days[month-1]))-timedelta(days=(months-whole)*30.4375)
    return shifted.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z")

def _transport_timestamp(reports,windows):
    report_ids=[w.get("report") for w in windows]
    for report_id in report_ids:
        for report in reports:
            if report.get("index")==report_id and report.get("timestamp"):
                return report["timestamp"]
    return None

def derive_transport_meta(cid,reports,windows,values):
    if values is None:return None
    text=" ".join(w.get("text","") for w in windows)
    meta={"timestamp":_transport_timestamp(reports,windows)}
    if cid=="265":
        match=re.search(r"(cTnI|cTnT|\u808c\u9499\u86cb\u767d[IT])\s*[:\uff1a=]?\s*(\d+(?:\.\d+)?)",text,re.I)
        if match:
            meta["analyte"]="cTnT" if match.group(1).lower() in ("ctnt","\u808c\u9499\u86cb\u767dt") else "cTnI"
    if cid=="555":
        match=re.search(r"(\d+)\s*\u4e2a?\u6708\u524d.*(?:\u624b\u672f|\u5207\u9664)",text)
        if match:meta["relative_months"]=float(match.group(1))
    if cid=="755":meta["duration_hours"]=values.get("duration_hours")
    if cid=="805":
        match=re.search(r"(?:\u6212\u70df|quit)\s*(\d+(?:\.\d+)?)\s*(?:\u5e74|years?)",text,re.I)
        if match:meta["cessation_months"]=float(match.group(1))*12
    if cid=="855":meta["labs"]=_labs_855(text)
    return meta

def _expc_observation(patient,profile,code,value,unit,ucum,timestamp=None):
    resource=_base("Observation",profile,patient)
    resource.update({"status":"final","code":_concept("http://loinc.org",code),"valueQuantity":{"value":value,"unit":unit,"system":"http://unitsofmeasure.org","code":ucum}})
    if timestamp:resource["effectiveDateTime"]=canonical_datetime(timestamp)
    return resource

def build_expc_resources(cid,patient,values,transport_meta):
    if values is None or transport_meta is None:return []
    timestamp=transport_meta.get("timestamp")
    if cid=="265":
        analyte=transport_meta.get("analyte")
        if analyte not in ("cTnI","cTnT") or "number" not in values:return []
        loinc="10839-9" if analyte=="cTnI" else "6598-7"
        resource=_base("Observation",BASE+"Profile/cnwqk265-serum-cardiac-troponin-observation",patient)
        resource["meta"]["profile"].append(BASE+"Profile/cnwqk265-preoperative-cardiac-troponin-observation")
        resource.update({"status":"final","category":[_concept("http://terminology.hl7.org/CodeSystem/observation-category","laboratory")],"code":{"coding":[{"system":BASE+"CodeSystem/cnwqk265-cardiac-troponin-tests","code":analyte},{"system":"http://loinc.org","code":loinc}],"text":analyte},"valueQuantity":{"value":values["number"],"unit":"ug/L","system":"http://unitsofmeasure.org","code":"ug/L"},"extension":[{"url":BASE+"Extension/cnwqk265-preoperative-extension","valueBoolean":True}]})
        if timestamp:resource["effectiveDateTime"]=canonical_datetime(timestamp)
        return [resource]
    if cid=="555":
        months=transport_meta.get("relative_months")
        if timestamp is None or months is None:return []
        resource=_base("Procedure",BASE+"Profile/cnwqk555-SurgeryHistoryProfile",patient)
        resource.update({"status":"completed","code":_concept(BASE+"CodeSystem/cnwqk555-SurgeryProcedureCS","surgery"),"performedDateTime":months_before(timestamp,months)})
        return [resource]
    if cid=="755":
        hours=transport_meta.get("duration_hours")
        if timestamp is None or hours is None:return []
        resource=_base("Procedure",BASE+"Profile/cnwqk755-MechanicalVentilationProcedure",patient)
        resource.update({"status":"completed","code":_concept(BASE+"CodeSystem/cnwqk755-MechanicalVentilationCodes","mechanical-ventilation"),"performedPeriod":{"start":hours_before(timestamp,hours),"end":canonical_datetime(timestamp)}})
        return [resource]
    if cid=="805":
        status=values.get("smoking","current-smoker")
        smoking=_base("Observation",BASE+"Profile/cnwqk805-SmokingStatusObservation",patient)
        smoking.update({"status":"final","code":_concept("http://loinc.org","72166-2"),"valueCodeableConcept":_concept(BASE+"CodeSystem/cnwqk805-SmokingStatusCS",status)})
        if timestamp:smoking["effectiveDateTime"]=canonical_datetime(timestamp)
        resources=[smoking]
        months=transport_meta.get("cessation_months")
        if status=="former-smoker" and months is not None:
            cessation=_expc_observation(patient,BASE+"Profile/cnwqk805-SmokingCessationDurationObservation","63586-4",months/12,"\u5e74","a",timestamp)
            resources.append(cessation)
        return resources
    if cid=="855":
        labs=transport_meta.get("labs") or {}
        if not all(labs.values()):return []
        specs=[("Scr","cnwqk855-serum-creatinine-observation","2160-0","umol/L","umol/L"),("BUN","cnwqk855-blood-urea-nitrogen-observation","3094-0","mmol/L","mmol/L"),("ALT","cnwqk855-alanine-aminotransferase-observation","1742-6","U/L","U/L"),("AST","cnwqk855-aspartate-aminotransferase-observation","1920-8","U/L","U/L")]
        return [_expc_observation(patient,BASE+"Profile/"+profile,code,(labs[name][0] if isinstance(labs[name],tuple) else labs[name]),unit,ucum,timestamp) for name,profile,code,unit,ucum in specs]
    return _frozen_build_resources(cid,patient,values)

class FHIRResourceBundleGenerator(_FrozenGenerator):
    def parse_clinical_text_to_fhir_bundle(self,patient_id,case_reports,ai_algorithm_type="nlp"):
        reports=normalize_reports(case_reports);windows=retrieve_evidence(reports,SPEC);decision,reason=rule_decide(TITLE,windows);route="RULE";attempts=0;parse="NA";transport="NA";prompt_len=0
        if decision is not None:decision="MATCH" if decision else "NO_MATCH"
        if decision is None:route="LLM";decision,parse,attempts,prompt_len,transport=llm_decide(SPEC,windows,self.transport)
        values=extract_payload(TITLE,reports,decision,windows)
        if decision=="MATCH" and ((TITLE in ("265","855") and "number" not in values) or (TITLE=="635" and "labs" not in values)):
            decision="NO_MATCH";reason="MISSING_GROUNDED_PAYLOAD";values=extract_payload(TITLE,reports,decision,windows)
        transport_meta=derive_transport_meta(TITLE,reports,windows,values)
        resources=build_expc_resources(TITLE,str(patient_id),values,transport_meta)
        reason=reason or ("MATCH" if decision=="MATCH" else "NO_MATCH")
        rm=windows.metrics
        print("V5S_METRICS|criterion="+str(TITLE)+"|route="+route+"|evidence_windows="+str(len(windows))+"|anchor_hits="+str(rm["true_anchor_hits"])+"|groups_required="+str(rm["groups_required"])+"|groups_hit="+str(rm["groups_hit"])+"|group_ids_hit="+json.dumps(rm["group_ids_hit"])+"|true_anchor_hits="+str(rm["true_anchor_hits"])+"|fallback_used="+str(int(rm["fallback_used"]))+"|llm_called="+str(int(attempts>0))+"|attempts="+str(attempts)+"|transport="+str(transport)+"|parse="+str(parse)+"|decision="+decision+"|resources="+str(len(resources))+"|reason="+reason+"|prompt_length="+str(prompt_len))
        return {"resourceType":"Bundle","type":"transaction","entry":[{"resource":r,"request":{"method":"POST","url":r["resourceType"]}} for r in resources]}
'''
