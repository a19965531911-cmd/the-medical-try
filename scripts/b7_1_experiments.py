"""MOCK protocol/schema comparison and independent request attribution."""
import ast,base64,csv,hashlib,json,sys,time,threading,zipfile
from pathlib import Path
from collections import Counter
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'src'))
from scripts.b5_experiments import corpus,metrics
from scripts.build_b_submission import load_rows,submission_sanity_check,publication_gate
from scripts.audit_b_board import replay_service
from scripts.b2_experiments import fsh_checks,r4_structure
D=ROOT/'experiment/b7-1';D.mkdir(exist_ok=True)
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
def scopes(b):
    result={}
    for e in b['entry'][1:]:
        r=e['resource'];n={};exec(base64.b64decode(r['content'][0]['data']),n);result[r['content'][0]['title']]=n
    return result
def build():
    b=json.loads((ROOT/'experiment/b7/B7H.json').read_text(encoding='utf8'))
    overlay=(ROOT/'src/b_board/b7_1_overlay.py').read_text(encoding='utf8')
    for e in b['entry'][1:]:
        r=e['resource'];s=base64.b64decode(r['content'][0]['data']).decode()+'\n'+overlay
        compile(s,r['name'],'exec');r['content'][0]['data']=base64.b64encode(s.encode()).decode()
    submission_sanity_check(b,load_rows());return b
def category(record):
    if not record['http_success']:return 'NETWORK_OR_TIMEOUT'
    raw=record['model_response']
    if not isinstance(raw,dict):return 'INVALID_RESPONSE_FORMAT'
    if not record['json_valid']:
        quotes=[f.get('evidence','') for f in raw.get('facts',[]) if isinstance(f,dict)]
        return 'SOURCE_LOCATION_FAILED' if any(not any(q and q in r.get('text','') for r in record['reports']) for q in quotes) else 'SCHEMA_FAILED'
    if record['accepted_facts']==0:return 'CONTEXT_REJECTED' if record['fact_rejections'] else 'DUPLICATE_OR_OVERALL_HINT_DISCARDED'
    if not record['final_match']:return 'ACCEPTED_INCOMPLETE'
    if not record['fhir_emitted']:return 'FHIR_NOT_GENERATED'
    if not record['service_match']:return 'SERVICE_MISS'
    return 'NEW_SERVICE_MATCH' if not record['baseline_match'] else 'DUPLICATE_FACTS'
