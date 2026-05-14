"""Load unified Orbitron lab YAML (schema v2) or legacy logical-only YAML / JSON.

Schema v2: ``orbitron_lab.yaml`` with ``logical: { root, groups, connections, glossary }``.
Legacy: top-level ``root`` + ``groups`` (e.g. old ``orbitron_logical_assemblies.yaml``).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


def load_logical_assemblies_spec(path: Path) -> dict[str, Any]:
    suf = path.suffix.lower()
    raw_text = path.read_text(encoding="utf-8")
    if suf in (".yaml", ".yml"):
        data = yaml.safe_load(raw_text)
    elif suf == ".json":
        data = json.loads(raw_text)
    else:
        raise ValueError(f"unsupported assemblies spec: {path} (use .yaml, .yml, or .json)")
    if not isinstance(data, dict):
        raise ValueError("assemblies spec must be a mapping")

    if int(data.get("schema_version", 1)) >= 2 and "logical" in data:
        L = data["logical"]
        if not isinstance(L, dict):
            raise ValueError("schema v2 requires mapping 'logical'")
        out = {
            "root": L["root"],
            "glossary": L.get("glossary", []),
            "connections": L.get("connections", []),
            "groups": L["groups"],
        }
        if "root" not in out or "groups" not in out:
            raise ValueError("logical.root and logical.groups are required for schema v2")
        if not isinstance(out["groups"], dict):
            raise ValueError("'logical.groups' must be a mapping")
        return out

    if "root" not in data or "groups" not in data:
        raise ValueError("assemblies spec must have 'root' and 'groups' (or schema v2 with 'logical')")
    groups = data["groups"]
    if not isinstance(groups, dict):
        raise ValueError("'groups' must be a mapping")
    return data
