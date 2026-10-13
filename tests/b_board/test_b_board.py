"""Adversarial semantics, not real patient labels or a score estimate."""
import copy
import pytest

from b_board.runtime import evaluate

# strong, paraphrased, fragmented; negative, negated, near miss, uncertain, temporal
CASES = {
    "2": (["患者咳嗽", "活动后喘憋", "无发热。\n气促明显"], ["头痛", "无咳嗽、胸闷、气短", "胸痛", "可能气短", "既往咳嗽已完全消失"]),
    "3": (["病理证实肝细胞癌，已行肝癌根治性切除R0", "病理HCC。肝切除术后，切缘阴性", "病理提示肝细胞癌。\n患者此前接受肝癌根治切除，切缘阴性（R0）"], ["肝细胞癌", "病理未证实肝细胞癌，已行肝切除R0", "病理肝细胞癌，肝切除术后R1", "病理疑似HCC，已行根治性切除", "肝细胞癌，拟行根治性肝切除术"]),
    "85": (["拟择期行胸腔镜肺叶切除术", "计划VATS肺段切除术", "拟择期手术。\n胸腔镜入路。\n肺叶切除术"], ["急诊胸腔镜肺叶切除术", "不行胸腔镜肺切除术", "择期开胸肺叶切除术", "考虑胸腔镜肺切除术", "既往行开胸肺叶切除术"]),
    "205": (["拟择期全麻下胸部手术", "计划全身麻醉下肺叶切除术", "择期肺切除手术。\n麻醉方式为全麻"], ["急诊全麻胸部手术", "不行全麻胸部手术", "择期局麻胸部手术", "考虑全麻胸部手术", "全麻阑尾切除术后"]),
    "225": (["已接受放疗", "曾接受radiotherapy", "肿瘤治疗。\n放射治疗已完成"], ["仅化疗", "未接受放疗", "放射检查", "考虑放疗", "拟行放疗"]),
    "255": (["确诊2型糖尿病", "T2DM", "出院诊断。\nII型糖尿病"], ["1型糖尿病", "否认2型糖尿病", "糖耐量异常", "疑似T2DM", "拟排查2型糖尿病"]),
    "295": (["目前每天吸烟20支", "现吸烟1包/日", "目前吸烟。\n每日20支"], ["从不吸烟", "否认吸烟，每日20支", "目前每日5支", "可能每日20支吸烟", "曾每天20支，戒烟5年"]),
    "465": (["肾活检病理提示IgA肾病", "肾穿刺病理证实狼疮性肾炎", "肾活检已完成。\n病理诊断原发性膜性肾病"], ["糖尿病肾病", "肾活检未提示IgA肾病", "确诊IgA肾病", "肾活检疑似狼疮性肾炎", "拟肾活检，诊断IgA肾病"]),
    "475": (["腰椎间盘突出导致腰痛3个月", "脊柱病变所致疼痛半年", "腰椎间盘突出导致疼痛。\n疼痛持续3个月"], ["膝痛半年", "无腰痛，腰椎间盘突出3个月", "腰痛3个月", "疑似脊柱源性疼痛半年", "腰椎间盘突出导致疼痛2个月"]),
    "495": (["病理诊断弥漫大B细胞淋巴瘤", "活检证实DLBCL", "病理报告。\n结论DLBCL"], ["NHL", "病理排除DLBCL", "B细胞淋巴瘤NOS", "病理疑似DLBCL", "拟活检排查DLBCL"]),
    "525": (["术前诊断胸中段食管癌", "拟手术，诊断胸下段食管癌", "术前诊断食管癌。\n肿瘤位于中下段"], ["胃癌", "术前排除中下段食管癌", "术前诊断上段食管癌", "术前疑似中段食管癌", "术后病理中段食管癌"]),
    "585": (["反复腰痛3个月", "下背痛半年余", "腰痛。\n疼痛持续1年"], ["头痛半年", "否认腰痛3个月", "腰痛2个月", "可能腰痛半年", "腰痛已消失，曾持续半年"]),
    "625": (["TBIL 1.5 ULN ALT 3 ULN AST 2.9 ULN", "总胆红素1倍正常上限，ALT 2倍正常上限，AST 3倍正常上限", "TBIL 30上限20。\nALT 120上限40。\nAST 116上限40"], ["无检验", "未查TBIL ALT AST", "TBIL 1.51 ULN ALT 3 ULN AST 2 ULN", "拟查肝功能", "ALT 2 ULN AST 2 ULN"]),
    "695": (["证实有远处转移", "肿瘤分期M1", "影像确诊。\n肺癌伴骨转移"], ["M0", "无远处转移", "区域淋巴结转移", "不排除远处转移", "拟排查骨转移"]),
    "715": (["增强CT示下腔静脉及门静脉均未见肿瘤侵犯", "未侵及下腔静脉、门静脉", "下腔静脉未受侵。\n门静脉未受侵"], ["门静脉可见癌栓，下腔静脉未受侵", "下腔静脉受侵，门静脉未侵", "未见血管侵犯", "考虑门静脉侵犯，下腔静脉未侵", "既往未侵及门静脉及下腔静脉，目前门静脉受侵"]),
    "765": (["有窒息缺氧史", "曾发生窒息", "出生记录。\n新生儿缺氧病史"], ["SpO2 80%", "无窒息缺氧史", "目前低氧血症", "可能有窒息史", "拟评估缺氧风险"]),
}


