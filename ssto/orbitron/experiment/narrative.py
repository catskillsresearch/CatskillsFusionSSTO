"""Extract stage mathematics and narrative from validation_steps.md."""
from __future__ import annotations

import re
from pathlib import Path

from ssto.orbitron.experiment.paths import VALIDATION_STEPS_MD

_REPO = Path(__file__).resolve().parents[3]
_UNOBTANIUM_MD = _REPO / "ssto" / "orbitron" / "UNOBTANIUM.md"
_PB11_REACTION_MD = _REPO / "pb11.md"
_PROTON_BORON_RAND_MD = _REPO / "proton_boron_rand.md"

_STEP_HEADING = re.compile(r"^### Step (\d+)\s*[—–-]", re.MULTILINE)
_DISPLAY_MATH = re.compile(r"\\\[(.*?)\\\]", re.DOTALL)
_INLINE_MATH = re.compile(r"\\\((.*?)\\\)", re.DOTALL)


def _simplify_math_body(body: str) -> str:
    """Make LaTeX bodies render in GitHub / VS Code $…$ preview."""
    body = body.replace(r"\text{--}", "–")
    body = body.replace(r"\text{–}", "–")
    body = body.replace(r"\text{-}", "-")
    body = re.sub(r"\\mathrm\{([^}]+)\}", r"\1", body)
    body = re.sub(r"\\mathbf\{([^}]+)\}", r"\1", body)
    return body


def md_math_for_preview(text: str) -> str:
    """
    Convert LaTeX ``\\( … \\)`` / ``\\[ … \\]`` to ``$…$`` / ``$$…$$``.

    ``validation_steps.md`` and gap-agent output use ``\\(`` delimiters; most markdown
    previews (Cursor, VS Code, GitHub) need ``$`` / ``$$``.
    """

    def _display(m: re.Match[str]) -> str:
        body = _simplify_math_body(m.group(1).strip())
        return f"$$\n{body}\n$$"

    def _inline(m: re.Match[str]) -> str:
        body = _simplify_math_body(m.group(1).strip())
        return f"${body}$"

    out = _DISPLAY_MATH.sub(_display, text)
    out = _INLINE_MATH.sub(_inline, out)
    # Bare $$ blocks from agent output
    out = re.sub(
        r"\$\$([^$]+)\$\$",
        lambda m: f"$$\n{_simplify_math_body(m.group(1).strip())}\n$$",
        out,
        flags=re.DOTALL,
    )
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


def equations_for_step(step: int, equations: dict[int, str]) -> str:
    """Equations-only slice for a proof-chain step (no operational / script narrative)."""
    if step not in equations:
        return ""
    return inline_publishable_markdown(equations[step])


_MD_LINK = re.compile(r"\[([^\]]+)\]\([^)]+\)")
_CODE_FENCE = re.compile(r"```[\s\S]*?```", re.MULTILINE)
_POINTER_LINE = re.compile(
    r"^\s*(\*\*Related:\*\*|See \*\*|Guides:|See \[|^\*\*GUI simulator:\*\*)",
    re.I | re.MULTILINE,
)


