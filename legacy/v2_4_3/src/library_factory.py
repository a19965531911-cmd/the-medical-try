import json

PROFILES = {
 '51':'cnwqk165-chemotherapy-history','49':'cnwqk185-chemotherapy-administration','21':'cnwqk265-preoperative-cardiac-troponin-observation','8':'cnwqk485-popq-assessment',
 '46':'cnwqk555-SurgeryHistoryProfile','41':'cnwqk565-symptomobservation','20':'cnwqk615-pathological-t-stage-observation','22':'cnwqk635-LaboratoryExaminationProfile',
 '24':'cnwqk675headfacialherpeszostercondition','30':'cnwqk735_nonneoplasmdiseasestage','31':'cnwqk745postopmechanicalventilation','32':'cnwqk755mechanicalventilationprocedure',
 '39':'smokingstatusobservation','35':'cnwqk835-OrganOrTissueStatus','33':'cnwqk855serumcreatinineobservation','37':'cnwqk875-intracranialhypertension-profile'}

RESOURCE = {'51':'Procedure','49':'MedicationAdministration','21':'Observation','8':'Observation','46':'Procedure','41':'Observation','20':'Observation','22':'Observation','24':'Condition','30':'Condition','31':'Procedure','32':'Procedure','39':'Observation','35':'Observation','33':'Observation','37':'Observation'}

RULES = {
'51': "return bool(re.search(r'(?:外院|当地医院|外地医院).{0,18}(?:接受|行|做过|完成).{0,8}化疗|(?:曾|既往).{0,18}(?:外院|当地医院).{0,12}化疗',t)) and not planned(t,'化疗') and not negated(t,'化疗')",
'49': "return bool(re.search(r'(?:首次|第一次|初次).{0,16}(?:伊立替康|含伊立替康).{0,12}(?:化疗|方案|治疗)|(?:首次|第一次|初次).{0,10}(?:化疗|方案).{0,12}伊立替康',t)) and not bool(re.search(r'(?:既往|曾经|已).{0,10}(?:使用|应用|用过).{0,6}伊立替康',t))",
'21': "vals=measurements(t,['cTnI','cTnT']); return any(n=='ctni' and v>=.06 and unit_ok(u,['ug/l','ng/ml']) for n,v,u in vals) or any(n=='ctnt' and v>=.03 and unit_ok(u,['ug/l','ng/ml']) for n,v,u in vals)",
'8': "return bool(re.search(r'(?:POP\\s*[-－]?\\s*Q|盆腔器官脱垂分度).{0,12}(?:III|IV|3|4)(?:度|级|期)',t,re.I)) and not negated(t,'盆腔器官脱垂')",
'46': "m=event_months(t,'手术'); return m is not None and m<=6 and not negated(t,'手术') and not planned(t,'手术')",
'41': "return ((bool(re.search(r'(?:严重|重度|剧烈).{0,5}腹泻',t)) and not negated(t,'腹泻')) or ('便秘' in t and not negated(t,'便秘'))) and not bool(re.search(r'已缓解|已恢复|既往',t))",
'20': "return bool(re.search(r'\\bpT(?:3a|3b|4(?:a|b)?)\\b|\\bR1\\b|\\bpN1\\b',t,re.I)) or any(v>=8 for _,v,_ in measurements(t,['GS','Gleason'])) or any(v>.1 and unit_ok(u,['ng/ml']) for _,v,u in measurements(t,['PSA']))",
'22': "labs=with_upper_limits(t,['AST','ALT','BUN','Cr']); return len(labs)==4 and all(v<=hi for _,v,hi in labs)",
'24': "age=patient_age(t); return age is not None and age>=50 and bool(re.search(r'(?:头|面|脸|眼周|耳周|三叉神经).{0,10}带状疱疹|带状疱疹.{0,10}(?:头|面|脸|眼周|耳周|三叉神经)',t)) and not family_context(t) and not negated(t,'带状疱疹')",
'30': "d=r'(?:甲肝|乙肝|乙型肝炎|艾滋病|HIV|结核|系统性红斑狼疮|结缔组织病)'; return any((re.search(d+r'.{0,8}(?:活动|活动性)',c,re.I) or re.search(r'(?:活动|活动性).{0,8}'+d,c,re.I)) and not negated(c,'活动') and not re.search(r'稳定|缓解|治愈|陈旧',c) for c in clauses(t))",
'31': "return any(bool(re.search(r'术后.{0,15}(?:需|需要|予|给予).{0,10}(?:有创|气管插管).{0,8}(?:机械通气|呼吸机)',c)) and not re.search(r'无需|不需要|无创|术前',c) for c in clauses(t))",
'32': "h=ventilation_hours(t); return h is not None and h>=24 and not planned(t,'机械通气') and not negated(t,'机械通气')",
'39': "q=quit_months(t); return (q is not None and q<24) or (q is None and bool(re.search(r'(?:目前|当前|仍|每日|长期)(?:吸烟|抽烟)|(?:吸烟|抽烟)每日',t)) and not negated(t,'吸烟') and not re.search(r'从不吸烟|家属|吸烟史不详',t))",
'35': "return bool(re.search(r'凝血(?:功能)?(?:异常|障碍)',t)) and not bool(re.search(r'凝血(?:功能)?(?:正常|未见异常)',t) or re.search(r'(?:未见|无).{0,6}凝血(?:异常|障碍)',t))",
'33': "scr=measurements(t,['Scr']); bun=measurements(t,['BUN']); liver=bool(re.search(r'(?:ALT|AST)(?:均|及|、|和)?(?:正常|无明显升高)|ALT.{0,12}正常.{0,12}AST.{0,12}正常|AST.{0,12}正常.{0,12}ALT.{0,12}正常',t,re.I)); return bool(scr and bun and scr[-1][1]<178 and unit_ok(scr[-1][2],['umol/l']) and bun[-1][1]<9 and unit_ok(bun[-1][2],['mmol/l']) and liver)",
'37': "return not bool(re.search(r'目前.{0,4}(?:意识清楚|神志清醒|清醒)',t)) and any((bool(re.search(r'颅内高压|颅内压升高|ICP升高|意识不清|意识模糊|昏迷|嗜睡',c,re.I)) and not re.search(r'意识清楚|神志清醒',c) and not negated(c,'颅内') and not negated(c,'意识')) for c in clauses(t))"
}

