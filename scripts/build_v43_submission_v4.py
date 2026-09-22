"""Build V4.3 candidate V4 with reviewed semantic IR prompt context."""
from __future__ import annotations

import base64
import json
from pathlib import Path
import sys

import build_v43_submission_v3 as v3


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from v43.ir.loader import load_criterion_ir
from v43.references import frozen_reference_paths


OUT = ROOT / "submission" / "a_test_message_bundle_v4_3_candidate_v4.json"
SEMANTIC_IDS = ("185", "675", "745", "875")
SEMANTIC_FIELDS = (
    "criterion_id", "title", "original_text", "criterion_type", "clinical_domain",
    "entities", "constraint_semantics", "fact_schema", "event_schema", "relation_schema",
    "relations", "logical_expression", "numeric_constraints", "temporal_constraints",
    "subject_constraints", "negation_constraints", "episode_policy", "temporal_scope",
)


def reviewed_semantic_ir():
    verified = load_criterion_ir(frozen_reference_paths()["criterion_ir_draft"], SEMANTIC_IDS)
    return {
        criterion: {field: verified[criterion].raw[field] for field in SEMANTIC_FIELDS if field in verified[criterion].raw}
        for criterion in SEMANTIC_IDS
    }


def flattened_runtime():
    runtime_prefix = "m" + str(v3.MODULES.index("v43.production_runtime")) + "_"
    return v3.flatten() + "\n" + runtime_prefix + "PRODUCTION_SEMANTIC_IR=" + repr(reviewed_semantic_ir()) + "\n"


def main():
    bundle = json.loads(v3.INPUT.read_text(encoding="utf-8"))
    runtime = flattened_runtime() + "\n" + v3.BOOT
    transformed = []
    for entry in bundle["entry"]:
        resource = json.loads(json.dumps(entry["resource"]))
        if resource.get("resourceType") == "Library":
            old = base64.b64decode(resource["content"][0]["data"]).decode("utf-8")
            title = str(resource["content"][0].get("title") or resource.get("name") or resource.get("id"))
            source = v3.constants(old) + "TITLE=" + repr(title) + "\n" + runtime
            compile(source, resource["name"], "exec")
            resource["content"][0]["data"] = base64.b64encode(source.encode("utf-8")).decode("ascii")
        transformed.append({**entry, "resource": resource})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({**bundle, "entry": transformed}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
