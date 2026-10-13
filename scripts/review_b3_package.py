"""Audit the actually submitted B3 and produce an isolated input-boundary repair."""
import ast
import base64
from collections import Counter
import contextlib
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/"src"))
from scripts.build_b_submission import parse_submission,submission_sanity_check,load_rows,publication_gate
from scripts.b2_experiments import r4_structure,fsh_checks
from scripts.audit_b_board import replay_service
from scripts.check_b_submission import CHILD

SOURCE=ROOT/"experiment/b3-final/B3.json"
DEST=ROOT/"experiment/b3-review"


def repaired_bundle():
    manifest=parse_submission((ROOT/"experiment/b3-final/B3.manifest.json").read_text(encoding="utf8"))
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==manifest["sha256"]
    bundle=parse_submission(SOURCE.read_text(encoding="utf8"))
    guard=(ROOT/"src/b_board/b3_input_guard.py").read_text(encoding="utf8")
    for entry in bundle["entry"][1:]:
        resource=entry["resource"]
        source=base64.b64decode(resource["content"][0]["data"],validate=True).decode("utf8")+"\n"+guard
        compile(source,resource["name"],"exec")
        resource["content"][0]["data"]=base64.b64encode(source.encode()).decode("ascii")
    submission_sanity_check(bundle,load_rows())
    return bundle


def namespace(resource):
    result={}
    exec(compile(base64.b64decode(resource["content"][0]["data"]),resource["name"],"exec"),result)
    return result


def replay(ns,data):
    generator=ns["FHIRResourceBundleGenerator"]("http://localhost:3456")
    generator.transport=lambda p:"NO"
    with contextlib.redirect_stdout(io.StringIO()):
        output=generator.parse_clinical_text_to_fhir_bundle("p1",data)
    return output,generator.last_result


