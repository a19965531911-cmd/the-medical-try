"""Final-source MOCK pair evaluation; historical artifacts are read-only."""
import ast,base64,csv,hashlib,json,sys,time,threading,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'src'))
from scripts.b7_1_experiments import scopes
from scripts.b5_experiments import metrics
from scripts.build_b_submission import load_rows,submission_sanity_check
from scripts.audit_b_board import replay_service
from scripts.b2_experiments import r4_structure,fsh_checks
D=ROOT/'experiment/b7-2';D.mkdir(exist_ok=True)
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
def build():
    b=json.loads((ROOT/'experiment/b7-1/B7_1H.json').read_text(encoding='utf8'));overlay=(ROOT/'src/b_board/b7_2_overlay.py').read_text(encoding='utf8')
    for e in b['entry'][1:]:
        r=e['resource'];s=base64.b64decode(r['content'][0]['data']).decode()+'\n'+overlay;compile(s,r['name'],'exec');r['content'][0]['data']=base64.b64encode(s.encode()).decode()
    submission_sanity_check(b,load_rows());return b
def robust(base):
    out=[]
    for c in base:
        if c['case'] not in ('2_false_hint','3_false_hint','495_false_hint'):continue
        q=c['reports'][0]['text'];cid=c['profile_id']
        variants=[('original',q),('reorder',q.replace('，','。')),('synonym',q.replace('活动后','走动以后').replace('已完整切除','已彻底切除')),('sentence_split',q.replace('，','；'))]
        for name,text in variants:
            r=json.loads(json.dumps(c));r['case']+='_'+name;r['reports']=[dict(text=text,timestamp='2026-10-09')]
            for f in r['raw']['facts']:f['evidence']=text
            r['raw']['evidence']=[text];out.append(r)
        for name,records,index in [('irrelevant_before',[dict(text='血压120/80'),c['reports'][0]],1),('irrelevant_after',[c['reports'][0],dict(text='血压120/80')],0),('ambiguous',[c['reports'][0],dict(c['reports'][0],event_id='other')],0)]:
            r=json.loads(json.dumps(c));r['case']+='_'+name;r['reports']=records
            for f in r['raw']['facts']:f['report']=index
            out.append(r)
        # Negative/plan additions preserve noneligibility, with identical response quote.
        for name,prefix in [('negated','否认'),('planned','拟评估')]:
            r=json.loads(json.dumps(c));r['case']+='_'+name;r['reports']=[dict(text=prefix+q)];r['expected']=False;out.append(r)
        if cid=='3':
            parts=q.split('，')
            for reverse in (False,True):
                r=json.loads(json.dumps(c));r['case']+='_distributed_'+str(reverse)
                r['reports']=[dict(text=t,event_id='same_event',timestamp='2026-10-09') for t in (list(reversed(parts)) if reverse else parts)]
                atom_parts={'hcc':parts[0],'pathology':parts[0],'resection':parts[1],'r0':parts[2]}
                for f in r['raw']['facts']:
                    f['evidence']=atom_parts[f['atom']];f['report']=next(i for i,x in enumerate(r['reports']) if x['text']==f['evidence'])
                r['raw']['evidence']=list(dict.fromkeys(f['evidence'] for f in r['raw']['facts']));out.append(r)
    return out
