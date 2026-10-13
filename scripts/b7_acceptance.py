"""Reproducible SYNTHETIC acceptance; no platform submission or actual model claims."""
import base64,csv,hashlib,json,sys,time,threading,statistics,xml.etree.ElementTree as ET
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'src'))
from scripts.b7_experiments import build
from scripts.b5_experiments import metrics,corpus
from scripts.build_b_submission import load_rows,submission_sanity_check
from scripts.audit_b_board import replay_service
from scripts.b2_experiments import r4_structure,fsh_checks
D=ROOT/'experiment/b7';R=ROOT/'reports';A=ROOT/'analysis'

def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
def report(name,text):(R/name).write_text(text+'\n',encoding='utf8')
def scopes(b):
    out={}
    for e in b['entry'][1:]:
        r=e['resource'];ns={};exec(base64.b64decode(r['content'][0]['data']),ns);out[r['content'][0]['title']]=ns
    return out
def response(facts):return dict(match=bool(facts),facts=facts,subject='patient',negated=False,planned=False,uncertain=False,evidence=[f['evidence'] for f in facts],reason='SYNTHETIC author-defined evidence')
def fact(a,q,i=0):return dict(atom=a,state='PRESENT',evidence=q,report=i)

def run():
    frozen={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ('submission','experiment/b2-official-contract','experiment/b4-semantic-recall','experiment/b5','experiment/b6') for p in (ROOT/folder).rglob('*') if p.is_file()}
    dump(D/'acceptance_frozen.json',frozen)
    tree=ET.parse(D/'regression.xml').getroot().find('testsuite');assert tree.attrib['failures']=='0' and tree.attrib['errors']=='0'
    report('B7_REGRESSION.md','Existing complete regression: '+str(tree.attrib)+'. No duplicate run started. Fresh regression after schema edits is recorded separately.')
    b7=build();dump(D/'B7H.json',b7)
    bundles={'B6H':json.loads((ROOT/'experiment/b6/B6H_platform_candidate.json').read_text(encoding='utf8')),'B7H':b7}
    nsall={v:scopes(b) for v,b in bundles.items()};rows={str(r['profile_id']):r for r in load_rows()}
    cases=[]
    for cid,text,atoms in [
        ('2','活动后透不过气',['respiratory']),
        ('3','组织学提示肝细胞恶性肿瘤，已完整切除肝肿瘤，切缘未残留癌细胞',['hcc','pathology','resection','r0']),
        ('255','已确诊第二型糖尿病',['t2dm']),
        ('465','肾标本取样完成，病理IgA肾病',['renal_biopsy']),
        ('495','病理报告。确诊弥漫性大细胞B淋巴瘤',['dlbcl']),
        ('695','影像明确癌细胞播散至远隔器官',['distant']),
        ('765','出生记录记载曾发生严重缺氧事件',['history_hypoxia'])]:
        raw=response([fact(a,text) for a in atoms])
        context=dict(text=text,timestamp='2026-10-09')
        if cid=='495':context['topic']='病理报告'
        cases.append(dict(case_id=cid+'_rescue',profile_id=cid,reports=[context],expected=True,raw=raw))
        for label,prefix in [('family','父亲'),('negative','否认'),('uncertain','可能'),('planned','拟评估')]:
            cases.append(dict(case_id=cid+'_'+label,profile_id=cid,reports=[dict(text=prefix+text,timestamp='2026-10-09')],expected=False,raw=raw))
        cases.append(dict(case_id=cid+'_hallucination',profile_id=cid,reports=[dict(text='患者无相关病史')],expected=False,raw=raw))
    cases.append(dict(case_id='3_incomplete',profile_id='3',reports=[dict(text='组织学提示肝细胞恶性肿瘤')],expected=False,raw=response([fact('hcc','组织学提示肝细胞恶性肿瘤')])))
    records=[];requests=[];settings={'raw':None,'delay':0,'status':200,'fault':None}
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_POST(self):
            payload=json.loads(self.rfile.read(int(self.headers['Content-Length'])));requests.append(dict(path=self.path,model=payload['model'],max_tokens=payload['max_tokens']))
            delay,status,raw=settings['delay'],settings['status'],settings['raw'];time.sleep(delay)
            self.send_response(status);self.end_headers()
            try:self.wfile.write(json.dumps({'choices':[{'message':{'content':json.dumps(raw)}}]}).encode())
            except (BrokenPipeError,ConnectionResetError,ConnectionAbortedError):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
    endpoint='http://127.0.0.1:'+str(server.server_port)+'/v1/chat/completions'
    try:
        for v in bundles:
            for c in cases:
                ns=nsall[v][c['profile_id']];ns['B6_CONFIG']['endpoint']=endpoint;settings['raw']=c['raw']
                g=ns['FHIRResourceBundleGenerator']('http://localhost:3456');start=time.perf_counter();out=g.parse_clinical_text_to_fhir_bundle('p1',c['reports'])
                baseline=ns['evaluate_b2'](c['profile_id'],c['reports'],'B2E')['match'];m=g.model_metrics
                accepted=sum(f.get('source')=='semantic' for f in g.last_result['facts'].values());hit=replay_service(rows[c['profile_id']],out)['hit']
                records.append(dict(variant=v,case_id=c['case_id'],profile_id=c['profile_id'],expected_label=c['expected'],expected=c['expected'],baseline_match=baseline,model_response=c['raw'],http_success=m['http_success'],json_valid=m['json_valid'],evidence_grounded=m['grounded'],accepted_facts=accepted,final_match=g.last_result['match'],predicted=g.last_result['match'],fhir_emitted=len(out['entry']),service_match=hit,failure_reason=g.last_result['reason'],calls=m['calls'],elapsed=time.perf_counter()-start,r4_errors=r4_structure(out),fsh_violations=fsh_checks(rows[c['profile_id']],out)))
        # Small real-delay corroboration, not hundreds of long sleeps.
        real=[];ns=nsall['B7H']['2'];settings['raw']=cases[0]['raw']
        for budget,delay in [(.2,.5),(1,.5),(1,3)]:
            settings['delay']=delay;ns['B5_CONFIG']['total_model_budget_seconds']=budget
            g=ns['FHIRResourceBundleGenerator']('http://localhost:3456');start=time.perf_counter();out=g.parse_clinical_text_to_fhir_bundle('p1',cases[0]['reports'])
            real.append(dict(budget=budget,delay=delay,elapsed=time.perf_counter()-start,matched=bool(out['entry']),slots_available=ns['_B7_SLOTS']._value))
        time.sleep(3.2);assert ns['_B7_SLOTS']._value==2
        dump(D/'real_delay_checks.json',real)
    finally:server.shutdown();server.server_close()
    dump(D/'rescue_results.json',records);dump(D/'http_summaries.json',requests)
    with (A/'B7_RESCUE_CASES.csv').open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    summary={v:metrics([r for r in records if r['variant']==v]) for v in bundles};dump(D/'rescue_summary.json',summary)
    # Virtual deadline model: deterministic schedule, not measured model/token quality.
    matrix=[]
    for budget in (5,8,15,30):
        for tokens in (256,512,1024,2048):
            for delay in (.5,3,7,12,25):
                for fault in ('normal','429','500','503','invalid_json','disconnect','timeout','truncated'):
                    success=fault=='normal' and delay<budget;elapsed=min(delay,budget) if fault!='timeout' else budget
                    matrix.append(dict(budget=budget,max_tokens=tokens,delay=delay,fault=fault,success=int(success),p50=elapsed,p95=elapsed,max_calls=1,max_workers_per_library=2,max_workers_16_libraries=32,measurement='VIRTUAL_DEADLINE_MODEL_NOT_LLM'))
    with (A/'B7_TIMEOUT_RESULTS.csv').open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(matrix[0]));w.writeheader();w.writerows(matrix)
    # Extended schema and legacy-compatibility validation against actual embedded decoder.
    ns=scopes(b7)['2'];text=cases[0]['reports'];base=cases[0]['raw'];checks=[]
    extended=dict(base,profile_id='2',criterion=ns['QUESTION']);extended['facts']=[dict(atom='respiratory',state='PRESENT',evidence=text[0]['text'],report_index=0,subject='patient',event_identity=None)]
    malformed=['{}','{"facts":',dict(base,facts={}),dict(base,match='true'),dict(base,facts=[fact('unknown',text[0]['text'])]),dict(base,facts=base['facts']*2),dict(base,facts=[fact('respiratory','invented')]),dict(base,facts=[dict(base['facts'][0],value=99,unit='mg',date='2030-01-01')]),dict(extended,profile_id='3'),dict(base,subject='family'),dict(base,uncertain=True),dict(base,planned=True),dict(base,negated=True), 'extra '+json.dumps(base)]
    for raw,valid in [(base,True),(extended,True),('```json\n'+json.dumps(extended)+'\n```',True)]+[(x,False) for x in malformed]:
        try:ns['_b4_decode'](raw,'2',text,['respiratory']);actual=True
        except Exception:actual=False
        assert actual==valid;checks.append(dict(expected=valid,actual=actual))
    dump(D/'schema_checks.json',checks)
    for name,body in [('B7_POSITIVE_RESCUE.md','Actual local HTTP, authored SYNTHETIC positive and adversarial cases. '+json.dumps(summary)+'\nDetailed original evidence/response/stages: rescue_results.json. Renal disease semantic spelling may pass extraction but builder cannot map unknown code: report as mapping failure, never success.'),('B7_END_TO_END_GAIN.md',json.dumps(summary)+'\nSame fixed responses and Service. Both systems already support categorical rescue; no B7-specific recall improvement claimed.'),('B7_TIMEOUT_MATRIX.md','640 virtual deadline combinations; token parameter is transmitted but token quality cannot be simulated by clock math. P50/P95 are degenerate one-schedule virtual values, not empirical inference latency. Three actual HTTP delay corroborations saved. Slots returned after workers exit. Per namespace2; sixteen32; separate processes multiply this bound. No platform quota evidence. Keep8 seconds comparison; do not select30 by assumption.'),('B7_SCHEMA_VALIDATION.md',str(len(checks))+' closed-schema checks passed. Extended criterion/profile_id and fact report_index/subject/event_identity verified, legacy schema remains compatible. No invented numeric/unit/date fields accepted. Top-level grounded counter combines schema+literal location; contextual rejection is later fact_rejections. No measured max_tokens JSON quality.'),('B7_JSON_SUCCESS.md','Closed legacy/extended schema tests and Markdown normalization verified. Output capacity of256/512/1024/2048 cannot be measured without Qwen; virtual token settings do not establish JSON success ratios.')]:report(name,body)
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in frozen.items())
    good=[r for r in records if r['variant']=='B7H'];res=sum(r['expected'] and not r['baseline_match'] and r['final_match'] for r in good);service=sum(r['expected'] and not r['baseline_match'] and r['final_match'] and r['service_match'] for r in good);fp=sum(not r['expected'] and r['final_match'] for r in good)
    report('B7_FINAL_VERDICT.md',f'''B7_STATUS = OFFLINE_RESEARCH_ACCEPTANCE; PLATFORM_BLOCKED
REGRESSION = existing1114 PASS; final rerun separately
LIBRARIES_VERIFIED = pending isolated final artifact acceptance
HTTP_WORKER_LIMIT = 2 per namespace;32 across16; no unbounded worker creation
HTTP_RESOURCE_LEAKS = slots reclaimed in delay checks; indefinite trickle can occupy slots, cannot cancel server work
TIMEOUT_MATRIX = 640 virtual combinations +3 actual delay checks
SCHEMA_VALIDATION = {len(checks)} checks passed
POSITIVE_RESCUE_CASES = 7 targeted profiles plus attacks/incomplete
RESCUED_TRUE_POSITIVES = {res}
INTRODUCED_FALSE_POSITIVES = {fp}
FHIR_SERVICE_SUCCESSFUL_RESCUES = {service}
B6H_SYNTHETIC_F1 = {summary['B6H']['f1']}
B7H_SYNTHETIC_F1 = {summary['B7H']['f1']}
B6H_SYNTHETIC_RECALL = {summary['B6H']['recall']}
B7H_SYNTHETIC_RECALL = {summary['B7H']['recall']}
PLATFORM_LIVE_INFERENCE_VERIFIED = NO
B7_OFFLINE_CANDIDATE = B7H research artifact
B_OFFLINE_BEST = B2E retained; no stable B7-specific clinical improvement
B_BOARD_READY = NO
REMAINING_BLOCKERS = platform time quota/live model;2/3 identities;MessageHeader;18 FSH conflicts;official checker; actual token-quality study
''')
    print(json.dumps(dict(summary=summary,rescues=res,service_rescues=service,false_positives=fp)),flush=True)

if __name__=='__main__':run()
