"""Extract stage mathematics and narrative from validation_steps.md."""
from __future__ import annotations

import re
from pathlib import Path

from ssto.orbitron.experiment.paths import VALIDATION_STEPS_MD

_STEP_HEADING = re.compile(r"^### Step (\d+)\s*[—–-]", re.MULTILINE)
_DISPLAY_MATH = re.compile(r"\\\[(.*?)\]", re.DOTALL)
_INLINE_MATH = re.compile(r"\\\((.*?)\\\)", re.DOTALL)


def md_math_for_preview(text: str) -> str:
    """
    Convert LaTeX ``\\( … \\)`` / ``\\[ … \\]`` to ``$…$`` / ``$$…$$``.

    ``validation_steps.md`` uses LaTeX delimiters; Cursor/VS Code markdown preview
    (Ctrl+Shift+V) renders ``$`` / ``$$`` but not ``\\(`` / ``\\[`` by default.
    """

    def _display(m: re.Match[str]) -> str:
        body = m.group(1).strip()
        return f"$$\n{body}\n$$"

    out = _DISPLAY_MATH.sub(_display, text)
    out = _INLINE_MATH.sub(r"$\1$", out)
    return out


def _split_sections(text: str, start_marker: str, end_marker: str | None) -> str:
    i = text.find(start_marker)
    if i < 0:
        return ""
    i += len(start_marker)
    if end_marker:
        j = text.find(end_marker, i)
        if j < 0:
            j = len(text)
        return text[i:j].strip()
    return text[i:].strip()


def _sections_by_step(block: str) -> dict[int, str]:
    out: dict[int, str] = {}
    matches = list(_STEP_HEADING.finditer(block))
    for idx, m in enumerate(matches):
        step = int(m.group(1))
        start = m.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(block)
        out[step] = block[start:end].strip()
    return out


def load_validation_narratives(
    md_path: Path | None = None,
) -> tuple[dict[int, str], dict[int, str]]:
    """
    Return (equations_ssot, step_by_step) dicts keyed by step number 0–9.
    """
    path = md_path or VALIDATION_STEPS_MD
    text = path.read_text(encoding="utf-8")
    eq_block = _split_sections(text, "## State evolution (equations SSOT)", "## Step-by-step")
    ops_block = _split_sections(text, "## Step-by-step (apps, dependencies, gates)", "## Fidelity ladder")
    return _sections_by_step(eq_block), _sections_by_section_ops(ops_block)


def _sections_by_section_ops(block: str) -> dict[int, str]:
    return _sections_by_step(block)


def narrative_for_step(
    step: int,
    *,
    equations: dict[int, str],
    operations: dict[int, str],
) -> str:
    parts: list[str] = []
    if step in equations:
        parts.append(equations[step])
    if step in operations:
        parts.append("\n\n---\n\n### Operational summary (validation_steps.md)\n\n")
        parts.append(operations[step])
    if not parts:
        return f"*(No validation_steps.md section found for step {step}.)*\n"
    return md_math_for_preview("".join(parts))
