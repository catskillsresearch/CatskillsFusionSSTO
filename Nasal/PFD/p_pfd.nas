#---------------------------------------
# SpaceShuttle PFD Page include:
#        Page: p_pfd, p_pfd_orbit
# Description: MEDS PFD for launch/entry and orbit
#      Authors: Thorsten Renk, 2015 - 2017 // GinGin, 2020
#---------------------------------------




#Font variables

var p_pfd_font_1 = 0;
var p_pfd_font_2 = 0;	


var PFD_addpage_p_pfd = func(device)
{
	#Font variables "loaded" for the rest of the nasal script and .nas

	p_pfd_font_1 = getprop("/sim/config/shuttle/font_A");
	p_pfd_font_2 = getprop("/sim/config/shuttle/font_B");

    var p_pfd = device.addPage("PFD", "p_pfd");
    
    #
    #
    # device page update
    p_pfd.group = device.svg.getElementById("p_pfd");
    p_pfd.group.setColor(1, 1, 1);

    p_pfd.keas = device.svg.getElementById("p_pfd_keas");
    p_pfd.keas.enableUpdate();

	p_pfd.label_keas = device.svg.getElementById("p_pfd_label_keas");
    p_pfd.label_keas.enableUpdate();
	
	p_pfd.label_alpha = device.svg.getElementById("p_pfd_alpha_label");
	p_pfd.label_alpha.enableUpdate();

    p_pfd.beta = device.svg.getElementById("p_pfd_beta");
    p_pfd.beta.enableUpdate();

	p_pfd.label_beta = device.svg.getElementById("p_pfd_label_beta");
	p_pfd.label_beta.enableUpdate();

	p_pfd.beta_Sign = device.svg.getElementById("p_pfd_beta_Sign");
	p_pfd.beta_Sign.enableUpdate();

    p_pfd.r = device.svg.getElementById("p_pfd_r");
    p_pfd.p = device.svg.getElementById("p_pfd_p");
    p_pfd.y = device.svg.getElementById("p_pfd_y");

    p_pfd.r.enableFast();
    p_pfd.p.enableFast();
    p_pfd.y.enableFast();

	p_pfd.label_r = device.svg.getElementById("p_pfd_label_r");
    p_pfd.label_p = device.svg.getElementById("p_pfd_label_p");
    p_pfd.label_y = device.svg.getElementById("p_pfd_label_y");
 
    p_pfd.dap = device.svg.getElementById("p_pfd_dap");
    p_pfd.dap.enableUpdate();

	p_pfd.label_dap = device.svg.getElementById("p_pfd_label_dap");
    p_pfd.label_dap.enableUpdate();

	p_pfd.label_pitch = device.svg.getElementById("p_pfd_label_pitch");
	p_pfd.label_pitch.enableUpdate();

    p_pfd.throt = device.svg.getElementById("p_pfd_throt");
    p_pfd.throt.enableUpdate();

    p_pfd.label_throt = device.svg.getElementById("p_pfd_label_throt");
    p_pfd.label_throt.enableUpdate();

	p_pfd.label_RY = device.svg.getElementById("p_pfd_label_RY");
    p_pfd.label_RY.enableUpdate();

	p_pfd.label_att = device.svg.getElementById("p_pfd_label_att");
    p_pfd.label_att.enableUpdate();

	p_pfd.label_SB = device.svg.getElementById("p_pfd_label_SB");
	p_pfd.label_SB.enableUpdate();

    p_pfd.label_mvi = device.svg.getElementById("p_pfd_mach_label");
    p_pfd.label_mvi.enableUpdate();

    p_pfd.att = device.svg.getElementById("p_pfd_att");
    p_pfd.att.enableUpdate();

    p_pfd.MM = device.svg.getElementById("p_pfd_MM");
    p_pfd.MM.enableUpdate();

	p_pfd.label_MM = device.svg.getElementById("p_pfd_label_MM");
	p_pfd.label_MM.enableUpdate();


    p_pfd.menu_item = device.svg.getElementById("MI_1"); 
    p_pfd.menu_item_frame = device.svg.getElementById("MI_1_frame"); 

    p_pfd.rect1 = device.svg.getElementById("p_pfd_rect1");
    p_pfd.rect2 = device.svg.getElementById("p_pfd_rect2");
	p_pfd.rect_dap = device.svg.getElementById("p_pfd_rect_dap");
	p_pfd.rect_throt = device.svg.getElementById("p_pfd_rect_throt");
	p_pfd.rect_att = device.svg.getElementById("p_pfd_rect_att");

	p_pfd.label_H = device.svg.getElementById("p_pfd_H_label");
	p_pfd.label_H_dot = device.svg.getElementById("p_pfd_Hdot_label");
	p_pfd.dotH = device.svg.getElementById("p_pfd_dot");

	
	#Colors that do not change and are differents than white

		#Yellow for Manual CSS boxes

	p_pfd.rect_dap.setColor(1,1,0);
	p_pfd.rect_throt.setColor(1,1,0);
	p_pfd.rect_att.setColor(1,1,0);


		#Light Grey (Lighter RGB than lower ADI or HSI/tape dark grey) for Label/SVG elements

	p_pfd.label_keas.setColor(0.7,0.7,0.78);
	p_pfd.label_alpha.setColor(0.7,0.7,0.78);
	p_pfd.label_beta.setColor(0.7,0.7,0.78);
	p_pfd.label_r.setColor(0.7,0.7,0.78);
    p_pfd.label_p.setColor(0.7,0.7,0.78); 
    p_pfd.label_y.setColor(0.7,0.7,0.78); 
	p_pfd.label_dap.setColor(0.7,0.7,0.78);
	p_pfd.label_pitch.setColor(0.7,0.7,0.78);
	p_pfd.label_SB.setColor(0.7,0.7,0.78);
	p_pfd.label_RY.setColor(0.7,0.7,0.78);
	p_pfd.label_throt.setColor(0.7,0.7,0.78);
	p_pfd.label_att.setColor(0.7,0.7,0.78);
	p_pfd.label_mvi.setColor(0.7,0.7,0.78);
	p_pfd.label_MM.setColor(0.7,0.7,0.78);
	#p_pfd.rect1.setColor(0.7,0.7,0.78);   Boxes are white 
	#p_pfd.rect2.setColor(0.7,0.7,0.78);
	p_pfd.label_H.setColor(0.7,0.7,0.78);
	p_pfd.label_H_dot.setColor(0.7,0.7,0.78);
	p_pfd.dotH.setColor(0.7,0.7,0.78);


	#Font B for some specific SVG elements in the PFD  (Keas, Beta, PYR)

	p_pfd.keas.setFont(p_pfd_font_2);
	p_pfd.beta.setFont(p_pfd_font_2);

	p_pfd.r.setFont(p_pfd_font_2);
	p_pfd.p.setFont(p_pfd_font_2);
	p_pfd.y.setFont(p_pfd_font_2);

	p_pfd.label_r.setFont(p_pfd_font_2);
	p_pfd.label_p.setFont(p_pfd_font_2);
	p_pfd.label_y.setFont(p_pfd_font_2);

	p_pfd.beta_Sign.setFont(p_pfd_font_2);

	#Blink variables

	p_pfd.blink_daz = 0;
	p_pfd.blink_gs = 0;



    # references to property nodes for improved performance of getter methods

    p_pfd.nd_ref_pitch = props.globals.getNode("/fdm/jsbsim/systems/navigation/state-vector/pitch-deg", 1);
    p_pfd.nd_ref_yaw = props.globals.getNode("/fdm/jsbsim/systems/navigation/state-vector/yaw-deg", 1);
    p_pfd.nd_ref_roll = props.globals.getNode("/fdm/jsbsim/systems/navigation/state-vector/roll-deg", 1);

    p_pfd.nd_ref_pitch_inrtl = props.globals.getNode("/fdm/jsbsim/systems/pointing/inertial/attitude/pitch-deg", 1);
    p_pfd.nd_ref_yaw_inrtl = props.globals.getNode("/fdm/jsbsim/systems/pointing/inertial/attitude/yaw-deg", 1);
    p_pfd.nd_ref_roll_inrtl = props.globals.getNode("/fdm/jsbsim/systems/pointing/inertial/attitude/roll-deg", 1);

    p_pfd.nd_ref_p_rad_s = props.globals.getNode("/fdm/jsbsim/velocities/p-rad_sec", 1);
    p_pfd.nd_ref_q_rad_s = props.globals.getNode("/fdm/jsbsim/velocities/q-rad_sec", 1);
    p_pfd.nd_ref_r_rad_s = props.globals.getNode("/fdm/jsbsim/velocities/r-rad_sec", 1);

    p_pfd.nd_ref_sid_ang_rad = props.globals.getNode("/fdm/jsbsim/systems/pointing/sidereal/sidereal-angle-rad", 1);

    p_pfd.nd_ref_course_deg = props.globals.getNode("/fdm/jsbsim/velocities/course-deg", 1);
    p_pfd.nd_ref_groundtrack_course_deg = props.globals.getNode("/fdm/jsbsim/systems/entry_guidance/groundtrack-course-deg", 1);

    p_pfd.nd_ref_beta_deg = props.globals.getNode("/fdm/jsbsim/aero/beta-deg", 1);
    p_pfd.nd_ref_alpha_deg = props.globals.getNode("/fdm/jsbsim/aero/alpha-deg", 1);

    p_pfd.nd_ref_mach = props.globals.getNode("/fdm/jsbsim/velocities/mach", 1);
    p_pfd.nd_ref_veci = props.globals.getNode("/fdm/jsbsim/velocities/eci-velocity-mag-fps", 1);
	p_pfd.nd_ref_vrel = props.globals.getNode("/fdm/jsbsim/velocities/vtrue-fps", 1);
	p_pfd.nd_ref_eas = props.globals.getNode("/velocities/equivalent-kt", 1);

    p_pfd.nd_ref_major_mode = props.globals.getNode("/fdm/jsbsim/systems/dps/major-mode", 1);
    p_pfd.nd_ref_major_mode_bfs = props.globals.getNode("/fdm/jsbsim/systems/dps/major-mode-bfs", 1);
    p_pfd.nd_ref_abort_mode = props.globals.getNode("/fdm/jsbsim/systems/abort/abort-mode", 1);

    p_pfd.nd_ref_adi_att_sel = props.globals.getNode("/fdm/jsbsim/systems/adi/attitude-select", 1);
    p_pfd.nd_ref_adi_rate_range_sel = props.globals.getNode("/fdm/jsbsim/systems/adi/rate-range-select", 1);
    p_pfd.nd_ref_adi_err_sel = props.globals.getNode("/fdm/jsbsim/systems/adi/error-range-select", 1);

    p_pfd.nd_ref_autolaunch_master = props.globals.getNode("/fdm/jsbsim/systems/ap/launch/autolaunch-master", 1);
    p_pfd.nd_ref_launch_stage = props.globals.getNode("/fdm/jsbsim/systems/ap/launch/stage", 1);
    #p_pfd.nd_ref_auto_pitch = props.globals.getNode("/fdm/jsbsim/systems/ap/launch/autolaunch-pitch-channel", 1);
    p_pfd.nd_ref_auto_pitch = props.globals.getNode("/fdm/jsbsim/systems/ap/automatic-pitch-control", 1);


    #p_pfd.nd_ref_auto_roll = props.globals.getNode("/fdm/jsbsim/systems/ap/launch/autolaunch-roll-yaw-channel", 1);
    p_pfd.nd_ref_auto_roll = props.globals.getNode("/fdm/jsbsim/systems/ap/automatic-roll-control", 1);
    p_pfd.nd_ref_auto_sb = props.globals.getNode("/fdm/jsbsim/systems/ap/automatic-sb-control", 1);
	p_pfd.nd_ref_auto_throttle = props.globals.getNode("/fdm/jsbsim/systems/ap/automatic-throttle-control", 1);

    p_pfd.nd_ref_orbital_dap_auto = props.globals.getNode("/fdm/jsbsim/systems/ap/orbital-dap-auto", 1);
    p_pfd.nd_ref_up_mnvr_flag = props.globals.getNode("/fdm/jsbsim/systems/ap/up-mnvr-flag", 1);
    p_pfd.nd_ref_oms_mnvr_flag = props.globals.getNode("/fdm/jsbsim/systems/ap/oms-mnvr-flag", 1);

    p_pfd.nd_ref_altitude = props.globals.getNode("/position/altitude-ft", 1);
	p_pfd.nd_ref_altitude_agl = props.globals.getNode("/position/altitude-agl-ft", 1);

    p_pfd.nd_ref_acceleration = props.globals.getNode("/fdm/jsbsim/accelerations/a-pilot-ft_sec2", 1);
    p_pfd.nd_ref_Nz = props.globals.getNode("/fdm/jsbsim/accelerations/Nz", 1);


    p_pfd.nd_ref_tgt_inc = props.globals.getNode("/fdm/jsbsim/systems/ap/launch/inclination-target", 1);
    p_pfd.nd_ref_current_inc = props.globals.getNode("/fdm/jsbsim/systems/orbital/inclination-deg", 1);

    p_pfd.nd_ref_rem_dist = props.globals.getNode("/fdm/jsbsim/systems/entry_guidance/remaining-distance-nm", 1);
    p_pfd.nd_ref_hsi_source = props.globals.getNode("/fdm/jsbsim/systems/adi/hsi-source-select", 1);
    p_pfd.nd_ref_air_data = props.globals.getNode("/fdm/jsbsim/systems/adi/air-data-select", 1);

    p_pfd.nd_ref_xtrk = props.globals.getNode("/fdm/jsbsim/systems/ap/launch/cross-track", 1);







    p_pfd.air_data_stored = 1;


    p_pfd.ondisplay = func
    {
        device.set_DPS_off();
        device.dps_page_flag = 0;


	# FC bus selection

	device.fc_bus_displayed = "FC"~device.fc_bus;

	if (me.layer_id == "p_pfd")
		{
        	device.MEDS_menu_title.setText("FLIGHT INSTRUMENT MENU");

		# menu items

		p_pfd.menu_item.setColor(1.0, 1.0, 1.0);
		p_pfd.menu_item_frame.setColor(1.0, 1.0, 1.0);

		}
	else 
		{
        	device.MEDS_menu_title.setText("DATA BUS SELECT MENU");
		}







	# draw the fixed elements

	# ADI ################################################

	# ADI sphere grid	

	p_pfd.adi_sphere_bg = device.ADI.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(0.88,0.88,0.88)
	.setTranslation (255, 175)
        .setColor(1,1,1);

	p_pfd.adi_sphere_bg.max_pts = 0;
	p_pfd.adi_sphere_bg.coord_nd_ref_array = [];
	p_pfd.adi_sphere_bg.cmd_nd_ref_array = [];

	p_pfd.adi_sphere_bg_bright = device.ADI.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(0.24, 0.24, 0.32)
	.setTranslation (255, 175)
        .setColor(1,1,1);

	p_pfd.adi_sphere_bg_bright.max_pts = 0;
	p_pfd.adi_sphere_bg_bright.coord_nd_ref_array = [];
	p_pfd.adi_sphere_bg_bright.cmd_nd_ref_array = [];

	p_pfd.adi_sphere = device.ADI.createChild("path")
        .setStrokeLineWidth(1)
	.setTranslation (255, 175)
        .setColor(0.1,0.1,0.1);

	p_pfd.adi_sphere.max_pts = 0;
	p_pfd.adi_sphere.coord_nd_ref_array = [];
	p_pfd.adi_sphere.cmd_nd_ref_array = [];

	# group for dynamically re-drawn labels

	p_pfd.adi_inner = device.ADI.createChild("group");
	p_pfd.adi_inner.setTranslation (255, 175);
	p_pfd.adi_inner.flag = 0;



	# upper compass rose

	var plot_compass_upper = device.ADI.createChild("path", "data")
        .setStrokeLineWidth(1)
        .setColor(0.7,0.7,0.78);

	var data = SpaceShuttle.draw_compass_scale(71.25,12, 1.1, 6, 1.05);
	pfd_segment_draw(data, plot_compass_upper);

	data = SpaceShuttle.draw_circle(71.25, 30);
	pfd_segment_draw(data, plot_compass_upper);

	data = SpaceShuttle.draw_circle(95.0, 30);
	pfd_segment_draw(data, plot_compass_upper);

	plot_compass_upper.setTranslation (255, 175);

	place_compass_label(device.ADI, "0", 0.0, 85.0, 0,255,180);
	place_compass_label(device.ADI, "33", 30.0, 85.0, 0,255,180);
	place_compass_label(device.ADI, "30", 60.0, 85.0, 0,255,180);
	place_compass_label(device.ADI, "27", 90.0, 85.0, 0,255,180);
	place_compass_label(device.ADI, "24", 120.0, 85.0, 0,255,180);
	place_compass_label(device.ADI, "21", 150.0, 85.0, 0,255,180);
	place_compass_label(device.ADI, "18", 180.0, 85.0, 0,255,180);
	place_compass_label(device.ADI, "15", 210.0, 85.0, 0,255,180);
	place_compass_label(device.ADI, "12", 240.0, 85.0, 0,255,180);
	place_compass_label(device.ADI, "9", 270.0, 85.0, 0,255,180);
	place_compass_label(device.ADI, "6", 300.0, 85.0, 0,255,180);
	place_compass_label(device.ADI, "3", 330.0, 85.0, 0,255,180);

	# nose position indicator

	data = [[0.0, -26.0, 0], [0.0, -26.0, 1], [0.0, 26.0,1], [-28.0,0.0,0],[-23.0,0.0,1],[23.0,0.0,0],[28.0,0.0,1], [-10,0,0], [-8.6, 5.0, 1], [-5.0, 8.6, 1], [0.0,10.0,1],[5.0,8.6,1],[8.6,5.0,1],[10.0,0.0,1]];
	var plot_cross_thick = device.ADI.createChild("path", "cross_thick")
        .setStrokeLineWidth(2)
        .setColor(0.0, 0.8, 0.0);    #	 lighter green for better contrast
	pfd_segment_draw(data, plot_cross_thick);
	plot_cross_thick.setTranslation (255, 175);

	data = [[-23.0, 0.0, 0], [-23.0, 0.0, 1], [23.0,0.0,1]];
	var plot_cross_thin = device.ADI.createChild("path", "cross_thin")
        .setStrokeLineWidth(1)
        .setColor(0.0, 0.8, 0.0);
	pfd_segment_draw(data, plot_cross_thin);
	plot_cross_thin.setTranslation (255, 175);


	# ADI error needles

	var adi_errors = device.ADI.createChild("group");

	# scale
	
	var plot_error_arcs = adi_errors.createChild("path")
        .setStrokeLineWidth(1)
        .setColor(1, 0, 1);
	data = SpaceShuttle.draw_arc (92, 10, 335, 385);
	pfd_segment_draw(data, plot_error_arcs);

	data = SpaceShuttle.draw_comb (92, 11, 0.05, 335, 385, 1);
	pfd_segment_draw(data, plot_error_arcs);

	data = SpaceShuttle.draw_arc (92, 10, 65, 115);
	pfd_segment_draw(data, plot_error_arcs);

	data = SpaceShuttle.draw_comb (92, 11, 0.05, 65, 115, 2);
	pfd_segment_draw(data, plot_error_arcs);

	data = SpaceShuttle.draw_arc (92, 10, 155, 205);
	pfd_segment_draw(data, plot_error_arcs);

	data = SpaceShuttle.draw_comb (92, 11, 0.05, 155, 205, 3);
	pfd_segment_draw(data, plot_error_arcs);

	# labels	

	p_pfd.adi_error_label_p_u = write_small_label(device.ADI, "5", [348, 139,1], [0.9,0.1,0.85]);
	p_pfd.adi_error_label_p_l = write_small_label(device.ADI, "5", [348, 222,1], [0.9,0.1,0.85]);

	p_pfd.adi_error_label_p_u.enableUpdate();
	p_pfd.adi_error_label_p_l.enableUpdate();

	#p_pfd.adi_error_label_p_u.enableUpdate();
	#p_pfd.adi_error_label_p_l.enableUpdate();

	# needles

	p_pfd.att_error_needles = adi_errors.createChild("group");

	p_pfd.att_error_pitch = p_pfd.att_error_needles.createChild("path")
        .setStrokeLineWidth(3)
        .setColor(1,0,1);

	data = [[28.0, 0.0, 0], [95.0,0.0, 1]];
	pfd_segment_draw(data, p_pfd.att_error_pitch);

	p_pfd.att_error_yaw = p_pfd.att_error_needles.createChild("path")
        .setStrokeLineWidth(3)
        .setColor(1,0,1);

	data = [[0.0, 28, 0], [0.0,95.0, 1]];
	pfd_segment_draw(data, p_pfd.att_error_yaw);
	
	p_pfd.att_error_roll = p_pfd.att_error_needles.createChild("path")
        .setStrokeLineWidth(3)
        .setColor(1,0,1);

	data = [[0.0, -28, 0], [0.0,-95.0, 1]];
	pfd_segment_draw(data, p_pfd.att_error_roll);
	


	
	 adi_errors.setTranslation (255, 175);

	# ADI rate indicators ################################################

	# ADI rate ladders

	data = SpaceShuttle.draw_ladder (130, 3, 0.07, 4, 0.04, 0, 0 , 1);
	var plot_ADI_rate_roll = device.ADI.createChild("path", "ADI_rate_roll")
        .setStrokeLineWidth(1)
        .setColor(1, 1, 1);
	pfd_segment_draw(data, plot_ADI_rate_roll);
	plot_ADI_rate_roll.setTranslation(255, 70);

	data = SpaceShuttle.draw_ladder (130, 3, 0.07, 4, 0.04, 0, 1, 1);
	var plot_ADI_rate_yaw = device.ADI.createChild("path", "ADI_rate_yaw")
        .setStrokeLineWidth(1)
        .setColor(1, 1, 1);
	pfd_segment_draw(data, plot_ADI_rate_yaw);
	plot_ADI_rate_yaw.setTranslation(255, 280);

	data = SpaceShuttle.draw_ladder (130, 3, 0.07, 4, 0.04, 1, 1, 1);
	var plot_ADI_rate_pitch = device.ADI.createChild("path", "ADI_rate_pitch")
        .setStrokeLineWidth(1)
        .setColor(1, 1, 1);
	pfd_segment_draw(data, plot_ADI_rate_pitch);
	plot_ADI_rate_pitch.setTranslation(360, 175);

	# ADI rate labels

	p_pfd.rate_label_r_l = write_small_label(device.ADI, "5", [184, 78,1], [1,1,1]);
	p_pfd.rate_label_r_c = write_small_label(device.ADI, "0", [255, 68,1], [1,1,1]);   # fixed 0 in the center of the rate ladders, hidden by the triangle when centered
	p_pfd.rate_label_r_r = write_small_label(device.ADI, "5", [326, 78,1], [1,1,1]);

	p_pfd.rate_label_y_l = write_small_label(device.ADI, "5", [184, 280,1], [1,1,1]);
	p_pfd.rate_label_y_c = write_small_label(device.ADI, "0", [255, 291,1], [1,1,1]);
	p_pfd.rate_label_y_r = write_small_label(device.ADI, "5", [326, 280,1], [1,1,1]);

	p_pfd.rate_label_p_u = write_small_label(device.ADI, "5", [355, 109,1], [1,1,1]);
	p_pfd.rate_label_p_c = write_small_label(device.ADI, "0", [368.5, 179,1], [1,1,1]); 
	p_pfd.rate_label_p_l = write_small_label(device.ADI, "5", [355, 252,1], [1,1,1]);

	p_pfd.rate_label_r_l.enableUpdate();
	p_pfd.rate_label_r_r.enableUpdate();

	p_pfd.rate_label_y_l.enableUpdate();
	p_pfd.rate_label_y_r.enableUpdate();

	p_pfd.rate_label_p_u.enableUpdate();
	p_pfd.rate_label_p_l.enableUpdate();

	# ADI rate needles

	data = SpaceShuttle.draw_tmarker_down();
	p_pfd.adi_roll_rate_needle = device.ADI.createChild("path", "ADI_roll_rate_needle")
        .setStrokeLineWidth(1)
        .setColor(0,1,0)
		.setScale(0.75,1.3)
	.setColorFill(0,1,0)
	.moveTo(data[0][0], data[0][1]);
	for (var i = 0; (i< size(data)-1); i=i+1) 
		{p_pfd.adi_roll_rate_needle.lineTo(data[i+1][0], data[i+1][1]);}

	data = SpaceShuttle.draw_tmarker_left();
	p_pfd.adi_pitch_rate_needle = device.ADI.createChild("path", "ADI_pitch_rate_needle")
        .setStrokeLineWidth(1)
        .setColor(0,1,0)
		.setScale(1.3,0.75)
	.setColorFill(0,1,0)
	.moveTo(data[0][0], data[0][1]);
	for (var i = 0; (i< size(data)-1); i=i+1) 
		{p_pfd.adi_pitch_rate_needle.lineTo(data[i+1][0], data[i+1][1]);}

	data = SpaceShuttle.draw_tmarker_up();
	p_pfd.adi_yaw_rate_needle = device.ADI.createChild("path", "ADI_yaw_rate_needle")
        .setStrokeLineWidth(1)
        .setColor(0,1,0)
		.setScale(0.75,1.3)
	.setColorFill(0,1,0)
	.moveTo(data[0][0], data[0][1]);
	for (var i = 0; (i< size(data)-1); i=i+1) 
		{p_pfd.adi_yaw_rate_needle.lineTo(data[i+1][0], data[i+1][1]);}
	

	device.ADI.setScale (1.20);      #Resize of ADI 
	device.ADI.setTranslation (-65.0, -25.0); #(-50;-10)


	#BRG Flag ( if pointers are not fed with datas)

	p_pfd.brgflag = device.ADI.createChild("path")
	.setStrokeLineWidth(1)
	.setColorFill(1,0,0)
        .setColor(1,0,0);
	data = SpaceShuttle.draw_rect(20, 11);
	pfd_segment_draw(data, p_pfd.brgflag);
	p_pfd.brgflag.setTranslation (182, 305);

	p_pfd.brgflag_text = device.ADI.createChild("text")
	.setText("BRG")
        .setColor(0,0,0.15)
	.setFontSize(10)
	.setFont(p_pfd_font_1)
	.setAlignment("center-bottom")
	.setTranslation(182,309)
	.setRotation(0.0);







	# HSI ################################################

	# common clipping for all elements

	device.HSI.set("clip", "rect(0px, 512px, 460px, 0px)");

	p_pfd.HSI_static_group = device.HSI.createChild("group");   
	p_pfd.HSI_dynamic_group = device.HSI.createChild("group");

	# lower HSI compass rose


	var plot_compass_lower = p_pfd.HSI_static_group.createChild("path")
        .setStrokeLineWidth(1)
        .setColor(1,1,1);

	data = SpaceShuttle.draw_circle(95.0, 30);
	pfd_segment_draw(data, plot_compass_lower);

	data = SpaceShuttle.draw_compass_scale(95.0,8, 1.05, 1, 1.0);
	pfd_segment_draw(data, plot_compass_lower);


	# inner lower HSI compass rose 


	var plot_inner_compass_lower = p_pfd.HSI_dynamic_group.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(0.24, 0.24, 0.32)
        .setColor(1,1,1);

	data = SpaceShuttle.draw_circle(84.0, 30);
	pfd_segment_draw(data, plot_inner_compass_lower);

	data = SpaceShuttle.draw_compass_scale(84,36, 0.9, 2, 0.95);
	pfd_segment_draw(data, plot_inner_compass_lower);

	data = SpaceShuttle.draw_circle(58.0, 30);
	pfd_segment_draw(data, plot_inner_compass_lower);

	place_compass_label(p_pfd.HSI_dynamic_group, "N", 0.0, 63.0, 1,0,0);
	place_compass_label(p_pfd.HSI_dynamic_group, "E", 90.0, 63.0, 1,0,0);
	place_compass_label(p_pfd.HSI_dynamic_group, "S", 180.0, 63.0, 1,0,0);
	place_compass_label(p_pfd.HSI_dynamic_group, "W", 270.0, 63.0, 1,0,0);
	place_compass_label(p_pfd.HSI_dynamic_group, "3", 30.0, 63.0, 1,0,0);
	place_compass_label(p_pfd.HSI_dynamic_group, "6", 60.0, 63.0, 1,0,0);
	place_compass_label(p_pfd.HSI_dynamic_group, "12", 120.0, 63.0, 1,0,0);
	place_compass_label(p_pfd.HSI_dynamic_group, "15", 150.0, 63.0, 1,0,0);
	place_compass_label(p_pfd.HSI_dynamic_group, "21", 210.0, 63.0, 1,0,0);
	place_compass_label(p_pfd.HSI_dynamic_group, "24", 240.0, 63.0, 1,0,0);    
	place_compass_label(p_pfd.HSI_dynamic_group, "30", 300.0, 63.0, 1,0,0);
	place_compass_label(p_pfd.HSI_dynamic_group, "33", 330.0, 63.0, 1,0,0);

	# HSI bearing pointers 
	
	# earth-relative

	p_pfd.bearing_earth_relative = p_pfd.HSI_dynamic_group.createChild("group");

	var bearing_earthrel_symbol = p_pfd.bearing_earth_relative.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(1,0.5,0.0)
	.setScale(1.25)		
	.setTranslation(0.0,-110.0)
        .setColor(0,0,0);

	data = SpaceShuttle.draw_bearing_pointer_up();
	pfd_segment_draw(data, bearing_earthrel_symbol);

	var bearing_earthrel_label = p_pfd.bearing_earth_relative.createChild("text")
      	.setText("E")
        .setColor(0,0,0)
	.setFontSize(12)
	.setFont(p_pfd_font_1)
	.setAlignment("center-bottom")
	.setRotation(0.0)
	.setTranslation(0.0, -93.0);


	# earth-relative tail ( for mm 601 post PPA)

	
	p_pfd.bearing_earth_relative_tail = p_pfd.HSI_dynamic_group.createChild("group");

	var bearing_earth_relative_tail_symbol = p_pfd.bearing_earth_relative_tail.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(1,0.5,0)
	.setScale(1.0)	
	.setTranslation(0.0,-93.0)
        .setColor(0,0,0);

	data = SpaceShuttle.draw_rect(10.0, 14.0);
	pfd_segment_draw(data, bearing_earth_relative_tail_symbol);

	var bearing_earth_relative_tail_label = p_pfd.bearing_earth_relative_tail.createChild("text")
      	.setText("E")
        .setColor(0,0,0)
	.setFontSize(10)
	.setFont(p_pfd_font_1)
	.setAlignment("center-bottom")
	.setRotation(3.1415926)
	.setTranslation(0.0, -97.0);




	# inertial

	p_pfd.bearing_inertial = p_pfd.HSI_dynamic_group.createChild("group");

	var bearing_inertial_symbol = p_pfd.bearing_inertial.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(1,1,1)
	.setScale(1.25)	
	.setTranslation(0.0,-102.5)
        .setColor(0,0,0);

	data = SpaceShuttle.draw_bearing_pointer_up();
	pfd_segment_draw(data, bearing_inertial_symbol);

	var bearing_inertial_label = p_pfd.bearing_inertial.createChild("text")
      	.setText("I")
        .setColor(0,0,0)
	.setFontSize(12)
	.setFont(p_pfd_font_1)
	.setAlignment("center-bottom")
	.setRotation(0.0)
	.setTranslation(0.0, -87.0);

	p_pfd.bearing_inertial.setRotation(45.0 * math.pi/180.0);

	# HAC WP 1

	p_pfd.bearing_HAC_H = p_pfd.HSI_dynamic_group.createChild("group");

	var bearing_HAC_H_symbol = p_pfd.bearing_HAC_H.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(0,1,0)
	.setScale(1.4)	
	.setTranslation(0.0,-110.0)
        .setColor(0,0,0);

	data = SpaceShuttle.draw_runway_pointer_up();
	pfd_segment_draw(data, bearing_HAC_H_symbol);

	var bearing_HAC_H_label = p_pfd.bearing_HAC_H.createChild("text")
      	.setText("H")
        .setColor(0,0,0)
	.setFontSize(12)
	.setFont(p_pfd_font_1)
	.setAlignment("center-bottom")
	.setRotation(0.0)
	.setTranslation(0.0, -93.0);

	#p_pfd.bearing_HAC_H.setRotation(90.0 * math.pi/180.0);

	# HAC center

	p_pfd.bearing_HAC_C = p_pfd.HSI_dynamic_group.createChild("group");

	var bearing_HAC_C_symbol = p_pfd.bearing_HAC_C.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(1,1,1)
	.setScale(1.4)	
	.setTranslation(0.0,-95.0)
        .setColor(0,0,0);

	data = SpaceShuttle.draw_runway_pointer_up();
	pfd_segment_draw(data, bearing_HAC_C_symbol);

	var bearing_HAC_C_label = p_pfd.bearing_HAC_C.createChild("text")
      	.setText("C")
        .setColor(0,0,0)
	.setFontSize(12)
	.setFont(p_pfd_font_1)
	.setAlignment("center-bottom")
	.setRotation(0.0)
	.setTranslation(0.0, -79.0);



	# Runway

	p_pfd.bearing_rwy = p_pfd.HSI_dynamic_group.createChild("group");

	var bearing_rwy_symbol = p_pfd.bearing_rwy.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(0,1,0)
	.setScale(1.4)	
	.setTranslation(0.0,-110.0)  
        .setColor(0,0,0);

	data = SpaceShuttle.draw_runway_pointer_up();
	pfd_segment_draw(data, bearing_rwy_symbol);

	var bearing_rwy_label = p_pfd.bearing_rwy.createChild("text")
      	.setText("R")
        .setColor(0,0,0)
	.setFontSize(12)
	.setFont(p_pfd_font_1)
	.setAlignment("center-bottom")
	.setRotation(0.0)
	.setTranslation(0.0, -93.0);

	# Runway tail

	p_pfd.bearing_rwy_tail = p_pfd.HSI_dynamic_group.createChild("group");

	var bearing_rwy_tail_symbol = p_pfd.bearing_rwy_tail.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(0,1,0)
	.setScale(1.0)	
	.setTranslation(0.0,-86.0)
        .setColor(0,0,0);

	data = SpaceShuttle.draw_rect(10.0, 14.0);
	pfd_segment_draw(data, bearing_rwy_tail_symbol);

	var bearing_rwy_tail_label = p_pfd.bearing_rwy_tail.createChild("text")
      	.setText("R")
        .setColor(0,0,0)
	.setFontSize(10)
	.setFont(p_pfd_font_1)
	.setAlignment("center-bottom")
	.setRotation(3.1415926)
	.setTranslation(0.0, -90.0);

	# HSI course arrow 

	p_pfd.course_arrow = p_pfd.HSI_dynamic_group.createChild("group");

	var course_arrow_symbol = p_pfd.course_arrow.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(1,0,1)
	.setTranslation(0.0,-80.0)
        .setColor(0,0,0);

	data = SpaceShuttle.draw_course_arrow();
	pfd_segment_draw(data, course_arrow_symbol);


	# CDI

	p_pfd.cdi = p_pfd.HSI_dynamic_group.createChild("group");

	var cdi_center = p_pfd.HSI_static_group.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(0.7, 0.7, 0.78)
	.setTranslation(0.0, -20.0)
        .setColor(0.7,0.7,0.78);

	data = SpaceShuttle.draw_cdi_center();
	pfd_segment_draw(data, cdi_center);

	p_pfd.cdi_dots = p_pfd.cdi.createChild("group");

	var cdi_dot1 = p_pfd.cdi_dots.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(1, 1, 1)
	.setTranslation(20.0,0)
        .setColor(1,1,1);

	data = SpaceShuttle.draw_circle(4, 10);
	pfd_segment_draw(data, cdi_dot1);

	var cdi_dot2 = p_pfd.cdi_dots.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(1, 1, 1)
	.setTranslation(40.0,0)
        .setColor(1,1,1);
	pfd_segment_draw(data, cdi_dot2);

	var cdi_dot3 = p_pfd.cdi_dots.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(1, 1, 1)
	.setTranslation(-20.0,0)
        .setColor(1,1,1);
	pfd_segment_draw(data, cdi_dot3);

	var cdi_dot4 = p_pfd.cdi_dots.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(1, 1, 1)
	.setTranslation(-40.0,0)
        .setColor(1,1,1);
	pfd_segment_draw(data, cdi_dot4);

	#Scale of CDI for TAEM (10°/2.5°)
	p_pfd.cdi_scale_l = p_pfd.cdi.createChild("text")
	.setText("10")
    .setColor(0.7, 0.7, 0.78)
	.setFontSize(10)
	.setFont(p_pfd_font_2)
	.setAlignment("center-bottom")
	.setTranslation(47.5,12.5)
	.setRotation(0.0)
	.setVisible(0);
	

	p_pfd.cdi_scale_r = p_pfd.cdi.createChild("text")
	.setText("10")
    .setColor(0.7, 0.7, 0.78)
	.setFontSize(10)
	.setFont(p_pfd_font_2)
	.setAlignment("center-bottom")
	.setTranslation(-47.5,12.5)
	.setRotation(0.0)
	.setVisible(0);
	

	# CDI needle
	
	p_pfd.cdi_needle = p_pfd.cdi.createChild("path")
	.setStrokeLineWidth(3)
        .setColor(1, 0, 1);

	data = [[0.0,-35.0,0],[0.0, 35.0, 1]];
	pfd_segment_draw(data, p_pfd.cdi_needle);


	#CDI Flag (if CDI not fed by datas, for mm 104 and in OPS 3 with no entry guidance or TAEM available)

	p_pfd.cdiflag = p_pfd.cdi.createChild("path")
	.setStrokeLineWidth(1)
	.setColorFill(1,0,0)
        .setColor(1,0,0);
	data = SpaceShuttle.draw_rect(20, 11);
	pfd_segment_draw(data, p_pfd.cdiflag);
	p_pfd.cdiflag.setTranslation (0.0, -30.0);

	p_pfd.cdiflag_text = p_pfd.cdi.createChild("text")
	.setText("CDI")
        .setColor(0,0,0.15)
	.setFontSize(10)
	.setFont(p_pfd_font_1)
	.setAlignment("center-bottom")
	.setTranslation(0.0,-26.0)
	.setRotation(0.0);


	
	

	#HSI size adjustments and colors
	
	device.HSI.setScale (1.10);

	p_pfd.HSI_static_group.setColor(0.7,0.7,0.78); #Grey external arc
	p_pfd.HSI_static_group.setTranslation (-13.0, 18.0); #(-10;20)

	p_pfd.HSI_dynamic_group.setTranslation (-13.0, 18.0);
	

	# KEAS tape ################################################

	# common clipping for tape group

	device.tapes.set("clip", "rect(90px, 512px, 280px, 0px)");

	var keas_group = device.tapes.createChild("group");

	# frame
	p_pfd.plot_keas_tape = keas_group.createChild("path", "data")
        .setStrokeLineWidth(1)
        .setColor(1,1,1);
	data= SpaceShuttle.draw_rect(45, 190);
	pfd_segment_draw(data, p_pfd.plot_keas_tape);
	p_pfd.plot_keas_tape.setTranslation (40, 185);

	# inner tape

	p_pfd.keas_tape = keas_group.createChild("group");

	p_pfd.keas_tape_background = p_pfd.keas_tape.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(1, 1, 1)
        .setColor(1,1,1);
	var data1 = SpaceShuttle.draw_rect(43, 10800);
	pfd_segment_draw(data1, p_pfd.keas_tape_background);

	p_pfd.keas_tape_ladder = p_pfd.keas_tape.createChild("path")
        .setStrokeLineWidth(1)
		.setScale(1)
        .setColor(0,0,0.15);	
		data1 = SpaceShuttle.draw_ladder(10800, 280, 1.5 * 0.001296, 0, 0, 1, 1, 0);
	pfd_segment_draw(data1, p_pfd.keas_tape_ladder);
	p_pfd.keas_tape_ladder.setTranslation(10,0);

	p_pfd.keas_tape.labels = p_pfd.keas_tape.createChild("group");
	draw_mach_labels(p_pfd.keas_tape.labels);

	# display box

	p_pfd.keas_display_box = keas_group.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(0,0,0.15)
        .setColor(0.7,0.7,0.78);
	data1= SpaceShuttle.draw_rect(45, 20);
	pfd_segment_draw(data1, p_pfd.keas_display_box);
	p_pfd.keas_display_box.setTranslation (40, 185);

	p_pfd.keas_display_text = keas_group.createChild("text")
	.setText("0.0")
        .setColor(1,1,1)
	.setFontSize(14)
	.setFont(p_pfd_font_2)
	.setAlignment("center-bottom")
	.setTranslation(40,190)
	.setRotation(0.0);

	p_pfd.keas_display_text.enableFast();





	# alpha tape ################################################

	var alpha_group = device.tapes.createChild("group");

	# frame

	p_pfd.plot_alpha_tape = alpha_group.createChild("path", "data")
        .setStrokeLineWidth(1)
        .setColor(1,1,1);
	pfd_segment_draw(data, p_pfd.plot_alpha_tape);
	p_pfd.plot_alpha_tape.setTranslation (92.5, 185);

	# inner tape

	p_pfd.alpha_tape = alpha_group.createChild("group");

	


	p_pfd.alpha_tape_background1 = p_pfd.alpha_tape.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(1, 1, 1)
	.setTranslation(0.0, -855.0)
        .setColor(1,1,1);
	var data1 = SpaceShuttle.draw_rect(43, 1710);
	pfd_segment_draw(data1, p_pfd.alpha_tape_background1);

	p_pfd.alpha_tape_background2 = p_pfd.alpha_tape.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(0.24, 0.24, 0.32)
	.setTranslation(0.0, 855.0)
        .setColor(1,1,1);
	pfd_segment_draw(data1, p_pfd.alpha_tape_background2);

	p_pfd.alpha_tape_ladder_upper = p_pfd.alpha_tape.createChild("path")
        .setStrokeLineWidth(1)
	.setTranslation(13,-855.0)
        .setColor(0,0,0.15);	
	data1 = SpaceShuttle.draw_ladder(1710, 180, 0.50*0.01169, 0, 0, 1, 0, 0);
	pfd_segment_draw(data1, p_pfd.alpha_tape_ladder_upper);

	p_pfd.alpha_tape_ladder_lower = p_pfd.alpha_tape.createChild("path")
        .setStrokeLineWidth(1)
	.setTranslation(13,855.0)
        .setColor(1,1,1);	
	pfd_segment_draw(data1, p_pfd.alpha_tape_ladder_lower);

	

	p_pfd.alpha_tape.labels_upper = p_pfd.alpha_tape.createChild("group");
	draw_alpha_labels_upper(p_pfd.alpha_tape.labels_upper);

	p_pfd.alpha_tape.labels_lower = p_pfd.alpha_tape.createChild("group");
	draw_alpha_labels_lower(p_pfd.alpha_tape.labels_lower);


	

	#Green transparent Band in OPS 3 for allowable alpha range (min/max)

	p_pfd.alpha_tape_green_stripe = p_pfd.alpha_tape.createChild("path")
        .setStrokeLineWidth(1.0)
	.setTranslation(18,0)
	.setRotation(0)
	.setScale(1,0.5)
    .setColor(0.0, 1.0, 0.0, 0.7)
	.setColorFill(0.0, 1.0, 0.0, 0.7); 	
	var data1 = SpaceShuttle.draw_rect(9, 190);
	pfd_segment_draw(data1, p_pfd.alpha_tape_green_stripe);

	p_pfd.alpha_tape_green_stripe.setVisible(0); 

	#Losange for max L/D in Taem ( double losange or one losange with big black width fill with purple)

	p_pfd.alpha_tape_max_LD = p_pfd.alpha_tape.createChild("path")
        .setStrokeLineWidth(2.0)
	.setTranslation(18,0.0)
	.setRotation(180,180)
        .setColor(1,0,1)
		.setColorFill(0, 0, 0.15);	
	var data1 = SpaceShuttle.draw_rect(7, 7);
	pfd_segment_draw(data1, p_pfd.alpha_tape_max_LD);

	p_pfd.alpha_tape_max_LD.setVisible(0);
	#p_pfd.alpha_tape_max_LD.set("z-index",-1);


	# display box

	p_pfd.alpha_display_box = alpha_group.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(0,0,0.15)
        .setColor(0.7,0.7,0.78);
	data1= [[-24, -10,0], [-24, 10, 1], [16, 10, 1], [22,0,1], [16,-10,1],[-24,-10,1], [-24,-10,1]];
	pfd_segment_draw(data1, p_pfd.alpha_display_box);
	p_pfd.alpha_display_box.setTranslation (90, 185);

	p_pfd.alpha_display_text = alpha_group.createChild("text")
	.setText("0.0")
        .setColor(1,1,1)
	.setFontSize(14)
	.setFont(p_pfd_font_2)
	.setAlignment("center-bottom")
	.setTranslation(90,190)
	.setRotation(0.0);

	p_pfd.alpha_display_text.enableFast();




	# H tape  ################################################

	var H_group = device.tapes.createChild("group");

	p_pfd.H_tape = H_group.createChild("group");

	# frame

	p_pfd.plot_H_tape = H_group.createChild("path", "data")
        .setStrokeLineWidth(1)
        .setColor(1,1,1);
	pfd_segment_draw(data, p_pfd.plot_H_tape);
	p_pfd.plot_H_tape.setTranslation (417, 185);

	# inner tape

	p_pfd.H_tape_background1 = p_pfd.H_tape.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(1, 1, 1)
	.setTranslation(0.0, -750.0)
        .setColor(1,1,1);
	var data1 = SpaceShuttle.draw_rect(43, 1500.0);
	pfd_segment_draw(data1, p_pfd.H_tape_background1);

	p_pfd.H_tape_background2 = p_pfd.H_tape.createChild("path")
        .setStrokeLineWidth(1)
	#.setColorFill(0.24, 0.24, 0.32) 
	.setColorFill(1, 1, 1) #Grey only for ladder below 0 ie. lowerladder 2k
	.setTranslation(0.0, 50.0)
        .setColor(1,1,1);
	var data1 = SpaceShuttle.draw_rect(43, 100.0);
	pfd_segment_draw(data1, p_pfd.H_tape_background2);

	p_pfd.H_tape_ladder_upper = p_pfd.H_tape.createChild("path")
        .setStrokeLineWidth(1)
	.setTranslation(-12,-750)
        .setColor(0,0,0.15);	
	data1 = SpaceShuttle.draw_ladder(1500, 100, 1.5 * 0.01, 0, 0, 1, 0, 0);
	pfd_segment_draw(data1, p_pfd.H_tape_ladder_upper);

	p_pfd.H_tape_ladder_lower = p_pfd.H_tape.createChild("path")
        .setStrokeLineWidth(1)
	.setTranslation(-12, 50)
        .setColor(0,0,0.15);	#White only for ladder below 0 ie. lowerladder 2k	
	data1 = SpaceShuttle.draw_ladder(100, 10, 1.5 * 0.1, 0, 0, 1, 0, 0);
	pfd_segment_draw(data1, p_pfd.H_tape_ladder_lower);

	p_pfd.H_tape.labels_upper_miles = p_pfd.H_tape.createChild("group");
	draw_H_labels_upper_miles(p_pfd.H_tape.labels_upper_miles);

	p_pfd.H_tape.labels_lower_miles = p_pfd.H_tape.createChild("group");
	draw_H_labels_lower_miles(p_pfd.H_tape.labels_lower_miles);

	p_pfd.H_tape.labels_upper_2k = p_pfd.H_tape.createChild("group");
	draw_H_labels_upper_2k(p_pfd.H_tape.labels_upper_2k);

	p_pfd.H_tape.labels_lower_2k = p_pfd.H_tape.createChild("group");
	draw_H_labels_lower_2k(p_pfd.H_tape.labels_lower_2k);

	p_pfd.H_tape.labels_upper_30k = p_pfd.H_tape.createChild("group");
	draw_H_labels_upper_30k(p_pfd.H_tape.labels_upper_30k);

	p_pfd.H_tape.labels_lower_30k = p_pfd.H_tape.createChild("group");
	draw_H_labels_lower_30k(p_pfd.H_tape.labels_lower_30k);

	p_pfd.H_tape.labels_upper_100k = p_pfd.H_tape.createChild("group");
	draw_H_labels_upper_100k(p_pfd.H_tape.labels_upper_100k);

	p_pfd.H_tape.labels_lower_100k = p_pfd.H_tape.createChild("group");
	draw_H_labels_lower_100k(p_pfd.H_tape.labels_lower_100k);

	p_pfd.H_tape.labels_upper_400k = p_pfd.H_tape.createChild("group");
	draw_H_labels_upper_400k(p_pfd.H_tape.labels_upper_400k);

	p_pfd.H_tape.labels_lower_400k = p_pfd.H_tape.createChild("group");
	draw_H_labels_lower_400k(p_pfd.H_tape.labels_lower_400k);

	# display box

	p_pfd.H_display_box = H_group.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(0,0,0.15)
        .setColor(0.7,0.7,0.78);
	data1= SpaceShuttle.draw_rect(45, 20);
	pfd_segment_draw(data1, p_pfd.H_display_box);
	p_pfd.H_display_box.setTranslation (417, 185);

	p_pfd.H_display_text = H_group.createChild("text")
	.setText("0.0")
        .setColor(1,1,1)
	.setFontSize(14)
	.setFont(p_pfd_font_2)
	.setAlignment("center-bottom")
	.setTranslation(417,190)
	.setRotation(0.0);

	p_pfd.H_display_text.enableFast();




	# Hdot tape ##############################################

	var Hdot_group = device.tapes.createChild("group");

	p_pfd.Hdot_tape = Hdot_group.createChild("group");


	p_pfd.plot_Hdot_tape = Hdot_group.createChild("path", "data")
        .setStrokeLineWidth(1)
        .setColor(1,1,1);
	pfd_segment_draw(data, p_pfd.plot_Hdot_tape);
	p_pfd.plot_Hdot_tape.setTranslation (480, 185);


	# inner tape

	p_pfd.Hdot_tape_background1 = p_pfd.Hdot_tape.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(1, 1, 1)
	.setTranslation(0.0, -900.0)
        .setColor(1,1,1);
	var data1 = SpaceShuttle.draw_rect(43, 1800.0);
	pfd_segment_draw(data1, p_pfd.Hdot_tape_background1);

	p_pfd.Hdot_tape_background2 = p_pfd.Hdot_tape.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(0.24,0.24,0.32)
	.setTranslation(0.0, 900.0)
        .setColor(1,1,1);
	var data1 = SpaceShuttle.draw_rect(43, 1800.0);
	pfd_segment_draw(data1, p_pfd.Hdot_tape_background2);

	p_pfd.Hdot_tape_ladder_upper = p_pfd.Hdot_tape.createChild("path")
        .setStrokeLineWidth(1)
	.setTranslation(-7.5,-900)
        .setColor(0,0,0.15);	
	data1 = SpaceShuttle.draw_ladder(1800, 60, 2.0 * 0.0055, 0, 0, 1, 0, 0);
	pfd_segment_draw(data1, p_pfd.Hdot_tape_ladder_upper);

	p_pfd.Hdot_tape_ladder_lower = p_pfd.Hdot_tape.createChild("path")
        .setStrokeLineWidth(1)
	.setTranslation(-7.5, 900)
        .setColor(1,1,1);	
	data1 = SpaceShuttle.draw_ladder(1800, 60, 2.0 * 0.0055, 0, 0, 1, 0, 0);
	pfd_segment_draw(data1, p_pfd.Hdot_tape_ladder_lower);

	p_pfd.Hdot_tape.labels_upper = p_pfd.Hdot_tape.createChild("group");
	draw_Hdot_labels_upper(p_pfd.Hdot_tape.labels_upper);

	p_pfd.Hdot_tape.labels_lower = p_pfd.Hdot_tape.createChild("group");
	draw_Hdot_labels_lower(p_pfd.Hdot_tape.labels_lower);

	# display box

	p_pfd.Hdot_display_box = Hdot_group.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(0,0,0.15)
        .setColor(0.7,0.7,0.78);
	data1= SpaceShuttle.draw_rect(45, 20);
	pfd_segment_draw(data1, p_pfd.Hdot_display_box);
	p_pfd.Hdot_display_box.setTranslation (480, 185);

	p_pfd.Hdot_display_text = Hdot_group.createChild("text")
	.setText("0.0")
        .setColor(1,1,1)
	.setFontSize(14)
	.setFont(p_pfd_font_2)
	.setAlignment("center-bottom")
	.setTranslation(480,190)
	.setRotation(0.0);

	p_pfd.Hdot_display_text.enableFast();


	device.HSI.setTranslation (255, 425);

	# accelerometer #############################################

	p_pfd.acc_arc = device.symbols.createChild("path")
        .setStrokeLineWidth(1)
        .setColor(0.7,0.7,0.78);
	data= SpaceShuttle.draw_arc(35, 20, 135.0, 360.0);
	pfd_segment_draw(data, p_pfd.acc_arc);

	data = SpaceShuttle.draw_arc_scale(35 ,6, 1.15, 0, 1.0, 135.0,360.0);
	pfd_segment_draw(data, p_pfd.acc_arc);

	p_pfd.acc_labels = device.symbols.createChild("group");
	draw_acc_labels(p_pfd.acc_labels);

	p_pfd.acc_arc.setTranslation (65, 408);
	p_pfd.acc_labels.setTranslation (65, 413);

	# display box

	p_pfd.acc_display_box = device.symbols.createChild("path")
        .setStrokeLineWidth(1)
        .setColor(1,1,1);                            #light grey (?)
	data = SpaceShuttle.draw_rect(45, 20);
	pfd_segment_draw(data, p_pfd.acc_display_box);
	p_pfd.acc_display_box.setTranslation (95, 393);

	p_pfd.acc_display_text = device.symbols.createChild("text")
	.setText("0.0g")
        .setColor(1,1,1)
	.setFontSize(14)
	.setFont(p_pfd_font_2)
	.setAlignment("center-bottom")
	.setTranslation(100,400)
	.setRotation(0.0);

	p_pfd.acc_display_text.enableFast();

	p_pfd.acc_label = device.symbols.createChild("text")
	.setText("Accel")
        .setColor(0.7,0.7,0.78)
	.setFontSize(12)
	.setFont(p_pfd_font_1)
	.setAlignment("center-bottom")
	.setTranslation(102,417)
	.setRotation(0.0);

	p_pfd.acc_label.enableUpdate();

	#Nz to Hold marker

	p_pfd.acc_nz_marker = device.symbols.createChild("path")
    .setStrokeLineWidth(2.0)
	.setColorFill(1.0, 0.0, 1.0)
	.setScale(0.9)
    .setColor(1.0, 0.0, 1.0);
	
	data = SpaceShuttle.draw_slim_line();
	pfd_segment_draw(data, p_pfd.acc_nz_marker);
	p_pfd.acc_nz_marker.setTranslation (65, 408);
	p_pfd.acc_nz_marker.setVisible(0);

	# marker arrow


	p_pfd.acc_needle = device.symbols.createChild("path")
        .setStrokeLineWidth(2)
	.setColorFill(0.0, 1.0, 0.0)
	.setScale(0.9)
        .setColor(0.0, 1.0, 0.0);
	
	data = draw_slim_arrow_down();
	pfd_segment_draw(data, p_pfd.acc_needle);
	p_pfd.acc_needle.setTranslation (65, 408);


	

	# glideslope indicator ######################################################

	p_pfd.glideslope = device.symbols.createChild("group");

	var glideslope_upper_box = p_pfd.glideslope.createChild("path")
        .setStrokeLineWidth(1)
	.setTranslation(440,335)
        .setColor(1,1,1);
	data = SpaceShuttle.draw_rect(12, 75);
	pfd_segment_draw(data, glideslope_upper_box);

	var glideslope_lower_box = p_pfd.glideslope.createChild("path")
        .setStrokeLineWidth(1)
	.setTranslation(440,411)
        .setColor(1,1,1);
	data = SpaceShuttle.draw_rect(12, 75);
	pfd_segment_draw(data, glideslope_lower_box);

	p_pfd.glideslope_label_upper = p_pfd.glideslope.createChild("text")
	.setText("5K")
        .setColor(0.7,0.7,0.78)
	.setFontSize(12)
	.setFont(p_pfd_font_1)
	.setAlignment("center-bottom")
	.setTranslation(440,296)
	.setRotation(0.0);

	p_pfd.glideslope_label_lower = p_pfd.glideslope.createChild("text")
	.setText("5K")
        .setColor(0.7,0.7,0.78)
	.setFontSize(12)
	.setFont(p_pfd_font_1)
	.setAlignment("center-bottom")
	.setTranslation(440,458)
	.setRotation(0.0);

	var glideslope_dot1 = p_pfd.glideslope.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(0.7,0.7,0.78)
	.setTranslation(440.0,305.0)
        .setColor(0.7,0.7,0.78);

	data = SpaceShuttle.draw_circle(4, 10);
	pfd_segment_draw(data, glideslope_dot1);

	var glideslope_dot2 = p_pfd.glideslope.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(0.7,0.7,0.78)
	.setTranslation(440.0,340.0)
        .setColor(0.7,0.7,0.78);

	pfd_segment_draw(data, glideslope_dot2);

	var glideslope_dot3 = p_pfd.glideslope.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(0.7,0.7,0.78)
	.setTranslation(440.0,406.0)
        .setColor(0.7,0.7,0.78);

	pfd_segment_draw(data, glideslope_dot3);

	var glideslope_dot4 = p_pfd.glideslope.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(0.7,0.7,0.78)
	.setTranslation(440.0,441.0)
        .setColor(0.7,0.7,0.78);

	pfd_segment_draw(data, glideslope_dot4);

	data = SpaceShuttle.draw_tmarker_left();
	p_pfd.glideslope_needle = p_pfd.glideslope.createChild("path")
        .setStrokeLineWidth(1)
        .setColor(0.0, 1.0, 0.0)
	.setScale(1.56,0.9)
	.setColorFill(0.0, 1.0, 0.0)
	.moveTo(data[0][0], data[0][1]);
	for (var i = 0; (i< size(data)-1); i=i+1) 
		{p_pfd.glideslope_needle.lineTo(data[i+1][0], data[i+1][1]);}


		#GS Flag ( below 1500 ft AGL)

	p_pfd.gsflag = p_pfd.glideslope.createChild("path")
	.setStrokeLineWidth(1)
	.setColorFill(1,0,0)
        .setColor(1,0,0);
	data = SpaceShuttle.draw_rect(20, 11);
	pfd_segment_draw(data, p_pfd.gsflag);
	p_pfd.gsflag.setTranslation (440, 372.5);

	p_pfd.gsflag_text = p_pfd.glideslope.createChild("text")
	.setText("GS")
        .setColor(0,0,0.15)
	.setFontSize(10)
	.setFont(p_pfd_font_1)
	.setAlignment("center-bottom")
	.setTranslation(440,376)
	.setRotation(0.0);


	# H dot dot indicator ######################################################

	p_pfd.vert_acc = device.symbols.createChild("group");

	var vert_acc_upper_box = p_pfd.vert_acc.createChild("path")
        .setStrokeLineWidth(1)
	.setTranslation(475,342)
	.setColorFill(1,1,1)
        .setColor(1,1,1);
	data = SpaceShuttle.draw_rect(10, 75);
	pfd_segment_draw(data, vert_acc_upper_box);

	var vert_acc_lower_box = p_pfd.vert_acc.createChild("path")
        .setStrokeLineWidth(1)
	.setTranslation(475,418)
	.setColorFill(0.24, 0.24, 0.32)
        .setColor(1,1,1);
	data = SpaceShuttle.draw_rect(10, 75);
	pfd_segment_draw(data, vert_acc_lower_box);

	var vert_acc_ladder = p_pfd.vert_acc.createChild("path")
        .setStrokeLineWidth(1)
	.setTranslation(480, 380)
        .setColor(1,1,1);	
	data1 = SpaceShuttle.draw_ladder(140, 11, 0.025, 0, 0, 1, 0, 0);
	pfd_segment_draw(data1, vert_acc_ladder);

	var vert_acc_label1 = p_pfd.vert_acc.createChild("text")
	.setText("H")
        .setColor(0.7,0.7,0.78)
	.setFontSize(12)
	.setFont(p_pfd_font_1)
	.setAlignment("center-bottom")
	.setTranslation(475,300)
	.setRotation(0.0);

	var vert_acc_label2 = p_pfd.vert_acc.createChild("text")
	.setText(".")
        .setColor(0.7,0.7,0.78)
	.setFontSize(9)
	.setFont(p_pfd_font_1)
	.setAlignment("center-bottom")
	.setTranslation(474,289);

	var vert_acc_label2bis = p_pfd.vert_acc.createChild("text")
	.setText(".")
        .setColor(0.7,0.7,0.78)
	.setFontSize(9)
	.setFont(p_pfd_font_1)
	.setAlignment("center-bottom")
	.setTranslation(476,289);

	var vert_acc_label3 = p_pfd.vert_acc.createChild("text")
	.setText("10")
        .setColor(1,1,1)
	.setFontSize(12)
	.setFont(p_pfd_font_2)
	.setAlignment("center-bottom")
	.setTranslation(495,315);

	var vert_acc_label4 = p_pfd.vert_acc.createChild("text")
	.setText("-10")
        .setColor(1,1,1)
	.setFontSize(12)
	.setFont(p_pfd_font_2) 
	.setAlignment("center-bottom")
	.setTranslation(495,455);

	var vert_acc_label5 = p_pfd.vert_acc.createChild("text")
	.setText("0")
        .setColor(1,1,1)
	.setFontSize(12)
	.setFont(p_pfd_font_2) 
	.setAlignment("center-bottom")
	.setTranslation(488,385);

	data = SpaceShuttle.draw_tmarker_right();
	p_pfd.vert_acc_needle = p_pfd.vert_acc.createChild("path")
        .setStrokeLineWidth(1)
        .setColor(0.0, 1.0, 0.0)
	.setScale(1.56,0.9)
	.setTranslation(475, 380)
	.setColorFill(0.0, 1.0, 0.0)
	.moveTo(data[0][0], data[0][1]);
	for (var i = 0; (i< size(data)-1); i=i+1) 
		{p_pfd.vert_acc_needle.lineTo(data[i+1][0], data[i+1][1]);}



	# numerical values #############################################

	# X-Trk

	p_pfd.xtrk = device.symbols.createChild("group");

	p_pfd.xtrk_display_box = p_pfd.xtrk.createChild("path")
        .setStrokeLineWidth(1)
	.setTranslation(470,355)
        .setColor(1,1,1);
	data = SpaceShuttle.draw_rect(40, 20);
	pfd_segment_draw(data, p_pfd.xtrk_display_box);

	p_pfd.xtrk_display_text = p_pfd.xtrk.createChild("text")
	.setText("0.0")
        .setColor(1,1,1)
	.setFontSize(14)
	.setFont(p_pfd_font_2)
	.setAlignment("center-bottom")
	.setTranslation(473,361)
	.setRotation(0.0);

	var xtrk_label =p_pfd.xtrk.createChild("text")
	.setText("X-Trk")
        .setColor(0.7,0.7,0.78)
	.setFontSize(13)
	.setFont(p_pfd_font_1)
	.setAlignment("center-bottom")
	.setTranslation(425,360)
	.setRotation(0.0);
	
	# Delta-Inc

	p_pfd.dInc = device.symbols.createChild("group");

	p_pfd.dInc_display_box = p_pfd.dInc.createChild("path")
        .setStrokeLineWidth(1)
	.setTranslation(466,390)
        .setColor(1,1,1);
	data = SpaceShuttle.draw_rect(48, 20);
	pfd_segment_draw(data, p_pfd.dInc_display_box);

	p_pfd.dInc_display_text = p_pfd.dInc.createChild("text")
	.setText("0.0")
        .setColor(1,1,1)
	.setFontSize(14)
	.setFont(p_pfd_font_2)
	.setAlignment("center-bottom")
	.setTranslation(471.5,396)
	.setRotation(0.0);

	var dInc_label = p_pfd.dInc.createChild("text")
	.setText("Δ Inc")
        .setColor(0.7,0.7,0.78)
	.setFontSize(13)
	.setFont(p_pfd_font_1)
	.setAlignment("center-bottom")
	.setTranslation(416,395)
	.setRotation(0.0);


	# dist to rwy

	p_pfd.dist_to_rwy = device.symbols.createChild("group");

	p_pfd.dist_to_rwy_display_box = p_pfd.dist_to_rwy.createChild("path")
        .setStrokeLineWidth(1)
	.setTranslation(385,408)
        .setColor(1,1,1);
	data = SpaceShuttle.draw_rect(35, 13);
	pfd_segment_draw(data, p_pfd.dist_to_rwy_display_box);

	p_pfd.dist_to_rwy_display_text = p_pfd.dist_to_rwy.createChild("text")
	.setText("0.0")
        .setColor(1,1,1)
	.setFontSize(11)
	.setFont(p_pfd_font_2)
	.setAlignment("center-bottom")
	.setTranslation(389,413)
	.setRotation(0.0);

	 p_pfd.dist_to_rwy_label = p_pfd.dist_to_rwy.createChild("text")
	.setText("RWY")
        .setColor(0.7,0.7,0.78)
	.setFontSize(14)
	.setFont(p_pfd_font_1)
	.setAlignment("center-bottom")
	.setTranslation(390,401)
	.setRotation(0.0);
	
	p_pfd.dist_to_rwy_label.enableUpdate();

	# dist to HAC-C

	p_pfd.dist_to_HAC_C = device.symbols.createChild("group");

	p_pfd.dist_to_HAC_C_display_box = p_pfd.dist_to_HAC_C.createChild("path")
        .setStrokeLineWidth(1)
	.setTranslation(385,442)
        .setColor(1,1,1);
	data = SpaceShuttle.draw_rect(35, 13);
	pfd_segment_draw(data, p_pfd.dist_to_HAC_C_display_box);

	p_pfd.dist_to_HAC_C_display_text = p_pfd.dist_to_HAC_C.createChild("text")
	.setText("0.0")
        .setColor(1,1,1)
	.setFontSize(11)
	.setFont(p_pfd_font_2)
	.setAlignment("center-bottom")
	.setTranslation(389,447)
	.setRotation(0.0);

	 p_pfd.dist_to_HAC_C_label = p_pfd.dist_to_HAC_C.createChild("text")
	.setText("HAC-C")
        .setColor(0.7,0.7,0.78)
	.setFontSize(14)
	.setFont(p_pfd_font_1)
	.setAlignment("center-bottom")
	.setTranslation(390,435)
	.setRotation(0.0);

	# Delta-Az

	p_pfd.Daz = device.symbols.createChild("group");

	p_pfd.Daz_display_box = p_pfd.Daz.createChild("path")
        .setStrokeLineWidth(1)
	.setTranslation(352,340)
        .setColor(1,1,1);
	data = SpaceShuttle.draw_rect(27, 20);
	pfd_segment_draw(data, p_pfd.Daz_display_box);

	p_pfd.Daz_display_text = p_pfd.Daz.createChild("text")
	.setText("0.0°")
        .setColor(1,1,1)
	.setFontSize(11)
	.setFont(p_pfd_font_2)
	.setAlignment("center-bottom")
	.setTranslation(354,345)
	.setRotation(0.0);

	p_pfd.Daz_label =p_pfd.Daz.createChild("text")
	.setText("ΔAZ")
        .setColor(0.7,0.7,0.78)
	.setFontSize(14)
	.setFont(p_pfd_font_1)
	.setAlignment("center-bottom")
	.setTranslation(322,345)
	.setRotation(0.0);

	p_pfd.Daz_label.enableUpdate();

	

	}

    
    p_pfd.offdisplay = func
    {
	device.symbols.removeAllChildren();
	device.HSI.removeAllChildren();
	device.tapes.removeAllChildren();
	device.ADI.removeAllChildren();
	p_pfd.adi_inner.flag = -1;

        p_pfd.menu_item.setColor(meds_r, meds_g, meds_b);
	p_pfd.menu_item_frame.setColor(meds_r, meds_g, meds_b);

	device.fc_bus_displayed = "";

    }
    
    p_pfd.update = func
    {


	# get mission-specific parameters and manage devices #########################################



    	var major_mode = p_pfd.nd_ref_major_mode.getValue();

	if (SpaceShuttle.bfs_in_control == 1)
		{
    		major_mode = p_pfd.nd_ref_major_mode_bfs.getValue();
		}

	var mm_appendix = "";
    	var abort_mode = p_pfd.nd_ref_abort_mode.getValue();


	#var pitch = getprop("/fdm/jsbsim/systems/navigation/state-vector/pitch-deg");
	#var yaw = getprop("/fdm/jsbsim/systems/navigation/state-vector/yaw-deg");
	#var roll = getprop("/fdm/jsbsim/systems/navigation/state-vector/roll-deg");

    	var pitch = p_pfd.nd_ref_pitch.getValue();
	var yaw =  p_pfd.nd_ref_yaw.getValue();
    	var roll = p_pfd.nd_ref_roll.getValue();

	#var course = getprop("/fdm/jsbsim/velocities/course-deg");
	var course = p_pfd.nd_ref_course_deg.getValue();
	

	#var beta_deg = getprop("/fdm/jsbsim/aero/beta-deg");
	#var alpha_deg = getprop("/fdm/jsbsim/aero/alpha-deg");

    	var beta_deg = p_pfd.nd_ref_beta_deg.getValue();
    	var alpha_deg = p_pfd.nd_ref_alpha_deg.getValue();



	#var adi_att_selection = getprop("/fdm/jsbsim/systems/adi/attitude-select");
	var adi_att_selection =  p_pfd.nd_ref_adi_att_sel.getValue();

	var adi_att_string = "LVLH";

	#var adi_rate_selection = getprop("/fdm/jsbsim/systems/adi/rate-range-select");
	#var adi_error_selection = getprop("/fdm/jsbsim/systems/adi/error-range-select");

	var adi_rate_selection = p_pfd.nd_ref_adi_rate_range_sel.getValue();
    	var adi_error_selection = p_pfd.nd_ref_adi_err_sel.getValue();



	#Geo.norm function to have a positive number (though for pitch, it interfers with ADI display so far, white ball as positive attitude all the time, )
	#To do later, too much interferences with ADI drawing and colors even with roll for now ( 0 degree horizon line)

	var pitch_adi = pitch;
	var yaw_adi = yaw;
	var roll_adi = roll;


	#SCOM 2.7-7 // Closer to real logic  02/02/2021

		#Rate variables 
	var adi_rate_range = 5.0;

		#Error variables (roll, pitch, yaw) 
	var adi_error_range_r = 5.0;
	var adi_error_range_p = 5.0;
	var adi_error_range_y = 5.0;


	#Rate Logic

		#Rate outside TAEM
		if ((major_mode != 305) and (major_mode != 603))
			{
			if (adi_rate_selection == -1) {adi_rate_range = 1.0;}
			else if (adi_rate_selection == 0) {adi_rate_range = 5.0;}
			else {adi_rate_range = 10.0;}
			}
		
		#TAEM 5deg/s everywhere (Medium handled later)
		else {adi_rate_range = 5.0;}

	
			
		



	#Error (Only OPS 1,2 and 304/601 have pitch error feedbacks //305/603 have vspeed target error feedback

	if ((major_mode == 304) or (major_mode == 602) or (major_mode == 305) or (major_mode == 603)) #Entry/TAEM
		{
		
		#Common part to Entry and TAEM
		if (adi_error_selection == -1)
			{
			adi_error_range_r = 10.0;
			adi_error_range_p = 1.0;
			adi_error_range_y = 2.5;
			}
		else if (adi_error_selection == 0)
				{
				adi_error_range_r = 25.0;
				adi_error_range_p = 2.0;
				adi_error_range_y = 2.5;
				}
		else 
			{
			adi_error_range_r = 25.0;
			adi_error_range_p = 5.0;
			adi_error_range_y = 2.5;
			}

		}

	else  #OPS 1 / 601/ 301/303/302
		{
		if (adi_error_selection == -1)
			{
			adi_error_range_r = 1.0;
			adi_error_range_p = 1.0;
			adi_error_range_y = 1.0;
			}
		else if (adi_error_selection == 0)
				{
				adi_error_range_r = 5.0;
				adi_error_range_p = 5.0;
				adi_error_range_y = 5.0;
				}
		else 
			{
			adi_error_range_r = 10.0;
			adi_error_range_p = 10.0;
			adi_error_range_y = 10.0;
			}	
		}
	

		
		
	if (adi_att_selection == 1)   #INRTL
		{
		if ((major_mode == 304) or (major_mode == 305))
			{
			adi_att_string = "LVLH";
			}
		else
			{
			#pitch_adi = getprop("/fdm/jsbsim/systems/pointing/inertial/attitude/pitch-deg");
			#yaw_adi = getprop("/fdm/jsbsim/systems/pointing/inertial/attitude/yaw-deg");
			#roll_adi = -getprop("/fdm/jsbsim/systems/pointing/inertial/attitude/roll-deg");

    			pitch_adi = p_pfd.nd_ref_pitch_inrtl.getValue();
    			yaw_adi = p_pfd.nd_ref_yaw_inrtl.getValue();
    			roll_adi = -p_pfd.nd_ref_roll_inrtl.getValue();

			adi_att_string = "INRTL";
			}
		}
	else if (adi_att_selection == -1)   #REF
		{
		adi_att_string = "Ref";
		if ((major_mode == 201) or (major_mode == 202))
			{
			#var sid_ang = getprop("/fdm/jsbsim/systems/pointing/sidereal/sidereal-angle-rad") * 180.0/math.pi;
			#pitch_adi = getprop("/fdm/jsbsim/systems/pointing/inertial/attitude/pitch-deg");
			#yaw_adi = getprop("/fdm/jsbsim/systems/pointing/inertial/attitude/yaw-deg") + sid_ang - 260.0;
			#roll_adi = -getprop("/fdm/jsbsim/systems/pointing/inertial/attitude/roll-deg");


   			var sid_ang = p_pfd.nd_ref_sid_ang_rad.getValue() * 180.0/math.pi;
    			pitch_adi = p_pfd.nd_ref_pitch_inrtl.getValue();
    			yaw_adi = p_pfd.nd_ref_yaw_inrtl.getValue()  + sid_ang - 260.0;
			roll_adi =  -p_pfd.nd_ref_roll_inrtl.getValue();
			yaw_adi = geo.normdeg(yaw_adi);   #Back to original value ( mistake)
			}
		}
	else    #LVLH in Orbit ( != from entry where it displays course)
		{
		if ((major_mode == 102) or (major_mode == 103) or (major_mode == 104) or (major_mode == 105) or (major_mode == 201) or (major_mode == 202) or (major_mode == 301) or (major_mode == 302) or (major_mode == 303))
			{
			yaw_adi = yaw - course;
			if (yaw_adi < 0.0) {yaw_adi = yaw_adi + 360.0;}
			}
		}

	#var launch_stage = getprop("/fdm/jsbsim/systems/ap/launch/stage");
	#var altitude = getprop("/position/altitude-ft");

    	var launch_stage = p_pfd.nd_ref_launch_stage.getValue();
		var altitude = p_pfd.nd_ref_altitude.getValue();
		var altitude_agl = p_pfd.nd_ref_altitude_agl.getValue();

		


	var pitch_error = 0.0;
	var yaw_error = 0.0;
	var roll_error = 0.0;
	
	var Delta_inc = 0.0;
	var hsi_course = - yaw;
	var cdi_limit = 10.0;
	var cdi_displacement = 0.0;
	var course_arrow = 0.0;
	var glideslope_needle_offset = 0.0;
	var acceleration = 0.0;

	var bearing_earthrel = 0.0;
	var bearing_inertial = 0.0;
	var bearing_HAC_C = 0.0;
	var bearing_HAC_H = 0.0;
	var bearing_rwy = 0.0;

	var hac_c_distance = 0.0;
	var rwy_distance = 0;

	var v_acc_needle_offset = 0.0;

	var delta_az = 0;
	var Daz_label_text = "ΔAZ";

	
	var dap_text = "CSS";
	var dap_label_text = "DAP:";
	var att_label_text = "ATT:";
	var SB_label_text = "";
	var pitch_label_text = "";
	var throt_text = "";
	var RY_label_text = "";
	var landing_site_text = "";
	var throt_label_text = "";
	var acc_label_text = "Accel";
	var beta_Sign_text = "";


	#Items not visible most of the time (Boxes for Manual flight mainly and Flags)

		# CSS boxes

	p_pfd.rect_dap.setVisible(0);
	p_pfd.rect_throt.setVisible(0);
	p_pfd.rect_att.setVisible(0);

		#Flags

	p_pfd.brgflag.setVisible(0);
	p_pfd.brgflag_text.setVisible(0);

	p_pfd.cdiflag.setVisible(0);
	p_pfd.cdiflag_text.setVisible(0);

	p_pfd.gsflag.setVisible(0);
	p_pfd.gsflag_text.setVisible(0);



    
	if (major_mode == 101)
		{

		throt_label_text = "Throt:";
		throt_text = "Auto";
		dap_text = "Auto";

		p_pfd.keas_tape.setVisible(0);   
		p_pfd.keas_display_text.setVisible(0);

		p_pfd.alpha_tape.setVisible(0); 
		p_pfd.alpha_display_text.setVisible(0);     

		p_pfd.H_tape.setVisible(0);   
		p_pfd.H_display_text.setVisible(0);   

		p_pfd.Hdot_tape.setVisible(0);   
		p_pfd.Hdot_display_text.setVisible(0);

		p_pfd.beta.setVisible(0);
		p_pfd.label_beta.setVisible(0);
		p_pfd.beta_Sign.setVisible(0);
		p_pfd.acc_label.setVisible(0);
		p_pfd.acc_needle.setVisible(0);
		p_pfd.acc_display_box.setVisible(0);
		p_pfd.acc_display_text.setVisible(0);
		p_pfd.acc_arc.setVisible(0);
		p_pfd.acc_labels.setVisible(0);

		
		p_pfd.bearing_HAC_H.setVisible(0);
		p_pfd.bearing_HAC_C.setVisible(0);
		p_pfd.bearing_rwy.setVisible(0);
		p_pfd.bearing_rwy_tail.setVisible(0);
		p_pfd.glideslope.setVisible(0);
		p_pfd.Daz.setVisible(0);
		p_pfd.vert_acc.setVisible(0);
		p_pfd.dist_to_HAC_C.setVisible(0);
		p_pfd.bearing_earth_relative.setVisible(0);
		p_pfd.bearing_earth_relative_tail.setVisible(0);
		p_pfd.bearing_inertial.setVisible(1);
		p_pfd.dInc.setVisible(0);
		p_pfd.xtrk.setVisible(0);
		p_pfd.dist_to_rwy.setVisible(0);


		p_pfd.plot_keas_tape.setColor(1,0,0);
		p_pfd.plot_alpha_tape.setColor(1,0,0);
		p_pfd.plot_H_tape.setColor(1,0,0);
		p_pfd.plot_Hdot_tape.setColor(1,0,0);

		
		p_pfd.keas_display_box.setColor(1,0,0);
		#p_pfd.keas_display_box.setColorFill(0,0,0.15);
		p_pfd.alpha_display_box.setColor(1,0,0);
		#p_pfd.alpha_display_box.setColorFill(0,0,0.15);
		p_pfd.H_display_box.setColor(1,0,0);
		#p_pfd.H_display_box.setColorFill(0,0,0.15);
		p_pfd.Hdot_display_box.setColor(1,0,0);
		#p_pfd.Hdot_display_box.setColorFill(0,0,0.15);
		p_pfd.rect1.setColor(1,0,0);
		p_pfd.rect2.setVisible(0);
	    p_pfd.keas.setVisible(0);


		}
		

	if ((major_mode == 102) or (major_mode == 103))
		{
		
		p_pfd.bearing_HAC_H.setVisible(0);
		p_pfd.bearing_HAC_C.setVisible(0);
		p_pfd.bearing_rwy.setVisible(0);
		p_pfd.bearing_rwy_tail.setVisible(0);
		p_pfd.bearing_earth_relative_tail.setVisible(0);
		p_pfd.glideslope.setVisible(0);
		p_pfd.Daz.setVisible(0);
		p_pfd.vert_acc.setVisible(0);
		p_pfd.dist_to_HAC_C.setVisible(0);
		p_pfd.cdi_needle.setVisible(1);
		p_pfd.cdi_dots.setVisible(1);
		p_pfd.course_arrow.setVisible(1);
		p_pfd.bearing_inertial.setVisible(1);
		if (altitude < 200000.0)
			{
			p_pfd.bearing_earth_relative.setVisible(1);
			p_pfd.beta.setVisible(1);
			p_pfd.beta_Sign.setVisible(1);
		    p_pfd.label_beta.setVisible(1);
			p_pfd.rect2.setVisible(1);
			}
		else
			{
			p_pfd.bearing_earth_relative.setVisible(0);   # No Beta above 200 kfeet
			p_pfd.beta.setVisible(0);
			p_pfd.label_beta.setVisible(0);
			p_pfd.beta_Sign.setVisible(0);
			p_pfd.rect2.setVisible(0);
			}
		p_pfd.dInc.setVisible(1);
		p_pfd.xtrk.setVisible(1);
		p_pfd.dist_to_rwy.setVisible(0);

        
		p_pfd.keas_tape.setVisible(1);   
		p_pfd.keas_display_text.setVisible(1);

		p_pfd.alpha_tape.setVisible(1); 
		p_pfd.alpha_display_text.setVisible(1);     

		p_pfd.H_tape.setVisible(1);   
		p_pfd.H_display_text.setVisible(1);   

		p_pfd.Hdot_tape.setVisible(1);   
		p_pfd.Hdot_display_text.setVisible(1);

		
		p_pfd.acc_label.setVisible(1); 
		p_pfd.acc_needle.setVisible(1);	
		p_pfd.acc_display_box.setVisible(1);
		p_pfd.acc_display_text.setVisible(1);
		p_pfd.acc_arc.setVisible(1);
		p_pfd.acc_labels.setVisible(1);
		
		
		
		p_pfd.plot_keas_tape.setColor(1,1,1);
		p_pfd.plot_alpha_tape.setColor(1,1,1);
		p_pfd.plot_H_tape.setColor(1,1,1);
		p_pfd.plot_Hdot_tape.setColor(1,1,1);

		p_pfd.keas_display_box.setColor(0.7,0.7,0.78);    
		#p_pfd.keas_display_box.setColorFill(0,0,0.15);
		p_pfd.alpha_display_box.setColor(0.7,0.7,0.78);
		#p_pfd.alpha_display_box.setColorFill(0,0,0.15);
		p_pfd.H_display_box.setColor(0.7,0.7,0.78);
		#p_pfd.H_display_box.setColorFill(0,0,0.15);
		p_pfd.Hdot_display_box.setColor(0.7,0.7,0.78);
		#p_pfd.Hdot_display_box.setColorFill(0,0,0.15);
		p_pfd.rect1.setColor(1,1,1);   #Light Grey (?)
     	p_pfd.keas.setVisible(1);


		throt_label_text = "Throt:";
		
		
		#acceleration = getprop("/fdm/jsbsim/accelerations/a-pilot-ft_sec2") * 0.03108095;
		acceleration = p_pfd.nd_ref_acceleration.getValue() * 0.03108095;



		#Pushbutton linked to Sb and not directly to throttle property (done in cockpit.xml) // Yellow Box when in manual

		

		if (p_pfd.nd_ref_auto_throttle.getValue() == 1)
			{
			throt_text = "Auto";
			p_pfd.rect_throt.setVisible(0);
			}
		else	
			{
			throt_text = "Man";	
			p_pfd.rect_throt.setVisible(1);
			}



		#Trials and errors to have either both Pitch and Roll in AUTO or CSS //  Yellow box in CSS
			

    		#var auto_pitch = p_pfd.nd_ref_auto_pitch.getValue();
    		#var auto_roll_yaw = p_pfd.nd_ref_auto_roll.getValue();
			#var auto_pitch_ctr = getprop("/fdm/jsbsim/systems/ap/automati-pitch-control");
			#var auto_roll_ctr = getprop("/fdm/jsbsim/systems/ap/automati-roll-control");

			#if (auto_pitch_ctr == 0) {setprop("/fdm/jsbsim/systems/ap/automati-roll-control", 0);} else {setprop("/fdm/jsbsim/systems/ap/automati-roll-control", 1);}
	   		#if (auto_roll_ctr == 0) {setprop("/fdm/jsbsim/systems/ap/automati-pitch-control", 0);} else {set (auto_pitch_ctr == 1);}
	
			#if (auto_pitch == 1) {(auto_roll_yaw == 1);}
			#if (auto_pitch == 0) {(auto_roll_yaw == 0);}


		
		var auto_pitch = getprop("/fdm/jsbsim/systems/ap/launch/autolaunch-pitch-channel");
		var auto_roll_yaw = getprop("/fdm/jsbsim/systems/ap/launch/autolaunch-roll-yaw-channel");

		if ((auto_pitch == 1) and (auto_roll_yaw == 1))
			{
			dap_text = "Auto";
			p_pfd.rect_dap.setVisible(0);
			}
		else {p_pfd.rect_dap.setVisible(1);}
			 	



				

		if ((launch_stage > 0) and (launch_stage < 5) and (altitude_agl > 500.0)) # we have launch guidance # Agl altitude in case we launch from high elevation fields
		{

    		var tgt_inc = p_pfd.nd_ref_tgt_inc.getValue();
    		var current_inc = p_pfd.nd_ref_current_inc.getValue();


		var groundtrack_course_deg = p_pfd.nd_ref_groundtrack_course_deg.getValue();

		var inertial_course_deg = yaw + beta_deg;

		bearing_earthrel = groundtrack_course_deg - yaw;
		bearing_inertial = inertial_course_deg - yaw;

		Delta_inc = tgt_inc - current_inc;

		hsi_course = Delta_inc;

		p_pfd.xtrk_display_text.setText(sprintf("%2.1f", p_pfd.nd_ref_xtrk.getValue() - SpaceShuttle.xtrack_refloc.correction ));
		#p_pfd.xtrk_display_text.setText(sprintf("%2.1f", p_pfd.nd_ref_xtrk.getValue() ));

		#We have to flip pitch error sign once rthu is done
		var rthu_factor = 1;
		if ((math.abs(roll) < 90) and (launch_stage > 2)) {rthu_factor = -1;} #RTHU done
		
		if (launch_stage == 1)
			{
			roll_error = -math.asin(getprop("/fdm/jsbsim/systems/ap/launch/stage1-course-error")) * 180.0/math.pi;
			}

		else if ((launch_stage > 1) and (launch_stage < 5) and (abort_mode != 2))
			{
			pitch_error = rthu_factor * getprop("/fdm/jsbsim/systems/ap/launch/stage"~launch_stage~"-pitch-error");
			yaw_error = getprop("/fdm/jsbsim/systems/ap/launch/stage"~launch_stage~"-yaw-error");
			roll_error = getprop("/fdm/jsbsim/systems/ap/launch/stage"~launch_stage~"-roll-error");
			}
		else  #TAL launch stage errors
			{
			if (launch_stage == 3)
					{
					pitch_error = rthu_factor * getprop("/fdm/jsbsim/systems/ap/launch/stage3-TAL-pitch-error");
					yaw_error = getprop("/fdm/jsbsim/systems/ap/launch/stage3-TAL-yaw-error");
					roll_error = getprop("/fdm/jsbsim/systems/ap/launch/stage3-TAL-roll-error");
					}
			else if (launch_stage == 4)
					{
					pitch_error = rthu_factor * getprop("/fdm/jsbsim/systems/ap/launch/stage4-TAL-pitch-error");
					yaw_error = getprop("/fdm/jsbsim/systems/ap/launch/stage4-TAL-yaw-error");
					roll_error = getprop("/fdm/jsbsim/systems/ap/launch/stage4-TAL-roll-error");
					}
			}
		}
	

		if (altitude_agl < 500.0) #zero motion of HSI and alpha tape before liftoff
			{
			hsi_course = 0.0;
			alpha_deg = 0.0;
			}


		

		if (abort_mode == 3)
			{
			mm_appendix = "ATO";
			}

		else if (abort_mode == 2)
		    {
			mm_appendix = "T";


			#TAL differences for MM 103 Blanked CDI/ RW range DAz DXtrk

		    p_pfd.cdi_dots.setVisible(0);
			p_pfd.dInc.setVisible(0);
			p_pfd.Daz.setVisible(1);
			p_pfd.bearing_rwy.setVisible(1);
			p_pfd.dist_to_rwy.setVisible(1);

			

			
			var shuttle_pos = geo.aircraft_position();

			delta_az = shuttle_pos.course_to (SpaceShuttle.landing_site) - yaw;
			bearing_rwy = shuttle_pos.course_to (SpaceShuttle.landing_site) - yaw;
			rwy_distance = shuttle_pos.distance_to (SpaceShuttle.landing_site) / 1853.0;
			

			if (SpaceShuttle.landing_site.rwy_sel == 0)
				{landing_site_text = SpaceShuttle.landing_site.rwy_pri;}
			else	
				{landing_site_text = SpaceShuttle.landing_site.rwy_sec;}
		    }


		}

	if ((major_mode == 104) or (major_mode == 105) or (major_mode == 106) or (major_mode == 201) or (major_mode == 202) or (major_mode == 301) or (major_mode == 302) or (major_mode == 303))
		{
		p_pfd.bearing_inertial.setVisible(0);
		p_pfd.bearing_earth_relative.setVisible(0);
		p_pfd.bearing_earth_relative_tail.setVisible(0);
		p_pfd.bearing_rwy.setVisible(0);
		p_pfd.dInc.setVisible(0);
		p_pfd.xtrk.setVisible(0);
		p_pfd.dist_to_rwy.setVisible(0);
		p_pfd.glideslope.setVisible(0);
		p_pfd.Daz.setVisible(0);
		p_pfd.vert_acc.setVisible(0);
		p_pfd.dist_to_HAC_C.setVisible(0);
		

		p_pfd.alpha_tape.setVisible(0);
		p_pfd.alpha_display_text.setVisible(0);
		p_pfd.alpha_display_box.setVisible(0);
		p_pfd.plot_alpha_tape.setVisible(0);
		p_pfd.acc_label.setVisible(0);
		p_pfd.acc_needle.setVisible(0);
		p_pfd.acc_display_box.setVisible(0);
		p_pfd.acc_display_text.setVisible(0);
		p_pfd.acc_arc.setVisible(0);
		p_pfd.acc_labels.setVisible(0);

		p_pfd.label_alpha.setVisible(0);
		p_pfd.label_beta.setVisible(0);	
		p_pfd.beta_Sign.setVisible(0);
		p_pfd.rect2.setVisible(0);
		p_pfd.bearing_rwy.setVisible(0);
		p_pfd.dist_to_rwy.setVisible(0);


		#CDI/BRG flag for MM 104 only 

		p_pfd.cdiflag.setVisible(1);
		p_pfd.cdiflag_text.setVisible(1);
		p_pfd.cdi_needle.setVisible(1);	
		p_pfd.cdi_dots.setVisible(1);
		p_pfd.course_arrow.setVisible(1);	

		p_pfd.brgflag.setVisible(1);
		p_pfd.brgflag_text.setVisible(1);



		


		#Normally, everything is removed post mm 104 except Attitude/needles// kept Some informations for better On Orbit management

		if ((major_mode == 105) or (major_mode == 106) or (major_mode == 201) or (major_mode == 202) or (major_mode == 301) or (major_mode == 302) or (major_mode == 303))
			{
			p_pfd.rect1.setVisible(0);
			p_pfd.keas.setVisible(0);
			p_pfd.label_keas.setVisible(0);
			p_pfd.HSI_dynamic_group.setVisible(0);
		    p_pfd.HSI_static_group.setVisible(0);
			p_pfd.cdiflag.setVisible(0);
			p_pfd.cdiflag_text.setVisible(0);
			p_pfd.brgflag.setVisible(0);
			p_pfd.brgflag_text.setVisible(0);
			p_pfd.cdi_needle.setVisible(0);	
			p_pfd.cdi_dots.setVisible(0);
			p_pfd.course_arrow.setVisible(0);
			}	


		if (p_pfd.nd_ref_orbital_dap_auto.getValue() == 1)
			{dap_text = "Auto";}
		else
			{dap_text = "INRTL";}
	

		#var up_mnvr_flag = getprop("/fdm/jsbsim/systems/ap/up-mnvr-flag");
    		var up_mnvr_flag = p_pfd.nd_ref_up_mnvr_flag.getValue();

		#if ((up_mnvr_flag > 0) or (getprop("/fdm/jsbsim/systems/ap/oms-mnvr-flag") > 0))
		if ((up_mnvr_flag > 0) or (p_pfd.nd_ref_oms_mnvr_flag.getValue() > 0))

			{
			yaw_error = -getprop("/fdm/jsbsim/systems/ap/track/yaw-error-deg");
			pitch_error = getprop("/fdm/jsbsim/systems/ap/track/pitch-error-deg");

			
			if (up_mnvr_flag < 3)
				{roll_error = -getprop("/fdm/jsbsim/systems/ap/track/roll-error-deg");}
			else
				{roll_error = 0.0;}
			}
		}
	

	if ((major_mode == 304) or (major_mode == 305))
		{
		p_pfd.bearing_inertial.setVisible(0);
		p_pfd.bearing_earth_relative.setVisible(0);
		p_pfd.bearing_earth_relative_tail.setVisible(0);
		p_pfd.bearing_rwy.setVisible(0);
		p_pfd.bearing_rwy_tail.setVisible(0);
		p_pfd.dInc.setVisible(0);
		p_pfd.xtrk.setVisible(0);
		p_pfd.dist_to_rwy.setVisible(1);
		p_pfd.Daz.setVisible(1);
		p_pfd.vert_acc.setVisible(1);
		p_pfd.dist_to_HAC_C.setVisible(0);
		p_pfd.cdi_needle.setVisible(1);
		p_pfd.cdi_dots.setVisible(1);
		p_pfd.course_arrow.setVisible(1);

		p_pfd.alpha_tape.setVisible(1);
		p_pfd.alpha_display_text.setVisible(1);
		p_pfd.alpha_display_box.setVisible(1);
		p_pfd.plot_alpha_tape.setVisible(1);

		p_pfd.label_alpha.setVisible(1);
		p_pfd.label_beta.setVisible(1);	
		p_pfd.rect2.setVisible(1);

		p_pfd.rect1.setVisible(1);
		p_pfd.keas.setVisible(1);
		p_pfd.label_keas.setVisible(1);

		p_pfd.HSI_dynamic_group.setVisible(1);
		p_pfd.HSI_static_group.setVisible(1);

		p_pfd.acc_label.setVisible(1);
		p_pfd.acc_needle.setVisible(1);
		p_pfd.acc_display_box.setVisible(1);
		p_pfd.acc_display_text.setVisible(1);
		p_pfd.acc_arc.setVisible(1);
		p_pfd.acc_labels.setVisible(1);

		p_pfd.beta.setVisible(0);
		p_pfd.beta_Sign.setVisible(0);
		p_pfd.label_beta.setVisible(0);
		p_pfd.rect2.setVisible(0);



		#BRG and CDI flags if no pointers fed by relevant datas ( either entry guidance or taem guidance active)// Mostly Relevant for Entry or TAEM scenario which do not transit via prior MM ( No need for OPS 6 as guidance automatically selected to rtls site)

		var entry_guidance_mode = getprop("/fdm/jsbsim/systems/entry_guidance/guidance-mode"); 
		
		if ((entry_guidance_mode > 0) or (SpaceShuttle.TAEM_guidance_available == 1))
			{
			p_pfd.brgflag.setVisible(0);
			p_pfd.brgflag_text.setVisible(0);
			p_pfd.cdiflag.setVisible(0);
			p_pfd.cdiflag_text.setVisible(0);
			}
		else
			{
			p_pfd.brgflag.setVisible(1);
			p_pfd.brgflag_text.setVisible(1);
			p_pfd.cdiflag.setVisible(1);
			p_pfd.cdiflag_text.setVisible(1);	
			}

		#Runway identificator for rwy distance in both 304 and 305

		if (SpaceShuttle.landing_site.rwy_sel == 0)
			{landing_site_text = SpaceShuttle.landing_site.rwy_pri;}
		else	
			{landing_site_text = SpaceShuttle.landing_site.rwy_sec;}
			

		


		#if (getprop("/fdm/jsbsim/systems/ap/automatic-sb-control") == 1)

		#Yellow Boxes for manual mode above Mach 1 and display reorganisation ( Pitch R/Y and SB)

		dap_label_text = "";
        att_label_text = "";

		SB_label_text = "SB:";
		var mach = getprop("/fdm/jsbsim/velocities/mach");


		if (p_pfd.nd_ref_auto_sb.getValue() == 1)
			{
			adi_att_string = "Auto";
			p_pfd.rect_att.setVisible(0);
			}
		else	
			{
			adi_att_string = "Man";
			p_pfd.rect_att.setVisible(1);
			}
		


        throt_label_text = "";
		RY_label_text = "R/Y:";

        if (p_pfd.nd_ref_auto_roll.getValue() == 1)
			{
			throt_text = "Auto";
			p_pfd.rect_throt.setVisible(0);
			}
		else	
			{
			throt_text = "CSS";
			if (mach > 1) {p_pfd.rect_throt.setVisible(1);}
			else {p_pfd.rect_dap.setVisible(0);}
			}


        pitch_label_text = "Pitch:";  

	    if (p_pfd.nd_ref_auto_pitch.getValue() == 1)
			{
			dap_text = "Auto";
			p_pfd.rect_dap.setVisible(0);
			}
		else
			{
			dap_text = "CSS";
			if (mach > 1) {p_pfd.rect_dap.setVisible(1);}
			else {p_pfd.rect_dap.setVisible(0);}
			}
			
			
		acc_label_text = "NZ";

		if (abort_mode == 2) {mm_appendix = "T";}

		acceleration = p_pfd.nd_ref_Nz.getValue();






		if (major_mode == 304) # Entry HSI Logic Hac Wp1 bearing and Rwy distance only
			{
			p_pfd.vert_acc_needle.setVisible(1);
			p_pfd.glideslope.setVisible(0);
			p_pfd.glideslope_needle.setVisible(0);
			v_acc_needle_offset = -SpaceShuttle.clamp(getprop("/fdm/jsbsim/accelerations/hdotdot-ft_s2"),-10.0, 10.0) * 5.5;
			roll_error = roll - getprop("/fdm/jsbsim/systems/ap/entry/bank-angle-target-deg");
			pitch_error = getprop("/fdm/jsbsim/systems/ap/alpha-error") * 180.0/math.pi;
			delta_az = getprop("/fdm/jsbsim/systems/entry_guidance/delta-azimuth-deg");

			#Blinking Daz in roll reversal (Red/Black)

			var roll_reversal = getprop("/fdm/jsbsim/systems/ap/entry/roll-reversal-init");

			if (roll_reversal == 1)
				{
				if (p_pfd.blink_daz == 0)
					{
					p_pfd.Daz_display_box.setColor(0,0,0.15);
					p_pfd.blink_daz = 1;
					}
				else 
					{
					p_pfd.Daz_display_box.setColor(1,0,0);
					p_pfd.blink_daz = 0;
					}
					
				}
			else {p_pfd.Daz_display_box.setColor(1,1,1);}



			if (entry_guidance_mode > 0)
				{
				rwy_distance = p_pfd.nd_ref_rem_dist.getValue();
				}

			}
		else
			{
			p_pfd.vert_acc_needle.setVisible(0);
			p_pfd.vert_acc.setVisible(0);
			p_pfd.glideslope.setVisible(1);
			p_pfd.glideslope_needle.setVisible(1);

			}

		if (SpaceShuttle.TAEM_guidance_available == 1) # TAEM HSI Logic Hac C and H bearing, Hac C and rwy distance
			{
			p_pfd.bearing_HAC_H.setVisible(1);
			p_pfd.bearing_HAC_C.setVisible(1);
			p_pfd.dist_to_HAC_C.setVisible(1);

			#Avoid blank box if Roll reversal at TAEM transition
			p_pfd.Daz_display_box.setColor(1,1,1);


			#CDI scale labels visible for TAEM(10°, 10°)
			p_pfd.cdi_scale_l.setVisible(1);
			p_pfd.cdi_scale_r.setVisible(1);

			#Roll/Pitch error for error needles during TAEM

				# Roll Error based on TAEM bank target
				roll_error = roll - getprop("/fdm/jsbsim/systems/ap/taem/bank-target");

				#Pitch error based on TAEM vspeed error (test) High 200fts // Medium 80 fts // Low 40 fts

				var vspeed_error = -getprop("/fdm/jsbsim/systems/ap/taem/vspeed-error");
				pitch_error = vspeed_error * 5;
		
	
			#var hsi_source = getprop("/fdm/jsbsim/systems/adi/hsi-source-select");
			var hsi_source = p_pfd.nd_ref_hsi_source.getValue();
			
			var pos = {};

			if (hsi_source == 0) # NAV
				{
				pos = SpaceShuttle.state_vector_position();
				}
			else if (hsi_source == 1) # TACAN
				{
				pos = geo.aircraft_position();
				}
			else # MLS
				{
				pos = geo.aircraft_position();
				}

			
			var dist = pos.distance_to(SpaceShuttle.TAEM_WP_1) / 1853.0;
			hac_c_distance = pos.distance_to(SpaceShuttle.TAEM_HAC_center) / 1853.0;
			var course_WP1 = pos.course_to (SpaceShuttle.TAEM_WP_1);
			var course_HAC_C = pos.course_to (SpaceShuttle.TAEM_HAC_center);
			var course_threshold = 	pos.course_to(SpaceShuttle.TAEM_threshold);	
			var runway_distance_nm = getprop("/fdm/jsbsim/systems/taem-guidance/distance-to-runway-nm");
			

			if (hsi_source == 1) # query individual receiver filter
				{
				var hsi_unit = getprop("/fdm/jsbsim/systems/adi/hsi-unit-select");

				dist = SpaceShuttle.tacan_system.receiver[hsi_unit-1].indicated_range(dist);
				hac_c_distance = SpaceShuttle.tacan_system.receiver[hsi_unit-1].indicated_range(hac_c_distance);
				course_WP1 = SpaceShuttle.tacan_system.receiver[hsi_unit-1].indicated_azimuth(course_WP1);
				course_HAC_C = SpaceShuttle.tacan_system.receiver[hsi_unit-1].indicated_azimuth(course_HAC_C);
				course_threshold = SpaceShuttle.tacan_system.receiver[hsi_unit-1].indicated_azimuth(course_threshold);
				}

			hsi_course = -yaw;
			bearing_HAC_C = course_HAC_C;
			bearing_HAC_H = course_WP1;
			course_arrow = SpaceShuttle.TAEM_threshold.heading;

			var auto_pitch = getprop("/fdm/jsbsim/systems/ap/automatic-pitch-control");
			var auto_roll_yaw = getprop("/fdm/jsbsim/systems/ap/automatic-roll-control");
			#if ((auto_pitch == 1) and (auto_roll_yaw == 1)) {dap_text = "Auto";}

			cdi_displacement =  course_threshold - SpaceShuttle.TAEM_threshold.heading;



			var glideslope_deviation = getprop("/fdm/jsbsim/systems/taem-guidance/glideslope-deviation-ft");

			glideslope_needle_offset = SpaceShuttle.clamp(glideslope_deviation, -5000, 5000)/5000.0 * 68.0;

			#GS needle blink logic if above limits ( only the GS needle/ not medium adi rate)
			
			if ((glideslope_deviation < -4999) or (glideslope_deviation > 4999))
				{
				if (p_pfd.blink_gs == 0)
					{
					p_pfd.glideslope_needle.setVisible(0);
					p_pfd.blink_gs = 1;
					}
				else 
					{
					p_pfd.glideslope_needle.setVisible(1);
					p_pfd.blink_gs = 0;
					}
					
				}
			else {p_pfd.glideslope_needle.setVisible(1);}


			delta_az = course_WP1 - yaw;    #Delta Az relative to WP 1
			rwy_distance = runway_distance_nm;

			#Hac turn init then HTA ( HAC turn angle) // init at HAC intercept // normdeg to have a positive HTA and not a bearing/azimuth +/- 
			#It works OK now, almost all case covered 16/06/2020
		
			#Nasal global variable from taem_guidance.nas doest not work all the time (SpaceShuttle.TAEM_guidance_phase)
			var hac_init = getprop("/fdm/jsbsim/systems/ap/taem/hac-turn-init");
			var al_init = getprop("/fdm/jsbsim/systems/ap/taem/al-init");
					

			if (hac_init == 1)
				{

				var HTA_init = getprop("/fdm/jsbsim/systems/ap/taem/hta-init");
				var HTA = geo.normdeg( SpaceShuttle.TAEM_threshold.heading - yaw);
				var approach_mode = getprop("/fdm/jsbsim/systems/taem-guidance/approach-mode-string");


				if (approach_mode == "OVHD")
					{
					if ((HTA > 180.0) and (HTA_init < 2))   #conditionnal with HTA init to avoid changing HTA init sign when turning into the HAC with HTA going from > 180 to < 180 and switching delta az from HTA to (360 - HTA)
						{
						setprop("/fdm/jsbsim/systems/ap/taem/hta-init", 1);
						}
					else if ((HTA < 180.0) and (HTA_init != 1))
						{
						setprop("/fdm/jsbsim/systems/ap/taem/hta-init", 2);
						}
					}

				else if (approach_mode == "STRT")
					{
					if ((HTA < 180.0) and (HTA_init < 2)) 
						{  
						setprop("/fdm/jsbsim/systems/ap/taem/hta-init", 1);
						}
					else if ((HTA > 180.0) and (HTA_init != 1))
						{
						setprop("/fdm/jsbsim/systems/ap/taem/hta-init", 2);
						}
					}
					
				


				Daz_label_text = "HTA";

				if (HTA_init == 1) {delta_az = HTA;}
				else if (HTA_init == 2) {delta_az = -HTA + 360;}


				}


			if (al_init == 1)   #Approach HSI Logic, Runway bearing and Rwy distance only
				{
				p_pfd.bearing_rwy.setVisible(1);
		   	 	p_pfd.bearing_rwy_tail.setVisible(1);
				p_pfd.Daz.setVisible(0);	
		   		p_pfd.bearing_HAC_H.setVisible(0);
				p_pfd.bearing_HAC_C.setVisible(0);
				p_pfd.dist_to_HAC_C.setVisible(0);
				bearing_rwy = course_threshold;

				#Glideslope scale 1000 feet

				glideslope_needle_offset = SpaceShuttle.clamp(glideslope_deviation, -1000, 1000)/1000.0 * 68.0;
				p_pfd.glideslope_label_upper.setText("1K");
				p_pfd.glideslope_label_lower.setText("1K");

				#GS needle blink logic if above limits 
				if ((glideslope_deviation < -999) or (glideslope_deviation > 999))
					{
					if (p_pfd.blink_gs == 0)
						{
						p_pfd.glideslope_needle.setVisible(0);
						p_pfd.blink_gs = 1;
						}
					else 
						{
						p_pfd.glideslope_needle.setVisible(1);
						p_pfd.blink_gs = 0;
						}
						
					}
				else {p_pfd.glideslope_needle.setVisible(1);}

				#Null error for error needles once on final 

				roll_error = 0;
				pitch_error = 0;


				#GS flag below 1500 AGL (RA)

				if (altitude_agl < 1500.0) 
					{
					p_pfd.gsflag.setVisible(1);
					p_pfd.gsflag_text.setVisible(1);
					p_pfd.glideslope_needle.setVisible(0);
					}

				#CDI 1.25° per dot in A/L
				cdi_limit = 2.5;
				p_pfd.cdi_scale_l.setText("2.5");
				p_pfd.cdi_scale_r.setText("2.5");
						
				}

			#CDI displacement clamp at the end to take into account the A/L condition
			cdi_displacement = SpaceShuttle.clamp(cdi_displacement, -cdi_limit, cdi_limit);

			}
		else       #MM 304 Entry HSI logic
			{
			p_pfd.bearing_HAC_H.setVisible(1);
			bearing_HAC_H = getprop("/fdm/jsbsim/systems/entry_guidance/target-azimuth-deg");
			p_pfd.bearing_HAC_C.setVisible(0);
			}
		}


	if ((major_mode == 601) or (major_mode == 602) or (major_mode == 603))
		{

		p_pfd.bearing_inertial.setVisible(0);
		p_pfd.dInc.setVisible(0);
		p_pfd.xtrk.setVisible(0);
		p_pfd.dist_to_rwy.setVisible(1);
		p_pfd.Daz.setVisible(1);
		p_pfd.alpha_tape.setVisible(1);	
		




		throt_text = "Man";

		mm_appendix = "R";




		if (SpaceShuttle.landing_site.rwy_sel == 0)
			{landing_site_text = SpaceShuttle.landing_site.rwy_pri;}
		else	
			{landing_site_text = SpaceShuttle.landing_site.rwy_sec;}




		if (major_mode == 601) # PRTLS
			{
			
			var flyout_active = getprop("/fdm/jsbsim/systems/ap/rtls/flyout-active");

			#Error Needles
			roll_error = getprop("/fdm/jsbsim/systems/ap/rtls/roll-error");
			pitch_error = getprop("/fdm/jsbsim/systems/ap/rtls/pitch-error");;

			p_pfd.vert_acc.setVisible(0);
			p_pfd.bearing_earth_relative.setVisible(1);
			p_pfd.bearing_earth_relative_tail.setVisible(1);
			p_pfd.dist_to_HAC_C.setVisible(0);
			p_pfd.cdi_needle.setVisible(0);	
			p_pfd.cdi_dots.setVisible(0);
			p_pfd.glideslope.setVisible(0);
			p_pfd.course_arrow.setVisible(0);
			p_pfd.bearing_HAC_C.setVisible(0);
			p_pfd.beta.setVisible(1);       #Beta always visible during OPS 601
		    p_pfd.label_beta.setVisible(1);
			p_pfd.beta_Sign.setVisible(1);
			p_pfd.rect2.setVisible(1);
			
			if (flyout_active == 1)   
				{
				p_pfd.bearing_rwy.setVisible(1);
				p_pfd.bearing_rwy_tail.setVisible(1);
				p_pfd.bearing_HAC_H.setVisible(0);	
				}
			else
				{
				p_pfd.bearing_rwy.setVisible(0);
				p_pfd.bearing_rwy_tail.setVisible(0);
				p_pfd.bearing_HAC_H.setVisible(1);	
				}	



			acc_label_text = "Accel";
			throt_label_text = "Throt:";

			#acceleration = getprop("/fdm/jsbsim/accelerations/a-pilot-ft_sec2") * 0.03108095;
			acceleration = p_pfd.nd_ref_acceleration.getValue() * 0.03108095;



			#Like 102/103 Pushbutton linked to SB and not throttle directly// need to link SB and Throttle for real manual throttling when pushbutton depressed
			#Done in cockpit.xml
			#Pushbutton linked to Sb and not directly to throttle property // Yellow Box when in manual

			if (p_pfd.nd_ref_auto_throttle.getValue() == 1)
				{
				throt_text = "Auto";
				p_pfd.rect_throt.setVisible(0);
				}
			else	
				{
				throt_text = "Man";		
				p_pfd.rect_throt.setVisible(1);
				}



			#DAP AUTO/CSS and Yellow Boxes if manual

			var auto_pitch = getprop("/fdm/jsbsim/systems/ap/automatic-pitch-control");
			var auto_roll_yaw = getprop("/fdm/jsbsim/systems/ap/automatic-roll-control");

			if ((auto_pitch == 1) and (auto_roll_yaw == 1))
				{
				dap_text = "Auto";
				p_pfd.rect_dap.setVisible(0);
				}
			else {p_pfd.rect_dap.setVisible(1);}




			var groundtrack_course_deg = getprop("/fdm/jsbsim/systems/entry_guidance/groundtrack-course-deg");
			bearing_earthrel = groundtrack_course_deg;
			#rwy_distance = getprop("/fdm/jsbsim/systems/entry_guidance/remaining-distance-nm");
			rwy_distance = p_pfd.nd_ref_rem_dist.getValue();
			
			
			bearing_HAC_H = getprop("/fdm/jsbsim/systems/entry_guidance/target-azimuth-deg");
			bearing_rwy = bearing_HAC_H;
			delta_az = getprop("/fdm/jsbsim/systems/entry_guidance/delta-azimuth-deg");

			}
		else	# GRTLS Entry HSI Logic mm 602( aka 304)
			{
			
			#CA appendix for contigency abort in 602/603
			if (abort_mode > 4) {mm_appendix = "CA";}

			#Nz hold magenta line on acceleration device
			if (getprop("/fdm/jsbsim/systems/ap/grtls/Nz-hold-active") == 1) {p_pfd.acc_nz_marker.setVisible(1);}
			else {p_pfd.acc_nz_marker.setVisible(0);}
			

			p_pfd.bearing_earth_relative.setVisible(0);
			p_pfd.bearing_earth_relative_tail.setVisible(0);
			p_pfd.bearing_rwy.setVisible(0);
			p_pfd.bearing_rwy_tail.setVisible(0);
			p_pfd.bearing_HAC_H.setVisible(1);
			p_pfd.beta.setVisible(0);
		    p_pfd.label_beta.setVisible(0);
			p_pfd.beta_Sign.setVisible(0);
			p_pfd.rect2.setVisible(0);
			p_pfd.course_arrow.setVisible(1);

			acc_label_text = "NZ";
			acceleration = getprop("/fdm/jsbsim/accelerations/Nz");
			throt_label_text = "";
			dap_label_text = "";
        	att_label_text = "";
			SB_label_text = "SB:";
			pitch_label_text = "Pitch:";
			RY_label_text = "R/Y:";

			var mach = getprop("/fdm/jsbsim/velocities/mach");


			if (p_pfd.nd_ref_auto_sb.getValue() == 1)
				{
				adi_att_string = "Auto";
				p_pfd.rect_att.setVisible(0);
				}
			else	
				{
				adi_att_string = "Man";
				p_pfd.rect_att.setVisible(1);
				}
		

     		if (p_pfd.nd_ref_auto_roll.getValue() == 1)
				{
				throt_text = "Auto";
				p_pfd.rect_throt.setVisible(0);
				}
			else	
				{
				throt_text = "CSS";
				if (mach > 1) {p_pfd.rect_throt.setVisible(1);}
				else {p_pfd.rect_dap.setVisible(0);}
				}


	    	if (p_pfd.nd_ref_auto_pitch.getValue() == 1)
				{
				dap_text = "Auto";
				p_pfd.rect_dap.setVisible(0);
				}
			else
				{
				dap_text = "CSS";
				if (mach > 1) {p_pfd.rect_dap.setVisible(1);}
				else {p_pfd.rect_dap.setVisible(0);}
				}


			if (getprop("/fdm/jsbsim/systems/ap/grtls/taem-transition-init") == 0) # before TAEM
				{
				p_pfd.dist_to_HAC_C.setVisible(0);
				p_pfd.cdi_needle.setVisible(1);
				p_pfd.cdi_dots.setVisible(1);
				p_pfd.glideslope.setVisible(0);	
				p_pfd.course_arrow.setVisible(0);
				p_pfd.vert_acc.setVisible(1);

				#Error Needles for Alpha transition/Nz hold/ Alpha redovery
				roll_error = roll - getprop("/fdm/jsbsim/systems/ap/grtls/roll-tgt-deg");
				pitch_error = getprop("/fdm/jsbsim/systems/ap/grtls/pitch-error");
				

				v_acc_needle_offset = -SpaceShuttle.clamp(getprop("/fdm/jsbsim/accelerations/hdotdot-ft_s2"),-10.0, 10.0) * 5.5;
				#rwy_distance = getprop("/fdm/jsbsim/systems/entry_guidance/remaining-distance-nm");
				rwy_distance = p_pfd.nd_ref_rem_dist.getValue();
				bearing_HAC_H = getprop("/fdm/jsbsim/systems/entry_guidance/target-azimuth-deg");
				delta_az = getprop("/fdm/jsbsim/systems/entry_guidance/delta-azimuth-deg");
				}
			else # with TAEM guidance TAEM HSI Logic mm 603 (aka 305)
				{

				#CDI scale visible for TAEM
				p_pfd.cdi_scale_l.setVisible(1);
				p_pfd.cdi_scale_r.setVisible(1);

				#Roll/Pitch error for error needles during TAEM

				# Roll Error based on TAEM bank target
				roll_error = roll - getprop("/fdm/jsbsim/systems/ap/taem/bank-target");

				#Pitch error based on TAEM vspeed error (test) High 200fts // Medium 80 fts // Low 40 fts

				var vspeed_error = -getprop("/fdm/jsbsim/systems/ap/taem/vspeed-error");
				pitch_error = vspeed_error * 5;

				p_pfd.dist_to_HAC_C.setVisible(1);
				p_pfd.bearing_rwy.setVisible(0);
				p_pfd.bearing_rwy_tail.setVisible(0);
				p_pfd.bearing_HAC_H.setVisible(1);
				p_pfd.bearing_HAC_C.setVisible(1);
				p_pfd.cdi_needle.setVisible(1);	
				p_pfd.cdi_dots.setVisible(1);
				p_pfd.glideslope.setVisible(1);
				p_pfd.course_arrow.setVisible(1);
				p_pfd.vert_acc.setVisible(0);

				var hsi_source = getprop("/fdm/jsbsim/systems/adi/hsi-source-select");
				var pos = {};

				if (hsi_source == 0) # NAV
					{
					pos = SpaceShuttle.state_vector_position();
					}
				else if (hsi_source == 1) # TACAN
					{
					pos = geo.aircraft_position();
					}
				else # MLS
					{
					pos = geo.aircraft_position();
					}

				var dist = pos.distance_to(SpaceShuttle.TAEM_WP_1) / 1853.0;
				hac_c_distance = pos.distance_to(SpaceShuttle.TAEM_HAC_center) / 1853.;
				var course_WP1 = pos.course_to (SpaceShuttle.TAEM_WP_1);
				var course_HAC_C = pos.course_to (SpaceShuttle.TAEM_HAC_center);
				var course_threshold = 	pos.course_to(SpaceShuttle.TAEM_threshold);

				if (hsi_source == 1) # query individual receiver filter
					{
					var hsi_unit = getprop("/fdm/jsbsim/systems/adi/hsi-unit-select");

					dist = SpaceShuttle.tacan_system.receiver[hsi_unit-1].indicated_range(dist);
					hac_c_distance = SpaceShuttle.tacan_system.receiver[hsi_unit-1].indicated_range(hac_c_distance);
					course_WP1 = SpaceShuttle.tacan_system.receiver[hsi_unit-1].indicated_azimuth(course_WP1);
					course_HAC_C = SpaceShuttle.tacan_system.receiver[hsi_unit-1].indicated_azimuth(course_HAC_C);
					course_threshold = SpaceShuttle.tacan_system.receiver[hsi_unit-1].indicated_azimuth(course_threshold);
					}	

				#CDI logic (mm305)

				cdi_displacement =  course_threshold - SpaceShuttle.TAEM_threshold.heading;

				
				#GS 5000 feet scale

				var glideslope_deviation = getprop("/fdm/jsbsim/systems/taem-guidance/glideslope-deviation-ft");

				glideslope_needle_offset = SpaceShuttle.clamp(glideslope_deviation, -5000, 5000)/5000.0 * 68.0;

				#GS needle blink logic if above limits ( only the GS needle/ not medium adi rate)
			
				if ((glideslope_deviation < -4999) or (glideslope_deviation > 4999))
					{
					if (p_pfd.blink_gs == 0)
						{
						p_pfd.glideslope_needle.setVisible(0);
						p_pfd.blink_gs = 1;
						}
					else 
						{
						p_pfd.glideslope_needle.setVisible(1);
						p_pfd.blink_gs = 0;
						}
						
					}
				else {p_pfd.glideslope_needle.setVisible(1);}



				bearing_HAC_C = course_HAC_C;
				bearing_HAC_H = course_WP1;
				course_arrow = SpaceShuttle.TAEM_threshold.heading;
				rwy_distance = getprop("/fdm/jsbsim/systems/taem-guidance/distance-to-runway-nm");
				delta_az = course_WP1 - yaw;


				#Hac turn init then HTA ( same than OPS3 )

				var hac_init = getprop("/fdm/jsbsim/systems/ap/taem/hac-turn-init");
				var al_init = getprop("/fdm/jsbsim/systems/ap/taem/al-init");

				if (hac_init == 1)
				{

				var HTA_init = getprop("/fdm/jsbsim/systems/ap/taem/hta-init");
				var HTA = geo.normdeg( SpaceShuttle.TAEM_threshold.heading - yaw);
				var approach_mode = getprop("/fdm/jsbsim/systems/taem-guidance/approach-mode-string");


				if (approach_mode == "OVHD")
					{
					if ((HTA > 180.0) and (HTA_init < 2))   
						{
						setprop("/fdm/jsbsim/systems/ap/taem/hta-init", 1);
						}
					else if ((HTA < 180.0) and (HTA_init != 1))
						{
						setprop("/fdm/jsbsim/systems/ap/taem/hta-init", 2);
						}
					}

				else if (approach_mode == "STRT")
					{
					if ((HTA < 180.0) and (HTA_init < 2)) 
						{  
						setprop("/fdm/jsbsim/systems/ap/taem/hta-init", 1);
						}
					else if ((HTA > 180.0) and (HTA_init != 1))
						{
						setprop("/fdm/jsbsim/systems/ap/taem/hta-init", 2);
						}
					}
					
				


				Daz_label_text = "HTA";

				if (HTA_init == 1) {delta_az = HTA;}
				else if (HTA_init == 2) {delta_az = -HTA + 360;}


				}


				if (al_init == 1)   #Approach HSI Logic
					{
					p_pfd.bearing_rwy.setVisible(1);
		   	 		p_pfd.bearing_rwy_tail.setVisible(1);
					p_pfd.Daz.setVisible(0);
		   			p_pfd.bearing_HAC_H.setVisible(0);
					p_pfd.bearing_HAC_C.setVisible(0);
					p_pfd.dist_to_HAC_C.setVisible(0);
					bearing_rwy = course_threshold;

					#GS 1000 feet scale

					glideslope_needle_offset = SpaceShuttle.clamp(glideslope_deviation, -1000, 1000)/1000.0 * 68.0;
					p_pfd.glideslope_label_upper.setText("1K");
					p_pfd.glideslope_label_lower.setText("1K");

					#GS needle blink logic if above limits ( only the GS needle/ not medium adi rate)
			
					if ((glideslope_deviation < -999) or (glideslope_deviation > 999))
						{
						if (p_pfd.blink_gs == 0)
							{
							p_pfd.glideslope_needle.setVisible(0);
							p_pfd.blink_gs = 1;
							}
						else 
							{
							p_pfd.glideslope_needle.setVisible(1);
							p_pfd.blink_gs = 0;
							}
							
						}
					else {p_pfd.glideslope_needle.setVisible(1);}

					#Null error for error needles once on final 

					roll_error = 0;
					pitch_error = 0;

					#GS flag below 1500 AGL

					if (altitude_agl < 1500.0) 
						{
						p_pfd.gsflag.setVisible(1);
						p_pfd.gsflag_text.setVisible(1);
						p_pfd.glideslope_needle.setVisible(0);
						}

					#CDI A/L 1.25°/dot
					cdi_limit = 2.5;
					p_pfd.cdi_scale_l.setText("2.5");
					p_pfd.cdi_scale_r.setText("2.5");
					}

				}
			
			cdi_displacement = SpaceShuttle.clamp(cdi_displacement, -cdi_limit, cdi_limit);

			}


		}


	# ADI sphere animation ##############################################

	# clear previous step

	p_pfd.adi_inner.removeAllChildren();

	# draw

	# projection vecs for labels
	var p_vecs = SpaceShuttle.projection_vecs(-pitch_adi, yaw_adi, -roll_adi);

	# ADI sphere
	var data = SpaceShuttle.draw_circle(0.75*95, 30);
	update_plot_data (p_pfd.adi_sphere_bg, data);
	#pfd_segment_draw(data,adi_sphere_bg);
	

	data = SpaceShuttle.draw_adi_bg(pitch_adi, yaw_adi, roll_adi);
	#pfd_segment_draw(data,adi_sphere_bg_bright);
	update_plot_data (p_pfd.adi_sphere_bg_bright, data);

	if (getprop("/fdm/jsbsim/systems/adi/quality-level") > 0)
		{
		#draw_adi_sphere(adi_sphere, p_vecs);
		update_adi_sphere(p_pfd.adi_sphere, p_vecs);
		p_pfd.adi_sphere.setVisible(1);
		}
	else
		{
		p_pfd.adi_sphere.setVisible(0);
		}


	draw_sphere_labels(p_pfd.adi_inner, p_vecs, pitch_adi, yaw_adi, roll_adi);
	
	# ADI error needles



	var pitch_error_ntrans = SpaceShuttle.clamp(pitch_error, -adi_error_range_p, adi_error_range_p) * -40.0/adi_error_range_p;
	var yaw_error_ntrans = SpaceShuttle.clamp(yaw_error, -adi_error_range_y, adi_error_range_y) * -40.0/adi_error_range_y;
	var roll_error_ntrans = SpaceShuttle.clamp(roll_error, -adi_error_range_r, adi_error_range_r) * -40.0/adi_error_range_r;


	p_pfd.att_error_pitch.setTranslation(0.0, pitch_error_ntrans);
	p_pfd.att_error_yaw.setTranslation(yaw_error_ntrans, 0.0);
	p_pfd.att_error_roll.setTranslation(roll_error_ntrans,0.0);
	
	p_pfd.att_error_pitch.setScale(math.sqrt(9025. - pitch_error_ntrans*pitch_error_ntrans)/95.0,1.0);
	p_pfd.att_error_yaw.setScale(1.0,math.sqrt(9025. - yaw_error_ntrans*yaw_error_ntrans)/95.0);
	p_pfd.att_error_roll.setScale(1.0,math.sqrt(9025. - roll_error_ntrans*roll_error_ntrans)/95.0);
	

	#Placeholder for TAEM pitch error label (g's error instead of pitch error // in FG vspeed error drives the ap guidance)

	if ((major_mode == 305) or (major_mode == 603)) #TAEM
		{
		if (adi_error_selection == -1) # 0.5 g's in Low
			{
			p_pfd.adi_error_label_p_u.updateText("0.5g");
			p_pfd.adi_error_label_p_l.updateText("0.5g");
			}
		else # 1.2 g's in Medium and High
			{
			p_pfd.adi_error_label_p_u.updateText("1.2g");
			p_pfd.adi_error_label_p_l.updateText("1.2g");
			}
		}
	else #Error in degrees everywhere else
		{
		p_pfd.adi_error_label_p_u.updateText(sprintf("%d", adi_error_range_p));
		p_pfd.adi_error_label_p_l.updateText(sprintf("%d", adi_error_range_p));
		}


	# ADI rate needles

	
	if (((major_mode == 305) or (major_mode == 603)) and (altitude_agl > 7000) and (adi_rate_selection == 0) and (SpaceShuttle.TAEM_guidance_available == 1)) #TAEM Medium logic above 7kfeet qfe
		{
		
		#Variables common to all the conditionnals

		#GS
		var glideslope_deviation = getprop("/fdm/jsbsim/systems/taem-guidance/glideslope-deviation-ft");
		var yfrac = glideslope_deviation / 5000;

		

		#Before Hac
		if ((hac_init == 0) and (al_init == 0))
			{
			

			### Roll Rate ###
			#HAC time on horizontal ladder (starting 10 seconds before HAC)

			var gs_kts = getprop("/velocities/groundspeed-kt");
			var wp_1_distance = pos.distance_to(SpaceShuttle.TAEM_WP_1) / 1853.0;
			var wp_1_time = ((wp_1_distance - 1.5) / gs_kts) * 3600; #Turn 1.5 Nm before real Hac (taem_guidance.nas /anticipation)
			
			var tfrac = (10 - wp_1_time);
			tfrac = SpaceShuttle.clamp(tfrac, 0, 10);

			#No zero in the middle of the scale
			p_pfd.rate_label_r_c.setVisible(0);

			if (SpaceShuttle.TAEM_WP_1.turn_direction == "left") #Needle from right to left		
				{
				p_pfd.rate_label_r_l.updateText("0");
				p_pfd.rate_label_r_r.updateText("10s");
				p_pfd.rate_label_r_r.setTranslation(330,78);
				p_pfd.adi_roll_rate_needle.setTranslation(320 - tfrac * 13.0, 70);
				}
			else #Needle from left to right		
				{
				p_pfd.rate_label_r_l.updateText("10s");
				p_pfd.rate_label_r_l.setTranslation(180,78);
				p_pfd.rate_label_r_r.updateText("0");
				p_pfd.adi_roll_rate_needle.setTranslation(190 + tfrac * 13.0, 70);
				}


			### Yaw Rate ###
			#It displays delta azimuth +/-5°

			var course_WP1 = pos.course_to (SpaceShuttle.TAEM_WP_1);
			var delta_az = course_WP1 - yaw;    #Delta Az relative to WP 1
			delta_az = SpaceShuttle.clamp(delta_az, -5, 5);

			p_pfd.rate_label_y_l.updateText("5");
			p_pfd.rate_label_y_r.updateText("5");

			p_pfd.adi_yaw_rate_needle.setTranslation(255 + 13.0 * delta_az, 280.0);


			### Pitch Rate ###
			#It displays GS scale 5kfeet / fly to

			p_pfd.rate_label_p_u.updateText("5K");
			p_pfd.rate_label_p_l.updateText("5K");
			yfrac = SpaceShuttle.clamp(yfrac, -1, 1);
			p_pfd.adi_pitch_rate_needle.setTranslation(360, 175 - 65.0 * yfrac);
			}

		#In the HAC
		else if (hac_init == 1)
			{
			### Roll Rate ###
			#Blanked

			p_pfd.rate_label_r_l.setVisible(0);
			p_pfd.rate_label_r_c.setVisible(0);
			p_pfd.rate_label_r_r.setVisible(0);
			p_pfd.adi_roll_rate_needle.setVisible(0);


			### Yaw Rate ###
			#Deviation in the HAC based on Hac Xrange (fly to HSI like)

			var radial_error_feet = getprop("/fdm/jsbsim/systems/taem-guidance/radial-error-nm") * 6076.12;
			var xfrac = radial_error_feet / 5000;

			p_pfd.rate_label_y_l.updateText("5K");
			p_pfd.rate_label_y_r.updateText("5K");
			xfrac = SpaceShuttle.clamp(xfrac, -1, 1);
			p_pfd.adi_yaw_rate_needle.setTranslation(255 + 65.0 * xfrac, 280.0);

			### Pitch Rate ###
			#It displays GS scale 5kfeet / fly to

			p_pfd.rate_label_p_u.updateText("5K");
			p_pfd.rate_label_p_l.updateText("5K");
			yfrac = SpaceShuttle.clamp(yfrac, -1, 1);
			p_pfd.adi_pitch_rate_needle.setTranslation(360, 175 - 65.0 * yfrac);
			}


		#In A/L above 7000 feet

		else if (al_init == 1)
			{
			### Roll Rate ###
			#Blanked

			p_pfd.rate_label_r_l.setVisible(0);
			p_pfd.rate_label_r_c.setVisible(0);
			p_pfd.rate_label_r_r.setVisible(0);
			p_pfd.adi_roll_rate_needle.setVisible(0);


			### Yaw Rate ###

			#LOC / Fly to HSI like 
			var course_threshold = 	pos.course_to(SpaceShuttle.TAEM_threshold); 
			var cdi_dispacement_rad = (course_threshold - SpaceShuttle.TAEM_threshold.heading) * 0.0175; 
			var runway_distance_feet = pos.distance_to(SpaceShuttle.TAEM_threshold) * 3.28;
			var cross_range_feet = math.tan(cdi_dispacement_rad) * runway_distance_feet;
			

			p_pfd.rate_label_y_l.updateText("2.5K");
			p_pfd.rate_label_y_l.setTranslation(179,280);

			p_pfd.rate_label_y_r.updateText("2.5K");
			p_pfd.rate_label_y_r.setTranslation(331, 280);

			xfrac = cross_range_feet / 2500;
			xfrac = SpaceShuttle.clamp(xfrac, -1, 1);

			p_pfd.adi_yaw_rate_needle.setTranslation(255 + 65.0 * xfrac, 280.0);

			### Pitch Rate ###

			#It displays GS scale 5kfeet / fly to

			p_pfd.rate_label_p_u.updateText("1K");
			p_pfd.rate_label_p_l.updateText("1K");

			yfrac = glideslope_deviation / 1000;
			yfrac = SpaceShuttle.clamp(yfrac, -1, 1);

			p_pfd.adi_pitch_rate_needle.setTranslation(360, 175 - 65.0 * yfrac);
			}

		}

	else #OPS1/3/mm 601/602 and TAEM Low/High settings and Medium below 7 kfeet
		{
			
		#Re-enable Roll rate which might be blanked from medium setting
		p_pfd.rate_label_r_l.setVisible(1);
		p_pfd.rate_label_r_c.setVisible(1);
		p_pfd.rate_label_r_r.setVisible(1);
		p_pfd.adi_roll_rate_needle.setVisible(1);

		#Re-enable Correct Translation for some of rate labels moved from their initial position for medium rate
		p_pfd.rate_label_r_l.setTranslation(184,78);
		p_pfd.rate_label_y_l.setTranslation(184,280);
		p_pfd.rate_label_y_r.setTranslation(326, 280);
		p_pfd.rate_label_r_r.setTranslation(326,78);

		p_pfd.rate_label_r_l.updateText(sprintf("%d", adi_rate_range));
		p_pfd.rate_label_r_r.updateText(sprintf("%d", adi_rate_range));
		p_pfd.rate_label_y_l.updateText(sprintf("%d", adi_rate_range));
		p_pfd.rate_label_y_r.updateText(sprintf("%d", adi_rate_range));
		p_pfd.rate_label_p_u.updateText(sprintf("%d", adi_rate_range));
		p_pfd.rate_label_p_l.updateText(sprintf("%d", adi_rate_range));

		var s_adi_rate_range = sprintf("%d", adi_rate_range);


		#var roll_rate = getprop("/fdm/jsbsim/velocities/p-rad_sec") * 57.2957;
		var roll_rate = p_pfd.nd_ref_p_rad_s.getValue() * 57.2957;
		roll_rate = SpaceShuttle.clamp(roll_rate, -adi_rate_range, adi_rate_range);
		p_pfd.adi_roll_rate_needle.setTranslation(255 + 13.0 * roll_rate * 5.0/adi_rate_range, 70);

		#var pitch_rate = getprop("/fdm/jsbsim/velocities/q-rad_sec") * 57.2957;
		var pitch_rate = p_pfd.nd_ref_q_rad_s.getValue() * 57.2957 ;
		pitch_rate = SpaceShuttle.clamp(pitch_rate, -adi_rate_range, adi_rate_range);
		p_pfd.adi_pitch_rate_needle.setTranslation(360, 175 - 13.0 * pitch_rate * 5.0/adi_rate_range);

		#var yaw_rate = getprop("/fdm/jsbsim/velocities/r-rad_sec") * 57.2957;
		var yaw_rate =  p_pfd.nd_ref_r_rad_s.getValue() * 57.2957;
		yaw_rate = SpaceShuttle.clamp(yaw_rate, -adi_rate_range, adi_rate_range);
		p_pfd.adi_yaw_rate_needle.setTranslation(255 + 13.0 * yaw_rate * 5.0/adi_rate_range, 280.0);
		}


	# HSI

	p_pfd.HSI_dynamic_group.setRotation(hsi_course * math.pi/180.0);

	p_pfd.bearing_earth_relative.setRotation(bearing_earthrel * math.pi/180.0);
	p_pfd.bearing_earth_relative_tail.setRotation((bearing_earthrel + 180.0) * math.pi/180.0);
	p_pfd.bearing_inertial.setRotation(bearing_inertial * math.pi/180.0);

	p_pfd.bearing_HAC_C.setRotation(bearing_HAC_C * math.pi/180.0);
	p_pfd.bearing_HAC_H.setRotation(bearing_HAC_H * math.pi/180.0);
	p_pfd.bearing_rwy.setRotation(bearing_rwy * math.pi/180.0);
	p_pfd.bearing_rwy_tail.setRotation((bearing_rwy + 180.0) * math.pi/180.0);


	p_pfd.course_arrow.setRotation(course_arrow *  math.pi/180.0);
	p_pfd.cdi.setRotation(course_arrow * math.pi/180.0);
    
	p_pfd.cdi_needle.setTranslation(cdi_displacement/cdi_limit * 40.0, 0);

	# KEAS /Mach tape


	var mach = p_pfd.nd_ref_mach.getValue();
	var mach_label = "M/VR";
	var eas = p_pfd.nd_ref_eas.getValue();
	var keas_label_text = "KEAS";
	var vtrue = p_pfd.nd_ref_vrel.getValue();

	if ((major_mode == 103) or (major_mode == 104) or (major_mode == 105) or (major_mode == 106))
		{
		mach = p_pfd.nd_ref_veci.getValue() / 1000.0;
		mach_label = "M/VI";
		}
	else if ((major_mode == 201) or (major_mode == 202))
		{
		mach = p_pfd.nd_ref_veci.getValue() / 1000.0;
		mach_label = "M/VI";
		}
	else if ((major_mode == 301) or (major_mode == 302) or (major_mode == 303))
		{
		mach = p_pfd.nd_ref_veci.getValue() / 1000.0;
		mach_label = "M/VI";
		}
	else if ((major_mode == 601) and (flyout_active == 1))
		{
		mach = p_pfd.nd_ref_veci.getValue() / 1000.0;
		mach_label = "M/VI";
		}
	else if ((major_mode == 304) or ((major_mode == 601) and (flyout_active == 0)))
		{
		mach = p_pfd.nd_ref_vrel.getValue() / 1000.0;
		mach_label = "M/VR";
		}
	else if (((major_mode == 305) or (major_mode == 603)) and (mach <= 0.9))
	    {
		mach = p_pfd.nd_ref_eas.getValue();
		mach_label = "KEAS";
		}

	var air_data_select = p_pfd.nd_ref_air_data.getValue();

	var air_data_good = 1;

	if ((air_data_select == 1) or (air_data_select == -1))
		{
		air_data_good = 0;
		}

	if (air_data_good != p_pfd.air_data_stored)
		{
		p_pfd.air_data_stored = air_data_good;
		if (air_data_good == 0)
			{
			adi_invalid_air_data (p_pfd);
			}
		else
			{
			adi_valid_air_data (p_pfd);
			}
		}


    #Below Mach 0.9, switch over between tape and rectangle ( tape from mach to keas and rectangle from keas to M/VR) // new var for mach as previous one is fed by eas now
	#To Do : proper tape with keas in back ground and not point mach.

	var mach_bis = getprop("/velocities/mach");  # var mach previously defined is fed by eas in those conditions

	if (((major_mode == 305) or (major_mode == 603)) and (mach_bis <= 0.9))
		{
		keas_label_text = "M/VR";
		p_pfd.keas.updateText(sprintf("%1.2f",mach_bis));
		p_pfd.keas_tape.setTranslation (40, 185 - 5400 + 381.0 * vtrue / 900.8);   
		p_pfd.keas_display_text.setTextFast(sprintf("%3.0f",eas));    
		}
	else
	    {
		p_pfd.keas.updateText(sprintf("%3.0f",eas));
		p_pfd.keas_tape.setTranslation (40, 185 - 5400 + 381.0 * mach);   
		p_pfd.keas_display_text.setTextFast(sprintf("%2.1f",mach));    
		}	

	p_pfd.label_mvi.updateText(mach_label);
	p_pfd.label_keas.updateText(keas_label_text);


	# alpha tape
	

	p_pfd.alpha_display_text.setTextFast(sprintf("%2.1f",alpha_deg));
	p_pfd.alpha_tape.setTranslation (92.5, 185 + 9.5 * alpha_deg);

	#alpha L/D (ENTRY/TAEM Mach below 3.0 only)

	var alpha_max_LD = getprop("/fdm/jsbsim/systems/entry_guidance/taem-max-LD");

	if (((major_mode == 304) or (major_mode == 305) or (major_mode == 602) or (major_mode == 603)) and (mach_bis <= 3.0))
		{
		p_pfd.alpha_tape_max_LD.setVisible(1);
		p_pfd.alpha_tape_max_LD.setTranslation(17, -alpha_max_LD * 9.5)
		}
	

	#Green Alpha stripe for Min/Max alpha (304/305 and RTLS 602/603 only// not for contigency)

	#var abort_mode = getprop("/fdm/jsbsim/systems/abort/abort-mode");
	var alpha_max = getprop("/fdm/jsbsim/systems/entry_guidance/aoa-max");
	var alpha_min = getprop("/fdm/jsbsim/systems/entry_guidance/aoa-min");
	var delta_alpha = alpha_max - alpha_min;

	if (((major_mode == 304) or (major_mode == 305) or (major_mode == 602) or (major_mode == 603)) and (abort_mode < 5))
		{
		p_pfd.alpha_tape_green_stripe.setVisible(1);
		#Center of rectangle drawing in the middle for translation
		p_pfd.alpha_tape_green_stripe.setTranslation(18, -((delta_alpha / 2) + alpha_min) * 9.5);

		#Scale only the Y axis around the center depending of the length of the alpha stripe desired / full length scale (1,1) 190 px == 20 ° alpha
		p_pfd.alpha_tape_green_stripe.setScale(1, delta_alpha / 20)
		}

	# H tape

	if (altitude > 400000.0)
		{
		var H_miles = altitude / 6076.1154;
		var tape_offset = (H_miles - 70.0) * 10.0;
		if (tape_offset<0.0) {tape_offset = 0.0;}
		p_pfd.H_display_text.setTextFast(sprintf("%3.1f",H_miles)~"M");
		p_pfd.H_tape.setTranslation (417, 185 + tape_offset);

		p_pfd.H_tape.labels_upper_2k.setVisible(0);
		p_pfd.H_tape.labels_lower_2k.setVisible(0);
		p_pfd.H_tape.labels_upper_30k.setVisible(0);
		p_pfd.H_tape.labels_lower_30k.setVisible(0);
		p_pfd.H_tape.labels_upper_100k.setVisible(0);
		p_pfd.H_tape.labels_lower_100k.setVisible(0);
		p_pfd.H_tape.labels_upper_400k.setVisible(0);
		p_pfd.H_tape.labels_lower_400k.setVisible(0);
		p_pfd.H_tape.labels_upper_miles.setVisible(1);
		p_pfd.H_tape.labels_lower_miles.setVisible(1);
		}
	else if (altitude > 100000.0) #Altitude Baro above 100 kfeet (Outside Initial Launch and TAEM)
		{
		var tape_offset = (altitude - 100000.0)/50000.0 * 50.0;
		if (tape_offset<0.0) {tape_offset = 0.0;}
		p_pfd.H_display_text.setTextFast(sprintf("%3.0f",altitude/1000)~"K");
		p_pfd.H_tape.setTranslation (417, 185 + tape_offset);

		p_pfd.H_tape.labels_upper_2k.setVisible(0);
		p_pfd.H_tape.labels_lower_2k.setVisible(0);
		p_pfd.H_tape.labels_upper_30k.setVisible(0);
		p_pfd.H_tape.labels_lower_30k.setVisible(0);
		p_pfd.H_tape.labels_upper_100k.setVisible(0);
		p_pfd.H_tape.labels_lower_100k.setVisible(0);
		p_pfd.H_tape.labels_upper_400k.setVisible(1);
		p_pfd.H_tape.labels_lower_400k.setVisible(1);
		p_pfd.H_tape.labels_upper_miles.setVisible(0);
		p_pfd.H_tape.labels_lower_miles.setVisible(0);
		}
	else if (altitude_agl > 30000.0) #Altitude Agl starting there ( and QFE for TAEM later)
		{
		var tape_offset = (altitude_agl - 30000.0)/1000.0 * 10.0;
		if (tape_offset<0.0) {tape_offset = 0.0;}
		p_pfd.H_display_text.setTextFast(sprintf("%2.0f",altitude_agl/1000)~"K");
		p_pfd.H_tape.setTranslation (417, 185 + tape_offset);

		p_pfd.H_tape.labels_upper_2k.setVisible(0);
		p_pfd.H_tape.labels_lower_2k.setVisible(0);
		p_pfd.H_tape.labels_upper_30k.setVisible(0);
		p_pfd.H_tape.labels_lower_30k.setVisible(0);
		p_pfd.H_tape.labels_upper_100k.setVisible(1);
		p_pfd.H_tape.labels_lower_100k.setVisible(1);
		p_pfd.H_tape.labels_upper_400k.setVisible(0);
		p_pfd.H_tape.labels_lower_400k.setVisible(0);
		p_pfd.H_tape.labels_upper_miles.setVisible(0);
		p_pfd.H_tape.labels_lower_miles.setVisible(0);
		}
	else if ((altitude_agl > 2000.0) and (major_mode == 102)) #above 2000 feet in OPS 1
		{
		

		var tape_offset = (altitude_agl - 2000.0)/1000.0 * 50.0;
		if (tape_offset<0.0) {tape_offset = 0.0;}

		if (altitude_agl > 10000) {p_pfd.H_display_text.setTextFast(sprintf("%2.0f",altitude_agl/1000)~"K");} #above 10000 feet ( more than 5 digit), output goes to 10 K etc
		else {p_pfd.H_display_text.setTextFast(sprintf("%4.0f",altitude_agl));}  # Below 10000 feet, output stays with 4 digit

		p_pfd.H_tape.setTranslation (417, 185 + tape_offset);
		p_pfd.H_tape_background2.setColorFill(1, 1, 1); #White background for all the other lowerladders
		p_pfd.H_tape_ladder_lower.setColor(0,0,0.15); #dark ladder tape for all the other lowerladders 


		p_pfd.H_tape.labels_upper_2k.setVisible(0);
		p_pfd.H_tape.labels_lower_2k.setVisible(0);
		p_pfd.H_tape.labels_upper_30k.setVisible(1);
		p_pfd.H_tape.labels_lower_30k.setVisible(1);
		p_pfd.H_tape.labels_upper_100k.setVisible(0);
		p_pfd.H_tape.labels_lower_100k.setVisible(0);
		p_pfd.H_tape.labels_upper_400k.setVisible(0);
		p_pfd.H_tape.labels_lower_400k.setVisible(0);
		p_pfd.H_tape.labels_upper_miles.setVisible(0);
		p_pfd.H_tape.labels_lower_miles.setVisible(0);
		}
	else if ((altitude_agl < 2000.0) and (major_mode == 102))  # Below 2000 feet in OPS 1
		{
		var tape_offset = altitude_agl/100.0 * 50.0;
		if (tape_offset<0.0) {tape_offset = 0.0;}
		p_pfd.H_display_text.setTextFast(sprintf("%4.0f",altitude_agl));
		p_pfd.H_tape.setTranslation (417, 185 + tape_offset);
		p_pfd.H_tape_background2.setColorFill(0.24, 0.24, 0.32); #Grey Background for 2klowerladder and alti below 0
		p_pfd.H_tape_ladder_lower.setColor(1, 1, 1); #White ladder tape for 2klowerladder and alti below 0

		p_pfd.H_tape.labels_upper_2k.setVisible(1);
		p_pfd.H_tape.labels_lower_2k.setVisible(1);
		p_pfd.H_tape.labels_upper_30k.setVisible(0);
		p_pfd.H_tape.labels_lower_30k.setVisible(0);
		p_pfd.H_tape.labels_upper_100k.setVisible(0);
		p_pfd.H_tape.labels_lower_100k.setVisible(0);
		p_pfd.H_tape.labels_upper_400k.setVisible(0);
		p_pfd.H_tape.labels_lower_400k.setVisible(0);
		p_pfd.H_tape.labels_upper_miles.setVisible(0);
		p_pfd.H_tape.labels_lower_miles.setVisible(0);	
		}
	
	


	# H tape management for OPS 3/6 below 30Kfeet
	
	else if (((major_mode == 305) or (major_mode == 603)) and (altitude_agl < 30000.0))  
		{

		#For TAEM // difference between agl (pure height for RA) and QFE (alti displayed in TAEM instead of QNH if runway elevation is known ie. taem guidance available)
		#Nasal global variable needs TAEM to be initiated		 
		var altitude_qfe = altitude;
		if (SpaceShuttle.TAEM_guidance_available == 1) {altitude_qfe = altitude - SpaceShuttle.TAEM_threshold.elevation;}

		var radar_alt = getprop("/fdm/jsbsim/systems/navigation/radar-alt-available"); 
		var alti_OPS3 = altitude_qfe;
		
	

		if ((radar_alt == 1) and (altitude_agl < 5000.0)) {alti_OPS3 = altitude_agl;}   # Radar Alti displayed below 5000 AGL if radar alti On
		else {alti_OPS3 = altitude_qfe;}  # Allow switching from radar alti on to off and on again 


		var tape_offset = (alti_OPS3 - 2000.0)/1000.0 * 50.0;
		if (tape_offset<0.0) {tape_offset = 0.0;}

		if (alti_OPS3 > 10000)   # More than 5 digit, output goes with 2 digit and 10K etc
			{
			p_pfd.H_display_text.setTextFast(sprintf("%2.0f",alti_OPS3/1000)~"K");
			}  
		else if ((alti_OPS3 > 5000) and (alti_OPS3 < 10000))  # 4 digit number up to 5000 feet
			{
			p_pfd.H_display_text.setTextFast(sprintf("%4.0f",alti_OPS3));
			}
		else     #below 5000 feet, if radar alti on, R displayed after 4 digit box altitude
			{
			if (radar_alt == 1){p_pfd.H_display_text.setTextFast(sprintf("%4.0f",alti_OPS3)~"R");}   #Radar
			else {p_pfd.H_display_text.setTextFast(sprintf("%4.0f",alti_OPS3));} #Baro
			}

		p_pfd.H_tape.setTranslation (417, 185 + tape_offset);
		p_pfd.H_tape_background2.setColorFill(1, 1, 0); #Yellow background for lower 30k ladder// upper 2k ladder
		p_pfd.H_tape_ladder_lower.setColor(0,0,0.15); #dark ladder tape 

		p_pfd.H_tape.labels_upper_2k.setVisible(0);
		p_pfd.H_tape.labels_lower_2k.setVisible(0);
		p_pfd.H_tape.labels_upper_30k.setVisible(1);
		p_pfd.H_tape.labels_lower_30k.setVisible(1);
		p_pfd.H_tape.labels_upper_100k.setVisible(0);
		p_pfd.H_tape.labels_lower_100k.setVisible(0);
		p_pfd.H_tape.labels_upper_400k.setVisible(0);
		p_pfd.H_tape.labels_lower_400k.setVisible(0);
		p_pfd.H_tape.labels_upper_miles.setVisible(0);
		p_pfd.H_tape.labels_lower_miles.setVisible(0);




		if (alti_OPS3 < 2000.0) # 2000 feet tape starts at 2000 AGL or Baro in OPS 3, depending of Radar alt on or off ( managed by alti_OPS3 var)
			{
			var tape_offset = alti_OPS3/100.0 * 50.0;
			if (tape_offset<0.0) {tape_offset = 0.0;}

			if (radar_alt == 1) {p_pfd.H_display_text.setTextFast(sprintf("%4.0f",alti_OPS3)~"R");}   #below 5000 feet, if radar alti on, R displayed after 4 digit box altitude
			else {p_pfd.H_display_text.setTextFast(sprintf("%4.0f",alti_OPS3));}

			
			p_pfd.H_tape.setTranslation (417, 185 + tape_offset);
			p_pfd.H_tape_background1.setColorFill(1, 1, 0); #Yellow background for upper 2k ladder
			p_pfd.H_tape_background2.setColorFill(0.24, 0.24, 0.32); #Grey Background for 2klowerladder and alti below 0
			p_pfd.H_tape_ladder_lower.setColor(1, 1, 1); #White ladder tape for 2klowerladder and alti below 0

			p_pfd.H_tape.labels_upper_2k.setVisible(1);
			p_pfd.H_tape.labels_lower_2k.setVisible(1);
			p_pfd.H_tape.labels_upper_30k.setVisible(0);
			p_pfd.H_tape.labels_lower_30k.setVisible(0);
			p_pfd.H_tape.labels_upper_100k.setVisible(0);
			p_pfd.H_tape.labels_lower_100k.setVisible(0);
			p_pfd.H_tape.labels_upper_400k.setVisible(0);
			p_pfd.H_tape.labels_lower_400k.setVisible(0);
			p_pfd.H_tape.labels_upper_miles.setVisible(0);
			p_pfd.H_tape.labels_lower_miles.setVisible(0);
			}
		}	
			
		
	# Hdot tape

	var vspeed = -getprop("/fdm/jsbsim/velocities/v-down-fps");

	var tape_offset = SpaceShuttle.clamp(vspeed, -2900.0, 2900.0) * 0.6;
	p_pfd.Hdot_tape.setTranslation (480, 185 + tape_offset);
	p_pfd.Hdot_display_text.setTextFast(sprintf("%4.0f",vspeed));

	# accelerometer needle

	var acc_needle_rot = acceleration * 45.0 * math.pi/180.0;
	var acc_needle_nz = getprop("/fdm/jsbsim/systems/ap/grtls/Nz-tgt") * 45.0 * math.pi/180.0;
	

	p_pfd.acc_needle.setRotation(acc_needle_rot);
	p_pfd.acc_nz_marker.setRotation(acc_needle_nz);

	p_pfd.acc_display_text.setTextFast(sprintf("%1.1f",acceleration)~"g");
	

	# glideslope needle

	p_pfd.glideslope_needle.setTranslation(440,373 - glideslope_needle_offset);

	# H dot dot needle

	p_pfd.vert_acc_needle.setTranslation(475, 380 - v_acc_needle_offset);

	# numerical values


		#left/right sign instead of -/+

	var beta_deg_abs = math.abs(beta_deg);

	if ((altitude < 200000.0) or (major_mode == 601))
       	{
		p_pfd.beta.updateText(sprintf("%2.1f",beta_deg_abs));

		if (beta_deg < 0) {beta_Sign_text = "L";}
		else {beta_Sign_text = "R";}
		}
			
	else 
		{
		p_pfd.beta.updateText("");
		beta_Sign_text = "";
		}



	var roll_alphanum = roll_adi;

	if (adi_att_selection == -1)
		{
		if ((major_mode == 201) or (major_mode == 202))
			{
			roll_alphanum = geo.normdeg180(roll_adi + 90.0);
			}
		}

	#Print a 0 or 00 instead of blank space for numbers less than 100

	p_pfd.r.setTextFast(sprintf("%03d", roll_alphanum));
	p_pfd.p.setTextFast(sprintf("%03d", pitch_adi));
	p_pfd.y.setTextFast(sprintf("%03d", yaw_adi));
	p_pfd.dInc_display_text.setText(sprintf("%2.2f", Delta_inc));
	#p_pfd.dist_to_rwy_display_text.setText(sprintf("%3.1f", getprop("/fdm/jsbsim/systems/taem-guidance/distance-to-runway-nm")));
	if (rwy_distance < 100.0)
		{p_pfd.dist_to_rwy_display_text.setText(sprintf("%3.1f",rwy_distance));}
	else
		{p_pfd.dist_to_rwy_display_text.setText(sprintf("%4.0f",rwy_distance));}

	p_pfd.dist_to_HAC_C_display_text.setText(sprintf("%3.1f",hac_c_distance));

	p_pfd.Daz_display_text.setText(sprintf("%3.0f", delta_az)~"°");

	# mode texts

	
	p_pfd.label_pitch.updateText(pitch_label_text);
	p_pfd.dap.updateText(dap_text);
	p_pfd.label_dap.updateText(dap_label_text);
    p_pfd.throt.updateText(throt_text);
	p_pfd.label_throt.updateText(throt_label_text);
	p_pfd.dist_to_rwy_label.updateText(landing_site_text);
	p_pfd.MM.updateText(sprintf("%d", major_mode)~mm_appendix);
	p_pfd.att.updateText(adi_att_string);
	p_pfd.label_att.updateText(att_label_text);
	p_pfd.label_SB.updateText(SB_label_text);
	p_pfd.label_RY.updateText(RY_label_text);
	p_pfd.acc_label.updateText(acc_label_text);
	p_pfd.Daz_label.updateText(Daz_label_text);
	p_pfd.beta_Sign.updateText(beta_Sign_text);
	
	
	

    };
    
    return p_pfd;
}





