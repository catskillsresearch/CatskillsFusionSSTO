# CATSKILLS-SSTO-TA-GRENADIER operator model
# Property bus + mode machine + panel aliases + stage gates.
# Coupled JSBSim thrust comes later; this layer is the ops SSOT for screens/checklists.

var G = "/fdm/jsbsim/systems/grenadier/";
var C = G ~ "charm/";
var E = G ~ "engine/";
var S = "/sim/model/grenadier/";

var MODE = ["OFF", "CRYO", "ARM", "LIGHT", "POWER", "SCRAM"];

var _init_done = 0;

var _num = func (p, d) {
    var v = getprop(p);
    if (v == nil) return d;
    return v;
};

var _set = func (p, v) { setprop(p, v); };

var init_defaults = func {
    if (_init_done) return;
    _init_done = 1;

    _set(S ~ "enabled", 1);
    _set(S ~ "aircraft-id", "CATSKILLS-SSTO-TA-GRENADIER");

    _set(C ~ "mode", "OFF");
    _set(C ~ "mode-index", 0);
    _set(C ~ "fuel-b11-kg", 120.0);
    _set(C ~ "fuel-proton-kg", 40.0);
    _set(C ~ "battery-kwh", 500.0);
    _set(C ~ "battery-min-kwh", 300.0);
    _set(C ~ "battery-online", 0);
    _set(C ~ "ground-cart", 0);
    _set(C ~ "startup-source", "CART");
    _set(C ~ "cart-tied", 0);
    _set(C ~ "cryo-enable", 0);
    _set(C ~ "cryo-kw", 0.0);
    _set(C ~ "magnet-arm", 0);
    _set(C ~ "magnet-i-frac", 0.0);
    _set(C ~ "magnet-t-k", 80.0);
    _set(C ~ "fuel-enable", 0);
    _set(C ~ "fuel-ready", 0);
    _set(C ~ "vacuum-ready", 0);
    _set(C ~ "rf-enable", 0);
    _set(C ~ "light-cmd", 0);
    _set(C ~ "plasma-proxy", 0.0);
    _set(C ~ "dec-online", 0);
    _set(C ~ "bus-mw", 0.0);
    _set(C ~ "recirc-mw", 0.0);
    _set(C ~ "aux-bus-v", 0.0);
    _set(C ~ "scram", 0);
    _set(C ~ "go-fuel", 0);
    _set(C ~ "go-cryo", 0);
    _set(C ~ "go-magnet", 0);
    _set(C ~ "go-bus", 0);

    _set(E ~ "sigma", 1);
    _set(E ~ "sigma-recommended", 1);
    _set(E ~ "sigma-allowed", 1);
    _set(E ~ "sigma2-alt-ft", 25000.0);
    _set(E ~ "sigma3-alt-ft", 120000.0);
    _set(E ~ "inlet-sealed", 0);
    _set(E ~ "throttle", 0.0);
    _set(E ~ "thrust-kn", 0.0);
    _set(E ~ "power-draw-mw", 0.0);
    _set(E ~ "water-kg", 44000.0);
    _set(E ~ "water-flow-kgps", 0.0);
    _set(E ~ "alt-ft", 0.0);
    _set(E ~ "q-psf", 0.0);
    _set(E ~ "stage-go", 0);
    _set(E ~ "plant-ok", 0);
};

var _set_mode = func (name) {
    var idx = 0;
    for (var i = 0; i < size(MODE); i += 1) {
        if (MODE[i] == name) { idx = i; break; }
    }
    _set(C ~ "mode", name);
    _set(C ~ "mode-index", idx);
};

var scram = func {
    _set(C ~ "scram", 1);
    _set(C ~ "light-cmd", 0);
    _set(C ~ "rf-enable", 0);
    _set(C ~ "bus-mw", 0.0);
    _set(C ~ "plasma-proxy", 0.0);
    _set_mode("SCRAM");
};

