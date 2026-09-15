"""Small, deterministic helpers matching the observed online slot contract."""

import json
import math


def _slot_candidates(library, slot):
    slot = str(slot)
    content = library.get("content") or [{}]
    title = str(content[0].get("title", ""))
    name = str(library.get("name", ""))
    identifier = str((library.get("identifier") or [{}])[0].get("value", ""))
    return [
        ("content.title", title == slot),
        ("name", name == f"cnwqk{slot}"),
        ("id", str(library.get("id", "")) == slot),
        ("identifier", identifier == slot),
    ]


def resolve_library_by_slot(libraries, slot):
    """Resolve by submission slot metadata, with identifier as a last resort."""
    ranked = []
    for library in libraries:
        matches = _slot_candidates(library, slot)
        score = sum(weight for weight, (_, matched) in zip((100, 80, 60, 10), matches) if matched)
        if score:
            ranked.append((score, library))
    if not ranked:
        raise KeyError(f"online slot {slot!r} not found")
    ranked.sort(key=lambda item: item[0], reverse=True)
    if len(ranked) > 1 and ranked[0][0] == ranked[1][0]:
        raise ValueError(f"online slot {slot!r} is ambiguous")
    return ranked[0][1]


def strict_json_roundtrip(value):
    """Reject values that a permissive Python JSON encoder could silently coerce."""
    def validate(node, path="$", seen=None):
        seen = seen or set()
        if isinstance(node, dict):
            if id(node) in seen:
                raise TypeError(f"{path}: circular reference")
            seen.add(id(node))
            for key, child in node.items():
                if not isinstance(key, str):
                    raise TypeError(f"{path}: non-string object key")
                validate(child, f"{path}.{key}", seen)
            seen.remove(id(node))
        elif isinstance(node, list):
            if id(node) in seen:
                raise TypeError(f"{path}: circular reference")
            seen.add(id(node))
            for index, child in enumerate(node):
                validate(child, f"{path}[{index}]", seen)
            seen.remove(id(node))
        elif node is None or isinstance(node, (str, bool, int)):
            return
        elif isinstance(node, float):
            if not math.isfinite(node):
                raise ValueError(f"{path}: non-finite float")
        else:
            raise TypeError(f"{path}: unsupported {type(node).__name__}")

    validate(value)
    return json.loads(json.dumps(value, ensure_ascii=False, allow_nan=False))
