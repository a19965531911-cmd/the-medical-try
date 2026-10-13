"""B7 bounded worker pool: no per-timeout unbounded daemon creation."""
_B7_TRANSPORT = _b6_transport
_B7_ENTRY = FHIRResourceBundleGenerator.parse_clinical_text_to_fhir_bundle
_B7_SLOTS = _b6_threading.BoundedSemaphore(2)
_B7_POST = _b6_requests.Session.post
_B7_DECODE = _b4_decode


def _b4_decode(raw,cid,reports,requested):
    if isinstance(raw,str):
        raw=raw.strip()
        if raw.startswith('```json\n') and raw.endswith('```'):raw=raw[8:-3].strip()
        raw=json.loads(raw,object_pairs_hook=_b4_unique,parse_constant=_b4_invalid)
    # Extended provenance fields are required together; legacy schema remains compatible.
    if isinstance(raw,dict) and 'profile_id' in raw:
        if set(raw)!={*B4_SCHEMA['required'],'profile_id','criterion'} or raw['profile_id']!=cid or raw['criterion']!=QUESTION:
            raise ValueError('criterion/profile identity mismatch')
        raw=copy.deepcopy(raw);raw.pop('profile_id');raw.pop('criterion')
        for fact in raw.get('facts',[]):
            if type(fact) is not dict or set(fact)!={'atom','state','evidence','report_index','subject','event_identity'}:
                raise ValueError('closed provenance fact required')
            index=fact.pop('report_index')
            if type(index) is not int or not 0<=index<len(reports) or fact.pop('subject')!='patient':
                raise ValueError('report index/subject')
            expected=reports[index].get('event_id') or reports[index].get('procedure_id') or reports[index].get('encounter_id')
            if fact.pop('event_identity')!=expected:raise ValueError('event identity mismatch')
            fact['report']=index
    return _B7_DECODE(raw,cid,reports,requested)


def _b7_transport(self, prompt):
    self.transport_error = None
    self.transport_error_kind = None
    if not _B7_SLOTS.acquire(blocking=False):
        self.transport_error = 'WORKER_LIMIT'
        self.transport_error_kind = 'WORKER_LIMIT'
        return None
    # Hold the slot until the actual network operation ends, not caller timeout.
    payload = dict(model='local-model', temperature=0.0, max_tokens=B6_CONFIG['max_tokens'], stop=None,
        messages=[dict(role='system',content='Return closed JSON facts only. Patient evidence must be literal. UNKNOWN is allowed. Never fabricate values or events.'),dict(role='user',content=prompt)])
    output = _b6_queue.Queue(1)
    remaining = self.b5_deadline-_b4_time.perf_counter()
    if remaining <= 0:
        _B7_SLOTS.release()
        self.transport_error='BUDGET_EXHAUSTED';self.transport_error_kind='TOTAL_BUDGET_TIMEOUT'
        return None
    def worker():
        try:
            with _b6_requests.Session() as session:
                session.trust_env=False
                response=session.post(B6_CONFIG['endpoint'],json=payload,timeout=min(remaining,30))
                response.raise_for_status()
                output.put((True,response.json()['choices'][0]['message']['content']))
        except Exception as exc:output.put((False,type(exc).__name__))
        finally:_B7_SLOTS.release()
    _b6_threading.Thread(target=worker,daemon=True).start()
    try:
        ok,value=output.get(timeout=remaining)
        if not ok:raise ValueError(value)
        self.model_metrics['http_success']+=1
        return value
    except Exception as exc:
        self.transport_error=type(exc).__name__
        self.transport_error_kind='TIMEOUT_OR_RESPONSE_ERROR'
        return None


def _b7_entry(self,*args,**kwargs):
    response=_B7_ENTRY(self,*args,**kwargs)
    m=self.model_metrics
    accepted=sum(f.get('source')=='semantic' for f in self.last_result['facts'].values())
    self.b7_stages=dict(NO_CALL_RULE_DECIDED=not m['calls'],CALL_TRIGGERED=bool(m['calls']),
        HTTP_SUCCESS=bool(m['http_success']),JSON_VALID=bool(m['json_valid']),GROUNDED=bool(m['grounded']),
        FACT_ACCEPTED=accepted,FHIR_EMITTED=bool(response['entry']),FALLBACK=bool(m['errors']))
    return response


FHIRResourceBundleGenerator._transport=_b7_transport
FHIRResourceBundleGenerator.parse_clinical_text_to_fhir_bundle=_b7_entry
