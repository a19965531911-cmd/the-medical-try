import json
from collections import Counter
from pathlib import Path

from v5.criterion_specs import CRITERION_IDS


CASES=json.loads((Path(__file__).parents[1]/"fixtures/v5_matcher_cases.json").read_text(encoding="utf-8"))


def test_fixture_corpus_has_required_coverage():
 assert len(CASES) >= 112
 counts=Counter((x["criterion"],x["class"]) for x in CASES)
 assert {x["criterion"] for x in CASES} == set(CRITERION_IDS)
 for cid in CRITERION_IDS:
  assert counts[cid,"positive"] >= 3
  assert counts[cid,"negative"] >= 3
  assert counts[cid,"ambiguous"] >= 1
  assert any(x["expected"] == "MATCH" for x in CASES if x["criterion"] == cid)


def test_fixture_corpus_is_synthetic_and_has_no_hidden_identifiers():
 raw=json.dumps(CASES,ensure_ascii=False)
 assert "PAPERLESS" not in raw and "hidden" not in raw.lower()