var reset_scram = func {
    if (_num(C ~ "scram", 0) == 0) return;
    _set(C ~ "scram", 0);
    _set(C ~ "light-cmd", 0);
    _set(C ~ "dec-online", 0);
    _set_mode("OFF");
};

var set_sigma = func (s) {
    if (s < 1) s = 1;
    if (s > 3) s = 3;
    _set(E ~ "sigma", s);
};

var _update_charm = func (dt) {
    if (_num(C ~ "scram", 0)) {
        _set_mode("SCRAM");
        _set(C ~ "bus-mw", 0.0);
        _set(C ~ "go-bus", 0);
        return;
    }

    var cart = _num(C ~ "ground-cart", 0);
    var batt = _num(C ~ "battery-online", 0);
    var tied = _num(C ~ "cart-tied", 0);
    if (cart and tied)
        _set(C ~ "aux-bus-v", 270.0);
    else if (batt)
        _set(C ~ "aux-bus-v", 260.0);
    else
        _set(C ~ "aux-bus-v", 0.0);

    var cryo = _num(C ~ "cryo-enable", 0);
    if (cryo and _num(C ~ "aux-bus-v", 0) > 200) {
        _set(C ~ "cryo-kw", 88.0);
        var tk = _num(C ~ "magnet-t-k", 80);
        _set(C ~ "magnet-t-k", tk + (20.0 - tk) * 0.02);
        _set(C ~ "go-cryo", (_num(C ~ "magnet-t-k", 80) < 35.0));
    } else {
        _set(C ~ "cryo-kw", 0.0);
        _set(C ~ "go-cryo", 0);
    }

    var marm = _num(C ~ "magnet-arm", 0);
    var mi = _num(C ~ "magnet-i-frac", 0);
    if (marm and cryo and _num(C ~ "aux-bus-v", 0) > 200)
        mi = mi + (1.0 - mi) * 0.05;
    else if (!marm)
        mi = mi * 0.9;
    if (mi > 1) mi = 1;
    if (mi < 0) mi = 0;
    _set(C ~ "magnet-i-frac", mi);
    _set(C ~ "go-magnet", (mi >= 0.95));

    var fuel_en = _num(C ~ "fuel-enable", 0);
    _set(C ~ "fuel-ready", (fuel_en and _num(C ~ "fuel-b11-kg", 0) > 1 and _num(C ~ "fuel-proton-kg", 0) > 0.5));
    _set(C ~ "go-fuel", _num(C ~ "fuel-ready", 0) and _num(C ~ "vacuum-ready", 0));

    # Mode progression
    var mode = getprop(C ~ "mode");
    if (mode == nil) mode = "OFF";

    if (cryo and _num(C ~ "aux-bus-v", 0) > 200 and mode == "OFF")
        _set_mode("CRYO");

    if (mode == "CRYO" and _num(C ~ "go-magnet", 0) and _num(C ~ "go-fuel", 0))
        _set_mode("ARM");

    if (mode == "ARM" and _num(C ~ "rf-enable", 0) and _num(C ~ "light-cmd", 0))
        _set_mode("LIGHT");

    if (mode == "LIGHT" or mode == "POWER") {
        var pp = _num(C ~ "plasma-proxy", 0);
        if (_num(C ~ "light-cmd", 0) and _num(C ~ "rf-enable", 0))
            pp = pp + (1.0 - pp) * 0.08;
        else
            pp = pp * 0.95;
        _set(C ~ "plasma-proxy", pp);

        var bus = 0.0;
        if (_num(C ~ "dec-online", 0) and pp > 0.3)
            bus = 50.0 + 950.0 * pp; # ramp toward ~1 GW class
        _set(C ~ "bus-mw", bus);
        _set(C ~ "recirc-mw", cryo * 0.088 + _num(C ~ "rf-enable", 0) * 20.0);
        _set(C ~ "go-bus", (bus > 100.0));
        if (_num(C ~ "go-bus", 0))
            _set_mode("POWER");
    }

    if (mode == "POWER" and (!_num(C ~ "dec-online", 0) or !_num(C ~ "light-cmd", 0))) {
        # soft drop — stay LIGHT if still lit
        if (_num(C ~ "light-cmd", 0))
            _set_mode("LIGHT");
    }
};

