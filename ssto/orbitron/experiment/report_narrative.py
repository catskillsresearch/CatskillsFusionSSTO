"""LinkedIn-ready narrative sections for experiment REPORT.md (physics audience)."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ssto.orbitron.experiment.assembly_narrative import ASSEMBLY_WALKTHROUGH
from ssto.orbitron.experiment.narrative import (
    inline_publishable_markdown,
    load_benchmark_introduction_block,
    load_benchmark_methodology_block,
    load_brayton_air_cycle_block,
    load_equations_ssot_block,
    load_fidelity_and_claims_block,
    load_pb11_fusion_reaction_block,
    load_unobtanium_basis_block,
)
from ssto.orbitron.experiment.benchmark_scenarios import benchmark_scenarios_table_md
from ssto.orbitron.experiment.report_formatting import (
    gap_factors_table_md,
    physics_parameters_md,
    step_metrics_row,
)
from ssto.orbitron.experiment.runner import ExperimentRunResult



def _target_mw(result: ExperimentRunResult) -> float:
    scales = result.parameters.get("plant_scales") or {}
    return float(scales.get("target_gross_power_mw", 3.5))


def _is_in_silico_benchmark(result: ExperimentRunResult) -> bool:
    return "in silico benchmark" in result.experiment.experiment_name.lower()


def _embed_figure(
    report_dir: Path,
    figures: dict[str, str | None],
    key: str,
    caption: str,
) -> str:
    name = figures.get(key)
    if not name:
        return ""
    rel = f"figures/{name}"
    return f"![{caption}]({rel})\n\n"


def _flatten_markdown_bullets(md: str) -> str:
    """No nested bullet lists in the published report."""
    out: list[str] = []
    for line in md.splitlines():
        m = re.match(r"^(\s{2,})[-*]\s+(.*)$", line)
        if m:
            out.append(f"- {m.group(2).strip()}")
        else:
            out.append(line)
    return "\n".join(out)


def _strip_leading_h1(md: str) -> str:
    lines = md.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines and lines[0].startswith("# "):
        lines.pop(0)
        while lines and not lines[0].strip():
            lines.pop(0)
    return "\n".join(lines)


_GAP_HTML_COMMENT = re.compile(r"<!--[\s\S]*?-->\s*")
_GAP_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
_GAP_NUMBERED_HEADING = re.compile(r"^\d+\.\s+")
_OVERALL_LIKELIHOOD = re.compile(
    r"^\*\*(Overall likelihood of closing[^*]+)\*\*\s*$",
    re.IGNORECASE,
)
_GAP_LOCAL_REFERENCE = re.compile(
    r"(?:"
    r"repo:|ssto/|tools/|scripts/|build/orbitron|"
    r"fusion_pb11|physics_evidence|UNOBTANIUM\.md|SIMULATOR\.md|"
    r"\.py`|\.json`|design basis\s*/\s*fidelity|"
    r"⟨σv⟩\s*design\s*vs\s*literature|sigma.*design\s*vs\s*literature"
    r")",
    re.I,
)
_GAP_TABLE_ROW = re.compile(r"^\|([^|]+)\|([^|]+)\|?\s*$")


def _is_local_gap_reference(topic: str, reference: str) -> bool:
    return bool(_GAP_LOCAL_REFERENCE.search(f"{topic} {reference}"))


def _extract_gap_reference_rows(body: str) -> list[tuple[str, str]]:
    """Parse Sources table rows (valid GFM or collapsed single-line)."""
    rows: list[tuple[str, str]] = []
    for line in body.splitlines():
        line = line.strip()
        if not line or re.match(r"^\|[-:\s|]+\|$", line):
            continue
        m = _GAP_TABLE_ROW.match(line)
        if not m:
            continue
        topic, ref = m.group(1).strip(), m.group(2).strip()
        if topic.lower() in ("topic", "reference") or topic.startswith(":---"):
            continue
        rows.append((topic, ref))
    if rows:
        return rows
    collapsed = " ".join(body.split())
    for chunk in re.split(r"\s*\|\s*\|\s*", collapsed):
        chunk = chunk.strip().strip("|").strip()
        if not chunk or chunk.lower().startswith("topic"):
            continue
        if "|" in chunk:
            topic, _, ref = chunk.partition("|")
            rows.append((topic.strip(), ref.strip()))
    return rows


def _format_references_section(rows: list[tuple[str, str]]) -> str:
    kept = [(t, r) for t, r in rows if not _is_local_gap_reference(t, r)]
    if not kept:
        return "### References\n\n*(No external literature citations in this synthesis.)*\n"
    lines = ["### References\n"]
    for i, (topic, ref) in enumerate(kept, 1):
        lines.append(f"{i}. **{topic}.** {ref}")
    return "\n\n".join(lines) + "\n"


def _restructure_gap_references_and_conclusions(md: str) -> str:
    """
    Replace broken Sources tables with a numbered reference list; rename and order tail sections.

    **Conclusions** (from **Bottom line:**) comes first; **References** is last.
    """
    text = md.rstrip()
    conclusions_body = ""

    bottom_m = re.search(
        r"\n\*\*Bottom line:\*\*\s*(.*)\Z",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if bottom_m:
        text = text[: bottom_m.start()].rstrip()
        conclusions_body = bottom_m.group(1).strip()

    refs_section = ""
    sources_m = re.search(
        r"^#{3,4}\s+(?:\d+\.\s*)?(?:Sources|References)\s*\n(.*?)(?=\n#{3,4}\s+|\Z)",
        text,
        flags=re.DOTALL | re.MULTILINE | re.IGNORECASE,
    )
    if sources_m:
        body = sources_m.group(1).strip()
        if re.search(r"(?m)^\d+\.\s+\*\*", body):
            refs_section = "### References\n\n" + body + "\n"
        else:
            refs_section = _format_references_section(_extract_gap_reference_rows(body))
        text = text[: sources_m.start()].rstrip()

    if not conclusions_body:
        conc_m = re.search(
            r"^#{3,4}\s+(?:\d+\.\s*)?Conclusions\s*\n(.*)\Z",
            text,
            flags=re.DOTALL | re.MULTILINE | re.IGNORECASE,
        )
        if conc_m:
            conclusions_body = conc_m.group(1).strip()
            text = text[: conc_m.start()].rstrip()

    tail: list[str] = []
    if conclusions_body:
        tail.append(f"### Conclusions\n\n{conclusions_body}\n")
    if refs_section:
        tail.append(refs_section.strip())
    if not tail:
        return text
    return f"{text}\n\n" + "\n\n".join(tail)


def normalize_gap_markdown_for_report(md: str) -> str:
    """Normalize gap-agent markdown (headings, references list, conclusions title)."""
    text = _normalize_gap_conclusion_markdown(md)
    return _restructure_gap_references_and_conclusions(text)


def _normalize_gap_conclusion_markdown(md: str) -> str:
    """
    Fit ``UNOBTANIUM_GAP.md`` under report ``## Conclusion``.

    - Drop agent HTML comment and duplicate document ``#`` title
    - Remove ``## N.`` numbering; demote headings one level (``##`` → ``###``, ``###`` → ``####``)
    - Replace ``## 1. Executive summary`` with ``### Overall likelihood…`` lead heading
    """
    text = _GAP_HTML_COMMENT.sub("", md)
    text = _strip_leading_h1(text)
    out: list[str] = []
    after_exec_heading = False

    for line in text.splitlines():
        hm = _GAP_HEADING.match(line)
        if hm:
            level = len(hm.group(1))
            title = _GAP_NUMBERED_HEADING.sub("", hm.group(2).strip())
            if re.search(r"executive\s+summary", title, re.I):
                after_exec_heading = True
                continue
            new_level = min(level + 1, 4)
            out.append("#" * new_level + " " + title)
            after_exec_heading = False
            continue

        overall = _OVERALL_LIKELIHOOD.match(line.strip())
        if overall:
            out.append("### " + overall.group(1).strip())
            after_exec_heading = False
            continue

        if after_exec_heading and line.strip() and not line.startswith("|"):
            # Body lines before next heading stay as paragraphs under Overall likelihood.
            pass
        out.append(line)
        after_exec_heading = False

    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip()


def _prepare_gap_conclusion_body(raw: str) -> str:
    normalized = normalize_gap_markdown_for_report(raw)
    flattened = _flatten_markdown_bullets(normalized)
    return inline_publishable_markdown(flattened, cap_headings_at=None)


_TRAILING_REFERENCES_SECTION = re.compile(
    r"\n### References\s*\n(.*)\Z",
    flags=re.DOTALL | re.IGNORECASE,
)
_GAP_NUMBERED_REFERENCE = re.compile(
    r"^(\d+)\.\s+\*\*(.+?)\.\*\*\s+(.+)$",
    re.DOTALL,
)


def _split_trailing_references_section(md: str) -> tuple[str, str]:
    """Remove a trailing ``### References`` block (body for report-wide merge)."""
    m = _TRAILING_REFERENCES_SECTION.search(md.rstrip())
    if not m:
        return md.rstrip() + "\n\n", ""
    return md[: m.start()].rstrip() + "\n\n", m.group(1).strip()


