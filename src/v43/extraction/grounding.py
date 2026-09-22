from v43.clinical.models import ClinicalEvent, ClinicalFact, ClinicalRelation


def validate_grounding(objects, packet) -> None:
    valid = {span.span_id for span in packet.spans}
    for obj in objects:
        if isinstance(obj, ClinicalFact):
            ids = (obj.evidence_span_id,)
        elif isinstance(obj, (ClinicalEvent, ClinicalRelation)):
            ids = obj.evidence_span_ids
        else:
            raise ValueError("unsupported semantic object")
        if not ids or any(span_id not in valid for span_id in ids):
            raise ValueError("unknown evidence span")
