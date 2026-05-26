"""Extract stage mathematics and narrative from validation_steps.md."""
from __future__ import annotations

import re
from pathlib import Path

from ssto.orbitron.experiment.paths import VALIDATION_STEPS_MD

_REPO = Path(__file__).resolve().parents[3]
_UNOBTANIUM_MD = _REPO / "ssto" / "orbitron" / "UNOBTANIUM.md"
_PB11_WHY_FUSION_MD = Path(__file__).resolve().parents[1] / "pb11_why_fusion.md"
_BENCHMARK_INTRODUCTION_MD = Path(__file__).resolve().parents[1] / "benchmark_introduction.md"
_BENCHMARK_METHODOLOGY_REPORT_MD = (
    Path(__file__).resolve().parents[1] / "benchmark_methodology_report.md"
)
_MD_FILE_REF = re.compile(
    r"(?:\(see\s+)?[`']?(?:[\w./_-]+/)?[\w.-]+\.md[`']?\)?",
    re.I,
)
_BRAYTON_AIR_CYCLE_MD = Path(__file__).resolve().parents[1] / "brayton_air_cycle.md"
_BRACKET_REFERENCE_LINE = re.compile(r"^\[(\d+)\]\s+(.+)$")
_BRAYTON_REFERENCES_HEADING = re.compile(r"\n#{2,3}\s+References\s*\n", re.IGNORECASE)

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


_DISPLAY_MATH_BLOCK = re.compile(r"^\s*\$\$\s*$", re.MULTILINE)


def _normalize_display_math_blocks(text: str) -> str:
    """
    Put ``$$`` delimiters at column 0 and dedent bodies.

    Indented ``$$`` (common under list items) leaves VS Code/KaTeX math mode open
    through following ``---`` and headings.
    """
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        if _DISPLAY_MATH_BLOCK.match(lines[i]):
            out.append("$$")
            i += 1
            body: list[str] = []
            while i < len(lines) and not _DISPLAY_MATH_BLOCK.match(lines[i]):
                body.append(lines[i].lstrip())
                i += 1
            if body:
                out.extend(body)
            if i < len(lines):
                out.append("$$")
                i += 1
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out)


def sanitize_markdown_math_for_vscode(text: str) -> str:
    """Fix constructs that break the VS Code Markdown+KaTeX preview."""
    text = _normalize_display_math_blocks(text)
    # HR lines are often parsed inside an unclosed math block; use spacing instead.
    text = re.sub(r"^---\s*$", "", text, flags=re.MULTILINE)
    # **$…$** confuses the math tokenizer; keep math delimiters only.
    text = re.sub(r"\*\*(\$[^$\n]+\$)\*\*", r"\1", text)
    text = re.sub(r"\*\*\$c\$ does not appear\.\*\*", r"$c$ does not appear.", text)
    # Single-letter bold next to display math (e.g. "**E** only") corrupts preview.
    text = re.sub(
        r"multiplies \*\*E\*\* only",
        "multiplies the electric field E only",
        text,
        flags=re.I,
    )
    text = re.sub(r"\*\*\$c\$\*\* does not appear", r"$c$ does not appear", text)
    # Prose function notation without nested $ (avoids errors if math mode stuck).
    text = re.sub(
        r"No \$f\(S\(t\)\)\$ — not a time integrator",
        "No *f(S(t))* — not a time integrator",
        text,
    )
    return re.sub(r"\n{3,}", "\n\n", text).strip()


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
    out = re.sub(
        r"\$\$([^$]+)\$\$",
        lambda m: f"$$\n{_simplify_math_body(m.group(1).strip())}\n$$",
        out,
        flags=re.DOTALL,
    )
    return sanitize_markdown_math_for_vscode(out)


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

# Lines dropped from inlined SSOT text for external readers (no implementation artifacts).
_SOFTWARE_LINE = re.compile(
    r"(?:"
    r"\.(?:py|json|yaml|npz|sh)\b|"
    r"build/orbitron|chain_config|results/step_|ORBITRON_|"
    r"poetry\s+run|pip\s+install|ssto/|tools/|scripts/|"
    r"Proof Suite|Implementation:|^\s*\*\*Display|\(C\)\s+Display|"
    r"^\|[^\n]*build/orbitron|"
    r"fusion_pb11|physics_evidence|plant_0d|validation\.py|"
    r"laminar_flow_2d|fusion_channel_sr|base_inputs|surrogate_calib|"
    r"pb11_reactivity|compile_|run_all|picmi_overrides|step_ok\.json|"
    r"JSBSim|FlightGear|holdout T|module default in|"
    r"Repo:\s*`"
    r")",
    re.I,
)

