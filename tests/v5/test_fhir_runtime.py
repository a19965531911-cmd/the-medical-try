import pytest

from v43.fhir.compiler import FHIRCompileResult
from v43.fhir.contracts import contract_for_criterion
from v43.fhir.service_replay import replay_service
from v43.fhir.validator import validate_fhir
from v5.criterion_specs import CRITERION_IDS, load_criterion_specs
from v5.fhir_adapter import build_resources
from v5.models import Decision, ParsedDecision, ParseMethod
from v5.payload_extractors import extract_payload
from v5.runtime import evaluate_and_compile
from v5.transport import TransportResult, TransportStatus


POSITIVE = {
 "165":"已在外院完成两周期化疗", "185":"首次接受伊立替康化疗", "265":"术前cTnI 0.08 ug/L",
 "485":"盆腔器官脱垂 POP-Q III期", "555":"3个月前完成胆囊切除术", "565":"目前严重腹泻",
 "615":"术后病理 pN1", "635":"AST 30上限40 ALT 30上限40 BUN 8上限9 Cr 80上限100",
 "675":"患者70岁确诊头面部带状疱疹", "735":"活动性乙型肝炎", "745":"术后行有创机械通气",
 "755":"机械通气持续30小时", "805":"目前每日吸烟", "835":"目前凝血功能异常",
 "855":"Scr 120 umol/L", "875":"既往发生颅内高压",
}


class MatchTransport:
 def decide(self, prompt):
  return TransportResult(TransportStatus.OK, ParsedDecision(Decision.MATCH, ParseMethod.PARSED_SENTINEL), 1, .01, "choices")


@pytest.mark.parametrize("criterion", CRITERION_IDS)
def test_positive_payload_builds_structural_and_service_visible_fhir(criterion):
 reports=[{"text":POSITIVE[criterion],"timestamp":"2026-01-01"}]
 payload=extract_payload(load_criterion_specs()[criterion], reports, Decision.MATCH)
 assert payload.status == "READY", payload.reason_code
 resources=build_resources(criterion,"p1",payload)
 compiled=FHIRCompileResult("MATCH","COMPILED",resources)
 assert validate_fhir(compiled,contract_for_criterion(criterion)).structural_status == "VALID"
 assert replay_service(resources,contract_for_criterion(criterion).service,"http://localhost:3456",{"p1":"p1"}).status == "SERVICE_HIT"


@pytest.mark.parametrize("text", ["pT3a", "R1", "pN1", "GS 8", "PSA 0.2 ng/mL"])
def test_615_all_five_branches_replay(text):
 payload=extract_payload(load_criterion_specs()["615"],[{"text":text}],Decision.MATCH)
 resources=build_resources("615","p1",payload)
 assert replay_service(resources,contract_for_criterion("615").service,"",{"p1":"p1"}).status == "SERVICE_HIT"


@pytest.mark.parametrize("text,code", [("目前每日吸烟","current-smoker"),("戒烟1年","former-smoker")])
def test_805_two_positive_branches(text,code):
 payload=extract_payload(load_criterion_specs()["805"],[{"text":text}],Decision.MATCH)
 resource=build_resources("805","p1",payload)[0]
 assert resource["valueCodeableConcept"]["coding"][0]["code"] == code
 assert replay_service((resource,),contract_for_criterion("805").service,"",{"p1":"p1"}).status == "SERVICE_HIT"


def test_runtime_records_payload_drop_instead_of_silent_match():
 result=evaluate_and_compile("635","p1",[{"text":"化验结果符合标准但数值未提供"}],MatchTransport())
 assert result.match.final_decision is Decision.MATCH
 assert result.resources == ()
 assert result.reason_code == "MISSING_REQUIRED_LAB_VALUES"
