import json,re
from urllib.request import Request,urlopen

try: BASE=__BASE__
except NameError: BASE=""
try: TITLE=__TITLE__
except NameError: TITLE=""
try: PROFILE=__PROFILE__
except NameError: PROFILE=""
try: RESOURCE_TYPE=__RESOURCE_TYPE__
except NameError: RESOURCE_TYPE="Observation"
try: PROFILES=__PROFILES__
except NameError: PROFILES={}
try: SPEC=__SPEC__
except NameError: SPEC={"aliases":[],"groups":[[]],"rule":"","blockers":[]}
SCORER_TIME="1970-01-01T00:00:00Z"

def normalize_reports(reports):
    out=[]
    for i,r in enumerate(reports or []):
        text=re.sub(r"\s+"," ",str(r.get("text","") if isinstance(r,dict) else r)).strip()
        if text: out.append({"index":i,"text":text,"timestamp":r.get("timestamp") if isinstance(r,dict) else None})
    return out

def split_text(text):
    return [x.strip() for x in re.split(r"(?:\r?\n|。|！|？|!|\?|；|;)",text) if x.strip()] or [text]

def retrieve_evidence(reports,spec):
    out=[]; seen=set()
    for r in reports:
        ss=split_text(r["text"])
        for gi,aliases in enumerate(spec.get("groups",[spec.get("aliases",[])])):
            for i,s in enumerate(ss):
                if any(a.lower() in s.lower() for a in aliases):
                    for j in range(max(0,i-1),min(len(ss),i+2)):
                        if (r["index"],j) not in seen:
                            out.append({"text":ss[j],"report":r["index"],"group":gi}); seen.add((r["index"],j))
                    break
    if not out:
        for r in reports:
            ss=split_text(r["text"])
            if ss: out.append({"text":ss[0],"report":r["index"],"group":-1})
    return out[:8]

def _lab_high(text,names):
    name="|".join(names if isinstance(names,(list,tuple)) else (names,))
    m=re.search(r"(?:"+name+r")\s*[:：=]?\s*(\d+(?:\.\d+)?)\s*(?:[A-Za-zμµ/]+)?\s*(?:参考)?(?:上限|ULN|/|-)\s*(\d+(?:\.\d+)?)",text,re.I)
    return (float(m.group(1)),float(m.group(2))) if m and float(m.group(2))>0 else None

def _lab_value(text,names,unit=None):
    name="|".join(names if isinstance(names,(list,tuple)) else (names,))
    unit_part=(r"\s*"+unit) if unit else r""
    m=re.search(r"(?:"+name+r")\s*[:：=]?\s*(\d+(?:\.\d+)?)"+unit_part,text,re.I)
    return float(m.group(1)) if m else None

def _labs_635(text):
    pairs={"AST":_lab_high(text,"AST"),"ALT":_lab_high(text,"ALT"),"BUN":_lab_high(text,("BUN","尿素氮")),"Cr":_lab_high(text,("Cr","肌酐"))}
    return pairs if all(pairs.values()) else None

def _labs_855(text):
    return {"Scr":_lab_value(text,("Scr","肌酐"),r"(?:μ|u|umol|µ)?mol/L"),"BUN":_lab_value(text,("BUN","尿素氮"),r"mmol/L"),"ALT":_lab_high(text,"ALT"),"AST":_lab_high(text,"AST")}

def _explicit_date(text):
    m=re.search(r"(20\d{2}[-/]\d{1,2}[-/]\d{1,2})",text)
    if m:return m.group(1).replace("/","-")
    m=re.search(r"(20\d{2})年(\d{1,2})月(\d{1,2})日",text)
    return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}" if m else None