_KNOB_BACKTICK: dict[str, str] = {
    "field_emission_margin": "field-emission margin",
    "max_wall_heat_flux_W_m2": "maximum wall heat flux",
    "ch4_cooling_effectiveness": "CH₄ cooling effectiveness",
    "hts_capability_scale": "HTS capability scale",
    "fusion_reactivity_scale": "fusion reactivity scale",
    "beam_coupling_scale": "beam coupling scale",
}

_INLINE_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    (r"`plant_0d(?:\.py)?`", "0D plant model"),
    (r"`fusion_pb11(?:\.py)?`", "p-¹¹B fusion reactivity model"),
    (r"`validation(?:\.py)?`", "design validation checks"),
    (r"`pad\.throttle`", "throttle τ"),
    (r"`pad\.cathode_pulse`", "cathode pulse p"),
    (r"chain_config\.json", "run configuration"),
    (r"proof[- ]?chain", "forward model"),
    (r"proof[- ]?forward", "nominal forward model"),
    (r"proof mode", "nominal reactivity assumption"),
    (r"Tier[- ]?1", "first-tier"),
    (r"design_validated", "design gates passed"),
    (r"last `density_diag` on disk", "last electron-density diagnostic from stage 1"),
    (r"`electron_ring_only`", "electron-only model"),
    (r"`fusion_channel\.stochastic_seed`", "stochastic seed"),
    (r"same NPZ `clump_index`", "clump-index time series"),
    (r"WarpX plotfile `rho_electrons` every `diag_period` steps", "electron-density snapshots each diagnostic period"),
    (r"from step 01 artifact \+ levers", "from stage 1 output and control levers"),
    (r"\*\*Controls on screen:\*\*[^\n]+\n", ""),
    (r"\(GUI \*\*λ\*\*\)", "(injection lever λ)"),
    (r"pad \$c_\{eff\}", r"compressor effectiveness $$c_{eff}"),
    (r", pad \$c_\{eff\}", r", compressor effectiveness $$c_{eff}"),
    (r"user edits in GUI or checked-in YAML", "operator sets geometry and pad interlocks"),
    (r"full chain artifacts", "full forward-model states"),
    (r"first-tier \*\*design gates passed\*\* at nominal knobs is \*\*first-tier calibrated closure\*\*",
     "**Design gates passed** at nominal knobs reflect **first-tier calibrated closure**"),
    (r"Removed from default deck \([^)]+\)", "Omitted in the electron-only model"),
    (r"\\rho_e\^\{\\mathrm\{plotfile\}\}", r"\\rho_e^{\\mathrm{sim}}"),
    (r"first-tier plant closure\s+design closure passed", "first-tier design gates passed"),
    (r"first-tier plant closure calibrated closure", "first-tier calibrated closure"),
    (r"Macroparticle set.*`electrons` only", "Electron macroparticles"),
    (r"\$Y\$ = YAML spec bundle", r"$$Y$$ = design specification bundle"),
    (r"PIC / core YAML", "PIC / core specification"),
    (r"Tier-1 \*\*design gates passed\*\*", "**Design gates passed**"),
)

_READER_DROP_LINE = re.compile(
    r"(?:"
    r"^\| Plot \|"
    r"|plotfile|density_diag|diag_period|"
    r"^\| x–z heatmap \|"
    r"|^\| Clump vs time \|"
    r"|^\| Radial profile \|"
    r"|^\| Metrics \| Ring"
    r"|^\| \*\*Not plotted\*\* \|"
    r"|GUI or checked-in YAML"
    r")",
    re.I,
)


_LITERAL_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    ("pad $c_{eff}", "compressor effectiveness $c_{eff}$"),
    (r"pad \(c_{\mathrm{eff}}\)", "compressor effectiveness $c_{eff}$"),
    ("$Y$ = YAML spec bundle", "$Y$ = design specification bundle"),
    (r"\(Y\) = YAML spec bundle", "$Y$ = design specification bundle"),
)


def _apply_literal_reader_replacements(text: str) -> str:
    for old, new in _LITERAL_REPLACEMENTS:
        text = text.replace(old, new)
    return text


