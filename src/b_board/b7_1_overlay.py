"""B7.1 source binding and fact-level hints; retains all deterministic vetoes."""
_B71_DECODE = _b4_decode
_B71_PROMPT = _b4_prompt


def _b4_prompt(cid,reports,requested,items=None):
    return json.dumps(dict(profile_id=cid,criterion=QUESTION,requested_atoms=requested,
        instruction='Return only patient facts quoted literally. No numeric/date/event invention. UNKNOWN is allowed. Overall match is a hint; facts must stand independently.',
        output=dict(match=None,facts=[dict(atom=a,state='UNKNOWN',evidence='') for a in requested],
                    subject='patient',negated=False,planned=False,uncertain=False,evidence=[],reason=''),
        records=reports),ensure_ascii=False)


def _b4_decode(raw,cid,reports,requested):
    if isinstance(raw,str):
        raw=raw.strip()
        if raw.startswith('```json\n') and raw.endswith('```'):raw=raw[8:-3].strip()
        raw=json.loads(raw,object_pairs_hook=_b4_unique,parse_constant=_b4_invalid)
    raw=copy.deepcopy(raw)
    if isinstance(raw,dict) and type(raw.get('facts')) is list:
        for fact in raw['facts']:
            if type(fact) is dict and set(fact)=={'atom','state','evidence'}:
                quote=fact['evidence']
                matches=[i for i,r in enumerate(reports) if isinstance(quote,str) and len(quote.strip())>=2 and quote in r.get('text','')]
                if len(matches)!=1:raise ValueError('SOURCE_LOCATION: unique original report required')
                fact['report']=matches[0]
    checked=_B71_DECODE(raw,cid,reports,requested)
    # False/UNKNOWN overall assessment cannot discard independently valid categorical facts.
    # Full criterion, subject, negation and event checks remain in the final merger.
    if any(f['state'] in ACCEPTED and f['atom'] not in B4_PROTECTED and _b4_quote_safe(f,reports) for f in checked['facts']):
        checked['match']=True
    return checked
