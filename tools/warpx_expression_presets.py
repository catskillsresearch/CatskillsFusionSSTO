"""
Vetted template layer for WarpX / PICMI ``AnalyticAppliedField`` and analytic distribution
strings. YAML may only select ``preset`` names registered here and ``slots`` validated
per-preset — no free-form parser strings from the repo.

Used by ``orbitron_physics_spec`` (JSON overrides) and ``laminar_flow_2d_arcjet.py``.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Callable

# ---------------------------------------------------------------------------
# Default bundle (must match orbitron_physics_surrogate.yaml defaults)
# ---------------------------------------------------------------------------

DEFAULT_EXPRESSION_BUNDLE: dict[str, Any] = {
    "version": 1,
    "applied_E": {"preset": "orbitron_cylindrical_radial_e_xz", "slots": {}},
    "electron_ring_density": {"preset": "orbitron_annulus_uniform_density_xz", "slots": {}},
    "electron_ring_momentum": {
        "preset": "orbitron_exb_ring_momentum_xz",
        "slots": {"r_floor_m": 1.0e-4},
    },
    "arc_channel_seed_density": {
        "preset": "orbitron_annulus_uniform_density_xz",
        "slots": {"r_outer_scale": 0.98},
    },
}

# preset -> allowed slot keys -> (min, max) inclusive; key absent => optional slot
_SLOT_BOUNDS: dict[str, dict[str, tuple[float, float]]] = {
    "orbitron_cylindrical_radial_e_xz": {},
    "orbitron_annulus_uniform_density_xz": {
        "r_outer_scale": (0.5, 1.0),
    },
    "orbitron_exb_ring_momentum_xz": {
        "r_floor_m": (1.0e-8, 1.0e-2),
    },
}

_EMITTERS: dict[str, Callable[..., Any]] = {}


def _register(name: str, fn: Callable[..., Any]) -> None:
    _EMITTERS[name] = fn


def allowed_presets() -> frozenset[str]:
    return frozenset(_EMITTERS.keys())


def _emit_cylindrical_radial_e_xz(_slots: dict[str, float], *, E0s: str, r_ca: str, r_ca2: str) -> tuple[str, str, str]:
    ex = (
        f"({E0s} * x / if(sqrt(x*x + z*z) > {r_ca}, sqrt(x*x + z*z), {r_ca})) * "
        f"if(x*x + z*z >= {r_ca2}, 1.0, 0.0)"
    )
    ez = (
        f"({E0s} * z / if(sqrt(x*x + z*z) > {r_ca}, sqrt(x*x + z*z), {r_ca})) * "
        f"if(x*x + z*z >= {r_ca2}, 1.0, 0.0)"
    )
    return ex, "0.0", ez


def _emit_annulus_uniform_density_xz(
    _slots: dict[str, float],
    *,
    n_scale: str,
    r_inner: str,
    r_outer: str,
) -> str:
    return (
        f"{n_scale} * if(sqrt(x*x + z*z) > {r_inner}, 1.0, 0.0) * "
        f"if(sqrt(x*x + z*z) < {r_outer}, 1.0, 0.0)"
    )


def _emit_exb_ring_momentum_xz(
    slots: dict[str, float],
    *,
    E0s: str,
    Bys: str,
    r_eps: str,
) -> tuple[str, str, str]:
    _ = slots
    ux = f"-({E0s} * z / if(sqrt(x*x + z*z) > {r_eps}, sqrt(x*x + z*z), {r_eps})) / {Bys}"
    uz = f"({E0s} * x / if(sqrt(x*x + z*z) > {r_eps}, sqrt(x*x + z*z), {r_eps})) / {Bys}"
    return ux, "0.0", uz


_register("orbitron_cylindrical_radial_e_xz", _emit_cylindrical_radial_e_xz)
_register("orbitron_annulus_uniform_density_xz", _emit_annulus_uniform_density_xz)
_register("orbitron_exb_ring_momentum_xz", _emit_exb_ring_momentum_xz)


def _validate_slots(preset: str, slots: dict[str, Any]) -> dict[str, float]:
    bounds = _SLOT_BOUNDS.get(preset)
    if bounds is None:
        raise ValueError(f"unknown preset for slot validation: {preset!r}")
    out: dict[str, float] = {}
    for k, v in (slots or {}).items():
        if k not in bounds:
            raise ValueError(f"preset {preset!r} does not allow slot {k!r}; allowed: {sorted(bounds)}")
        out[k] = float(v)
    for k, val in out.items():
        lo, hi = bounds[k]
        if not (lo <= val <= hi):
            raise ValueError(f"slot {preset}.{k}={val} out of bounds [{lo}, {hi}]")
    return out


def _validate_entry(name: str, entry: Any) -> dict[str, Any]:
    if not isinstance(entry, dict):
        raise TypeError(f"expression_bundle.{name} must be a mapping")
    preset = entry.get("preset")
    if not isinstance(preset, str) or preset not in _EMITTERS:
        raise ValueError(
            f"expression_bundle.{name}.preset must be one of {sorted(_EMITTERS)}; got {preset!r}"
        )
    slots_raw = entry.get("slots") or {}
    if not isinstance(slots_raw, dict):
        raise TypeError(f"expression_bundle.{name}.slots must be a mapping")
    slots = _validate_slots(preset, slots_raw)
    return {"preset": preset, "slots": slots}


_ALLOWED_TOP_KEYS = frozenset(
    {"version", "applied_E", "electron_ring_density", "electron_ring_momentum", "arc_channel_seed_density"}
)


def validate_expression_bundle(bundle: dict[str, Any] | None) -> dict[str, Any]:
    """
    Return a normalized expression_bundle dict. ``None`` / missing → DEFAULT copy.
    Raises ValueError/TypeError on unknown presets, bad slots, or wrong version.
    """
    if bundle is None:
        return copy.deepcopy(DEFAULT_EXPRESSION_BUNDLE)
    if not isinstance(bundle, dict):
        raise TypeError("expression_bundle must be a mapping or null")
    for k in bundle:
        if k not in _ALLOWED_TOP_KEYS:
            raise ValueError(f"expression_bundle: unknown key {k!r}")
    ver = bundle.get("version", 1)
    if int(ver) != 1:
        raise ValueError(f"expression_bundle.version must be 1; got {ver!r}")
    out: dict[str, Any] = {"version": 1}
    for key in (
        "applied_E",
        "electron_ring_density",
        "electron_ring_momentum",
        "arc_channel_seed_density",
    ):
        if key not in bundle:
            raise ValueError(f"expression_bundle missing required key {key!r}")
        out[key] = _validate_entry(key, bundle[key])
    if out["electron_ring_density"]["slots"]:
        raise ValueError(
            "expression_bundle.electron_ring_density.slots must be empty — "
            "ring radii come from picmi.species_geometry only."
        )
    return out


@dataclass(frozen=True)
class PicmiEmitContext:
    """Pre-formatted numeric strings (_wx) and species scalars for preset emitters."""

    E0s: str
    r_ca: str
    r_ca2: str
    Bys: str
    r_eps: str
    n_es: str
    r_ring_in: str
    r_ring_out: str
    arc_s: str
    r_arc_in: str
    r_arc_out: str


def emit_picmi_expressions(
    expression_bundle: dict[str, Any] | None,
    ctx: PicmiEmitContext,
) -> dict[str, Any]:
    """
    Build PICMI string fields from a validated bundle + emit context.

    Returns keys: ``Ex_expression``, ``Ez_expression``, ``Ey_expression``,
    ``electron_density_expression``, ``electron_momentum_expressions`` (list of 3),
    ``arc_density_expression``.
    """
    bundle = validate_expression_bundle(expression_bundle)

    e_e = bundle["applied_E"]
    fn_e = _EMITTERS[str(e_e["preset"])]
    ex, ey, ez = fn_e(e_e["slots"], E0s=ctx.E0s, r_ca=ctx.r_ca, r_ca2=ctx.r_ca2)

    ed = bundle["electron_ring_density"]
    fn_d = _EMITTERS[str(ed["preset"])]
    if ed["preset"] != "orbitron_annulus_uniform_density_xz":
        raise ValueError("electron_ring_density: only orbitron_annulus_uniform_density_xz is supported")
    rho_e = fn_d(ed["slots"], n_scale=ctx.n_es, r_inner=ctx.r_ring_in, r_outer=ctx.r_ring_out)

    em = bundle["electron_ring_momentum"]
    fn_m = _EMITTERS[str(em["preset"])]
    if em["preset"] != "orbitron_exb_ring_momentum_xz":
        raise ValueError("electron_ring_momentum: only orbitron_exb_ring_momentum_xz is supported")
    mux, muy, muz = fn_m(em["slots"], E0s=ctx.E0s, Bys=ctx.Bys, r_eps=ctx.r_eps)

    ad = bundle["arc_channel_seed_density"]
    if ad["preset"] != "orbitron_annulus_uniform_density_xz":
        raise ValueError("arc_channel_seed_density: only orbitron_annulus_uniform_density_xz is supported")
    rho_a = fn_d(ad["slots"], n_scale=ctx.arc_s, r_inner=ctx.r_arc_in, r_outer=ctx.r_arc_out)

    return {
        "Ex_expression": ex,
        "Ey_expression": ey,
        "Ez_expression": ez,
        "electron_density_expression": rho_e,
        "electron_momentum_expressions": [mux, muy, muz],
        "arc_density_expression": rho_a,
    }


def merge_expression_bundle_into_picmi_json(picmi_json: dict[str, Any], spec: dict[str, Any]) -> None:
    """Mutate ``picmi_json`` to include validated ``expression_bundle`` from physics spec."""
    pic = spec.get("picmi") or {}
    raw = pic.get("expression_bundle")
    picmi_json["expression_bundle"] = validate_expression_bundle(raw)


if __name__ == "__main__":
    assert validate_expression_bundle(None)["applied_E"]["preset"] == "orbitron_cylindrical_radial_e_xz"
    try:
        validate_expression_bundle({"version": 1})
    except ValueError:
        pass
    else:
        raise SystemExit("expected ValueError for missing keys")
    try:
        validate_expression_bundle(
            {
                "version": 1,
                "applied_E": {"preset": "orbitron_cylindrical_radial_e_xz", "slots": {}},
                "electron_ring_density": {"preset": "orbitron_annulus_uniform_density_xz", "slots": {}},
                "electron_ring_momentum": {
                    "preset": "orbitron_exb_ring_momentum_xz",
                    "slots": {"r_floor_m": 999.0},
                },
                "arc_channel_seed_density": {
                    "preset": "orbitron_annulus_uniform_density_xz",
                    "slots": {"r_outer_scale": 0.98},
                },
            }
        )
    except ValueError:
        pass
    else:
        raise SystemExit("expected ValueError for r_floor out of bounds")
    try:
        validate_expression_bundle(
            {
                "version": 1,
                "applied_E": {"preset": "orbitron_cylindrical_radial_e_xz", "slots": {}},
                "electron_ring_density": {"preset": "orbitron_annulus_uniform_density_xz", "slots": {}},
                "electron_ring_momentum": {
                    "preset": "orbitron_exb_ring_momentum_xz",
                    "slots": {"r_floor_m": 1e-4},
                },
                "arc_channel_seed_density": {
                    "preset": "orbitron_annulus_uniform_density_xz",
                    "slots": {"r_outer_scale": 0.98},
                },
                "extra": {},
            }
        )
    except ValueError:
        pass
    else:
        raise SystemExit("expected ValueError for unknown top key")
    ctx = PicmiEmitContext(
        E0s="1.0",
        r_ca="0.005",
        r_ca2="2.5e-5",
        Bys="2.0",
        r_eps="0.0001",
        n_es="1e15",
        r_ring_in="0.01",
        r_ring_out="0.03",
        arc_s="1e14",
        r_arc_in="0.035",
        r_arc_out="0.049",
    )
    out = emit_picmi_expressions(None, ctx)
    assert "sqrt(x*x + z*z)" in out["Ex_expression"]
    print("warpx_expression_presets: OK")
