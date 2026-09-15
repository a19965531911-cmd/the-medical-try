from legacy.v2_4_3.src.baseline import FHIRResourceBundleGenerator


def test_empty_input_returns_transaction_bundle():
    generator = FHIRResourceBundleGenerator("")
    generator.question = "机械通气"
    generator.profile_id = "synthetic-profile"

    bundle = generator.parse_clinical_text_to_fhir_bundle("synthetic-001", [])

    assert bundle["type"] == "transaction"
    assert bundle["entry"] == []


def test_negated_synthetic_surgery_history_is_not_emitted():
    generator = FHIRResourceBundleGenerator("")
    generator.question = "手术史"
    generator.profile_id = "synthetic-profile"

    bundle = generator.parse_clinical_text_to_fhir_bundle(
        "synthetic-002", [{"text": "否认手术史。", "timestamp": "2026-01-01"}]
    )

    assert bundle["entry"] == []