var PFD_addpage_p_pfd_orbit = func(device)
{
    var p_pfd_orbit = device.addPage("PFDOrbit", "p_pfd_orbit");

	
    
    #
    #
    # device page update
    p_pfd_orbit.group = device.svg.getElementById("p_pfd_orbit");
    p_pfd_orbit.group.setColor(0.88, 0.88, 0.88);


    p_pfd_orbit.r = device.svg.getElementById("p_pfd_orbit_r");
    p_pfd_orbit.p = device.svg.getElementById("p_pfd_orbit_p");
    p_pfd_orbit.y = device.svg.getElementById("p_pfd_orbit_y");

    p_pfd_orbit.label_r = device.svg.getElementById("p_pfd_orbit_label_r");
    p_pfd_orbit.label_p = device.svg.getElementById("p_pfd_orbit_label_p");
    p_pfd_orbit.label_y = device.svg.getElementById("p_pfd_orbit_label_y");

    p_pfd_orbit.menu_item = device.svg.getElementById("MI_2"); 
    p_pfd_orbit.menu_item_frame = device.svg.getElementById("MI_2_frame"); 


	#Font and Colors for Orbit PFD elements

	p_pfd_orbit.r.setFont(p_pfd_font_2);
	p_pfd_orbit.p.setFont(p_pfd_font_2);
	p_pfd_orbit.y.setFont(p_pfd_font_2);

	p_pfd_orbit.label_r.setFont(p_pfd_font_2);
	p_pfd_orbit.label_p.setFont(p_pfd_font_2);
	p_pfd_orbit.label_y.setFont(p_pfd_font_2);

	p_pfd_orbit.label_r.setColor(0.7,0.7,0.78);
    p_pfd_orbit.label_p.setColor(0.7,0.7,0.78); 
    p_pfd_orbit.label_y.setColor(0.7,0.7,0.78);



	#references to property nodes for improved performance of getter methods for Orbit PFD

	p_pfd_orbit.nd_ref_pitch = props.globals.getNode("/fdm/jsbsim/systems/navigation/state-vector/pitch-deg", 1);
    p_pfd_orbit.nd_ref_yaw = props.globals.getNode("/fdm/jsbsim/systems/navigation/state-vector/yaw-deg", 1);
    p_pfd_orbit.nd_ref_roll = props.globals.getNode("/fdm/jsbsim/systems/navigation/state-vector/roll-deg", 1);

    p_pfd_orbit.nd_ref_pitch_inrtl = props.globals.getNode("/fdm/jsbsim/systems/pointing/inertial/attitude/pitch-deg", 1);
    p_pfd_orbit.nd_ref_yaw_inrtl = props.globals.getNode("/fdm/jsbsim/systems/pointing/inertial/attitude/yaw-deg", 1);
    p_pfd_orbit.nd_ref_roll_inrtl = props.globals.getNode("/fdm/jsbsim/systems/pointing/inertial/attitude/roll-deg", 1);

	p_pfd_orbit.nd_ref_sid_ang_rad = props.globals.getNode("/fdm/jsbsim/systems/pointing/sidereal/sidereal-angle-rad", 1);

	p_pfd_orbit.nd_ref_major_mode = props.globals.getNode("/fdm/jsbsim/systems/dps/major-mode", 1);

	p_pfd_orbit.nd_ref_adi_att_sel = props.globals.getNode("/fdm/jsbsim/systems/adi/attitude-select", 1);
    p_pfd_orbit.nd_ref_adi_rate_range_sel = props.globals.getNode("/fdm/jsbsim/systems/adi/rate-range-select", 1);
    p_pfd_orbit.nd_ref_adi_err_sel = props.globals.getNode("/fdm/jsbsim/systems/adi/error-range-select", 1);

	p_pfd_orbit.nd_ref_course_deg = props.globals.getNode("/fdm/jsbsim/velocities/course-deg", 1);

    

    p_pfd_orbit.ondisplay = func
    {
        device.set_DPS_off();
        device.dps_page_flag = 0;

	# FC bus selection

	device.fc_bus_displayed = "FC"~device.fc_bus;

	if (me.layer_id == "p_pfd_orbit")
		{
        	device.MEDS_menu_title.setText("FLIGHT INSTRUMENT MENU");

		# menu items

		p_pfd_orbit.menu_item.setColor(1.0, 1.0, 1.0);
		p_pfd_orbit.menu_item_frame.setColor(1.0, 1.0, 1.0);

		}
	else 
		{
        	device.MEDS_menu_title.setText("DATA BUS SELECT MENU");
		}


	# group for dynamically re-drawn inner part



	# ADI sphere grid	

	p_pfd_orbit.adi_sphere_bg = device.ADI.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(0.88,0.88,0.88)
	.setTranslation (255, 175)
        .setColor(1,1,1);

	p_pfd_orbit.adi_sphere_bg.max_pts = 0;
	p_pfd_orbit.adi_sphere_bg.coord_nd_ref_array = [];
	p_pfd_orbit.adi_sphere_bg.cmd_nd_ref_array = [];

	p_pfd_orbit.adi_sphere_bg_bright = device.ADI.createChild("path")
        .setStrokeLineWidth(1)
	.setColorFill(0.24, 0.24, 0.32)
	.setTranslation (255, 175)
        .setColor(1,1,1);

	p_pfd_orbit.adi_sphere_bg_bright.max_pts = 0;
	p_pfd_orbit.adi_sphere_bg_bright.coord_nd_ref_array = [];
	p_pfd_orbit.adi_sphere_bg_bright.cmd_nd_ref_array = [];

	p_pfd_orbit.adi_sphere = device.ADI.createChild("path")
        .setStrokeLineWidth(1)
	.setTranslation (255, 175)
        .setColor(0.1,0.1,0.1);

	p_pfd_orbit.adi_inner = device.ADI.createChild("group");
	p_pfd_orbit.adi_inner.setTranslation(255, 175);

	p_pfd_orbit.adi_sphere.max_pts = 0;
	p_pfd_orbit.adi_sphere.coord_nd_ref_array = [];
	p_pfd_orbit.adi_sphere.cmd_nd_ref_array = [];

	# draw the fixed elements

	# ADI ################################################



	# upper compass rose

	var plot_compass_upper = device.ADI.createChild("path")
        .setStrokeLineWidth(1)
        .setColor(1,1,1);

	var data = SpaceShuttle.draw_compass_scale(71.25,12, 1.1, 6, 1.05);
	pfd_segment_draw(data, plot_compass_upper);

	data = SpaceShuttle.draw_circle(71.25, 30);
	pfd_segment_draw(data, plot_compass_upper);

	data = SpaceShuttle.draw_circle(95.0, 30);
	pfd_segment_draw(data, plot_compass_upper);

	plot_compass_upper.setTranslation (255, 175);

	place_compass_label(device.ADI, "0", 0.0, 85.0, 0,255,180);
	place_compass_label(device.ADI, "33", 30.0, 85.0, 0,255,180);
	place_compass_label(device.ADI, "30", 60.0, 85.0, 0,255,180);
	place_compass_label(device.ADI, "27", 90.0, 85.0, 0,255,180);
	place_compass_label(device.ADI, "24", 120.0, 85.0, 0,255,180);
	place_compass_label(device.ADI, "21", 150.0, 85.0, 0,255,180);
	place_compass_label(device.ADI, "18", 180.0, 85.0, 0,255,180);
	place_compass_label(device.ADI, "15", 210.0, 85.0, 0,255,180);
	place_compass_label(device.ADI, "12", 240.0, 85.0, 0,255,180);
	place_compass_label(device.ADI, "9", 270.0, 85.0, 0,255,180);
	place_compass_label(device.ADI, "6", 300.0, 85.0, 0,255,180);
	place_compass_label(device.ADI, "3", 330.0, 85.0, 0,255,180);

	# nose position indicator

	data = [[0.0, -26.0, 0], [0.0, -26.0, 1], [0.0, 26.0,1], [-28.0,0.0,0],[-23.0,0.0,1],[23.0,0.0,0],[28.0,0.0,1], [-10,0,0], [-8.6, 5.0, 1], [-5.0, 8.6, 1], [0.0,10.0,1],[5.0,8.6,1],[8.6,5.0,1],[10.0,0.0,1]];
	var plot_cross_thick = device.ADI.createChild("path", "cross_thick")
        .setStrokeLineWidth(2)
        .setColor(0.0, 1.0, 0.0);
	pfd_segment_draw(data, plot_cross_thick);
	plot_cross_thick.setTranslation (255, 175);

	data = [[-23.0, 0.0, 0], [-23.0, 0.0, 1], [23.0,0.0,1]];
	var plot_cross_thin = device.ADI.createChild("path", "cross_thin")
        .setStrokeLineWidth(1)
        .setColor(0.0, 1.0, 0.0);
	pfd_segment_draw(data, plot_cross_thin);
	plot_cross_thin.setTranslation (255, 175);


	# ADI error needles

	var adi_errors = device.ADI.createChild("group");

	var plot_error_arcs = adi_errors.createChild("path")
        .setStrokeLineWidth(1)
        .setColor(1, 0, 1);
	data = SpaceShuttle.draw_arc (92, 10, 335, 385);
	pfd_segment_draw(data, plot_error_arcs);

	data = SpaceShuttle.draw_arc (92, 10, 65, 115);
	pfd_segment_draw(data, plot_error_arcs);

	data = SpaceShuttle.draw_arc (92, 10, 155, 205);
	pfd_segment_draw(data, plot_error_arcs);

	data = SpaceShuttle.draw_comb (92, 11, 0.05, 335, 385, 1);
	pfd_segment_draw(data, plot_error_arcs);

	data = SpaceShuttle.draw_comb (92, 11, 0.05, 65, 115, 2);
	pfd_segment_draw(data, plot_error_arcs);

	data = SpaceShuttle.draw_comb (92, 11, 0.05, 155, 205, 3);
	pfd_segment_draw(data, plot_error_arcs);

	p_pfd_orbit.adi_error_label_p_u = write_small_label(device.ADI, "5", [348, 139,1], [1.0,0.0,1.0]);
	p_pfd_orbit.adi_error_label_p_l = write_small_label(device.ADI, "5", [348, 222,1], [1.0,0.0,1.0]);

	p_pfd_orbit.adi_error_label_p_u.enableUpdate();
	p_pfd_orbit.adi_error_label_p_l.enableUpdate();

	p_pfd_orbit.att_error_needles = adi_errors.createChild("group");

	p_pfd_orbit.att_error_pitch = p_pfd_orbit.att_error_needles.createChild("path")
        .setStrokeLineWidth(3)
        .setColor(1, 0, 1);

	data = [[28.0, 0.0, 0], [95.0,0.0, 1]];
	pfd_segment_draw(data, p_pfd_orbit.att_error_pitch);

	p_pfd_orbit.att_error_yaw = p_pfd_orbit.att_error_needles.createChild("path")
        .setStrokeLineWidth(3)
        .setColor(1, 0, 1);

	data = [[0.0, 28, 0], [0.0,95.0, 1]];
	pfd_segment_draw(data, p_pfd_orbit.att_error_yaw);
	
	p_pfd_orbit.att_error_roll = p_pfd_orbit.att_error_needles.createChild("path")
        .setStrokeLineWidth(3)
        .setColor(1, 0, 1);

	data = [[0.0, -28, 0], [0.0,-95.0, 1]];
	pfd_segment_draw(data, p_pfd_orbit.att_error_roll);
	

	
	 adi_errors.setTranslation (255, 175);

	# ADI rate indicators ################################################

	# ADI rate ladders

	data = SpaceShuttle.draw_ladder (130, 3, 0.07, 4, 0.04, 0, 0 , 1);
	var plot_ADI_rate_roll = device.ADI.createChild("path", "ADI_rate_roll")
        .setStrokeLineWidth(1)
        .setColor(1, 1, 1);
	pfd_segment_draw(data, plot_ADI_rate_roll);
	plot_ADI_rate_roll.setTranslation(255, 70);

	data = SpaceShuttle.draw_ladder (130, 3, 0.07, 4, 0.04, 0, 1, 1);
	var plot_ADI_rate_yaw = device.ADI.createChild("path", "ADI_rate_yaw")
        .setStrokeLineWidth(1)
        .setColor(1, 1, 1);
	pfd_segment_draw(data, plot_ADI_rate_yaw);
	plot_ADI_rate_yaw.setTranslation(255, 280);

	data = SpaceShuttle.draw_ladder (130, 3, 0.07, 4, 0.04, 1, 1, 1);
	var plot_ADI_rate_pitch = device.ADI.createChild("path", "ADI_rate_pitch")
        .setStrokeLineWidth(1)
        .setColor(1, 1, 1);
	pfd_segment_draw(data, plot_ADI_rate_pitch);
	plot_ADI_rate_pitch.setTranslation(360, 175);

	# ADI rate labels (not shown in Orbit pfd except neutral 0)

		#p_pfd_orbit.rate_label_r_l = write_small_label(device.ADI, "5", [184, 78,1], [1,1,1]);
		p_pfd_orbit.rate_label_r_c = write_small_label(device.ADI, "0", [255, 68.5,1], [1,1,1]);    # 0 in the middle of rate ladders, hidden by green moving triangle
		#p_pfd_orbit.rate_label_r_r = write_small_label(device.ADI, "5", [326, 78,1], [1,1,1]);

		#p_pfd_orbit.rate_label_y_l = write_small_label(device.ADI, "5", [184, 280,1], [1,1,1]);
		p_pfd_orbit.rate_label_y_c = write_small_label(device.ADI, "0", [255, 290.5,1], [1,1,1]);
		#p_pfd_orbit.rate_label_y_r = write_small_label(device.ADI, "5", [326, 280,1], [1,1,1]);

		#p_pfd_orbit.rate_label_p_u = write_small_label(device.ADI, "5", [355, 109,1], [1,1,1]);
		p_pfd_orbit.rate_label_p_c = write_small_label(device.ADI, "0", [368, 179,1], [1,1,1]);
		#p_pfd_orbit.rate_label_p_l = write_small_label(device.ADI, "5", [355, 252,1], [1,1,1]);

		#p_pfd_orbit.rate_label_r_l.enableUpdate();
		#p_pfd_orbit.rate_label_r_c.enableUpdate();
		#p_pfd_orbit.rate_label_r_r.enableUpdate();

		#p_pfd_orbit.rate_label_y_l.enableUpdate();
		#p_pfd_orbit.rate_label_y_c.enableUpdate();
		#p_pfd_orbit.rate_label_y_r.enableUpdate();

		#p_pfd_orbit.rate_label_p_u.enableUpdate();
		#p_pfd_orbit.rate_label_p_c.enableUpdate();
		#p_pfd_orbit.rate_label_p_l.enableUpdate();

	# ADI rate needles

	data = SpaceShuttle.draw_tmarker_down();
	p_pfd_orbit.adi_roll_rate_needle = device.ADI.createChild("path", "ADI_roll_rate_needle")
        .setStrokeLineWidth(1)
        .setColor(0.0, 1.0, 0.0)
		.setScale(0.7, 1.16)
	.setColorFill(0.0, 1.0, 0.0)
	.moveTo(data[0][0], data[0][1]);
	for (var i = 0; (i< size(data)-1); i=i+1) 
		{p_pfd_orbit.adi_roll_rate_needle.lineTo(data[i+1][0], data[i+1][1]);}

	data = SpaceShuttle.draw_tmarker_left();
	p_pfd_orbit.adi_pitch_rate_needle = device.ADI.createChild("path", "ADI_pitch_rate_needle")
        .setStrokeLineWidth(1)
        .setColor(0.0, 1.0, 0.0)
		.setScale(1.16, 0.7)
	.setColorFill(0.0, 1.0, 0.0)
	.moveTo(data[0][0], data[0][1]);
	for (var i = 0; (i< size(data)-1); i=i+1) 
		{p_pfd_orbit.adi_pitch_rate_needle.lineTo(data[i+1][0], data[i+1][1]);}

	data = SpaceShuttle.draw_tmarker_up();
	p_pfd_orbit.adi_yaw_rate_needle = device.ADI.createChild("path", "ADI_yaw_rate_needle")
        .setStrokeLineWidth(1)
        .setColor(0.0, 1.0, 0.0)
		.setScale(0.7, 1.16)
	.setColorFill(0.0, 1.0, 0.0)
	.moveTo(data[0][0], data[0][1]);
	for (var i = 0; (i< size(data)-1); i=i+1) 
		{p_pfd_orbit.adi_yaw_rate_needle.lineTo(data[i+1][0], data[i+1][1]);}
	

	#Orbit PFD re organisation


	#device.ADI.setTranslation (-76.5, 40.0);
	device.ADI.setScale (1.35);
	device.ADI.setTranslation (-88.0, 5.0);

	#p_pfd_orbit.label_r.setFontSize(22);
	#p_pfd_orbit.label_p.setFontSize(22);
	#p_pfd_orbit.label_y.setFontSize(22);

	#p_pfd_orbit.r.setFontSize(20);
	#p_pfd_orbit.p.setFontSize(20);
	#p_pfd_orbit.y.setFontSize(20);

	p_pfd_orbit.label_r.setTranslation(25, 45);
	p_pfd_orbit.r.setTranslation(25.0, 45.0);

	p_pfd_orbit.label_p.setTranslation(25, 45);
	p_pfd_orbit.p.setTranslation(25, 45);

	p_pfd_orbit.label_y.setTranslation(25, 45);
	p_pfd_orbit.y.setTranslation(25, 45);





	}

    
    p_pfd_orbit.offdisplay = func
    {
	
	#Clear PFD when A/E pfd is called

		#Newer logic

	device.ADI.removeAllChildren();

		#Older logic

		#device.ADI.setScale(1.35);
		#device.ADI.setTranslation (-88.0, 5.0);

		#p_pfd_orbit.att_error_needles.setVisible(0);
		#p_pfd_orbit.adi_roll_rate_needle.setVisible(0);
		#p_pfd_orbit.adi_pitch_rate_needle.setVisible(0);
		#p_pfd_orbit.adi_yaw_rate_needle.setVisible(0);

		#p_pfd_orbit.adi_error_label_p_u.setVisible(0);
		#p_pfd_orbit.adi_error_label_p_l.setVisible(0);

	
	#p_pfd_orbit.label_r.setFontSize(14);
	#p_pfd_orbit.label_p.setFontSize(14);
	#p_pfd_orbit.label_y.setFontSize(14);


	p_pfd_orbit.menu_item.setColor(meds_r, meds_g, meds_b);
	p_pfd_orbit.menu_item_frame.setColor(meds_r, meds_g, meds_b);

	device.fc_bus_displayed = "";

	
    }
    
    p_pfd_orbit.update = func
    {

	# get mission-specific parameters and manage devices #########################################

	#Used GetValue instead of getprop
	#MM 201 and 202 and OPS 3 up to mm303 only

	var major_mode = p_pfd_orbit.nd_ref_major_mode.getValue();


	#var pitch = getprop("/orientation/pitch-deg");
	#var yaw = getprop("/orientation/heading-deg");
	#var roll = getprop("/orientation/roll-deg");

	var pitch = p_pfd_orbit.nd_ref_pitch.getValue();
	var yaw = p_pfd_orbit.nd_ref_yaw.getValue();
	var roll = p_pfd_orbit.nd_ref_roll.getValue();
	var course = p_pfd_orbit.nd_ref_course_deg.getValue();


	var adi_att_selection = p_pfd_orbit.nd_ref_adi_att_sel.getValue();

	var pitch_adi = pitch;
	var yaw_adi = yaw;
	var roll_adi = roll;

	var adi_rate_selection = p_pfd_orbit.nd_ref_adi_rate_range_sel.getValue();
	var adi_error_selection = p_pfd_orbit.nd_ref_adi_err_sel.getValue();

	#ADI rate range Orbit ( 5/2/0.2)  
	var adi_rate_range = 5.0;

	#ADI error range Orbit (10/5/1)
	var adi_error_range = 5.0;



	if ((major_mode == 201) or (major_mode == 202) or (major_mode == 301) or (major_mode == 302) or (major_mode == 303))   # Up to 304 (?)
		{

		p_pfd_orbit.att_error_needles.setVisible(1);
		p_pfd_orbit.adi_roll_rate_needle.setVisible(1);
		p_pfd_orbit.adi_pitch_rate_needle.setVisible(1);
		p_pfd_orbit.adi_yaw_rate_needle.setVisible(1);

		p_pfd_orbit.adi_error_label_p_u.setVisible(1);
		p_pfd_orbit.adi_error_label_p_l.setVisible(1);

		#Attitude

		if (adi_att_selection == 1)  #Inertial
			{
			pitch_adi = p_pfd_orbit.nd_ref_pitch_inrtl.getValue();
    		yaw_adi = p_pfd_orbit.nd_ref_yaw_inrtl.getValue();
    		roll_adi = -p_pfd_orbit.nd_ref_roll_inrtl.getValue();	
			}

		else if (adi_att_selection == -1)   # REF
			{
			var sid_ang = p_pfd_orbit.nd_ref_sid_ang_rad.getValue() * 180.0/math.pi;
    		pitch_adi = p_pfd_orbit.nd_ref_pitch_inrtl.getValue();
    		yaw_adi = p_pfd_orbit.nd_ref_yaw_inrtl.getValue()  + sid_ang - 260.0;
			roll_adi = -p_pfd_orbit.nd_ref_roll_inrtl.getValue();
			yaw_adi = yaw_adi;
			}

		else  # LVLH Orbit
			{ 
			yaw_adi = yaw - course;
			if (yaw_adi < 0.0) {yaw_adi = yaw_adi + 360.0;}
			}

		#ADI rate
		if ((major_mode == 201) or (major_mode == 202))
			{
			if (adi_rate_selection == -1) {adi_rate_range = 0.2;}
			else if (adi_rate_selection == 0) {adi_rate_range = 1.0;}
			else {adi_rate_range = 5.0;}
			}
		else #MM 301  through 303
			{
			if (adi_rate_selection == -1) {adi_rate_range = 1.0;}
			else if (adi_rate_selection == 0) {adi_rate_range = 5.0;}
			else {adi_rate_range = 10.0;}
			}


		#ADI error

		if (adi_error_selection == -1) {adi_error_range = 1.0;}
		else if (adi_error_selection == 0) {adi_error_range = 5.0;}
		else {adi_error_range = 10.0;}
		
		}
		

	else   # Inert Orbit PFD not driven by Datas outside OPS 2 /mm301 - 303
		{

		#Frozen orbit PFD PYR
		 pitch_adi = -89;
		 yaw_adi = 270;
		 roll_adi = 0;

		#Blank error needles
		p_pfd_orbit.att_error_needles.setVisible(0);
		p_pfd_orbit.adi_roll_rate_needle.setVisible(0);
		p_pfd_orbit.adi_pitch_rate_needle.setVisible(0);
		p_pfd_orbit.adi_yaw_rate_needle.setVisible(0);

		#Blank error labels 
		p_pfd_orbit.adi_error_label_p_u.setVisible(0);
		p_pfd_orbit.adi_error_label_p_l.setVisible(0);

			
		}


	
	
	var pitch_error = 0.0;
	var yaw_error = 0.0;
	var roll_error = 0.0;

	if ((major_mode == 201) or (major_mode == 202))
		{
			
		var up_mnvr_flag = getprop("/fdm/jsbsim/systems/ap/up-mnvr-flag");

		if ((up_mnvr_flag > 0) or (getprop("/fdm/jsbsim/systems/ap/oms-mnvr-flag") > 0))
			{
			yaw_error = -getprop("/fdm/jsbsim/systems/ap/track/yaw-error-deg");
			pitch_error = getprop("/fdm/jsbsim/systems/ap/track/pitch-error-deg");

			
			if (up_mnvr_flag < 3)
				{roll_error = -getprop("/fdm/jsbsim/systems/ap/track/roll-error-deg");}
			else
				{roll_error = 0.0;}
			}
		}





	

	# ADI sphere animation ##############################################

	# clear previous step

	p_pfd_orbit.adi_inner.removeAllChildren();

	# draw

	# projection vecs for labels
	var p_vecs = SpaceShuttle.projection_vecs(-pitch_adi, yaw_adi, -roll_adi);

	# ADI sphere
	var data = SpaceShuttle.draw_circle(0.75*95, 30);
	update_plot_data (p_pfd_orbit.adi_sphere_bg, data);

	data = SpaceShuttle.draw_adi_bg(pitch_adi, yaw_adi, roll_adi);
	update_plot_data (p_pfd_orbit.adi_sphere_bg_bright, data);

	if (getprop("/fdm/jsbsim/systems/adi/quality-level") > 0)
		{
		update_adi_sphere(p_pfd_orbit.adi_sphere, p_vecs);
		p_pfd_orbit.adi_sphere.setVisible(1);
		}
	else
		{
		p_pfd_orbit.adi_sphere.setVisible(0);
		}


	draw_sphere_labels(p_pfd_orbit.adi_inner, p_vecs, pitch_adi, yaw_adi, roll_adi);
	
	# ADI error needles

	var pitch_error_ntrans = SpaceShuttle.clamp(pitch_error, -adi_error_range, adi_error_range) * -40.0/adi_error_range;
	var yaw_error_ntrans = SpaceShuttle.clamp(yaw_error, -adi_error_range, adi_error_range) * -40.0/adi_error_range;
	var roll_error_ntrans = SpaceShuttle.clamp(roll_error, -adi_error_range, adi_error_range) * -40.0/adi_error_range;



	p_pfd_orbit.att_error_pitch.setTranslation(0.0, pitch_error_ntrans);
	p_pfd_orbit.att_error_yaw.setTranslation(yaw_error_ntrans, 0.0);
	p_pfd_orbit.att_error_roll.setTranslation(roll_error_ntrans,0.0);
	
	p_pfd_orbit.att_error_pitch.setScale(math.sqrt(9025. - pitch_error_ntrans*pitch_error_ntrans)/95.0,1.0);
	p_pfd_orbit.att_error_yaw.setScale(1.0,math.sqrt(9025. - yaw_error_ntrans*yaw_error_ntrans)/95.0);
	p_pfd_orbit.att_error_roll.setScale(1.0,math.sqrt(9025. - roll_error_ntrans*roll_error_ntrans)/95.0);

	p_pfd_orbit.adi_error_label_p_u.updateText(sprintf("%d", adi_error_range));
	p_pfd_orbit.adi_error_label_p_l.updateText(sprintf("%d", adi_error_range));

	
	

	# ADI rate needles / Labels not shown in Orbit pfd

	#p_pfd_orbit.rate_label_r_l.updateText(sprintf("%d", adi_rate_range));
	#p_pfd_orbit.rate_label_r_r.updateText(sprintf("%d", adi_rate_range));
	#p_pfd_orbit.rate_label_y_l.updateText(sprintf("%d", adi_rate_range));
	#p_pfd_orbit.rate_label_y_r.updateText(sprintf("%d", adi_rate_range));
	#p_pfd_orbit.rate_label_p_u.updateText(sprintf("%d", adi_rate_range));
	#p_pfd_orbit.rate_label_p_l.updateText(sprintf("%d", adi_rate_range));

	var roll_rate = getprop("/fdm/jsbsim/velocities/p-rad_sec") * 57.2957;
	roll_rate = SpaceShuttle.clamp(roll_rate, -adi_rate_range, adi_rate_range);
	p_pfd_orbit.adi_roll_rate_needle.setTranslation(255 + 13.0 * roll_rate * 5.0/adi_rate_range, 70);

	var pitch_rate = getprop("/fdm/jsbsim/velocities/q-rad_sec") * 57.2957;
	pitch_rate = SpaceShuttle.clamp(pitch_rate, -adi_rate_range, adi_rate_range);
	p_pfd_orbit.adi_pitch_rate_needle.setTranslation(360, 175 - 13.0 * pitch_rate * 5.0/adi_rate_range);

	var yaw_rate = getprop("/fdm/jsbsim/velocities/r-rad_sec") * 57.2957;
	yaw_rate = SpaceShuttle.clamp(yaw_rate, -adi_rate_range, adi_rate_range);
	p_pfd_orbit.adi_yaw_rate_needle.setTranslation(255 + 13.0 * yaw_rate * 5.0/adi_rate_range, 280.0);





	# numerical pitch, yaw and roll readouts

	var roll_alphanum = roll_adi;

	if (adi_att_selection == -1)
		{
		if ((major_mode == 201) or (major_mode == 202))
			{
			roll_alphanum = geo.normdeg180(roll_adi + 90.0);
			}
		}


	# 0 or 00 instead of blank spaces if number < 100

	p_pfd_orbit.r.setText(sprintf("%03d", roll_alphanum));
	p_pfd_orbit.p.setText(sprintf("%03d", pitch_adi));
	p_pfd_orbit.y.setText(sprintf("%03d", yaw_adi));




	
	

    };
    
    return p_pfd_orbit;
}







