import base64,json,sys
from pathlib import Path
ROOT=Path(__file__).parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/"src"))
from scripts.build_v5s_submission import build_source as build_frozen_source
from v5s.expc_overlay import OVERLAY_SOURCE
from v5s.expe_overlay import EXPE_FINAL_SOURCE,EXPE_OVERLAY_SOURCE
TARGETS={"265","555","755","805","855"};SHELL=ROOT/"submission/a_test_message_bundle_v5s1_candidate.json";OUT=ROOT/"submission/a_test_message_bundle_v5s2_expe_aggressive_candidate.json"
def build_source(cid,title,identifier):
    source=build_frozen_source(str(cid),title,identifier)+EXPE_OVERLAY_SOURCE
    if str(cid) in TARGETS:source+=OVERLAY_SOURCE
    source+=EXPE_FINAL_SOURCE;compile(source,title,"exec");return source
def main():
    bundle=json.loads(SHELL.read_text(encoding="utf-8"));count=0
    for e in bundle["entry"]:
        r=e["resource"]
        if r.get("resourceType")!="Library":continue
        cid=str(r["content"][0]["title"]);src=build_source(cid,r["name"],r.get("identifier",{}));r["content"][0]["data"]=base64.b64encode(src.encode("utf-8")).decode("ascii");count+=1
    assert count==16;OUT.write_text(json.dumps(bundle,ensure_ascii=False,indent=2),encoding="utf-8",newline="\n");print(OUT,OUT.stat().st_size)
if __name__=="__main__":main()
