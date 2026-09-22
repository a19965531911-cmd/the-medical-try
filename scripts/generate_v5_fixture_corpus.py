import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
POS={
"165":"已在外院完成两周期化疗","185":"首次接受伊立替康化疗","265":"术前cTnI 0.08 ug/L","485":"盆腔器官脱垂 POP-Q III期","555":"3个月前完成胆囊切除术","565":"目前严重腹泻","615":"术后病理 pN1","635":"AST 30上限40 ALT 30上限40 BUN 8上限9 Cr 80上限100","675":"患者70岁确诊头面部带状疱疹","735":"活动性乙型肝炎","745":"术后行有创机械通气","755":"机械通气持续30小时","805":"目前每日吸烟","835":"目前凝血功能异常","855":"Scr 120 umol/L","875":"既往发生颅内高压"}
NEG={
"165":"仅计划转外院化疗","185":"拟首次使用伊立替康，尚未给药","265":"术后cTnI 0.08 ug/L","485":"POP-Q II期","555":"手术距今8个月","565":"严重腹泻已缓解","615":"pN0且GS 7，PSA 0.05","635":"AST 30上限40 ALT 30上限40 BUN 8上限9 Cr 250上限100","675":"躯干部带状疱疹，非头面部","735":"乙肝病情稳定","745":"术后仅无创通气","755":"机械通气持续3天但仅12小时","805":"从不吸烟","835":"凝血功能正常","855":"Scr 80 umol/L","875":"否认颅内高压且意识清楚"}
rows=[]
for cid in POS:
 for i in range(3): rows.append({"criterion":cid,"case_id":f"{cid}-p{i+1}","class":"positive","reports":[{"text":POS[cid]+("。"*i)}],"expected":"MATCH"})
 for i in range(3): rows.append({"criterion":cid,"case_id":f"{cid}-n{i+1}","class":"negative","reports":[{"text":NEG[cid]+("。"*i)}],"expected":"NO_MATCH"})
 rows.append({"criterion":cid,"case_id":f"{cid}-u1","class":"ambiguous","reports":[{"text":"相关病史存在，但关键细节未记录"}],"expected":"UNKNOWN"})
out=ROOT/"tests/fixtures/v5_matcher_cases.json"; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
print(out,len(rows))