var _update_engine = func (dt) {
    var alt = _num("/position/altitude-ft", 0);
    var q = _num("/velocities/dynamic-pressure-psf", 0);
    _set(E ~ "alt-ft", alt);
    _set(E ~ "q-psf", q);

    var a2 = _num(E ~ "sigma2-alt-ft", 25000);
    var a3 = _num(E ~ "sigma3-alt-ft", 120000);
    var rec = 1;
    if (alt >= a2) rec = 2;
    if (alt >= a3) rec = 3;
    _set(E ~ "sigma-recommended", rec);

    var plant_ok = (getprop(C ~ "mode") == "POWER") and (_num(C ~ "scram", 0) == 0);
    _set(E ~ "plant-ok", plant_ok);

    var allowed = 0;
    if (plant_ok) {
        allowed = 1;
        if (alt >= a2) allowed = 2;
        if (alt >= a3 and _num(E ~ "inlet-sealed", 0) and _num(E ~ "water-kg", 0) > 10)
            allowed = 3;
        elsif (alt >= a3)
            allowed = 2;
    }
    _set(E ~ "sigma-allowed", allowed);

    var sig = int(_num(E ~ "sigma", 1));
    if (sig < 1) sig = 1;
    if (sig > 3) sig = 3;

    # Soft inhibit: clamp if hard constraints fail
    if (sig == 3 and (_num(E ~ "water-kg", 0) <= 10 or !_num(E ~ "inlet-sealed", 0)))
        sig = (allowed >= 2) ? 2 : 1;
    if (!plant_ok)
        sig = 1;
    _set(E ~ "sigma", sig);
    _set(E ~ "stage-go", plant_ok and (sig <= allowed or (sig == 3 and _num(E ~ "inlet-sealed", 0))));

    var thr = _num(E ~ "throttle", 0);
    if (thr < 0) thr = 0;
    if (thr > 1) thr = 1;
    _set(E ~ "throttle", thr);

    var pdraw = 0.0;
    var thrust = 0.0;
    var wflow = 0.0;
    if (plant_ok and thr > 0.01) {
        if (sig == 1) { pdraw = 200.0 * thr; thrust = 400.0 * thr; }
        elsif (sig == 2) { pdraw = 600.0 * thr; thrust = 800.0 * thr; }
        else {
            pdraw = 900.0 * thr;
            thrust = 1200.0 * thr;
            wflow = 80.0 * thr;
        }
        # Bus limit
        var bus = _num(C ~ "bus-mw", 0);
        if (pdraw > bus and bus > 1) {
            var s = bus / pdraw;
            pdraw *= s; thrust *= s; wflow *= s;
        }
    }
    _set(E ~ "power-draw-mw", pdraw);
    _set(E ~ "thrust-kn", thrust);
    _set(E ~ "water-flow-kgps", wflow);
    if (wflow > 0) {
        var w = _num(E ~ "water-kg", 0) - wflow * dt;
        if (w < 0) w = 0;
        _set(E ~ "water-kg", w);
    }
};

# Panel aliases: listen to Shuttle APU/MPS/OMS props when grenadier enabled
var _alias_bool = func (src, dst) {
    setlistener(src, func {
        if (!_num(S ~ "enabled", 0)) return;
        var v = _num(src, 0);
        # APU operate uses -1/0/1; treat >0 as ON
        _set(dst, (v > 0) ? 1 : 0);
    }, 0, 0);
};

