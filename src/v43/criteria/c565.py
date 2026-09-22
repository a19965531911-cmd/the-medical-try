from .shared import build_constraints as _build, extract as _extract
criterion_id="565"
def build_constraints(ir): return _build(criterion_id)
def extract(packet): return _extract(criterion_id, packet)
