"""Build the local V4.3 candidate from the verified V2.4.3 A-test shell."""
from __future__ import annotations

import base64
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT.parent / "CHIP2026_CP2_A_baseline_v2_4_3" / "submission" / "a_test_message_bundle_v2_4_3.json"
OUT = ROOT / "submission" / "a_test_message_bundle_v4_3_candidate.json"


RUNTIME = r'''ENGINE_VERSION="v4.3"
TEMPORAL_POLICY_875="EVER_PRESENT"
import html,json,re,uuid,urllib.request
from datetime import datetime,timezone,timedelta
from enum import Enum

SEMANTIC_CRITERIA={"24","31","37","49"}
SPECS={
 "8":{"expr":("atom","popq_high_grade")},
 "20":{"expr":("any",[("atom","margin_r1"),("atom","path_t_high"),("atom","path_n1"),("gte","gleason",8),("gt","psa",0.1)])},
 "21":{"expr":("any",[("gte","troponin_i",0.06),("gte","troponin_t",0.03)])},
 "22":{"expr":("all",[("atom","ast_normal"),("atom","alt_normal"),("atom","bun_normal"),("atom","creatinine_normal")])},
 "24":{"expr":("all",[("gte","age",50),("atom","herpes_zoster"),("atom","head_facial_site")])},
 "30":{"expr":("all",[("atom","target_disease"),("atom","active_state"),("not","resolved_or_stable")])},
 "31":{"expr":("all",[("atom","surgery"),("atom","postoperative_state"),("atom","invasive_mechanical_ventilation"),("relation","ventilation","postoperative_state","SAME_EVENT")])},
 "32":{"expr":("all",[("gte","ventilation_hours",24),("not","planned_only")])},
 "33":{"expr":("all",[("lt","serum_creatinine",178),("unit","serum_creatinine","umol/l"),("lt","bun",9),("unit","bun","mmol/l"),("atom","alt_normal"),("atom","ast_normal")])},
 "35":{"expr":("all",[("atom","coagulation_abnormality"),("not","coagulation_normal")])},
 "37":{"expr":("any",[("atom","intracranial_hypertension"),("atom","consciousness_impairment")])},
 "39":{"expr":("any",[("atom","current_smoker"),("lt","quit_months",24)])},
 "41":{"expr":("all",[("any",[("atom","severe_diarrhea"),("atom","constipation")]),("not","resolved_symptom")])},
 "46":{"expr":("all",[("lte","surgery_months",6),("not","planned_only")])},
 "49":{"expr":("all",[("atom","irinotecan"),("atom","administered"),("atom","first_use"),("not","planned_only"),("not","previous_multiple_use")])},
 "51":{"expr":("all",[("atom","chemotherapy"),("atom","administered"),("atom","outside_hospital"),("not","planned_only")])},
}
ATOM_SCHEMAS={
 "24":["herpes_zoster","head_facial_site"],"30":["target_disease","active_state","resolved_or_stable"],
 "31":["surgery","postoperative_state","invasive_mechanical_ventilation"],"35":["coagulation_abnormality","coagulation_normal"],
 "37":["intracranial_hypertension","consciousness_impairment"],"41":["severe_diarrhea","constipation","resolved_symptom"],
 "49":["irinotecan","administered","first_use","planned_only","previous_multiple_use"],
 "51":["chemotherapy","administered","outside_hospital","planned_only"]}
COUNTERS={k:0 for k in ("deterministic_atoms","llm_candidates","llm_calls","llm_success","llm_timeout","llm_http_error","llm_invalid_json","llm_transport_error","llm_atoms_entailed","llm_atoms_contradicted","llm_atoms_unknown","llm_schema_reject","llm_grounding_reject","compiler_positive","typed_builder_resources")}

class AtomState(str,Enum):
 ENTAILED="ENTAILED"
 CONTRADICTED="CONTRADICTED"
 UNKNOWN="UNKNOWN"

class Evidence:
 def __init__(self,atom,state,value=None,evidence="",report_index=None,topic="",timestamp="",subject="patient",source="deterministic",event_id=""):
  self.atom=atom;self.state=state;self.value=value;self.evidence=evidence;self.report_index=report_index;self.topic=topic;self.timestamp=timestamp;self.subject=subject;self.source=source;self.event_id=event_id

class EvidenceLedger:
 def __init__(self,patient_id,criterion_id): self.patient_id=str(patient_id);self.criterion_id=str(criterion_id);self.items=[];self.relations=[]
 def add(self,e):
  if e.subject!="patient": return
  key=(e.atom,e.state,json.dumps(e.value,sort_keys=True,ensure_ascii=False,default=str),e.report_index,e.event_id)
  if not any((x.atom,x.state,json.dumps(x.value,sort_keys=True,ensure_ascii=False,default=str),x.report_index,x.event_id)==key for x in self.items): self.items.append(e)
 def add_relation(self,left,right,kind,report_index=None,event_id=""):
  rel=(left,right,kind,report_index,event_id)
  if rel not in self.relations:self.relations.append(rel)
 def merge(self,other):
  for e in other.items:self.add(e)
  for r in other.relations:
   if r not in self.relations:self.relations.append(r)
 def contradicted(self,atom): return any(e.atom==atom and e.state==AtomState.CONTRADICTED for e in self.items)
 def entailed(self,atom): return any(e.atom==atom and e.state==AtomState.ENTAILED for e in self.items) and not self.contradicted(atom)
 def evidence(self,atom): return [e for e in self.items if e.atom==atom and e.state==AtomState.ENTAILED]
 def values(self,atom): return [e.value for e in self.evidence(atom) if e.value is not None]
 def relation(self,left,right,kind): return any(r[0]==left and r[1]==right and r[2]==kind for r in self.relations)

def _number(value):
 if isinstance(value,dict):value=value.get("value")
 try:return float(value)
 except (TypeError,ValueError):return None

class CriterionCompiler:
 def _eval(self,node,ledger):
  op=node[0]
  if op=="atom":return ledger.entailed(node[1])
  if op=="not":return not ledger.entailed(node[1])
  if op=="all":return all(self._eval(x,ledger) for x in node[1])
  if op=="any":return any(self._eval(x,ledger) for x in node[1])
  if op=="relation":return ledger.relation(node[1],node[2],node[3])
  if op=="unit":return any(isinstance(v,dict) and str(v.get("unit","")).lower()==node[2] for v in ledger.values(node[1]))
  vals=[_number(v) for v in ledger.values(node[1])];vals=[v for v in vals if v is not None]
  if op=="gte":return any(v>=node[2] for v in vals)
  if op=="gt":return any(v>node[2] for v in vals)
  if op=="lte":return any(v<=node[2] for v in vals)
  if op=="lt":return any(v<node[2] for v in vals)
  return False
 def compile(self,criterion,ledger):
  spec=SPECS.get(str(criterion));ok=bool(spec and self._eval(spec["expr"],ledger))
  if ok:COUNTERS["compiler_positive"]+=1
  return {"satisfied":ok,"satisfied_atoms":[e.atom for e in ledger.items if e.state==AtomState.ENTAILED],"blocking_atoms":[e.atom for e in ledger.items if e.state==AtomState.CONTRADICTED]}

def normalize(value):return re.sub(r"\s+"," ",html.unescape(str(value or "")).replace("μ","u").replace("µ","u").replace("×","x")).strip()
def clauses(text):return [x.strip() for x in re.split(r"[，。；;!?！？\n]",text) if x.strip()]
def _blocked(clause):return bool(re.search(r"(?:母亲|父亲|家属|家族|其母|其父)",clause))
def _planned(clause):return bool(re.search(r"(?:拟|计划|建议|准备|预计|将行|待行)",clause))
def _negated(clause):return bool(re.search(r"(?:否认|未见|没有|无(?:明显)?|不存在)",clause))
def _add(ledger,atom,value,evidence,index,topic,timestamp,state=AtomState.ENTAILED,event_id=""):
 ledger.add(Evidence(atom,state,value,evidence,index,topic,timestamp,"patient","deterministic",event_id));COUNTERS["deterministic_atoms"]+=1
def _measurements(text,names):
 out=[]
 for name in names:
  for m in re.finditer(r"(?<![A-Za-z])"+re.escape(name)+r"\s*[=:：]?\s*(\d+(?:\.\d+)?)\s*([a-zA-Z/uU^0-9]+)?",text,re.I):out.append((name.lower(),float(m.group(1)),normalize(m.group(2) or ""),m.group(0)))
 return out
def _duration_months(clause):
 matches=list(re.finditer(r"(\d+(?:\.\d+)?)\s*(年|个月|月)",clause));m=matches[-1] if matches else None
 if m:return float(m.group(1))*(12 if m.group(2)=="年" else 1)
 if "半年" in clause:return 6.0
 return None
def _duration_hours(clause):
 m=re.search(r"(\d+(?:\.\d+)?)\s*(小时|h|hr|天|d|分钟|min)",clause,re.I)
 if not m:return None
 return float(m.group(1))*{"天":24,"d":24,"分钟":1/60,"min":1/60}.get(m.group(2).lower(),1)

def extract_deterministic_atoms(text,criterion,report_index=0,topic="",timestamp=""):
 t=normalize(text);c=str(criterion);ledger=EvidenceLedger("runtime",c)
 if not t:return ledger
 for ci,clause in enumerate(clauses(t)):
  event=f"r{report_index}c{ci}"
  if _blocked(clause):continue
  if c=="8":
   m=re.search(r"(?:POP\s*[-－]?\s*Q|盆腔器官脱垂分度).{0,12}(III|IV|3|4)(?:度|级|期)",clause,re.I)
   if m and not _negated(clause):_add(ledger,"popq_high_grade",{"3":"III","4":"IV"}.get(m.group(1).upper(),m.group(1).upper()),clause,report_index,topic,timestamp,event_id=event)
  elif c=="20":
   if re.search(r"\bR1\b",clause,re.I):_add(ledger,"margin_r1","R1",clause,report_index,topic,timestamp,event_id=event)
   m=re.search(r"\bpT(3a|3b|4a|4b|4)\b",clause,re.I)
   if m:_add(ledger,"path_t_high","pT"+m.group(1),clause,report_index,topic,timestamp,event_id=event)
   if re.search(r"(?<![A-Za-z])pN1(?![A-Za-z0-9])",clause,re.I):_add(ledger,"path_n1","pN1",clause,report_index,topic,timestamp,event_id=event)
   for name,value,unit,quote in _measurements(clause,["GS","Gleason","PSA"]):_add(ledger,"gleason" if name!="psa" else "psa",{"value":value,"unit":unit},quote,report_index,topic,timestamp,event_id=event)
  elif c=="21":
   for name,value,unit,quote in (_measurements(clause,["cTnI","cTnT"]) if "术前" in clause else []):
    if unit.lower() in ("ug/l","ng/ml"):_add(ledger,"troponin_i" if name=="ctni" else "troponin_t",{"value":value,"unit":unit},quote,report_index,topic,timestamp,event_id=event)
  elif c=="22":
   for name in ("AST","ALT","BUN","Cr"):
    m=re.search(r"(?<![A-Za-z])"+name+r"\s*[=:：]?\s*(\d+(?:\.\d+)?).{0,20}?(?:参考|正常|上限)[^0-9]{0,5}(?:\d+(?:\.\d+)?\s*[-~至]\s*)?(\d+(?:\.\d+)?)",clause,re.I)
    if m:_add(ledger,{"ast":"ast_normal","alt":"alt_normal","bun":"bun_normal","cr":"creatinine_normal"}[name.lower()],{"value":float(m.group(1)),"upper":float(m.group(2)),"unit":""},m.group(0),report_index,topic,timestamp,AtomState.ENTAILED if float(m.group(1))<=2*float(m.group(2)) else AtomState.CONTRADICTED,event)
  elif c=="24":
   m=re.search(r"(?:年龄|患者|病人)?\s*(\d+(?:\.\d+)?)\s*岁",clause)
   if m:_add(ledger,"age",float(m.group(1)),m.group(0),report_index,topic,timestamp,event_id=event)
   if "带状疱疹" in clause and not _negated(clause):_add(ledger,"herpes_zoster",True,clause,report_index,topic,timestamp,event_id=event)
   if re.search(r"头|面|脸|眼周|耳周|三叉神经",clause):_add(ledger,"head_facial_site",True,clause,report_index,topic,timestamp,event_id=event)
  elif c=="30":
   if _negated(clause):
    _add(ledger,"target_disease",False,clause,report_index,topic,timestamp,AtomState.CONTRADICTED,event);_add(ledger,"active_state",False,clause,report_index,topic,timestamp,AtomState.CONTRADICTED,event);continue
   if re.search(r"甲肝|乙肝|乙型肝炎|艾滋病|HIV|结核|系统性红斑狼疮|结缔组织病",clause,re.I) and not _negated(clause):_add(ledger,"target_disease",True,clause,report_index,topic,timestamp,event_id=event)
   if re.search(r"活动期|活动性|活动阶段|目前活动",clause) and not _negated(clause):_add(ledger,"active_state",True,clause,report_index,topic,timestamp,event_id=event)
   if re.search(r"稳定|治愈|缓解|陈旧",clause):_add(ledger,"resolved_or_stable",True,clause,report_index,topic,timestamp,event_id=event)
  elif c=="31":
   surgery=bool(re.search(r"手术|术后|术毕",clause));post=bool(re.search(r"术后|术毕",clause));vent=bool(re.search(r"(?:有创|气管插管).{0,8}(?:机械通气|呼吸机)|(?:机械通气|呼吸机).{0,8}(?:有创|气管插管)",clause))
   if surgery:_add(ledger,"surgery",True,clause,report_index,topic,timestamp,event_id=event)
   if post:_add(ledger,"postoperative_state",True,clause,report_index,topic,timestamp,event_id=event)
   if vent and not re.search(r"无需|不需要|无创|术前",clause):_add(ledger,"invasive_mechanical_ventilation",True,clause,report_index,topic,timestamp,event_id=event)
   if post and vent:ledger.add_relation("ventilation","postoperative_state","SAME_EVENT",report_index,event)
  elif c=="32" and re.search(r"机械通气|有创通气|呼吸机",clause):
   hours=_duration_hours(clause)
   if hours is not None:_add(ledger,"ventilation_hours",{"value":hours,"unit":"h"},clause,report_index,topic,timestamp,event_id=event)
   if _planned(clause):_add(ledger,"planned_only",True,clause,report_index,topic,timestamp,event_id=event)
  elif c=="33":
   for name,value,unit,quote in _measurements(clause,["Scr","BUN"]):_add(ledger,"serum_creatinine" if name=="scr" else "bun",{"value":value,"unit":unit},quote,report_index,topic,timestamp,event_id=event)
   alt=_measurements(clause,["ALT"]);ast=_measurements(clause,["AST"])
   for name,atom in (("ALT","alt_normal"),("AST","ast_normal")):
    m=re.search(name+r"\s*(\d+(?:\.\d+)?)\s*[A-Za-z/uU]+.{0,12}?上限\s*(\d+(?:\.\d+)?)",clause,re.I)
    if m and float(m.group(1))<=float(m.group(2)):_add(ledger,atom,{"value":float(m.group(1)),"unit":"U/L"},m.group(0),report_index,topic,timestamp,event_id=event)
   if re.search(r"ALT.{0,12}正常|(?:ALT|AST)(?:均|及|、|和)?正常",clause,re.I):_add(ledger,"alt_normal",{"value":alt[-1][1],"unit":alt[-1][2]} if alt else True,clause,report_index,topic,timestamp,event_id=event)
   if re.search(r"AST.{0,12}正常|(?:ALT|AST)(?:均|及|、|和)?正常",clause,re.I):_add(ledger,"ast_normal",{"value":ast[-1][1],"unit":ast[-1][2]} if ast else True,clause,report_index,topic,timestamp,event_id=event)
  elif c=="35":
   if re.search(r"凝血(?:功能)?(?:异常|障碍|紊乱)",clause) and not _negated(clause):_add(ledger,"coagulation_abnormality",True,clause,report_index,topic,timestamp,event_id=event)
   if re.search(r"凝血(?:功能)?(?:正常|未见异常)|(?:未见|无).{0,6}凝血(?:异常|障碍)",clause):_add(ledger,"coagulation_normal",True,clause,report_index,topic,timestamp,event_id=event)
  elif c=="37":
   if _negated(clause):
    _add(ledger,"intracranial_hypertension",False,clause,report_index,topic,timestamp,AtomState.CONTRADICTED,event);_add(ledger,"consciousness_impairment",False,clause,report_index,topic,timestamp,AtomState.CONTRADICTED,event);continue
   if re.search(r"颅内高压|颅内压升高|ICP升高",clause,re.I) and not _negated(clause):_add(ledger,"intracranial_hypertension",True,clause,report_index,topic,timestamp,event_id=event)
   if re.search(r"意识不清|意识模糊|昏迷|嗜睡",clause) and not _negated(clause):_add(ledger,"consciousness_impairment",True,clause,report_index,topic,timestamp,event_id=event)
   if re.search(r"目前.{0,6}(?:意识清楚|神志清醒|神志清楚|清醒)",clause):_add(ledger,"consciousness_impairment",False,clause,report_index,topic,timestamp,AtomState.CONTRADICTED,event)
  elif c=="39":
   if re.search(r"(?:目前|当前|仍|每日|长期)(?:吸烟|抽烟)|(?:吸烟|抽烟)每日",clause) and not _negated(clause):_add(ledger,"current_smoker",True,clause,report_index,topic,timestamp,event_id=event)
   if "戒烟" in clause:
    months=_duration_months(clause)
    if months is not None:_add(ledger,"quit_months",months,clause,report_index,topic,timestamp,event_id=event)
  elif c=="41":
   if re.search(r"(?:严重|重度|剧烈).{0,5}腹泻",clause) and not _negated(clause):_add(ledger,"severe_diarrhea",True,clause,report_index,topic,timestamp,event_id=event)
   if "便秘" in clause and not re.search(r"(?:无|否认|没有).{0,5}便秘",clause):_add(ledger,"constipation",True,clause,report_index,topic,timestamp,event_id=event)
   if re.search(r"已缓解|已恢复|既往",clause):_add(ledger,"resolved_symptom",True,clause,report_index,topic,timestamp,event_id=event)
  elif c=="46" and re.search(r"手术|切除术",clause):
   months=_duration_months(clause)
   if months is not None and not _negated(clause):_add(ledger,"surgery_months",months,clause,report_index,topic,timestamp,event_id=event)
   if _planned(clause):_add(ledger,"planned_only",True,clause,report_index,topic,timestamp,event_id=event)
  elif c=="49" and re.search(r"伊立替康|irinotecan|CPT[- ]?11",clause,re.I):
   _add(ledger,"irinotecan",True,clause,report_index,topic,timestamp,event_id=event)
   if _planned(clause):_add(ledger,"planned_only",True,clause,report_index,topic,timestamp,event_id=event)
   elif re.search(r"使用|应用|给予|采用|接受|完成|化疗|治疗",clause):_add(ledger,"administered",True,clause,report_index,topic,timestamp,event_id=event)
   if re.search(r"首次|第一次|初次|首程|第一周期",clause):_add(ledger,"first_use",True,clause,report_index,topic,timestamp,event_id=event)
   if re.search(r"既往|曾经|多次|已使用|用过",clause):_add(ledger,"previous_multiple_use",True,clause,report_index,topic,timestamp,event_id=event)
  elif c=="51" and "化疗" in clause:
   _add(ledger,"chemotherapy",True,clause,report_index,topic,timestamp,event_id=event)
   if _planned(clause):_add(ledger,"planned_only",True,clause,report_index,topic,timestamp,event_id=event)
   elif re.search(r"接受|行|做过|完成|曾|既往",clause):_add(ledger,"administered",True,clause,report_index,topic,timestamp,event_id=event)
   if re.search(r"外院|当地医院|外地医院",clause):_add(ledger,"outside_hospital",True,clause,report_index,topic,timestamp,event_id=event)
 return ledger

def _semantic_prefilter(text,criterion):
 cues={"24":r"疱疹|皮疹|神经痛|岁","30":r"肝炎|HIV|结核|狼疮|结缔组织|活动","31":r"术|通气|插管|呼吸机","35":r"凝血|PT|APTT|INR","37":r"颅内|意识|神志|昏迷|嗜睡","41":r"腹泻|便秘|排便","49":r"伊立替康|irinotecan|CPT","51":r"化疗|外院|肿瘤治疗"}
 return bool(re.search(cues.get(str(criterion),r"$^"),text,re.I))
def _official_atom_transport(text,criterion,schema):
 prompt={"task":"classify grounded clinical atoms only","criterion":str(criterion),"allowed_atoms":schema,"states":["ENTAILED","CONTRADICTED","UNKNOWN"],"text":text,"output":{"atoms":"object","evidence":"object mapping atom to exact quote"}}
 body=json.dumps({"model":"local-model","temperature":0,"messages":[{"role":"user","content":json.dumps(prompt,ensure_ascii=False)}]},ensure_ascii=False).encode("utf-8")
 request=urllib.request.Request("http://127.0.0.1:1213/v1/chat/completions",data=body,headers={"Content-Type":"application/json"},method="POST")
 with urllib.request.urlopen(request,timeout=1.5) as response:obj=json.loads(response.read().decode("utf-8"))
 content=obj["choices"][0]["message"]["content"]
 return json.loads(content)
def _merge_semantic(ledger,text,criterion,index,topic,timestamp,transport=None):
 schema=ATOM_SCHEMAS[str(criterion)];COUNTERS["llm_candidates"]+=1
 try:
  COUNTERS["llm_calls"]+=1;obj=(transport or _official_atom_transport)(text,str(criterion),schema)
 except Exception as exc:
  name=exc.__class__.__name__.lower()
  if "timeout" in name:COUNTERS["llm_timeout"]+=1
  elif "http" in name:COUNTERS["llm_http_error"]+=1
  elif isinstance(exc,(json.JSONDecodeError,KeyError,TypeError,ValueError)):COUNTERS["llm_invalid_json"]+=1
  else:COUNTERS["llm_transport_error"]+=1
  return
 if not isinstance(obj,dict) or not isinstance(obj.get("atoms"),dict):COUNTERS["llm_schema_reject"]+=1;return
 COUNTERS["llm_success"]+=1
 evidence=obj.get("evidence",{});evidence=evidence if isinstance(evidence,dict) else {}
 for atom in schema:
  raw=obj["atoms"].get(atom,"UNKNOWN");state=str(raw).upper()
  if state not in ("ENTAILED","CONTRADICTED","UNKNOWN"):COUNTERS["llm_schema_reject"]+=1;continue
  COUNTERS["llm_atoms_"+state.lower()]+=1
  if state=="UNKNOWN":continue
  quote=str(evidence.get(atom,"")).strip()
  if not quote or quote not in text or _blocked(quote) or (state=="ENTAILED" and _negated(quote)):COUNTERS["llm_grounding_reject"]+=1;continue
  if atom in ("administered","first_use") and _planned(quote):COUNTERS["llm_grounding_reject"]+=1;continue
  ledger.add(Evidence(atom,AtomState(state),True,quote,index,topic,timestamp,"patient","llm",f"r{index}:llm"))

def evaluate_patient(patient_id,case_reports,criterion,llm_transport=None):
 ledger=EvidenceLedger(patient_id,str(criterion))
 semantic_called=False
 for report_index,report in enumerate(case_reports or []):
  if not isinstance(report,dict):continue
  text=normalize(report.get("text",""));topic=str(report.get("topic","") or "");timestamp=str(report.get("timestamp") or report.get("end_datetime") or "")
  ledger.merge(extract_deterministic_atoms(text,criterion,report_index,topic,timestamp))
  spec=SPECS.get(str(criterion));deterministic_complete=bool(spec and CriterionCompiler()._eval(spec["expr"],ledger))
  if not deterministic_complete and not semantic_called and str(criterion) in SEMANTIC_CRITERIA and _semantic_prefilter(text,criterion):
   _merge_semantic(ledger,text,criterion,report_index,topic,timestamp,llm_transport);semantic_called=True
 return CriterionCompiler().compile(str(criterion),ledger),ledger

def _date(ledger,fallback):
 dates=[e.timestamp for e in ledger.items if e.timestamp]
 return str(dates[-1] if dates else fallback)
def _summary(e):
 if isinstance(e.value,dict):
  value=e.value.get("value");unit=e.value.get("unit","");return (str(value)+((" "+str(unit)) if unit else "")).strip()
 return str(e.value if e.value is not None else e.atom)
def _coding(system,code,display=None):
 out={"system":system,"code":code}
 if display:out["display"]=display
 return out
def _concept(system,code,display=None):
 out={"coding":[_coding(system,code,display)]}
 if display:out["text"]=display
 return out
def _base(kind,patient,profile=None,resource_id=None):
 out={"resourceType":kind,"id":resource_id or str(uuid.uuid4()),"subject":{"reference":"Patient/"+str(patient)}}
 if profile:out["meta"]={"profile":profile if isinstance(profile,list) else [profile]}
 return out
def _quantity(value,unit,code=None):return {"value":value,"unit":unit,"system":"http://unitsofmeasure.org","code":code or unit}
def _obs(patient,profile,code,date):
 out=_base("Observation",patient,profile);out.update({"status":"final","code":code,"effectiveDateTime":date});return out
def _ev(ledger,atom):return ledger.evidence(atom)
def _first(ledger,atom):return _ev(ledger,atom)[0] if _ev(ledger,atom) else None
def _numeric(e):return _number(e.value)
def _unit(e):return str(e.value.get("unit","") if isinstance(e.value,dict) else "")
def _months_before(date,months):
 dt=datetime.fromisoformat(str(date).replace("Z","+00:00"));whole=int(months);idx=dt.year*12+dt.month-1-whole;year,month=divmod(idx,12);month+=1
 days=[31,29 if year%4==0 and (year%100!=0 or year%400==0) else 28,31,30,31,30,31,31,30,31,30,31]
 return (dt.replace(year=year,month=month,day=min(dt.day,days[month-1]))-timedelta(days=(months-whole)*30.4375)).astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z")
def build_typed_resources(patient,ledger,decision,date):
 if not decision.get("satisfied"):return []
 date=_date(ledger,date);resources=[];base="http://localhost:3456/api/terminology/"
 if IDENTIFIER=="51":
  r=_base("Procedure",patient,base+"Profile/cnwqk165-chemotherapy-history");r.update({"status":"completed","code":{"text":"化疗"},"extension":[{"url":base+"StructureDefinition/cnwqk165-treatment-location","valueCode":"external"}]});resources=[r]
 elif IDENTIFIER=="49":
  r=_base("MedicationAdministration",patient,base+"Profile/cnwqk185-chemotherapy-administration");r.update({"status":"completed","medicationCodeableConcept":_concept(base+"CodeSystem/cnwqk185-custom-cs","cnwqk185-drug-irinotecan","伊立替康"),"extension":[{"url":base+"Extension/cnwqk185-application-order","valueCode":"cnwqk185-application-first"}],"effectiveDateTime":date,"dosage":{"text":"首次伊立替康化疗"}});resources=[r]
 elif IDENTIFIER=="21":
  for atom,marker,loinc in (("troponin_i","cTnI","10839-9"),("troponin_t","cTnT","6598-7")):
   for e in _ev(ledger,atom):
    r=_base("Observation",patient,[base+"Profile/cnwqk265-serum-cardiac-troponin-observation",base+"Profile/cnwqk265-preoperative-cardiac-troponin-observation"]);r.update({"status":"final","category":[_concept("http://terminology.hl7.org/CodeSystem/observation-category","laboratory","Laboratory")],"code":{"coding":[_coding(base+"CodeSystem/cnwqk265-cardiac-troponin-tests",marker,marker),_coding("http://loinc.org",loinc,marker)],"text":marker},"effectiveDateTime":date,"valueQuantity":_quantity(_numeric(e),"ug/L"),"extension":[{"url":base+"Extension/cnwqk265-preoperative-extension","valueBoolean":True}]});resources.append(r)
 elif IDENTIFIER=="8":
  e=_first(ledger,"popq_high_grade");grade=str(e.value);r=_base("Observation",patient,base+"Profile/cnwqk485-popq-assessment");r.update({"status":"final","code":_concept(base+"CodeSystem/cnwqk485-observation-cs","popq-grade","POP-Q分度"),"valueCodeableConcept":_concept(base+"CodeSystem/cnwqk485-popq-grade-cs",grade,grade+"度")});resources=[r]
 elif IDENTIFIER=="46":
  e=_first(ledger,"surgery_months");r=_base("Procedure",patient,base+"Profile/cnwqk555-SurgeryHistoryProfile");r.update({"status":"completed","code":_concept(base+"CodeSystem/cnwqk555-SurgeryProcedureCS","surgery","手术"),"performedDateTime":_months_before(date,_numeric(e))});resources=[r]
 elif IDENTIFIER=="41":
  atom="severe_diarrhea" if _ev(ledger,"severe_diarrhea") else "constipation";code="diarrhea" if atom=="severe_diarrhea" else "constipation";r=_base("Observation",patient,base+"Profile/cnwqk565-symptomobservation");r.update({"status":"final","code":_concept(base+"CodeSystem/cnwqk565-symptomtype-cs",code,code),"extension":[{"url":base+"Extension/cnwqk565-observation-severity-ext","valueCodeableConcept":_concept(base+"CodeSystem/cnwqk565-symptomseverity-cs","severe","severe")}]});resources=[r]
 elif IDENTIFIER=="20":
  system=base+"CodeSystem/cnwqk615-observation-codes-cs"
  for atom,profile,code,vs in (("path_t_high","pathological-t-stage-observation","pathological-t-stage","tnm-pathological-t-stage-cs"),("margin_r1","resection-margin-status-observation","resection-margin-status","resection-margin-status-cs"),("path_n1","pathological-n-stage-observation","pathological-n-stage","tnm-pathological-n-stage-cs")):
   for e in _ev(ledger,atom):
    value=str(e.value);value="pT4" if atom=="path_t_high" and value.lower().startswith("pt4") else value;r=_obs(patient,base+"Profile/cnwqk615-"+profile,_concept(system,code,code),date);r["valueCodeableConcept"]=_concept(base+"CodeSystem/cnwqk615-"+vs,value,value);resources.append(r)
  for atom,profile,code in (("gleason","gleason-score-observation","gleason-score"),("psa","psa-observation","2857-1")):
   for e in _ev(ledger,atom):
    r=_obs(patient,base+"Profile/cnwqk615-"+profile,_concept("http://loinc.org" if atom=="psa" else system,code,code),date);r["valueQuantity"]={"value":_numeric(e)} if atom=="gleason" else _quantity(_numeric(e),"ng/mL");resources.append(r)
 elif IDENTIFIER=="22":
  for atom,name,unit in (("ast_normal","AST","U/L"),("alt_normal","ALT","U/L"),("bun_normal","BUN","mmol/L"),("creatinine_normal","Cr","umol/L")):
   for e in _ev(ledger,atom):
    r=_obs(patient,base+"Profile/cnwqk635-LaboratoryExaminationProfile",_concept(base+"CodeSystem/cnwqk635-LaboratoryTestsCS",name,name),date);r["valueQuantity"]=_quantity(e.value["value"],unit);r["referenceRange"]=[{"high":_quantity(e.value["upper"],unit)}];resources.append(r)
 elif IDENTIFIER=="24":
  site_e=_first(ledger,"head_facial_site");q=site_e.evidence if site_e else "";site="head_and_face" if "头面" in q else ("face" if re.search(r"面|脸",q) else "head");r=_base("Condition",patient,base+"Profile/cnwqk675-head-facial-herpes-zoster-condition");r.update({"clinicalStatus":_concept("http://terminology.hl7.org/CodeSystem/condition-clinical","active","活跃"),"verificationStatus":_concept("http://terminology.hl7.org/CodeSystem/condition-ver-status","confirmed","已确认"),"code":_concept(base+"CodeSystem/icd10","B02.9","带状疱疹"),"bodySite":[_concept(base+"CodeSystem/cnwqk675-head-facial-body-site-cs",site,site)]});resources=[r]
 elif IDENTIFIER=="30":
  r=_base("Condition",patient,base+"StructureDefinition/cnwqk735-nonneoplasm-disease-stage");r.update({"clinicalStatus":_concept("http://terminology.hl7.org/CodeSystem/condition-clinical","active","active"),"code":_concept(base+"CodeSystem/icd10","saB16","活动性疾病")});resources=[r]
 elif IDENTIFIER=="31":
  surgery=_base("Procedure",patient,None,"postoperative-surgery");surgery.update({"status":"completed","code":{"text":"手术"},"performedDateTime":date});vent=_base("Procedure",patient,base+"Profile/cnwqk745-postop-mechanical-ventilation");vent.update({"status":"completed","code":_concept(base+"CodeSystem/cnwqk745-procedure-type-cs","invasive_mechanical_ventilation","有创机械通气"),"performedDateTime":date,"partOf":[{"reference":"Procedure/postoperative-surgery"}]});resources=[surgery,vent]
 elif IDENTIFIER=="32":
  e=_first(ledger,"ventilation_hours");hours=_numeric(e);end=datetime.fromisoformat(date.replace("Z","+00:00"));start=(end-timedelta(hours=hours)).astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z");r=_base("Procedure",patient,base+"Profile/cnwqk755-MechanicalVentilationProcedure");r.update({"status":"completed","code":_concept(base+"CodeSystem/cnwqk755-MechanicalVentilationCodes","mechanical-ventilation","mechanical ventilation"),"performedPeriod":{"start":start,"end":end.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z")}});resources=[r]
 elif IDENTIFIER=="39":
  if _ev(ledger,"current_smoker"):
   r=_obs(patient,base+"Profile/cnwqk805-SmokingStatusObservation",_concept("http://loinc.org","72166-2","Smoking status"),date);r["valueCodeableConcept"]=_concept(base+"CodeSystem/cnwqk805-SmokingStatusCS","current-smoker","current-smoker");resources.append(r)
  for e in _ev(ledger,"quit_months"):
   r=_obs(patient,base+"Profile/cnwqk805-SmokingStatusObservation",_concept("http://loinc.org","72166-2","Smoking status"),date);r["valueCodeableConcept"]=_concept(base+"CodeSystem/cnwqk805-SmokingStatusCS","former-smoker","former-smoker");resources.append(r);q=_obs(patient,base+"Profile/cnwqk805-SmokingCessationDurationObservation",_concept("http://loinc.org","63586-4","Smoking cessation duration"),date);q["valueQuantity"]=_quantity(_numeric(e)/12,"年","a");resources.append(q)
 elif IDENTIFIER=="35":
  r=_base("Observation",patient,base+"Profile/cnwqk835-OrganOrTissueStatus");r.update({"status":"final","code":_concept(base+"CodeSystem/cnwqk835-CoagulationTestCS","coagulation_function","coagulation_function"),"valueCodeableConcept":_concept(base+"CodeSystem/cnwqk835-AbnormalityStatusCS","abnormal","abnormal")});resources=[r]
 elif IDENTIFIER=="33":
  for atom,profile,code,unit in (("serum_creatinine","serum-creatinine-observation","2160-0","umol/L"),("bun","blood-urea-nitrogen-observation","3094-0","mmol/L"),("alt_normal","alanine-aminotransferase-observation","1742-6","U/L"),("ast_normal","aspartate-aminotransferase-observation","1920-8","U/L")):
   for e in _ev(ledger,atom):
    value=_numeric(e)
    if value is None:continue
    r=_obs(patient,base+"Profile/cnwqk855-"+profile,_concept("http://loinc.org",code,atom),date);r["valueQuantity"]=_quantity(value,unit);resources.append(r)
 elif IDENTIFIER=="37":
  presence=base+"CodeSystem/cnwqk875-presence-cs"
  for atom,profile,system,code in (("intracranial_hypertension","intracranialhypertension-profile","intracranialhypertension-cs","intracranial-hypertension"),("consciousness_impairment","unconsciousness-profile","unconsciousness-cs","unconsciousness")):
   if _ev(ledger,atom):
    r=_obs(patient,base+"Profile/cnwqk875-"+profile,_concept(base+"CodeSystem/cnwqk875-"+system,code,code),date);r["valueCodeableConcept"]=_concept(presence,"present","present");resources.append(r)
 COUNTERS["typed_builder_resources"]+=len(resources);return resources

class FHIRResourceBundleGenerator:
 profile_id=PROFILE
 identifier=IDENTIFIER
 def __init__(self,fhir_api_base):self.fhir_api_base=fhir_api_base
 def parse_clinical_text_to_fhir_bundle(self,patient_id,case_reports,ai_algorithm_type="nlp"):
  before=dict(COUNTERS)
  decision,ledger=evaluate_patient(patient_id,case_reports,IDENTIFIER)
  fallback=datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
  resources=build_typed_resources(patient_id,ledger,decision,fallback)
  delta={k:COUNTERS[k]-before.get(k,0) for k in COUNTERS}
  atoms=delta["llm_atoms_entailed"]+delta["llm_atoms_contradicted"]+delta["llm_atoms_unknown"]
  print("V43_PROD_METRICS|title="+str(TITLE)+"|policy875="+TEMPORAL_POLICY_875+"|calls="+str(delta["llm_calls"])+"|decision="+str(bool(decision.get("satisfied")))+"|resources="+str(delta["typed_builder_resources"]))
  return {"resourceType":"Bundle","type":"transaction","entry":[{"resource":r,"request":{"method":"POST","url":r["resourceType"]}} for r in resources]}
'''


