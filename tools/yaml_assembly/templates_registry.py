"""Template id → CadQuery geometry builders (params from YAML only; no layout constants here)."""

from __future__ import annotations

from typing import Any, Callable

import cadquery as cq

from arcjet_test_stand_cad import (
    bay_inlet_annulus_shroud,
    bd_annulus_sleeve,
    bd_bracket_seal_flange,
    bd_shock_core_insert,
    bellmouth_flare,
    blast_detuner,
    compressor_housing,
    lab_fuel_feed_valve,
    load_cell_puck,
    nozzle_cd_contour,
    nozzle_exit_hardware,
    nozzle_inlet_plenum,
    nozzle_stub,
    rail_beam,
    thrust_sled_frame,
)
from full_reactor_cad import (
    IntegratedOrbitronTube,
    LabInfrastructure,
    fusion_exhaust_outlet_ring,
    lab_b2h6_injectant_trunk_params,
    lab_h2_injectant_trunk_params,
)

from yaml_assembly.connector_routing import build_connector_routing


def _tube() -> tuple[cq.Workplane, ...]:
    return IntegratedOrbitronTube().build()


def tpl_bellmouth_flare(**params: Any) -> cq.Workplane:
    return bellmouth_flare(
        inlet_r=float(params.get("inlet_r", 0.18)),
        throat_r=float(params.get("throat_r", 0.05)),
        length=float(params.get("length", 0.35)),
    )


def tpl_compressor_housing(**params: Any) -> cq.Workplane:
    return compressor_housing(
        od=float(params.get("od", 0.14)),
        length=float(params.get("length", 0.25)),
    )


def tpl_bay_inlet_annulus_shroud(**params: Any) -> cq.Workplane:
    return bay_inlet_annulus_shroud(
        x0=float(params.get("x0", -0.31)),
        length=float(params.get("length", 0.175)),
        outer_r=float(params.get("outer_r", 0.149)),
        inner_r=float(params.get("inner_r", 0.088)),
    )


def tpl_nozzle_stub(**params: Any) -> cq.Workplane:
    return nozzle_stub(
        throat_r=float(params.get("throat_r", 0.045)),
        exit_r=float(params.get("exit_r", 0.09)),
        length=float(params.get("length", 0.2)),
    )


def tpl_blast_detuner(**params: Any) -> cq.Workplane:
    return blast_detuner(
        inner_r=float(params.get("inner_r", 0.35)),
        wall=float(params.get("wall", 0.04)),
        length=float(params.get("length", 2.0)),
    )


def tpl_nozzle_inlet_plenum(**params: Any) -> cq.Workplane:
    return nozzle_inlet_plenum(
        inlet_r=float(params.get("inlet_r", 0.056)),
        mid_r=float(params.get("mid_r", 0.048)),
        length=float(params.get("length", 0.07)),
    )


def tpl_nozzle_cd_contour(**params: Any) -> cq.Workplane:
    return nozzle_cd_contour(
        r0=float(params.get("r0", 0.048)),
        throat_r=float(params.get("throat_r", 0.045)),
        length=float(params.get("length", 0.05)),
    )


def tpl_nozzle_exit_hardware(**params: Any) -> cq.Workplane:
    return nozzle_exit_hardware(
        throat_r=float(params.get("throat_r", 0.045)),
        exit_r=float(params.get("exit_r", 0.09)),
        length=float(params.get("length", 0.08)),
    )


def tpl_bd_annulus_sleeve(**params: Any) -> cq.Workplane:
    return bd_annulus_sleeve(
        inner_flow_r=float(params.get("inner_flow_r", 0.34)),
        annulus_gap=float(params.get("annulus_gap", 0.048)),
        wall=float(params.get("wall", 0.042)),
        length=float(params.get("length", 0.75)),
    )


def tpl_bd_shock_core_insert(**params: Any) -> cq.Workplane:
    return bd_shock_core_insert(
        radius=float(params.get("radius", 0.29)),
        length=float(params.get("length", 0.9)),
    )


