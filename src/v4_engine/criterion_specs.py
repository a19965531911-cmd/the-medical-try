from dataclasses import dataclass
from .expressions import *

@dataclass(frozen=True)
class CriterionSpec:
    criterion_id: str; title: str; question: str; expression: object; required_atoms: tuple[str,...]; llm_required: bool=False; relation_required: bool=False

SPECS={
 '51':CriterionSpec('51','165','已经在外院接受过化疗者',AllOf(Atom('chemotherapy'),Atom('administered'),Atom('outside_hospital'),Atom('patient_subject'),Not(Atom('planned_only'))),('chemotherapy','administered','outside_hospital','patient_subject')),
 '49':CriterionSpec('49','185','首次应用包含伊立替康的化疗方案治疗',AllOf(Atom('irinotecan'),Atom('administered'),Atom('first_use'),Not(Atom('planned_only')),Not(Atom('previous_multiple_use'))),('irinotecan','administered','first_use'),True),
 '41':CriterionSpec('41','565','患有严重腹泻或便秘',AllOf(AnyOf(Atom('diarrhea'),Atom('constipation')),Atom('severity_severe')),('diarrhea','constipation','severity_severe'),True),
 '24':CriterionSpec('24','675','年龄≥50岁且患头面部带状疱疹',AllOf(GTE('age',50),Atom('herpes_zoster'),Atom('diagnosis_confirmed'),In('zoster_site',('head','face','head_face'))),('age','herpes_zoster','diagnosis_confirmed','zoster_site')),
 '30':CriterionSpec('30','735','目标传染病或结缔组织病处于活动期',AllOf(Atom('target_disease'),Atom('active_state'),Not(Atom('resolved_or_stable'))),('target_disease','active_state'),True),
 '31':CriterionSpec('31','745','术后需要有创机械通气',AllOf(Atom('surgery'),Atom('postoperative_state'),Atom('invasive_mechanical_ventilation'),RelationExpr('ventilation','postoperative_state','SAME_CLAUSE')),('surgery','postoperative_state','invasive_mechanical_ventilation'),True,True),
 '35':CriterionSpec('35','835','凝血功能异常',AllOf(Atom('coagulation_abnormality'),Not(Atom('coagulation_normal'))),('coagulation_abnormality',),True),
 '37':CriterionSpec('37','875','颅内高压或意识不清',AnyOf(Atom('intracranial_hypertension'),Atom('consciousness_impairment')),('intracranial_hypertension','consciousness_impairment'),True),
}
