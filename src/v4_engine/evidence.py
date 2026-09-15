from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class AtomState(str, Enum):
    ENTAILED='ENTAILED'; CONTRADICTED='CONTRADICTED'; UNKNOWN='UNKNOWN'

@dataclass(frozen=True)
class Evidence:
    atom: str; state: AtomState; evidence: str=''; value: Any=None
    report_index: int|None=None; topic: str=''; timestamp: str=''
    subject: str='patient'; temporality: str='unknown'; source: str='deterministic'

@dataclass(frozen=True)
class Relation:
    left: str; right: str; kind: str; report_index: int|None=None
