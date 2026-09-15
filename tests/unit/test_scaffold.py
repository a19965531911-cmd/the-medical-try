from pathlib import Path

from v43.fixtures import load_fixture
from v43.references import CRITERION_IDS, REFERENCE_ROOT, frozen_reference_paths


def test_fixture_loader_returns_reports_from_json():
    reports = load_fixture("tests/fixtures/reports.json")
    assert reports == [{"text": "测试病历", "source_type": "synthetic"}]


def test_frozen_reference_configuration_points_to_existing_external_files():
    assert CRITERION_IDS == ("185", "675", "745", "875")
    assert REFERENCE_ROOT.resolve() != Path.cwd().resolve()
    assert all(path.is_file() for path in frozen_reference_paths().values())


def test_scaffold_does_not_generate_submission_artifacts():
    assert not list(Path.cwd().rglob("Bundle*.json"))
