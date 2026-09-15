import re, uuid, html
from datetime import datetime, timezone

BASE = 'http://localhost:3456/api/terminology/'

def norm(s):
    s = html.unescape(str(s or '')).replace('μ','u').replace('µ','u').replace('×','x')
    return re.sub(r'\s+', ' ', s).strip()

def reports_text(reports):
    return ' '.join(norm((r or {}).get('text','')) for r in (reports or []) if isinstance(r, dict))

def dt(reports):
    for r in (reports or []):
        if isinstance(r, dict):
            v = r.get('timestamp') or r.get('end_datetime')
            if v: return str(v)
    return datetime.now(timezone.utc).isoformat().replace('+00:00','Z')

def numbers(text, name):
    return [float(x) for x in re.findall(rf'{re.escape(name)}\s*[=:：]?\s*(\d+(?:\.\d+)?)', text, re.I)]

def has_neg(text, term):
    return bool(re.search(rf'(?:否认|无|未|没有|不|排除).{{0,10}}{re.escape(term)}', text))

def duration_hours(text):
    m=re.search(r'(?:机械通气|有创通气).{0,12}?(\d+(?:\.\d+)?)\s*(小时|h|hr|天|d)',text,re.I)
    if not m:return None
    return float(m.group(1))*(24 if m.group(2) in ('天','d') else 1)

def resource(profile, patient, typ, **fields):
    x={'resourceType':typ,'id':str(uuid.uuid4()),'meta':{'profile':[BASE+'Profile/'+profile]},'subject':{'reference':'Patient/'+str(patient)}}
    x.update(fields); return x

def entry(r): return {'resource':r,'request':{'method':'POST','url':r['resourceType']}}

def quantity_obs(profile, patient, code_system, code, display, value, unit, date):
    return resource(profile,patient,'Observation',status='final',code={'coding':[{'system':code_system,'code':code,'display':display}]},effectiveDateTime=date,valueQuantity={'value':value,'unit':unit,'system':'http://unitsofmeasure.org'})

