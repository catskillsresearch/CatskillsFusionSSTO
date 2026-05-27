"""Human-readable Markdown tables and lists for experiment reports (no raw JSON/YAML)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from ssto.orbitron.experiment.assembly_narrative import PHYSICS_DESIGNATORS

_SKIP_TOP_KEYS = frozenset({"step", "generated_utc"})
_PATH_SUFFIXES = ("_npz", "_yaml", "_json", "_path", "_dir")


def _fmt_scalar(v: Any) -> str:
    if v is None:
        return "—"
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, int) and not isinstance(v, bool):
        return str(v)
    if isinstance(v, float):
        av = abs(v)
        if av >= 1e4 or (0 < av < 1e-2):
            return f"{v:.4g}"
        return f"{v:.6g}".rstrip("0").rstrip(".")
    if isinstance(v, str) and len(v) > 72 and ("/" in v or "\\" in v):
        return f"`{Path(v).name}`"
    return str(v)


def _kv_table(rows: list[tuple[str, str]], *, headers: tuple[str, str] = ("Setting", "Value")) -> str:
    if not rows:
        return ""
    lines = [
        f"| {headers[0]} | {headers[1]} |",
        f"|{'-' * len(headers[0])}|{'-' * len(headers[1])}|",
    ]
    for k, v in rows:
        lines.append(f"| {k} | {v} |")
    return "\n".join(lines) + "\n"


def _spec_checks_table(checks: list[dict[str, Any]]) -> str:
    if not checks:
        return ""
    lines = [
        "| Spec | Status | Required | Achieved |",
        "|------|--------|----------|----------|",
    ]
    for c in checks:
        sid = c.get("spec_id", "—")
        title = (c.get("title") or "").strip()
        label = f"**{sid}**" + (f" — {title}" if title else "")
        lines.append(
            f"| {label} | {c.get('status', '—')} | {c.get('required', '—')} | {c.get('achieved', '—')} |"
        )
    return "\n".join(lines) + "\n"


def step_metrics_row(step_id: str, data: dict[str, Any]) -> str:
    if data.get("error"):
        return f"error: {data['error']}"
    if step_id == "02":
        return f"ρ_e_norm={data.get('rho_e_norm', '—')}"
    if step_id == "03":
        ci = data.get("clump_index_final")
        ratio = data.get("clump_reduction_ratio")
        ci_s = f"{float(ci):.2f}" if ci is not None else "—"
        ratio_s = f"{float(ratio):.2f}×" if ratio is not None else "—"
        return f"clump_ON={ci_s}, OFF/ON={ratio_s}, armed={data.get('reactor_armed')}"
    if step_id in ("05", "05_gap"):
        p = data.get("fusion_power_mw", "—")
        return f"P_fusion={p:.3g} MW" if isinstance(p, (int, float)) else f"P_fusion={p}"
    if step_id in ("06", "06_gap"):
        s = data.get("steady_state") or {}
        pg = s.get("gross_power_mw", "—")
        return (
            f"P_gross={pg:.3g} MW, feasible={data.get('feasible')}"
            if isinstance(pg, (int, float))
            else f"P_gross={pg}, feasible={data.get('feasible')}"
        )
    if step_id in ("07", "07_gap"):
        return f"closure={data.get('closure_rel_error', 0):.2%}"
    if step_id in ("08", "08_gap"):
        dv = data.get("design_validated")
        return f"design closure={'yes' if dv else 'no'}" if dv is not None else "design closure=—"
    if step_id == "09":
        u = data.get("unobtanium_required") or {}
        fs = u.get("fusion_reactivity_scale", "—")
        conf = data.get("forward_confirmation_passes")
        if isinstance(fs, (int, float)):
            return f"success={data.get('success')}, η_react={fs:.3g}×, CNF={conf}"
        return f"success={data.get('success')}, CNF={conf}"
    if step_id == "physics":
        return (
            f"physics_evidence={data.get('physics_evidence')}, "
            f"lit_fwd={data.get('literature_forward_mw', '—')} MW"
        )
    if step_id == "forward":
        parts = []
        for row in data.get("scenarios") or []:
            sid = row.get("id", "?")
            pg = row.get("gross_power_mw", "—")
            if isinstance(pg, (int, float)):
                parts.append(f"{sid}={pg:.3g}MW")
        return ", ".join(parts) if parts else "see table"
    if step_id == "01" and data.get("skipped"):
        return "SKIP_PIC"
    return "OK"


def gap_factors_table_md(gap: dict[str, float]) -> str:
    if not gap:
        return ""
    rows = [(k.replace("_", " "), f"**{float(v):.3f}×**") for k, v in sorted(gap.items())]
    return _kv_table(rows, headers=("Knob", "Required / nominal"))


def _steady_state_table(steady: dict[str, Any]) -> str:
    if not steady:
        return ""
    order = [
        ("gross_power_mw", "Gross power", "MW"),
        ("fusion_power_mw_physics", "Fusion (physics)", "MW"),
        ("fusion_power_mw_surrogate", "Fusion (surrogate)", "MW"),
        ("wall_heat_kw", "First-wall load", "kW"),
        ("ch4_wall_intercept_kw", "CH₄ wall intercept", "kW"),
        ("air_annulus_kw", "Air annulus (Brayton)", "kW"),
        ("brayton_thermal_kw", "Brayton thermal total", "kW"),
        ("hts_cryo_kw", "HTS cryostat load", "kW"),
        ("cryostat_radiation_budget_kw", "Cryostat radiative budget", "kW"),
        ("reactor_outer_diameter_m", "Reactor OD (zoned)", "m"),
        ("beam_current_ma", "Beam current", "mA"),
        ("beam_power_kw", "Beam power", "kW"),
        ("thrust_lbf", "Thrust", "lbf"),
        ("mass_flow_kgps", "Mass flow", "kg/s"),
        ("jet_kinetic_power_mw", "Jet kinetic power", "MW"),
        ("cathode_surface_field_V_m", "Cathode |E|", "V/m"),
        ("wall_heat_flux_W_m2", "Wall heat flux", "W/m²"),
        ("plasma_density_cm3", "Plasma density", "cm⁻³"),
        ("ion_temperature_kev", "Ion temperature", "keV"),
        ("sigma_v_m3_s", "⟨σv⟩", "m³/s"),
        ("feasible", "Plant feasible", ""),
    ]
    rows: list[tuple[str, str]] = []
    for key, label, unit in order:
        if key not in steady:
            continue
        val = _fmt_scalar(steady[key])
        if unit and key != "feasible":
            val = f"{val} {unit}"
        rows.append((label, val))
    for key, val in steady.items():
        if key in {x[0] for x in order} or key in ("violations", "log10_density"):
            continue
        if isinstance(val, (dict, list)):
            continue
        rows.append((key.replace("_", " "), _fmt_scalar(val)))
    return _kv_table(rows)


def _bool_list(items: list[str], *, prefix: str = "- ") -> str:
    if not items:
        return f"{prefix}*(none)*\n"
    return "".join(f"{prefix}{x}\n" for x in items)


def physics_parameters_md(parameters: dict[str, Any]) -> str:
    """Physics-facing design point only (no pad interlocks, PIC, or file paths)."""
    sections: list[tuple[str, dict[str, Any] | None]] = [
        ("Geometry & fields", parameters.get("geometry")),
        ("Fueling", parameters.get("injectants")),
        ("Unobtanium knobs", parameters.get("unobtanium")),
        ("Plant targets", parameters.get("plant_scales")),
    ]
    lines: list[str] = []
    for title, block in sections:
        if not block or not isinstance(block, dict):
            continue
        rows = [(k.replace("_", " "), _fmt_scalar(v)) for k, v in block.items()]
        lines.append(f"**{title}** — ")
        lines.append(
            "; ".join(f"{k}: {v}" for k, v in rows[:8])
            + ("; …" if len(rows) > 8 else "")
            + ".\n\n"
        )
    return "".join(lines) if lines else ""


def parameters_tables_md(parameters: dict[str, Any]) -> str:
    """All experiment parameters as sectioned tables with designator links."""
    sections: list[tuple[str, str, dict[str, Any] | None]] = [
        ("Geometry", "geometry", parameters.get("geometry")),
        ("Injectants", "injectants", parameters.get("injectants")),
        ("Pad interlocks & controls", "pad", parameters.get("pad")),
        ("PIC (WarpX)", "pic", parameters.get("pic")),
        ("Fusion channel grid", "fusion_channel", parameters.get("fusion_channel")),
        ("Unobtanium knobs", "unobtanium", parameters.get("unobtanium")),
        ("Plant scales", "plant_scales", parameters.get("plant_scales")),
    ]
    lines: list[str] = []
    for title, prefix, block in sections:
        if not block or not isinstance(block, dict):
            continue
        lines.append(f"### {title}\n\n")
        rows: list[tuple[str, str]] = []
        for key, val in block.items():
            path = f"{prefix}.{key}"
            tag = PHYSICS_DESIGNATORS.get(path)
            name = key.replace("_", " ")
            if tag:
                name = f"{name} ({tag[0]})"
            rows.append((name, _fmt_scalar(val)))
        lines.append(_kv_table(rows))
        lines.append("\n")
    lines.append(
        "*Machine-readable snapshot: `parameters.json` in the report directory.*\n\n"
    )
    return "".join(lines)


def step_results_md(step_id: str, data: dict[str, Any]) -> str:
    """Format a step result dict for REPORT.md (no JSON fences)."""
    if data.get("error"):
        return f"**Error:** {data['error']}\n\n"

    sid = step_id.replace("_gap", "")
    lines: list[str] = []

    if sid == "00":
        lines.append(_kv_table(
            [
                ("Layout focus", _fmt_scalar(data.get("focus") or data.get("layout"))),
                ("Output", _fmt_scalar(data.get("layout_png") or data.get("output"))),
            ]
        ))

    elif sid == "01":
        if data.get("skipped"):
            lines.append("- **PIC:** skipped (`run.skip_pic`)\n")
        else:
            lines.extend(
                [
                    _kv_table(
                        [
                            ("WarpX steps", _fmt_scalar(data.get("steps"))),
                            ("Grid cells", _fmt_scalar(data.get("grid_cells"))),
                            ("Final plotfile", _fmt_scalar(data.get("final_plotfile"))),
                        ]
                    ),
                ]
            )

    elif sid == "02":
        if data.get("skipped"):
            lines.append(
                "- **PIC skipped** — no WarpX plotfiles; **ρ_e_norm = 1.0** is a unity placeholder "
                "(not measured from the electron ring). Turn off `run.skip_pic` for a real norm.\n"
            )
        lines.append(
            _kv_table(
                [
                    ("ρ_e_norm", _fmt_scalar(data.get("rho_e_norm"))),
                    ("Target band (when PIC runs)", "0.2 – 3.0"),
                ]
            )
        )

    elif sid == "03":
        lines.append(
            _kv_table(
                [
                    ("Integrated fusion power", f"{_fmt_scalar(data.get('integrated_fusion_power_mw'))} MW"),
                    ("Clump index (ON, final)", _fmt_scalar(data.get("clump_index_final"))),
                    ("Clump index (OFF)", _fmt_scalar(data.get("clump_index_off"))),
                    ("OFF / ON ratio", f"{_fmt_scalar(data.get('clump_reduction_ratio'))}×"),
                    ("Reactor armed", _fmt_scalar(data.get("reactor_armed"))),
                    ("Compare pair cached", _fmt_scalar(data.get("compare_pair_cached"))),
                ]
            )
        )
        if data.get("fields_laminar_off_npz"):
            lines.append("\n**Field archives** (see `results/step_03.json` paths on disk):\n")
            lines.append(_bool_list(
                [
                    f"OFF: `{Path(str(data['fields_laminar_off_npz'])).name}`",
                    f"ON: `{Path(str(data['fields_laminar_on_npz'])).name}`",
                ]
            ))

    elif sid == "04":
        lines.append(
            _kv_table(
                [
                    (k.replace("_", " "), _fmt_scalar(v))
                    for k, v in data.items()
                    if k not in _SKIP_TOP_KEYS
                    and not any(str(k).endswith(s) for s in _PATH_SUFFIXES)
                    and isinstance(v, (int, float, str, bool))
                ]
            )
        )

    elif sid == "05":
        lines.append(
            _kv_table(
                [
                    ("Fusion power", f"{_fmt_scalar(data.get('fusion_power_mw'))} MW"),
                    ("Target gross", f"{_fmt_scalar(data.get('target_gross_power_mw'))} MW"),
                    ("Shortfall", f"{_fmt_scalar(data.get('shortfall_mw'))} MW"),
                    ("Volume reaction rate", f"{_fmt_scalar(data.get('reaction_rate_m3_s'))} m³/s"),
                ]
            )
        )

    elif sid == "06":
        if "steady_state" in data:
            lines.append("**Steady-state plant**\n\n")
            lines.append(_steady_state_table(data["steady_state"]))
        lines.append(
            _kv_table(
                [
                    ("Feasible", _fmt_scalar(data.get("feasible"))),
                    ("Clump index", _fmt_scalar(data.get("clump_index"))),
                    ("Clump OFF/ON ratio", f"{_fmt_scalar(data.get('clump_reduction_ratio'))}×"),
                ]
            )
        )
        viol = data.get("violations") or (data.get("steady_state") or {}).get("violations")
        if viol:
            lines.append("\n**Violations**\n\n")
            lines.append(_bool_list([str(v) for v in viol]))

    elif sid == "07":
        lines.append(
            _kv_table(
                [
                    ("Relative closure error", f"{100 * float(data.get('closure_rel_error', 0)):.2f}%"),
                    ("Jet kinetic power", f"{_fmt_scalar(data.get('jet_kinetic_power_mw'))} MW"),
                    ("Gross power", f"{_fmt_scalar(data.get('gross_power_mw'))} MW"),
                    ("Thrust", f"{_fmt_scalar(data.get('thrust_lbf'))} lbf"),
                ]
            )
        )

    elif sid == "08":
        lines.append(
            _kv_table(
                [
                    ("Design validated", _fmt_scalar(data.get("design_validated"))),
                    ("Summary", _fmt_scalar(data.get("summary"))),
                ]
            )
        )
        if data.get("spec_checks"):
            lines.append("\n**Specification checks**\n\n")
            lines.append(_spec_checks_table(data["spec_checks"]))

    elif sid == "09":
        lines.append(
            _kv_table(
                [
                    ("Solve success", _fmt_scalar(data.get("success"))),
                    ("Mode", _fmt_scalar(data.get("inverse_mode"))),
                    ("Target MW", _fmt_scalar(data.get("target_mw"))),
                    ("Residual MW", _fmt_scalar(data.get("residual_mw"))),
                    ("Forward confirmation", _fmt_scalar(data.get("forward_confirmation_passes"))),
                    ("Message", _fmt_scalar(data.get("message"))),
                ]
            )
        )
        if data.get("gap_factors"):
            lines.append("\n**Stress inverse — gap factors (honest goals)**\n\n")
            lines.append(gap_factors_table_md(data["gap_factors"]))
        margin = (data.get("margin_inverse") or {}).get("gap_factors")
        if margin:
            lines.append("\n**Margin audit gap factors (design σv)**\n\n")
            lines.append(gap_factors_table_md(margin))
        if data.get("pad_solved"):
            lines.append("\n**Pad knobs solved**\n\n")
            lines.append(
                _kv_table([(k.replace("_", " "), _fmt_scalar(v)) for k, v in data["pad_solved"].items()])
            )
        if data.get("steady_state"):
            lines.append("\n**Plant @ solved knobs**\n\n")
            lines.append(_steady_state_table(data["steady_state"]))
        if data.get("spec_checks"):
            lines.append("\n**Specification checks @ solved knobs**\n\n")
            lines.append(_spec_checks_table(data["spec_checks"]))

    elif sid == "physics":
        lines.append(
            _kv_table(
                [
                    ("Physics evidence", _fmt_scalar(data.get("physics_evidence"))),
                    ("Summary", _fmt_scalar(data.get("summary"))),
                    ("Literature forward MW", _fmt_scalar(data.get("literature_forward_mw"))),
                    ("Confirmation MW", _fmt_scalar(data.get("confirmation_design_mw"))),
                    ("Confirmation passes", _fmt_scalar(data.get("confirmation_passes"))),
                ]
            )
        )

    elif sid == "forward":
        lines.append(
            "*See **Forward performance** section for the scenario table.*\n\n"
        )

    else:
        lines.append(_generic_step_summary(data))

    if step_id.endswith("_gap"):
        lines.insert(0, "*Gap-closed run (inverse-solved unobtanium knobs applied).*\n\n")

    artifact = f"`results/step_{step_id}.json`"
    lines.append(f"\n*Full payload on disk: {artifact}*\n\n")
    return "".join(lines)


def _generic_step_summary(data: dict[str, Any]) -> str:
    rows: list[tuple[str, str]] = []
    for key, val in data.items():
        if key in _SKIP_TOP_KEYS:
            continue
        if any(str(key).endswith(s) for s in _PATH_SUFFIXES) and isinstance(val, str):
            rows.append((key.replace("_", " "), f"`{Path(val).name}`"))
            continue
        if isinstance(val, (int, float, str, bool)) or val is None:
            rows.append((key.replace("_", " "), _fmt_scalar(val)))
        elif isinstance(val, list) and val and all(isinstance(x, str) for x in val):
            return _bool_list([str(x) for x in val])
    if rows:
        return _kv_table(rows)
    return "- *(See `results/` JSON for nested fields.)*\n"
