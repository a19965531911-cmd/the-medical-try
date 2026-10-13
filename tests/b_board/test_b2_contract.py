import json
import pytest
from b_board.b2_runtime import evaluate_b2,build_b2_resources,labs_b2,smoking_b2


def r(text,day="2026-10-09",**kw):
    return dict(text=text,timestamp=day,**kw)


@pytest.mark.parametrize("text,strict,compatible",[
    ("TBIL 1.5 ULN ALT 3 ULN AST 3 ULN",True,True),
    ("TBIL 1.51 ULN ALT 3 ULN AST 3 ULN",False,False),
    ("TBIL 1 ULN ALT 3.01 ULN AST 3 ULN",False,False),
    ("TBIL 1 ULN ALT 3 ULN",False,True),
    ("TBIL 20 ALT 40 AST 40",False,False),
])
def test_625_strategies(text,strict,compatible):
    data=[r(text)]
    assert labs_b2(data,"CLINICAL_STRICT")["match"] is strict
    assert labs_b2(data,"OFFICIAL_COMPATIBLE")["match"] is compatible


def test_encounter_and_hospital_priority():
    data=[r("TBIL 1 ULN",encounter_id="one",hospital_id="A"),r("ALT 2 ULN AST 2 ULN","2026-10-08",encounter_id="one",hospital_id="A")]
    assert labs_b2(data)["match"]
    data[1]["hospital_id"]="B"
    assert not labs_b2(data)["match"]
    data=[{"text":"TBIL 1 ULN"},{"text":"ALT 2 ULN AST 2 ULN"}]
    assert not labs_b2(data)["match"]


def test_conflicts_order_independent_and_existential_panels():
    good=r("TBIL 1 ULN ALT 2 ULN AST 2 ULN","2026-10-08",encounter_id="good")
    bad=r("ALT 4 ULN","2026-10-09",encounter_id="bad")
    for data in ([good,bad],[bad,good]):
        assert labs_b2(data)["match"]
        assert not labs_b2(data,"OFFICIAL_COMPATIBLE")["match"]
    bad["encounter_id"]="good"
    assert not labs_b2([good,bad])["match"]


@pytest.mark.parametrize("text,service,complete",[
    ("目前每天吸烟20支",True,False),
    ("不能保证试验期间停止吸烟",True,False),
    ("目前每天吸烟20支，不能保证停止吸烟",True,True),
    ("目前每天吸烟5支，能保证停止吸烟",False,False),
    ("目前每天吸烟5支，不能保证停止吸烟",True,True),
    ("可能不能保证停止吸烟",False,False),
])
def test_295_or_and_strategies(text,service,complete):
    assert smoking_b2([r(text)])["match"] is service
    assert smoking_b2([r(text)],"PROFILE_COMPLETE")["match"] is complete
    result=smoking_b2([r(text)])
    resources=build_b2_resources("295","p1",[r(text)],result)
    if resources:
        components=resources[0]["component"]
        assert len(components)==(2 if "每天" in text and "保证" in text else 1)


@pytest.mark.parametrize("cid,left,right",[
    ("3","病理证实肝细胞癌","已行肝切除R0"),
    ("465","肾活检已完成","IgA肾病"),
    ("495","病理报告","DLBCL"),
    ("475","腰椎间盘突出导致疼痛","疼痛持续半年"),
])
def test_other_profile_event_binding(cid,left,right):
    split=[r(left,event_id="A"),r(right,event_id="B")]
    assert not evaluate_b2(cid,split)["match"]
    split[1]["event_id"]="A"
    assert evaluate_b2(cid,split)["match"]


def test_xhtml_injection_escaped():
    data=[r("咳嗽<script>alert(1)</script>")]
    res=build_b2_resources("2","p1",data,evaluate_b2("2",data))
    assert "<script>" not in res[0]["text"]["div"]
    assert "&lt;script&gt;" in res[0]["text"]["div"]
    json.dumps(res,allow_nan=False)


def test_85_category_and_truthful_r4_status():
    data=[r("拟择期行胸腔镜肺叶切除术")]
    result=evaluate_b2("85",data)
    output=build_b2_resources("85","p1",data,result)
    assert output[0]["category"]["coding"][0]["code"]=="surgery"
    assert output[0]["status"]=="preparation"
    assert "performedDateTime" not in output[0]


def test_smoking_distributed_context_retains_quantity_provenance():
    data=[r("目前吸烟。"),r("每日20支")]
    result=smoking_b2(data)
    assert result["match"]
    fact=result["facts"]["smoking_eligible"]
    assert fact["report"]==1
    assert fact["value"]["cigarettes_per_day"]==20
    data[1]["hospital_id"]="other"
    assert not smoking_b2(data)["match"]
    data[1].pop("hospital_id")
    data[1]["timestamp"]="2026-10-08"
    assert not smoking_b2(data)["match"]


def test_smoking_explicit_evaluation_anchor_and_90_day_boundary():
    assert not smoking_b2([r("目前每天吸烟20支","2026-10-09",evaluation_timestamp="2026-06-01")])["match"]
    assert not smoking_b2([r("目前每天吸烟20支","2026-10-09",evaluation_timestamp="2026-06-01"),r("其他记录")])["match"]
    assert smoking_b2([r("目前每天吸烟20支","2026-07-11",evaluation_timestamp="2026-10-09")])["match"]
    assert not smoking_b2([r("目前每天吸烟20支","2026-07-10",evaluation_timestamp="2026-10-09")])["match"]


def test_rescue_unknown_fields_do_not_create_facts():
    from b_board.runtime import evaluate,semantic_rescue
    data=[r("病理报告。确诊弥漫性大细胞B淋巴瘤")]
    result=evaluate("495",data)
    response={"facts":{"extra":{"state":"PRESENT","evidence":data[0]["text"],"report":0}},"match":True}
    rescued=semantic_rescue("495",data,result,lambda p:response,"病理DLBCL")
    assert not rescued["match"]
    assert set(rescued["facts"])==set(result["facts"])


@pytest.mark.parametrize("state",["NEGATED","ABSENT","PLANNED","UNCERTAIN"])
def test_rescue_deterministic_veto_never_calls_model(state):
    from b_board.runtime import evaluate,semantic_rescue
    data=[r("病理报告。确诊弥漫性大细胞B淋巴瘤")]
    result=evaluate("495",data)
    result["facts"]["dlbcl"]["state"]=state
    def forbidden(prompt):
        pytest.fail("deterministic veto must bypass model")
    assert semantic_rescue("495",data,result,forbidden,"病理DLBCL")==result


@pytest.mark.parametrize("cid,text",[("475","腰椎间盘突出导致疼痛持续半年"),("525","术前诊断下段食管癌"),("715","病变未侵及下腔静脉、门静脉")])
def test_fsh_profile_resolved_by_explicit_canonical_url(cid,text):
    from scripts.b2_experiments import fsh_checks
    from scripts.build_b_submission import load_rows
    data=[r(text)]
    output=build_b2_resources(cid,"p1",data,evaluate_b2(cid,data))
    assert output
    row=next(row for row in load_rows() if str(row["profile_id"])==cid)
    errors=fsh_checks(row,{"entry":[{"resource":resource} for resource in output]})
    assert not any("No matching FSH profile" in error for error in errors)
