"""Evidence states and B-only constraints. Standalone-safe for embedded Libraries."""
import html
import json
import re
import uuid
from datetime import datetime

B_VERSION = "b1-evidence"
B_IDS = ("2", "3", "85", "205", "225", "255", "295", "465", "475", "495", "525", "585", "625", "695", "715", "765")
TERMINOLOGY = "http://localhost:3456/api/terminology/"
ACCEPTED = {"PRESENT", "HISTORICAL"}
PATTERNS = {
    "respiratory": r"咳嗽|胸闷|气短|气促|气急|呼吸困难|喘憋|喘息|dyspn(?:ea|oea)|cough|shortness of breath",
    "hcc": r"肝细胞癌|(?<![A-Za-z])HCC(?![A-Za-z])|hepatocellular carcinoma",
    "pathology": r"病理|活检证实|组织学证实|histolog|patholog|biopsy.confirm",
    "resection": r"(?:肝|肝癌)[^，,。；\n]{0,12}(?:切除|切术)|hepatectomy|liver resection",
    "r0": r"(?<![A-Za-z0-9])R0(?![A-Za-z0-9])|切缘阴性|根治(?:性)?(?:肝|肝癌)?切除|根治性手术切除|negative margins",
    "elective": r"择期|计划|拟行|拟择期|scheduled|elective|planned",
    "thoracoscopy": r"胸腔镜|(?<![A-Za-z])VATS(?![A-Za-z])|thoracoscop",
    "lung_resection": r"肺(?:叶|段|楔形|大疱|癌)?(?:切除|根治)|(?:肺[^。；\n]{0,10}切除)|lobectomy|pneumonectomy|segmentectomy",
    "thoracic_surgery": r"胸部手术|胸外科手术|(?:肺|食管|纵隔|胸壁|心脏)[^。；\n]{0,12}(?:手术|切除|根治术)|thoracic surgery|lobectomy",
    "general_anesthesia": r"全麻|全身麻醉|general an[ae]esthesia|\bGA\b",
    "radiotherapy": r"放疗|放射治疗|radiotherapy|radiation therapy|IMRT|SBRT",
    "t2dm": r"(?:2|Ⅱ|II|二)\s*型糖尿病|(?<![A-Za-z])T2DM(?![A-Za-z])|type\s*2\s*diabetes",
    "renal_biopsy": r"肾(?:脏)?(?:活检|穿刺)|renal biopsy|kidney biopsy|肾组织[^。；]{0,12}病理",
    "autoimmune_renal": r"原发性膜性肾病|ANCA[^。；]{0,12}(?:血管炎|肾)|狼疮性肾炎|IgA\s*肾病|微小病变肾病|局灶节段性肾小球硬化|膜增生性肾小球肾炎|新月体性肾小球肾炎|抗(?:GBM|肾小球基底膜)病|紫癜性肾炎|过敏性紫癜肾炎|C3肾小球病|干燥综合征肾炎|lupus nephritis|IgA nephropathy|primary membranous nephropathy",
    "pain": r"疼痛|腰痛|颈痛|背痛|pain",
    "spinal_cause": r"脊柱(?:源性|病变|退变|损伤|炎症|肿瘤)|腰椎间盘突出|椎管狭窄|颈椎病|spondylosis|spinal (?:disease|degeneration)",
    "pain_relation": r"(?:导致|所致|引起|源性|原因为|继发于)|caused by|due to",
    "dlbcl": r"弥漫(?:性)?大\s*B\s*细胞淋巴瘤|(?<![A-Za-z])DLBCL(?![A-Za-z])|diffuse large B.cell lymphoma",
    "esophageal": r"食管癌|食道癌|esophageal (?:cancer|carcinoma)",
    "middle_lower": r"(?:胸)?中下段|(?:胸)?中段|(?:胸)?下段|middle|lower",
    "preoperative": r"术前|拟手术|拟行[^。；]{0,12}手术|preoperative|pre.op",
    "low_back_pain": r"腰痛|下背痛|腰背痛|low back pain|lumbago",
    "distant": r"远处转移|(?<![A-Za-z0-9])M1[a-c]?(?![A-Za-z0-9])|(?:骨|脑|肝|肺|肾上腺)转移|distant metastas",
    "history_hypoxia": r"窒息(?:缺氧)?史|缺氧(?:病)?史|(?:曾|既往|出生时|新生儿)[^。；]{0,12}(?:窒息|缺氧)|history of (?:asphyxia|hypoxia|suffocation)",
}
REQUIRED = {
    "2": ("respiratory",), "3": ("hcc", "pathology", "resection", "r0"),
    "85": ("elective", "thoracoscopy", "lung_resection"),
    "205": ("elective", "thoracic_surgery", "general_anesthesia"),
    "225": ("radiotherapy",), "255": ("t2dm",), "295": ("smoking_eligible",),
    "465": ("renal_biopsy", "autoimmune_renal"),
    "475": ("pain", "spinal_cause", "pain_relation", "duration"),
    "495": ("dlbcl", "pathology"), "525": ("esophageal", "middle_lower", "preoperative"),
    "585": ("low_back_pain", "duration"), "625": ("labs",),
    "695": ("distant",), "715": ("ivc_clear", "portal_clear"), "765": ("history_hypoxia",),
}
NEGATIVE = r"否认|未见|没有|不伴|未诉|排除|未证实|未提示|未接受|不行|无(?:明显)?|未发生|未行"
UNCERTAIN = r"可能|疑似|考虑|不排除|待排|可疑|suspect|possible|cannot exclude"
PLANNED = r"拟|计划|建议|准备|待行|将行|planned|scheduled|recommend"
HISTORICAL = r"既往|曾|此前|术后|已完成|已行|previous|history|underwent"
RESOLVED = r"已(?:完全)?(?:消失|缓解|治愈)|resolved"


