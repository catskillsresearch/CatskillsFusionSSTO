var ReactorUI = {
    new: func() {
        var m = { parents: [ReactorUI] };
        m.canvas = canvas.new({
            "name": "Reactor_Telemetry",
            "size":[1024, 1024],
            "view": [1024, 1024],
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
             .rect(0, 0, 1024, 1024)
             .setColorFill(0.06, 0.08, 0.12, 1.0);
        m.root.createChild("path")
             .rect(20, 20, 984, 984)
             .setColorFill(0.0, 0.0, 0.0, 1.0);

        m.root.createChild("text")
              .setText("p-B11 ORBITRON TELEMETRY")
              .setFont("LiberationFonts/LiberationSans-Bold.ttf")
              .setFontSize(62)
              .setColor(1, 0.8, 0) 
              .setAlignment("center-center")
              .setTranslation(512, 120);

        m.txt_state = m.create_text(250, "Startup Trigger: OFF");

        m.txt_nbi   = m.create_text(390, "NBI Flow: 0.00 sccm");
        m.txt_power = m.create_text(530, "Gross Power: 0.00 MW");
        m.txt_amps  = m.create_text(670, "DEC Current: 0.000 A");
        m.txt_heat  = m.create_text(810, "Brem. Heat: 0.00 kW");
        m.txt_q     = m.create_text(940, "Q-Factor: 0.00");

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
                     .setFontSize(52)
                     .setColor(0, 1, 0) 
                     .setAlignment("center-center")
                     .setTranslation(512, y);
    },

    sync_debug_window: func() {
        var enabled = (getprop("/sim/model/reactor/debug-ui-window") or 0) != 0;
        if (enabled) {
            if (me.debug_window != nil) return;

            me.debug_window = canvas.Window.new([400, 300], "dialog")
                .set("title", "Reactor Telemetry (Debug)");
            var dbg_canvas = me.debug_window.createCanvas().set("background", [0.03, 0.03, 0.03, 0.90]);
            me.debug_root = dbg_canvas.createGroup();

            me.debug_txt = [];
            append(me.debug_txt, me.debug_root.createChild("text")
                .setText("Startup Trigger: OFF")
                .setFont("LiberationFonts/LiberationMono-Bold.ttf")
                .setFontSize(24).setColor(0, 1, 0).setAlignment("left-center")
                .setTranslation(20, 45));
            append(me.debug_txt, me.debug_root.createChild("text")
                .setText("NBI Flow: 0.00 sccm")
                .setFont("LiberationFonts/LiberationMono-Bold.ttf")
                .setFontSize(24).setColor(0, 1, 0).setAlignment("left-center")
                .setTranslation(20, 95));
            append(me.debug_txt, me.debug_root.createChild("text")
                .setText("Gross Power: 0.00 MW")
                .setFont("LiberationFonts/LiberationMono-Bold.ttf")
                .setFontSize(24).setColor(0, 1, 0).setAlignment("left-center")
                .setTranslation(20, 145));
            append(me.debug_txt, me.debug_root.createChild("text")
                .setText("DEC Current: 0.000 A")
                .setFont("LiberationFonts/LiberationMono-Bold.ttf")
                .setFontSize(24).setColor(0, 1, 0).setAlignment("left-center")
                .setTranslation(20, 195));
            append(me.debug_txt, me.debug_root.createChild("text")
                .setText("Q-Factor: 0.00")
                .setFont("LiberationFonts/LiberationMono-Bold.ttf")
                .setFontSize(24).setColor(0, 1, 0).setAlignment("left-center")
                .setTranslation(20, 245));
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
        var power = getprop("/fdm/jsbsim/systems/reactor/gross-power-mw") or 0.0;
        var amps  = getprop("/fdm/jsbsim/systems/reactor/current-amps") or 0.0;
        var heat  = getprop("/fdm/jsbsim/systems/reactor/heat-kw") or 0.0;
        var q     = getprop("/fdm/jsbsim/systems/reactor/q-factor") or 0.0;

        var nbi_display = nbi * 100.0;
        me.txt_state.setText("Startup Trigger: " ~ (startup_on ? "ON" : "OFF"));

        me.txt_nbi.setText(sprintf("NBI Flow: %.2f sccm", nbi_display));
        me.txt_power.setText(sprintf("Gross Power: %.3f MW", power));
        me.txt_amps.setText(sprintf("DEC Current: %.3f A", amps));
        me.txt_heat.setText(sprintf("Brem. Heat: %.1f kW", heat));
        me.txt_q.setText(sprintf("Q-Factor: %.2f", q));

        if (size(me.debug_txt) == 5) {
            me.debug_txt[0].setText("Startup Trigger: " ~ (startup_on ? "ON" : "OFF"));
            me.debug_txt[1].setText(sprintf("NBI Flow: %.2f sccm", nbi_display));
            me.debug_txt[2].setText(sprintf("Gross Power: %.3f MW", power));
            me.debug_txt[3].setText(sprintf("DEC Current: %.3f A", amps));
            me.debug_txt[4].setText(sprintf("Q-Factor: %.2f", q));
        }
    }
};

var sys = ReactorUI.new();
