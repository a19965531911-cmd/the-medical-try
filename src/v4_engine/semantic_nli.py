from .evidence import Evidence, AtomState

ALLOWED={'ENTAILED','CONTRADICTED','UNKNOWN'}
def parse_atom_response(obj, report_index, topic='', timestamp='', source='llm'):
    if not isinstance(obj,dict) or 'match' in obj or not isinstance(obj.get('atoms'),dict): return []
    out=[]
    for atom,data in obj['atoms'].items():
        if not isinstance(data,dict) or data.get('state') not in ALLOWED: continue
        ev=data.get('evidence',[]); ev=ev if isinstance(ev,list) else []
        state=AtomState(data['state'])
        if state!=AtomState.UNKNOWN and (not ev or not all(isinstance(x,str) and len(x.strip())>=2 for x in ev)): continue
        out.append(Evidence(atom,state,ev[0] if ev else '',data.get('value'),report_index,topic,timestamp,'patient','unknown',source))
    return out
