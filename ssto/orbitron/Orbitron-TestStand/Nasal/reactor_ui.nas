var ReactorUI = {
    new: func() {
        var m = { parents: [ReactorUI] };
        
        m.canvas = canvas.new({
            "name": "Reactor_Telemetry",
            "size":[1024, 1024],
            "view": [1024, 1024],
            "mipmapping": 1
        });

        # TARGETS THE 3D PLASTIC MONITOR INSTEAD OF A 2D WINDOW
        m.canvas.addPlacement({"node": "Screen"});
        m.root = m.canvas.createGroup();
        
        m.bg = m.root.createChild("path")
                     .rect(0, 0, 1024, 1024)
                     .setColorFill(0.05, 0.05, 0.05);

        m.root.createChild("text")
              .setText("p-B11 ORBITRON TELEMETRY")
              .setFontSize(55)
              .setColor(1, 0.8, 0) 
              .setAlignment("center-center")
              .setTranslation(512, 120);

        m.txt_nbi   = m.create_text(300, "NBI Flow: 0.00 sccm");
        m.txt_power = m.create_text(450, "Gross Power: 0.00 MW");
        m.txt_amps  = m.create_text(600, "DEC Current: 0.000 A");
        m.txt_heat  = m.create_text(750, "Brem. Heat: 0.00 kW");
        m.txt_q     = m.create_text(900, "Q-Factor: 0.00");

        m.timer = maketimer(0.1, m, ReactorUI.update);
        m.timer.start();
        
        return m;
    },
    
    create_text: func(y, initial_text) {
        return me.root.createChild("text")
                     .setText(initial_text)
                     .setFont("LiberationFonts/LiberationMono-Bold.ttf")
                     .setFontSize(50)
                     .setColor(0, 1, 0) 
                     .setAlignment("center-center")
                     .setTranslation(512, y);
    },

    update: func() {
        var nbi   = getprop("/controls/reactor/throttle") or 0.0;
        var power = getprop("/fdm/jsbsim/systems/reactor/gross-power-mw") or 0.0;
        var amps  = getprop("/fdm/jsbsim/systems/reactor/current-amps") or 0.0;
        var heat  = getprop("/fdm/jsbsim/systems/reactor/heat-kw") or 0.0;
        var q     = getprop("/fdm/jsbsim/systems/reactor/q-factor") or 0.0;

        var nbi_display = nbi * 100.0;

        me.txt_nbi.setText(sprintf("NBI Flow: %.2f sccm", nbi_display));
        me.txt_power.setText(sprintf("Gross Power: %.3f MW", power));
        me.txt_amps.setText(sprintf("DEC Current: %.3f A", amps));
        me.txt_heat.setText(sprintf("Brem. Heat: %.1f kW", heat));
        me.txt_q.setText(sprintf("Q-Factor: %.2f", q));
    }
};

var sys = ReactorUI.new();
