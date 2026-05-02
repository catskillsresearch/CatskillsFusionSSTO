#---------------------------------------
# SpaceShuttle PFD Page include:
#        Page: p_dps_sm_sys_summ2
# Description: the SM SYS SUMM 2 page
#      Author: Thorsten Renk, 2015 // GinGin, 2020
#---------------------------------------

#var sm_simulation_detail_level = getprop("/sim/config/shuttle/sm-detail-level");

var PFD_addpage_p_dps_sm_sys_summ2 = func(device)
{
    var p_dps_sm_sys_summ2 = device.addPage("CRTSMSysSumm2", "p_dps_sm_sys_summ2");

    p_dps_sm_sys_summ2.group = device.svg.getElementById("p_dps_sm_sys_summ2");
    p_dps_sm_sys_summ2.group.setColor(dps_r, dps_g, dps_b);    

    p_dps_sm_sys_summ2.apu1_egt = device.svg.getElementById("p_dps_sm_sys_summ2_apu1_egt");
    p_dps_sm_sys_summ2.apu2_egt = device.svg.getElementById("p_dps_sm_sys_summ2_apu2_egt");
    p_dps_sm_sys_summ2.apu3_egt = device.svg.getElementById("p_dps_sm_sys_summ2_apu3_egt");
    
    p_dps_sm_sys_summ2.apu1_egt_bu = device.svg.getElementById("p_dps_sm_sys_summ2_apu1_egt_bu");
    p_dps_sm_sys_summ2.apu2_egt_bu = device.svg.getElementById("p_dps_sm_sys_summ2_apu2_egt_bu");
    p_dps_sm_sys_summ2.apu3_egt_bu = device.svg.getElementById("p_dps_sm_sys_summ2_apu3_egt_bu");
    
    p_dps_sm_sys_summ2.apu1_oil_in = device.svg.getElementById("p_dps_sm_sys_summ2_apu1_oil_in");
    p_dps_sm_sys_summ2.apu2_oil_in = device.svg.getElementById("p_dps_sm_sys_summ2_apu2_oil_in");
    p_dps_sm_sys_summ2.apu3_oil_in = device.svg.getElementById("p_dps_sm_sys_summ2_apu3_oil_in");
    
    p_dps_sm_sys_summ2.apu1_oil_out = device.svg.getElementById("p_dps_sm_sys_summ2_apu1_oil_out");
    p_dps_sm_sys_summ2.apu2_oil_out = device.svg.getElementById("p_dps_sm_sys_summ2_apu2_oil_out");
    p_dps_sm_sys_summ2.apu3_oil_out = device.svg.getElementById("p_dps_sm_sys_summ2_apu3_oil_out");
    
    p_dps_sm_sys_summ2.apu1_speed = device.svg.getElementById("p_dps_sm_sys_summ2_apu1_speed");
    p_dps_sm_sys_summ2.apu2_speed = device.svg.getElementById("p_dps_sm_sys_summ2_apu2_speed");
    p_dps_sm_sys_summ2.apu3_speed = device.svg.getElementById("p_dps_sm_sys_summ2_apu3_speed");
    
    p_dps_sm_sys_summ2.apu1_fuel = device.svg.getElementById("p_dps_sm_sys_summ2_apu1_fuel");
    p_dps_sm_sys_summ2.apu2_fuel = device.svg.getElementById("p_dps_sm_sys_summ2_apu2_fuel");
    p_dps_sm_sys_summ2.apu3_fuel = device.svg.getElementById("p_dps_sm_sys_summ2_apu3_fuel");
    
    p_dps_sm_sys_summ2.apu1_oil_p = device.svg.getElementById("p_dps_sm_sys_summ2_apu1_oil_p");
    p_dps_sm_sys_summ2.apu2_oil_p = device.svg.getElementById("p_dps_sm_sys_summ2_apu2_oil_p");
    p_dps_sm_sys_summ2.apu3_oil_p = device.svg.getElementById("p_dps_sm_sys_summ2_apu3_oil_p");

    p_dps_sm_sys_summ2.apu1_pump_leakP = device.svg.getElementById("p_dps_sm_sys_summ2_apu1_pmp_p");
    p_dps_sm_sys_summ2.apu2_pump_leakP = device.svg.getElementById("p_dps_sm_sys_summ2_apu2_pmp_p");
    p_dps_sm_sys_summ2.apu3_pump_leakP = device.svg.getElementById("p_dps_sm_sys_summ2_apu3_pmp_p");
    
    p_dps_sm_sys_summ2.hyd1_p = device.svg.getElementById("p_dps_sm_sys_summ2_hyd1_p");
    p_dps_sm_sys_summ2.hyd2_p = device.svg.getElementById("p_dps_sm_sys_summ2_hyd2_p");
    p_dps_sm_sys_summ2.hyd3_p = device.svg.getElementById("p_dps_sm_sys_summ2_hyd3_p");
    
    p_dps_sm_sys_summ2.hyd1_rsvr_t = device.svg.getElementById("p_dps_sm_sys_summ2_hyd1_rsvr_t");
    p_dps_sm_sys_summ2.hyd2_rsvr_t = device.svg.getElementById("p_dps_sm_sys_summ2_hyd2_rsvr_t");
    p_dps_sm_sys_summ2.hyd3_rsvr_t = device.svg.getElementById("p_dps_sm_sys_summ2_hyd3_rsvr_t");
    
    p_dps_sm_sys_summ2.hyd1_rsvr_qty = device.svg.getElementById("p_dps_sm_sys_summ2_hyd1_rsvr_qty");
    p_dps_sm_sys_summ2.hyd2_rsvr_qty = device.svg.getElementById("p_dps_sm_sys_summ2_hyd2_rsvr_qty");
    p_dps_sm_sys_summ2.hyd3_rsvr_qty = device.svg.getElementById("p_dps_sm_sys_summ2_hyd3_rsvr_qty");
    
    p_dps_sm_sys_summ2.hyd1_rsvr_p = device.svg.getElementById("p_dps_sm_sys_summ2_hyd1_rsvr_p");
    p_dps_sm_sys_summ2.hyd2_rsvr_p = device.svg.getElementById("p_dps_sm_sys_summ2_hyd2_rsvr_p");
    p_dps_sm_sys_summ2.hyd3_rsvr_p = device.svg.getElementById("p_dps_sm_sys_summ2_hyd3_rsvr_p");
    
    p_dps_sm_sys_summ2.wb1_h2o_qty = device.svg.getElementById("p_dps_sm_sys_summ2_wb1_h2o_qty");
    p_dps_sm_sys_summ2.wb2_h2o_qty = device.svg.getElementById("p_dps_sm_sys_summ2_wb2_h2o_qty");
    p_dps_sm_sys_summ2.wb3_h2o_qty = device.svg.getElementById("p_dps_sm_sys_summ2_wb3_h2o_qty");
    
    p_dps_sm_sys_summ2.wb1_byp_vlv = device.svg.getElementById("p_dps_sm_sys_summ2_wb1_byp_vlv");
    p_dps_sm_sys_summ2.wb2_byp_vlv = device.svg.getElementById("p_dps_sm_sys_summ2_wb2_byp_vlv");
    p_dps_sm_sys_summ2.wb3_byp_vlv = device.svg.getElementById("p_dps_sm_sys_summ2_wb3_byp_vlv");
    
    
    p_dps_sm_sys_summ2.avbay1_t = device.svg.getElementById("p_dps_sm_sys_summ2_avbay1_t");
    p_dps_sm_sys_summ2.avbay2_t = device.svg.getElementById("p_dps_sm_sys_summ2_avbay2_t");
    p_dps_sm_sys_summ2.avbay3_t = device.svg.getElementById("p_dps_sm_sys_summ2_avbay3_t");
    

    p_dps_sm_sys_summ2.tk1_ph2 = device.svg.getElementById("p_dps_sm_sys_summ2_tk1_ph2");
    p_dps_sm_sys_summ2.tk2_ph2 = device.svg.getElementById("p_dps_sm_sys_summ2_tk2_ph2");
    p_dps_sm_sys_summ2.tk3_ph2 = device.svg.getElementById("p_dps_sm_sys_summ2_tk3_ph2");
    p_dps_sm_sys_summ2.tk4_ph2 = device.svg.getElementById("p_dps_sm_sys_summ2_tk4_ph2");
    p_dps_sm_sys_summ2.tk5_ph2 = device.svg.getElementById("p_dps_sm_sys_summ2_tk5_ph2");

    p_dps_sm_sys_summ2.mf1_ph2 = device.svg.getElementById("p_dps_sm_sys_summ2_mf1_ph2");
    p_dps_sm_sys_summ2.mf2_ph2 = device.svg.getElementById("p_dps_sm_sys_summ2_mf2_ph2");


    p_dps_sm_sys_summ2.tk1_po2 = device.svg.getElementById("p_dps_sm_sys_summ2_tk1_po2");
    p_dps_sm_sys_summ2.tk2_po2 = device.svg.getElementById("p_dps_sm_sys_summ2_tk2_po2");
    p_dps_sm_sys_summ2.tk3_po2 = device.svg.getElementById("p_dps_sm_sys_summ2_tk3_po2");
    p_dps_sm_sys_summ2.tk4_po2 = device.svg.getElementById("p_dps_sm_sys_summ2_tk4_po2");
    p_dps_sm_sys_summ2.tk5_po2 = device.svg.getElementById("p_dps_sm_sys_summ2_tk5_po2");
    
    p_dps_sm_sys_summ2.mf1_po2 = device.svg.getElementById("p_dps_sm_sys_summ2_mf1_po2");
    p_dps_sm_sys_summ2.mf2_po2 = device.svg.getElementById("p_dps_sm_sys_summ2_mf2_po2");

    p_dps_sm_sys_summ2.tk1_htrt1 = device.svg.getElementById("p_dps_sm_sys_summ2_tk1_htrt1");
    p_dps_sm_sys_summ2.tk2_htrt1 = device.svg.getElementById("p_dps_sm_sys_summ2_tk2_htrt1");
    p_dps_sm_sys_summ2.tk3_htrt1 = device.svg.getElementById("p_dps_sm_sys_summ2_tk3_htrt1");
    p_dps_sm_sys_summ2.tk4_htrt1 = device.svg.getElementById("p_dps_sm_sys_summ2_tk4_htrt1");
    p_dps_sm_sys_summ2.tk5_htrt1 = device.svg.getElementById("p_dps_sm_sys_summ2_tk5_htrt1");

    p_dps_sm_sys_summ2.tk1_htrt2 = device.svg.getElementById("p_dps_sm_sys_summ2_tk1_htrt2");
    p_dps_sm_sys_summ2.tk2_htrt2 = device.svg.getElementById("p_dps_sm_sys_summ2_tk2_htrt2");
    p_dps_sm_sys_summ2.tk3_htrt2 = device.svg.getElementById("p_dps_sm_sys_summ2_tk3_htrt2");
    p_dps_sm_sys_summ2.tk4_htrt2 = device.svg.getElementById("p_dps_sm_sys_summ2_tk4_htrt2");
    p_dps_sm_sys_summ2.tk5_htrt2 = device.svg.getElementById("p_dps_sm_sys_summ2_tk5_htrt2");

    p_dps_sm_sys_summ2.avbay1_fan = device.svg.getElementById("p_dps_sm_sys_summ2_avbay1_fan");
    p_dps_sm_sys_summ2.avbay2_fan = device.svg.getElementById("p_dps_sm_sys_summ2_avbay2_fan");
    p_dps_sm_sys_summ2.avbay3_fan = device.svg.getElementById("p_dps_sm_sys_summ2_avbay3_fan");

    p_dps_sm_sys_summ2.tc1_h2o_p = device.svg.getElementById("p_dps_sm_sys_summ2_tc1_h2o_p");
    p_dps_sm_sys_summ2.tc2_h2o_p = device.svg.getElementById("p_dps_sm_sys_summ2_tc2_h2o_p");

    p_dps_sm_sys_summ2.tc1_freon = device.svg.getElementById("p_dps_sm_sys_summ2_tc1_freon");
    p_dps_sm_sys_summ2.tc2_freon = device.svg.getElementById("p_dps_sm_sys_summ2_tc2_freon");

    p_dps_sm_sys_summ2.tc1_evap_t = device.svg.getElementById("p_dps_sm_sys_summ2_tc1_evap_t");
    p_dps_sm_sys_summ2.tc2_evap_t = device.svg.getElementById("p_dps_sm_sys_summ2_tc2_evap_t");


    #Arrow parameters



    p_dps_sm_sys_summ2.hyd1_p_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_hyd1_p_arrow");
    p_dps_sm_sys_summ2.hyd2_p_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_hyd2_p_arrow");
    p_dps_sm_sys_summ2.hyd3_p_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_hyd3_p_arrow");
    p_dps_sm_sys_summ2.hyd1_p_arrow.enableUpdate();
    p_dps_sm_sys_summ2.hyd2_p_arrow.enableUpdate();
    p_dps_sm_sys_summ2.hyd3_p_arrow.enableUpdate();

    p_dps_sm_sys_summ2.apu1_speed_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_apu1_speed_arrow");
    p_dps_sm_sys_summ2.apu2_speed_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_apu2_speed_arrow");
    p_dps_sm_sys_summ2.apu3_speed_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_apu3_speed_arrow");
    p_dps_sm_sys_summ2.apu1_speed_arrow.enableUpdate();
    p_dps_sm_sys_summ2.apu2_speed_arrow.enableUpdate();
    p_dps_sm_sys_summ2.apu3_speed_arrow.enableUpdate();

    p_dps_sm_sys_summ2.apu1_fuel_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_apu1_fuel_arrow");
    p_dps_sm_sys_summ2.apu2_fuel_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_apu2_fuel_arrow");
    p_dps_sm_sys_summ2.apu3_fuel_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_apu3_fuel_arrow");
    p_dps_sm_sys_summ2.apu1_fuel_arrow.enableUpdate();
    p_dps_sm_sys_summ2.apu2_fuel_arrow.enableUpdate();
    p_dps_sm_sys_summ2.apu3_fuel_arrow.enableUpdate();

    p_dps_sm_sys_summ2.wb1_h2o_qty_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_wb1_h2o_qty_arrow");
    p_dps_sm_sys_summ2.wb2_h2o_qty_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_wb2_h2o_qty_arrow");
    p_dps_sm_sys_summ2.wb3_h2o_qty_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_wb3_h2o_qty_arrow");
    p_dps_sm_sys_summ2.wb1_h2o_qty_arrow.enableUpdate();
    p_dps_sm_sys_summ2.wb2_h2o_qty_arrow.enableUpdate();
    p_dps_sm_sys_summ2.wb3_h2o_qty_arrow.enableUpdate();

    p_dps_sm_sys_summ2.tc1_h2o_p_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_tc1_h2o_p_arrow");
    p_dps_sm_sys_summ2.tc2_h2o_p_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_tc2_h2o_p_arrow");
    p_dps_sm_sys_summ2.tc1_h2o_p_arrow.enableUpdate();
    p_dps_sm_sys_summ2.tc2_h2o_p_arrow.enableUpdate();

    p_dps_sm_sys_summ2.avbay1_t_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_avbay1_t_arrow");
    p_dps_sm_sys_summ2.avbay2_t_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_avbay2_t_arrow");
    p_dps_sm_sys_summ2.avbay3_t_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_avbay3_t_arrow");
    p_dps_sm_sys_summ2.avbay1_t_arrow.enableUpdate();
    p_dps_sm_sys_summ2.avbay2_t_arrow.enableUpdate();
    p_dps_sm_sys_summ2.avbay3_t_arrow.enableUpdate();

    p_dps_sm_sys_summ2.tc1_freon_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_tc1_freon_arrow");
    p_dps_sm_sys_summ2.tc2_freon_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_tc2_freon_arrow");
    p_dps_sm_sys_summ2.tc1_freon_arrow.enableUpdate();
    p_dps_sm_sys_summ2.tc2_freon_arrow.enableUpdate();

    p_dps_sm_sys_summ2.avbay1_fan_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_avbay1_fan_arrow");
    p_dps_sm_sys_summ2.avbay2_fan_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_avbay2_fan_arrow");
    p_dps_sm_sys_summ2.avbay3_fan_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_avbay3_fan_arrow");
    p_dps_sm_sys_summ2.avbay1_fan_arrow.enableUpdate();
    p_dps_sm_sys_summ2.avbay2_fan_arrow.enableUpdate();
    p_dps_sm_sys_summ2.avbay3_fan_arrow.enableUpdate();

    p_dps_sm_sys_summ2.tc1_evap_t_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_tc1_evap_t_arrow");
    p_dps_sm_sys_summ2.tc2_evap_t_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_tc2_evap_t_arrow");
    p_dps_sm_sys_summ2.tc1_evap_t_arrow.enableUpdate();
    p_dps_sm_sys_summ2.tc2_evap_t_arrow.enableUpdate();

    p_dps_sm_sys_summ2.apu1_oil_p_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_apu1_oil_p_arrow");
    p_dps_sm_sys_summ2.apu2_oil_p_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_apu2_oil_p_arrow");
    p_dps_sm_sys_summ2.apu3_oil_p_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_apu3_oil_p_arrow");
    p_dps_sm_sys_summ2.apu1_oil_p_arrow.enableUpdate();
    p_dps_sm_sys_summ2.apu2_oil_p_arrow.enableUpdate();
    p_dps_sm_sys_summ2.apu3_oil_p_arrow.enableUpdate();

    p_dps_sm_sys_summ2.hyd1_rsvr_qty_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_hyd1_rsvr_qty_arrow");
    p_dps_sm_sys_summ2.hyd2_rsvr_qty_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_hyd2_rsvr_qty_arrow");
    p_dps_sm_sys_summ2.hyd3_rsvr_qty_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_hyd3_rsvr_qty_arrow");
    p_dps_sm_sys_summ2.hyd1_rsvr_qty_arrow.enableUpdate();
    p_dps_sm_sys_summ2.hyd2_rsvr_qty_arrow.enableUpdate();
    p_dps_sm_sys_summ2.hyd3_rsvr_qty_arrow.enableUpdate();

    p_dps_sm_sys_summ2.apu1_egt_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_apu1_egt_arrow");
    p_dps_sm_sys_summ2.apu2_egt_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_apu2_egt_arrow");
    p_dps_sm_sys_summ2.apu3_egt_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_apu3_egt_arrow");
    p_dps_sm_sys_summ2.apu1_egt_arrow.enableUpdate();
    p_dps_sm_sys_summ2.apu2_egt_arrow.enableUpdate();
    p_dps_sm_sys_summ2.apu3_egt_arrow.enableUpdate();

    p_dps_sm_sys_summ2.apu1_egt_bu_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_apu1_egt_bu_arrow");
    p_dps_sm_sys_summ2.apu2_egt_bu_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_apu2_egt_bu_arrow");
    p_dps_sm_sys_summ2.apu3_egt_bu_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_apu3_egt_bu_arrow");
    p_dps_sm_sys_summ2.apu1_egt_bu_arrow.enableUpdate();
    p_dps_sm_sys_summ2.apu2_egt_bu_arrow.enableUpdate();
    p_dps_sm_sys_summ2.apu3_egt_bu_arrow.enableUpdate();


        #BFS arrow for GG BED temp
        
    p_dps_sm_sys_summ2.gg1_bed_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_gg1_bed_arrow");
    p_dps_sm_sys_summ2.gg2_bed_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_gg2_bed_arrow");
    p_dps_sm_sys_summ2.gg3_bed_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_gg3_bed_arrow");
    p_dps_sm_sys_summ2.gg1_bed_arrow.enableUpdate();
    p_dps_sm_sys_summ2.gg2_bed_arrow.enableUpdate();
    p_dps_sm_sys_summ2.gg3_bed_arrow.enableUpdate();



    #Subgroups that contain Pass/bfs only elements/arrows ( GGbed// Hyd P)

    p_dps_sm_sys_summ2.bfs_only_arrow = device.svg.getElementById("p_dps_sm_sys_summ2_bfs_only_arrow");
    p_dps_sm_sys_summ2.bfs_only_element = device.svg.getElementById("p_dps_sm_sys_summ2_bfs_only_element");
    p_dps_sm_sys_summ2.pass_only_element = device.svg.getElementById("p_dps_sm_sys_summ2_pass_only_element");

    #All arrows in a group for Yellow color

    p_dps_sm_sys_summ2.arrow_group = device.svg.getElementById("p_dps_sm_sys_summ2_arrow_group");
    p_dps_sm_sys_summ2.arrow_group.setColor(1, 1, 0);


    #Labels that change for BFS (limited implementation as it would require some up shift of the cells// two complicated for just 2 new parameters (fuel tank valve temp and injector temp) 5-36 DPS pictionnary)
    #Relevant BFS parameters: GG BED Temp

    p_dps_sm_sys_summ2.rsvr_p_label = device.svg.getElementById("p_dps_sm_sys_summ2_rsvr_p_label");

    p_dps_sm_sys_summ2.line3_bfs = device.svg.getElementById("p_dps_sm_sys_summ2_line3_bfs");

    p_dps_sm_sys_summ2.gg_bed_label = device.svg.getElementById("p_dps_sm_sys_summ2_gg_bed_label");
    p_dps_sm_sys_summ2.gg1_bed = device.svg.getElementById("p_dps_sm_sys_summ2_gg1_bed");
    p_dps_sm_sys_summ2.gg2_bed = device.svg.getElementById("p_dps_sm_sys_summ2_gg2_bed");
    p_dps_sm_sys_summ2.gg3_bed = device.svg.getElementById("p_dps_sm_sys_summ2_gg3_bed");





    p_dps_sm_sys_summ2.ondisplay = func
    {
        device.DPS_menu_title.setText("                  SM SYS SUMM 2");
        device.MEDS_menu_title.setText("      DPS MENU");

    #Correct BFS/PASS layout based on sys summ 1 logic
    
    p_dps_sm_sys_summ2.major_function = SpaceShuttle.idp_array[device.port_selected-1].get_major_function();

	if (p_dps_sm_sys_summ2.major_function == 4)
		{
		var major_mode = "000";
		var spec = getprop("/fdm/jsbsim/systems/dps/spec-bfs");
		}
	else
		{
		var major_mode = getprop("/fdm/jsbsim/systems/dps/major-mode-sm");
		var spec =  getprop("/fdm/jsbsim/systems/dps/spec-sm");
		}
    	var spec_string = assemble_spec_string(spec);
        var ops_string = major_mode~"1/"~spec_string~"/079";  
    
        device.DPS_menu_ops.setText(ops_string);
    
    
    # set a few values not modeled explicitly to reasonable values
    

    
        p_dps_sm_sys_summ2.hyd1_rsvr_p.setText(sprintf(" 54")); 
        p_dps_sm_sys_summ2.hyd2_rsvr_p.setText(sprintf(" 56")); 
        p_dps_sm_sys_summ2.hyd3_rsvr_p.setText(sprintf(" 55")); 

	p_dps_sm_sys_summ2.tk1_ph2.setText(sprintf("208")); 
	p_dps_sm_sys_summ2.tk2_ph2.setText(sprintf("208")); 
	p_dps_sm_sys_summ2.tk3_ph2.setText(sprintf("206")); 
	p_dps_sm_sys_summ2.tk4_ph2.setText(sprintf("206")); 
	p_dps_sm_sys_summ2.tk5_ph2.setText(sprintf("206"));

	p_dps_sm_sys_summ2.mf1_ph2.setText(sprintf("208"));
	p_dps_sm_sys_summ2.mf2_ph2.setText(sprintf("207"));

	p_dps_sm_sys_summ2.tk1_po2.setText(sprintf(" 816")); 
	p_dps_sm_sys_summ2.tk2_po2.setText(sprintf(" 813")); 
	p_dps_sm_sys_summ2.tk3_po2.setText(sprintf(" 816")); 
	p_dps_sm_sys_summ2.tk4_po2.setText(sprintf(" 814")); 
	p_dps_sm_sys_summ2.tk5_po2.setText(sprintf(" 814")); 

	p_dps_sm_sys_summ2.mf1_po2.setText(sprintf(" 815"));
	p_dps_sm_sys_summ2.mf2_po2.setText(sprintf(" 815"));
    
   	p_dps_sm_sys_summ2.tk1_htrt1.setText(sprintf("-248")); 
   	p_dps_sm_sys_summ2.tk2_htrt1.setText(sprintf("-248")); 
   	p_dps_sm_sys_summ2.tk3_htrt1.setText(sprintf("-248")); 
   	p_dps_sm_sys_summ2.tk4_htrt1.setText(sprintf("-248")); 
   	p_dps_sm_sys_summ2.tk5_htrt1.setText(sprintf("-248")); 

  	p_dps_sm_sys_summ2.tk1_htrt2.setText(sprintf("-248")); 
   	p_dps_sm_sys_summ2.tk2_htrt2.setText(sprintf("-248")); 
   	p_dps_sm_sys_summ2.tk3_htrt2.setText(sprintf("-248")); 
   	p_dps_sm_sys_summ2.tk4_htrt2.setText(sprintf("-248")); 
   	p_dps_sm_sys_summ2.tk5_htrt2.setText(sprintf("-248")); 

    #Leak into a drain through fuel pump seal // normal up to a certain value
    p_dps_sm_sys_summ2.apu1_pump_leakP.setText(sprintf(" 0"));
    p_dps_sm_sys_summ2.apu2_pump_leakP.setText(sprintf(" 0"));
    p_dps_sm_sys_summ2.apu3_pump_leakP.setText(sprintf(" 0"));

    }
    
    p_dps_sm_sys_summ2.update = func
    {
    
        p_dps_sm_sys_summ2.major_function = SpaceShuttle.idp_array[device.port_selected-1].get_major_function(); # For BFS differences (major function 4)

        

        

        var apu1_egt = K_to_F(getprop("/fdm/jsbsim/systems/apu/apu/egt-K"));
        var apu2_egt = K_to_F(getprop("/fdm/jsbsim/systems/apu/apu[1]/egt-K"));
        var apu3_egt = K_to_F(getprop("/fdm/jsbsim/systems/apu/apu[2]/egt-K"));

        apu1_egt = math.max(apu1_egt, 0);
        apu2_egt = math.max(apu2_egt, 0);
        apu3_egt = math.max(apu3_egt, 0);

        p_dps_sm_sys_summ2.apu1_egt.setText(sprintf("%4.0f", apu1_egt+1.0));
        p_dps_sm_sys_summ2.apu2_egt.setText(sprintf("%4.0f", apu2_egt+ 1.0));
        p_dps_sm_sys_summ2.apu3_egt.setText(sprintf("%4.0f", apu3_egt));
    
        p_dps_sm_sys_summ2.apu1_egt_bu.setText(sprintf("%4.0f", apu1_egt+3.0));
        p_dps_sm_sys_summ2.apu2_egt_bu.setText(sprintf("%4.0f", apu2_egt+1.0));
        p_dps_sm_sys_summ2.apu3_egt_bu.setText(sprintf("%4.0f", apu3_egt+4.0));

        

    #APU oil in/out (logic from apu_hyd.nas for heater)

    var oil_T1 = K_to_F(getprop("/fdm/jsbsim/systems/apu/apu/oil-in-T-K"));
    var oil_out_T1 = K_to_F(getprop("/fdm/jsbsim/systems/thermal-distribution/apu1-temperature-K"));
	if (math.abs(getprop("/fdm/jsbsim/systems/apu/apu/lube-line-heater-status")) == 1)
		{
        if (oil_T1 < 57.0) {oil_T1 = 57.0;}
        if (oil_out_T1 < 57.0) {oil_out_T1 = 57.0;}
        }
    

	var oil_T2 = K_to_F(getprop("/fdm/jsbsim/systems/apu/apu[1]/oil-in-T-K"));
    var oil_out_T2 = K_to_F(getprop("/fdm/jsbsim/systems/thermal-distribution/apu2-temperature-K"));
	if (math.abs(getprop("/fdm/jsbsim/systems/apu/apu[1]/lube-line-heater-status")) == 1)
		{
        if (oil_T2 < 58.0) {oil_T2 = 58.0;}
        if (oil_out_T2 < 58.0) {oil_out_T2 = 58.0;}
        }

	var oil_T3 = K_to_F(getprop("/fdm/jsbsim/systems/apu/apu[2]/oil-in-T-K"));
    var oil_out_T3 = K_to_F(getprop("/fdm/jsbsim/systems/thermal-distribution/apu3-temperature-K"));
	if (math.abs(getprop("/fdm/jsbsim/systems/apu/apu[2]/lube-line-heater-status")) == 1)
		{
        if (oil_T3 < 60.0) {oil_T3 = 60.0;}
        if (oil_out_T3 < 60.0) {oil_out_T3 = 60.0;}
        }

    
        p_dps_sm_sys_summ2.apu1_oil_in.setText(sprintf("%3.0f", math.max(oil_T1, 0)));
        p_dps_sm_sys_summ2.apu2_oil_in.setText(sprintf("%3.0f", math.max(oil_T2, 0)));
        p_dps_sm_sys_summ2.apu3_oil_in.setText(sprintf("%3.0f", math.max(oil_T3, 0)));
    
        p_dps_sm_sys_summ2.apu1_oil_out.setText(sprintf("%3.0f", math.max(oil_out_T1, 0)));
        p_dps_sm_sys_summ2.apu2_oil_out.setText(sprintf("%3.0f", math.max(oil_out_T2, 0)));
        p_dps_sm_sys_summ2.apu3_oil_out.setText(sprintf("%3.0f", math.max(oil_out_T3, 0)));

        

        

        var apu1_oil_p = getprop("/fdm/jsbsim/systems/apu/apu/oil-p-psia");
        var apu2_oil_p = getprop("/fdm/jsbsim/systems/apu/apu[1]/oil-p-psia");
        var apu3_oil_p = getprop("/fdm/jsbsim/systems/apu/apu[2]/oil-p-psia");

    
        p_dps_sm_sys_summ2.apu1_oil_p.setText(sprintf("%3.0f", apu1_oil_p));
        p_dps_sm_sys_summ2.apu2_oil_p.setText(sprintf("%3.0f", apu2_oil_p));
        p_dps_sm_sys_summ2.apu3_oil_p.setText(sprintf("%3.0f", apu3_oil_p));



        

        var apu1_speed = 100.0 * getprop("/fdm/jsbsim/systems/apu/apu/apu-rpm-fraction");
        var apu2_speed = 100.0 * getprop("/fdm/jsbsim/systems/apu/apu[1]/apu-rpm-fraction");
        var apu3_speed = 100.0 * getprop("/fdm/jsbsim/systems/apu/apu[2]/apu-rpm-fraction");

        p_dps_sm_sys_summ2.apu1_speed.setText(sprintf("%3.0f", apu1_speed));
        p_dps_sm_sys_summ2.apu2_speed.setText(sprintf("%3.0f", apu2_speed));
        p_dps_sm_sys_summ2.apu3_speed.setText(sprintf("%3.0f", apu3_speed));



        





        

        var hyd1_p = getprop("/fdm/jsbsim/systems/apu/apu/hyd-pressure-psia");
        var hyd2_p = getprop("/fdm/jsbsim/systems/apu/apu[1]/hyd-pressure-psia");
        var hyd3_p = getprop("/fdm/jsbsim/systems/apu/apu[2]/hyd-pressure-psia");

        p_dps_sm_sys_summ2.hyd1_p.setText(sprintf("%4.0f", hyd1_p));
        p_dps_sm_sys_summ2.hyd2_p.setText(sprintf("%4.0f", hyd2_p));
        p_dps_sm_sys_summ2.hyd3_p.setText(sprintf("%4.0f", hyd3_p));


        
    
        p_dps_sm_sys_summ2.hyd1_rsvr_t.setText(sprintf("%3.0f", K_to_F(getprop("/fdm/jsbsim/systems/apu/apu/hyd-rsvr-T-K")-1.0))); 
        p_dps_sm_sys_summ2.hyd2_rsvr_t.setText(sprintf("%3.0f", K_to_F(getprop("/fdm/jsbsim/systems/apu/apu[1]/hyd-rsvr-T-K")))); 
        p_dps_sm_sys_summ2.hyd3_rsvr_t.setText(sprintf("%3.0f", K_to_F(getprop("/fdm/jsbsim/systems/apu/apu[2]/hyd-rsvr-T-K")+5.0))); 
    
    
        

        var apu1_fuel = getprop("/consumables/fuel/tank[14]/level-lbs")/3.5;
        var apu2_fuel = getprop("/consumables/fuel/tank[15]/level-lbs")/3.5;
        var apu3_fuel = getprop("/consumables/fuel/tank[16]/level-lbs")/3.5;

        p_dps_sm_sys_summ2.apu1_fuel.setText(sprintf("%3.0f", apu1_fuel));
        p_dps_sm_sys_summ2.apu2_fuel.setText(sprintf("%3.0f", apu2_fuel));
        p_dps_sm_sys_summ2.apu3_fuel.setText(sprintf("%3.0f", apu3_fuel));


        



        
        var wb1_h2o_qty = getprop("/fdm/jsbsim/propulsion/tank[20]/contents-lbs")/1.42;
        var wb2_h2o_qty = getprop("/fdm/jsbsim/propulsion/tank[21]/contents-lbs")/1.42;
        var wb3_h2o_qty = getprop("/fdm/jsbsim/propulsion/tank[22]/contents-lbs")/1.42;
    
        p_dps_sm_sys_summ2.wb1_h2o_qty.setText(sprintf("%3.0f", wb1_h2o_qty)); 
        p_dps_sm_sys_summ2.wb2_h2o_qty.setText(sprintf("%3.0f", wb2_h2o_qty)); 
        p_dps_sm_sys_summ2.wb3_h2o_qty.setText(sprintf("%3.0f", wb3_h2o_qty)); 




    
        p_dps_sm_sys_summ2.wb1_byp_vlv.setText(sprintf("%s", wsb_vlv_to_string(getprop("/fdm/jsbsim/systems/thermal-distribution/spray-boiler-1-switch"))));
        p_dps_sm_sys_summ2.wb2_byp_vlv.setText(sprintf("%s", wsb_vlv_to_string(getprop("/fdm/jsbsim/systems/thermal-distribution/spray-boiler-2-switch"))));
        p_dps_sm_sys_summ2.wb3_byp_vlv.setText(sprintf("%s", wsb_vlv_to_string(getprop("/fdm/jsbsim/systems/thermal-distribution/spray-boiler-3-switch"))));
    
    

        

        var avbay1_t = K_to_F(getprop("/fdm/jsbsim/systems/eclss/avbay/temperature-K")-2.0);
        var avbay2_t = K_to_F(getprop("/fdm/jsbsim/systems/eclss/avbay[1]/temperature-K"));
        var avbay3_t = K_to_F(getprop("/fdm/jsbsim/systems/eclss/avbay[2]/temperature-K")+1.0);

        avbay1_t = SpaceShuttle.clamp(avbay1_t, 45, 145);
        avbay2_t = SpaceShuttle.clamp(avbay2_t, 45, 145);
        avbay3_t = SpaceShuttle.clamp(avbay3_t, 45, 145);

        p_dps_sm_sys_summ2.avbay1_t.setText(sprintf("%3.0f", avbay1_t)); 
        p_dps_sm_sys_summ2.avbay2_t.setText(sprintf("%3.0f", avbay2_t)); 
        p_dps_sm_sys_summ2.avbay3_t.setText(sprintf("%3.0f", avbay3_t)); 



    
    

    var avbay1_fan = getprop("/fdm/jsbsim/systems/eclss/avbay/fan-cooling-effect") * 3.80;
    var avbay2_fan = getprop("/fdm/jsbsim/systems/eclss/avbay[1]/fan-cooling-effect") * 3.77;
    var avbay3_fan = getprop("/fdm/jsbsim/systems/eclss/avbay[2]/fan-cooling-effect") * 3.92;

	p_dps_sm_sys_summ2.avbay1_fan.setText(sprintf("%4.2f", avbay1_fan)); 
	p_dps_sm_sys_summ2.avbay2_fan.setText(sprintf("%4.2f", avbay2_fan)); 
	p_dps_sm_sys_summ2.avbay3_fan.setText(sprintf("%4.2f", avbay3_fan));  



    




    

    var water_pump1_active = getprop("/fdm/jsbsim/systems/atcs/water-pump-1-active");
    var water_pump2_active = getprop("/fdm/jsbsim/systems/atcs/water-pump-2-active");

    # Condition for water pump failure 

    var water_pump1_condition = getprop("/fdm/jsbsim/systems/failures/water-pump-1-condition");
    var water_pump2_condition = getprop("/fdm/jsbsim/systems/failures/water-pump-2-condition");
    #var water_loop_state = getprop("/fdm/jsbsim/systems/atcs/water-pump-2-active"); 

    #If no Pump failure, always a small residual flow like coded ( 20 ish psia)// if pump failure, no more pressure even with pump status 1
    
    var water_pressure1 = water_pump1_condition * 20 + water_pump1_active * 43;
	var water_pressure2 = water_pump2_condition * 23 + water_pump2_active * 41;


	p_dps_sm_sys_summ2.tc1_h2o_p.setText(sprintf("%3.0f", water_pressure1));
	p_dps_sm_sys_summ2.tc2_h2o_p.setText(sprintf("%3.0f", water_pressure2));


    
    



    
    
	var freon_flow1 = getprop("/fdm/jsbsim/systems/atcs/freon-pump-1-active") * 2246.0;
	var freon_flow2 = getprop("/fdm/jsbsim/systems/atcs/freon-pump-2-active") * 2258.0;

        p_dps_sm_sys_summ2.tc1_freon.setText(sprintf("%4.0f", math.max(freon_flow1, 570)));
    	p_dps_sm_sys_summ2.tc2_freon.setText(sprintf("%4.0f", math.max(freon_flow2, 570)));


    



    
    
	var evap_t1 = K_to_F(getprop("/fdm/jsbsim/systems/thermal-distribution/freon-out-temperature-K"));
    var ops = getprop("/fdm/jsbsim/systems/dps/ops");
    

    evap_t1 = SpaceShuttle.clamp(evap_t1, 0, 130);

	p_dps_sm_sys_summ2.tc1_evap_t.setText(sprintf("%3.0f", evap_t1));
    p_dps_sm_sys_summ2.tc2_evap_t.setText(sprintf("%3.0f", evap_t1));



    

   
	var mission_time = getprop("/fdm/jsbsim/systems/timer/delta-MET") + getprop("/sim/time/elapsed-sec");
	var qty = (1.0 - 0.4 * (mission_time/(86400.0 * 12.0))) * 100.0;
	if (qty < 3.0) {qty = 3.0;}

    var hyd_rsvr_qty = int(qty);
    

        p_dps_sm_sys_summ2.hyd1_rsvr_qty.setText(sprintf("%3d", hyd_rsvr_qty + 1)); 
        p_dps_sm_sys_summ2.hyd2_rsvr_qty.setText(sprintf("%3d", hyd_rsvr_qty)); 
        p_dps_sm_sys_summ2.hyd3_rsvr_qty.setText(sprintf("%3d", hyd_rsvr_qty + 3)); 


     


    #SM realistic option with indicators

	if (SpaceShuttle.sm_simulation_detail_level == 1)
		{
        
        p_dps_sm_sys_summ2.arrow_group.setVisible(1);

        #APU egt (↑ above 1150°, which is the case with high speed mode)
        
        if (apu1_egt > 1150)
            {
            p_dps_sm_sys_summ2.apu1_egt_arrow.updateText("↑");
            p_dps_sm_sys_summ2.apu1_egt_bu_arrow.updateText("↑");
            }
        else if (apu1_egt == 0)
            {
            p_dps_sm_sys_summ2.apu1_egt_arrow.updateText("L");
            p_dps_sm_sys_summ2.apu1_egt_bu_arrow.updateText("L");
            }
        else
            {
            p_dps_sm_sys_summ2.apu1_egt_arrow.updateText("");
            p_dps_sm_sys_summ2.apu1_egt_bu_arrow.updateText("");
            }

        if (apu2_egt > 1150)
            {
            p_dps_sm_sys_summ2.apu2_egt_arrow.updateText("↑");
            p_dps_sm_sys_summ2.apu2_egt_bu_arrow.updateText("↑");
            }
        else if (apu2_egt == 0)
            {
            p_dps_sm_sys_summ2.apu2_egt_arrow.updateText("L");
            p_dps_sm_sys_summ2.apu2_egt_bu_arrow.updateText("L");
            }
        else
            {
            p_dps_sm_sys_summ2.apu2_egt_arrow.updateText("");
            p_dps_sm_sys_summ2.apu2_egt_bu_arrow.updateText("");
            }

        if (apu3_egt > 1150)
            {
            p_dps_sm_sys_summ2.apu3_egt_arrow.updateText("↑");
            p_dps_sm_sys_summ2.apu3_egt_bu_arrow.updateText("↑");
            }
        else if (apu3_egt == 0)
            {
            p_dps_sm_sys_summ2.apu3_egt_arrow.updateText("L");
            p_dps_sm_sys_summ2.apu3_egt_bu_arrow.updateText("L");
            }
        else
            {
            p_dps_sm_sys_summ2.apu3_egt_arrow.updateText("");
            p_dps_sm_sys_summ2.apu3_egt_bu_arrow.updateText("");
            }


            #Oil Out pressure (↓ below 25)

        if (apu1_oil_p < 25) {p_dps_sm_sys_summ2.apu1_oil_p_arrow.updateText("↓");}
        else {p_dps_sm_sys_summ2.apu1_oil_p_arrow.updateText("");}

        if (apu2_oil_p < 25) {p_dps_sm_sys_summ2.apu2_oil_p_arrow.updateText("↓");}
        else {p_dps_sm_sys_summ2.apu2_oil_p_arrow.updateText("");}

        if (apu3_oil_p < 25) {p_dps_sm_sys_summ2.apu3_oil_p_arrow.updateText("↓");}
        else {p_dps_sm_sys_summ2.apu3_oil_p_arrow.updateText("");}



            #Apu speed (L for 0 and ↓ below 80)

        if (apu1_speed == 0) {p_dps_sm_sys_summ2.apu1_speed_arrow.updateText("L");}
        else if ((apu1_speed > 0) and (apu1_speed < 80)) {p_dps_sm_sys_summ2.apu1_speed_arrow.updateText("↓");}
        else {p_dps_sm_sys_summ2.apu1_speed_arrow.updateText("");}

        if (apu2_speed == 0) {p_dps_sm_sys_summ2.apu2_speed_arrow.updateText("L");}
        else if ((apu2_speed > 0) and (apu2_speed < 80)) {p_dps_sm_sys_summ2.apu2_speed_arrow.updateText("↓");}
        else {p_dps_sm_sys_summ2.apu2_speed_arrow.updateText("");}

        if (apu3_speed == 0) {p_dps_sm_sys_summ2.apu3_speed_arrow.updateText("L");}
        else if ((apu3_speed > 0) and (apu3_speed < 80)) {p_dps_sm_sys_summ2.apu3_speed_arrow.updateText("↓");}
        else {p_dps_sm_sys_summ2.apu3_speed_arrow.updateText("");}


        #Hyd Press (L for 0 and ↓ below 1930)

        if (hyd1_p < 10) {p_dps_sm_sys_summ2.hyd1_p_arrow.updateText("L");}
        else if ((hyd1_p > 10) and (hyd1_p < 1930)) {p_dps_sm_sys_summ2.hyd1_p_arrow.updateText("↓");}
        else {p_dps_sm_sys_summ2.hyd1_p_arrow.updateText("");}

        if (hyd2_p < 10) {p_dps_sm_sys_summ2.hyd2_p_arrow.updateText("L");}
        else if ((hyd2_p > 10) and (hyd2_p < 1930)) {p_dps_sm_sys_summ2.hyd2_p_arrow.updateText("↓");}
        else {p_dps_sm_sys_summ2.hyd2_p_arrow.updateText("");}

        if (hyd3_p < 10) {p_dps_sm_sys_summ2.hyd3_p_arrow.updateText("L");}
        else if ((hyd3_p > 10) and (hyd3_p < 1930)) {p_dps_sm_sys_summ2.hyd3_p_arrow.updateText("↓");}
        else {p_dps_sm_sys_summ2.hyd3_p_arrow.updateText("");}



        #Apu Fuel (H,L and ↓ below 35 // mean from PASS and BFS)

        if (apu1_fuel > 99.4) {p_dps_sm_sys_summ2.apu1_fuel_arrow.updateText("H");}
        else if (apu1_fuel < 0.6) {p_dps_sm_sys_summ2.apu1_fuel_arrow.updateText("L");}
        else if ((apu1_fuel > 0.6) and (apu1_fuel < 35)) {p_dps_sm_sys_summ2.apu1_fuel_arrow.updateText("↓");}
        else {p_dps_sm_sys_summ2.apu1_fuel_arrow.updateText("");}

        if (apu2_fuel > 99.4) {p_dps_sm_sys_summ2.apu2_fuel_arrow.updateText("H");}
        else if (apu2_fuel < 0.6) {p_dps_sm_sys_summ2.apu2_fuel_arrow.updateText("L");}
        else if ((apu2_fuel > 0.6) and (apu2_fuel < 35)) {p_dps_sm_sys_summ2.apu2_fuel_arrow.updateText("↓");}
        else {p_dps_sm_sys_summ2.apu2_fuel_arrow.updateText("");}

        if (apu3_fuel > 99.4) {p_dps_sm_sys_summ2.apu3_fuel_arrow.updateText("H");}
        else if (apu3_fuel < 0.6) {p_dps_sm_sys_summ2.apu3_fuel_arrow.updateText("L");}
        else if ((apu3_fuel > 0.6) and (apu3_fuel < 35)) {p_dps_sm_sys_summ2.apu3_fuel_arrow.updateText("↓");}
        else {p_dps_sm_sys_summ2.apu3_fuel_arrow.updateText("");}



        #H2O Qty (L/H and ↓ below 50 // mean between PASS and BFS)


        if (wb1_h2o_qty > 99.4) {p_dps_sm_sys_summ2.wb1_h2o_qty_arrow.updateText("H");}
        else if (wb1_h2o_qty < 0.6) {p_dps_sm_sys_summ2.wb1_h2o_qty_arrow.updateText("L");}
        else if ((wb1_h2o_qty > 0.6) and (wb1_h2o_qty < 50)) {p_dps_sm_sys_summ2.wb1_h2o_qty_arrow.updateText("↓");}
        else {p_dps_sm_sys_summ2.wb1_h2o_qty_arrow.updateText("");}

        if (wb2_h2o_qty > 99.4) {p_dps_sm_sys_summ2.wb2_h2o_qty_arrow.updateText("H");}
        else if (wb2_h2o_qty < 0.6) {p_dps_sm_sys_summ2.wb2_h2o_qty_arrow.updateText("L");}
        else if ((wb2_h2o_qty > 0.6) and (wb2_h2o_qty < 50)) {p_dps_sm_sys_summ2.wb2_h2o_qty_arrow.updateText("↓");}
        else {p_dps_sm_sys_summ2.wb2_h2o_qty_arrow.updateText("");}

        if (wb3_h2o_qty > 99.4) {p_dps_sm_sys_summ2.wb3_h2o_qty_arrow.updateText("H");}
        else if (wb3_h2o_qty < 0.6) {p_dps_sm_sys_summ2.wb3_h2o_qty_arrow.updateText("L");}
        else if ((wb3_h2o_qty > 0.6) and (wb3_h2o_qty < 50)) {p_dps_sm_sys_summ2.wb3_h2o_qty_arrow.updateText("↓");}
        else {p_dps_sm_sys_summ2.wb3_h2o_qty_arrow.updateText("");}


        #Av Bay temp ( clamp for higher value that can be excedeed in case of dual fan failure) ( L/H 45/145 and ↑ above 130)

        if (avbay1_t == 145) {p_dps_sm_sys_summ2.avbay1_t_arrow.updateText("H");}
        else if ((avbay1_t > 130) and (avbay1_t < 145)) {p_dps_sm_sys_summ2.avbay1_t_arrow.updateText("↑");}
        else {p_dps_sm_sys_summ2.avbay1_t_arrow.updateText("");}

        if (avbay2_t == 145) {p_dps_sm_sys_summ2.avbay2_t_arrow.updateText("H");}
        else if ((avbay2_t > 130) and (avbay2_t < 145)) {p_dps_sm_sys_summ2.avbay2_t_arrow.updateText("↑");}
        else {p_dps_sm_sys_summ2.avbay2_t_arrow.updateText("");}

        if (avbay3_t == 145) {p_dps_sm_sys_summ2.avbay3_t_arrow.updateText("H");}
        else if ((avbay3_t > 130) and (avbay3_t < 145)) {p_dps_sm_sys_summ2.avbay3_t_arrow.updateText("↑");}
        else {p_dps_sm_sys_summ2.avbay3_t_arrow.updateText("");}


        #Av Bay fan pressure (L for 0 // ↓ below 3)

    if (avbay1_fan == 0) {p_dps_sm_sys_summ2.avbay1_fan_arrow.updateText("L");}
    else if ((avbay1_fan > 0) and (avbay1_fan < 3)) {p_dps_sm_sys_summ2.avbay1_fan_arrow.updateText("↓");}
    else {p_dps_sm_sys_summ2.avbay1_fan_arrow.updateText("");}

    if (avbay2_fan == 0) {p_dps_sm_sys_summ2.avbay2_fan_arrow.updateText("L");}
    else if ((avbay2_fan > 0) and (avbay2_fan < 3)) {p_dps_sm_sys_summ2.avbay2_fan_arrow.updateText("↓");}
    else {p_dps_sm_sys_summ2.avbay2_fan_arrow.updateText("");}

    if (avbay3_fan == 0) {p_dps_sm_sys_summ2.avbay3_fan_arrow.updateText("L");}
    else if ((avbay3_fan > 0) and (avbay3_fan < 3)) {p_dps_sm_sys_summ2.avbay3_fan_arrow.updateText("↓");}
    else {p_dps_sm_sys_summ2.avbay3_fan_arrow.updateText("");}



        #Water Pump (L for 0 and ↓ below 30 // fix values for water pressure anyway)
    
    if (water_pressure1 == 0) {p_dps_sm_sys_summ2.tc1_h2o_p_arrow.updateText("L");}
    else if (water_pressure1 == 20) {p_dps_sm_sys_summ2.tc1_h2o_p_arrow.updateText("↓");}
    else if (water_pressure1 == 63) {p_dps_sm_sys_summ2.tc1_h2o_p_arrow.updateText("");}

    if (water_pressure2 == 0) {p_dps_sm_sys_summ2.tc2_h2o_p_arrow.updateText("L");}
    else if (water_pressure2 == 23) {p_dps_sm_sys_summ2.tc2_h2o_p_arrow.updateText("↓");}
    else if (water_pressure2 == 64) {p_dps_sm_sys_summ2.tc2_h2o_p_arrow.updateText("");}


            #Freon Flow ( L for 0)

    if (freon_flow1 == 0) {p_dps_sm_sys_summ2.tc1_freon_arrow.updateText("L");}
    else {p_dps_sm_sys_summ2.tc1_freon_arrow.updateText("");}

    if (freon_flow2 == 0) {p_dps_sm_sys_summ2.tc2_freon_arrow.updateText("L");}
    else {p_dps_sm_sys_summ2.tc2_freon_arrow.updateText("");}



            #Evap temp( L for 25 / H for 130/ ↓ below 32 and ↑ above 65 (115 for ascent) in real) (In sim adjusted value L for 0 / H for 130 / ↓ below 20 / ↑ above 65)

    if (ops == 1)
        {
        if (evap_t1 == 0)
            {
            p_dps_sm_sys_summ2.tc1_evap_t_arrow.updateText("L");
            p_dps_sm_sys_summ2.tc2_evap_t_arrow.updateText("L");
            }
        else if ((evap_t1 > 0) and (evap_t1 < 20))
            {
            p_dps_sm_sys_summ2.tc1_evap_t_arrow.updateText("↓");
            p_dps_sm_sys_summ2.tc2_evap_t_arrow.updateText("↓");
            }
        else if ((evap_t1 > 115) and (evap_t1 < 130)) # 115 ° for OPS 1, to let time to fes to work and bring evap below 70 °
            {
            p_dps_sm_sys_summ2.tc1_evap_t_arrow.updateText("↑");
            p_dps_sm_sys_summ2.tc2_evap_t_arrow.updateText("↑");
            }
        else if (evap_t1 == 130)
            {
            p_dps_sm_sys_summ2.tc1_evap_t_arrow.updateText("H");
            p_dps_sm_sys_summ2.tc2_evap_t_arrow.updateText("H");
            }
        else
            {
            p_dps_sm_sys_summ2.tc1_evap_t_arrow.updateText("");
            p_dps_sm_sys_summ2.tc2_evap_t_arrow.updateText("");
            }
        }
    else
        {
        if (evap_t1 == 0)
            {
            p_dps_sm_sys_summ2.tc1_evap_t_arrow.updateText("L");
            p_dps_sm_sys_summ2.tc2_evap_t_arrow.updateText("L");
            }
        else if ((evap_t1 > 0) and (evap_t1 < 20))
            {
            p_dps_sm_sys_summ2.tc1_evap_t_arrow.updateText("↓");
            p_dps_sm_sys_summ2.tc2_evap_t_arrow.updateText("↓");
            }
        else if ((evap_t1 > 65) and (evap_t1 < 130))   # 65° for OPS != than ascent
            {
            p_dps_sm_sys_summ2.tc1_evap_t_arrow.updateText("↑");
            p_dps_sm_sys_summ2.tc2_evap_t_arrow.updateText("↑");
            }
        else if (evap_t1 == 130)
            {
            p_dps_sm_sys_summ2.tc1_evap_t_arrow.updateText("H");
            p_dps_sm_sys_summ2.tc2_evap_t_arrow.updateText("H");
            }
        else
            {
            p_dps_sm_sys_summ2.tc1_evap_t_arrow.updateText("");
            p_dps_sm_sys_summ2.tc2_evap_t_arrow.updateText("");
            }
        }



            #Hyd quantity (H/L, ↓ below 40, ↑ above 90) 

    
    if (hyd_rsvr_qty > 90) 
        {
        p_dps_sm_sys_summ2.hyd1_rsvr_qty_arrow.updateText("↑");
        p_dps_sm_sys_summ2.hyd2_rsvr_qty_arrow.updateText("↑");
        p_dps_sm_sys_summ2.hyd3_rsvr_qty_arrow.updateText("↑");
        }
    else 
        {
        p_dps_sm_sys_summ2.hyd1_rsvr_qty_arrow.updateText("");
        p_dps_sm_sys_summ2.hyd2_rsvr_qty_arrow.updateText("");
        p_dps_sm_sys_summ2.hyd3_rsvr_qty_arrow.updateText("");
        }
    

        }

    else {p_dps_sm_sys_summ2.arrow_group.setVisible(0);}






    #Some of the BFS differences ( No rsvr hyd pressure // GG bed temps // one more sep line)

    if (p_dps_sm_sys_summ2.major_function == 4)
        {

        #p_dps_sm_sys_summ2.gg1_bed_arrow.setVisible(1);
        #p_dps_sm_sys_summ2.gg2_bed_arrow.setVisible(1);
        #p_dps_sm_sys_summ2.gg3_bed_arrow.setVisible(1);

        #p_dps_sm_sys_summ2.rsvr_p_label.setVisible(0);
        #p_dps_sm_sys_summ2.hyd1_rsvr_p.setVisible(0);
        #p_dps_sm_sys_summ2.hyd2_rsvr_p.setVisible(0);
        #p_dps_sm_sys_summ2.hyd3_rsvr_p.setVisible(0);
        #p_dps_sm_sys_summ2.gg_bed_label.setVisible(1);
        #p_dps_sm_sys_summ2.gg1_bed.setVisible(1);
        #p_dps_sm_sys_summ2.gg2_bed.setVisible(1);
        #p_dps_sm_sys_summ2.gg3_bed.setVisible(1);

        p_dps_sm_sys_summ2.pass_only_element.setVisible(0);

        #GG bed temp items

        
        p_dps_sm_sys_summ2.bfs_only_element.setVisible(1);
        p_dps_sm_sys_summ2.bfs_only_arrow.setVisible(1);
        

        p_dps_sm_sys_summ2.line3_bfs.setVisible(1);


        #GG bed calculations ( H 500 // ↓ below 258 for BFS )

        var ggbed_T1 = K_to_F(getprop("/fdm/jsbsim/systems/apu/apu/gg-bed-T-K"));
        var ggbed_T2 = K_to_F(getprop("/fdm/jsbsim/systems/apu/apu[1]/gg-bed-T-K")) - 1;
        var ggbed_T3 = K_to_F(getprop("/fdm/jsbsim/systems/apu/apu[2]/gg-bed-T-K")) + 3;

        ggbed_T1 = SpaceShuttle.clamp(ggbed_T1, 0, 500);
        ggbed_T2 = SpaceShuttle.clamp(ggbed_T2, 0, 500);
        ggbed_T3 = SpaceShuttle.clamp(ggbed_T3, 0, 500);

        p_dps_sm_sys_summ2.gg1_bed.setText(sprintf("%3d", ggbed_T1));
        p_dps_sm_sys_summ2.gg2_bed.setText(sprintf("%3d", ggbed_T2));
        p_dps_sm_sys_summ2.gg3_bed.setText(sprintf("%3d", ggbed_T3));

        if (ggbed_T1 == 500) {p_dps_sm_sys_summ2.gg1_bed_arrow.updateText("H");}
        else if (ggbed_T1 < 258) {p_dps_sm_sys_summ2.gg1_bed_arrow.updateText("↓");}
        else {p_dps_sm_sys_summ2.gg1_bed_arrow.updateText("");}

        if (ggbed_T2 == 500) {p_dps_sm_sys_summ2.gg2_bed_arrow.updateText("H");}
        else if (ggbed_T2 < 258) {p_dps_sm_sys_summ2.gg2_bed_arrow.updateText("↓");}
        else {p_dps_sm_sys_summ2.gg2_bed_arrow.updateText("");}

        if (ggbed_T3 == 500) {p_dps_sm_sys_summ2.gg3_bed_arrow.updateText("H");}
        else if (ggbed_T3 < 258) {p_dps_sm_sys_summ2.gg3_bed_arrow.updateText("↓");}
        else {p_dps_sm_sys_summ2.gg3_bed_arrow.updateText("");}

        }
    else
        {

        #p_dps_sm_sys_summ2.gg1_bed_arrow.setVisible(0);
        #p_dps_sm_sys_summ2.gg2_bed_arrow.setVisible(0);
        #p_dps_sm_sys_summ2.gg3_bed_arrow.setVisible(0);

        #p_dps_sm_sys_summ2.rsvr_p_label.setVisible(1);
        #p_dps_sm_sys_summ2.hyd1_rsvr_p.setVisible(1);
        #p_dps_sm_sys_summ2.hyd2_rsvr_p.setVisible(1);
        #p_dps_sm_sys_summ2.hyd3_rsvr_p.setVisible(1);
        #p_dps_sm_sys_summ2.gg_bed_label.setVisible(0);
        #p_dps_sm_sys_summ2.gg1_bed.setVisible(0);
        #p_dps_sm_sys_summ2.gg2_bed.setVisible(0);
        #p_dps_sm_sys_summ2.gg3_bed.setVisible(0);


        p_dps_sm_sys_summ2.pass_only_element.setVisible(1);

        #GG bed temp items

        p_dps_sm_sys_summ2.bfs_only_element.setVisible(0);
        p_dps_sm_sys_summ2.bfs_only_arrow.setVisible(0);
       
        
        p_dps_sm_sys_summ2.line3_bfs.setVisible(0);

        }








        device.update_common_DPS();
    
    
    
    
    }
    
    return p_dps_sm_sys_summ2;
}