FHIR_BUILDERS = {
'51': r'''def build_resources(patient,text,date):
 r=base_resource('Procedure',patient,'http://localhost:3456/api/terminology/Profile/cnwqk165-chemotherapy-history')
 r.update({'status':'completed','code':{'text':'化疗'},'extension':[{'url':'http://localhost:3456/api/terminology/StructureDefinition/cnwqk165-treatment-location','valueCode':'external'}]})
 return [r]''',
'49': r'''def build_resources(patient,text,date):
 r=base_resource('MedicationAdministration',patient,'http://localhost:3456/api/terminology/Profile/cnwqk185-chemotherapy-administration')
 r.update({'status':'completed','medicationCodeableConcept':concept('http://localhost:3456/api/terminology/CodeSystem/cnwqk185-custom-cs','cnwqk185-drug-irinotecan','伊立替康'),'extension':[{'url':'http://localhost:3456/api/terminology/Extension/cnwqk185-application-order','valueCode':'cnwqk185-application-first'}],'effectiveDateTime':date,'dosage':{'text':'首次伊立替康化疗'}})
 return [r]''',
'21': r'''def build_resources(patient,text,date):
 out=[]
 for name,value,unit in measurements(text,['cTnI','cTnT']):
  if not unit_ok(unit,['ug/l','ng/ml']):continue
  marker='cTnI' if name=='ctni' else 'cTnT'; threshold=.06 if marker=='cTnI' else .03
  if value<threshold:continue
  loinc='10839-9' if marker=='cTnI' else '6598-7'
  r=base_resource('Observation',patient,['http://localhost:3456/api/terminology/Profile/cnwqk265-serum-cardiac-troponin-observation','http://localhost:3456/api/terminology/Profile/cnwqk265-preoperative-cardiac-troponin-observation'])
  r.update({'status':'final','category':[concept('http://terminology.hl7.org/CodeSystem/observation-category','laboratory','Laboratory')],'code':{'coding':[coding('http://localhost:3456/api/terminology/CodeSystem/cnwqk265-cardiac-troponin-tests',marker,marker),coding('http://loinc.org',loinc,marker)],'text':marker},'effectiveDateTime':date,'valueQuantity':quantity(value,'ug/L','ug/L'),'extension':[{'url':'http://localhost:3456/api/terminology/Extension/cnwqk265-preoperative-extension','valueBoolean':True}]})
  out.append(r)
 return out''',
'8': r'''def build_resources(patient,text,date):
 m=re.search(r'(?:POP\s*[-－]?\s*Q|盆腔器官脱垂分度).{0,12}(III|IV|3|4)',text,re.I); grade={'3':'III','4':'IV'}.get(m.group(1).upper(),m.group(1).upper())
 r=base_resource('Observation',patient,'http://localhost:3456/api/terminology/Profile/cnwqk485-popq-assessment')
 r.update({'status':'final','code':concept('http://localhost:3456/api/terminology/CodeSystem/cnwqk485-observation-cs','popq-grade','POP-Q分度'),'valueCodeableConcept':concept('http://localhost:3456/api/terminology/CodeSystem/cnwqk485-popq-grade-cs',grade,grade+'度')})
 return [r]''',
'46': r'''def build_resources(patient,text,date):
 r=base_resource('Procedure',patient,'http://localhost:3456/api/terminology/Profile/cnwqk555-SurgeryHistoryProfile')
 r.update({'status':'completed','code':concept('http://localhost:3456/api/terminology/CodeSystem/cnwqk555-SurgeryProcedureCS','surgery','手术'),'performedDateTime':months_before(date,event_months(text,'手术'))})
 return [r]''',
'41': r'''def build_resources(patient,text,date):
 symptom='constipation' if '便秘' in text and not negated(text,'便秘') else 'diarrhea'; display='便秘' if symptom=='constipation' else '腹泻'
 r=base_resource('Observation',patient,'http://localhost:3456/api/terminology/Profile/cnwqk565-symptomobservation')
 r.update({'status':'final','code':concept('http://localhost:3456/api/terminology/CodeSystem/cnwqk565-symptomtype-cs',symptom,display),'extension':[{'url':'http://localhost:3456/api/terminology/Extension/cnwqk565-observation-severity-ext','valueCodeableConcept':concept('http://localhost:3456/api/terminology/CodeSystem/cnwqk565-symptomseverity-cs','severe','重度')}]})
 return [r]''',
'20': r'''def build_resources(patient,text,date):
 out=[]; obs_system='http://localhost:3456/api/terminology/CodeSystem/cnwqk615-observation-codes-cs'
 m=re.search(r'\bpT(3a|3b|4(?:a|b)?)\b',text,re.I)
 if m:
  value='pT'+m.group(1); value='pT4' if value.lower().startswith('pt4') else value
  out.append(coded_observation(patient,'http://localhost:3456/api/terminology/Profile/cnwqk615-pathological-t-stage-observation',obs_system,'pathological-t-stage','http://localhost:3456/api/terminology/CodeSystem/cnwqk615-tnm-pathological-t-stage-cs',value,date))
 if re.search(r'\bR1\b',text,re.I):out.append(coded_observation(patient,'http://localhost:3456/api/terminology/Profile/cnwqk615-resection-margin-status-observation',obs_system,'resection-margin-status','http://localhost:3456/api/terminology/CodeSystem/cnwqk615-resection-margin-status-cs','R1',date))
 if re.search(r'\bpN1\b',text,re.I):out.append(coded_observation(patient,'http://localhost:3456/api/terminology/Profile/cnwqk615-pathological-n-stage-observation',obs_system,'pathological-n-stage','http://localhost:3456/api/terminology/CodeSystem/cnwqk615-tnm-pathological-n-stage-cs','pN1',date))
 for _,value,_ in measurements(text,['GS','Gleason']):
  if value>=8:
   r=observation(patient,'http://localhost:3456/api/terminology/Profile/cnwqk615-gleason-score-observation',concept(obs_system,'gleason-score','Gleason评分'),date); r['valueQuantity']={'value':value}; out.append(r)
 for _,value,unit in measurements(text,['PSA']):
  if value>.1 and unit_ok(unit,['ng/ml']):
   r=observation(patient,'http://localhost:3456/api/terminology/Profile/cnwqk615-psa-observation',concept('http://loinc.org','2857-1','PSA'),date); r['valueQuantity']=quantity(value,'ng/mL','ng/mL'); out.append(r)
 return out''',
'22': r'''def build_resources(patient,text,date):
 out=[]; units={'AST':('U/L','U/L'),'ALT':('U/L','U/L'),'BUN':('mmol/L','mmol/L'),'Cr':('umol/L','umol/L')}; system='http://localhost:3456/api/terminology/CodeSystem/cnwqk635-LaboratoryTestsCS'
 for name,value,high in with_upper_limits(text,['AST','ALT','BUN','Cr']):
  unit,ucum=units[name]; r=observation(patient,'http://localhost:3456/api/terminology/Profile/cnwqk635-LaboratoryExaminationProfile',concept(system,name,name),date)
  r['valueQuantity']=quantity(value,unit,ucum); r['referenceRange']=[{'high':quantity(high,unit,ucum)}]; out.append(r)
 return out''',
'24': r'''def build_resources(patient,text,date):
 site='head_and_face' if re.search(r'头面',text) else ('face' if re.search(r'面|脸',text) else 'head')
 r=base_resource('Condition',patient,'http://localhost:3456/api/terminology/Profile/cnwqk675-head-facial-herpes-zoster-condition')
 r.update({'clinicalStatus':concept('http://terminology.hl7.org/CodeSystem/condition-clinical','active','活跃'),'verificationStatus':concept('http://terminology.hl7.org/CodeSystem/condition-ver-status','confirmed','已确认'),'code':concept('http://localhost:3456/api/terminology/CodeSystem/icd10','B02.9','带状疱疹'),'bodySite':[concept('http://localhost:3456/api/terminology/CodeSystem/cnwqk675-head-facial-body-site-cs',site,site)]})
 return [r]''',
'30': r'''def build_resources(patient,text,date):
 choices=[('乙型肝炎','saB16'),('乙肝','saB16'),('甲肝','saB15'),('HIV','saB20'),('艾滋病','saB20'),('结核','saA15'),('系统性红斑狼疮','saM32'),('结缔组织病','saM35')]; label,code=next(((label,code) for label,code in choices if label.lower() in text.lower()),('非肿瘤疾病',''))
 r=base_resource('Condition',patient,'http://localhost:3456/api/terminology/StructureDefinition/cnwqk735-nonneoplasm-disease-stage')
 r.update({'clinicalStatus':concept('http://terminology.hl7.org/CodeSystem/condition-clinical','active','活动期'),'code':concept('http://localhost:3456/api/terminology/CodeSystem/icd10',code,label)})
 return [r]''',
'31': r'''def build_resources(patient,text,date):
 surgery=base_resource('Procedure',patient,None,'postoperative-surgery'); surgery.update({'status':'completed','code':{'text':'手术'},'performedDateTime':date})
 r=base_resource('Procedure',patient,'http://localhost:3456/api/terminology/Profile/cnwqk745-postop-mechanical-ventilation')
 r.update({'status':'completed','code':concept('http://localhost:3456/api/terminology/CodeSystem/cnwqk745-procedure-type-cs','invasive_mechanical_ventilation','有创机械通气'),'performedDateTime':date,'partOf':[{'reference':'Procedure/postoperative-surgery'}]})
 return [surgery,r]''',
'32': r'''def build_resources(patient,text,date):
 hours=ventilation_hours(text); r=base_resource('Procedure',patient,'http://localhost:3456/api/terminology/Profile/cnwqk755-MechanicalVentilationProcedure')
 r.update({'status':'completed','code':concept('http://localhost:3456/api/terminology/CodeSystem/cnwqk755-MechanicalVentilationCodes','mechanical-ventilation','机械通气'),'performedPeriod':{'start':hours_before(date,hours),'end':canonical_datetime(date)}})
 return [r]''',
'39': r'''def build_resources(patient,text,date):
 out=[]; q=quit_months(text); status='former-smoker' if q is not None else 'current-smoker'
 r=observation(patient,'http://localhost:3456/api/terminology/Profile/cnwqk805-SmokingStatusObservation',concept('http://loinc.org','72166-2','吸烟状态'),date); r['valueCodeableConcept']=concept('http://localhost:3456/api/terminology/CodeSystem/cnwqk805-SmokingStatusCS',status,'既往吸烟' if q is not None else '当前吸烟'); out.append(r)
 if q is not None:
  r=observation(patient,'http://localhost:3456/api/terminology/Profile/cnwqk805-SmokingCessationDurationObservation',concept('http://loinc.org','63586-4','戒烟持续时间'),date); r['valueQuantity']=quantity(q/12,'年','a'); out.append(r)
 return out''',
'35': r'''def build_resources(patient,text,date):
 r=observation(patient,'http://localhost:3456/api/terminology/Profile/cnwqk835-OrganOrTissueStatus',concept('http://localhost:3456/api/terminology/CodeSystem/cnwqk835-CoagulationTestCS','coagulation_function','凝血功能'),date)
 r['valueCodeableConcept']=concept('http://localhost:3456/api/terminology/CodeSystem/cnwqk835-AbnormalityStatusCS','abnormal','异常'); return [r]''',
'33': r'''def build_resources(patient,text,date):
 out=[]; specs=[('Scr','http://localhost:3456/api/terminology/Profile/cnwqk855-serum-creatinine-observation','2160-0','umol/L','umol/L'),('BUN','http://localhost:3456/api/terminology/Profile/cnwqk855-blood-urea-nitrogen-observation','3094-0','mmol/L','mmol/L'),('ALT','http://localhost:3456/api/terminology/Profile/cnwqk855-alanine-aminotransferase-observation','1742-6','U/L','U/L'),('AST','http://localhost:3456/api/terminology/Profile/cnwqk855-aspartate-aminotransferase-observation','1920-8','U/L','U/L')]
 for name,profile,code,unit,ucum in specs:
  vals=measurements(text,[name])
  if not vals:continue
  r=observation(patient,profile,concept('http://loinc.org',code,name),date); r['valueQuantity']=quantity(vals[-1][1],unit,ucum); out.append(r)
 return out''',
'37': r'''def build_resources(patient,text,date):
 out=[]; presence='http://localhost:3456/api/terminology/CodeSystem/cnwqk875-presence-cs'
 if re.search(r'颅内高压|颅内压升高|ICP升高',text,re.I) and not negated(text,'颅内'):
  out.append(coded_observation(patient,'http://localhost:3456/api/terminology/Profile/cnwqk875-intracranialhypertension-profile','http://localhost:3456/api/terminology/CodeSystem/cnwqk875-intracranialhypertension-cs','intracranial-hypertension',presence,'present',date))
 if re.search(r'意识不清|意识模糊|昏迷|嗜睡',text) and not negated(text,'意识'):
  out.append(coded_observation(patient,'http://localhost:3456/api/terminology/Profile/cnwqk875-unconsciousness-profile','http://localhost:3456/api/terminology/CodeSystem/cnwqk875-unconsciousness-cs','unconsciousness',presence,'present',date))
 return out'''
}

