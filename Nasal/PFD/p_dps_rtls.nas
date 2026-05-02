#---------------------------------------
# SpaceShuttle PFD Page include:
#        Page: p_dps_rtls
# Description: the RTLS TRAJ 2
#      Author: Thorsten Renk, 2016 // GinGin, 2020
#---------------------------------------

var PFD_addpage_p_dps_rtls = func(device)
{
    var p_dps_rtls = device.addPage("CRTRTLS", "p_dps_rtls");

    p_dps_rtls.group = device.svg.getElementById("p_dps_rtls");
    p_dps_rtls.group.setColor(dps_r, dps_g, dps_b);

    p_dps_rtls.throttle = device.svg.getElementById("p_dps_rtls_throttle");
    p_dps_rtls.throttle_text = device.svg.getElementById("p_dps_rtls_throttle_txt");
    
    p_dps_rtls.prplt = device.svg.getElementById("p_dps_rtls_prplt");
    p_dps_rtls.prplt_text = device.svg.getElementById("p_dps_rtls_prplt_txt");

    p_dps_rtls.guid = device.svg.getElementById("p_dps_rtls_guid");

    p_dps_rtls.vco  = device.svg.getElementById("p_dps_rtls_vco");
    p_dps_rtls.vcoscale_co = device.svg.getElementById("p_dps_rtls_vcoscale_co");
    p_dps_rtls.vcoscale_labelco = device.svg.getElementById("p_dps_rtls_vcoscale_labelco");   

    p_dps_rtls.serc = device.svg.getElementById("p_dps_rtls_serc");
    p_dps_rtls.serc_on = device.svg.getElementById("p_dps_rtls_serc_on");

    p_dps_rtls.yaw_steer = device.svg.getElementById("p_dps_rtls_yaw_steer");
    p_dps_rtls.abort = device.svg.getElementById("p_dps_rtls_abort");
    p_dps_rtls.arm = device.svg.getElementById("p_dps_rtls_arm");

    p_dps_rtls.abort_region = device.svg.getElementById("p_dps_rtls_2EO_abort_region");
    p_dps_rtls.abort_region_3eo = device.svg.getElementById("p_dps_rtls_3EO_abort_region");

    p_dps_rtls.abort_region.enableUpdate();
    p_dps_rtls.abort_region_3eo.enableUpdate();

    p_dps_rtls.engine1_fail_vi = device.svg.getElementById("p_dps_rtls_engine1_fail_vi");
    p_dps_rtls.engine2_fail_vi = device.svg.getElementById("p_dps_rtls_engine2_fail_vi");

	#TMECO and TGO on RTLS Pass display

	p_dps_rtls.tmeco_txt = device.svg.getElementById("p_dps_rtls_tmeco_txt");
    p_dps_rtls.tmeco = device.svg.getElementById("p_dps_rtls_tmeco");

    p_dps_rtls.tmeco_txt.enableUpdate();
    #p_dps_rtls.tmeco.enableUpdate();

	p_dps_rtls.tgo_txt = device.svg.getElementById("p_dps_rtls_tgo_txt");
    p_dps_rtls.tgo = device.svg.getElementById("p_dps_rtls_tgo");

    p_dps_rtls.tgo_txt.enableUpdate();
    #p_dps_rtls.tgo.enableUpdate();


	#Group elements for better BFS/PASS handling

	p_dps_rtls.bfs_group = device.svg.getElementById("p_dps_rtls_bfs");
	p_dps_rtls.pass_group = device.svg.getElementById("p_dps_rtls_pass");


	#BFS elements that are driven by same parameters than PASS parameters ( Prplt, guid,Tmeco, throt)

	p_dps_rtls.tmeco_txt_bfs = device.svg.getElementById("p_dps_rtls_tmeco_txt_bfs");
    p_dps_rtls.tmeco_bfs = device.svg.getElementById("p_dps_rtls_tmeco_bfs");

	p_dps_rtls.tmeco_txt_bfs.enableUpdate();
    #p_dps_rtls.tmeco_bfs.enableUpdate();


	p_dps_rtls.throttle_bfs = device.svg.getElementById("p_dps_rtls_throttle_bfs");
    p_dps_rtls.throttle_text_bfs = device.svg.getElementById("p_dps_rtls_throttle_txt_bfs");
    
    p_dps_rtls.prplt_bfs = device.svg.getElementById("p_dps_rtls_prplt_bfs");
    p_dps_rtls.prplt_text_bfs = device.svg.getElementById("p_dps_rtls_prplt_txt_bfs");

	p_dps_rtls.guid_bfs = device.svg.getElementById("p_dps_rtls_guid_bfs");


	#Specific BFS elements (alpha, beta, Hdot, ppa active, alpha ladder, G's ladder, RPY error)

	p_dps_rtls.H_dot_bfs = device.svg.getElementById("p_dps_rtls_H_dot_bfs");
	p_dps_rtls.H_dot_bfs.enableUpdate();

	p_dps_rtls.alpha_bfs = device.svg.getElementById("p_dps_rtls_alpha_bfs");
	p_dps_rtls.alpha_bfs.enableUpdate();

	p_dps_rtls.beta_bfs = device.svg.getElementById("p_dps_rtls_beta_bfs");
	p_dps_rtls.beta_bfs.enableUpdate();
	
	p_dps_rtls.ppa_bfs = device.svg.getElementById("p_dps_rtls_ppa_bfs");
	p_dps_rtls.ppa_bfs.enableUpdate();

	p_dps_rtls.bfs_roll_error = device.svg.getElementById("p_dps_rtls_bfs_roll_error");
    p_dps_rtls.bfs_pitch_error = device.svg.getElementById("p_dps_rtls_bfs_pitch_error");
    p_dps_rtls.bfs_yaw_error = device.svg.getElementById("p_dps_rtls_bfs_yaw_error");

		#Font B for g ladder bfs

	p_dps_rtls.bfs_label_g = device.svg.getElementById("p_dps_rtls_bfs_label_g");
	p_dps_rtls.bfs_label_g.setFont(p_pfd_font_2);

    
    p_dps_rtls.ondisplay = func
    {
	
	#Translation capability of RTLS traj shape

	var downshift = -50.0;
	var rightshift = -20.0;


	# generate the symbols for the graphical part of the display

	var data = SpaceShuttle.draw_triangle_up();
	
	 p_dps_rtls.shuttle_marker = device.symbols.createChild("path", "shuttle_marker")
        .setStrokeLineWidth(2)
        .setColor(0.8, 0.8, 0.4)
		.setScale(0.7, 1.20)
		.setTranslation(rightshift,downshift)
	.moveTo(data[0][0], data[0][1]);

 	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_dps_rtls.shuttle_marker.lineTo(set[0], set[1]);
		}

	setsize(data,0);

	data = SpaceShuttle.draw_circle(3, 10);

	p_dps_rtls.pred1 = device.symbols.createChild("path", "pred1")
        .setStrokeLineWidth(1)
        .setColor(0.8, 0.8, 0.4)
	.moveTo(data[0][0], data[0][1]);

	 p_dps_rtls.pred2 = device.symbols.createChild("path", "pred2")
        .setStrokeLineWidth(1)
        .setColor(0.8, 0.8, 0.4)
	.moveTo(data[0][0], data[0][1]);



	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_dps_rtls.pred1.lineTo(set[0], set[1]);
		p_dps_rtls.pred2.lineTo(set[0], set[1]);
		}

        p_dps_rtls.prplt_text.setText(sprintf("PRPLT"));
        p_dps_rtls.throttle_text.setText(sprintf("THROT"));	


        SpaceShuttle.rtls_traj_update_set();


	var plot = device.nom_traj_plot.createChild("path", "data")
        .setStrokeLineWidth(2)
        .setColor(dps_r,dps_g,dps_b)
		.setTranslation(rightshift,downshift)
        .moveTo(traj_data[0][0],traj_data[0][1]); 
    
        for (var i = 1; i< (size(traj_data)-1); i=i+1)
        {
            var set = traj_data[i+1];
            plot.lineTo(set[0], set[1]);	
        }

	var plot_limit1 = device.limit1_traj_plot.createChild("path", "data")
        .setStrokeLineWidth(2)
        .setColor(dps_r, dps_g, dps_b)
		.setTranslation(rightshift,downshift)
        .moveTo(limit1_data[0][0],limit1_data[0][1]); 
    
        for (var i = 1; i< (size(limit1_data)-1); i=i+1)
        {
            var set = limit1_data[i+1];
            plot_limit1.lineTo(set[0], set[1]);	
        }
    
        var plot_limit2 = device.limit2_traj_plot.createChild("path", "data")
        .setStrokeLineWidth(2)
        .setColor(dps_r,dps_g,dps_b)
		.setTranslation(rightshift,downshift)
        .moveTo(limit2_data[0][0],limit2_data[0][1]); 
    
        for (var i = 1; i< (size(limit2_data)-1); i=i+1)
        {
            var set = limit2_data[i+1];
            plot_limit2.lineTo(set[0], set[1]);	
        }


	setsize(data,0);



	
		
	



	var set = [SpaceShuttle.parameter_to_x(0.0, 10), SpaceShuttle.parameter_to_y(200000, 10)];
	append(data, set);
	set = [SpaceShuttle.parameter_to_x(0.0, 10), SpaceShuttle.parameter_to_y(450000, 10)];
	append(data, set);

	 p_dps_rtls.zero_line = device.symbols.createChild("path", "zline")
        .setStrokeLineWidth(2)
        .setColor(dps_r, dps_g, dps_b)
		.setTranslation(rightshift + 70,downshift + 110)
		.setScale(0.7)
	.moveTo(data[0][0], data[0][1])
	.lineTo(data[1][0], data[1][1]);

	p_dps_rtls.zero_line_text = device.symbols.createChild("text")
      	.setText("0")
        .setColor(dps_r, dps_g, dps_b)
	.setFontSize(14)
	.setFont(p_pfd_font_1)
	.setAlignment("center-bottom")
        .setTranslation(data[0][0] + rightshift, data[0][1] + 18.0 + downshift);


	#MECO Cutoff marker for PASS 601

	data = SpaceShuttle.draw_tmarker_down();
	p_dps_rtls.vco_marker = device.symbols.createChild("path", "vco_marker")
        .setStrokeLineWidth(1)
        .setColor(0.8, 0.8, 0.4) # Cutoff marker yellow
		.setScale(0.7, 1.20)   
	.moveTo(data[0][0], data[0][1]);

	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_dps_rtls.vco_marker.lineTo(set[0], set[1]);
		}

	#Alpha bfs scale marker

	data = SpaceShuttle.draw_tmarker_left();
	p_dps_rtls.bfs_alpha_marker = device.symbols.createChild("path", "alpha_marker")
        .setStrokeLineWidth(2)
        .setColor(0.8, 0.8, 0.4)
		.setScale(0.9, 0.7)
	.moveTo(data[0][0], data[0][1]);

	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_dps_rtls.bfs_alpha_marker.lineTo(set[0], set[1]);
		}

	#G's scale bfs marker

	p_dps_rtls.bfs_g_marker = device.symbols.createChild("path", "g_marker")
        .setStrokeLineWidth(2)
        .setColor(0.8, 0.8, 0.4)
		.setScale(0.9, 0.7)
	.moveTo(data[0][0], data[0][1]);

	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_dps_rtls.bfs_g_marker.lineTo(set[0], set[1]);
		}


	p_dps_rtls.engine1_fail_vi.setText("");
	p_dps_rtls.engine2_fail_vi.setText("");

	p_dps_rtls.tmeco_txt.setText("TMECO");
    p_dps_rtls.tmeco.setText("");
	p_dps_rtls.tgo_txt.setText("TGO");
    p_dps_rtls.tgo.setText("");
	p_dps_rtls.tmeco_txt_bfs.setText("TMECO");
    p_dps_rtls.tmeco_bfs.setText("");


	p_dps_rtls.major_func = SpaceShuttle.idp_array[device.port_selected-1].get_major_function();  # Preparing RTLS BFS display differences


        #device.DPS_menu_title.setText("                    RTLS TRAJ 2");
        device.MEDS_menu_title.setText("      DPS MENU");
    
        var major_mode = getprop("/fdm/jsbsim/systems/dps/major-mode");
    
        var ops_string = major_mode~"1/   /";
		var ops_string_bfs = major_mode~"1/";
        

		# different dps menu ops for PASS and BFS (No second /)

		if (p_dps_rtls.major_func != 4) 
			{
			device.DPS_menu_ops.setText(ops_string);
			device.DPS_menu_title.setText("                    RTLS TRAJ 2");
			}
		else 
			{
			device.DPS_menu_ops.setText(ops_string_bfs);
			device.DPS_menu_title.setText("                 RTLS TRAJ 2"); # 3 space less for RTLS BFS Title ( Scom GNC)
			}
    }


    p_dps_rtls.offdisplay = func
    {

        device.nom_traj_plot.removeAllChildren();
  	device.limit1_traj_plot.removeAllChildren();
        device.limit2_traj_plot.removeAllChildren();
	device.symbols.removeAllChildren();

    }
    
    p_dps_rtls.update = func
    {
    
 	var throttle = getprop("/fdm/jsbsim/fcs/throttle-pos-norm");
	if (throttle == 0 ){throttle = getprop("/fdm/jsbsim/fcs/throttle-pos-norm[1]");}
	if (throttle == 0 ){throttle = getprop("/fdm/jsbsim/fcs/throttle-pos-norm[2]");}
        if (throttle < 0.61) {throttle = 0.0;} else {throttle = throttle * 100.0;}
        p_dps_rtls.throttle.setText(sprintf("%-3.0f",throttle));
		p_dps_rtls.throttle_bfs.setText(sprintf("%-3.0f",throttle));

	p_dps_rtls.prplt.setText(sprintf("%-3.0f",100.0* getprop("/consumables/fuel/tank/level-norm")));
	p_dps_rtls.guid.setText(sprintf("%-2.0f", getprop("/fdm/jsbsim/systems/ap/rtls/guid-percent")));

	p_dps_rtls.prplt_bfs.setText(sprintf("%5.0f",100.0* getprop("/consumables/fuel/tank/level-norm")));
	p_dps_rtls.guid_bfs.setText(sprintf("%-2.0f", getprop("/fdm/jsbsim/systems/ap/rtls/guid-percent")));


	if (getprop("/fdm/jsbsim/systems/abort/enable-yaw-steer") == 1)
		{p_dps_rtls.yaw_steer.setText("ENA");}
	else	
		{p_dps_rtls.yaw_steer.setText("INH");}

	p_dps_rtls.abort_region.updateText(getprop("/fdm/jsbsim/systems/abort/contingency-abort-region"));
	p_dps_rtls.abort_region_3eo.updateText(getprop("/fdm/jsbsim/systems/abort/contingency-abort-region-3eo"));
	
	p_dps_rtls.engine1_fail_vi.setText(getprop("/fdm/jsbsim/systems/abort/engine-fail-string"));
	p_dps_rtls.engine2_fail_vi.setText(getprop("/fdm/jsbsim/systems/abort/engine2-fail-string"));
	

	if (getprop("/fdm/jsbsim/systems/abort/arm-contingency") == 1)
		{p_dps_rtls.arm.setText("*");}
	else
		{p_dps_rtls.arm.setText("");}

	var abort_mode = getprop("/fdm/jsbsim/systems/abort/abort-mode");

	if ((abort_mode > 4) and (abort_mode < 10))
		{
		p_dps_rtls.abort.setText("*");
		p_dps_rtls.abort_region.setColor(0.8, 0.8, 0.4);
		}
	else if (abort_mode > 9)	
		{
		p_dps_rtls.abort.setText("");
		p_dps_rtls.abort_region_3eo.setColor(0.8, 0.8, 0.4);
		}
	else
		{p_dps_rtls.abort.setText("");}


	var control_mode = getprop("/fdm/jsbsim/systems/fcs/control-mode");

	if (control_mode == 13)
    		{
		p_dps_rtls.serc.setText("*");
    		p_dps_rtls.serc_on.setText("ON");
		}
	else
		{
		p_dps_rtls.serc.setText("");
    		p_dps_rtls.serc_on.setText("");
		}


	#MECO time calculation

	var elapsed = getprop("/sim/time/elapsed-sec");
	var delta_met= getprop("/fdm/jsbsim/systems/timer/delta-MET");


	tmeco = elapsed + SpaceShuttle.meco_time.get();
	tgo = SpaceShuttle.meco_time.get() - delta_met;
	        
	if (SpaceShuttle.meco_time.get_mode() < 2)
	    	{
			p_dps_rtls.tmeco.setText(seconds_to_stringMS(tmeco));
			p_dps_rtls.tmeco_bfs.setText(seconds_to_stringMS(tmeco));
			p_dps_rtls.tgo.setText(seconds_to_stringMS(tgo));
			}


	

	#MECO marker activation (MECO around 7400 Vrel//250 Nm and PD around 6800 Vrel// 260 Nm)
	#Scale in distance vs landing site in real ( we do it in vrel-fps )

	var site_rel_velocity = getprop("/fdm/jsbsim/systems/entry_guidance/vrel-fps");
	var velocity = getprop("/fdm/jsbsim/systems/entry_guidance/ground-relative-velocity-fps"); 


	#Same value than above but much more stable parameter g's wise for meco scale that requires fine tunning ( if not, marker "jumps ")

	var velocity_true = getprop("fdm/jsbsim/velocities/vtrue-fps"); 

	#var vfrac = (velocity_true - 6000.0)/1600.0;
	var vfrac = (velocity_true - 5950.0)/1700.0;


	if (vfrac < 0) {vfrac = 0.0;}

	#p_dps_rtls.vco_marker.setTranslation(478.0 - vfrac * 420.0 ,90.0);

	#To avoid translation during PPA with high vrel ( late RTLS abort) // time conditionnal (MECO around 11mn)

	if ((elapsed + delta_met) > 540) {p_dps_rtls.vco_marker.setTranslation(478.0 - vfrac * 420.0 ,95.0);}
	else {p_dps_rtls.vco_marker.setTranslation(478.0 ,95.0);}
	



	var sign = 1;

	if (getprop("/fdm/jsbsim/systems/ap/rtls/flyback-active") == 1)
		{sign = -1;}

	if (site_rel_velocity < 0.0) {velocity = -velocity; }

	var altitude = getprop("/position/altitude-ft");

	#same shift logic than ascent.nas to allow better placement of the envelop
	
		var downshift = -50.0;
		var rightshift = -20.0;

        var x = SpaceShuttle.parameter_to_x(velocity, 10);
        var y = SpaceShuttle.parameter_to_y(altitude, 10);
    	
	p_dps_rtls.shuttle_marker.setTranslation(x + rightshift,y + downshift);


	var velocity1 = SpaceShuttle.ascent_predictors[0][2] * sign + velocity;
	altitude = SpaceShuttle.ascent_predictors[0][1];

	x = SpaceShuttle.parameter_to_x(velocity1, 10);
	y = SpaceShuttle.parameter_to_y(altitude, 10);

	p_dps_rtls.pred1.setTranslation(x + rightshift,y + downshift);

	velocity1 = SpaceShuttle.ascent_predictors[1][2] * sign + velocity;
	altitude = SpaceShuttle.ascent_predictors[1][1];

	x = SpaceShuttle.parameter_to_x(velocity1, 10);
	y = SpaceShuttle.parameter_to_y(altitude, 10);

	p_dps_rtls.pred2.setTranslation(x + rightshift,y + downshift); 

        device.update_common_DPS();


	#BFS differences

	if (p_dps_rtls.major_func == 4) # we drive BFS specific items
		{
		
		p_dps_rtls.pass_group.setVisible(0);
		p_dps_rtls.bfs_group.setVisible(1);



		#H dot

		var vspeed = -getprop("/fdm/jsbsim/velocities/v-down-fps");
		p_dps_rtls.H_dot_bfs.updateText(sprintf("%5.0f",vspeed)); #4.0


		#Alpha

		var alpha_deg = getprop("/fdm/jsbsim/aero/alpha-deg");
		p_dps_rtls.alpha_bfs.updateText(sprintf("%5.0f",alpha_deg)); #3


		#Beta

		var beta_deg = getprop("/fdm/jsbsim/aero/beta-deg");
		p_dps_rtls.beta_bfs.updateText(sprintf("%5.2f",beta_deg)); #1.2


		#PPA started indication

		var flyback_active = getprop("/fdm/jsbsim/systems/ap/rtls/flyback-active");
		if (flyback_active == 1) {p_dps_rtls.ppa_bfs.setText("1");}


		#Alpha scale

		var alpha_frac = alpha_deg/16.0;
		alpha_frac = SpaceShuttle.clamp(alpha_frac, -0.75, 0.25);

		p_dps_rtls.bfs_alpha_marker.setTranslation(36.945,171 - 260.0 * alpha_frac);


		#G's scale

		var g_frac = getprop("/fdm/jsbsim/accelerations/a-pilot-ft_sec2") * 0.03108095;
		g_frac = SpaceShuttle.clamp(g_frac, 2.0, 3.3) - 2.0;

		p_dps_rtls.bfs_g_marker.setTranslation(426.46,379 - 100.0 * g_frac);


		#P,Y,R BFS errors

		var pitch_error = 0.0;
		var roll_error = 0.0;
		var yaw_error = 0.0;

		pitch_error = getprop("/fdm/jsbsim/systems/ap/rtls/pitch-error");
		yaw_error = getprop("/fdm/jsbsim/systems/ap/rtls/yaw-error");
		roll_error = getprop("/fdm/jsbsim/systems/ap/rtls/roll-error");

		p_dps_rtls.bfs_roll_error.setText(sprintf("%03d", roll_error));
		p_dps_rtls.bfs_pitch_error.setText(sprintf("%03d", pitch_error));
		p_dps_rtls.bfs_yaw_error.setText(sprintf("%03d", yaw_error));



		}
	
	else
		{
		p_dps_rtls.pass_group.setVisible(1);
		p_dps_rtls.bfs_group.setVisible(0);
		}


    }
    
    
    
    return p_dps_rtls;
}