def tpl_bd_bracket_seal_flange(**params: Any) -> cq.Workplane:
    return bd_bracket_seal_flange(
        outer_r=float(params.get("outer_r", 0.42)),
        inner_r=float(params.get("inner_r", 0.33)),
        thickness=float(params.get("thickness", 0.06)),
        n_bolts=int(params.get("n_bolts", 8)),
    )


def tpl_lab_fuel_feed_valve(**params: Any) -> cq.Workplane:
    return lab_fuel_feed_valve(
        body_r=float(params.get("body_r", 0.045)),
        stem_r=float(params.get("stem_r", 0.018)),
        stem_h=float(params.get("stem_h", 0.055)),
    )


def tpl_orbitron_exhaust_outlet_ring(**params: Any) -> cq.Workplane:
    return fusion_exhaust_outlet_ring(
        outer_r=float(params.get("outer_r", 0.082)),
        inner_r=float(params.get("inner_r", 0.055)),
        thickness=float(params.get("thickness", 0.016)),
    )


def tpl_thrust_sled_frame(**params: Any) -> cq.Workplane:
    return thrust_sled_frame(
        length=float(params.get("length", 2.2)),
        width=float(params.get("width", 1.0)),
        rail_h=float(params.get("rail_h", 0.08)),
    )


def tpl_rail_beam(**params: Any) -> cq.Workplane:
    return rail_beam(span=float(params.get("span", 3.5)))


def tpl_load_cell_puck(**params: Any) -> cq.Workplane:
    return load_cell_puck()


def tpl_orbitron_anode(**_: Any) -> cq.Workplane:
    a, *_ = _tube()
    return a


def tpl_orbitron_dec_grid(**_: Any) -> cq.Workplane:
    return _tube()[1]


def tpl_orbitron_cathode(**_: Any) -> cq.Workplane:
    return _tube()[2]


def tpl_orbitron_insulators(**_: Any) -> cq.Workplane:
    return _tube()[3]


def tpl_orbitron_magnet(**_: Any) -> cq.Workplane:
    return _tube()[4]


def tpl_orbitron_nbi(**_: Any) -> cq.Workplane:
    return _tube()[5]


def _infra() -> LabInfrastructure:
    return LabInfrastructure()


def tpl_lab_tank_hydrogen(**_: Any) -> cq.Workplane:
    h2, *_ = _infra().build_fuel_farm()
    return h2


def tpl_lab_tank_diborane(**_: Any) -> cq.Workplane:
    _, b2, *_ = _infra().build_fuel_farm()
    return b2


def tpl_lab_tank_cryo_methane(**_: Any) -> cq.Workplane:
    _, _, d, *_ = _infra().build_fuel_farm()
    return d


def tpl_lab_decal_h2(**_: Any) -> cq.Workplane:
    return _infra().build_fuel_farm()[3]


def tpl_lab_decal_b2h6(**_: Any) -> cq.Workplane:
    return _infra().build_fuel_farm()[4]


def tpl_lab_decal_ch4(**_: Any) -> cq.Workplane:
    return _infra().build_fuel_farm()[5]


def tpl_lab_hv_umbilical(**params: Any) -> cq.Workplane:
    if params.get("connector_ports") and params.get("connector_links"):
        anchors = LabInfrastructure().hv_connector_anchors()
        return build_connector_routing(params, anchors)
    hv, _, _ = _infra().build_rigid_plumbing()
    return hv


def tpl_lab_fuel_gas_lines(**params: Any) -> cq.Workplane:
    if params.get("connector_ports") and params.get("connector_links"):
        anchors = LabInfrastructure().fuel_line_connector_anchors()
        return build_connector_routing(params, anchors)
    _, gas, _ = _infra().build_rigid_plumbing()
    return gas


def tpl_lab_h2_injectant_trunk(**params: Any) -> cq.Workplane:
    anchors = LabInfrastructure().fuel_line_connector_anchors()
    merged = {**lab_h2_injectant_trunk_params(), **params}
    return build_connector_routing(merged, anchors)


