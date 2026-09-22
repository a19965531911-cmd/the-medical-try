"""Non-production V6 patient-level fact engine prototype.

The prototype is deliberately limited to six MVP criteria, uses plain
dictionaries/lists, performs no network calls, and is not imported by any
submission builder.
"""

from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from v43.fhir.contracts import BASE, contract_for_criterion
from v43.fhir.service_replay import replay_service


MVP_CRITERIA = ("555", "565", "675", "735", "745")


def normalize_reports(case_reports):
    reports = []
    for index, report in enumerate(case_reports or []):
        text = str(report.get("text", "") if isinstance(report, dict) else report)
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            reports.append({"index": index, "text": text,
                            "timestamp": report.get("timestamp") if isinstance(report, dict) else None})
    return reports


def _sentences(text):
    return [part.strip() for part in re.split(r"[。！？!?；;\n]+", text) if part.strip()]


def _date(text):
    match = re.search(r"(20\d{2})[-/年](\d{1,2})[-/月](\d{1,2})日?", text)
    return f"{int(match.group(1)):04d}-{int(match.group(2)):02d}-{int(match.group(3)):02d}" if match else None


def _report_date(value):
    match = re.match(r"(20\d{2}-\d{2}-\d{2})", str(value or ""))
    return match.group(1) if match else None


def _flags(text):
    return {
        "negated": False,
        "planned": bool(re.search(r"计划|拟(?:行|予|用|接受)?|准备|待(?:行|予)?|将行|尚未", text)),
        "historical": bool(re.search(r"既往|曾经|曾有|病史", text)),
        "current": bool(re.search(r"目前|当前|现为|活动期|活动性|正在治疗|未控制", text)),
        "resolved": bool(re.search(r"已缓解|已恢复|已治愈|稳定|非活动期", text)),
    }


def _concept_negated(text, concept):
    patterns = {
        "smoking": r"否认吸烟|无吸烟(?:史)?|不吸烟",
        "mechanical_ventilation": r"否认(?:有创)?机械通气|未见(?:有创)?机械通气|(?<!创)无机械通气",
        "diarrhea": r"否认腹泻|未见腹泻|无腹泻",
        "constipation": r"否认便秘|未见便秘|无便秘",
        "herpes_zoster": r"否认[^。；，,]{0,8}带状疱疹|未见[^。；，,]{0,8}带状疱疹|无[^。；，,]{0,8}带状疱疹",
        "surgery": r"否认手术|无手术史|未行手术",
    }
    pattern = patterns.get(concept)
    return bool(pattern and re.search(pattern, text, re.I))


def _add(facts, fact_type, concept, report, evidence, flags, **values):
    flags = dict(flags)
    flags["negated"] = _concept_negated(evidence, concept)
    fact = {
        "id": f"f{len(facts) + 1}", "type": fact_type, "concept": concept,
        "value": values.pop("value", None), "unit": values.pop("unit", None),
        "status": values.pop("status", "asserted"), "negated": flags["negated"],
        "planned": flags["planned"], "historical": flags["historical"],
        "time": values.pop("time", None), "source_report": report["index"],
        "evidence_text": evidence,
    }
    fact.update(values)
    facts.append(fact)
    return fact


