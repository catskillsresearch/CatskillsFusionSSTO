#---------------------------------------
# SpaceShuttle PFD Page include:
#        Page: p_dps_env
# Description: the SM environemnt CRT page
#      Author: Thorsten Renk, 2016 // GinGin, 2020
#---------------------------------------

var PFD_addpage_p_dps_env = func(device)
{
    var p_dps_env = device.addPage("CRTEnv", "p_dps_env");

    p_dps_env.group = device.svg.getElementById("p_dps_env");
    p_dps_env.group.setColor(dps_r, dps_g, dps_b);
    

    p_dps_env.avbay_temp1 = device.svg.getElementById("p_dps_env_avbay_temp1");
    p_dps_env.avbay_temp2 = device.svg.getElementById("p_dps_env_avbay_temp2");
    p_dps_env.avbay_temp3 = device.svg.getElementById("p_dps_env_avbay_temp3");    

    p_dps_env.avbay_fan_dp1 = device.svg.getElementById("p_dps_env_avbay_fan_dp1");
    p_dps_env.avbay_fan_dp2 = device.svg.getElementById("p_dps_env_avbay_fan_dp2");
    p_dps_env.avbay_fan_dp3 = device.svg.getElementById("p_dps_env_avbay_fan_dp3");

    p_dps_env.imu_fan_A = device.svg.getElementById("p_dps_env_imu_fan_A");
    p_dps_env.imu_fan_B = device.svg.getElementById("p_dps_env_imu_fan_B");
    p_dps_env.imu_fan_C = device.svg.getElementById("p_dps_env_imu_fan_C");

    p_dps_env.imu_fan_dP = device.svg.getElementById("p_dps_env_imu_fan_dP");
    p_dps_env.cabin_fan_dp = device.svg.getElementById("p_dps_env_cabin_fan_dp");


    p_dps_env.o2_flow1 = device.svg.getElementById("p_dps_env_o2_flow1");
    p_dps_env.o2_flow2 = device.svg.getElementById("p_dps_env_o2_flow2");

    p_dps_env.o2_regp1 = device.svg.getElementById("p_dps_env_o2_regp1");
    p_dps_env.o2_regp2 = device.svg.getElementById("p_dps_env_o2_regp2");

    p_dps_env.emer_o2_reg_p = device.svg.getElementById("p_dps_env_emer_o2_reg_p");
    p_dps_env.emer_ppco2 = device.svg.getElementById("p_dps_env_ppco2");


    p_dps_env.n2_flow1 = device.svg.getElementById("p_dps_env_n2_flow1");
    p_dps_env.n2_flow2 = device.svg.getElementById("p_dps_env_n2_flow2");

    p_dps_env.n2_qty1 = device.svg.getElementById("p_dps_env_n2_qty1");
    p_dps_env.n2_qty2 = device.svg.getElementById("p_dps_env_n2_qty2");

    p_dps_env.n2_regp1 = device.svg.getElementById("p_dps_env_n2_reg_p1");
    p_dps_env.n2_regp2 = device.svg.getElementById("p_dps_env_n2_reg_p2");

    p_dps_env.h2o_tk_n2_1 = device.svg.getElementById("p_dps_env_h2o_tk_n2_1");
    p_dps_env.h2o_tk_n2_2 = device.svg.getElementById("p_dps_env_h2o_tk_n2_2");

    p_dps_env.o2n2_cntl_vlv1 = device.svg.getElementById("p_dps_env_o2n2_cntl_vlv1");
    p_dps_env.o2n2_cntl_vlv2 = device.svg.getElementById("p_dps_env_o2n2_cntl_vlv2");

    p_dps_env.ppo2a = device.svg.getElementById("p_dps_env_ppo2a");
    p_dps_env.ppo2b = device.svg.getElementById("p_dps_env_ppo2b");
    p_dps_env.ppo2c = device.svg.getElementById("p_dps_env_ppo2c");

    p_dps_env.cabin_press = device.svg.getElementById("p_dps_env_cabin_press");
    p_dps_env.cabin_airlk_p = device.svg.getElementById("p_dps_env_cabin_airlk_p");
    p_dps_env.cabin_dpdT = device.svg.getElementById("p_dps_env_cabin_dpdT");


    p_dps_env.cabin_t = device.svg.getElementById("p_dps_env_cabin_t");
    p_dps_env.cabin_hx_out_t = device.svg.getElementById("p_dps_env_cabin_hx_out_t");

    p_dps_env.supply_h2o_qty_a = device.svg.getElementById("p_dps_env_supply_h2o_qty_a");
    p_dps_env.supply_h2o_qty_b = device.svg.getElementById("p_dps_env_supply_h2o_qty_b");
    p_dps_env.supply_h2o_qty_c = device.svg.getElementById("p_dps_env_supply_h2o_qty_c");
    p_dps_env.supply_h2o_qty_d = device.svg.getElementById("p_dps_env_supply_h2o_qty_d");

    p_dps_env.supply_h2o_press = device.svg.getElementById("p_dps_env_supply_h2o_press");
    p_dps_env.supply_dmp_ln_t = device.svg.getElementById("p_dps_env_supply_h2o_dmp_ln_t");
    p_dps_env.supply_h2o_noz_t_a = device.svg.getElementById("p_dps_env_supply_h2o_noz_t_a");
    p_dps_env.supply_h2o_noz_t_b = device.svg.getElementById("p_dps_env_supply_h2o_noz_t_b");

    p_dps_env.waste_h2o_qty = device.svg.getElementById("p_dps_env_waste_h2o_qty");
    p_dps_env.waste_h2o_press = device.svg.getElementById("p_dps_env_waste_h2o_press");
    p_dps_env.waste_h2o_dmp_ln_t = device.svg.getElementById("p_dps_env_waste_h2o_dmp_ln_t");
    p_dps_env.waste_h2o_noz_t_A = device.svg.getElementById("p_dps_env_waste_h2o_noz_t_A");
    p_dps_env.waste_h2o_noz_t_B = device.svg.getElementById("p_dps_env_waste_h2o_noz_t_B");
    p_dps_env.waste_h2o_vac_vt_noz_t = device.svg.getElementById("p_dps_env_waste_h2o_vac_vt_noz_t");

    p_dps_env.humid_sep_A = device.svg.getElementById("p_dps_env_humid_sep_A");
    p_dps_env.humid_sep_B = device.svg.getElementById("p_dps_env_humid_sep_B");

    p_dps_env.co2_cntlr_1 = device.svg.getElementById("p_dps_env_co2_cntlr_1");
    p_dps_env.co2_cntlr_2 = device.svg.getElementById("p_dps_env_co2_cntlr_2");
    p_dps_env.co2_filter_dp = device.svg.getElementById("p_dps_env_co2_filter_dp");
    p_dps_env.co2_ppco2 = device.svg.getElementById("p_dps_env_co2_ppco2");
    p_dps_env.co2_temp = device.svg.getElementById("p_dps_env_co2_temp");
    p_dps_env.co2_bedA_press_1 = device.svg.getElementById("p_dps_env_co2_bedA_press_1");
    p_dps_env.co2_bedA_press_2 = device.svg.getElementById("p_dps_env_co2_bedA_press_2");
    p_dps_env.co2_bedB_press_1 = device.svg.getElementById("p_dps_env_co2_bedB_press_1");
    p_dps_env.co2_bedB_press_2 = device.svg.getElementById("p_dps_env_co2_bedB_press_2");
    p_dps_env.co2_bed_dp_1 = device.svg.getElementById("p_dps_env_co2_bed_dp_1");
    p_dps_env.co2_bed_dp_2 = device.svg.getElementById("p_dps_env_co2_bed_dp_2");
    p_dps_env.vac_press = device.svg.getElementById("p_dps_env_vac_press");


	#Failure Arrow indicators // Yellow Color (Parameters that can reach their limits L or H //  valve state ↓↑)


	p_dps_env.avbay_temp1_arrow = device.svg.getElementById("p_dps_env_avbay_temp1_arrow");
    p_dps_env.avbay_temp2_arrow = device.svg.getElementById("p_dps_env_avbay_temp2_arrow");
    p_dps_env.avbay_temp3_arrow = device.svg.getElementById("p_dps_env_avbay_temp3_arrow");    

    p_dps_env.avbay_fan_dp1_arrow = device.svg.getElementById("p_dps_env_avbay_fan_dp1_arrow");
    p_dps_env.avbay_fan_dp2_arrow = device.svg.getElementById("p_dps_env_avbay_fan_dp2_arrow");
    p_dps_env.avbay_fan_dp3_arrow = device.svg.getElementById("p_dps_env_avbay_fan_dp3_arrow");

    p_dps_env.imu_fan_A_arrow = device.svg.getElementById("p_dps_env_imu_fan_A_arrow");
    p_dps_env.imu_fan_B_arrow = device.svg.getElementById("p_dps_env_imu_fan_B_arrow");
    p_dps_env.imu_fan_C_arrow = device.svg.getElementById("p_dps_env_imu_fan_C_arrow");

    p_dps_env.imu_fan_dP_arrow = device.svg.getElementById("p_dps_env_imu_fan_dP_arrow");
    p_dps_env.cabin_fan_dp_arrow = device.svg.getElementById("p_dps_env_cabin_fan_dp_arrow");

	p_dps_env.o2_flow1_arrow = device.svg.getElementById("p_dps_env_o2_flow1_arrow");
    p_dps_env.o2_flow2_arrow = device.svg.getElementById("p_dps_env_o2_flow2_arrow");

    p_dps_env.o2_regp1_arrow = device.svg.getElementById("p_dps_env_o2_regp1_arrow");
    p_dps_env.o2_regp2_arrow = device.svg.getElementById("p_dps_env_o2_regp2_arrow");

    p_dps_env.emer_o2_reg_p_arrow = device.svg.getElementById("p_dps_env_emer_o2_reg_p_arrow");

	p_dps_env.n2_flow1_arrow = device.svg.getElementById("p_dps_env_n2_flow1_arrow");
    p_dps_env.n2_flow2_arrow = device.svg.getElementById("p_dps_env_n2_flow2_arrow");

    p_dps_env.n2_regp1_arrow = device.svg.getElementById("p_dps_env_n2_reg_p1_arrow");
    p_dps_env.n2_regp2_arrow = device.svg.getElementById("p_dps_env_n2_reg_p2_arrow");

    p_dps_env.h2o_tk_n2_1_arrow = device.svg.getElementById("p_dps_env_h2o_tk_n2_1_arrow");
    p_dps_env.h2o_tk_n2_2_arrow = device.svg.getElementById("p_dps_env_h2o_tk_n2_2_arrow");

	p_dps_env.ppo2a_arrow = device.svg.getElementById("p_dps_env_ppo2a_arrow");
    p_dps_env.ppo2b_arrow = device.svg.getElementById("p_dps_env_ppo2b_arrow");
    p_dps_env.ppo2c_arrow = device.svg.getElementById("p_dps_env_ppo2c_arrow");

    p_dps_env.cabin_press_arrow = device.svg.getElementById("p_dps_env_cabin_press_arrow");
    p_dps_env.cabin_airlk_p_arrow = device.svg.getElementById("p_dps_env_cabin_airlk_p_arrow");
    p_dps_env.cabin_dpdT_arrow = device.svg.getElementById("p_dps_env_cabin_dpdT_arrow");

	p_dps_env.supply_h2o_press_arrow = device.svg.getElementById("p_dps_env_supply_h2o_press_arrow");
	p_dps_env.waste_h2o_press_arrow = device.svg.getElementById("p_dps_env_waste_h2o_press_arrow");

	#Indicators enableUpdate

	p_dps_env.avbay_temp1_arrow.enableUpdate();
    p_dps_env.avbay_temp2_arrow.enableUpdate();
    p_dps_env.avbay_temp3_arrow.enableUpdate();    

    p_dps_env.avbay_fan_dp1_arrow.enableUpdate();
    p_dps_env.avbay_fan_dp2_arrow.enableUpdate();
    p_dps_env.avbay_fan_dp3_arrow.enableUpdate();

    p_dps_env.imu_fan_A_arrow.enableUpdate();
    p_dps_env.imu_fan_B_arrow.enableUpdate();
    p_dps_env.imu_fan_C_arrow.enableUpdate();

    p_dps_env.imu_fan_dP_arrow.enableUpdate();
    p_dps_env.cabin_fan_dp_arrow.enableUpdate();

	p_dps_env.o2_flow1_arrow.enableUpdate();
    p_dps_env.o2_flow2_arrow.enableUpdate();

    p_dps_env.o2_regp1_arrow.enableUpdate();
    p_dps_env.o2_regp2_arrow.enableUpdate();
    p_dps_env.emer_o2_reg_p_arrow.enableUpdate();

	p_dps_env.n2_flow1_arrow.enableUpdate();
    p_dps_env.n2_flow2_arrow.enableUpdate();

    p_dps_env.n2_regp1_arrow.enableUpdate();
    p_dps_env.n2_regp2_arrow.enableUpdate();

    p_dps_env.h2o_tk_n2_1_arrow.enableUpdate();
    p_dps_env.h2o_tk_n2_2_arrow.enableUpdate();

	p_dps_env.ppo2a_arrow.enableUpdate();
    p_dps_env.ppo2b_arrow.enableUpdate();
    p_dps_env.ppo2c_arrow.enableUpdate();

    p_dps_env.cabin_press_arrow.enableUpdate();
    p_dps_env.cabin_airlk_p_arrow.enableUpdate();
    p_dps_env.cabin_dpdT_arrow.enableUpdate();

	p_dps_env.supply_h2o_press_arrow.enableUpdate();
	p_dps_env.waste_h2o_press_arrow.enableUpdate();


	#All arrows in a group to have just one line for setcolor

	p_dps_env.arrow_group = device.svg.getElementById("p_dps_env_arrow_group");
	p_dps_env.arrow_group.setColor(1, 1, 0);



    p_dps_env.ondisplay = func
    {
        device.DPS_menu_title.setText("                  ENVIRONMENT");
        device.MEDS_menu_title.setText("      DPS MENU");
    
        var major_mode = getprop("/fdm/jsbsim/systems/dps/major-mode-sm");
	var spec =  getprop("/fdm/jsbsim/systems/dps/spec-sm");
	var spec_string = assemble_spec_string(spec);
    
        var ops_string = major_mode~"1/"~spec_string~"/066";    
    
        device.DPS_menu_ops.setText(ops_string);

	# defaults for items that aren't yet implemented

	p_dps_env.waste_h2o_qty.setText(" 15");


	# RCRS is not flown on Atlantis (Yellow M with arrow group next to CO2 CNTLR to indicate Missing system)

    	p_dps_env.co2_cntlr_1.setText("1"); 
    	p_dps_env.co2_cntlr_2.setText("2"); 
    	p_dps_env.co2_filter_dp.setText(""); 
    	p_dps_env.co2_ppco2.setText(""); 
    	p_dps_env.co2_temp.setText(""); 
    	p_dps_env.co2_bedA_press_1.setText(""); 
    	p_dps_env.co2_bedA_press_2.setText(""); 
    	p_dps_env.co2_bedB_press_1.setText(""); 
    	p_dps_env.co2_bedB_press_2.setText(""); 
    	p_dps_env.co2_bed_dp_1.setText(""); 
    	p_dps_env.co2_bed_dp_2.setText(""); 
    	p_dps_env.vac_press.setText(""); 


    }
    
    p_dps_env.update = func
    {

		#Av bay temp ( clamp for max value)

		var avbay1_t = K_to_F(getprop("/fdm/jsbsim/systems/eclss/avbay/temperature-K")-2.0);
        var avbay2_t = K_to_F(getprop("/fdm/jsbsim/systems/eclss/avbay[1]/temperature-K"));
        var avbay3_t = K_to_F(getprop("/fdm/jsbsim/systems/eclss/avbay[2]/temperature-K")+1.0);


		avbay1_t = SpaceShuttle.clamp(avbay1_t, 45, 145);
        avbay2_t = SpaceShuttle.clamp(avbay2_t, 45, 145);
        avbay3_t = SpaceShuttle.clamp(avbay3_t, 45, 145);
    
       	p_dps_env.avbay_temp1.setText(sprintf("%4.0f", avbay1_t)); 
    	p_dps_env.avbay_temp2.setText(sprintf("%4.0f", avbay2_t)); 
    	p_dps_env.avbay_temp3.setText(sprintf("%4.0f", avbay3_t)); 

		


		var avbay1_fan = getprop("/fdm/jsbsim/systems/eclss/avbay/fan-cooling-effect") * 3.80;
    	var avbay2_fan = getprop("/fdm/jsbsim/systems/eclss/avbay[1]/fan-cooling-effect") * 3.77;
    	var avbay3_fan = getprop("/fdm/jsbsim/systems/eclss/avbay[2]/fan-cooling-effect") * 3.92;
    

    	p_dps_env.avbay_fan_dp1.setText(sprintf("%4.2f", avbay1_fan)); 
    	p_dps_env.avbay_fan_dp2.setText(sprintf("%4.2f", avbay2_fan)); 
    	p_dps_env.avbay_fan_dp3.setText(sprintf("%4.2f", avbay3_fan));  



	# oxygen system

	var airflow_in = getprop("/fdm/jsbsim/systems/eclss/cabin/air-gain-rate-lb_h");

	var o2_valve1 = getprop("/fdm/jsbsim/systems/eclss/oxygen/sys1-o2-supply-valve-status");
	var o2_valve2 = getprop("/fdm/jsbsim/systems/eclss/oxygen/sys2-o2-supply-valve-status");

	var oxygen_flow = math.abs(getprop("/fdm/jsbsim/systems/eclss/cabin/oxygen-in-fraction-av") * airflow_in);
	
	if ((o2_valve1 == 1) and (o2_valve2 == 1)) {oxygen_flow = 0.5 * oxygen_flow;}

	var o2_flow1 = oxygen_flow * o2_valve1;
	var o2_flow2 = oxygen_flow * o2_valve2;

	o2_flow1 = SpaceShuttle.clamp(o2_flow1, 0, 5);
	o2_flow2 = SpaceShuttle.clamp(o2_flow2, 0, 5);

 	p_dps_env.o2_flow1.setText(sprintf("%3.1f", o2_flow1)); 	
	p_dps_env.o2_flow2.setText(sprintf("%3.1f", o2_flow2)); 

    	p_dps_env.o2_regp1.setText(sprintf("%3.0f", 101.0 * o2_valve1));
    	p_dps_env.o2_regp2.setText(sprintf("%3.0f", 100.0 * o2_valve2));

	var regp = 103.0;
	if ((o2_valve1 == 0) and (o2_valve2 == 0)) {regp = 0.0;}

	p_dps_env.emer_o2_reg_p.setText(sprintf("%4.0f", regp));



	# nitrogen system
	
	var n2_sys1 = getprop("/fdm/jsbsim/systems/eclss/nitrogen/sys1-pressurized");
	var n2_sys2 = getprop("/fdm/jsbsim/systems/eclss/nitrogen/sys2-pressurized");

    	p_dps_env.n2_regp1.setText(sprintf("%3.0f", 203.0 * n2_sys1));
    	p_dps_env.n2_regp2.setText(sprintf("%3.0f", 198.0 * n2_sys2));

    	p_dps_env.h2o_tk_n2_1.setText(sprintf("%3.0f", 15.8 * n2_sys1));
    	p_dps_env.h2o_tk_n2_2.setText(sprintf("%3.0f", 16.4 * n2_sys2));

	#Indicators here for Supply/waste h2o pressure

	if ((n2_sys1 > 0.0) or (n2_sys2 > 0.0))
		{
		p_dps_env.supply_h2o_press.setText(" 34");
		p_dps_env.waste_h2o_press.setText(" 18");
		p_dps_env.supply_h2o_press_arrow.updateText("");
		p_dps_env.waste_h2o_press_arrow.updateText("");
		}
	else
		{
		p_dps_env.supply_h2o_press.setText("  0");
		p_dps_env.waste_h2o_press.setText("  0");
		p_dps_env.supply_h2o_press_arrow.updateText("L");
		p_dps_env.waste_h2o_press_arrow.updateText("L");
		}

	var nitrogen_flow = getprop("/fdm/jsbsim/systems/eclss/cabin/nitrogen-in-fraction-av") * airflow_in;

	if ((n2_sys1 == 1) and (n2_sys2 == 1)) {nitrogen_flow = 0.5 * nitrogen_flow;}

	var n2_flow1 = nitrogen_flow * n2_sys1;
	var n2_flow2 = nitrogen_flow * n2_sys2;

	n2_flow1 = SpaceShuttle.clamp(n2_flow1, 0, 5);
	n2_flow2= SpaceShuttle.clamp(n2_flow2, 0, 5);

    	p_dps_env.n2_flow1.setText(sprintf("%3.1f", n2_flow1));
    	p_dps_env.n2_flow2.setText(sprintf("%3.1f", n2_flow2));



    	# pressures

		var ppo2 = getprop("/fdm/jsbsim/systems/eclss/cabin/ppo2-psi"); #Lower limit reached when depress ( 2.7 ↓ and 0 L)

    	p_dps_env.ppo2a.setText(sprintf("%4.2f", ppo2));
    	p_dps_env.ppo2b.setText(sprintf("%4.2f", ppo2 + 0.1));
    	p_dps_env.ppo2c.setText(sprintf("%4.2f", ppo2));


	var cabin_p = getprop("/fdm/jsbsim/systems/eclss/cabin/air-pressure-psi");

	p_dps_env.cabin_press.setText(sprintf("%5.2f", cabin_p));
	p_dps_env.cabin_airlk_p.setText(sprintf("%4.1f", cabin_p));


	var fan_A = getprop("/fdm/jsbsim/systems/eclss/cabin/fan-A-operational");
	var fan_B = getprop("/fdm/jsbsim/systems/eclss/cabin/fan-B-operational");

	var cabin_dp = fan_A + fan_B;
	
	if (cabin_dp > 1.0) {cabin_dp = 6.61;}
	else if (cabin_dp > 0.0) {cabin_dp = 5.54;}
	else {cabin_dp = 0.0;}
	
	p_dps_env.cabin_fan_dp.setText(sprintf("%4.2f", cabin_dp));

	#PPCO2 clamp (30) : it increases when cabin fan are off

	var co2_pp = SpaceShuttle.clamp(getprop("/fdm/jsbsim/systems/eclss/cabin/co2-accumulation") * 15.0 + 0.3, 0, 30);
	p_dps_env.emer_ppco2.setText(sprintf("%4.1f",co2_pp));



	# IMU fans

	var imu_fanA_op = getprop("/fdm/jsbsim/systems/eclss/avbay/imu-fan-A-operational");
	var imu_fanB_op = getprop("/fdm/jsbsim/systems/eclss/avbay/imu-fan-B-operational");
	var imu_fanC_op = getprop("/fdm/jsbsim/systems/eclss/avbay/imu-fan-C-operational");

	var imu_fanA_sw = getprop("/fdm/jsbsim/systems/eclss/avbay/imu-fan-A-switch"); #Var for indicators (↓)
	var imu_fanB_sw = getprop("/fdm/jsbsim/systems/eclss/avbay/imu-fan-B-switch");
	var imu_fanC_sw = getprop("/fdm/jsbsim/systems/eclss/avbay/imu-fan-C-switch");


	var sym = "*";
	if (imu_fanA_op == 0){sym = "";}
	p_dps_env.imu_fan_A.setText(sym);

	sym = "*";
	if (imu_fanB_op == 0){sym = "";}
	p_dps_env.imu_fan_B.setText(sym);

	sym = "*";
	if (imu_fanC_op == 0){sym = "";}
	p_dps_env.imu_fan_C.setText(sym);


	#IMU Delta P

	var imu_dp = imu_fanA_op + imu_fanB_op + imu_fanC_op;

	if (imu_dp > 2.0) {imu_dp = 6.5;}
	else if (imu_dp > 1.0) {imu_dp = 5.3;}
	else if (imu_dp >0.0) {imu_dp = 4.5;}
	else imu_dp = 0;

	p_dps_env.imu_fan_dP.setText(sprintf("%4.2f", imu_dp));




	var mix_valve1 = getprop("/fdm/jsbsim/systems/eclss/nitrogen/sys1-oxygen-in-fraction");
	var mix_valve2 = getprop("/fdm/jsbsim/systems/eclss/nitrogen/sys1-oxygen-in-fraction");

	if (mix_valve1 == 0){p_dps_env.o2n2_cntl_vlv1.setText("N2");}
	else {p_dps_env.o2n2_cntl_vlv1.setText("O2");}

	if (mix_valve2 == 0){p_dps_env.o2n2_cntl_vlv2.setText("N2");}
	else {p_dps_env.o2n2_cntl_vlv2.setText("O2");}



	# pressure change

	var dpdt_value = getprop("/fdm/jsbsim/systems/eclss/cabin/air-pressure-change-psi_s") * 60;
	dpdt_value = SpaceShuttle.clamp(dpdt_value, -0.55, 0.45);

	p_dps_env.cabin_dpdT.setText(sprintf("%+5.2f", dpdt_value));



	# cabin temperature

	var cabin_T =  K_to_F(getprop("/fdm/jsbsim/systems/thermal-distribution/interior-temperature-K"));
    p_dps_env.cabin_t.setText(sprintf("%3.0f", cabin_T));
	p_dps_env.cabin_hx_out_t.setText(sprintf("%3.0f", cabin_T + 30.0));



	# N2 quantity - this is just guesstimated

	var mission_time = getprop("/fdm/jsbsim/systems/timer/delta-MET") + getprop("/sim/time/elapsed-sec");
	var qty = (1.0 - (mission_time/(86400.0 * 12.0)));
	if (qty < 0.0) {qty = 0.0;}

    	p_dps_env.n2_qty1.setText(sprintf("%3.0f", 460.0 * qty));
    	p_dps_env.n2_qty2.setText(sprintf("%3.0f", 457.0 * qty));


	# supply water
	# we don't have tanks separated, so assume they fill from A to D

	var supply_water_fraction = getprop("/fdm/jsbsim/propulsion/tank[19]/contents-lbs") / 165.0;

	if (supply_water_fraction > 1.0) 
		{	
		p_dps_env.supply_h2o_qty_a.setText("100");
		supply_water_fraction = supply_water_fraction -1.0; 
		}
	else
		{
		p_dps_env.supply_h2o_qty_a.setText(sprintf("%3.0f", supply_water_fraction * 100.0));
		supply_water_fraction = 0.0; 
		}

	if (supply_water_fraction > 1.0) 
		{	
		p_dps_env.supply_h2o_qty_b.setText("100");
		supply_water_fraction = supply_water_fraction -1.0; 
		}
	else
		{
		p_dps_env.supply_h2o_qty_b.setText(sprintf("%3.0f", supply_water_fraction * 100.0));
		supply_water_fraction = 0.0; 
		}
	if (supply_water_fraction > 1.0) 
		{	
		p_dps_env.supply_h2o_qty_c.setText("100");
		supply_water_fraction = supply_water_fraction -1.0; 
		}
	else
		{
		p_dps_env.supply_h2o_qty_c.setText(sprintf("%3.0f", supply_water_fraction * 100.0));
		supply_water_fraction = 0.0; 
		}
	
	p_dps_env.supply_h2o_qty_d.setText(sprintf("%3.0f", supply_water_fraction * 100.0));



	var left_temp = K_to_F(getprop("/fdm/jsbsim/systems/thermal-distribution/left-temperature-K"));

	#Generic clamp to avoid too low displayed values (no heaters simulated yet, so no interest in indicators and fault messages)

	left_temp = SpaceShuttle.clamp(left_temp, 0, 200);

    	p_dps_env.supply_dmp_ln_t.setText(sprintf("%3.0f", left_temp + 3.0));
    	p_dps_env.supply_h2o_noz_t_a.setText(sprintf("%3.0f", left_temp + 5.0));
   		p_dps_env.supply_h2o_noz_t_b.setText(sprintf("%3.0f", left_temp - 2.0));


    	p_dps_env.waste_h2o_dmp_ln_t.setText(sprintf("%3.0f", left_temp + 2.0));
    	p_dps_env.waste_h2o_noz_t_A.setText(sprintf("%3.0f", left_temp - 3.0));
    	p_dps_env.waste_h2o_noz_t_B.setText(sprintf("%3.0f", left_temp + 1.0)); 
    	p_dps_env.waste_h2o_vac_vt_noz_t.setText(sprintf("%3.0f", left_temp + 4.0));
	
	if (getprop("/fdm/jsbsim/systems/eclss/cabin/humidity-sep-A-switch") == 0)
    		{p_dps_env.humid_sep_A.setText("");}
	else
		{p_dps_env.humid_sep_A.setText("*");}

	if (getprop("/fdm/jsbsim/systems/eclss/cabin/humidity-sep-B-switch") == 0)
    		{p_dps_env.humid_sep_B.setText("");}
	else
		{p_dps_env.humid_sep_B.setText("*");}



	#SM realistic option with indicators

	if (SpaceShuttle.sm_simulation_detail_level == 1)
		{

		p_dps_env.arrow_group.setVisible(1);

		#Av bays temps ( max 145°) and fans (Low at 0 dP)

		if (avbay1_t == 145) {p_dps_env.avbay_temp1_arrow.updateText("H");}
		else if  ((avbay1_t > 130) and (avbay1_t < 145)) {p_dps_env.avbay_temp1_arrow.updateText("↑");}
		else {p_dps_env.avbay_temp1_arrow.updateText("");}

		if (avbay2_t == 145) {p_dps_env.avbay_temp2_arrow.updateText("H");}
		else if  ((avbay2_t > 130) and (avbay2_t < 145)) {p_dps_env.avbay_temp2_arrow.updateText("↑");}
		else {p_dps_env.avbay_temp2_arrow.updateText("");}

		if (avbay3_t == 145) {p_dps_env.avbay_temp3_arrow.updateText("H");}
		else if  ((avbay3_t > 130) and (avbay3_t < 145)) {p_dps_env.avbay_temp3_arrow.updateText("↑");}
		else {p_dps_env.avbay_temp3_arrow.updateText("");}


		if (avbay1_fan == 0) {p_dps_env.avbay_fan_dp1_arrow.updateText("L");}
		else if ((avbay1_fan > 0) and (avbay1_fan < 3)) {p_dps_env.avbay_fan_dp1_arrow.updateText("↓");}
		else {p_dps_env.avbay_fan_dp1_arrow.updateText("");}

		if (avbay2_fan == 0) {p_dps_env.avbay_fan_dp2_arrow.updateText("L");}
		else if ((avbay2_fan > 0) and (avbay2_fan < 3)) {p_dps_env.avbay_fan_dp2_arrow.updateText("↓");}
		else {p_dps_env.avbay_fan_dp2_arrow.updateText("");}

		if (avbay3_fan == 0) {p_dps_env.avbay_fan_dp3_arrow.updateText("L");}
		else if ((avbay3_fan > 0) and (avbay3_fan < 3)) {p_dps_env.avbay_fan_dp3_arrow.updateText("↓");}
		else {p_dps_env.avbay_fan_dp3_arrow.updateText("");}



		#Oxygen system flow

		if (o2_flow1 == 0) {p_dps_env.o2_flow1_arrow.updateText("L");}
		else if (o2_flow1 == 5) {p_dps_env.o2_flow1_arrow.updateText("H");}
		else {p_dps_env.o2_flow1_arrow.updateText("");}

		if (o2_flow2 == 0) {p_dps_env.o2_flow2_arrow.updateText("L");}
		else if (o2_flow2 == 5) {p_dps_env.o2_flow2_arrow.updateText("H");}
		else {p_dps_env.o2_flow2_arrow.updateText("");}

		#Oxygen Reg and Emer

		if (o2_valve1 == 0)
			{
			p_dps_env.o2_regp1_arrow.updateText("L");
			}
		else
			{
			p_dps_env.o2_regp1_arrow.updateText("");
			}

		if (o2_valve2 == 0)
			{
			p_dps_env.o2_regp2_arrow.updateText("L");
			}
		else
			{
			p_dps_env.o2_regp2_arrow.updateText("");
			}

		#Oxy emer

		if ((o2_valve1 == 0) and (o2_valve2 == 0)) {p_dps_env.emer_o2_reg_p_arrow.updateText("L");}
		else {p_dps_env.emer_o2_reg_p_arrow.updateText("");}


		#Nitrogen system flow

		if (n2_flow1 == 0) {p_dps_env.n2_flow1_arrow.updateText("L");}
		else if (n2_flow1 == 5) {p_dps_env.n2_flow1_arrow.updateText("H");}
		else {p_dps_env.n2_flow1_arrow.updateText("");}

		if (n2_flow2 == 0) {p_dps_env.n2_flow2_arrow.updateText("L");}
		else if (n2_flow2 == 5) {p_dps_env.n2_flow2_arrow.updateText("H");}
		else {p_dps_env.n2_flow2_arrow.updateText("");}


		#Nitrogen Reg and H2O tk N2 press

		if (n2_sys1 == 0) 
			{
			p_dps_env.n2_regp1_arrow.updateText("L");
			p_dps_env.h2o_tk_n2_1_arrow.updateText("L");
			}
		else
			{
			p_dps_env.n2_regp1_arrow.updateText("");
			p_dps_env.h2o_tk_n2_1_arrow.updateText("");
			}

		if (n2_sys2 == 0) 
			{
			p_dps_env.n2_regp2_arrow.updateText("L");
			p_dps_env.h2o_tk_n2_2_arrow.updateText("L");
			}
		else
			{
			p_dps_env.n2_regp2_arrow.updateText("");
			p_dps_env.h2o_tk_n2_2_arrow.updateText("");
			}

		#Supply/ waste Press (see line 310)

		#PPO2 (in case of depressurisation scenario) // no ↓↑ for C 

		if (ppo2 < 0.01)
			{
			p_dps_env.ppo2a_arrow.updateText("L");
			p_dps_env.ppo2b_arrow.updateText("L");
			p_dps_env.ppo2c_arrow.updateText("L");
			}
		else if ((ppo2 > 0.01) and (ppo2 < 2.70))
			{
			p_dps_env.ppo2a_arrow.updateText("↓");
			p_dps_env.ppo2b_arrow.updateText("↓");
			p_dps_env.ppo2c_arrow.updateText("");
			}
		else
			{
			p_dps_env.ppo2a_arrow.updateText("");
			p_dps_env.ppo2b_arrow.updateText("");
			p_dps_env.ppo2c_arrow.updateText("");
			}

		#Cabin Pressure

		if (cabin_p < 0.05) 
			{
			p_dps_env.cabin_press_arrow.updateText("L");
			p_dps_env.cabin_airlk_p_arrow.updateText("L");
			}
		else if ((cabin_p > 0.05) and (cabin_p < 13.8))
			{
			p_dps_env.cabin_press_arrow.updateText("↓");
			p_dps_env.cabin_airlk_p_arrow.updateText("↓");
			}
		else
			{
			p_dps_env.cabin_press_arrow.updateText("");
			p_dps_env.cabin_airlk_p_arrow.updateText("");
			}


		#Pressure change dP/dT

		if (dpdt_value == -0.55) {p_dps_env.cabin_dpdT_arrow.updateText("L");}
		else if ((dpdt_value > .055) and (dpdt_value < -0.12)) {p_dps_env.cabin_dpdT_arrow.updateText("↓");}
		else if (dpdt_value == 0.45) {p_dps_env.cabin_dpdT_arrow.updateText("H");}
		else {p_dps_env.cabin_dpdT_arrow.updateText("");}

		
		#Cabin fan DP

		if (cabin_dp == 0) {p_dps_env.cabin_fan_dp_arrow.updateText("L");}
		else {p_dps_env.cabin_fan_dp_arrow.updateText("");}


		#IMU fans malfunction arrow ( switch on but not powered = ↓)

		if (imu_fanA_op != imu_fanA_sw) {p_dps_env.imu_fan_A_arrow.updateText("↓");}
		else {p_dps_env.imu_fan_A_arrow.updateText("");}

		if (imu_fanB_op != imu_fanB_sw) {p_dps_env.imu_fan_B_arrow.updateText("↓");}
		else {p_dps_env.imu_fan_B_arrow.updateText("");}

		if (imu_fanC_op != imu_fanC_sw) {p_dps_env.imu_fan_C_arrow.updateText("↓");}
		else {p_dps_env.imu_fan_C_arrow.updateText("");}


		#IMU deltaP

		if (imu_dp == 0) {p_dps_env.imu_fan_dP_arrow.updateText("L");}
		else {p_dps_env.imu_fan_dP_arrow.updateText("");}


		

		}
	
	else {p_dps_env.arrow_group.setVisible(0);}


        device.update_common_DPS();
    }
    
    
    
    return p_dps_env;
}
