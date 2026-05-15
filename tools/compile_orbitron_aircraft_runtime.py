#!/usr/bin/env python3
"""Emit <aircraft.package_dir>-set.xml, Models/Orbitron.xml, and orbitron-jsbsim.xml under Aircraft/.

YAML: ssto/orbitron/assembly_specs/orbitron_aircraft_flightgear.yaml
Physics (optional): surrogate_engineering corner scales → /sim/model/orbitron/surrogate/* bilinear ctc.
JSBSim: copy tools/templates/orbitron-jsbsim.xml (structure); full JSBSim-in-YAML is future work.
"""
from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Mapping

import yaml


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

    snd = sim["sound"]
    sound_el = ET.SubElement(sim_el, "sound")
    _text(sound_el, "path", snd["path"])
    sound_el.append(ET.Comment(" KILL AI & RADIO CHATTER "))
    _typed_prop(sound_el, "chatter-volume", float(snd["chatter_volume"]))
    _typed_prop(sound_el, "atc-volume", float(snd["atc_volume"]))
    _typed_prop(sound_el, "avionics-volume", float(snd["avionics_volume"]))

    v = sim["view_operator"]
    view = ET.SubElement(sim_el, "view")
    view.set("n", "0")
    _text(view, "name", v["name"])
    _text(view, "type", v["type"])
    _text(view, "internal", str(v["internal"]).lower())
    cfg = ET.SubElement(view, "config")
    ex = _typed_prop(cfg, "x-offset-m", float(v["x_offset_m"]))
    ex.set("archive", "n")
    ey = _typed_prop(cfg, "y-offset-m", float(v["y_offset_m"]))
    ey.set("archive", "n")
    ey.append(ET.Comment(" Operator eye-level height "))
    ez = _typed_prop(cfg, "z-offset-m", float(v["z_offset_m"]))
    ez.set("archive", "n")
    ez.append(ET.Comment(" Stand exactly 2 meters (~6.5 ft) back from the console "))
    ep = _typed_prop(cfg, "pitch-offset-deg", float(v["pitch_offset_deg"]))
    ep.set("archive", "n")
    ep.append(ET.Comment(" Angled down to look at the console "))

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
    ctrls = ET.SubElement(root, "controls")
    cd = sim["controls_defaults"]
    rth = ET.SubElement(ctrls, "reactor")
    _typed_prop(rth, "throttle", float(cd["reactor_throttle"]))
    ob = ET.SubElement(ctrls, "orbitron")
    _typed_prop(ob, "compressor", float(cd["orbitron_compressor"]))

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


def _build_orbitron_model_xml(fg_model: Mapping[str, Any]) -> str:
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

    for i, pick in enumerate(fg_model.get("pick_animations") or []):
        if i == 0:
            root.append(ET.Comment(" ANIMATION 1: Armed Big Red Button "))
        anim = ET.SubElement(root, "animation")
        _text(anim, "type", "pick")
        _text(anim, "object-name", pick["object_name"])
        act = ET.SubElement(anim, "action")
        _text(act, "button", int(pick["button"]))
        _text(act, "repeatable", str(pick.get("repeatable", False)).lower())
        b = ET.SubElement(act, "binding")
        _text(b, "command", "property-toggle")
        _text(b, "property", pick["toggle_property"])

    return '<?xml version="1.0"?>\n' + ET.tostring(root, encoding="unicode")


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
    if args.physics_spec is not None:
        pp = args.physics_spec.resolve()
        if pp.is_file():
            phys = yaml.safe_load(pp.read_text(encoding="utf-8"))
            if isinstance(phys, dict):
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

    set_text = _build_set_xml(fg, physics_eng, thrust_sled_load)
    set_name = f"{pkg}-set.xml"
    (out_dir / set_name).write_text(set_text, encoding="utf-8")
    print("Wrote", out_dir / set_name)

    model_text = _build_orbitron_model_xml(fg_model)
    (models / "Orbitron.xml").write_text(model_text, encoding="utf-8")
    print("Wrote", models / "Orbitron.xml")

    jsb = data.get("jsbsim") or {}
    tmpl_name = str(jsb.get("template_file", "orbitron-jsbsim.xml"))
    repo_root = spec_path.parents[3]
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
    dst.write_text(raw, encoding="utf-8")
    print("Wrote", dst, "(from template)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
