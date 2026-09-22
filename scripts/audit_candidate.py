import json,base64,hashlib,re,os
p='submission/a_test_message_bundle_v5a_transportfix_candidate.json'; d=json.load(open(p,encoding='utf8')); libs=[e['resource'] for e in d['entry'] if e.get('resource',{}).get('resourceType')=='Library']; ok=sem=model=inp=0; internal=[]; external=[]
for x in libs:
 s=base64.b64decode(next(c['data'] for c in x.get('content',[]) if c.get('data'))).decode('utf8')
 try: compile(s,'<lib>','exec'); ok+=1
 except Exception as e: print('ERR',e)
 sem+= '127.0.0.1:1213' in s; model+= 'local-model' in s; inp+= 'input(' in s
 for h in re.findall(r'''["']([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})["']''',s):
  (internal if h.startswith(('v43.','v5.')) else external).append(h)
print({'libs':len(libs),'compile':ok,'semantic':sem,'model':model,'input':inp,'internal':len(internal),'external':len(external),'size':os.path.getsize(p),'sha256':hashlib.sha256(open(p,'rb').read()).hexdigest()})
