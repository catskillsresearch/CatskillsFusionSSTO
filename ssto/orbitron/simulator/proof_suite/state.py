"""Proof Suite application state — sync UI ↔ chain_config.json."""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from tools.orbitron_proof_chain.chain_lib import (  # noqa: E402
    CHAIN_ROOT,
    CONFIG_PATH,
    ensure_config,
    load_config,
    load_step_json,
    save_config,
    step_completed,
)


class ProofSuiteState:
    """Mutable view of the proof chain for the GUI."""

    STEPS = [
        ("00", "Design SSOT", "Reply 19 BOM, geometry, PICMI overrides"),
        ("01", "1.1 Vacuum", "Rough + turbo pump-down; gauge interlock"),
        ("02", "1.3 Laser", "355 nm align, pulse meter, arm laser"),
        ("03", "1.2+1.4 Core HV", "Orbitron grid, Spellman bias, interlocks"),
        ("04", "1.5 Diagnostics", "PIPS / MCA 3-alpha check"),
        ("05", "Fueling H₂+B11", "H₂ sccm + solid ¹¹B laser ablation rate"),
        ("06", "0D plant", "U1–U4, wall, CH₄, HTS (Phase 2 jacket)"),
        ("07", "2.2 Jet closure", "Brayton F² ≈ 2ηPṁ; compressor/turbine"),
        ("08", "Validation export", "Spec YAML + pass/fail table"),
        ("09", "Inverse solve", "Required unobtanium if forward chain fails"),
    ]

    def __init__(self) -> None:
        self._cfg: dict[str, Any] | None = None

    def ensure_initialized(self) -> dict[str, Any]:
        self._cfg = ensure_config()
        return self._cfg

    @property
    def config(self) -> dict[str, Any]:
        if self._cfg is None:
            return self.ensure_initialized()
        return self._cfg

    def reload(self) -> dict[str, Any]:
        self._cfg = load_config() if CONFIG_PATH.is_file() else ensure_config()
        return self._cfg

    def save(self) -> None:
        save_config(self.config)

    def step_status(self, step: str) -> str:
        if not CONFIG_PATH.is_file():
            return "pending"
        if not step_completed(step):
            return "pending"
        try:
            data = load_step_json(step)
        except Exception:
            return "ok"
        if data.get("skipped"):
            return "skipped"
        if step == "08" and not data.get("design_validated"):
            return "warn"
        if step == "06" and not data.get("feasible", True):
            return "warn"
        if step == "05" and data.get("shortfall_mw", 0) > 0.5:
            return "warn"
        if step == "03" and data.get("clump_index_final", 99) > 2.8:
            return "warn"
        return "ok"

    def try_load_step(self, step: str) -> dict[str, Any] | None:
        if not step_completed(step):
            return None
        try:
            return load_step_json(step)
        except Exception:
            return None

    def update_geometry(
        self,
        *,
        r_anode_m: float,
        r_cathode_m: float,
        length_m: float,
        V_cathode_v: float,
        B_axial_tesla: float,
    ) -> None:
        g = self.config["geometry"]
        g.update(
            {
                "r_anode_m": r_anode_m,
                "r_cathode_m": r_cathode_m,
                "length_m": length_m,
                "V_cathode_v": V_cathode_v,
                "B_axial_tesla": B_axial_tesla,
            }
        )

    def update_injectants(
        self,
        *,
        h2_sccm: float,
        laser_ablation_hz: float,
        b11_target_index: int = 0,
    ) -> None:
        self.config["injectants"].update(
            {
                "h2_sccm": h2_sccm,
                "laser_ablation_hz": laser_ablation_hz,
                "b11_target_index": b11_target_index,
            }
        )

    def update_pad(
        self,
        *,
        throttle: float,
        compressor: float,
        cathode_pulse: float,
        laminar: bool,
        vacuum_interlock_ok: bool | None = None,
        laser_armed: bool | None = None,
        hv_enabled: bool | None = None,
    ) -> None:
        p = self.config["pad"]
        p.update(
            {
                "throttle": throttle,
                "compressor": compressor,
                "cathode_pulse": cathode_pulse,
                "laminar_relaminarization": laminar,
            }
        )
        if vacuum_interlock_ok is not None:
            p["vacuum_interlock_ok"] = vacuum_interlock_ok
        if laser_armed is not None:
            p["laser_armed"] = laser_armed
        if hv_enabled is not None:
            p["hv_enabled"] = hv_enabled

    def update_pic_settings(self, *, steps: int, diag_period: int, skip_pic: bool) -> None:
        self.config["pic"]["steps"] = steps
        self.config["pic"]["diag_period"] = max(1, int(diag_period))
        self.config.setdefault("gui", {})["skip_pic"] = skip_pic

    def picmi_overrides_text(self) -> str:
        path = CHAIN_ROOT / "00_spec" / "picmi_overrides.json"
        if path.is_file():
            return path.read_text(encoding="utf-8")
        gen = _REPO / "build/orbitron/generated/picmi_overrides.json"
        if gen.is_file():
            return gen.read_text(encoding="utf-8")
        return "{}"