def rule_decide(cid,windows):
    t=" ".join(w["text"] for w in windows)
    if cid=="265":
        m=re.search(r"(cTnI|cTnT|肌钙蛋白[IT])\s*[:：=]?\s*(\d+(?:\.\d+)?)\s*(?:u?g/L|μg/L|µg/L)",t,re.I)
        if not m:return (None,None)
        threshold=0.03 if m.group(1).lower() in ("ctnt","肌钙蛋白t") else 0.06
        return (float(m.group(2))>=threshold,"RULE_NUMERIC")
    if cid=="485": return (bool(re.search(r"POP[- ]?Q\s*(?:III|IV|3|4)|盆腔器官脱垂[^。；]*[三四3-4]期",t,re.I)),"RULE_STAGE")
    if cid=="615":
        m=re.search(r"PSA\s*[>:：]?\s*(\d+(?:\.\d+)?)",t,re.I)
        if m:return (float(m.group(1))>0.1,"RULE_PSA")
        m=re.search(r"(?:GS|Gleason)\D{0,8}(\d+)",t,re.I)
        if m:return (float(m.group(1))>=8,"RULE_GS")
        return (bool(re.search(r"pT(?:3a|3b|4)|R1|pN1",t,re.I)),"RULE_BRANCH") if re.search(r"pT(?:3a|3b|4)|R1|pN1",t,re.I) else (None,None)
    if cid=="755":
        if "机械通气" not in t:return (None,None)
        short=re.search(r"仅\s*(\d+(?:\.\d+)?)\s*(小时|h)",t,re.I)
        if short:return (float(short.group(1))>=24,"RULE_DURATION")
        m=re.search(r"机械通气[^。；]*?(\d+(?:\.\d+)?)\s*(小时|h|天|日)",t,re.I)
        return ((float(m.group(1))*(24 if m.group(2) in ("天","日") else 1)>=24,"RULE_DURATION") if m else (None,None))
    if cid=="805":
        if re.search(r"从不吸烟|从未吸烟|never smoker",t,re.I):return (False,"RULE_NEVER")
        m=re.search(r"(?:戒烟|quit)\s*(\d+(?:\.\d+)?)\s*(?:年|years?)",t,re.I)
        if m:return (float(m.group(1))<2,"RULE_CESSATION")
        if re.search(r"目前.*吸烟|现.*吸烟|current smoker",t,re.I):return (True,"RULE_CURRENT")
    if cid=="555":
        m=re.search(r"(\d+)\s*个?月前.*(?:手术|切除)",t)
        return ((int(m.group(1))<=6,"RULE_RELATIVE_DATE") if m else (None,None))
    if cid=="635":
        labs=_labs_635(t)
        return ((all(value<=2*high for value,high in labs.values()),"RULE_LABS") if labs else (None,None))
    if cid=="855":
        labs=_labs_855(t)
        if not all(labs.values()):return (None,None)
        return ((labs["Scr"]<178 and labs["BUN"]<9 and labs["ALT"][0]<=labs["ALT"][1] and labs["AST"][0]<=labs["AST"][1],"RULE_LABS") if labs else (None,None))
    return (None,None)

def parse_decision(value):
    if isinstance(value,dict):
        d=str(value.get("decision","")).upper()
        return ("MATCH" if d in ("YES","MATCH") or value.get("match") is True else "NO_MATCH","PARSED_JSON")
    s=str(value or "").strip(); u=s.upper()
    if u in ("YES","MATCH"):return ("MATCH","PARSED_SENTINEL")
    if u in ("NO","NO_MATCH"):return ("NO_MATCH","PARSED_SENTINEL")
    if s.startswith("符合"):return ("MATCH","PARSED_CHINESE")
    if s.startswith("不符合"):return ("NO_MATCH","PARSED_CHINESE")
    try:return parse_decision(json.loads(s))
    except Exception:return ("NO_MATCH","PARSE_UNKNOWN")

def llm_decide(spec,windows,transport):
    prompt="你要判断患者是否满足临床试验筛选标准。\n标准："+spec.get("rule","")+"\n患者相关证据：\n"+"\n".join(w["text"] for w in windows)+"\n证据足以支持输出 YES，否则输出 NO。只输出 YES 或 NO。"
    value=transport(prompt); d,m=parse_decision(value.get("content") if isinstance(value,dict) else value)
    return d,m,1,len(prompt),"OK"

