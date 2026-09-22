import base64,json,io
from contextlib import redirect_stdout
from pathlib import Path
from v5s.runtime_template import retrieve_evidence,rule_decide,extract_payload,build_resources,parse_decision

ROOT=Path(__file__).parents[2]
CRITERIA=("485","615","265","635","675","735","745","755","855","835","875","805","565","555","185","165")
POS={"165":"已在外院完成两周期化疗","185":"首次接受伊立替康化疗","265":"cTnI 0.08 ug/L","485":"盆腔器官脱垂 POP-Q III期","555":"3个月前完成胆囊切除术","565":"目前严重腹泻","615":"术后病理 pN1","635":"AST 30上限40 ALT 30上限40 BUN 8上限9 Cr 180上限100","675":"患者70岁确诊头面部带状疱疹","735":"活动性乙型肝炎","745":"术后行有创机械通气","755":"机械通气持续30小时","805":"目前每日吸烟","835":"目前凝血功能异常","855":"Scr 120 umol/L，BUN 7 mmol/L，ALT 30 U/L上限40，AST 25 U/L上限40","875":"既往发生颅内高压"}
NEG={"165":"仅计划转外院化疗","185":"拟首次使用伊立替康，尚未给药","265":"cTnI 0.03 ug/L","485":"POP-Q II期","555":"8个月前完成胆囊切除术","565":"严重腹泻已缓解","615":"pN0且GS 7，PSA 0.05 ng/mL","635":"AST 30上限40 ALT 30上限40 BUN 8上限9 Cr 250上限100","675":"躯干部带状疱疹，非头面部","735":"乙肝病情稳定","745":"术后仅无创通气","755":"机械通气持续12小时","805":"从不吸烟","835":"凝血功能正常","855":"Scr 120 umol/L，BUN 7 mmol/L，ALT 50 U/L上限40，AST 25 U/L上限40","875":"否认颅内高压且意识清楚"}

def decoded_libraries():
    b=json.loads((ROOT/"submission/a_test_message_bundle_v5s_candidate.json").read_text(encoding="utf8"))
    out=[]
    for e in b["entry"]:
        r=e["resource"]
        if r.get("resourceType")=="Library":
            out.append((str(r["content"][0]["title"]),r,base64.b64decode(r["content"][0]["data"]).decode()))
    return out

def generator_for(cid):
    source=next(s for c,_,s in decoded_libraries() if c==cid)
    ns={};exec(compile(source,cid,"exec"),ns)
    gen=ns["FHIRResourceBundleGenerator"]("http://localhost:3456")
    return gen

def run_embedded(cid,text,transport="YES"):
    gen=generator_for(cid)
    calls=[]
    gen.transport=lambda prompt:(calls.append(prompt) or transport)
    buf=io.StringIO()
    with redirect_stdout(buf):
        bundle=gen.parse_clinical_text_to_fhir_bundle("patient-1",[{"text":text,"timestamp":"2026-01-01"}])
    return bundle,calls,buf.getvalue()

def test_retrieval_finds_late_anchor_and_adjacent_sentence():
    reports=[{"text":"无关。"+"普通信息。"*250+"患者年龄70岁，头面部带状疱疹。后续说明。"}]
    w=retrieve_evidence([{"index":0,"text":reports[0]["text"]}],{"groups":[["带状疱疹"]],"aliases":["带状疱疹"]})
    assert any("带状疱疹" in x["text"] for x in w)
def test_retrieval_covers_beginning_deep_offset_end_and_cross_report():
    spec={"groups":[["年龄"],["带状疱疹"],["头面部"]],"aliases":["年龄","带状疱疹","头面部"]}
    cases=["年龄70岁。"+"无关。"*20,"无关。"*800+"年龄70岁。","无关。"*1200+"头面部带状疱疹"]
    for text in cases:
        w=retrieve_evidence([{"index":0,"text":text}],spec)
        assert any(any(a in x["text"] for a in spec["aliases"]) for x in w)
    w=retrieve_evidence([{"index":0,"text":"患者年龄70岁"},{"index":1,"text":"确诊头面部带状疱疹"}],spec)
    assert {x["report"] for x in w}=={0,1}
    w=retrieve_evidence([{"index":0,"text":"患者年龄70岁。"+"无关。"*20+"确诊带状疱疹。"+"无关。"*20+"病灶位于头面部"}],spec)
    assert all(any(anchor in " ".join(x["text"] for x in w) for anchor in group) for group in spec["groups"])
def test_retrieval_uses_second_report():
    w=retrieve_evidence([{"index":0,"text":"无关"},{"index":1,"text":"首次伊立替康实际给药"}],{"groups":[["伊立替康"]],"aliases":["伊立替康"]})
    assert any(x["report"]==1 for x in w)
