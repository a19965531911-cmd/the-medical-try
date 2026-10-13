"""Bounded local generation transport and trace appended to frozen B4F."""
import subprocess as _b5_subprocess
import sys as _b5_sys

_B5_B4_CALL = _b4_call
_B5_B4_ENTRY = _b4_entry
_B5_B4_EVALUATE = _b4_evaluate

_B5_HTTP_CHILD = r'''import json,sys,socket
from urllib.request import Request,build_opener,ProxyHandler
from urllib.error import HTTPError,URLError
p=json.load(sys.stdin)
try:
    req=Request(p['endpoint'],json.dumps(p['payload'],ensure_ascii=False).encode('utf8'),{'Content-Type':'application/json'},method='POST')
    with build_opener(ProxyHandler({})).open(req,timeout=p['timeout']) as r:
        raw=r.read(2000001)
        if len(raw)>2000000: raise ValueError('response too large')
        print(json.dumps({'http_status':r.status,'raw_response':raw.decode('utf8')}))
except HTTPError as e:
    print(json.dumps({'error_kind':'HTTP_ERROR','http_status':e.code,'error':e.read(10000).decode('utf8',errors='replace')}))
except Exception as e:
    kind='TIMEOUT' if isinstance(e,(TimeoutError,socket.timeout)) or isinstance(e,URLError) and isinstance(e.reason,(TimeoutError,socket.timeout)) else 'CONNECTION_FAILED' if isinstance(e,URLError) else 'RESPONSE_PARSE_FAILED'
    print(json.dumps({'error_kind':kind,'error':type(e).__name__+': '+str(e)}))
'''


def _b5_transport(self, prompt):
    self.transport_error = None
    self.transport_error_kind = None
    remaining = self.b5_deadline - _b4_time.perf_counter()
    payload = {"model": B5_CONFIG["model"], "temperature": 0, "max_tokens": B5_CONFIG["max_tokens"],
               "messages": [{"role": "user", "content": prompt}]}
    record = dict(endpoint=B5_CONFIG["endpoint"], request=payload, remaining_budget_seconds=remaining)
    self.b5_trace["requests"].append(record)
    started = _b4_time.perf_counter()
    try:
        parts = _b4_urlparse(B5_CONFIG["endpoint"])
        if parts.scheme != "http" or parts.hostname not in {"127.0.0.1", "localhost", "::1"}:
            raise ValueError("Only authorized loopback HTTP endpoints allowed")
        if remaining <= 0:
            raise _b5_subprocess.TimeoutExpired("budget", 0)
        timeout = min(B5_CONFIG["request_timeout_seconds"], remaining)
        child = _b5_subprocess.run([_b5_sys.executable, "-I", "-c", _B5_HTTP_CHILD],
            input=json.dumps(dict(endpoint=B5_CONFIG["endpoint"], payload=payload, timeout=timeout)),
            capture_output=True, encoding="utf8", errors="replace", timeout=timeout)
        if child.returncode:
            raise ValueError("HTTP subprocess failed: " + child.stderr[:1000])
        response = json.loads(child.stdout, object_pairs_hook=_b4_unique, parse_constant=_b4_invalid)
        record["response"] = response
        if response.get("error_kind"):
            self.transport_error_kind = response["error_kind"]
            raise ValueError(response["error"])
        self.model_metrics["http_success"] += 1
        raw = json.loads(response["raw_response"], object_pairs_hook=_b4_unique, parse_constant=_b4_invalid)
        record["reported_model"] = raw.get("model")
        return raw["choices"][0]["message"]["content"]
    except Exception as exc:
        self.transport_error_kind = self.transport_error_kind or ("TOTAL_BUDGET_TIMEOUT" if isinstance(exc, _b5_subprocess.TimeoutExpired) else "RESPONSE_PARSE_FAILED")
        self.transport_error = type(exc).__name__ + ": " + str(exc)
        record["error_kind"] = self.transport_error_kind
        record["error"] = self.transport_error
        return None
    finally:
        record["elapsed_seconds"] = _b4_time.perf_counter() - started


