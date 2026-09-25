#!/usr/bin/env python3
"""Generate Agent Ops index.md from active operating thought frontmatter.

The operating thought pages are canonical. index.md is a deterministic retrieval view.
Every declared consult_when and do_not_use_when trigger must appear; there is no
positional cutoff. Active pages must live in a routed family directory.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPERATING_THOUGHT = ROOT / "operating-thought"
INDEX = ROOT / "index.md"
FAMILY_ORDER = ["authority", "knowledge", "decisions", "design", "capabilities"]
FAMILY_TITLES = {
    "authority": "Authority, approval, and access",
    "knowledge": "Information placement and source authority",
    "decisions": "Decision quality and strategic response",
    "design": "Architecture, change, and documentation",
    "capabilities": "External capabilities and integrations",
}


def parse_frontmatter(path: Path) -> dict[str, object]:
    """Read the flat string/list grammar documented in GOVERNANCE.md, not YAML."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError(f"{path}: missing frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError(f"{path}: missing closing frontmatter delimiter") from exc
    data: dict[str, object] = {}
    current: str | None = None

    def scalar(raw: str, line: int) -> str:
        value = raw.strip()
        if value.startswith("'"):
            match = re.fullmatch(r"'((?:[^']|'')*)'(?:\s+#.*)?", value)
            if match:
                return match[1].replace("''", "'")
        elif value.startswith('"'):
            match = re.fullmatch(r'"((?:[^"\\]|\\.)*)"(?:\s+#.*)?', value)
            if match:
                try:
                    decoded = json.loads('"' + match[1] + '"')
                except ValueError:
                    pass
                else:
                    if "\n" in decoded or "\r" in decoded:
                        raise ValueError(f"{path}:{line}: metadata strings must be single-line")
                    return decoded
        else:
            value = re.split(r"\s+#", value, maxsplit=1)[0].strip()
            if value and value[0] not in "[]{}|>&*!#" and value not in {"null", "~", "true", "false"}:
                return value
        raise ValueError(f"{path}:{line}: unsupported metadata scalar {raw!r}")

    for number, raw in enumerate(lines[1:end], 2):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        match = re.fullmatch(r"([a-z_]+):(?:[ \t]+(.*))?", raw)
        if match:
            key, value = match.groups()
            if key in data:
                raise ValueError(f"{path}:{number}: duplicate metadata key {key}")
            value = (value or "").strip()
            if not value or value.startswith("#"):
                data[key] = []
                current = key
            elif re.fullmatch(r"\[\](?:\s+#.*)?", value):
                data[key] = []
                current = None
            else:
                data[key] = scalar(value, number)
                current = None
            continue
        match = re.fullmatch(r"  - (.+)", raw)
        if match and current is not None:
            values = data[current]
            assert isinstance(values, list)
            values.append(scalar(match[1], number))
            continue
        raise ValueError(f"{path}:{number}: unsupported metadata syntax {raw!r}")
    return data


def validate_metadata(path: Path, meta: dict[str, object]) -> None:
    """Validate all operating-thought records before inactive-page filtering."""
    scalar_fields = {"id", "title", "type", "status", "authority", "confidence",
                     "router_summary", "last_material_revision", "lineage"}
    list_fields = {"confidence_basis", "scope", "consult_when", "do_not_use_when",
                   "decision_effect", "implemented_by", "known_failures", "review_when"}
    errors = []
    missing = sorted((scalar_fields | list_fields) - meta.keys())
    if missing:
        errors.extend(f"missing {key}" for key in missing)
    for key in sorted(scalar_fields & meta.keys()):
        if not isinstance(meta[key], str) or not meta[key].strip():
            errors.append(f"{key} must be a nonempty string")
    for key in sorted(list_fields & meta.keys()):
        value = meta[key]
        if not isinstance(value, list) or any(not isinstance(v, str) or not v.strip() for v in value):
            errors.append(f"{key} must be a list of nonempty strings")
    for key in ("consult_when", "do_not_use_when", "confidence_basis", "review_when"):
        if not meta.get(key):
            errors.append(f"empty {key}")
    enums = {
        "type": {"operating-thought"},
        "status": {"active", "superseded", "archived"},
        "authority": {"adopted", "advisory", "historical"},
        "confidence": {"low", "medium", "high", "mixed", "not-applicable"},
    }
    for key, allowed in enums.items():
        value = meta.get(key)
        if not isinstance(value, str) or value not in allowed:
            errors.append(f"invalid {key}: {value!r}")
    if meta.get("status") == "active" and meta.get("authority") == "historical":
        errors.append("active authority must be adopted or advisory")
    if errors:
        raise ValueError(f"{path}: " + "; ".join(errors))


def items(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(v) for v in value]
    if value:
        return [str(value)]
    return []


def discover_active_pages(
    root: Path | None = None,
) -> tuple[list[tuple[str, Path, dict[str, object]]], list[Path]]:
    """Return routed (family, path, meta) pages and active pages outside FAMILY_ORDER."""
    root = root or ROOT
    routed: list[tuple[str, Path, dict[str, object]]] = []
    unknown: list[Path] = []
    operating_thought = root / "operating-thought"
    if not operating_thought.is_dir():
        return routed, unknown
    errors: list[str] = []
    ids: dict[str, Path] = {}
    for path in sorted(operating_thought.rglob("*.md")):
        try:
            meta = parse_frontmatter(path)
            validate_metadata(path, meta)
        except (ValueError, OSError) as exc:
            errors.append(str(exc))
            continue
        ident = str(meta["id"])
        if ident in ids:
            errors.append(f"duplicate operating thought id {ident}: {ids[ident]} and {path}")
        ids[ident] = path
        if meta.get("status") != "active":
            continue
        rel = path.relative_to(operating_thought)
        if len(rel.parts) != 2 or rel.parts[0] not in FAMILY_ORDER:
            unknown.append(path)
            continue
        routed.append((rel.parts[0], path, meta))
    if errors:
        raise ValueError("\n".join(errors))
    return routed, unknown