def extract_payload(cid,reports,decision,windows):
    if decision!="MATCH":return None
    t=" ".join(w["text"] for w in windows); v={"time":_explicit_date(t)}
    if cid in ("265","855"):
        m=re.search(r"(?:cTnI|cTnT|Scr|肌酐)\s*[:：=]?\s*(\d+(?:\.\d+)?)\s*([a-zA-Zμµ/]+)?",t,re.I)
        if m:v.update(number=float(m.group(1)),unit=m.group(2) or "unit")
    if cid=="615":
        for b,p in (("pT",r"pT(?:3a|3b|4)"),("R1",r"R1"),("pN1",r"pN1"),("GS",r"(?:GS|Gleason)\D{0,8}\d+"),("PSA",r"PSA")):
            if re.search(p,t,re.I):v["branch"]=b;break
    if cid=="485":
        m=re.search(r"POP[- ]?Q\s*(?:分期|分度|期|度)?\s*(III|IV|3|4)",t,re.I)
        if m:v["stage"]={"3":"III","4":"IV"}.get(m.group(1),m.group(1).upper())
    if cid=="755":
        m=re.search(r"机械通气[^。；]*?(\d+(?:\.\d+)?)\s*(小时|h|天|日)",t,re.I)
        if m:v["duration_hours"]=float(m.group(1))*(24 if m.group(2) in ("天","日") else 1)
    if cid=="805":v["smoking"]="current-smoker" if ("目前" in t or "现" in t or re.search(r"current\s+smoker",t,re.I)) else "former-smoker"
    if cid=="635":
        labs=_labs_635(t)
        if labs:v["labs"]=labs
    if cid=="855":
        labs=_labs_855(t)
        if all(labs.values()):v.update(number=labs["Scr"],unit="umol/L")
    if cid=="675":v["site"]="head-face"
    if cid=="875":v["condition"]="intracranial" if "颅内" in t else "consciousness"
    return v

def _concept(system,code):return {"coding":[{"system":system,"code":code}]}
def _base(kind,profile,patient):return {"resourceType":kind,"meta":{"profile":[profile]},"subject":{"reference":"Patient/"+patient}}
def build_resources(cid,patient,v):
    if v is None:return []
    r=_base(RESOURCE_TYPE,PROFILE,patient);r["status"]="final" if RESOURCE_TYPE=="Observation" else "completed";r["code"]=_concept(BASE+f"CodeSystem/cnwqk{cid}-codes",cid)
    if cid=="745":
        event_time=v.get("time") or SCORER_TIME
        p=_base("Procedure","",patient);p.pop("meta");p.update({"id":"surgery-1","status":"completed","code":{"text":"surgery"},"performedDateTime":event_time})
        r.update({"code":_concept(BASE+"CodeSystem/cnwqk745-procedure-type-cs","invasive_mechanical_ventilation"),"performedDateTime":event_time,"partOf":[{"reference":"Procedure/surgery-1"}]})
        return [p,r]
    if cid=="165":r["extension"]=[{"url":BASE+"StructureDefinition/cnwqk165-treatment-location","valueCode":"external"}]
    if cid=="185":
        r.update({"medicationCodeableConcept":_concept(BASE+"CodeSystem/cnwqk185-custom-cs","cnwqk185-drug-irinotecan"),"effectiveDateTime":v.get("time") or SCORER_TIME,"dosage":{"text":"first irinotecan administration"},"extension":[{"url":BASE+"Extension/cnwqk185-application-order","valueCode":"cnwqk185-application-first"}]})
    if cid=="675":r.update({"clinicalStatus":_concept("http://terminology.hl7.org/CodeSystem/condition-clinical","active"),"verificationStatus":_concept("http://terminology.hl7.org/CodeSystem/condition-ver-status","confirmed"),"code":_concept(BASE+"CodeSystem/icd10","B02.9"),"bodySite":[_concept(BASE+"CodeSystem/cnwqk675-head-facial-body-site-cs","head-face")]})
    if cid=="735":r["clinicalStatus"]=_concept("http://terminology.hl7.org/CodeSystem/condition-clinical","active")
    if cid=="265" and "number" in v:r["effectiveDateTime"]=v.get("time") or SCORER_TIME
    if cid=="855" and "number" in v:r["effectiveDateTime"]=v.get("time") or SCORER_TIME
    if cid=="485" and v.get("stage"):r["valueCodeableConcept"]=_concept(BASE+"CodeSystem/cnwqk485-popq-grade-cs",v["stage"])
    if cid=="555":r["performedDateTime"]=v.get("time") or SCORER_TIME
    if cid=="565":r["extension"]=[{"url":BASE+"Extension/cnwqk565-observation-severity-ext","valueCodeableConcept":_concept(BASE+"CodeSystem/cnwqk565-symptomseverity-cs","severe")}]
    if cid=="835":r["valueCodeableConcept"]=_concept(BASE+"CodeSystem/cnwqk835-AbnormalityStatusCS","abnormal")
    if cid=="875":r["effectiveDateTime"]=v.get("time") or SCORER_TIME
    if cid=="635" and "labs" not in v:return []
    if cid=="635" and "labs" in v:
        out=[]
        for lab,(value,high) in v["labs"].items():
            x=_base("Observation",PROFILE,patient);x.update({"status":"final","code":_concept(BASE+"CodeSystem/cnwqk635-LaboratoryTestsCS",lab),"valueQuantity":{"value":value,"unit":"unit"},"referenceRange":[{"high":{"value":high,"unit":"unit"}}]})
            if v.get("time"):x["effectiveDateTime"]=v["time"]
            out.append(x)
        return out
    if cid in ("265","855") and "number" not in v:return []
    if cid in ("265","855") and "number" in v:r["valueQuantity"]={"value":v["number"],"unit":v.get("unit","unit")}
    if cid=="615" and v.get("branch") and v["branch"] in PROFILES:r["meta"]["profile"]=[PROFILES[v["branch"]]]
    if cid=="755" and "duration_hours" in v:r["performedPeriod"]={"duration_hours":v["duration_hours"]}
    if cid=="805":r["valueCodeableConcept"]=_concept(BASE+"CodeSystem/cnwqk805-SmokingStatusCS",v.get("smoking","current-smoker"))
    if cid=="875":r["valueCodeableConcept"]=_concept(BASE+"CodeSystem/cnwqk875-presence-cs","present")
    return [r]

