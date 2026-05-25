"""Load experiment YAML and apply to chain_config.json."""
from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from tools.orbitron_proof_chain.chain_lib import (
    ensure_config,
    patch_geometry_into_picmi_overrides,
    save_config,
    stabilize_pic_settings,
    utc_now,
)


@dataclass
class ExperimentConfig:
    """Parsed experiment file."""

    experiment_name: str
    description: str = ""
    run: dict[str, Any] = field(default_factory=dict)
    geometry: dict[str, Any] = field(default_factory=dict)
    injectants: dict[str, Any] = field(default_factory=dict)
    pad: dict[str, Any] = field(default_factory=dict)
    pic: dict[str, Any] = field(default_factory=dict)
    fusion_channel: dict[str, Any] = field(default_factory=dict)
    unobtanium: dict[str, Any] = field(default_factory=dict)
    plant_scales: dict[str, Any] = field(default_factory=dict)
    source_path: Path | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def skip_pic(self) -> bool:
        return bool(self.run.get("skip_pic", False))

    @property
    def run_inverse(self) -> bool:
        return bool(self.run.get("run_inverse", True))

    @property
    def run_gap_agent(self) -> bool:
        return bool(self.run.get("run_gap_agent", True))

    @property
    def reuse_gap_analysis(self) -> bool:
        """If ``UNOBTANIUM_GAP.md`` already exists in the report dir, skip the Cursor agent."""
        return bool(self.run.get("reuse_gap_analysis", False))

    @property
    def pic_steps_override(self) -> int | None:
        v = self.run.get("pic_steps")
        return int(v) if v is not None else None

    @property
    def require_pic(self) -> bool:
        return bool(self.run.get("require_pic", False))

    @property
    def physics_strict(self) -> bool:
        return bool(self.run.get("physics_strict", True))


def load_experiment_yaml(path: Path) -> ExperimentConfig:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Experiment YAML must be a mapping: {path}")
    name = data.get("experiment_name")
    if not name or not str(name).strip():
        raise ValueError("experiment_name is required in experiment YAML")
    run = dict(data.get("run") or {})
    # Headless reports: inverse + gap analytics on unless opted out.
    run.setdefault("run_inverse", True)
    run.setdefault("run_gap_agent", True)
    return ExperimentConfig(
        experiment_name=str(name).strip(),
        description=str(data.get("description", "") or "").strip(),
        run=run,
        geometry=dict(data.get("geometry") or {}),
        injectants=dict(data.get("injectants") or {}),
        pad=dict(data.get("pad") or {}),
        pic=dict(data.get("pic") or {}),
        fusion_channel=dict(data.get("fusion_channel") or {}),
        unobtanium=dict(data.get("unobtanium") or {}),
        plant_scales=dict(data.get("plant_scales") or {}),
        source_path=path.resolve(),
        raw=data,
    )


def apply_experiment_to_chain(exp: ExperimentConfig) -> dict[str, Any]:
    """Merge experiment dict into chain_config and persist."""
    cfg = ensure_config()
    if exp.geometry:
        cfg["geometry"].update(exp.geometry)
    if exp.injectants:
        cfg["injectants"].update(exp.injectants)
    if exp.pad:
        cfg["pad"].update(exp.pad)
    pic_notes: list[str] = []
    if exp.pic:
        cfg["pic"].update(exp.pic)
        pic_notes = stabilize_pic_settings(cfg)
    if exp.fusion_channel:
        cfg.setdefault("fusion_channel", {}).update(exp.fusion_channel)
    if exp.unobtanium:
        cfg["unobtanium"].update(exp.unobtanium)
    if exp.plant_scales:
        cfg.setdefault("plant_scales", {}).update(exp.plant_scales)
    cfg["experiment"] = {
        "name": exp.experiment_name,
        "description": exp.description,
        "source_yaml": str(exp.source_path) if exp.source_path else None,
        "applied_utc": utc_now(),
        "pic_stability_notes": pic_notes,
    }
    patch_geometry_into_picmi_overrides(cfg)
    save_config(cfg)
    return cfg


def snapshot_parameters(exp: ExperimentConfig, cfg: dict[str, Any]) -> dict[str, Any]:
    """Parameters block for the report (experiment + resolved chain)."""
    return {
        "experiment_name": exp.experiment_name,
        "description": exp.description,
        "run": exp.run,
        "geometry": copy.deepcopy(cfg.get("geometry", {})),
        "injectants": copy.deepcopy(cfg.get("injectants", {})),
        "pad": copy.deepcopy(cfg.get("pad", {})),
        "pic": copy.deepcopy(cfg.get("pic", {})),
        "fusion_channel": copy.deepcopy(cfg.get("fusion_channel", {})),
        "unobtanium": copy.deepcopy(cfg.get("unobtanium", {})),
        "plant_scales": copy.deepcopy(cfg.get("plant_scales", {})),
        "proof_mode": cfg.get("proof_mode", True),
        "chain_root": cfg.get("chain_root"),
    }


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=_json_default), encoding="utf-8")


def _json_default(o: Any) -> Any:
    if isinstance(o, Path):
        return str(o)
    raise TypeError(type(o))
