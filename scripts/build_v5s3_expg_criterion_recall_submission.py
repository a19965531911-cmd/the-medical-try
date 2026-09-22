import base64
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.build_v5s2_expe_aggressive_submission import build_source as build_expe_source
from v5s.expg_overlay import EXPG_SOURCE


TARGETS = {"485", "635", "855", "675", "735", "745"}
SHELL = ROOT / "submission/a_test_message_bundle_v5s1_candidate.json"
OUT = ROOT / "submission/a_test_message_bundle_v5s3_expg_criterion_recall_candidate.json"


def build_source(cid, title, identifier):
    source = build_expe_source(str(cid), title, identifier)
    if str(cid) in TARGETS:
        source += EXPG_SOURCE
    compile(source, title, "exec")
    return source


def main():
    bundle = json.loads(SHELL.read_text(encoding="utf-8"))
    count = 0
    for entry in bundle["entry"]:
        resource = entry["resource"]
        if resource.get("resourceType") != "Library":
            continue
        cid = str(resource["content"][0]["title"])
        source = build_source(cid, resource["name"], resource.get("identifier", {}))
        resource["content"][0]["data"] = base64.b64encode(source.encode("utf-8")).decode("ascii")
        count += 1
    assert count == 16
    OUT.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    print(OUT, OUT.stat().st_size)


if __name__ == "__main__":
    main()
