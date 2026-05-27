"""Thermal zoning splits and radial budget."""
from __future__ import annotations

from ssto.orbitron.simulator.plant_0d import evaluate_steady_state
from ssto.orbitron.simulator.thermal_zoning import (
    evaluate_thermal_split,
    radial_zones_from_geometry,
)
from ssto.orbitron.simulator.types import DeviceGeometry, SimulatorInputs


def test_radial_zones_phase1_budget():
    g = DeviceGeometry(r_anode_m=0.04, r_cathode_m=0.01, length_m=1.2)
    z = radial_zones_from_geometry(g)
    assert abs(z.r_first_wall_m - 0.04) < 1e-9
    assert abs(z.r_air_channel_outer_m - 0.06) < 1e-9
    assert abs(z.r_magnet_outer_m - 0.10) < 1e-9
    assert abs(z.reactor_outer_diameter_m - 0.20) < 1e-9


def test_thermal_split_partitions_first_wall():
    split = evaluate_thermal_split(
        first_wall_kw=400.0,
        gross_power_mw=3.5,
        magnet_cryo_kw=0.18,
    )
    assert abs(split.ch4_wall_intercept_kw + split.air_annulus_kw - 400.0) < 1e-6
    assert split.brayton_thermal_kw > split.air_annulus_kw


def test_plant_exposes_thermal_fields_when_armed():
    inp = SimulatorInputs(
        geometry=DeviceGeometry(r_anode_m=0.04, r_cathode_m=0.01),
    )
    inp.pad.startup_trigger = True
    inp.pad.bleed_air_open = True
    inp.pad.pad_apu_online = True
    inp.pad.starter_engage = True
    inp.pad.vacuum_interlock_ok = True
    inp.pad.laser_armed = True
    inp.pad.hv_enabled = True
    res = evaluate_steady_state(inp)
    assert res.reactor_outer_diameter_m > 0.15
    assert res.brayton_thermal_kw > 0
    assert res.ch4_wall_intercept_kw > 0
