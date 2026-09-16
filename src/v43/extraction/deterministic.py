import re

from v43.clinical.models import AssertionState, ClinicalEvent, ClinicalFact, ClinicalRelation


def parse_number(text: str):
    match = re.search(r"(?<!\d)(\d+(?:\.\d+)?)", text)
    return float(match.group(1)) if match and "." in match.group(1) else (int(match.group(1)) if match else None)


def normalize_unit(unit: str):
    return {"岁": "year", "年": "year", "小时": "h"}.get(unit, unit)


def normalize_date(text: str):
    match = re.fullmatch(r"\s*(\d{4})[年/-](\d{1,2})[月/-](\d{1,2})日?\s*", text)
    if match is None:
        return None
    year, month, day = (int(value) for value in match.groups())
    return f"{year:04d}-{month:02d}-{day:02d}"


def subject_of(text: str) -> str:
    return "family" if re.search(r"母亲|父亲|家族|姐姐|妹妹|兄弟|子女", text) else "patient"


def is_negated(text: str) -> bool:
    explicit = r"否认|未见|没有|未(?:接受|确诊|行|予|使用)|(?:已)?排除"
    target_absence = r"(?:目前)?无(?:颅内高压|颅内压升高|意识不清|神志朦胧|带状疱疹)"
    return bool(re.search(rf"{explicit}|{target_absence}", text))


def is_planned(text: str) -> bool:
    return bool(re.search(r"计划|拟(?:行|于|接受|使用|予)?|准备|待(?:行|予)?|将行|术前", text))


def _fact(span, n, concept, *, value=None, unit=None, state=AssertionState.PRESENT, subject="patient"):
    return ClinicalFact(f"f-{span.span_id}-{n}", "assertion", concept, value, unit, state, subject,
                        "current", span.timestamp, span.span_id, span.report_index, 1.0, "deterministic")


def _event(span, n, event_type, concept, attributes=None):
    return ClinicalEvent(f"e-{span.span_id}-{n}", event_type, concept, "occurred", attributes or {},
                         "patient", span.timestamp, None, "current", None, (span.span_id,),
                         (span.report_index,), 1.0, "deterministic")


def _extract_185(packet):
    events = []
    for span in packet.spans:
        text = span.text
        if not re.search(r"伊立替康|irinotecan|CPT-?11", text, re.I) or subject_of(text) != "patient": continue
        if is_negated(text) or is_planned(text) or re.search(r"既往|曾经|多次|方案.*(?:含|提及)", text): continue
        if not re.search(r"给药|接受|应用|输注|化疗", text): continue
        first = _fact(span, "first", "first_use", state=AssertionState.PRESENT if re.search(r"首次|初次|首程", text) else AssertionState.UNKNOWN)
        events.append(_event(span, 0, "MedicationAdministration", "irinotecan", {"first_use": first,
                      "planned_only": _fact(span, "planned", "planned_only", state=AssertionState.ABSENT),
                      "previous_multiple_use": _fact(span, "prior", "previous_multiple_use", state=AssertionState.ABSENT)}))
    return (), tuple(events), ()


def _extract_675(packet):
    facts=[]; events=[]; relations=[]
    for span in packet.spans:
        text=span.text
        age=re.search(r"(?:年龄|患者)?\s*(\d{1,3})\s*岁", text)
        if age and subject_of(text)=="patient": facts.append(_fact(span, 0, "patient_age", value=int(age.group(1)), unit="year"))
        if "带状疱疹" in text and subject_of(text)=="patient" and not is_negated(text) and re.search(r"确诊|诊断|患", text):
            event=_event(span, 0, "Diagnosis", "herpes_zoster"); events.append(event)
            if re.search(r"头面部|头部|面部|颜面|眼周|耳周", text):
                site=_fact(span, "site", "head_face_site", value="head_face")
                facts.append(site)
                relations.append(ClinicalRelation(f"r-{span.span_id}", event.event_id, site.fact_id, "LOCATED_AT",
                                 AssertionState.PRESENT, (span.span_id,), (span.report_index,), 1.0, "deterministic"))
    return tuple(facts), tuple(events), tuple(relations)


def _extract_745(packet):
    events=[]; relations=[]
    for span in packet.spans:
        text=span.text
        if subject_of(text)!="patient" or is_negated(text): continue
        surgery=None
        if re.search(r"手术|术后|切除术", text) and not re.search(r"术前|计划|拟行", text):
            surgery=_event(span, "s", "Surgery", "Surgery"); events.append(surgery)
        if re.search(r"有创机械通气|气管插管", text) and not is_planned(text) and "无创" not in text:
            invasive=_fact(span, "invasive", "invasive", state=AssertionState.PRESENT)
            vent=_event(span, "v", "MechanicalVentilation", "MechanicalVentilation", {"invasive": invasive}); events.append(vent)
            if surgery and "术后" in text:
                relations.append(ClinicalRelation(f"r-{span.span_id}", vent.event_id, surgery.event_id, "POSTOPERATIVE_TO",
                                 AssertionState.PRESENT, (span.span_id,), (span.report_index,), 1.0, "deterministic"))
    return (), tuple(events), tuple(relations)


def _extract_875(packet):
    facts=[]
    for span in packet.spans:
        text=span.text
        if subject_of(text)!="patient": continue
        state=AssertionState.ABSENT if is_negated(text) else AssertionState.PRESENT
        if re.search(r"颅内高压|颅内压升高|ICP升高", text, re.I): facts.append(_fact(span, 0, "intracranial_hypertension", state=state))
        if re.search(r"意识不清|神志朦胧|意识模糊|昏迷|嗜睡|呼之能应", text): facts.append(_fact(span, 1, "consciousness_impairment", state=state))
    return tuple(facts), (), ()


