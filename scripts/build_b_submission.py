"""Build B Libraries from workbook identities and frozen E runtime primitives."""
import argparse
import ast
import base64
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / "src"))
from b_board.runtime import B_IDS, REQUIRED, PATTERNS

DEFAULT_INPUT = Path(r"C:\Users\32433\Desktop\CHIP2026-CP2-data-test_b.xlsx")
CHAMPION = ROOT / "submission/a_test_message_bundle_v5s2_expe_aggressive_candidate.json"
OUT = ROOT / "submission/b_test_message_bundle_b1_candidate.json"


def load_rows(path=DEFAULT_INPUT):
    import openpyxl
    with Path(path).open("rb") as stream:
        workbook = openpyxl.load_workbook(stream,read_only=True,data_only=True)
        sheet = workbook["criterions"]
        values = list(sheet.values)
        rows = [dict(zip(values[0],r)) for r in values[1:] if any(x is not None for x in r)]
        workbook.close()
    if tuple(str(r["profile_id"]) for r in rows) != B_IDS:
        raise ValueError("Unexpected B criterion count, order or profile IDs")
    for row in rows:
        for column in ("question","deepquery_id","FHIR_FSH","NLP_CODE","FHIR_SERVICE_CODE"):
            if not isinstance(row[column],str) or not row[column].strip():
                raise ValueError("Missing " + column)
        # Parse only: workbook code is data, never instructions or a build-time command.
        ast.parse(row["NLP_CODE"])
        ast.parse(row["FHIR_SERVICE_CODE"])
    return rows


def frozen_primitives():
    champion = json.loads(CHAMPION.read_text(encoding="utf-8"))
    source = base64.b64decode(champion["entry"][1]["resource"]["content"][0]["data"],validate=True).decode("utf-8")
    tree = ast.parse(source)
    names = ("normalize_reports","split_text","EvidenceWindows","_expe_spec","retrieve_evidence")
    nodes = {node.name:node for node in tree.body if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name in names}
    method = next(node for cls in tree.body if isinstance(cls,ast.ClassDef) for node in cls.body if isinstance(node,ast.FunctionDef) and node.name == "_transport")
    # E used 32 tokens for YES/NO; structured B fact extraction needs a larger response.
    class Budget(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value) is int and node.value == 32:
                return ast.copy_location(ast.Constant(value=1024),node)
            return node
    method = Budget().visit(copy.deepcopy(method))
    # B IDs have no entries in E's A-only alias overrides.
    return "_EXPE_ALIASES={}\n_EXPE_GROUPS={}\n"+"\n\n".join(ast.unparse(nodes[n]) for n in names),ast.unparse(method)


WRAPPER = '''
class FHIRResourceBundleGenerator:
    def __init__(self, fhir_api_base):
        self.fhir_api_base = fhir_api_base
        self.transport = self._transport

__TRANSPORT__

    def parse_clinical_text_to_fhir_bundle(self, patient_id, case_reports, ai_algorithm_type="nlp"):
        if not isinstance(case_reports, (list, tuple)):
            raise ValueError("case_reports must be a list")
        reports = [dict(r) if isinstance(r,dict) else {"text":str(r)} for r in case_reports]
        result = evaluate(TITLE, reports)
        if not result["match"] and not any(f["state"] in {"NEGATED","ABSENT","PLANNED","UNCERTAIN"} for f in result["facts"].values()):
            normalized = normalize_reports(reports)
            windows = retrieve_evidence(normalized, SPEC)
            if windows.metrics["true_anchor_hits"]:
                # Include full selected records for distributed evidence and stable indices.
                selected = sorted({w["report"] for w in windows})
                selected_reports = [reports[i] for i in selected]
                local_result = evaluate(TITLE, selected_reports)
                rescued = semantic_rescue(TITLE,selected_reports,local_result,self.transport,QUESTION)
                if rescued["match"]:
                    for fact in rescued["facts"].values():
                        if fact.get("report") is not None:
                            fact["report"] = selected[fact["report"]]
                    result = rescued
        resources = build_b_resources(TITLE,str(patient_id),reports,result)
        self.last_result = dict(result, emitted_resources=len(resources))
        print("B1_METRICS|criterion="+TITLE+"|decision="+result["decision"]+"|resources="+str(len(resources))+"|reason="+result["reason"])
        return {"resourceType":"Bundle","type":"transaction","entry":[{"resource":r,"request":{"method":"POST","url":r["resourceType"]}} for r in resources]}
'''


def build_source(row):
    cid = str(row["profile_id"])
    shared,transport = frozen_primitives()
    aliases = [word for atom in REQUIRED[cid] for word in re_aliases(PATTERNS.get(atom,""))]
    spec = {"aliases":aliases or [row["question"]],"groups":[aliases or [row["question"]]]}
    source = "import re,json\nfrom urllib.request import Request,urlopen\n"
    source += "TITLE="+repr(cid)+"\nQUESTION="+repr(row["question"])+"\nSPEC="+repr(spec)+"\n"
    source += shared+"\n"+(ROOT/"src/b_board/runtime.py").read_text(encoding="utf-8")
    source += WRAPPER.replace("__TRANSPORT__","\n".join("    "+line for line in transport.splitlines()))
    compile(source,"cnwqk"+cid,"exec")
    return source


