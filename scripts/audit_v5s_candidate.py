import ast
import base64
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "submission" / "a_test_message_bundle_v5s_candidate.json"


def main():
    raw = CANDIDATE.read_bytes()
    bundle = json.loads(raw.decode("utf-8"))
    resources = [entry["resource"] for entry in bundle["entry"]]
    libraries = [resource for resource in resources if resource.get("resourceType") == "Library"]
    decoded = compiled = executed = secure = 0
    dataclasses = enums = flatten_rename = unresolved_symbols = 0
    symbol_errors = []
    for library in libraries:
        source = base64.b64decode(library["content"][0]["data"], validate=True).decode("utf-8")
        decoded += 1
        code = compile(source, library["name"], "exec")
        compiled += 1
        namespace = {}
        exec(code, namespace)
        executed += 1
        secure += int(not any(token in source for token in ("input(", "eval(", "os.system", "subprocess")))
        dataclasses += source.count("dataclass")
        enums += source.count("Enum")
        flatten_rename += sum(source.count(token) for token in ("z0", "z1", "z2"))
        unresolved_symbols += sum(source.count(token) for token in ("__BASE__", "__TITLE__", "__SPEC__"))
        tree = ast.parse(source, filename=library["name"])
        symbol_errors.extend(
            node.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Name)
            and node.id.startswith("__")
            and node.id.endswith("__")
            and node.id not in {"__name__"}
        )
    result = {
        "size": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "message_header": sum(resource.get("resourceType") == "MessageHeader" for resource in resources),
        "libraries": len(libraries),
        "decoded": decoded,
        "compiled": compiled,
        "executed": executed,
        "secure": secure,
        "dataclasses": dataclasses,
        "enums": enums,
        "flatten_rename": flatten_rename,
        "unresolved_symbols": unresolved_symbols,
        "symbol_errors": sorted(set(symbol_errors)),
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
