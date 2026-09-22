import base64,json
from pathlib import Path
import sys
ROOT=Path(__file__).parents[1];sys.path.insert(0,str(ROOT/"src"))
from v43.fhir.contracts import BASE,contract_for_criterion
from v5s.criterion_data import CRITERION_IDS
TEMPLATE=(ROOT/"src/v5s/runtime_template.py").read_text(encoding="utf-8")
SHELL=ROOT.parent/"CHIP2026_CP2_A_baseline_v2_4_3/submission/a_test_message_bundle_v2_4_3.json"
OUT=ROOT/"submission/a_test_message_bundle_v5s1_candidate.json"
ALIASES={
"165":["化疗","外院","外部医院"],"185":["伊立替康","irinotecan","CPT-11","首次","初次"],"265":["cTnI","cTnT","肌钙蛋白"],
"485":["POP-Q","盆腔器官脱垂"],"555":["手术","切除","个月前"],"565":["腹泻","便秘","严重"],"615":["pT","R1","pN1","GS","Gleason","PSA"],
"635":["AST","ALT","BUN","Cr","肌酐","尿素氮"],"675":["年龄","带状疱疹","头面部"],"735":["乙型肝炎","HIV","结核","结缔组织"],
"745":["手术","术后","机械通气","有创"],"755":["机械通气","持续","小时","天"],"805":["吸烟","戒烟"],"835":["凝血","PT","APTT","INR"],
"855":["Scr","肌酐","BUN","ALT","AST"],"875":["颅内高压","意识障碍","昏迷"]
}
RULES={
"165":"\u5df2\u5728\u5916\u9662\u5b8c\u6210\u65e2\u5f80\u5316\u7597\uff1b\u5fc5\u987b\u6709\u5df2\u5b8c\u6210\u4e14\u5730\u70b9\u4e3a\u5916\u9662\u7684\u8bc1\u636e",
"185":"\u9996\u6b21\u63a5\u53d7\u4f0a\u7acb\u66ff\u5eb7\uff08irinotecan/CPT-11\uff09\u7ed9\u836f\uff1b\u4ec5\u8ba1\u5212\u6216\u62df\u7528\u4e0d\u7b97",
"265":"cTnI >= 0.06 ug/L OR cTnT >= 0.03 ug/L; \u6570\u503c\u5fc5\u987b\u7ed1\u5b9a\u5bf9\u5e94\u5206\u6790\u7269",
"485":"POP-Q stage III OR IV（\u76c6\u8154\u5668\u5b98\u8131\u5782\u5206\u671f\u5fc5\u987b\u660e\u786e）",
"555":"\u624b\u672f\u6216\u5207\u9664\u53d1\u751f\u5728\u8fc7\u53bb6\u4e2a\u6708\u5185\uff1b\u65f6\u95f4\u4e0e\u624b\u672f\u4e8b\u4ef6\u9700\u6709\u8bc1\u636e\u5173\u8054",
"565":"\u5f53\u524d\u5b58\u5728\u4e25\u91cd\u8179\u6cfb\u6216\u4e25\u91cd\u4fbf\u79d8\uff1b\u5df2\u7f13\u89e3\u6216\u975e\u4e25\u91cd\u4e0d\u7b97",
"615":"pT3a OR pT3b OR pT4 OR R1 OR pN1 OR Gleason/GS >=8 OR PSA >0.1 ng/mL",
"635":"AST AND ALT AND BUN AND Cr \u56db\u9879\u5747\u6709\u503c\u53ca\u5bf9\u5e94 ULN\uff0c\u4e14\u6bcf\u9879 value <= 2*ULN\uff1b\u56db\u9879\u5fc5\u987b\u5b8c\u6574",
"675":"age >=50 AND \u5df2\u786e\u8bca\u5e26\u72b6\u75b1\u75b9 AND \u75c5\u7076\u4f4d\u4e8e\u5934\u9762\u90e8",
"735":"\u6d3b\u52a8\u6027\u4e59\u578b\u809d\u708e\u3001HIV\u3001\u7ed3\u6838\u6216\u7ed3\u7f14\u7ec4\u7ec7\u75c5\uff1b\u5386\u53f2/\u6cbb\u6108/\u4e0d\u6d3b\u52a8\u5355\u72ec\u4e0d\u7b97",
"745":"\u672f\u540e\u53d1\u751f\u6709\u521b\u673a\u68b0\u901a\u6c14\uff1b\u673a\u68b0\u901a\u6c14\u4e0e\u672f\u540e\u5173\u7cfb\u5fc5\u987b\u6709\u8bc1\u636e\u652f\u6301",
"755":"\u673a\u68b0\u901a\u6c14\u6301\u7eed >=24\u5c0f\u65f6\uff1b\u652f\u6301\u5c0f\u65f6/\u5929\u6362\u7b97\uff0c\u65f6\u957f\u5fc5\u987b\u5c5e\u4e8e\u673a\u68b0\u901a\u6c14",
"805":"\u5f53\u524d\u5438\u70df\u6216\u6212\u70df\u672a\u6ee12\u5e74\uff1b\u4fdd\u7559\u5df2\u6279\u51c6\u7684\u5f53\u524d\u5438\u70df/\u8fd1\u671f\u6212\u70df\u8bed\u4e49",
"835":"\u660e\u786e\u51dd\u8840\u529f\u80fd\u969c\u788d\u6216\u4e34\u5e8a\u6e05\u695a\u7684\u51dd\u8840\u5f02\u5e38\uff1b\u4e0d\u8bbe\u901a\u7528\u6570\u503c\u9608\u503c",
"855":"Scr <178 umol/L AND BUN <9 mmol/L AND ALT <= ULN AND AST <= ULN; \u6bcf\u4e2a\u503c\u5fc5\u987b\u5c40\u90e8\u7ed1\u5b9a\u5bf9\u5e94\u5206\u6790\u7269",
"875":"intracranial hypertension OR impaired consciousness; temporal policy = EVER_PRESENT",
}
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
    if cid=="875": ps={"intracranial":profiles[0],"consciousness":profiles[min(1,len(profiles)-1)]}
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
