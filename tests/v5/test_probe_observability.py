import base64
import ast
import importlib.util
import json
import re
from pathlib import Path
from types import SimpleNamespace

import pytest
from test_fhir_runtime import POSITIVE

ROOT = Path(__file__).parents[2]
spec = importlib.util.spec_from_file_location('probe_builder', ROOT / 'scripts/build_v5_submission.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
OLD = ROOT / 'submission/a_test_message_bundle_v5a_probe_fixed_candidate.json'
PROBE = ROOT / 'submission/a_test_message_bundle_v5a_probe_candidate.json'


def test_all_16_probe_libraries_security_and_only_logging_changed():
    old = json.loads(OLD.read_text(encoding='utf-8'))
    new = json.loads(PROBE.read_text(encoding='utf-8'))
    count = 0
    for before, after in zip(old['entry'], new['entry'], strict=True):
        if before['resource'].get('resourceType') != 'Library':
            assert before == after
            continue
        a = before['resource']['content'][0]
        b = after['resource']['content'][0]
        s1 = base64.b64decode(a['data'], validate=True).decode()
        s2 = base64.b64decode(b['data'], validate=True).decode()
        compile(s2, '<probe>', 'exec')
        assert 'ENGINE_VERSION=' in s1 and 'ENGINE_VERSION=' in s2
        assert '127.0.0.1:1213' in s2 and 'local-model' in s2
        assert 'V5_METRICS|' in s2 and 'input(' not in s2
        assert not [h for h in re.findall(r'''['"]([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})['"]''', s2)
                    if h not in {'127.0.0.1', 'localhost'}]
        trees = [ast.parse(s) for s in (s1, s2)]
        for tree in trees:
            cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'FHIRResourceBundleGenerator')
            method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'parse_clinical_text_to_fhir_bundle')
            # Keep evaluation and return; the middle statements are logging only.
            method.body = [method.body[0], method.body[-1]]
        assert 'z1_CriterionSpec(' in s2
        count += 1
    assert count == 16


def sources():
    bundle = json.loads(OLD.read_text(encoding='utf-8'))
    return {str(e['resource']['content'][0]['title']): base64.b64decode(e['resource']['content'][0]['data']).decode()
            for e in bundle['entry'] if e['resource'].get('resourceType') == 'Library'}


def runtime(source):
    ns = {'__name__': '__main__'}
    exec(compile(source, '<embedded>', 'exec'), ns)
    return ns


@pytest.mark.parametrize('criterion', POSITIVE)
def test_old_and_patched_predictions_and_fhir_identical(criterion, capsys):
    from v5.criterion_specs import load_criterion_specs
    from v5.runtime import evaluate_and_compile
    from v5.transport import LocalModelTransport
    source = sources()[criterion]
    ns = runtime(source)
    transport = LocalModelTransport(request_fn=lambda payload, timeout: {'choices': [{'message': {'content': 'MATCH'}}]})
    reports = [{'text': POSITIVE[criterion], 'timestamp': '2026-01-01'}]
    canonical = evaluate_and_compile(criterion, 'private-patient-id', reports, transport)
    embedded_transport = ns['LocalModelTransport'](request_fn=lambda payload, timeout: {'choices': [{'message': {'content': 'MATCH'}}]})
    embedded = ns['z12_evaluate_and_compile'](criterion, 'private-patient-id', reports, embedded_transport)
    generator = ns['FHIRResourceBundleGenerator']('http://localhost:3456')
    generator.transport = embedded_transport
    bundle = generator.parse_clinical_text_to_fhir_bundle('private-patient-id', reports)
    results = [(canonical.match.final_decision.value, canonical.resources), (embedded.match.final_decision.value, embedded.resources)]
    log = capsys.readouterr().out
    assert results[0] == results[1]
    assert log.startswith('V5_METRICS|criterion=' + criterion + '|')
    assert 'private-patient-id' not in log and POSITIVE[criterion] not in log
    assert '|final=' + results[1][0] + '|' in log


@pytest.mark.parametrize('status', ['OK', 'CONNECT_ERROR', 'HTTP_4XX', 'HTTP_5XX', 'TIMEOUT', 'EMPTY_RESPONSE', 'INVALID_RESPONSE', 'PARSE_UNKNOWN', None])
@pytest.mark.parametrize('method', ['PARSED_SENTINEL', 'PARSED_JSON', 'PARSED_CHINESE', 'PARSE_UNKNOWN', None])
def test_metrics_preserve_statuses_and_none_without_clinical_content(status, method, capsys):
    enum = lambda value: SimpleNamespace(value=value) if value is not None else None
    match = SimpleNamespace(deterministic_decision=enum('UNKNOWN'), model_decision=enum('MATCH'),
                            guarded_decision=enum('MATCH'), final_decision=enum('MATCH'),
                            attempts=2 if status else 0, transport_status=enum(status),
                            parse_method=enum(method), prompt_length=321)
    ns = {'TITLE': '185', 'PROFILE': 'p', 'IDENTIFIER': 'i', 'LocalModelTransport': lambda: None,
          'evaluate_and_compile': lambda *args: SimpleNamespace(match=match, resources=(), reason_code=None)}
    exec(builder.BOOT, ns)
    ns['FHIRResourceBundleGenerator']('').parse_clinical_text_to_fhir_bundle('SECRET', [{'text': 'CLINICAL SECRET'}])
    line = capsys.readouterr().out.strip()
    assert line.startswith('V5_METRICS|')
    fields = dict(item.split('=', 1) for item in line.split('|')[1:])
    assert fields == dict(criterion='185', deterministic='UNKNOWN', llm_called='1' if status else '0',
                         attempts='2' if status else '0', transport=status or 'NA', parse=method or 'NA',
                         model='MATCH', guarded='MATCH', final='MATCH', resources='0', reason='NA', prompt_length='321')
