"""B2 overlay: invoke after the frozen B1 definitions when embedding."""
import copy
from datetime import timezone, timedelta

try:
    _B1_EVALUATE = evaluate
    _B1_BUILD = build_b_resources
    _B1_SMOKING = _smoking
except NameError:
    from b_board.runtime import evaluate as _B1_EVALUATE, build_b_resources as _B1_BUILD, _smoking as _B1_SMOKING
    from b_board.runtime import _has, _fact, _labs, REQUIRED, PATTERNS, ACCEPTED, TERMINOLOGY, concept, resource
    from b_board.runtime import re, datetime, json

B2_VARIANTS = ("B1","B2A","B2B","B2C","B2D","B2E")
EVENT_PROFILES = {"3","85","205","465","475","495"}


def event_groups(reports):
    """Explicit event outranks encounter; hospital disambiguates IDs and dates."""
    groups = {}
    explicit = any(r.get("event_id") or r.get("procedure_id") or r.get("encounter_id") for r in reports)
    dates = {str(r.get("timestamp",""))[:10] for r in reports if r.get("timestamp")}
    for i,r in enumerate(reports):
        hospital = r.get("hospital_id","")
        key = r.get("event_id") or r.get("procedure_id") or r.get("encounter_id")
        if key:
            key = (hospital,"explicit",str(key))
        elif explicit:
            # Unlinked records cannot silently join an explicit event.
            key = (hospital,"unlinked",i)
        elif len(dates)>1:
            key = (hospital,"date",str(r.get("timestamp",""))[:10] or str(i))
        else:
            key = (hospital,"implicit","shared")
        groups.setdefault(key,[]).append((i,r))
    return groups


def _restore_indexes(result,indexes):
    result = copy.deepcopy(result)
    seen=set()
    for fact in list(result.get("facts",{}).values())+result.get("evidence",[]):
        if id(fact) in seen:
            continue
        seen.add(id(fact))
        if fact.get("report") is not None:
            fact["report"] = indexes[fact["report"]]
        if isinstance(fact.get("value"),dict) and "labs" in fact["value"]:
            for item in fact["value"]["labs"].values():
                item["report"] = indexes[item["report"]]
    return result


def bound_event_evaluate(cid,reports):
    candidates=[]
    for key,items in event_groups(reports).items():
        indexes=[i for i,r in items]
        result=_B1_EVALUATE(cid,[r for i,r in items])
        result=_restore_indexes(result,indexes)
        result["event_key"]=list(key)
        result["event_reports"]=indexes
        candidates.append(result)
    result=next((r for r in candidates if r["match"]),None)
    if result:
        return result
    result=_B1_EVALUATE(cid,reports)
    if result["match"]:
        result=dict(result,match=False,decision="NO_MATCH",reason="CROSS_EVENT_ATOMS")
        result["facts"]=dict(result["facts"])
        atom=REQUIRED[cid][0]
        result["facts"][atom]=dict(result["facts"][atom],state="UNCERTAIN")
    return result


def _date(value):
    try:
        return datetime.fromisoformat(str(value).replace("Z","+00:00")).date()
    except (ValueError,TypeError):
        return None


