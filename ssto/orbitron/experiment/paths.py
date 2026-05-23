"""Report directory layout for headless experiments."""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
REPORTS_ROOT = _REPO / "reports"
VALIDATION_STEPS_MD = _REPO / "ssto" / "orbitron" / "validation_steps.md"


def experiment_slug(name: str) -> str:
    """Lower-case name with non-alphanumerics → hyphen."""
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "experiment"


def report_timestamp() -> str:
    """Local wall-clock stamp YYYY-MM-DD-HH-MM."""
    return datetime.now().strftime("%Y-%m-%d-%H-%M")


def make_report_dir(experiment_name: str, *, when: datetime | None = None) -> Path:
    """``reports/<slug>/<YYYY-MM-DD-HH-MM>/`` (adds seconds if that folder exists)."""
    slug = experiment_slug(experiment_name)
    now = when or datetime.now()
    ts = now.strftime("%Y-%m-%d-%H-%M")
    out = REPORTS_ROOT / slug / ts
    if out.exists():
        ts = now.strftime("%Y-%m-%d-%H-%M-%S")
        out = REPORTS_ROOT / slug / ts
    out.mkdir(parents=True, exist_ok=False)
    (out / "figures").mkdir(exist_ok=True)
    (out / "results").mkdir(exist_ok=True)
    return out
