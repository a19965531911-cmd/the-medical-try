import re
from .evidence import Evidence,AtomState
def age(text,index=0):
 m=re.search(r'(?:年龄|患者|病人)?\s*(\d+(?:\.\d+)?)\s*岁',text)
 return [] if not m else [Evidence('age',AtomState.ENTAILED,m.group(0),float(m.group(1)),index,source='deterministic')]
def keyword(text,atom,pattern,index=0,negated=()):
 if not re.search(pattern,text,re.I): return []
 state=AtomState.CONTRADICTED if any(x in text for x in negated) else AtomState.ENTAILED
 return [Evidence(atom,state,re.search(pattern,text,re.I).group(0),True,index,source='deterministic')]
