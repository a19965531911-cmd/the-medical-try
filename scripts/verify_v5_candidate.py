import base64, hashlib, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; PATH=ROOT/"submission/a_test_message_bundle_v5a_candidate.json"
HOST_RE=re.compile(r'''[\'"]([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})[\'"]''')
def main():
 raw=PATH.read_bytes(); bundle=json.loads(raw); libs=[e["resource"] for e in bundle["entry"] if e["resource"].get("resourceType") == "Library"]
 decoded=compiled=secure=0
 for lib in libs:
  source=base64.b64decode(lib["content"][0]["data"],validate=True).decode(); decoded+=1; compile(source,lib["name"],"exec"); compiled+=1
  hits=HOST_RE.findall(source); bad=[x for x in hits if x not in {"127.0.0.1","localhost"}]
  if not bad and "input(" not in source and "VERIFIED_MODULE_SOURCES" not in source: secure+=1
 print(f"LIBRARIES={len(libs)} DECODE={decoded}/16 COMPILE={compiled}/16 SECURITY={secure}/16")
 print("SIZE="+str(len(raw))); print("SHA256="+hashlib.sha256(raw).hexdigest())
if __name__ == "__main__": main()
