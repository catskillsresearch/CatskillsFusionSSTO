var ReactorUI = {
    new: func() {
        var m = { parents: [ReactorUI] };
        m.canvas = canvas.new({
            "name": "Reactor_Telemetry",
            "size":[1024, 1200],
            "view": [1024, 1200],
            "mipmapping": 1
        });

        # Placement probe: bind to likely runtime node names to discover
        # which scene-graph nodes are canvas-capable in this model.
        var probe_nodes = [
            "Screen", "screen",
            "Operator_Console", "operator_console",
            "Optics_Table", "optics_table",
            "Big_Red_Button", "big_red_button"
        ];
        foreach (var node_name; probe_nodes) {
            var placed = m.canvas.addPlacement({"node": node_name});
            print("Orbitron canvas placement probe node=", node_name, " result=", placed);
        }

        m.root = m.canvas.createGroup();
        m.root.createChild("path")
             .rect(0, 0, 1024, 1200)
             .setColorFill(0.06, 0.08, 0.12, 1.0);
        m.root.createChild("path")
             .rect(20, 20, 984, 1160)
             .setColorFill(0.0, 0.0, 0.0, 1.0);

        m.root.createChild("text")
              .setText("ORBITRON + ARCJET TEST STAND")
              .setFont("LiberationFonts/LiberationSans-Bold.ttf")
              .setFontSize(56)
              .setColor(1, 0.8, 0)
              .setAlignment("center-center")
              .setTranslation(512, 100);

        m.txt_state = m.create_text(210, "Startup Trigger: OFF");
        m.txt_nbi   = m.create_text(300, "NBI Flow: 0.00 sccm");
        m.txt_comp  = m.create_text(390, "Compressor: 0.00");
        m.txt_power = m.create_text(480, "Gross Power: 0.00 MW");
        m.txt_amps  = m.create_text(570, "DEC Current: 0.000 A");
        m.txt_decv  = m.create_text(660, "DEC Bias: 0.0 MV");
        m.txt_heat  = m.create_text(750, "Brem. Heat: 0.00 kW");
        m.txt_q     = m.create_text(840, "Q-Factor: 0.00");
        m.txt_thrust = m.create_text(930, "Thrust: 0 lbf");
        m.txt_mdot  = m.create_text(1020, "Mass Flow: 0.000 kg/s");
        m.txt_load  = m.create_text(1110, "Load Cell Avg: 0 lbf");
        m.txt_beam  = m.create_text(1165, "Viewport beam: 0.0 kW  |  0.00 mA");

        m.debug_window = nil;
        m.debug_root = nil;
        m.debug_txt = [];

        m.sync_debug_window();

        m.timer = maketimer(0.1, m, ReactorUI.update);
        m.timer.start();

        return m;
    },

    create_text: func(y, initial_text) {
        return me.root.createChild("text")
                     .setText(initial_text)
                     .setFont("LiberationFonts/LiberationMono-Bold.ttf")
                     .setFontSize(44)
                     .setColor(0, 1, 0)
                     .setAlignment("center-center")
                     .setTranslation(512, y);
    },

    sync_debug_window: func() {
        var enabled = (getprop("/sim/model/reactor/debug-ui-window") or 0) != 0;
        if (enabled) {
            if (me.debug_window != nil) return;

            me.debug_window = canvas.Window.new([460, 500], "dialog")
                .set("title", "Arcjet / Reactor Telemetry");
            var dbg_canvas = me.debug_window.createCanvas().set("background", [0.03, 0.03, 0.03, 0.90]);
            me.debug_root = dbg_canvas.createGroup();

            me.debug_txt = [];
            var labels = [
                "Startup Trigger: OFF",
                "NBI Flow: 0.00 sccm",
                "Compressor: 0.00",
                "Gross Power: 0.00 MW",
                "DEC Current: 0.000 A",
                "DEC Bias: 0.0 MV",
                "Brem. Heat: 0.0 kW",
                "Beam viewport: 0.0 kW (WarpX ROI)",
                "Beam current: 0.00 mA (8 MV eq.)",
                "Thrust: 0 lbf",
                "Mass Flow: 0.000 kg/s",
                "Load Cell Avg: 0 lbf",
                "Q-Factor: 0.00"
            ];
            for (var i = 0; i < size(labels); i += 1) {
                var y = 28 + i * 38;
                append(me.debug_txt, me.debug_root.createChild("text")
                    .setText(labels[i])
                    .setFont("LiberationFonts/LiberationMono-Bold.ttf")
                    .setFontSize(20).setColor(0, 1, 0).setAlignment("left-center")
                    .setTranslation(16, y));
            }
            return;
        }

        if (me.debug_window != nil) {
            call(canvas.Window.del, [], me.debug_window);
            me.debug_window = nil;
            me.debug_root = nil;
            me.debug_txt = [];
        }
    },

    update: func() {
        me.sync_debug_window();

        var startup_on = (getprop("/sim/model/reactor/startup-trigger") or 0) != 0;
        var nbi   = getprop("/controls/reactor/throttle") or 0.0;
        var comp  = getprop("/controls/orbitron/compressor") or 0.0;
        var power = getprop("/fdm/jsbsim/systems/reactor/gross-power-mw") or 0.0;
        var amps  = getprop("/fdm/jsbsim/systems/reactor/current-amps") or 0.0;
        var heat  = getprop("/fdm/jsbsim/systems/reactor/heat-kw") or 0.0;
        var q     = getprop("/fdm/jsbsim/systems/reactor/q-factor") or 0.0;
        var decv  = getprop("/fdm/jsbsim/systems/arcjet/dec-voltage-mv") or 0.0;
        var thrust = getprop("/fdm/jsbsim/systems/arcjet/thrust-lbf") or 0.0;
        var mdot  = getprop("/fdm/jsbsim/systems/arcjet/mass-flow-kgps") or 0.0;
        var load  = getprop("/fdm/jsbsim/systems/arcjet/load-cell-avg-lbf") or 0.0;
        var bkw   = getprop("/fdm/jsbsim/systems/reactor/beam-screen-deposition-kw") or 0.0;
        var bma   = getprop("/fdm/jsbsim/systems/reactor/beam-current-ma") or 0.0;

        var nbi_display = nbi * 100.0;
        me.txt_state.setText("Startup Trigger: " ~ (startup_on ? "ON" : "OFF"));
        me.txt_nbi.setText(sprintf("NBI Flow: %.2f sccm", nbi_display));
        me.txt_comp.setText(sprintf("Compressor: %.2f", comp));
        me.txt_power.setText(sprintf("Gross Power: %.3f MW", power));
        me.txt_amps.setText(sprintf("DEC Current: %.3f A", amps));
        me.txt_decv.setText(sprintf("DEC Bias: %.1f MV", decv));
        me.txt_heat.setText(sprintf("Brem. Heat: %.1f kW", heat));
        me.txt_q.setText(sprintf("Q-Factor: %.2f", q));
        me.txt_thrust.setText(sprintf("Thrust: %.0f lbf", thrust));
        me.txt_mdot.setText(sprintf("Mass Flow: %.3f kg/s", mdot));
        me.txt_load.setText(sprintf("Load Cell Avg: %.0f lbf", load));
        me.txt_beam.setText(sprintf("Viewport beam: %.1f kW  |  %.2f mA", bkw, bma));

        var n_dbg = size(me.debug_txt);
        if (n_dbg == 13) {
            me.debug_txt[0].setText("Startup Trigger: " ~ (startup_on ? "ON" : "OFF"));
            me.debug_txt[1].setText(sprintf("NBI Flow: %.2f sccm", nbi_display));
            me.debug_txt[2].setText(sprintf("Compressor: %.2f", comp));
            me.debug_txt[3].setText(sprintf("Gross Power: %.3f MW", power));
            me.debug_txt[4].setText(sprintf("DEC Current: %.3f A", amps));
            me.debug_txt[5].setText(sprintf("DEC Bias: %.1f MV", decv));
            me.debug_txt[6].setText(sprintf("Brem. Heat: %.1f kW", heat));
            me.debug_txt[7].setText(sprintf("Beam viewport: %.1f kW", bkw));
            me.debug_txt[8].setText(sprintf("Beam current: %.2f mA", bma));
            me.debug_txt[9].setText(sprintf("Thrust: %.0f lbf", thrust));
            me.debug_txt[10].setText(sprintf("Mass Flow: %.3f kg/s", mdot));
            me.debug_txt[11].setText(sprintf("Load Cell Avg: %.0f lbf", load));
            me.debug_txt[12].setText(sprintf("Q-Factor: %.2f", q));
        }
    }
};

var sys = ReactorUI.new();
