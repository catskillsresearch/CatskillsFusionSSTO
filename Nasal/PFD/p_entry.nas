#---------------------------------------
# SpaceShuttle PFD Page include:
#        Page: p_entry
# Description: the entry PFD page showing the vertical trajectory status
#      Author: Thorsten Renk, 2015 // GinGin, 2020
#---------------------------------------

var PFD_addpage_p_entry = func(device)
{
    var p_entry = device.addPage("Entry", "p_entry");

    p_entry.group = device.svg.getElementById("p_entry");
    p_entry.group.setColor(dps_r, dps_g, dps_b);
    
    p_entry.D_az = device.svg.getElementById("p_entry_D_az");
    p_entry.qbar = device.svg.getElementById("p_entry_qbar");
    p_entry.dref = device.svg.getElementById("p_entry_dref");
    p_entry.bias = device.svg.getElementById("p_entry_bias");
        
    p_entry.ny = device.svg.getElementById("p_entry_ny");   
    p_entry.ny_trim = device.svg.getElementById("p_entry_ny_trim");
    p_entry.ail_trim = device.svg.getElementById("p_entry_ail_trim");     
    p_entry.rud_trim = device.svg.getElementById("p_entry_rud_trim"); 
    p_entry.low_energy = device.svg.getElementById("p_entry_low_energy");
    p_entry.loe_label = device.svg.getElementById("p_entry_loe_label");

	#Hdot

	p_entry.hdot_bias = device.svg.getElementById("p_entry_hdot_bias");    
    p_entry.hdot_ref = device.svg.getElementById("p_entry_hdot_ref");
	p_entry.hdot_ref.enableUpdate();


	#Roll

	p_entry.roll_ref = device.svg.getElementById("p_entry_roll_ref");  
	p_entry.roll_cmd = device.svg.getElementById("p_entry_roll_cmd");  
	
    #Alpha/drag scale                   

    p_entry.alabel1 = device.svg.getElementById("p_entry_alabel1");
    p_entry.alabel2 = device.svg.getElementById("p_entry_alabel2");
    p_entry.alabel3 = device.svg.getElementById("p_entry_alabel3");
    p_entry.alabel4 = device.svg.getElementById("p_entry_alabel4");
    p_entry.alabel5 = device.svg.getElementById("p_entry_alabel5");
    p_entry.alabel6 = device.svg.getElementById("p_entry_alabel6");

	

    p_entry.pass = device.svg.getElementById("p_entry_pass");
    p_entry.bfs = device.svg.getElementById("p_entry_bfs");

    p_entry.bfs_roll_error = device.svg.getElementById("p_entry_bfs_roll_error");
    p_entry.bfs_pitch_error = device.svg.getElementById("p_entry_bfs_pitch_error");
    p_entry.bfs_yaw_error = device.svg.getElementById("p_entry_bfs_yaw_error");



	#Boundaries/drag lines subgroups

	p_entry.lines_traj1 = device.svg.getElementById("p_entry_lines_traj1");
	p_entry.lines_traj2 = device.svg.getElementById("p_entry_lines_traj2");
	p_entry.lines_traj3 = device.svg.getElementById("p_entry_lines_traj3");
	p_entry.lines_traj4 = device.svg.getElementById("p_entry_lines_traj4");
	p_entry.lines_traj5 = device.svg.getElementById("p_entry_lines_traj5");

	p_entry.lines_traj1.setVisible(0);
	p_entry.lines_traj2.setVisible(0);
	p_entry.lines_traj3.setVisible(0);
	p_entry.lines_traj4.setVisible(0);
	p_entry.lines_traj5.setVisible(0);



	#Shuttle marker blink while in a roll reversal
	p_entry.blink = 0;
	#Actual alpha marker blink if difference with required more than 2°
	p_entry.blink_alpha = 0;
	


    p_entry.ondisplay = func
    {
        # called once whenever this page goes on display
    
        p_entry.bias.setText("+00");
        device.MEDS_menu_title.setText("      DPS MENU");

	p_entry.major_func = SpaceShuttle.idp_array[device.port_selected-1].get_major_function();

	


	# draw defaults

	p_entry.ny_trim.setText(" .000");
	p_entry.ail_trim.setText(" 0.0");
	p_entry.rud_trim.setText(" 0.0");
	#p_entry.hdot_bias.setText("");
	#p_entry.hdot_ref.updateText("");

	# acquire the symbols we'd like to draw

	#Six trail symbols for Shuttle path history
	var data = SpaceShuttle.draw_triangle_down();
	
	 p_entry.marker1 = device.symbols.createChild("path", "m1")
        .setStrokeLineWidth(1)
        .setColor(0.8, 0.8, 0.4)
		.setScale(0.7, 1.20)
	.moveTo(data[0][0], data[0][1]);

	p_entry.marker2 = device.symbols.createChild("path", "m2")
        .setStrokeLineWidth(1)
        .setColor(0.8, 0.8, 0.4)
		.setScale(0.7, 1.20)
	.moveTo(data[0][0], data[0][1]);

	p_entry.marker3 = device.symbols.createChild("path", "m3")
        .setStrokeLineWidth(1)
        .setColor(0.8, 0.8, 0.4)
		.setScale(0.7, 1.20)
	.moveTo(data[0][0], data[0][1]);

	p_entry.marker4 = device.symbols.createChild("path", "m4")
        .setStrokeLineWidth(1)
        .setColor(0.8, 0.8, 0.4)
		.setScale(0.7, 1.20)
	.moveTo(data[0][0], data[0][1]);

	p_entry.marker5 = device.symbols.createChild("path", "m5")
        .setStrokeLineWidth(1)
        .setColor(0.8, 0.8, 0.4)
		.setScale(0.7, 1.20)
	.moveTo(data[0][0], data[0][1]);

	p_entry.marker6 = device.symbols.createChild("path", "m6")
        .setStrokeLineWidth(1)
        .setColor(0.8, 0.8, 0.4)
		.setScale(0.7, 1.20)
	.moveTo(data[0][0], data[0][1]);

	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_entry.marker1.lineTo(set[0], set[1]);
		p_entry.marker2.lineTo(set[0], set[1]);
		p_entry.marker3.lineTo(set[0], set[1]);
		p_entry.marker4.lineTo(set[0], set[1]);
		p_entry.marker5.lineTo(set[0], set[1]);
		p_entry.marker6.lineTo(set[0], set[1]);
		}

	setsize(data, 0);

	#Six trail symbols for guidance box
	var data = SpaceShuttle.draw_circle(1, 5);
	
	 p_entry.marker1_guidance_box = device.symbols.createChild("path", "m1_box")
        .setStrokeLineWidth(1)
        .setColor(0.8, 0.8, 0.4)
		.setScale(0.7, 1.20)
	.moveTo(data[0][0], data[0][1]);

	p_entry.marker2_guidance_box  = device.symbols.createChild("path", "m2_box")
        .setStrokeLineWidth(1)
        .setColor(0.8, 0.8, 0.4)
		.setScale(0.7, 1.20)
	.moveTo(data[0][0], data[0][1]);

	p_entry.marker3_guidance_box  = device.symbols.createChild("path", "m3_box")
        .setStrokeLineWidth(1)
        .setColor(0.8, 0.8, 0.4)
		.setScale(0.7, 1.20)
	.moveTo(data[0][0], data[0][1]);

	p_entry.marker4_guidance_box  = device.symbols.createChild("path", "m4_box")
        .setStrokeLineWidth(1)
        .setColor(0.8, 0.8, 0.4)
		.setScale(0.7, 1.20)
	.moveTo(data[0][0], data[0][1]);

	p_entry.marker5_guidance_box  = device.symbols.createChild("path", "m5_box")
        .setStrokeLineWidth(1)
        .setColor(0.8, 0.8, 0.4)
		.setScale(0.7, 1.20)
	.moveTo(data[0][0], data[0][1]);

	p_entry.marker6_guidance_box  = device.symbols.createChild("path", "m6_box")
        .setStrokeLineWidth(1)
        .setColor(0.8, 0.8, 0.4)
		.setScale(0.7, 1.20)
	.moveTo(data[0][0], data[0][1]);

	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_entry.marker1_guidance_box .lineTo(set[0], set[1]);
		p_entry.marker2_guidance_box .lineTo(set[0], set[1]);
		p_entry.marker3_guidance_box .lineTo(set[0], set[1]);
		p_entry.marker4_guidance_box .lineTo(set[0], set[1]);
		p_entry.marker5_guidance_box .lineTo(set[0], set[1]);
		p_entry.marker6_guidance_box .lineTo(set[0], set[1]);
		}

	setsize(data, 0);


	# switch BFS elements on and PASS elements off if we run BFS

	if (p_entry.major_func == 4)
		{
		p_entry.pass.setVisible(0);
		p_entry.bfs.setVisible(1);

		#Green History path in BFS

		p_entry.marker1.setColor(dps_r, dps_g, dps_b);
		p_entry.marker2.setColor(dps_r, dps_g, dps_b);
		p_entry.marker3.setColor(dps_r, dps_g, dps_b);
		p_entry.marker4.setColor(dps_r, dps_g, dps_b);
		p_entry.marker5.setColor(dps_r, dps_g, dps_b);
		p_entry.marker6.setColor(dps_r, dps_g, dps_b);

		p_entry.marker1_guidance_box.setColor(dps_r, dps_g, dps_b);
		p_entry.marker2_guidance_box.setColor(dps_r, dps_g, dps_b);
		p_entry.marker3_guidance_box.setColor(dps_r, dps_g, dps_b);
		p_entry.marker4_guidance_box.setColor(dps_r, dps_g, dps_b);
		p_entry.marker5_guidance_box.setColor(dps_r, dps_g, dps_b);
		p_entry.marker6_guidance_box.setColor(dps_r, dps_g, dps_b);

		#No ending / for BFS
		device.DPS_menu_ops.setText("3041/    ");
		
		}
	else
		{
		p_entry.pass.setVisible(1);
		p_entry.bfs.setVisible(0);
		device.DPS_menu_ops.setText("3041/   /");
		}



	data = SpaceShuttle.draw_shuttle_side();
	 
	p_entry.shuttle_sym = device.symbols.createChild("path", "shuttle_sym")
        .setStrokeLineWidth(0.25)
        .setColor(0.8, 0.8, 0.4)
	.moveTo(data[0][0], data[0][1]);

	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_entry.shuttle_sym.lineTo(set[0], set[1]);
		}

	p_entry.shuttle_sym.setScale(3.5);
	

	setsize(data,0);

	#Guidance Box
	data = SpaceShuttle.draw_rect(10, 10);
	 
	p_entry.shuttle_guidance_box = device.symbols.createChild("path", "shuttle_guidance_box")
        .setStrokeLineWidth(1.0)
        .setColor(0.8, 0.8, 0.4)
	.moveTo(data[0][0], data[0][1]);

	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_entry.shuttle_guidance_box.lineTo(set[0], set[1]);
		}

	setsize(data,0);

	data = SpaceShuttle.draw_tmarker_right();
	p_entry.alpha = device.symbols.createChild("path", "alpha")
        .setStrokeLineWidth(1.0)
        .setColor(0.8, 0.8, 0.4)  # Yellow color for alpha markers
		.setScale(0.9, 0.7)  
	.moveTo(data[0][0], data[0][1]);

	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_entry.alpha.lineTo(set[0], set[1]);
		}

	setsize(data,0);

	data = SpaceShuttle.draw_arrowmarker_right();
	p_entry.alpha_nom = device.symbols.createChild("path", "alpha_nom")
        .setStrokeLineWidth(1.0)
        .setColor(0.8, 0.8, 0.4) # Yellow color for alpha markers
		.setScale(0.4, 1.0)
	.moveTo(data[0][0], data[0][1]);

	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_entry.alpha_nom.lineTo(set[0], set[1]);
		}


	setsize(data,0);

	#Vertical ladder for Drag based on Alpha ladder logic

	data = SpaceShuttle.draw_tmarker_left();
	p_entry.drag = device.symbols.createChild("path", "drag")
        .setStrokeLineWidth(1.0)
        .setColor(0.8, 0.8, 0.4)  # Yellow color for alpha markers
		.setScale(0.9, 0.7)  
	.moveTo(data[0][0], data[0][1]);

	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_entry.drag.lineTo(set[0], set[1]);
		}

	setsize(data,0);

	data = SpaceShuttle.draw_arrowmarker_left();
	p_entry.drag_nom = device.symbols.createChild("path", "drag_nom")
        .setStrokeLineWidth(1.0)
        .setColor(0.8, 0.8, 0.4) # Yellow color for alpha markers
		.setScale(0.4, 1.0)
	.moveTo(data[0][0], data[0][1]);

	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_entry.drag_nom.lineTo(set[0], set[1]);
		}


	setsize(data,0);

	data = SpaceShuttle.draw_tmarker_down();
	p_entry.phug = device.symbols.createChild("path")
        .setStrokeLineWidth(1.0)
        .setColor(0.8, 0.8, 0.4)
		.setScale(0.7, 1.20)
	.moveTo(data[0][0], data[0][1]);

	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_entry.phug.lineTo(set[0], set[1]);
		}


	
	
    }
    
    p_entry.offdisplay = func
    {
        device.nom_traj_plot.removeAllChildren();
	
	device.symbols.removeAllChildren();
        device.set_DPS_off();
    }
    
    p_entry.update = func
    {
    
    
    
        device.update_common_DPS();
    
    
        device.nom_traj_plot.removeAllChildren();
    
        SpaceShuttle.ascent_traj_update_set();
    
        var major_mode = getprop("/fdm/jsbsim/systems/dps/major-mode");
	if (SpaceShuttle.bfs_in_control == 1)
		{
		major_mode = getprop("/fdm/jsbsim/systems/dps/major-mode-bfs");
		}
    
	var alpha_max = 50.0;
	var alpha_min = 25.0;
    
        if  ((SpaceShuttle.traj_display_flag == 3) and (major_mode == 304))
    	{
            device.DPS_menu_title.setText("                 ENTRY TRAJ 1");
			p_entry.lines_traj1.setVisible(1);
			p_entry.lines_traj2.setVisible(0);
			p_entry.lines_traj3.setVisible(0);
			p_entry.lines_traj4.setVisible(0);
			p_entry.lines_traj5.setVisible(0);
			
			

    	}
        else if ((SpaceShuttle.traj_display_flag == 4) and (major_mode == 304))
    	{
            device.DPS_menu_title.setText("                 ENTRY TRAJ 2");
	    	p_entry.lines_traj1.setVisible(0);
			p_entry.lines_traj2.setVisible(1);
			p_entry.lines_traj3.setVisible(0);
			p_entry.lines_traj4.setVisible(0);
			p_entry.lines_traj5.setVisible(0);

    	}
        else if ((SpaceShuttle.traj_display_flag == 5) and (major_mode == 304))
    	{
            device.DPS_menu_title.setText("                 ENTRY TRAJ 3");
	    p_entry.alabel1.setText("45");
	    p_entry.alabel2.setText("40");
	    p_entry.alabel3.setText("35");
	    p_entry.alabel4.setText("30");
	    p_entry.alabel5.setText("25");
	    p_entry.alabel6.setText("20");
	    alpha_max = 45.0;
	    alpha_min = 20.0;

		p_entry.lines_traj1.setVisible(0);
		p_entry.lines_traj2.setVisible(0);
		p_entry.lines_traj3.setVisible(1);
		p_entry.lines_traj4.setVisible(0);
		p_entry.lines_traj5.setVisible(0);

    	}
        else if (( SpaceShuttle.traj_display_flag == 6) and (major_mode == 304))
    	{
            device.DPS_menu_title.setText("                  ENTRY TRAJ 4");
	    p_entry.alabel1.setText("45");
	    p_entry.alabel2.setText("40");
	    p_entry.alabel3.setText("35");
	    p_entry.alabel4.setText("30");
	    p_entry.alabel5.setText("25");
	    p_entry.alabel6.setText("20");
	    alpha_max = 45.0;
	    alpha_min = 20.0;

		p_entry.lines_traj1.setVisible(0);
		p_entry.lines_traj2.setVisible(0);
		p_entry.lines_traj3.setVisible(0);
		p_entry.lines_traj4.setVisible(1);
		p_entry.lines_traj5.setVisible(0);
    	}
        else if ((SpaceShuttle.traj_display_flag == 7)and (major_mode == 304))
    	{
            device.DPS_menu_title.setText("                 ENTRY TRAJ 5");
	    p_entry.alabel1.setText("30");
	    p_entry.alabel2.setText("25");
	    p_entry.alabel3.setText("20");
	    p_entry.alabel4.setText("15");
	    p_entry.alabel5.setText("10");
	    p_entry.alabel6.setText(" 5");
	    alpha_max = 30.0;
	    alpha_min = 5.0;

		p_entry.lines_traj1.setVisible(0);
		p_entry.lines_traj2.setVisible(0);
		p_entry.lines_traj3.setVisible(0);
		p_entry.lines_traj4.setVisible(0);
		p_entry.lines_traj5.setVisible(1);
    	}
    
    
		#Entry nominal traj data (removed but logic kept to fine tune the range/velocity scales if needed)
    
        #var plot = device.nom_traj_plot.createChild("path", "data")
        #.setStrokeLineWidth(2)
        #.setColor(1, 0, 0)
        #.moveTo(traj_data[0][0],traj_data[0][1]); 
    
        #for (var i = 1; i< (size(traj_data)-1); i=i+1)
        #{
        #    var set = traj_data[i+1];
        #    plot.lineTo(set[0], set[1]);	
        #}



    
		#Vrel velocity for OPS 3
		
		
        var velocity_rel = getprop("/fdm/jsbsim/velocities/vtrue-fps");
        var altitude = getprop("/position/altitude-ft");
    
	#Alpha ladder

	var alpha_act = getprop("/fdm/jsbsim/aero/alpha-deg");
	var alpha_nom = getprop("/fdm/jsbsim/systems/ap/entry/drag-target-alpha-rad") * 57.2958;
	#var alpha_nom = getprop("/fdm/jsbsim/systems/ap/entry/drag-target-alpha-rad") * 180.0/math.pi;

	alpha_act = SpaceShuttle.clamp(alpha_act, alpha_min, alpha_max);
	alpha_nom = SpaceShuttle.clamp(alpha_nom, alpha_min, alpha_max);

	var alpha_fract = (alpha_act - alpha_min)/(alpha_max - alpha_min);
	var alpha_nom_fract = (alpha_nom - alpha_min)/(alpha_max - alpha_min);

	p_entry.alpha.setTranslation(39.26, 362.5 - 272.5 * alpha_fract); # minus 4.92 Dx  plus 2.5 Dy
	p_entry.alpha_nom.setTranslation(40.0, 362.5 - 272.5 * alpha_nom_fract);


	#Drag ladder

	var drag_act = getprop("/fdm/jsbsim/systems/entry_guidance/aero-drag-deceleration-fts");
	var drag_nom = getprop("/fdm/jsbsim/systems/entry_guidance/drag-required"); #Drag required to stay or get back on Nominal Path

	drag_act = SpaceShuttle.clamp(drag_act, 0, 50);
	drag_nom = SpaceShuttle.clamp(drag_nom, 0, 50);


	var drag_fract = drag_act / 50;
	var drag_nom_fract = drag_nom / 50;

	p_entry.drag.setTranslation(39.26, 362.5 - 272.5 * drag_fract); # minus 4.92 Dx  plus 2.5 Dy
	p_entry.drag_nom.setTranslation(40.0, 362.5 - 272.5 * drag_nom_fract);

	#Phugoid Roll ladder

	var roll = getprop("/orientation/roll-deg");
	var roll_error = getprop("/fdm/jsbsim/systems/ap/entry/bank-angle-target-deg") - roll;
	roll_error = SpaceShuttle.clamp(roll_error, -30.0, 30.0);	

	#Translation +/- 60
	p_entry.phug.setTranslation(170.0 + 2.0 * roll_error, 80.0);
    
        var range = getprop("/fdm/jsbsim/systems/entry_guidance/remaining-distance-nm");

	
	#Shuttle Path Marker
        var x = SpaceShuttle.parameter_to_x(range, SpaceShuttle.traj_display_flag);
        var y = SpaceShuttle.parameter_to_y(velocity_rel, SpaceShuttle.traj_display_flag);
	p_entry.shuttle_sym.setTranslation(x, y);

	x = SpaceShuttle.parameter_to_x(SpaceShuttle.trailer_set.entry[0][0], SpaceShuttle.traj_display_flag);
	y = SpaceShuttle.parameter_to_y(SpaceShuttle.trailer_set.entry[0][1], SpaceShuttle.traj_display_flag);
    	p_entry.marker1.setTranslation(x,y);

	x = SpaceShuttle.parameter_to_x(SpaceShuttle.trailer_set.entry[1][0], SpaceShuttle.traj_display_flag);
	y = SpaceShuttle.parameter_to_y(SpaceShuttle.trailer_set.entry[1][1], SpaceShuttle.traj_display_flag);
    	p_entry.marker2.setTranslation(x,y);

	x = SpaceShuttle.parameter_to_x(SpaceShuttle.trailer_set.entry[2][0], SpaceShuttle.traj_display_flag);
	y = SpaceShuttle.parameter_to_y(SpaceShuttle.trailer_set.entry[2][1], SpaceShuttle.traj_display_flag);
    	p_entry.marker3.setTranslation(x,y);

	x = SpaceShuttle.parameter_to_x(SpaceShuttle.trailer_set.entry[3][0], SpaceShuttle.traj_display_flag);
	y = SpaceShuttle.parameter_to_y(SpaceShuttle.trailer_set.entry[3][1], SpaceShuttle.traj_display_flag);
    	p_entry.marker4.setTranslation(x,y);

	x = SpaceShuttle.parameter_to_x(SpaceShuttle.trailer_set.entry[4][0], SpaceShuttle.traj_display_flag);
	y = SpaceShuttle.parameter_to_y(SpaceShuttle.trailer_set.entry[4][1], SpaceShuttle.traj_display_flag);
    	p_entry.marker5.setTranslation(x,y);

	x = SpaceShuttle.parameter_to_x(SpaceShuttle.trailer_set.entry[5][0], SpaceShuttle.traj_display_flag);
	y = SpaceShuttle.parameter_to_y(SpaceShuttle.trailer_set.entry[5][1], SpaceShuttle.traj_display_flag);
    	p_entry.marker6.setTranslation(x,y);
		

	
        

	#Closed loop init (Q bar > 8 psi or Drag actual > 3 fts²)

	var drag_init = getprop("/fdm/jsbsim/systems/ap/entry/drag-management-init"); #Trigger for entry guidance closed loop start ( Drag 3ft.s² or 8 lb.ft²)
	
	if (drag_init == 0)
		{
		p_entry.hdot_bias.setVisible(0);
		p_entry.hdot_ref.setVisible(0);
		p_entry.roll_ref.setVisible(0);
		p_entry.roll_cmd.setVisible(0);
		p_entry.drag_nom.setVisible(0);
		p_entry.drag.setVisible(0);
		
		}
	else
		{
		p_entry.hdot_bias.setVisible(1);
		p_entry.hdot_ref.setVisible(1);
		p_entry.roll_ref.setVisible(1);
		p_entry.roll_cmd.setVisible(1);
		p_entry.drag_nom.setVisible(1);
		p_entry.drag.setVisible(1);
		
		#Guidance Box Marker available when guidance is in Closed Loop mode
		var drag_ratio = 1 + (drag_act - drag_nom) / (drag_act + drag_nom);
        var x = SpaceShuttle.parameter_to_x(drag_ratio * range, SpaceShuttle.traj_display_flag);
        var y = SpaceShuttle.parameter_to_y(velocity_rel, SpaceShuttle.traj_display_flag);
		p_entry.shuttle_guidance_box.setTranslation(x, y);

		x = SpaceShuttle.parameter_to_x(SpaceShuttle.trailer_set.entry_box[0][0], SpaceShuttle.traj_display_flag);
		y = SpaceShuttle.parameter_to_y(SpaceShuttle.trailer_set.entry_box[0][1], SpaceShuttle.traj_display_flag);
			p_entry.marker1_guidance_box.setTranslation(x,y);

		x = SpaceShuttle.parameter_to_x(SpaceShuttle.trailer_set.entry_box[1][0], SpaceShuttle.traj_display_flag);
		y = SpaceShuttle.parameter_to_y(SpaceShuttle.trailer_set.entry_box[1][1], SpaceShuttle.traj_display_flag);
			p_entry.marker2_guidance_box.setTranslation(x,y);

		x = SpaceShuttle.parameter_to_x(SpaceShuttle.trailer_set.entry_box[2][0], SpaceShuttle.traj_display_flag);
		y = SpaceShuttle.parameter_to_y(SpaceShuttle.trailer_set.entry_box[2][1], SpaceShuttle.traj_display_flag);
			p_entry.marker3_guidance_box.setTranslation(x,y);

		x = SpaceShuttle.parameter_to_x(SpaceShuttle.trailer_set.entry_box[3][0], SpaceShuttle.traj_display_flag);
		y = SpaceShuttle.parameter_to_y(SpaceShuttle.trailer_set.entry_box[3][1], SpaceShuttle.traj_display_flag);
			p_entry.marker4_guidance_box.setTranslation(x,y);

		x = SpaceShuttle.parameter_to_x(SpaceShuttle.trailer_set.entry_box[4][0], SpaceShuttle.traj_display_flag);
		y = SpaceShuttle.parameter_to_y(SpaceShuttle.trailer_set.entry_box[4][1], SpaceShuttle.traj_display_flag);
			p_entry.marker5_guidance_box.setTranslation(x,y);

		x = SpaceShuttle.parameter_to_x(SpaceShuttle.trailer_set.entry_box[5][0], SpaceShuttle.traj_display_flag);
		y = SpaceShuttle.parameter_to_y(SpaceShuttle.trailer_set.entry_box[5][1], SpaceShuttle.traj_display_flag);
			p_entry.marker6_guidance_box.setTranslation(x,y);
		}

	#Phugoid Damper

	p_entry.D_az.setText(sprintf("%+5.2f",getprop("/fdm/jsbsim/systems/entry_guidance/delta-azimuth-deg")));
    p_entry.qbar.setText(sprintf("%5.1f",getprop("/fdm/jsbsim/aero/qbar-psf")));

	#Dref phugoid display based on Drag experienced if on nominal path (dont take into account if we are high/low energy)
	#Drag ref = Function(nominal Vrel) // Cue Card Entry
	p_entry.dref.setText(sprintf("%4.1f", getprop("/fdm/jsbsim/systems/entry_guidance/nominal-dref")));
		


	#Roll logic

	var bank_ref = getprop("/fdm/jsbsim/systems/ap/entry/bank-angle-target-deg"); #Guidance bank calculated (ref)
	#var roll_abs = getprop("/fdm/jsbsim/systems/ap/entry/roll-abs-deg"); #Roll real ( commanded by guidance)
	var bank_cmd = getprop("/fdm/jsbsim/systems/navigation/state-vector/roll-deg"); #Roll real ( commanded by guidance)
	var bank_ref_sign = "";
	var bank_cmd_sign = "";
	

	if (bank_ref > 1) {bank_ref_sign = "R";}
	else {bank_ref_sign = "L";}

	if (bank_cmd > 1) {bank_cmd_sign = "R";}
	else {bank_cmd_sign = "L";}

	p_entry.roll_ref.setText(bank_ref_sign~sprintf("%03d", abs(bank_ref))); 
	p_entry.roll_cmd.setText(bank_cmd_sign~sprintf("%03d", abs(bank_cmd)));



	#H dot logic
    
	var vspeed_target = -getprop("/fdm/jsbsim/systems/ap/entry/vspeed-target-fps"); #vspeed calculated by guidance (ref)
	var hdot_fps = getprop("/fdm/jsbsim/velocities/h-dot-fps");
	var vspeed_bias = vspeed_target - hdot_fps; 
	var hdot_ref = -getprop("/fdm/jsbsim/systems/entry_guidance/nominal-hdot-target-href");

	p_entry.hdot_bias.setText(sprintf("%+4.0f", vspeed_bias)); #bias (vspeed calculated by guidance minus actual vspeed)
	p_entry.hdot_ref.setText(sprintf("%+4.0f", hdot_ref)); #ref (hdot if on nominal profile / hdotref = function(range nominal))


	#Ny/Aileron/Rudder display ( elevons/rudder deflection instead of trim) // bfs sys summ 1 gnc logic


	var rudder_pos = getprop("/fdm/jsbsim/fcs/rudder-pos-rad");
	var aileron_pos = getprop("/fdm/jsbsim/fcs/left-aileron-pos-rad");

	var deflection_rudder = "";
	var deflection_aileron = "";

	p_entry.ny.setText(sprintf("%+5.2f", getprop("/fdm/jsbsim/accelerations/Ny")));

	if (rudder_pos > 0.0){deflection_rudder = "L";}
	else {deflection_rudder = "R";}
	p_entry.rud_trim.setText(deflection_rudder~sprintf("%04.1f", SpaceShuttle.clamp(abs(57.2974 * rudder_pos), 00.0, 27.1)));

	if (aileron_pos > 0.0){deflection_aileron = "R";}
	else {deflection_aileron = "L";}
	p_entry.ail_trim.setText(deflection_aileron~sprintf("%04.1f", SpaceShuttle.clamp(abs(57.2974 * aileron_pos), 00.0, 05.0)));
	
	
	#Blink Logic for shuttle marker when in a roll reversal (p_entry.shuttle_sym)

	var roll_reversal = getprop("/fdm/jsbsim/systems/ap/entry/roll-reversal-init");

	if (roll_reversal == 1)
		{
		if (p_entry.blink == 0)
		 	{
		 	p_entry.shuttle_sym.setVisible(0);
			p_entry.blink = 1;
			}
		else 
			{
		 	p_entry.shuttle_sym.setVisible(1);
			p_entry.blink = 0;
			}
			
		}
	else {p_entry.shuttle_sym.setVisible(1);}


	#Blink Logic for alpha marker if different than required one by more than 2° (Alpha modulation during roll reversals mainly)

	if (math.abs(alpha_act - alpha_nom) > 2)
		{
		if (p_entry.blink_alpha == 0)
		 	{
		 	p_entry.alpha.setVisible(0);
			p_entry.blink_alpha = 1;
			}
		else 
			{
		 	p_entry.alpha.setVisible(1);
			p_entry.blink_alpha = 0;
			}
			
		}
	else {p_entry.alpha.setVisible(1);}


	if (p_entry.major_func == 4) # we drive the BFS-specific items
		{
		if (SpaceShuttle.bfs_in_control == 0)
			{
		
			var roll = getprop("/orientation/roll-deg");
			var roll_error = roll - getprop("/fdm/jsbsim/systems/ap/entry/bank-angle-target-deg");
			var pitch_error = getprop("/fdm/jsbsim/systems/ap/alpha-error") * 180.0/math.pi;
			var yaw_error = getprop("/fdm/jsbsim/aero/beta-deg");

			p_entry.bfs_roll_error.setText(sprintf("%+03.0f", roll_error));
			p_entry.bfs_pitch_error.setText(sprintf("%+03.0f", pitch_error));
			p_entry.bfs_yaw_error.setText(sprintf("%+03.0f", yaw_error));

			}
		else
			{
			p_entry.bfs.setVisible(0);
			}

		}
	else # we drive PASS
		{
		var low_energy = getprop("/fdm/jsbsim/systems/ap/entry/low-energy-logic");

		if (low_energy == 0) 
			{
			p_entry.low_energy.setText(" INH");
			p_entry.loe_label.setColor(dps_r, dps_g, dps_b);
			}
		else 
			{
			p_entry.low_energy.setText(" ENA");
			p_entry.loe_label.setColor(0.8, 0.8, 0.4);
			}	
		}
	


    };
    
    
    
    return p_entry;
}