def _parse_gap_reference_entries(refs_block: str) -> list[tuple[str, str]]:
    """Parse ``### References`` entries as ``(topic, citation)``."""
    if not refs_block.strip():
        return []
    entries: list[tuple[str, str]] = []
    for chunk in re.split(r"\n(?=\d+\.\s+\*\*)", refs_block.strip()):
        chunk = chunk.strip()
        if not chunk:
            continue
        m = _GAP_NUMBERED_REFERENCE.match(chunk)
        if m:
            cite = re.sub(r"\s+", " ", m.group(3).strip())
            entries.append((m.group(2).strip(), cite))
    return entries


def render_combined_references_section(
    brayton_refs: list[tuple[int, str]],
    gap_refs: list[tuple[str, str]],
) -> str:
    """Single numbered reference list at the end of the report."""
    if not brayton_refs and not gap_refs:
        return ""
    lines = ["## References\n\n"]
    n = 0
    for _num, cite in sorted(brayton_refs, key=lambda x: x[0]):
        n += 1
        lines.append(f"{n}. {cite}")
    for topic, cite in gap_refs:
        n += 1
        lines.append(f"{n}. **{topic}.** {cite}")
    return "\n\n".join(lines) + "\n\n"


def render_brayton_air_cycle_section() -> tuple[str, list[tuple[int, str]]]:
    body, refs = load_brayton_air_cycle_block()
    if not body:
        return "", []
    return f"## The air-breathing Brayton cycle\n\n{body}\n\n", refs


