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
        ("00", "Design SSOT", "Geometry, injectants, compile PICMI overrides"),
        ("01", "WarpX PIC", "2D arcjet: ρ_e and beam coupling at pad point"),
        ("02", "PIC reduce", "Normalize ρ proxies for plant"),
        ("03", "Fusion channel", "Longitudinal s–r + laminar clump metrics"),
        ("04", "Fueling", "n_p, n_B, T_i from injectants + PIC"),
        ("05", "p-¹¹B burn", "Fusion power (proof: scale = 1)"),
        ("06", "0D plant", "U1–U4, wall, CH₄, HTS"),
        ("07", "Jet closure", "F² ≈ 2ηPṁ discipline"),
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

    def update_injectants(self, *, h2_sccm: float, b2h6_sccm: float) -> None:
        self.config["injectants"].update({"h2_sccm": h2_sccm, "b2h6_sccm": b2h6_sccm})

    def update_pad(
        self,
        *,
        throttle: float,
        compressor: float,
        cathode_pulse: float,
        laminar: bool,
    ) -> None:
        self.config["pad"].update(
            {
                "throttle": throttle,
                "compressor": compressor,
                "cathode_pulse": cathode_pulse,
                "laminar_relaminarization": laminar,
            }
        )

    def update_pic_settings(self, *, steps: int, skip_pic: bool) -> None:
        self.config["pic"]["steps"] = steps
        self.config.setdefault("gui", {})["skip_pic"] = skip_pic

    def picmi_overrides_text(self) -> str:
        path = CHAIN_ROOT / "00_spec" / "picmi_overrides.json"
        if path.is_file():
            return path.read_text(encoding="utf-8")
        gen = _REPO / "build/orbitron/generated/picmi_overrides.json"
        if gen.is_file():
            return gen.read_text(encoding="utf-8")
        return "{}"
