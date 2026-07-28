# Grenadier CHARM operator screens (Fuel + Startup)

var cdlg_grenadier_reactor = {
    window: nil,
    root: nil,
    timer: nil,
    page: 0, # 0 fuel, 1 startup
    lines: [],

    init: func {
        if (me.window != nil) {
            me.window.set("visible", 1);
            return;
        }
        me.window = canvas.Window.new([520, 560], "dialog")
            .set("title", "GRENADIER CHARM");
        var c = me.window.createCanvas().set("background", "#0a1210");
        me.root = c.createGroup();

        me.root.createChild("text")
            .setTranslation(12, 22)
            .setAlignment("left-center")
            .setFontSize(18)
            .setColor(0.4, 1.0, 0.7)
            .setText("CATSKILLS-SSTO-TA-GRENADIER");

        me.title = me.root.createChild("text")
            .setTranslation(12, 48)
            .setAlignment("left-center")
            .setFontSize(16)
            .setColor(0.8, 1.0, 0.9)
            .setText("FUEL");

        me.lines = [];
        for (var i = 0; i < 18; i += 1) {
            append(me.lines, me.root.createChild("text")
                .setTranslation(16, 80 + i * 22)
                .setAlignment("left-center")
                .setFontSize(14)
                .setColor(0.7, 0.95, 0.8)
                .setText(""));
        }

        me._btn(20, 520, 100, 28, "FUEL", func { me.page = 0; });
        me._btn(130, 520, 120, 28, "STARTUP", func { me.page = 1; });
        me._btn(260, 520, 100, 28, "CART", func {
            var p = "/fdm/jsbsim/systems/grenadier/charm/ground-cart";
            setprop(p, getprop(p) ? 0 : 1);
            if (getprop(p)) setprop("/fdm/jsbsim/systems/grenadier/charm/cart-tied", 1);
        });
        me._btn(370, 520, 100, 28, "SCRAM", func {
            setprop("/fdm/jsbsim/systems/grenadier/charm/scram", 1);
        });
        me._btn(370, 480, 100, 28, "RST SCRAM", func {
            grenadier_reset_scram();
        });

        me.timer = maketimer(0.25, func { me.update(); });
        me.timer.start();
        me.update();
    },

    _btn: func (x, y, w, h, label, f) {
        var g = me.root.createChild("group");
        g.createChild("path")
            .rect(x, y - h, w, h)
            .setColorFill(0.15, 0.25, 0.2)
            .setColor(0.4, 0.8, 0.6);
        g.createChild("text")
            .setTranslation(x + w/2, y - h/2)
            .setAlignment("center-center")
            .setFontSize(12)
            .setColor(0.9, 1, 0.9)
            .setText(label);
        g.addEventListener("click", f);
    },

    _g: func (p) {
        var v = getprop("/fdm/jsbsim/systems/grenadier/" ~ p);
        if (v == nil) return "—";
        return v;
    },

    _gf: func (p, fmt) {
        var v = getprop("/fdm/jsbsim/systems/grenadier/" ~ p);
        if (v == nil) return "—";
        return sprintf(fmt, v);
    },

    update: func {
        if (me.page == 0) {
            me.title.setText("FUEL / TANKS");
            me.lines[0].setText(sprintf("B11 solid     %s kg", me._gf("charm/fuel-b11-kg", "%.1f")));
            me.lines[1].setText(sprintf("Proton        %s kg", me._gf("charm/fuel-proton-kg", "%.1f")));
            me.lines[2].setText(sprintf("Flight batt   %s kWh (min %s)", me._gf("charm/battery-kwh", "%.0f"), me._gf("charm/battery-min-kwh", "%.0f")));
            me.lines[3].setText(sprintf("Water (engine)%s kg", me._gf("engine/water-kg", "%.0f")));
            me.lines[4].setText(sprintf("Ground cart   %s   Batt online %s", me._g("charm/ground-cart"), me._g("charm/battery-online")));
            me.lines[5].setText(sprintf("Cart tied     %s   Source %s", me._g("charm/cart-tied"), me._g("charm/startup-source")));
            me.lines[6].setText(sprintf("Aux bus       %s V", me._gf("charm/aux-bus-v", "%.0f")));
            me.lines[7].setText("");
            me.lines[8].setText("GO lamps:");
            me.lines[9].setText(sprintf("  fuel %s  cryo %s  magnet %s  bus %s",
                me._g("charm/go-fuel"), me._g("charm/go-cryo"), me._g("charm/go-magnet"), me._g("charm/go-bus")));
            for (var i = 10; i < 18; i += 1) me.lines[i].setText("");
        } else {
            me.title.setText("STARTUP SEQUENCE");
            me.lines[0].setText(sprintf("MODE  %s   SCRAM %s", me._g("charm/mode"), me._g("charm/scram")));
            me.lines[1].setText(sprintf("1 Cryo enable     %s   cryo kW %s", me._g("charm/cryo-enable"), me._gf("charm/cryo-kw", "%.0f")));
            me.lines[2].setText(sprintf("2 Magnet arm      %s   Ifrac %s  T %s K",
                me._g("charm/magnet-arm"), me._gf("charm/magnet-i-frac", "%.2f"), me._gf("charm/magnet-t-k", "%.0f")));
            me.lines[3].setText(sprintf("3 Fuel enable     %s   ready %s  vac %s",
                me._g("charm/fuel-enable"), me._g("charm/fuel-ready"), me._g("charm/vacuum-ready")));
            me.lines[4].setText(sprintf("4 RF enable       %s", me._g("charm/rf-enable")));
            me.lines[5].setText(sprintf("5 Light cmd       %s   plasma %s",
                me._g("charm/light-cmd"), me._gf("charm/plasma-proxy", "%.2f")));
            me.lines[6].setText(sprintf("6 DEC online      %s", me._g("charm/dec-online")));
            me.lines[7].setText(sprintf("7 Bus             %s MW   recirc %s MW",
                me._gf("charm/bus-mw", "%.1f"), me._gf("charm/recirc-mw", "%.1f")));
            me.lines[8].setText("");
            me.lines[9].setText("Panel aliases: APU1 cart  APU2 batt  APU3 cryo");
            me.lines[10].setText("APU ctrl pwr → magnet / fuel / RF");
            me.lines[11].setText("SSME ctrl A L/C/R → light / DEC / SCRAM");
            for (var i = 12; i < 18; i += 1) me.lines[i].setText("");
        }
    },
};

var grenadier_reset_scram = func {
    setprop("/fdm/jsbsim/systems/grenadier/charm/scram", 0);
    setprop("/fdm/jsbsim/systems/grenadier/charm/light-cmd", 0);
    setprop("/fdm/jsbsim/systems/grenadier/charm/dec-online", 0);
    setprop("/fdm/jsbsim/systems/grenadier/charm/mode", "OFF");
    setprop("/fdm/jsbsim/systems/grenadier/charm/mode-index", 0);
};
