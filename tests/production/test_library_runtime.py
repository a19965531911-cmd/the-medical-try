import base64
from copy import deepcopy
import inspect
import io
import json
from pathlib import Path
from contextlib import redirect_stdout
from time import perf_counter

import pytest

from v43.fhir.contracts import contract_for_criterion
from v43.fhir.compiler import FHIRCompileResult
from v43.fhir.service_replay import replay_service
from v43.fhir.validator import validate_fhir


ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = ROOT / "submission" / "a_test_message_bundle_v4_3_candidate.json"
SHELL = ROOT.parent / "CHIP2026_CP2_A_baseline_v2_4_3" / "submission" / "a_test_message_bundle_v2_4_3.json"
IDS = ("8", "20", "21", "22", "24", "30", "31", "32", "33", "35", "37", "39", "41", "46", "49", "51")
TITLES = ("485", "615", "265", "635", "675", "735", "745", "755", "855", "835", "875", "805", "565", "555", "185", "165")
TITLE_BY_ID = dict(zip(IDS, TITLES))
POSITIVE = {
    "8": "盆腔器官脱垂，POP-Q III期", "20": "术后病理pN1", "21": "术前cTnI 0.08 μg/L",
    "22": "AST 30 U/L上限40，ALT 50 U/L上限40，BUN 12 mmol/L上限9，Cr 180 umol/L上限100",
    "24": "患者70岁，确诊头面部带状疱疹", "30": "活动性乙型肝炎",
    "31": "术后行有创机械通气", "32": "机械通气持续30小时",
    "33": "Scr 120 μmol/L，BUN 7 mmol/L，ALT 30 U/L上限40，AST 25 U/L上限40",
    "35": "目前凝血功能异常", "37": "目前意识不清", "39": "目前每日吸烟",
    "41": "目前严重腹泻", "46": "3个月前行胆囊切除术",
    "49": "首次接受伊立替康化疗", "51": "转入我院前于当地医院完成2周期化疗",
}
NEGATIVE = {
    "8": "POP-Q II期", "20": "pN0，GS 7", "21": "术后cTnI 0.08 μg/L",
    "22": "AST 30 U/L上限40，ALT 50 U/L上限40，BUN 12 mmol/L上限9，Cr 201 umol/L上限100",
    "24": "母亲70岁患头面部带状疱疹", "30": "乙型肝炎已稳定", "31": "术前计划无创通气",
    "32": "机械通气20小时", "33": "Scr 180 μmol/L，BUN 7 mmol/L，ALT 30 U/L上限40，AST 25 U/L上限40",
    "35": "凝血功能正常", "37": "否认颅内高压，意识清楚", "39": "戒烟2年",
    "41": "严重腹泻已缓解", "46": "8个月前行手术", "49": "拟接受伊立替康化疗",
    "51": "母亲在外院接受化疗",
}
TRANSPORT = {"51": "Procedure", "8": "Observation", "41": "Observation"}


@pytest.fixture(scope="module")
def libraries():
    bundle = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    return bundle, [entry["resource"] for entry in bundle["entry"]
                    if entry["resource"].get("resourceType") == "Library"]


def _load(resource):
    source = base64.b64decode(resource["content"][0]["data"], validate=True).decode("utf-8")
    namespace = {}
    exec(compile(source, resource["name"], "exec"), namespace)
    return source, namespace


def _run(resource, text):
    _, namespace = _load(resource)
    generator = namespace["FHIRResourceBundleGenerator"]("http://127.0.0.1:3456/api/fhir/baseDstu4")
    return generator.parse_clinical_text_to_fhir_bundle(
        "p1", [{"text": text, "timestamp": "2026-01-01", "fixture_source": "synthetic"}])


def test_candidate_preserves_exact_verified_a_shell(libraries):
    candidate, libs = libraries
    source = json.loads(SHELL.read_text(encoding="utf-8"))
    assert candidate["resourceType"] == "Bundle" and candidate["type"] == "message"
    assert sum(e["resource"].get("resourceType") == "MessageHeader" for e in candidate["entry"]) == 1
    assert len(libs) == 16
    assert tuple(str(x["identifier"][0]["value"]) for x in libs) == IDS
    assert tuple(str(x["content"][0]["title"]) for x in libs) == TITLES
    assert tuple(x["name"] for x in libs) == tuple("cnwqk" + title for title in TITLES)
    assert [e["resource"].get("resourceType") for e in candidate["entry"]] == [e["resource"].get("resourceType") for e in source["entry"]]
    normalized_candidate = deepcopy(candidate)
    normalized_source = deepcopy(source)
    for bundle in (normalized_candidate, normalized_source):
        for entry in bundle["entry"]:
            if entry["resource"].get("resourceType") == "Library":
                entry["resource"]["content"][0]["data"] = "<library-source>"
    assert normalized_candidate == normalized_source