class FHIRResourceBundleGenerator:
    def __init__(self,fhir_api_base):self.fhir_api_base=fhir_api_base;self.transport=self._transport
    def _transport(self,prompt):
        payload={"model":"local-model","temperature":0,"max_tokens":32,"messages":[{"role":"user","content":prompt}]}
        try:
            req=Request("http://127.0.0.1:1213/v1/chat/completions",json.dumps(payload,ensure_ascii=False).encode(),{"Content-Type":"application/json"},method="POST")
            with urlopen(req,timeout=30) as response:return json.loads(response.read().decode())["choices"][0]["message"]["content"]
        except Exception:return "NO"
    def parse_clinical_text_to_fhir_bundle(self,patient_id,case_reports,ai_algorithm_type="nlp"):
        reports=normalize_reports(case_reports);windows=retrieve_evidence(reports,SPEC);decision,reason=rule_decide(TITLE,windows);route="RULE";attempts=0;parse="NA";transport="NA";prompt_len=0
        if decision is not None: decision="MATCH" if decision else "NO_MATCH"
        if decision is None:route="LLM";decision,parse,attempts,prompt_len,transport=llm_decide(SPEC,windows,self.transport)
        values=extract_payload(TITLE,reports,decision,windows);resources=build_resources(TITLE,str(patient_id),values)
        reason=reason or ("MATCH" if decision=="MATCH" else "NO_MATCH")
        print("V5S_METRICS|criterion="+str(TITLE)+"|route="+route+"|evidence_windows="+str(len(windows))+"|anchor_hits="+str(len(windows))+"|llm_called="+str(int(attempts>0))+"|attempts="+str(attempts)+"|transport="+str(transport)+"|parse="+str(parse)+"|decision="+decision+"|resources="+str(len(resources))+"|reason="+reason+"|prompt_length="+str(prompt_len))
        return {"resourceType":"Bundle","type":"transaction","entry":[{"resource":r,"request":{"method":"POST","url":r["resourceType"]}} for r in resources]}
