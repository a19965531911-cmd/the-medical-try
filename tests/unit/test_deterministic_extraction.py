from v43.clinical.models import ClinicalEvent, ClinicalFact, ClinicalRelation
from v43.extraction.deterministic import (
    extract_deterministic,
    is_negated,
    is_planned,
    normalize_date,
    normalize_unit,
    parse_number,
    subject_of,
)
from v43.retrieval.models import EvidencePacket, EvidenceSpan


class IR:
    def __init__(self, criterion_id): self.criterion_id = criterion_id


def pkt(*texts):
    return EvidencePacket(tuple(EvidenceSpan(f"s{i}", text, i, None, "2026-01-01", 0, len(text), f"h{i}") for i, text in enumerate(texts)))


def test_shared_numeric_unit_and_subject_primitives():
    assert parse_number("年龄55岁") == 55
    assert normalize_unit("岁") == "year"
    assert subject_of("母亲曾患带状疱疹") == "family"
    assert subject_of("患者确诊带状疱疹") == "patient"


def test_shared_date_planning_and_negation_primitives_are_conservative():
    assert normalize_date("2026年1月2日") == "2026-01-02"
    assert is_planned("拟于明日行气管插管")
    assert is_negated("否认带状疱疹")
    assert not is_negated("无明显诱因出现头面部带状疱疹，已确诊")


def test_185_distinguishes_actual_planned_prior_family_and_mention():
    actual = extract_deterministic(IR("185"), pkt("患者首次接受伊立替康静脉给药"))[1]
    assert len(actual) == 1 and actual[0].attributes["first_use"].state.value == "PRESENT"
    for text in ("计划首次使用伊立替康", "拟首次接受伊立替康给药", "既往多次使用伊立替康", "母亲曾使用伊立替康", "方案中提及伊立替康"):
        assert extract_deterministic(IR("185"), pkt(text))[1] == ()


def test_negation_and_family_subject_never_create_positive_875_facts():
    for text in ("否认颅内高压", "已排除颅内高压", "母亲曾意识不清"):
        facts = extract_deterministic(IR("875"), pkt(text))[0]
        assert not any(fact.state.value == "PRESENT" for fact in facts)


def test_explicit_negation_is_target_scoped_without_broad_substring_matches():
    for text in ("未接受伊立替康给药", "未确诊头面部带状疱疹", "未行气管插管有创机械通气", "已排除颅内高压"):
        assert is_negated(text)
    assert not is_negated("无明显不适，后确诊头面部带状疱疹")


def test_675_emits_age_diagnosis_and_only_corresponding_location_relation():
    facts, events, relations = extract_deterministic(IR("675"), pkt("患者55岁", "确诊头面部带状疱疹"))
    assert facts[0].concept == "patient_age" and facts[0].value == 55 and facts[0].unit == "year"
    assert events[0].concept == "herpes_zoster"
    assert relations[0].relation_type == "LOCATED_AT"
    assert extract_deterministic(IR("675"), pkt("确诊躯干部带状疱疹", "面部皮损"))[2] == ()


def test_plugins_return_only_typed_objects():
    objects = extract_deterministic(IR("745"), pkt("术后继续气管插管有创机械通气"))
    assert all(isinstance(x, (ClinicalFact, ClinicalEvent, ClinicalRelation)) for group in objects for x in group)
