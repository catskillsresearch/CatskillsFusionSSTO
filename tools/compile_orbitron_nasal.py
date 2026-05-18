#!/usr/bin/env python3
"""Emit Orbitron Nasal modules from orbitron_nasal.yaml under Aircraft/<pkg>/Nasal/."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

import yaml


def _nas_literal_string(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _coeffs_from_json_surface(surf: Any) -> tuple[float, float, float, float] | None:
    if not isinstance(surf, dict):
        return None
    t = surf.get("type")
    if t == "bilinear":
        c = surf.get("coeffs")
        if isinstance(c, dict):
            return (
                float(c.get("c0", 0)),
                float(c.get("c_t", 0)),
                float(c.get("c_c", 0)),
                float(c.get("c_tc", 0)),
            )
    if t in (None, "", "linear"):
        return (
            float(surf.get("intercept", 0)),
            float(surf.get("slope", 0)),
            0.0,
            0.0,
        )
    return None


def _surface_from_doc(
    doc: Mapping[str, Any],
    bil_key: str,
    linear_key: str | None,
) -> tuple[float, float, float, float] | None:
    surf = doc.get(bil_key)
    if surf is None and linear_key:
        surf = doc.get(linear_key)
    return _coeffs_from_json_surface(surf)


def _emit_surrogate_load(
    sl: Mapping[str, Any], surrogate_json: Path | None
) -> str:
    header = str(sl.get("header") or "").strip()
    root = str(sl["fg_surrogate_root"])
    delay = float(sl.get("init_delay_sec", 0))
    surfaces = sl.get("surfaces") or []
    beam = sl.get("beam_screen_optional") or {}

    doc: Mapping[str, Any] | None = None
    bake_source = "set.xml defaults (no engine_surrogate.json at compile time)"
    if surrogate_json is not None and surrogate_json.is_file():
        loaded = json.loads(surrogate_json.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            doc = loaded
            bake_source = surrogate_json.name

    lines: list[str] = []
    if header:
        for ln in header.splitlines():
            lines.append("# " + ln if ln.strip() else "#")
    else:
        lines.append("# (generated surrogate_load)")

    lines += [
        "",
        "var _set_surface = func(root, prefix, c0, ct, cc, ctc) {",
        '    setprop(root ~ "/" ~ prefix ~ "-c0", c0);',
        '    setprop(root ~ "/" ~ prefix ~ "-ct", ct);',
        '    setprop(root ~ "/" ~ prefix ~ "-cc", cc);',
        '    setprop(root ~ "/" ~ prefix ~ "-ctc", ctc);',
        "};",
        "",
        "var _load_once = func {",
        f'    var root = {_nas_literal_string(root)};',
    ]

    if doc is not None:
        for s in surfaces:
            if not isinstance(s, dict):
                continue
            pfx = str(s["fg_prefix"])
            bil = str(s["json_bilinear"])
            fb = s.get("json_linear_fallback")
            coeffs = _surface_from_doc(
                doc, bil, str(fb) if fb else None
            )
            if coeffs is None:
                continue
            c0, ct, cc, ctc = coeffs
            lines.append(
                f"    _set_surface(root, {_nas_literal_string(pfx)}, "
                f"{c0}, {ct}, {cc}, {ctc});"
            )
        if isinstance(beam, dict) and beam.get("json_bilinear") and beam.get(
            "fg_prefix"
        ):
            bil = str(beam["json_bilinear"])
            pfx = str(beam["fg_prefix"])
            coeffs = _coeffs_from_json_surface(doc.get(bil))
            if coeffs is not None:
                c0, ct, cc, ctc = coeffs
                lines.append(
                    f"    _set_surface(root, {_nas_literal_string(pfx)}, "
                    f"{c0}, {ct}, {cc}, {ctc});"
                )

    p0 = str(surfaces[0]["fg_prefix"]) if surfaces else "thrust"
    p1 = str(surfaces[1]["fg_prefix"]) if len(surfaces) > 1 else "mdot"
    beam_pfx = (
        str(beam["fg_prefix"])
        if isinstance(beam, dict) and beam.get("fg_prefix")
        else "beam-screen-kw"
    )
    lines += [
        f'    print("surrogate_load: applied baked coefficients ({bake_source})");',
        '    print("  thrust ctc=", getprop(root ~ "/' + p0 + '-ctc"),',
        '          " mdot ctc=", getprop(root ~ "/' + p1 + '-ctc"),',
        '          " beam-kw ctc=", getprop(root ~ "/' + beam_pfx + '-ctc"));',
        "};",
        "",
        f"settimer(func {{ _load_once(); }}, {delay});",
        "",
    ]
    return "\n".join(lines)


def _main_row_initial(row: Mapping[str, Any]) -> str:
    if row.get("hud_placeholder") is not None:
        return str(row["hud_placeholder"])
    k = row["kind"]
    if k == "bool_word":
        return str(row["prefix"]) + str(row["false_word"])
    if k == "static":
        return str(row["text"])
    if k == "scaled_float":
        return str(row["sprintf"]) % (0.0,)
    if k == "float":
        return str(row["sprintf"]) % (0.0,)
    if k == "sprintf2":
        return str(row["fmt"]) % (0.0, 0.0)
    raise ValueError(f"unknown main_rows kind {k!r}")


def _float_prop_var_map(
    main_rows: list[Any], dbg_rows: list[Any] | None = None
) -> dict[str, str]:
    """Property path → Nasal variable name used in update()."""
    m: dict[str, str] = {
        "/controls/orbitron/compressor": "comp",
        "/controls/orbitron/cathode-pulse": "cathode_pulse",
        "/fdm/jsbsim/systems/reactor/gross-power-mw": "power",
        "/fdm/jsbsim/systems/reactor/current-amps": "amps",
        "/fdm/jsbsim/systems/reactor/cathode-voltage-kv": "cathode_kv",
        "/fdm/jsbsim/systems/reactor/plasma-density-log10": "plasma_n",
        "/fdm/jsbsim/systems/arcjet/dec-voltage-mv": "decv",
        "/fdm/jsbsim/systems/reactor/heat-kw": "heat",
        "/fdm/jsbsim/systems/reactor/beam-screen-deposition-kw": "bkw",
        "/fdm/jsbsim/systems/reactor/beam-current-ma": "bma",
        "/fdm/jsbsim/systems/arcjet/thrust-lbf": "thrust",
        "/fdm/jsbsim/systems/arcjet/thrust-kn": "thrust_kn",
        "/fdm/jsbsim/systems/arcjet/equiv-exhaust-velocity-mps": "jet_ve",
        "/fdm/jsbsim/systems/arcjet/jet-kinetic-power-mw": "jet_p_mw",
        "/fdm/jsbsim/systems/arcjet/mass-flow-kgps": "mdot",
        "/fdm/jsbsim/systems/arcjet/sled-load-total-lbf": "sled_load",
        "/fdm/jsbsim/systems/arcjet/load-cell-0-lbf": "lc0",
        "/fdm/jsbsim/systems/arcjet/load-cell-1-lbf": "lc1",
        "/fdm/jsbsim/systems/arcjet/load-cell-2-lbf": "lc2",
        "/fdm/jsbsim/systems/arcjet/load-cell-3-lbf": "lc3",
        "/fdm/jsbsim/systems/reactor/q-factor": "q",
    }
    for rows in (main_rows, dbg_rows or []):
        for row in rows:
            if not isinstance(row, dict):
                continue
            if row.get("kind") == "float" and row.get("prop"):
                prop = str(row["prop"])
                if prop not in m:
                    m[prop] = str(row.get("id") or "v")
    return m


def _float_prop_var(prop: str, var_map: dict[str, str]) -> str:
    v = var_map.get(prop)
    if v is None:
        raise ValueError(f"no float var mapping for prop {prop!r}")
    return v


def _bool_prop_var(prop: str) -> str:
    """Nasal variable name for a bool_word row property (must exist in update())."""
    m = {
        "/sim/model/reactor/startup-trigger": "startup_on",
        "/sim/model/orbitron/pad-apu-online": "apu_on",
        "/sim/model/orbitron/starter-engage": "starter_on",
        "/sim/model/orbitron/bleed-air-open": "bleed_on",
    }
    v = m.get(prop)
    if v is None:
        raise ValueError(f"no bool_word var mapping for prop {prop!r}")
    return v


def _emit_update_main_line(row: Mapping[str, Any], float_vars: dict[str, str]) -> str:
    rid = str(row["id"])
    k = row["kind"]
    if k == "static":
        return f'        me.txt_{rid}.setText({_nas_literal_string(str(row["text"]))});'
    if k == "bool_word":
        p = str(row["prefix"])
        tw = str(row["true_word"])
        fw = str(row["false_word"])
        v = _bool_prop_var(str(row["prop"]))
        return (
            f'        me.txt_{rid}.setText({_nas_literal_string(p)} ~ '
            f'({v} ? {_nas_literal_string(tw)} : {_nas_literal_string(fw)}));'
        )
    if k == "scaled_float":
        fmt = str(row["sprintf"])
        return f'        me.txt_{rid}.setText(sprintf({_nas_literal_string(fmt)}, nbi_display));'
    if k == "float":
        fmt = str(row["sprintf"])
        v = _float_prop_var(str(row["prop"]), float_vars)
        return f'        me.txt_{rid}.setText(sprintf({_nas_literal_string(fmt)}, {v}));'
    if k == "sprintf2":
        fmt = str(row["fmt"])
        return f'        me.txt_{rid}.setText(sprintf({_nas_literal_string(fmt)}, bkw, bma));'
    raise ValueError(f"unknown main_rows kind {k!r}")


def _emit_update_debug_line(
    idx: int, row: Mapping[str, Any], float_vars: dict[str, str]
) -> str:
    k = row["kind"]
    if k == "bool_word":
        p = str(row["prefix"])
        tw = str(row["true_word"])
        fw = str(row["false_word"])
        return (
            f'            me.debug_txt[{idx}].setText({_nas_literal_string(p)} ~ '
            f'(startup_on ? {_nas_literal_string(tw)} : {_nas_literal_string(fw)}));'
        )
    if k == "scaled_float":
        fmt = str(row["sprintf"])
        return f'            me.debug_txt[{idx}].setText(sprintf({_nas_literal_string(fmt)}, nbi_display));'
    if k == "float":
        fmt = str(row["sprintf"])
        prop = str(row["prop"])
        return f'            me.debug_txt[{idx}].setText(sprintf({_nas_literal_string(fmt)}, {_float_prop_var(prop, float_vars)}));'
    raise ValueError(f"unknown debug_window.rows kind {k!r}")


def _emit_orbitron_ops(ops: Mapping[str, Any]) -> str:
    header = str(ops.get("header") or "").strip()
    hz = float(ops.get("timer_hz", 10))
    crank_prop = str(ops.get("crank_prop", "/sim/model/reactor/startup-starter-crank"))
    crank_reset = float(ops.get("crank_reset_sec", 0.18))
    props = ops.get("props") or {}
    pad_apu = str(props.get("pad_apu", "/sim/model/orbitron/pad-apu-online"))
    starter = str(props.get("starter", "/sim/model/orbitron/starter-engage"))
    bleed = str(props.get("bleed", "/sim/model/orbitron/bleed-air-open"))
    ignite = str(props.get("ignite", "/sim/model/reactor/startup-trigger"))
    repos = ops.get("startup_reposition") or {}
    stab = ops.get("pad_stabilize") or {}
    stab_hz = float(stab.get("hz", 120)) if isinstance(stab, dict) else 120.0
    pad_tol = float(repos.get("pad_tolerance_deg", 0.02)) if repos else 0.02
    pad_clearance_ft = float(repos.get("pad_clearance_ft", 15)) if repos else 15.0
    place_retry_sec = float(repos.get("place_retry_sec", 1.0)) if repos else 1.0
    place_retry_max = int(repos.get("place_retry_max", 30)) if repos else 30
    block_hijack = bool(ops.get("block_hijack_views", False))
    opview = ops.get("operator_view") or {}
    ov_eye = opview.get("eye", [1.6, 8.2, 4.5]) if isinstance(opview, dict) else [1.6, 8.2, 4.5]
    ov_tgt = opview.get("target", [1.6, 11.4, 4.5]) if isinstance(opview, dict) else [1.6, 11.4, 4.5]

    lines: list[str] = []
    if header:
        for ln in header.splitlines():
            lines.append("# " + ln if ln.strip() else "#")
    lines += [
        "",
        "var OrbitronOps = {",
        "    new: func() {",
        "        var m = { parents: [OrbitronOps] };",
        f"        m._last_starter = 0;",
        f"        m._last_ignite = 0;",
        "        OrbitronOps._pad_heading_deg = 0.0;",
        "        OrbitronOps._parked = 0;",
        "        OrbitronOps._placement_locked = 0;",
        "        OrbitronOps._teleport_done = 0;",
        "        OrbitronOps._finalize_tries = 0;",
    ]
    if repos:
        rlat = float(repos.get("latitude_deg", 63.98187))
        rlon = float(repos.get("longitude_deg", -22.5884))
        ralt = float(repos.get("altitude_ft", 561))
        rhdg = float(repos.get("heading_deg", 0))
        lines.append(
            f"        OrbitronOps._park = {{ lat: {rlat}, lon: {rlon}, alt: {ralt}, hdg: {rhdg} }};"
        )
        lines.append(f"        OrbitronOps._pad_clearance_ft = {pad_clearance_ft};")
    else:
        lines.append('        OrbitronOps._park = { lat: 0, lon: 0, alt: 0, hdg: 0 };')
    lines += [
        '        print("OrbitronOps: BIKF East-Apron-119 — placing at field elevation");',
        '        setprop("/sim/model/reactor/debug-ui-window", 0);',
        "        OrbitronOps.disable_carriers();",
        f"        m.timer = maketimer({1.0 / hz}, m, OrbitronOps.update);",
        "        m.timer.start();",
    ]
    if block_hijack:
        lines += [
            '        setlistener("/sim/current-view/name", func(n) {',
            '            var nm = n.getValue() or "";',
            '            if (find(nm, "Carrier") != -1 or find(nm, "carrier") != -1',
            '                or find(nm, "Nimitz") != -1 or find(nm, "Eisenhower") != -1) {',
            "                OrbitronOps.select_startup_view();",
            "            }",
            "        }, 1, 0);",
        ]
    operator_view_idx = int(ops.get("operator_view_index", ops.get("startup_view_number", 2)))
    view_n = ops.get("startup_view_number", operator_view_idx)
    if view_n is not None:
        lines.append(f'        setprop("/sim/current-view/view-number", {int(view_n)});')
    lines += [
        "        OrbitronOps._stab_timer = nil;",
        "        settimer(func() { OrbitronOps.log_position(); }, 8.0);",
    ]
    if stab:
        lines += [
            f"        OrbitronOps._stab_timer = maketimer({1.0 / stab_hz}, m, OrbitronOps.stabilize_pad);",
            "        OrbitronOps._stab_timer.start();",
            '        setlistener("/sim/signals/fdm-initialized", func {',
            "            if (OrbitronOps._placement_locked) return;",
            "            OrbitronOps._placement_locked = 1;",
            "            settimer(func() { OrbitronOps.finalize_pad_placement(); }, 0.15);",
            "        }, 1, 0);",
        ]
    lines += [
        "        return m;",
        "    },",
        "",
        "    disable_carriers: func() {",
        '        setprop("/sim/mp-carriers/enabled", 0);',
        '        setprop("/sim/mp-carriers/auto-attach", 0);',
        '        setprop("/sim/mp-carriers/latch-always", 0);',
        '        setprop("/sim/ai/enabled", 0);',
        '        setprop("/sim/ai/scenarios-enabled", 0);',
        '        setprop("/sim/ai/scenario", "");',
        "    },",
        "",
        "    far_from_pad: func() {",
        "        var p = OrbitronOps._park;",
        f"        var tol = {pad_tol};",
        "        var lat = getprop(\"/position/latitude-deg\");",
        "        var lon = getprop(\"/position/longitude-deg\");",
        "        if (lat == nil or lon == nil) return 1;",
        "        return (math.abs(lat - p.lat) > tol or math.abs(lon - p.lon) > tol);",
        "    },",
        "",
        "    is_null_island: func() {",
        "        var lat = getprop(\"/position/latitude-deg\");",
        "        var lon = getprop(\"/position/longitude-deg\");",
        "        if (lat == nil or lon == nil) return 0;",
        "        var p = OrbitronOps._park;",
        "        return (math.abs(lat) < 0.5 and math.abs(lon) < 0.5",
        "            and math.abs(lat - p.lat) > 1.0);",
        "    },",
        "",
        "    freeze_pad: func() {",
        '        setprop("/sim/freeze/latitude", 1);',
        '        setprop("/sim/freeze/longitude", 1);',
        '        setprop("/sim/freeze/altitude", 1);',
        '        setprop("/sim/freeze/attitude", 1);',
        '        setprop("/sim/freeze/roll", 1);',
        '        setprop("/sim/freeze/pitch", 1);',
        "    },",
        "",
        "    sync_fdm_to_pad: func() {",
        "        var p = OrbitronOps._park;",
        "        var gnd = getprop(\"/position/ground-elev-ft\") or 0;",
        "        var agl = OrbitronOps._pad_clearance_ft;",
        "        var msl = p.alt;",
        "        if (gnd > 50) msl = gnd + agl;",
        "        var hdg_rad = p.hdg * 0.017453292519943295;",
        '        setprop("/position/altitude-ft", msl);',
        '        setprop("/orientation/roll-deg", 0);',
        '        setprop("/orientation/pitch-deg", 0);',
        '        setprop("/orientation/heading-deg", p.hdg);',
        '        setprop("/fdm/jsbsim/position/lat-gc-deg", p.lat);',
        '        setprop("/fdm/jsbsim/position/long-gc-deg", p.lon);',
        '        setprop("/fdm/jsbsim/position/h-sl-ft", msl);',
        '        setprop("/fdm/jsbsim/position/h-agl-ft", agl);',
        '        setprop("/position/altitude-agl-ft", agl);',
        '        setprop("/fdm/jsbsim/attitude/phi-rad", 0);',
        '        setprop("/fdm/jsbsim/attitude/theta-rad", 0);',
        '        setprop("/fdm/jsbsim/attitude/psi-rad", hdg_rad);',
        "    },",
        "",
        "    apply_pad_props: func() {",
        "        var p = OrbitronOps._park;",
        '        setprop("/position/latitude-deg", p.lat);',
        '        setprop("/position/longitude-deg", p.lon);',
        "        OrbitronOps.sync_fdm_to_pad();",
        "        foreach (var axis; [\"u-fps\", \"v-fps\", \"w-fps\"]) {",
        '            var n = props.globals.getNode("/fdm/jsbsim/velocities/" ~ axis, 1);',
        "            if (n != nil) n.setDoubleValue(0);",
        "        }",
        "    },",
        "",
        "    teleport_to_pad_once: func() {",
        "        if (OrbitronOps._teleport_done) return;",
        "        if (!getprop(\"/sim/signals/fdm-initialized\")) return;",
        "        OrbitronOps._teleport_done = 1;",
        "        var p = OrbitronOps._park;",
        '        print("OrbitronOps: teleport_to_pad (once)");',
        '        aircraft.teleport("", "", p.lat, p.lon, p.alt, 0, 0, 0, 0, p.hdg);',
        "    },",
        "",
        "    finalize_pad_placement: func() {",
        "        if (OrbitronOps._parked) return;",
        "        if (!getprop(\"/sim/signals/fdm-initialized\")) return;",
        f"        if (OrbitronOps._finalize_tries >= {place_retry_max}) {{",
        '            print("OrbitronOps: finalize gave up — check fs.sh lat/lon/alt");',
        "            OrbitronOps.log_position();",
        "            return;",
        "        }",
        "        OrbitronOps._finalize_tries += 1;",
        "        var gnd = getprop(\"/position/ground-elev-ft\") or 0;",
        f"        if (gnd < 50 and OrbitronOps._finalize_tries < {min(place_retry_max, 12)}) {{",
        f"            settimer(func() {{ OrbitronOps.finalize_pad_placement(); }}, {place_retry_sec});",
        "            return;",
        "        }",
        "        OrbitronOps.apply_pad_props();",
        "        var p = OrbitronOps._park;",
        "        OrbitronOps._pad_heading_deg = p.hdg;",
        "        OrbitronOps.freeze_pad();",
        "        OrbitronOps._parked = 1;",
        f'        print("OrbitronOps: on pad OK — view {operator_view_idx} console (v); b=apron overview, p=pad orbit");',
        f'        setprop("/sim/current-view/view-number", {operator_view_idx});',
        "        OrbitronOps.log_position();",
        "    },",
        "",
        "    select_view_by_name: func(substr) {",
        "        var i = 0;",
        "        while (1) {",
        '            var nm = getprop("/sim/view[" ~ i ~ "]/name");',
        "            if (nm == nil) break;",
        "            if (nm == substr or find(nm, substr) != -1) {",
        '                setprop("/sim/current-view/view-number", i);',
        '                print("OrbitronOps: view -> ", nm, " (#", i, ")");',
        "                return 1;",
        "            }",
        "            i += 1;",
        "        }",
        "        return 0;",
        "    },",
        "",
        "    select_startup_view: func() {",
        f'        setprop("/sim/current-view/view-number", {operator_view_idx});',
        "    },",
        "",
        "    log_position: func() {",
        '        var lat = getprop("/position/latitude-deg");',
        '        var lon = getprop("/position/longitude-deg");',
        '        var alt = getprop("/position/altitude-ft");',
        '        var gnd = getprop("/position/ground-elev-ft");',
        '        var agl = getprop("/position/altitude-agl-ft");',
        '        var vn = getprop("/sim/current-view/name");',
        '        print(sprintf("OrbitronOps: lat=%.5f lon=%.5f alt=%.0f gnd=%.0f agl=%.1f view=%s",',
        "            lat or 0, lon or 0, alt or 0, gnd or 0, agl or 0, vn or \"?\"));",
        "    },",
        "",
        "",
        "    apply_position: func() {",
        "        OrbitronOps.apply_pad_props();",
        "    },",
        "",
        "    stabilize_pad: func() {",
        "        if (!getprop(\"/sim/signals/fdm-initialized\")) return;",
        "        if (!OrbitronOps._parked) {",
        "            var gnd = getprop(\"/position/ground-elev-ft\") or 0;",
        "            if (gnd < 50) return;",
        "        }",
    ]
    if stab:
        roll = float(stab.get("roll_deg", 0))
        pitch = float(stab.get("pitch_deg", 0))
        roll_rad = roll * 0.017453292519943295
        pitch_rad = pitch * 0.017453292519943295
        lines += [
            f"        var hdg = OrbitronOps._pad_heading_deg;",
            f"        var hdg_rad = hdg * 0.017453292519943295;",
            f"        setprop(\"/orientation/roll-deg\", {roll});",
            f"        setprop(\"/orientation/pitch-deg\", {pitch});",
            "        setprop(\"/orientation/heading-deg\", hdg);",
            f"        setprop(\"/fdm/jsbsim/attitude/phi-rad\", {roll_rad});",
            f"        setprop(\"/fdm/jsbsim/attitude/theta-rad\", {pitch_rad});",
            "        setprop(\"/fdm/jsbsim/attitude/psi-rad\", hdg_rad);",
            "        foreach (var axis; [\"p-rad_sec\", \"q-rad_sec\", \"r-rad_sec\"]) {",
            "            var n = props.globals.getNode(\"/fdm/jsbsim/velocities/\" ~ axis, 1);",
            "            if (n != nil) n.setDoubleValue(0);",
            "        }",
            "        foreach (var axis; [\"u-fps\", \"v-fps\", \"w-fps\"]) {",
            "            var n = props.globals.getNode(\"/fdm/jsbsim/velocities/\" ~ axis, 1);",
            "            if (n != nil) n.setDoubleValue(0);",
            "        }",
            "        foreach (var axis; [\"phidot-rad_sec\", \"thetadot-rad_sec\", \"psidot-rad_sec\"]) {",
            "            var n = props.globals.getNode(\"/fdm/jsbsim/velocities/\" ~ axis, 1);",
            "            if (n != nil) n.setDoubleValue(0);",
            "        }",
            "        foreach (var p; [\"/velocities/groundspeed-kt\", \"/velocities/speed-kt\",",
            "            \"/velocities/vertical-speed-fps\", \"/velocities/speed-down-fps\",",
            "            \"/velocities/uBody-fps\", \"/velocities/vBody-fps\", \"/velocities/wBody-fps\"]) {",
            "            setprop(p, 0);",
            "        }",
            "        if (OrbitronOps._parked) {",
            "            OrbitronOps.sync_fdm_to_pad();",
            '            var gc = props.globals.getNode("/gear/gear[0]/compression-norm", 1);',
            "            if (gc != nil) gc.setDoubleValue(0);",
            "        }",
        ]
    else:
        lines += [
            "        return;",
        ]
    lines += [
        "    },",
        "",
        "    update: func() {",
        f'        var apu = (getprop({_nas_literal_string(pad_apu)}) or 0) != 0;',
        f'        var starter = (getprop({_nas_literal_string(starter)}) or 0) != 0;',
        f'        var bleed = (getprop({_nas_literal_string(bleed)}) or 0) != 0;',
        f'        var ignite = (getprop({_nas_literal_string(ignite)}) or 0) != 0;',
        "",
        "        if (starter and apu and !me._last_starter) {",
        f"            setprop({_nas_literal_string(crank_prop)}, 1);",
        f"            settimer(func() {{ setprop({_nas_literal_string(crank_prop)}, 0); }}, {crank_reset});",
        "        }",
        "        me._last_starter = starter;",
        "",
        "        if (ignite and !bleed) {",
        '            setprop("/sim/model/reactor/startup-trigger", 0);',
        "            print(\"OrbitronOps: ignite blocked — open bleed air first (key 3 or panel).\");",
        "        }",
        "        if (starter and !apu) {",
        f"            setprop({_nas_literal_string(starter)}, 0);",
        "            print(\"OrbitronOps: starter blocked — pad APU must be online first (key 1).\");",
        "        }",
        "        me._last_ignite = ignite;",
        "    }",
        "};",
        "",
        "var orbitron_ops = OrbitronOps.new();",
        "",
    ]
    return "\n".join(lines)


def _emit_reactor_ui(ui: Mapping[str, Any]) -> str:
    cname = str(ui.get("class_name", "ReactorUI"))
    canvas = ui["canvas"]
    colors = ui["colors"]
    fonts = ui["fonts"]
    title = ui["title"]
    use_placement = bool(ui.get("use_screen_placement", True))
    startup_dialog = bool(ui.get("startup_open_debug_dialog", False))
    placement = ui.get("canvas_placement") or {}
    place_node = str(placement.get("node", "Screen")) if placement else "Screen"
    place_hz = float(placement.get("retry_hz", 2)) if placement else 2.0
    place_max = int(placement.get("max_attempts", 30)) if placement else 30
    place_dbg = bool(placement.get("open_debug_window_on_fail", True)) if placement else True
    timer_hz = float(ui.get("timer_hz", 10))
    main_rows = ui.get("main_rows") or []
    dbg = ui.get("debug_window") or {}
    dbg_rows = dbg.get("rows") or []
    cname_ = cname
    cv = canvas["name"]
    sz = canvas["size"]
    vw = canvas["view"]
    mm = canvas.get("mipmapping", 1)
    of = colors["outer_fill"]
    inn = colors["inner_fill"]
    hudc = colors["hud_text"]
    titc = colors["title"]
    f_title = fonts["title"]
    f_hud = fonts["hud"]
    f_dbg = fonts["debug"]
    title_text = str(title["text"])
    tx, ty = title["position"]
    dbg_title = str(dbg.get("title", ""))
    dsx, dsy = dbg.get("size", [460, 500])
    dbg_bg = dbg.get("background", [0.03, 0.03, 0.03, 0.90])
    y0 = int(dbg.get("line_start_y", 28))
    ystep = int(dbg.get("line_step", 38))
    lx = int(dbg.get("label_x", 16))

    lines: list[str] = [
        f"var {cname_} = {{",
        "    new: func() {",
        f"        var m = {{ parents: [{cname_}] }};",
        f"        m._dialog_only = {1 if not use_placement else 0};",
    ]
    if use_placement:
        lines += [
            "        m.canvas = canvas.new({",
            f'            "name": {_nas_literal_string(cv)},',
            f'            "size":[{int(sz[0])}, {int(sz[1])}],',
            f'            "view": [{int(vw[0])}, {int(vw[1])}],',
            f'            "mipmapping": {int(mm)}',
            "        });",
            "",
            f"        m._place_node = {_nas_literal_string(place_node)};",
            "        m._place_attempts = 0;",
            f"        m._place_max = {place_max};",
            f"        m._place_dbg = {1 if place_dbg else 0};",
            "        m.canvas.setColorBackground(0.06, 0.08, 0.12, 1.0);",
            '        m._placed = m.canvas.addPlacement({"node": m._place_node});',
            "        if (m._placed) {",
            f'            print("Orbitron: canvas bound to ", m._place_node, " (immediate)");',
            "        } else {",
            f"            m.place_timer = maketimer({1.0 / place_hz}, m, {cname_}.try_place_canvas);",
            "            m.place_timer.start();",
            f"            settimer(func() {{ {cname_}.try_place_canvas(); }}, 0.05);",
            "        }",
            "        m.root = m.canvas.createGroup();",
            '        m.root.createChild("path")',
            f"             .rect(0, 0, {int(sz[0])}, {int(sz[1])})",
            f"             .setColorFill({of[0]}, {of[1]}, {of[2]}, {of[3]});",
            '        m.root.createChild("path")',
            f"             .rect(20, 20, {int(sz[0]) - 40}, {int(sz[1]) - 40})",
            f"             .setColorFill({inn[0]}, {inn[1]}, {inn[2]}, {inn[3]});",
            "",
            '        m.root.createChild("text")',
            f"              .setText({_nas_literal_string(title_text)})",
            f'              .setFont({_nas_literal_string(str(f_title["path"]))})',
            f'              .setFontSize({int(f_title["size"])})',
            f"              .setColor({titc[0]}, {titc[1]}, {titc[2]})",
            '              .setAlignment("center-center")',
            f"              .setTranslation({int(tx)}, {int(ty)});",
            "",
        ]
        for row in main_rows:
            if not isinstance(row, dict):
                continue
            y = int(row["y"])
            init = _main_row_initial(row)
            rid = str(row["id"])
            lines.append(
                f'        m.txt_{rid} = m.create_text({y}, {_nas_literal_string(init)});'
            )
    else:
        lines += [
            '        print("Orbitron: Screen canvas off — press M for telemetry dialog");',
            '        setprop("/sim/model/reactor/debug-ui-window", 0);',
        ]
        if startup_dialog:
            lines += [
                '        setprop("/sim/model/reactor/debug-ui-window", 1);',
            ]

    lines += [
        "",
        "        m.debug_window = nil;",
        "        m.debug_root = nil;",
        "        m.debug_txt = [];",
        "",
        "",
        "        m.sync_debug_window();",
        "",
        f"        m.timer = maketimer({1.0 / timer_hz}, m, {cname_}.update);",
        "        m.timer.start();",
        "",
        "        return m;",
        "    },",
        "",
        "    try_place_canvas: func() {",
        "        if (me._dialog_only) return;",
        "        if (me._placed) return;",
        "        if (me._place_attempts >= me._place_max) {",
        '            print("Orbitron: canvas placement failed on ", me._place_node, " — opening debug HUD");',
        "            if (me._place_dbg) {",
        '                setprop("/sim/model/reactor/debug-ui-window", 1);',
        "            }",
        "            if (me.place_timer != nil) { me.place_timer.stop(); }",
        "            return;",
        "        }",
        "        me._place_attempts += 1;",
        '        var ok = me.canvas.addPlacement({"node": me._place_node});',
        "        if (ok) {",
        '            print("Orbitron: canvas bound to ", me._place_node);',
        "            me._placed = 1;",
        "            if (me.place_timer != nil) { me.place_timer.stop(); }",
        "        }",
        "    },",
        "",
        "    create_text: func(y, initial_text) {",
        '        return me.root.createChild("text")',
        "                     .setText(initial_text)",
        f'                     .setFont({_nas_literal_string(str(f_hud["path"]))})',
        f'                     .setFontSize({int(f_hud["size"])})',
        f"                     .setColor({hudc[0]}, {hudc[1]}, {hudc[2]})",
        '                     .setAlignment("center-center")',
        "                     .setTranslation(512, y);",
        "    },",
        "",
        "    sync_debug_window: func() {",
        '        var enabled = (getprop("/sim/model/reactor/debug-ui-window") or 0) != 0;',
        "        if (enabled) {",
        "            if (me.debug_window != nil) return;",
        "",
        f"            me.debug_window = canvas.Window.new([{int(dsx)}, {int(dsy)}], \"dialog\")",
        f'                .set("title", {_nas_literal_string(dbg_title)});',
        "            var dbg_canvas = me.debug_window.createCanvas()",
        f'                .set("background", [{dbg_bg[0]}, {dbg_bg[1]}, {dbg_bg[2]}, {dbg_bg[3]}]);',
        "            me.debug_root = dbg_canvas.createGroup();",
        "",
        "            me.debug_txt = [];",
        "            var labels = [",
    ]
    for i, dr in enumerate(dbg_rows):
        if not isinstance(dr, dict):
            continue
        lab = str(dr.get("label_static", ""))
        suf = "," if i + 1 < len(dbg_rows) else ""
        lines.append(f"                {_nas_literal_string(lab)}{suf}")
    lines += [
        "            ];",
        "            for (var i = 0; i < size(labels); i += 1) {",
        f"                var y = {y0} + i * {ystep};",
        "                append(me.debug_txt, me.debug_root.createChild(\"text\")",
        "                    .setText(labels[i])",
        f'                    .setFont({_nas_literal_string(str(f_dbg["path"]))})',
        f'                    .setFontSize({int(f_dbg["size"])}).setColor({hudc[0]}, {hudc[1]}, {hudc[2]})',
        '                    .setAlignment("left-center")',
        f"                    .setTranslation({lx}, y));",
        "            }",
        "            return;",
        "        }",
        "",
        "        if (me.debug_window != nil) {",
        "            call(canvas.Window.del, [], me.debug_window);",
        "            me.debug_window = nil;",
        "            me.debug_root = nil;",
        "            me.debug_txt = [];",
        "        }",
        "    },",
        "",
        "    update: func() {",
        "        me.sync_debug_window();",
        "",
    ]

    float_vars = _float_prop_var_map(main_rows, dbg_rows)

    lines += [
        '        var startup_on = (getprop("/sim/model/reactor/startup-trigger") or 0) != 0;',
        '        var apu_on = (getprop("/sim/model/orbitron/pad-apu-online") or 0) != 0;',
        '        var starter_on = (getprop("/sim/model/orbitron/starter-engage") or 0) != 0;',
        '        var bleed_on = (getprop("/sim/model/orbitron/bleed-air-open") or 0) != 0;',
        '        var nbi   = getprop("/controls/reactor/throttle") or 0.0;',
    ]
    for prop, var in sorted(float_vars.items(), key=lambda kv: kv[1]):
        lines.append(
            f"        var {var} = getprop({_nas_literal_string(prop)}) or 0.0;"
        )
    lines.append("")

    # nbi_display from yaml scale on the scaled_float row
    scale = 100.0
    for row in main_rows:
        if (
            isinstance(row, dict)
            and row.get("id") == "nbi"
            and row.get("kind") == "scaled_float"
        ):
            scale = float(row.get("scale", 100.0))
            break
    lines.append(f"        var nbi_display = nbi * {scale};")

    if use_placement:
        for row in main_rows:
            if isinstance(row, dict):
                lines.append(_emit_update_main_line(row, float_vars))
        lines.append("")

    n_dbg = len([r for r in dbg_rows if isinstance(r, dict)])
    lines += [
        f"        var n_dbg = size(me.debug_txt);",
        f"        if (n_dbg == {n_dbg}) {{",
    ]
    for i, dr in enumerate(dbg_rows):
        if isinstance(dr, dict):
            lines.append(_emit_update_debug_line(i, dr, float_vars))
    lines += [
        "        }",
        "    }",
        "};",
        "",
        f"var sys = {cname_}.new();",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--spec",
        type=Path,
        required=True,
        help="orbitron_nasal.yaml",
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        required=True,
        help="Aircraft/<package>/Nasal/ output directory",
    )
    ap.add_argument(
        "--surrogate-json",
        type=Path,
        default=None,
        help="engine_surrogate.json to bake into surrogate_load.nas (default: <parent of out-dir>/engine_surrogate.json)",
    )
    args = ap.parse_args()
    spec = args.spec.resolve()
    if not spec.is_file():
        print(f"error: spec not found: {spec}", file=sys.stderr)
        return 1
    data = yaml.safe_load(spec.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        print("error: spec root must be a mapping", file=sys.stderr)
        return 1
    sl = data.get("surrogate_load")
    ops = data.get("orbitron_ops")
    ui = data.get("reactor_ui")
    if not isinstance(sl, dict) or not isinstance(ops, dict) or not isinstance(ui, dict):
        print("error: missing surrogate_load, orbitron_ops, or reactor_ui mapping", file=sys.stderr)
        return 1

    out = args.out_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    json_path = args.surrogate_json
    if json_path is None:
        json_path = out.parent / "engine_surrogate.json"
    else:
        json_path = json_path.resolve()
    (out / "surrogate_load.nas").write_text(
        _emit_surrogate_load(sl, json_path), encoding="utf-8"
    )
    (out / "orbitron_ops.nas").write_text(_emit_orbitron_ops(ops), encoding="utf-8")
    (out / "reactor_ui.nas").write_text(_emit_reactor_ui(ui), encoding="utf-8")
    print("Wrote", out / "surrogate_load.nas")
    print("Wrote", out / "orbitron_ops.nas")
    print("Wrote", out / "reactor_ui.nas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
