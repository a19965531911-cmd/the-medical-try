import base64
from functools import lru_cache
import pytest

from scripts.review_b3_package import repaired_bundle


@lru_cache(maxsize=1)
def bundle():
    return repaired_bundle()


@pytest.mark.parametrize("cid",["2","3","85","205","225","255","295","465","475","495","525","585","625","695","715","765"])
@pytest.mark.parametrize("text",[None,123])
def test_invalid_text_is_empty_evidence(cid,text):
    entry=next(e["resource"] for e in bundle()["entry"][1:] if e["resource"]["content"][0]["title"]==cid)
    ns={};exec(base64.b64decode(entry["content"][0]["data"]),ns)
    generator=ns["FHIRResourceBundleGenerator"]("http://localhost:3456")
    generator.transport=lambda prompt:"NO"
    reports=[{"text":text}]
    output=generator.parse_clinical_text_to_fhir_bundle("p1",reports)
    assert output=={"resourceType":"Bundle","type":"transaction","entry":[]}
    assert reports==[{"text":text}]
