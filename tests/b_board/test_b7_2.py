import base64
import pytest

@pytest.fixture(scope='module')
def ns():
    from scripts.b7_2_experiments import build
    n={};exec(base64.b64decode(build()['entry'][1]['resource']['content'][0]['data']),n);return n

def raw(q,evidence=None):
    r=dict(match=False,facts=[dict(atom='respiratory',state='PRESENT',evidence=q)],subject='patient',negated=False,planned=False,uncertain=False,reason='MOCK')
    if evidence is not None:r['evidence']=evidence
    return r

@pytest.mark.parametrize('top',[None,[]])
def test_verified_facts_fill_missing_top_evidence(ns,top):
    q='活动后透不过气';x=ns['_b4_decode'](raw(q,top),'2',[dict(text=q)],['respiratory'])
    assert x['evidence']==[q] and x['facts'][0]['report']==0 and x['match']

def test_top_evidence_conflict_rejected(ns):
    q='活动后透不过气'
    with pytest.raises(ValueError):ns['_b4_decode'](raw(q,['咳嗽']),'2',[dict(text=q+'。咳嗽')],['respiratory'])

@pytest.mark.parametrize('records',[
    [dict(text='活动后透不过气'),dict(text='活动后透不过气')],
    [dict(text='活动后透不过气',event_id='A'),dict(text='活动后透不过气',event_id='B')],
    [dict(text='父亲活动后透不过气'),dict(text='患者活动后透不过气')]])
def test_ambiguous_source_rejected_even_with_model_index(ns,records):
    r=raw('活动后透不过气', ['活动后透不过气']);r['facts'][0]['report']=1
    with pytest.raises(ValueError):ns['_b4_decode'](r,'2',records,['respiratory'])

def test_false_overall_hint_and_incomplete_and(ns):
    q='活动后透不过气';g=ns['FHIRResourceBundleGenerator']('http://localhost:3456');g.transport=lambda p:raw(q)
    assert g.parse_clinical_text_to_fhir_bundle('p1',[dict(text=q)])['entry']

def test_protected_numeric_unknown_is_not_a_model_call():
    from scripts.b7_2_experiments import build
    b=build();n={};e=next(e['resource'] for e in b['entry'][1:] if e['resource']['content'][0]['title']=='625')
    exec(base64.b64decode(e['content'][0]['data']),n)
    g=n['FHIRResourceBundleGenerator']('http://localhost:3456');g.transport=lambda p:pytest.fail('protected numeric call')
    assert not g.parse_clinical_text_to_fhir_bundle('p1',[dict(text='TBIL 1 ULN')])['entry']
    assert g.model_metrics['calls']==0