###############################################################################################
# batch functions for label drawing ###########################################################
###############################################################################################

var pfd_segment_draw = func (data, plot) {

	if (size(data) < 2) {return;}

	plot.moveTo(data[0][0],data[0][1]); 

        for (var i = 0; i< (size(data)-1); i=i+1)
        {
            var set = data[i+1];
	    if (set[2] == 1)
            	{plot.lineTo(set[0], set[1]);}
	    else
		{plot.moveTo(set[0], set[1]);}	
        }


}


var segment_append = func (draw, data) {

var n = size(data);

if (n==0) {return draw;}

# make sure the first point is always marked as MOVE TO
data[0][2] = 0;

for (var i=0; i<n; i=i+1)
	{
	append(draw, data[i]);
	}

return draw;
}

var update_plot_data = func (group, draw_raw) {

var draw = [];
var cmd = [];



var n_cur = size(draw_raw);


draw_raw[0][2] = 0;

#var n_move = 0;
#var n_draw = 0;

var move_flag = 0;

var move_buffer_coord = [0,0];

for (var i=0; i< n_cur; i=i+1)
	{


	if (draw_raw[i][2] == 1)
		{
		if (move_flag == 1)
			{
			append(cmd, canvas.Path.VG_MOVE_TO);
			append(draw, move_buffer_coord[0], move_buffer_coord[1]);
			#n_move = n_move + 1;
			}
		append(cmd, canvas.Path.VG_LINE_TO);
		append(draw, draw_raw[i][0], draw_raw[i][1]);
		#n_draw = n_draw + 1;
		move_flag = 0;
		}
	else
		{
		move_buffer_coord[0] = draw_raw[i][0];
		move_buffer_coord[1] = draw_raw[i][1];
		move_flag = 1;
		}
	
	}

n_cur = size(cmd);
var n_max = group.max_pts;

if (n_cur < 0.8 * n_max) # we likely used the quality slider and want to wipe
	{
	group._node.removeChildren("coord");
	group._node.removeChildren("cmd");
	group.max_pts = 0;
	n_max = n_cur;
	print("Node wipe!");
	}

var n = n_max;
if (n_cur > n_max)
	{
	n = n_cur;
	group.max_pts = n_cur;
	}


if (n_cur == 0) 
	{
	group.setVisible(0);
	return;
	}
else
	{
	group.setVisible(1);
	}

#print ("Draw: ", n_draw, " move: ", n_move);

# below is a fast workaround for the low performing canvas API
# should a fast method become available in the API, simply uncomment the
# setData method instead and end the routing afterwards

#




var adi_update_method = getprop("/fdm/jsbsim/systems/adi/update-method");

if (adi_update_method == 0)
{

# canvas-native setData method

#print ("Native");
group.setData(cmd, draw);
}
else if (adi_update_method == 1)
{

# use an array with node-references to speed up property I/O for the ADI

#print ("New");

var index = 0;
var index1 = 0;

var n_written = size(group.cmd_nd_ref_array);

var path = group._node.getPath();


var cmd_string = path~"/cmd";
var coord_string = path~"/coord";

for (var i=0; i< n_max; i=i+1)
	{
	index = 2.0 * i;
	index1 = index + 1;
	if ((i < n_written) and (i < n_cur))
		{
		group.cmd_nd_ref_array[i].setValue(cmd[i]);
		group.coord_nd_ref_array[index].setValue(draw[index]);
		group.coord_nd_ref_array[index1].setValue(draw[index1]);
		}
	else if (i < n_cur)
		{
		var cmd_ref = props.globals.getNode(cmd_string~"["~i~"]", 1);
		append(group.cmd_nd_ref_array, cmd_ref);
		cmd_ref.setValue(cmd[i]);

		var coord_ref = props.globals.getNode(coord_string~"["~index~"]", 1);
		append(group.coord_nd_ref_array, coord_ref);
		coord_ref.setValue(draw[index]);

		var coord_ref1 = props.globals.getNode(coord_string~"["~index1~"]", 1);
		append(group.coord_nd_ref_array, coord_ref1);
		coord_ref1.setValue(draw[index1]);

		#print("Creating");
		}
	else if (i< n_written)
		{
		group.cmd_nd_ref_array[i].setValue(canvas.Path.VG_MOVE_TO);
		group.coord_nd_ref_array[index].setValue(0);
		group.coord_nd_ref_array[index1].setValue(0);
		}
	else
		{
		var cmd_ref = props.globals.getNode(cmd_string~"["~i~"]", 1);
		append(group.cmd_nd_ref_array, cmd_ref);
		cmd_ref.setValue(canvas.Path.VG_MOVE_TO);

		var coord_ref = props.globals.getNode(coord_string~"["~index~"]", 1);
		append(group.coord_nd_ref_array, coord_ref);
		coord_ref.setValue(0);

		var coord_ref1 = props.globals.getNode(coord_string~"["~index1~"]", 1);
		append(group.coord_nd_ref_array, coord_ref1);
		coord_ref1.setValue(0);
		}

	}

group.max_pts = n_cur;


}
else
{

#print ("Old");

# old-style method with setprop

var index = 0;
var index1 = 0;
var path = group._node.getPath();

#print (path);



var cmd_string = path~"/cmd";
var coord_string = path~"/coord";

for (var i=0; i< n_max; i=i+1)
	{
	index = 2.0 * i;
	index1 = index + 1;
	if (i < n_cur)
		{
		setprop(cmd_string,i, cmd[i]);
		setprop(coord_string, index, draw[index]);
		setprop(coord_string, index1, draw[index1]);
		}
	else
		{
		setprop(cmd_string,i, canvas.Path.VG_MOVE_TO);
		setprop(coord_string, index, 0);
		setprop(coord_string, index1, 0);
		}

	}

group.max_pts = n_cur;
}

}


