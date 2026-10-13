import base64,json,sys,time,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'src'))
from scripts.build_b_submission import submission_sanity_check,load_rows
from scripts.b5_experiments import corpus,metrics
from scripts.audit_b_board import replay_service
D=ROOT/'experiment/b7';D.mkdir(exist_ok=True)


def build():
    b=json.loads((ROOT/'experiment/b6/B6H_platform_candidate.json').read_text(encoding='utf8'))
    overlay=(ROOT/'src/b_board/b7_overlay.py').read_text(encoding='utf8')
    for e in b['entry'][1:]:
        r=e['resource'];s=base64.b64decode(r['content'][0]['data']).decode()+'\n'+overlay
        compile(s,r['name'],'exec');r['content'][0]['data']=base64.b64encode(s.encode()).decode()
    submission_sanity_check(b,load_rows());return b


def run():
    b=build();(D/'B7H.json').write_text(json.dumps(b,ensure_ascii=False,indent=2),encoding='utf8')
    rows={str(r['profile_id']):r for r in load_rows()};results=[]
    for variant,bundle in [('B6H',json.loads((ROOT/'experiment/b6/B6H_platform_candidate.json').read_text(encoding='utf8'))),('B7H',b)]:
        scopes={}
        for e in bundle['entry'][1:]:
            r=e['resource'];ns={};exec(base64.b64decode(r['content'][0]['data']),ns);scopes[r['content'][0]['title']]=ns
        for case in corpus():
            ns=scopes[case['profile_id']];g=ns['FHIRResourceBundleGenerator']('http://localhost:3456')
            # Fixed negative response is a fixture, never a live-model claim.
            g.transport=lambda p:dict(match=False,facts=[],subject='patient',negated=False,planned=False,uncertain=False,evidence=[],reason='SYNTHETIC fixed UNKNOWN/negative control')
            started=time.perf_counter();out=g.parse_clinical_text_to_fhir_bundle('p1',case['reports'])
            results.append(dict(**case,variant=variant,predicted=g.last_result['match'],metrics=g.model_metrics,
                stages=getattr(g,'b7_stages',{}),service_hit=replay_service(rows[case['profile_id']],out)['hit'],elapsed=time.perf_counter()-started))
    (D/'fixed_response_comparison.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({v:metrics([r for r in results if r['variant']==v]) for v in ('B6H','B7H')}))


if __name__=='__main__':run()
