import pytest

from v43.observability.reason_codes import ReasonCodeRegistry
from v43.observability.trace import emit_trace


def test_no_raw_text_or_stable_patient_identifier_crosses_observability_boundary():
    event = emit_trace({"run_id": "run-ephemeral", "stage": "retrieval", "span_count": 2,
                        "raw_text": "secret", "patient_id": "stable-id",
                        "reason_code": "RETRIEVAL_FALLBACK_USED"})
    assert event == {"run_id": "run-ephemeral", "stage": "retrieval", "span_count": 2,
                     "reason_code": "RETRIEVAL_FALLBACK_USED"}


def test_reason_registry_accepts_frozen_codes_and_rejects_unknown_codes():
    registry = ReasonCodeRegistry.from_frozen_csv()
    registry.validate("SERVICE_MISS")
    with pytest.raises(ValueError, match="unregistered reason code"):
        registry.validate("MADE_UP")

