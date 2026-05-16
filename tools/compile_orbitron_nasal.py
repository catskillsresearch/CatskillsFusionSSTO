#!/usr/bin/env python3
"""Emit Orbitron Nasal modules from orbitron_nasal.yaml under Aircraft/<pkg>/Nasal/."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Mapping

import yaml


def _nas_literal_string(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _emit_surrogate_load(sl: Mapping[str, Any]) -> str:
    header = str(sl.get("header") or "").strip()
    root = str(sl["fg_surrogate_root"])
    json_fn = str(sl["json_filename"])
    delay = float(sl.get("init_delay_sec", 0))
    probe = sl.get("aircraft_dir_probe") or {}
    max_attempts = int(probe.get("max_attempts", 24))
    interval = float(probe.get("interval_sec", 0.05))
    surfaces = sl.get("surfaces") or []
    beam = sl.get("beam_screen_optional") or {}

    lines: list[str] = []
    if header:
        for ln in header.splitlines():
            lines.append("# " + ln if ln.strip() else "#")
    else:
        lines.append("# (generated surrogate_load)")

    lines += [
        "",
        "var _num = func(s) {",
        "    if (s == nil) return 0.0;",
        "    var x = num(s);",
        "    return x == nil ? 0.0 : x;",
        "};",
        "",
        "var _set_surface = func(root, prefix, c0, ct, cc, ctc) {",
        '    setprop(root ~ "/" ~ prefix ~ "-c0", _num(c0));',
        '    setprop(root ~ "/" ~ prefix ~ "-ct", _num(ct));',
        '    setprop(root ~ "/" ~ prefix ~ "-cc", _num(cc));',
        '    setprop(root ~ "/" ~ prefix ~ "-ctc", _num(ctc));',
        "};",
        "",
        "var _apply_surface = func(node, prefix, block) {",
        '    if (typeof(block) != "hash") return;',
        "    var t = block.type;",
        '    if (t == "bilinear") {',
        "        var c = block.coeffs;",
        '        if (typeof(c) != "hash") return;',
        "        _set_surface(node, prefix, c.c0, c.c_t, c.c_c, c.c_tc);",
        "        return;",
        "    }",
        "    # Backward compatibility for old linear JSON:",
        "    # y = intercept + slope*T  => c0=intercept, ct=slope, cc=0, ctc=0",
        '    if (t == nil or t == "" or t == "linear") {',
        "        _set_surface(node, prefix, block.intercept, block.slope, 0.0, 0.0);",
        "    }",
        "};",
        "",
        "var _load_once = func {",
        '    if (!contains(globals, "parsejson")) {',
        '        print("surrogate_load: parsejson not available in this FG build; using set.xml defaults");',
        "        return;",
        "    }",
        f'    var root = {_nas_literal_string(root)};',
        '    var dir = getprop("/sim/aircraft-dir");',
        "    if (dir == nil) {",
        '        print("surrogate_load: aircraft-dir still nil; using set.xml defaults");',
        "        return;",
        "    }",
        f'    var path = dir ~ "/" ~ {_nas_literal_string(json_fn)};',
        "    var txt = io.readfile(path);",
        "    if (txt == nil) {",
        '        print("surrogate_load: no file ", path, " (using set.xml defaults)");',
        "        return;",
        "    }",
        "    var j = parsejson(txt);",
        '    if (j == nil or typeof(j) != "hash") {',
        '        print("surrogate_load: parsejson failed for ", path);',
        "        return;",
        "    }",
    ]

    for s in surfaces:
        if not isinstance(s, dict):
            continue
        pfx = str(s["fg_prefix"])
        bil = str(s["json_bilinear"])
        lines.append(
            f'    _apply_surface(root, {_nas_literal_string(pfx)}, j[{_nas_literal_string(bil)}]);'
        )

    if isinstance(beam, dict) and beam.get("json_bilinear") and beam.get("fg_prefix"):
        bil = str(beam["json_bilinear"])
        pfx = str(beam["fg_prefix"])
        lines += [
            f'    if (j[{_nas_literal_string(bil)}] != nil) {{',
            f'        _apply_surface(root, {_nas_literal_string(pfx)}, j[{_nas_literal_string(bil)}]);',
            "    }",
        ]

    lines.append("    # Legacy fallback key names")
    for s in surfaces:
        if not isinstance(s, dict):
            continue
        bil = s.get("json_bilinear")
        fb = s.get("json_linear_fallback")
        pfx = s.get("fg_prefix")
        if bil and fb and pfx:
            lines.append(
                f'    if (j[{_nas_literal_string(str(bil))}] == nil) '
                f'_apply_surface(root, {_nas_literal_string(str(pfx))}, '
                f'j[{_nas_literal_string(str(fb))}]);'
            )

    p0 = str(surfaces[0]["fg_prefix"]) if surfaces else "thrust"
    p1 = str(surfaces[1]["fg_prefix"]) if len(surfaces) > 1 else "mdot"
    beam_pfx = (
        str(beam["fg_prefix"])
        if isinstance(beam, dict) and beam.get("fg_prefix")
        else "beam-screen-kw"
    )
    lines += [
        '    print("surrogate_load: applied ", path,',
        f'          " thrust ctc=", getprop(root ~ "/{p0}-ctc"),',
        f'          " mdot ctc=", getprop(root ~ "/{p1}-ctc"),',
        f'          " beam-kw ctc=", getprop(root ~ "/{beam_pfx}-ctc"));',
        "};",
        "",
        "var _load = func (attempt) {",
        '    var dir = getprop("/sim/aircraft-dir");',
        f"    if (dir == nil and attempt < {max_attempts}) {{",
        f"        settimer(func {{ _load(attempt + 1); }}, {interval});",
        "        return;",
        "    }",
        "    _load_once();",
        "};",
        "",
        "# Defer so aircraft-dir and property tree exist across FG versions.",
        f"settimer(func {{ _load(0); }}, {delay});",
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


def _emit_update_main_line(row: Mapping[str, Any]) -> str:
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
        return f'        me.txt_{rid}.setText(sprintf({_nas_literal_string(fmt)}, {rid}));'
    if k == "sprintf2":
        fmt = str(row["fmt"])
        return f'        me.txt_{rid}.setText(sprintf({_nas_literal_string(fmt)}, bkw, bma));'
    raise ValueError(f"unknown main_rows kind {k!r}")


def _emit_update_debug_line(idx: int, row: Mapping[str, Any]) -> str:
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
        # Map debug row prop to variable name used in update() — same as original hardcoded set.
        prop = str(row["prop"])
        var_map = {
            "/controls/orbitron/compressor": "comp",
            "/controls/orbitron/cathode-pulse": "cathode_pulse",
            "/fdm/jsbsim/systems/reactor/gross-power-mw": "power",
            "/fdm/jsbsim/systems/reactor/current-amps": "amps",
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
        v = var_map.get(prop)
        if v is None:
            raise ValueError(f"no debug var mapping for prop {prop!r}")
        return f'            me.debug_txt[{idx}].setText(sprintf({_nas_literal_string(fmt)}, {v}));'
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
        f"        m.timer = maketimer({1.0 / hz}, m, OrbitronOps.update);",
        "        m.timer.start();",
        "        return m;",
        "    },",
        "",
        "    update: func() {",
        f'        var apu = (getprop({_nas_literal_string(pad_apu)}) or 0) != 0;',
        f'        var starter = (getprop({_nas_literal_string(starter)}) or 0) != 0;',
        f'        var bleed = (getprop({_nas_literal_string(bleed)}) or 0) != 0;',
        f'        var ignite = (getprop({_nas_literal_string(ignite)}) or 0) != 0;',
        "",
        "        if (starter and apu and !m._last_starter) {",
        f"            setprop({_nas_literal_string(crank_prop)}, 1);",
        f"            settimer(func() {{ setprop({_nas_literal_string(crank_prop)}, 0); }}, {crank_reset});",
        "        }",
        "        m._last_starter = starter;",
        "",
        "        if (ignite and !bleed) {",
        '            setprop("/sim/model/reactor/startup-trigger", 0);',
        "            print(\"OrbitronOps: ignite blocked — open bleed air first (key 3 or panel).\");",
        "        }",
        "        if (starter and !apu) {",
        f"            setprop({_nas_literal_string(starter)}, 0);",
        "            print(\"OrbitronOps: starter blocked — pad APU must be online first (key 1).\");",
        "        }",
        "        m._last_ignite = ignite;",
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
    probes = ui.get("probe_nodes") or []
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
        "        m.canvas = canvas.new({",
        f'            "name": {_nas_literal_string(cv)},',
        f'            "size":[{int(sz[0])}, {int(sz[1])}],',
        f'            "view": [{int(vw[0])}, {int(vw[1])}],',
        f'            "mipmapping": {int(mm)}',
        "        });",
        "",
        "        # Placement probe: bind to likely runtime node names to discover",
        "        # which scene-graph nodes are canvas-capable in this model.",
        "        var probe_nodes = [",
    ]
    for i, pn in enumerate(probes):
        suf = "," if i + 1 < len(probes) else ""
        lines.append(f'            {_nas_literal_string(str(pn))}{suf}')
    lines += [
        "        ];",
        "        foreach (var node_name; probe_nodes) {",
        '            var placed = m.canvas.addPlacement({"node": node_name});',
        '            print("Orbitron canvas placement probe node=", node_name, " result=", placed);',
        "        }",
        "",
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

    # Variable reads (same set as original reactor_ui.nas)
    lines += [
        '        var startup_on = (getprop("/sim/model/reactor/startup-trigger") or 0) != 0;',
        '        var apu_on = (getprop("/sim/model/orbitron/pad-apu-online") or 0) != 0;',
        '        var starter_on = (getprop("/sim/model/orbitron/starter-engage") or 0) != 0;',
        '        var bleed_on = (getprop("/sim/model/orbitron/bleed-air-open") or 0) != 0;',
        '        var nbi   = getprop("/controls/reactor/throttle") or 0.0;',
        '        var comp  = getprop("/controls/orbitron/compressor") or 0.0;',
        '        var cathode_pulse = getprop("/controls/orbitron/cathode-pulse") or 0.0;',
        '        var power = getprop("/fdm/jsbsim/systems/reactor/gross-power-mw") or 0.0;',
        '        var amps  = getprop("/fdm/jsbsim/systems/reactor/current-amps") or 0.0;',
        '        var heat  = getprop("/fdm/jsbsim/systems/reactor/heat-kw") or 0.0;',
        '        var q     = getprop("/fdm/jsbsim/systems/reactor/q-factor") or 0.0;',
        '        var decv  = getprop("/fdm/jsbsim/systems/arcjet/dec-voltage-mv") or 0.0;',
        '        var thrust = getprop("/fdm/jsbsim/systems/arcjet/thrust-lbf") or 0.0;',
        '        var thrust_kn = getprop("/fdm/jsbsim/systems/arcjet/thrust-kn") or 0.0;',
        '        var jet_ve = getprop("/fdm/jsbsim/systems/arcjet/equiv-exhaust-velocity-mps") or 0.0;',
        '        var jet_p_mw = getprop("/fdm/jsbsim/systems/arcjet/jet-kinetic-power-mw") or 0.0;',
        '        var mdot  = getprop("/fdm/jsbsim/systems/arcjet/mass-flow-kgps") or 0.0;',
        '        var sled_load = getprop("/fdm/jsbsim/systems/arcjet/sled-load-total-lbf") or 0.0;',
        '        var lc0 = getprop("/fdm/jsbsim/systems/arcjet/load-cell-0-lbf") or 0.0;',
        '        var lc1 = getprop("/fdm/jsbsim/systems/arcjet/load-cell-1-lbf") or 0.0;',
        '        var lc2 = getprop("/fdm/jsbsim/systems/arcjet/load-cell-2-lbf") or 0.0;',
        '        var lc3 = getprop("/fdm/jsbsim/systems/arcjet/load-cell-3-lbf") or 0.0;',
        '        var bkw   = getprop("/fdm/jsbsim/systems/reactor/beam-screen-deposition-kw") or 0.0;',
        '        var bma   = getprop("/fdm/jsbsim/systems/reactor/beam-current-ma") or 0.0;',
        "",
    ]

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

    for row in main_rows:
        if isinstance(row, dict):
            lines.append(_emit_update_main_line(row))

    lines.append("")
    n_dbg = len([r for r in dbg_rows if isinstance(r, dict)])
    lines += [
        f"        var n_dbg = size(me.debug_txt);",
        f"        if (n_dbg == {n_dbg}) {{",
    ]
    for i, dr in enumerate(dbg_rows):
        if isinstance(dr, dict):
            lines.append(_emit_update_debug_line(i, dr))
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
    (out / "surrogate_load.nas").write_text(_emit_surrogate_load(sl), encoding="utf-8")
    (out / "orbitron_ops.nas").write_text(_emit_orbitron_ops(ops), encoding="utf-8")
    (out / "reactor_ui.nas").write_text(_emit_reactor_ui(ui), encoding="utf-8")
    print("Wrote", out / "surrogate_load.nas")
    print("Wrote", out / "orbitron_ops.nas")
    print("Wrote", out / "reactor_ui.nas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
