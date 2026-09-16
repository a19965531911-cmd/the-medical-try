from v43.extraction.deterministic import extract_deterministic
criterion_id = "745"
def build_constraints(ir):
    return (
        {"constraint_id": "surgery", "operator": "required_present", "event_type": "Surgery", "event_alias": "surgery"},
        {"constraint_id": "ventilation", "operator": "required_present", "event_type": "MechanicalVentilation", "event_alias": "ventilation"},
        {"constraint_id": "invasive", "operator": "required_present", "event_alias": "ventilation", "event_attribute": "invasive"},
        {"constraint_id": "postoperative", "operator": "relation_required", "source_node": "ventilation", "target_node": "surgery", "relation_type": "POSTOPERATIVE_TO"},
        {"constraint_id": "root", "operator": "AND", "input_node_ids": ("surgery", "ventilation", "invasive", "postoperative")},
    )
def extract(packet): return extract_deterministic(type("IR", (), {"criterion_id": criterion_id})(), packet)