var place_compass_label = func (group, text, angle, radius, flag, xoffset, yoffset) {

	

	var placement = SpaceShuttle.compass_label_pos(radius, angle);

	var canvas_text = group.createChild("text")
      	.setText(text)
        .setColor(1,1,1)
	.setFontSize(10)
	.setFont(p_pfd_font_2)
	.setAlignment("center-bottom")
	.setRotation(angle * math.pi/180.0 * flag)
	.setTranslation(placement[0] + xoffset,-placement[1] + yoffset);


}

var write_sphere_label = func (group, text, angle, coords) {




if (coords[2] ==1)
	{

	var canvas_text = group.createChild("text")
      	.setText(text)
        .setColor(1,1,1)
	.setColorFill(0.2,0.2,0.2)
	.setFontSize(10)
	.setFont(p_pfd_font_2)
	.setAlignment("center-bottom")
	.setRotation(angle + coords[3] * 0.8 * math.pi/2.0)
	.setTranslation(coords[0], coords[1]);

	canvas_text.setDrawMode(canvas_text.FILLEDBOUNDINGBOX + canvas_text.TEXT);
	}

}




var write_tape_label = func (group, text, coords, color) {




if (coords[2] ==1)
	{
	var canvas_text = group.createChild("text")
      	.setText(text)
        .setColor(color[0],color[1],color[2])
	.setFontSize(14)
	.setFont(p_pfd_font_2)
	.setAlignment("center-bottom")
	.setRotation(0.0)
	.setTranslation(coords[0], coords[1]);
	}

}