COMMON = r'''import re,uuid,html
from datetime import datetime,timezone,timedelta
PROFILE={profile!r}
IDENTIFIER={identifier!r}
RESOURCE_TYPE={rtype!r}
def normalize(x): return re.sub(r'\s+',' ',html.unescape(str(x or '')).replace('μ','u').replace('µ','u').replace('×','x')).strip()
def clauses(t): return [x.strip() for x in re.split(r'[，。；;!?！？]',t) if x.strip()]
def concept_clause(t,term): return next((c for c in clauses(t) if term.lower() in c.lower()),'')
def negated(t,term):
 c=concept_clause(t,term); return bool(c and (re.search(r'(?:否认|未见|没有|无|未).{0,8}'+re.escape(term),c) or re.search(re.escape(term)+r'.{0,5}(?:阴性|不存在)',c)))
def planned(t,term):
 c=concept_clause(t,term); return bool(re.search(r'(?:计划|准备|拟|预计|将).{0,12}'+re.escape(term),c))
def unit_ok(u,allowed): return normalize(u).lower().replace('μ','u') in allowed
def measurements(t,names):
 out=[]
 for n in names:
  for m in re.finditer(r'(?<![A-Za-z])'+re.escape(n)+r'\s*[=:：]?\s*(\d+(?:\.\d+)?)\s*([a-zA-Zμµ/]+(?:\^?\d+)?)?',t,re.I): out.append((n.lower(),float(m.group(1)),normalize(m.group(2) or '').lower()))
 return out
def with_upper_limits(t,names):
 out=[]
 for n in names:
  m=re.search(r'(?<![A-Za-z])'+n+r'\s*[=:：]?\s*(\d+(?:\.\d+)?).{0,20}?(?:参考|正常)[^0-9]{0,5}(?:\d+(?:\.\d+)?\s*[-~至]\s*)?(\d+(?:\.\d+)?)',t,re.I)
  if m: out.append((n,float(m.group(1)),float(m.group(2))))
 return out
def event_months(t,event):
 for c in clauses(t):
  if event not in c: continue
  m=re.search(r'(?<!\d)(\d+(?:\.\d+)?)\s*(?:个)?月',c)
  if m:return float(m.group(1))
  m=re.search(r'(?<!\d)(\d+(?:\.\d+)?)\s*年',c)
  if m:return float(m.group(1))*12
  if '半年' in c:return 6.0
  cn={'零':0,'一':1,'二':2,'两':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10}
  m=re.search(r'([一二两三四五六七八九十]+)个?月',c)
  if m:
   s=m.group(1); return float(10+(cn.get(s[1],0) if len(s)>1 else 0) if s.startswith('十') else cn.get(s,99))
 return None
def ventilation_hours(t):
 for c in clauses(t):
  if not re.search(r'机械通气|有创通气|呼吸机',c):continue
  m=re.search(r'(\d+(?:\.\d+)?)\s*(小时|h|hr|天|d|分钟|min)',c,re.I)
  if m:return float(m.group(1))*({'天':24,'d':24,'分钟':1/60,'min':1/60}.get(m.group(2).lower(),1))
 return None
def quit_months(t):
 m=re.search(r'戒烟\s*(\d+(?:\.\d+)?)\s*(年|月|个月)',t)
 if m:return float(m.group(1))*(12 if m.group(2)=='年' else 1)
 if re.search(r'戒烟\s*1年半',t):return 18
 return None
def patient_age(t):
 m=re.search(r'(?:年龄|患者|病人)?\s*(\d+(?:\.\d+)?)\s*岁',t); return float(m.group(1)) if m else None
def family_context(t): return bool(re.search(r'(?:母亲|父亲|家族|其母|其父).{0,12}(?:带状疱疹)',t))
def match_contract(t):
 t=normalize(t)
 {rule}
def coding(system,code,display=None):
 r={'system':system,'code':code}
 if display:r['display']=display
 return r
def concept(system,code,display=None):
 r={'coding':[coding(system,code,display)]}
 if display:r['text']=display
 return r
def quantity(value,unit,code): return {'value':value,'unit':unit,'system':'http://unitsofmeasure.org','code':code}
def base_resource(kind,patient,profiles=None,resource_id=None):
 r={'resourceType':kind,'id':resource_id or str(uuid.uuid4()),'subject':{'reference':'Patient/'+str(patient)}}
 if profiles:r['meta']={'profile':profiles if isinstance(profiles,list) else [profiles]}
 return r
def observation(patient,profile,code,date):
 r=base_resource('Observation',patient,profile); r.update({'status':'final','code':code,'effectiveDateTime':date}); return r
def coded_observation(patient,profile,code_system,code,value_system,value,date):
 r=observation(patient,profile,concept(code_system,code,code),date); r['valueCodeableConcept']=concept(value_system,value,value); return r
def parse_datetime(value): return datetime.fromisoformat(str(value).replace('Z','+00:00'))
def canonical_datetime(value): return parse_datetime(value).astimezone(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
def hours_before(value,hours): return (parse_datetime(value)-timedelta(hours=hours)).astimezone(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
def months_before(value,months):
 dt=parse_datetime(value); whole=int(months); month_index=dt.year*12+dt.month-1-whole; year,month=divmod(month_index,12); month+=1
 leap=year%4==0 and (year%100!=0 or year%400==0); days=[31,29 if leap else 28,31,30,31,30,31,31,30,31,30,31]
 shifted=dt.replace(year=year,month=month,day=min(dt.day,days[month-1]))-timedelta(days=(months-whole)*30.4375)
 return shifted.astimezone(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
{fhir_builder}
class FHIRResourceBundleGenerator:
 profile_id=PROFILE
 identifier=IDENTIFIER
 def __init__(self,fhir_api_base):self.fhir_api_base=fhir_api_base
 def parse_clinical_text_to_fhir_bundle(self,patient_id,case_reports,ai_algorithm_type='nlp'):
  entries=[]
  for report in case_reports or []:
   if not isinstance(report,dict):continue
   text=normalize(report.get('text',''))
   if text and match_contract(text):
    date=str(report.get('timestamp') or report.get('end_datetime') or datetime.now(timezone.utc).isoformat().replace('+00:00','Z'))
    for r in build_resources(patient_id,text,date):entries.append({'resource':r,'request':{'method':'POST','url':r['resourceType']}})
  return {'resourceType':'Bundle','type':'transaction','entry':entries}
'''

def build_source(identifier):
    return (COMMON.replace('{profile!r}',repr(PROFILES[identifier]))
                  .replace('{identifier!r}',repr(identifier))
                  .replace('{rtype!r}',repr(RESOURCE[identifier]))
                  .replace('{rule}',RULES[identifier])
                  .replace('{fhir_builder}',FHIR_BUILDERS[identifier]))
