from v43.extraction.deterministic import extract_deterministic


CONSTRAINTS = {
    "165": (("chemo", "required_present", "event", "MedicationAdministration"), ("outside", "required_present", "attr", "outside_hospital")),
    "265": (("ctni", "numeric_compare", "ctni", ">=", 0.06, "ug/L"), ("ctnt", "numeric_compare", "ctnt", ">=", 0.03, "ug/L")),
    "485": (("pop", "required_present", "pelvic_organ_prolapse"), ("stage", "required_present", "popq_high_grade")),
    "555": (("recent", "numeric_compare", "surgery_months", "<=", 6, "month"),),
    "565": (("diarrhea", "required_present", "severe_diarrhea"), ("constipation", "required_present", "severe_constipation")),
    "615": (("pt", "required_present", "pt_high"), ("r1", "required_present", "margin_r1"), ("pn", "required_present", "pn1"), ("gs", "numeric_compare", "gleason_score", ">=", 8, "score"), ("psa", "numeric_compare", "psa", ">", 0.1, "ng/mL")),
    "635": (("ast", "numeric_compare", "AST_ratio", "<=", 2, "ratio"),
            ("alt", "numeric_compare", "ALT_ratio", "<=", 2, "ratio"),
            ("bun", "numeric_compare", "BUN_ratio", "<=", 2, "ratio"),
            ("cr", "numeric_compare", "Cr_ratio", "<=", 2, "ratio")),
    "735": (("active", "required_present", "active_target_disease"),),
    "755": (("duration", "numeric_compare", "ventilation_duration", ">=", 24, "h"),),
    "805": (("current", "required_present", "current_smoker"), ("recent", "numeric_compare", "cessation_elapsed", "<", 2, "year")),
    "835": (("abnormal", "required_present", "coagulation_abnormality"),),
    "855": (("scr", "numeric_compare", "Scr", "<", 178, "umol/L"), ("bun", "numeric_compare", "BUN", "<", 9, "mmol/L"), ("alt", "numeric_compare", "ALT_ratio", "<=", 1, "ratio"), ("ast", "numeric_compare", "AST_ratio", "<=", 1, "ratio")),
}

OR_CRITERIA = {"265", "565", "615", "805"}


def build_constraints(criterion_id):
    nodes = []
    for item in CONSTRAINTS[criterion_id]:
        node_id, operator, *args = item
        if operator == "numeric_compare":
            concept, op, value, unit = args
            nodes.append({"constraint_id": node_id, "operator": operator, "concept": concept,
                          "op": op, "value": value, "unit": unit})
        elif args[0] == "event":
            nodes.append({"constraint_id": node_id, "operator": operator,
                          "event_type": args[1], "event_alias": "treatment"})
        elif args[0] == "attr":
            nodes.append({"constraint_id": node_id, "operator": operator,
                          "event_alias": "treatment", "event_attribute": args[1]})
        else:
            nodes.append({"constraint_id": node_id, "operator": operator, "concept": args[0]})
    nodes.append({"constraint_id": "root", "operator": "OR" if criterion_id in OR_CRITERIA else "AND",
                  "input_node_ids": tuple(node["constraint_id"] for node in nodes)})
    return tuple(nodes)


def extract(criterion_id, packet):
    return extract_deterministic(type("IR", (), {"criterion_id": criterion_id})(), packet)