var write_small_label = func (group, text, coords, color) {




if (coords[2] ==1)
	{
	var canvas_text = group.createChild("text")
      	.setText(text)
        .setColor(color[0],color[1],color[2])
	.setFontSize(10)
	.setFont(p_pfd_font_2)
	.setAlignment("center-bottom")
	.setRotation(0.0)
	.setTranslation(coords[0], coords[1]);
	}

}

var write_tape_label_bg = func (group, text, coords, color, bg_color) {




if (coords[2] ==1)
	{
	var canvas_text = group.createChild("text")
      	.setText(text)
        .setColor(color[0],color[1],color[2])
        .setColorFill(bg_color[0],bg_color[1],bg_color[2])
	.setFontSize(14)
	.setFont(p_pfd_font_2)
	.setAlignment("center-bottom")
	.setRotation(0.0)
	.setTranslation(coords[0], coords[1]);

	canvas_text.setDrawMode(canvas_text.FILLEDBOUNDINGBOX + canvas_text.TEXT);
	}

}



var label_from_degree = func (angle, flag) {

if (angle == 0.0) 
	{
	if (flag == 1) {return "N";}
	else {return "0";}
	}
else if (angle == 30.0)
	{return "3";}
else if (angle == 60.0)
	{return "6";}
else if (angle == 90.0)
	{
	if (flag == 1) {return "E";}	
	else	{return "9";}
	}
else if (angle == 120.0)
	{return "12";}
else if (angle == 15.0)
	{return "15";}
else if (angle == 180.0)
	{
	if (flag == 1) {return "S";}
	else {return "18";}
	}
else if (angle == 210.0)
	{return "21";}
else if (angle == 240.0)
	{return "24";}
else if (angle == 270.0)
	{	
	if (flag == 1) {return "W";}
	else {return "27";}
	}
else if (angle == 300.0)
	{return "30";}
else if (angle == 330.0)
	{return "33";}
else return "";
}


