import base64
import json
from pathlib import Path

import pytest

from v43.clinical.store import ClinicalStore
from v43.constraints.executor import execute
from v43.ir.loader import load_criterion_ir
from v43.references import frozen_reference_paths
from v43.retrieval.retriever import retrieve
from v43.runtime import RuntimeServices, evaluate_criterion


ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = ROOT / "submission" / "a_test_message_bundle_v4_3_candidate.json"
IDS = ("8", "20", "21", "22", "24", "30", "31", "32", "33", "35", "37", "39", "41", "46", "49", "51")
TITLE_BY_ID = dict(zip(IDS, ("485", "615", "265", "635", "675", "735", "745", "755", "855", "835", "875", "805", "565", "555", "185", "165")))


POSITIVE = {
    "8": "盆腔器官脱垂，POP-Q III期", "20": "术后病理pN1", "21": "术前cTnI 0.08 μg/L",
    "22": "AST 30 U/L上限40，ALT 30 U/L上限40，BUN 8 mmol/L上限9，Cr 80 umol/L上限100",
    "24": "患者70岁，确诊头面部带状疱疹", "30": "活动性乙型肝炎", "31": "术后行有创机械通气",
    "32": "机械通气持续30小时", "33": "Scr 120 μmol/L，BUN 7 mmol/L，ALT 30 U/L上限40，AST 25 U/L上限40",
    "35": "目前凝血功能异常", "37": "目前意识不清", "39": "目前每日吸烟", "41": "目前严重腹泻",
    "46": "3个月前行胆囊切除术", "49": "首次接受伊立替康化疗", "51": "转入我院前于当地医院完成2周期化疗",
}
NEGATIVE = {
    "8": "POP-Q II期", "20": "pN0，GS 7", "21": "术后cTnI 0.08 μg/L",
    "22": "AST 30 U/L上限40，ALT 30 U/L上限40，BUN 8 mmol/L上限9，Cr 201 umol/L上限100",
    "24": "母亲70岁患头面部带状疱疹", "30": "乙型肝炎已稳定", "31": "术前计划无创通气",
    "32": "机械通气20小时", "33": "Scr 180 μmol/L，BUN 7 mmol/L，ALT 30 U/L上限40，AST 25 U/L上限40",
    "35": "凝血功能正常", "37": "否认颅内高压，意识清楚", "39": "戒烟2年", "41": "严重腹泻已缓解",
    "46": "8个月前行手术", "49": "拟接受伊立替康化疗", "51": "母亲在外院接受化疗",
}


def _libraries():
    bundle = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    return {str(e["resource"]["identifier"][0]["value"]): e["resource"] for e in bundle["entry"] if e["resource"].get("resourceType") == "Library"}


def _production(resource, text):
    source = base64.b64decode(resource["content"][0]["data"]).decode("utf-8")
    namespace = {}
    exec(compile(source, resource["name"], "exec"), namespace)
    generator = namespace["FHIRResourceBundleGenerator"]("http://127.0.0.1:3456/api/fhir/baseDstu4")
    return source, generator.parse_clinical_text_to_fhir_bundle("p1", [{"text": text, "timestamp": "2026-01-01"}])


@pytest.mark.parametrize("criterion_id", IDS)
def test_production_decision_matches_verified_engine(criterion_id):
    criterion = TITLE_BY_ID[criterion_id]
    reports = [{"text": POSITIVE[criterion_id], "timestamp": "2026-01-01"}]
    verified = evaluate_criterion(criterion, "p1", reports, RuntimeServices(None, 1.0)).decision_trace.eligibility_result.value == "ELIGIBLE"
    _, bundle = _production(_libraries()[criterion_id], POSITIVE[criterion_id])
    assert bool(bundle["entry"]) == verified


@pytest.mark.parametrize("criterion_id", IDS)
def test_production_hard_negative_matches_verified_engine(criterion_id):
    criterion = TITLE_BY_ID[criterion_id]
    reports = [{"text": NEGATIVE[criterion_id], "timestamp": "2026-01-01"}]
    verified = evaluate_criterion(criterion, "p1", reports, RuntimeServices(None, 1.0)).decision_trace.eligibility_result.value == "ELIGIBLE"
    _, bundle = _production(_libraries()[criterion_id], NEGATIVE[criterion_id])
    assert bool(bundle["entry"]) == verified


def test_production_source_is_verified_engine_not_parallel_runtime():
    for resource in _libraries().values():
        source, _ = _production(resource, "")
        assert "class AtomState" not in source
        assert "class EvidenceLedger" not in source
        assert "class CriterionCompiler" not in source
        assert "ClinicalFact" in source
        assert "ClinicalEvent" in source
        assert "ClinicalRelation" in source
        assert "ClinicalEpisode" in source
        assert "REVIEW_REQUIRED" in source

