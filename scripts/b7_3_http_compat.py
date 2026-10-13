"""Final embedded transport compatibility fixtures, all MOCK."""
import base64,json,sys,threading
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'src'))
from scripts.b7_3_experiments import build,D,dump
def run():
    b=build();n={};exec(base64.b64decode(b['entry'][1]['resource']['content'][0]['data']),n)
    q='活动后透不过气';base=dict(match=None,facts=[],subject='patient',negated=False,planned=False,uncertain=False,evidence=[],reason='MOCK')
    unknown=dict(base,facts=[dict(atom='respiratory',state='UNKNOWN',evidence='')]);positive=dict(base,match=False,facts=[dict(atom='respiratory',state='PRESENT',evidence=q)])
    settings={};records=[]
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_POST(self):
            self.rfile.read(int(self.headers['Content-Length']));self.send_response(settings.get('status',200));self.end_headers()
            self.wfile.write(json.dumps(settings['envelope']).encode())
    s=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=s.serve_forever,daemon=True).start();n['B6_CONFIG']['endpoint']='http://127.0.0.1:'+str(s.server_port)+'/v1/chat/completions'
    scenarios=[('UNKNOWN',json.dumps(unknown),False),('empty_facts',json.dumps(base),False),('positive_false_hint',json.dumps(positive),True),('Markdown','```json\n'+json.dumps(unknown)+'\n```',False),('null',None,False),('empty','',False),('truncated',json.dumps(positive)[:-10],False),('missing_fields','{}',False)]
    try:
        for name,content,expected in scenarios:
            settings.update(status=200,envelope={'choices':[{'message':{'content':content}}]});g=n['FHIRResourceBundleGenerator']('http://localhost:3456');out=g.parse_clinical_text_to_fhir_bundle('p1',[dict(text=q)])
            assert bool(out['entry'])==expected
            if name in ('UNKNOWN','empty_facts','Markdown'):assert g.model_metrics['json_valid']==1
            records.append(dict(case=name,expected=expected,actual=bool(out['entry']),metrics=g.model_metrics))
        for status in (429,500,503):
            settings.update(status=status,envelope={'error':'controlled'});g=n['FHIRResourceBundleGenerator']('http://localhost:3456');out=g.parse_clinical_text_to_fhir_bundle('p1',[dict(text=q)]);assert not out['entry'];records.append(dict(case='HTTP'+str(status),actual=False,metrics=g.model_metrics))
    finally:s.shutdown();s.server_close()
    dump(D/'http_compatibility.json',records);print(str(len(records))+' final-embedded HTTP compatibility cases PASS (MOCK)')
if __name__=='__main__':run()