def strip_software_implementation_references(md: str) -> str:
    """Remove implementation paths, modules, and repo pointers from reader-facing prose."""
    text = _apply_literal_reader_replacements(md)
    for key, label in _KNOB_BACKTICK.items():
        text = text.replace(f"`{key}`", label)
    for pattern, repl in _INLINE_REPLACEMENTS:
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
    kept: list[str] = []
    for line in text.splitlines():
        if not line.strip():
            kept.append("")
            continue
        if _SOFTWARE_LINE.search(line) or _READER_DROP_LINE.search(line):
            continue
        if re.search(r"\.md\)|\.md`|/[\w-]+\.md", line, re.I):
            continue
        line = _MD_FILE_REF.sub("", line)
        line = re.sub(r"\(\s*\)", "", line)
        line = re.sub(r"\s{2,}", " ", line).strip()
        if line:
            kept.append(line)
    text = "\n".join(kept)
    text = re.sub(
        r"The throttle lever τ \(ring density scale\) is distinct from beam fueling\.\s*",
        "The throttle lever τ (ring density scale) is distinct from beam fueling.\n\n",
        text,
        count=1,
    )
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def inline_publishable_markdown(
    md: str,
    *,
    cap_headings_at: int | None = 3,
    preserve_code_fences: bool = False,
    strip_implementation_refs: bool = True,
) -> str:
    """
    Prepare SSOT/gap text for REPORT.md: keep math, drop code fences and doc pointers.

    ``cap_headings_at``: demote headings deeper than this level (``None`` = leave as-is).
    """
    text = md if preserve_code_fences else _CODE_FENCE.sub("", md)
    if strip_implementation_refs:
        text = strip_software_implementation_references(text)
    text = _MD_LINK.sub(r"\1", text)
    kept: list[str] = []
    for line in text.splitlines():
        if _POINTER_LINE.search(line):
            continue
        kept.append(line)
    text = "\n".join(kept)
    if cap_headings_at is not None and cap_headings_at >= 1:
        cap = "#" * cap_headings_at
        text = re.sub(rf"^#{{{cap_headings_at + 1},}}\s+", f"{cap} ", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    text = md_math_for_preview(text)
    return _apply_literal_reader_replacements(text)


def load_equations_ssot_block(md_path: Path | None = None) -> str:
    """Full state-evolution equations (steps 0–8) for embedding in the report."""
    path = md_path or VALIDATION_STEPS_MD
    text = path.read_text(encoding="utf-8")
    block = _split_sections(
        text,
        "## State evolution (equations SSOT)",
        "## Step-by-step (apps, dependencies, gates)",
    )
    body = inline_publishable_markdown(block)
    empty_compile = "**Update (algebraic, one shot):**\n\n$$\n\n$$"
    if empty_compile in body:
        body = body.replace(
            empty_compile,
            "**Update (algebraic, one shot):**\n\n$$\n"
            r"\mathbf{S}_1 = \mathrm{Compile}(Y, G, I)"
            "\n$$",
            1,
        )
    return body


_READER_FIDELITY_TABLE = """| Tier | Mechanism | What it proves |
|------|-----------|----------------|
| **0** | Pad interlock sequence | Correct startup order before fueling and reaction |
| **1** | 0D plant + U1–U4 gates | **3.5 MW** headline, jet closure, materials limits |
| **2** | Electron-ring simulation (stages 1–2) | Density and beam coupling at 600 kV — **not** fusion Q |
| **3** | p-¹¹B channel + burn models | ⟨σv⟩(T_i) × fueling × volume; laminar / clump checks |
| **4** | *Future* | Transport-integrated reactivity without analytical surrogate blend |

**Critical honesty:** The electron-ring simulation integrates **electrons in prescribed E×B fields only**. It does not include fuel species, compressor airflow, or p-¹¹B fusion yield. Fueling and the air-breathing Brayton path enter at later stages.
"""


def load_fidelity_and_claims_block(md_path: Path | None = None) -> str:
    """Fidelity ladder + what would constitute first-principles proof (reader-facing)."""
    path = md_path or VALIDATION_STEPS_MD
    text = path.read_text(encoding="utf-8")
    claims = _split_sections(text, "## When you can claim", "## Mapping chain")
    if not claims:
        claims = _split_sections(text, "## When you can claim", "## Individual commands")
    mapping = _split_sections(text, "## Mapping chain", "## Individual commands")
    if not mapping:
        mapping = _split_sections(text, "## Mapping chain", None)
    parts = [_READER_FIDELITY_TABLE]
    if claims:
        parts.append(claims)
    if mapping:
        mapping = re.sub(
            r"\| 8 \| Spec-ready YAML for UNOBTANIUM / test stand \|",
            "| 8 | Design validation summary |",
            mapping,
        )
        parts.append(mapping)
    return inline_publishable_markdown("\n\n".join(parts))


def _flatten_markdown_bullets(md: str) -> str:
    flat: list[str] = []
    for line in md.splitlines():
        m = re.match(r"^(\s{2,})[-*]\s+(.*)$", line)
        if m:
            flat.append(f"- {m.group(2).strip()}")
        else:
            flat.append(line)
    return "\n".join(flat)


def load_benchmark_introduction_block(
    md_path: Path | None = None,
) -> str:
    """Reader-facing benchmark introduction from ``ssto/orbitron/benchmark_introduction.md``."""
    path = md_path or _BENCHMARK_INTRODUCTION_MD
    if not path.is_file():
        return ""
    raw = path.read_text(encoding="utf-8").strip()
    return inline_publishable_markdown(
        raw,
        cap_headings_at=None,
        strip_implementation_refs=False,
    )


def load_benchmark_methodology_block(
    md_path: Path | None = None,
) -> str:
    """Benchmark methodology body for REPORT.md (no cross-file doc links)."""
    path = md_path or _BENCHMARK_METHODOLOGY_REPORT_MD
    if not path.is_file():
        return ""
    raw = path.read_text(encoding="utf-8").strip()
    return inline_publishable_markdown(
        raw,
        cap_headings_at=3,
        strip_implementation_refs=True,
    )


def load_pb11_fusion_reaction_block(
    md_path: Path | None = None,
) -> str:
    """Reader-facing ``Why p-¹¹B fusion?`` body from ``ssto/orbitron/pb11_why_fusion.md``."""
    path = md_path or _PB11_WHY_FUSION_MD
    if not path.is_file():
        return ""
    raw = path.read_text(encoding="utf-8").strip()
    return _flatten_markdown_bullets(inline_publishable_markdown(raw, cap_headings_at=4))


def load_brayton_air_cycle_block(
    md_path: Path | None = None,
) -> tuple[str, list[tuple[int, str]]]:
    """
    Reader-facing Brayton-cycle background from ``ssto/orbitron/brayton_air_cycle.md``.

    Returns ``(body, references)`` where ``references`` are ``(number, citation)`` pairs.
    """
    path = md_path or _BRAYTON_AIR_CYCLE_MD
    if not path.is_file():
        return "", []
    raw = path.read_text(encoding="utf-8").strip()
    refs: list[tuple[int, str]] = []
    ref_m = _BRAYTON_REFERENCES_HEADING.search(raw)
    if ref_m:
        for line in raw[ref_m.end() :].splitlines():
            line = line.strip()
            if not line:
                continue
            m = _BRACKET_REFERENCE_LINE.match(line)
            if m:
                refs.append((int(m.group(1)), m.group(2).strip()))
        raw = raw[: ref_m.start()].strip()
    body = _flatten_markdown_bullets(
        inline_publishable_markdown(
            raw,
            cap_headings_at=4,
            preserve_code_fences=True,
            strip_implementation_refs=False,
        )
    )
    return body, refs


_TWO_COL_TABLE_ROW = re.compile(r"^\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*$")
_GFM_TABLE_SEP = re.compile(r"^\|[\s\-:|]+\|\s*$")


def _spec_tables_to_bullets(md: str) -> str:
    """
    Convert ``| Spec | Value |`` GFM tables to bullet lines (LinkedIn-safe, no half-pipe layout).
    """
    lines = md.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        hm = _TWO_COL_TABLE_ROW.match(line.strip())
        if (
            hm
            and hm.group(1).strip().lower() == "spec"
            and i + 1 < len(lines)
            and _GFM_TABLE_SEP.match(lines[i + 1].strip())
        ):
            i += 2
            while i < len(lines):
                dm = _TWO_COL_TABLE_ROW.match(lines[i].strip())
                if not dm:
                    break
                out.append(f"- **{dm.group(1).strip()}:** {dm.group(2).strip()}")
                i += 1
            out.append("")
            continue
        out.append(line)
        i += 1
    return "\n".join(out)


def load_unobtanium_basis_block(md_path: Path | None = None) -> str:
    """Design-basis prose and U1–U4 specs (no repo / GUI run instructions)."""
    path = md_path or _UNOBTANIUM_MD
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8")
    # U1–U4 specs only (skip workflow / simulator install prose).
    start = text.find("## U1")
    if start < 0:
        start = text.find("**Context:**")
    if start < 0:
        start = 0
    end = text.find("## Removed from design")
    if end < 0:
        end = len(text)
    body = inline_publishable_markdown(text[start:end])
    return _spec_tables_to_bullets(body)
