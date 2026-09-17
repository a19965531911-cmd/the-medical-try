from v5.metrics import MatcherMetrics
from v5.models import Decision
from v5.transport import TransportStatus


def test_metrics_are_aggregate_and_privacy_safe():
    metrics = MatcherMetrics()
    metrics.record("675", Decision.MATCH, Decision.NO_MATCH, TransportStatus.OK, "NON_HEAD_FACE_SITE")
    line = metrics.format_line()
    assert line.startswith("V5_METRICS ")
    assert "criterion=675" in line
    assert "guarded_drop=1" in line
    assert "patient" not in line.lower()
    assert "患者" not in line
