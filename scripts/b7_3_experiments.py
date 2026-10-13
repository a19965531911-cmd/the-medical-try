"""Offline gates, AST alias audit and exact-response MOCK comparison."""
import ast,base64,hashlib,json,sys,time,threading,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'src'))
from scripts.b7_1_experiments import scopes
from scripts.b5_experiments import corpus,metrics
from scripts.build_b_submission import load_rows,submission_sanity_check,publication_gate
from scripts.audit_b_board import replay_service
from scripts.b2_experiments import r4_structure,fsh_checks
from scripts.check_b_submission import CHILD
D=ROOT/'experiment/b7-3';D.mkdir(exist_ok=True)
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
def build():
    b=json.loads((ROOT/'experiment/b7-2/B7_2H.json').read_text(encoding='utf8'));overlay=(ROOT/'src/b_board/b7_3_overlay.py').read_text(encoding='utf8')
    for e in b['entry'][1:]:
        r=e['resource'];s=base64.b64decode(r['content'][0]['data']).decode()+'\n'+overlay;compile(s,r['name'],'exec');r['content'][0]['data']=base64.b64encode(s.encode()).decode()
    submission_sanity_check(b,load_rows());return b
def run():
    frozen={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ('submission','experiment/b2-official-contract','experiment/b4-semantic-recall','experiment/b5','experiment/b6','experiment/b7','experiment/b7-1','experiment/b7-2') for p in (ROOT/folder).rglob('*') if p.is_file()};dump(D/'frozen_hashes.json',frozen)
    b=build();dump(D/'B7_3H.json',b);rows=load_rows();rowmap={str(r['profile_id']):r for r in rows}
    audit=[]
    for e in b['entry'][1:]:
        r=e['resource'];source=base64.b64decode(r['content'][0]['data']).decode();tree=ast.parse(source);defs={};aliases=[];bindings=[]
        for n in tree.body:
            if isinstance(n,ast.FunctionDef):defs.setdefault(n.name,[]).append(n.lineno)
            if isinstance(n,ast.ClassDef):
                for f in n.body:
                    if isinstance(f,ast.FunctionDef):defs.setdefault(n.name+'.'+f.name,[]).append(f.lineno)
            if isinstance(n,ast.Assign) and isinstance(n.value,(ast.Name,ast.Attribute)):
                aliases.append(dict(line=n.lineno,targets=[ast.unparse(t) for t in n.targets],captured=ast.unparse(n.value)))
                if any(isinstance(t,ast.Attribute) for t in n.targets):bindings.append(ast.unparse(n))
        ns={};exec(compile(source,'actual Library','exec'),ns)
        assert ns['FHIRResourceBundleGenerator']._transport is ns['_b7_transport']
        assert ns['FHIRResourceBundleGenerator'].parse_clinical_text_to_fhir_bundle is ns['_b7_entry']
        audit.append(dict(profile_id=r['content'][0]['title'],definitions={k:dict(first=v[0],overrides=v[1:],last=v[-1]) for k,v in defs.items()},captures=aliases,class_bindings=bindings,protocol=ns['B6_CONFIG']))
    dump(D/'active_function_audit.json',audit)
    cases=json.loads((ROOT/'experiment/b7-1/cases.json').read_text(encoding='utf8'));bundles={'B7_2H':json.loads((ROOT/'experiment/b7-2/B7_2H.json').read_text(encoding='utf8')),'B7_3H':b};nss={v:scopes(x) for v,x in bundles.items()};settings={'raw':None};http=[]
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_POST(self):
            p=json.loads(self.rfile.read(int(self.headers['Content-Length'])));http.append(dict(path=self.path,model=p['model'],tokens=p['max_tokens']));self.send_response(200);self.end_headers();self.wfile.write(json.dumps({'choices':[{'message':{'content':json.dumps(settings['raw'])}}]}).encode())
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();endpoint='http://127.0.0.1:'+str(server.server_port)+'/v1/chat/completions';results=[]
    try:
        for v in bundles:
            for c in cases:
                ns=nss[v][c['profile_id']];ns['B6_CONFIG']['endpoint']=endpoint;settings['raw']=c['raw'];g=ns['FHIRResourceBundleGenerator']('http://localhost:3456');out=g.parse_clinical_text_to_fhir_bundle('p1',c['reports']);m=g.model_metrics;base=ns['evaluate_b2'](c['profile_id'],c['reports'],'B2E')['match']
                results.append(dict(variant=v,case=c['case'],profile_id=c['profile_id'],expected=c['expected'],predicted=g.last_result['match'],baseline=base,calls=m['calls'],http=m['http_success'],json=m['json_valid'],source=m['grounded'],fact=sum(f.get('source')=='semantic' for f in g.last_result['facts'].values()),fhir=len(out['entry']),service=replay_service(rowmap[c['profile_id']],out)['hit'],errors=m['errors'],r4=r4_structure(out),fsh=fsh_checks(rowmap[c['profile_id']],out)))
    finally:server.shutdown();server.server_close()
    dump(D/'match_results.json',results);dump(D/'http_summaries.json',http)
    summary={}
    for v in bundles:
        x=[r for r in results if r['variant']==v];summary[v]=dict(metrics=metrics(x),calls=sum(r['calls'] for r in x),http=sum(r['http'] for r in x),json=sum(r['json'] for r in x),source=sum(r['source'] for r in x),fact=sum(r['fact'] for r in x),rescues=sum(r['expected'] and not r['baseline'] and r['service'] for r in x))
    assert summary['B7_3H']==summary['B7_2H'];dump(D/'match_summary.json',summary)
    start=time.perf_counter();isolated=[]
    samples=corpus()
    for row,e in zip(rows,b['entry'][1:]):
        cid=str(row['profile_id']);f=next(f for f in samples if f['profile_id']==cid and f['group']=='clear_positive')
        child=subprocess.run([sys.executable,'-I','-c','import sys;sys.path.insert(0,'+repr(str(ROOT/'work/b6-python-deps'))+');'+CHILD],input=json.dumps(dict(source=e['resource']['content'][0]['data'],reports=f['reports'])),capture_output=True,encoding='utf8',timeout=30)
        assert child.returncode==0,child.stderr
        out=json.loads(child.stdout);assert out['entry'] and replay_service(row,out)['hit'] and not r4_structure(out)
        isolated.append(dict(profile_id=cid,status='PASS',service=True))
    dump(D/'integration.json',dict(seconds=time.perf_counter()-start,libraries=isolated))
    try:publication_gate(b,rows)
    except ValueError as exc:dump(D/'publication_gate.json',dict(status='BLOCKED',error=str(exc)))
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in frozen.items())
    def report(name,text):(ROOT/'reports'/name).write_text(text+'\n',encoding='utf8')
    report('B7_3_UNKNOWN_CONTRACT.md','B7.2 final decoder reproduced ValueError SOURCE:nonempty literal quote for UNKNOWN empty evidence. B7.3 final prompt facts=[]; omit unknown atoms. Strict legacy UNKNOWN empty fact may be omitted only with legal requested atom, no duplicate, closed fields and optional valid integer report. Unknown never upgrades; evidence derived solely from retained uniquely verified fact quotes. PRESENT empty/invented quote rejected; wrong indices, duplicate source and contradictory top evidence still reject. FAST tests cover mixed PRESENT+UNKNOWN, empty facts, Markdown and false overall hint.')
    report('B7_3_ACTIVE_FUNCTION_AUDIT.md','All16 actual Base64 AST inventories: active_function_audit.json. First/override/final lines, class entry bindings and captured historical aliases included for every function. Final prompt/decode B7.3 wrap captured B7.2; _b4_call remains B7.2; _b4_evaluate B5 safety; _b7_transport and _b7_entry B7. Historical alias chains are intentional, not recursion. Global name lookups in captured functions reach final decoder. Executed final bindings verified; full regression catches accidental old calls. Static inventory does not prove arbitrary Python reachability: older unbound transports are unreachable from current entry but retained for rollback. No redundant definition removed.')
    report('B7_3_QWEN_COMPATIBILITY.md','Protocol final bindings verified: HTTP POST1213/v1/chat/completions,local-model,OpenAI-compatible system/user messages,temperature0,max_tokens2048,stopNone.256-token official example is protocol reference, not B fact capacity proof. Pure/Markdown JSON, UNKNOWN/partial positives tested. null/empty/truncation/missing fields reject and fall back; HTTP500/nonexpected status and sockets covered by retained integration tests. Counters SOURCE combines closed-schema+literal grounding (legacy); FACT is separate accepted count. Same158 MOCK stage counts:'+json.dumps(summary)+'\nNo LIVE stage verified. Socket inactivity/request exception returns are not cancellation:2 worker per namespace,32 across16; slots held until Session exits; trickle can persist cross patients. Resource lifecycle is RISK_REMAINING, not PASS.')
    report('B7_3_MATCH_DIFF.md','Exact original158 samples and response objects;60 requests per variant. No outputs/expected labels changed. '+json.dumps(summary)+'\n8 Service rescues and3 former exclusive false-hint rescues remain; no new B7.3 clinical rescue. UNKNOWN-only compatibility improves safe acceptance path; original fixtures lacked that format so call/productive counts unchanged. No claim about real Qwen adherence.')
    sha=hashlib.sha256((D/'B7_3H.json').read_bytes()).hexdigest()
    report('B7_3_PLATFORM_RELEASE_CHECKLIST.md','MANUAL AUTHORIZATION REQUIRED; no submission performed. Candidate experiment/b7-3/B7_3H.json SHA256='+sha+'\nOriginal B workbook identities:'+json.dumps([{k:r[k] for k in ('profile_id','id','index','deepquery_id')} for r in rows])+'\nHeader preserved:'+json.dumps(b['entry'][0])+'\n2/3tbd/null and train_set header remain UNVERIFIED. Never substitute test_b from A test_a example.18historicalFSH conflicts unchanged;full official checker and runtime quota not supplied. Local sanity is not formal checker.\nMinimal plan: first obtain official mapping/header/checker/runtime/thread/log permissions. Prefer organizer sandbox with synthetic inputs if provided. Only after explicit human upload approval perform one reviewed hashed validation artifact; it may consume one official evaluation opportunity, platform accounting unverified. Available Qwen request/error logs currently unknown. Request stage counters without raw clinical text; HTTP success alone insufficient: require parsed JSON, sourced categorical accepted facts, generated resources,Service retrieval; official scoring separately. Overall MATCH/score cannot distinguish rule fallback from model. Without permitted logs report participation UNVERIFIED. On invalid JSON/runtime failure or source false positives retain B2E/B7.2 hashes and roll back; no blind batches/score-formula probes.')
    print(json.dumps(summary),flush=True)
if __name__=='__main__':run()
