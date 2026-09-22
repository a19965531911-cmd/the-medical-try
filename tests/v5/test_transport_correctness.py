from v5.criterion_specs import load_criterion_specs
from v5.models import Decision
from v5.payload_extractors import extract_payload
from v5.fhir_adapter import build_resources

def p(cid, text):
    return extract_payload(load_criterion_specs()[cid], [{"text": text}], Decision.MATCH)

def test_265_does_not_use_age_as_troponin():
    x = p("265", "patient age 65, preop cTnT 0.04 ug/L")
    assert x.values["number"] == 0.04
    assert x.values["unit"] == "ug/L"

def test_855_requires_scr_association():
    x = p("855", "patient age 70, Scr 120 umol/L")
    assert x.values["number"] == 120
    assert x.values["unit"] == "umol/L"

def test_615_binds_branch_value():
    assert p("615", "patient age 65, PSA 0.2 ng/mL").values["branch"] == "PSA"
    assert p("615", "patient age 70, GS 9").values["branch"] == "GS"
    assert "number" not in p("615", "pT3a, date 2026-01-01").values

def test_805_four_states():
    assert p("805", "current smoker").values["smoking"] == "current-smoker"
    assert p("805", "former smoker quit 1 year").values["smoking"] == "former-smoker"
    assert p("805", "former smoker quit 3 years").values["smoking"] == "former-smoker"
    assert p("805", "never smoker").values["smoking"] == "never-smoker"

def test_no_fabricated_defaults():
    assert "number" not in p("855", "Scr not recorded").values


def test_555_uses_explicit_surgery_date_only():
    payload = p("555", "手术日期 2025-03-04")
    resource = build_resources("555", "p1", payload)[0]
    assert resource["performedDateTime"] == "2025-03-04"
    no_date = build_resources("555", "p1", p("555", "3个月前完成手术"))
    assert no_date == ()

def test_745_does_not_fabricate_procedure_dates():
    payload = p("745", "术后行有创机械通气")
    resources = build_resources("745", "p1", payload)
    assert resources == ()

def test_755_requires_duration_and_keeps_explicit_start_only():
    payload = p("755", "机械通气持续30小时")
    resource = build_resources("755", "p1", payload)[0]
    assert resource["performedPeriod"] == {"duration_hours": 30.0}
    assert build_resources("755", "p1", p("755", "机械通气")) == ()
