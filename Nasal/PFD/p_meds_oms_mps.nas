#---------------------------------------
# SpaceShuttle PFD Page include:
#        Page: p_meds_oms_mps
# Description: the OMS/MPS MEDS page
#      Author: Gijs de Rooy, Thorsten Renk (2016), GinGin (2020)
#---------------------------------------

var PFD_addpage_p_meds_oms_mps = func(device)
{
    var p_meds_oms_mps = device.addPage("MEDSOmsMps", "p_meds_oms_mps");

    p_meds_oms_mps.He_Tk_left = device.svg.getElementById("p_meds_oms_mps_He_Tk_left"); 
    p_meds_oms_mps.He_Tk_center = device.svg.getElementById("p_meds_oms_mps_He_Tk_center"); 
    p_meds_oms_mps.He_Tk_right = device.svg.getElementById("p_meds_oms_mps_He_Tk_right"); 
    p_meds_oms_mps.He_Tk_pneu = device.svg.getElementById("p_meds_oms_mps_He_Tk_pneu"); 

    p_meds_oms_mps.He_Tk_left.enableUpdate();
    p_meds_oms_mps.He_Tk_center.enableUpdate();
    p_meds_oms_mps.He_Tk_right.enableUpdate();
    p_meds_oms_mps.He_Tk_pneu.enableUpdate();

    p_meds_oms_mps.He_reg_right = device.svg.getElementById("p_meds_oms_mps_He_reg_right"); 
    p_meds_oms_mps.He_reg_left = device.svg.getElementById("p_meds_oms_mps_He_reg_left"); 
    p_meds_oms_mps.He_reg_center = device.svg.getElementById("p_meds_oms_mps_He_reg_center"); 
    p_meds_oms_mps.He_reg_pneu = device.svg.getElementById("p_meds_oms_mps_He_reg_pneu"); 

    p_meds_oms_mps.He_reg_right.enableUpdate();
    p_meds_oms_mps.He_reg_left.enableUpdate();
    p_meds_oms_mps.He_reg_center.enableUpdate();
    p_meds_oms_mps.He_reg_pneu.enableUpdate();

    p_meds_oms_mps.Pc_right = device.svg.getElementById("p_meds_oms_mps_Pc_right"); 
    p_meds_oms_mps.Pc_left = device.svg.getElementById("p_meds_oms_mps_Pc_left"); 
    p_meds_oms_mps.Pc_center = device.svg.getElementById("p_meds_oms_mps_Pc_center"); 

    p_meds_oms_mps.Pc_right.enableUpdate();
    p_meds_oms_mps.Pc_left.enableUpdate();
    p_meds_oms_mps.Pc_center.enableUpdate();

    p_meds_oms_mps.LO2 = device.svg.getElementById("p_meds_oms_mps_LO2"); 
    p_meds_oms_mps.LH2 = device.svg.getElementById("p_meds_oms_mps_LH2"); 

    p_meds_oms_mps.LO2.enableUpdate();
    p_meds_oms_mps.LH2.enableUpdate();

    p_meds_oms_mps.N2_Tk_oleft = device.svg.getElementById("p_meds_oms_mps_N2_Tk_oleft"); 
    p_meds_oms_mps.N2_Tk_oright = device.svg.getElementById("p_meds_oms_mps_N2_Tk_oright"); 

    p_meds_oms_mps.N2_Tk_oleft.enableUpdate(); 
    p_meds_oms_mps.N2_Tk_oright.enableUpdate();

    p_meds_oms_mps.He_Tk_oleft = device.svg.getElementById("p_meds_oms_mps.He_Tk_oleft"); 
    p_meds_oms_mps.He_Tk_oright = device.svg.getElementById("p_meds_oms_mps.He_Tk_oright"); 

    p_meds_oms_mps.He_Tk_oleft.enableUpdate();
    p_meds_oms_mps.He_Tk_oright.enableUpdate();

    p_meds_oms_mps.Pc_oright = device.svg.getElementById("p_meds_oms_mps_Pc_oright"); 
    p_meds_oms_mps.Pc_oleft = device.svg.getElementById("p_meds_oms_mps_Pc_oleft"); 

    p_meds_oms_mps.Pc_oright.enableUpdate();
    p_meds_oms_mps.Pc_oleft.enableUpdate();

    p_meds_oms_mps.menu_item = device.svg.getElementById("MI_1"); 
    p_meds_oms_mps.menu_item_frame = device.svg.getElementById("MI_1_frame"); 
    


    p_meds_oms_mps.tape_TkP_left = device.svg.getElementById("p_meds_oms_mps_tape_TkP_left"); 
    p_meds_oms_mps.tape_TkP_right = device.svg.getElementById("p_meds_oms_mps_tape_TkP_right"); 
    p_meds_oms_mps.tape_TkP_center = device.svg.getElementById("p_meds_oms_mps_tape_TkP_center"); 
    p_meds_oms_mps.tape_TkP_pneu = device.svg.getElementById("p_meds_oms_mps_tape_TkP_pneu"); 

    p_meds_oms_mps.tape_regP_left = device.svg.getElementById("p_meds_oms_mps_tape_regP_left"); 
    p_meds_oms_mps.tape_regP_right = device.svg.getElementById("p_meds_oms_mps_tape_regP_right"); 
    p_meds_oms_mps.tape_regP_center = device.svg.getElementById("p_meds_oms_mps_tape_regP_center"); 
    p_meds_oms_mps.tape_regP_pneu = device.svg.getElementById("p_meds_oms_mps_tape_regP_pneu"); 


    p_meds_oms_mps.tape_Pc_left = device.svg.getElementById("p_meds_oms_mps_tape_Pc_left"); 
    p_meds_oms_mps.tape_Pc_right = device.svg.getElementById("p_meds_oms_mps_tape_Pc_right"); 
    p_meds_oms_mps.tape_Pc_center = device.svg.getElementById("p_meds_oms_mps_tape_Pc_center"); 

    p_meds_oms_mps.tape_Pc_oleft = device.svg.getElementById("p_meds_oms_mps_tape_Pc_oleft"); 
    p_meds_oms_mps.tape_Pc_oright = device.svg.getElementById("p_meds_oms_mps_tape_Pc_oright"); 

    p_meds_oms_mps.tape_LH2 = device.svg.getElementById("p_meds_oms_mps_tape_LH2"); 
    p_meds_oms_mps.tape_LO2 = device.svg.getElementById("p_meds_oms_mps_tape_LO2"); 

    p_meds_oms_mps.tape_HeTkP_oleft = device.svg.getElementById("p_meds_oms_mps_tape_HeTkP_oleft"); 
    p_meds_oms_mps.tape_HeTkP_oright = device.svg.getElementById("p_meds_oms_mps_tape_HeTkP_oright"); 

    p_meds_oms_mps.tape_N2TkP_oleft = device.svg.getElementById("p_meds_oms_mps_tape_N2TkP_oleft"); 
    p_meds_oms_mps.tape_N2TkP_oright = device.svg.getElementById("p_meds_oms_mps_tape_N2TkP_oright"); 

	p_meds_oms_mps.MPS_label = device.svg.getElementById("MPS_label"); 
	p_meds_oms_mps.OMS_label = device.svg.getElementById("OMS_label");


    p_meds_oms_mps.cp1 = device.svg.getElementById("p_meds_oms_mps_cp1"); 


	#SVG elements with different fonts (SSU B) and green color// OMS and MPS PC numbers

	p_meds_oms_mps.MPS_label.setFont(p_pfd_font_2);
	p_meds_oms_mps.OMS_label.setFont(p_pfd_font_2);
	p_meds_oms_mps.Pc_oleft.setFont(p_pfd_font_2);
	p_meds_oms_mps.Pc_oright.setFont(p_pfd_font_2);
	p_meds_oms_mps.Pc_right.setFont(p_pfd_font_2);
	p_meds_oms_mps.Pc_center.setFont(p_pfd_font_2);
	p_meds_oms_mps.Pc_left.setFont(p_pfd_font_2);

	p_meds_oms_mps.MPS_label.setColor(0,1,0);
	p_meds_oms_mps.OMS_label.setColor(0,1,0);



    p_meds_oms_mps.ondisplay = func
    {
    
        device.set_DPS_off();
        device.MEDS_menu_title.setText("    SUBSYSTEM MENU");
	p_meds_oms_mps.menu_item.setColor(1.0, 1.0, 1.0);
	p_meds_oms_mps.menu_item_frame.setColor(1.0, 1.0, 1.0);
	p_meds_oms_mps.OMS_label.setText("STAGE");
	p_meds_oms_mps.MPS_label.setText("ENGINE");
    

    }
    
    p_meds_oms_mps.update = func
    {
	# Grenadier Stage / engine — reuse OMS/MPS tape layout.
	var E = "/fdm/jsbsim/systems/grenadier/engine/";
	var C = "/fdm/jsbsim/systems/grenadier/charm/";
	var sig = getprop(E ~ "sigma"); if (sig == nil) sig = 1;
	var rec = getprop(E ~ "sigma-recommended"); if (rec == nil) rec = 1;
	var allw = getprop(E ~ "sigma-allowed"); if (allw == nil) allw = 0;
	var thr = getprop(E ~ "throttle"); if (thr == nil) thr = 0;
	var sealed = getprop(E ~ "inlet-sealed"); if (sealed == nil) sealed = 0;
	var water = getprop(E ~ "water-kg"); if (water == nil) water = 0;
	var thrust = getprop(E ~ "thrust-kn"); if (thrust == nil) thrust = 0;
	var busf = getprop(E ~ "bus-frac"); if (busf == nil) busf = 0;
	var pdraw = getprop(E ~ "power-draw-mw"); if (pdraw == nil) pdraw = 0;
	var plant = getprop(E ~ "plant-ok"); if (plant == nil) plant = 0;
	var stage_go = getprop(E ~ "stage-go"); if (stage_go == nil) stage_go = 0;
	var coupled = getprop(E ~ "coupled-ok"); if (coupled == nil) coupled = 0;
	var bus = getprop(C ~ "bus-mw"); if (bus == nil) bus = 0;
	var mode = getprop(C ~ "mode"); if (mode == nil) mode = "OFF";

	var water_frac = water / 44000.0;
	if (water_frac > 1.0) water_frac = 1.0;
	var peak = 400.0;
	if (sig == 2) peak = 800.0;
	if (sig == 3) peak = 1200.0;
	var thrust_frac = 0.0;
	if (peak > 1) thrust_frac = thrust / peak;
	if (thrust_frac > 1.0) thrust_frac = 1.0;

	# Left OMS-like column: stage cmd / allowed / recommended
	p_meds_oms_mps.He_Tk_oleft.updateText(sprintf("%04d", sig * 1000));
	p_meds_oms_mps.He_Tk_oright.updateText(sprintf("%04d", allw * 1000));
	p_meds_oms_mps.N2_Tk_oleft.updateText(sprintf("%04d", rec * 1000));
	p_meds_oms_mps.N2_Tk_oright.updateText(sprintf("%04d", sealed * 1000));
	p_meds_oms_mps.tape_HeTkP_oleft.setScale(1.0, sig / 3.0);
	p_meds_oms_mps.tape_HeTkP_oleft.setTranslation(0.0, (1.0 - sig / 3.0) * (49.5 + 175.6));
	p_meds_oms_mps.tape_HeTkP_oright.setScale(1.0, allw / 3.0);
	p_meds_oms_mps.tape_HeTkP_oright.setTranslation(0.0, (1.0 - allw / 3.0) * (49.5 + 175.6));
	p_meds_oms_mps.tape_N2TkP_oleft.setScale(1.0, rec / 3.0);
	p_meds_oms_mps.tape_N2TkP_oleft.setTranslation(0.0, (1.0 - rec / 3.0) * (49.5 + 270.8));
	p_meds_oms_mps.tape_N2TkP_oright.setScale(1.0, sealed);
	p_meds_oms_mps.tape_N2TkP_oright.setTranslation(0.0, (1.0 - sealed) * (49.5 + 270.8));
	p_meds_oms_mps.tape_HeTkP_oleft.setColorFill(0.0, 1.0, 0.0);
	p_meds_oms_mps.tape_HeTkP_oright.setColorFill(0.0, 1.0, 0.0);
	p_meds_oms_mps.tape_N2TkP_oleft.setColorFill(0.0, 1.0, 0.0);
	if (sealed) {p_meds_oms_mps.tape_N2TkP_oright.setColorFill(0.0, 1.0, 0.0);} else {p_meds_oms_mps.tape_N2TkP_oright.setColorFill(1.0, 0.0, 0.0);}

	# Stage "Pc" OMS side = throttle / plant-ok
	p_meds_oms_mps.Pc_oleft.updateText(sprintf("%03d", thr * 100.0));
	p_meds_oms_mps.Pc_oright.updateText(sprintf("%03d", plant * 100.0));
	p_meds_oms_mps.tape_Pc_oleft.setScale(1.0, thr);
	p_meds_oms_mps.tape_Pc_oleft.setTranslation(0.0, (1.0 - thr) * (80.4 + 366));
	p_meds_oms_mps.tape_Pc_oright.setScale(1.0, plant);
	p_meds_oms_mps.tape_Pc_oright.setTranslation(0.0, (1.0 - plant) * (80.4 + 366));
	p_meds_oms_mps.tape_Pc_oleft.setColorFill(1.0, 1.0, 1.0);
	if (plant) {p_meds_oms_mps.tape_Pc_oright.setColorFill(1.0, 1.0, 1.0);} else {p_meds_oms_mps.tape_Pc_oright.setColorFill(1.0, 0.0, 0.0);}

	# MPS-like He tanks: water frac, bus MW, thrust frac, bus-frac
	p_meds_oms_mps.He_Tk_left.updateText(sprintf("%04d", water_frac * 1000));
	p_meds_oms_mps.He_Tk_center.updateText(sprintf("%04d", bus));
	p_meds_oms_mps.He_Tk_right.updateText(sprintf("%04d", thrust));
	p_meds_oms_mps.He_Tk_pneu.updateText(sprintf("%04d", busf * 1000));
	p_meds_oms_mps.tape_TkP_left.setScale(1.0, water_frac);
	p_meds_oms_mps.tape_TkP_left.setTranslation(0.0, (1.0 - water_frac) * (49.4 + 175));
	p_meds_oms_mps.tape_TkP_center.setScale(1.0, bus / 1000.0);
	p_meds_oms_mps.tape_TkP_center.setTranslation(0.0, (1.0 - bus / 1000.0) * (49.4 + 175));
	p_meds_oms_mps.tape_TkP_right.setScale(1.0, thrust_frac);
	p_meds_oms_mps.tape_TkP_right.setTranslation(0.0, (1.0 - thrust_frac) * (49.4 + 175));
	p_meds_oms_mps.tape_TkP_pneu.setScale(1.0, busf);
	p_meds_oms_mps.tape_TkP_pneu.setTranslation(0.0, (1.0 - busf) * (49.4 + 175));
	p_meds_oms_mps.tape_TkP_left.setColorFill(0.0, 1.0, 0.0);
	p_meds_oms_mps.tape_TkP_center.setColorFill(0.0, 1.0, 0.0);
	p_meds_oms_mps.tape_TkP_right.setColorFill(0.0, 1.0, 0.0);
	p_meds_oms_mps.tape_TkP_pneu.setColorFill(0.0, 1.0, 0.0);

	# Reg tapes: stage-go / coupled / power-draw / mode-index proxy
	var midx = getprop(C ~ "mode-index"); if (midx == nil) midx = 0;
	p_meds_oms_mps.He_reg_left.updateText(sprintf("%04d", stage_go * 1000));
	p_meds_oms_mps.He_reg_center.updateText(sprintf("%04d", coupled * 1000));
	p_meds_oms_mps.He_reg_right.updateText(sprintf("%04d", pdraw));
	p_meds_oms_mps.He_reg_pneu.updateText(sprintf("%04d", midx * 200));
	p_meds_oms_mps.tape_regP_left.setScale(1.0, stage_go);
	p_meds_oms_mps.tape_regP_left.setTranslation(0.0, (1.0 - stage_go) * (49.4 + 270.8));
	p_meds_oms_mps.tape_regP_center.setScale(1.0, coupled);
	p_meds_oms_mps.tape_regP_center.setTranslation(0.0, (1.0 - coupled) * (49.4 + 270.8));
	p_meds_oms_mps.tape_regP_right.setScale(1.0, pdraw / 1000.0);
	p_meds_oms_mps.tape_regP_right.setTranslation(0.0, (1.0 - pdraw / 1000.0) * (49.4 + 270.8));
	p_meds_oms_mps.tape_regP_pneu.setScale(1.0, midx / 5.0);
	p_meds_oms_mps.tape_regP_pneu.setTranslation(0.0, (1.0 - midx / 5.0) * (49.4 + 270.8));

	# Main Pc L/C/R = Stage 1/2/3 active fraction
	var s1 = 0.0; var s2 = 0.0; var s3 = 0.0;
	if (sig == 1) s1 = thr;
	if (sig == 2) s2 = thr;
	if (sig == 3) s3 = thr;
	p_meds_oms_mps.Pc_left.updateText(sprintf("%03d", s1 * 100));
	p_meds_oms_mps.Pc_center.updateText(sprintf("%03d", s2 * 100));
	p_meds_oms_mps.Pc_right.updateText(sprintf("%03d", s3 * 100));
	p_meds_oms_mps.tape_Pc_left.setScale(1.0, s1);
	p_meds_oms_mps.tape_Pc_left.setTranslation(0.0, (1.0 - s1) * (82.5 + 364.8));
	p_meds_oms_mps.tape_Pc_center.setScale(1.0, s2);
	p_meds_oms_mps.tape_Pc_center.setTranslation(0.0, (1.0 - s2) * (82.5 + 364.8));
	p_meds_oms_mps.tape_Pc_right.setScale(1.0, s3);
	p_meds_oms_mps.tape_Pc_right.setTranslation(0.0, (1.0 - s3) * (82.5 + 364.8));
	p_meds_oms_mps.tape_Pc_left.setColorFill(1.0, 1.0, 1.0);
	p_meds_oms_mps.tape_Pc_center.setColorFill(1.0, 1.0, 1.0);
	p_meds_oms_mps.tape_Pc_right.setColorFill(1.0, 1.0, 1.0);

	# LO2/LH2 manifolds → water remaining % and inlet seal code
	p_meds_oms_mps.LO2.updateText(sprintf("%03d", water_frac * 100));
	p_meds_oms_mps.LH2.updateText(sprintf("%03d", sealed * 100));
	p_meds_oms_mps.tape_LO2.setScale(1.0, water_frac);
	p_meds_oms_mps.tape_LO2.setTranslation(0.0, (1.0 - water_frac) * (49.0 + 384.0));
	p_meds_oms_mps.tape_LH2.setScale(1.0, sealed);
	p_meds_oms_mps.tape_LH2.setTranslation(0.0, (1.0 - sealed) * (49.0 + 384.0));

    }

    p_meds_oms_mps.offdisplay = func
    {
    
        p_meds_oms_mps.menu_item.setColor(meds_r, meds_g, meds_b);
	p_meds_oms_mps.menu_item_frame.setColor(meds_r, meds_g, meds_b);
    }
    
    
    
    return p_meds_oms_mps;
}
