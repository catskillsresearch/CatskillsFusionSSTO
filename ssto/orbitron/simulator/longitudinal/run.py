"""Orchestrate longitudinal focus runs (PIC timelapse + annulus flow)."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np

from ssto.orbitron.simulator.longitudinal.annulus_flow import AnnulusFlowConfig, run_annulus_flow
from ssto.orbitron.simulator.longitudinal.focus import FocusDomain, LongitudinalFocus, focus_domain
from ssto.orbitron.simulator.longitudinal.fusion_channel_sr import (
    fusion_channel_to_longitudinal_run,
    run_fusion_channel_sr,
)
from ssto.orbitron.simulator.longitudinal.heuristic_pic import run_heuristic_pic_frames
from ssto.orbitron.simulator.longitudinal.warpx_frames import PicFrameStack, load_warpx_density_frames
from ssto.orbitron.simulator.plant_0d import evaluate_steady_state
from ssto.orbitron.simulator.types import SimulatorInputs
from ssto.orbitron.simulator.warpx_backend import run_pic_slice, repo_root


class FieldKind(str, Enum):
    RHO_E = "rho_e"
    RHO_BEAM = "rho_beam"
    TEMPERATURE = "temperature_k"
    VELOCITY_S = "velocity_s"
    DENSITY_AIR = "density_air"


@dataclass
class LongitudinalRun:
    """Unified timelapse payload for the GUI player."""

    focus: LongitudinalFocus
    domain: FocusDomain
    time_s: np.ndarray
    # 2D slice for display: (nt, n_vertical, n_horizontal)
    primary: np.ndarray
    secondary: np.ndarray | None
    axis_horizontal: np.ndarray
    axis_vertical: np.ndarray
    primary_label: str
    secondary_label: str
    horizontal_label: str
    vertical_label: str
    meta: dict[str, Any] = field(default_factory=dict)


def _stack_to_longitudinal_run(
    focus: LongitudinalFocus,
    domain: FocusDomain,
    stack: PicFrameStack,
    *,
    meta_extra: dict | None = None,
) -> LongitudinalRun:
    mask = stack.r_m <= domain.r_max_m
    r = stack.r_m[mask]
    rho_e = stack.rho_e[:, :, mask]
    rho_b = stack.rho_beam[:, :, mask]
    meta = {"model": stack.meta.get("model", "pic_frames"), **(meta_extra or {})}
    meta.update(stack.meta)
    return LongitudinalRun(
        focus=focus,
        domain=domain,
        time_s=stack.time_s,
        primary=rho_e,
        secondary=rho_b,
        axis_horizontal=r,
        axis_vertical=stack.z_m,
        primary_label="|ρ_e| (PIC)",
        secondary_label="|ρ_beam| (PIC)",
        horizontal_label="Radius r [m]",
        vertical_label="Cross-section z [m] (transverse plane at core)",
        meta=meta,
    )


def run_longitudinal(
    focus: LongitudinalFocus,
    inputs: SimulatorInputs,
    *,
    work_dir: Path | None = None,
    pic_steps: int = 400,
    annulus_cfg: AnnulusFlowConfig | None = None,
    use_heuristic_pic: bool = False,
    pic_stack: PicFrameStack | None = None,
) -> LongitudinalRun:
    domain = focus_domain(focus, inputs)

    if focus == LongitudinalFocus.FUSION_CHANNEL_SR:
        from ssto.orbitron.simulator.longitudinal.fusion_channel_sr import laminar_hack_from_inputs

        laminar = laminar_hack_from_inputs(
            inputs,
            force_off=not inputs.pad.laminar_relaminarization,
        )
        fc = run_fusion_channel_sr(domain, inputs, laminar=laminar)
        return fusion_channel_to_longitudinal_run(fc, domain)

    if focus == LongitudinalFocus.FULL_DUCT_AIR:
        af = run_annulus_flow(domain, inputs, annulus_cfg)
        return LongitudinalRun(
            focus=focus,
            domain=domain,
            time_s=af.time_s,
            primary=af.temperature_k,
            secondary=af.velocity_s_mps,
            axis_horizontal=af.s_m,
            axis_vertical=af.r_m,
            primary_label="Air temperature [K]",
            secondary_label="Axial velocity u_s [m/s]",
            horizontal_label="Axial s [m] (intake → nozzle)",
            vertical_label="Radius r [m]",
            meta={
                "model": "annulus_flow_2d",
                "mdot_kgps": evaluate_steady_state(inputs).mass_flow_kgps,
            },
        )

    if pic_stack is not None:
        return _stack_to_longitudinal_run(focus, domain, pic_stack)

    if use_heuristic_pic:
        stack = run_heuristic_pic_frames(domain, inputs, n_frames=min(60, pic_steps // 5))
        return _stack_to_longitudinal_run(
            focus,
            domain,
            stack,
            meta_extra={"note": "Heuristic transverse preview — run WarpX for PIC data."},
        )

    # Core levels: WarpX transverse PIC timelapse
    root = repo_root()
    work = work_dir or (root / "build" / "simulator_longitudinal" / focus.value)
    work.mkdir(parents=True, exist_ok=True)
    diags = work / "diags"
    if (diags).exists() and list(diags.glob("density_diag*")):
        stack = load_warpx_density_frames(diags, domain)
        return _stack_to_longitudinal_run(
            focus,
            domain,
            stack,
            meta_extra={"note": "Loaded cached WarpX diags."},
        )

    log = run_pic_slice(inputs, work, n_steps=pic_steps)
    if not log.get("ok"):
        raise RuntimeError(log.get("error", "WarpX failed"))

    stack = load_warpx_density_frames(diags, domain)
    return _stack_to_longitudinal_run(
        focus,
        domain,
        stack,
        meta_extra={
            "note": "Fusion E×B physics is transverse; magnet outline in level 2 is schematic.",
            "warpx_log": log,
        },
    )
