#---------------------------------------
# SpaceShuttle PFD Page include:
#        Page: p_dps_mnvr
# Description: the maneuver page
#      Author: Thorsten Renk, 2015 // GinGin, 2020
#---------------------------------------

var PFD_addpage_p_dps_mnvr = func(device)
{
    var p_dps_mnvr = device.addPage("CRTMnvr", "p_dps_mnvr");

    p_dps_mnvr.group = device.svg.getElementById("p_dps_mnvr");
    p_dps_mnvr.group.setColor(dps_r, dps_g, dps_b);
    
    p_dps_mnvr.oms_pitch_left = device.svg.getElementById("p_dps_mnvr_gmbl_l_pitch");
    p_dps_mnvr.oms_pitch_right = device.svg.getElementById("p_dps_mnvr_gmbl_r_pitch");
    p_dps_mnvr.oms_yaw_left = device.svg.getElementById("p_dps_mnvr_gmbl_l_yaw");
    p_dps_mnvr.oms_yaw_right = device.svg.getElementById("p_dps_mnvr_gmbl_r_yaw");
    
    p_dps_mnvr.current_apoapsis = device.svg.getElementById("p_dps_mnvr_ha_cur");
    p_dps_mnvr.current_periapsis = device.svg.getElementById("p_dps_mnvr_hp_cur");
    p_dps_mnvr.ha_tgt = device.svg.getElementById("p_dps_mnvr_ha_tgt");
    p_dps_mnvr.hp_tgt = device.svg.getElementById("p_dps_mnvr_hp_tgt");

    p_dps_mnvr.current_apoapsis.enableUpdate();
    p_dps_mnvr.current_periapsis.enableUpdate();
    p_dps_mnvr.ha_tgt.enableUpdate();
    p_dps_mnvr.hp_tgt.enableUpdate();
    
    p_dps_mnvr.fwd_rcs_dump = device.svg.getElementById("p_dps_mnvr_fwd_rcs_dump");
    p_dps_mnvr.fwd_rcs_arm = device.svg.getElementById("p_dps_mnvr_fwd_rcs_arm");
    p_dps_mnvr.fwd_rcs_off = device.svg.getElementById("p_dps_mnvr_fwd_rcs_off");

    p_dps_mnvr.fwd_rcs_dump.enableUpdate();
    p_dps_mnvr.fwd_rcs_arm.enableUpdate();
    p_dps_mnvr.fwd_rcs_off.enableUpdate();    

    p_dps_mnvr.surf_drive_on = device.svg.getElementById("p_dps_mnvr_surf_drive_on");
    p_dps_mnvr.surf_drive_off = device.svg.getElementById("p_dps_mnvr_surf_drive_off");
    
    p_dps_mnvr.surf_drive_on.enableUpdate();
    p_dps_mnvr.surf_drive_off.enableUpdate();

    p_dps_mnvr.oms_both = device.svg.getElementById("p_dps_mnvr_oms_both");
    p_dps_mnvr.oms_l = device.svg.getElementById("p_dps_mnvr_oms_l");
    p_dps_mnvr.oms_r = device.svg.getElementById("p_dps_mnvr_oms_r");
    p_dps_mnvr.rcs_sel = device.svg.getElementById("p_dps_mnvr_rcs_sel");

    p_dps_mnvr.oms_both.enableUpdate();
    p_dps_mnvr.oms_l.enableUpdate();
    p_dps_mnvr.oms_r.enableUpdate();
    p_dps_mnvr.rcs_sel.enableUpdate();

    
    p_dps_mnvr.tv_roll = device.svg.getElementById("p_dps_mnvr_tv_roll");
    
    p_dps_mnvr.p = device.svg.getElementById("p_dps_mnvr_p");
    p_dps_mnvr.ly = device.svg.getElementById("p_dps_mnvr_ly");
    p_dps_mnvr.ry = device.svg.getElementById("p_dps_mnvr_ry");
    
    p_dps_mnvr.wt = device.svg.getElementById("p_dps_mnvr_wt");
    
    p_dps_mnvr.tig = device.svg.getElementById("p_dps_mnvr_tig");
    
    p_dps_mnvr.c1 = device.svg.getElementById("p_dps_mnvr_c1");
    p_dps_mnvr.c2 = device.svg.getElementById("p_dps_mnvr_c2");
    p_dps_mnvr.ht = device.svg.getElementById("p_dps_mnvr_ht");
    p_dps_mnvr.tt = device.svg.getElementById("p_dps_mnvr_tt");
    p_dps_mnvr.prplt = device.svg.getElementById("p_dps_mnvr_prplt");

    p_dps_mnvr.c1.enableUpdate();
    p_dps_mnvr.c2.enableUpdate();
    p_dps_mnvr.ht.enableUpdate();
    p_dps_mnvr.tt.enableUpdate();
    p_dps_mnvr.prplt.enableUpdate();


    p_dps_mnvr.dvx = device.svg.getElementById("p_dps_mnvr_dvx");
    p_dps_mnvr.dvy = device.svg.getElementById("p_dps_mnvr_dvy");
    p_dps_mnvr.dvz = device.svg.getElementById("p_dps_mnvr_dvz");

    p_dps_mnvr.dvx.enableUpdate();
    p_dps_mnvr.dvy.enableUpdate();
    p_dps_mnvr.dvz.enableUpdate();

    
    p_dps_mnvr.load = device.svg.getElementById("p_dps_mnvr_load");
    
    p_dps_mnvr.burn_att_roll = device.svg.getElementById("p_dps_mnvr_burn_att_roll");
    p_dps_mnvr.burn_att_pitch = device.svg.getElementById("p_dps_mnvr_burn_att_pitch");
    p_dps_mnvr.burn_att_yaw = device.svg.getElementById("p_dps_mnvr_burn_att_yaw");
    
    p_dps_mnvr.mnvr = device.svg.getElementById("p_dps_mnvr_mnvr");
    p_dps_mnvr.active_dap = device.svg.getElementById("p_dps_mnvr_active_dap");

    p_dps_mnvr.mnvr.enableUpdate();
    p_dps_mnvr.active_dap.enableUpdate();
    
    p_dps_mnvr.dvtot = device.svg.getElementById("p_dps_mnvr_dvtot");
    p_dps_mnvr.tgo = device.svg.getElementById("p_dps_mnvr_tgo");

    p_dps_mnvr.dvtot.enableUpdate();
    p_dps_mnvr.tgo.enableUpdate();
    
    p_dps_mnvr.exec = device.svg.getElementById("p_dps_mnvr_exec_msg");
    p_dps_mnvr.exec.setColor(1.0, 1.0, 0.0);   # Yellow flashing exec
    
    p_dps_mnvr.ttapsis_text = device.svg.getElementById("p_dps_mnvr_ttapsis_text");
    p_dps_mnvr.ttapsis = device.svg.getElementById("p_dps_mnvr_ttapsis");
    
    p_dps_mnvr.vgo_x = device.svg.getElementById("p_dps_mnvr_vgo_x");
    p_dps_mnvr.vgo_y = device.svg.getElementById("p_dps_mnvr_vgo_y");
    p_dps_mnvr.vgo_z = device.svg.getElementById("p_dps_mnvr_vgo_z");
    
    
    p_dps_mnvr.pri_l = device.svg.getElementById("p_dps_mnvr_pri_l");
    p_dps_mnvr.pri_r = device.svg.getElementById("p_dps_mnvr_pri_r");
    p_dps_mnvr.sec_l = device.svg.getElementById("p_dps_mnvr_sec_l");
    p_dps_mnvr.sec_r = device.svg.getElementById("p_dps_mnvr_sec_r");
    p_dps_mnvr.off_l = device.svg.getElementById("p_dps_mnvr_off_l");
    p_dps_mnvr.off_r = device.svg.getElementById("p_dps_mnvr_off_r");
    p_dps_mnvr.gmbl_ck = device.svg.getElementById("p_dps_mnvr_gmbl_ck");

    p_dps_mnvr.pri_l.enableUpdate();
    p_dps_mnvr.pri_r.enableUpdate();
    p_dps_mnvr.sec_l.enableUpdate();
    p_dps_mnvr.sec_r.enableUpdate();
    p_dps_mnvr.off_l.enableUpdate();
    p_dps_mnvr.off_r.enableUpdate();
    p_dps_mnvr.gmbl_ck.enableUpdate(); 


    #OPS 2 PEG 7 EXT DV or LAMBERT symbology

    p_dps_mnvr.ext_dv = device.svg.getElementById("p_dps_mnvr_extdv");
    p_dps_mnvr.ext_dv.enableUpdate();
    

    p_dps_mnvr.tta = device.svg.getElementById("p_dps_mnvr_tta");
    p_dps_mnvr.rei = device.svg.getElementById("p_dps_mnvr_rei");

    p_dps_mnvr.abort_tgt = device.svg.getElementById("p_dps_mnvr_abort_tgt");
    p_dps_mnvr.abort_tgt.enableUpdate();



    p_dps_mnvr.blink = 0;
    
    
    
    p_dps_mnvr.ondisplay = func
    {
    var major_mode = getprop("/fdm/jsbsim/systems/dps/major-mode");
	var abort_mode = getprop("/fdm/jsbsim/systems/abort/abort-mode");  
    p_dps_mnvr.major_func = SpaceShuttle.idp_array[device.port_selected-1].get_major_function();

	if (p_dps_mnvr.major_func == 4)  
		{
		major_mode = getprop("/fdm/jsbsim/systems/dps/major-mode-bfs");
        device.DPS_menu_ops.setText(major_mode~"1/");  #BFS Menu
		}
    else {device.DPS_menu_ops.setText(major_mode~"1/   /");}  #PASS menu

        var string1 = "                     ";
    
        if ((major_mode == 104) and (abort_mode < 3))
    		{string1 = "               OMS 1 ";}
	else if ((major_mode == 104) and (abort_mode == 3))
		{string1 = "               ATO 1 ";}
	else if ((major_mode == 104) and (abort_mode == 4))
		{string1 = "                AOA 1 ";}		
        else if ((major_mode == 105) and (abort_mode < 3))
    		{string1 = "               OMS 2 ";}
 	else if ((major_mode == 105) and (abort_mode == 3))
    		{string1 = "               ATO 2 ";}
 	else if ((major_mode == 105) and (abort_mode == 4))
    		{string1 = "               AOA 2 ";}
        else if ((major_mode == 106) and (abort_mode < 3))
    		{string1 = "               OMS 2 ";}
 	else if ((major_mode == 106) and (abort_mode == 3))
    		{string1 = "               ATO 2 ";}
 	else if ((major_mode == 106) and (abort_mode == 4))
    		{string1 = "               AOA 2 ";}
        else if (major_mode == 202)
    		{string1 = "               ORBIT ";}
        else if ((major_mode == 301) or (major_mode == 302) or (major_mode == 303))
    		{string1 = "               DEORB ";}
    
        var string2 = " EXEC";
    
        if ((major_mode == 106) or (major_mode == 301) or (major_mode == 303))
    	{string2 = " COAST ";}
    
        var weight = getprop("/fdm/jsbsim/systems/ap/oms-plan/weight");
        if (weight ==0) {setprop("/fdm/jsbsim/systems/ap/oms-plan/weight", getprop("/fdm/jsbsim/inertia/weight-lbs"));}
    
        p_dps_mnvr.load.setText("LOAD");
    
        device.DPS_menu_title.setText(string1~"MNVR"~string2);
        device.MEDS_menu_title.setText("      DPS MENU");



	p_dps_mnvr.rei.setText("");


    }


    
    
    p_dps_mnvr.update = func
    {
    
        device.update_common_DPS();
    
        #Clamp values to avoid trim > 9.9° and Apsis > 999.9 Nm ( max allowed for display// DPS pictionnary)
    
        p_dps_mnvr.oms_pitch_left.setText(sprintf("%+4.1f",SpaceShuttle.clamp(getprop("/fdm/jsbsim/propulsion/engine[5]/pitch-angle-rad") * 57.297 + 11.7, -9.9, 9.9))); #4 letters (+0.0)
        p_dps_mnvr.oms_pitch_right.setText(sprintf("%+4.1f",SpaceShuttle.clamp(getprop("/fdm/jsbsim/propulsion/engine[6]/pitch-angle-rad") * 57.297 + 11.7, -9.9, 9.9)));
        p_dps_mnvr.oms_yaw_left.setText(sprintf("%+4.1f",SpaceShuttle.clamp(getprop("/fdm/jsbsim/propulsion/engine[5]/yaw-angle-rad") * 57.297 - 5.7, -9.9, 9.9)));
        p_dps_mnvr.oms_yaw_right.setText(sprintf("%+4.1f",SpaceShuttle.clamp(getprop("/fdm/jsbsim/propulsion/engine[6]/yaw-angle-rad") * 57.297 + 5.7, -9.9, 9.9)));
    
        p_dps_mnvr.current_apoapsis.updateText(sprintf("%3.0f",SpaceShuttle.clamp(getprop("/fdm/jsbsim/systems/orbital/apoapsis-km")/1.853, 000, 999)));
        p_dps_mnvr.current_periapsis.updateText(sprintf("%+5.0f",SpaceShuttle.clamp(getprop("/fdm/jsbsim/systems/orbital/periapsis-km")/1.853, -999, 999))); #Periapsis up to -999Nm
    
        
    
        var fwd_rcs_dump = getprop("/fdm/jsbsim/systems/rcs/fwd-dump-cmd");
        var fwd_rcs_dump_arm = getprop("/fdm/jsbsim/systems/rcs/fwd-dump-arm-cmd");
    
        if ((fwd_rcs_dump == 0) and (fwd_rcs_dump_arm == 0))
    	{
            p_dps_mnvr.fwd_rcs_off.updateText("*");
            p_dps_mnvr.fwd_rcs_arm.updateText("");
            p_dps_mnvr.fwd_rcs_dump.updateText("");
    	}
        else if ((fwd_rcs_dump_arm == 1) and (fwd_rcs_dump == 0))
    	{
            p_dps_mnvr.fwd_rcs_off.updateText("");
            p_dps_mnvr.fwd_rcs_arm.updateText("*");
            p_dps_mnvr.fwd_rcs_dump.updateText("");
    	}
        else
    	{
            p_dps_mnvr.fwd_rcs_off.updateText("");
            p_dps_mnvr.fwd_rcs_arm.updateText("*");
            p_dps_mnvr.fwd_rcs_dump.updateText("*");
    	}
    
        var control_mode = getprop("/fdm/jsbsim/systems/fcs/control-mode");
    
        if ((control_mode == 24) or (control_mode == 29))
    	{
            p_dps_mnvr.surf_drive_on.updateText("*");
            p_dps_mnvr.surf_drive_off.updateText("");
    	}
        else
    	{
            p_dps_mnvr.surf_drive_on.updateText("");
            p_dps_mnvr.surf_drive_off.updateText("*");
    	}
    

	var burn_mode = getprop("/fdm/jsbsim/systems/ap/oms-plan/burn-mode");

	if (burn_mode == 1)
		{
       		p_dps_mnvr.oms_both.updateText("*");
        	p_dps_mnvr.oms_l.updateText("");
        	p_dps_mnvr.oms_r.updateText("");
        	p_dps_mnvr.rcs_sel.updateText("");
		}
	else if (burn_mode == 2)
		{
       		p_dps_mnvr.oms_both.updateText("");
        	p_dps_mnvr.oms_l.updateText("*");
        	p_dps_mnvr.oms_r.updateText("");
        	p_dps_mnvr.rcs_sel.updateText("");
		}
	else if (burn_mode == 3)
		{
       		p_dps_mnvr.oms_both.updateText("");
        	p_dps_mnvr.oms_l.updateText("");
        	p_dps_mnvr.oms_r.updateText("*");
        	p_dps_mnvr.rcs_sel.updateText("");
		}
	else if (burn_mode == 4)
		{
       		p_dps_mnvr.oms_both.updateText("");
        	p_dps_mnvr.oms_l.updateText("");
        	p_dps_mnvr.oms_r.updateText("");
        	p_dps_mnvr.rcs_sel.updateText("*");
		}

    
    
        p_dps_mnvr.tv_roll.setText(sprintf("%03d",getprop("fdm/jsbsim/systems/ap/oms-plan/tv-roll")));
    
        p_dps_mnvr.p.setText(sprintf("%+4.1f",getprop("fdm/jsbsim/systems/ap/oms-plan/trim-pitch"))); # 4 letters (+0.0)
        p_dps_mnvr.ly.setText(sprintf("%+4.1f",getprop("fdm/jsbsim/systems/ap/oms-plan/trim-yaw-left")));
        p_dps_mnvr.ry.setText(sprintf("%+4.1f",getprop("fdm/jsbsim/systems/ap/oms-plan/trim-yaw-right")));
    
        p_dps_mnvr.wt.setText(sprintf("%6.0f",getprop("fdm/jsbsim/systems/ap/oms-plan/weight")));
    
        p_dps_mnvr.tig.setText(getprop("fdm/jsbsim/systems/ap/oms-plan/tig-string"));
    
        
    	
        #Geonormdeg to have modulo 2Pi values ( tested, it works ok) // No need for Yaw
    
        var tgt_roll = geo.normdeg(getprop("/fdm/jsbsim/systems/pointing/inertial/attitude/tgt-roll-deg"));
        var tgt_pitch = geo.normdeg(getprop("/fdm/jsbsim/systems/pointing/inertial/attitude/tgt-pitch-deg"));
        var tgt_yaw = getprop("/fdm/jsbsim/systems/pointing/inertial/attitude/tgt-yaw-deg");

        #var dvx = getprop("/fdm/jsbsim/systems/ap/oms-plan/dvx");
        #var dvy = getprop("/fdm/jsbsim/systems/ap/oms-plan/dvy");
        #var dvz = getprop("/fdm/jsbsim/systems/ap/oms-plan/dvz");

        #var H = getprop("/fdm/jsbsim/systems/ap/oms-plan/ht");
        #var thetaT = getprop("/fdm/jsbsim/systems/ap/oms-plan/theta-t");
        #var c1 = getprop("/fdm/jsbsim/systems/ap/oms-plan/c1");
        #var c2 = getprop("/fdm/jsbsim/systems/ap/oms-plan/c2");
        #var prplt = getprop("fdm/jsbsim/systems/ap/oms-plan/prplt");
    
        


        #Trigger for blanking PEG 7 if PEG 4 entered or vice versa ()
        #If PEG 4 converged in OPS1/3, datas for both peg 4 and 7 stay together

        var peg4_status = getprop("/fdm/jsbsim/systems/ap/oms-plan/peg4-entered");
        var major_mode = getprop("/fdm/jsbsim/systems/dps/major-mode");

        if (major_mode == 202) #OPS 2 no PEG 4
            {
            p_dps_mnvr.c1.updateText(""); #no PEG 4
            p_dps_mnvr.c2.updateText("");
            p_dps_mnvr.ht.updateText("");
            p_dps_mnvr.tt.updateText("");
            p_dps_mnvr.prplt.updateText("");

            p_dps_mnvr.dvx.updateText(sprintf("%+07.1f",SpaceShuttle.oms_burn_target.dvx_plan));
            p_dps_mnvr.dvy.updateText(sprintf("%+06.1f",SpaceShuttle.oms_burn_target.dvy_plan));
            p_dps_mnvr.dvz.updateText(sprintf("%+06.1f",SpaceShuttle.oms_burn_target.dvz_plan));


            #If burn solution comes from spec 34, LAMBERT is displayed in OPS 202 
        
            if (SpaceShuttle.lambert_manager.lambert_peg7 == 0) {p_dps_mnvr.ext_dv.updateText("EXT ΔV");}
            else {p_dps_mnvr.ext_dv.updateText("LAMBERT");}
            
            
            }
        else # OPS1/3 Peg 4 available
            {
            
            #No Ext DV/Lambert notifications outside OPS2
            p_dps_mnvr.ext_dv.updateText("");

            if (peg4_status == 1) #PEG 4 value entered
                {
                p_dps_mnvr.dvx.updateText(""); #no PEG 7 while peg4 is calculating
                p_dps_mnvr.dvy.updateText("");
                p_dps_mnvr.dvz.updateText("");

                p_dps_mnvr.c1.updateText(sprintf("%05d",SpaceShuttle.oms_burn_target.c1));
    	        p_dps_mnvr.c2.updateText(sprintf("%+7.4f",SpaceShuttle.oms_burn_target.c2));
    	        p_dps_mnvr.ht.updateText(sprintf("%07.3f",SpaceShuttle.oms_burn_target.ht));
    	        p_dps_mnvr.tt.updateText(sprintf("%07.3f",SpaceShuttle.oms_burn_target.thetaT));
    	        p_dps_mnvr.prplt.updateText(sprintf("%+06d",SpaceShuttle.oms_burn_target.prplt));
                }

            else if (oms_burn_target.peg4 == 1) #PEG 4 converged, both PEG 4 values and DV visible
                {
                p_dps_mnvr.dvx.updateText(sprintf("%+07.1f",SpaceShuttle.oms_burn_target.dvx_plan));
                p_dps_mnvr.dvy.updateText(sprintf("%+06.1f",SpaceShuttle.oms_burn_target.dvy_plan));
                p_dps_mnvr.dvz.updateText(sprintf("%+06.1f",SpaceShuttle.oms_burn_target.dvz_plan));

                p_dps_mnvr.c1.updateText(sprintf("%05d",SpaceShuttle.oms_burn_target.c1));
    	        p_dps_mnvr.c2.updateText(sprintf("%+7.4f",SpaceShuttle.oms_burn_target.c2));
    	        p_dps_mnvr.ht.updateText(sprintf("%07.3f",SpaceShuttle.oms_burn_target.ht));
    	        p_dps_mnvr.tt.updateText(sprintf("%07.3f",SpaceShuttle.oms_burn_target.thetaT));
    	        p_dps_mnvr.prplt.updateText(sprintf("%+06d",SpaceShuttle.oms_burn_target.prplt));
            
                }
            else if ((peg4_status == 0) and (oms_burn_target.peg4 == 0)) #PEG 4 not entered or not converged and PEG 7 entered manually
                {
                p_dps_mnvr.dvx.updateText(sprintf("%+07.1f",SpaceShuttle.oms_burn_target.dvx_plan));
                p_dps_mnvr.dvy.updateText(sprintf("%+06.1f",SpaceShuttle.oms_burn_target.dvy_plan));
                p_dps_mnvr.dvz.updateText(sprintf("%+06.1f",SpaceShuttle.oms_burn_target.dvz_plan));

                p_dps_mnvr.c1.updateText(""); #no PEG 4
                p_dps_mnvr.c2.updateText("");
                p_dps_mnvr.ht.updateText("");
                p_dps_mnvr.tt.updateText("");
                p_dps_mnvr.prplt.updateText("");
                }

            }



        #Trigger for blanking burn ATT and Velocity box, no TGT HA HP if no solution loaded
        #Flashing item 22 LOAD if not loaded and no burn occured

        var burn_plan = getprop("/fdm/jsbsim/systems/ap/oms-plan/burn-plan-available");
        var burn_accel = getprop("/fdm/jsbsim/systems/navigation/acc-int-flag");   # Reset to zero once mm is changed or load/cancel ( perfect to keep datas after a burn)

        var load_string = "";

        #Variables for VGO and DVOT (SpaceShuttle.oms_burn_target.vgo_x works but doest not update as a burn takes place)

        var dvgo_x = getprop("fdm/jsbsim/systems/ap/oms-plan/vgo-x");
        var dvgo_y = getprop("fdm/jsbsim/systems/ap/oms-plan/vgo-y");
        var dvgo_z = getprop("fdm/jsbsim/systems/ap/oms-plan/vgo-z");
        var dvgo_t = getprop("fdm/jsbsim/systems/ap/oms-plan/dvtot");
        

    
    
        if ((burn_plan == 0) and (burn_accel == 0)) #No burn occured while in the present mm // and Page reset after a burn
    	    {
            load_string = "LOAD";
            if (p_dps_mnvr.blink == 0) {p_dps_mnvr.blink = 1; load_string = "";}
            else {p_dps_mnvr.blink = 0;}
            #p_dps_mnvr.load.setText(load_string);

            p_dps_mnvr.burn_att_roll.setText("");
            p_dps_mnvr.burn_att_pitch.setText("");
            p_dps_mnvr.burn_att_yaw.setText("");

            p_dps_mnvr.dvtot.updateText("");
            p_dps_mnvr.tgo.updateText("");

            p_dps_mnvr.vgo_x.setText("");
            p_dps_mnvr.vgo_y.setText("");
            p_dps_mnvr.vgo_z.setText("");

            p_dps_mnvr.ha_tgt.updateText("");
            p_dps_mnvr.hp_tgt.updateText("");


            p_dps_mnvr.load.setText(load_string);
            }

        else #if ((burn_plan == 1) or (burn_accel == 1)) #Burned occured, datas stay until change of mm // OR burn target loaded
    	    {

            #Clamp function for Output only, that can exceed max allowed size on display ( Dvtot//TGO and Tgt Apsis)

            p_dps_mnvr.vgo_x.setText(sprintf("%+08.2f",SpaceShuttle.clamp(dvgo_x, -9999.99, 9999.99)));
            p_dps_mnvr.vgo_y.setText(sprintf("%+07.2f",SpaceShuttle.clamp(dvgo_y, -999.99, 999.99)));
            p_dps_mnvr.vgo_z.setText(sprintf("%+07.2f",SpaceShuttle.clamp(dvgo_z, -999.99, 999.99)));

            p_dps_mnvr.dvtot.updateText(sprintf("%6.1f",SpaceShuttle.clamp(dvgo_t, 0000.0, 9999.9)));
            p_dps_mnvr.tgo.updateText(getprop("/fdm/jsbsim/systems/ap/oms-plan/tgo-string"));

            p_dps_mnvr.burn_att_roll.setText(sprintf("%03d",tgt_roll));
            p_dps_mnvr.burn_att_pitch.setText(sprintf("%03d",tgt_pitch));
            p_dps_mnvr.burn_att_yaw.setText(sprintf("%03d",tgt_yaw));

            p_dps_mnvr.ha_tgt.updateText(sprintf("%3.0f",SpaceShuttle.clamp(getprop("/fdm/jsbsim/systems/ap/oms-plan/apoapsis-nm"), 000, 999)));
            p_dps_mnvr.hp_tgt.updateText(sprintf("%+5.0f",SpaceShuttle.clamp(getprop("/fdm/jsbsim/systems/ap/oms-plan/periapsis-nm"), -999, 999)));

            p_dps_mnvr.load.setText("LOAD"); # Steady LOAD once target loaded or burn finished ( no cancel)

            

            }
    

    


        var oms_mnvr_flag = getprop("/fdm/jsbsim/systems/ap/oms-mnvr-flag");
    
        var dap_text = "FREE";
        if (getprop("/fdm/jsbsim/systems/ap/orbital-dap-auto") == 1)
    	{dap_text = "AUTO";}
        else if(getprop("/fdm/jsbsim/systems/ap/orbital-dap-inertial") == 1)
    	{dap_text = "INRTL";}
        else if(getprop("/fdm/jsbsim/systems/ap/orbital-dap-lvlh") == 1)
    	{dap_text = "LVLH";}

        var oms_mnvr_text = "MNVR 27";

        if (oms_mnvr_flag == 1) 
		{
		oms_mnvr_text = "MNVR 27*";
		
		if (dap_text != "AUTO")
			{
			p_dps_mnvr.active_dap.setColor(0.8, 0.8, 0.4);
			}
		else
			{
			p_dps_mnvr.active_dap.setColor(dps_r, dps_g, dps_b);
			}

		}
    
    
        p_dps_mnvr.mnvr.updateText(oms_mnvr_text);

	if (SpaceShuttle.bfs_in_control == 0)
        	{p_dps_mnvr.active_dap.updateText(dap_text);}
	else
		{p_dps_mnvr.active_dap.updateText("");}



        var attitude_flag = getprop("/fdm/jsbsim/systems/ap/track/in-attitude");

	if ((oms_mnvr_flag == 1) and (dap_text == "AUTO") and (attitude_flag == 0))
		{
		var rate = getprop("/fdm/jsbsim/systems/ap/rot-rate-degps");
		var yaw_error = getprop("/fdm/jsbsim/systems/ap/track/yaw-error-deg");
		var pitch_error = getprop("/fdm/jsbsim/systems/ap/track/pitch-error-deg");
		var roll_error = getprop("/fdm/jsbsim/systems/ap/track/roll-error-deg");

		var tt_pitch_yaw = math.max(pitch_error, yaw_error)/rate;
		var tt_roll = math.abs(roll_error)/rate;

		var tta = SpaceShuttle.seconds_to_stringMS (tt_pitch_yaw + tt_roll);
		p_dps_mnvr.tta.setText(tta);
		}
	else
		{
		p_dps_mnvr.tta.setText("");
		}
    
    
        
    

        
        
    

        var exec_string = "";
    
        var MET = getprop("/sim/time/elapsed-sec") + getprop("/fdm/jsbsim/systems/timer/delta-MET");
    
        var exec_timer_flag = 0;
    
        if (SpaceShuttle.oms_burn_target.tig - MET < 15.0)
    	{
            exec_timer_flag = 1;
    	}
    
        if ((attitude_flag == 1) and (burn_plan == 1) and (exec_timer_flag == 1) )
    	{
            exec_string = "EXEC";
            var exec_cmd = getprop("/fdm/jsbsim/systems/ap/oms-plan/exec-cmd");
            if (exec_cmd == 0) # blink before ignition
    		{
                if (p_dps_mnvr.blink == 0) 
    			{p_dps_mnvr.blink = 1; exec_string = "";}
                else
    			{p_dps_mnvr.blink = 0;}
    		}
            else if (exec_cmd == 1) {exec_string = "";} #EXEC extiguinshed after exec keyboard pressed
    	}
    
        p_dps_mnvr.exec.setText(exec_string);
    
        var ops = getprop("/fdm/jsbsim/systems/dps/ops");

	var apoapsis_miles = getprop("/fdm/jsbsim/systems/orbital/apoapsis-km") * 0.539956803456;
	var periapsis_miles = getprop("/fdm/jsbsim/systems/orbital/periapsis-km") * 0.539956803456;

	if ((ops == 1) or (ops == 2) or (ops == 6))
        	{
		var tta = SpaceShuttle.time_to_apsis();

        	var tta_string = "TTP";
        	if (tta[0] == 2) {tta_string = "TTA";}

		var tta_time = "";

		if ((apoapsis_miles - periapsis_miles) < 5.0)	
			{tta_string = "TTC";}
		else
			{tta_time = SpaceShuttle.seconds_to_stringMS(tta[1]);}


        	p_dps_mnvr.ttapsis_text.setText(tta_string);
        	p_dps_mnvr.ttapsis.setText(tta_time);

		}

	else if (ops == 3)
		{
        	var tff_string = "TFF";
		
		var tff_time = "";

		if (periapsis_miles < 65.83)
			{
			var tff = SpaceShuttle.time_to_interface();
			if (tff > 0.0) 
				{tff_time = SpaceShuttle.seconds_to_stringMS(tff);}
			else
				{tff_time = "";}
			}
		
		p_dps_mnvr.ttapsis_text.setText(tff_string);
        	p_dps_mnvr.ttapsis.setText(tff_time);	

		var rei = getprop("/fdm/jsbsim/systems/ap/oms-plan/rei-nm");
		
		if (rei > 0.0)
			{
			p_dps_mnvr.rei.setText(sprintf("%4d", SpaceShuttle.clamp(rei, 0, 9999)));
			}
		else
			{
			p_dps_mnvr.rei.setText("");
			}

		}
	
    

    

    

    
         
    
    
        var gimbal_l_pri = getprop("/fdm/jsbsim/systems/oms-hardware/gimbal-left-pri-selected");
        var gimbal_l_sec = getprop("/fdm/jsbsim/systems/oms-hardware/gimbal-left-sec-selected");
        var gimbal_r_pri = getprop("/fdm/jsbsim/systems/oms-hardware/gimbal-right-pri-selected");
        var gimbal_r_sec = getprop("/fdm/jsbsim/systems/oms-hardware/gimbal-right-sec-selected");
    
        var gsym1 = ""; var gsym2 = ""; var gsym3 = "";
    
        if (gimbal_l_pri == 1) {gsym1 = "*";}
        else if (gimbal_l_sec == 1) {gsym2 = "*";}
        else {gsym3 = "*";}
    
        p_dps_mnvr.pri_l.updateText( gsym1);
        p_dps_mnvr.sec_l.updateText( gsym2);
        p_dps_mnvr.off_l.updateText( gsym3);
    
        gsym1 = ""; gsym2 = ""; gsym3 = "";
    
        if (gimbal_r_pri == 1) {gsym1 = "*";}
        else if (gimbal_r_sec == 1) {gsym2 = "*";}
        else {gsym3 = "*";}
    
        p_dps_mnvr.pri_r.updateText( gsym1);
        p_dps_mnvr.sec_r.updateText( gsym2);
        p_dps_mnvr.off_r.updateText( gsym3);
    
        var gimbal_check = getprop("/fdm/jsbsim/systems/oms-hardware/gimbal-chk-cmd");
    
        if (gimbal_check == 1) {gsym1 = "*";} else {gsym1 = "";}
    
        p_dps_mnvr.gmbl_ck.updateText( gsym1);

	p_dps_mnvr.abort_tgt.updateText(sprintf("%2d", getprop("/fdm/jsbsim/systems/abort/oms-abort-tgt-id")));
    }
    
    return p_dps_mnvr;
}
