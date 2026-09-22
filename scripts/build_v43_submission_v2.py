"""Build a self-contained candidate from verified V4.3 core modules."""
from __future__ import annotations
import base64, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT.parent / "CHIP2026_CP2_A_baseline_v2_4_3" / "submission" / "a_test_message_bundle_v2_4_3.json"
OUT = ROOT / "submission" / "a_test_message_bundle_v4_3_candidate_v2.json"
MODULES = ("v43.clinical.models","v43.clinical.store","v43.retrieval.models","v43.retrieval.segmenter","v43.constraints.values","v43.constraints.boolean","v43.constraints.leaves","v43.constraints.trace","v43.constraints.executor","v43.extraction.deterministic","v43.criteria.shared",*(f"v43.criteria.c{x}" for x in ("485","615","265","635","675","735","745","755","855","835","875","805","565","555","185","165")),"v43.fhir.contracts","v43.fhir.compiler","v43.production_runtime")
BOOTSTRAP = r'''ENGINE_VERSION="v4.3-verified-core"
import importlib.abc,importlib.util,sys
class _VerifiedCoreLoader(importlib.abc.MetaPathFinder,importlib.abc.Loader):
 def find_spec(self,fullname,path=None,target=None):
  if fullname in VERIFIED_MODULE_SOURCES:return importlib.util.spec_from_loader(fullname,self,is_package=False)
  if fullname in VERIFIED_PACKAGES:return importlib.util.spec_from_loader(fullname,self,is_package=True)
 def create_module(self,spec):return None
 def exec_module(self,module):
  if module.__name__ in VERIFIED_PACKAGES:module.__path__=[];return
  exec(compile(VERIFIED_MODULE_SOURCES[module.__name__],module.__name__,"exec"),module.__dict__)
sys.meta_path.insert(0,_VerifiedCoreLoader())
from v43.production_runtime import PRODUCTION_TEMPORAL_POLICY_875,evaluate_and_compile
class FHIRResourceBundleGenerator:
 profile_id=PROFILE
 identifier=IDENTIFIER
 def __init__(self,fhir_api_base):self.fhir_api_base=fhir_api_base
 def parse_clinical_text_to_fhir_bundle(self,patient_id,case_reports,ai_algorithm_type="nlp"):
  trace,store,resources=evaluate_and_compile(str(TITLE),patient_id,case_reports,PRODUCTION_TEMPORAL_POLICY_875)
  print("V43_PROD_METRICS|title="+str(TITLE)+"|policy875="+PRODUCTION_TEMPORAL_POLICY_875+"|decision="+trace.eligibility_result.value+"|resources="+str(len(resources)))
  return {"resourceType":"Bundle","type":"transaction","entry":[{"resource":r,"request":{"method":"POST","url":r["resourceType"]}} for r in resources]}
'''
def path_for(module): return ROOT / "src" / Path(*module.split(".")).with_suffix(".py")
def constants(source):
 selected=[line for line in source.splitlines() if line.startswith(("PROFILE=","IDENTIFIER=","RESOURCE_TYPE="))]
 if len(selected)!=3: raise ValueError("library constants missing")
 return "\n".join(selected)+"\n"
def main():
 bundle=json.loads(INPUT.read_text(encoding="utf-8")); sources={m:path_for(m).read_text(encoding="utf-8") for m in MODULES}
 packages={".".join(m.split(".")[:d]) for m in MODULES for d in range(1,len(m.split(".")))}; transformed=[]; count=0
 for entry in bundle["entry"]:
  resource=json.loads(json.dumps(entry["resource"]))
  if resource.get("resourceType")=="Library":
   old=base64.b64decode(resource["content"][0]["data"]).decode("utf-8"); title=str(resource["content"][0].get("title") or resource.get("name") or resource.get("id"))
   source=constants(old)+"TITLE="+repr(title)+"\nVERIFIED_MODULE_SOURCES="+repr(sources)+"\nVERIFIED_PACKAGES="+repr(packages)+"\n"+BOOTSTRAP
   compile(source,resource["name"],"exec"); resource["content"][0]["data"]=base64.b64encode(source.encode("utf-8")).decode("ascii"); count+=1
  transformed.append({**entry,"resource":resource})
 if count!=16: raise ValueError(f"expected 16 Libraries, got {count}")
 OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps({**bundle,"entry":transformed},ensure_ascii=False,indent=2),encoding="utf-8"); print(OUT)
if __name__=="__main__": main()