var draw_sphere_labels = func (group, p_vecs, pitch, yaw, roll) {

var coords = [];
var label = "";
var lon = 0;


var lat = 15;
for (var i=0; i< 12; i=i+1)
	{
	lon = 30.0 * i;
	label = label_from_degree(lon, 0);
	coords = SpaceShuttle.label_coords_sphere(lat, lon, p_vecs, pitch, yaw);
	write_sphere_label(group, label, -roll * math.pi/180.0, coords);
	}

var lat = 45;
for (var i=0; i< 12; i=i+1)
	{
	lon = 30.0 * i;
	label = label_from_degree(lon, 0);
	coords = SpaceShuttle.label_coords_sphere(lat, lon, p_vecs, pitch, yaw);
	write_sphere_label(group, label, -roll * math.pi/180.0, coords);
	}

var lat = -15;
for (var i=0; i< 12; i=i+1)
	{
	lon = 30.0 * i;
	label = label_from_degree(lon, 0);
	coords = SpaceShuttle.label_coords_sphere(lat, lon, p_vecs, pitch, yaw);
	write_sphere_label(group, label, -roll * math.pi/180.0, coords);
	}

var lat = -45;
for (var i=0; i< 12; i=i+1)
	{
	lon = 30.0 * i;
	label = label_from_degree(lon, 0);
	coords = SpaceShuttle.label_coords_sphere(lat, lon, p_vecs, pitch, yaw);
	write_sphere_label(group, label, -roll * math.pi/180.0, coords);
	}

}

