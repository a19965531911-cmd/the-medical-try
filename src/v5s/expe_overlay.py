"""Experiment E aggressive recall overlay."""

EXPE_OVERLAY_SOURCE = r'''
_expe_frozen_extract_payload=extract_payload
_EXPE_ALIASES={"165":["化疗","外院","外部医院","outside hospital"],"185":["伊立替康","irinotecan","CPT-11","首次","给药"],"265":["cTnI","cTnT","肌钙蛋白","troponin"],"485":["POP-Q","盆腔器官脱垂","prolapse"],"555":["手术","切除","个月前","surgery"],"565":["腹泻","便秘","diarrhea","constipation","当前","目前"],"615":["pT","R1","pN1","GS","Gleason","PSA"],"635":["AST","ALT","BUN","Cr","肌酐","尿素氮","lab"],"675":["年龄","岁","带状疱疹","herpes zoster","zoster","HZ","头面部","头部","面部","额部","眼周","三叉神经区"],"735":["乙型肝炎","乙肝","HBV","hepatitis B","HIV","AIDS","结核","TB","结缔组织病"],"745":["手术","术后","术毕","手术后","post-op","postoperative","机械通气","气管插管","有创","ventilation"],"755":["机械通气","呼吸机","气管插管","ventilation","MV","有创通气","持续","小时","天"],"805":["吸烟","smoking","smoker","戒烟","quit","从不","从未"],"835":["凝血","PT","APTT","INR","coagulation","异常"],"855":["Scr","肌酐","creatinine","BUN","尿素氮","ALT","AST","lab"],"875":["颅内高压","intracranial pressure","intracranial hypertension","意识障碍","昏迷","impaired consciousness"]}
_EXPE_GROUPS={"675":[["年龄","岁","age"],["带状疱疹","herpes zoster","zoster","HZ"],["头面部","头部","面部","额部","眼周","head","face"]],"735":[["乙型肝炎","乙肝","HBV","hepatitis B","HIV","AIDS","结核","TB","结缔组织病"],["活动性","活动期","正在治疗","未控制","active"]],"745":[["手术","术后","术毕","post-op"],["机械通气","气管插管","有创","ventilation"]],"755":[["机械通气","呼吸机","气管插管","ventilation","MV","有创通气"],["小时","天","持续","历时","duration"]]}
def _expe_spec(spec):
    out=dict(spec);cid=str(TITLE);out["aliases"]=_EXPE_ALIASES.get(cid,out.get("aliases",[]));out["groups"]=_EXPE_GROUPS.get(cid,out.get("groups") or [out["aliases"]]);return out
def retrieve_evidence(reports,spec):
    groups=_expe_spec(spec).get("groups") or [_expe_spec(spec).get("aliases",[])];candidates={};order=[]
    for r in reports:
        ss=split_text(r["text"])
        for gi,aliases in enumerate(groups):
            for i,s in enumerate(ss):
                if any(str(a).lower() in s.lower() for a in aliases):
                    for j in [i]+[x for x in range(max(0,i-1),min(len(ss),i+2)) if x!=i]:
                        key=(r["index"],ss[j])
                        if key not in candidates:candidates[key]={"text":ss[j],"report":r["index"],"group":gi,"groups":[gi]};order.append(key)
                        elif gi not in candidates[key]["groups"]:candidates[key]["groups"].append(gi)
                    break
    selected=[];used=set()
    for gi in range(len(groups)):
        key=next((k for k in order if gi in candidates[k]["groups"]),None)
        if key is not None and key not in used:selected.append(candidates[key]);used.add(key)
    for key in order:
        if len(selected)>=12:break
        if key not in used:selected.append(candidates[key]);used.add(key)
    fallback=False
    if not selected:
        fallback=True
        for r in reports:
            ss=split_text(r["text"])
            if ss:selected.append({"text":ss[0],"report":r["index"],"group":-1,"groups":[]})
            if len(selected)>=12:break
    ids=sorted({g for x in selected for g in x.get("groups",[])})
    return EvidenceWindows(selected,{"groups_required":len(groups),"groups_hit":len(ids),"group_ids_hit":ids,"true_anchor_hits":len(ids),"fallback_used":fallback,"evidence_windows":len(selected)})
def _expe_text(w):return " ".join(x.get("text","") for x in w)
def _expe_has(t,*p):return any(re.search(x,t,re.I) for x in p)
def _expe_hard_contradiction(cid,t):
    if cid=="485" and _expe_has(t,r"POP[- ]?Q\s*(?<!I)(?:II(?!I)|I(?!I)|[12])(?:期|级)?|盆腔器官脱垂.{0,8}(?<!I)(?:II(?!I)|I(?!I)|[12])(?:期|级)"):return "EXPLICIT_LOW_STAGE"
    if cid=="265":
        for m in re.finditer(r"(?:cTnI|cTnT|肌钙蛋白[IT]).{0,20}?([0-9]+(?:\.[0-9]+)?)",t,re.I):
            th=.03 if "ctnt" in m.group(0).lower() or "肌钙蛋白t" in m.group(0).lower() else .06
            if float(m.group(1))<th:return "EXPLICIT_BELOW_THRESHOLD"
    if cid=="555":
        m=re.search(r"(\d+)\s*个?月前",t)
        if m and int(m.group(1))>6:return "EXPLICIT_OVER_6_MONTHS"
    if cid=="755":
        m=re.search(r"(\d+(?:\.\d+)?)\s*(小时|h|天|日)",t,re.I)
        if m and float(m.group(1))*(24 if m.group(2) in ("天","日") else 1)<24:return "EXPLICIT_UNDER_24_HOURS"
    if cid in ("735","565") and _expe_has(t,r"已解决|已治愈|inactive|resolved|history only|既往史|历史|稳定|stable"):return "RESOLVED_OR_HISTORY_ONLY"
    if cid=="635":
        labs={name:_lab_high(t,names) for name,names in {"AST":"AST","ALT":"ALT","BUN":("BUN","尿素氮"),"Cr":("Cr","肌酐")}.items()}
        if any(pair and pair[0]>2*pair[1] for pair in labs.values()):return "EXPLICIT_THRESHOLD_VIOLATION"
    if cid=="745" and _expe_has(t,r"NIV|无创通气|non[- ]?invasive|计划|拟行|planned|术前|pre[- ]?op") and not _expe_has(t,r"有创|插管|机械通气.*术后|术后.*机械通气|invasive"):return "NON_INVASIVE_OR_PLANNED_ONLY"
    if cid=="805":
        m=re.search(r"(?:戒烟|quit)\s*(\d+(?:\.\d+)?)\s*(?:年|years?)",t,re.I)
        if m and float(m.group(1))>=2:return "QUIT_2Y_OR_MORE"
        if _expe_has(t,r"从不吸烟|从未吸烟|never smoker"):return "NEVER_SMOKER"
    if cid=="185" and _expe_has(t,r"计划|拟用|planned|planned-only"):return "PLANNED_ONLY"
    if cid=="185" and _expe_has(t,r"既往使用|曾用过|prior|previous") and _expe_has(t,r"伊立替康|irinotecan|CPT-11"):return "REPEATED_PRIOR_IRINOTECAN"
    if cid=="165" and _expe_has(t,r"计划|拟行|拟转|planned|尚未|未开始"):return "PLANNED_ONLY"
    if cid=="855":
        labs=_labs_855(t)
        if (labs["Scr"] is not None and labs["Scr"]>=178) or (labs["BUN"] is not None and labs["BUN"]>=9):return "EXPLICIT_THRESHOLD_VIOLATION"
        if any(labs[name] and labs[name][0]>labs[name][1] for name in ("ALT","AST")):return "EXPLICIT_THRESHOLD_VIOLATION"
    if cid=="835" and _expe_has(t,r"正常|normal") and not _expe_has(t,r"异常|障碍|abnormal"):return "EXPLICIT_NORMAL"
    if cid=="485" and _expe_has(t,r"否认|未见|无") and _expe_has(t,r"POP[- ]?Q|盆腔器官脱垂|prolapse"):return "EXPLICIT_DENIAL"
    if cid=="675" and _expe_has(t,r"否认|未见|无") and _expe_has(t,r"带状疱疹|herpes zoster|zoster"):return "EXPLICIT_DENIAL"
    if cid=="875" and _expe_has(t,r"否认|未见|无") and _expe_has(t,r"颅内高压|intracranial|意识障碍|昏迷|impaired consciousness"):return "EXPLICIT_DENIAL"
    return None
def rule_decide(cid,w):
    cid=str(cid);t=_expe_text(w)
    if cid=="485":
        if _expe_has(t,r"POP[- ]?Q|盆腔器官脱垂|prolapse") and _expe_has(t,r"III|IV|3期|4期|high grade"):return (True,"RULE_STAGE")
    if cid=="615":
        if _expe_has(t,r"pT3a|pT3b|pT4|R1|pN1"):return (True,"RULE_BRANCH")
        m=re.search(r"(?:GS|Gleason)\D{0,8}(\d+)",t,re.I)
        if m:return (float(m.group(1))>=8,"RULE_GS")
        m=re.search(r"PSA\s*[>:：=]?\s*(\d+(?:\.\d+)?)",t,re.I)
        if m:return (float(m.group(1))>0.1,"RULE_PSA")
    if cid=="675":
        zoster=_expe_has(t,r"带状疱疹|herpes zoster|zoster|HZ")
        site=_expe_has(t,r"头面部|头部|面部|额部|眼周|三叉神经区|head|face")
        age=re.search(r"(?:年龄|age)\s*[:：]?\s*(\d{2,3})|(?<!\d)(\d{2,3})\s*岁",t,re.I)
        if zoster and (site or (age and float(age.group(1) or age.group(2))>=50)):return (True,"RULE_ZOSTER")
    if cid=="265":
        m=re.search(r"(cTnI|cTnT|肌钙蛋白[IT])\s*[:：=]?\s*([0-9]+(?:\.[0-9]+)?)",t,re.I)
        if m:return (float(m.group(2))>=(.03 if m.group(1).lower() in ("ctnt","肌钙蛋白t") else .06),"RULE_NUMERIC")
    if cid=="755":
        m=re.search(r"(?:机械通气|呼吸机|气管插管|ventilation|MV).{0,30}?(\d+(?:\.\d+)?)\s*(小时|h|天|日)",t,re.I)
        if m:return (float(m.group(1))*(24 if m.group(2) in ("天","日") else 1)>=24,"RULE_DURATION")
    if cid=="555":
        m=re.search(r"(\d+)\s*个?月前.*(?:手术|切除|surgery|resection)",t,re.I)
        if m:return (int(m.group(1))<=6,"RULE_RELATIVE_DATE")
    if cid=="805":
        if re.search(r"从不吸烟|从未吸烟|never smoker",t,re.I):return (False,"RULE_NEVER")
        m=re.search(r"(?:戒烟|quit)\s*(\d+(?:\.\d+)?)\s*(?:年|years?)",t,re.I)
        if m:return (float(m.group(1))<2,"RULE_CESSATION")
        if re.search(r"目前.*吸烟|现.*吸烟|current smoker",t,re.I):return (True,"RULE_CURRENT")
    if cid=="635":
        labs=_labs_635(t)
        if labs:return (all(v<=2*h for v,h in labs.values()),"RULE_LABS")
    if cid=="855":
        labs=_labs_855(t)
        if all(labs.values()):return (labs["Scr"]<178 and labs["BUN"]<9 and labs["ALT"][0]<=labs["ALT"][1] and labs["AST"][0]<=labs["AST"][1],"RULE_LABS")
    return (None,None)
def _expe_semantic(cid,t):
    if cid=="485":return _expe_has(t,r"POP[- ]?Q|盆腔器官脱垂|prolapse")
    if cid=="615":return _expe_has(t,r"pT3a|pT3b|pT4|R1|pN1|GS|Gleason|PSA")
    if cid=="265":return _expe_has(t,r"cTnI|cTnT|肌钙蛋白|troponin")
    if cid=="635":return _expe_has(t,r"AST|ALT|BUN|Cr|肌酐|尿素氮|lab|化验")
    if cid=="675":return _expe_has(t,r"带状疱疹|herpes zoster|zoster|HZ|头面部|头部|面部|额部|眼周|head|face")
    if cid=="735":return _expe_has(t,r"乙型肝炎|乙肝|HBV|hepatitis B|HIV|AIDS|结核|TB|tuberculosis|结缔组织病")
    if cid=="745":return _expe_has(t,r"手术|术后|术毕|手术后|post[- ]?op|postoperative|机械通气|呼吸机|气管插管|有创|ventilation|MV") and not _expe_has(t,r"NIV|无创通气|non[- ]?invasive")
    if cid=="755":return _expe_has(t,r"机械通气|呼吸机|气管插管|有创|ventilation|MV") and not _expe_has(t,r"NIV|无创通气|non[- ]?invasive")
    if cid=="875":return _expe_has(t,r"颅内高压|intracranial pressure|intracranial hypertension|意识障碍|意识改变|昏迷|impaired consciousness")
    if cid=="805":return _expe_has(t,r"吸烟|smoking|smoker")
    if cid=="565":return _expe_has(t,r"腹泻|便秘|diarrhea|constipation")
    if cid=="555":return _expe_has(t,r"手术|切除|surgery|resection")
    if cid=="185":return _expe_has(t,r"伊立替康|irinotecan|CPT-11")
    if cid=="165":return _expe_has(t,r"化疗|chemotherapy|外院|外部医院|outside hospital|external hospital")
    if cid=="835":return _expe_has(t,r"凝血|PT|APTT|INR|coagulation|血凝")
    return False
def _expe_payload(cid,reports,decision,w):
    v=_expe_frozen_extract_payload(cid,reports,decision,w) or {};t=_expe_text(w)
    if cid=="755" and "duration_hours" not in v:
        m=re.search(r"(?:机械通气|呼吸机|ventilation).{0,30}?(\d+(?:\.\d+)?)\s*(小时|h|天|日)",t,re.I)
        if m:v["duration_hours"]=float(m.group(1))*(24 if m.group(2) in ("天","日") else 1)
    return v
'''
EXPE_FINAL_SOURCE = r'''
class FHIRResourceBundleGenerator(_FrozenGenerator if "_FrozenGenerator" in globals() else FHIRResourceBundleGenerator):
    def parse_clinical_text_to_fhir_bundle(self,patient_id,case_reports,ai_algorithm_type="nlp"):
        reports=normalize_reports(case_reports);w=retrieve_evidence(reports,SPEC);cid=str(TITLE);t=_expe_text(w);deterministic,reason=rule_decide(cid,w);attempts=0;parse="NA";transport="NA";prompt_len=0;contradiction=_expe_hard_contradiction(cid,t)
        if deterministic is True and not contradiction:decision="MATCH";mode="RULE"
        elif deterministic is False or contradiction:decision="NO_MATCH";mode="RULE";reason=reason or contradiction or "EXPLICIT_NEGATIVE"
        else:
            llm,parse,attempts,prompt_len,transport=llm_decide(_expe_spec(SPEC),w,self.transport);anchors=w.metrics["true_anchor_hits"]
            if anchors>=1 and llm=="MATCH" and not contradiction and _expe_semantic(cid,t):decision="MATCH";mode="PARTIAL_GROUNDED"
            elif anchors==0 and w.metrics["fallback_used"] and llm=="MATCH":decision="NO_MATCH";mode="FALLBACK_BLOCK";reason="ZERO_ANCHOR_FALLBACK_BLOCK"
            else:decision="NO_MATCH";mode="FALLBACK_BLOCK" if w.metrics["fallback_used"] else "RULE";reason=reason or "INSUFFICIENT_GROUNDED_EVIDENCE"
        v=_expe_payload(cid,reports,decision,w)
        if decision!="MATCH": resources=[]
        elif cid in {"265","555","755","805","855"} and "build_expc_resources" in globals():resources=build_expc_resources(cid,str(patient_id),v,derive_transport_meta(cid,reports,w,v))
        else:resources=build_resources(cid,str(patient_id),v)
        reason=reason or ("MATCH" if decision=="MATCH" else "NO_MATCH");m=w.metrics
        print("V5S2E_METRICS|criterion="+cid+"|anchor_hits="+str(m["true_anchor_hits"])+"|groups_hit="+str(m["groups_hit"])+"|groups_required="+str(m["groups_required"])+"|fallback_used="+str(int(m["fallback_used"]))+"|model_decision="+("MATCH" if attempts and decision=="MATCH" else ("NO_MATCH" if attempts else "NA"))+"|hard_contradiction="+str(contradiction or "NONE")+"|admission_mode="+mode+"|final_decision="+decision+"|resources="+str(len(resources))+"|reason="+reason)
        return {"resourceType":"Bundle","type":"transaction","entry":[{"resource":r,"request":{"method":"POST","url":r["resourceType"]}} for r in resources]}
'''


