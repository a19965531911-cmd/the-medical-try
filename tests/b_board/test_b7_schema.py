import base64
import pytest
from scripts.b7_experiments import build


@pytest.fixture(scope='module')
def scope():
    ns={};exec(base64.b64decode(build()['entry'][1]['resource']['content'][0]['data']),ns);return ns


def test_extended_provenance(scope):
    text='活动后透不过气'
    raw=dict(profile_id='2',criterion=scope['QUESTION'],match=True,facts=[dict(atom='respiratory',state='PRESENT',evidence=text,report_index=0,subject='patient',event_identity='A')],subject='patient',negated=False,planned=False,uncertain=False,evidence=[text],reason='synthetic')
    assert scope['_b4_decode'](raw,'2',[dict(text=text,event_id='A')],['respiratory'])['facts'][0]['report']==0
    raw['facts'][0]['event_identity']='B'
    with pytest.raises(ValueError):scope['_b4_decode'](raw,'2',[dict(text=text,event_id='A')],['respiratory'])


def test_worker_capacity(scope):
    slots=scope['_B7_SLOTS']
    assert slots.acquire(False) and slots.acquire(False)
    try:
        g=scope['FHIRResourceBundleGenerator']('http://localhost:3456')
        assert not g.parse_clinical_text_to_fhir_bundle('p1',[dict(text='活动后透不过气')])['entry']
        assert g.transport_error_kind=='WORKER_LIMIT'
    finally:slots.release();slots.release()
