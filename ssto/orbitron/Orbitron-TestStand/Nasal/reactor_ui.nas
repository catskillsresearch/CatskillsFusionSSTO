var ReactorUI = {
    new: func() {
        var m = { parents: [ReactorUI] };
        
        # 1. Create a 1024x1024 Canvas texture
        m.canvas = canvas.new({
            "name": "Reactor_Telemetry",
            "size": [1024, 1024],
            "view": [1024, 1024],
            "mipmapping": 1
        });

        # 2. Place this Canvas texture ON the 3D model object named "Screen"
        m.canvas.addPlacement({"node": "Screen"});
        
        # 3. Create a drawing group
        m.root = m.canvas.createGroup();
        
        # Background
        m.bg = m.root.createChild("path")
                     .rect(0, 0, 1024, 1024)
                     .setColorFill(0.05, 0.05, 0.1);

        # Title
        m.root.createChild("text")
              .setText("p-B11 ORBITRON TELEMETRY")
              .setFontSize(50)
              .setColor(1, 0.8, 0) # Gold
              .setAlignment("center-center")
              .setTranslation(512, 100);

        # Telemetry Text Elements
        m.txt_nbi   = m.create_text(200, "NBI Flow: 0.00 sccm");
        m.txt_power = m.create_text(300, "Gross Power: 0.00 MW");
        m.txt_amps  = m.create_text(400, "DEC Current: 0.000 A");
        m.txt_heat  = m.create_text(500, "Brem. Heat: 0.00 kW");
        m.txt_q     = m.create_text(600, "Q-Factor: 0.00");

        # Render PIC Image
        # Make sure warpx_frame.png is in the Models folder
        m.pic_img = m.root.createChild("image")
                          .setFile("Aircraft/Orbitron-TestStand/Models/warpx_frame.png")
                          .setTranslation(200, 650)
                          .setSize(624, 350);

        # 4. Start Telemetry Update Loop
        m.timer = maketimer(0.1, m, ReactorUI.update);
        m.timer.start();
        
        return m;
    },
    
    create_text: func(y, initial_text) {
        return me.root.createChild("text")
                     .setText(initial_text)
                     .setFont("LiberationFonts/LiberationMono-Bold.ttf")
                     .setFontSize(40)
                     .setColor(0, 1, 0) # Green text
                     .setAlignment("center-center")
                     .setTranslation(512, y);
    },

    update: func() {
        # Fetch properties from JSBSim
        var nbi   = getprop("/fdm/jsbsim/systems/reactor/nbi-sccm") or 0.0;
        var power = getprop("/fdm/jsbsim/systems/reactor/gross-power-mw") or 0.0;
        var amps  = getprop("/fdm/jsbsim/systems/reactor/current-amps") or 0.0;
        var heat  = getprop("/fdm/jsbsim/systems/reactor/heat-kw") or 0.0;
        var q     = getprop("/fdm/jsbsim/systems/reactor/q-factor") or 0.0;

        # Update Canvas Text Elements
        me.txt_nbi.setText(sprintf("NBI Flow: %.2f sccm", nbi));
        me.txt_power.setText(sprintf("Gross Power: %.3f MW", power));
        me.txt_amps.setText(sprintf("DEC Current: %.3f A", amps));
        me.txt_heat.setText(sprintf("Brem. Heat: %.1f kW", heat));
        me.txt_q.setText(sprintf("Q-Factor: %.2f", q));
    }
};

# Initialize when Nasal loads
var sys = ReactorUI.new();