def _has(pattern, text):
    return bool(re.search(pattern, text, re.I))


def _normal(text):
    return re.sub(r"\s+", " ", html.unescape(str(text))).strip()


def _fact(atom, state="UNKNOWN", evidence="", report=None, value=None):
    return {"atom": atom, "state": state, "evidence": evidence, "report": report, "value": value, "source": "deterministic"}


def _state(text, start, end, atom, topic=""):
    # Commas delimit unrelated findings; enumeration punctuation retains shared negation.
    left = re.split(r"[，,。；;\n]|但|然而", text[:start])[-1]
    right = re.split(r"[，,。；;\n]|但|然而", text[end:])[0]
    local = left + text[start:end] + right
    if _has(r"父亲|母亲|家族|家属|其父|其母", left):
        return "ABSENT"
    if _has(UNCERTAIN, left) or _has(r"(?:待排|可能|可疑)$", right):
        return "UNCERTAIN"
    if _has(NEGATIVE, left) or _has(r"^(?:阴性|未证实|不存在)", right):
        return "NEGATED"
    if atom == "pathology" and _has(r"^\s*(?:未明确|未回报|结果待回|待回报|待证实)", right):
        return "UNCERTAIN"
    if _has(RESOLVED, local) and atom in ("respiratory", "pain", "low_back_pain"):
        return "ABSENT"
    if _has(PLANNED, left):
        return "PLANNED"
    if _has(HISTORICAL, local) or topic == "手术记录":
        return "HISTORICAL"
    return "PRESENT"


def _duration_facts(reports, cid):
    out = []
    target = PATTERNS["low_back_pain" if cid == "585" else "pain"]
    pain_reports = [i for i,r in enumerate(reports) if _has(target, r.get("text", ""))]
    for i,r in enumerate(reports):
        text = r.get("text", "")
        if not _has(target, text) and not (pain_reports and _has(r"疼痛持续|症状持续|持续时间", text)):
            continue
        for sentence in re.split(r"[。；;\n]", text):
            if not _has(target + r"|疼痛持续|症状持续|持续时间", sentence):
                continue
            m = re.search(r"(\d+(?:\.\d+)?|三|四|五|六|二|一|十)\s*个?\s*(月|年|周|天)", sentence)
            number = None
            if m:
                nums = {"一":1,"二":2,"三":3,"四":4,"五":5,"六":6,"十":10}
                number = float(nums[m[1]]) if m[1] in nums else float(m[1])
                number *= {"年":12,"月":1,"周":7/30.4375,"天":1/30.4375}[m[2]]
            elif "半年" in sentence:
                number = 6.0
            elif _has(r"数年|多年", sentence):
                number = 24.0
            elif "自去年" in sentence and r.get("timestamp"):
                try:
                    now = datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00"))
                    number = float(now.month)  # Even December last year is >=3 months after March.
                    if number < 3:
                        number = None
                except ValueError:
                    pass
            if number is not None:
                state = "PRESENT" if number >= 3 else "NEGATED"
                if _has(UNCERTAIN, sentence):
                    state = "UNCERTAIN"
                out.append(_fact("duration", state, sentence, i, number))
    return out