def tpl_lab_b2h6_injectant_trunk(**params: Any) -> cq.Workplane:
    anchors = LabInfrastructure().fuel_line_connector_anchors()
    merged = {**lab_b2h6_injectant_trunk_params(), **params}
    return build_connector_routing(merged, anchors)


def tpl_lab_cryo_methane_piping(**params: Any) -> cq.Workplane:
    if params.get("connector_ports") and params.get("connector_links"):
        anchors = LabInfrastructure().cryo_methane_connector_anchors()
        return build_connector_routing(params, anchors)
    _, _, meth = _infra().build_rigid_plumbing()
    return meth


def tpl_lab_operator_console_desk(**_: Any) -> cq.Workplane:
    d, _, _ = _infra().build_console()
    return d


def tpl_lab_operator_screen(**_: Any) -> cq.Workplane:
    _, s, _ = _infra().build_console()
    return s


def tpl_lab_big_red_button(**_: Any) -> cq.Workplane:
    *_, b = _infra().build_console()
    return b


TEMPLATE_REGISTRY: dict[str, Callable[..., cq.Workplane]] = {
    "bellmouth_flare": tpl_bellmouth_flare,
    "compressor_housing": tpl_compressor_housing,
    "bay_inlet_annulus_shroud": tpl_bay_inlet_annulus_shroud,
    "nozzle_stub": tpl_nozzle_stub,
    "nozzle_inlet_plenum": tpl_nozzle_inlet_plenum,
    "nozzle_cd_contour": tpl_nozzle_cd_contour,
    "nozzle_exit_hardware": tpl_nozzle_exit_hardware,
    "blast_detuner": tpl_blast_detuner,
    "bd_annulus_sleeve": tpl_bd_annulus_sleeve,
    "bd_shock_core_insert": tpl_bd_shock_core_insert,
    "bd_bracket_seal_flange": tpl_bd_bracket_seal_flange,
    "lab_fuel_feed_valve": tpl_lab_fuel_feed_valve,
    "orbitron_exhaust_outlet_ring": tpl_orbitron_exhaust_outlet_ring,
    "thrust_sled_frame": tpl_thrust_sled_frame,
    "rail_beam": tpl_rail_beam,
    "load_cell_puck": tpl_load_cell_puck,
    "orbitron_anode": tpl_orbitron_anode,
    "orbitron_dec_grid": tpl_orbitron_dec_grid,
    "orbitron_cathode": tpl_orbitron_cathode,
    "orbitron_insulators": tpl_orbitron_insulators,
    "orbitron_magnet": tpl_orbitron_magnet,
    "orbitron_nbi": tpl_orbitron_nbi,
    "lab_tank_hydrogen": tpl_lab_tank_hydrogen,
    "lab_tank_diborane": tpl_lab_tank_diborane,
    "lab_tank_cryo_methane": tpl_lab_tank_cryo_methane,
    "lab_decal_h2": tpl_lab_decal_h2,
    "lab_decal_b2h6": tpl_lab_decal_b2h6,
    "lab_decal_ch4": tpl_lab_decal_ch4,
    "lab_hv_umbilical": tpl_lab_hv_umbilical,
    "lab_fuel_gas_lines": tpl_lab_fuel_gas_lines,
    "lab_h2_injectant_trunk": tpl_lab_h2_injectant_trunk,
    "lab_b2h6_injectant_trunk": tpl_lab_b2h6_injectant_trunk,
    "lab_cryo_methane_piping": tpl_lab_cryo_methane_piping,
    "lab_operator_console_desk": tpl_lab_operator_console_desk,
    "lab_operator_screen": tpl_lab_operator_screen,
    "lab_big_red_button": tpl_lab_big_red_button,
}


def build_template(template_id: str, params: dict[str, Any] | None) -> cq.Workplane:
    fn = TEMPLATE_REGISTRY.get(template_id)
    if fn is None:
        keys = ", ".join(sorted(TEMPLATE_REGISTRY))
        raise KeyError(f"Unknown template {template_id!r}. Known: {keys}")
    return fn(**(params or {}))
