import base64,json
from pathlib import Path
import sys
ROOT=Path(__file__).parents[1];sys.path.insert(0,str(ROOT/"src"))
from v43.fhir.contracts import BASE,contract_for_criterion
from v5s.criterion_data import CRITERION_IDS
TEMPLATE=(ROOT/"src/v5s/runtime_template.py").read_text(encoding="utf-8")
SHELL=ROOT.parent/"CHIP2026_CP2_A_baseline_v2_4_3/submission/a_test_message_bundle_v2_4_3.json"
OUT=ROOT/"submission/a_test_message_bundle_v5s_candidate.json"
ALIASES={
"165":["化疗","外院","外部医院"],"185":["伊立替康","irinotecan","CPT-11","首次","初次"],"265":["cTnI","cTnT","肌钙蛋白"],
"485":["POP-Q","盆腔器官脱垂"],"555":["手术","切除","个月前"],"565":["腹泻","便秘","严重"],"615":["pT","R1","pN1","GS","Gleason","PSA"],
"635":["AST","ALT","BUN","Cr","肌酐","尿素氮"],"675":["年龄","带状疱疹","头面部"],"735":["乙型肝炎","HIV","结核","结缔组织"],
"745":["手术","术后","机械通气","有创"],"755":["机械通气","持续","小时","天"],"805":["吸烟","戒烟"],"835":["凝血","PT","APTT","INR"],
"855":["Scr","肌酐","BUN","ALT","AST"],"875":["颅内高压","意识障碍","昏迷"]
}
RULES={c:"患者相关证据是否明确满足标准："+",".join(ALIASES.get(c,[c])) for c in CRITERION_IDS}
GROUPS={
"165":[["化疗"],["外院","外部医院"],["完成","接受","已行","治疗"]],
"185":[["伊立替康","irinotecan","CPT-11"],["首次","初次"],["给药","接受","使用","化疗"]],
"265":[["cTnI"],["cTnT"],["肌钙蛋白"]],
"485":[["POP-Q","盆腔器官脱垂"]],
"555":[["手术","切除"],["个月前"]],
"565":[["腹泻","便秘"],["严重","重度"],["目前","当前"]],
"615":[["pT","R1","pN1","GS","Gleason","PSA"]],
"635":[["AST"],["ALT"],["BUN","尿素氮"],["Cr","肌酐"]],
"675":[["年龄","岁"],["带状疱疹"],["头面部","面部","头部"]],
"735":[["乙型肝炎","HIV","结核","结缔组织"],["活动性","活动期","正在治疗","未控制"]],
"745":[["手术","术后"],["机械通气","有创"]],
"755":[["机械通气"],["持续","历时","小时","天","日"]],
"805":[["吸烟","烟民"],["戒烟","quit","从不","从未"]],
"835":[["凝血","PT","APTT","INR"],["异常","障碍","紊乱"]],
"855":[["Scr","肌酐"],["BUN","尿素氮"],["ALT"],["AST"]],
"875":[["颅内高压"],["意识障碍","昏迷"]],
}
def lit(v): return repr(v)
def build_source(cid,title,identifier):
    c=contract_for_criterion(cid)
    profiles=list(c.profiles)
    ps={"pT":profiles[0],"R1":profiles[min(1,len(profiles)-1)],"pN1":profiles[min(2,len(profiles)-1)],"GS":profiles[min(3,len(profiles)-1)],"PSA":profiles[min(4,len(profiles)-1)]}
    spec={"aliases":ALIASES.get(cid,[cid]),"groups":GROUPS.get(cid,[ALIASES.get(cid,[cid])]),"rule":RULES[cid],"blockers":[]}
    src=TEMPLATE
    repl={"__BASE__":lit(BASE),"__TITLE__":lit(cid),"__PROFILE__":lit(profiles[0]),"__RESOURCE_TYPE__":lit(c.resource_type),"__PROFILES__":lit(ps),"__SPEC__":lit(spec)}
    for k,v in repl.items(): src=src.replace(k,v)
    compile(src,title,"exec"); return src
def main():
    bundle=json.loads(SHELL.read_text(encoding="utf-8"));count=0
    for e in bundle["entry"]:
        r=e["resource"]
        if r.get("resourceType")!="Library":continue
        cid=str(r["content"][0]["title"]);src=build_source(cid,r["name"],r.get("identifier",{}));r["content"][0]["data"]=base64.b64encode(src.encode()).decode();count+=1
    assert count==16
    OUT.write_text(json.dumps(bundle,ensure_ascii=False,indent=2),encoding="utf-8");print(OUT,OUT.stat().st_size)
if __name__=="__main__":main()
