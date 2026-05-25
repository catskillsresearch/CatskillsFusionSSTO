"""LinkedIn-ready narrative sections for experiment REPORT.md (physics audience)."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ssto.orbitron.experiment.assembly_narrative import ASSEMBLY_WALKTHROUGH
from ssto.orbitron.experiment.narrative import md_math_for_preview
from ssto.orbitron.experiment.report_formatting import (
    gap_factors_table_md,
    physics_parameters_md,
    step_metrics_row,
)
from ssto.orbitron.experiment.runner import ExperimentRunResult

_REPO = Path(__file__).resolve().parents[3]
_UNOBTANIUM_MD = _REPO / "ssto" / "orbitron" / "UNOBTANIUM.md"

_OPS_LINE_RE = re.compile(
    r"(pip install|poetry run|\./scripts/|make orbitron|chain_config|build/orbitron|"
    r"run\.skip_pic|--no-gap-agent|results/step_|parameters\.json|experiment\.yaml)",
    re.I,
)


def _target_mw(result: ExperimentRunResult) -> float:
    scales = result.parameters.get("plant_scales") or {}
    return float(scales.get("target_gross_power_mw", 3.5))


def _is_in_silico_benchmark(result: ExperimentRunResult) -> bool:
    return "in silico benchmark" in result.experiment.experiment_name.lower()


BENCHMARK_INSPIRATION_INTRO = (
    "This report is inspired by the Avalanche Energy Orbitron and imagines an Orbitron "
    "direct cycle p-11B fuel 3.5MW power output turbojet engine.  We do a benchmark software "
    "simulation assuming nominal performance for some Unobtanium materials and then do an "
    "inverse solve to find the optimal levels of performance for the Unobtanium assuming some "
    "realistic constraints to work towards the same performance levels.  Finally, we use Cursor "
    "AI to assess the R&D requirements to develop the Unobtanium components to those levels. "
    "Cursor and some @Google AI was used to develop the benchmark software, which also depends "
    "on CadQuery, Blender and WarpX. The results also carry over to a FlightGear implementation "
    "of the engine testbed."
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


def _sanitize_gap_markdown(md: str) -> str:
    """Strip code, ops notes, and deep headings for a public physics narrative."""
    md = re.sub(r"```[\s\S]*?```", "", md)
    md = re.sub(r"^#{4,}\s+", "### ", md, flags=re.MULTILINE)
    flat: list[str] = []
    for line in md.splitlines():
        if _OPS_LINE_RE.search(line):
            continue
        m = re.match(r"^(\s{2,})[-*]\s+(.*)$", line)
        if m:
            flat.append(f"- {m.group(2).strip()}")
            continue
        flat.append(line)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(flat)).strip()


def _strip_leading_h1(md: str) -> str:
    lines = md.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines and lines[0].startswith("# "):
        lines.pop(0)
        while lines and not lines[0].strip():
            lines.pop(0)
    return "\n".join(lines)


def render_introduction(result: ExperimentRunResult) -> str:
    target = _target_mw(result)
    lines = ["## Introduction\n\n"]
    if _is_in_silico_benchmark(result):
        lines.append(f"{BENCHMARK_INSPIRATION_INTRO}\n\n")
    lines.append(
        "The Orbitron direct-cycle concept couples a **p-¹¹B** fusion core to an **air-breathing Brayton "
        "train** on a laboratory test stand. The question for this benchmark is whether a credible "
        f"**{target:g} MW** gross plant can close while respecting first-wall, field-emission, HTS, and "
        "reactivity **Unobtanium** gates — and, if not at today's art, what performance must improve.\n\n"
        "We walk from the **physical hardware layout** through **nominal** performance, then an "
        "**honest stress inverse** under literature-class fusion reactivity, and finish with a "
        "**technology gap** and R&D program. Figures are placeholders for manual illustration upload "
        "in the published article.\n\n"
    )
    s08 = result.step_results.get("08") or {}
    if s08.get("design_validated") is True:
        lines.append(
            f"At **nominal** unobtanium knobs the plant model **closes {target:g} MW** with Tier-1 "
            "validation satisfied.\n\n"
        )
    elif "08" in result.step_results:
        lines.append(
            "At nominal knobs the plant model **does not fully close** the power and materials gates — "
            "see baseline and inverse sections.\n\n"
        )
    return "".join(lines)


def render_test_stand_section(staged: dict[str, str | None]) -> str:
    lines = [
        "## The Phase-1 test stand\n\n",
        "Propulsion runs **−X → +X** from bellmouth intake to nozzle exit. Cryogenic **H₂** and **CH₄** "
        "services sit on the pad deck; the electrostatic core, laser ablation line, and Phase-2 Brayton "
        "hardware share one logical layout. Labels below (**LAB-01**, **CORE-01**, **AIR-01**, …) are "
        "engineering tags for cross-reference only.\n\n",
    ]
    lab = staged.get("LAB-01")
    if lab:
        lines.append(_embed_figure(Path(), {"x": lab}, "x", "Full laboratory test stand"))
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
        "## Unobtanium gates (U1–U4)\n\n",
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
        "**Baseline** sections use the **design-calibrated** reactivity curve. **Inverse** stress "
        "uses **literature-class** ⟨σv⟩ (~3× lower peak) to report honest gap factors.\n\n",
    ]
    if _UNOBTANIUM_MD.is_file():
        text = _UNOBTANIUM_MD.read_text(encoding="utf-8")
        if "Energy offload:" in text:
            lines.append(
                "Design intent: fusion-heated Brayton on ingested air — sprint power without a "
                "multi‑MV grid tie. The benchmark asks whether this geometry and fueling can deliver "
                "**3.5 MW** while passing U1–U4.\n\n"
            )
    return "".join(lines)


def render_baseline_overview(result: ExperimentRunResult) -> str:
    target = _target_mw(result)
    lines = [
        "## Baseline at nominal Unobtanium\n\n",
        f"Proof-forward chain at **design σv** and unity unobtanium scales, targeting **{target:g} MW** "
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
        "Re-running the fusion channel and plant steps with **inverse-solved** knobs (design σv, proof mode off). "
        "Compare to baseline panels below.\n\n",
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
            f"Tier-1 at gap-closed knobs: **{'yes' if s08g.get('design_validated') else 'no'}**.\n\n"
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
        body = _sanitize_gap_markdown(_strip_leading_h1(gap_md.read_text(encoding="utf-8")))
        lines.append(md_math_for_preview(body))
        lines.append("\n")
    else:
        lines.append("*Gap synthesis unavailable for this run.*\n\n")
    return "".join(lines)