def extract_facts(case_reports):
    reports = normalize_reports(case_reports)
    facts, relations = [], []
    for report in reports:
        for text in _sentences(report["text"]):
            if re.search(r"母亲|父亲|家族|姐姐|妹妹|兄弟|子女", text):
                continue
            flags = _flags(text)
            age = re.search(r"(?<!\d)(\d{1,3})\s*岁", text)
            if age:
                _add(facts, "demographic", "age", report, text, flags,
                     value=int(age.group(1)), unit="year")
            if re.search(r"手术|切除术|术后", text):
                _add(facts, "procedure", "surgery", report, text, flags,
                     status="planned" if flags["planned"] else "performed", time=_date(text))
            symptom = re.search(r"腹泻|便秘", text)
            if symptom:
                status = "resolved" if flags["resolved"] else "active" if flags["current"] else "documented"
                _add(facts, "symptom", "diarrhea" if symptom.group() == "腹泻" else "constipation",
                     report, text, flags, status=status,
                     severity="severe" if re.search(r"严重|重度", text) else None)
            gs = re.search(r"(?:Gleason(?:评分)?|\bGS\b)\s*[:：=]?\s*(\d+)", text, re.I)
            if gs:
                _add(facts, "staging", "gleason_score", report, text, flags,
                     value=int(gs.group(1)), unit="score")
            psa = re.search(r"(?<![A-Za-z0-9])PSA(?![A-Za-z0-9])\s*[:：=]?\s*(\d+(?:\.\d+)?)\s*(ng/mL)?", text, re.I)
            if psa:
                _add(facts, "lab", "PSA", report, text, flags,
                     value=float(psa.group(1)), unit=psa.group(2) or "ng/mL")
            for concept, pattern in (("pT_high", r"\bpT(?:3a|3b|4)\b"),
                                     ("margin_r1", r"\bR1\b"), ("pN1", r"\bpN1\b")):
                if re.search(pattern, text, re.I):
                    _add(facts, "staging", concept, report, text, flags, value=True)
            if re.search(r"带状疱疹|herpes zoster|\bzoster\b", text, re.I):
                diagnosis = _add(facts, "diagnosis", "herpes_zoster", report, text, flags,
                                 status="confirmed" if re.search(r"确诊|诊断", text) else "documented")
                if re.search(r"头面部|头部|面部|颜面|眼周|三叉神经", text):
                    site = _add(facts, "organ_status", "head_face_site", report, text, flags,
                                value="head_face")
                    relations.append({"type": "LOCATED_AT", "source": diagnosis["id"],
                                      "target": site["id"], "evidence_text": text})
            if re.search(r"吸烟|抽烟|smoking", text, re.I):
                _add(facts, "behavior", "smoking", report, text, flags,
                     status="active" if flags["current"] else "documented")
            for concept, pattern, unit in (
                ("AST", r"\bAST\b\s*[:：=]?\s*(\d+(?:\.\d+)?)", "U/L"),
                ("ALT", r"\bALT\b\s*[:：=]?\s*(\d+(?:\.\d+)?)", "U/L"),
                ("BUN", r"\bBUN\b\s*[:：=]?\s*(\d+(?:\.\d+)?)", "mmol/L"),
                ("Cr", r"\b(?:Cr|Scr)\b\s*[:：=]?\s*(\d+(?:\.\d+)?)", "umol/L"),
                ("cTnI", r"\bcTnI\b\s*[:：=]?\s*(\d+(?:\.\d+)?)", "ug/L"),
                ("cTnT", r"\bcTnT\b\s*[:：=]?\s*(\d+(?:\.\d+)?)", "ug/L"),
            ):
                match = re.search(pattern, text, re.I)
                if match:
                    _add(facts, "lab", concept, report, text, flags,
                         value=float(match.group(1)), unit=unit)
            if re.search(r"吸烟|烟草|smok", text, re.I):
                _add(facts, "smoking", "smoking", report, text, flags,
                     status="current" if flags["current"] else "documented")
            if re.search(r"化疗|化学治疗", text):
                _add(facts, "treatment", "chemotherapy", report, text, flags,
                     status="planned" if flags["planned"] else "performed")
            if re.search(r"伊立替康|irinotecan", text, re.I):
                _add(facts, "treatment", "irinotecan", report, text, flags,
                     status="planned" if flags["planned"] else "performed",
                     first_use=bool(re.search(r"首次|初次|第一次", text)))
            if re.search(r"凝血功能异常|凝血异常", text):
                _add(facts, "organ_status", "coagulation_abnormal", report, text, flags,
                     status="active" if flags["current"] else "documented")
            if re.search(r"颅内高压|意识不清|昏迷", text):
                _add(facts, "symptom", "intracranial_or_consciousness", report, text, flags,
                     status="active" if flags["current"] else "documented")
            disease = re.search(r"甲肝|乙肝|乙型肝炎|HIV|艾滋病|结核|结缔组织病", text, re.I)
            if disease:
                status = "resolved" if flags["resolved"] else "active" if flags["current"] else "documented"
                _add(facts, "diagnosis", disease.group().lower(), report, text, flags, status=status)
            if re.search(r"有创机械通气|气管插管|机械通气", text):
                invasive = "无创" not in text and bool(re.search(r"有创|气管插管", text))
                vent = _add(facts, "procedure", "mechanical_ventilation", report, text, flags,
                            status="planned" if flags["planned"] else "performed",
                            invasive=invasive, time=_date(text))
                if re.search(r"术后|手术后|postoperative|post-op", text, re.I):
                    relations.append({"type": "POSTOPERATIVE_TO", "source": vent["id"],
                                      "target_concept": "surgery", "evidence_text": text})
    return {"reports": reports, "facts": facts, "relations": relations, "semantic_calls": 0}


def _facts(store, concept, usable=True):
    values = [fact for fact in store["facts"] if fact["concept"] == concept]
    return [fact for fact in values if not fact["negated"] and not fact["planned"]] if usable else values


def _result(cid, decision, reason, facts=(), payload=None, ready=False):
    return {"criterion": cid, "decision": decision, "reason_code": reason,
            "supporting_fact_ids": [fact["id"] for fact in facts], "payload": payload or {},
            "payload_ready": ready, "scorer_contract_ready": ready}


