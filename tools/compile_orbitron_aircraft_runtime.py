#!/usr/bin/env python3
"""Emit <aircraft.package_dir>-set.xml, Models/Orbitron.xml, and orbitron-jsbsim.xml under Aircraft/.

YAML: ssto/orbitron/assembly_specs/orbitron_aircraft_flightgear.yaml
Physics (optional): surrogate_engineering corner scales → /sim/model/orbitron/surrogate/* bilinear ctc.
JSBSim: copy tools/templates/orbitron-jsbsim.xml (structure); full JSBSim-in-YAML is future work.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Mapping

import yaml

_EARTH_R_M = 6378137.0


def _text(parent: ET.Element, tag: str, value: str | float | int | bool) -> ET.Element:
    el = ET.SubElement(parent, tag)
    el.text = str(value).lower() if isinstance(value, bool) else str(value)
    return el


def _typed_prop(
    parent: ET.Element, name: str, value: float | int | bool, typ: str = "double"
) -> ET.Element:
    el = ET.SubElement(parent, name)
    el.set("type", typ)
    if typ == "bool":
        el.text = "true" if value else "false"
    elif typ == "double":
        el.text = f" {float(value)} "
    else:
        el.text = str(value)
    return el


def _indent(elem: ET.Element, level: int = 0) -> None:
    pad = "\n" + "    " * level
    pad_child = "\n" + "    " * (level + 1)
    children = list(elem)
    if children:
        if not elem.text or not elem.text.strip():
            elem.text = pad_child
        for child in children:
            _indent(child, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = pad
    else:
        if level and (not elem.tail or not str(elem.tail).strip()):
            elem.tail = pad
    for j, child in enumerate(children):
        if j + 1 < len(children):
            nxt = children[j + 1]
            if child.tail is None or not str(child.tail).strip():
                child.tail = pad_child


def _dest_point(lat_deg: float, lon_deg: float, course_deg: float, dist_m: float) -> tuple[float, float]:
    """Move dist_m along true course (deg); matches Nasal geo.Coord.apply_course_distance."""
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    brng = math.radians(course_deg)
    d = dist_m / _EARTH_R_M
    lat2 = math.asin(
        math.sin(lat) * math.cos(d) + math.cos(lat) * math.sin(d) * math.cos(brng)
    )
    lon2 = lon + math.atan2(
        math.sin(brng) * math.sin(d) * math.cos(lat),
        math.cos(d) - math.sin(lat) * math.sin(lat2),
    )
    return math.degrees(lat2), math.degrees(lon2)


def _lab_to_fg_view_offset(x_m: float, y_m: float, z_m: float) -> tuple[float, float, float]:
    """Identity pass-through for view offsets.

    Per FG wiki "Howto:Configure views in FlightGear" §View Offsets, the x/y/z-offset-m
    properties on from-model lookfrom AND lookat views are in FG body axes:
      +x = RIGHT of model origin (starboard)
      +y = UP from model origin
      +z = BACK / AFT from model origin
    The orbitron.ac mesh frame uses the same convention, so mesh coordinates pass
    through unchanged to FG.
    """
    return (x_m, y_m, z_m)


def _mesh_step_back_eye(
    base: tuple[float, float, float],
    aim: tuple[float, float, float],
    back_ft: float,
) -> tuple[float, float, float]:
    """Move eye away from aim along (base − aim), preserving look direction (lookat)."""
    back_m = back_ft * 0.3048
    dx = base[0] - aim[0]
    dy = base[1] - aim[1]
    dz = base[2] - aim[2]
    length = math.hypot(dx, dy, dz)
    if length < 1e-9:
        return base
    scale = back_m / length
    return (base[0] + dx * scale, base[1] + dy * scale, base[2] + dz * scale)


def _mesh_to_fg_body_view_offset(x_m: float, y_m: float, z_m: float) -> tuple[float, float, float]:
    """orbitron.ac mesh → FG body view offsets (wiki: +x right, +y up, +z aft).

    Verified part extents: mesh +X = rig nose, +Y = up, +Z = starboard / console side.
    Model heading 0 ⇒ mesh +X aligns with FG forward (−z), mesh +Z with FG right (+x).
    """
    return (z_m, y_m, -x_m)


def _ac_to_fg_body_view_offset(x_m: float, y_m: float, z_up_m: float) -> tuple[float, float, float]:
    return _mesh_to_fg_body_view_offset(x_m, y_m, z_up_m)


def _ac_to_fg_lookfrom_offset(x_m: float, y_m: float, z_up_m: float) -> tuple[float, float, float]:
    return (y_m, z_up_m, -x_m)


def _mesh_lookfrom_aim_angles_deg(
    eye: tuple[float, float, float],
    aim: tuple[float, float, float],
) -> tuple[float, float]:
    """Heading/pitch (deg) for orbitron.ac mesh (+X nose, +Y up, +Z starboard)."""
    dx = aim[0] - eye[0]
    dy = aim[1] - eye[1]
    dz = aim[2] - eye[2]
    hdist = math.hypot(dx, dz)
    if hdist < 1e-9:
        return (90.0 if dy > 0 else -90.0, 90.0 if dy > 0 else -90.0)
    return (math.degrees(math.atan2(dz, dx)), math.degrees(math.atan2(dy, hdist)))


def _ac_lookfrom_aim_angles_deg(
    eye: tuple[float, float, float],
    aim: tuple[float, float, float],
) -> tuple[float, float]:
    """Heading/pitch (deg) in AC (+X fwd, +Y right, +Z up) from eye toward aim."""
    dx = aim[0] - eye[0]
    dy = aim[1] - eye[1]
    dz = aim[2] - eye[2]
    hdist = math.hypot(dx, dy)
    if hdist < 1e-9:
        return (0.0, 90.0 if dz > 0 else -90.0)
    return (math.degrees(math.atan2(dy, dx)), math.degrees(math.atan2(dz, hdist)))


def _lab_offset_latlon(
    lat_deg: float,
    lon_deg: float,
    hdg_deg: float,
    x_m: float,
    y_m: float,
) -> tuple[float, float]:
    """Orbitron lab frame (+X thrust forward, +Y right, +Z up) → lat/lon at true heading."""
    lat, lon = lat_deg, lon_deg
    if x_m >= 0:
        lat, lon = _dest_point(lat, lon, hdg_deg, x_m)
    else:
        lat, lon = _dest_point(lat, lon, hdg_deg + 180.0, abs(x_m))
    if y_m >= 0:
        lat, lon = _dest_point(lat, lon, hdg_deg + 90.0, y_m)
    else:
        lat, lon = _dest_point(lat, lon, hdg_deg - 90.0, abs(y_m))
    return lat, lon


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    return 2 * _EARTH_R_M * math.asin(math.sqrt(a))


def _bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlon = math.radians(lon2 - lon1)
    y = math.sin(dlon) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dlon)
    return (math.degrees(math.atan2(y, x)) + 360.0) % 360.0


def _compute_sightline_operator_view(
    pad_lat: float,
    pad_lon: float,
    apron: Mapping[str, Any],
    distance_m: float,
    eye_agl_m: float,
    gnd_ft: float,
    clearance_ft: float,
) -> dict[str, float]:
    """World lookat eye on the BIKF Apron → pad line, close in; same mechanism as view_bikf_apron."""
    apron_lat = float(apron["latitude_deg"])
    apron_lon = float(apron["longitude_deg"])
    toward_apron = _bearing_deg(pad_lat, pad_lon, apron_lat, apron_lon)
    eye_lat, eye_lon = _dest_point(pad_lat, pad_lon, toward_apron, distance_m)
    eye_alt_ft = gnd_ft + clearance_ft + eye_agl_m / 0.3048
    look_hdg = _bearing_deg(eye_lat, eye_lon, pad_lat, pad_lon)
    pad_msl_ft = gnd_ft + clearance_ft + 2.0
    horiz_m = _haversine_m(eye_lat, eye_lon, pad_lat, pad_lon)
    pitch = float(apron.get("pitch_deg", -8.0))
    if not apron.get("use_fixed_heading_pitch", True) and horiz_m > 0.5:
        pitch = math.degrees(
            math.atan2((pad_msl_ft - eye_alt_ft) * 0.3048, horiz_m)
        )
    look_hdg = float(apron.get("heading_deg", look_hdg)) if apron.get("use_fixed_heading_pitch", True) else look_hdg
    return {
        "latitude_deg": eye_lat,
        "longitude_deg": eye_lon,
        "altitude_ft": eye_alt_ft,
        "heading_deg": look_hdg,
        "pitch_deg": pitch,
    }


def _compute_operator_aim(
    lat_deg: float,
    lon_deg: float,
    hdg_deg: float,
    gnd_ft: float,
    clearance_ft: float,
    eye: tuple[float, float, float],
    target: tuple[float, float, float],
) -> dict[str, float]:
    """Static world lookat eye at console, aimed at screen (lab +X fwd, +Y right, +Z up)."""
    base_ft = gnd_ft + clearance_ft
    eye_lat, eye_lon = _lab_offset_latlon(lat_deg, lon_deg, hdg_deg, eye[0], eye[1])
    tgt_lat, tgt_lon = _lab_offset_latlon(lat_deg, lon_deg, hdg_deg, target[0], target[1])
    eye_alt_ft = base_ft + eye[2] / 0.3048
    tgt_alt_ft = base_ft + target[2] / 0.3048
    horiz_m = _haversine_m(eye_lat, eye_lon, tgt_lat, tgt_lon)
    pitch = 0.0
    if horiz_m > 0.1:
        pitch = math.degrees(math.atan2((tgt_alt_ft - eye_alt_ft) * 0.3048, horiz_m))
    return {
        "latitude_deg": eye_lat,
        "longitude_deg": eye_lon,
        "altitude_ft": eye_alt_ft,
        "heading_deg": _bearing_deg(eye_lat, eye_lon, tgt_lat, tgt_lon),
        "pitch_deg": pitch,
        "roll_deg": 0.0,
    }


def _patch_jsbsim_template(raw: str, phys: Mapping[str, Any] | None) -> str:
    """Substitute @TOKENS@ from orbitron_physics_surrogate.yaml test_stand_fdm."""
    fdm: Mapping[str, Any] = {}
    if isinstance(phys, dict):
        block = phys.get("test_stand_fdm")
        if isinstance(block, dict):
            fdm = block
    tokens = {
        "EMPTYWT_LBF": fdm.get("empty_weight_lbf", 120000),
        "INERTIA_SLUGFT2": fdm.get("inertia_slug_ft2", 250000),
        "PAD_SPRING_LBSFT": fdm.get("pad_spring_lbs_ft", 250000),
        "PAD_DAMP_LBSFTSEC": fdm.get("pad_damping_lbs_ft_sec", 25000),
        "RATE_DAMP_LBFFT": -abs(
            float(fdm.get("angular_rate_damp_lbf_ft", 2500000))
        ),
        "THRUST_ARM_X_M": fdm.get("thrust_arm_x_m", 0.0),
        "THRUST_ARM_Y_M": fdm.get("thrust_arm_y_m", 0.0),
        "THRUST_ARM_Z_M": fdm.get("thrust_arm_z_m", 0.0),
    }
    for key, val in tokens.items():
        raw = raw.replace(f"@{key}@", str(val))
    return raw


def _emit_fdm_jsbsim_bootstrap(
    root: ET.Element,
    *,
    thrust: tuple[float, float, float, float],
    mdot: tuple[float, float, float, float],
    power: tuple[float, float, float, float],
    heat: tuple[float, float, float, float],
    beam: Mapping[str, Any],
    thrust_sled: Mapping[str, Any],
) -> None:
    """Declare /fdm/jsbsim/systems/orbitron/* before JSBSim reads them (Nasal mirrors sim state)."""
    root.append(
        ET.Comment(
            " JSBSim FCS inputs — must exist at FDM init (OrbitronOps.sync_fdm_inputs updates) "
        )
    )
    fdm = ET.SubElement(root, "fdm")
    jsb = ET.SubElement(fdm, "jsbsim")
    systems = ET.SubElement(jsb, "systems")
    orb = ET.SubElement(systems, "orbitron")
    _typed_prop(orb, "fg-pad-apu-online", 0.0)
    _typed_prop(orb, "fg-starter-engage", 0.0)
    _typed_prop(orb, "fg-bleed-air-open", 0.0)
    _typed_prop(orb, "fg-startup-armed", 0.0)
    _typed_prop(orb, "fg-throttle", 0.0)
    _typed_prop(orb, "fg-compressor", 0.0)
    _typed_prop(orb, "fg-cathode-pulse", 0.5)

    def bilinear(parent: ET.Element, prefix: str, c: tuple[float, float, float, float]) -> None:
        _typed_prop(parent, f"{prefix}-c0", c[0])
        _typed_prop(parent, f"{prefix}-ct", c[1])
        _typed_prop(parent, f"{prefix}-cc", c[2])
        _typed_prop(parent, f"{prefix}-ctc", c[3])

    sur = ET.SubElement(orb, "surrogate")
    bilinear(sur, "thrust", thrust)
    bilinear(sur, "mdot", mdot)
    bilinear(sur, "power", power)
    bilinear(sur, "heat", heat)
    _typed_prop(sur, "beam-screen-kw-c0", float(beam.get("c0", 0)))
    _typed_prop(sur, "beam-screen-kw-ct", float(beam.get("ct", 0)))
    _typed_prop(sur, "beam-screen-kw-cc", float(beam.get("cc", 0)))
    _typed_prop(sur, "beam-screen-kw-ctc", float(beam.get("ctc", 0)))

    sled = ET.SubElement(orb, "thrust-sled")
    _typed_prop(sled, "tare-lbf", float(thrust_sled.get("tare_lbf", 180.0)))
    _typed_prop(
        sled,
        "compressor-moment-gain",
        float(thrust_sled.get("compressor_moment_gain", 0.14)),
    )
    _typed_prop(
        sled,
        "throttle-moment-gain",
        float(thrust_sled.get("throttle_moment_gain", 0.07)),
    )


def _surrogate_corner(
    eng: Mapping[str, Any], key: str
) -> tuple[float, float, float, float]:
    """Bilinear placeholder: c0=ct=cc=0, ctc=scale from surrogate_engineering."""
    v = float(eng.get(key, 0.0))
    return (0.0, 0.0, 0.0, v)


def _build_set_xml(
    sim: Mapping[str, Any],
    physics_eng: Mapping[str, Any] | None,
    thrust_sled_load: Mapping[str, Any] | None = None,
) -> str:
    use_phys = bool(sim.get("surrogate_from_physics")) and physics_eng is not None
    beam = sim.get("surrogate_beam_screen_kw") or {}

    def corner(phys_key: str) -> tuple[float, float, float, float]:
        if use_phys and phys_key in physics_eng:
            return _surrogate_corner(physics_eng, phys_key)
        return (0.0, 0.0, 0.0, 0.0)

    thrust = corner("thrust_lbf_scale")
    mdot = corner("mass_flow_kgps_scale")
    power = corner("gross_power_mw_scale")
    heat = corner("heat_kw_scale")

    root = ET.Element("PropertyList")
    sim_el = ET.SubElement(root, "sim")
    _text(sim_el, "description", sim["description"])
    _text(sim_el, "author", sim["author"])
    _text(sim_el, "status", sim["status"])
    sim_el.append(ET.Comment(" Fixes the Version Warning "))
    _text(sim_el, "minimum-fg-version", sim["minimum_fg_version"])
    _text(sim_el, "flight-model", sim["flight_model"])
    _text(sim_el, "aero", sim["aero"])

    presets_cfg = sim.get("presets") or {}
    if isinstance(presets_cfg, dict) and presets_cfg:
        presets_el = ET.SubElement(sim_el, "presets")
        if "trim" in presets_cfg:
            _typed_prop(presets_el, "trim", bool(presets_cfg["trim"]), "bool")
        if presets_cfg.get("airport_id"):
            _text(presets_el, "airport-id", str(presets_cfg["airport_id"]))
        if presets_cfg.get("parkpos"):
            _text(presets_el, "parkpos", str(presets_cfg["parkpos"]))
        if "latitude_deg" in presets_cfg:
            _typed_prop(presets_el, "latitude-deg", float(presets_cfg["latitude_deg"]))
        if "longitude_deg" in presets_cfg:
            _typed_prop(presets_el, "longitude-deg", float(presets_cfg["longitude_deg"]))
        if "altitude_ft" in presets_cfg:
            _typed_prop(presets_el, "altitude-ft", float(presets_cfg["altitude_ft"]))
        if "heading_deg" in presets_cfg:
            _typed_prop(presets_el, "heading-deg", float(presets_cfg["heading_deg"]))
        if "onground" in presets_cfg:
            _typed_prop(presets_el, "onground", bool(presets_cfg["onground"]), "bool")

    sim_el.append(ET.Comment(" Pure relative paths for custom desktop directories "))
    model = ET.SubElement(sim_el, "model")
    _text(model, "path", sim["model_path"])
    model.append(ET.Comment(" Moved trigger here so it becomes /sim/model/reactor/startup-trigger "))
    r = ET.SubElement(model, "reactor")
    rf = sim["reactor_flags"]
    _typed_prop(r, "startup-trigger", bool(rf["startup_trigger"]), "bool")
    _typed_prop(r, "debug-ui-window", bool(rf["debug_ui_window"]), "bool")
    r.append(ET.Comment(" Set true briefly to fire reactor_audio_heavy.wav (optional one-shot). "))
    _typed_prop(r, "startup-commissioning-audio", bool(rf["startup_commissioning_audio"]), "bool")
    r.append(ET.Comment(" Pulse true briefly on arm to fire orbitron_pad_starter_crank.wav (Nasal). "))
    _typed_prop(
        r,
        "startup-starter-crank",
        bool(rf.get("startup_starter_crank", False)),
        "bool",
    )

    model.append(
        ET.Comment(
            " Bilinear coefficients read by orbitron-jsbsim.xml; Nasal may overwrite from engine_surrogate.json "
        )
    )
    orb = ET.SubElement(model, "orbitron")
    sur = ET.SubElement(orb, "surrogate")

    def add_bilinear(prefix: str, c: tuple[float, float, float, float]) -> None:
        _typed_prop(sur, f"{prefix}-c0", c[0])
        _typed_prop(sur, f"{prefix}-ct", c[1])
        _typed_prop(sur, f"{prefix}-cc", c[2])
        _typed_prop(sur, f"{prefix}-ctc", c[3])

    add_bilinear("thrust", thrust)
    add_bilinear("mdot", mdot)
    add_bilinear("power", power)
    add_bilinear("heat", heat)
    _typed_prop(sur, "beam-screen-kw-c0", float(beam.get("c0", 0)))
    _typed_prop(sur, "beam-screen-kw-ct", float(beam.get("ct", 0)))
    _typed_prop(sur, "beam-screen-kw-cc", float(beam.get("cc", 0)))
    _typed_prop(sur, "beam-screen-kw-ctc", float(beam.get("ctc", 0)))

    tsl = thrust_sled_load if thrust_sled_load is not None else {}
    model.append(
        ET.Comment(
            " Thrust-sled load-cell split coeffs (orbitron_physics_surrogate.yaml → JSBSim) "
        )
    )
    sled = ET.SubElement(orb, "thrust-sled")
    _typed_prop(sled, "tare-lbf", float(tsl.get("tare_lbf", 180.0)))
    _typed_prop(sled, "compressor-moment-gain", float(tsl.get("compressor_moment_gain", 0.14)))
    _typed_prop(sled, "throttle-moment-gain", float(tsl.get("throttle_moment_gain", 0.07)))

    ops = sim.get("orbitron_ops_flags") or {}
    model.append(
        ET.Comment(
            " Pad startup sequence (panel picks / keys 1–3); see orbitron_operator_console_spec.yaml "
        )
    )
    _typed_prop(orb, "pad-apu-online", bool(ops.get("pad_apu_online", False)), "bool")
    _typed_prop(orb, "starter-engage", bool(ops.get("starter_engage", False)), "bool")
    _typed_prop(orb, "bleed-air-open", bool(ops.get("bleed_air_open", False)), "bool")
    _typed_prop(orb, "spool-sfx-armed", bool(ops.get("spool_sfx_armed", False)), "bool")
    sfx = ET.SubElement(orb, "sfx")
    _typed_prop(sfx, "inlet-volume", 0.0)
    _typed_prop(sfx, "motor-volume", 0.0)
    _typed_prop(sfx, "nozzle-volume", 0.0)
    _typed_prop(ET.SubElement(orb, "vfx"), "nozzle-active", 0.0)

    carriers = sim.get("mp_carriers") or {}
    if isinstance(carriers, dict) and carriers:
        mc = ET.SubElement(sim_el, "mp-carriers")
        if "enabled" in carriers:
            _typed_prop(mc, "enabled", bool(carriers["enabled"]), "bool")
        if "auto_attach" in carriers:
            _typed_prop(mc, "auto-attach", bool(carriers["auto_attach"]), "bool")
        if "latch_always" in carriers:
            _typed_prop(mc, "latch-always", bool(carriers["latch_always"]), "bool")

    snd = sim["sound"]
    sound_el = ET.SubElement(sim_el, "sound")
    _text(sound_el, "path", snd["path"])
    sound_el.append(ET.Comment(" KILL AI & RADIO CHATTER "))
    _typed_prop(sound_el, "chatter-volume", float(snd["chatter_volume"]))
    _typed_prop(sound_el, "atc-volume", float(snd["atc_volume"]))
    _typed_prop(sound_el, "avionics-volume", float(snd["avionics_volume"]))

    def _append_lookfrom_view(parent: ET.Element, n: int, v: Mapping[str, Any]) -> None:
        view = ET.SubElement(parent, "view")
        view.set("n", str(n))
        _text(view, "name", v["name"])
        _text(view, "type", "lookfrom")
        _text(view, "internal", str(v.get("internal", False)).lower())
        cfg = ET.SubElement(view, "config")
        if v.get("from_model") and not v.get("property_paths"):
            _typed_prop(cfg, "from-model", 1, "int")
            ex = _typed_prop(cfg, "x-offset-m", float(v["x_offset_m"]))
            ex.set("archive", "n")
            ey = _typed_prop(cfg, "y-offset-m", float(v["y_offset_m"]))
            ey.set("archive", "n")
            ez = _typed_prop(cfg, "z-offset-m", float(v["z_offset_m"]))
            ez.set("archive", "n")
            if "pitch_offset_deg" in v:
                ep = _typed_prop(cfg, "pitch-offset-deg", float(v["pitch_offset_deg"]))
                ep.set("archive", "n")
            if "heading_offset_deg" in v:
                eh = _typed_prop(cfg, "heading-offset-deg", float(v["heading_offset_deg"]))
                eh.set("archive", "n")
            if v.get("limits_enabled") is False:
                limits = ET.SubElement(cfg, "limits")
                _typed_prop(limits, "enabled", False, "bool")
            if "ground_level_nearplane_m" in v:
                _typed_prop(
                    cfg,
                    "ground-level-nearplane-m",
                    float(v["ground_level_nearplane_m"]),
                )
        elif v.get("property_paths"):
            _typed_prop(cfg, "from-model", 0, "int")
            _typed_prop(cfg, "eye-fixed", True, "bool")
            base = "/sim/model/orbitron/operator-view"
            _text(cfg, "eye-lat-deg-path", f"{base}/latitude-deg")
            _text(cfg, "eye-lon-deg-path", f"{base}/longitude-deg")
            _text(cfg, "eye-alt-ft-path", f"{base}/altitude-ft")
            _text(cfg, "eye-heading-deg-path", f"{base}/heading-deg")
            _text(cfg, "eye-pitch-deg-path", f"{base}/pitch-deg")
            _text(cfg, "eye-roll-deg-path", f"{base}/roll-deg")
            _typed_prop(cfg, "ground-level-nearplane-m", 0.5)
        else:
            _typed_prop(cfg, "from-model", 0, "int")
            _typed_prop(cfg, "latitude-deg", float(v["latitude_deg"]))
            _typed_prop(cfg, "longitude-deg", float(v["longitude_deg"]))
            _typed_prop(cfg, "altitude-ft", float(v["altitude_ft"]))
            _typed_prop(cfg, "heading-deg", float(v.get("heading_deg", 0.0)))
            _typed_prop(cfg, "pitch-deg", float(v.get("pitch_deg", -10.0)))
            if "roll_deg" in v:
                _typed_prop(cfg, "roll-deg", float(v["roll_deg"]))
            _typed_prop(cfg, "ground-level-nearplane-m", float(v.get("ground_level_nearplane_m", 1.0)))
            if v.get("limits_enabled") is False:
                limits = ET.SubElement(cfg, "limits")
                _typed_prop(limits, "enabled", False, "bool")
        if "field_of_view_deg" in v:
            ef = _typed_prop(cfg, "field-of-view-deg", float(v["field_of_view_deg"]))
            ef.set("archive", "n")

    def _append_lookat_view(parent: ET.Element, n: int, v: Mapping[str, Any]) -> None:
        view = ET.SubElement(parent, "view")
        view.set("n", str(n))
        _text(view, "name", v["name"])
        _text(view, "type", v["type"])
        _text(view, "internal", str(v["internal"]).lower())
        cfg = ET.SubElement(view, "config")
        if v.get("world_eye"):
            _typed_prop(cfg, "from-model", 0, "int")
            _typed_prop(cfg, "at-model", 1 if v.get("at_model", True) else 0, "int")
            if v.get("property_paths"):
                _typed_prop(cfg, "eye-fixed", True, "bool")
                base = "/sim/model/orbitron/operator-view"
                _text(cfg, "eye-lat-deg-path", f"{base}/latitude-deg")
                _text(cfg, "eye-lon-deg-path", f"{base}/longitude-deg")
                _text(cfg, "eye-alt-ft-path", f"{base}/altitude-ft")
                _typed_prop(cfg, "ground-level-nearplane-m", 0.5)
                for key, tag in (
                    ("target_x_offset_m", "target-x-offset-m"),
                    ("target_y_offset_m", "target-y-offset-m"),
                    ("target_z_offset_m", "target-z-offset-m"),
                ):
                    if key in v:
                        el = _typed_prop(cfg, tag, float(v[key]))
                        el.set("archive", "n")
                if v.get("limits_enabled") is False:
                    limits = ET.SubElement(cfg, "limits")
                    _typed_prop(limits, "enabled", False, "bool")
            else:
                _typed_prop(cfg, "latitude-deg", float(v["latitude_deg"]))
                _typed_prop(cfg, "longitude-deg", float(v["longitude_deg"]))
                _typed_prop(cfg, "altitude-ft", float(v["altitude_ft"]))
                if "heading_deg" in v:
                    _typed_prop(cfg, "heading-deg", float(v["heading_deg"]))
                if "pitch_deg" in v:
                    _typed_prop(cfg, "pitch-deg", float(v["pitch_deg"]))
                if "roll_deg" in v:
                    _typed_prop(cfg, "roll-deg", float(v["roll_deg"]))
                if v.get("limits_enabled") is False:
                    limits = ET.SubElement(cfg, "limits")
                    _typed_prop(limits, "enabled", False, "bool")
        elif v.get("model_eye_world_target"):
            _typed_prop(cfg, "from-model", 1, "int")
            _typed_prop(cfg, "at-model", 0, "int")
            ex = _typed_prop(cfg, "x-offset-m", float(v["x_offset_m"]))
            ex.set("archive", "n")
            ey = _typed_prop(cfg, "y-offset-m", float(v["y_offset_m"]))
            ey.set("archive", "n")
            ez = _typed_prop(cfg, "z-offset-m", float(v["z_offset_m"]))
            ez.set("archive", "n")
            base = "/sim/model/orbitron/operator-view"
            _text(cfg, "target-lat-deg-path", f"{base}/target-latitude-deg")
            _text(cfg, "target-lon-deg-path", f"{base}/target-longitude-deg")
            _text(cfg, "target-alt-ft-path", f"{base}/target-altitude-ft")
            if v.get("limits_enabled") is False:
                limits = ET.SubElement(cfg, "limits")
                _typed_prop(limits, "enabled", False, "bool")
            if "ground_level_nearplane_m" in v:
                _typed_prop(
                    cfg, "ground-level-nearplane-m", float(v["ground_level_nearplane_m"])
                )
            if "field_of_view_deg" in v:
                ef = _typed_prop(cfg, "field-of-view-deg", float(v["field_of_view_deg"]))
                ef.set("archive", "n")
        elif v.get("chase"):
            _typed_prop(cfg, "from-model", 0, "int")
            _typed_prop(cfg, "platform", True, "bool")
            dm = _typed_prop(cfg, "distance-m", float(v.get("distance_m", 50.0)))
            dm.set("archive", "y")
            ho = _typed_prop(cfg, "height-offset", float(v.get("height_offset_m", 10.0)))
            ho.set("archive", "y")
            _typed_prop(cfg, "side-offset", 0.0)
            _typed_prop(cfg, "side-step", 0.0)
            tz = float(v.get("target_z_offset_m", 0.0))
            _typed_prop(cfg, "target-z-offset-m", tz)
            _typed_prop(cfg, "x-offset-m", 0.0)
            _typed_prop(cfg, "y-offset-m", 0.0)
            _typed_prop(cfg, "z-offset-m", 0.0)
        else:
            _typed_prop(cfg, "from-model", 1, "int")
            _typed_prop(cfg, "at-model", 1, "int")
            ex = _typed_prop(cfg, "x-offset-m", float(v["x_offset_m"]))
            ex.set("archive", "n")
            ey = _typed_prop(cfg, "y-offset-m", float(v["y_offset_m"]))
            ey.set("archive", "n")
            ez = _typed_prop(cfg, "z-offset-m", float(v["z_offset_m"]))
            ez.set("archive", "n")
            for key, tag in (
                ("target_x_offset_m", "target-x-offset-m"),
                ("target_y_offset_m", "target-y-offset-m"),
                ("target_z_offset_m", "target-z-offset-m"),
            ):
                if key in v:
                    el = _typed_prop(cfg, tag, float(v[key]))
                    el.set("archive", "n")
            if "pitch_offset_deg" in v:
                ep = _typed_prop(cfg, "pitch-offset-deg", float(v["pitch_offset_deg"]))
                ep.set("archive", "n")
            if "heading_offset_deg" in v:
                eh = _typed_prop(cfg, "heading-offset-deg", float(v["heading_offset_deg"]))
                eh.set("archive", "n")
            if v.get("platform"):
                _typed_prop(cfg, "platform", True, "bool")
            if v.get("limits_enabled") is False:
                limits = ET.SubElement(cfg, "limits")
                _typed_prop(limits, "enabled", False, "bool")
            if "ground_level_nearplane_m" in v:
                _typed_prop(
                    cfg,
                    "ground-level-nearplane-m",
                    float(v["ground_level_nearplane_m"]),
                )
        if "field_of_view_deg" in v and not v.get("model_eye_world_target"):
            ef = _typed_prop(cfg, "field-of-view-deg", float(v["field_of_view_deg"]))
            ef.set("archive", "n")

    apron_cfg = sim.get("view_bikf_apron") or {}
    vo_cfg = sim.get("view_operator") or {}
    operator_idx = int(vo_cfg.get("view_index", 2)) if isinstance(vo_cfg, dict) else 2
    apron_idx = int(apron_cfg.get("view_index", 3)) if isinstance(apron_cfg, dict) else 3
    pad_view = sim.get("view_pad_overview") or sim.get("view_chase")
    if pad_view:
        _append_lookat_view(sim_el, 1, pad_view)
    if (
        isinstance(vo_cfg, dict)
        and vo_cfg.get("lookfrom_world")
        and vo_cfg.get("eye_offset_m")
    ):
        eye = tuple(float(x) for x in vo_cfg["eye_offset_m"])
        aim_pt = tuple(
            float(x)
            for x in vo_cfg.get("aim_offset_m", vo_cfg.get("target_offset_m", [-1.4, -2.3, 1.25]))
        )
        plat_lat = float(presets_cfg.get("latitude_deg", 63.98187))
        plat_lon = float(presets_cfg.get("longitude_deg", -22.5884))
        plat_hdg = float(presets_cfg.get("heading_deg", 0.0))
        preset_alt = float(presets_cfg.get("altitude_ft", 158.0))
        clearance = float(vo_cfg.get("pad_clearance_ft", 1.5))
        gnd_ft = preset_alt - clearance
        aim = _compute_operator_aim(plat_lat, plat_lon, plat_hdg, gnd_ft, clearance, eye, aim_pt)
        console_lf: dict[str, Any] = {
            "name": vo_cfg["name"],
            "internal": vo_cfg.get("internal", False),
            "latitude_deg": aim["latitude_deg"],
            "longitude_deg": aim["longitude_deg"],
            "altitude_ft": aim["altitude_ft"],
            "heading_deg": aim["heading_deg"],
            "pitch_deg": aim["pitch_deg"],
            "roll_deg": aim.get("roll_deg", 0.0),
            "limits_enabled": vo_cfg.get("limits_enabled"),
            "ground_level_nearplane_m": vo_cfg.get("ground_level_nearplane_m", 0.25),
            "field_of_view_deg": vo_cfg.get("field_of_view_deg", 55.0),
        }
        _append_lookfrom_view(sim_el, operator_idx, console_lf)
    elif (
        isinstance(vo_cfg, dict)
        and vo_cfg.get("same_as_bikf_apron")
        and isinstance(apron_cfg, dict)
    ):
        baked_apron: dict[str, Any] = {
            "name": vo_cfg["name"],
            "type": "lookat",
            "internal": vo_cfg.get("internal", False),
            "world_eye": True,
            "at_model": True,
            "latitude_deg": float(apron_cfg["latitude_deg"]),
            "longitude_deg": float(apron_cfg["longitude_deg"]),
            "altitude_ft": float(apron_cfg["altitude_ft"]),
            "heading_deg": float(apron_cfg["heading_deg"]),
            "pitch_deg": float(apron_cfg["pitch_deg"]),
            "field_of_view_deg": float(
                vo_cfg.get("field_of_view_deg", apron_cfg.get("field_of_view_deg", 65.0))
            ),
        }
        _append_lookat_view(sim_el, operator_idx, baked_apron)
    elif (
        isinstance(vo_cfg, dict)
        and vo_cfg.get("type") == "lookfrom"
        and vo_cfg.get("from_model")
        and (
            vo_cfg.get("camera_offset_m")
            or vo_cfg.get("eye_offset_m")
            or vo_cfg.get("look_at_offset_m")
            or vo_cfg.get("aim_offset_m")
        )
    ):
        eye = tuple(
            float(x)
            for x in vo_cfg.get(
                "camera_offset_m",
                vo_cfg.get("eye_offset_m", [0.12, 0.5, 1.75]),
            )
        )
        aim_pt = tuple(
            float(x)
            for x in vo_cfg.get(
                "look_at_offset_m",
                vo_cfg.get(
                    "aim_offset_m",
                    vo_cfg.get("target_offset_m", [-1.4, 1.6, 4.5]),
                ),
            )
        )
        if vo_cfg.get("use_ac_view_offsets"):
            ex, ey, ez = _mesh_to_fg_body_view_offset(*eye)
            hdg, pit = _mesh_lookfrom_aim_angles_deg(eye, aim_pt)
        else:
            ex, ey, ez = _ac_to_fg_lookfrom_offset(*eye)
            hdg, pit = _ac_lookfrom_aim_angles_deg(eye, aim_pt)
        if vo_cfg.get("pitch_sign_invert"):
            pit = -pit
        lf_body: dict[str, Any] = {
            "name": vo_cfg["name"],
            "from_model": True,
            "x_offset_m": ex,
            "y_offset_m": ey,
            "z_offset_m": ez,
            "limits_enabled": vo_cfg.get("limits_enabled"),
            "ground_level_nearplane_m": vo_cfg.get("ground_level_nearplane_m", 0.05),
            "field_of_view_deg": vo_cfg.get("field_of_view_deg", 52.0),
            "heading_offset_deg": float(vo_cfg.get("heading_offset_deg", hdg)),
            "pitch_offset_deg": float(vo_cfg.get("pitch_offset_deg", pit)),
        }
        _append_lookfrom_view(sim_el, operator_idx, lf_body)
    elif (
        isinstance(vo_cfg, dict)
        and (
            vo_cfg.get("camera_offset_m")
            or vo_cfg.get("eye_offset_m")
            or vo_cfg.get("look_at_offset_m")
            or vo_cfg.get("aim_offset_m")
        )
        and vo_cfg.get("type", "lookat") != "lookfrom"
        and not vo_cfg.get("lookfrom")
        and not vo_cfg.get("world_eye")
        and not vo_cfg.get("sightline_from_apron")
    ):
        look = tuple(
            float(x)
            for x in vo_cfg.get(
                "look_at_offset_m",
                vo_cfg.get(
                    "aim_offset_m",
                    vo_cfg.get("target_offset_m", [-1.4, 1.6, 4.5]),
                ),
            )
        )
        if vo_cfg.get("eye_base_offset_m"):
            base = tuple(float(x) for x in vo_cfg["eye_base_offset_m"])
            back_ft = float(vo_cfg.get("eye_step_back_ft", 0))
            cam = _mesh_step_back_eye(base, look, back_ft) if back_ft > 0 else base
        else:
            cam = tuple(
                float(x)
                for x in vo_cfg.get(
                    "camera_offset_m",
                    vo_cfg.get("eye_offset_m", [-0.12, 0.5, 4.65]),
                )
            )
        if vo_cfg.get("use_fg_body_offsets") or vo_cfg.get("use_fg_view_offsets"):
            cx, cy, cz = cam
            lx, ly, lz = look
        elif vo_cfg.get("use_ac_lookat_direct"):
            cx, cy, cz = cam
            lx, ly, lz = look
        elif vo_cfg.get("use_ac_view_offsets"):
            cx, cy, cz = _ac_to_fg_body_view_offset(*cam)
            lx, ly, lz = _ac_to_fg_body_view_offset(*look)
        else:
            cx, cy, cz = _lab_to_fg_view_offset(*cam)
            lx, ly, lz = _lab_to_fg_view_offset(*look)
        if vo_cfg.get("lookat_fg_swap", False):
            ex, ey, ez = lx, ly, lz
            tx, ty, tz = cx, cy, cz
        else:
            ex, ey, ez = cx, cy, cz
            tx, ty, tz = lx, ly, lz
        body: dict[str, Any] = {
            "name": vo_cfg["name"],
            "type": "lookat",
            "internal": vo_cfg.get("internal", False),
            "x_offset_m": ex,
            "y_offset_m": ey,
            "z_offset_m": ez,
            "limits_enabled": vo_cfg.get("limits_enabled"),
            "ground_level_nearplane_m": vo_cfg.get("ground_level_nearplane_m", 0.25),
            "field_of_view_deg": vo_cfg.get("field_of_view_deg", 48.0),
        }
        if vo_cfg.get("aim_world"):
            body["model_eye_world_target"] = True
            body["aim_latitude_deg"] = float(vo_cfg["aim_latitude_deg"])
            body["aim_longitude_deg"] = float(vo_cfg["aim_longitude_deg"])
            body["aim_altitude_ft"] = float(vo_cfg.get("aim_altitude_ft", 162.0))
        else:
            body["target_x_offset_m"] = tx
            body["target_y_offset_m"] = ty
            body["target_z_offset_m"] = tz
        if "heading_offset_deg" in vo_cfg:
            body["heading_offset_deg"] = float(vo_cfg["heading_offset_deg"])
        if "pitch_offset_deg" in vo_cfg:
            body["pitch_offset_deg"] = float(vo_cfg["pitch_offset_deg"])
        _append_lookat_view(sim_el, operator_idx, body)
    elif (
        isinstance(vo_cfg, dict)
        and vo_cfg.get("sightline_from_apron")
        and isinstance(apron_cfg, dict)
    ):
        plat_lat = float(presets_cfg.get("latitude_deg", 63.98187))
        plat_lon = float(presets_cfg.get("longitude_deg", -22.5884))
        preset_alt = float(presets_cfg.get("altitude_ft", 158.0))
        clearance = float(vo_cfg.get("pad_clearance_ft", 1.5))
        gnd_ft = preset_alt - clearance
        aim = _compute_sightline_operator_view(
            plat_lat,
            plat_lon,
            apron_cfg,
            float(vo_cfg.get("sightline_distance_m", 14.0)),
            float(vo_cfg.get("eye_agl_m", 1.75)),
            gnd_ft,
            clearance,
        )
        baked_sight: dict[str, Any] = {
            "name": vo_cfg["name"],
            "type": "lookat",
            "internal": vo_cfg.get("internal", False),
            "world_eye": True,
            "at_model": vo_cfg.get("at_model", True),
            "latitude_deg": aim["latitude_deg"],
            "longitude_deg": aim["longitude_deg"],
            "altitude_ft": aim["altitude_ft"],
            "heading_deg": aim["heading_deg"],
            "pitch_deg": aim["pitch_deg"],
            "limits_enabled": vo_cfg.get("limits_enabled"),
            "field_of_view_deg": vo_cfg.get("field_of_view_deg", 48.0),
        }
        _append_lookat_view(sim_el, operator_idx, baked_sight)
    elif isinstance(vo_cfg, dict) and vo_cfg.get("world_eye") and vo_cfg.get("eye_offset_m"):
        eye = tuple(float(x) for x in vo_cfg["eye_offset_m"])
        aim_pt = tuple(
            float(x)
            for x in vo_cfg.get("aim_offset_m", vo_cfg.get("target_offset_m", [-1.4, -2.3, 1.25]))
        )
        plat_lat = float(presets_cfg.get("latitude_deg", 63.98187))
        plat_lon = float(presets_cfg.get("longitude_deg", -22.5884))
        plat_hdg = float(presets_cfg.get("heading_deg", 0.0))
        preset_alt = float(presets_cfg.get("altitude_ft", 158.0))
        clearance = float(vo_cfg.get("pad_clearance_ft", 1.5))
        gnd_ft = preset_alt - clearance
        aim = _compute_operator_aim(plat_lat, plat_lon, plat_hdg, gnd_ft, clearance, eye, aim_pt)
        baked: dict[str, Any] = {
            "name": vo_cfg["name"],
            "type": "lookat",
            "internal": vo_cfg.get("internal", False),
            "world_eye": True,
            "at_model": vo_cfg.get("at_model", False),
            "latitude_deg": aim["latitude_deg"],
            "longitude_deg": aim["longitude_deg"],
            "altitude_ft": aim["altitude_ft"],
            "heading_deg": aim["heading_deg"],
            "pitch_deg": aim["pitch_deg"],
            "limits_enabled": vo_cfg.get("limits_enabled"),
            "field_of_view_deg": vo_cfg.get("field_of_view_deg", 48.0),
        }
        _append_lookat_view(sim_el, operator_idx, baked)
    elif isinstance(vo_cfg, dict) and vo_cfg.get("lookfrom"):
        if vo_cfg.get("from_model"):
            _append_lookfrom_view(sim_el, operator_idx, vo_cfg)
        else:
            _append_lookfrom_view(sim_el, operator_idx, vo_cfg)
    else:
        _append_lookat_view(sim_el, operator_idx, vo_cfg)
    if isinstance(apron_cfg, dict) and not (
        isinstance(vo_cfg, dict) and vo_cfg.get("same_as_bikf_apron")
    ):
        _append_lookat_view(sim_el, apron_idx, apron_cfg)

    startup = sim.get("startup") or {}
    if isinstance(startup, dict) and "view_number" in startup:
        su = ET.SubElement(sim_el, "startup")
        _typed_prop(su, "view-number", int(startup["view_number"]), "int")

    root.append(
        ET.Comment(
            " ======================================================== "
        )
    )
    root.append(ET.Comment(" MUST BE OUTSIDE THE <sim> TAG SO JSBSIM CAN FIND IT!     "))
    root.append(
        ET.Comment(
            " ======================================================== "
        )
    )
    _emit_fdm_jsbsim_bootstrap(
        root,
        thrust=thrust,
        mdot=mdot,
        power=power,
        heat=heat,
        beam=beam,
        thrust_sled=tsl,
    )
    ctrls = ET.SubElement(root, "controls")
    cd = sim["controls_defaults"]
    rth = ET.SubElement(ctrls, "reactor")
    _typed_prop(rth, "throttle", float(cd["reactor_throttle"]))
    ob = ET.SubElement(ctrls, "orbitron")
    _typed_prop(ob, "compressor", float(cd["orbitron_compressor"]))
    if "orbitron_cathode_pulse" in cd:
        _typed_prop(ob, "cathode-pulse", float(cd["orbitron_cathode_pulse"]))

    root.append(ET.Comment(" CUSTOM KEYBOARD CONTROLS (Must be outside <sim>) "))
    kb_root = ET.SubElement(root, "input")
    kb = ET.SubElement(kb_root, "keyboard")
    for row in sim["keyboard"]:
        key_el = ET.SubElement(kb, "key")
        key_el.set("n", str(int(row["key_n"])))
        key_el.append(ET.Comment(f" {row['name']} (Key {row['key_n']}) : {row['desc']} "))
        _text(key_el, "name", row["name"])
        _text(key_el, "desc", row["desc"])
        b = ET.SubElement(key_el, "binding")
        if "toggle_property" in row:
            _text(b, "command", "property-toggle")
            _text(b, "property", row["toggle_property"])
        elif "assign_property" in row:
            _text(b, "command", "property-assign")
            _text(b, "property", row["assign_property"])
            val = row["assign_value"]
            v_el = ET.SubElement(b, "value")
            v_el.set("type", "int" if isinstance(val, int) else "double")
            v_el.text = f" {val} "
        elif "nasal_script" in row:
            _text(b, "command", "nasal")
            script = row["nasal_script"]
            if script.startswith("OrbitronOps."):
                script = "globals." + script
            _text(b, "script", script + "();")
        else:
            _text(b, "command", "property-adjust")
            _text(b, "property", row["adjust_property"])
            _text(b, "step", row["step"])
            _text(b, "min", row["min"])
            _text(b, "max", row["max"])

    nas = ET.SubElement(root, "nasal")
    for n in sim["nasal"]:
        el = ET.SubElement(nas, n["id"])
        _text(el, "file", n["file"])

    _indent(root, 0)
    root_el = root
    root_el.tail = "\n"
    return '<?xml version="1.0"?>\n' + ET.tostring(root_el, encoding="unicode")


def _install_panel_click_sounds(out_dir: Path, repo_root: Path) -> None:
    """Copy Shuttle panel click WAVs for knob/pick bindings in Models/Orbitron.xml."""
    dst = out_dir / "Sounds"
    dst.mkdir(parents=True, exist_ok=True)
    for wav in ("button_down.wav", "button_press1.wav"):
        src = repo_root / "Sounds" / wav
        if src.is_file():
            shutil.copy2(src, dst / wav)


def _install_vfx_assets(out_dir: Path, repo_root: Path, fg_model: Mapping[str, Any]) -> None:
    """Copy nozzle exhaust effect XML + textures into the aircraft package."""
    effects = fg_model.get("effect_models") or []
    if not effects:
        return
    dst_effects = out_dir / "Models" / "Effects"
    dst_effects.mkdir(parents=True, exist_ok=True)
    src_shared = repo_root / "Models" / "Effects"
    tmpl = repo_root / "tools" / "templates" / "orbitron_nozzle_exhaust.xml"
    if tmpl.is_file():
        shutil.copy2(tmpl, dst_effects / "orbitron_nozzle_exhaust.xml")
    missing: list[str] = []
    for tex in ("orbitron_nozzle_flame.png", "orbitron_nozzle_plume.png"):
        src = src_shared / tex
        if src.is_file():
            shutil.copy2(src, dst_effects / tex)
        else:
            missing.append(tex)
    if missing:
        print(
            "warning: missing VFX textures under Models/Effects/: "
            + ", ".join(missing)
            + " (run make to copy into the aircraft package)",
            file=sys.stderr,
        )


def _panel_click_binding(parent: ET.Element) -> None:
    """Shuttle-style avionics click (Sounds/button_press1.wav in aircraft package)."""
    b = ET.SubElement(parent, "binding")
    _text(b, "command", "nasal")
    _text(
        b,
        "script",
        "OrbitronOps.play_panel_click()",
    )


def _emit_panel_hotspot_highlight(root: ET.Element, object_names: list[str]) -> None:
    """Yellow emission on panel meshes when /sim/panel-hotspots is on (CTRL-C)."""
    if not object_names:
        return
    anim = ET.SubElement(root, "animation")
    _text(anim, "type", "material")
    for name in object_names:
        _text(anim, "object-name", name)
    em = ET.SubElement(anim, "emission")
    _text(em, "red", 1.0)
    _text(em, "green", 0.85)
    _text(em, "blue", 0.15)
    cond = ET.SubElement(anim, "condition")
    _text(cond, "property", "/sim/panel-hotspots")


def _ac3d_object_names(ac_path: Path) -> set[str]:
    """Object names from an AC3D export (top-level OBJECT poly names)."""
    if not ac_path.is_file():
        return set()
    names: set[str] = set()
    for line in ac_path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r'^\s*name\s+"(.+)"\s*$', line)
        if m:
            names.add(m.group(1))
    return names


def _emit_panel_pick_animation(root: ET.Element, spec: Mapping[str, Any]) -> None:
    """Pick hotspot for CTRL-C (/sim/panel-hotspots) and mouse clicks."""
    anim = ET.SubElement(root, "animation")
    _text(anim, "type", "pick")
    _text(anim, "object-name", spec["object_name"])
    _text(anim, "visible", True)
    act = ET.SubElement(anim, "action")
    _text(act, "button", 0)
    _text(act, "repeatable", "false")
    b = ET.SubElement(act, "binding")
    _text(b, "command", "property-toggle")
    _text(b, "property", spec["property"])
    _panel_click_binding(act)
    if spec.get("tooltip"):
        hov = ET.SubElement(anim, "hovered")
        hb = ET.SubElement(hov, "binding")
        _text(hb, "command", "set-tooltip")
        _text(hb, "tooltip-id", str(spec["object_name"]))
        _text(hb, "label", str(spec["tooltip"]))


def _is_shuttle_panel_mesh(name: str) -> bool:
    """Meshes in orbitron_panel_shuttle.ac (nested model)."""
    return (
        name.startswith("Panel_Switch_")
        or name.startswith("Panel_Lever_")
        or name.startswith("Panel_Guard_")
    )


def _shuttle_panel_knob_in_nested_xml(name: str) -> bool:
    """All panel knobs/guards — mesh is panel-local; nested model offsets place on console."""
    return _is_shuttle_panel_mesh(name)


def _emit_knob_animation(root: ET.Element, knob: Mapping[str, Any]) -> None:
    anim = ET.SubElement(root, "animation")
    _text(anim, "type", "knob")
    _text(anim, "object-name", knob["object_name"])
    _text(anim, "property", knob["property"])
    _text(anim, "factor", float(knob.get("factor", -45)))
    if "offset_deg" in knob:
        _text(anim, "offset-deg", float(knob["offset_deg"]))
    center = knob.get("center_m")
    if isinstance(center, (list, tuple)) and len(center) == 3:
        cen = ET.SubElement(anim, "center")
        _text(cen, "x-m", float(center[0]))
        _text(cen, "y-m", float(center[1]))
        _text(cen, "z-m", float(center[2]))
    axis = knob.get("axis") or [0, 1, 0]
    ax = ET.SubElement(anim, "axis")
    _text(ax, "x", float(axis[0]))
    _text(ax, "y", float(axis[1]))
    _text(ax, "z", float(axis[2]))
    act = ET.SubElement(anim, "action")
    is_analog = str(knob.get("property", "")).startswith("/controls/")
    _text(
        act,
        "repeatable",
        str(knob.get("repeatable", is_analog)).lower(),
    )
    b = ET.SubElement(act, "binding")
    _text(b, "command", "property-adjust")
    _text(b, "property", knob["property"])
    adj_factor = knob.get("drag_factor")
    if adj_factor is None:
        adj_factor = 0.04 if is_analog else 1
    _text(b, "factor", float(adj_factor))
    _text(b, "min", 0)
    _text(b, "max", 1)
    _text(b, "wrap", "false")
    _panel_click_binding(act)
    if knob.get("tooltip"):
        hov = ET.SubElement(anim, "hovered")
        hb = ET.SubElement(hov, "binding")
        _text(hb, "command", "set-tooltip")
        _text(hb, "tooltip-id", str(knob["object_name"]))
        _text(hb, "label", str(knob["tooltip"]))


def _emit_slider_animation(root: ET.Element, spec: Mapping[str, Any]) -> None:
    anim = ET.SubElement(root, "animation")
    _text(anim, "type", "slider")
    _text(anim, "object-name", spec["object_name"])
    for extra in spec.get("extra_object_names") or []:
        _text(anim, "object-name", str(extra))
    _text(anim, "property", spec["property"])
    axis = spec.get("axis") or [-1, 0, 0]
    ax = ET.SubElement(anim, "axis")
    _text(ax, "x", float(axis[0]))
    _text(ax, "y", float(axis[1]))
    _text(ax, "z", float(axis[2]))
    _text(anim, "factor", float(spec.get("factor", 0.002)))
    act = ET.SubElement(anim, "action")
    b = ET.SubElement(act, "binding")
    _text(b, "command", "property-toggle")
    _text(b, "property", spec["property"])
    _panel_click_binding(act)
    if spec.get("tooltip"):
        hov = ET.SubElement(anim, "hovered")
        hb = ET.SubElement(hov, "binding")
        _text(hb, "command", "set-tooltip")
        _text(hb, "tooltip-id", str(spec["object_name"]))
        _text(hb, "label", str(spec["tooltip"]))


def _emit_translate_animation(root: ET.Element, tr: Mapping[str, Any]) -> None:
    anim = ET.SubElement(root, "animation")
    _text(anim, "type", "translate")
    _text(anim, "object-name", tr["object_name"])
    _text(anim, "property", tr["property"])
    axis = tr.get("axis") or [0, 0, 1]
    ax = ET.SubElement(anim, "axis")
    _text(ax, "x", float(axis[0]))
    _text(ax, "y", float(axis[1]))
    _text(ax, "z", float(axis[2]))
    _text(anim, "factor", float(tr.get("factor", -0.012)))


def _merge_panel_animation_json(
    fg_model: Mapping[str, Any], models_dir: Path
) -> None:
    """Apply pivots/axis from build_orbitron_shuttle_panel_ac.py (must match mesh)."""
    path = models_dir / "orbitron_panel_anims.json"
    if not path.is_file():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return
    objects = data.get("objects")
    if not isinstance(objects, dict):
        return
    default_factor = float(data.get("knob_factor", -35))
    lever_factor = float(data.get("lever_factor", -36))
    lever_offset = float(data.get("lever_offset_deg", 0))
    knobs = fg_model.get("knob_animations")
    if not isinstance(knobs, list):
        return
    for knob in knobs:
        if not isinstance(knob, dict):
            continue
        name = str(knob.get("object_name", ""))
        block = objects.get(name)
        if not isinstance(block, dict):
            continue
        if "center_m" in block:
            knob["center_m"] = block["center_m"]
        if "axis" in block:
            knob["axis"] = block["axis"]
        if block.get("kind") == "lever":
            knob["kind"] = "lever"
        is_lever = name.startswith("Panel_Lever_") or block.get("kind") == "lever"
        if is_lever:
            if knob.get("sync_shuttle_factor", True):
                knob["factor"] = lever_factor
            if "offset_deg" not in knob:
                knob["offset_deg"] = lever_offset
        elif knob.get("sync_shuttle_factor", True):
            knob["factor"] = default_factor


def _xml_property_list(root: ET.Element) -> str:
    _indent(root, 0)
    return '<?xml version="1.0"?>\n' + ET.tostring(root, encoding="unicode")


def _collect_panel_hotspot_names(
    fg_model: Mapping[str, Any], *, include_ignite: bool = True
) -> list[str]:
    names: list[str] = [
        "Panel_Guard_APU",
        "Panel_Guard_Starter",
        "Panel_Guard_Bleed",
    ]
    if include_ignite:
        names.append("Big_Red_Button")
    for knob in fg_model.get("knob_animations") or []:
        if isinstance(knob, dict):
            oname = str(knob.get("object_name", ""))
            if _is_shuttle_panel_mesh(oname):
                names.append(oname)
    for spec in fg_model.get("slider_animations") or []:
        if isinstance(spec, dict):
            oname = str(spec.get("object_name", ""))
            if _is_shuttle_panel_mesh(oname):
                names.append(oname)
                for extra in spec.get("extra_object_names") or []:
                    if _is_shuttle_panel_mesh(str(extra)):
                        names.append(str(extra))
    for pick in fg_model.get("pick_animations") or []:
        if isinstance(pick, dict):
            oname = str(pick.get("object_name", ""))
            if _is_shuttle_panel_mesh(oname):
                names.append(oname)
    return names


def _build_shuttle_panel_model_xml(
    fg_model: Mapping[str, Any], hotspot_names: list[str] | None = None
) -> str:
    """Panel-local PropertyList — knob rotations use the nested model frame (Shuttle-style)."""
    root = ET.Element("PropertyList")
    root.append(
        ET.Comment(
            " Space Shuttle panel: animations must live here so rotate centers match "
            "orbitron_panel_shuttle.ac (see cockpit.xml L1-disp-dim knob). "
        )
    )
    _text(root, "path", "orbitron_panel_shuttle.ac")

    knobs = fg_model.get("knob_animations") or []
    if knobs:
        root.append(ET.Comment(" Panel knobs — rotate in place on drag "))
    for knob in knobs:
        if not isinstance(knob, dict):
            continue
        oname = str(knob.get("object_name", ""))
        if not _shuttle_panel_knob_in_nested_xml(oname):
            continue
        _emit_knob_animation(root, knob)
        _emit_panel_pick_animation(root, knob)

    if hotspot_names:
        shuttle_only = [n for n in hotspot_names if n != "Big_Red_Button"]
        if shuttle_only:
            root.append(
                ET.Comment(
                    " CTRL-C — highlight switches/guards/levers (must be in this XML) "
                )
            )
            _emit_panel_hotspot_highlight(root, shuttle_only)

    return _xml_property_list(root)


def _build_orbitron_model_xml(fg_model: Mapping[str, Any], models_dir: Path) -> str:
    root = ET.Element("PropertyList")
    root.append(ET.Comment(f" {fg_model['comment']} "))
    _text(root, "path", fg_model["ac_path"])
    off = ET.SubElement(root, "offsets")
    o = fg_model["offsets"]
    _text(off, "pitch-deg", o["pitch_deg"])
    _text(off, "roll-deg", o["roll_deg"])
    off.append(ET.Comment(" Rotates the rig to point forward "))
    _text(off, "heading-deg", o["heading_deg"])
    off.append(ET.Comment(" Pulls the long nose of the 3D model straight backward "))
    _text(off, "y-m", o["y_m"])
    _text(off, "z-m", o["z_m"])

    shuttle_panel = fg_model.get("shuttle_panel_model")
    use_nested_panel = (
        isinstance(shuttle_panel, dict) and bool(shuttle_panel.get("path"))
    )
    if use_nested_panel:
        root.append(
            ET.Comment(
                " Space Shuttle R1 guarded toggles (cont-bus-pwr-mn-a/b/c + R1-guards) "
            )
        )
        sp = ET.SubElement(root, "model")
        _text(sp, "path", shuttle_panel["path"])
        sp_off = shuttle_panel.get("offsets") or {}
        if sp_off:
            sp_ofs = ET.SubElement(sp, "offsets")
            if "x_m" in sp_off:
                _text(sp_ofs, "x-m", float(sp_off["x_m"]))
            if "y_m" in sp_off:
                _text(sp_ofs, "y-m", float(sp_off["y_m"]))
            if "z_m" in sp_off:
                _text(sp_ofs, "z-m", float(sp_off["z_m"]))

    knobs = fg_model.get("knob_animations") or []
    panel_knobs = [
        k
        for k in knobs
        if isinstance(k, dict) and _is_shuttle_panel_mesh(str(k.get("object_name", "")))
    ]
    if panel_knobs and not use_nested_panel:
        root.append(
            ET.Comment(
                " Panel controls merged into orbitron.ac — knob pivots use mesh coords "
            )
        )
        for knob in panel_knobs:
            _emit_knob_animation(root, knob)
            _emit_panel_pick_animation(root, knob)
        panel_hotspots = _collect_panel_hotspot_names(fg_model, include_ignite=False)
        if panel_hotspots:
            root.append(
                ET.Comment(
                    " CTRL-C — panel switches/guards/levers (meshes in orbitron.ac) "
                )
            )
            _emit_panel_hotspot_highlight(root, panel_hotspots)

    if fg_model.get("hide_cadquery_panel_labels"):
        ac_names = _ac3d_object_names(models_dir / fg_model.get("ac_path", "orbitron.ac"))
        hide_labels = (
            "Panel_Label_APU",
            "Panel_Label_STARTER",
            "Panel_Label_BLEED",
            "Panel_Label_IGNITE",
        )
        present = [lb for lb in hide_labels if lb in ac_names]
        if present:
            root.append(
                ET.Comment(" Hide CadQuery embossed labels when exported in orbitron.ac ")
            )
            for label in present:
                anim = ET.SubElement(root, "animation")
                _text(anim, "type", "material")
                _text(anim, "object-name", label)
                amb = ET.SubElement(anim, "ambient")
                _text(amb, "alpha", 0.0)
                diff = ET.SubElement(anim, "diffuse")
                _text(diff, "alpha", 0.0)
                em = ET.SubElement(anim, "emission")
                _text(em, "alpha", 0.0)

    for eff in fg_model.get("effect_models") or []:
        if not isinstance(eff, dict):
            continue
        m = ET.SubElement(root, "model")
        _text(m, "name", eff["name"])
        _text(m, "path", eff["path"])
        eo = eff.get("offsets") or {}
        eoff = ET.SubElement(m, "offsets")
        _text(eoff, "x-m", eo.get("x_m", 0.0))
        _text(eoff, "y-m", eo.get("y_m", 0.0))
        _text(eoff, "z-m", eo.get("z_m", 0.0))
        if "pitch_deg" in eo:
            _text(eoff, "pitch-deg", eo["pitch_deg"])
        if "heading_deg" in eo:
            _text(eoff, "heading-deg", eo["heading_deg"])

    for tr in fg_model.get("translate_animations") or []:
        if isinstance(tr, dict):
            _emit_translate_animation(root, tr)

    sliders = fg_model.get("slider_animations") or []
    if sliders:
        root.append(ET.Comment(" IGNITE pushbutton (CadQuery Big_Red_Button on orbitron.ac) "))
    for spec in sliders:
        if isinstance(spec, dict):
            _emit_slider_animation(root, spec)

    picks = fg_model.get("pick_animations") or []
    for i, pick in enumerate(picks):
        if not isinstance(pick, dict):
            continue
        if i == 0:
            root.append(ET.Comment(" IGNITE pick (click) "))
        anim = ET.SubElement(root, "animation")
        _text(anim, "type", "pick")
        _text(anim, "object-name", pick["object_name"])
        for extra in pick.get("extra_object_names") or []:
            _text(anim, "object-name", str(extra))
        _text(anim, "visible", True)
        act = ET.SubElement(anim, "action")
        _text(act, "button", int(pick["button"]))
        _text(act, "repeatable", str(pick.get("repeatable", False)).lower())
        b = ET.SubElement(act, "binding")
        _text(b, "command", "property-toggle")
        _text(b, "property", pick["toggle_property"])
        _panel_click_binding(act)
        if pick.get("tooltip"):
            hov = ET.SubElement(anim, "hovered")
            hb = ET.SubElement(hov, "binding")
            _text(hb, "command", "set-tooltip")
            _text(hb, "tooltip-id", str(pick["object_name"]))
            _text(hb, "label", str(pick["tooltip"]))

    root.append(ET.Comment(" IGNITE armed — brighten red cap "))
    brb_em = ET.SubElement(root, "animation")
    _text(brb_em, "type", "material")
    _text(brb_em, "object-name", "Big_Red_Button")
    em = ET.SubElement(brb_em, "emission")
    _text(em, "red", 0.45)
    _text(em, "green", 0.05)
    _text(em, "blue", 0.02)
    cond = ET.SubElement(brb_em, "condition")
    gt = ET.SubElement(cond, "greater-than")
    _text(gt, "property", "/sim/model/reactor/startup-trigger")
    _text(gt, "value", 0.5)

    root.append(ET.Comment(" CTRL-C — IGNITE on orbitron.ac (not nested shuttle panel) "))
    _emit_panel_hotspot_highlight(root, ["Big_Red_Button"])

    return _xml_property_list(root)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--aircraft-spec",
        type=Path,
        required=True,
        help="orbitron_aircraft_flightgear.yaml",
    )
    ap.add_argument(
        "--physics-spec",
        type=Path,
        default=None,
        help="orbitron_physics_surrogate.yaml (for surrogate_engineering scales)",
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        required=True,
        help="Aircraft/<aircraft.package_dir>/ directory (basename must match YAML)",
    )
    args = ap.parse_args()
    spec_path = args.aircraft_spec.resolve()
    if not spec_path.is_file():
        print(f"error: aircraft spec not found: {spec_path}", file=sys.stderr)
        return 1
    data = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        print("error: aircraft spec root must be a mapping", file=sys.stderr)
        return 1
    fg = data.get("fg_set")
    if not isinstance(fg, dict):
        print("error: missing fg_set", file=sys.stderr)
        return 1
    fg_model = data.get("fg_model_orbitron_xml")
    if not isinstance(fg_model, dict):
        print("error: missing fg_model_orbitron_xml", file=sys.stderr)
        return 1

    physics_eng: dict[str, Any] | None = None
    thrust_sled_load: dict[str, Any] | None = None
    physics_root: dict[str, Any] | None = None
    if args.physics_spec is not None:
        pp = args.physics_spec.resolve()
        if pp.is_file():
            phys = yaml.safe_load(pp.read_text(encoding="utf-8"))
            if isinstance(phys, dict):
                physics_root = phys
                se = phys.get("surrogate_engineering")
                if isinstance(se, dict):
                    physics_eng = se
                tsl = phys.get("thrust_sled_load_cells")
                if isinstance(tsl, dict):
                    thrust_sled_load = tsl

    out_dir = args.out_dir.resolve()
    ac = data.get("aircraft")
    if not isinstance(ac, dict):
        print("error: missing aircraft mapping", file=sys.stderr)
        return 1
    pkg = ac.get("package_dir")
    if not isinstance(pkg, str) or not pkg.strip():
        print("error: aircraft.package_dir must be a non-empty string", file=sys.stderr)
        return 1
    pkg = pkg.strip()
    if out_dir.name != pkg:
        print(
            f"error: --out-dir basename {out_dir.name!r} must equal "
            f"aircraft.package_dir {pkg!r}",
            file=sys.stderr,
        )
        return 1

    models = out_dir / "Models"
    models.mkdir(parents=True, exist_ok=True)
    repo_root = spec_path.parents[3]
    _install_vfx_assets(out_dir, repo_root, fg_model)
    _install_panel_click_sounds(out_dir, repo_root)
    _merge_panel_animation_json(fg_model, models)

    if fg_model.get("shuttle_panel_model"):
        shuttle_hotspots = _collect_panel_hotspot_names(fg_model, include_ignite=False)
        panel_xml = _build_shuttle_panel_model_xml(fg_model, shuttle_hotspots)
        (models / "orbitron_panel_shuttle.xml").write_text(panel_xml, encoding="utf-8")
        print("Wrote", models / "orbitron_panel_shuttle.xml")

    set_text = _build_set_xml(fg, physics_eng, thrust_sled_load)
    set_name = f"{pkg}-set.xml"
    (out_dir / set_name).write_text(set_text, encoding="utf-8")
    print("Wrote", out_dir / set_name)

    model_text = _build_orbitron_model_xml(fg_model, models)
    (models / "Orbitron.xml").write_text(model_text, encoding="utf-8")
    print("Wrote", models / "Orbitron.xml")

    jsb = data.get("jsbsim") or {}
    tmpl_name = str(jsb.get("template_file", "orbitron-jsbsim.xml"))
    tmpl = (repo_root / "tools" / "templates" / tmpl_name).resolve()
    if not tmpl.is_file():
        print(f"error: JSBSim template not found: {tmpl}", file=sys.stderr)
        return 1
    dst = out_dir / "orbitron-jsbsim.xml"
    raw = tmpl.read_text(encoding="utf-8")
    token = "@AIRCRAFT_PACKAGE_DIR@"
    if token not in raw:
        print(
            f"error: JSBSim template missing {token!r} placeholder: {tmpl}",
            file=sys.stderr,
        )
        return 1
    raw = raw.replace(token, pkg)
    raw = _patch_jsbsim_template(raw, physics_root)
    dst.write_text(raw, encoding="utf-8")
    print("Wrote", dst, "(from template)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
