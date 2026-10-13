"""Experiment L: 675-only deterministic precision guard over Experiment E."""

EXPL_SOURCE = r'''
_ExperimentEGenerator_L = FHIRResourceBundleGenerator

def _expl675_clauses(text):
    return [x.strip() for x in re.split(r"[。！？!?；;，,]", text) if x.strip()]

def _expl675_facts(reports):
    text = "。".join(str(r.get("text", "")) for r in reports)
    clauses = _expl675_clauses(text)
    age = None
    for clause in clauses:
        if re.search(r"母亲|父亲|家族|姐姐|妹妹|兄弟|子女", clause):
            continue
        match = re.search(r"(?:年龄|age)\s*[:：]?\s*(\d{2,3})|(?<!\d)(\d{2,3})\s*(?:岁|years? old|year-old)", clause, re.I)
        if match:
            value = int(match.group(1) or match.group(2))
            age = value if age is None else max(age, value)
    zoster_pattern = r"带状疱疹|herpes zoster|\bzoster\b|\bHZ\b"
    site_pattern = r"头面部|头部|面部|额部|眼周|三叉神经区|head|face"
    zoster_clauses = [clause for clause in clauses if re.search(zoster_pattern, clause, re.I)]
    zoster = bool(zoster_clauses)
    negated = bool(re.search(r"(?:否认|排除|无|未见)[^。；，,]{0,10}(?:带状疱疹|herpes zoster|\bzoster\b)", text, re.I))
    site = bool(re.search(site_pattern, text, re.I))
    bound_site = any(re.search(site_pattern, clause, re.I) and not re.search(r"(?:无|未见|否认|排除)[^。；，,]{0,6}(?:皮疹|症状|带状疱疹)", clause, re.I) for clause in zoster_clauses)
    if not bound_site:
        bound_site = any(
            re.search(site_pattern, clause, re.I)
            and re.search(r"累及|位于|分布|病变|部位|involv|located|distribution", clause, re.I)
            and not re.search(r"(?:无|未见|否认|排除)[^。；，,]{0,8}(?:皮疹|症状)", clause, re.I)
            for clause in clauses
        )
    return age, zoster, site, bound_site, negated

class FHIRResourceBundleGenerator(_ExperimentEGenerator_L):
    def parse_clinical_text_to_fhir_bundle(self, patient_id, case_reports, ai_algorithm_type="nlp"):
        cid = str(TITLE)
        if cid != "675":
            return super().parse_clinical_text_to_fhir_bundle(patient_id, case_reports, ai_algorithm_type)
        age, zoster, site, bound_site, negated = _expl675_facts(case_reports)
        complete = age is not None and age >= 50 and zoster and site and bound_site and not negated
        if not complete:
            print("V5S8L_METRICS|criterion=675|age_found=" + str(int(age is not None and age >= 50)) +
                  "|zoster_found=" + str(int(zoster and not negated)) + "|site_found=" + str(int(site and bound_site)) +
                  "|final_decision=NO_MATCH|resources=0|reason=MISSING_REQUIRED_675_FACT")
            return {"resourceType": "Bundle", "type": "transaction", "entry": []}
        bundle = super().parse_clinical_text_to_fhir_bundle(patient_id, case_reports, ai_algorithm_type)
        print("V5S8L_METRICS|criterion=675|age_found=1|zoster_found=1|site_found=1|final_decision=MATCH|resources=" + str(len(bundle.get("entry", []))) + "|reason=RETAINED_E_MATCH")
        return bundle
'''
