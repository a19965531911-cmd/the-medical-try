import json, sys, time
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from v5.criterion_specs import load_criterion_specs
from v5.prompt import build_prompt
from v5.retrieval import select_evidence
from v5.transport import LocalModelTransport, TransportStatus

def main():
 cases=json.loads((ROOT/"tests/fixtures/v5_matcher_cases.json").read_text(encoding="utf-8")); selected=[]
 for cid in load_criterion_specs(): selected.extend([x for x in cases if x["criterion"] == cid][:4])
 transport=LocalModelTransport(timeout=.5); rows=[]
 for case in selected:
  spec=load_criterion_specs()[case["criterion"]]; prompt=build_prompt(spec,select_evidence(spec,case["reports"])); started=time.perf_counter(); result=transport.decide(prompt)
  rows.append({"criterion":case["criterion"],"case_id":case["case_id"],"status":result.status.value,"attempts":result.attempts,"latency_ms":round((time.perf_counter()-started)*1000,2),"shape":result.output_shape,"parse_method":result.parsed.method.value,"decision":result.parsed.decision.value})
 statuses=Counter(x["status"] for x in rows); ok=sum(x["status"] == "OK" for x in rows); parseable=sum(x["decision"] != "UNKNOWN" for x in rows)
 lines=["# V5 Real Local-Model Probe","",f"- Cases: {len(rows)}",f"- Transport success: {ok}/{len(rows)} ({ok/len(rows):.1%})",f"- Parseability: {parseable}/{len(rows)} ({parseable/len(rows):.1%})",f"- Status counts: `{dict(statuses)}`","","Raw patient text and model output are intentionally omitted."]
 (ROOT/"reports/V5_REAL_MODEL_PROBE.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
 (ROOT/"reports/V5_REAL_MODEL_PROBE.json").write_text(json.dumps(rows,indent=2),encoding="utf-8")
 print(lines[2]); print(lines[3]); print(lines[4]); print(lines[5])
 return 0 if ok/len(rows) >= .95 and parseable/len(rows) >= .95 else 2
if __name__ == "__main__": raise SystemExit(main())