def render_introduction(result: ExperimentRunResult) -> str:
    target = _target_mw(result)
    lines = ["## Introduction\n\n"]
    if _is_in_silico_benchmark(result):
        intro = load_benchmark_introduction_block()
        if intro:
            lines.append(intro)
            lines.append("\n\n")
        else:
            lines.append(
                f"*Introduction unavailable; target plant **{target:g} MW**.*\n\n"
            )
    else:
        lines.append(
            "The Orbitron direct-cycle concept couples a **p-¹¹B** fusion core to an **air-breathing "
            "Brayton train** on a laboratory test stand. The question is whether a credible "
            f"**{target:g} MW** gross plant can close while respecting first-wall, field-emission, HTS, "
            "and reactivity limits.\n\n"
        )
    return "".join(lines)


def render_benchmark_methodology_section(result: ExperimentRunResult) -> str:
    if not _is_in_silico_benchmark(result):
        return ""
    body = load_benchmark_methodology_block()
    if not body:
        return ""
    return f"## Benchmark Methodology\n\n{body}\n\n"


def render_governing_equations_section() -> str:
    body = load_equations_ssot_block()
    if not body:
        return ""
    return (
        "## Governing equations\n\n"
        "State evolution for the forward model (stages 0–8). Each stage defines a state vector, "
        "initial condition, and discrete update.\n\n"
        f"{body}\n\n"
    )


def render_fidelity_section() -> str:
    body = load_fidelity_and_claims_block()
    if not body:
        return ""
    return f"## Fidelity tiers and what each stage proves\n\n{body}\n\n"


def render_benchmark_scenarios_section(result: ExperimentRunResult) -> str:
    fwd = result.step_results.get("forward")
    if not fwd:
        return ""
    return benchmark_scenarios_table_md(fwd)


def render_pb11_fusion_reaction_section() -> str:
    body = load_pb11_fusion_reaction_block()
    if not body:
        return "## Why p-¹¹B fusion?\n\n*(Fusion pathway sources unavailable.)*\n\n"
    return f"## Why p-¹¹B fusion?\n\n{body}\n"


