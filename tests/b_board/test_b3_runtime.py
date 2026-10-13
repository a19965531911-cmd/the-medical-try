import base64
from functools import lru_cache
import json
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[2]


@lru_cache(maxsize=1)
def candidate_bundle():
    from scripts.build_b3_candidate import build_b3
    path=ROOT/"experiment/b3-final/B3.json"
    return json.loads(path.read_text(encoding="utf8")) if path.exists() else build_b3()


def namespace(cid="495"):
    bundle=candidate_bundle()
    entry=next(e["resource"] for e in bundle["entry"][1:] if e["resource"]["content"][0]["title"]==cid)
    ns={}
    exec(base64.b64decode(entry["content"][0]["data"]),ns)
    return ns


def response(index=0,**extra):
    return {"facts":{"dlbcl":{"state":"PRESENT","evidence":"确诊弥漫性大细胞B淋巴瘤","report":index,**extra}}}


def test_rescue_rejects_extra_schema_fields():
    ns=namespace()
    data=[{"text":"病理报告。确诊弥漫性大细胞B淋巴瘤"}]
    result=ns["evaluate"]("495",data)
    assert not ns["semantic_rescue"]("495",data,result,lambda p:response(value=999),"test")["match"]


def test_rescue_cannot_join_separate_events():
    ns=namespace()
    data=[{"text":"病理报告。","event_id":"A"},{"text":"确诊弥漫性大细胞B淋巴瘤","event_id":"B"}]
    result=ns["evaluate"]("495",data)
    assert not ns["semantic_rescue"]("495",data,result,lambda p:response(1),"test")["match"]


def test_embedded_rescue_fact_provenance_is_one_event():
    ns=namespace()
    data=[{"text":"病理报告。","event_id":"A"},{"text":"病理报告。确诊弥漫性大细胞B淋巴瘤","event_id":"B"}]
    g=ns["FHIRResourceBundleGenerator"]("http://localhost:3456")
    g.transport=lambda p:response(1)
    assert g.parse_clinical_text_to_fhir_bundle("p1",data)["entry"]
    assert {f["report"] for f in g.last_result["facts"].values()}=={1}


@pytest.mark.parametrize("raw",[
    "YES",'{"facts":{},"facts":{}}','{"facts":{"bad":NaN}}',
    {"facts":{},"match":True},response(state="PRESENT",report=True),
    response(evidence="确诊 弥漫性大细胞B淋巴瘤"),response(state="INVALID"),
])
def test_embedded_bad_json_and_schema_fall_back(raw):
    ns=namespace()
    data=[{"text":"病理报告。确诊弥漫性大细胞B淋巴瘤"}]
    g=ns["FHIRResourceBundleGenerator"]("http://localhost:3456")
    g.transport=lambda p:raw
    assert not g.parse_clinical_text_to_fhir_bundle("p1",data)["entry"]


def test_embedded_timeout_transport_is_local_and_bounded(monkeypatch):
    ns=namespace()
    calls=[]
    def timeout(request,timeout):
        calls.append((request.full_url,timeout))
        raise TimeoutError("controlled local timeout")
    monkeypatch.setitem(ns,"urlopen",timeout)
    g=ns["FHIRResourceBundleGenerator"]("http://localhost:3456")
    assert g._transport("synthetic only")=="NO"
    assert calls==[("http://127.0.0.1:1213/v1/chat/completions",30)]
    assert g.transport_error.startswith("TimeoutError")


@pytest.mark.parametrize("cid",["2","3","85","205","225","255","295","465","475","495","525","585","625","695","715","765"])
def test_final_entrypoints_reach_b2_overlay(monkeypatch,cid):
    ns=namespace(cid)
    calls=[]
    evaluate=ns["evaluate_b2"]
    build=ns["build_b2_resources"]
    def spy_evaluate(*args,**kwargs):
        calls.append("evaluate_b2")
        return evaluate(*args,**kwargs)
    def spy_build(*args,**kwargs):
        calls.append("build_b2_resources")
        return build(*args,**kwargs)
    monkeypatch.setitem(ns,"evaluate_b2",spy_evaluate)
    monkeypatch.setitem(ns,"build_b2_resources",spy_build)
    g=ns["FHIRResourceBundleGenerator"]("http://localhost:3456")
    assert not g.parse_clinical_text_to_fhir_bundle("p1",[])["entry"]
    assert calls==["evaluate_b2","build_b2_resources"]
