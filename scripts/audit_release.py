"""Create a metadata-only release audit for immutable CHIP2026 snapshots."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


DATA_EXTENSIONS = {".csv", ".tsv", ".xls", ".xlsx"}
SECRET_EXTENSIONS = {".key", ".pem"}
CACHE_PARTS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".ipynb_checkpoints",
    "node_modules",
}
BUILD_PARTS = {"build", "dist", "coverage"}
TEXT_EXTENSIONS = {
    ".cfg", ".ini", ".json", ".md", ".py", ".rst", ".toml", ".txt", ".yaml", ".yml"
}

SECRET_PATTERNS = {
    "private key": re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY", re.I),
    "authorization token": re.compile(r"(?:authorization|bearer)\s*[:= ]", re.I),
    "credential assignment": re.compile(
        r"(?:api[_-]?key|access[_-]?key|token|secret|password|cookie|session)\s*[:=]", re.I
    ),
}
PATIENT_PATTERNS = {
    "Chinese identity number": re.compile(r"(?<!\d)\d{17}[\dXx](?!\d)"),
    "Chinese mobile number": re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"),
    "medical record identifier": re.compile(r"(?:住院号|病案号|patient[_ -]?id)\s*[:：=]\s*[A-Za-z0-9_-]+", re.I),
    "case-report marker": re.compile(r"(?:病例|病历|case report|patient data)", re.I),
}
PERSONAL_PATH = re.compile(
    r"[A-Za-z]:\\Users\\[^\\\s]+|(?:^|[\\/])(?:Desktop|Documents)(?:[\\/]|$)",
    re.I | re.M,
)


@dataclass
class Finding:
    source: str
    path: str
    size: int
    kind: str
    decision: str
    reason: str


def read_text(path: Path) -> str | None:
    if path.suffix.lower() not in TEXT_EXTENSIONS or path.stat().st_size > 5 * 1024 * 1024:
        return None
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def classify(root: Path, path: Path) -> Finding:
    relative = path.relative_to(root).as_posix()
    parts = {part.lower() for part in path.relative_to(root).parts}
    name = path.name.lower()
    suffix = path.suffix.lower()
    size = path.stat().st_size
    text = read_text(path)

    if parts & CACHE_PARTS or suffix in {".pyc", ".pyo"}:
        return Finding(root.name, relative, size, "CACHE", "EXCLUDE", "Generated cache")
    if parts & BUILD_PARTS or suffix in {".tmp", ".bak"}:
        return Finding(root.name, relative, size, "BUILD_OUTPUT", "EXCLUDE", "Generated build output")
    if name in {".env", "credentials.json"} or name.startswith(".env.") or suffix in SECRET_EXTENSIONS:
        return Finding(root.name, relative, size, "SECRET_RISK", "EXCLUDE", "Secret-bearing filename")
    if suffix in DATA_EXTENSIONS or "data" in parts or "datasets" in parts:
        kind = "COMPETITION_INPUT" if "chip2026" in name or "train_set" in name or "test_a" in name else "DATA"
        return Finding(root.name, relative, size, kind, "EXCLUDE", "Data files are outside repository scope")
    if "submission" in parts or "submissions" in parts or name.startswith("a_test_message_bundle"):
        return Finding(root.name, relative, size, "SUBMISSION_ARTIFACT", "EXCLUDE", "Generated competition submission")
    if "logs" in parts or suffix == ".log":
        return Finding(root.name, relative, size, "LOG", "EXCLUDE", "Runtime log")
    if "vendor" in parts:
        return Finding(root.name, relative, size, "SOURCE_CODE", "EXCLUDE", "Third-party vendored research source")
    if size > 20 * 1024 * 1024:
        return Finding(root.name, relative, size, "LARGE_FILE", "EXCLUDE", "File exceeds 20 MB")

    if text is not None:
        for label, pattern in SECRET_PATTERNS.items():
            match = pattern.search(text)
            if match:
                line = text.count("\n", 0, match.start()) + 1
                return Finding(root.name, relative, size, "SECRET_RISK", "EXCLUDE", f"{label} indicator at line {line}")
        for label, pattern in PATIENT_PATTERNS.items():
            match = pattern.search(text)
            if match:
                line = text.count("\n", 0, match.start()) + 1
                return Finding(root.name, relative, size, "PATIENT_DATA", "EXCLUDE", f"{label} indicator at line {line}")
        match = PERSONAL_PATH.search(text)
        if match:
            line = text.count("\n", 0, match.start()) + 1
            return Finding(root.name, relative, size, "PERSONAL_PATH_RISK", "SANITIZE", f"Local path at line {line}")

    if "tests" in parts or name.startswith("test_"):
        return Finding(root.name, relative, size, "TEST", "REVIEW", "Test requires fixture/privacy review")
    if suffix == ".py":
        return Finding(root.name, relative, size, "SOURCE_CODE", "REVIEW", "Candidate source code")
    if suffix in {".yaml", ".yml", ".toml", ".ini", ".cfg"}:
        return Finding(root.name, relative, size, "CONFIG", "REVIEW", "Configuration requires content review")
    if suffix in {".md", ".rst", ".txt"}:
        kind = "ARCHITECTURE" if {"architecture", "design"} & parts or "architect" in name else "DOCUMENTATION"
        return Finding(root.name, relative, size, kind, "REVIEW", "Documentation requires content review")
    return Finding(root.name, relative, size, "UNKNOWN", "EXCLUDE", "Not required by explicit code-focused allowlist")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("roots", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    findings: list[Finding] = []
    for root in args.roots:
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if path.is_file():
                findings.append(classify(root, path))

    lines = [
        "# GitHub Upload Audit",
        "",
        "Metadata-only audit. Paths are relative to named source snapshots; secret values are never recorded.",
        "",
        "| source | path | size_bytes | type | upload_decision | reason |",
        "|---|---|---:|---|---|---|",
    ]
    for item in findings:
        safe_path = item.path.replace("|", "\\|")
        safe_reason = item.reason.replace("|", "\\|")
        lines.append(
            f"| {item.source} | {safe_path} | {item.size} | {item.kind} | {item.decision} | {safe_reason} |"
        )
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"audited_files={len(findings)}")
    print(f"audit_bytes={sum(item.size for item in findings)}")
    for decision in ("REVIEW", "SANITIZE", "EXCLUDE"):
        print(f"{decision.lower()}={sum(item.decision == decision for item in findings)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
