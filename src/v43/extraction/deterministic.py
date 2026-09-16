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


_EXTRACTORS={"185":_extract_185,"675":_extract_675,"745":_extract_745,"875":_extract_875}


def extract_deterministic(ir, packet):
    return _EXTRACTORS[str(ir.criterion_id)](packet)
