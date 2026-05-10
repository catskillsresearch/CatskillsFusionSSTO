var ReactorUI = {
    new: func() {
        var m = { parents: [ReactorUI] };
        
        # Create a floating 2D Window on your screen
        m.window = canvas.Window.new([400, 350], "dialog").set("title", "p-B11 ORBITRON TELEMETRY");
        m.canvas = m.window.createCanvas();
        m.root = m.canvas.createGroup();
        
        # Dark translucent background
        m.root.createChild("path").rect(0, 0, 400, 350).setColorFill(0.05, 0.05, 0.1, 0.85);
        
        # Telemetry Text Elements
        m.txt_nbi   = m.create_text(50,  "NBI Flow: 0.00 sccm");
        m.txt_power = m.create_text(100, "Gross Power: 0.00 MW");
        m.txt_amps  = m.create_text(150, "DEC Current: 0.000 A");
        m.txt_heat  = m.create_text(200, "Brem. Heat: 0.00 kW");
        m.txt_q     = m.create_text(250, "Q-Factor: 0.00");

        # 10Hz Update Loop
        m.timer = maketimer(0.1, m, ReactorUI.update);
        m.timer.start();
        
        return m;
    },
    
    create_text: func(y, initial_text) {
        return me.root.createChild("text")
                     .setText(initial_text)
                     .setFont("LiberationFonts/LiberationMono-Bold.ttf")
                     .setFontSize(24)
                     .setColor(0, 1, 0) # Hacker Green
                     .setAlignment("left-center")
                     .setTranslation(30, y);
    },

    update: func() {
        # Fetch properties from JSBSim
        var nbi   = getprop("/fdm/jsbsim/systems/reactor/nbi-sccm") or 0.0;
        var power = getprop("/fdm/jsbsim/systems/reactor/gross-power-mw") or 0.0;
        var amps  = getprop("/fdm/jsbsim/systems/reactor/current-amps") or 0.0;
        var heat  = getprop("/fdm/jsbsim/systems/reactor/heat-kw") or 0.0;
        var q     = getprop("/fdm/jsbsim/systems/reactor/q-factor") or 0.0;

        # Update Canvas
        me.txt_nbi.setText(sprintf("NBI Flow: %.2f sccm", nbi));
        me.txt_power.setText(sprintf("Gross Power: %.3f MW", power));
        me.txt_amps.setText(sprintf("DEC Current: %.3f A", amps));
        me.txt_heat.setText(sprintf("Brem. Heat: %.1f kW", heat));
        me.txt_q.setText(sprintf("Q-Factor: %.2f", q));
    }
};

var sys = ReactorUI.new();