def test_rule_first_branches():
    assert rule_decide("615",[{"text":"PSA 0.2 ng/mL"}])[0] is True
    assert rule_decide("755",[{"text":"机械通气持续2天"}])[0] is True
    assert rule_decide("805",[{"text":"戒烟1年"}])[0] is True
    assert rule_decide("805",[{"text":"戒烟3年"}])[0] is False
    assert rule_decide("755",[{"text":"持续2天"}])[0] is None
    assert rule_decide("755",[{"text":"机械通气持续2天"}])[0] is True
    assert rule_decide("755",[{"text":"机械通气持续3天但仅12小时"}])[0] is False
    assert rule_decide("805",[{"text":"current smoker"}])[0] is True
    assert rule_decide("805",[{"text":"quit 1.5 years ago"}])[0] is True

def test_615_all_five_authorized_or_branches():
    for text in ("病理pT3a","切缘R1","pN1","Gleason评分8分","PSA 0.2 ng/mL"):
        assert rule_decide("615",[{"text":text}])[0] is True
    assert rule_decide("615",[{"text":"pT2 pN0 Gleason评分7分 PSA 0.05 ng/mL"}])[0] is False

def test_265_binds_analyte_before_applying_threshold():
    assert rule_decide("265",[{"text":"肌钙蛋白T 0.03 ug/L"}])[0] is True
    assert rule_decide("265",[{"text":"肌钙蛋白T 0.02 ug/L"}])[0] is False
    assert rule_decide("265",[{"text":"肌钙蛋白 0.20 ug/L"}])[0] is None
def test_all_decoded_libraries_compile_exec_and_smoke():
    b=json.loads((ROOT/"submission/a_test_message_bundle_v5s_candidate.json").read_text(encoding="utf8")); count=0
    for e in b["entry"]:
        r=e["resource"]
        if r.get("resourceType")!="Library":continue
        s=base64.b64decode(r["content"][0]["data"]).decode(); compile(s,r["name"],"exec"); ns={}; exec(compile(s,r["name"],"exec"),ns)
        g=ns["FHIRResourceBundleGenerator"]("http://localhost:3456"); g.transport=lambda prompt:"YES"
        assert g.parse_clinical_text_to_fhir_bundle("p1",[{"text":"明确符合条件","timestamp":"2026-01-01"}])["resourceType"]=="Bundle"
        assert g.parse_clinical_text_to_fhir_bundle("p1",[{"text":"无相关信息"}])["resourceType"]=="Bundle"; count+=1
    assert count==16

def test_615_profile_is_a_list():
    v=extract_payload("615",[],"MATCH",[{"text":"术后病理 pN1"}])
    resources=build_resources("615","p1",v)
    assert resources
    assert isinstance(resources[0]["meta"]["profile"],list)

def test_635_extracts_real_lab_values_and_ulns():
    text="AST 30上限40 ALT 30上限40 BUN 8上限9 Cr 80上限100"
    v=extract_payload("635",[],"MATCH",[{"text":text}])
    assert v["labs"]=={"AST":(30.0,40.0),"ALT":(30.0,40.0),"BUN":(8.0,9.0),"Cr":(80.0,100.0)}

def test_635_and_855_require_complete_audited_local_lab_bindings():
    assert rule_decide("635",[{"text":"AST 30上限40 ALT 50上限40 BUN 12上限9 Cr 180上限100"}])[0] is True
    assert rule_decide("635",[{"text":"AST 30上限40 ALT 50上限40 BUN 12上限9 Cr 250上限100"}])[0] is False
    assert rule_decide("635",[{"text":"AST 30上限40 ALT 50上限40"}])[0] is None
    assert rule_decide("855",[{"text":"Scr 120 umol/L，BUN 7 mmol/L，ALT 30 U/L上限40，AST 25 U/L上限40"}])[0] is True
    assert rule_decide("855",[{"text":"Scr 190 umol/L，BUN 7 mmol/L，ALT 30 U/L上限40，AST 25 U/L上限40"}])[0] is False
    assert rule_decide("855",[{"text":"Scr 120 umol/L"}])[0] is None

def test_635_missing_lab_values_does_not_fabricate_resources():
    v=extract_payload("635",[],"MATCH",[{"text":"AST 30上限40 ALT 30上限40"}])
    assert "labs" not in v
    assert build_resources("635","p1",v)==[]

def test_date_dependent_resources_do_not_fabricate_dates():
    for cid,text in (("185","首次接受伊立替康化疗"),("555","3个月前完成胆囊切除术"),("875","既往发生颅内高压")):
        v=extract_payload(cid,[],"MATCH",[{"text":text}])
        resources=build_resources(cid,"p1",v)
        assert all("2026-01-01" not in json.dumps(x,ensure_ascii=False) for x in resources)

