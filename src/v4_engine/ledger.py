from .evidence import Evidence, AtomState, Relation

class EvidenceLedger:
    def __init__(self, patient_id, criterion_id):
        self.patient_id=patient_id; self.criterion_id=criterion_id; self.evidence=[]; self.relations=[]
    def add(self, item: Evidence):
        if item.subject=='patient': self.evidence.append(item)
    def add_relation(self, relation: Relation): self.relations.append(relation)
    def items(self, atom): return [x for x in self.evidence if x.atom==atom]
    def entailed(self, atom): return any(x.state==AtomState.ENTAILED for x in self.items(atom)) and not self.contradicted(atom)
    def contradicted(self, atom): return any(x.state==AtomState.CONTRADICTED for x in self.items(atom))
    def unknown(self, atom): return not self.entailed(atom) and not self.contradicted(atom)
    def values(self, atom): return [x.value for x in self.items(atom) if x.state==AtomState.ENTAILED and x.value is not None]
    def relation(self,left,right,kinds=None): return any(x.left==left and x.right==right and (kinds is None or x.kind in kinds) for x in self.relations)