def _smoking(reports):
    out = []
    joined = "。".join(r.get("text", "") for r in reports)
    current = _has(r"目前|现(?:在)?|近三个月|近3个月|current", joined)
    if not current and _has(r"吸烟|抽烟",joined) and not _has(r"既往|曾|过去|吸烟史|戒烟|已戒|停止吸烟",joined):
        current = True
    for i,r in enumerate(reports):
        text = r.get("text", "")
        if _has(r"不能保证[^。；]{0,15}(?:停止吸烟|戒烟)|cannot guarantee.*stop smoking", text):
            out.append(_fact("smoking_eligible", "PRESENT", text, i, {"cannot_guarantee":True}))
        m = re.search(r"(?:(?:每天|每日|日均)\s*(?:吸烟)?\s*(\d+(?:\.\d+)?)\s*(支|包)|(?:吸烟|抽烟)?\s*(\d+(?:\.\d+)?)\s*(支|包)\s*[/／每]\s*(?:天|日))", text)
        if m:
            value = float(m[1] or m[3]) * (20 if (m[2] or m[4]) == "包" else 1)
            state = "PRESENT" if current and value > 5 else "NEGATED" if value <= 5 else "UNKNOWN"
            if _has(r"从不|否认|戒烟\s*\d+\s*年|已戒烟", joined):
                state = "NEGATED"
            elif _has(UNCERTAIN, text):
                state = "UNCERTAIN"
            out.append(_fact("smoking_eligible", state, text, i, {"cigarettes_per_day":value}))
    return out


def _vessels(reports):
    out = []
    targets = [("ivc_clear", r"下腔静脉|inferior vena cava|\bIVC\b"), ("portal_clear", r"门静脉|portal vein")]
    for i,r in enumerate(reports):
        for clause in re.split(r"[，,。；;\n]|但|然而", r.get("text", "")):
            for atom,pattern in targets:
                if not _has(pattern, clause):
                    continue
                state = "UNKNOWN"
                if _has(UNCERTAIN, clause):
                    state = "UNCERTAIN"
                elif _has(r"未(?:见|受)?(?:肿瘤)?(?:侵犯|侵及|受侵|侵)|无[^。；]{0,8}(?:侵犯|癌栓)|未见[^。；]{0,8}侵犯|not invaded|no invasion", clause):
                    state = "PRESENT"
                elif _has(r"侵犯|侵及|受侵|癌栓|invad", clause):
                    state = "NEGATED"
                out.append(_fact(atom, state, clause, i))
    return out


