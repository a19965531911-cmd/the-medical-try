"""Typed builder boundary; FHIR implementation is injected from frozen contracts."""
def require_facts(facts, required):
    missing=[x for x in required if facts.get(x) is None]
    if missing: raise ValueError('missing typed facts: '+','.join(missing))
    return facts
