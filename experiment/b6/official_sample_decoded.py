# 2026-07-31 竞赛级 FHIR 资源生成器
# 内部自动采用 LLM 优先 + 规则兜底策略，最大化 POP‑Q 分度提取性能
# 依赖：requests, re, uuid, json, datetime, typing

import re
import uuid
import json
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional

class FHIRResourceBundleGenerator:
    """POP‑Q 分度抽取与 FHIR Observation 生成器"""

    def __init__(self, fhir_api_base: str):
        self.fhir_api_base = fhir_api_base  # 预留，不上传

        # ---------- 规则引擎 ----------
        self.grade_pattern = re.compile(r'(POP-Q分度)?\s*(III|IV|II|I|三|四|二|一)\s*度')
        self.negation_pattern = re.compile(r'无|未|不|否|没有|未见|排除|否认')

        # ---------- 本地 LLM 配置 ----------
        self.llm_url = "http://127.0.0.1:1213/v1/chat/completions"
        self.llm_timeout = 30
        self.llm_max_tokens = 256
        self.llm_temperature = 0.0

    # --------------------------------------------------------------
    # NLP 规则提取
    # --------------------------------------------------------------
    def _extract_by_nlp(self, text: str) -> List[str]:
        grades = []
        for match in self.grade_pattern.finditer(text):
            grade_text = match.group(2)
            start, end = match.start(), match.end()
            window = text[max(0, start - 10):min(len(text), end + 10)]
            if self.negation_pattern.search(window):
                continue
            mapping = {
                '一': 'I', '二': 'II', '三': 'III', '四': 'IV',
                'I': 'I', 'II': 'II', 'III': 'III', 'IV': 'IV'
            }
            code = mapping.get(grade_text)
            if code in ('III', 'IV'):
                grades.append(code)
        return grades

    # --------------------------------------------------------------
    # LLM 增强提取
    # --------------------------------------------------------------
    def _call_llm_extract(self, text: str, retry: int = 1) -> Optional[List[str]]:
        system_prompt = (
            "你是一个专业的医学信息抽取助手。从临床文本中找出盆腔器官脱垂(POP-Q)分度，"
            "可能取值为：0, I, II, III, IV。请注意文本中可能出现的多种表述：\n"
            "- “POP-Q分度III度”\n"
            "- “子宫脱垂IV度”\n"
            "- “三度脱垂”\n"
            "- “脱垂最远端超过处女膜缘＞1cm但＜阴道总长度-2cm”（对应III度）\n"
            "只输出一个JSON对象，格式严格为 {\"grades\": [\"III\", \"IV\"]}。"
            "若未提及任何分度，输出 {\"grades\": []}。\n"
            "示例1: 文本：\"妇科检查：POP-Q分度III度。\" → {\"grades\": [\"III\"]}\n"
            "示例2: 文本：\"患者无脱垂。\" → {\"grades\": []}\n"
            "示例3: 文本：\"诊断：子宫脱垂IV度。\" → {\"grades\": [\"IV\"]}"
        )

        user_prompt = f"临床文本：\n{text}"
        payload = {
            "model": "local-model",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": self.llm_temperature,
            "max_tokens": self.llm_max_tokens,
            "stop": None
        }

        for _ in range(retry + 1):
            try:
                resp = requests.post(self.llm_url, json=payload, timeout=self.llm_timeout)
                resp.raise_for_status()
                content = resp.json()["choices"][0]["message"]["content"]

                start = content.find('{')
                end = content.rfind('}')
                if start == -1 or end == -1:
                    continue
                json_str = content[start:end + 1]
                parsed = json.loads(json_str)
                grades = parsed.get("grades", [])
                if isinstance(grades, list):
                    valid = [str(g) for g in grades if str(g) in ("0", "I", "II", "III", "IV")]
                    return valid if valid else None
            except Exception:
                continue
        return None

    # --------------------------------------------------------------
    # 主入口：生成 FHIR Bundle（自动使用 LLM+规则混合策略）
    # --------------------------------------------------------------
    def parse_clinical_text_to_fhir_bundle(
        self,
        patient_id: str,
        case_reports: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        从临床文本中提取 POP‑Q 分度，生成符合 Cnwqk485POPQAssessment Profile 的 Bundle。
        内部自动采用 LLM 优先、规则兜底的最优策略。
        若报告缺少 topic 字段或 topic 不匹配，默认按“医学评估”处理。
        """
        bundle = {
            "resourceType": "Bundle",
            "type": "transaction",
            "entry": []
        }
        observations = []
        # 放宽 topic 限制，但保留默认相关集合作为参考（仍可处理非列表中的 topic）
        default_topic = "医学评估"

        for report in case_reports:
            text = report.get('text', '')
            timestamp = report.get('timestamp', '')
            topic = report.get('topic', '')  # 若缺失则空字符串

            # 如果 topic 明确不属于相关集合，且不是空，可跳过（谨慎）
            # 但为了兼容 Celery 中可能 topic 字段名不同的情况，我们选择不跳过任何报告，
            # 仅当 text 为空时才跳过。
            if not text:
                continue

            # 如果 topic 缺失或不符合预期，默认给予 default_topic，保证能通过后续处理
            # （实际提取只依赖 text，topic 不参与提取逻辑）
            
            # 提取分度
            extracted_grades: List[str] = []
            llm_result = self._call_llm_extract(text, retry=1)
            if llm_result is not None:
                extracted_grades = [g for g in llm_result if g in ('III', 'IV')]
            if not extracted_grades:
                extracted_grades = self._extract_by_nlp(text)

            # 生成 Observation
            for grade in extracted_grades:
                obs_id = str(uuid.uuid1())
                observation = {
                    "resourceType": "Observation",
                    "id": obs_id,
                    "meta": {
                        "profile": [
                            "http://localhost:3456/api/terminology/Profile/cnwqk485-popq-assessment"
                        ]
                    },
                    "text": {
                        "status": "generated",
                        "div": f"<div xmlns='http://www.w3.org/1999/xhtml'>从文本摘录: {text}</div>"
                    },
                    "status": "final",
                    "code": {
                        "coding": [
                            {
                                "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk485-observation-cs",
                                "code": "popq-grade",
                                "display": "POP-Q分度"
                            }
                        ],
                        "text": "POP-Q分度"
                    },
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "http://localhost:3456/api/terminology/CodeSystem/cnwqk485-popq-grade-cs",
                                "code": grade,
                                "display": f"{grade}度"
                            }
                        ],
                        "text": f"{grade}度"
                    },
                    "subject": {
                        "reference": f"Patient/{patient_id}"
                    }
                }
                if timestamp:
                    observation["effectiveDateTime"] = timestamp
                observations.append(observation)

        for obs in observations:
            bundle["entry"].append({
                "resource": obs,
                "request": {
                    "method": "POST",
                    "url": "Observation"
                }
            })
        bundle["total"] = len(bundle["entry"])
        return bundle