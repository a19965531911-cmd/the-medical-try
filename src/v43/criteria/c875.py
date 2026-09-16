from v43.extraction.deterministic import extract_deterministic
criterion_id = "875"
def build_constraints(ir):
    return (
        {"constraint_id": "intracranial_hypertension", "operator": "required_present", "concept": "intracranial_hypertension"},
        {"constraint_id": "consciousness_impairment", "operator": "required_present", "concept": "consciousness_impairment"},
        {"constraint_id": "root", "operator": "OR", "input_node_ids": ("intracranial_hypertension", "consciousness_impairment")},
    )
def extract(packet): return extract_deterministic(type("IR", (), {"criterion_id": criterion_id})(), packet)
