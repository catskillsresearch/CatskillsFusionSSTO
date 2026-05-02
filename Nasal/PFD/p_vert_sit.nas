#---------------------------------------
# SpaceShuttle PFD Page include:
#        Page: p_vert_sit
# Description: the vertical situation PFD page showing the TAEM guidance
#      Author: Thorsten Renk, 2015 // GinGin, 2020
#---------------------------------------

var PFD_addpage_p_vert_sit = func(device)
{
    var p_vert_sit = device.addPage("VertSit", "p_vert_sit");

    p_vert_sit.group = device.svg.getElementById("p_vert_sit");
    p_vert_sit.group.setColor(dps_r, dps_g, dps_b);
    
    p_vert_sit.speedbrake = device.svg.getElementById("p_vert_sit_speedbrake");
    p_vert_sit.speedbrake_cmd = device.svg.getElementById("p_vert_sit_speedbrake_cmd");
    p_vert_sit.tgt_Nz = device.svg.getElementById("p_vert_sit_tgt_Nz");
    p_vert_sit.tgt_Nz_label = device.svg.getElementById("p_vert_sit_tgt_Nz_label");

	#NZ in Yellow for mm 602 Nz Hold Phase 
    p_vert_sit.Nz_label = device.svg.getElementById("p_vert_sit_Nz_label");
	p_vert_sit.Nz_label.setColor(0.8, 0.8, 0.4);

    p_vert_sit.bailout = device.svg.getElementById("p_vert_sit_bailout");    
    p_vert_sit.ecal = device.svg.getElementById("p_vert_sit_ecal");    

    p_vert_sit.bfs = device.svg.getElementById("p_vert_sit_bfs");    
    p_vert_sit.bfs_roll_error = device.svg.getElementById("p_vert_sit_bfs_roll_error");    
    p_vert_sit.bfs_pitch_error = device.svg.getElementById("p_vert_sit_bfs_pitch_error");    
    p_vert_sit.bfs_yaw_error = device.svg.getElementById("p_vert_sit_bfs_yaw_error");    

	#Ny/Ail/Rud

	p_vert_sit.Ny = device.svg.getElementById("p_vert_sit_Ny"); 
	p_vert_sit.Ny_trim = device.svg.getElementById("p_vert_sit_Ny_trim"); 
	p_vert_sit.ail = device.svg.getElementById("p_vert_sit_ail"); 
	p_vert_sit.rud = device.svg.getElementById("p_vert_sit_rud"); 

	p_vert_sit.Ny_trim.enableUpdate();



	#Square Bracket

	p_vert_sit.tgt_Nz_hook = device.svg.getElementById("p_vert_sit_tgt_Nz_hook");   
	

    p_vert_sit.blink = 0;

    p_vert_sit.ondisplay = func
    {

		#Boundaries coming from svg

        #SpaceShuttle.fill_vert_sit1_nom_data();
        #SpaceShuttle.fill_vert_sit1_SB_data();
        #SpaceShuttle.fill_vert_sit1_maxLD_data();
        SpaceShuttle.traj_display_flag = 8;
        device.MEDS_menu_title.setText(sprintf("%s","      DPS MENU"));
        device.DPS_menu_title.setText(sprintf("%s","                 VERT SIT 1"));

	p_vert_sit.bailout.setVisible(0);

	p_vert_sit.major_func = SpaceShuttle.idp_array[device.port_selected-1].get_major_function();

	# switch BFS elements on and PASS elements off if we run BFS
	# tgt Nz label displays always in PASS (602---305) // never in BFS

	var major_mode = getprop("/fdm/jsbsim/systems/dps/major-mode");
       

	if (p_vert_sit.major_func == 4) #BFS
		{
		#No ending / for BFS
		device.DPS_menu_ops.setText(sprintf("%s", major_mode~"1/    "));
		p_vert_sit.bfs.setVisible(1);
		
		#No Tgt Nz label / ECAL for BFS
		p_vert_sit.tgt_Nz.setVisible(0);
		p_vert_sit.tgt_Nz_label.setVisible(0);
		p_vert_sit.tgt_Nz_hook.setVisible(0);
		p_vert_sit.ecal.setVisible(0);

		#No Aileron/rudder values display for BFS
		p_vert_sit.ail.setVisible(0);
		p_vert_sit.rud.setVisible(0);

		}
	else #PASS
		{

		#PASS common OPS1/6
		device.DPS_menu_ops.setText(sprintf("%s", major_mode~"1/   /"));
		p_vert_sit.bfs.setVisible(0);

		#Ail/rud
		p_vert_sit.ail.setVisible(1);
		p_vert_sit.rud.setVisible(1);

		#Tgt Nz label
		p_vert_sit.tgt_Nz_label.setVisible(1);
		p_vert_sit.tgt_Nz.setVisible(0);
		p_vert_sit.tgt_Nz_hook.setVisible(0);

		if ((major_mode == 602) or (major_mode == 603)) #OPS6
			{
			p_vert_sit.tgt_Nz.setVisible(1);
			p_vert_sit.tgt_Nz_hook.setVisible(1);
			p_vert_sit.ecal.setVisible(1);
			}		
		}
	

	# draw defaults

	p_vert_sit.Ny_trim.updateText(" .000");

	#Placeholder for now (Logic in ascent.nas)
	p_vert_sit.bfs_roll_error.setText("L00");
	p_vert_sit.bfs_pitch_error.setText("D00");
	p_vert_sit.bfs_yaw_error.setText("R00");



		#No need for vertical_traj.nas datas // hardcoded in svg now for boundaries

			#var plot = device.nom_traj_plot.createChild("path", "data")
			#.setStrokeLineWidth(2)
			#.setColor(1, 0, 0) #Red for nominal path
			#.moveTo(traj_data[0][0],traj_data[0][1]); 
		
			#for (var i = 1; i< (size(traj_data)-1); i=i+1)
			#{
			#    var set = traj_data[i+1];
			#    plot.lineTo(set[0], set[1]);	
			#}
		
			#var plot_limit1 = device.limit1_traj_plot.createChild("path", "data")
			#.setStrokeLineWidth(1)
			#.setColor(dps_r, dps_g, dps_b)
			#.moveTo(limit1_data[0][0],limit1_data[0][1]); 
		
			#for (var i = 1; i< (size(limit1_data)-1); i=i+1)
			#{
			#    var set = limit1_data[i+1];
			#    plot_limit1.lineTo(set[0], set[1]);	
			#}
		
			#var plot_limit2 = device.limit2_traj_plot.createChild("path", "data")
			#.setStrokeLineWidth(1)
			#.setColor(dps_r,dps_g,dps_b)
			#.moveTo(limit2_data[0][0],limit2_data[0][1]); 
		
			#for (var i = 1; i< (size(limit2_data)-1); i=i+1)
			#{
			#    var set = limit2_data[i+1];
			#    plot_limit2.lineTo(set[0], set[1]);	
			#}


	var data = SpaceShuttle.draw_shuttle_side();
	 
	p_vert_sit.shuttle_sym = device.symbols.createChild("path", "shuttle_sym")
        .setStrokeLineWidth(0.25)
        .setColor(0.8, 0.8, 0.4)
	.moveTo(data[0][0], data[0][1]);

	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_vert_sit.shuttle_sym.lineTo(set[0], set[1]);
		}

	p_vert_sit.shuttle_sym.setScale(3.5);

	data = SpaceShuttle.draw_tmarker_right();
	p_vert_sit.theta = device.symbols.createChild("path", "theta")
        .setStrokeLineWidth(1.0)
        .setColor(0.8, 0.8, 0.4)  # Yellow color for ladder markers
		.setScale(0.9, 0.7) 
	.moveTo(data[0][0], data[0][1]);

	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_vert_sit.theta.lineTo(set[0], set[1]);
		}

	data = SpaceShuttle.draw_tmarker_left();
	p_vert_sit.energy = device.symbols.createChild("path", "energy")
        .setStrokeLineWidth(1.0)
        .setColor(0.8, 0.8, 0.4)  # Yellow color for ladder markers
		.setScale(0.9, 0.7) 
	.moveTo(data[0][0], data[0][1]);

	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_vert_sit.energy.lineTo(set[0], set[1]);
		}


	#Nominal E/W

	data = SpaceShuttle.draw_rect(10, 0);
	p_vert_sit.energy_nom = device.symbols.createChild("path", "energy_nom")
        .setStrokeLineWidth(1.0)
        .setColor(0.8, 0.8, 0.4)  # Yellow color for ladder markers
		#.setScale(0.9, 0.7) 
	.moveTo(data[0][0], data[0][1]);

	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_vert_sit.energy_nom.lineTo(set[0], set[1]);
		}

	
	#Upper Nominal E/W (+8000 ft)

	data = SpaceShuttle.draw_rect(12, 0);
	p_vert_sit.energy_nom_upper = device.symbols.createChild("path", "energy_nom_upper")
        .setStrokeLineWidth(1.0)
		#.setColor(1, 0, 0)
        .setColor(0.8, 0.8, 0.4)  # Yellow color for ladder markers
		#.setScale(0.9, 0.7) 
	.moveTo(data[0][0], data[0][1]);

	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_vert_sit.energy_nom_upper.lineTo(set[0], set[1]);
		}

	
	#Lower Nominal E/W (-4000 ft)

	data = SpaceShuttle.draw_rect(12, 0);
	p_vert_sit.energy_nom_lower = device.symbols.createChild("path", "energy_nom_lower")
        .setStrokeLineWidth(1.0)
        .setColor(0.8, 0.8, 0.4)  # Yellow color for ladder markers
		#.setScale(0.9, 0.7) 
	.moveTo(data[0][0], data[0][1]);

	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_vert_sit.energy_nom_lower.lineTo(set[0], set[1]);
		}


	#Straight in reverting E/W cue

	data = SpaceShuttle.draw_arrowmarker_left();
	p_vert_sit.energy_stin = device.symbols.createChild("path", "energy_stin")
        .setStrokeLineWidth(1.0)
        .setColor(dps_r, dps_g, dps_b) # Green color
		.setScale(0.4, 1.0)
	.moveTo(data[0][0], data[0][1]);

	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_vert_sit.energy_stin.lineTo(set[0], set[1]);
		}

	#Alpha traj available for Vert Traj1, fed with datas only for RTLS/Contigency abort. Not displayed for Vert Traj2
	##Upper One is dashed (done in svg)

	var alpha_trajectories = device.symbols.createChild("group");

	#data = [[0.0, 0.0], [180.0,-35.0] ]; 
	#p_vert_sit.alpha_nom = device.symbols.createChild("path")
    #    .setStrokeLineWidth(1.0)
    #    .setColor(dps_r, dps_g, dps_b)
	#.setTranslation(30, 160)
	#.moveTo(data[0][0], data[0][1])
	#.lineTo(data[1][0], data[1][1]);

	data = [[0.0, 35.0], [30.0, 20.0], [180.0,-5.0] ]; 
	p_vert_sit.alpha_min = device.symbols.createChild("path")
        .setStrokeLineWidth(1.0)
        .setColor(dps_r, dps_g, dps_b)
	.setTranslation(30, 160)
	.moveTo(data[0][0], data[0][1])
	.lineTo(data[1][0], data[1][1])
	.lineTo(data[2][0], data[2][1]);

	#alpha_trajectories.setTranslation(20, 160);
	
	#if ((major_mode == 602) or (major_mode == 603))
		#{
		alpha_trajectories.setVisible(1);
		#}
	#else
		#{
		#alpha_trajectories.setVisible(0);
		#}

    
    }
    
    p_vert_sit.offdisplay = func
    {
        device.nom_traj_plot.removeAllChildren();
        device.limit1_traj_plot.removeAllChildren();
        device.limit2_traj_plot.removeAllChildren();
	device.symbols.removeAllChildren();
        device.set_DPS_off();
    }
    
    p_vert_sit.update = func
    {
    
        device.update_common_DPS();
    
    
    
    
    
        if (SpaceShuttle.TAEM_guidance_available == 1)
    	{
            var altitude = getprop("/position/altitude-ft") - SpaceShuttle.TAEM_threshold.elevation;
            var range = getprop("/fdm/jsbsim/systems/taem-guidance/distance-to-runway-nm");
            var x = SpaceShuttle.parameter_to_x(range, SpaceShuttle.traj_display_flag);
            var y = SpaceShuttle.parameter_to_y(altitude, SpaceShuttle.traj_display_flag);
    	
			#Traj 2 transition at Vert traj 1 boundaries

            if ((range < 10.0) or (altitude < 30000)) {device.selectPage(device.p_vert_sit2);}

		#Rotation of Shuttle

	    var vspeed = getprop("/velocities/vertical-speed-fps");
	    var mach = getprop("/velocities/mach");
	    if (mach< 0.5) {mach = 0.5;}	
	    var rot = vspeed * 0.0035 /mach;
	    rot = SpaceShuttle.clamp(rot, -1.57, 1.57);
	    p_vert_sit.shuttle_sym.setRotation(rot);
        p_vert_sit.shuttle_sym.setTranslation(x,y);

		#Energy Scale New (need TAEM guidance available for distance-to-runway defined)

			var EW_actual = getprop("/fdm/jsbsim/systems/entry_guidance/taem-EW-actual-ratio-ft");
			var EW_sturn = getprop("/fdm/jsbsim/systems/entry_guidance/taem-EW-sturn-ratio-ft");
			var EW_nominal = getprop("/fdm/jsbsim/systems/entry_guidance/taem-EW-nominal-ratio-ft");
			var EW_mep = getprop("/fdm/jsbsim/systems/entry_guidance/taem-EW-mep-ratio-ft");
			var EW_stin = getprop("/fdm/jsbsim/systems/entry_guidance/taem-EW-stin-ratio-ft");

			var dEW = EW_sturn - EW_mep;

	
			#Actual EW scale

			var frac_EW_ac = (EW_actual - EW_mep) / dEW;
			frac_EW_ac = SpaceShuttle.clamp(frac_EW_ac, -0.5, 1.5);
			p_vert_sit.energy.setTranslation(460,340 - frac_EW_ac * 112);


			#Nominal EW scale

			var frac_EW_nom = (EW_nominal - EW_mep) / dEW;
			frac_EW_nom = SpaceShuttle.clamp(frac_EW_nom, -0.5, 1.5);
			p_vert_sit.energy_nom.setTranslation(467,340 - frac_EW_nom * 112);

			#Nominal EW scale high (+8000ft)

			var frac_EW_nom_upper = ((EW_nominal + 8000) - EW_mep) / dEW;
			frac_EW_nom_upper = SpaceShuttle.clamp(frac_EW_nom_upper, -0.5, 1.5);
			p_vert_sit.energy_nom_upper.setTranslation(465,340 - frac_EW_nom_upper * 112);

			#Nominal EW scale low (-4000ft)

			var frac_EW_nom_lower = ((EW_nominal - 4000) - EW_mep) / dEW;
			frac_EW_nom_lower = SpaceShuttle.clamp(frac_EW_nom_lower, -0.5, 1.5);
			p_vert_sit.energy_nom_lower.setTranslation(465,340 - frac_EW_nom_lower * 112);

			#Stin reverting EW cue ( vanished below 45 Nm)

			if (range > 45)
				{
				p_vert_sit.energy_stin.setVisible(1);
				var frac_EW_stin = (EW_stin - EW_mep) / dEW;
				frac_EW_stin = SpaceShuttle.clamp(frac_EW_stin, 0, 1);
				p_vert_sit.energy_stin.setTranslation(460,340 - frac_EW_stin * 112);
				}
			else {p_vert_sit.energy_stin.setVisible(0);}
		}
	else if (getprop("/fdm/jsbsim/systems/ap/grtls/alpha-transition-active") == 1)
	{
	    var alpha = getprop("/fdm/jsbsim/aero/alpha-deg");
	    var mach = getprop("/velocities/mach");
	    

	    var x = 30.0 + 180 * (mach - 1.5)/4.5;	
	    var y = 160 - 25 * (alpha - 9.0)/14.0; 
	    p_vert_sit.shuttle_sym.setRotation(0.0);
            p_vert_sit.shuttle_sym.setTranslation(x,y);


	}

	#Pitch scale based on Max/Min theta from Entry Workbook (Subsonic only, would need a mach dependency to be more accurate)

	    var pitch = getprop("/orientation/pitch-deg");
		var max_theta = getprop("/fdm/jsbsim/systems/entry_guidance/taem-theta-max");
		var min_theta = getprop("/fdm/jsbsim/systems/entry_guidance/taem-theta-min");

		#var yp = 254.0 - (pitch -5.0) * 5.6;
	    var frac_theta = (pitch - min_theta) / (max_theta - min_theta);
		frac_theta = SpaceShuttle.clamp(frac_theta, -0.5, 1.5);
	    p_vert_sit.theta.setTranslation(458,340 - frac_theta * 112);


	#Energy Scale Old

	    #var dE = getprop("/fdm/jsbsim/systems/taem-guidance/dH-equiv-ft");
	    #dE = SpaceShuttle.clamp(dE, -20000.0, 20000.0);		
	    #var yde = 254.0 - dE/10000.0 * 28.;
	    #p_vert_sit.energy.setTranslation(459,yde);
		#p_vert_sit.energy_nom.setTranslation(465,228);

	
	#Speedbrakes

	p_vert_sit.speedbrake.setText(sprintf("%3.0f", 100.0 * getprop("/fdm/jsbsim/fcs/speedbrake-pos-norm")));
    p_vert_sit.speedbrake_cmd.setText(sprintf("%3.0f", 100.0 * getprop("/fdm/jsbsim/systems/fcs/speedbrake-cmd-norm")));


	# Nz holding phase

	if (getprop("/fdm/jsbsim/systems/ap/grtls/Nz-hold-active") == 1)
		{p_vert_sit.Nz_label.setVisible(1);}
	else
		{p_vert_sit.Nz_label.setVisible(0);}
    
	# Nz predictor
	
	if (getprop("/fdm/jsbsim/systems/dps/ops") == 6)
		{
		p_vert_sit.tgt_Nz.setText(sprintf("%+1.1f", getprop("/fdm/jsbsim/systems/ap/grtls/Nz-tgt")));

		}
	# bailout	

	var bailout_arm = getprop("/fdm/jsbsim/systems/abort/arm-bailout");
	var bailout_active = getprop("/fdm/jsbsim/systems/ap/auto-bailout-active");

	if (bailout_active == 1)
		{
		p_vert_sit.bailout.setVisible(1);
		p_vert_sit.bailout.setColor(0.8, 0.8, 0.4);
		}
	else if (bailout_arm == 1)
		{
		if (p_vert_sit.blink == 1)
			{
			p_vert_sit.bailout.setVisible(1);
			p_vert_sit.blink = 0;
			}
		else
			{
			p_vert_sit.bailout.setVisible(0);
			p_vert_sit.blink = 1;
			}
		}

	#Aileron/Rudder display ( elevons/rudder deflection instead of trim) // bfs sys summ 1 gnc logic and Ny

	p_vert_sit.Ny.setText(sprintf("%+5.2f", getprop("/fdm/jsbsim/accelerations/Ny")));

	var rudder_pos = getprop("/fdm/jsbsim/fcs/rudder-pos-rad");
	var aileron_pos = getprop("/fdm/jsbsim/fcs/left-aileron-pos-rad");

	var deflection_rudder = "";
	var deflection_aileron = "";

	if (rudder_pos > 0.0){deflection_rudder = "L";}
	else {deflection_rudder = "R";}
	p_vert_sit.rud.setText(deflection_rudder~sprintf("%03.1f", SpaceShuttle.clamp(abs(57.2974 * rudder_pos), 00.0, 27.1)));

	if (aileron_pos > 0.0){deflection_aileron = "R";}
	else {deflection_aileron = "L";}
	p_vert_sit.ail.setText(deflection_aileron~sprintf("%03.1f", SpaceShuttle.clamp(abs(57.2974 * aileron_pos), 00.0, 05.0)));

    
    };

