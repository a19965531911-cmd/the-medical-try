"""Self-contained safety rules shared by V3 development and generated code."""
import json, re

PROMPT_VERSION = "v3.0"
def validate_llm_result(obj, source):
    if not isinstance(obj, dict) or not isinstance(obj.get("match"), bool): return None
    required={"confidence","subject","negated","planned","uncertain","evidence","facts","reason"}
    if not required.issubset(obj) or obj["subject"]!="patient" or obj["negated"] or obj["planned"] or obj["uncertain"]: return None
    if not isinstance(obj["evidence"], list) or not obj["evidence"] or not all(str(e) in source for e in obj["evidence"]): return None
    return obj

def safe_rescue(result, source):
    return bool(validate_llm_result(result, source) and result["match"])
