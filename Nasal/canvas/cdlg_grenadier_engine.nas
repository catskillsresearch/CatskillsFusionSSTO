# Grenadier 3-cycle engine operator screen

var cdlg_grenadier_engine = {
    window: nil,
    root: nil,
    timer: nil,
    lines: [],

    init: func {
        if (me.window != nil) {
            me.window.set("visible", 1);
            return;
        }
        me.window = canvas.Window.new([520, 480], "dialog")
            .set("title", "GRENADIER ENGINE");
        var c = me.window.createCanvas().set("background", "#0a1018");
        me.root = c.createGroup();

        me.root.createChild("text")
            .setTranslation(12, 22)
            .setAlignment("left-center")
            .setFontSize(18)
            .setColor(0.5, 0.85, 1.0)
            .setText("CATSKILLS-SSTO-TA-GRENADIER");

        me.root.createChild("text")
            .setTranslation(12, 48)
            .setAlignment("left-center")
            .setFontSize(16)
            .setColor(0.8, 0.95, 1.0)
            .setText("3-CYCLE ENGINE");

        me.lines = [];
        for (var i = 0; i < 14; i += 1) {
            append(me.lines, me.root.createChild("text")
                .setTranslation(16, 80 + i * 22)
                .setAlignment("left-center")
                .setFontSize(14)
                .setColor(0.75, 0.9, 1.0)
                .setText(""));
        }

        me._btn(20, 440, 70, 28, "σ1", func { setprop("/fdm/jsbsim/systems/grenadier/engine/sigma", 1); });
        me._btn(100, 440, 70, 28, "σ2", func { setprop("/fdm/jsbsim/systems/grenadier/engine/sigma", 2); });
        me._btn(180, 440, 70, 28, "σ3", func { setprop("/fdm/jsbsim/systems/grenadier/engine/sigma", 3); });
        me._btn(260, 440, 90, 28, "SEAL", func {
            var p = "/fdm/jsbsim/systems/grenadier/engine/inlet-sealed";
            setprop(p, getprop(p) ? 0 : 1);
        });
        me._btn(360, 440, 60, 28, "THR+", func {
            # Pilot lever is SSOT for thrust demand
            var p = "/controls/engines/engine[0]/throttle";
            var t = getprop(p);
            if (t == nil) t = 0;
            t += 0.1;
            if (t > 1) t = 1;
            setprop(p, t);
        });
        me._btn(430, 440, 60, 28, "THR-", func {
            var p = "/controls/engines/engine[0]/throttle";
            var t = getprop(p);
            if (t == nil) t = 0;
            t -= 0.1;
            if (t < 0) t = 0;
            setprop(p, t);
        });

        me.timer = maketimer(0.25, func { me.update(); });
        me.timer.start();
        me.update();
    },

    _btn: func (x, y, w, h, label, f) {
        var g = me.root.createChild("group");
        g.createChild("path")
            .rect(x, y - h, w, h)
            .setColorFill(0.12, 0.2, 0.3)
            .setColor(0.4, 0.7, 1.0);
        g.createChild("text")
            .setTranslation(x + w/2, y - h/2)
            .setAlignment("center-center")
            .setFontSize(12)
            .setColor(0.9, 0.95, 1)
            .setText(label);
        g.addEventListener("click", f);
    },

    _g: func (p) {
        var v = getprop("/fdm/jsbsim/systems/grenadier/engine/" ~ p);
        if (v == nil) return "—";
        return v;
    },

    _gf: func (p, fmt) {
        var v = getprop("/fdm/jsbsim/systems/grenadier/engine/" ~ p);
        if (v == nil) return "—";
        return sprintf(fmt, v);
    },

    update: func {
        me.lines[0].setText(sprintf("ALT (sensor)     %s ft", me._gf("alt-ft", "%.0f")));
        me.lines[1].setText(sprintf("Q               %s psf", me._gf("q-psf", "%.1f")));
        me.lines[2].setText(sprintf("σ commanded     %s", me._g("sigma")));
        me.lines[3].setText(sprintf("σ recommended   %s   allowed %s", me._g("sigma-recommended"), me._g("sigma-allowed")));
        me.lines[4].setText(sprintf("Gates σ2≥%s ft  σ3≥%s ft", me._gf("sigma2-alt-ft", "%.0f"), me._gf("sigma3-alt-ft", "%.0f")));
        me.lines[5].setText(sprintf("Inlet sealed    %s", me._g("inlet-sealed")));
        me.lines[6].setText(sprintf("Water           %s kg   flow %s kg/s", me._gf("water-kg", "%.0f"), me._gf("water-flow-kgps", "%.1f")));
        me.lines[7].setText(sprintf("Throttle        %s   (pilot lever or THR±)", me._gf("throttle", "%.2f")));
        me.lines[8].setText(sprintf("Thrust          %s kN  (%s lbf)  draw %s MW",
            me._gf("thrust-kn", "%.0f"), me._gf("thrust-lbf", "%.0f"), me._gf("power-draw-mw", "%.0f")));
        me.lines[9].setText(sprintf("Plant OK        %s   stage-go %s   coupled %s",
            me._g("plant-ok"), me._g("stage-go"), me._g("coupled-ok")));
        me.lines[10].setText(sprintf("Bus fraction    %s   (CHARM cable limit)", me._gf("bus-frac", "%.2f")));
        me.lines[11].setText("DUAL CONTROL: CHARM→POWER  AND  σ cycle + throttle");
        me.lines[12].setText("Either alone → zero JSBSim thrust; σ3 needs seal+water");
        me.lines[13].setText("OMS L/R arm: σ− / σ+");
    },
};
