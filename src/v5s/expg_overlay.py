"""Experiment G target-only criterion recall overlay."""


EXPG_SOURCE = r'''
_ExperimentEGenerator=FHIRResourceBundleGenerator
_expg_e_payload=_expe_payload
_EXPG_ALIASES={
"485":["POP-Q","POPQ","POP Q","盆腔器官脱垂","盆底器官脱垂","子宫脱垂","阴道前壁脱垂","阴道后壁脱垂","阴道穹隆脱垂","uterine prolapse","pelvic organ prolapse","prolapse","III","IV","Ⅲ","Ⅳ","3期","4期","III度","IV度","三期","四期","重度","高度脱垂"],
"635":["AST","ALT","BUN","Cr","creatinine","肌酐","尿素氮","肝功能","肾功能","肝肾功能","正常","无明显异常","未见明显异常"],
"855":["Scr","Cr","creatinine","肌酐","BUN","尿素氮","ALT","AST","肝功能","肾功能","肝肾功能","正常","无明显异常","未见明显异常"],
"675":["年龄","岁","aged","year-old","带状疱疹","带状疱疹病毒","herpes zoster","zoster","HZ","VZV reactivation","头面部","面部","额部","眼周","眼部","耳部","颅面","三叉神经","V1","ophthalmic","facial"],
"735":["乙型肝炎","乙肝","HBV","hepatitis B","HIV","AIDS","结核","TB","tuberculosis","结缔组织病","活动期","活动性","当前感染","现症","正在治疗","治疗中","未控制","未治愈","持续感染","active","ongoing","currently treated","persistent"],
"745":["手术","术后","术毕","手术后","operation","surgery","post-op","postoperative","机械通气","呼吸机支持","气管插管","有创机械通气","invasive ventilation","ventilation","remained intubated"]}
_EXPG_GROUPS={
"485":[["POP-Q","POPQ","POP Q","盆腔器官脱垂","盆底器官脱垂","子宫脱垂","阴道前壁脱垂","阴道后壁脱垂","阴道穹隆脱垂","uterine prolapse","pelvic organ prolapse","prolapse"],["III","IV","Ⅲ","Ⅳ","3期","4期","III度","IV度","三期","四期","重度","高度脱垂"]],
"635":[["AST"],["ALT"],["BUN","尿素氮"],["Cr","creatinine","肌酐"],["肝功能","肾功能","肝肾功能"]],
"855":[["Scr","Cr","creatinine","肌酐"],["BUN","尿素氮"],["ALT"],["AST"],["肝功能","肾功能","肝肾功能"]],
"675":[["年龄","岁","aged","year-old"],["带状疱疹","带状疱疹病毒","herpes zoster","zoster","HZ","VZV reactivation"],["头面部","面部","额部","眼周","眼部","耳部","颅面","三叉神经","V1","ophthalmic","facial"]],
"735":[["乙型肝炎","乙肝","HBV","hepatitis B","HIV","AIDS","结核","TB","tuberculosis","结缔组织病"],["活动期","活动性","当前感染","现症","正在治疗","治疗中","未控制","未治愈","持续感染","active","ongoing","currently treated","persistent"]],
"745":[["手术","operation","surgery"],["机械通气","呼吸机支持","气管插管","有创机械通气","invasive ventilation","ventilation","remained intubated"],["术后","术毕","手术后","post-op","postoperative","after surgery","after operation"]]}
_EXPG_PROMPTS={
"485":"标准为 POP-Q III 或 IV 期盆腔器官脱垂。III/IV 必须与脱垂或 POP-Q 局部绑定；癌症、NYHA、压疮或 CKD 的分期不能作为脱垂分期。明确低分期回答 NO。",
"635":"标准要求相关肝肾功能检查未超过允许范围。如果病历明确说明肝肾功能正常、无明显异常，即使没有同时列出 AST/ALT/BUN/Cr 四项，也可回答 YES。若出现明确超过允许范围的数值，则回答 NO。",
"855":"若病历明确描述肝肾功能正常或无明显异常，且没有出现超出标准阈值的明确数值，可以回答 YES。无需四项检查全部逐项出现；Scr>=178、BUN>=9 或 ALT/AST 超过上限回答 NO。",
"675":"确诊带状疱疹并累及头面部，或确诊带状疱疹且年龄至少 50 岁，可以回答 YES。只有年龄或只有面部症状回答 NO。",
"735":"目标疾病当前活动、现患、正在治疗或治疗中可以回答 YES。仅既往史、已治愈、已缓解、inactive 或 resolved 回答 NO。",
"745":"患者在手术后接受有创机械通气即可回答 YES，相关信息可出现在相邻句子中。术前通气、无创通气、仅计划通气回答 NO。"}

def _expg_spec(spec):
    out=dict(spec);cid=str(TITLE);out["aliases"]=_EXPG_ALIASES[cid];out["groups"]=_EXPG_GROUPS[cid];out["rule"]=_EXPG_PROMPTS[cid];return out

def retrieve_evidence(reports,spec):
    groups=_EXPG_GROUPS[str(TITLE)];candidates={};order=[]
    for r in reports:
        ss=split_text(r["text"])
        for i,s in enumerate(ss):
            hits=[gi for gi,aliases in enumerate(groups) if any(str(a).lower() in s.lower() for a in aliases)]
            if not hits:continue
            for j in range(max(0,i-1),min(len(ss),i+2)):
                key=(r["index"],j)
                if key not in candidates:candidates[key]={"text":ss[j],"report":r["index"],"group":hits[0],"groups":list(hits)};order.append(key)
                else:
                    for gi in hits:
                        if gi not in candidates[key]["groups"]:candidates[key]["groups"].append(gi)
    selected=[];used=set();per_group={gi:0 for gi in range(len(groups))}
    for gi in range(len(groups)):
        key=next((k for k in order if gi in candidates[k]["groups"] and k not in used),None)
        if key is not None:selected.append(candidates[key]);used.add(key);per_group[gi]+=1
    for key in order:
        if len(selected)>=16:break
        if key in used:continue
        gs=candidates[key]["groups"]
        if gs and min(per_group[g] for g in gs)>=4:continue
        selected.append(candidates[key]);used.add(key)
        for g in gs:per_group[g]+=1
    fallback=False
    if not selected:
        fallback=True
        for r in reports:
            ss=split_text(r["text"])
            if ss:selected.append({"text":ss[0],"report":r["index"],"group":-1,"groups":[]})
            if len(selected)>=16:break
    ids=sorted({g for x in selected for g in x.get("groups",[])})
    return EvidenceWindows(selected,{"groups_required":len(groups),"groups_hit":len(ids),"group_ids_hit":ids,"true_anchor_hits":len(ids),"fallback_used":fallback,"evidence_windows":len(selected)})

def llm_decide(spec,windows,transport):
    prompt="你要判断患者是否满足临床试验筛选标准。\n标准："+_EXPG_PROMPTS[str(TITLE)]+"\n患者相关证据：\n"+"\n".join(w["text"] for w in windows)+"\n只输出 YES 或 NO。"
    value=transport(prompt);d,m=parse_decision(value.get("content") if isinstance(value,dict) else value)
    return d,m,1,len(prompt),"OK"

def _expg_clauses(t):return [x.strip() for x in re.split(r"[。！？!?；;，,]",t) if x.strip()]
def _expg_prolapse(s):return _expe_has(s,r"POP\s*[- ]?\s*Q|POPQ|盆腔器官脱垂|盆底器官脱垂|子宫脱垂|阴道(?:前壁|后壁|穹隆)脱垂|uterine prolapse|pelvic organ prolapse|prolapse")
def _expg_stage(t):
    high=r"(?:III|IV|Ⅲ|Ⅳ|[34]|三|四)(?:期|度|级)?|重度|高度脱垂"
    low=r"(?:II|I|Ⅱ|Ⅰ|[12]|一|二)(?:期|度|级)?"
    for s in _expg_clauses(t):
        if not _expg_prolapse(s):continue
        m=re.search(r"(?:POP\s*[- ]?\s*Q|POPQ).{0,12}?("+high+r")|(?:盆腔器官脱垂|盆底器官脱垂|子宫脱垂|阴道(?:前壁|后壁|穹隆)脱垂|uterine prolapse|pelvic organ prolapse|prolapse).{0,12}?("+high+r")",s,re.I)
        if m:return "IV" if _expe_has(m.group(0),r"IV|Ⅳ|4|四") else "III"
        if re.search(r"(?:POP\s*[- ]?\s*Q|POPQ).{0,12}?"+low+r"|(?:盆腔器官脱垂|盆底器官脱垂|子宫脱垂|阴道(?:前壁|后壁|穹隆)脱垂).{0,12}?"+low,s,re.I):return "LOW"
    return None
def _expg_qual_normal(t):return _expe_has(t,r"肝肾功能(?:正常|无明显异常|未见明显异常)|肝功能(?:正常|无明显异常|未见明显异常)|肾功能(?:正常|无明显异常|未见明显异常)|(?:AST|ALT|BUN|Cr|Scr|肌酐|尿素氮)\s*(?:正常|未超过正常上限|within normal|normal)")
def _expg_age(t):
    m=re.search(r"(?:年龄\s*[:：]?\s*|aged\s+)?(\d{2,3})\s*(?:岁|years? old|year-old)",t,re.I);return int(m.group(1)) if m else None
def _expg_zoster(t):return _expe_has(t,r"带状疱疹|带状疱疹病毒|herpes zoster|\bzoster\b|\bHZ\b|VZV reactivation")
def _expg_face(t):return _expe_has(t,r"头面部|面部|额部|眼周|眼部|耳部|颅面|三叉神经|\bV1\b|ophthalmic|facial")
def _expg_disease(t):return _expe_has(t,r"乙型肝炎|乙肝|HBV|hepatitis B|HIV|AIDS|结核|TB|tuberculosis|结缔组织病")
def _expg_active(t):return _expe_has(t,r"活动期|活动性|当前感染|现症|现患|正在治疗|治疗中|抗结核治疗|未控制|未治愈|持续感染|\bactive\b|\bongoing\b|currently treated|\bpersistent\b")
def _expg_invasive(t):return _expe_has(t,r"机械通气|呼吸机支持|气管插管|有创(?:机械)?通气|invasive ventilation|remained intubated|\bventilat(?:ed|ion)\b") and not (_expe_has(t,r"NIV|无创通气|non[- ]?invasive") and not _expe_has(t,r"有创|气管插管|invasive ventilation"))
def _expg_postop_relation(t):
    ss=split_text(t)
    for i,s in enumerate(ss):
        if _expe_has(s,r"计划|拟行|planned|术前|pre[- ]?op"):continue
        if _expe_has(s,r"术后|术毕|手术后|post[- ]?op|postoperative|after (?:surgery|operation)") and _expg_invasive(s):return "SAME_SENTENCE"
        if _expe_has(s,r"手术|surgery|operation") and i+1<len(ss) and _expe_has(ss[i+1],r"术后|术毕|手术后|post[- ]?op|postoperative|after") and _expg_invasive(ss[i+1]):return "ADJACENT_SENTENCE"
    return None

def _expg_hard_contradiction(cid,t):
    if cid=="485":
        stage=_expg_stage(t)
        if stage=="LOW":return "EXPLICIT_LOW_STAGE"
        if _expg_prolapse(t) and stage is None and _expe_has(t,r"(?:癌|cancer|NYHA|压疮|pressure ulcer|CKD).{0,12}(?:III|IV|Ⅲ|Ⅳ|[34])(?:期|度|级)?"):return "UNBOUND_STAGE_CONTEXT"
        if _expe_has(t,r"否认|未见|无") and _expg_prolapse(t):return "EXPLICIT_DENIAL"
    if cid=="635":
        for names in ("AST","ALT",("BUN","尿素氮"),("Cr","creatinine","肌酐")):
            pair=_lab_high(t,names)
            if pair and pair[0]>2*pair[1]:return "EXPLICIT_THRESHOLD_VIOLATION"
    if cid=="855":
        labs=_labs_855(t)
        if labs["Scr"] is not None and labs["Scr"]>=178:return "EXPLICIT_THRESHOLD_VIOLATION"
        if labs["BUN"] is not None and labs["BUN"]>=9:return "EXPLICIT_THRESHOLD_VIOLATION"
        if any(labs[x] and labs[x][0]>labs[x][1] for x in ("ALT","AST")):return "EXPLICIT_THRESHOLD_VIOLATION"
    if cid=="675" and _expe_has(t,r"否认|未见|无") and _expg_zoster(t):return "EXPLICIT_DENIAL"
    if cid=="735" and _expe_has(t,r"既往史|感染史|已治愈|已缓解|inactive|resolved|history only|稳定病史|stable history"):return "RESOLVED_OR_HISTORY_ONLY"
    if cid=="745":
        if _expe_has(t,r"计划|拟行|planned"):return "PLANNED_ONLY"
        if _expe_has(t,r"术前|pre[- ]?op") and not _expe_has(t,r"术后|术毕|手术后|post[- ]?op|postoperative"):return "PREOPERATIVE_ONLY"
        if _expe_has(t,r"NIV|无创通气|non[- ]?invasive") and not _expe_has(t,r"有创|气管插管|invasive ventilation"):return "NON_INVASIVE_ONLY"
    return None

def _expg_rule(cid,t):
    if cid=="485":return (True,"RULE_STAGE") if _expg_stage(t) in ("III","IV") else (None,None)
    if cid=="635":
        labs=_labs_635(t)
        if labs:return (all(v<=2*h for v,h in labs.values()),"RULE_LABS")
    if cid=="855":
        labs=_labs_855(t)
        if all(labs.values()):return (labs["Scr"]<178 and labs["BUN"]<9 and labs["ALT"][0]<=labs["ALT"][1] and labs["AST"][0]<=labs["AST"][1],"RULE_LABS")
    if cid=="675":
        age=_expg_age(t)
        if _expg_zoster(t) and (_expg_face(t) or (age is not None and age>=50)):return (True,"RULE_ZOSTER")
    if cid=="735" and _expg_disease(t) and _expg_active(t):return (True,"RULE_ACTIVE_DISEASE")
    if cid=="745" and _expg_postop_relation(t):return (True,"RULE_POSTOP_VENTILATION")
    return (None,None)

def _expg_semantic(cid,t):
    if cid=="485":return _expg_prolapse(t) and _expg_stage(t) in ("III","IV")
    if cid in ("635","855"):return _expg_qual_normal(t) or _expe_has(t,r"AST|ALT|BUN|Scr|Cr|creatinine|肌酐|尿素氮")
    if cid=="675":return _expg_zoster(t) and (_expg_face(t) or ((_expg_age(t) or 0)>=50))
    if cid=="735":return _expg_disease(t)
    if cid=="745":return _expg_postop_relation(t) is not None
    return False

def _expg_payload(cid,reports,decision,w):
    v=_expg_e_payload(cid,reports,decision,w) or {}
    if cid=="485" and decision=="MATCH":
        stage=_expg_stage(_expe_text(w))
        if stage in ("III","IV"):v["stage"]=stage
    return v

def _expg_reason(cid,t,mode,rule_reason):
    if mode=="RULE":
        if cid=="485" and not _expe_has(t,r"POP[- ]?Q|盆腔器官脱垂"):return "ALIAS_RECOVERY"
        if cid=="745" and _expg_postop_relation(t)=="ADJACENT_SENTENCE":return "CROSS_SENTENCE_RELATION"
        return "RULE_DIRECT"
    if cid in ("635","855") and _expg_qual_normal(t):return "QUALITATIVE_LAB_NORMAL"
    if cid in ("635","855"):return "PARTIAL_LAB_SUPPORTED"
    return "PARTIAL_GROUNDED_SEMANTIC"

class FHIRResourceBundleGenerator(_ExperimentEGenerator):
    def parse_clinical_text_to_fhir_bundle(self,patient_id,case_reports,ai_algorithm_type="nlp"):
        reports=normalize_reports(case_reports);w=retrieve_evidence(reports,SPEC);cid=str(TITLE);t="。".join(r["text"] for r in reports);deterministic,reason=_expg_rule(cid,t);attempts=0;parse="NA";transport="NA";prompt_len=0;model="NA";contradiction=_expg_hard_contradiction(cid,t);expansion="NONE"
        if deterministic is True and not contradiction:decision="MATCH";mode="RULE";expansion=_expg_reason(cid,t,mode,reason)
        elif deterministic is False or contradiction:decision="NO_MATCH";mode="RULE";reason=reason or contradiction or "EXPLICIT_NEGATIVE"
        else:
            llm,parse,attempts,prompt_len,transport=llm_decide(_expg_spec(SPEC),w,self.transport);model=llm;anchors=w.metrics["true_anchor_hits"]
            if anchors>=1 and llm=="MATCH" and not contradiction and _expg_semantic(cid,t):decision="MATCH";mode="PARTIAL_GROUNDED";expansion=_expg_reason(cid,t,mode,reason)
            elif anchors==0 and w.metrics["fallback_used"] and llm=="MATCH":decision="NO_MATCH";mode="FALLBACK_BLOCK";reason="ZERO_ANCHOR_FALLBACK_BLOCK"
            else:decision="NO_MATCH";mode="FALLBACK_BLOCK" if w.metrics["fallback_used"] else "RULE";reason=reason or "INSUFFICIENT_GROUNDED_EVIDENCE"
        v=_expg_payload(cid,reports,decision,w)
        if decision!="MATCH":resources=[]
        elif cid=="855" and "build_expc_resources" in globals():resources=build_expc_resources(cid,str(patient_id),v,derive_transport_meta(cid,reports,w,v))
        else:resources=build_resources(cid,str(patient_id),v)
        reason=reason or ("MATCH" if decision=="MATCH" else "NO_MATCH");m=w.metrics
        print("V5S3G_METRICS|criterion="+cid+"|anchor_hits="+str(m["true_anchor_hits"])+"|groups_hit="+str(m["groups_hit"])+"|groups_required="+str(m["groups_required"])+"|fallback_used="+str(int(m["fallback_used"]))+"|model_decision="+model+"|hard_contradiction="+str(contradiction or "NONE")+"|admission_mode="+mode+"|final_decision="+decision+"|resources="+str(len(resources))+"|expansion_reason="+expansion+"|reason="+reason)
        return {"resourceType":"Bundle","type":"transaction","entry":[{"resource":r,"request":{"method":"POST","url":r["resourceType"]}} for r in resources]}
'''