def run():
    frozen={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ('submission','experiment/b2-official-contract','experiment/b4-semantic-recall','experiment/b5','experiment/b6','experiment/b7','experiment/b7-1') for p in (ROOT/folder).rglob('*') if p.is_file()};dump(D/'frozen_hashes.json',frozen)
    base=json.loads((ROOT/'experiment/b7-1/cases.json').read_text(encoding='utf8'));perturbed=robust(base)
    b=build();dump(D/'B7_2H.json',b);bundles={'B7_1H':json.loads((ROOT/'experiment/b7-1/B7_1H.json').read_text(encoding='utf8')),'B7_2H':b};rows={str(r['profile_id']):r for r in load_rows()};nss={v:scopes(b) for v,b in bundles.items()};settings={'raw':None};requests=[]
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_POST(self):
            raw=json.loads(self.rfile.read(int(self.headers['Content-Length'])));requests.append(dict(path=self.path,model=raw['model'],tokens=raw['max_tokens']))
            self.send_response(200);self.end_headers();self.wfile.write(json.dumps({'choices':[{'message':{'content':json.dumps(settings['raw'])}}]}).encode())
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();endpoint='http://127.0.0.1:'+str(server.server_port)+'/v1/chat/completions';results=[]
    try:
        for v in bundles:
            for group,cases in [('original',base),('robustness',perturbed)]:
                for c in cases:
                    n=nss[v][c['profile_id']];n['B6_CONFIG']['endpoint']=endpoint;settings['raw']=c['raw'];g=n['FHIRResourceBundleGenerator']('http://localhost:3456');start=time.perf_counter();out=g.parse_clinical_text_to_fhir_bundle('p1',c['reports']);m=g.model_metrics
                    baseline=n['evaluate_b2'](c['profile_id'],c['reports'],'B2E')['match'];hit=replay_service(rows[c['profile_id']],out)['hit'];accepted=sum(f.get('source')=='semantic' for f in g.last_result['facts'].values())
                    results.append(dict(variant=v,group=group,case=c['case'],profile_id=c['profile_id'],expected=c['expected'],predicted=g.last_result['match'],baseline_match=baseline,calls=m['calls'],http=m['http_success'],json_valid=m['json_valid'],facts=accepted,hit=hit,resources=len(out['entry']),fsh=fsh_checks(rows[c['profile_id']],out),r4=r4_structure(out),elapsed=time.perf_counter()-start,errors=m['errors'],rejections=m['fact_rejections'],skips=g.b5_trace.get('unrescuable_call_skips',[])))
    finally:server.shutdown();server.server_close()
    dump(D/'results.json',results);dump(D/'robust_cases.json',perturbed);dump(D/'http_requests.json',requests)
    summary={}
    for v in bundles:
        r=[x for x in results if x['variant']==v and x['group']=='original'];calls=sum(x['calls'] for x in r);res=sum(x['expected'] and not x['baseline_match'] and x['hit'] for x in r)
        summary[v]=dict(metrics=metrics(r),calls=calls,rescues=res,productive_rate=res/calls if calls else None,accepted_facts=sum(x['facts'] for x in r),facts_per_call=sum(x['facts'] for x in r)/calls if calls else None,calls_per_rescue=calls/res if res else None,robust_metrics=metrics([x for x in results if x['variant']==v and x['group']=='robustness']))
    dump(D/'summary.json',summary)
    audit=[]
    for e in b['entry'][1:]:
        source=base64.b64decode(e['resource']['content'][0]['data']).decode();tree=ast.parse(source);wanted=['_b4_prompt','_b4_decode','_b4_call','_b4_evaluate','_b7_transport','_b7_entry'];defs={name:[n.lineno for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name] for name in wanted};audit.append(dict(profile_id=e['resource']['content'][0]['title'],definitions=defs,last_lines={k:v[-1] for k,v in defs.items()}))
    dump(D/'binding_audit.json',audit)
    # B7.1 timing XML identifies measured hotspots instead of guessing.
    old=ET.parse(ROOT/'experiment/b7-1/regression.xml').getroot();tests=sorted([dict(file=x.attrib.get('classname'),test=x.attrib.get('name'),seconds=float(x.attrib.get('time',0))) for x in old.iter('testcase')],key=lambda x:x['seconds'],reverse=True);dump(D/'historical_slowest_tests.json',tests[:30])
    def report(name,text):(ROOT/'reports'/name).write_text(text+'\n',encoding='utf8')
    report('B7_2_EFFECTIVE_CALL_CHAIN.md','Decoded all16 final Libraries; binding_audit.json lists ALL definition lines and last definitions.\n```mermaid\nflowchart LR\nEntry[_b7_entry] --> B5[_b5_entry] --> Eval[_b4_evaluate] --> Call[_b4_call final B7.2] --> Decode[_b4_decode final B7.2]\nCall --> HTTP[_b7_transport]\nDecode --> Merge[UNKNOWN categorical merge] --> Builder[deterministic B2 Builder] --> Service[official replay]\n```\nAliases preserve earlier implementations, whose global prompt/decode lookups reach final overrides. Final class transport remains _b7_transport.')
    report('B7_2_SCHEMA_FIX.md','Compact facts exactly atom/state/evidence; source binding is unique across every supplied record, even legacy model report hints. Ambiguity rejected; no first-match fallback. Missing/empty top evidence deterministically filled only after all facts literally located; conflicting list rejected. B7.1 false overall hint rescue retained; AND and protected numeric/event constraints unchanged. Historical schemas accepted only with correct independently validated provenance. New prompt states this contract.')
    report('B7_2_CALL_EFFICIENCY.md','MOCK paired original158 cases and unchanged model responses:\n'+json.dumps(summary,indent=2)+'\nOnly calls with exclusively protected deterministic atoms suppressed. No broad anchor filter and no removal of difficult categorical cases. No clinical recall gained on original responses; reduced calls are nonrescuable numeric/duration/vessel inquiries. Repeated unproductive empty fixtures cannot establish Qwen behavior. Valid accepted facts-per-call is measured, not raw grounded proposals.')
    report('B7_2_ROBUST_RESCUES.md','Same paired perturbations and fixed response policies: '+json.dumps(summary,indent=2)+'\nAmbiguous source preserves true clinical label but should abstain; resulting FN is intentionally counted. Report-order changes carry the same quote with correct legacy index. Fact-changing negation/plans explicitly use negative labels. Response quotes are rewritten along with source: measures deterministic plumbing robustness, not model language generalization. Same-event four-atom evidence distributed over three records tested in both report orders; conservative pathology UNKNOWN/UNCERTAIN gate can still prevent rescue. These failures are counted, not relabelled.')
    report('B7_2_TEST_PERFORMANCE.md','Historical slowest30 measured testcases: historical_slowest_tests.json. XML elapsed is host wall time, not platform inference. FAST: tests/b_board/test_b7_2.py +test_b7_1.py +test_b7_schema.py. INTEGRATION: final16 isolated Library/Service checks. STRESS: existing test_b6_http.py real socket tests retained; acceptance delay checks scripts/b7_acceptance.py remain unchanged. FULL: bare pytest with writable cache. Group elapsed saved as tests complete; no stress tests deleted.')
    report('B7_2_PLATFORM_SMOKE_PLAN.md','PRE-SUBMISSION REVIEW ONLY. Confirm B2/3 identifiers, B header and official checker first. Obtain explicit user authorization for any upload/score consumption. Preserve artifact hash. If official rules permit logs: record only stage/counter/latency/profile and model identifier, never raw patient text or quotes. Distinguish MOCK_HTTP, PLATFORM_HTTP, PARSED_JSON, ACCEPTED_FACT, FHIR_SERVICE_MATCH, OFFICIAL_SCORE. Authorised official sandbox or fixed synthetic probe preferable; no platform facility currently available. Do not claim test_a sample validates B routing. Config1213/local-model remains;8s policy remains unverified. Max2 residual worker per namespace,32 for16; trickle requests cannot force cancellation. Platform quota/thread/network permissions must be confirmed before publish.')
    report('B7_2_PUBLICATION_AUDIT.md','Original workbook load_rows: '+json.dumps([{k:r[k] for k in ('profile_id','id','index','deepquery_id')} for r in load_rows() if str(r['profile_id']) in ('2','3')])+'\nActual header: '+json.dumps(b['entry'][0])+'\ntrain_set left unchanged, not assumed correct B contract. All16 Library id/name/title pass existing sanity checks; checker is local, not official.18 known historical FSH case conflicts preserved; new outputs subset validation only. Official full checker, B announcement/header/mapping and runtime quota not supplied; UNVERIFIED.')
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in frozen.items())
    print(json.dumps(summary),flush=True)
if __name__=='__main__':run()
