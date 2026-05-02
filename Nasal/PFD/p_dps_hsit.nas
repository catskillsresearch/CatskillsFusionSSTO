#---------------------------------------
# SpaceShuttle PFD Page include:
#        Page: p_dps_hsit
# Description: the horizontal situation DPS page
#      Author: Thorsten Renk, 2016 // GinGin, 2020
#---------------------------------------

var PFD_addpage_p_dps_hsit = func(device)
{
    var p_dps_hsit = device.addPage("CRTHsit", "p_dps_hsit");

    p_dps_hsit.group = device.svg.getElementById("p_dps_hsit");
    p_dps_hsit.group.setColor(dps_r, dps_g, dps_b);
    
    p_dps_hsit.altm = device.svg.getElementById("p_dps_hsit_altm");  
    p_dps_hsit.pti = device.svg.getElementById("p_dps_hsit_pti"); 
    p_dps_hsit.pti_index_1 = device.svg.getElementById("p_dps_hsit_pti_index_1"); 
    p_dps_hsit.pti_index_2 = device.svg.getElementById("p_dps_hsit_pti_index_2");     	

    p_dps_hsit.tal_label = device.svg.getElementById("p_dps_hsit_label8");  
    p_dps_hsit.tal_site = device.svg.getElementById("p_dps_hsit_tal_site");  

    p_dps_hsit.tal_label.enableUpdate();  
    p_dps_hsit.tal_site.enableUpdate();

    p_dps_hsit.landing_label = device.svg.getElementById("p_dps_hsit_label9");
    p_dps_hsit.landing_site = device.svg.getElementById("p_dps_hsit_landing_site");    

    p_dps_hsit.landing_label.enableUpdate(); 
    p_dps_hsit.landing_site.enableUpdate(); 

    p_dps_hsit.gn_approach = device.svg.getElementById("p_dps_hsit_gn_approach");
    p_dps_hsit.entry_point = device.svg.getElementById("p_dps_hsit_entry_point");
    p_dps_hsit.aim = device.svg.getElementById("p_dps_hsit_aim");
    p_dps_hsit.sb = device.svg.getElementById("p_dps_hsit_sb");
    p_dps_hsit.pri_rwy = device.svg.getElementById("p_dps_hsit_pri_rwy");
    p_dps_hsit.sec_rwy = device.svg.getElementById("p_dps_hsit_sec_rwy");
    p_dps_hsit.gn_dir = device.svg.getElementById("p_dps_hsit_gn_dir");
    p_dps_hsit.hsi_dir = device.svg.getElementById("p_dps_hsit_hsi_dir");
    p_dps_hsit.gps_fom = device.svg.getElementById("p_dps_hsit_gps_fom");
    p_dps_hsit.gps_ra = device.svg.getElementById("p_dps_hsit_gps_ra");


    p_dps_hsit.pri_rwy_sel = device.svg.getElementById("p_dps_hsit_pri_rwy_sel");
    p_dps_hsit.sec_rwy_sel = device.svg.getElementById("p_dps_hsit_sec_rwy_sel");

    p_dps_hsit.pri_rwy_sel.enableUpdate(); 
    p_dps_hsit.sec_rwy_sel.enableUpdate(); 

    p_dps_hsit.nav_Dx = device.svg.getElementById("p_dps_hsit_nav_Dx");
    p_dps_hsit.nav_Dy = device.svg.getElementById("p_dps_hsit_nav_Dy");
    p_dps_hsit.nav_Dz = device.svg.getElementById("p_dps_hsit_nav_Dz");
    p_dps_hsit.nav_Dxdot = device.svg.getElementById("p_dps_hsit_nav_Dxdot");
    p_dps_hsit.nav_Dydot = device.svg.getElementById("p_dps_hsit_nav_Dydot");
    p_dps_hsit.nav_Dzdot = device.svg.getElementById("p_dps_hsit_nav_Dzdot");
    p_dps_hsit.Dt = device.svg.getElementById("p_dps_hsit_Dt");

    p_dps_hsit.nav_Dx.enableUpdate();
    p_dps_hsit.nav_Dy.enableUpdate();
    p_dps_hsit.nav_Dz.enableUpdate();
    p_dps_hsit.nav_Dxdot.enableUpdate();
    p_dps_hsit.nav_Dydot.enableUpdate();
    p_dps_hsit.nav_Dzdot.enableUpdate();
    p_dps_hsit.Dt.enableUpdate();

    p_dps_hsit.tac_az_ratio = device.svg.getElementById("p_dps_hsit_tac_az_ratio");
    p_dps_hsit.tac_az_resid = device.svg.getElementById("p_dps_hsit_tac_az_resid");
    p_dps_hsit.tac_az_aut = device.svg.getElementById("p_dps_hsit_tac_az_aut");
    p_dps_hsit.tac_az_inh = device.svg.getElementById("p_dps_hsit_tac_az_inh");
    p_dps_hsit.tac_az_for = device.svg.getElementById("p_dps_hsit_tac_az_for");

    p_dps_hsit.tac_az_aut.enableUpdate();
    p_dps_hsit.tac_az_inh.enableUpdate();
    p_dps_hsit.tac_az_for.enableUpdate();

    p_dps_hsit.tac_rng_resid = device.svg.getElementById("p_dps_hsit_tac_rng_resid");
    p_dps_hsit.tac_rng_ratio = device.svg.getElementById("p_dps_hsit_tac_rng_ratio");

    p_dps_hsit.dragh_resid = device.svg.getElementById("p_dps_hsit_dragh_resid");
    p_dps_hsit.dragh_ratio = device.svg.getElementById("p_dps_hsit_dragh_ratio");

    p_dps_hsit.gps_resid = device.svg.getElementById("p_dps_hsit_gps_resid");
    p_dps_hsit.gps_ratio = device.svg.getElementById("p_dps_hsit_gps_ratio");

    p_dps_hsit.adtah_resid = device.svg.getElementById("p_dps_hsit_adtah_resid");
    p_dps_hsit.adtah_ratio = device.svg.getElementById("p_dps_hsit_adtah_ratio");

    p_dps_hsit.gps_aut = device.svg.getElementById("p_dps_hsit_gps_aut");
    p_dps_hsit.gps_inh = device.svg.getElementById("p_dps_hsit_gps_inh");
    p_dps_hsit.gps_for = device.svg.getElementById("p_dps_hsit_gps_for");

    p_dps_hsit.gps_aut.enableUpdate();
    p_dps_hsit.gps_inh.enableUpdate();
    p_dps_hsit.gps_for.enableUpdate();

    p_dps_hsit.abs = device.svg.getElementById("p_dps_hsit_abs");
    p_dps_hsit.delta = device.svg.getElementById("p_dps_hsit_delta");

    p_dps_hsit.abs.enableUpdate();
    p_dps_hsit.delta.enableUpdate();

    p_dps_hsit.tac_az_tac1 = device.svg.getElementById("p_dps_hsit_tac_az_tac1");
    p_dps_hsit.tac_az_tac2 = device.svg.getElementById("p_dps_hsit_tac_az_tac2");
    p_dps_hsit.tac_az_tac3 = device.svg.getElementById("p_dps_hsit_tac_az_tac3");

    p_dps_hsit.tac_rng_tac1 = device.svg.getElementById("p_dps_hsit_tac_rng_tac1");
    p_dps_hsit.tac_rng_tac2 = device.svg.getElementById("p_dps_hsit_tac_rng_tac2");
    p_dps_hsit.tac_rng_tac3 = device.svg.getElementById("p_dps_hsit_tac_rng_tac3");

    p_dps_hsit.tac1_des = device.svg.getElementById("p_dps_hsit_tac1_des");
    p_dps_hsit.tac2_des = device.svg.getElementById("p_dps_hsit_tac2_des");
    p_dps_hsit.tac3_des = device.svg.getElementById("p_dps_hsit_tac3_des");

    p_dps_hsit.tac1_des.enableUpdate();
    p_dps_hsit.tac2_des.enableUpdate();
    p_dps_hsit.tac3_des.enableUpdate();
    
    p_dps_hsit.tac = device.svg.getElementById("p_dps_hsit_tac");
    p_dps_hsit.tac1 = device.svg.getElementById("p_dps_hsit_tac1");
    p_dps_hsit.tac2 = device.svg.getElementById("p_dps_hsit_tac2");
    p_dps_hsit.tac3 = device.svg.getElementById("p_dps_hsit_tac3");


    p_dps_hsit.statlabel = device.svg.getElementById("p_dps_hsit_statlabel");

    p_dps_hsit.adtah_aut = device.svg.getElementById("p_dps_hsit_adtah_aut");
    p_dps_hsit.adtah_inh = device.svg.getElementById("p_dps_hsit_adtah_inh");
    p_dps_hsit.adtah_for = device.svg.getElementById("p_dps_hsit_adtah_for");

    p_dps_hsit.adtah_aut.enableUpdate();
    p_dps_hsit.adtah_inh.enableUpdate();
    p_dps_hsit.adtah_for.enableUpdate();

    p_dps_hsit.dragh_aut = device.svg.getElementById("p_dps_hsit_dragh_aut");
    p_dps_hsit.dragh_inh = device.svg.getElementById("p_dps_hsit_dragh_inh");
    p_dps_hsit.dragh_for = device.svg.getElementById("p_dps_hsit_dragh_for");

    p_dps_hsit.dragh_aut.enableUpdate();
    p_dps_hsit.dragh_inh.enableUpdate();
    p_dps_hsit.dragh_for.enableUpdate();

    p_dps_hsit.adta_aut = device.svg.getElementById("p_dps_hsit_adta_aut");
    p_dps_hsit.adta_inh = device.svg.getElementById("p_dps_hsit_adta_inh");
    p_dps_hsit.adta_for = device.svg.getElementById("p_dps_hsit_adta_for");

    p_dps_hsit.adta_aut.enableUpdate();
    p_dps_hsit.adta_inh.enableUpdate();
    p_dps_hsit.adta_for.enableUpdate();

    p_dps_hsit.aif1 = device.svg.getElementById("p_dps_hsit_aif1");
    p_dps_hsit.aif2 = device.svg.getElementById("p_dps_hsit_aif2");
    p_dps_hsit.aif3 = device.svg.getElementById("p_dps_hsit_aif3");

    p_dps_hsit.aif1.enableUpdate();
    p_dps_hsit.aif2.enableUpdate();
    p_dps_hsit.aif3.enableUpdate();

    p_dps_hsit.gps_s_rn = device.svg.getElementById("p_dps_hsit_gps_s_rn");
    p_dps_hsit.gps_az = device.svg.getElementById("p_dps_hsit_gps_az");
    p_dps_hsit.gps_h = device.svg.getElementById("p_dps_hsit_gps_h");

    p_dps_hsit.MLS = device.svg.getElementById("p_dps_hsit_MLS");

    p_dps_hsit.pass = device.svg.getElementById("p_dps_hsit_pass");
    p_dps_hsit.bfs = device.svg.getElementById("p_dps_hsit_bfs");

    p_dps_hsit.bfs_gps_az = device.svg.getElementById("p_dps_hsit_bfs_gps_az");
    p_dps_hsit.bfs_gps_rng = device.svg.getElementById("p_dps_hsit_bfs_gps_rng");


	


	#Subgroups for Horizontal/vertical ladders

	p_dps_hsit.pass_before_left_hac_subgroup = device.svg.getElementById("p_dps_hsit_pass_before_left_hac_subgroup");
	p_dps_hsit.pass_before_right_hac_subgroup = device.svg.getElementById("p_dps_hsit_pass_before_right_hac_subgroup");
	p_dps_hsit.pass_before_left_hac_subgroup.setVisible(0);
	p_dps_hsit.pass_before_right_hac_subgroup.setVisible(0);

	p_dps_hsit.pass_after_hac_subgroup = device.svg.getElementById("p_dps_hsit_pass_after_hac_subgroup");
	p_dps_hsit.pass_after_hac_subgroup.setVisible(0);
	
	p_dps_hsit.hac_5K_left = device.svg.getElementById("p_dps_hsit_hac_5K_left");
	p_dps_hsit.hac_5K_right = device.svg.getElementById("p_dps_hsit_hac_5K_right");
	p_dps_hsit.hac_5K_left.enableUpdate();
	p_dps_hsit.hac_5K_right.enableUpdate();

	p_dps_hsit.hac_5K_up = device.svg.getElementById("p_dps_hsit_hac_5K_up");
	p_dps_hsit.hac_5K_down = device.svg.getElementById("p_dps_hsit_hac_5K_down");
	p_dps_hsit.hac_5K_up.enableUpdate();
	p_dps_hsit.hac_5K_down.enableUpdate();

	#Blinking Loc/GS deviation Arrow

	p_dps_hsit.blink_gs = 0;
	p_dps_hsit.blink_loc = 0;
	p_dps_hsit.blink_time_hac = 0;




	



    p_dps_hsit.ondisplay = func
    {
        device.DPS_menu_title.setText("                   HORIZ SIT");
        device.MEDS_menu_title.setText("      DPS MENU");

	p_dps_hsit.major_func = SpaceShuttle.idp_array[device.port_selected-1].get_major_function();

	

    
        var major_mode = getprop("/fdm/jsbsim/systems/dps/major-mode");

	if (SpaceShuttle.idp_array[device.port_selected-1].get_major_function() == 4)
		{
		major_mode = getprop("/fdm/jsbsim/systems/dps/major-mode-bfs");
		}
    
        var ops_string = major_mode~"1/050/";


        device.DPS_menu_ops.setText(ops_string);

	p_dps_hsit.MLS.setVisible(0);
	p_dps_hsit.MLS.setColor(0.8, 0.8, 0.4);
		
	# set defaults for functions which are not yet implemented

	p_dps_hsit.pti.setText("INH");
	p_dps_hsit.pti_index_1.setText("");
	p_dps_hsit.pti_index_2.setText("");
	p_dps_hsit.Dt.setText("+00:00");
	p_dps_hsit.statlabel.setText("");
	p_dps_hsit.gps_fom.setText("4");
	p_dps_hsit.gps_ra.setText("");

	# these are overwritten once TAEM guidance comes online

	p_dps_hsit.tac_az_aut.updateText("");
	p_dps_hsit.tac_az_inh.updateText("*");
	p_dps_hsit.tac_az_for.updateText("");

	p_dps_hsit.adtah_aut.updateText("");
	p_dps_hsit.adtah_inh.updateText("*");
	p_dps_hsit.adtah_for.updateText("");

	p_dps_hsit.gps_aut.updateText("");
	p_dps_hsit.gps_inh.updateText("*");
	p_dps_hsit.gps_for.updateText("");

	p_dps_hsit.dragh_aut.updateText("");
	p_dps_hsit.dragh_inh.updateText("*");
	p_dps_hsit.dragh_for.updateText("");

	p_dps_hsit.aif1.updateText("");
	p_dps_hsit.aif2.updateText("*");
	p_dps_hsit.aif3.updateText("");

	p_dps_hsit.adta_aut.updateText("");
	p_dps_hsit.adta_inh.updateText("*");
	p_dps_hsit.adta_for.updateText("");

	# generate the symbols for the graphical part of the display


	#HAC

	var data = SpaceShuttle.draw_circle(19, 16);
	
	 p_dps_hsit.hac = device.symbols.createChild("path", "hac")
        .setStrokeLineWidth(1)
        .setColor(dps_r, dps_g, dps_b)
	.moveTo(data[0][0], data[0][1]);

 	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_dps_hsit.hac.lineTo(set[0], set[1]);
		}

	setsize(data,0);

	data = SpaceShuttle.draw_circle(3, 10);

	 p_dps_hsit.touchdown = device.symbols.createChild("path", "touchdown")
        .setStrokeLineWidth(1)
        .setColor(dps_r, dps_g, dps_b)
	.moveTo(data[0][0], data[0][1]);

	 p_dps_hsit.pred1 = device.symbols.createChild("path", "pred1")
        .setStrokeLineWidth(1)
        .setColor(0.8, 0.8, 0.4)
	.moveTo(data[0][0], data[0][1]);

	 p_dps_hsit.pred2 = device.symbols.createChild("path", "pred2")
        .setStrokeLineWidth(1)
        .setColor(0.8, 0.8, 0.4)
	.moveTo(data[0][0], data[0][1]);

	 p_dps_hsit.pred3 = device.symbols.createChild("path", "pred3")
        .setStrokeLineWidth(1)
        .setColor(0.8, 0.8, 0.4)
	.moveTo(data[0][0], data[0][1]);


	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_dps_hsit.touchdown.lineTo(set[0], set[1]);
		p_dps_hsit.pred1.lineTo(set[0], set[1]);
		p_dps_hsit.pred2.lineTo(set[0], set[1]);
		p_dps_hsit.pred3.lineTo(set[0], set[1]);
		}

    #Final segment

 	p_dps_hsit.aimpoint = device.symbols.createChild("path", "aimpoint")
        .setStrokeLineWidth(1)
        .setColor(dps_r, dps_g, dps_b)
	.moveTo(0,0);

	data = SpaceShuttle.draw_shuttle_top();

	 p_dps_hsit.shuttle_marker = device.symbols.createChild("path", "shuttle")
        .setStrokeLineWidth(0.25)
        .setColor(dps_r, dps_g, dps_b)
	.moveTo(data[0][0], data[0][1]);

	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_dps_hsit.shuttle_marker.lineTo(set[0], set[1]);
		}
	p_dps_hsit.shuttle_marker.setScale (2.5);    #Shuttle size
	p_dps_hsit.shuttle_marker.setTranslation (265, 265);


	#Horizontal ladder (time to HAC )

	data = SpaceShuttle.draw_tmarker_down();
	p_dps_hsit.hac_marker = device.symbols.createChild("path", "hac_marker")
        .setStrokeLineWidth(1)
        .setColor(0.8, 0.8, 0.4)
		.setScale(0.6, 1.10)   
	.moveTo(data[0][0], data[0][1]);

	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_dps_hsit.hac_marker.lineTo(set[0], set[1]);
		}

	p_dps_hsit.hac_marker.setTranslation(396.57 - 0.0 * 17.33 ,88.0);
	p_dps_hsit.hac_marker.setVisible(0);


	#Horizontal ladder (Loc deviation after entering HAC )

	data = SpaceShuttle.draw_shuttle_top();
	p_dps_hsit.loc_marker = device.symbols.createChild("path", "loc_marker")
        .setStrokeLineWidth(0.25)
        .setColor(dps_r, dps_g, dps_b)
		.setScale(2.5)  
	.moveTo(data[0][0], data[0][1]);

	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_dps_hsit.loc_marker.lineTo(set[0], set[1]);
		}

	p_dps_hsit.loc_marker.setTranslation(309.92 + 0.0 * 86.65 ,83.0);
	p_dps_hsit.loc_marker.setVisible(0);


	#Vertical ladder (GS deviation)

	data = SpaceShuttle.draw_tmarker_left();
	p_dps_hsit.gs_marker = device.symbols.createChild("path", "gs_marker")
        .setStrokeLineWidth(1.0)
        .setColor(dps_r, dps_g, dps_b)
		.setScale(1.10, 0.6)
	.moveTo(data[0][0], data[0][1]);

	for (var i = 0; (i< size(data)-1); i=i+1)
        	{
		var set = data[i+1]; 
		p_dps_hsit.gs_marker.lineTo(set[0], set[1]);
		}

	p_dps_hsit.gs_marker.setTranslation(402.2 ,200.5 + 0.0 * 63);	
	



	# switch BFS elements on and PASS elements off if we run BFS

	if (p_dps_hsit.major_func == 4)
		{
		p_dps_hsit.pass.setVisible(0);
		p_dps_hsit.bfs.setVisible(1);
		p_dps_hsit.gs_marker.setVisible(0);
		}
	else
		{
		p_dps_hsit.pass.setVisible(1);
		p_dps_hsit.bfs.setVisible(0);
		p_dps_hsit.gs_marker.setVisible(1);
		}

    }

    p_dps_hsit.offdisplay = func 
    {
    device.symbols.removeAllChildren();
    device.nom_traj_plot.removeAllChildren();
    }
    
    p_dps_hsit.update = func
    {
    

	var ops = getprop("/fdm/jsbsim/systems/dps/ops");
	var guidance_mode = getprop("/fdm/jsbsim/systems/entry_guidance/guidance-mode");

	p_dps_hsit.altm.setText(sprintf("%5.2f", getprop("/instrumentation/altimeter/setting-inhg") ));
      
	if ((ops == 1) and (guidance_mode == 0))
		{
		var tal_iloaded = getprop("/fdm/jsbsim/systems/entry_guidance/tal-site-iloaded");
		p_dps_hsit.tal_site.updateText(sprintf("%2d",tal_iloaded));
		p_dps_hsit.tal_label.updateText("40 TAL  SITE");
		}
	else 
		{
		p_dps_hsit.tal_label.updateText("");
		p_dps_hsit.tal_site.updateText("");
		}


	if ((guidance_mode == 1) or (guidance_mode == 0))
		{p_dps_hsit.landing_label.updateText("41 LAND SITE");}
	else if (guidance_mode == 2)
		{p_dps_hsit.landing_label.updateText("41 TAL  SITE");}
	else if (guidance_mode == 3)
		{p_dps_hsit.landing_label.updateText("41 RTLS SITE");}
	else
		{p_dps_hsit.landing_label.updateText("41 LAND SITE");}
	
	p_dps_hsit.landing_site.updateText(sprintf("%2d",SpaceShuttle.landing_site.index));

	var string = getprop("/fdm/jsbsim/systems/taem-guidance/approach-mode-string");
	p_dps_hsit.gn_approach.setText(string);

	var entry_point_string = getprop("/fdm/jsbsim/systems/taem-guidance/entry-point-string");
	p_dps_hsit.entry_point.setText(entry_point_string);

	var aim_string = getprop("/fdm/jsbsim/systems/approach-guidance/aim-point-string");
	p_dps_hsit.aim.setText(aim_string);

	var sb_mode_string = getprop("/fdm/jsbsim/systems/approach-guidance/speedbrake-mode-string");
	p_dps_hsit.sb.setText(sb_mode_string);


	string = "";
	var rwy_sel = "";
	var field_altitude = 0.0;
	if (SpaceShuttle.TAEM_guidance_available == 1)
		{
		if (SpaceShuttle.TAEM_WP_1.turn_direction == "left"){string = "L";}
		else {string = "R";}
		field_altitude = SpaceShuttle.TAEM_threshold.elevation;
		}
 	else if (SpaceShuttle.TAEM_TACAN_available == 1)
		{
		field_altitude = SpaceShuttle.TAEM_threshold.elevation;
		}
		


	p_dps_hsit.gn_dir.setText(string);
	p_dps_hsit.hsi_dir.setText(string);

	p_dps_hsit.pri_rwy.setText(SpaceShuttle.landing_site.rwy_pri);
	p_dps_hsit.sec_rwy.setText(SpaceShuttle.landing_site.rwy_sec);

	var tacan_disp_mode = getprop("/fdm/jsbsim/systems/taem-guidance/tacan-abs");

	string = "";
	if (tacan_disp_mode == 1) {string = "*";}
	p_dps_hsit.abs.updateText(string);

	string = "";
	if (tacan_disp_mode == 0) {string = "*";}
	p_dps_hsit.delta.updateText(string);

	string = "";
	var tacan1_des = SpaceShuttle.tacan_system.receiver[0].deselected;
	if (tacan1_des == 1){string = "*";}
	p_dps_hsit.tac1_des.updateText(string);

	string = "";
	var tacan2_des = SpaceShuttle.tacan_system.receiver[1].deselected;
	if (tacan2_des == 1){string = "*";}
	p_dps_hsit.tac2_des.updateText(string);

	string = "";
	var tacan3_des = SpaceShuttle.tacan_system.receiver[2].deselected;
	if (tacan3_des == 1){string = "*";}
	p_dps_hsit.tac3_des.updateText(string);
	
	string = "";
	if (SpaceShuttle.landing_site.rwy_sel == 0){string = "*";}
	p_dps_hsit.pri_rwy_sel.updateText(string);

	string = "";
	if (SpaceShuttle.landing_site.rwy_sel == 1){string = "*";}
	p_dps_hsit.sec_rwy_sel.updateText(string);


	if ((SpaceShuttle.area_nav_set.air_data_available == 1) and (SpaceShuttle.area_nav_set.MLS_processing == 0))
		{
		var adta_resid_pos = SpaceShuttle.area_nav_set.baro_alt_m/0.3048 - getprop("/fdm/jsbsim/systems/navigation/state-vector/altitude-ft");
		

		p_dps_hsit.adtah_resid.setText(sprintf("%+6.0f", SpaceShuttle.clamp(SpaceShuttle.area_nav_set.adta_resid_h, 0, 99999)));
		p_dps_hsit.adtah_ratio.setText(sprintf("%4.1f", SpaceShuttle.clamp(SpaceShuttle.area_nav_set.adta_ratio_h, 0, 99.9)));
		}
	else
		{
		p_dps_hsit.adtah_resid.setText("");
		p_dps_hsit.adtah_ratio.setText("");
		}




	p_dps_hsit.dragh_resid.setText(sprintf("%+6.0f", SpaceShuttle.clamp(SpaceShuttle.area_nav_set.drag_h_resid, 0, 99999)));
	p_dps_hsit.dragh_ratio.setText(sprintf("%4.1f", SpaceShuttle.clamp(SpaceShuttle.area_nav_set.drag_h_ratio, 0, 99.9)));


	p_dps_hsit.tac.setText(SpaceShuttle.landing_site.tacan);
	p_dps_hsit.tac1.setText(SpaceShuttle.landing_site.tacan);
	p_dps_hsit.tac2.setText(SpaceShuttle.landing_site.tacan);
	p_dps_hsit.tac3.setText(SpaceShuttle.landing_site.tacan);

	


	if ((SpaceShuttle.TAEM_guidance_available == 1) or (SpaceShuttle.TAEM_TACAN_available == 1))
		{
		var MLS_active = SpaceShuttle.area_nav_set.MLS_processing;

		if (MLS_active == 1) 
			{
			p_dps_hsit.MLS.setVisible(1);
			p_dps_hsit.tac_az_ratio.setText("");
			p_dps_hsit.tac_rng_ratio.setText("");
			p_dps_hsit.tac_az_resid.setText("");
			p_dps_hsit.tac_rng_resid.setText("");
			}
		else
			{
			p_dps_hsit.MLS.setVisible(0);
			p_dps_hsit.tac_az_ratio.setText(sprintf("%4.1f", SpaceShuttle.clamp(SpaceShuttle.area_nav_set.tac_ratio_bearing, 0, 99.9)));
			p_dps_hsit.tac_rng_ratio.setText(sprintf("%4.1f", SpaceShuttle.clamp(SpaceShuttle.area_nav_set.tac_ratio_range, 0, 99.9)));
			p_dps_hsit.tac_az_resid.setText(sprintf("%+6.2f", SpaceShuttle.area_nav_set.tac_resid_bearing));
			p_dps_hsit.tac_rng_resid.setText(sprintf("%+6.2f", SpaceShuttle.clamp(SpaceShuttle.area_nav_set.tac_resid_range, -99.9, 99.9)));
			}

	

		var course = getprop("/fdm/jsbsim/systems/taem-guidance/course");
		var heading = getprop("/orientation/heading-deg");
		var range = getprop("/fdm/jsbsim/systems/taem-guidance/distance-to-runway-nm");
		var course_disp = course;
		if (tacan_disp_mode == 0) {course_disp = getprop("/fdm/jsbsim/systems/taem-guidance/delta-azimuth-deg");}

		if ((TAEM_TACAN_available == 1) and (TAEM_guidance_available == 0))
			{
			course = SpaceShuttle.area_nav_set.nav_bearing_tacan;
			range = SpaceShuttle.area_nav_set.nav_dist_tacan/1853.0;
			course_disp = course;

			var delta_az = course - heading;
			if (delta_az > 180.0) {delta_az = delta_az - 360.0;}
			if (delta_az < -180.0) {delta_az = delta_az + 360.0;}
			if (tacan_disp_mode == 0) {course_disp = delta_az;}
			}


		
		if (tacan1_des == 0)
			{
			
			var course_disp1 = SpaceShuttle.tacan_system.receiver[0].indicated_azimuth(course_disp);
			var status = SpaceShuttle.tacan_system.receiver[0].get_status_string();
			p_dps_hsit.tac_az_tac1.setText(sprintf("%+7.2f", course_disp1)~status);

			var rng1 = SpaceShuttle.tacan_system.receiver[0].indicated_range(range);
			rng1 = SpaceShuttle.clamp(rng1, -999.99, 999.99);
			p_dps_hsit.tac_rng_tac1.setText(sprintf("%+7.2f", rng1)~status);
			}
		else
			{
			p_dps_hsit.tac_az_tac1.setText("");
			p_dps_hsit.tac_rng_tac1.setText("");
			}

		if (tacan2_des == 0)
			{
			var course_disp2 = SpaceShuttle.tacan_system.receiver[1].indicated_azimuth(course_disp);
			var status = SpaceShuttle.tacan_system.receiver[1].get_status_string();
			p_dps_hsit.tac_az_tac2.setText(sprintf("%+7.2f", course_disp2)~status);

			var rng2 = SpaceShuttle.tacan_system.receiver[1].indicated_range(range);
			rng2 = SpaceShuttle.clamp(rng2, -999.99, 999.99);
			p_dps_hsit.tac_rng_tac2.setText(sprintf("%+7.2f", rng2)~status);
			}
		else
			{
			p_dps_hsit.tac_az_tac2.setText("");
			p_dps_hsit.tac_rng_tac2.setText("");
			}

		if (tacan3_des == 0)
			{
			var course_disp3 = SpaceShuttle.tacan_system.receiver[2].indicated_azimuth(course_disp);
			var status = SpaceShuttle.tacan_system.receiver[2].get_status_string();
			p_dps_hsit.tac_az_tac3.setText(sprintf("%+7.2f", course_disp3)~status);

			var rng3 = SpaceShuttle.tacan_system.receiver[2].indicated_range(range);
			rng3 = SpaceShuttle.clamp(rng3, -999.99, 999.99);
			p_dps_hsit.tac_rng_tac3.setText(sprintf("%+7.2f", rng3)~status);
			}
		else
			{
			p_dps_hsit.tac_az_tac3.setText("");
			p_dps_hsit.tac_rng_tac3.setText("");
			}
	
		var altitude_above_site = (getprop("/position/altitude-ft") - field_altitude)/1000.0;
		altitude_above_site = SpaceShuttle.clamp(altitude_above_site, 0, 999.9);


		if (SpaceShuttle.area_nav_set.gps_available == 1)
			{

			range = SpaceShuttle.clamp(range, -9999.9, 9999.9);

	  		p_dps_hsit.gps_s_rn.setText(sprintf("%+7.1f",range));
	    		p_dps_hsit.gps_az.setText(sprintf("%+7.2f", course_disp));
	    		p_dps_hsit.bfs_gps_az.setText(sprintf("%+7.2f", course_disp));
	    		p_dps_hsit.bfs_gps_rng.setText(sprintf("%7.2f", range));
			p_dps_hsit.gps_h.setText(sprintf("%5.1f", altitude_above_site));


			}
		else
			{
	  		p_dps_hsit.gps_s_rn.setText("");
	    		p_dps_hsit.gps_az.setText("");
			p_dps_hsit.gps_h.setText("");
	    		p_dps_hsit.bfs_gps_az.setText("");
	    		p_dps_hsit.bfs_gps_rng.setText("");
			}




		string = "";
		if (SpaceShuttle.area_nav_set.TACAN_aut == 1) {string = "*";}	
		p_dps_hsit.tac_az_aut.setText(string);

		string = "";
		if (SpaceShuttle.area_nav_set.TACAN_inh == 1) {string = "*";}	
		p_dps_hsit.tac_az_inh.setText(string);

		string = "";
		if (SpaceShuttle.area_nav_set.TACAN_for == 1) {string = "*";}	
		p_dps_hsit.tac_az_for.setText(string);

		string = "";
		if (SpaceShuttle.area_nav_set.air_data_h_aut == 1) {string = "*";}	
		p_dps_hsit.adtah_aut.updateText(string);

		string = "";
		if (SpaceShuttle.area_nav_set.air_data_h_inh == 1) {string = "*";}
		p_dps_hsit.adtah_inh.updateText(string);

		string = "";
		if (SpaceShuttle.area_nav_set.air_data_h_for == 1) {string = "*";}
		p_dps_hsit.adtah_for.updateText(string);
		

		string = "";
		if (SpaceShuttle.area_nav_set.air_data_gc_aut == 1) {string = "*";}	
		p_dps_hsit.adta_aut.updateText(string);

		string = "";
		if (SpaceShuttle.area_nav_set.air_data_gc_inh == 1) {string = "*";}	
		p_dps_hsit.adta_inh.updateText(string);

		string = "";
		if (SpaceShuttle.area_nav_set.air_data_gc_for == 1) {string = "*";}	
		p_dps_hsit.adta_for.updateText(string);


		string = "";
		if (SpaceShuttle.area_nav_set.gps_gc_aut == 1) {string = "*";}	
		p_dps_hsit.aif1.updateText(string);

		string = "";
		if (SpaceShuttle.area_nav_set.gps_gc_inh == 1) {string = "*";}	
		p_dps_hsit.aif2.updateText(string);

		string = "";
		if (SpaceShuttle.area_nav_set.gps_gc_for == 1) {string = "*";}	
		p_dps_hsit.aif3.updateText(string);


		}

	else
		{
		p_dps_hsit.tac_az_ratio.setText("");
		p_dps_hsit.tac_rng_ratio.setText("");
		p_dps_hsit.tac_az_resid.setText("");
		p_dps_hsit.tac_rng_resid.setText("");
		p_dps_hsit.tac_az_tac1.setText("");
		p_dps_hsit.tac_az_tac2.setText("");
		p_dps_hsit.tac_az_tac3.setText("");
		p_dps_hsit.tac_rng_tac1.setText("");
		p_dps_hsit.tac_rng_tac2.setText("");
		p_dps_hsit.tac_rng_tac3.setText("");

  		p_dps_hsit.gps_s_rn.setText("");
    		p_dps_hsit.gps_az.setText("");
		p_dps_hsit.gps_h.setText("");
    		p_dps_hsit.bfs_gps_az.setText("");
    		p_dps_hsit.bfs_gps_rng.setText("");


		}

	


	#No Nav Delta text when nothing entered

	dx_delta = getprop("/fdm/jsbsim/systems/taem-guidance/Dx");
	dy_delta = getprop("/fdm/jsbsim/systems/taem-guidance/Dy");
	dz_delta = getprop("/fdm/jsbsim/systems/taem-guidance/Dz");

	dx_dot_delta = getprop("/fdm/jsbsim/systems/taem-guidance/Dxdot");
	dy_dot_delta = getprop("/fdm/jsbsim/systems/taem-guidance/Dydot");
	dz_dot_delta = getprop("/fdm/jsbsim/systems/taem-guidance/Dzdot");

	delta_sum = dx_delta + dy_delta + dz_delta + dx_dot_delta + dy_dot_delta + dz_dot_delta;

	if (delta_sum == 0)
		{
		p_dps_hsit.nav_Dx.updateText("");
		p_dps_hsit.nav_Dy.updateText("");
		p_dps_hsit.nav_Dz.updateText("");

		p_dps_hsit.nav_Dxdot.updateText("");
		p_dps_hsit.nav_Dydot.updateText("");
		p_dps_hsit.nav_Dzdot.updateText("");
		}

	else
		{
		p_dps_hsit.nav_Dx.updateText(sprintf("%+07.0f", dx_delta));
		p_dps_hsit.nav_Dy.updateText(sprintf("%+07.0f", dy_delta));
		p_dps_hsit.nav_Dz.updateText(sprintf("%+07.0f", dz_delta));

		p_dps_hsit.nav_Dxdot.updateText(sprintf("%+05.0f", dx_dot_delta));
		p_dps_hsit.nav_Dydot.updateText(sprintf("%+05.0f", dy_dot_delta));
		p_dps_hsit.nav_Dzdot.updateText(sprintf("%+05.0f", dz_dot_delta));
		}

	# drag altitude is always available, independent on TACAN lockon

	var sym = "";
	if (SpaceShuttle.area_nav_set.drag_h_aut == 1) {sym = "*";}	
	p_dps_hsit.dragh_aut.updateText(sym);

	sym = "";
	if (SpaceShuttle.area_nav_set.drag_h_inh == 1) {sym = "*";}	
	p_dps_hsit.dragh_inh.updateText(sym);

	var sym = "";
	if (SpaceShuttle.area_nav_set.drag_h_for == 1) {sym = "*";}	
	p_dps_hsit.dragh_for.updateText(sym);

	# GPS ratio and residual are always available

	if (SpaceShuttle.area_nav_set.gps_available == 1)
		{
		p_dps_hsit.gps_resid.setText(sprintf("%+6.2f", SpaceShuttle.clamp(SpaceShuttle.area_nav_set.gps_resid, -99.99, 99.99)));
		p_dps_hsit.gps_ratio.setText(sprintf("%4.1f", SpaceShuttle.clamp(SpaceShuttle.area_nav_set.gps_ratio, 0, 99.9)));
		}	

	else
		{
		p_dps_hsit.gps_resid.setText("");
		p_dps_hsit.gps_ratio.setText("");
		}

	sym = "";
	if (SpaceShuttle.area_nav_set.gps_aut == 1) {sym = "*";}	
	p_dps_hsit.gps_aut.updateText(sym);

	sym = "";
	if (SpaceShuttle.area_nav_set.gps_inh == 1) {sym = "*";}	
	p_dps_hsit.gps_inh.updateText(sym);

	sym = "";
	if (SpaceShuttle.area_nav_set.gps_for == 1) {sym = "*";}	
	p_dps_hsit.gps_for.updateText(sym);


	if (SpaceShuttle.TAEM_guidance_available == 1)
	{

	
	# create the graphical portion of the display
	# the graphical portion is a 230 x 140 sheet at 150-380:90-230 
	#var pos = geo.aircraft_position();
	

	var pos = SpaceShuttle.state_vector_position();
	var hac_init = getprop("/fdm/jsbsim/systems/ap/taem/hac-turn-init");
	var al_init = getprop("/fdm/jsbsim/systems/ap/taem/al-init");
	var distance_rwy = getprop("/fdm/jsbsim/systems/taem-guidance/distance-to-runway-nm");
	var hac_radius_factor_mep = getprop("fdm/jsbsim/systems/ap/taem/hac-radius-factor-mep");
	var hac_radius_factor_nep = getprop("fdm/jsbsim/systems/ap/taem/hac-radius-factor-nep");
	var hac_factor_wp1 = getprop("fdm/jsbsim/systems/ap/taem/hac-radius-factor-wp1");
	var hac_radius_factor = 1.0;
	
	#To avoid HAC display at max size before hac init, we take first the hac factor for the wp 1 drawing, replaced then by the dynamic hac factor once we are in hac
	#That starts to decrease after wp 1

	#Factor difference between MEP and NEP ( 3Nm difference for distance remaining)
	if (entry_point_string == "MEP") {hac_radius_factor = math.min(hac_radius_factor_mep, hac_factor_wp1);}
	else {hac_radius_factor = math.min(hac_radius_factor_nep, hac_factor_wp1);}
	
	
	var dist = pos.distance_to(SpaceShuttle.TAEM_HAC_center);
	#var rel_angle = math.pi / 180.0 * (pos.course_to(SpaceShuttle.TAEM_HAC_center) - getprop("/orientation/heading-deg"));
	var rel_angle = math.pi / 180.0 * (pos.course_to(SpaceShuttle.TAEM_HAC_center) - heading);

	#Different scale parameters before and after HAC 
	#var dist_scale = 0.0;
	#if ((hac_init == 1) or (al_init == 1)) {dist_scale = distance_rwy;}
	#else {dist_scale = dist / 1853;}

	#Scale == function(distance to runway)
	var scale = SpaceShuttle.get_hsit_scale(distance_rwy);


	var linescale = scale;
	if (linescale > 1.0) {linescale = 1.0;}

	var x = SpaceShuttle.get_hsit_x(dist, rel_angle, scale);
	var y = SpaceShuttle.get_hsit_y(dist, rel_angle, scale);

	
	#if (entry_point_string == "MEP")
		#{
		#p_dps_hsit.hac
		#	.setStrokeLineWidth(1.0)
		#	.setScale(4.0/7.0*scale*hac_radius_factor);

		#}
	#else
		#{
		#p_dps_hsit.hac
		#	.setStrokeLineWidth(1.0)
		#	.setScale(1.0*scale*hac_radius_factor);
		#}

	#Hac_radius_factor allows for the HAC to shrink from Initial radius (3.0 Nm) to final radius (2.3Nm) 
	#Same Hac size for MEP and NEP, just the target point change ( from 7 Nm to 4 Nm)
	p_dps_hsit.hac
			.setStrokeLineWidth(1.0/linescale)
			.setScale(1.0*scale*hac_radius_factor);

	p_dps_hsit.hac.setTranslation (x,y);



	dist = pos.distance_to(SpaceShuttle.TAEM_threshold);
	#rel_angle = math.pi / 180.0 * (pos.course_to(SpaceShuttle.TAEM_threshold) - getprop("/orientation/heading-deg"));
	rel_angle = math.pi / 180.0 * (pos.course_to(SpaceShuttle.TAEM_threshold) - heading);


	x = SpaceShuttle.get_hsit_x(dist, rel_angle, scale);
	y = SpaceShuttle.get_hsit_y(dist, rel_angle, scale);
	
	#Circle representing touchdown zone ( scale independant of zoom up to A/L where scale > 2)
	p_dps_hsit.touchdown.setScale(1);
	p_dps_hsit.touchdown.setStrokeLineWidth(1.0);
	p_dps_hsit.touchdown.setTranslation (x,y);

	device.nom_traj_plot.removeAllChildren();
 	var plot = device.nom_traj_plot.createChild("path", "data")
        .setStrokeLineWidth(1.0)
        .setColor(dps_r,dps_g,dps_b)
        .moveTo(x,y);

	dist = pos.distance_to(SpaceShuttle.TAEM_WP_2);
	#rel_angle = math.pi / 180.0 * (pos.course_to(SpaceShuttle.TAEM_WP_2) - getprop("/orientation/heading-deg"));
	rel_angle = math.pi / 180.0 * (pos.course_to(SpaceShuttle.TAEM_WP_2) -heading);

	x = SpaceShuttle.get_hsit_x(dist, rel_angle, scale);
	y = SpaceShuttle.get_hsit_y(dist, rel_angle, scale);
	
	plot.lineTo(x,y);

	x = SpaceShuttle.get_hsit_x(SpaceShuttle.TAEM_predictor_set.entry[0][0], SpaceShuttle.TAEM_predictor_set.entry[0][1], scale);
	y = SpaceShuttle.get_hsit_y(SpaceShuttle.TAEM_predictor_set.entry[0][0], SpaceShuttle.TAEM_predictor_set.entry[0][1], scale);

	p_dps_hsit.pred1.setTranslation (x,y);

	x = SpaceShuttle.get_hsit_x(SpaceShuttle.TAEM_predictor_set.entry[1][0], SpaceShuttle.TAEM_predictor_set.entry[1][1], scale);
	y = SpaceShuttle.get_hsit_y(SpaceShuttle.TAEM_predictor_set.entry[1][0], SpaceShuttle.TAEM_predictor_set.entry[1][1], scale);

	p_dps_hsit.pred2.setTranslation (x,y);

	x = SpaceShuttle.get_hsit_x(SpaceShuttle.TAEM_predictor_set.entry[2][0], SpaceShuttle.TAEM_predictor_set.entry[2][1], scale);
	y = SpaceShuttle.get_hsit_y(SpaceShuttle.TAEM_predictor_set.entry[2][0], SpaceShuttle.TAEM_predictor_set.entry[2][1], scale);

	p_dps_hsit.pred3.setTranslation (x,y);


	#Management of Pass horizontal/vertical deviation ladder (PASS only)

	if (p_dps_hsit.major_func != 4)
		{
		#Vertical (up to A/L)

		var glideslope_deviation = getprop("/fdm/jsbsim/systems/taem-guidance/glideslope-deviation-ft");
		var yfrac = glideslope_deviation / 5000;
		

		#Lateral

		if ((hac_init == 0) and (al_init == 0)) #Before HAC
			{
			#HAC time on horizontal ladder (starting 10 seconds before HAC)
			# Time to hac in seconds 

			var gs_kts = getprop("/velocities/groundspeed-kt");
			var wp_1_distance = pos.distance_to(SpaceShuttle.TAEM_WP_1) / 1853.0;
			var wp_1_time = ((wp_1_distance - 1.5) / gs_kts) * 3600; #9seconds of lag between hac_init and wp1 real position (Switch to HAC 1 Nm before)
			
			var tfrac = (10 - wp_1_time);

			#Blink logic (15 seconds before HAC init)
			if ((tfrac > -5) and (tfrac < 0))
				{
				if (p_dps_hsit.blink_time_hac == 0)
					{
					p_dps_hsit.hac_marker.setVisible(0);
					p_dps_hsit.blink_time_hac = 1;
					}
				else 
					{
					p_dps_hsit.hac_marker.setVisible(1);
					p_dps_hsit.blink_time_hac = 0;
					}	
				}
			else if (tfrac > 0) {p_dps_hsit.hac_marker.setVisible(1);}
			else {p_dps_hsit.hac_marker.setVisible(0);} #No marker if time to HAC is above 15s


			#Turn dependency for display
			if (SpaceShuttle.TAEM_WP_1.turn_direction == "left") #Needle from right to left		
				{
				p_dps_hsit.pass_before_left_hac_subgroup.setVisible(1);
				p_dps_hsit.pass_before_right_hac_subgroup.setVisible(0);
				p_dps_hsit.hac_marker.setTranslation(396.57 - SpaceShuttle.clamp(tfrac, 0, 10) * 17.33 ,88); 
				}
			else #Needle from left to right		
				{
				p_dps_hsit.pass_before_left_hac_subgroup.setVisible(0);
				p_dps_hsit.pass_before_right_hac_subgroup.setVisible(1);
				p_dps_hsit.hac_marker.setTranslation(223.27 + SpaceShuttle.clamp(tfrac, 0, 10) * 17.33 ,88); 
				}

			}
		
		else #After HAC
			{
			
			#Loc deviation on horizontal ladder (5000 feet half deviation)

			p_dps_hsit.hac_marker.setVisible(0);
			p_dps_hsit.pass_before_left_hac_subgroup.setVisible(0);
			p_dps_hsit.pass_before_right_hac_subgroup.setVisible(0);

			if (p_dps_hsit.major_func != 4) {p_dps_hsit.loc_marker.setVisible(1);}
			p_dps_hsit.pass_after_hac_subgroup.setVisible(1);

			#Deviation in the HAC based on Hac Xrange (not a fly to HSI like)
			var radial_error_feet = -getprop("/fdm/jsbsim/systems/taem-guidance/radial-error-nm") * 6076.12;
			var xfrac = radial_error_feet / 5000;

			

			#If in final // Loc and GS deviation 2500 feet/1000 feet and no more HAC displayed
			if (al_init == 1)
				{

				#Loc deviation (5000feet max before A/L / 2500 feet then)
				var course_threshold = 	pos.course_to(SpaceShuttle.TAEM_threshold); 
				var cdi_dispacement_rad = (course_threshold - SpaceShuttle.TAEM_threshold.heading) * 0.0175; 
				var runway_distance_feet = pos.distance_to(SpaceShuttle.TAEM_threshold) * 3.28;

				#NOT a fly to HSI like (hence the -)
				var cross_range_feet = -math.tan(cdi_dispacement_rad) * runway_distance_feet;
				

				#Lateral (2500 feet after A/L)
				xfrac = cross_range_feet / 2500;
				p_dps_hsit.hac.setVisible(0);
				p_dps_hsit.hac_5K_left.updateText("2.5K");
				p_dps_hsit.hac_5K_right.updateText("2.5K");

				#Vertical (1000 feet after A/L)
				
				p_dps_hsit.hac_5K_up.updateText("1.0K");
				p_dps_hsit.hac_5K_down.updateText("1.0K");
				yfrac = glideslope_deviation / 1000;

				}
			

			xfrac = SpaceShuttle.clamp(xfrac, -1, 1);
			p_dps_hsit.loc_marker.setTranslation(309.92 + xfrac * 86.65 ,83.0);

			#Blinking Logic if GS or LOC reached upper/lower limit
			#Loc
			if ((xfrac == 1) or (xfrac == -1))
				{
				if (p_dps_hsit.blink_loc == 0)
					{
					p_dps_hsit.loc_marker.setVisible(0);
					p_dps_hsit.blink_loc = 1;
					}
				else 
					{
					p_dps_hsit.loc_marker.setVisible(1);
					p_dps_hsit.blink_loc = 0;
					}
					
				}
			else {p_dps_hsit.loc_marker.setVisible(1);}

			}

			yfrac = SpaceShuttle.clamp(yfrac, -1, 1);
			p_dps_hsit.gs_marker.setTranslation(402.2 ,200.5 - yfrac * 63); #Fly to like the GS indicator

		
			#GS
			if ((yfrac == 1) or (yfrac == -1))
				{
				if (p_dps_hsit.blink_gs == 0)
					{
					p_dps_hsit.gs_marker.setVisible(0);
					p_dps_hsit.blink_gs = 1;
					}
				else 
					{
					p_dps_hsit.gs_marker.setVisible(1);
					p_dps_hsit.blink_gs = 0;
					}
					
				}
			else {p_dps_hsit.gs_marker.setVisible(1);}
		}

	}

	
        device.update_common_DPS();
    }
    
    
    
    return p_dps_hsit;
}
