"""Strict package check and fresh-process smoke test of the on-disk B artifact."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"src"))
from scripts.build_b_submission import load_rows,parse_submission,submission_sanity_check,publication_gate,OUT
from scripts.audit_b_board import fixture_reports,replay_service

CHILD = '''import sys,json,base64,io,contextlib
payload=json.load(sys.stdin)
namespace={}
exec(compile(base64.b64decode(payload["source"]),"library","exec"),namespace)
generator=namespace["FHIRResourceBundleGenerator"]("http://localhost:3456/api/fhir/baseDstu4")
generator.transport=lambda prompt:"NO"
with contextlib.redirect_stdout(io.StringIO()):
    bundle=generator.parse_clinical_text_to_fhir_bundle("p1",payload["reports"])
    empty=generator.parse_clinical_text_to_fhir_bundle("p2",[])
assert empty["resourceType"]=="Bundle" and empty["type"]=="transaction" and not empty["entry"]
json.dump(bundle,sys.stdout,ensure_ascii=True,allow_nan=False)
'''


def check(path=OUT):
    import importlib.util
    spec = importlib.util.spec_from_file_location("b_cases",ROOT/"tests/b_board/test_b_board.py")
    cases = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cases)
    rows = load_rows()
    raw = Path(path).read_bytes()
    bundle = parse_submission(raw.decode("utf-8"))
    result = {"sha256":hashlib.sha256(raw).hexdigest(),"package":submission_sanity_check(bundle,rows),"libraries":[],"publication":"BLOCKED"}
    for row,entry in zip(rows,bundle["entry"][1:]):
        cid = str(row["profile_id"])
        reports = fixture_reports(cid,cases.CASES[cid][0][0])
        payload = {"source":entry["resource"]["content"][0]["data"],"reports":reports}
        child = subprocess.run([sys.executable,"-I","-c",CHILD],input=json.dumps(payload,ensure_ascii=True),encoding="utf-8",capture_output=True,timeout=30,cwd=ROOT/"submission")
        if child.returncode:
            raise RuntimeError("Isolated Library failed: "+cid+" "+child.stderr)
        response = parse_submission(child.stdout)
        if response.get("resourceType")!="Bundle" or response.get("type")!="transaction" or not response.get("entry"):
            raise ValueError("Missing positive FHIR output: "+cid)
        for item in response["entry"]:
            r = item["resource"]
            if item["request"]!={"method":"POST","url":r["resourceType"]} or r["subject"]["reference"]!="Patient/p1":
                raise ValueError("Invalid resource request/subject")
        service = replay_service(row,response)
        if not service["hit"]:
            raise ValueError("Official service missed positive candidate: "+cid)
        result["libraries"].append({"profile_id":cid,"isolated_import_constructor_entrypoint":"PASS","official_mock_service_hit":True,"resources":len(response["entry"])})
    try:
        publication_gate(bundle,rows)
    except ValueError as exc:
        result["publication_blocker"] = str(exc)
    result["additional_blockers"] = ["Official platform checker and B patient/query data unavailable","Full FSH validation unresolved for partial OR evidence in 295 and in-progress radiotherapy in 225","Real local-model structured JSON not exercised","Official 625 service conflicts with requested encounter-scoped complete-panel semantics"]
    destination = ROOT/"analysis/B_SUBMISSION_DRY_RUN.json"
    destination.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,default=OUT)
    parser.add_argument("--publication",action="store_true",help="Fail on unresolved publication requirements")
    args = parser.parse_args()
    result = check(args.input)
    if args.publication and result["publication"]!="PASS":
        raise SystemExit(2)
