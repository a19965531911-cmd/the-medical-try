from pathlib import Path

from scripts.audit_v5_sources import CRITERIA, OFFICIAL_TITLES, build_official_audits, render_reports, transport_matrix


ROOT = Path(__file__).resolve().parents[2]


def test_official_bundle_audit_covers_exact_frozen_sequence():
    audits = build_official_audits()
    assert tuple(audits) == OFFICIAL_TITLES
    assert len(audits) == 16
    assert all(item.source_compiles for item in audits.values())
    assert sum(item.architecture == "LLM_PER_REPORT" for item in audits.values()) >= 15
    assert all(item.endpoint and item.model and item.response_parser for item in audits.values())


def test_transport_matrix_is_complete_and_635_is_resolved():
    matrix = transport_matrix()
    assert tuple(matrix) == CRITERIA
    for contract in matrix.values():
        assert contract.resource_type
        assert contract.profile
        assert contract.query_behavior
        assert contract.minimum_fields
        assert contract.selected_source in {"OFFICIAL", "V2.4.3", "V4"}
    c635 = matrix["635"]
    assert c635.polarity == "INCLUSION"
    assert c635.logical_interpretation == "AST_AND_ALT_AND_BUN_AND_CR"
    assert c635.threshold_interpretation == "EACH_LTE_2X_ULN"


def test_reports_render_all_criteria(tmp_path):
    paths = render_reports(build_official_audits(), transport_matrix(), tmp_path)
    assert len(paths) == 4
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert "audited" in text or "criterion" in text.lower()
