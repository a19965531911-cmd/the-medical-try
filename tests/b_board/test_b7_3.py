import base64,json
from functools import lru_cache
import pytest

@lru_cache(maxsize=None)
def ns(cid='2'):
    from scripts.b7_3_experiments import build
    b=build();n={};r=next(e['resource'] for e in b['entry'][1:] if e['resource']['content'][0]['title']==cid)
    exec(base64.b64decode(r['content'][0]['data']),n);return n

def raw(facts,**extra):
    return dict(match=None,facts=facts,subject='patient',negated=False,planned=False,uncertain=False,evidence=[],reason='MOCK',**extra)

@pytest.mark.parametrize('facts',[[],[dict(atom='respiratory',state='UNKNOWN',evidence='')],[dict(atom='respiratory',state='UNKNOWN',evidence='',report=0)]])
def test_unknown_empty_safely_omitted(facts):
    n=ns();checked=n['_b4_decode'](raw(facts),'2',[dict(text='活动后透不过气')],['respiratory'])
    assert checked['facts']==[] and checked['evidence']==[]
    g=n['FHIRResourceBundleGenerator']('http://localhost:3456');g.transport=lambda p:raw(facts)
    assert not g.parse_clinical_text_to_fhir_bundle('p1',[dict(text='活动后透不过气')])['entry']

def test_mixed_unknown_preserves_grounded_present():
    n=ns('3');q='组织学提示肝细胞恶性肿瘤'
    checked=n['_b4_decode'](raw([dict(atom='hcc',state='PRESENT',evidence=q),dict(atom='r0',state='UNKNOWN',evidence='')]),'3',[dict(text=q)],['hcc','r0'])
    assert [f['atom'] for f in checked['facts']]==['hcc'] and checked['evidence']==[q]

@pytest.mark.parametrize('quote',['','不在原文的事实'])
def test_positive_needs_literal_evidence(quote):
    with pytest.raises(ValueError):ns()['_b4_decode'](raw([dict(atom='respiratory',state='PRESENT',evidence=quote)]),'2',[dict(text='活动后透不过气')],['respiratory'])

def test_source_and_top_contract_stays_strict():
    q='活动后透不过气';n=ns();f=dict(atom='respiratory',state='PRESENT',evidence=q)
    for reports,output in [([dict(text=q),dict(text=q)],raw([f])),([dict(text=q)],dict(raw([dict(f,report=1)]))),([dict(text=q+'。咳嗽')],dict(raw([f]),evidence=['咳嗽']))]:
        with pytest.raises(ValueError):n['_b4_decode'](output,'2',reports,['respiratory'])

@pytest.mark.parametrize('content',[None,'','{"facts":','{}'])
def test_null_empty_truncated_content_falls_back(content):
    n=ns();g=n['FHIRResourceBundleGenerator']('http://localhost:3456');g.transport=lambda p:content
    assert not g.parse_clinical_text_to_fhir_bundle('p1',[dict(text='活动后透不过气')])['entry']

def test_markdown_false_hint_grounded_fact():
    q='活动后透不过气';n=ns();g=n['FHIRResourceBundleGenerator']('http://localhost:3456')
    g.transport=lambda p:'```json\n'+json.dumps(dict(raw([dict(atom='respiratory',state='PRESENT',evidence=q)]),match=False))+'\n```'
    assert g.parse_clinical_text_to_fhir_bundle('p1',[dict(text=q)])['entry']

def test_prompt_omits_unknown_fact_templates():
    n=ns();p=json.loads(n['_b4_prompt']('2',[dict(text='活动后透不过气')],['respiratory']))
    assert p['output']['facts']==[]

def test_legacy_extended_unknown_is_safe():
    n=ns();r=dict(raw([dict(atom='respiratory',state='UNKNOWN',evidence='',report_index=0,subject='patient',event_identity='A')]),profile_id='2',criterion=n['QUESTION'])
    assert n['_b4_decode'](r,'2',[dict(text='活动后透不过气',event_id='A')],['respiratory'])['facts']==[]
