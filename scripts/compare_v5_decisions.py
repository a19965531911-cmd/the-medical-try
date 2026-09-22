import json, sys
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from v43.runtime import RuntimeServices, evaluate_criterion
from v5.criterion_specs import load_criterion_specs
from v5.matcher import match_patient
from v5.models import Decision, ParsedDecision, ParseMethod
from v5.transport import TransportResult, TransportStatus

class Unavailable:
 def decide(self,prompt): return TransportResult(TransportStatus.CONNECT_ERROR,ParsedDecision(Decision.UNKNOWN,ParseMethod.PARSE_UNKNOWN),2,0,"error")

def main():
 cases=json.loads((ROOT/"tests/fixtures/v5_matcher_cases.json").read_text(encoding="utf-8")); v4=Counter(); v5=Counter(); recovered=0
 for case in cases:
  old=evaluate_criterion(case["criterion"],case["case_id"],case["reports"],RuntimeServices(None,1.0,"EVER_PRESENT")).decision_trace.eligibility_result.value
  new=match_patient(load_criterion_specs()[case["criterion"]],case["reports"],Unavailable()).final_decision.value
  v4[old]+=1; v5[new]+=1; recovered += old == "INSUFFICIENT_EVIDENCE" and new == "MATCH"
 text="# V5A Decision Delta\n\n- Corpus: 112 synthetic cases\n- V4 totals: `"+str(dict(v4))+"`\n- V5 totals with observed 1213-unavailable state: `"+str(dict(v5))+"`\n- V4 UNKNOWN -> V5 MATCH: "+str(recovered)+"\n- Limitation: real-model recovery delta is not measurable while port 1213 is unavailable.\n"
 (ROOT/"reports/V5A_DECISION_DELTA.md").write_text(text,encoding="utf-8"); print(text)
if __name__ == "__main__": main()