def run():
    DEST.mkdir(parents=True,exist_ok=True)
    original=parse_submission(SOURCE.read_text(encoding="utf8"))
    source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    repaired=repaired_bundle()
    (DEST/"B3R.json").write_text(json.dumps(repaired,ensure_ascii=False,allow_nan=False,indent=2)+"\n",encoding="utf8")
    repaired=parse_submission((DEST/"B3R.json").read_text(encoding="utf8"))
    rows=load_rows();row_by_id={str(r["profile_id"]):r for r in rows}
    boundaries=[];syntax=[];new_namespaces={}
    for old,new in zip(original["entry"][1:],repaired["entry"][1:]):
        resource=old["resource"];cid=resource["content"][0]["title"]
        old_ns=namespace(resource);new_ns=namespace(new["resource"]);new_namespaces[cid]=new_ns
        source=base64.b64decode(resource["content"][0]["data"]).decode("utf8")
        versions={}
        for version in (7,8,9,10,11):
            try:
                ast.parse(source,feature_version=(3,version));versions[str(version)]="PASS"
            except SyntaxError as exc:
                versions[str(version)]={"line":exc.lineno,"error":exc.msg}
        syntax.append({"profile_id":cid,"grammar":versions})
        for name,data in (("null_text",[{"text":None}]),("number_text",[{"text":123}]),("null_record",[None]),("empty_record",[{}])):
            record={"profile_id":cid,"case":name}
            try:
                before,_=replay(old_ns,data);record["before"]="PASS"
            except Exception as exc:
                record["before_error"]=type(exc).__name__+": "+str(exc)
            after,_=replay(new_ns,data)
            assert not after["entry"] and not r4_structure(after)
            record["after"]="VALID_EMPTY_TRANSACTION";boundaries.append(record)
    old_results=parse_submission((ROOT/"experiment/b3-final/results.json").read_text(encoding="utf8"))
    comparisons=[]
    for case in old_results["matrix"]:
        cid=case["profile_id"]
        output,result=replay(new_namespaces[cid],case["reports"])
        row=row_by_id[cid]
        assert result["decision"]==case["decision"]
        assert replay_service(row,output)["hit"]==case["service_hit"]
        assert fsh_checks(row,output)==case["fsh_violations"]
        assert not r4_structure(output)
        comparisons.append({"case":case["case"],"decision":result["decision"],"unchanged":True})
    isolated=[]
    for row,entry in zip(rows,repaired["entry"][1:]):
        cid=str(row["profile_id"])
        fixture=next(r for r in old_results["matrix"] if r["case"]==cid+"_positive_0")
        payload={"source":entry["resource"]["content"][0]["data"],"reports":[{"text":None}]+fixture["reports"]}
        child=subprocess.run([sys.executable,"-I","-c",CHILD],input=json.dumps(payload),capture_output=True,text=True,timeout=30,cwd=DEST)
        assert child.returncode==0,child.stderr
        output=parse_submission(child.stdout)
        assert output["entry"] and replay_service(row,output)["hit"]
        isolated.append({"profile_id":cid,"null_plus_positive":"PASS","empty":"PASS"})
    try:
        publication_gate(repaired,rows)
        gate="UNEXPECTED_PASS"
    except ValueError as exc:
        gate=str(exc)
    assert "Publication blocked" in gate
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_hash
    assert original["entry"][0]==repaired["entry"][0]
    summary={"submitted_b3_sha256":source_hash,"b3_unchanged":True,
        "b3r_sha256":hashlib.sha256((DEST/"B3R.json").read_bytes()).hexdigest(),
        "reproduced_input_errors":sum("before_error" in r for r in boundaries),
        "boundary_cases_after_pass":len(boundaries),"existing_cases_unchanged":len(comparisons),
        "isolated_mixed_input_pass":len(isolated),"publication_gate":gate,
        "proven_online_zero_root_cause":False,"fsh_remaining":old_results["summary"]["fsh_violating_cases"]}
    data={"summary":summary,"boundary_cases":boundaries,"python_grammar":syntax,"comparisons":comparisons,"isolated":isolated}
    (DEST/"review.json").write_text(json.dumps(data,ensure_ascii=False,allow_nan=False,indent=2)+"\n",encoding="utf8")
    report=["# Submitted B3 Package Review","",
        "## Findings","",
        "1. Confirmed runtime defect: report text=null or a non-string raises uncaught TypeError in all 16 Libraries. Reproduced 32 failures in 64 boundary cases. A single invalid record can interrupt that patient/criterion call, including records alongside genuine positive evidence. Whether actual B patients contain such records, or the platform aborts a full task after an exception, is unknown. This is not a proven explanation of the zero score.","",
        "2. Publication remains unverified: profile 2/3 identifiers are inherited placeholders, B Header challenge_id is not confirmed, and complete platform/Profile validation is unavailable. No guessed identifier/header change was made.","",
        "3. Existing 18 FSH conflict cases remain. Local mocks replay query behavior but do not reproduce platform resource ingestion, publication routing or complete validation; local PASS never establishes the production chain.","",
        "## Compatibility and Entry Review","",
        "All 16 submitted sources compile/import under the current Python and preserve the final B2 evaluation/build routes. No missing repository import is required by the submitted source. All use assignment-expression syntax, requiring Python >=3.8. The preserved historical A server traceback explicitly references /usr/local/lib/python3.11, so Python 3.7 failure is a conditional compatibility risk, not credible evidence by itself of this B zero. No new platform version is known.","",
        "Header is identical to the A Champion and original B3; unique IDs/Base64/UTF-8/transaction serialization are locally valid under the existing checks. Standard R4 validity of the custom platform message envelope is not certified. Model HTTP errors downgrade to NO; deterministic positives do not require a successful model call. A socket timeout of 30 seconds is not an overall evaluation time guarantee. No actual B timing limit or live model throughput is available.","",
        "## Isolated Repair","",
        "experiment/b3-review/B3R.json appends an input boundary guard only. Invalid text becomes empty evidence, not a fabricated value; valid text and report indexes are retained. Null records are empty records. This preserves the public signature, 16 clinical rules, header and routing metadata. Original A/B1/B2E/B3 files are not overwritten. The repaired review package remains NOT READY and has no online result.","",
        "```json",json.dumps(summary,ensure_ascii=False,indent=2),"```","",
        "Actual serialized B3R was reloaded, tested on all 167 existing cases and executed in 16 Python -I processes with a null record plus genuine positive records. All existing decisions, Service results and subset FSH findings are unchanged. Controlled transport stubs are offline tests, not real model results. The prior entire repository suite was not repeated during this scoped input-boundary review.","",
        "## Conclusion","",
        "A real input-boundary bug is identified and repaired separately. The total online zero is still not explained conclusively. Organizer refusal to provide B logs is accepted; no log is requested as a next-step prerequisite. Official routing/header evidence and checker remain unavailable external dependencies. Do not label this fix a score improvement or automatically resubmit."]
    (ROOT/"reports/B3_SUBMITTED_PACKAGE_REVIEW.md").write_text("\n".join(report)+"\n",encoding="utf8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=="__main__":
    run()
