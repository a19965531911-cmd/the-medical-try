from __future__ import annotations
import ast, base64, json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from v5.criterion_specs import CRITERION_IDS, load_criterion_specs

INPUT=ROOT.parent/"CHIP2026_CP2_A_baseline_v2_4_3"/"submission"/"a_test_message_bundle_v2_4_3.json"
OUT=ROOT/"submission"/"a_test_message_bundle_v5a_candidate.json"
MODULES=("v43.fhir.contracts","v5.models","v5.response_parser","v5.retrieval","v5.prompt","v5.transport","v5.deterministic","v5.guards","v5.matcher","v5.payload_extractors","v5.fhir_adapter","v5.criterion_specs","v5.runtime")

def source_for(module):
 if module == "v5.criterion_specs":
  specs=load_criterion_specs(); args=[]
  for cid in CRITERION_IDS:
   s=specs[cid]; args.append(repr(cid)+":CriterionSpec("+",".join(repr(getattr(s,f)) for f in s.__dataclass_fields__)+")")
  return "CRITERION_IDS="+repr(CRITERION_IDS)+"\ndef load_criterion_specs():\n return {"+",".join(args)+"}\n"
 return (ROOT/"src"/Path(*module.split(".")).with_suffix(".py")).read_text(encoding="utf-8")

def definitions(tree):
 out=set()
 for node in tree.body:
  if isinstance(node,(ast.FunctionDef,ast.ClassDef)): out.add(node.name)
  elif isinstance(node,(ast.Assign,ast.AnnAssign)):
   for target in node.targets if isinstance(node,ast.Assign) else (node.target,):
    if isinstance(target,ast.Name): out.add(target.id)
 return out

def imports(module,tree):
 out={}
 for node in tree.body:
  if isinstance(node,ast.ImportFrom) and (node.level or (node.module or "").startswith(("v5","v43"))):
   if node.level:
    base=module.split(".")[:-node.level]; target=".".join(base+(([node.module] if node.module else [])))
   else: target=node.module
   for item in node.names: out[item.asname or item.name]=(target,item.name)
 return out

class Flat(ast.NodeTransformer):
 def __init__(self,prefix,own,imp,mapping): self.prefix=prefix; self.own=own; self.imp=imp; self.mapping=mapping
 def visit_ImportFrom(self,node): return None if node.level or (node.module or "").startswith(("v5","v43")) else node
 def visit_Name(self,node):
  if node.id in self.own: node.id=self.prefix+node.id
  elif node.id in self.imp: node.id=self.mapping.get(self.imp[node.id],node.id)
  return node
 def visit_FunctionDef(self,node):
  name=node.name; node=self.generic_visit(node); node.name=self.prefix+name if name in self.own else name; return node
 def visit_ClassDef(self,node):
  name=node.name; node=self.generic_visit(node); node.name=self.prefix+name if name in self.own else name; return node

def flatten():
 trees={m:ast.parse(source_for(m),filename=m) for m in MODULES}; defs={m:definitions(t) for m,t in trees.items()}; mapping={(m,n):f"z{i}_{n}" for i,m in enumerate(MODULES) for n in defs[m]}; parts=[]
 for i,m in enumerate(MODULES):
  tree=Flat(f"z{i}_",defs[m],imports(m,trees[m]),mapping).visit(trees[m]); ast.fix_missing_locations(tree); parts.append(ast.unparse(tree))
 parts.append("LocalModelTransport="+mapping[("v5.transport","LocalModelTransport")]+"\nevaluate_and_compile="+mapping[("v5.runtime","evaluate_and_compile")])
 return "\n".join(parts)

BOOT=r'''
ENGINE_VERSION="v5a-pragmatic-matcher-flattened"
V5_MATCHER_AUTHORITY=True
V4_TYPED_SEMANTIC_GRAPH_AUTHORITY=False
class FHIRResourceBundleGenerator:
 profile_id=PROFILE
 identifier=IDENTIFIER
 def __init__(self,fhir_api_base): self.fhir_api_base=fhir_api_base; self.transport=LocalModelTransport()
 def parse_clinical_text_to_fhir_bundle(self,patient_id,case_reports,ai_algorithm_type="nlp"):
  result=evaluate_and_compile(str(TITLE),str(patient_id),case_reports,self.transport)
  print("V5_METRICS criterion="+str(TITLE)+" decision="+result.match.final_decision.value+" resources="+str(len(result.resources))+" reason="+str(result.reason_code))
  return {"resourceType":"Bundle","type":"transaction","entry":[{"resource":r,"request":{"method":"POST","url":r["resourceType"]}} for r in result.resources]}
'''
def constants(source):
 lines=[x for x in source.splitlines() if x.startswith(("PROFILE=","IDENTIFIER=","RESOURCE_TYPE="))]
 if len(lines)!=3: raise ValueError("library constants missing")
 return "\n".join(lines)+"\n"
def main():
 bundle=json.loads(INPUT.read_text(encoding="utf-8")); runtime=flatten()+"\n"+BOOT; entries=[]
 for entry in bundle["entry"]:
  resource=json.loads(json.dumps(entry["resource"]))
  if resource.get("resourceType") == "Library":
   old=base64.b64decode(resource["content"][0]["data"]).decode("utf-8"); title=str(resource["content"][0]["title"]); source=constants(old)+"TITLE="+repr(title)+"\n"+runtime; compile(source,resource["name"],"exec"); resource["content"][0]["data"]=base64.b64encode(source.encode()).decode()
  entries.append({**entry,"resource":resource})
 OUT.write_text(json.dumps({**bundle,"entry":entries},ensure_ascii=False,indent=2),encoding="utf-8"); print(OUT,OUT.stat().st_size)
if __name__ == "__main__": main()
