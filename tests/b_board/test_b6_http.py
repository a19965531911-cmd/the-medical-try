import base64
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import pytest
from scripts.build_b6 import build
from functools import lru_cache
build=lru_cache(maxsize=None)(build)


@pytest.mark.parametrize('cid',['2','3','85','205','225','255','295','465','475','495','525','585','625','695','715','765'])
@pytest.mark.parametrize('mode',['json','markdown','negative','invalid','500','missing'])
def test_embedded_http(cid,mode):
    seen=[]
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args): pass
        def do_POST(self):
            payload=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            seen.append((self.path,payload))
            value=dict(match=False,facts=[],subject='patient',negated=False,planned=False,uncertain=False,evidence=[],reason='synthetic negative')
            content=json.dumps(value)
            if mode=='markdown':content='```json\n'+content+'\n```'
            if mode=='invalid':content='malicious unrelated output'
            self.send_response(500 if mode=='500' else 200);self.end_headers()
            self.wfile.write(json.dumps({} if mode=='missing' else {'choices':[{'message':{'content':content}}]}).encode())
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        bundle=build('B6H');scope={}
        entry=next(e['resource'] for e in bundle['entry'][1:] if e['resource']['content'][0]['title']==cid)
        exec(base64.b64decode(entry['content'][0]['data']),scope)
        scope['B6_CONFIG']['endpoint']='http://127.0.0.1:'+str(server.server_port)+'/v1/chat/completions'
        g=scope['FHIRResourceBundleGenerator']('http://localhost:3456')
        g.parse_clinical_text_to_fhir_bundle('p1',[{'text':'活动后透不过气'}])
        assert seen and seen[0][0]=='/v1/chat/completions'
        p=seen[0][1];assert p['model']=='local-model' and p['temperature']==0 and p['stop'] is None
        assert len(seen)==1
        assert not g.last_result['match']
    finally:server.shutdown();server.server_close()


def test_positive_grounding_xhtml_and_budget():
    bundle=build('B6H');scope={}
    exec(base64.b64decode(bundle['entry'][1]['resource']['content'][0]['data']),scope)
    g=scope['FHIRResourceBundleGenerator']('http://localhost:3456')
    text='活动后透不过气 <script>alert(1)</script>'
    raw=dict(match=True,facts=[dict(atom='respiratory',state='PRESENT',evidence=text,report=0)],subject='patient',negated=False,planned=False,uncertain=False,evidence=[text],reason='synthetic')
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_POST(self):
            self.rfile.read(int(self.headers['Content-Length']))
            self.send_response(200);self.end_headers()
            self.wfile.write(json.dumps({'choices':[{'message':{'content':json.dumps(raw)}}]}).encode())
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    scope['B6_CONFIG']['endpoint']='http://127.0.0.1:'+str(server.server_port)+'/v1/chat/completions'
    try:
        output=g.parse_clinical_text_to_fhir_bundle('p1',[dict(text=text)])
        assert output['entry'] and '&lt;script&gt;' in output['entry'][0]['resource']['text']['div']
        g.b5_deadline=0
        assert g._transport('synthetic') is None
        assert g.transport_error_kind=='TOTAL_BUDGET_TIMEOUT'
    finally:server.shutdown();server.server_close()