def _eval_555(store):
    surgeries = [fact for fact in _facts(store, "surgery") if fact["status"] == "performed"]
    if not surgeries:
        return _result("555", "UNKNOWN", "NO_COMPLETED_SURGERY")
    dates = [value for report in store["reports"] if (value := _report_date(report["timestamp"]))]
    dated = [fact for fact in surgeries if fact["time"]]
    if not dates or not dated:
        return _result("555", "UNKNOWN", "MISSING_GROUNDED_TIME", surgeries)
    surgery = max(dated, key=lambda fact: fact["time"])
    elapsed = (max(datetime.fromisoformat(value) for value in dates) -
               datetime.fromisoformat(surgery["time"])).days
    if elapsed < 0:
        return _result("555", "UNKNOWN", "SURGERY_AFTER_INDEX", [surgery])
    if elapsed <= 183:
        return _result("555", "MATCH", "SURGERY_WITHIN_6_MONTHS", [surgery],
                       {"time": surgery["time"]}, True)
    return _result("555", "NO_MATCH", "SURGERY_OVER_6_MONTHS", [surgery])


def _eval_565(store):
    symptoms = [fact for fact in store["facts"]
                if fact["concept"] in {"diarrhea", "constipation"} and not fact["negated"]]
    positives = [fact for fact in symptoms
                 if fact["status"] == "active" and fact.get("severity") == "severe"]
    if positives:
        fact = positives[-1]
        return _result("565", "MATCH", "CURRENT_SEVERE_SYMPTOM", [fact],
                       {"symptom": fact["concept"]}, True)
    if any(fact["status"] == "resolved" for fact in symptoms):
        return _result("565", "NO_MATCH", "SYMPTOM_RESOLVED", symptoms)
    return _result("565", "UNKNOWN",
                   "SEVERITY_OR_CURRENT_STATE_MISSING" if symptoms else "NO_SYMPTOM_FACT", symptoms)


def _eval_615(store):
    for fact in store["facts"]:
        if fact["negated"] or fact["planned"]:
            continue
        branch = None
        if fact["concept"] in {"pT_high", "margin_r1", "pN1"}:
            branch = fact["concept"]
        elif fact["concept"] == "gleason_score" and fact["value"] >= 8:
            branch = "GS"
        elif fact["concept"] == "PSA" and fact["value"] > 0.1:
            branch = "PSA"
        if branch:
            return _result("615", "MATCH", "ONCOLOGY_OR_BRANCH", [fact],
                           {"branch": branch, "value": fact["value"], "unit": fact["unit"]}, True)
    return _result("615", "UNKNOWN", "NO_SATISFYING_ONCOLOGY_BRANCH")


def _eval_675(store):
    zoster_facts = _facts(store, "herpes_zoster", usable=False)
    if zoster_facts and zoster_facts[-1]["negated"]:
        return _result("675", "NO_MATCH", "EXPLICIT_ZOSTER_NEGATION")
    ages = [fact for fact in _facts(store, "age") if fact["value"] is not None]
    diagnoses = [fact for fact in _facts(store, "herpes_zoster") if fact["status"] == "confirmed"]
    sites = _facts(store, "head_face_site")
    if not ages or not diagnoses or not sites:
        return _result("675", "UNKNOWN", "MISSING_AGE_DIAGNOSIS_OR_SITE",
                       ages + diagnoses + sites)
    age = max(ages, key=lambda fact: fact["value"])
    if age["value"] < 50:
        return _result("675", "NO_MATCH", "AGE_UNDER_50", [age])
    diagnosis, site = diagnoses[-1], sites[-1]
    relation = next((item for item in store["relations"]
                     if item["type"] == "LOCATED_AT" and item["source"] == diagnosis["id"]
                     and item["target"] == site["id"]), None)
    if not relation:
        return _result("675", "UNKNOWN", "SITE_RELATION_UNRESOLVED", [age, diagnosis, site])
    return _result("675", "MATCH", "AGE_CONFIRMED_ZOSTER_SITE", [age, diagnosis, site],
                   {"site": "head-face"}, True)


def _eval_735(store):
    diseases = [fact for fact in store["facts"]
                if fact["type"] == "diagnosis" and fact["concept"] != "herpes_zoster"]
    if any(fact["status"] == "resolved" for fact in diseases):
        return _result("735", "NO_MATCH", "TARGET_DISEASE_RESOLVED", diseases)
    active = [fact for fact in diseases if fact["status"] == "active" and not fact["negated"]]
    if active:
        fact = active[-1]
        return _result("735", "MATCH", "ACTIVE_TARGET_DISEASE", [fact],
                       {"disease": fact["concept"]}, True)
    return _result("735", "UNKNOWN", "ACTIVITY_STATE_MISSING" if diseases else "NO_TARGET_DISEASE",
                   diseases)


