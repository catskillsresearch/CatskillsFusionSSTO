# CATSKILLS-SSTO-TA-GRENADIER operator model
# Property bus + mode machine + panel aliases + stage gates.
#
# Dual-control thrust (plant × engine):
#   CHARM must be POWER (bus live, not scrammed)  AND
#   engine cycle (sigma) must be stage-go with throttle demand.
# Either side alone produces zero JSBSim force.

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

    # CDR/PLT meshes live in cockpit-detailed.ac; aircraft-data used to force this to 0.
    _set("/sim/config/shuttle/detailed-flightdeck", 1);

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
    _set(E ~ "thrust-lbf", 0.0);
    _set(E ~ "power-draw-mw", 0.0);
    _set(E ~ "fan-spin-deg", 0.0);
    _set(E ~ "water-kg", 44000.0);
    _set(E ~ "water-flow-kgps", 0.0);
    _set(E ~ "alt-ft", 0.0);
    _set(E ~ "q-psf", 0.0);
    _set(E ~ "stage-go", 0);
    _set(E ~ "plant-ok", 0);
    _set(E ~ "coupled-ok", 0);
    _set(E ~ "bus-frac", 0.0);
    # Peak thrust by cycle at throttle=1 with full bus (kN → also published as lbf)
    _set(E ~ "thrust-peak-kn-sigma1", 400.0);
    _set(E ~ "thrust-peak-kn-sigma2", 800.0);
    _set(E ~ "thrust-peak-kn-sigma3", 1200.0);

    # Exhaust VFX bus (tiny flame → big plasma plume)
    var V = G ~ "vfx/";
    _set(V ~ "plume-norm", 0.0);
    _set(V ~ "flame-scale", 0.0);
    _set(V ~ "core-size-m", 0.2);
    _set(V ~ "plume-size-m", 0.4);
    _set(V ~ "core-rate", 0.0);
    _set(V ~ "plume-rate", 0.0);
    _set(V ~ "exhaust-speed-mps", 40.0);
    _set(V ~ "show-flame", 0);
    _set(V ~ "show-plume", 0);
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

# Keep heritage SSME/OMS cold while Grenadier owns propulsion.
# Note: controls/engines/engine[0]/throttle is reused as Grenadier thrust demand — do not zero it.
var _hold_heritage_engines_cold = func {
    if (!_num(S ~ "enabled", 0)) return;
    var i = 0;
    while (i < 3) {
        setprop("/fdm/jsbsim/systems/mps/engine[" ~ i ~ "]/run-cmd", 0);
        setprop("/controls/engines/engine[" ~ i ~ "]/ap-throttle-cmd", 0);
        i += 1;
    }
    # Side/center SSME levers unused; leave engine[0] for Grenadier demand
    setprop("/controls/engines/engine[1]/throttle", 0);
    setprop("/controls/engines/engine[2]/throttle", 0);
    # OMS engines are indices 5/6 in the Shuttle kit
    setprop("/controls/engines/engine[5]/throttle", 0);
    setprop("/controls/engines/engine[6]/throttle", 0);
};