def reports(text):
    return [{"text": part, "timestamp": "2026-10-09T12:00:00+08:00"} for part in text.split("\n")]


@pytest.mark.parametrize("cid,text,expected", [(c,t,True) for c,(pos,neg) in CASES.items() for t in pos] + [(c,t,False) for c,(pos,neg) in CASES.items() for t in neg])
def test_adversarial(cid, text, expected):
    assert evaluate(cid, reports(text))["match"] is expected


@pytest.mark.parametrize("value,expected", [(3,True),(3.01,False)])
def test_alt_ast_boundary(value, expected):
    for lab in ("ALT", "AST"):
        text = f"TBIL 1.5 ULN ALT 3 ULN AST 3 ULN".replace(f"{lab} 3", f"{lab} {value}")
        assert evaluate("625", reports(text))["match"] is expected


def test_b_submission_routes_tbd_and_validates():
    from scripts.build_b_submission import load_rows, build_bundle, submission_sanity_check
    rows = load_rows()
    assert rows[0]["id"] == rows[1]["id"] == "tbd"
    assert rows[0]["index"] is rows[1]["index"] is None
    bundle = build_bundle(rows)
    submission_sanity_check(bundle, rows)
    libraries = [e["resource"] for e in bundle["entry"][1:]]
    assert len({r["id"] for r in libraries}) == 16
    assert [r["content"][0]["title"] for r in libraries][:2] == ["2", "3"]
    bad = copy.deepcopy(bundle)
    bad["entry"][2]["resource"]["id"] = bad["entry"][1]["resource"]["id"]
    with pytest.raises(ValueError):
        submission_sanity_check(bad, rows)
    from scripts.build_b_submission import publication_gate,parse_submission
    with pytest.raises(ValueError,match="Publication blocked"):
        publication_gate(bundle,rows)
    for raw in ('{"id":1,"id":2}', '{"value":NaN}', '{"value":Infinity}'):
        with pytest.raises(ValueError):
            parse_submission(raw)


@pytest.mark.parametrize("cid,text,expected", [
    ("3","确诊肝细胞癌，病理未明确。已行肝癌根治切除R0",False),
    ("3","病理证实肝细胞癌，拟行肝切除，R0切缘为目标",False),
    ("3","病理证实肝细胞癌。已行肝切除，切缘阳性R1",False),
    ("3","病理证实胃癌。临床诊断肝细胞癌，肝切除术后R0",False),
    ("495","病理诊断肺腺癌。临床诊断DLBCL",False),
    ("2","母亲咳嗽，患者无症状",False),
    ("255","母亲2型糖尿病，患者仅高血糖",False),
    ("475","腰痛半年。腰椎间盘突出。头痛导致失眠",False),
    ("585","腰痛2个月。高血压5年",False),
    ("585","反复腰痛三个月",True),
    ("585","腰痛数年",True),
    ("585","腰痛自去年起持续至今",True),
    ("715","未侵及下腔静脉，门静脉受侵",False),
    ("715","下腔静脉及门静脉均未受侵",True),
    ("295","目前每日5.01支吸烟",True),
    ("295","吸烟20支/日，持续30年",True),
    ("295","有吸烟史，曾每日20支",False),
    ("295","不能保证试验期间停止吸烟",True),
    ("625","TBIL 30 umol/L参考范围0-20 ALT 120 U/L参考范围0-40 AST 120 U/L参考范围0-40",True),
])
def test_additional_attacks(cid,text,expected):
    assert evaluate(cid,reports(text))["match"] is expected


def test_labs_different_encounters_do_not_complete_each_other():
    data = [{"text":"TBIL 1 ULN", "timestamp":"2026-09-01"}, {"text":"ALT 2 ULN AST 2 ULN", "timestamp":"2026-10-01"}]
    assert not evaluate("625",data)["match"]
    data[0]["text"] += " ALT 2 ULN AST 2 ULN"
    data[1]["text"] = "TBIL 5 ULN ALT 5 ULN AST 5 ULN"
    assert evaluate("625",data)["match"]