def _labs(reports):
    # Group by explicit encounter, otherwise report date. Never combine distinct dates.
    groups = {}
    for i,r in enumerate(reports):
        key = r.get("encounter_id") or (str(r.get("timestamp", ""))[:10] or "undated")
        group = groups.setdefault(key, {})
        text = r.get("text", "")
        for lab,alias in (("total_bilirubin",r"TBIL|总胆红素|total bilirubin"),("alt",r"ALT|丙氨酸氨基转移酶|谷丙转氨酶"),("ast",r"AST|天冬氨酸氨基转移酶|谷草转氨酶")):
            for m in re.finditer(r"(?<![A-Za-z])(?:" + alias + r")(?![A-Za-z])\s*[:：=]?\s*(\d+(?:\.\d+)?)\s*([^，,。；;\n]*?)(?=(?:TBIL|ALT|AST|总胆红素)|$|[，,。；;\n])", text, re.I):
                tail = m[2]
                value = float(m[1])
                uln_match = re.search(r"(?:ULN|正常上限|正常范围上限|上限)\s*[:：=]?\s*(\d+(?:\.\d+)?)", tail, re.I)
                range_match = re.search(r"(?:参考范围|正常范围|参考值)\s*[:：(（]?\s*\d+(?:\.\d+)?\s*[-~～至]\s*(\d+(?:\.\d+)?)", tail)
                ratio = _has(r"^\s*(?:倍\s*(?:正常上限|正常范围上限|ULN)|(?:×|x)?\s*ULN)", tail)
                high = float(uln_match[1]) if uln_match else float(range_match[1]) if range_match else 1.0 if ratio else None
                unit = "{ratio-to-ULN}" if ratio else (re.match(r"\s*([uμµ]?mol/L|U/L|mg/dL)", tail, re.I)[1] if re.match(r"\s*([uμµ]?mol/L|U/L|mg/dL)", tail, re.I) else None)
                if high is not None and high > 0 and not _has(UNCERTAIN + "|" + PLANNED + "|未查", text[:m.start()]):
                    group.setdefault(lab, []).append({"value":value,"high":high,"unit":unit,"evidence":m[0],"report":i})
    complete = []
    for key,group in groups.items():
        if set(group) == {"total_bilirubin", "alt", "ast"}:
            ok = all(all(x["value"] <= x["high"]*(1.5 if lab=="total_bilirubin" else 3) for x in values) for lab,values in group.items())
            complete.append(_fact("labs", "PRESENT" if ok else "NEGATED", json.dumps(group,ensure_ascii=False), value={"encounter":key,"labs":{k:v[-1] for k,v in group.items()}}))
    return complete


def extract_facts(cid, reports):
    cid = str(cid)
    if cid not in REQUIRED:
        raise ValueError("Unsupported B profile: " + cid)
    out = []
    for atom in REQUIRED[cid]:
        if atom not in PATTERNS:
            continue
        for i,r in enumerate(reports):
            text = html.unescape(r.get("text", ""))
            for m in re.finditer(PATTERNS[atom], text, re.I):
                state = _state(text,m.start(),m.end(),atom,r.get("topic", ""))
                if atom == "pathology" and state in ACCEPTED:
                    sentence = re.split(r"[。；;\n]", text[:m.start()])[-1] + re.split(r"[。；;\n]", text[m.start():])[0]
                    disease_pattern = PATTERNS["hcc" if cid=="3" else "dlbcl"]
                    heading_only = bool(re.fullmatch(r"\s*(?:病理|病理报告|病理检查|病理结果)[：:。\s]*",sentence))
                    if not _has(disease_pattern,sentence) and not heading_only:
                        out.append(_fact(atom,"UNCERTAIN",sentence,i))
                        continue
                if atom == "pain_relation":
                    sentence = re.split(r"[。；;\n]", text[:m.start()])[-1] + re.split(r"[。；;\n]", text[m.start():])[0]
                    if not _has(PATTERNS["spinal_cause"],sentence) or not _has(PATTERNS["pain"],sentence):
                        continue
                if cid in ("85","205") and state == "PLANNED":
                    state = "PRESENT"
                if cid in ("85","205") and _has(r"急诊|emergency", text):
                    state = "NEGATED"
                if atom == "preoperative" and state == "PLANNED":
                    state = "PRESENT"
                if atom in ("pathology", "renal_biopsy") and state == "PRESENT" and _has(r"拟|待行|计划", text[:m.start()]):
                    state = "PLANNED"
                out.append(_fact(atom,state,text,i))
    if cid in ("475","585"):
        out += _duration_facts(reports,cid)
    if cid == "295":
        out += _smoking(reports)
    if cid == "715":
        out += _vessels(reports)
    if cid == "625":
        out += _labs(reports)
    return out


