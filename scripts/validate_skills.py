"""Validate every skills/<name>/SKILL.md. Exit 0 when all are valid, 1 when any is not.

Standard library only. Reads the small YAML subset that SKILL.md frontmatter uses.
"""

from __future__ import annotations

import sys
from pathlib import Path

STANDARD_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
KNOWN_USES = {"transcript", "meeting", "voice"}
USES_KEY = "s1ft-uses"


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def split_frontmatter(text: str) -> list[str] | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return lines[1:index]
    return None


def parse_block(lines: list[str]) -> dict[str, object]:
    """Parse `key: value` lines. A key with no value takes the deeper lines that follow:
    a list when they start with `- `, a nested map otherwise."""
    result: dict[str, object] = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        index += 1
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.strip().partition(":")
        if value.strip():
            result[key.strip()] = unquote(value)
            continue
        child: list[str] = []
        while index < len(lines) and (not lines[index].strip() or lines[index][0] in " \t"):
            child.append(lines[index])
            index += 1
        items = [c.strip() for c in child if c.strip()]
        if items and all(i.startswith("- ") or i == "-" for i in items):
            result[key.strip()] = [unquote(i[1:]) for i in items]
        elif items:
            dedented = [c.lstrip() for c in child]
            result[key.strip()] = parse_block(dedented)
        else:
            result[key.strip()] = ""
    return result


def validate_uses(value: object) -> str | None:
    if not isinstance(value, str):
        return f"metadata.{USES_KEY} must be a comma separated string, not a list or map"
    tokens = [token.strip() for token in value.split(",")]
    if not value.strip() or "" in tokens:
        return f"metadata.{USES_KEY} must not be empty"
    unknown = [token for token in tokens if token not in KNOWN_USES]
    if unknown:
        known = ", ".join(sorted(KNOWN_USES))
        return f"metadata.{USES_KEY} has unknown value {unknown[0]!r} (known: {known})"
    return None


def validate_skill(folder: Path) -> list[str]:
    skill_file = folder / "SKILL.md"
    if not skill_file.is_file():
        return ["SKILL.md is missing"]
    block = split_frontmatter(skill_file.read_text(encoding="utf-8"))
    if block is None:
        return ["frontmatter is missing or not closed with ---"]
    data = parse_block(block)
    errors: list[str] = []
    for key in data:
        if key not in STANDARD_KEYS:
            errors.append(f"top-level key {key!r} is not an Agent Skills standard key")
    name = data.get("name")
    if name != folder.name:
        errors.append(f"name {name!r} must equal the folder name {folder.name!r}")
    description = data.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append("description is missing or empty")
    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        errors.append(f"metadata must be a map that holds {USES_KEY}")
    elif USES_KEY not in metadata:
        errors.append(f"metadata.{USES_KEY} is missing")
    else:
        problem = validate_uses(metadata[USES_KEY])
        if problem:
            errors.append(problem)
    return errors


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parent.parent / "skills"
    if not root.is_dir():
        print(f"error: skills folder not found: {root}")
        return 1
    folders = sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith("."))
    if not folders:
        print(f"error: no skills in {root}")
        return 1
    failed = False
    for folder in folders:
        for error in validate_skill(folder):
            failed = True
            print(f"{folder.name}: {error}")
    if not failed:
        print(f"ok: {len(folders)} skill(s) valid")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