var _update_engine = func (dt) {
    var alt = _num("/position/altitude-ft", 0);
    var q = _num("/velocities/dynamic-pressure-psf", 0);
    _set(E ~ "alt-ft", alt);
    _set(E ~ "q-psf", q);

    # --- Power system (CHARM) ---
    var plant_ok = (getprop(C ~ "mode") == "POWER") and (_num(C ~ "scram", 0) == 0);
    var bus = _num(C ~ "bus-mw", 0);
    if (!plant_ok) bus = 0;
    _set(E ~ "plant-ok", plant_ok ? 1 : 0);

    # --- Engine system (cycle + throttle demand) ---
    var a2 = _num(E ~ "sigma2-alt-ft", 25000);
    var a3 = _num(E ~ "sigma3-alt-ft", 120000);
    var rec = 1;
    if (alt >= a2) rec = 2;
    if (alt >= a3) rec = 3;
    _set(E ~ "sigma-recommended", rec);

    # Cycle allow depends on sensors; plant must also be up for any stage-go
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
    if (sig == 3 and (_num(E ~ "water-kg", 0) <= 10 or !_num(E ~ "inlet-sealed", 0)))
        sig = (allowed >= 2) ? 2 : 1;
    _set(E ~ "sigma", sig);

    var stage_go = plant_ok and (sig <= allowed);
    if (sig == 3)
        stage_go = plant_ok and _num(E ~ "inlet-sealed", 0) and (_num(E ~ "water-kg", 0) > 10);
    _set(E ~ "stage-go", stage_go ? 1 : 0);

    # Throttle demand SSOT: pilot lever (controls/engines/engine[0]/throttle).
    # Canvas THR± writes that same prop. Not an SSME run command — heritage run-cmd stays 0.
    var thr = _num("/controls/engines/engine[0]/throttle", 0);
    if (thr < 0) thr = 0;
    if (thr > 1) thr = 1;
    _set(E ~ "throttle", thr);

    # --- Couple: both systems required ---
    var coupled = plant_ok and stage_go and (thr > 0.01) and (bus > 1.0);
    _set(E ~ "coupled-ok", coupled ? 1 : 0);

    var pdraw = 0.0;
    var thrust_kn = 0.0;
    var wflow = 0.0;
    var bus_frac = 0.0;

    if (coupled) {
        var peak = _num(E ~ "thrust-peak-kn-sigma1", 400);
        if (sig == 1) { pdraw = 200.0 * thr; peak = _num(E ~ "thrust-peak-kn-sigma1", 400); }
        elsif (sig == 2) { pdraw = 600.0 * thr; peak = _num(E ~ "thrust-peak-kn-sigma2", 800); }
        else {
            pdraw = 900.0 * thr;
            peak = _num(E ~ "thrust-peak-kn-sigma3", 1200);
            wflow = 80.0 * thr;
        }
        thrust_kn = peak * thr;
        # Power cable limit: engine cannot exceed CHARM bus
        if (pdraw > bus and bus > 1) {
            bus_frac = bus / pdraw;
            pdraw *= bus_frac;
            thrust_kn *= bus_frac;
            wflow *= bus_frac;
        } else {
            bus_frac = 1.0;
        }
    } else {
        # Explicit zeros when either control set is not ready
        pdraw = 0.0;
        thrust_kn = 0.0;
        wflow = 0.0;
        bus_frac = 0.0;
    }

    _set(E ~ "bus-frac", bus_frac);
    _set(E ~ "power-draw-mw", pdraw);
    _set(E ~ "thrust-kn", thrust_kn);
    # JSBSim external_reactions reads lbf
    _set(E ~ "thrust-lbf", thrust_kn * 224.808943);
    _set(E ~ "water-flow-kgps", wflow);
    if (wflow > 0) {
        var w = _num(E ~ "water-kg", 0) - wflow * dt;
        if (w < 0) w = 0;
        _set(E ~ "water-kg", w);
    }

    _hold_heritage_engines_cold();

    # Visual: spin σ1 EDF when coupled in air-breathing
    var spin = _num(E ~ "fan-spin-deg", 0);
    if (coupled and sig == 1)
        spin += dt * (720.0 * thr);
    elsif (coupled)
        spin += dt * (180.0 * thr);
    while (spin > 360.0) spin -= 360.0;
    _set(E ~ "fan-spin-deg", spin);

    _update_exhaust_vfx(thrust_kn, sig, coupled);
};

