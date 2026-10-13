"""Append to a frozen B3 Library; preserve indexes and never invent clinical text."""
_B3_ENTRY=FHIRResourceBundleGenerator.parse_clinical_text_to_fhir_bundle


def _b3_review_entry(self,patient_id,case_reports,ai_algorithm_type="nlp"):
    if not isinstance(case_reports,(list,tuple)):
        raise ValueError("case_reports must be a list")
    reports=[]
    for original in case_reports:
        if isinstance(original,dict):
            report=dict(original)
            if not isinstance(report.get("text",""),str):
                report["text"]=""
        elif original is None:
            report={"text":""}
        else:
            report={"text":str(original)}
        reports.append(report)
    return _B3_ENTRY(self,patient_id,reports,ai_algorithm_type)


FHIRResourceBundleGenerator.parse_clinical_text_to_fhir_bundle=_b3_review_entry