def evaluate(cid, reports):
    cid = str(cid)
    facts = extract_facts(cid,reports)
    selected = {}
    for atom in REQUIRED[cid]:
        candidates = [f for f in facts if f["atom"] == atom]
        positive = next((f for f in candidates if f["state"] in ACCEPTED), None)
        # Lab eligibility is existential across encounters, unlike vessel contradictions.
        blocked = next((f for f in candidates if f["state"] in {"NEGATED","ABSENT"}), None)
        selected[atom] = (positive if atom == "labs" and positive else blocked or positive or next(iter(candidates),_fact(atom)))
    match = all(f["state"] in ACCEPTED for f in selected.values())
    return {"match":match,"decision":"MATCH" if match else "NO_MATCH","facts":selected,"evidence":facts,"reason":"ALL_REQUIRED_FACTS" if match else "INCOMPLETE_OR_BLOCKED_FACTS"}


def semantic_rescue(cid, reports, result, transport, question):
    """Structured suggestions may fill unknown categorical facts, never numeric facts."""
    if result["match"] or str(cid) in ("295","475","585","625","715"):
        return result
    if not any(f["state"] in ACCEPTED for f in result["facts"].values()):
        return result
    if any(f["state"] in {"NEGATED","ABSENT","PLANNED","UNCERTAIN"} for f in result["facts"].values()):
        return result
    schema = {a:{"state":"UNKNOWN","evidence":"","report":0} for a in REQUIRED[str(cid)]}
    prompt = "仅从患者原文提取事实，不能补充缺失事实。否定、疑似、计划分别用NEGATED、UNCERTAIN、PLANNED。已发生用PRESENT或HISTORICAL。返回JSON facts，每项附原文证据和报告序号。标准：" + question + "\n结构：" + json.dumps({"facts":schema},ensure_ascii=False) + "\n病历：" + json.dumps(reports,ensure_ascii=False)
    try:
        raw = transport(prompt)
        if isinstance(raw,dict):
            raw = raw.get("content",raw)
        if isinstance(raw,str):
            raw = json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip()))
        proposed = raw["facts"]
        merged = dict(result["facts"])
        for atom,old in merged.items():
            if old["state"] != "UNKNOWN":
                continue
            fact = proposed.get(atom,{})
            index = fact.get("report")
            quote = fact.get("evidence", "")
            if type(index) is not int or not 0 <= index < len(reports) or not isinstance(quote,str) or len(_normal(quote)) < 2:
                continue
            if _normal(quote).lower() not in _normal(reports[index].get("text", "")).lower():
                continue
            if fact.get("state") not in ACCEPTED or _has(UNCERTAIN + "|" + NEGATIVE + "|" + PLANNED, quote):
                continue
            merged[atom] = dict(_fact(atom,fact["state"],quote,index),source="semantic")
        ok = all(f["state"] in ACCEPTED for f in merged.values())
        return dict(result, facts=merged, match=ok, decision="MATCH" if ok else "NO_MATCH", reason="GROUNDED_SEMANTIC" if ok else result["reason"])
    except (ValueError,TypeError,KeyError,AttributeError):
        return result


def concept(system, code):
    return {"coding":[{"system":system if system.startswith("http") else TERMINOLOGY+"CodeSystem/"+system,"code":code}]}


PROFILE_NAMES = {
    "2":"cnwqk2", "3":"cnwqk3-condition", "85":"cnwqk85-lung-resection", "205":"cnwqk205-thoracic-surgery", "225":"cnwqk225-radiotherapy-procedure", "255":"cnwqk255-t2dm-diagnosis", "295":"cnwqk295-smokingstatus", "465":"cnwqk465-AutoimmuneNephropathyConditionProfile", "475":"cnwqk475-SpinalChronicPainDiagnosis", "495":"cnwqk495-PathologicalDiagnosisObservation", "525":"cnwqk525-esophageal-cancer-preop-diagnosis", "585":"cnwqk585-symptom-profile", "625":"cnwqk625-liver-function-tests", "695":"cnwqk695-neoplasm-status", "715":"cnwqk715-NeoplasmStatus", "765":"cnwqk765-condition-history",
}