def test_procedure_atoms_must_share_event_or_explicit_encounter():
    from b_board.b2_runtime import evaluate_b2 as evaluate
    split = [
        {"text":"择期胸腔镜肺叶切除术", "encounter_id":"s1"},
        {"text":"急诊开胸肺切除术", "encounter_id":"s2"},
    ]
    assert evaluate("85",split)["match"] is True
    split = [
        {"text":"择期手术", "encounter_id":"s1"},
        {"text":"胸腔镜检查，肺叶切除术", "encounter_id":"s2"},
    ]
    assert evaluate("85",split)["match"] is False
    split = [
        {"text":"择期全麻下胸部手术", "encounter_id":"s1"},
        {"text":"急诊全麻胸部手术", "encounter_id":"s2"},
    ]
    assert evaluate("205",split)["match"] is True
    split = [
        {"text":"择期手术", "encounter_id":"s1"},
        {"text":"全麻下胸部手术", "encounter_id":"s2"},
    ]
    assert evaluate("205",split)["match"] is False


def test_smoking_requires_recent_window_when_dates_are_available():
    from b_board.b2_runtime import evaluate_b2 as evaluate
    reports = [
        {"text":"每天吸烟20支", "timestamp":"2025-01-01"},
        {"text":"本次就诊", "timestamp":"2025-10-01"},
    ]
    assert evaluate("295",reports)["match"] is False
    reports[0]["timestamp"] = "2025-08-01"
    assert evaluate("295",reports)["match"] is True


def test_semantic_schema_and_grounding():
    from b_board.runtime import semantic_rescue
    data = reports("病理报告。确诊弥漫性大细胞B淋巴瘤")
    result = evaluate("495",data)
    assert not result["match"]
    response = {"facts":{"dlbcl":{"state":"PRESENT","evidence":"确诊弥漫性大细胞B淋巴瘤","report":0}}}
    assert semantic_rescue("495",data,result,lambda p:response,"病理DLBCL")["match"]
    response["facts"]["dlbcl"]["evidence"] = "不存在于原文的证据"
    assert not semantic_rescue("495",data,result,lambda p:response,"病理DLBCL")["match"]
    for raw in ("YES",{}, {"facts":None}):
        assert not semantic_rescue("495",data,result,lambda p:raw,"病理DLBCL")["match"]


def test_smoking_timezone_serialization_is_accepted_by_official_service():
    from scripts.audit_b_board import replay_service
    from scripts.build_b_submission import load_rows
    from b_board.runtime import build_b_resources
    row = next(r for r in load_rows() if r["profile_id"]==295)
    data = reports("目前每天吸烟20支")
    resources = build_b_resources("295","p1",data,evaluate("295",data))
    assert replay_service(row,{"entry":[{"resource":r} for r in resources]})["hit"]


@pytest.fixture(scope="module")
def embedded_generators():
    import base64
    from scripts.build_b_submission import load_rows,build_bundle
    bundle = build_bundle(load_rows())
    classes = {}
    for entry in bundle["entry"][1:]:
        r = entry["resource"]
        namespace = {}
        exec(compile(base64.b64decode(r["content"][0]["data"]),r["name"],"exec"),namespace)
        classes[r["content"][0]["title"]] = namespace["FHIRResourceBundleGenerator"]
    return classes


@pytest.mark.parametrize("cid",list(CASES))
def test_embedded_entrypoint_and_official_service(cid,embedded_generators):
    from scripts.audit_b_board import fixture_reports,replay_service
    from scripts.build_b_submission import load_rows
    row = next(r for r in load_rows() if str(r["profile_id"])==cid)
    gen = embedded_generators[cid]("http://localhost:3456/api/fhir/baseDstu4")
    gen.transport = lambda prompt:"NO"
    for expected,texts in zip((True,False),CASES[cid]):
        for text in texts:
            data = fixture_reports(cid,text)
            bundle = gen.parse_clinical_text_to_fhir_bundle("p1",data)
            assert gen.last_result["match"] is expected
            assert bool(bundle["entry"]) is expected
            assert replay_service(row,bundle)["hit"] is expected
            for entry in bundle["entry"]:
                r = entry["resource"]
                assert entry["request"] == {"method":"POST","url":r["resourceType"]}
                assert r["subject"]["reference"] == "Patient/p1"
    assert not gen.parse_clinical_text_to_fhir_bundle("p2",[])["entry"]