def smoking_b2(reports,strategy="SERVICE_GROUNDED"):
    evaluation_dates=[_date(r.get("evaluation_timestamp")) for r in reports]
    evaluation_dates=[d for d in evaluation_dates if d]
    dates=evaluation_dates or [d for r in reports if (d:=_date(r.get("timestamp")))]
    anchor=max(dates) if dates else None
    recent_reports=[]
    for i,r in enumerate(reports):
        observed=_date(r.get("timestamp"))
        if not anchor or not observed or 0 <= (anchor-observed).days <= 90:
            recent_reports.append((i,r))
    numeric_by_report={}
    # Distributed quantity/current context may join only within linked recent records.
    for items in event_groups([r for i,r in recent_reports]).values():
        for fact in _B1_SMOKING([r for i,r in items]):
            if isinstance(fact.get("value"),dict) and "cigarettes_per_day" in fact["value"]:
                original_index=recent_reports[items[fact["report"]][0]][0]
                numeric_by_report[original_index]=fact
    facts=[]
    for i,r in enumerate(reports):
        text=r.get("text","")
        observed=_date(r.get("timestamp"))
        recent=not anchor or not observed or 0 <= (anchor-observed).days <= 90
        if not recent:
            continue
        # B1 OR aggregation is vetoed by quantity<=5 even with an explicit refusal.
        value={}
        numeric=numeric_by_report.get(i)
        quantity_eligible=bool(numeric and numeric["state"] in ACCEPTED)
        if numeric:
            value["cigarettes_per_day"]=numeric["value"]["cigarettes_per_day"]
        refusal=_has(r"不能保证[^。；]{0,15}(?:停止吸烟|戒烟)|cannot guarantee.*stop smoking",text)
        if _has(r"并非不能保证|否认不能保证|不是不能保证|可能|疑似|考虑",text):
            refusal=False
        guarantee=_has(r"(?<!不)能保证[^。；]{0,15}(?:停止吸烟|戒烟)",text)
        if refusal:
            value["guarantee"]="cannot-guarantee"
        elif guarantee:
            value["guarantee"]="can-guarantee"
        if not quantity_eligible and not refusal:
            continue
        if strategy=="PROFILE_COMPLETE" and not {"cigarettes_per_day","guarantee"}.issubset(value):
            continue
        # Observation time documents recent behavior; never call it smoking onset.
        value["observation_date"]=observed.isoformat() if observed else None
        facts.append(_fact("smoking_eligible","PRESENT",text,i,value))
    chosen=next(iter(facts),_fact("smoking_eligible"))
    ok=chosen["state"] in ACCEPTED
    return {"match":ok,"decision":"MATCH" if ok else "NO_MATCH","facts":{"smoking_eligible":chosen},"evidence":facts,"reason":"RECENT_OR_EVIDENCE" if ok else "MISSING_RECENT_OR_EVIDENCE","smoking_strategy":strategy}


def lab_observations(reports):
    """Retain each supported measurement; never manufacture a missing panel member."""
    observations=[]
    aliases={"total_bilirubin":r"TBIL|总胆红素|total bilirubin","alt":r"ALT|丙氨酸氨基转移酶|谷丙转氨酶","ast":r"AST|天冬氨酸氨基转移酶|谷草转氨酶"}
    all_names="|".join(aliases.values())
    for i,r in enumerate(reports):
        text=r.get("text","")
        for lab,alias in aliases.items():
            for m in re.finditer(r"(?<![A-Za-z])(?:"+alias+r")(?![A-Za-z])\s*[:：=]?\s*(\d+(?:\.\d+)?)\s*([^，,。；;\n]*?)(?=(?:"+all_names+r")|$|[，,。；;\n])",text,re.I):
                local=re.split(r"[，,。；;\n]",text[:m.start()])[-1]
                if _has(r"拟|计划|未查|可能|疑似",local):
                    continue
                tail=m[2]
                ratio=_has(r"^\s*(?:倍\s*(?:正常上限|正常范围上限|ULN)|(?:×|x)?\s*ULN)",tail)
                high=re.search(r"(?:ULN|正常上限|正常范围上限|上限)\s*[:：=]?\s*(\d+(?:\.\d+)?)",tail,re.I)
                rr=re.search(r"(?:参考范围|正常范围|参考值)\s*[:：(（]?\s*\d+(?:\.\d+)?\s*[-~～至]\s*(\d+(?:\.\d+)?)",tail)
                uln=float(high[1]) if high else float(rr[1]) if rr else 1.0 if ratio else None
                if uln is None or uln<=0:
                    continue
                unit=re.match(r"\s*([uμµ]?mol/L|U/L|mg/dL)",tail,re.I)
                observations.append({"lab":lab,"value":float(m[1]),"high":uln,"unit":"1" if ratio else unit[1] if unit else None,"report":i,"evidence":m[0]})
    return observations