def resource(kind, cid, patient, system, code, profile=None):
    name = profile or PROFILE_NAMES[cid]
    prefix = "StructureDefinition/" if cid in ("2","255") else "Profile/"
    r = {"resourceType":kind,"id":str(uuid.uuid4()),"meta":{"profile":[TERMINOLOGY+prefix+name]},"subject":{"reference":"Patient/"+str(patient)},"code":concept(system,code)}
    if kind == "Condition":
        r.update(clinicalStatus=concept("http://terminology.hl7.org/CodeSystem/condition-clinical","active"),verificationStatus=concept("http://terminology.hl7.org/CodeSystem/condition-ver-status","confirmed"),category=[concept("http://terminology.hl7.org/CodeSystem/condition-category","encounter-diagnosis")])
    else:
        r["status"] = "final" if kind == "Observation" else "completed"
    return r


def extension(url, system, code):
    return {"url":TERMINOLOGY+"StructureDefinition/"+url,"valueCodeableConcept":concept(system,code)}


def build_b_resources(cid, patient, reports, result):
    cid = str(cid)
    if not result["match"]:
        return []
    facts = result["facts"]
    text = "。".join(f["evidence"] for f in facts.values())
    timestamps = [reports[f["report"]].get("timestamp") for f in facts.values() if f.get("report") is not None]
    timestamp = next((t for t in timestamps if t),None)
    if cid == "2":
        code = "咳嗽" if _has(r"咳嗽|cough",text) else "胸闷" if "胸闷" in text else "气短" if _has(r"气短|气促|气急",text) else "呼吸困难"
        out = [resource("Observation",cid,patient,"cnwqk2",code)]
    elif cid == "3":
        r = resource("Procedure",cid,patient,"icd10","0FB00ZZ","cnwqk3-procedure")
        r["outcome"] = concept("cnwqk3","R0")
        out = [resource("Condition",cid,patient,"icd10","C22.0"),r]
    elif cid in ("85","205"):
        r = resource("Procedure",cid,patient,"cnwqk85-procedure-codes" if cid=="85" else "cnwqk205-thoracic-surgery-cs","pulmonary-lobectomy" if cid=="85" else "esophageal" if "食管" in text else "cardiac" if "心脏" in text else "mediastinal" if "纵隔" in text else "chestwall" if "胸壁" in text else "pulmonary")
        r["status"] = "preparation" if _has(PLANNED,text) else "completed"
        if cid == "85":
            r["extension"] = [extension("cnwqk85-procedure-priority","cnwqk85-priority-codes","elective"),extension("cnwqk85-surgical-approach","cnwqk85-approach-codes","thoracoscopic")]
        else:
            r["extension"] = [extension("anesthesia-method","cnwqk205-anesthesia-method-cs","GA"),extension("anesthesia-depth","cnwqk205-anesthesia-depth-cs","GA")]
        out = [r]
    elif cid == "225":
        r = resource("Procedure",cid,patient,"cnwqk225-radiotherapy-cs","radiotherapy")
        if _has(r"正在|接受中|进行中|undergoing",text):
            r["status"] = "in-progress"
        out = [r]
    elif cid == "255":
        out = [resource("Condition",cid,patient,"icd10","E11")]
    elif cid == "295":
        value = facts["smoking_eligible"]["value"] or {}
        r = resource("Observation",cid,patient,"cnwqk295-smokingcs","smoking-status-detail")
        r["component"] = []
        if "cigarettes_per_day" in value:
            r["component"].append({"code":concept("cnwqk295-smokingcs","number-of-cigarettes-per-day"),"valueQuantity":{"value":value["cigarettes_per_day"],"unit":"支/日"}})
        if value.get("cannot_guarantee"):
            r["component"].append({"code":concept("cnwqk295-smokingcs","smoking-cessation-guarantee"),"valueCodeableConcept":concept("cnwqk295-guaranteecs","cannot-guarantee")})
        if timestamp:
            # FHIR dateTime allows day precision; official 295 mixes naive/aware datetimes.
            # Retain the observed calendar date, without inventing a smoking start date.
            r["effectivePeriod"] = {"start":str(timestamp)[:10]}
        out = [r]
    elif cid == "465":
        codes = [("IgA|iga","iga-nephropathy"),("狼疮|lupus","lupus-nephritis"),("膜性|membranous","primary-membranous-nephropathy"),("ANCA","anca-associated-vasculitis"),("微小","minimal-change-disease"),("局灶","focal-segmental-glomerulosclerosis"),("新月体","crescentic-glomerulonephritis"),("紫癜","henoch-schonlein-purpura-nephritis"),("GBM|基底膜","anti-gbm-disease"),("C3","c3-glomerulopathy"),("干燥","sjogren-syndrome-nephritis"),("膜增生","membranoproliferative-glomerulonephritis")]
        code = next((code for p,code in codes if _has(p,facts["autoimmune_renal"]["evidence"])),None)
        if code is None:
            return []
        out = [resource("Procedure",cid,patient,"cnwqk465-RenalBiopsyProcedureCodeSystem","renal-biopsy","cnwqk465-RenalBiopsyProcedureProfile"),resource("Condition",cid,patient,"cnwqk465-AutoimmuneNephropathyCodeSystem",code)]
    elif cid == "475":
        r = resource("Condition",cid,patient,"cnwqk475-DiagnosisCS","spinal_chronic_pain")
        cause = "spinal_tumor" if "肿瘤" in text else "spinal_injury" if "损伤" in text else "spinal_inflammation" if "炎症" in text else "spinal_degeneration"
        r["extension"] = [extension("cnwqk475-pain-cause","cnwqk475-CauseCS",cause),extension("cnwqk475-pain-duration","cnwqk475-DurationCS","more_than_3_months")]
        out = [r]
    elif cid == "495":
        r = resource("Observation",cid,patient,"cnwqk495-ObservationTypesCS","pathological-diagnosis")
        r.update(valueCodeableConcept=concept("icd10","C83.3"),method=concept("cnwqk495-MethodsCS","pathological-exam"))
        out = [r]
    elif cid == "525":
        code = "C15.5" if "下段" in text else "C15.2"
        r = resource("Condition",cid,patient,"icd10",code)
        r.update(category=[concept("cnwqk525-diagnosis-category-codes","preoperative-diagnosis")],bodySite=[concept("icdo3",code)])
        out = [r]
    elif cid == "585":
        r = resource("Observation",cid,patient,"icd10","M54.5")
        r["component"] = [{"code":concept("cnwqk585-symptom-component-cs","duration"),"valueQuantity":{"value":facts["duration"]["value"],"unit":"月","system":"http://unitsofmeasure.org","code":"mo"}}]
        out = [r]
    elif cid == "625":
        out = []
        for lab,item in facts["labs"]["value"]["labs"].items():
            r = resource("Observation",cid,patient,"cnwqk625-laboratory-tests-cs",lab)
            quantity = {"value":item["value"]}
            high = {"value":item["high"]}
            if item["unit"]:
                quantity["unit"] = high["unit"] = item["unit"]
            r.update(valueQuantity=quantity,referenceRange=[{"type":concept("http://hl7.org/fhir/referencerange-meaning","normal"),"high":high}])
            date = reports[item["report"]].get("timestamp")
            if date:
                r["effectiveDateTime"] = date
            out.append(r)
    elif cid == "695":
        r = resource("Observation",cid,patient,"http://loinc.org","88040-1")
        r.update(valueCodeableConcept=concept("cnwqk695-neoplasm-status-cs","with_distant_metastasis"),category=[concept("http://terminology.hl7.org/CodeSystem/observation-category","clinical")])
        out = [r]
    elif cid == "715":
        r = resource("Observation",cid,patient,"cnwqk715-ObservationCS","neoplasm_infiltration_status")
        r["component"] = [{"code":concept("cnwqk715-InfiltrationSiteCS",site),"valueCodeableConcept":concept("cnwqk715-YesNoCS","no")} for site in ("inferior_vena_cava","portal_vein")]
        out = [r]
    else:
        out = [resource("Condition",cid,patient,"cnwqk765-history-codesystem","suffocation" if "窒息" in text else "hypoxia")]
    for r in out:
        if timestamp and cid != "625":
            if r["resourceType"] == "Observation" and cid != "295":
                r["effectiveDateTime"] = timestamp
            elif r["resourceType"] == "Procedure" and r["status"] == "completed":
                r["performedDateTime"] = timestamp
        # Original evidence is escaped before insertion into FHIR XHTML.
        r["text"] = {"status":"generated","div":'<div xmlns="http://www.w3.org/1999/xhtml">'+html.escape(text)+'</div>'}
    return out
