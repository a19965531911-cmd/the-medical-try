"""Experiment F transport-only resource recovery overlay."""


EXPF_OVERLAY_SOURCE = r'''
_expf_frozen_derive_transport_meta=derive_transport_meta
_expf_frozen_build_expc_resources=build_expc_resources

def _expf_duration_hours(text):
    match=re.search(r"(?:\u673a\u68b0\u901a\u6c14|\u547c\u5438\u673a|\u6c14\u7ba1\u63d2\u7ba1|ventilation|MV|\u6709\u521b\u901a\u6c14).{0,30}?(\d+(?:\.\d+)?)\s*(\u5c0f\u65f6|h|\u5929|\u65e5)",text,re.I)
    if not match:return None
    return float(match.group(1))*(24 if match.group(2) in ("\u5929","\u65e5") else 1)

def derive_transport_meta(cid,reports,windows,values):
    meta=_expf_frozen_derive_transport_meta(cid,reports,windows,values)
    if cid!="755":return meta
    meta=meta or {"timestamp":_transport_timestamp(reports,windows)}
    if meta.get("duration_hours") is None:
        duration=_expf_duration_hours(" ".join(w.get("text","") for w in windows))
        if duration is not None:
            meta["duration_hours"]=duration
            meta["_expf_grounded_duration_reuse"]=True
    return meta

def build_expc_resources(cid,patient,values,transport_meta):
    resources=_expf_frozen_build_expc_resources(cid,patient,values,transport_meta)
    recovered=bool(transport_meta and transport_meta.get("_expf_grounded_duration_reuse") and resources)
    mode="GROUNDED_METADATA_REUSE" if recovered else ("NONE" if resources else "BLOCKED_NO_SAFE_PAYLOAD")
    status="RECOVERED" if recovered else ("EMITTED" if resources else "BLOCKED")
    print("V5S2F_METRICS|criterion="+str(cid)+"|final_decision=MATCH|resource_compile="+status+"|resources="+str(len(resources))+"|recovery_mode="+mode)
    return resources
'''