def re_aliases(pattern):
    import re
    # Literal aliases only affect semantic retrieval; deterministic parsing sees all records.
    return [part for part in pattern.split("|") if part and not re.search(r"[\\()[?*+{}^$]",part)]


def build_bundle(rows):
    shell = json.loads(CHAMPION.read_text(encoding="utf-8"))
    template = shell["entry"][1]["resource"]
    shell["entry"] = [copy.deepcopy(shell["entry"][0])]
    for row in rows:
        cid = str(row["profile_id"])
        library = copy.deepcopy(template)
        library["id"] = row["id"] if row["id"] != "tbd" else "cnwqk"+cid
        library["name"] = "cnwqk"+cid
        library["identifier"] = [{"value":str(row["index"]) if row["index"] is not None else "profile-"+cid},{"system":"urn:chip:deepquery-id","value":row["deepquery_id"]}]
        library["content"] = [{"contentType":"text/x-python","title":cid,"data":base64.b64encode(build_source(row).encode("utf-8")).decode("ascii")}]
        shell["entry"].append({"resource":library})
    submission_sanity_check(shell,rows)
    return shell


def submission_sanity_check(bundle, rows):
    def fail(message):
        raise ValueError(message)
    if bundle.get("resourceType") != "Bundle" or bundle.get("type") != "message":
        fail("Not a message Bundle")
    entries = bundle.get("entry",[])
    if len(entries) != 17 or entries[0]["resource"].get("resourceType") != "MessageHeader":
        fail("Expected one MessageHeader and 16 Libraries")
    seen_ids,seen_queries,seen_indexes = set(),set(),set()
    for entry,row in zip(entries[1:],rows):
        r = entry["resource"]
        cid = str(row["profile_id"])
        if r.get("resourceType") != "Library" or r.get("name") != "cnwqk"+cid:
            fail("Invalid Library routing")
        if r.get("id") in seen_ids or r.get("id") in (None,"tbd",""):
            fail("Duplicate or unresolved Library id")
        expected_id = row["id"] if row["id"] != "tbd" else "cnwqk"+cid
        if r["id"] != expected_id:
            fail("Workbook Library id mismatch")
        seen_ids.add(r["id"])
        identifiers = r.get("identifier",[])
        query = next((x["value"] for x in identifiers if x.get("system")=="urn:chip:deepquery-id"),None)
        if query != row["deepquery_id"] or query in seen_queries:
            fail("Deepquery mapping mismatch")
        seen_queries.add(query)
        index = identifiers[0].get("value")
        expected_index = str(row["index"]) if row["index"] is not None else "profile-"+cid
        if index != expected_index:
            fail("Workbook index mismatch")
        if index in seen_indexes or index in (None,"None","null",""):
            fail("Missing or duplicate identifier")
        seen_indexes.add(index)
        content = r.get("content",[])
        if len(content)!=1 or content[0].get("title")!=cid or content[0].get("contentType")!="text/x-python":
            fail("Invalid source attachment")
        source = base64.b64decode(content[0]["data"],validate=True).decode("utf-8")
        tree = ast.parse(source)
        title = next((ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="TITLE" for t in n.targets)),None)
        if title!=cid:
            fail("Embedded criterion mismatch")
        compile(source,cid,"exec")
    serialized = json.dumps(bundle,ensure_ascii=False,allow_nan=False)
    if json.loads(serialized) != bundle:
        fail("JSON roundtrip mismatch")
    return {"libraries":16,"unique_ids":16,"deepquery_ids":16,"local_schema":"PASS","platform_mapping":"UNVERIFIED_FOR_TBD"}


def parse_submission(raw):
    def unique(pairs):
        out = {}
        for key,value in pairs:
            if key in out:
                raise ValueError("Duplicate JSON key: "+key)
            out[key] = value
        return out
    def invalid(value):
        raise ValueError("Invalid JSON constant: "+value)
    return json.loads(raw,object_pairs_hook=unique,parse_constant=invalid)


def publication_gate(bundle, rows):
    """Fail closed on unverified identity mapping; offline candidates remain reviewable."""
    submission_sanity_check(bundle,rows)
    if any(r["id"]=="tbd" or r["index"] is None for r in rows):
        raise ValueError("Publication blocked: official tbd/null routing contract unverified")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,default=DEFAULT_INPUT)
    parser.add_argument("--output",type=Path,default=OUT)
    args = parser.parse_args()
    rows = load_rows(args.input)
    bundle = build_bundle(rows)
    args.output.write_text(json.dumps(bundle,ensure_ascii=False,allow_nan=False,indent=2)+"\n",encoding="utf-8")
    manifest = {"candidate":str(args.output),"sha256":hashlib.sha256(args.output.read_bytes()).hexdigest(),"workbook_sha256":hashlib.sha256(args.input.read_bytes()).hexdigest(),"champion_sha256":hashlib.sha256(CHAMPION.read_bytes()).hexdigest(),"checks":submission_sanity_check(bundle,rows),"routing":[{k:r[k] for k in ("profile_id","id","index","deepquery_id")} for r in rows],"blockers":["Official publication mapping for tbd/null rows 2 and 3 is not documented locally","Official platform checker unavailable","Real patient/query inputs unavailable"]}
    args.output.with_suffix(".manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,allow_nan=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"output":str(args.output),"sha256":manifest["sha256"],"checks":manifest["checks"]},ensure_ascii=False))


if __name__ == "__main__":
    main()
