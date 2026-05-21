"""
Export design validation reports to YAML for spec documents (UNOBTANIUM / test stand).
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from ssto.orbitron.simulator.pad_startup import evaluate_pad_status
from ssto.orbitron.simulator.types import SimulatorInputs, SteadyStateResult
from ssto.orbitron.simulator.validation import DesignValidationReport, SpecStatus


def _spec_check_dict(c) -> dict[str, Any]:
    return {
        "spec_id": c.spec_id,
        "title": c.title,
        "required": c.required,
        "achieved": c.achieved,
        "margin": c.margin,
        "status": c.status.value,
        "notes": c.notes,
    }


def build_validation_document(
    inputs: SimulatorInputs,
    result: SteadyStateResult,
    report: DesignValidationReport,
    *,
    title: str = "p-¹¹B Orbitron design validation",
) -> dict[str, Any]:
    """Structured document for YAML export and spec traceability."""
    pad = evaluate_pad_status(inputs.pad)
    g = inputs.geometry
    u = inputs.unobtanium

    return {
        "schema_version": 1,
        "document_kind": "orbitron_design_validation",
        "title": title,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "proof_chain": os.environ.get("ORBITRON_PROOF_CHAIN") == "1",
            "proof_chain_artifact_root": os.environ.get("ORBITRON_CHAIN_ROOT", ""),
            "design_validated": report.design_validated,
            "message": report.summary,
            "fusion_operating_point": report.fusion_operating_point,
            "power_target_mw": report.power_target_mw,
            "power_achieved_mw": report.power_achieved_mw,
            "power_residual_mw": report.power_residual_mw,
            "jet_closure_rel_error": report.jet_closure_rel_error,
            "pic_coupling_used": report.pic_coupling_used,
        },
        "geometry": {
            "r_anode_m": g.r_anode_m,
            "r_cathode_m": g.r_cathode_m,
            "length_m": g.length_m,
            "V_cathode_kv": abs(g.V_cathode_v) / 1000.0,
            "B_axial_tesla": g.B_axial_tesla,
        },
        "pad_startup": {
            "pad_apu_online": pad.state.pad_apu_online,
            "starter_engage": pad.state.starter_engage,
            "bleed_air_open": pad.state.bleed_air_open,
            "startup_trigger": pad.state.startup_trigger,
            "throttle": pad.state.throttle,
            "compressor_command": pad.state.compressor,
            "compressor_effective": pad.compressor_effective,
            "cathode_pulse": pad.state.cathode_pulse,
        },
        "injectants": {
            "h2_sccm": inputs.operating.h2_sccm,
            "b2h6_sccm": inputs.operating.b2h6_sccm,
            "fueling_mix_scale": result.fueling_mix_scale,
        },
        "unobtanium_parameters": {
            "U1_field_emission_margin": u.field_emission_margin,
            "U2_max_wall_heat_flux_W_m2": u.max_wall_heat_flux_W_m2,
            "U2_ch4_cooling_effectiveness": u.ch4_cooling_effectiveness,
            "U3_hts_capability_scale": u.hts_capability_scale,
            "U4_fusion_reactivity_scale": u.fusion_reactivity_scale,
            "U4_beam_coupling_scale": u.beam_coupling_scale,
        },
        "fusion_physics_pb11": {
            "model": "ssto.orbitron.simulator.fusion_pb11",
            "reaction": "p + 11B -> 3 He4 + 8.68 MeV",
            "ion_temperature_kev": result.ion_temperature_kev,
            "sigma_v_m3_s": result.sigma_v_m3_s,
            "fusion_power_mw_physics": result.fusion_power_mw_physics,
            "fusion_power_mw_surrogate_blend": result.fusion_power_mw_surrogate,
            "gross_power_mw_blended": result.gross_power_mw,
            "plasma_density_cm3": result.plasma_density_cm3,
            "log10_density": result.log10_density,
            "pic_rho_e_norm": inputs.pic_rho_e_norm,
            "pic_beam_rho_norm": inputs.pic_beam_rho_norm,
        },
        "fusion_channel_sr": {
            "model": "ssto.orbitron.simulator.longitudinal.fusion_channel_sr",
            "view": "longitudinal s-r (tube along bore; not axial/transverse)",
            "laminar_relaminarization": inputs.pad.laminar_relaminarization,
            "laminar_hack_enabled": result.laminar_hack_enabled,
            "integrated_fusion_power_mw": result.fusion_channel_power_mw,
            "clump_index_final": result.clump_index,
            "clump_reduction_ratio_hack_off_on": result.clump_reduction_ratio,
            "fidelity_tier": 3,
            "notes": (
                "Demonstrates laminar relaminarization breaking mid-bore clumps; "
                "⟨σv⟩ is analytical p-11B fit, not PIC-integrated yield (Tier 4)."
            ),
        },
        "thermal_systems": {
            "wall_heat_kw": result.wall_heat_kw,
            "wall_heat_flux_W_m2": result.wall_heat_flux_W_m2,
            "ch4_mdot_kgps": result.ch4_mdot_kgps,
            "ch4_delta_T_K": result.ch4_delta_T_K,
            "hts_cryo_kw": result.hts_cryo_kw,
        },
        "plant_outputs": {
            "beam_current_ma": result.beam_current_ma,
            "beam_power_kw": result.beam_power_kw,
            "thrust_lbf": result.thrust_lbf,
            "mass_flow_kgps": result.mass_flow_kgps,
            "jet_kinetic_power_mw": result.jet_kinetic_power_mw,
            "equiv_exhaust_velocity_mps": result.equiv_exhaust_velocity_mps,
        },
        "spec_checks": [_spec_check_dict(c) for c in report.checks],
        "violations": list(result.violations),
        "feasible": result.feasible,
    }


def export_validation_yaml(
    path: Path,
    inputs: SimulatorInputs,
    result: SteadyStateResult,
    report: DesignValidationReport,
    *,
    title: str | None = None,
) -> Path:
    """Write validation document to ``path`` (creates parent dirs)."""
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = build_validation_document(
        inputs,
        result,
        report,
        title=title or "p-¹¹B Orbitron design validation",
    )
    header = (
        "# Auto-generated by Orbitron simulator — design validation for spec documents.\n"
        "# See ssto/orbitron/UNOBTANIUM.md and orbitron_physics_surrogate.yaml.\n"
    )
    with path.open("w", encoding="utf-8") as f:
        f.write(header)
        yaml.safe_dump(doc, f, sort_keys=False, default_flow_style=False, allow_unicode=True)
    return path
