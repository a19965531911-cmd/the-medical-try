"""Build V4.3 candidate with a flattened, scanner-safe verified runtime."""
from __future__ import annotations
import ast, base64, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT.parent / "CHIP2026_CP2_A_baseline_v2_4_3" / "submission" / "a_test_message_bundle_v2_4_3.json"
OUT = ROOT / "submission" / "a_test_message_bundle_v4_3_candidate_v3.json"
MODULES = ("v43.clinical.models","v43.retrieval.models","v43.retrieval.segmenter","v43.clinical.store","v43.constraints.values","v43.constraints.boolean","v43.constraints.leaves","v43.constraints.trace","v43.constraints.executor","v43.extraction.grounding","v43.extraction.transport","v43.extraction.semantic","v43.extraction.deterministic","v43.criteria.shared",*(f"v43.criteria.c{x}" for x in ("485","615","265","635","675","735","745","755","855","835","875","805","565","555","185","165")),"v43.fhir.contracts","v43.fhir.compiler","v43.production_runtime")
def path_for(module): return ROOT / "src" / Path(*module.split(".")).with_suffix(".py")

def _definitions(tree):
 names=set()
 for node in tree.body:
  if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)): names.add(node.name)
  elif isinstance(node,(ast.Assign,ast.AnnAssign)):
   targets=node.targets if isinstance(node,ast.Assign) else (node.target,)
   names.update(t.id for t in targets if isinstance(t,ast.Name))
 return names

def _internal_imports(module,tree):
 aliases={}
 for node in tree.body:
  if isinstance(node,ast.ImportFrom) and (node.level or (node.module or "").startswith("v43")):
   if node.level:
    base=module.split(".")[:-node.level]
    target=".".join(base+(([node.module] if node.module else [])))
   else: target=node.module
   for item in node.names: aliases[item.asname or item.name]=(target,item.name)
  elif isinstance(node,ast.Import):
   for item in node.names:
    if item.name.startswith("v43."): aliases[item.asname or item.name.split(".")[-1]]=(item.name,"__module__")
 return aliases

class _Flatten(ast.NodeTransformer):
 def __init__(self,prefix,own,imports,global_map): self.prefix=prefix; self.own=own; self.imports=imports; self.global_map=global_map
 def visit_ImportFrom(self,node):
  return None if node.level or (node.module or "").startswith("v43") else node
 def visit_Import(self,node):
  kept=[x for x in node.names if not x.name.startswith("v43.")]
  return ast.Import(names=kept) if kept else None
 def visit_Name(self,node):
  if node.id in self.own: node.id=self.prefix+node.id
  elif node.id in self.imports: node.id=self.global_map.get(self.imports[node.id],node.id)
  return node
 def visit_FunctionDef(self,node):
  original=node.name; node=self.generic_visit(node); node.name=self.prefix+original if original in self.own else original; return node
 visit_AsyncFunctionDef=visit_FunctionDef
 def visit_ClassDef(self,node):
  original=node.name; node=self.generic_visit(node); node.name=self.prefix+original if original in self.own else original; return node

def flatten():
 parsed={m:ast.parse(path_for(m).read_text(encoding="utf-8"),filename=m) for m in MODULES}
 definitions={m:_definitions(t) for m,t in parsed.items()}
 global_map={(m,name):"m"+str(i)+"_"+name for i,m in enumerate(MODULES) for name in definitions[m]}
 parts=[]
 for module in MODULES:
  idx=MODULES.index(module); tree=_Flatten("m"+str(idx)+"_",definitions[module],_internal_imports(module,parsed[module]),global_map).visit(parsed[module]); ast.fix_missing_locations(tree); parts.append(ast.unparse(tree))
 runtime_prefix="m"+str(MODULES.index("v43.production_runtime"))+"_"
 parts.append("\nAssertionState="+global_map[("v43.clinical.models","AssertionState")]+"\nCallGuard="+global_map[("v43.extraction.semantic","CallGuard")]+"\nClinicalFact="+global_map[("v43.clinical.models","ClinicalFact")]+"\nClinicalEvent="+global_map[("v43.clinical.models","ClinicalEvent")]+"\nClinicalRelation="+global_map[("v43.clinical.models","ClinicalRelation")]+"\nClinicalEpisode="+global_map[("v43.clinical.models","ClinicalEpisode")]+"\nPRODUCTION_TEMPORAL_POLICY_875="+runtime_prefix+"PRODUCTION_TEMPORAL_POLICY_875\nevaluate_and_compile="+runtime_prefix+"evaluate_and_compile\n")
 return "\n".join(parts)
BOOT = r'''
ENGINE_VERSION="v4.3-verified-core-flattened"
from urllib.request import Request,urlopen
class FHIRResourceBundleGenerator:
 profile_id=PROFILE
 identifier=IDENTIFIER
 def __init__(self,fhir_api_base): self.fhir_api_base=fhir_api_base; self._semantic_guard=CallGuard()
 def parse_clinical_text_to_fhir_bundle(self,patient_id,case_reports,ai_algorithm_type="nlp"):
  trace,store,resources=evaluate_and_compile(str(TITLE),patient_id,case_reports,PRODUCTION_TEMPORAL_POLICY_875,call_guard=self._semantic_guard)
  print("V43_PROD_METRICS|title="+str(TITLE)+"|policy875="+PRODUCTION_TEMPORAL_POLICY_875+"|decision="+trace.eligibility_result.value+"|resources="+str(len(resources)))
  return {"resourceType":"Bundle","type":"transaction","entry":[{"resource":r,"request":{"method":"POST","url":r["resourceType"]}} for r in resources]}
'''
def constants(source):
 selected=[line for line in source.splitlines() if line.startswith(("PROFILE=","IDENTIFIER=","RESOURCE_TYPE="))]
 if len(selected)!=3: raise ValueError("library constants missing")
 return "\n".join(selected)+"\n"
def main():
 bundle=json.loads(INPUT.read_text(encoding="utf-8")); runtime=flatten()+"\n"+BOOT; transformed=[]
 for entry in bundle["entry"]:
  resource=json.loads(json.dumps(entry["resource"]))
  if resource.get("resourceType")=="Library":
   old=base64.b64decode(resource["content"][0]["data"]).decode("utf-8"); title=str(resource["content"][0].get("title") or resource.get("name") or resource.get("id")); source=constants(old)+"TITLE="+repr(title)+"\n"+runtime; compile(source,resource["name"],"exec"); resource["content"][0]["data"]=base64.b64encode(source.encode("utf-8")).decode("ascii")
  transformed.append({**entry,"resource":resource})
 OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps({**bundle,"entry":transformed},ensure_ascii=False,indent=2),encoding="utf-8"); print(OUT)
if __name__=="__main__": main()
