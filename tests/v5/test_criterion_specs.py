from v5.criterion_specs import CRITERION_IDS, load_criterion_specs


def test_compact_specs_cover_all_criteria_from_reviewed_ir():
    specs = load_criterion_specs()
    assert tuple(specs) == CRITERION_IDS
    assert len(specs) == 16
    for criterion, spec in specs.items():
        assert spec.criterion_id == criterion
        assert spec.original_text and spec.original_text != criterion
        assert spec.plain_summary
        assert spec.positive_conditions
        assert spec.transport_requirements
        assert spec.aliases
        assert spec.temporal_requirement
        assert spec.polarity in {"inclusion", "eligibility", "exclusion"}


def test_numeric_specs_preserve_threshold_meaning():
    specs = load_criterion_specs()
    for criterion in ("265", "615", "635", "755", "805", "855"):
        assert specs[criterion].thresholds
    assert any("0.06" in item for item in specs["265"].thresholds)
    assert any("2" in item for item in specs["635"].thresholds)


def test_875_competition_policy_is_ever_present():
    assert load_criterion_specs()["875"].temporal_requirement == "EVER_PRESENT"
