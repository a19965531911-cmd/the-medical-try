from v43.extraction.deterministic import extract_deterministic
criterion_id = "675"
def build_constraints(ir):
    return (
        {"constraint_id": "age", "operator": "numeric_compare", "concept": "patient_age", "op": ">=", "value": 50, "unit": "year"},
        {"constraint_id": "zoster", "operator": "required_present", "event_type": "Diagnosis", "event_alias": "zoster"},
        {"constraint_id": "location", "operator": "relation_required", "source_node": "zoster", "target_node": "head_face_site", "relation_type": "LOCATED_AT"},
        {"constraint_id": "root", "operator": "AND", "input_node_ids": ("age", "zoster", "location")},
    )
def extract(packet): return extract_deterministic(type("IR", (), {"criterion_id": criterion_id})(), packet)