def join_triggers(values: list[str]) -> str:
    if not values:
        return ""
    text = "; ".join(values)
    if not text.endswith("."):
        text += "."
    return text


def page_block(root: Path, path: Path, meta: dict[str, object]) -> str:
    title = str(meta.get("title") or path.stem.replace("-", " ").title())
    summary = str(meta.get("router_summary") or "")
    consult = items(meta.get("consult_when"))
    skip = items(meta.get("do_not_use_when"))
    rel = path.relative_to(root).as_posix()
    block = [f"### [{title}]({rel})"]
    if summary:
        block.append(summary)
    if consult:
        block.append("**Consult when:** " + join_triggers(consult))
    if skip:
        block.append("**Do not use when:** " + join_triggers(skip))
    return "\n\n".join(block)


def render(root: Path | None = None) -> str:
    root = root or ROOT
    routed, unknown = discover_active_pages(root)
    if unknown:
        names = ", ".join(path.relative_to(root).as_posix() for path in unknown)
        raise ValueError(
            "active operating thought is not in a routed family: " + names
        )
    by_family: dict[str, list[str]] = {family: [] for family in FAMILY_ORDER}
    for family, path, meta in routed:
        by_family[family].append(page_block(root, path, meta))
    sections = [
        f"## {FAMILY_TITLES[family]}\n\n" + "\n\n".join(by_family[family])
        for family in FAMILY_ORDER
        if by_family[family]
    ]
    preamble = """# Agent Ops router

> Generated by `scripts/generate_index.py` from active operating thought frontmatter. Do not edit this file by hand.

Agent Ops is the agent's retrievable operating judgment. It is not a second SOUL, a tool inventory, or an encyclopedia.

## Router use

Persistent SOUL owns activation and re-entry behavior. Use the boundary map below when the exact owner is not already current. This generated view routes owner selection; it does not own activation.

## Boundary routing

- **Representation** → [Information Placement and Source Authority](operating-thought/knowledge/information-placement-and-source-authority.md) + domain skill — do not promote unknown to zero/false.
- **Causal inference** → [Decision Quality Under Uncertainty](operating-thought/decisions/decision-quality-under-uncertainty.md) + diagnostic skill — do not promote observation to cause.
- **Authority/effect** → [Permissions, Controls, and Discretion](operating-thought/authority/permissions-controls-and-discretion.md) + acting skill — capability is not authority; acknowledgement is not effect.
- **Outcome verification** → `artifact-verification` — do not promote tool success to user-visible success.
- **Correction** → source analysis and the canonical owner — repair dependent claims, artifacts, actions, and records.
- **Retention/stopping** → [Right-Sized Change](operating-thought/design/right-sized-change.md) + canonical owner — do not retain or compose machinery without material decision or acceptance value.

"""
    return preamble + "\n\n".join(sections) + "\n"


def active_router_blocks(text: str) -> dict[str, list[str]]:
    """Only live, linked level-three headings own router trigger paragraphs."""
    text = re.sub(r"<!--.*?(?:-->|\Z)", "", text, flags=re.S)
    active = []
    fence = None
    for line in text.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
            continue
        if marker:
            fence = marker[1]
            continue
        active.append(line)
    blocks: dict[str, list[str]] = {}
    owner = None
    for line in active:
        if re.match(r"^ {0,3}#{1,3}(?:\s|$)", line):
            match = re.fullmatch(r"### \[[^\]\n]+\]\(([^)\n]+)\)", line)
            owner = match[1] if match else None
            if owner:
                blocks.setdefault(owner, []).append("")
        elif owner:
            blocks[owner][-1] += line + "\n"
    return blocks


def coverage_errors(root: Path | None = None) -> list[str]:
    """Fail if an active page or declared trigger is missing from the generated router."""
    root = root or ROOT
    index_path = root / "index.md"
    index_text = index_path.read_text(encoding="utf-8") if index_path.is_file() else ""
    errors: list[str] = []
    try:
        routed, unknown = discover_active_pages(root)
    except (ValueError, OSError) as exc:
        return str(exc).splitlines()
    for path in unknown:
        errors.append(
            "active operating thought is not in a routed family: "
            + path.relative_to(root).as_posix()
        )
    blocks = active_router_blocks(index_text)
    for family, path, meta in routed:
        rel = path.relative_to(root).as_posix()
        owned = blocks.get(rel, [])
        if len(owned) != 1:
            errors.append(f"router omitted active page or duplicated linked heading: {rel}")
            continue
        for kind, key, label in (("consult", "consult_when", "Consult when"),
                                 ("skip", "do_not_use_when", "Do not use when")):
            paragraphs = re.findall(r"(?m)^\*\*" + label + r":\*\* (.+)$", owned[0])
            for item in items(meta.get(key)):
                if len(paragraphs) != 1 or item not in paragraphs[0]:
                    errors.append(f"router omitted {kind} trigger from {rel}: {item}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        generated = render()
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if args.check:
        current = INDEX.read_text(encoding="utf-8") if INDEX.exists() else ""
        if current != generated:
            print("index.md is stale; run scripts/generate_index.py", file=sys.stderr)
            return 1
        print("index.md matches active operating thought frontmatter")
        return 0
    INDEX.write_text(generated, encoding="utf-8")
    print(f"wrote {INDEX}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
