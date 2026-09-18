import base64, json, ast, builtins
from pathlib import Path
from types import SimpleNamespace

ROOT=Path(__file__).parents[1]
CAND=ROOT/'submission/a_test_message_bundle_v5a_probe_fixed_candidate.json'
POS={"165":"已在外院完成两周期化疗","185":"首次接受伊立替康化疗","265":"术前cTnI 0.08 ug/L","485":"盆腔器官脱垂 POP-Q III期","555":"3个月前完成胆囊切除术","565":"目前严重腹泻","615":"术后病理 pN1","635":"AST 30上限40 ALT 30上限40 BUN 8上限9 Cr 80上限100","675":"患者70岁确诊头面部带状疱疹","735":"活动性乙型肝炎","745":"术后行有创机械通气","755":"机械通气持续30小时","805":"目前每日吸烟","835":"目前凝血功能异常","855":"Scr 120 umol/L","875":"既往发生颅内高压"}
class Fake:
    def decide(self,prompt):
        return SimpleNamespace(parsed=SimpleNamespace(decision=SimpleNamespace(value='MATCH'),method=SimpleNamespace(value='PARSED_SENTINEL')),attempts=1,status=SimpleNamespace(value='OK'))
def main():
    b=json.loads(CAND.read_text(encoding='utf-8')); pos=neg=loaded=0
    for e in b['entry']:
        r=e['resource']
        if r.get('resourceType')!='Library': continue
        s=base64.b64decode(r['content'][0]['data']).decode(); compile(s,r['name'],'exec'); ns={}; exec(compile(s,r['name'],'exec'),ns)
        loader=next(v for k,v in ns.items() if k.endswith('_load_criterion_specs'))
        specs=loader(); assert len(specs)==16; loaded+=1
        g=ns['FHIRResourceBundleGenerator']('http://localhost:3456'); g.transport=Fake()
        assert g.parse_clinical_text_to_fhir_bundle('p1',[{'text':POS[r['content'][0]['title']],'timestamp':'2026-01-01'}])['resourceType']=='Bundle'; pos+=1
        assert g.parse_clinical_text_to_fhir_bundle('p1',[{'text':'无相关信息'}])['resourceType']=='Bundle'; neg+=1
    print(f'embedded_exec={loaded}/16 criterion_specs={loaded}/16 positive={pos}/16 negative={neg}/16')
if __name__=='__main__': main()
