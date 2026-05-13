"""Load ``orbitron_logical_assemblies.{yaml,yml,json}`` (nested lab / Mermaid logical graph)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


def load_logical_assemblies_spec(path: Path) -> dict[str, Any]:
    suf = path.suffix.lower()
    raw = path.read_text(encoding="utf-8")
    if suf in (".yaml", ".yml"):
        data = yaml.safe_load(raw)
    elif suf == ".json":
        data = json.loads(raw)
    else:
        raise ValueError(f"unsupported logical assemblies spec: {path} (use .yaml or .json)")
    if not isinstance(data, dict) or "root" not in data or "groups" not in data:
        raise ValueError("assemblies spec must be a mapping with 'root' and 'groups'")
    groups = data["groups"]
    if not isinstance(groups, dict):
        raise ValueError("'groups' must be a mapping")
    return data