def _b4_call(self, cid, reports, requested, items=None):
    if self.model_metrics["calls"] >= B5_CONFIG["max_calls"] or _b4_time.perf_counter() >= self.b5_deadline:
        self.b5_trace["budget_skips"] += 1
        return None
    parsed = _B5_B4_CALL(self, cid, reports, requested, items)
    self.b5_trace["validation"].append(dict(requested_atoms=requested, parsed=parsed,
        schema_and_literal_grounding="PASS" if parsed is not None else "FAIL_OR_NO_RESPONSE"))
    return parsed


def _b5_core_evaluate(self, cid, reports):
    result = _B5_B4_EVALUATE(self, cid, reports)
    if B4_CONFIG["mode"] == "llm_first" and self.model_metrics["errors"] and not self.model_metrics["responses"]:
        self.b5_trace["fallback"] = "RULES_AFTER_MODEL_FAILURE"
        return evaluate_b2(cid, reports, "B2E")
    if self.model_metrics["errors"]:
        self.b5_trace["fallback"] = "RULES_AFTER_MODEL_FAILURE"
    return result


def _b4_evaluate(self, cid, reports):
    if not any(isinstance(r.get("text"), str) and r["text"].strip() for r in reports):
        return evaluate_b2(cid, reports, "B2E")
    if B4_CONFIG["mode"] == "rules":
        return _b5_core_evaluate(self, cid, reports)
    if cid == "525" and len(event_groups(reports)) > 1:
        baseline = evaluate_b2(cid, reports, "B2E")
        for items in event_groups(reports).values():
            indexes = [i for i, _ in items]
            local = _b5_core_evaluate(self, cid, [r for _, r in items])
            if local["match"]:
                return _restore_indexes(local, indexes)
        return dict(baseline, match=False, decision="NO_MATCH", reason="B5_CROSS_EVENT_INCOMPLETE")
    return _b5_core_evaluate(self, cid, reports)


def _b5_entry(self, patient_id, case_reports, ai_algorithm_type="nlp"):
    self.b5_deadline = _b4_time.perf_counter() + B5_CONFIG["total_model_budget_seconds"]
    # Broad evidence retrieval intentionally retains paraphrases and original indices.
    self.b5_trace = dict(retrieval_policy="ALL_ORIGINAL_RECORDS_EVENT_SCOPED_BY_B2E",
        selected_record_indices=list(range(len(case_reports))) if isinstance(case_reports, (list, tuple)) else [],
        requests=[], validation=[], budget_skips=0, fallback="NONE", variant=B5_CONFIG["variant"])
    scoped = case_reports
    self.b5_trace["subject_rejected_records"] = []
    if B4_CONFIG["mode"] != "rules" and isinstance(case_reports, (list, tuple)):
        scoped = []
        for i, original in enumerate(case_reports):
            r = dict(original) if isinstance(original, dict) else {"text": "" if original is None else str(original)}
            text = r.get("text", "")
            if isinstance(text, str) and (r.get("subject") in ("family", "other") or _has(r"父亲|母亲|家族|家属|其父|其母|father|mother|family", text)):
                # Ambiguous family records fail closed; explicitly patient-owned clauses remain.
                clauses = re.split(r"[。；;\n]", text)
                patient_clauses = [c for c in clauses if _has(r"患者|本人|patient", c) and not _has(r"父亲|母亲|家族|家属|其父|其母|father|mother|family", c)]
                r["text"] = "。".join(patient_clauses)
                self.b5_trace["subject_rejected_records"].append(i)
            scoped.append(r)
    response = _B5_B4_ENTRY(self, patient_id, scoped, ai_algorithm_type)
    self.b5_trace["fact_rejections"] = self.model_metrics["fact_rejections"]
    self.b5_trace["extraction"] = self.last_result
    self.b5_trace["resources_generated"] = len(response["entry"])
    return response


FHIRResourceBundleGenerator._transport = _b5_transport
FHIRResourceBundleGenerator.parse_clinical_text_to_fhir_bundle = _b5_entry