var draw_mach_labels = func (group)
{

for (var i=0; i< 140; i=i+1)
	{
	var y = 5385 - i * 76.0;
	var coords = [0.0, y, 1];

	var label = sprintf("%2.1f", 0.2 * i);

	write_tape_label(group, label, coords, [0,0,0.15]);
	}

}

var draw_alpha_labels_upper = func (group)
{

for (var i=0; i< 36; i=i+1)
	{
	var y = 5.0 - i * 47.5;
	var coords = [0.0, y, 1];

	var label = sprintf("%d", 5 * i);

	write_tape_label(group, label, coords, [0,0,0.15]);
	}

}

var draw_alpha_labels_lower = func (group)
{

for (var i=0; i< 36; i=i+1)
	{
	var y = 5.0 + i * 47.5;
	var coords = [0.0, y, 1];

	var label = sprintf("%d", -5 * i);

	write_tape_label(group, label, coords, [1,1,1]);
	}

}

#Color modifications for H Ladder to avoid grey transition in lower ladder while going to next level ( from 2 k to 30 k to 100 k to 400k to Miles)
#We just want grey for Alti below 0 ie. for lower 2k ladder
#Rest is white background  with dark/blue ladder (0, 0, 0.15)

var radar_alt = getprop("/fdm/jsbsim/systems/navigation/radar-alt-available");
var major_mode = getprop("/fdm/jsbsim/systems/dps/major-mode");