@pytest.mark.parametrize("identifier", IDS)
def test_each_library_decodes_compiles_constructs_and_runs_positive_and_negative(libraries, identifier):
    _, libs = libraries
    resource = next(x for x in libs if str(x["identifier"][0]["value"]) == identifier)
    source, namespace = _load(resource)
    assert "pytest" not in source and "v43.shadow" not in source and "yaml" not in source
    cls = namespace["FHIRResourceBundleGenerator"]
    assert tuple(inspect.signature(cls.parse_clinical_text_to_fhir_bundle).parameters) == (
        "self", "patient_id", "case_reports", "ai_algorithm_type")
    positive = _run(resource, POSITIVE[identifier])
    negative = _run(resource, NEGATIVE[identifier])
    json.dumps(positive, ensure_ascii=False)
    assert positive["resourceType"] == "Bundle" and positive["type"] == "transaction"
    assert positive["entry"]
    assert not negative["entry"]
    assert all(entry["request"] == {"method": "POST", "url": entry["resource"]["resourceType"]}
               for entry in positive["entry"])
    if identifier in TRANSPORT:
        assert {entry["resource"]["resourceType"] for entry in positive["entry"]} == {TRANSPORT[identifier]}


@pytest.mark.parametrize("identifier", IDS)
def test_each_library_isolates_empty_and_malformed_reports(libraries, identifier):
    _, libs = libraries
    resource = next(x for x in libs if str(x["identifier"][0]["value"]) == identifier)
    _, namespace = _load(resource)
    generator = namespace["FHIRResourceBundleGenerator"]("http://unavailable.invalid")
    for reports in ([], [{}, None, "bad"], [{"text": "中文否认相关病史"}]):
        result = generator.parse_clinical_text_to_fhir_bundle("p1", reports)
        assert result == {"resourceType": "Bundle", "type": "transaction", "entry": []}


@pytest.mark.parametrize("identifier", IDS)
def test_each_positive_library_bundle_replays_against_audited_service_contract(libraries, identifier):
    _, libs = libraries
    resource = next(x for x in libs if str(x["identifier"][0]["value"]) == identifier)
    bundle = _run(resource, POSITIVE[identifier])
    resources = tuple(entry["resource"] for entry in bundle["entry"])
    contract = contract_for_criterion(TITLE_BY_ID[identifier])
    assert replay_service(resources, contract.service, "fixture://fhir", {"p1": "doc"}).status == "SERVICE_HIT"
    assert replay_service(resources, contract.service, "fixture://fhir", {"other": "doc"}).status == "SERVICE_MISS"


@pytest.mark.parametrize("identifier", IDS)
def test_each_positive_library_bundle_is_structurally_valid(libraries, identifier):
    _, libs = libraries
    resource = next(x for x in libs if str(x["identifier"][0]["value"]) == identifier)
    bundle = _run(resource, POSITIVE[identifier])
    resources = tuple(entry["resource"] for entry in bundle["entry"])
    contract = contract_for_criterion(TITLE_BY_ID[identifier])
    result = FHIRCompileResult("SATISFIED", "COMPILED", resources)
    assert validate_fhir(result, contract).structural_status == "VALID"


def test_semantic_policy_is_zero_calls_when_deterministic_suffices_and_one_call_on_fallback(libraries):
    _, libs = libraries
    resource = next(x for x in libs if str(x["identifier"][0]["value"]) == "37")
    _, namespace = _load(resource)
    calls = []

    def transport(text, criterion, schema):
        calls.append((text, criterion, tuple(schema)))
        raise TimeoutError("controlled offline")

    decision, _ = namespace["evaluate_patient"](
        "p1", [{"text": POSITIVE["37"]}], "37", llm_transport=transport)
    assert decision["satisfied"] is True
    assert calls == []

    decision, _ = namespace["evaluate_patient"](
        "p2", [{"text": "神志情况待进一步评估"}, {"text": "仍需评估神志"}],
        "37", llm_transport=transport)
    assert decision["satisfied"] is False
    assert len(calls) == 1


def test_malformed_semantic_payload_degrades_to_empty_bundle(libraries):
    _, libs = libraries
    resource = next(x for x in libs if str(x["identifier"][0]["value"]) == "37")
    _, namespace = _load(resource)
    decision, ledger = namespace["evaluate_patient"](
        "p1", [{"text": "神志情况待进一步评估"}], "37",
        llm_transport=lambda *_: {"not_atoms": {}})
    assert decision["satisfied"] is False
    assert namespace["build_typed_resources"]("p1", ledger, decision, "2026-01-01T00:00:00Z") == []


def test_sixteen_by_fifty_runtime_has_no_exceptions_or_semantic_calls(libraries):
    _, libs = libraries
    runtimes = []
    for resource in libs:
        identifier = str(resource["identifier"][0]["value"])
        _, namespace = _load(resource)
        generator = namespace["FHIRResourceBundleGenerator"]("http://unavailable.invalid")
        runtimes.append((identifier, namespace, generator))

    start = perf_counter()
    with redirect_stdout(io.StringIO()):
        for identifier, namespace, generator in runtimes:
            for call in range(50):
                result = generator.parse_clinical_text_to_fhir_bundle(
                    f"p{call}", [{"text": POSITIVE[identifier], "timestamp": "2026-01-01"}])
                assert result["entry"]
            assert namespace["COUNTERS"]["llm_calls"] == 0
    elapsed = perf_counter() - start
    assert elapsed < 15