def test_report_timestamp_is_not_a_clinical_event_date_and_popq_stage_is_grounded():
    for cid,text in (("185","首次接受伊立替康化疗"),("555","3个月前完成胆囊切除术"),("875","既往发生颅内高压")):
        v=extract_payload(cid,[{"text":text,"timestamp":"2026-01-01"}],"MATCH",[{"text":text}])
        assert v.get("time") is None
    v=extract_payload("485",[],"MATCH",[{"text":"盆腔器官脱垂 POP-Q IV期"}])
    assert v["stage"]=="IV"

def test_required_fhir_dates_use_only_explicit_text_or_proven_marker():
    marker="1970-01-01T00:00:00Z"
    for cid,text in (("185","首次接受伊立替康化疗"),("265","cTnI 0.08 ug/L"),("555","3个月前完成胆囊切除术"),("745","术后行有创机械通气"),("855","Scr 120 umol/L，BUN 7 mmol/L，ALT 30 U/L上限40，AST 25 U/L上限40"),("875","既往发生颅内高压")):
        resources=build_resources(cid,"p1",extract_payload(cid,[{"text":text,"timestamp":"2026-01-01"}],"MATCH",[{"text":text}]))
        payload=json.dumps(resources,ensure_ascii=False)
        assert "2026-01-01" not in payload
        assert marker in payload

def test_candidate_shell_and_decoded_runtime_hard_gates():
    b=json.loads((ROOT/"submission/a_test_message_bundle_v5s_candidate.json").read_text(encoding="utf8"))
    libs=decoded_libraries()
    assert sum(e["resource"].get("resourceType")=="MessageHeader" for e in b["entry"])==1
    assert [c for c,_,_ in libs]==list(CRITERIA)
    assert len(libs)==16
    for cid,_,source in libs:
        assert "dataclass" not in source
        assert "Enum" not in source
        assert "z0" not in source and "z1" not in source and "z2" not in source
        assert "__BASE__" not in source and "__TITLE__" not in source and "__SPEC__" not in source
        compile(source,cid,"exec")
        ns={};exec(compile(source,cid,"exec"),ns)
        assert "FHIRResourceBundleGenerator" in ns

def test_parser_accepts_96_semantic_answer_fixtures():
    yes_values=("YES","MATCH","符合",'{"decision":"YES"}',{"match":True},{"decision":"MATCH"})
    no_values=("NO","NO_MATCH","不符合",'{"decision":"NO"}',{"match":False},{"decision":"NO_MATCH"})
    checked=0
    for _cid in CRITERIA:
        for value in yes_values:
            assert parse_decision(value)[0]=="MATCH"
            checked+=1
        for value in no_values:
            assert parse_decision(value)[0]=="NO_MATCH"
    assert checked==96

def test_embedded_positive_negative_fhir_security_and_metrics_for_all_criteria():
    for cid in CRITERIA:
        pos,calls,metrics=run_embedded(cid,POS[cid],"YES")
        neg,_,neg_metrics=run_embedded(cid,NEG[cid],"NO")
        assert pos["resourceType"]=="Bundle" and pos["type"]=="transaction"
        assert neg["resourceType"]=="Bundle" and neg["type"]=="transaction"
        assert pos["entry"], cid
        assert not neg["entry"], cid
        assert "V5S_METRICS|" in metrics
        assert "patient-1" not in metrics and POS[cid] not in metrics
        assert "route=RULE" in metrics or calls

def test_embedded_multi_anchor_prompt_fuses_distant_same_report_evidence():
    text="患者年龄70岁。"+"无关。"*20+"确诊带状疱疹。"+"无关。"*20+"病灶位于头面部"
    _,calls,_=run_embedded("675",text,"YES")
    assert len(calls)==1
    assert "70岁" in calls[0] and "带状疱疹" in calls[0] and "头面部" in calls[0]

def test_fhir_transaction_structure_and_security_for_all_embedded_resources():
    for cid in CRITERIA:
        bundle,_,_=run_embedded(cid,POS[cid],"YES")
        for entry in bundle["entry"]:
            resource=entry["resource"]
            assert entry["request"]=={"method":"POST","url":resource["resourceType"]}
            assert resource["resourceType"] in {"Observation","Condition","Procedure","MedicationAdministration"}
            assert "subject" in resource or resource["resourceType"]=="Procedure"
    for _cid,_,source in decoded_libraries():
        assert "input(" not in source and "eval(" not in source
        assert "os.system" not in source and "subprocess" not in source
        assert "patient text" not in source.lower()
