"""Load Cursor API credentials from env or a local YAML file (never committed)."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

# Outside repo by default — override with ORBITRON_TOKENS_YAML.
DEFAULT_TOKENS_PATH = Path("/home/catskills/Desktop/tokens_ssto.yaml")

_TOKEN_KEYS = (
    "CURSOR_API_KEY",
    "cursor_api_key",
    "cursor.api_key",
)


def tokens_yaml_path() -> Path:
    raw = os.environ.get("ORBITRON_TOKENS_YAML", "").strip()
    if raw:
        return Path(raw).expanduser().resolve()
    return DEFAULT_TOKENS_PATH.expanduser().resolve()


def _extract_key(data: Any) -> str | None:
    if isinstance(data, str):
        return data.strip() or None
    if not isinstance(data, dict):
        return None
    for key in _TOKEN_KEYS:
        val = data.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    cursor = data.get("cursor")
    if isinstance(cursor, dict):
        for key in ("api_key", "CURSOR_API_KEY", "apiKey"):
            val = cursor.get(key)
            if isinstance(val, str) and val.strip():
                return val.strip()
    return None


def load_cursor_api_key(*, path: Path | None = None) -> str | None:
    """
    Resolve Cursor API key: ``CURSOR_API_KEY`` env first, then tokens YAML file.
    """
    env = os.environ.get("CURSOR_API_KEY", "").strip()
    if env:
        return env

    path = path or tokens_yaml_path()
    if not path.is_file():
        return None

    import yaml

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return _extract_key(data)


def apply_cursor_api_key_to_env(*, path: Path | None = None) -> str | None:
    """
    Load key and set ``os.environ['CURSOR_API_KEY']`` for cursor-sdk. Returns key or None.
    """
    key = load_cursor_api_key(path=path)
    if key:
        os.environ["CURSOR_API_KEY"] = key
    return key
