"""Self-contained production entrypoint backed by the verified V4.3 core."""
import json
from types import SimpleNamespace
from urllib.error import HTTPError, URLError

from v43.clinical.store import ClinicalStore
from v43.constraints.executor import execute
from v43.fhir.compiler import compile_fhir
from v43.fhir.contracts import contract_for_criterion
from v43.retrieval.models import EvidencePacket
from v43.retrieval.segmenter import segment_reports
from v43.extraction.semantic import CallGuard, extract_semantic
from v43.extraction.transport import SemanticTransport
from v43.criteria.c165 import build_constraints as build_165, extract as extract_165
from v43.criteria.c185 import build_constraints as build_185, extract as extract_185
from v43.criteria.c265 import build_constraints as build_265, extract as extract_265
from v43.criteria.c485 import build_constraints as build_485, extract as extract_485
from v43.criteria.c555 import build_constraints as build_555, extract as extract_555
from v43.criteria.c565 import build_constraints as build_565, extract as extract_565
from v43.criteria.c615 import build_constraints as build_615, extract as extract_615
from v43.criteria.c635 import build_constraints as build_635, extract as extract_635
from v43.criteria.c675 import build_constraints as build_675, extract as extract_675
from v43.criteria.c735 import build_constraints as build_735, extract as extract_735
from v43.criteria.c745 import build_constraints as build_745, extract as extract_745
from v43.criteria.c755 import build_constraints as build_755, extract as extract_755
from v43.criteria.c805 import build_constraints as build_805, extract as extract_805
from v43.criteria.c835 import build_constraints as build_835, extract as extract_835
from v43.criteria.c855 import build_constraints as build_855, extract as extract_855
from v43.criteria.c875 import build_constraints as build_875, extract as extract_875

REVIEW_REQUIRED = "REVIEW_REQUIRED"
PRODUCTION_TEMPORAL_POLICY_875 = "EVER_PRESENT"
SEMANTIC_CAPABLE_CRITERIA = {"185", "675", "745", "875"}
PRODUCTION_SEMANTIC_TIMEOUT_SECONDS = 30.0
PRODUCTION_SEMANTIC_IR = {}
CRITERION_PLUGINS = {
    cid: SimpleNamespace(build_constraints=build, extract=extract) for cid, build, extract in (
        ("165", build_165, extract_165), ("185", build_185, extract_185),
        ("265", build_265, extract_265), ("485", build_485, extract_485),
        ("555", build_555, extract_555), ("565", build_565, extract_565),
        ("615", build_615, extract_615), ("635", build_635, extract_635),
        ("675", build_675, extract_675), ("735", build_735, extract_735),
        ("745", build_745, extract_745), ("755", build_755, extract_755),
        ("805", build_805, extract_805), ("835", build_835, extract_835),
        ("855", build_855, extract_855), ("875", build_875, extract_875),
    )
}

def evaluate_and_compile(criterion_id, patient_id, reports, temporal_policy_875=PRODUCTION_TEMPORAL_POLICY_875, semantic_transport=None, call_guard=None):
    criterion_id = str(criterion_id)
    spans = segment_reports([report for report in (reports or []) if isinstance(report, dict)])
    packet = EvidencePacket(spans=spans, retrieval_reason="PRODUCTION_ALL_SPANS")
    plugin = CRITERION_PLUGINS[criterion_id]
    constraints = plugin.build_constraints(SimpleNamespace(criterion_id=criterion_id, raw={}))
    store = ClinicalStore.from_packet(packet)
    facts, events, relations = plugin.extract(packet)
    for fact in facts: store.add_fact(fact)
    for event in events: store.add_event(event)
    for relation in relations: store.add_relation(relation)
    semantic_context = PRODUCTION_SEMANTIC_IR.get(criterion_id)
    ir = SimpleNamespace(
        criterion_id=criterion_id,
        title=str((semantic_context or {}).get("title", criterion_id)),
        original_text=str((semantic_context or {}).get("original_text", criterion_id)),
        raw=dict(semantic_context or {}),
    )
    trace = execute(SimpleNamespace(criterion_id=criterion_id, raw={}, constraints=constraints, root_constraint_id="root"), store)
    semantic_called = 0
    semantic_success = 0
    semantic_reason = "NOT_NEEDED"
    if criterion_id in SEMANTIC_CAPABLE_CRITERIA and trace.root_result.value == "UNKNOWN":
        transport = semantic_transport or SemanticTransport()
        guard = call_guard or CallGuard()
        semantic_called = 1
        try:
            semantic = extract_semantic(
                ir, packet, transport, guard, patient_id=str(patient_id),
                timeout=PRODUCTION_SEMANTIC_TIMEOUT_SECONDS,
            )
            for fact in semantic[0]: store.add_fact(fact)
            for event in semantic[1]: store.add_event(event)
            for relation in semantic[2]: store.add_relation(relation)
            trace = execute(SimpleNamespace(criterion_id=criterion_id, raw={}, constraints=constraints, root_constraint_id="root"), store)
            semantic_success = 1
            semantic_reason = "SUCCESS"
        except TimeoutError:
            semantic_reason = "TIMEOUT"
        except (HTTPError, URLError):
            semantic_reason = "HTTP_ERROR"
        except json.JSONDecodeError:
            semantic_reason = "INVALID_JSON"
        except Exception as exc:
            reason_code = getattr(exc, "reason_code", "")
            semantic_reason = {
                "SEMANTIC_SCHEMA_REJECT": "SCHEMA_REJECT",
                "GROUNDING_REJECT": "GROUNDING_REJECT",
            }.get(reason_code, "SCHEMA_REJECT")
    print(
        "V43_SEMANTIC_METRICS|criterion=" + criterion_id
        + "|semantic_called=" + str(semantic_called)
        + "|semantic_success=" + str(semantic_success)
        + "|semantic_reason=" + semantic_reason
    )
    if criterion_id == "875" and temporal_policy_875 == REVIEW_REQUIRED:
        return trace, store, ()
    if criterion_id == "875" and temporal_policy_875 not in {"EVER_PRESENT", "CURRENT_ACTIVE"}:
        raise ValueError("unsupported 875 production policy: " + str(temporal_policy_875))
    compiled = compile_fhir(trace, store, contract_for_criterion(criterion_id), "Patient/" + str(patient_id))
    return trace, store, compiled.resources
