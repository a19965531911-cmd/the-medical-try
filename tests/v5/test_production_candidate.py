import base64, json, re
from copy import deepcopy
from pathlib import Path

ROOT=Path(__file__).parents[2]
CAND=ROOT/"submission/a_test_message_bundle_v5a_candidate.json"
SHELL=ROOT.parent/"CHIP2026_CP2_A_baseline_v2_4_3/submission/a_test_message_bundle_v2_4_3.json"
HOST_RE=re.compile(r'''[\'"]([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})[\'"]''')

def libraries(bundle): return [e["resource"] for e in bundle["entry"] if e["resource"].get("resourceType") == "Library"]
def decoded():
 bundle=json.loads(CAND.read_text(encoding="utf-8")); return bundle,[(x,base64.b64decode(x["content"][0]["data"],validate=True).decode()) for x in libraries(bundle)]

def test_exact_shell_and_16_libraries():
 candidate,pairs=decoded(); source=json.loads(SHELL.read_text(encoding="utf-8")); a=deepcopy(candidate); b=deepcopy(source)
 for bundle in (a,b):
  for entry in bundle["entry"]:
   if entry["resource"].get("resourceType") == "Library": entry["resource"]["content"][0]["data"]="X"
 assert a == b and len(pairs) == 16

def test_all_decode_compile_and_contain_v5_runtime():
 for resource,source in decoded()[1]:
  compile(source,resource["name"],"exec")
  for marker in ("v5a-pragmatic-matcher-flattened","127.0.0.1:1213","local-model","V5_MATCHER_AUTHORITY=True","V4_TYPED_SEMANTIC_GRAPH_AUTHORITY=False"):
   assert marker in source
  assert "VERIFIED_MODULE_SOURCES" not in source and "_VerifiedCoreLoader" not in source

def test_security_preflight_all_16():
 for _,source in decoded()[1]:
  assert "input(" not in source
  hits=HOST_RE.findall(source)
  unauthorized=[x for x in hits if x not in {"127.0.0.1","localhost"}]
  assert not [x for x in unauthorized if x.startswith("v43.") or x.startswith("v5.")]
  assert not unauthorized