def render_test_stand_section(
    staged: dict[str, str | None],
    *,
    report_dir: Path,
) -> str:
    lines = [
        "## The Phase-1 test stand\n\n",
        "Propulsion runs **−X → +X** from bellmouth intake to nozzle exit. Cryogenic **H₂** and **CH₄** "
        "services sit on the pad deck; the electrostatic core, laser ablation line, and Phase-2 Brayton "
        "hardware share one logical layout. Labels below (**LAB-01**, **CORE-01**, **AIR-01**, …) are "
        "engineering tags for cross-reference only.\n\n",
    ]
    lab = staged.get("LAB-01")
    if lab:
        lines.append(f"![LAB-01 — full test stand]({lab})\n\n")
    for asm in ASSEMBLY_WALKTHROUGH:
        if asm.designator == "LAB-01":
            continue
        rel = staged.get(asm.designator)
        lines.append(f"### {asm.designator} — {asm.title}\n\n")
        if rel:
            lines.append(f"![{asm.designator}]({rel})\n\n")
        lines.append(f"{asm.narrative}\n\n")
    return "".join(lines)


def render_physics_design_section(parameters: dict[str, Any]) -> str:
    lines = [
        "## Design point\n\n",
        "Operating point for this benchmark — geometry, fueling, unobtanium knobs, and plant targets.\n\n",
        physics_parameters_md(parameters),
    ]
    return "".join(lines)


def render_unobtanium_section(parameters: dict[str, Any]) -> str:
    unob = parameters.get("unobtanium") or {}
    lines = [
        "## Unobtanium design basis (U1–U4)\n\n",
        "Closing **3.5 MW** requires simultaneous progress on emission, wall cooling, bore field, and "
        "p-¹¹B reactivity — not independent tuning knobs.\n\n",
        "- **U1 — Cathode emission:** 600 kV-class without vacuum arc — "
        f"margin **{unob.get('field_emission_margin', 1.0)}×**\n",
        "- **U2 — First wall + CH₄ loop:** "
        f"**{unob.get('max_wall_heat_flux_W_m2', '—')} W/m²**, "
        f"cooling **{unob.get('ch4_cooling_effectiveness', 1.0)}×**\n",
        "- **U3 — HTS bore:** 2 T at cryogenic temperature — "
        f"scale **{unob.get('hts_capability_scale', 1.0)}×**\n",
        "- **U4 — p-¹¹B reactivity × beam coupling:** "
        f"reactivity **{unob.get('fusion_reactivity_scale', 1.0)}×**, "
        f"coupling **{unob.get('beam_coupling_scale', 1.0)}×**\n\n",
        "**(a) Pretend** uses the **design-calibrated** ⟨σv⟩ curve. **(b) Today** uses "
        "**literature-class** ⟨σv⟩ (~10³× lower peak at operating T) plus experimental "
        "anchors in `scenario_anchors.yaml`. **(c) Minimum** is the stress-inverse solve.\n\n",
    ]
    basis = load_unobtanium_basis_block()
    if basis:
        lines.append(basis)
        lines.append("\n\n")
    return "".join(lines)


def render_baseline_overview(result: ExperimentRunResult) -> str:
    target = _target_mw(result)
    lines = [
        "## Baseline at nominal Unobtanium\n\n",
        f"Nominal forward model at **design σv** and unity Unobtanium scales, targeting **{target:g} MW** "
        "gross to the Brayton path.\n\n",
        "| Stage | Outcome |\n|-------|--------|\n",
    ]
    titles = {
        0: "Layout",
        1: "Electron ring",
        2: "ρ_e normalization",
        3: "Fusion channel",
        4: "Fueling",
        5: "p-¹¹B burn",
        6: "0D plant + U1–U4",
        7: "Jet closure",
        8: "Validation",
    }
    for step_num in range(9):
        sid = f"{step_num:02d}"
        if sid not in result.step_results:
            continue
        lines.append(f"| {titles.get(step_num, sid)} | {step_metrics_row(sid, result.step_results[sid])} |\n")
    lines.append("\n")
    return "".join(lines)