def _phase2_facts(packet, criterion):
    facts=[]; events=[]
    for span in packet.spans:
        text=span.text
        if subject_of(text)!="patient" or is_negated(text): continue
        def fact(concept, value=True, unit=None): facts.append(_fact(span, len(facts), concept, value=value, unit=unit))
        if criterion=="265" and re.search(r"术前", text):
            for concept, marker in (("ctni", r"cTnI"), ("ctnt", r"cTnT")):
                match=re.search(marker+r"\s*[:：]?\s*(\d+(?:\.\d+)?)\s*(?:μ|u)g/L", text, re.I)
                if match: fact(concept, float(match.group(1)), "ug/L")
        elif criterion=="615":
            if re.search(r"pT(?:3a|3b|4)", text, re.I): fact("pt_high")
            if re.search(r"(?:切缘\s*)?R1", text, re.I): fact("margin_r1")
            if re.search(r"pN1", text, re.I): fact("pn1")
            match=re.search(r"(?:Gleason|GS)(?:评分)?\s*[:：]?\s*(\d+)", text, re.I)
            if match: fact("gleason_score", int(match.group(1)), "score")
            match=re.search(r"PSA\s*[:：]?\s*(\d+(?:\.\d+)?)\s*ng/mL", text, re.I)
            if match: fact("psa", float(match.group(1)), "ng/mL")
        elif criterion=="635":
            for lab in ("AST","ALT","BUN","Cr"):
                match=re.search(lab+r"\s*(\d+(?:\.\d+)?)\s*([A-Za-zμ/]+).*?(?:参考)?上限\s*(\d+(?:\.\d+)?)", text, re.I)
                if match and float(match.group(3))>0:
                    value,unit,high=float(match.group(1)),match.group(2),float(match.group(3))
                    fact(lab,value,unit); fact(lab+"_high",high,unit); fact(lab+"_ratio",value/high,"ratio")
        elif criterion=="755":
            match=re.search(r"机械通气(?:持续)?\s*(\d+(?:\.\d+)?)\s*(小时|h)", text, re.I)
            if match: fact("ventilation_duration", float(match.group(1)), "h")
        elif criterion=="855":
            patterns=(("Scr",r"Scr\s*(\d+(?:\.\d+)?)\s*(?:μ|u)mol/L","umol/L"),("BUN",r"BUN\s*(\d+(?:\.\d+)?)\s*mmol/L","mmol/L"))
            for concept,pattern,unit in patterns:
                match=re.search(pattern,text,re.I)
                if match: fact(concept,float(match.group(1)),unit)
            for lab in ("ALT","AST"):
                match=re.search(lab+r"\s*(\d+(?:\.\d+)?)\s*U/L\s*(?:参考)?上限\s*(\d+(?:\.\d+)?)",text,re.I)
                if match: fact(lab+"_ratio",float(match.group(1))/float(match.group(2)),"ratio")
        elif criterion=="805":
            if re.search(r"目前|当前|每日",text) and re.search(r"吸烟|烟民",text) and not re.search(r"戒烟|从不",text): fact("current_smoker")
            match=re.search(r"戒烟\s*(\d+(?:\.\d+)?)\s*年",text)
            if match: fact("cessation_elapsed",float(match.group(1)),"year")
        elif criterion=="555":
            match=re.search(r"(\d+(?:\.\d+)?)\s*个月前.*(?:手术|切除术)",text)
            if match: fact("surgery_months",float(match.group(1)),"month")
        elif criterion=="485":
            if re.search(r"盆腔器官脱垂|子宫脱垂",text): fact("pelvic_organ_prolapse")
            if re.search(r"POP-?Q\s*(?:分期)?\s*(?:III|IV|3|4)(?:期|度)?",text,re.I): fact("popq_high_grade")
        elif criterion=="735":
            disease=r"甲型肝炎|乙型肝炎|甲肝|乙肝|HIV|AIDS|艾滋|结核|传染(?:性)?疾病|结缔组织病"
            if re.search(disease,text,re.I) and re.search(r"活动性|活动期|正在治疗|未控制",text) and not re.search(r"稳定|缓解|治愈|既往",text): fact("active_target_disease")
        elif criterion=="835":
            if re.search(r"凝血(?:功能)?(?:异常|障碍|紊乱)",text) and not re.search(r"正常|未见异常",text): fact("coagulation_abnormality")
        elif criterion=="565":
            resolved=bool(re.search(r"已?缓解|已恢复|既往",text))
            if not resolved and re.search(r"严重|重度",text) and re.search(r"腹泻",text): fact("severe_diarrhea")
            if not resolved and re.search(r"严重|重度",text) and re.search(r"便秘",text): fact("severe_constipation")
        elif criterion=="165":
            if re.search(r"化疗",text) and re.search(r"外院|当地医院|转入我院前",text) and re.search(r"完成|接受|已行|治疗",text) and not is_planned(text):
                outside=_fact(span,"outside","outside_hospital")
                events.append(_event(span,0,"MedicationAdministration","chemotherapy",{"outside_hospital":outside}))
    return tuple(facts),tuple(events),()


_EXTRACTORS={"185":_extract_185,"675":_extract_675,"745":_extract_745,"875":_extract_875}


def extract_deterministic(ir, packet):
    criterion=str(ir.criterion_id)
    return _EXTRACTORS[criterion](packet) if criterion in _EXTRACTORS else _phase2_facts(packet,criterion)