def _eval_745(store):
    surgeries = [fact for fact in store["facts"]
                 if fact["concept"] == "surgery" and fact["status"] == "performed"
                 and not fact["negated"] and not fact["planned"]]
    vents = [fact for fact in store["facts"]
             if fact["concept"] == "mechanical_ventilation" and fact["status"] == "performed"
             and not fact["negated"] and not fact["planned"]]
    invasive = [fact for fact in vents if fact.get("invasive")]
    if vents and not invasive:
        return _result("745", "NO_MATCH", "NONINVASIVE_ONLY", vents)
    if not surgeries or not invasive:
        return _result("745", "UNKNOWN", "MISSING_SURGERY_OR_INVASIVE_VENTILATION",
                       surgeries + invasive)
    vent = invasive[-1]
    relation = next((item for item in store["relations"]
                     if item["type"] == "POSTOPERATIVE_TO" and item["source"] == vent["id"]), None)
    if not relation:
        return _result("745", "UNKNOWN", "POSTOPERATIVE_RELATION_UNRESOLVED",
                       [surgeries[-1], vent])
    time = vent["time"] or surgeries[-1]["time"]
    return _result("745", "MATCH", "POSTOPERATIVE_INVASIVE_VENTILATION",
                   [surgeries[-1], vent], {"time": time} if time else {}, bool(time))


EVALUATORS = {"555": _eval_555, "565": _eval_565, "615": _eval_615,
              "675": _eval_675, "735": _eval_735, "745": _eval_745}


def evaluate_patient(case_reports, criteria=MVP_CRITERIA):
    store = extract_facts(case_reports)
    return store, {criterion: EVALUATORS[criterion](store) for criterion in criteria}


def _concept(system, code):
    return {"coding": [{"system": system, "code": code}]}


def _base(kind, profile, patient):
    return {"resourceType": kind, "meta": {"profile": [profile]},
            "subject": {"reference": f"Patient/{patient}"}}


def build_resources(patient, result):
    if result["decision"] != "MATCH" or not result["payload_ready"] or not result["scorer_contract_ready"]:
        return ()
    cid, payload = result["criterion"], result["payload"]
    contract = contract_for_criterion(cid)
    resource = _base(contract.resource_type, contract.profiles[0], patient)
    resource["status"] = "final" if contract.resource_type == "Observation" else "completed"
    if cid == "555":
        resource.update({"code": {"text": "surgery"}, "performedDateTime": payload["time"]})
    elif cid == "565":
        resource.update({"code": {"text": payload["symptom"]}, "extension": [{
            "url": BASE + "Extension/cnwqk565-observation-severity-ext",
            "valueCodeableConcept": _concept(BASE + "CodeSystem/cnwqk565-symptomseverity-cs", "severe")}]})
    elif cid == "615":
        index = {"pT_high": 0, "margin_r1": 1, "pN1": 2, "GS": 3, "PSA": 4}[payload["branch"]]
        resource["meta"]["profile"] = [contract.profiles[index]]
        resource["code"] = {"text": payload["branch"]}
        if payload["value"] is not None:
            resource["valueQuantity"] = {"value": payload["value"],
                                         "unit": payload["unit"] or "score"}
    elif cid == "675":
        resource.update({
            "clinicalStatus": _concept("http://terminology.hl7.org/CodeSystem/condition-clinical", "active"),
            "verificationStatus": _concept("http://terminology.hl7.org/CodeSystem/condition-ver-status", "confirmed"),
            "code": _concept(BASE + "CodeSystem/icd10", "B02.9"),
            "bodySite": [_concept(BASE + "CodeSystem/cnwqk675-head-facial-body-site-cs", "head-face")]})
    elif cid == "735":
        resource.update({
            "clinicalStatus": _concept("http://terminology.hl7.org/CodeSystem/condition-clinical", "active"),
            "code": {"text": payload["disease"]}})
    elif cid == "745":
        parent = _base("Procedure", "", patient)
        parent.pop("meta")
        parent.update({"id": "v6-surgery-1", "status": "completed", "code": {"text": "surgery"},
                       "performedDateTime": payload["time"]})
        resource.update({
            "code": _concept(BASE + "CodeSystem/cnwqk745-procedure-type-cs", "invasive_mechanical_ventilation"),
            "performedDateTime": payload["time"], "partOf": [{"reference": "Procedure/v6-surgery-1"}]})
        return (parent, resource)
    return (resource,)


def replay(patient, result):
    resources = build_resources(patient, result)
    outcome = replay_service(resources, contract_for_criterion(result["criterion"]).service,
                             "fixture://fhir", {patient: "case"})
    return {"resources": resources, "service_status": outcome.status}
