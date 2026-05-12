# Load engine_surrogate.json (from WarpX reduction) into /sim/model/orbitron/surrogate/*
# so orbitron-jsbsim.xml can read bilinear control-surface coefficients.
# Runs once at aircraft init.

var _num = func(s) {
    if (s == nil) return 0.0;
    var x = num(s);
    return x == nil ? 0.0 : x;
};

var _set_surface = func(root, prefix, c0, ct, cc, ctc) {
    setprop(root ~ "/" ~ prefix ~ "-c0", _num(c0));
    setprop(root ~ "/" ~ prefix ~ "-ct", _num(ct));
    setprop(root ~ "/" ~ prefix ~ "-cc", _num(cc));
    setprop(root ~ "/" ~ prefix ~ "-ctc", _num(ctc));
};

var _apply_surface = func(node, prefix, block) {
    if (typeof(block) != "hash") return;
    var t = block.type;
    if (t == "bilinear") {
        var c = block.coeffs;
        if (typeof(c) != "hash") return;
        _set_surface(node, prefix, c.c0, c.c_t, c.c_c, c.c_tc);
        return;
    }
    # Backward compatibility for old linear JSON:
    # y = intercept + slope*T  => c0=intercept, ct=slope, cc=0, ctc=0
    if (t == nil or t == "" or t == "linear") {
        _set_surface(node, prefix, block.intercept, block.slope, 0.0, 0.0);
    }
};

var _load_once = func {
    if (!contains(globals, "parsejson")) {
        print("surrogate_load: parsejson not available in this FG build; using set.xml defaults");
        return;
    }
    var root = "/sim/model/orbitron/surrogate";
    var dir = getprop("/sim/aircraft-dir");
    if (dir == nil) {
        print("surrogate_load: aircraft-dir still nil; using set.xml defaults");
        return;
    }
    var path = dir ~ "/engine_surrogate.json";
    var txt = io.readfile(path);
    if (txt == nil) {
        print("surrogate_load: no file ", path, " (using set.xml defaults)");
        return;
    }
    var j = parsejson(txt);
    if (j == nil or typeof(j) != "hash") {
        print("surrogate_load: parsejson failed for ", path);
        return;
    }
    # New multivariate surfaces
    _apply_surface(root, "thrust", j["thrust_lbf_surface"]);
    _apply_surface(root, "mdot", j["mass_flow_kgps_surface"]);
    _apply_surface(root, "power", j["gross_power_mw_surface"]);
    _apply_surface(root, "heat", j["heat_kw_surface"]);
    if (j["beam_screen_kw_surface"] != nil) {
        _apply_surface(root, "beam-screen-kw", j["beam_screen_kw_surface"]);
    }

    # Legacy fallback key names
    if (j["thrust_lbf_surface"] == nil) _apply_surface(root, "thrust", j["thrust_lbf_vs_throttle"]);
    if (j["mass_flow_kgps_surface"] == nil) _apply_surface(root, "mdot", j["mass_flow_kgps_vs_throttle"]);

    print("surrogate_load: applied ", path,
          " thrust ctc=", getprop(root ~ "/thrust-ctc"),
          " mdot ctc=", getprop(root ~ "/mdot-ctc"),
          " beam-kw ctc=", getprop(root ~ "/beam-screen-kw-ctc"));
};

var _load = func (attempt) {
    var dir = getprop("/sim/aircraft-dir");
    if (dir == nil and attempt < 24) {
        settimer(func { _load(attempt + 1); }, 0.05);
        return;
    }
    _load_once();
};

# Defer so aircraft-dir and property tree exist across FG versions.
settimer(func { _load(0); }, 0);
