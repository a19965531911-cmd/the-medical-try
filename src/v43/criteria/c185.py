from v43.extraction.deterministic import extract_deterministic
criterion_id = "185"
def build_constraints(ir):
    return (
        {"constraint_id": "administration", "operator": "required_present", "event_type": "MedicationAdministration", "event_alias": "administration"},
        {"constraint_id": "first_use", "operator": "required_present", "event_alias": "administration", "event_attribute": "first_use"},
        {"constraint_id": "planned_only", "operator": "blocking_if_present", "event_alias": "administration", "event_attribute": "planned_only"},
        {"constraint_id": "previous_multiple_use", "operator": "blocking_if_present", "event_alias": "administration", "event_attribute": "previous_multiple_use"},
        {"constraint_id": "root", "operator": "AND", "input_node_ids": ("administration", "first_use", "planned_only", "previous_multiple_use")},
    )
def extract(packet): return extract_deterministic(type("IR", (), {"criterion_id": criterion_id})(), packet)
