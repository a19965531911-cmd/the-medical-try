"""Append-only B3 runtime guard for the frozen embedded B2E source."""
import time as _b3_time

_B2_SEMANTIC_RESCUE=semantic_rescue


def _b3_unique(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError("Duplicate model JSON key")
        result[key]=value
    return result


def _b3_invalid_constant(value):
    raise ValueError("Nonfinite model JSON constant")


def _b3_checked_facts(raw,cid,reports):
    if isinstance(raw,str):
        raw=raw.strip()
        if raw.startswith("```json\n") and raw.endswith("```"):
            raw=raw[8:-3].strip()
        raw=json.loads(raw,object_pairs_hook=_b3_unique,parse_constant=_b3_invalid_constant)
    if type(raw) is not dict or set(raw)!={"facts"} or type(raw["facts"]) is not dict:
        raise ValueError("Expected closed facts object")
    if not set(raw["facts"]).issubset(REQUIRED[str(cid)]):
        raise ValueError("Unrecognized atom")
    for fact in raw["facts"].values():
        if type(fact) is not dict or set(fact)!={"state","evidence","report"}:
            raise ValueError("Unexpected fact fields")
        if fact["state"] not in {"UNKNOWN","PRESENT","HISTORICAL","NEGATED","ABSENT","PLANNED","UNCERTAIN"}:
            raise ValueError("Invalid fact state")
        index=fact["report"]
        quote=fact["evidence"]
        if type(index) is not int or not 0 <= index < len(reports) or not isinstance(quote,str):
            raise ValueError("Invalid evidence location")
        if fact["state"] in ACCEPTED and (len(quote.strip())<2 or quote not in reports[index].get("text","")):
            raise ValueError("Evidence must occur literally in the original report")
    return raw


def semantic_rescue(cid,reports,result,transport,question):
    proposed=None
    def checked_transport(prompt):
        nonlocal proposed
        try:
            proposed=_b3_checked_facts(transport(prompt),cid,reports)
            return proposed
        except Exception:
            return {"facts":{}}
    rescued=_B2_SEMANTIC_RESCUE(cid,reports,result,checked_transport,question)
    if not rescued["match"] or result["match"] or str(cid) not in EVENT_PROFILES:
        return rescued
    # Reuse a single model response and recompute deterministic facts in each event.
    for key,items in event_groups(reports).items():
        indexes=[i for i,r in items]
        local_reports=[r for i,r in items]
        local_result=evaluate_b2(cid,local_reports,"B2E")
        local_facts={atom:dict(fact,report=indexes.index(fact["report"]))
                     for atom,fact in (proposed or {"facts":{}})["facts"].items()
                     if fact["report"] in indexes}
        local=_B2_SEMANTIC_RESCUE(cid,local_reports,local_result,lambda p:{"facts":local_facts},question)
        if local["match"]:
            local=_restore_indexes(local,indexes)
            local["event_key"]=list(key)
            local["event_reports"]=indexes
            return local
    return result


def _b3_transport(self,prompt):
    started=_b3_time.perf_counter()
    self.transport_error=None
    payload={"model":"local-model","temperature":0,"max_tokens":1024,"messages":[{"role":"user","content":prompt}]}
    try:
        request=Request("http://127.0.0.1:1213/v1/chat/completions",json.dumps(payload,ensure_ascii=False).encode(),{"Content-Type":"application/json"},method="POST")
        with urlopen(request,timeout=30) as response:
            return json.loads(response.read().decode())["choices"][0]["message"]["content"]
    except Exception as exc:
        self.transport_error=type(exc).__name__+": "+str(exc)
        return "NO"
    finally:
        self.transport_seconds=_b3_time.perf_counter()-started


FHIRResourceBundleGenerator._transport=_b3_transport
B3_SELECTED="B2E_WITH_RUNTIME_GUARDS"