def constants(source: str) -> str:
    lines = source.splitlines()
    selected = [line for line in lines if line.startswith(("PROFILE=", "IDENTIFIER=", "RESOURCE_TYPE="))]
    if len(selected) != 3:
        raise ValueError("library constants missing")
    return "\n".join(selected) + "\n"


def main() -> None:
    bundle = json.loads(INPUT.read_text(encoding="utf8"))
    transformed = []
    count = 0
    for entry in bundle["entry"]:
        resource = json.loads(json.dumps(entry["resource"]))
        if resource.get("resourceType") == "Library":
            old = base64.b64decode(resource["content"][0]["data"]).decode("utf8")
            title = resource.get("content", [{}])[0].get("title") or resource.get("name") or resource.get("id")
            source = constants(old) + "TITLE=" + repr(str(title)) + "\n" + RUNTIME
            compile(source, resource["name"], "exec")
            resource["content"][0]["data"] = base64.b64encode(source.encode("utf8")).decode("ascii")
            count += 1
        transformed.append({**entry, "resource": resource})
    if count != 16:
        raise ValueError(f"expected 16 Libraries, got {count}")
    output = {**bundle, "entry": transformed}
    payload = json.dumps(output, ensure_ascii=False, indent=2).encode("utf8")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(payload)
    print(OUT)


if __name__ == "__main__":
    main()
