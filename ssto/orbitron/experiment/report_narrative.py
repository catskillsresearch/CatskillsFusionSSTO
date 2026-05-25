"""LinkedIn-ready narrative sections for experiment REPORT.md (physics audience)."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ssto.orbitron.experiment.assembly_narrative import ASSEMBLY_WALKTHROUGH
from ssto.orbitron.experiment.narrative import (
    inline_publishable_markdown,
    load_equations_ssot_block,
    load_fidelity_and_claims_block,
    load_pb11_fusion_reaction_block,
    load_unobtanium_basis_block,
)
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


BENCHMARK_INTRODUCTION = (
    "This report is inspired by a fusion device called the Orbitron developed by Avalanche Energy. "
    "It explores the idea of a jet engine powered directly by a proton-boron (p-¹¹B) "
    "Orbitron-style fusion reactor, designed to produce about 3.5 megawatts (MW) of total raw power.\n\n"
    "To test whether this idea is actually possible, we ran a series of computer simulations:\n\n"
    "1. **The Ideal Test:** First, we ran a standard simulation using the project's target fusion "
    "reaction rates, assuming we have perfect, ideal materials and conditions (which we refer to "
    'as "Unobtanium" levels U1 through U4).\n'
    "2. **The Stress Test:** Next, we ran a more conservative simulation using the standard reaction "
    "rates found in existing scientific papers. This helped us find the absolute minimum performance "
    "we would need to make the system work.\n"
    "3. **The Technology Review:** Finally, we used AI-assisted research (using a Cursor AI agent) "
    "to map out exactly what technological progress is needed to turn those ideal materials into a "
    "reality.\n\n"
    "For the physical shape of the engine we used CadQuery and Blender. "
    "To simulate how the electrons behave inside the engine we used WarpX "
    "Particle-In-Cell (PIC) simulation. The Blender output serves outside of this "
    "benchmark as a physical model input to FlightGear.\n\n"
    "In practice, this setup connects the proton-boron fusion reactor directly to a jet-engine-style "
    "turbine (an air-breathing Brayton cycle) on a laboratory test stand. The main question we wanted "
    "to answer is: can a **3.5 MW** power plant actually work while staying within safe physical limits? "
    "Specifically, we looked at the limits of the reactor's inner walls, electrical sparking/leakage, "
    "high-temperature superconducting (HTS) magnets, and reaction speeds. If today's technology isn't "
    "quite there yet, we wanted to find out exactly what needs to improve.\n\n"
    "This report is entirely self-contained, meaning we have included all the necessary math "
    "equations, material specifications, numerical results, and technology gap analyses below.\n\n"
)


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


def render_introduction(result: ExperimentRunResult) -> str:
    target = _target_mw(result)
    lines = ["## Introduction\n\n"]
    if _is_in_silico_benchmark(result):
        lines.append(BENCHMARK_INTRODUCTION)
        s08 = result.step_results.get("08") or {}
        if s08.get("design_validated") is True:
            lines.append(
                "Under ideal material conditions, the simulated power plant successfully works at "
                f"**{target:g} MW** and meets all of our primary design and safety limits. "
                "Reverse-solving under more realistic assumptions for the parameters of the "
                "Unobtanium components, we find that similar performance is possible. "
                "AI-driven analysis tells us what the critical gaps are on the Unobtanium and "
                "gives us a roadmap for further materials science R&D.\n\n"
            )
        elif "08" in result.step_results:
            lines.append(
                "Under ideal material assumptions the nominal forward model **closes** the power target "
                f"at **{target:g} MW**, but the conservative stress test and technology review sections "
                "below show where literature-class reactivity and today's art still fall short.\n\n"
            )
        else:
            lines.append(
                "Under ideal material conditions, the simulated power plant successfully works at "
                f"**{target:g} MW** and meets all of our primary design and safety limits. "
                "Reverse-solving under more realistic assumptions for the parameters of the "
                "Unobtanium components, we find that similar performance is possible. "
                "AI-driven analysis tells us what the critical gaps are on the Unobtanium and "
                "gives us a roadmap for further materials science R&D.\n\n"
            )
    else:
        lines.append(
            "The Orbitron direct-cycle concept couples a **p-¹¹B** fusion core to an **air-breathing "
            "Brayton train** on a laboratory test stand. The question is whether a credible "
            f"**{target:g} MW** gross plant can close while respecting first-wall, field-emission, HTS, "
            "and reactivity limits.\n\n"
        )
    return "".join(lines)


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
        "| Gate | Physical meaning | Nominal (this run) |\n",
        "|------|------------------|--------------------|\n",
        "| **U1** | 600 kV-class cathode emission without vacuum arc | "
        f"margin **{unob.get('field_emission_margin', 1.0)}×** |\n",
        "| **U2** | First-wall heat flux + CH₄ loop | "
        f"**{unob.get('max_wall_heat_flux_W_m2', '—')} W/m²**, "
        f"cooling **{unob.get('ch4_cooling_effectiveness', 1.0)}×** |\n",
        "| **U3** | 2 T HTS bore at cryogenic temperature | "
        f"scale **{unob.get('hts_capability_scale', 1.0)}×** |\n",
        "| **U4** | p-¹¹B ⟨σv⟩ × beam coupling | "
        f"reactivity **{unob.get('fusion_reactivity_scale', 1.0)}×**, "
        f"coupling **{unob.get('beam_coupling_scale', 1.0)}×** |\n\n",
        "**Baseline** uses the **design-calibrated** ⟨σv⟩ curve. **Stress inverse** uses "
        "**literature-class** ⟨σv⟩ (~3× lower peak) for honest gap factors.\n\n",
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
        "## Honest gap to 3.5 MW (stress inverse)\n\n",
        f"Under **literature-class** p-¹¹B reactivity we invert unobtanium knobs to find the minimum "
        f"multipliers that reach **{target:g} MW** while satisfying U1–U4. Gap factors ≫ 1× are the "
        "R&D stretch relative to nominal art.\n\n",
    ]
    factors = s09.get("gap_factors") or {}
    if factors:
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
            ". This confirms internal consistency — not that literature σv already hits target.\n\n"
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


def render_conclusion_gap(result: ExperimentRunResult, report_dir: Path) -> str:
    if "09" not in result.step_results:
        return ""
    gap_md = report_dir / "UNOBTANIUM_GAP.md"
    lines = [
        "## Conclusion — technology gaps and R&D program\n\n",
    ]
    if gap_md.is_file():
        body = _prepare_gap_conclusion_body(gap_md.read_text(encoding="utf-8"))
        lines.append(body)
        lines.append("\n")
    else:
        lines.append("*Gap synthesis unavailable for this run.*\n\n")
    return "".join(lines)