class FHIRResourceBundleGenerator:
    def __init__(self, fhir_api_base: str): self.fhir_api_base=fhir_api_base
    def parse_clinical_text_to_fhir_bundle(self, patient_id, case_reports, ai_algorithm_type='nlp'):
        text=reports_text(case_reports); date=dt(case_reports); p=self.profile_id
        rs=[]
        q=self.question; neg=r'(?:否认|无|未|没有|拟行|预计)'
        # Terminal contract gates. Each gate returns before any legacy compatibility code.
        def done(): return {'resourceType':'Bundle','type':'transaction','entry':[entry(r) for r in rs]}
        if '术后需要有创' in q or ('有创机械通气' in q and '术后' in q):
            if re.search(r'术后.{0,15}(?:需|需要|予|给予).{0,8}(?:有创|气管插管).{0,8}机械通气',text) and not re.search(r'(?:无需|不需要|无创)',text): rs.append(resource(p,patient_id,'Procedure',status='completed',performedDateTime=date,code={'text':'术后有创机械通气'}))
            return done()
        if 'POP-Q' in q or '盆腔器官脱垂' in q:
            m=re.search(r'(?:POP\s*[-－]?\s*Q|盆腔器官脱垂).{0,12}?(?:III|IV|3|4)(?:度|级|期)',text,re.I)
            if m and not re.search(r'(?:无|否认).{0,8}盆腔器官脱垂',text): rs.append(resource(p,patient_id,'Condition',clinicalStatus={'coding':[{'code':'active'}]},code={'text':'盆腔器官脱垂'},onsetDateTime=date))
            return done()
        if '腹泻' in q or '便秘' in q:
            severe=bool(re.search(r'(严重|重度|剧烈).{0,4}腹泻',text)); const=bool(re.search(r'便秘',text))
            if (severe or const) and not re.search(r'(?:无|否认|未见).{0,6}(?:腹泻|便秘)',text): rs.append(resource(p,patient_id,'Condition',clinicalStatus={'coding':[{'code':'active'}]},code={'text':'严重腹泻或便秘'},onsetDateTime=date))
            return done()
        if '活动期' in q or '传染性' in q or '结缔组织' in q:
            diseases=r'(?:甲肝|乙肝|乙型肝炎|艾滋病|HIV|结核|系统性红斑狼疮|结缔组织病)'; active=(re.search(diseases+r'.{0,8}(?:活动|活动性)',text,re.I) or re.search(r'(?:活动|活动性).{0,8}'+diseases,text,re.I))
            if re.search(r'(?:无|否认|未见).{0,10}(?:活动性|活动期)',text): active=None
            if active: rs.append(resource(p,patient_id,'Condition',clinicalStatus={'coding':[{'code':'active'}]},code={'text':'活动期疾病'},onsetDateTime=date))
            return done()
        if '凝血' in q:
            if re.search(r'凝血(?:功能)?(?:异常|障碍)',text) and not re.search(r'(?:正常|未见|无).{0,5}凝血',text): rs.append(resource(p,patient_id,'Observation',status='final',code={'text':'凝血功能'},effectiveDateTime=date,valueString='异常'))
            return done()
        if '颅内高压' in q or '意识不清' in q:
            pos=bool(re.search(r'颅内(?:高压|压升高)|ICP升高|意识不清|意识模糊|昏迷|嗜睡',text,re.I)) and not bool(re.search(r'(?:无|否认).{0,6}(?:颅内|意识)',text)) and not re.search(r'意识(?:清楚|清醒)',text)
            if pos: rs.append(resource(p,patient_id,'Condition',clinicalStatus={'coding':[{'code':'active'}]},code={'text':'颅内高压或意识不清'},onsetDateTime=date))
            return done()
        if '外院' in q and '化疗' in q:
            if re.search(r'(?:曾|既往|接受|行).{0,8}化疗',text) and '外院' in text and not re.search(r'(?:计划|准备|拟).{0,8}化疗',text) and not re.search(r'(?:未|否认|没有).{0,5}化疗',text): rs.append(resource(p,patient_id,'Procedure',status='completed',performedDateTime=date,code={'text':'化疗'}))
            return done()
        if '术后需要有创' in q or ('有创机械通气' in q and '术后' in q):
            if re.search(r'术后.{0,15}(?:需|需要|予|给予).{0,8}(?:有创|气管插管).{0,8}机械通气',text) and not re.search(r'(?:无需|不需要|无创)',text): rs.append(resource(p,patient_id,'Procedure',status='completed',performedDateTime=date,code={'text':'术后有创机械通气'}))
            return done()
        if 'Scr' in q or ('肝肾功能' in q and 'Scr' in q):
            scr=numbers(text,'Scr'); bun=numbers(text,'BUN'); good=bool(scr and bun and scr[0]<178 and bun[0]<9 and re.search(r'(?:ALT|AST).{0,12}(?:正常|无明显升高)',text))
            if good: rs.append(resource(p,patient_id,'Observation',status='final',code={'text':'肝肾功能'},effectiveDateTime=date,valueCodeableConcept={'text':'满足条件'}))
            return done()
        # Every known A question is terminally contract-routed; unknown questions are empty.
        known=('化疗','机械通气','手术','戒烟','吸烟','cTnI','cTnT','带状疱疹','头面部','PSA','pT','POP-Q','腹泻','便秘','AST','ALT','BUN','Cr','凝血','肝功','肾功','颅内','意识','传染性','结缔组织','年龄')
        if not any(k in q for k in known):
            return {'resourceType':'Bundle','type':'transaction','entry':[]}
        # A known A-contract is terminal: its decision must never reach the legacy handler.
        if 'cTnI' in q or 'cTnT' in q:
            if (any(x>=.06 for x in numbers(text,'cTnI')) or any(x>=.03 for x in numbers(text,'cTnT'))) and not has_neg(text,'cTn'):
                rs.append(quantity_obs(p,patient_id,'http://loinc.org','85354-9','cardiac troponin',next((x for x in numbers(text,'cTnI') if x>=.06),next((x for x in numbers(text,'cTnT') if x>=.03),0)),'ug/L',date))
            return {'resourceType':'Bundle','type':'transaction','entry':[entry(r) for r in rs]}
        if '机械通气' in q:
            h=duration_hours(text)
            if h is not None and h>=24 and not re.search(neg+r'.{0,8}机械通气',text): rs.append(resource(p,patient_id,'Procedure',status='completed',performedDateTime=date,code={'text':'机械通气'}))
            return {'resourceType':'Bundle','type':'transaction','entry':[entry(r) for r in rs]}
        if '半年' in q:
            if re.search(r'手术',text) and re.search(r'(?<!\d)(?:[0-5](?:\.\d+)?|6(?:\.0+)?|六)\s*(?:个)?月',text) and not has_neg(text,'手术'): rs.append(resource(p,patient_id,'Procedure',status='completed',performedDateTime=date,code={'text':'手术'}))
            return {'resourceType':'Bundle','type':'transaction','entry':[entry(r) for r in rs]}
        if '戒烟' in q:
            m=re.search(r'戒烟\s*(\d+(?:\.\d+)?)\s*年',text)
            if ('吸烟' in text and not m) or (m and float(m.group(1))<2): rs.append(resource(p,patient_id,'Observation',status='final',code={'text':'吸烟状态'},effectiveDateTime=date,valueString=text[:120]))
            return {'resourceType':'Bundle','type':'transaction','entry':[entry(r) for r in rs]}
        if '伊立替康' in q:
            if '伊立替康' in text and re.search(r'首次|第一次|初次',text) and not re.search(r'既往|曾经|已用过',text): rs.append(resource(p,patient_id,'MedicationAdministration',status='completed',effectiveDateTime=date,medicationCodeableConcept={'text':'伊立替康化疗'}))
            return {'resourceType':'Bundle','type':'transaction','entry':[entry(r) for r in rs]}
        if '带状疱疹' in q or '头面部' in q:
            ages=numbers(text,'年龄')
            if ages and ages[0]>=50 and '带状疱疹' in text and re.search(r'头|面|脸|眼|耳',text) and not has_neg(text,'带状疱疹'): rs.append(resource(p,patient_id,'Condition',clinicalStatus={'coding':[{'code':'active'}]},code={'text':'头面部带状疱疹'},onsetDateTime=date))
            return {'resourceType':'Bundle','type':'transaction','entry':[entry(r) for r in rs]}
        if 'PSA' in q or 'pT' in q:
            pt=bool(re.search(r'pT\s*(?:3a|4)',text,re.I)); r1='R1' in text; pn='pN1' in text; gs=any(x>=8 for x in numbers(text,'GS')); psa=any(x>.1 for x in numbers(text,'PSA'))
            if pt or r1 or pn or gs or psa: rs.append(resource(p,patient_id,'Observation',status='final',code={'text':'肿瘤分期'},effectiveDateTime=date,valueString=text[:160]))
            return {'resourceType':'Bundle','type':'transaction','entry':[entry(r) for r in rs]}
        # Each contract has its own evidence predicate; common helpers only normalize evidence.
        if 'cTnI' in q or 'cTnT' in q:
            if (any(x>=.06 for x in numbers(text,'cTnI')) or any(x>=.03 for x in numbers(text,'cTnT'))) and not has_neg(text,'cTn'):
                rs.append(quantity_obs(p,patient_id,'http://loinc.org','85354-9','cardiac troponin',1,'ug/L',date))
        elif '机械通气' in q:
            h=duration_hours(text)
            if h is not None and h>=24 and not re.search(neg+r'.{0,8}机械通气',text): rs.append(resource(p,patient_id,'Procedure',status='completed',performedDateTime=date,code={'text':'机械通气'}))
        elif '半年' in q:
            if re.search(r'(手术|手术史)',text) and re.search(r'(?:[0-6](?:\.\d+)?|六)\s*(?:个)?月',text) and not has_neg(text,'手术'): rs.append(resource(p,patient_id,'Procedure',status='completed',performedDateTime=date,code={'text':'手术'}))
        elif '戒烟' in q:
            m=re.search(r'戒烟\s*(\d+(?:\.\d+)?)\s*年',text)
            if ('吸烟' in text and not m) or (m and float(m.group(1))<2): rs.append(resource(p,patient_id,'Observation',status='final',code={'text':'吸烟状态'},effectiveDateTime=date,valueString=text[:120]))
        elif '伊立替康' in q:
            if '伊立替康' in text and re.search(r'首次|第一次|初次',text) and not re.search(r'既往|曾经|已用过',text): rs.append(resource(p,patient_id,'MedicationAdministration',status='completed',effectiveDateTime=date,medicationCodeableConcept={'text':'伊立替康化疗'}))
        elif '头面部' in q or '带状疱疹' in q:
            ages=numbers(text,'年龄');
            if ages and ages[0]>=50 and '带状疱疹' in text and re.search(r'头|面|脸|眼|耳',text) and not has_neg(text,'带状疱疹'): rs.append(resource(p,patient_id,'Condition',clinicalStatus={'coding':[{'code':'active'}]},code={'text':'头面部带状疱疹'},onsetDateTime=date))
        elif '肿瘤' in q or 'PSA' in q:
            pt=bool(re.search(r'pT\s*(?:3a|4)',text,re.I)); r1='R1' in text; pn='pN1' in text; gs=any(x>=8 for x in numbers(text,'GS')); psa=any(x>.1 for x in numbers(text,'PSA'))
            if pt or r1 or pn or gs or psa: rs.append(resource(p,patient_id,'Observation',status='final',code={'text':'肿瘤分期'},effectiveDateTime=date,valueString=text[:160]))
        # Remaining contracts retain conservative, evidence-gated handlers below.
        if any(k in self.question for k in ['化疗','手术史','接受过']):
            if any(k in text for k in ['化疗','手术','外院','术后','手术史']) and not re.search(r'(否认|无|未曾|没有).{0,8}(化疗|手术)',text):
                rs.append(resource(p,patient_id,'Procedure',status='completed',performedDateTime=date,code={'text':text[:120]}))
        elif any(k in self.question for k in ['机械通气','通气']):
            if '机械通气' in text or '有创通气' in text:
                rs.append(resource(p,patient_id,'Procedure',status='completed',performedDateTime=date,code={'text':'机械通气'}))
        elif any(k in self.question for k in ['吸烟','戒烟']):
            if re.search(r'吸烟|抽烟|烟龄|戒烟',text) and not re.search(r'(否认|不吸|从不|无).{0,5}(吸烟|抽烟)',text):
                rs.append(resource(p,patient_id,'Observation',status='final',code={'text':'吸烟状态'},effectiveDateTime=date,valueString=text[:120]))
        elif any(k in self.question for k in ['年龄','诊断','带状疱疹','活动期','意识','颅内压','腹泻','便秘','POP-Q']):
            terms=re.findall(r'\d+(?:\.\d+)?',text)
            rs.append(resource(p,patient_id,'Condition',clinicalStatus={'coding':[{'system':'http://terminology.hl7.org/CodeSystem/condition-clinical','code':'active'}]},code={'text':text[:160]},onsetDateTime=date)) if terms or any(k in text for k in ['诊断','疱疹','腹泻','便秘','活动','意识']) else None
        else:
            # Laboratory and organ status: emit observations only when explicit evidence exists.
            for lab in re.findall(r'\b(AST|ALT|BUN|Cr|cTnI|cTnT|PSA|Scr)\s*[=:：]?\s*([0-9]+(?:\.\d+)?)\s*([a-zA-Zuμ/²^0-9]*)',text):
                rs.append(quantity_obs(p,patient_id,'http://loinc.org',lab[0],lab[0],float(lab[1]),lab[2] or '1',date))
            if any(k in text for k in ['肝功能不全','肾功能不全','肝功异常','肾功异常']):
                rs.append(resource(p,patient_id,'Observation',status='final',code={'text':'器官功能'},effectiveDateTime=date,valueCodeableConcept={'text':'不全'}))
        return {'resourceType':'Bundle','type':'transaction','entry':[entry(r) for r in rs]}
