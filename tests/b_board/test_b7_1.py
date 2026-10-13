import base64
import pytest
from scripts.b7_1_experiments import build

@pytest.fixture(scope='module')
def scope():
    n={};exec(base64.b64decode(build()['entry'][1]['resource']['content'][0]['data']),n);return n

def raw(text):return dict(match=False,facts=[dict(atom='respiratory',state='PRESENT',evidence=text)],subject='patient',negated=False,planned=False,uncertain=False,evidence=[text],reason='MOCK')

def test_false_overall_hint_retains_valid_fact(scope):
    g=scope['FHIRResourceBundleGenerator']('http://localhost:3456');g.transport=lambda p:raw('活动后透不过气')
    assert g.parse_clinical_text_to_fhir_bundle('p1',[dict(text='活动后透不过气')])['entry']

def test_ambiguous_binding_rejected(scope):
    with pytest.raises(ValueError):scope['_b4_decode'](raw('活动后透不过气'),'2',[dict(text='活动后透不过气'),dict(text='活动后透不过气')],['respiratory'])

@pytest.mark.parametrize('prefix',['父亲','否认','可能','拟评估'])
def test_false_hint_does_not_remove_safety(scope,prefix):
    g=scope['FHIRResourceBundleGenerator']('http://localhost:3456');g.transport=lambda p:raw('活动后透不过气')
    assert not g.parse_clinical_text_to_fhir_bundle('p1',[dict(text=prefix+'活动后透不过气')])['entry']
