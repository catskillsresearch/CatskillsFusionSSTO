#---------------------------------------
# SpaceShuttle PFD Page include:
#        Page: p_dps_electric
# Description: the electric system display (DISP 67)
#      Author: Thorsten Renk, 2016 // GinGin, 2020
#---------------------------------------

var PFD_addpage_p_dps_electric = func(device)
{
    var p_dps_electric = device.addPage("CRTElectric", "p_dps_electric");

    p_dps_electric.group = device.svg.getElementById("p_dps_electric");
    p_dps_electric.group.setColor(dps_r, dps_g, dps_b);
    
    p_dps_electric.volt_fc1 = device.svg.getElementById("p_dps_electric_volt_fc1");
    p_dps_electric.volt_fc2 = device.svg.getElementById("p_dps_electric_volt_fc2");
    p_dps_electric.volt_fc3 = device.svg.getElementById("p_dps_electric_volt_fc3");

    p_dps_electric.volt_mn1 = device.svg.getElementById("p_dps_electric_volt_mn1");
    p_dps_electric.volt_mn2 = device.svg.getElementById("p_dps_electric_volt_mn2");
    p_dps_electric.volt_mn3 = device.svg.getElementById("p_dps_electric_volt_mn3");

    p_dps_electric.volt_ess1 = device.svg.getElementById("p_dps_electric_volt_ess1");
    p_dps_electric.volt_ess2 = device.svg.getElementById("p_dps_electric_volt_ess2");
    p_dps_electric.volt_ess3 = device.svg.getElementById("p_dps_electric_volt_ess3");

    p_dps_electric.volt_pcaf1 = device.svg.getElementById("p_dps_electric_volt_pcaf1");
    p_dps_electric.volt_pcaf2 = device.svg.getElementById("p_dps_electric_volt_pcaf2");
    p_dps_electric.volt_pcaf3 = device.svg.getElementById("p_dps_electric_volt_pcaf3");

    p_dps_electric.volt_pcaa1 = device.svg.getElementById("p_dps_electric_volt_pcaa1");
    p_dps_electric.volt_pcaa2 = device.svg.getElementById("p_dps_electric_volt_pcaa2");
    p_dps_electric.volt_pcaa3 = device.svg.getElementById("p_dps_electric_volt_pcaa3");    

    p_dps_electric.volt_cntl1_1 = device.svg.getElementById("p_dps_electric_volt_cntl1_1");
    p_dps_electric.volt_cntl1_2 = device.svg.getElementById("p_dps_electric_volt_cntl1_2");
    p_dps_electric.volt_cntl1_3 = device.svg.getElementById("p_dps_electric_volt_cntl1_3");

    p_dps_electric.volt_cntl2_1 = device.svg.getElementById("p_dps_electric_volt_cntl2_1");
    p_dps_electric.volt_cntl2_2 = device.svg.getElementById("p_dps_electric_volt_cntl2_2");
    p_dps_electric.volt_cntl2_3 = device.svg.getElementById("p_dps_electric_volt_cntl2_3");

    p_dps_electric.volt_cntl3_1 = device.svg.getElementById("p_dps_electric_volt_cntl3_1");
    p_dps_electric.volt_cntl3_2 = device.svg.getElementById("p_dps_electric_volt_cntl3_2");
    p_dps_electric.volt_cntl3_3 = device.svg.getElementById("p_dps_electric_volt_cntl3_3");

    p_dps_electric.amps_fc_1 = device.svg.getElementById("p_dps_electric_amps_fc_1");
    p_dps_electric.amps_fc_2 = device.svg.getElementById("p_dps_electric_amps_fc_2");
    p_dps_electric.amps_fc_3 = device.svg.getElementById("p_dps_electric_amps_fc_3");

    p_dps_electric.amps_fwd_1 = device.svg.getElementById("p_dps_electric_amps_fwd_1");
    p_dps_electric.amps_fwd_2 = device.svg.getElementById("p_dps_electric_amps_fwd_2");
    p_dps_electric.amps_fwd_3 = device.svg.getElementById("p_dps_electric_amps_fwd_3");

    p_dps_electric.amps_mid_1 = device.svg.getElementById("p_dps_electric_amps_mid_1");
    p_dps_electric.amps_mid_2 = device.svg.getElementById("p_dps_electric_amps_mid_2");
    p_dps_electric.amps_mid_3 = device.svg.getElementById("p_dps_electric_amps_mid_3");

    p_dps_electric.amps_aft_1 = device.svg.getElementById("p_dps_electric_amps_aft_1");
    p_dps_electric.amps_aft_2 = device.svg.getElementById("p_dps_electric_amps_aft_2");
    p_dps_electric.amps_aft_3 = device.svg.getElementById("p_dps_electric_amps_aft_3");

    p_dps_electric.V_phiA_1 = device.svg.getElementById("p_dps_electric_V_phiA_1");
    p_dps_electric.V_phiB_1 = device.svg.getElementById("p_dps_electric_V_phiB_1");
    p_dps_electric.V_phiC_1 = device.svg.getElementById("p_dps_electric_V_phiC_1");

    p_dps_electric.V_phiA_2 = device.svg.getElementById("p_dps_electric_V_phiA_2");
    p_dps_electric.V_phiB_2 = device.svg.getElementById("p_dps_electric_V_phiB_2");
    p_dps_electric.V_phiC_2 = device.svg.getElementById("p_dps_electric_V_phiC_2");

    p_dps_electric.V_phiA_3 = device.svg.getElementById("p_dps_electric_V_phiA_3");
    p_dps_electric.V_phiB_3 = device.svg.getElementById("p_dps_electric_V_phiB_3");
    p_dps_electric.V_phiC_3 = device.svg.getElementById("p_dps_electric_V_phiC_3");

    p_dps_electric.amp_phiA_1 = device.svg.getElementById("p_dps_electric_amp_phiA_1");
    p_dps_electric.amp_phiB_1 = device.svg.getElementById("p_dps_electric_amp_phiB_1");
    p_dps_electric.amp_phiC_1 = device.svg.getElementById("p_dps_electric_amp_phiC_1");

    p_dps_electric.amp_phiA_2 = device.svg.getElementById("p_dps_electric_amp_phiA_2");
    p_dps_electric.amp_phiB_2 = device.svg.getElementById("p_dps_electric_amp_phiB_2");
    p_dps_electric.amp_phiC_2 = device.svg.getElementById("p_dps_electric_amp_phiC_2");

    p_dps_electric.amp_phiA_3 = device.svg.getElementById("p_dps_electric_amp_phiA_3");
    p_dps_electric.amp_phiB_3 = device.svg.getElementById("p_dps_electric_amp_phiB_3");
    p_dps_electric.amp_phiC_3 = device.svg.getElementById("p_dps_electric_amp_phiC_3");

    p_dps_electric.ovld_1 = device.svg.getElementById("p_dps_electric_ovld_1");
    p_dps_electric.ovld_2 = device.svg.getElementById("p_dps_electric_ovld_2");
    p_dps_electric.ovld_3 = device.svg.getElementById("p_dps_electric_ovld_3");

    p_dps_electric.ouv_1 = device.svg.getElementById("p_dps_electric_ouv_1");
    p_dps_electric.ouv_2 = device.svg.getElementById("p_dps_electric_ouv_2");
    p_dps_electric.ouv_3 = device.svg.getElementById("p_dps_electric_ouv_3");


    p_dps_electric.total_amps = device.svg.getElementById("p_dps_electric_total_amps");
    p_dps_electric.total_kW = device.svg.getElementById("p_dps_electric_total_kW");

    p_dps_electric.amps_pl_B = device.svg.getElementById("p_dps_electric_amps_pl_B");
    p_dps_electric.amps_pl_C = device.svg.getElementById("p_dps_electric_amps_pl_C");


	#Failure Arrow indicators // Yellow Color (Parameters that can reach their limits L or H //  valve state ↓↑)

	p_dps_electric.volt_fc1_arrow = device.svg.getElementById("p_dps_electric_volt_fc1_arrow");
    p_dps_electric.volt_fc2_arrow = device.svg.getElementById("p_dps_electric_volt_fc2_arrow");
    p_dps_electric.volt_fc3_arrow = device.svg.getElementById("p_dps_electric_volt_fc3_arrow");

	p_dps_electric.volt_mn1_arrow = device.svg.getElementById("p_dps_electric_volt_mn1_arrow");
    p_dps_electric.volt_mn2_arrow = device.svg.getElementById("p_dps_electric_volt_mn2_arrow");
    p_dps_electric.volt_mn3_arrow = device.svg.getElementById("p_dps_electric_volt_mn3_arrow");

    p_dps_electric.volt_ess1_arrow = device.svg.getElementById("p_dps_electric_volt_ess1_arrow");
    p_dps_electric.volt_ess2_arrow = device.svg.getElementById("p_dps_electric_volt_ess2_arrow");
    p_dps_electric.volt_ess3_arrow = device.svg.getElementById("p_dps_electric_volt_ess3_arrow");

    p_dps_electric.volt_pcaf1_arrow = device.svg.getElementById("p_dps_electric_volt_pcaf1_arrow");
    p_dps_electric.volt_pcaf2_arrow = device.svg.getElementById("p_dps_electric_volt_pcaf2_arrow");
    p_dps_electric.volt_pcaf3_arrow = device.svg.getElementById("p_dps_electric_volt_pcaf3_arrow");

    p_dps_electric.volt_pcaa1_arrow = device.svg.getElementById("p_dps_electric_volt_pcaa1_arrow");
    p_dps_electric.volt_pcaa2_arrow = device.svg.getElementById("p_dps_electric_volt_pcaa2_arrow");
    p_dps_electric.volt_pcaa3_arrow = device.svg.getElementById("p_dps_electric_volt_pcaa3_arrow");

	p_dps_electric.amps_fc_1_arrow = device.svg.getElementById("p_dps_electric_amps_fc_1_arrow");
    p_dps_electric.amps_fc_2_arrow = device.svg.getElementById("p_dps_electric_amps_fc_2_arrow");
    p_dps_electric.amps_fc_3_arrow = device.svg.getElementById("p_dps_electric_amps_fc_3_arrow");

    p_dps_electric.amps_fwd_1_arrow = device.svg.getElementById("p_dps_electric_amps_fwd_1_arrow");
    p_dps_electric.amps_fwd_2_arrow = device.svg.getElementById("p_dps_electric_amps_fwd_2_arrow");
    p_dps_electric.amps_fwd_3_arrow = device.svg.getElementById("p_dps_electric_amps_fwd_3_arrow");

    p_dps_electric.amps_mid_1_arrow = device.svg.getElementById("p_dps_electric_amps_mid_1_arrow");
    p_dps_electric.amps_mid_2_arrow = device.svg.getElementById("p_dps_electric_amps_mid_2_arrow");
    p_dps_electric.amps_mid_3_arrow = device.svg.getElementById("p_dps_electric_amps_mid_3_arrow");

    p_dps_electric.amps_aft_1_arrow = device.svg.getElementById("p_dps_electric_amps_aft_1_arrow");
    p_dps_electric.amps_aft_2_arrow = device.svg.getElementById("p_dps_electric_amps_aft_2_arrow");
    p_dps_electric.amps_aft_3_arrow = device.svg.getElementById("p_dps_electric_amps_aft_3_arrow");

	p_dps_electric.total_amps_arrow = device.svg.getElementById("p_dps_electric_total_amps_arrow");
    p_dps_electric.total_kW_arrow = device.svg.getElementById("p_dps_electric_total_kW_arrow");

	

	#Enable Update

	p_dps_electric.volt_fc1_arrow.enableUpdate();
    p_dps_electric.volt_fc2_arrow.enableUpdate();
    p_dps_electric.volt_fc3_arrow.enableUpdate();

	p_dps_electric.volt_mn1_arrow.enableUpdate();
    p_dps_electric.volt_mn2_arrow.enableUpdate();
    p_dps_electric.volt_mn3_arrow.enableUpdate();

    p_dps_electric.volt_ess1_arrow.enableUpdate();
    p_dps_electric.volt_ess2_arrow.enableUpdate();
    p_dps_electric.volt_ess3_arrow.enableUpdate();

    p_dps_electric.volt_pcaf1_arrow.enableUpdate();
    p_dps_electric.volt_pcaf2_arrow.enableUpdate();
    p_dps_electric.volt_pcaf3_arrow.enableUpdate();

    p_dps_electric.volt_pcaa1_arrow.enableUpdate();
    p_dps_electric.volt_pcaa2_arrow.enableUpdate();
    p_dps_electric.volt_pcaa3_arrow.enableUpdate();

	p_dps_electric.amps_fc_1_arrow.enableUpdate();
    p_dps_electric.amps_fc_2_arrow.enableUpdate();
    p_dps_electric.amps_fc_3_arrow.enableUpdate();

    p_dps_electric.amps_fwd_1_arrow.enableUpdate();
    p_dps_electric.amps_fwd_2_arrow.enableUpdate();
    p_dps_electric.amps_fwd_3_arrow.enableUpdate();

    p_dps_electric.amps_mid_1_arrow.enableUpdate();
    p_dps_electric.amps_mid_2_arrow.enableUpdate();
    p_dps_electric.amps_mid_3_arrow.enableUpdate();

    p_dps_electric.amps_aft_1_arrow.enableUpdate();
    p_dps_electric.amps_aft_2_arrow.enableUpdate();
    p_dps_electric.amps_aft_3_arrow.enableUpdate();

	p_dps_electric.total_amps_arrow.enableUpdate();
    p_dps_electric.total_kW_arrow.enableUpdate();

	#Sugroup indicators that are linked to one variable ( AC volts/amps // L or "")

	p_dps_electric.arrow_group_AC1_subgroup = device.svg.getElementById("p_dps_electric_arrow_group_AC1_subgroup");
	p_dps_electric.arrow_group_AC2_subgroup = device.svg.getElementById("p_dps_electric_arrow_group_AC2_subgroup");
	p_dps_electric.arrow_group_AC3_subgroup = device.svg.getElementById("p_dps_electric_arrow_group_AC3_subgroup");

	#All arrows in a group to have just one line for .setcolor

	p_dps_electric.arrow_group = device.svg.getElementById("p_dps_electric_arrow_group");
	p_dps_electric.arrow_group.setColor(1, 1, 0);




    p_dps_electric.ondisplay = func
    {
        device.DPS_menu_title.setText("                    ELECTRIC");
        device.MEDS_menu_title.setText("      DPS MENU");
    
        var major_mode = getprop("/fdm/jsbsim/systems/dps/major-mode-sm");
	var spec =  getprop("/fdm/jsbsim/systems/dps/spec-sm");
	var spec_string = assemble_spec_string(spec);
    
        var ops_string = major_mode~"1/"~spec_string~"/067";  

        device.DPS_menu_ops.setText(ops_string);

	# blank fields which are not yet implemented

	p_dps_electric.amps_pl_B.setText("  0.0");
	p_dps_electric.amps_pl_C.setText("  0.0");

    }
    
    p_dps_electric.update = func
    {

	var voltage_fc1 = getprop("/fdm/jsbsim/systems/electrical/fc/voltage");
	var voltage_fc2 = getprop("/fdm/jsbsim/systems/electrical/fc[1]/voltage");
	var voltage_fc3 = getprop("/fdm/jsbsim/systems/electrical/fc[2]/voltage");

	var bus_connector1 = getprop("/fdm/jsbsim/systems/electrical/fc/bus-connector-status");
	var bus_connector2 = getprop("/fdm/jsbsim/systems/electrical/fc[1]/bus-connector-status");
	var bus_connector3 = getprop("/fdm/jsbsim/systems/electrical/fc[2]/bus-connector-status");

	var power_usage1 = getprop("/fdm/jsbsim/systems/electrical/bus/power-demand-kW") * 1000.0;
	var power_usage2 = getprop("/fdm/jsbsim/systems/electrical/bus[1]/power-demand-kW") * 1000.0;
	var power_usage3 = getprop("/fdm/jsbsim/systems/electrical/bus[2]/power-demand-kW") * 1000.0;

	var voltage_mainA = getprop("/fdm/jsbsim/systems/electrical/bus/voltage");
	var voltage_mainB = getprop("/fdm/jsbsim/systems/electrical/bus[1]/voltage");
	var voltage_mainC = getprop("/fdm/jsbsim/systems/electrical/bus[2]/voltage");

	power_usage1 = SpaceShuttle.clamp(power_usage1, 0, 5000); #Watts
	power_usage2 = SpaceShuttle.clamp(power_usage2, 0, 5000);
	power_usage3 = SpaceShuttle.clamp(power_usage3, 0, 5000);

	var amps_fc1 = power_usage1/voltage_fc1 * bus_connector1;
	var amps_fc2 = power_usage2/voltage_fc2 * bus_connector2;
	var amps_fc3 = power_usage3/voltage_fc3 * bus_connector3;

	var amps_bus1 = power_usage1/voltage_mainA;
	var amps_bus2 = power_usage2/voltage_mainB;
	var amps_bus3 = power_usage3/voltage_mainC;

	#Clamp here of Amps to avoid to do it later ( 0/ 500 A in case of bus shortcut)
	#We do it later for fc amps to allow total amps to go to the limit (1500H) in case of dual shortcut in 2 different AC circuit

	#amps_fc1 = SpaceShuttle.clamp(amps_fc1, 0, 500);
	#amps_fc2 = SpaceShuttle.clamp(amps_fc2, 0, 500);
	#amps_fc3 = SpaceShuttle.clamp(amps_fc3, 0, 500);

	amps_bus1 = SpaceShuttle.clamp(amps_bus1, 0, 500);
	amps_bus2 = SpaceShuttle.clamp(amps_bus2, 0, 500);
	amps_bus3 = SpaceShuttle.clamp(amps_bus3, 0, 500);

	

	if (voltage_fc1 == 0.0) {amps_fc1 = 0.0;}
	if (voltage_fc2 == 0.0) {amps_fc2 = 0.0;}
	if (voltage_fc3 == 0.0) {amps_fc3 = 0.0;}

	if (voltage_mainA == 0.0) {amps_bus1 = 0.0;}
	if (voltage_mainB == 0.0) {amps_bus2 = 0.0;}
	if (voltage_mainC == 0.0) {amps_bus3 = 0.0;}
    
        p_dps_electric.volt_fc1.setText(sprintf("%4.1f", voltage_fc1));
        p_dps_electric.volt_fc2.setText(sprintf("%4.1f", voltage_fc2));
        p_dps_electric.volt_fc3.setText(sprintf("%4.1f", voltage_fc3));    


	var voltage_essential1 = getprop("/fdm/jsbsim/systems/electrical/ess/voltage");
	var voltage_essential2 = getprop("/fdm/jsbsim/systems/electrical/ess[1]/voltage");
	var voltage_essential3 = getprop("/fdm/jsbsim/systems/electrical/ess[2]/voltage");

        p_dps_electric.volt_mn1.setText(sprintf("%4.1f", voltage_mainA));
        p_dps_electric.volt_mn2.setText(sprintf("%4.1f", voltage_mainB));
        p_dps_electric.volt_mn3.setText(sprintf("%4.1f", voltage_mainC)); 

        p_dps_electric.volt_pcaf1.setText(sprintf("%4.1f", voltage_mainA * 0.99));
        p_dps_electric.volt_pcaf2.setText(sprintf("%4.1f", voltage_mainB * 0.99));
        p_dps_electric.volt_pcaf3.setText(sprintf("%4.1f", voltage_mainC * 0.99)); 

        p_dps_electric.volt_pcaa1.setText(sprintf("%4.1f", voltage_mainA * 0.993));
        p_dps_electric.volt_pcaa2.setText(sprintf("%4.1f", voltage_mainB * 0.993));
        p_dps_electric.volt_pcaa3.setText(sprintf("%4.1f", voltage_mainC * 0.993)); 

        p_dps_electric.volt_ess1.setText(sprintf("%4.1f", voltage_essential1));
        p_dps_electric.volt_ess2.setText(sprintf("%4.1f", voltage_essential2));
        p_dps_electric.volt_ess3.setText(sprintf("%4.1f", voltage_essential3));    

	p_dps_electric.volt_cntl1_1.setText(sprintf("%5.1f", voltage_essential1 * 0.991));
	p_dps_electric.volt_cntl1_2.setText(sprintf("%5.1f", voltage_essential2 * 0.991));
	p_dps_electric.volt_cntl1_3.setText(sprintf("%5.1f", voltage_essential3 * 0.991));

	p_dps_electric.volt_cntl2_1.setText(sprintf("%5.1f", voltage_essential1 * 0.991));
	p_dps_electric.volt_cntl2_2.setText(sprintf("%5.1f", voltage_essential2 * 0.991));
	p_dps_electric.volt_cntl2_3.setText(sprintf("%5.1f", voltage_essential3 * 0.991));

	p_dps_electric.volt_cntl3_1.setText(sprintf("%5.1f", voltage_essential1 * 0.991));
	p_dps_electric.volt_cntl3_2.setText(sprintf("%5.1f", voltage_essential2 * 0.991));
	p_dps_electric.volt_cntl3_3.setText(sprintf("%5.1f", voltage_essential3 * 0.991));

   	p_dps_electric.amps_fc_1.setText(sprintf("%3.0f", SpaceShuttle.clamp(amps_fc1, 0, 500)));
   	p_dps_electric.amps_fc_2.setText(sprintf("%3.0f", SpaceShuttle.clamp(amps_fc2, 0, 500)));
   	p_dps_electric.amps_fc_3.setText(sprintf("%3.0f", SpaceShuttle.clamp(amps_fc3, 0, 500)));

	p_dps_electric.amps_fwd_1.setText(sprintf("%3.0f", amps_bus1 * 0.5)); #Max 250
	p_dps_electric.amps_fwd_2.setText(sprintf("%3.0f", amps_bus2 * 0.5));
	p_dps_electric.amps_fwd_3.setText(sprintf("%3.0f", amps_bus3 * 0.5));

	p_dps_electric.amps_mid_1.setText(sprintf("%3.0f", amps_bus1 * 0.2)); #Max 100
	p_dps_electric.amps_mid_2.setText(sprintf("%3.0f", amps_bus2 * 0.2));
	p_dps_electric.amps_mid_3.setText(sprintf("%3.0f", amps_bus3 * 0.2));

	p_dps_electric.amps_aft_1.setText(sprintf("%+4.0f", amps_bus1 * 0.35)); #Max 175
	p_dps_electric.amps_aft_2.setText(sprintf("%+4.0f", amps_bus2 * 0.35));
	p_dps_electric.amps_aft_3.setText(sprintf("%+4.0f", amps_bus3 * 0.35));

	var voltage_ac1 = getprop("/fdm/jsbsim/systems/electrical/ac/voltage");
	var voltage_ac2 = getprop("/fdm/jsbsim/systems/electrical/ac[1]/voltage");
	var voltage_ac3 = getprop("/fdm/jsbsim/systems/electrical/ac[2]/voltage");

	var power_ac1 = getprop("/fdm/jsbsim/systems/electrical/ac/power-demand-kW");
	var power_ac2 = getprop("/fdm/jsbsim/systems/electrical/ac[1]/power-demand-kW");
	var power_ac3 = getprop("/fdm/jsbsim/systems/electrical/ac[2]/power-demand-kW");

	var amps_ac1 = power_ac1 * 1000.0 /voltage_ac1;
	var amps_ac2 = power_ac2 * 1000.0 /voltage_ac2;
	var amps_ac3 = power_ac3 * 1000.0 /voltage_ac3;

	if (voltage_ac1 == 0.0) {amps_ac1 = 0.0;}
	if (voltage_ac2 == 0.0) {amps_ac2 = 0.0;}
	if (voltage_ac3 == 0.0) {amps_ac3 = 0.0;}


    	p_dps_electric.V_phiA_1.setText(sprintf("%3.0f", voltage_ac1));
    	p_dps_electric.V_phiA_2.setText(sprintf("%3.0f", voltage_ac2));
    	p_dps_electric.V_phiA_3.setText(sprintf("%3.0f", voltage_ac3));

   	p_dps_electric.V_phiB_1.setText(sprintf("%3.0f", voltage_ac1));
    	p_dps_electric.V_phiB_2.setText(sprintf("%3.0f", voltage_ac2));
    	p_dps_electric.V_phiB_3.setText(sprintf("%3.0f", voltage_ac3));

   	p_dps_electric.V_phiC_1.setText(sprintf("%3.0f", voltage_ac1));
    	p_dps_electric.V_phiC_2.setText(sprintf("%3.0f", voltage_ac2));
    	p_dps_electric.V_phiC_3.setText(sprintf("%3.0f", voltage_ac3));

	p_dps_electric.amp_phiA_1.setText(sprintf("%4.1f", amps_ac1/3.));
	p_dps_electric.amp_phiA_2.setText(sprintf("%4.1f", amps_ac2/3.));
	p_dps_electric.amp_phiA_3.setText(sprintf("%4.1f", amps_ac3/3.));

	p_dps_electric.amp_phiB_1.setText(sprintf("%4.1f", amps_ac1/3.));
	p_dps_electric.amp_phiB_2.setText(sprintf("%4.1f", amps_ac2/3.));
	p_dps_electric.amp_phiB_3.setText(sprintf("%4.1f", amps_ac3/3.));

	p_dps_electric.amp_phiC_1.setText(sprintf("%4.1f", amps_ac1/3.));
	p_dps_electric.amp_phiC_2.setText(sprintf("%4.1f", amps_ac2/3.));
	p_dps_electric.amp_phiC_3.setText(sprintf("%4.1f", amps_ac3/3.));

	var string = "";
	if (power_ac1 > 7.0) {string = "OL";}
	p_dps_electric.ovld_1.setText(string);

	string = "";
	if (power_ac2 > 7.0) {string = "OL";}
	p_dps_electric.ovld_2.setText(string);

	string = "";
	if (power_ac3 > 7.0) {string = "OL";}
	p_dps_electric.ovld_3.setText(string);

	string = "";
	if (voltage_ac1 < 115.0) {string = "OU";}
	p_dps_electric.ouv_1.setText(string);

	string = "";
	if (voltage_ac2 < 115.0) {string = "OU";}
	p_dps_electric.ouv_2.setText(string);

	string = "";
	if (voltage_ac3 < 115.0) {string = "OU";}
	p_dps_electric.ouv_3.setText(string);


	#Total elec

	var total_power_kw = getprop("/fdm/jsbsim/systems/electrical/total-power-demand-kW");
	total_power_kw = SpaceShuttle.clamp(total_power_kw, 0, 60);

	var total_amps = amps_fc1 + amps_fc2 + amps_fc3;
	total_amps = SpaceShuttle.clamp(total_amps, 0, 1500);

	p_dps_electric.total_kW.setText(sprintf("%5.1f", total_power_kw)); 

	p_dps_electric.total_amps.setText(sprintf("%4.0f", total_amps));



	#SM realistic option with indicators

	if (SpaceShuttle.sm_simulation_detail_level == 1)
		{

		p_dps_electric.arrow_group.setVisible(1);

		#Fc L (0) // ↓ below 27V // ↑ above 32 V

		if (voltage_fc1 == 0) {p_dps_electric.volt_fc1_arrow.updateText("L");}
		else if (voltage_fc1 > 32) {p_dps_electric.volt_fc1_arrow.updateText("↑");}
		else if ((voltage_fc1 > 0) and (voltage_fc1 < 27.5))  {p_dps_electric.volt_fc1_arrow.updateText("↓");}
		else {p_dps_electric.volt_fc1_arrow.updateText("");}

		if (voltage_fc2 == 0) {p_dps_electric.volt_fc2_arrow.updateText("L");}
		else if ( voltage_fc2 > 32) {p_dps_electric.volt_fc2_arrow.updateText("↑");}
		else if ((voltage_fc2 > 0) and (voltage_fc2 < 27.5))  {p_dps_electric.volt_fc2_arrow.updateText("↓");}
		else {p_dps_electric.volt_fc2_arrow.updateText("");}

		if (voltage_fc3 == 0) {p_dps_electric.volt_fc3_arrow.updateText("L");}
		else if ( voltage_fc3 > 32) {p_dps_electric.volt_fc3_arrow.updateText("↑");}
		else if ((voltage_fc3 > 0) and (voltage_fc3 < 27.5))  {p_dps_electric.volt_fc3_arrow.updateText("↓");}
		else {p_dps_electric.volt_fc3_arrow.updateText("");}

		#Main bus//PCA L(0) // ↓ below 27V // ↑ above 32 V // PCA only L or H

		if (voltage_mainA == 0) {p_dps_electric.volt_mn1_arrow.updateText("L"); p_dps_electric.volt_pcaf1_arrow.updateText("L"); p_dps_electric.volt_pcaa1_arrow.updateText("L");}
		else if ((voltage_mainA > 0) and (voltage_mainA < 27)) {p_dps_electric.volt_mn1_arrow.updateText("↓");}
		else if (voltage_mainA > 32) {p_dps_electric.volt_mn1_arrow.updateText("↑");}
		else {p_dps_electric.volt_mn1_arrow.updateText(""); p_dps_electric.volt_pcaf1_arrow.updateText(""); p_dps_electric.volt_pcaa1_arrow.updateText("");} 

		if (voltage_mainB == 0) {p_dps_electric.volt_mn2_arrow.updateText("L"); p_dps_electric.volt_pcaf2_arrow.updateText("L"); p_dps_electric.volt_pcaa2_arrow.updateText("L");}
		else if ((voltage_mainB > 0) and (voltage_mainB < 27)) {p_dps_electric.volt_mn2_arrow.updateText("↓");}
		else if (voltage_mainB > 32) {p_dps_electric.volt_mn2_arrow.updateText("↑");}
		else {p_dps_electric.volt_mn2_arrow.updateText(""); p_dps_electric.volt_pcaf2_arrow.updateText(""); p_dps_electric.volt_pcaa2_arrow.updateText("");}

		if (voltage_mainC == 0) {p_dps_electric.volt_mn3_arrow.updateText("L"); p_dps_electric.volt_pcaf3_arrow.updateText("L"); p_dps_electric.volt_pcaa3_arrow.updateText("L");}
		else if ((voltage_mainC > 0) and (voltage_mainC < 27)) {p_dps_electric.volt_mn3_arrow.updateText("↓");}
		else if (voltage_mainC > 32) {p_dps_electric.volt_mn3_arrow.updateText("↑");}
		else {p_dps_electric.volt_mn3_arrow.updateText(""); p_dps_electric.volt_pcaf3_arrow.updateText(""); p_dps_electric.volt_pcaa3_arrow.updateText("");}


		#Ess bus ↓ below 28V

		if (voltage_essential1 < 28) {p_dps_electric.volt_ess1_arrow.updateText("↓");}
		else {p_dps_electric.volt_ess1_arrow.updateText("");}

		if (voltage_essential2 < 28) {p_dps_electric.volt_ess2_arrow.updateText("↓");}
		else {p_dps_electric.volt_ess2_arrow.updateText("");}

		if (voltage_essential3 < 28) {p_dps_electric.volt_ess3_arrow.updateText("↓");}
		else {p_dps_electric.volt_ess3_arrow.updateText("");}


		#Amps FC L(0) // H (500)

		if (amps_fc1 > 499) {p_dps_electric.amps_fc_1_arrow.updateText("H");}
		else if (amps_fc1 == 0) {p_dps_electric.amps_fc_1_arrow.updateText("L");}
		else {p_dps_electric.amps_fc_1_arrow.updateText("");}

		if (amps_fc2 > 499) {p_dps_electric.amps_fc_2_arrow.updateText("H");}
		else if (amps_fc2 == 0) {p_dps_electric.amps_fc_2_arrow.updateText("L");}
		else {p_dps_electric.amps_fc_2_arrow.updateText("");}

		if (amps_fc3 > 499) {p_dps_electric.amps_fc_3_arrow.updateText("H");}
		else if (amps_fc3 == 0) {p_dps_electric.amps_fc_3_arrow.updateText("L");}
		else {p_dps_electric.amps_fc_3_arrow.updateText("");}


		#AMPS FWD/MID/AFT L(0) // (500)

		if (amps_bus1 > 499)
			{
			p_dps_electric.amps_fwd_1_arrow.updateText("H");
			p_dps_electric.amps_mid_1_arrow.updateText("H");
			p_dps_electric.amps_aft_1_arrow.updateText("H");
			}
		else if (amps_bus1 == 0)
			{
			p_dps_electric.amps_fwd_1_arrow.updateText("L");
			p_dps_electric.amps_mid_1_arrow.updateText("L");
			p_dps_electric.amps_aft_1_arrow.updateText("L");
			}
		else
			{
			p_dps_electric.amps_fwd_1_arrow.updateText("");
			p_dps_electric.amps_mid_1_arrow.updateText("");
			p_dps_electric.amps_aft_1_arrow.updateText("");
			}



		if (amps_bus2 > 499)
			{
			p_dps_electric.amps_fwd_2_arrow.updateText("H");
			p_dps_electric.amps_mid_2_arrow.updateText("H");
			p_dps_electric.amps_aft_2_arrow.updateText("H");
			}
		else if (amps_bus2 == 0)
			{
			p_dps_electric.amps_fwd_2_arrow.updateText("L");
			p_dps_electric.amps_mid_2_arrow.updateText("L");
			p_dps_electric.amps_aft_2_arrow.updateText("L");
			}
		else
			{
			p_dps_electric.amps_fwd_2_arrow.updateText("");
			p_dps_electric.amps_mid_2_arrow.updateText("");
			p_dps_electric.amps_aft_2_arrow.updateText("");
			}



		if (amps_bus3 > 499)
			{
			p_dps_electric.amps_fwd_3_arrow.updateText("H");
			p_dps_electric.amps_mid_3_arrow.updateText("H");
			p_dps_electric.amps_aft_3_arrow.updateText("H");
			}
		else if (amps_bus3 == 0)
			{
			p_dps_electric.amps_fwd_3_arrow.updateText("L");
			p_dps_electric.amps_mid_3_arrow.updateText("L");
			p_dps_electric.amps_aft_3_arrow.updateText("L");
			}
		else
			{
			p_dps_electric.amps_fwd_3_arrow.updateText("");
			p_dps_electric.amps_mid_3_arrow.updateText("");
			p_dps_electric.amps_aft_3_arrow.updateText("");
			}


		#Total elec Amps (0//1500A) and power ( 0//60kW)

		if (total_power_kw > 59) {p_dps_electric.total_kW_arrow.updateText("H");}
		else if ((total_power_kw > 40) and (total_power_kw < 59)) {p_dps_electric.total_kW_arrow.updateText("↑");}
		else {p_dps_electric.total_kW_arrow.updateText("");}

		if (total_amps == 1500) {p_dps_electric.total_amps_arrow.updateText("H");}
		else if ((total_amps > 1000) and (total_amps < 1500)) {p_dps_electric.total_amps_arrow.updateText("↑");}
		else {p_dps_electric.total_amps_arrow.updateText("");}



		#Ac Volts/Amps L(0)

		if (voltage_ac1 == 0)
			{
			p_dps_electric.arrow_group_AC1_subgroup.setVisible(1);
			}
		else	
			{
			p_dps_electric.arrow_group_AC1_subgroup.setVisible(0);
			}

		if (voltage_ac2 == 0)
			{
			p_dps_electric.arrow_group_AC2_subgroup.setVisible(1);
			}
		else	
			{
			p_dps_electric.arrow_group_AC2_subgroup.setVisible(0);
			}

		if (voltage_ac3 == 0)
			{
			p_dps_electric.arrow_group_AC3_subgroup.setVisible(1);
			}
		else	
			{
			p_dps_electric.arrow_group_AC3_subgroup.setVisible(0);
			}
		}

	else {p_dps_electric.arrow_group.setVisible(0);}
		


		   


        device.update_common_DPS();
    }
    
    
    
    return p_dps_electric;
}