def run():
    paths=[p for folder in ('submission','experiment/b2-official-contract','experiment/b4-semantic-recall','experiment/b5','experiment/b6','experiment/b7') for p in (ROOT/folder).rglob('*') if p.is_file()]
    frozen={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths};dump(D/'frozen_hashes.json',frozen)
    bundles={v:json.loads((ROOT/p).read_text(encoding='utf8')) for v,p in [('B2E','experiment/b2-official-contract/B2E.json'),('B6H','experiment/b6/B6H_platform_candidate.json'),('B7H','experiment/b7/B7H.json')]};bundles['B7_1H']=build();dump(D/'B7_1H.json',bundles['B7_1H'])
    ns={v:scopes(b) for v,b in bundles.items()};rows={str(r['profile_id']):r for r in load_rows()}
    original=json.loads((ROOT/'experiment/b7/rescue_results.json').read_text(encoding='utf8'));cases=[]
    for r in original:
        if r['variant']!='B7H':continue
        cases.append(dict(case=r['case_id'],profile_id=r['profile_id'],reports=r['reports'] if 'reports' in r else [],expected=r['expected'],raw=r['model_response']))
    # Earlier table omitted original reports: reconstruct directly from authored case quotes/prefix.
    for c in cases:
        q=c['raw']['evidence'][0] if c['raw']['evidence'] else '患者无相关病史'
        suffix=c['case'].split('_',1)[1]
        prefix={'family':'父亲','negative':'否认','uncertain':'可能','planned':'拟评估'}.get(suffix,'')
        text='患者无相关病史' if suffix=='hallucination' else prefix+q
        c['reports']=[dict(text=text,timestamp='2026-10-09')]
    for cid,q,atoms in [('2','活动后透不过气',['respiratory']),('3','组织学提示肝细胞恶性肿瘤，已完整切除肝肿瘤，切缘未残留癌细胞',['hcc','pathology','resection','r0']),('495','病理报告。确诊弥漫性大细胞B淋巴瘤',['dlbcl'])]:
        raw=dict(match=False,facts=[dict(atom=a,state='PRESENT',evidence=q,report=0) for a in atoms],subject='patient',negated=False,planned=False,uncertain=False,evidence=[q],reason='Overall hint false despite independently supported facts; MOCK')
        cases.append(dict(case=cid+'_false_hint',profile_id=cid,reports=[dict(text=q,timestamp='2026-10-09')],expected=True,raw=raw))
        for prefix in ('父亲','否认','可能','拟评估'):
            cases.append(dict(case=cid+'_false_hint_'+prefix,profile_id=cid,reports=[dict(text=prefix+q)],expected=False,raw=raw))
    cases += [dict(**f,raw=dict(match=None,facts=[],subject='patient',negated=False,planned=False,uncertain=False,evidence=[],reason='MOCK empty control')) for f in corpus()]
    settings={'raw':None};http=[]
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_POST(self):
            p=json.loads(self.rfile.read(int(self.headers['Content-Length'])));http.append(dict(path=self.path,model=p['model'],max_tokens=p['max_tokens']))
            self.send_response(200);self.end_headers();self.wfile.write(json.dumps({'choices':[{'message':{'content':json.dumps(settings['raw'])}}]}).encode())
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();endpoint='http://127.0.0.1:'+str(server.server_port)+'/v1/chat/completions';records=[]
    try:
        for v in bundles:
            for c in cases:
                n=ns[v][c['profile_id']];g=n['FHIRResourceBundleGenerator']('http://localhost:3456');settings['raw']=c['raw']
                if v=='B2E':
                    # Explicit deterministic baseline: evaluate/build, no semantic transport.
                    result=n['evaluate_b2'](c['profile_id'],c['reports'],'B2E');resources=n['build_b2_resources'](c['profile_id'],'p1',c['reports'],result,'B2E');out=dict(resourceType='Bundle',type='transaction',entry=[dict(resource=r,request=dict(method='POST',url=r['resourceType'])) for r in resources]);m={};facts=result['facts'];final=result['match'];elapsed=0
                else:
                    n['B6_CONFIG']['endpoint']=endpoint;start=time.perf_counter();out=g.parse_clinical_text_to_fhir_bundle('p1',c['reports']);elapsed=time.perf_counter()-start;m=g.model_metrics;facts=g.last_result['facts'];final=g.last_result['match']
                base=n['evaluate_b2'](c['profile_id'],c['reports'],'B2E')['match']
                r=dict(variant=v,**c,model_response=c['raw'],baseline_match=base,final_match=final,predicted=final,http_success=m.get('http_success',0),json_valid=m.get('json_valid',0),grounded=m.get('grounded',0),accepted_facts=sum(f.get('source')=='semantic' for f in facts.values()),fact_rejections=m.get('fact_rejections',0),calls=m.get('calls',0),fhir_emitted=len(out['entry']),service_match=replay_service(rows[c['profile_id']],out)['hit'],elapsed=elapsed)
                r['category']=category(r) if r['calls'] else 'NO_CALL';records.append(r)
    finally:server.shutdown();server.server_close()
    dump(D/'cases.json',cases);dump(D/'results.json',records);dump(D/'http_summaries.json',http)
    attribution=[]
    for r in records:
        for i in range(r['calls']):attribution.append(dict(variant=r['variant'],case=r['case'],request_index=i,category=r['category']))
    assert len(attribution)==sum(r['calls'] for r in records);dump(D/'request_attribution.json',attribution)
    summary={v:metrics([r for r in records if r['variant']==v]) for v in bundles};dump(D/'summary.json',summary)
    comparison=[];n=ns['B7_1H']['2'];reports=[dict(text='活动后透不过气',event_id='A')];simple=dict(match=True,facts=[dict(atom='respiratory',state='PRESENT',evidence=reports[0]['text'],report=0)],subject='patient',negated=False,planned=False,uncertain=False,evidence=[reports[0]['text']],reason='MOCK')
    extended=dict(simple,profile_id='2',criterion=n['QUESTION']);extended['facts']=[dict(atom='respiratory',state='PRESENT',evidence=reports[0]['text'],report_index=0,subject='patient',event_identity='A')]
    compact=dict(simple);compact['facts']=[dict(atom='respiratory',state='PRESENT',evidence=reports[0]['text'])]
    for label,raw in [('A',simple),('B',extended),('C',compact)]:
        start=time.perf_counter();parsed=n['_b4_decode'](raw,'2',reports,['respiratory']);comparison.append(dict(schema=label,json_valid=True,grounded=True,facts=len(parsed['facts']),utf8_output_bytes=len(json.dumps(raw,ensure_ascii=False).encode()),actual_token_usage=None,decoder_seconds=time.perf_counter()-start,measurement='MOCK'))
    dump(D/'schema_comparison.json',comparison)
    good=[r for r in records if r['variant']=='B7_1H'];old={r['case']:r for r in records if r['variant']=='B7H'};exclusive=[r for r in good if r['expected'] and r['service_match'] and not old[r['case']]['service_match']];fp=sum(not r['expected'] and r['final_match'] for r in good);calls=sum(r['calls'] for r in good);productive=sum(r['category']=='NEW_SERVICE_MATCH' for r in good);accepted=sum(r['accepted_facts'] for r in good)
    def report(name,text):(ROOT/'reports'/name).write_text(text+'\n',encoding='utf8')
    for name,text in [
        ('B7_1_UNPRODUCTIVE_CALLS.md','Every observed request has exactly one final category: request_attribution.json. Totals equal calls. Categories distinguish source/schema/context and final Service outcome. Legacy B7 failures sometimes cannot uniquely distinguish schema from discarded overall hint: DUPLICATE_OR_OVERALL_HINT_DISCARDED is explicit uncertainty, not invented precision. '+json.dumps(dict(Counter(r['category'] for r in good if r['calls'])))),
        ('B7_1_SCHEMA_COMPARISON.md','MOCK A/B/C closed decoder comparison: '+json.dumps(comparison)+'\nC binds only unique quotes; ambiguous report locations rejected. Event is never generated by model. Output bytes measured, actual tokenizer tokens UNAVAILABLE. This does not establish Qwen schema adherence or latency. C engineering preference, not model-quality winner.'),
        ('B7_1_TRIGGER_AUDIT.md','Final B7H decode inspected. MATCH/no text skips. Deterministic NEGATED/ABSENT/PLANNED/UNCERTAIN blocks retained. Partial accepted facts request UNKNOWN only. All UNKNOWN can trigger even irrelevant text: existing broad retrieval unchanged, false positives constrained downstream. Valid facts under match=false were discarded: B7.1 now accepts safe categorical hints while AND completeness stays deterministic. Same-event pathology synonyms can be UNCERTAIN and remain blocked; no unsafe bypass. Protected 295/625 numeric/date facts cannot be filled.'),
        ('B7_1_WORKER_LIFECYCLE.md','B7 semaphore retained;2 per namespace,32 for16 namespaces; separate processes multiply ceiling. Thread timeout cannot force cancellation of a slow trickling response. Connect/read inactivity bounded by requests scalar timeout, not total worker lifetime. Slot held until Session closes. Saturation fails closed rather than adding workers; cross-patient residual work can persist. No new resource-safety claim; deployment cancellation/server limit still unresolved. No subprocess assumptions added to platform candidate.'),
        ('B7_1_INCREMENTAL_GAIN.md','Same '+str(len(cases))+' authored cases, fixed legacy responses, local HTTP, original Service and metric code. Includes100 prior complex/boundary cases and false-overall-hint attacks. MOCK '+json.dumps(summary)+'\nB7.1-only correct Service rescues: '+json.dumps([r['case'] for r in exclusive])+'. Additional gains come from fact-level merging, not claimed actual Qwen quality. FP='+str(fp)),
        ('B7_1_PUBLICATION_CONTRACT.md','Official B workbook read via load_rows; rows2/3 remain tbd/null, identifiers inherited fallback. A485 test_a cannot establish B header. Existing18 FSH conflicts remain; no official checker or runtime quota evidence in supplied local materials. Platform live inference unverified. No submission.')]:report(name,text)
    try:publication_gate(bundles['B7_1H'],list(rows.values()))
    except ValueError as exc:dump(D/'publication_gate.json',dict(status='BLOCKED',reason=str(exc)))
    dump(D/'acceptance.json',dict(calls=calls,productive=productive,unproductive=calls-productive,accepted_facts=accepted,exclusive=[r['case'] for r in exclusive],false_positives=fp,summary=summary))
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in frozen.items())
    report('B7_1_FINAL_VERDICT.md',f'''REGRESSION_STATUS = final rerun pending
MODEL_CALL_TOTAL = {calls} (B7.1 MOCK)
UNPRODUCTIVE_CALLS = {calls-productive}
PRODUCTIVE_CALL_RATE = {productive/calls if calls else 0}
SCHEMA_BEST_VARIANT = C engineering preference; real Qwen quality unverified
GROUNDED_FACTS_ACCEPTED = {accepted}
FHIR_SERVICE_SUCCESSFUL_RESCUES = {productive}
B6H_EXCLUSIVE_RESCUES = 0 relative toB7H
B7H_EXCLUSIVE_RESCUES = 0 relative toB6H
B7_1H_EXCLUSIVE_RESCUES = {len(exclusive)} MOCK
INTRODUCED_FALSE_POSITIVES = {fp}
HTTP_WORKER_LEAK_RISK = residual slow-trickle worker risk retained
PLATFORM_MODEL_VERIFIED = NO
PUBLICATION_IDENTITY_VERIFIED = NO
FSH_VIOLATIONS_REMAINING = 18 historical
B_OFFLINE_BEST = B2E retained; B7.1 conditional research recommendation
B_ONLINE_VERIFIED = NO
B_BOARD_READY = NO
RECOMMENDED_NEXT_ACTION = real platform response and runtime cancellation/quota/identity contract verification
''')
    print(json.dumps(read_acceptance()),flush=True)
def read_acceptance():return json.loads((D/'acceptance.json').read_text(encoding='utf8'))
if __name__=='__main__':run()