def render_baseline_physics(
    result: ExperimentRunResult,
    report_dir: Path,
) -> str:
    lines: list[str] = []
    s05 = result.step_results.get("05") or {}
    s06 = result.step_results.get("06") or {}
    s07 = result.step_results.get("07") or {}
    s03 = result.step_results.get("03") or {}

    if "01" in result.step_results or "03" in result.step_results:
        lines.append("### Plasma channel and fusion fields\n\n")
        lines.append(
            "The electron ring sets the density scale that feeds the laminar fusion-channel model. "
            "With fueling armed, reaction-rate structure and clump metrics show how much power couples "
            "into the volume before the 0D burn step.\n\n"
        )
        lines.append(_embed_figure(report_dir, result.figures, "step01", "Electron density — final snapshot"))
        for key, cap in (
            ("step03_density", "Fuel density n(s,r)"),
            ("step03_reaction", "Reaction rate R(s,r)"),
            ("step03_clump", "Clump index vs time"),
        ):
            lines.append(_embed_figure(report_dir, result.figures, key, cap))
        if s03.get("integrated_fusion_power_mw") is not None:
            lines.append(
                f"Integrated channel power **{float(s03['integrated_fusion_power_mw']):.3f} MW**; "
                f"clump OFF/ON **{float(s03.get('clump_reduction_ratio', 0)):.2f}×**.\n\n"
            )

    if "05" in result.step_results or "06" in result.step_results:
        lines.append("### Burn power and plant closure\n\n")
        pf = s05.get("fusion_power_mw")
        if isinstance(pf, (int, float)):
            lines.append(f"p-¹¹B burn power **{float(pf):.3f} MW** against the gross target. ")
        ss = s06.get("steady_state") or {}
        pg = ss.get("gross_power_mw")
        if isinstance(pg, (int, float)):
            lines.append(f"0D plant gross **{float(pg):.3f} MW**, feasible **{s06.get('feasible')}**. ")
        lines.append("\n\n")
        lines.append(_embed_figure(report_dir, result.figures, "step05", "Fusion power vs target"))
        lines.append(_embed_figure(report_dir, result.figures, "step06_outputs", "Plant outputs"))
        lines.append(_embed_figure(report_dir, result.figures, "step06_u", "U1–U4 stress ratios"))

    if "07" in result.step_results:
        lines.append("### Thrust path\n\n")
        err = s07.get("closure_rel_error")
        if isinstance(err, (int, float)):
            lines.append(f"Jet closure relative error **{100 * float(err):.2f}%**. ")
        thrust = s07.get("thrust_lbf")
        if isinstance(thrust, (int, float)):
            lines.append(f"Booked thrust **{float(thrust):.1f} lbf** on the thrust sled.\n\n")
        lines.append(_embed_figure(report_dir, result.figures, "step07", "Jet power closure"))

    return "".join(lines)


def render_inverse_section(result: ExperimentRunResult, report_dir: Path) -> str:
    if "09" not in result.step_results:
        return ""
    s09 = result.step_results["09"]
    target = _target_mw(result)
    lines = [
        "## Honest gap to 3.5 MW (constrained stress inverse)\n\n",
        f"Under **literature-class** ⟨σv⟩ we minimize **η_react** (and other knobs) with a "
        "**trust-region constrained** solve: power ≥ **{target:g} MW** and **U1–U4** are hard "
        "inequalities. If no feasible point exists, scenario **(c)** is **infeasible** — not a "
        "violation-bearing “solution.”\n\n",
    ]
    stress = s09.get("stress_inverse") or {}
    branch = stress.get("sigma_v_design_over_literature")
    eta_req = stress.get("fusion_reactivity_scale_required")
    eff = stress.get("effective_reactivity_gap_vs_nominal")
    if branch is not None:
        lines.append(
            f"Primary reactivity gap at solve: ⟨σv⟩ design/literature ≈ **{float(branch):.1f}×**; "
        )
        if eta_req is not None:
            lines.append(f"`fusion_reactivity_scale` required ≈ **{float(eta_req):.1f}×**; ")
        if eff is not None:
            lines.append(f"combined ≈ **{float(eff):.1f}×** vs nominal scale.\n\n")
        else:
            lines.append("\n\n")
    if not stress.get("success", s09.get("success")):
        lines.append(
            "**Constrained stress inverse: INFEASIBLE** — no literature-σv point meets "
            f"**{target:g} MW** and **U1–U4** together. The ⟨σv⟩ branch gap (~10³×) cannot be "
            "closed with the allowed knob bounds while satisfying cathode, wall, and magnet gates. "
            "Scenario **(c)** in the table above is marked infeasible; do not treat optimizer "
            "knobs as a operating solution.\n\n"
        )
    factors = s09.get("gap_factors") or {}
    if factors and stress.get("success", s09.get("success")):
        lines.append(
            "Material knob ratios at the constrained minimum (required/nominal):\n\n"
        )
        lines.append(gap_factors_table_md(factors))
        lines.append("\n")
    elif factors:
        lines.append(
            "*Optimizer best-effort knobs (gates not satisfied — illustrative only):*\n\n"
        )
        lines.append(gap_factors_table_md(factors))
        lines.append("\n")
    conf = s09.get("forward_confirmation_passes")
    conf_mw = s09.get("forward_confirmation_mw")
    if conf is not None:
        lines.append(
            f"Forward check at **design σv** with solved knobs: "
            f"{'PASS' if conf else 'FAIL'}"
        )
        if conf_mw is not None:
            lines.append(f" (**{float(conf_mw):.3f} MW**)")
        lines.append(
            ". Uses **margin-inverse** knobs on design σv (back-solve ≈ pretend), "
            "not stress-inverse η_react ~10³× on literature σv.\n\n"
        )
    lines.append(_embed_figure(report_dir, result.figures, "step09_unobtanium_compare", "Gap factors vs nominal"))
    return "".join(lines)


