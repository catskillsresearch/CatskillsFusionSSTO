"""LinkedIn-safe HTML export for experiment REPORT.md."""
from __future__ import annotations

from pathlib import Path
from typing import Callable, TextIO

from tools.md_to_linkedin_html import write_linkedin_html


def write_report_linkedin_html(
    report_md: Path,
    *,
    title: str | None = None,
    log: TextIO | Callable[[str], None] | Path | None = None,
) -> Path:
    """
    Write ``REPORT.html`` beside ``REPORT.md`` (Unicode math, list-style tables).

    Open in Chrome/Firefox → *Select article for copy* → paste into LinkedIn Articles.
    """
    out = write_linkedin_html(report_md, title=title)
    msg = (
        f"LinkedIn HTML: {out.name} ({out.stat().st_size:,} bytes) — "
        "open in browser, Select article for copy, paste into LinkedIn\n"
    )
    if log is not None:
        if isinstance(log, Path):
            log.parent.mkdir(parents=True, exist_ok=True)
            with log.open("a", encoding="utf-8") as f:
                f.write(msg)
        elif hasattr(log, "write"):
            log.write(msg)  # type: ignore[union-attr]
        else:
            log(msg)  # type: ignore[misc]
    return out