# Map thrust → tiny nozzle glow vs big plasma plume
var _update_exhaust_vfx = func (thrust_kn, sig, coupled) {
    var V = G ~ "vfx/";
    var peak = _num(E ~ "thrust-peak-kn-sigma1", 400);
    if (sig == 2) peak = _num(E ~ "thrust-peak-kn-sigma2", 800);
    if (sig == 3) peak = _num(E ~ "thrust-peak-kn-sigma3", 1200);
    if (peak < 1) peak = 1;

    var n = 0.0;
    if (coupled and thrust_kn > 0.05)
        n = thrust_kn / peak;
    if (n < 0) n = 0;
    if (n > 1) n = 1;

    # Slightly punchier visual curve so mid throttle already reads as plasma
    var n2 = n * n;
    var show_flame = (n > 0.008) ? 1 : 0;
    # Plume kicks in once we're past "idle spit"
    var show_plume = (n > 0.12) ? 1 : 0;

    # Mesh flame scale: tiny at idle → large at full (σ2/σ3 a bit fatter)
    var flame_scale = 0.35 + 3.2 * n + (sig >= 2 ? 0.6 * n : 0);
    var core_size = 0.15 + 1.8 * n + 1.2 * n2;
    var plume_size = 0.35 + 4.5 * n + 3.5 * n2;
    var core_rate = 80.0 * n + 220.0 * n2;
    var plume_rate = 40.0 * n + 280.0 * n2;
    var speed = 60.0 + 420.0 * n + 200.0 * n2;
    if (sig == 3) {
        # Water-plasma: denser, brighter plume
        plume_size *= 1.25;
        plume_rate *= 1.35;
        core_size *= 1.15;
    }

    _set(V ~ "plume-norm", n);
    _set(V ~ "flame-scale", flame_scale);
    _set(V ~ "core-size-m", core_size);
    _set(V ~ "plume-size-m", plume_size);
    _set(V ~ "core-rate", core_rate);
    _set(V ~ "plume-rate", plume_rate);
    _set(V ~ "exhaust-speed-mps", speed);
    _set(V ~ "show-flame", show_flame);
    _set(V ~ "show-plume", show_plume);
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
    # cockpit maps ctr switch → engine[2] (Shuttle indexing quirk)
    setlistener("/fdm/jsbsim/systems/mps/engine[2]/controller-A-power-switch-status", func {
        if (!_num(S ~ "enabled", 0)) return;
        if (_num("/fdm/jsbsim/systems/mps/engine[2]/controller-A-power-switch-status", 0) > 0.5)
            _set(C ~ "dec-online", 1);
    }, 0, 0);
    # SSME-right controller → vacuum ready (not SCRAM — too easy to fat-finger next to LIGHT/DEC)
    setlistener("/fdm/jsbsim/systems/mps/engine[1]/controller-A-power-switch-status", func {
        if (!_num(S ~ "enabled", 0)) return;
        _set(C ~ "vacuum-ready",
            (_num("/fdm/jsbsim/systems/mps/engine[1]/controller-A-power-switch-status", 0) > 0.5) ? 1 : 0);
    }, 0, 0);
    # Main Engine Limit Shutdown → SCRAM when Enable (index 2)
    setlistener("/fdm/jsbsim/systems/mps/limit-shutdown-enable", func {
        if (!_num(S ~ "enabled", 0)) return;
        if (_num("/fdm/jsbsim/systems/mps/limit-shutdown-enable", 0) >= 2)
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
    # Never show heritage stack
    setprop("/controls/shuttle/ET-static-model", 0);
    setprop("/controls/shuttle/SRB-static-model", 0);
    setprop("/controls/shuttle/SRB-attach", 0);
    _hold_heritage_engines_cold();
    # Convenience: cart tied when cart on
    setlistener(C ~ "ground-cart", func {
        if (_num(C ~ "ground-cart", 0))
            _set(C ~ "cart-tied", 1);
    }, 0, 0);
    _wire_panel_aliases();
    _loop();
    print("Grenadier ops: dual-control thrust (CHARM plant × engine cycle) coupled to JSBSim");
};

setlistener("/sim/signals/fdm-initialized", func {
    settimer(start, 2.0);
});