INVERSE_COMPARE_FIGURES: list[tuple[str, str]] = [
    ("inverse_summary_compare", "Headline metrics — baseline vs gap-closed"),
    ("step05_burn_compare", "Burn power — baseline vs gap-closed"),
    ("step06_plant_compare", "Plant — baseline vs gap-closed"),
    ("step07_closure_compare", "Jet closure — baseline vs gap-closed"),
]

STEP03_GAP_FIGURES: list[tuple[str, str]] = [
    ("step03_gap_density", "Gap-closed fuel density"),
    ("step03_gap_reaction", "Gap-closed reaction rate"),
]


def render_gap_closed_performance(
    result: ExperimentRunResult,
    report_dir: Path,
) -> str:
    gap_ids = [k for k in result.step_results if k.endswith("_gap")]
    if not gap_ids:
        return ""

    lines = [
        "## Performance at gap-closed Unobtanium\n\n",
        "Re-running the fusion channel and plant with **inverse-solved** Unobtanium knobs "
        "(design σv, literature stress basis). Compare to baseline panels below.\n\n",
    ]
    for fig_key, caption in INVERSE_COMPARE_FIGURES:
        lines.append(_embed_figure(report_dir, result.figures, fig_key, caption))
    for fig_key, caption in STEP03_GAP_FIGURES:
        lines.append(_embed_figure(report_dir, result.figures, fig_key, caption))

    d3g = result.step_results.get("03_gap") or {}
    s06g = result.step_results.get("06_gap") or {}
    s08g = result.step_results.get("08_gap") or {}
    if d3g.get("integrated_fusion_power_mw") is not None:
        lines.append(
            f"Gap-closed channel power **{float(d3g['integrated_fusion_power_mw']):.3f} MW**. "
        )
    ss = s06g.get("steady_state") or {}
    if isinstance(ss.get("gross_power_mw"), (int, float)):
        lines.append(f"Gap-closed gross **{float(ss['gross_power_mw']):.3f} MW**. ")
    if s08g.get("design_validated") is not None:
        lines.append(
            f"First-tier gates at gap-closed knobs: **{'yes' if s08g.get('design_validated') else 'no'}**.\n\n"
        )
    else:
        lines.append("\n\n")
    return "".join(lines)


def render_conclusion_gap(
    result: ExperimentRunResult,
    report_dir: Path,
) -> tuple[str, list[tuple[str, str]]]:
    if "09" not in result.step_results:
        return "", []
    gap_md = report_dir / "UNOBTANIUM_GAP.md"
    lines = [
        "## Conclusion — technology gaps and R&D program\n\n",
    ]
    gap_refs: list[tuple[str, str]] = []
    if gap_md.is_file():
        body = _prepare_gap_conclusion_body(gap_md.read_text(encoding="utf-8"))
        body, refs_block = _split_trailing_references_section(body)
        gap_refs = _parse_gap_reference_entries(refs_block)
        lines.append(body)
        lines.append("\n")
    else:
        lines.append("*Gap synthesis unavailable for this run.*\n\n")
    return "".join(lines), gap_refs