def inline_publishable_markdown(md: str, *, cap_headings_at: int | None = 3) -> str:
    """
    Prepare SSOT/gap text for REPORT.md: keep math, drop code fences and doc pointers.

    ``cap_headings_at``: demote headings deeper than this level (``None`` = leave as-is).
    """
    text = _CODE_FENCE.sub("", md)
    text = _MD_LINK.sub(r"\1", text)
    kept: list[str] = []
    for line in text.splitlines():
        if _POINTER_LINE.search(line):
            continue
        if re.search(r"\.md\)|\.md`|/[\w-]+\.md", line, re.I):
            continue
        kept.append(line)
    text = "\n".join(kept)
    if cap_headings_at is not None and cap_headings_at >= 1:
        cap = "#" * cap_headings_at
        text = re.sub(rf"^#{{{cap_headings_at + 1},}}\s+", f"{cap} ", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return md_math_for_preview(text)


def load_equations_ssot_block(md_path: Path | None = None) -> str:
    """Full state-evolution equations (steps 0–8) for embedding in the report."""
    path = md_path or VALIDATION_STEPS_MD
    text = path.read_text(encoding="utf-8")
    block = _split_sections(
        text,
        "## State evolution (equations SSOT)",
        "## Step-by-step (apps, dependencies, gates)",
    )
    return inline_publishable_markdown(block)


def load_fidelity_and_claims_block(md_path: Path | None = None) -> str:
    """Fidelity ladder + proof-claim criteria (no command cheatsheet)."""
    path = md_path or VALIDATION_STEPS_MD
    text = path.read_text(encoding="utf-8")
    block = _split_sections(text, "## Fidelity ladder (what each tier proves)", "## Individual commands")
    if not block:
        block = _split_sections(
            text,
            "## Fidelity ladder (what each tier proves)",
            None,
        )
    return inline_publishable_markdown(block)


def _demote_markdown_headings(md: str, *, extra_levels: int = 1, max_level: int = 4) -> str:
    """Shift heading depth (e.g. embed ``pb11.md`` ``##`` as ``###`` under a report section)."""
    out: list[str] = []
    for line in md.splitlines():
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            level = min(len(m.group(1)) + extra_levels, max_level)
            out.append("#" * level + " " + m.group(2).strip())
        else:
            out.append(line)
    return "\n".join(out)


def _flatten_markdown_bullets(md: str) -> str:
    flat: list[str] = []
    for line in md.splitlines():
        m = re.match(r"^(\s{2,})[-*]\s+(.*)$", line)
        if m:
            flat.append(f"- {m.group(2).strip()}")
        else:
            flat.append(line)
    return "\n".join(flat)


def _slice_markdown_file(path: Path, start: str, end: str | None) -> str:
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8")
    block = _split_sections(text, start, end)
    lines = block.splitlines()
    if lines and lines[0].strip().startswith(start.strip().split()[0]):
        first = lines[0].strip()
        if first == start.strip() or first.startswith(start.strip()[:12]):
            lines = lines[1:]
    while lines and not lines[0].strip():
        lines.pop(0)
    return "\n".join(lines).strip()


def _prepare_fusion_embed(md: str, *, demote_levels: int) -> str:
    md = re.sub(r"^---\s*$", "", md, flags=re.MULTILINE)
    md = _demote_markdown_headings(md, extra_levels=demote_levels, max_level=4)
    md = _flatten_markdown_bullets(md)
    return inline_publishable_markdown(md, cap_headings_at=4)


def load_pb11_fusion_reaction_block(
    pb11_path: Path | None = None,
    proton_boron_path: Path | None = None,
) -> str:
    """
    Full in-repo p-¹¹B physics narrative (self-contained in the report).

    Sources (inlined, not linked):
    - ``pb11.md`` — compact multi-step pathway
    - ``proton_boron_rand.md`` Reply 4 — 8 GK threshold, Coulomb barrier, resonances, decay
    - ``proton_boron_rand.md`` Reply 5 — non-thermal 600 kV Orbitron vs thermal temperature
    - ``proton_boron_rand.md`` Reply 6 §2 — annotated emissions and side reactions
    """
    pb11_path = pb11_path or _PB11_REACTION_MD
    proton_boron_path = proton_boron_path or _PROTON_BORON_RAND_MD
    chunks: list[str] = []

    if pb11_path.is_file():
        raw = pb11_path.read_text(encoding="utf-8")
        lines = raw.splitlines()
        while lines and not lines[0].strip():
            lines.pop(0)
        if lines and lines[0].startswith("# "):
            lines.pop(0)
            while lines and not lines[0].strip():
                lines.pop(0)
        body = _prepare_fusion_embed("\n".join(lines), demote_levels=1)
        if body:
            chunks.append(f"### Reaction pathway (overview)\n\n{body}")

    if proton_boron_path.is_file():
        reply4 = _slice_markdown_file(proton_boron_path, "## Reply 4", "## Prompt 5")
        if reply4:
            chunks.append(
                "### Thermodynamic threshold, Coulomb barrier, and sequential decay\n\n"
                + _prepare_fusion_embed(reply4, demote_levels=2)
            )
        reply5 = _slice_markdown_file(proton_boron_path, "## Reply 5", "## Prompt 6")
        if reply5:
            chunks.append(
                "### 600 kV Orbitron beams vs billion-Kelvin thermal heat\n\n"
                + _prepare_fusion_embed(reply5, demote_levels=2)
            )
        annotated = _slice_markdown_file(
            proton_boron_path,
            "### 2. Step-by-Step Reaction Annotation",
            "## Prompt 7",
        )
        if annotated:
            chunks.append(
                "### Particles emitted at each step (primary chain and side channels)\n\n"
                + _prepare_fusion_embed(annotated, demote_levels=2)
            )

    return "\n\n".join(chunks)


def load_unobtanium_basis_block(md_path: Path | None = None) -> str:
    """Design-basis prose and U1–U4 specs (no repo / GUI run instructions)."""
    path = md_path or _UNOBTANIUM_MD
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8")
    # Drop top matter that only points at other docs / install commands.
    start = text.find("**Context:**")
    if start < 0:
        start = text.find("## U1")
    if start < 0:
        start = 0
    end = text.find("## Removed from design")
    if end < 0:
        end = len(text)
    return inline_publishable_markdown(text[start:end])