var draw_H_labels_upper_miles = func (group)
{

for (var i=0; i< 20; i=i+1)
	{
	var y = 5.0 - i * 50.0;
	var coords = [0.0, y, 1];

	var label = sprintf("%d", 70 + 5* i);
	label=label~"M";
	if (i>0)
		{write_tape_label_bg(group, label, coords, [0,0,0.15], [1,1,1]);}
	else
		{write_tape_label(group, label, coords, [0,0,0.15]);}
	}

}

var draw_H_labels_lower_miles = func (group)
{

for (var i=0; i< 2; i=i+1)
	{
	var y = 5.0 + i * 50.0;
	var coords = [0.0, y, 1];

	var label = sprintf("%d", 70 - 5* i);
	label=label~"M";

	write_tape_label(group, label, coords, [0,0,0.15]);
	}

}


var draw_H_labels_upper_2k = func (group)
{

for (var i=0; i< 20; i=i+1)
	{
	var y = 5.0 - i * 50.0;
	var coords = [0.0, y, 1];

	var label = sprintf("%d", 100 * i);
	
	


	if (i>0)
		{
		if ((major_mode == 304) or (major_mode == 305) or (major_mode == 602) or (major_mode == 603))  # Yellow bg for OPS3/6
			{
			write_tape_label_bg(group, label, coords, [0,0,0.15], [1,1,0]);
			}
		else 
			{
			write_tape_label_bg(group, label, coords, [0,0,0.15], [1,1,1]);    # White bg for OPS 1
			} 
		}

	else
		{
		write_tape_label(group, label, coords, [0,0,0.15]);
		}
	}
}

var draw_H_labels_lower_2k = func (group)
{

for (var i=0; i< 2; i=i+1)
	{
	var y = 5.0 + i * 50.0;
	var coords = [0.0, y, 1];

	var label = sprintf("%d", 100 *  i);

	write_tape_label(group, label, coords, [1,1,1]); #Grey Background and white letters ( only there)
	}
}

var draw_H_labels_upper_30k = func (group)
{

for (var i=0; i< 29; i=i+1)
	{
	var y = 5.0 - i * 50.0;
	var coords = [0.0, y, 1];

	var label = sprintf("%d", 2 + i);
	label=label~"K";

	if (i>0)
		{write_tape_label_bg(group, label, coords, [0,0,0.15], [1,1,1]);}
	else
		{write_tape_label(group, label, coords, [0,0,0.15]);} 
	}
}

var draw_H_labels_lower_30k = func (group)
{

for (var i=0; i< 2; i=i+1)
	{
	var y = 5.0 + i * 50.0;
	var coords = [0.0, y, 1];

	var label = sprintf("%d", 2 - i);
	label=label~"K";

	write_tape_label(group, label, coords, [0,0,0.15]); #White Back ground from now on and dark letters 
	}
}

var draw_H_labels_upper_100k = func (group)
{

for (var i=0; i< 14; i=i+1)
	{
	var y = 5.0 - i * 50.0;
	var coords = [0.0, y, 1];

	var label = sprintf("%d", 30 + 5*i);
	label=label~"K";
	if (i>0)
		{write_tape_label_bg(group, label, coords, [0,0,0.15], [1,1,1]);}
	else
		{write_tape_label(group, label, coords, [0,0,0.15]);}
	}
}

var draw_H_labels_lower_100k = func (group)
{

for (var i=0; i< 2; i=i+1)
	{
	var y = 5.0 + i * 50.0;
	var coords = [0.0, y, 1];

	var label = sprintf("%d", 30 - 5*i);
	label=label~"K";

	write_tape_label(group, label, coords, [0,0,0.15]);
	}
}

var draw_H_labels_upper_400k = func (group)
{

for (var i=0; i< 6; i=i+1)
	{
	var y = 5.0 - i * 50.0;
	var coords = [0.0, y, 1];

	var label = sprintf("%d", 100 + 50*i);
	label=label~"K";
	if (i>0)
		{write_tape_label_bg(group, label, coords, [0,0,0.15], [1,1,1]);}
	else
		{write_tape_label(group, label, coords, [0,0,0.15]);}
	}
}

var draw_H_labels_lower_400k = func (group)
{

for (var i=0; i< 2; i=i+1)
	{
	var y = 5.0 + i * 50.0;
	var coords = [0.0, y, 1];

	var label = sprintf("%d", 100 - 50*i);
	label=label~"K";
	write_tape_label(group, label, coords, [0,0,0.15]);
	}
}


var draw_Hdot_labels_upper = func (group)
{

for (var i=0; i< 30; i=i+1)
	{
	var y = 5.0 - i * 60.0;
	var coords = [0.0, y, 1];

	var label_value = i * 100;
	var label = "";

	if (label_value < 1000)
		{label = sprintf("%d", label_value);}
	else
		{label = sprintf("%1.1f", label_value/1000)~"K";}
	write_tape_label(group, label, coords, [0,0,0.15]);
	}
}

var draw_Hdot_labels_lower = func (group)
{

for (var i=0; i< 30; i=i+1)
	{
	var y = 5.0 + i * 60.0;
	var coords = [0.0, y, 1];

	var label_value = -i * 100;
	var label = "";

	if (label_value > -1000)
		{label = sprintf("%d", label_value);}
	else
		{label = sprintf("%d", label_value/1000)~"K";}
	write_tape_label(group, label, coords, [1,1,1]);
	}
}

var draw_acc_labels = func (group)
{

for (var i=0; i<5; i=i+1)
	{
	var ang = 135.0 + i * 45;
	ang = math.pi/180.0 * ang;

	var x = 45 * math.sin(ang);	
	var y = -45 * math.cos(ang);

	var coords = [x,y,1];
	var label = sprintf("%d", -1+i);

	write_tape_label(group, label, coords, [0.7,0.7,0.78]);
	}


}



var draw_adi_sphere_staggered = func (group, p_vecs, cycle) {

var meridian_res = 30;
var circle_res = 30;

var data = [];

if (group.flag == -1) {return;}

# do not accept update calls while update is running
if ((group.flag == 1) and (cycle==0 ))
	{return;}

if (cycle == 0)
	{
	settimer(func {draw_adi_sphere_staggered(group, p_vecs, 1);}, 0 );
	}
else if (cycle == 1)
	{
	group.flag = 1;
	group.adi_group1.removeAllChildren();
	var plot = group.adi_group1.createChild("path")
        .setStrokeLineWidth(1)
        .setColor(1,1,1);

	for (var i = 0; i<12; i=i+1)
		{
		data = SpaceShuttle.draw_meridian(i * 30.0, meridian_res, p_vecs );
		pfd_segment_draw(data, plot);
		}

	settimer(func {draw_adi_sphere_staggered(group, p_vecs, 3);}, 0 );

	}
else if (cycle == 2)
	{
	group.adi_group2.removeAllChildren();
	var plot = group.adi_group2.createChild("path")
        .setStrokeLineWidth(1)
        .setColor(1,1,1);

	for (var i = 0; i<12; i=i+1)
		{
		data = SpaceShuttle.draw_meridian_ladder(i * 30.0 + 15.0, 5, p_vecs );
		pfd_segment_draw(data, plot);
		}

	settimer(func {draw_adi_sphere_staggered(group, p_vecs, 3);}, 0 );
	}
else if (cycle == 3)
	{
	group.adi_group3.removeAllChildren();
	var plot = group.adi_group3.createChild("path")
        .setStrokeLineWidth(1)
        .setColor(1,1,1);

	data = SpaceShuttle.draw_coord_circle(0.0, circle_res, p_vecs );
	pfd_segment_draw(data, plot);

	data = SpaceShuttle.draw_coord_circle(30.0, circle_res, p_vecs );
	pfd_segment_draw(data, plot);

	data = SpaceShuttle.draw_coord_circle(-30.0, circle_res, p_vecs );
	pfd_segment_draw(data, plot);

	data = SpaceShuttle.draw_coord_circle(60.0, circle_res, p_vecs );
	pfd_segment_draw(data, plot);

	data = SpaceShuttle.draw_coord_circle(-60.0, circle_res, p_vecs );
	pfd_segment_draw(data, plot);

	data = SpaceShuttle.draw_coord_circle(85.0, int(0.3 * circle_res), p_vecs );
	pfd_segment_draw(data, plot);

	data = SpaceShuttle.draw_coord_circle(-85.0, int (0.3 * circle_res), p_vecs );
	pfd_segment_draw(data, plot);

	group.flag = 0;
	#settimer(func {draw_adi_sphere_staggered(group, p_vecs, 4);}, 0 );

	}

else if (cycle == 4)
	{
	group.adi_group4.removeAllChildren();
	var plot = group.adi_group4.createChild("path")
        .setStrokeLineWidth(1)
        .setColor(1,1,1);

	data = SpaceShuttle.draw_circle_ladder(15.0, 12, p_vecs );
	pfd_segment_draw(data, plot);

	data = SpaceShuttle.draw_circle_ladder(-15.0, 12, p_vecs );
	pfd_segment_draw(data, plot);

	data = SpaceShuttle.draw_circle_ladder(45.0, 12, p_vecs );
	pfd_segment_draw(data, plot);

	data = SpaceShuttle.draw_circle_ladder(-45.0, 12, p_vecs );
	pfd_segment_draw(data, plot);
	
	group.flag = 0;

	}




}




var draw_adi_sphere = func (group, p_vecs) {


var meridian_res = 30;
var circle_res = 30;

var quality_level = getprop("/fdm/jsbsim/systems/adi/quality-level");



if (quality_level == 1)
	{
	meridian_res = 20;
	circle_res = 20;
	setprop("/sim/config/shuttle/center-cull-level", 1);
	}
else if (quality_level == 3)
	{
	setprop("/sim/config/shuttle/center-cull-level", 2);
	}
else if (quality_level == 4)
	{
	meridian_res = 60;
	circle_res = 60;
	setprop("/sim/config/shuttle/center-cull-level", 2);
	}
else	
	{
	setprop("/sim/config/shuttle/center-cull-level", 1);
	}


var data = [];

for (var i = 0; i<12; i=i+1)
	{
	data = SpaceShuttle.draw_meridian(i * 30.0, meridian_res, p_vecs );
	pfd_segment_draw(data, group);

	if (quality_level > 2)
		{
		data = SpaceShuttle.draw_meridian_ladder(i * 30.0 + 15.0, 5, p_vecs );
		pfd_segment_draw(data, group);
		}
	}



data = SpaceShuttle.draw_coord_circle(0.0, circle_res, p_vecs );
pfd_segment_draw(data, group);


data = SpaceShuttle.draw_coord_circle(30.0, circle_res, p_vecs );
pfd_segment_draw(data, group);

data = SpaceShuttle.draw_coord_circle(-30.0, circle_res, p_vecs );
pfd_segment_draw(data, group);

data = SpaceShuttle.draw_coord_circle(60.0, circle_res, p_vecs );
pfd_segment_draw(data, group);

data = SpaceShuttle.draw_coord_circle(-60.0, circle_res, p_vecs );
pfd_segment_draw(data, group);

data = SpaceShuttle.draw_coord_circle(85.0, int(circle_res), p_vecs );
pfd_segment_draw(data, group);

data = SpaceShuttle.draw_coord_circle(-85.0, int (circle_res), p_vecs );
pfd_segment_draw(data, group);

if (quality_level > 2)
	{
	data = SpaceShuttle.draw_circle_ladder(-15.0, 12, p_vecs );
	pfd_segment_draw(data, group);

	data = SpaceShuttle.draw_circle_ladder(15.0, 12, p_vecs );
	pfd_segment_draw(data, group);

	data = SpaceShuttle.draw_circle_ladder(45.0, 12, p_vecs );
	pfd_segment_draw(data, group);

	data = SpaceShuttle.draw_circle_ladder(-45.0, 12, p_vecs );
	pfd_segment_draw(data, group);
	}




}


var update_adi_sphere = func (group, p_vecs) {


var meridian_res = 30;
var circle_res = 30;

var quality_level = getprop("/fdm/jsbsim/systems/adi/quality-level");

if (quality_level == 1)
	{
	meridian_res = 20;
	circle_res = 20;
	setprop("/sim/config/shuttle/center-cull-level", 1);
	}
else if (quality_level == 3)
	{
	setprop("/sim/config/shuttle/center-cull-level", 2);
	}
else if (quality_level == 4)
	{
	meridian_res = 60;
	circle_res = 60;
	setprop("/sim/config/shuttle/center-cull-level", 2);
	}
else	
	{
	setprop("/sim/config/shuttle/center-cull-level", 1);
	}


var data = [];
var draw_raw = [];
var draw_raw1 = [];


for (var i = 0; i<12; i=i+1)
	{
	data = SpaceShuttle.draw_meridian(i * 30.0, meridian_res, p_vecs );
	draw_raw = segment_append (draw_raw, data);

	if (quality_level > 2)
		{
		data = SpaceShuttle.draw_meridian_ladder(i * 30.0 + 15.0, 5, p_vecs );
		draw_raw = segment_append (draw_raw, data);
		}
	}



data = SpaceShuttle.draw_coord_circle(0.0, circle_res, p_vecs );
draw_raw = segment_append (draw_raw, data);


data = SpaceShuttle.draw_coord_circle(30.0, circle_res, p_vecs );
draw_raw = segment_append (draw_raw, data);

data = SpaceShuttle.draw_coord_circle(-30.0, circle_res, p_vecs );
draw_raw = segment_append (draw_raw, data);

data = SpaceShuttle.draw_coord_circle(60.0, circle_res, p_vecs );
draw_raw = segment_append (draw_raw, data);

data = SpaceShuttle.draw_coord_circle(-60.0, circle_res, p_vecs );
draw_raw = segment_append (draw_raw, data);

data = SpaceShuttle.draw_coord_circle(85.0, int(circle_res), p_vecs );
draw_raw = segment_append (draw_raw, data);

data = SpaceShuttle.draw_coord_circle(-85.0, int (circle_res), p_vecs );
draw_raw = segment_append (draw_raw, data);

if (quality_level > 2)
	{
	data = SpaceShuttle.draw_circle_ladder(-15.0, 12, p_vecs );
	draw_raw = segment_append (draw_raw, data);

	data = SpaceShuttle.draw_circle_ladder(15.0, 12, p_vecs );
	draw_raw = segment_append (draw_raw, data);

	data = SpaceShuttle.draw_circle_ladder(45.0, 12, p_vecs );
	draw_raw = segment_append (draw_raw, data);

	data = SpaceShuttle.draw_circle_ladder(-45.0, 12, p_vecs );
	draw_raw = segment_append (draw_raw, data);
	}

update_plot_data (group, draw_raw);



}


var adi_invalid_air_data = func (pfd) {

	#print ("Air data invalid!");

	pfd.keas_tape.setVisible(0);   
	pfd.keas_display_text.setVisible(0);

	pfd.alpha_tape.setVisible(0); 
	pfd.alpha_display_text.setVisible(0);     

	pfd.H_tape.setVisible(0);   
	pfd.H_display_text.setVisible(0);   

	pfd.Hdot_tape.setVisible(0);   
	pfd.Hdot_display_text.setVisible(0);   

	pfd.plot_keas_tape.setColor(1,0,0);
	pfd.plot_alpha_tape.setColor(1,0,0);
	pfd.plot_H_tape.setColor(1,0,0);
	pfd.plot_Hdot_tape.setColor(1,0,0);

	pfd.keas_display_box.setColor(1,0,0);
	pfd.alpha_display_box.setColor(1,0,0);
	pfd.H_display_box.setColor(1,0,0);
	pfd.Hdot_display_box.setColor(1,0,0);
	pfd.rect1.setColor(1,0,0);
	pfd.rect2.setColor(1,0,0);

        pfd.keas.setVisible(0);

}


var adi_valid_air_data = func (pfd) {

	#print ("Air data valid!");

	pfd.keas_tape.setVisible(1);   
	pfd.keas_display_text.setVisible(1);

	pfd.alpha_tape.setVisible(1);   
	pfd.alpha_display_text.setVisible(1);   

	pfd.H_tape.setVisible(1);   
	pfd.H_display_text.setVisible(1);   

	pfd.Hdot_tape.setVisible(1); 
	pfd.Hdot_display_text.setVisible(1);     

	pfd.plot_keas_tape.setColor(1,1,1);
	pfd.plot_alpha_tape.setColor(1,1,1);
	pfd.plot_H_tape.setColor(1,1,1);
	pfd.plot_Hdot_tape.setColor(1,1,1);

	pfd.keas_display_box.setColor(1,1,1);
	pfd.alpha_display_box.setColor(1,1,1);
	pfd.H_display_box.setColor(1,1,1);
	pfd.Hdot_display_box.setColor(1,1,1);
	pfd.rect1.setColor(1,1,1);
	pfd.rect2.setColor(1,1,1);


        pfd.keas.setVisible(1);

}

