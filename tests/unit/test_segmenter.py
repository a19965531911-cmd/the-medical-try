from dataclasses import fields
from hashlib import sha256

from v43.retrieval.models import EvidencePacket, EvidenceSpan
from v43.retrieval.segmenter import segment_reports


def test_preserves_report_metadata_and_original_offsets():
    text = "  发热。咳嗽！\n复查？  "
    spans = segment_reports(
        [{"text": text, "topic": "病程记录", "timestamp": "2026-09-15T08:30:00"}]
    )

    assert [span.text for span in spans] == ["发热。", "咳嗽！", "复查？"]
    assert [(span.start_offset, span.end_offset) for span in spans] == [
        (2, 5),
        (5, 8),
        (9, 12),
    ]
    assert all(span.report_index == 0 for span in spans)
    assert all(span.topic == "病程记录" for span in spans)
    assert all(span.timestamp == "2026-09-15T08:30:00" for span in spans)
    assert all(text[span.start_offset : span.end_offset] == span.text for span in spans)


def test_normalized_hash_and_span_id_are_stable_on_repeat():
    reports = [{"text": "  体温  38.5 ℃。", "topic": "护理", "timestamp": None}]

    first = segment_reports(reports)
    second = segment_reports(reports)

    expected_hash = sha256("体温 38.5 ℃。".encode("utf-8")).hexdigest()
    assert first == second
    assert first[0].normalized_hash == expected_hash
    assert first[0].span_id == second[0].span_id


def test_identical_text_in_different_reports_has_distinct_span_ids():
    spans = segment_reports([{"text": "无发热。"}, {"text": "无发热。"}])

    assert len(spans) == 2
    assert spans[0].normalized_hash == spans[1].normalized_hash
    assert spans[0].span_id != spans[1].span_id


def test_empty_and_whitespace_only_reports_produce_no_spans():
    assert segment_reports([]) == ()
    assert segment_reports([{}, {"text": ""}, {"text": " \t\r\n "}, {"text": None}]) == ()


def test_span_model_has_no_stable_patient_identifier_field():
    field_names = {field.name for field in fields(EvidenceSpan)}

    assert field_names.isdisjoint({"patient_id", "patient_identifier", "subject_id"})


def test_chinese_punctuation_semicolon_and_newline_are_deterministic_boundaries():
    reports = [{"text": "甲。乙！丙？丁；戊\n己\r\n庚"}]

    spans = segment_reports(reports)

    assert [span.text for span in spans] == ["甲。", "乙！", "丙？", "丁；", "戊", "己", "庚"]
    assert [(span.start_offset, span.end_offset) for span in spans] == [
        (0, 2),
        (2, 4),
        (4, 6),
        (6, 8),
        (8, 9),
        (10, 11),
        (13, 14),
    ]


def test_evidence_packet_preserves_span_provenance_without_copying_patient_id():
    spans = segment_reports(
        [{"text": "意识清楚。", "topic": "查房", "timestamp": "2026-09-15"}]
    )

    packet = EvidencePacket(spans=spans)

    assert packet.spans == spans
    assert packet.spans[0].report_index == 0
    assert packet.spans[0].topic == "查房"
    assert packet.spans[0].timestamp == "2026-09-15"
    assert packet.spans[0].start_offset == 0
    assert packet.spans[0].end_offset == 5
    assert not hasattr(packet, "patient_id")
