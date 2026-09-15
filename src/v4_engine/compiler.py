from dataclasses import dataclass, field
from .evidence import AtomState

@dataclass
class CriterionDecision:
    satisfied: bool; satisfied_atoms: list[str]=field(default_factory=list); blocking_atoms: list[str]=field(default_factory=list); reason: str=''

class CriterionCompiler:
    def compile(self,spec,ledger):
        ok=spec.expression.eval(ledger)
        required=getattr(spec,'required_atoms',[])
        blocking=[a for a in required if ledger.contradicted(a) or ledger.unknown(a)]
        if blocking and not ok: return CriterionDecision(False,[],blocking,'required atom unavailable or contradicted')
        atoms=[a for a in required if ledger.entailed(a)]
        return CriterionDecision(bool(ok),atoms,blocking,'criterion expression evaluated by Python')
