"""UNKNOWN means no sourced fact, never an invented positive."""
_B73_DECODE=_b4_decode
_B73_PROMPT=_b4_prompt


def _b4_prompt(cid,reports,requested,items=None):
    prompt=json.loads(_B73_PROMPT(cid,reports,requested,items))
    prompt['output']['facts']=[]
    prompt['instruction']+=' Omit unknown/unsupported atoms completely. facts=[] is a valid UNKNOWN response. Return a fact only with a nonempty unique verbatim quote. Legacy UNKNOWN with empty quote is ignored, never made positive.'
    return json.dumps(prompt,ensure_ascii=False)


def _b4_decode(raw,cid,reports,requested):
    if isinstance(raw,str):
        raw=raw.strip()
        if raw.startswith('```json\n') and raw.endswith('```'):raw=raw[8:-3].strip()
        raw=json.loads(raw,object_pairs_hook=_b4_unique,parse_constant=_b4_invalid)
    raw=copy.deepcopy(raw)
    if type(raw) is not dict or type(raw.get('facts')) is not list:raise ValueError('SCHEMA: facts list required')
    retained=[];seen=set()
    for fact in raw['facts']:
        if type(fact) is not dict:raise ValueError('SCHEMA: fact object required')
        atom=fact.get('atom')
        if not isinstance(atom,str) or atom not in requested or atom not in REQUIRED[cid] or atom in seen:raise ValueError('SCHEMA: invalid/duplicate atom')
        seen.add(atom)
        if fact.get('state')=='UNKNOWN' and fact.get('evidence')=='':
            extended={'atom','state','evidence','report_index','subject','event_identity'}
            if set(fact) not in ({'atom','state','evidence'},{'atom','state','evidence','report'},extended):
                raise ValueError('SCHEMA: closed legacy UNKNOWN fact required')
            if 'report' in fact and (type(fact['report']) is not int or not 0<=fact['report']<len(reports)):
                raise ValueError('SOURCE: invalid legacy index')
            if set(fact)==extended:
                index=fact['report_index']
                if 'profile_id' not in raw or type(index) is not int or not 0<=index<len(reports) or fact['subject']!='patient':raise ValueError('SOURCE: extended UNKNOWN provenance')
                event=reports[index].get('event_id') or reports[index].get('procedure_id') or reports[index].get('encounter_id')
                if fact['event_identity']!=event:raise ValueError('SOURCE: unknown event identity mismatch')
            continue
        retained.append(fact)
    raw['facts']=retained
    # Only the omitted UNKNOWN's empty placeholder is safe to remove from evidence.
    if type(raw.get('evidence')) is list and len(retained)!=len(seen):
        raw['evidence']=[q for q in raw['evidence'] if q!='']
    return _B73_DECODE(raw,cid,reports,requested)
