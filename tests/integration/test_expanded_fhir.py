from importlib import import_module

import pytest

from v43.clinical.store import ClinicalStore
from v43.fhir.compiler import compile_fhir
from v43.fhir.contracts import contract_for_criterion
from v43.fhir.service_replay import replay_service
from v43.fhir.validator import validate_fhir
from v43.ir.loader import load_criterion_ir
from v43.references import frozen_reference_paths
from v43.retrieval.retriever import retrieve
from v43.runtime import RuntimeServices, evaluate_criterion


CASES = {
    "165":"转入我院前于当地医院完成2周期化疗", "265":"术前cTnI 0.08 μg/L",
    "485":"盆腔器官脱垂，POP-Q III期", "555":"3个月前行胆囊切除术",
    "565":"目前严重腹泻", "615":"Gleason评分8分", "635":"AST 30 U/L上限40，ALT 50 U/L上限40，BUN 12 mmol/L上限9，Cr 180 umol/L上限100",
    "735":"活动性乙型肝炎", "755":"机械通气持续30小时", "805":"目前每日吸烟",
    "835":"目前凝血功能异常", "855":"Scr 120 μmol/L，BUN 7 mmol/L，ALT 30 U/L上限40，AST 25 U/L上限40",
}


def store_for(criterion, text):
    ir=load_criterion_ir(frozen_reference_paths()["criterion_ir_draft"],(criterion,))[criterion]
    packet=retrieve(ir,[{"text":text,"timestamp":"2026-01-01","fixture_source":"synthetic"}])
    store=ClinicalStore.from_packet(packet)
    facts,events,relations=import_module(f"v43.criteria.c{criterion}").extract(packet)
    for item in facts: store.add_fact(item)
    for item in events: store.add_event(item)
    for item in relations: store.add_relation(item)
    return store


@pytest.mark.parametrize("criterion", tuple(CASES))
def test_expanded_criterion_fhir_structural_and_service_boundaries(criterion):
    run=evaluate_criterion(criterion,"p1",[{"text":CASES[criterion],"timestamp":"2026-01-01","fixture_source":"synthetic"}],RuntimeServices(None,1.0))
    contract=contract_for_criterion(criterion)
    compiled=compile_fhir(run.decision_trace,store_for(criterion,CASES[criterion]),contract,"Patient/p1")
    valid=validate_fhir(compiled,contract)
    assert compiled.status == "COMPILED"
    assert valid.structural_status == "VALID"
    assert replay_service(valid.resources,contract.service,"fixture://fhir",{"p1":"doc"}).status == "SERVICE_HIT"
    assert replay_service(valid.resources,contract.service,"fixture://fhir",{"other":"doc"}).status == "SERVICE_MISS"