return p_vert_sit;
}
    

var PFD_addpage_p_vert_sit2 = func(device)
{    

    
    var p_vert_sit2 = device.addPage("VertSit2", "p_vert_sit2");
    
    p_vert_sit2.speedbrake = device.svg.getElementById("p_vert_sit2_speedbrake");
    p_vert_sit2.group = device.svg.getElementById("p_vert_sit2");
    p_vert_sit2.group.setColor(dps_r, dps_g, dps_b);

    p_vert_sit2.speedbrake_cmd = device.svg.getElementById("p_vert_sit2_speedbrake_cmd");
    p_vert_sit2.tgt_Nz = device.svg.getElementById("p_vert_sit2_tgt_Nz");
    p_vert_sit2.tgt_Nz_label = device.svg.getElementById("p_vert_sit2_tgt_Nz_label");
	p_vert_sit2.accel = device.svg.getElementById("p_vert_sit2_accel");
    
	#Yellow Color for Bailout/AL

	p_vert_sit2.al_label = device.svg.getElementById("p_vert_sit2_al_label");
    p_vert_sit2.bailout = device.svg.getElementById("p_vert_sit2_bailout");
	p_vert_sit2.al_label.setColor(0.8, 0.8, 0.4);
	p_vert_sit2.bailout.setColor(0.8, 0.8, 0.4);

    p_vert_sit2.bfs = device.svg.getElementById("p_vert_sit2_bfs"); 
    p_vert_sit2.bfs_roll_error = device.svg.getElementById("p_vert_sit2_bfs_roll_error");    
    p_vert_sit2.bfs_pitch_error = device.svg.getElementById("p_vert_sit2_bfs_pitch_error");    
    p_vert_sit2.bfs_yaw_error = device.svg.getElementById("p_vert_sit2_bfs_yaw_error"); 

	#Ny/Ail/Rud

	p_vert_sit2.Ny = device.svg.getElementById("p_vert_sit2_Ny"); 
	p_vert_sit2.Ny_trim = device.svg.getElementById("p_vert_sit2_Ny_trim"); 
	p_vert_sit2.ail = device.svg.getElementById("p_vert_sit2_ail"); 
	p_vert_sit2.rud = device.svg.getElementById("p_vert_sit2_rud"); 

	p_vert_sit2.Ny_trim.enableUpdate();



	#Square Bracket

	p_vert_sit2.tgt_Nz_hook = device.svg.getElementById("p_vert_sit2_tgt_Nz_hook");   
	 

    p_vert_sit2.blink = 0;
    p_vert_sit2.bout_blink = 0;
    
    
    p_vert_sit2.ondisplay = func
    {
	p_vert_sit2.major_func = SpaceShuttle.idp_array[device.port_selected-1].get_major_function();

	# switch BFS elements on and PASS elements off if we run BFS
	# Nz/Accel displays always in PASS (602---305) // never in BFS

	var major_mode = getprop("/fdm/jsbsim/systems/dps/major-mode");

	if (p_vert_sit2.major_func == 4)
		{
		device.DPS_menu_ops.setText(major_mode~"1/    ");
		p_vert_sit2.bfs.setVisible(1);

		#Not Tgt Nz label/ accel for BFS
		p_vert_sit2.tgt_Nz.setVisible(0);
		p_vert_sit2.tgt_Nz_label.setVisible(0);
		p_vert_sit2.tgt_Nz_hook.setVisible(0);
		p_vert_sit2.accel.setVisible(0);

		#No Aileron/rudder values display for BFS
		p_vert_sit2.ail.setVisible(0);
		p_vert_sit2.rud.setVisible(0);
		}
	else
		{
		device.DPS_menu_ops.setText(major_mode~"1/   /");
		p_vert_sit2.bfs.setVisible(0);

		#Ail/rud
		p_vert_sit2.ail.setVisible(1);
		p_vert_sit2.rud.setVisible(1);

		#Tgt Nz label/accel
		p_vert_sit2.tgt_Nz_label.setVisible(1);
		p_vert_sit2.accel.setVisible(1);
		p_vert_sit2.tgt_Nz.setVisible(0);
		p_vert_sit2.tgt_Nz_hook.setVisible(0);


		if ((major_mode == 602) or (major_mode == 603))
			{
			p_vert_sit2.tgt_Nz.setVisible(1);
			p_vert_sit2.tgt_Nz_hook.setVisible(1);
			p_vert_sit2.tgt_Nz.setText(sprintf("%+4.1f", getprop("/fdm/jsbsim/systems/ap/grtls/Nz-tgt")));
			}
		}

	


		#Boundaries coming from svg
			#SpaceShuttle.fill_vert_sit2_nom_data();
			#SpaceShuttle.fill_vert_sit2_SB_data();
			#SpaceShuttle.fill_vert_sit2_maxLD_data();
			SpaceShuttle.traj_display_flag = 9;

        device.MEDS_menu_title.setText("      DPS MENU");
        device.DPS_menu_title.setText("                VERT SIT 2");

	p_vert_sit2.bailout.setVisible(0);
	#p_vert_sit2.bailout.setColor(0.8, 0.8, 0.4);

	# draw defaults

	p_vert_sit2.Ny_trim.updateText(" .000");
	p_vert_sit2.bfs_roll_error.setText("L00");
	p_vert_sit2.bfs_pitch_error.setText("D00");
	p_vert_sit2.bfs_yaw_error.setText("R00");



    #No need for vertical_traj.nas datas // hardcoded in svg now for boundaries

        #var plot = device.nom_traj_plot.createChild("path", "data")
        #.setStrokeLineWidth(2)
        #.setColor(1, 0, 0) #Red for nominal path for tests
        #.moveTo(traj_data[0][0],traj_data[0][1]); 
    
        #for (var i = 1; i< (size(traj_data)-1); i=i+1)
        #{
        #    var set = traj_data[i+1];
        #    plot.lineTo(set[0], set[1]);	
        #}
    
        #var plot_limit1 = device.limit1_traj_plot.createChild("path", "data")
        #.setStrokeLineWidth(1)
        #.setColor(dps_r, dps_g, dps_b)
        #.moveTo(limit1_data[0][0],limit1_data[0][1]); 
    
        #for (var i = 1; i< (size(limit1_data)-1); i=i+1)
        #{
        #    var set = limit1_data[i+1];
        #    plot_limit1.lineTo(set[0], set[1]);	
        #}
    
        #var plot_limit2 = device.limit2_traj_plot.createChild("path", "data")
        #.setStrokeLineWidth(1)
        #.setColor(dps_r, dps_g, dps_b)
        #.moveTo(limit2_data[0][0],limit2_data[0][1]); 
    
        #for (var i = 1; i< (size(limit2_data)-1); i=i+1)
        #{
        #    var set = limit2_data[i+1];
        #    plot_limit2.lineTo(set[0], set[1]);	
        #}

	var data = SpaceShuttle.draw_shuttle_side();
	 
	p_vert_sit2.shuttle_sym = device.symbols.createChild("path", "shuttle_sym")
        .setStrokeLineWidth(0.25)
        .setColor(0.8, 0.8, 0.4)
	.moveTo(data[0][0], data[0][1]);

	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_vert_sit2.shuttle_sym.lineTo(set[0], set[1]);
		}

	p_vert_sit2.shuttle_sym.setScale(3.5);

	data = SpaceShuttle.draw_tmarker_right();
	p_vert_sit2.theta = device.symbols.createChild("path", "theta")
        .setStrokeLineWidth(1.0)
        .setColor(0.8, 0.8, 0.4)
		.setScale(0.9, 0.7) 
	.moveTo(data[0][0], data[0][1]);

	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_vert_sit2.theta.lineTo(set[0], set[1]);
		}

	data = SpaceShuttle.draw_tmarker_left();
	p_vert_sit2.energy = device.symbols.createChild("path", "energy")
        .setStrokeLineWidth(1.0)
        .setColor(0.8, 0.8, 0.4)
		.setScale(0.9, 0.7) 
	.moveTo(data[0][0], data[0][1]);

	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_vert_sit2.energy.lineTo(set[0], set[1]);
		}

	#Nominal E/W

	data = SpaceShuttle.draw_rect(10, 0);
	p_vert_sit2.energy_nom = device.symbols.createChild("path", "energy_nom")
        .setStrokeLineWidth(1.0)
        .setColor(0.8, 0.8, 0.4)  # Yellow color for ladder markers
		#.setScale(0.9, 0.7) 
	.moveTo(data[0][0], data[0][1]);

	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_vert_sit2.energy_nom.lineTo(set[0], set[1]);
		}

	
	#Upper Nominal E/W (+8000 ft)

	data = SpaceShuttle.draw_rect(12, 0);
	p_vert_sit2.energy_nom_upper = device.symbols.createChild("path", "energy_nom_upper")
        .setStrokeLineWidth(1.0)
		#.setColor(1, 0, 0)
        .setColor(0.8, 0.8, 0.4)  # Yellow color for ladder markers
		#.setScale(0.9, 0.7) 
	.moveTo(data[0][0], data[0][1]);

	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_vert_sit2.energy_nom_upper.lineTo(set[0], set[1]);
		}

	
	#Lower Nominal E/W (-4000 ft)

	data = SpaceShuttle.draw_rect(12, 0);
	p_vert_sit2.energy_nom_lower = device.symbols.createChild("path", "energy_nom_lower")
        .setStrokeLineWidth(1.0)
        .setColor(0.8, 0.8, 0.4)  # Yellow color for ladder markers
		#.setScale(0.9, 0.7) 
	.moveTo(data[0][0], data[0][1]);

	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_vert_sit2.energy_nom_lower.lineTo(set[0], set[1]);
		}

    
    }
    
    p_vert_sit2.offdisplay = func
    {
        device.nom_traj_plot.removeAllChildren();
        device.limit1_traj_plot.removeAllChildren();
        device.limit2_traj_plot.removeAllChildren();
	device.symbols.removeAllChildren();
        #device.p_ascent_shuttle_sym.setScale(0.0);
        device.set_DPS_off();
    }
    
    p_vert_sit2.update = func
    {
    
        device.update_common_DPS();
    
    
    
        if (SpaceShuttle.TAEM_guidance_available == 1)
    	{
            var altitude = getprop("/position/altitude-ft") - SpaceShuttle.TAEM_threshold.elevation;
            var range = getprop("/fdm/jsbsim/systems/taem-guidance/distance-to-runway-nm");
            var x = SpaceShuttle.parameter_to_x(range, SpaceShuttle.traj_display_flag);
            var y = SpaceShuttle.parameter_to_y(altitude, SpaceShuttle.traj_display_flag);
    	
            var vspeed = getprop("/velocities/vertical-speed-fps");
	    var mach = getprop("/velocities/mach");
	    if (mach< 0.5) {mach = 0.5;}	
	    var rot = vspeed * 0.005 /mach * 0.6;
	    rot = SpaceShuttle.clamp(rot, -1.57, 1.57);
	    p_vert_sit2.shuttle_sym.setRotation(rot);
	    p_vert_sit2.shuttle_sym.setTranslation(x,y);

		#Energy Scale New (need TAEM guidance available for distance-to-runway defined)

			var EW_actual = getprop("/fdm/jsbsim/systems/entry_guidance/taem-EW-actual-ratio-ft");
			var EW_sturn = getprop("/fdm/jsbsim/systems/entry_guidance/taem-EW-sturn-ratio-ft");
			var EW_nominal = getprop("/fdm/jsbsim/systems/entry_guidance/taem-EW-nominal-ratio-ft");
			var EW_mep = getprop("/fdm/jsbsim/systems/entry_guidance/taem-EW-mep-ratio-ft");

			var dEW = EW_sturn - EW_mep;

		if (altitude > 20000) #E/W ladder
			{
			#Actual EW scale

			var frac_EW_ac = (EW_actual - EW_mep) / dEW;
			frac_EW_ac = SpaceShuttle.clamp(frac_EW_ac, -0.5, 1.5);
			p_vert_sit2.energy.setTranslation(460,340 - frac_EW_ac * 112);


			#Nominal EW scale

			var frac_EW_nom = (EW_nominal - EW_mep) / dEW;
			frac_EW_nom = SpaceShuttle.clamp(frac_EW_nom, -0.5, 1.5);
			p_vert_sit2.energy_nom.setTranslation(467,340 - frac_EW_nom * 112);

			#Nominal EW scale high (+8000ft)

			var frac_EW_nom_upper = ((EW_nominal + 8000) - EW_mep) / dEW;
			frac_EW_nom_upper = SpaceShuttle.clamp(frac_EW_nom_upper, -0.5, 1.5);
			p_vert_sit2.energy_nom_upper.setTranslation(465,340 - frac_EW_nom_upper * 112);

			#Nominal EW scale low (-4000ft)

			var frac_EW_nom_lower = ((EW_nominal - 4000) - EW_mep) / dEW;
			frac_EW_nom_lower = SpaceShuttle.clamp(frac_EW_nom_lower, -0.5, 1.5);
			p_vert_sit2.energy_nom_lower.setTranslation(465,340 - frac_EW_nom_lower * 112);
			}

		else # No more E/W ladder below 20 kft
			{
			p_vert_sit2.energy.setVisible(0);
			p_vert_sit2.energy_nom.setVisible(0);
			p_vert_sit2.energy_nom_lower.setVisible(0);
			p_vert_sit2.energy_nom_upper.setVisible(0);
			}

    	}

		#Pitch scale based on Max/Min theta from Entry Workbook

	    var pitch = getprop("/orientation/pitch-deg");
		var max_theta = getprop("/fdm/jsbsim/systems/entry_guidance/taem-theta-max");
		var min_theta = getprop("/fdm/jsbsim/systems/entry_guidance/taem-theta-min");

		#var yp = 254.0 - (pitch -5.0) * 5.6;
	    var frac_theta = (pitch - min_theta) / (max_theta - min_theta);
		frac_theta = SpaceShuttle.clamp(frac_theta, -0.5, 1.5);
	    p_vert_sit2.theta.setTranslation(458,340 - frac_theta * 112);



		#Energy Scale Old

			#var dE = getprop("/fdm/jsbsim/systems/taem-guidance/dH-equiv-ft");
			#dE = SpaceShuttle.clamp(dE, -20000.0, 20000.0);		
			#var yde = 254.0 - dE/10000.0 * 28.;
			#p_vert_sit2.energy.setTranslation(467,yde);

		#Speedbrakes
    
            p_vert_sit2.speedbrake.setText(sprintf("%3.0f", 100.0 * getprop("/fdm/jsbsim/fcs/speedbrake-pos-norm")));
            p_vert_sit2.speedbrake_cmd.setText(sprintf("%3.0f", 100.0 * getprop("/fdm/jsbsim/systems/fcs/speedbrake-cmd-norm")));

		#Aileron/Rudder display ( elevons/rudder deflection instead of trim) // bfs sys summ 1 gnc logic and Ny

		p_vert_sit2.Ny.setText(sprintf("%+5.2f", getprop("/fdm/jsbsim/accelerations/Ny")));

		var rudder_pos = getprop("/fdm/jsbsim/fcs/rudder-pos-rad");
		var aileron_pos = getprop("/fdm/jsbsim/fcs/left-aileron-pos-rad");

		var deflection_rudder = "";
		var deflection_aileron = "";

		if (rudder_pos > 0.0){deflection_rudder = "L";}
		else {deflection_rudder = "R";}
		p_vert_sit2.rud.setText(deflection_rudder~sprintf("%03.1f", SpaceShuttle.clamp(abs(57.2974 * rudder_pos), 00.0, 27.1)));

		if (aileron_pos > 0.0){deflection_aileron = "R";}
		else {deflection_aileron = "L";}
		p_vert_sit2.ail.setText(deflection_aileron~sprintf("%03.1f", SpaceShuttle.clamp(abs(57.2974 * aileron_pos), 00.0, 05.0)));


		#A/L blinking logic

	    if (getprop("/fdm/jsbsim/systems/ap/taem/al-init") == 1)
		{
		if (p_vert_sit2.blink == 0)	
			{
			p_vert_sit2.al_label.setVisible(1);
			p_vert_sit2.blink = 1;
			}
		else
			{
			p_vert_sit2.al_label.setVisible(0);
			p_vert_sit2.blink = 0;
			}
		}
	    else
		{
		p_vert_sit2.al_label.setVisible(0);
		}

	# bailout	

	var bailout_arm = getprop("/fdm/jsbsim/systems/abort/arm-bailout");
	var bailout_active = getprop("/fdm/jsbsim/systems/ap/auto-bailout-active");

	if (bailout_active == 1)
		{
		p_vert_sit2.bailout.setVisible(1);
		p_vert_sit2.bailout.setColor(0.8, 0.8, 0.4);
		}
	else if (bailout_arm == 1)
		{
		if (p_vert_sit2.bout_blink == 1)
			{
			p_vert_sit2.bailout.setVisible(1);
			p_vert_sit2.bout_blink = 0;
			}
		else
			{
			p_vert_sit2.bailout.setVisible(0);
			p_vert_sit2.bout_blink = 1;
			}
		}
		
    
    
    };
    
    
    
    return p_vert_sit2;
}
