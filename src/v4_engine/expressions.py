class Expr:
    def eval(self, ledger): raise NotImplementedError
class Atom(Expr):
    def __init__(self,name): self.name=name
    def eval(self,l): return l.entailed(self.name)
class AllOf(Expr):
    def __init__(self,*xs): self.xs=xs
    def eval(self,l): return all(x.eval(l) for x in self.xs)
class AnyOf(Expr):
    def __init__(self,*xs): self.xs=xs
    def eval(self,l): return any(x.eval(l) for x in self.xs)
class Not(Expr):
    def __init__(self,x): self.x=x
    def eval(self,l): return not self.x.eval(l)
class Eq(Expr):
    def __init__(self,atom,value): self.atom=atom; self.value=value
    def eval(self,l): return any(v==self.value for v in l.values(self.atom))
class In(Expr):
    def __init__(self,atom,values): self.atom=atom; self.values_set=set(values)
    def eval(self,l): return any(v in self.values_set for v in l.values(self.atom))
class GTE(Expr):
    def __init__(self,atom,value): self.atom=atom; self.value=value
    def eval(self,l): return any(v>=self.value for v in l.values(self.atom))
class GT(Expr):
    def __init__(self,atom,value): self.atom=atom; self.value=value
    def eval(self,l): return any(v>self.value for v in l.values(self.atom))
class RelationExpr(Expr):
    def __init__(self,a,b,kind): self.a=a; self.b=b; self.kind=kind
    def eval(self,l): return l.relation(self.a,self.b,{self.kind})
