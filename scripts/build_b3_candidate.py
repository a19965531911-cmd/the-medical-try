"""Build a review-only B3 by appending verified guards to frozen B2E Libraries."""
import base64
import hashlib
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.build_b_submission import load_rows,parse_submission,submission_sanity_check

BASELINE=ROOT/"experiment/b2-official-contract/B2E.json"


def build_b3():
    manifest=parse_submission((ROOT/"submission/b2_candidate.manifest.json").read_text(encoding="utf8"))
    if hashlib.sha256(BASELINE.read_bytes()).hexdigest()!=manifest["sha256"]:
        raise ValueError("B2E hash no longer matches frozen manifest")
    bundle=parse_submission(BASELINE.read_text(encoding="utf8"))
    overlay=(ROOT/"src/b_board/b3_overlay.py").read_text(encoding="utf8")
    for entry in bundle["entry"][1:]:
        library=entry["resource"]
        original=base64.b64decode(library["content"][0]["data"],validate=True).decode("utf8")
        source=original+"\n"+overlay
        compile(source,library["name"],"exec")
        library["content"][0]["data"]=base64.b64encode(source.encode()).decode("ascii")
    submission_sanity_check(bundle,load_rows())
    return bundle
