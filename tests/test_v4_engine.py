from src.v4_engine.compiler import CriterionCompiler
from src.v4_engine.criterion_specs import SPECS
from src.v4_engine.evidence import AtomState, Evidence, Relation
from src.v4_engine.extractors import age
from src.v4_engine.ledger import EvidenceLedger
from src.v4_engine.semantic_nli import parse_atom_response


def evidence(atom, value=True, state=AtomState.ENTAILED):
    return Evidence(atom, state, atom, value, 0, "synthetic", "2026-01-01")


def test_synthetic_age_and_zoster_satisfy_criterion_675():
    ledger = EvidenceLedger("synthetic-001", "24")
    for item in age("患者56岁。", 0):
        ledger.add(item)
    ledger.add(evidence("herpes_zoster"))
    ledger.add(evidence("diagnosis_confirmed"))
    ledger.add(evidence("zoster_site", "face"))

    decision = CriterionCompiler().compile(SPECS["24"], ledger)

    assert decision.satisfied


def test_unrelated_events_do_not_satisfy_relation_constraint():
    ledger = EvidenceLedger("synthetic-002", "31")
    ledger.add(evidence("surgery"))
    ledger.add(evidence("postoperative_state"))
    ledger.add(evidence("invasive_mechanical_ventilation"))

    assert not CriterionCompiler().compile(SPECS["31"], ledger).satisfied

    ledger.add_relation(Relation("ventilation", "postoperative_state", "SAME_CLAUSE", 0))
    assert CriterionCompiler().compile(SPECS["31"], ledger).satisfied


def test_semantic_match_flag_has_no_authority():
    response = {
        "match": True,
        "atoms": {"first_use": {"state": "ENTAILED", "evidence": ["首次用药"]}},
    }

    assert parse_atom_response(response, 0) == []


def test_unknown_semantic_atom_is_retained_without_positive_evidence():
    response = {"atoms": {"first_use": {"state": "UNKNOWN", "evidence": []}}}

    parsed = parse_atom_response(response, 0)

    assert len(parsed) == 1
    assert parsed[0].state is AtomState.UNKNOWN