def labs_b2(reports,strategy="CLINICAL_STRICT"):
    obs=lab_observations(reports)
    groups={}
    for item in obs:
        r=reports[item["report"]]
        key=(r.get("hospital_id",""),"encounter",str(r["encounter_id"])) if r.get("encounter_id") else (r.get("hospital_id",""),"date",str(r.get("timestamp",""))[:10]) if r.get("timestamp") else (r.get("hospital_id",""),"unlinked",item["report"])
        groups.setdefault(key,[]).append(item)
    complete=[]
    for key,items in groups.items():
        panel={}
        for item in items:
            panel.setdefault(item["lab"],[]).append(item)
        valid=set(panel)=={"total_bilirubin","alt","ast"} and all(item["value"]<=item["high"]*(1.5 if item["lab"]=="total_bilirubin" else 3) for item in items)
        if valid:
            complete.append((key,items,panel))
    if strategy=="OFFICIAL_COMPATIBLE":
        # Matches the executable service on ALL observed tests, including partial panels.
        ok=bool(obs) and all(x["value"]>0 and x["value"]<=x["high"]*(1.5 if x["lab"]=="total_bilirubin" else 3) for x in obs)
        selected=obs if ok else []
    else:
        ok=bool(complete)
        selected=complete[0][1] if ok else []
    value={"observations":selected,"labs":{x["lab"]:x for x in selected},"strategy":strategy}
    f=_fact("labs","PRESENT" if ok else "UNKNOWN",json.dumps(selected,ensure_ascii=False),value=value)
    return {"match":ok,"decision":"MATCH" if ok else "NO_MATCH","facts":{"labs":f},"evidence":[f],"reason":strategy,"lab_strategy":strategy}


def evaluate_b2(cid,reports,variant="B2E",lab_strategy=None,smoking_strategy="SERVICE_GROUNDED"):
    cid=str(cid)
    if variant=="B1":
        return _B1_EVALUATE(cid,reports)
    if cid=="625" and variant in ("B2B","B2E"):
        return labs_b2(reports,lab_strategy or ("OFFICIAL_COMPATIBLE" if variant=="B2B" else "CLINICAL_STRICT"))
    if cid=="295" and variant in ("B2C","B2E"):
        return smoking_b2(reports,smoking_strategy)
    if cid in EVENT_PROFILES and (variant=="B2E" or variant=="B2D" and cid in ("85","205")):
        return bound_event_evaluate(cid,reports)
    return _B1_EVALUATE(cid,reports)


def build_b2_resources(cid,patient,reports,result,variant="B2E"):
    cid=str(cid)
    if not result["match"]:
        return []
    if cid=="625" and result.get("lab_strategy"):
        out=[]
        for x in result["facts"]["labs"]["value"]["observations"]:
            r=resource("Observation",cid,patient,"cnwqk625-laboratory-tests-cs",x["lab"])
            q={"value":x["value"]}; h={"value":x["high"]}
            if x["unit"]:
                q.update(unit=x["unit"],system="http://unitsofmeasure.org",code=x["unit"])
                h.update(unit=x["unit"],system="http://unitsofmeasure.org",code=x["unit"])
            r.update(valueQuantity=q,referenceRange=[{"type":concept("http://hl7.org/fhir/referencerange-meaning","normal"),"high":h}])
            original=reports[x["report"]]
            if original.get("timestamp"):
                r["effectiveDateTime"]=original["timestamp"]
            # Do not produce references to encounters that have not been supplied.
            if original.get("encounter_reference"):
                r["encounter"]={"reference":original["encounter_reference"]}
            out.append(r)
        return out
    resources=_B1_BUILD(cid,patient,reports,result)
    if cid=="295" and result.get("smoking_strategy"):
        value=result["facts"]["smoking_eligible"]["value"]
        if resources and value.get("guarantee"):
            resources[0]["component"]=[c for c in resources[0]["component"] if c["code"]["coding"][0]["code"]!="smoking-cessation-guarantee"]
            resources[0]["component"].append({"code":concept("cnwqk295-smokingcs","smoking-cessation-guarantee"),"valueCodeableConcept":concept("cnwqk295-guaranteecs",value["guarantee"])})
    if variant!="B1":
        for r in resources:
            if cid=="85":
                r["category"]=concept("http://terminology.hl7.org/CodeSystem/procedure-category","surgery")
            # condition/observation/procedure basics are already typed in B1.
            if r["resourceType"]=="Procedure" and r.get("status")=="preparation":
                r.pop("performedDateTime",None)
    return resources