var _wire_panel_aliases = func {
    # APU operate → cart / battery / cryo
    _alias_bool("/fdm/jsbsim/systems/apu/apu/apu-operate", C ~ "ground-cart");
    _alias_bool("/fdm/jsbsim/systems/apu/apu[1]/apu-operate", C ~ "battery-online");
    _alias_bool("/fdm/jsbsim/systems/apu/apu[2]/apu-operate", C ~ "cryo-enable");

    _alias_bool("/fdm/jsbsim/systems/apu/apu/apu-controller-power", C ~ "magnet-arm");
    _alias_bool("/fdm/jsbsim/systems/apu/apu[1]/apu-controller-power", C ~ "fuel-enable");
    _alias_bool("/fdm/jsbsim/systems/apu/apu[2]/apu-controller-power", C ~ "rf-enable");

    # SSME controller A left/ctr/right
    setlistener("/fdm/jsbsim/systems/mps/engine/controller-A-power-switch-status", func {
        if (!_num(S ~ "enabled", 0)) return;
        if (_num("/fdm/jsbsim/systems/mps/engine/controller-A-power-switch-status", 0) > 0.5)
            _set(C ~ "light-cmd", 1);
    }, 0, 0);
    # cockpit maps ctr switch → engine[2], right → engine[1] (Shuttle indexing quirk)
    setlistener("/fdm/jsbsim/systems/mps/engine[2]/controller-A-power-switch-status", func {
        if (!_num(S ~ "enabled", 0)) return;
        if (_num("/fdm/jsbsim/systems/mps/engine[2]/controller-A-power-switch-status", 0) > 0.5)
            _set(C ~ "dec-online", 1);
    }, 0, 0);
    setlistener("/fdm/jsbsim/systems/mps/engine[1]/controller-A-power-switch-status", func {
        if (!_num(S ~ "enabled", 0)) return;
        if (_num("/fdm/jsbsim/systems/mps/engine[1]/controller-A-power-switch-status", 0) > 0.5)
            scram();
    }, 0, 0);

    # OMS arm knobs (0 OFF, 1 ARM/PRESS, 2 ARM) nudge sigma on rising edge to ARM
    var prev_ol = 0;
    var prev_or = 0;
    setlistener("/fdm/jsbsim/systems/oms-hardware/engine-left-arm-cmd", func {
        if (!_num(S ~ "enabled", 0)) return;
        var v = _num("/fdm/jsbsim/systems/oms-hardware/engine-left-arm-cmd", 0);
        if (v >= 1 and prev_ol < 1)
            set_sigma(int(_num(E ~ "sigma", 1)) - 1);
        prev_ol = v;
    }, 0, 0);
    setlistener("/fdm/jsbsim/systems/oms-hardware/engine-right-arm-cmd", func {
        if (!_num(S ~ "enabled", 0)) return;
        var v = _num("/fdm/jsbsim/systems/oms-hardware/engine-right-arm-cmd", 0);
        if (v >= 1 and prev_or < 1)
            set_sigma(int(_num(E ~ "sigma", 1)) + 1);
        prev_or = v;
    }, 0, 0);
};

var _loop = func {
    _update_charm(0.2);
    _update_engine(0.2);
    settimer(_loop, 0.2);
};

var start = func {
    init_defaults();
    # Convenience: cart tied when cart on
    setlistener(C ~ "ground-cart", func {
        if (_num(C ~ "ground-cart", 0))
            _set(C ~ "cart-tied", 1);
    }, 0, 0);
    # Auto vacuum-ready once ARM path fuel enabled (stub)
    setlistener(C ~ "fuel-enable", func {
        if (_num(C ~ "fuel-enable", 0))
            _set(C ~ "vacuum-ready", 1);
    }, 0, 0);
    _wire_panel_aliases();
    _loop();
    print("Grenadier ops: CATSKILLS-SSTO-TA-GRENADIER operator model running");
};

setlistener("/sim/signals/fdm-initialized", func {
    settimer(start, 2.0);
});
