"""Consistent compact quote contract; source/event binding remains deterministic."""
_B72_DECODE=_b4_decode
_B72_CALL=_b4_call


def _b4_prompt(cid,reports,requested,items=None):
    return json.dumps(dict(profile_id=cid,criterion=QUESTION,requested_atoms=requested,
        instruction='Extract only independently supported patient categorical facts. Every fact has exactly atom,state,evidence. Quote verbatim from ONE unique source record. Do not output report indices, event identities, dates, values or units. Do not invent evidence. Overall match is only a hint; UNKNOWN may return facts=[]. Top evidence must equal unique fact quotes; omit or [] only to let the program derive it after unique literal validation. Family/negated/planned/uncertain evidence cannot become positive.',
        output=dict(match=None,facts=[dict(atom=a,state='UNKNOWN',evidence='') for a in requested],subject='patient',negated=False,planned=False,uncertain=False,evidence=[],reason=''),records=reports),ensure_ascii=False)


def _b4_decode(raw,cid,reports,requested):
    if isinstance(raw,str):
        raw=raw.strip()
        if raw.startswith('```json\n') and raw.endswith('```'):raw=raw[8:-3].strip()
        raw=json.loads(raw,object_pairs_hook=_b4_unique,parse_constant=_b4_invalid)
    raw=copy.deepcopy(raw)
    if type(raw) is not dict or type(raw.get('facts')) is not list:raise ValueError('SCHEMA: facts list required')
    quotes=[]
    for fact in raw['facts']:
        if type(fact) is not dict:raise ValueError('SCHEMA: fact object')
        quote=fact.get('evidence')
        if not isinstance(quote,str) or len(quote.strip())<2:raise ValueError('SOURCE: nonempty literal quote')
        matches=[i for i,r in enumerate(reports) if quote in r.get('text','')]
        if len(matches)!=1:raise ValueError('SOURCE: unique original record required')
        index=matches[0]
        supplied=fact.get('report',fact.get('report_index',index))
        if type(supplied) is not int or supplied!=index:raise ValueError('SOURCE: incorrect supplied index')
        if quote not in quotes:quotes.append(quote)
    top=raw.get('evidence')
    if top is None or top==[]:raw['evidence']=quotes
    elif type(top) is not list or any(not isinstance(q,str) for q in top) or list(dict.fromkeys(top))!=quotes:
        raise ValueError('SOURCE: top/fact evidence disagreement')
    else:raw['evidence']=quotes
    return _B72_DECODE(raw,cid,reports,requested)


def _b4_call(self,cid,reports,requested,items=None):
    eligible=[a for a in requested if a not in B4_PROTECTED]
    if not eligible:
        self.b5_trace.setdefault('unrescuable_call_skips',[]).append(dict(profile_id=cid,atoms=requested,reason='ONLY_DETERMINISTIC_PROTECTED_FACTS'))
        return None
    return _B72_CALL(self,cid,reports,eligible,items)
