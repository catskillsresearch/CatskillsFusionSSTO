#---------------------------------------
# SpaceShuttle PFD Page include:
#        Page: p_dps_sm_sys_summ1
# Description: the SM system summary page 1
#      Author: Thorsten Renk, 2016 // GinGin, 2020
#---------------------------------------


#Global variable for SM indicator details
var sm_simulation_detail_level = getprop("/sim/config/shuttle/sm-detail-level");

var PFD_addpage_p_dps_sm_sys_summ1 = func(device)
{
    var p_dps_sm_sys_summ1 = device.addPage("CRTSMSysSumm1", "p_dps_sm_sys_summ1");
        
    p_dps_sm_sys_summ1.group = device.svg.getElementById("p_dps_sm_sys_summ1");
    p_dps_sm_sys_summ1.group.setColor(dps_r, dps_g, dps_b);

    p_dps_sm_sys_summ1.volts_fc1 = device.svg.getElementById("p_dps_sm_sys_summ1_volts_fc1");
    p_dps_sm_sys_summ1.volts_fc2 = device.svg.getElementById("p_dps_sm_sys_summ1_volts_fc2");
    p_dps_sm_sys_summ1.volts_fc3 = device.svg.getElementById("p_dps_sm_sys_summ1_volts_fc3");

    p_dps_sm_sys_summ1.amps_fc1 = device.svg.getElementById("p_dps_sm_sys_summ1_amps_fc1");
    p_dps_sm_sys_summ1.amps_fc2 = device.svg.getElementById("p_dps_sm_sys_summ1_amps_fc2");
    p_dps_sm_sys_summ1.amps_fc3 = device.svg.getElementById("p_dps_sm_sys_summ1_amps_fc3");

    p_dps_sm_sys_summ1.reac_vlv_1 = device.svg.getElementById("p_dps_sm_sys_summ1_reac_vlv_1");
    p_dps_sm_sys_summ1.reac_vlv_2 = device.svg.getElementById("p_dps_sm_sys_summ1_reac_vlv_2");
    p_dps_sm_sys_summ1.reac_vlv_3 = device.svg.getElementById("p_dps_sm_sys_summ1_reac_vlv_3");

    p_dps_sm_sys_summ1.stackT_1 = device.svg.getElementById("p_dps_sm_sys_summ1_stackT_1");
    p_dps_sm_sys_summ1.stackT_2 = device.svg.getElementById("p_dps_sm_sys_summ1_stackT_2");
    p_dps_sm_sys_summ1.stackT_3 = device.svg.getElementById("p_dps_sm_sys_summ1_stackT_3");

    p_dps_sm_sys_summ1.exitT_1 = device.svg.getElementById("p_dps_sm_sys_summ1_exitT_1");
    p_dps_sm_sys_summ1.exitT_2 = device.svg.getElementById("p_dps_sm_sys_summ1_exitT_2");
    p_dps_sm_sys_summ1.exitT_3 = device.svg.getElementById("p_dps_sm_sys_summ1_exitT_3");

    p_dps_sm_sys_summ1.coolp_1 = device.svg.getElementById("p_dps_sm_sys_summ1_coolp_1");
    p_dps_sm_sys_summ1.coolp_2 = device.svg.getElementById("p_dps_sm_sys_summ1_coolp_2");
    p_dps_sm_sys_summ1.coolp_3 = device.svg.getElementById("p_dps_sm_sys_summ1_coolp_3");

    p_dps_sm_sys_summ1.pump1 = device.svg.getElementById("p_dps_sm_sys_summ1_pump1");
    p_dps_sm_sys_summ1.pump2 = device.svg.getElementById("p_dps_sm_sys_summ1_pump2");
    p_dps_sm_sys_summ1.pump3 = device.svg.getElementById("p_dps_sm_sys_summ1_pump3");

    p_dps_sm_sys_summ1.volts_mn1 = device.svg.getElementById("p_dps_sm_sys_summ1_volts_mn1");
    p_dps_sm_sys_summ1.volts_mn2 = device.svg.getElementById("p_dps_sm_sys_summ1_volts_mn2");
    p_dps_sm_sys_summ1.volts_mn3 = device.svg.getElementById("p_dps_sm_sys_summ1_volts_mn3");

    p_dps_sm_sys_summ1.volts_ess1 = device.svg.getElementById("p_dps_sm_sys_summ1_volts_ess1");
    p_dps_sm_sys_summ1.volts_ess2 = device.svg.getElementById("p_dps_sm_sys_summ1_volts_ess2");
    p_dps_sm_sys_summ1.volts_ess3 = device.svg.getElementById("p_dps_sm_sys_summ1_volts_ess3");

    p_dps_sm_sys_summ1.volts_cntl1_1 = device.svg.getElementById("p_dps_sm_sys_summ1_volts_cntl1_1");
    p_dps_sm_sys_summ1.volts_cntl1_2 = device.svg.getElementById("p_dps_sm_sys_summ1_volts_cntl1_2");
    p_dps_sm_sys_summ1.volts_cntl1_3 = device.svg.getElementById("p_dps_sm_sys_summ1_volts_cntl1_3");

    p_dps_sm_sys_summ1.volts_cntl2_1 = device.svg.getElementById("p_dps_sm_sys_summ1_volts_cntl2_1");
    p_dps_sm_sys_summ1.volts_cntl2_2 = device.svg.getElementById("p_dps_sm_sys_summ1_volts_cntl2_2");
    p_dps_sm_sys_summ1.volts_cntl2_3 = device.svg.getElementById("p_dps_sm_sys_summ1_volts_cntl2_3");

    p_dps_sm_sys_summ1.volts_cntl3_1 = device.svg.getElementById("p_dps_sm_sys_summ1_volts_cntl3_1");
    p_dps_sm_sys_summ1.volts_cntl3_2 = device.svg.getElementById("p_dps_sm_sys_summ1_volts_cntl3_2");
    p_dps_sm_sys_summ1.volts_cntl3_3 = device.svg.getElementById("p_dps_sm_sys_summ1_volts_cntl3_3");

    p_dps_sm_sys_summ1.volt_phiA_1 = device.svg.getElementById("p_dps_sm_sys_summ1_volt_phiA_1");
    p_dps_sm_sys_summ1.volt_phiA_2 = device.svg.getElementById("p_dps_sm_sys_summ1_volt_phiA_2");
    p_dps_sm_sys_summ1.volt_phiA_3 = device.svg.getElementById("p_dps_sm_sys_summ1_volt_phiA_3");

    p_dps_sm_sys_summ1.volt_phiB_1 = device.svg.getElementById("p_dps_sm_sys_summ1_volt_phiB_1");
    p_dps_sm_sys_summ1.volt_phiB_2 = device.svg.getElementById("p_dps_sm_sys_summ1_volt_phiB_2");
    p_dps_sm_sys_summ1.volt_phiB_3 = device.svg.getElementById("p_dps_sm_sys_summ1_volt_phiB_3");

    p_dps_sm_sys_summ1.volt_phiC_1 = device.svg.getElementById("p_dps_sm_sys_summ1_volt_phiC_1");
    p_dps_sm_sys_summ1.volt_phiC_2 = device.svg.getElementById("p_dps_sm_sys_summ1_volt_phiC_2");
    p_dps_sm_sys_summ1.volt_phiC_3 = device.svg.getElementById("p_dps_sm_sys_summ1_volt_phiC_3");

    p_dps_sm_sys_summ1.amps_phiA_1 = device.svg.getElementById("p_dps_sm_sys_summ1_amps_phiA_1");
    p_dps_sm_sys_summ1.amps_phiA_2 = device.svg.getElementById("p_dps_sm_sys_summ1_amps_phiA_2");
    p_dps_sm_sys_summ1.amps_phiA_3 = device.svg.getElementById("p_dps_sm_sys_summ1_amps_phiA_3");

    p_dps_sm_sys_summ1.amps_phiB_1 = device.svg.getElementById("p_dps_sm_sys_summ1_amps_phiB_1");
    p_dps_sm_sys_summ1.amps_phiB_2 = device.svg.getElementById("p_dps_sm_sys_summ1_amps_phiB_2");
    p_dps_sm_sys_summ1.amps_phiB_3 = device.svg.getElementById("p_dps_sm_sys_summ1_amps_phiB_3");

    p_dps_sm_sys_summ1.amps_phiC_1 = device.svg.getElementById("p_dps_sm_sys_summ1_amps_phiC_1");
    p_dps_sm_sys_summ1.amps_phiC_2 = device.svg.getElementById("p_dps_sm_sys_summ1_amps_phiC_2");
    p_dps_sm_sys_summ1.amps_phiC_3 = device.svg.getElementById("p_dps_sm_sys_summ1_amps_phiC_3");
    

    p_dps_sm_sys_summ1.DVSS1_1 = device.svg.getElementById("p_dps_sm_sys_summ1_DVSS1_1");
    p_dps_sm_sys_summ1.DVSS1_2 = device.svg.getElementById("p_dps_sm_sys_summ1_DVSS1_2");
    p_dps_sm_sys_summ1.DVSS1_3 = device.svg.getElementById("p_dps_sm_sys_summ1_DVSS1_3");

    p_dps_sm_sys_summ1.DVSS2_1 = device.svg.getElementById("p_dps_sm_sys_summ1_DVSS2_1");
    p_dps_sm_sys_summ1.DVSS2_2 = device.svg.getElementById("p_dps_sm_sys_summ1_DVSS2_2");
    p_dps_sm_sys_summ1.DVSS2_3 = device.svg.getElementById("p_dps_sm_sys_summ1_DVSS2_3");

    p_dps_sm_sys_summ1.DVSS3_1 = device.svg.getElementById("p_dps_sm_sys_summ1_DVSS3_1");
    p_dps_sm_sys_summ1.DVSS3_2 = device.svg.getElementById("p_dps_sm_sys_summ1_DVSS3_2");
    p_dps_sm_sys_summ1.DVSS3_3 = device.svg.getElementById("p_dps_sm_sys_summ1_DVSS3_3");

    p_dps_sm_sys_summ1.cabin = device.svg.getElementById("p_dps_sm_sys_summ1_cabin");   
    p_dps_sm_sys_summ1.cabin.enableUpdate();

    p_dps_sm_sys_summ1.lr_1 = device.svg.getElementById("p_dps_sm_sys_summ1_lr_1");
    p_dps_sm_sys_summ1.lr_2 = device.svg.getElementById("p_dps_sm_sys_summ1_lr_2");
    p_dps_sm_sys_summ1.lr_1.enableUpdate();
    p_dps_sm_sys_summ1.lr_2.enableUpdate();

    p_dps_sm_sys_summ1.avbay1_1 = device.svg.getElementById("p_dps_sm_sys_summ1_avbay1_1");
    p_dps_sm_sys_summ1.avbay1_2 = device.svg.getElementById("p_dps_sm_sys_summ1_avbay1_2");
    p_dps_sm_sys_summ1.avbay1_1.enableUpdate();
    p_dps_sm_sys_summ1.avbay1_2.enableUpdate();


    p_dps_sm_sys_summ1.avbay2_1 = device.svg.getElementById("p_dps_sm_sys_summ1_avbay2_1");
    p_dps_sm_sys_summ1.avbay2_2 = device.svg.getElementById("p_dps_sm_sys_summ1_avbay2_2");
    p_dps_sm_sys_summ1.avbay2_1.enableUpdate();
    p_dps_sm_sys_summ1.avbay2_2.enableUpdate();


    p_dps_sm_sys_summ1.avbay3_1 = device.svg.getElementById("p_dps_sm_sys_summ1_avbay3_1");
    p_dps_sm_sys_summ1.avbay3_2 = device.svg.getElementById("p_dps_sm_sys_summ1_avbay3_2");
    p_dps_sm_sys_summ1.avbay3_1.enableUpdate();
    p_dps_sm_sys_summ1.avbay3_2.enableUpdate();

    p_dps_sm_sys_summ1.press = device.svg.getElementById("p_dps_sm_sys_summ1_press");
    p_dps_sm_sys_summ1.dPdt = device.svg.getElementById("p_dps_sm_sys_summ1_dPdt");
    p_dps_sm_sys_summ1.eq = device.svg.getElementById("p_dps_sm_sys_summ1_eq");

    p_dps_sm_sys_summ1.o2_conc = device.svg.getElementById("p_dps_sm_sys_summ1_o2_conc");
    p_dps_sm_sys_summ1.ppo2_1 = device.svg.getElementById("p_dps_sm_sys_summ1_ppo2_1");
    p_dps_sm_sys_summ1.ppo2_2 = device.svg.getElementById("p_dps_sm_sys_summ1_ppo2_2");

    p_dps_sm_sys_summ1.fan_dp = device.svg.getElementById("p_dps_sm_sys_summ1_fan_dp");
    p_dps_sm_sys_summ1.hx_out_T = device.svg.getElementById("p_dps_sm_sys_summ1_hx_out_T");

    p_dps_sm_sys_summ1.o2flow_1 = device.svg.getElementById("p_dps_sm_sys_summ1_o2flow_1");
    p_dps_sm_sys_summ1.o2flow_2 = device.svg.getElementById("p_dps_sm_sys_summ1_o2flow_2");

    p_dps_sm_sys_summ1.n2flow_1 = device.svg.getElementById("p_dps_sm_sys_summ1_n2flow_1");
    p_dps_sm_sys_summ1.n2flow_2 = device.svg.getElementById("p_dps_sm_sys_summ1_n2flow_2");

    p_dps_sm_sys_summ1.imu_A = device.svg.getElementById("p_dps_sm_sys_summ1_imu_A");
    p_dps_sm_sys_summ1.imu_B = device.svg.getElementById("p_dps_sm_sys_summ1_imu_B");
    p_dps_sm_sys_summ1.imu_C = device.svg.getElementById("p_dps_sm_sys_summ1_imu_C");


	

    p_dps_sm_sys_summ1.kW = device.svg.getElementById("p_dps_sm_sys_summ1_kW");
    p_dps_sm_sys_summ1.total_amps = device.svg.getElementById("p_dps_sm_sys_summ1_total_amps");

	#Pass only element/arrow subgroups (IMU Fan // O2 Conc)

	p_dps_sm_sys_summ1.pass_only_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_pass_only_arrow");
	p_dps_sm_sys_summ1.pass_only_element = device.svg.getElementById("p_dps_sm_sys_summ1_pass_only_element");


	#Failure Arrow indicators // Yellow Color (Parameters that can reach their limits L or H //  valve state ↓↑)

	p_dps_sm_sys_summ1.volts_fc_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_volts_fc1_arrow");
    p_dps_sm_sys_summ1.volts_fc2_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_volts_fc2_arrow");
    p_dps_sm_sys_summ1.volts_fc3_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_volts_fc3_arrow");
	p_dps_sm_sys_summ1.volts_fc_arrow.enableUpdate();
	p_dps_sm_sys_summ1.volts_fc2_arrow.enableUpdate();
	p_dps_sm_sys_summ1.volts_fc3_arrow.enableUpdate();

	p_dps_sm_sys_summ1.volts_mn1_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_volts_mn1_arrow");
    p_dps_sm_sys_summ1.volts_mn2_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_volts_mn2_arrow");
    p_dps_sm_sys_summ1.volts_mn3_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_volts_mn3_arrow");
	p_dps_sm_sys_summ1.volts_mn1_arrow.enableUpdate();
	p_dps_sm_sys_summ1.volts_mn2_arrow.enableUpdate();
	p_dps_sm_sys_summ1.volts_mn3_arrow.enableUpdate();

	p_dps_sm_sys_summ1.volts_ess1_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_volts_ess1_arrow");
	p_dps_sm_sys_summ1.volts_ess2_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_volts_ess2_arrow");
	p_dps_sm_sys_summ1.volts_ess3_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_volts_ess3_arrow");
	p_dps_sm_sys_summ1.volts_ess1_arrow.enableUpdate();
	p_dps_sm_sys_summ1.volts_ess2_arrow.enableUpdate();
	p_dps_sm_sys_summ1.volts_ess3_arrow.enableUpdate();

	p_dps_sm_sys_summ1.press_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_press_arrow");
	p_dps_sm_sys_summ1.press_arrow.enableUpdate();


	p_dps_sm_sys_summ1.reac_vlv_1_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_reac_vlv_1_arrow");
    p_dps_sm_sys_summ1.reac_vlv_2_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_reac_vlv_2_arrow");
    p_dps_sm_sys_summ1.reac_vlv_3_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_reac_vlv_3_arrow");
	p_dps_sm_sys_summ1.reac_vlv_1_arrow.enableUpdate();
	p_dps_sm_sys_summ1.reac_vlv_2_arrow.enableUpdate();
	p_dps_sm_sys_summ1.reac_vlv_3_arrow.enableUpdate();

	p_dps_sm_sys_summ1.coolp_1_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_coolp_1_arrow");
    p_dps_sm_sys_summ1.coolp_2_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_coolp_2_arrow");
    p_dps_sm_sys_summ1.coolp_3_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_coolp_3_arrow");
	p_dps_sm_sys_summ1.coolp_1_arrow.enableUpdate();
	p_dps_sm_sys_summ1.coolp_2_arrow.enableUpdate();
	p_dps_sm_sys_summ1.coolp_3_arrow.enableUpdate();

	p_dps_sm_sys_summ1.o2flow_1_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_o2flow_1_arrow");
    p_dps_sm_sys_summ1.o2flow_2_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_o2flow_2_arrow");
	p_dps_sm_sys_summ1.o2flow_1_arrow.enableUpdate();
	p_dps_sm_sys_summ1.o2flow_2_arrow.enableUpdate();
	

    p_dps_sm_sys_summ1.n2flow_1_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_n2flow_1_arrow");
    p_dps_sm_sys_summ1.n2flow_2_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_n2flow_2_arrow");
	p_dps_sm_sys_summ1.n2flow_1_arrow.enableUpdate();
	p_dps_sm_sys_summ1.n2flow_2_arrow.enableUpdate();

	p_dps_sm_sys_summ1.imu_A_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_imu_A_arrow");
    p_dps_sm_sys_summ1.imu_B_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_imu_B_arrow");
    p_dps_sm_sys_summ1.imu_C_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_imu_C_arrow");
	p_dps_sm_sys_summ1.imu_A_arrow.enableUpdate();
	p_dps_sm_sys_summ1.imu_B_arrow.enableUpdate();
	p_dps_sm_sys_summ1.imu_C_arrow.enableUpdate();


	p_dps_sm_sys_summ1.amps_fc1_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_amps_fc1_arrow");
	p_dps_sm_sys_summ1.amps_fc2_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_amps_fc2_arrow");
	p_dps_sm_sys_summ1.amps_fc3_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_amps_fc3_arrow");
	p_dps_sm_sys_summ1.amps_fc1_arrow.enableUpdate();
	p_dps_sm_sys_summ1.amps_fc2_arrow.enableUpdate();
	p_dps_sm_sys_summ1.amps_fc3_arrow.enableUpdate();

	p_dps_sm_sys_summ1.stackT_1_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_stackT_1_arrow");
	p_dps_sm_sys_summ1.stackT_2_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_stackT_2_arrow");
	p_dps_sm_sys_summ1.stackT_3_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_stackT_3_arrow");
	p_dps_sm_sys_summ1.stackT_1_arrow.enableUpdate();
	p_dps_sm_sys_summ1.stackT_2_arrow.enableUpdate();
	p_dps_sm_sys_summ1.stackT_3_arrow.enableUpdate();

	p_dps_sm_sys_summ1.exitT_1_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_exitT_1_arrow");
	p_dps_sm_sys_summ1.exitT_2_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_exitT_2_arrow");
	p_dps_sm_sys_summ1.exitT_3_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_exitT_3_arrow");
	p_dps_sm_sys_summ1.exitT_1_arrow.enableUpdate();
	p_dps_sm_sys_summ1.exitT_2_arrow.enableUpdate();
	p_dps_sm_sys_summ1.exitT_3_arrow.enableUpdate();

	p_dps_sm_sys_summ1.pump1_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_pump1_arrow");
	p_dps_sm_sys_summ1.pump2_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_pump2_arrow");
	p_dps_sm_sys_summ1.pump3_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_pump3_arrow");
	p_dps_sm_sys_summ1.pump1_arrow.enableUpdate();
	p_dps_sm_sys_summ1.pump2_arrow.enableUpdate();
	p_dps_sm_sys_summ1.pump3_arrow.enableUpdate();

	p_dps_sm_sys_summ1.kW_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_kW_arrow");
	p_dps_sm_sys_summ1.kW_arrow.enableUpdate();

    p_dps_sm_sys_summ1.total_amps_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_total_amps_arrow");
	p_dps_sm_sys_summ1.total_amps_arrow.enableUpdate();

	p_dps_sm_sys_summ1.dPdt_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_dPdt_arrow");
	p_dps_sm_sys_summ1.dPdt_arrow.enableUpdate();

	p_dps_sm_sys_summ1.ppo2_1_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_ppo2_1_arrow");
	p_dps_sm_sys_summ1.ppo2_2_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_ppo2_2_arrow");
	p_dps_sm_sys_summ1.ppo2_1_arrow.enableUpdate();
	p_dps_sm_sys_summ1.ppo2_2_arrow.enableUpdate();

	p_dps_sm_sys_summ1.o2_conc_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_o2_conc_arrow");
	p_dps_sm_sys_summ1.o2_conc_arrow.enableUpdate();

	p_dps_sm_sys_summ1.fan_dp_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_fan_dp_arrow");
	p_dps_sm_sys_summ1.fan_dp_arrow.enableUpdate();

	p_dps_sm_sys_summ1.imu_bfs_deltaP_value_arrow = device.svg.getElementById("p_dps_sm_sys_summ1_imu_bfs_deltaP_value_arrow"); #Arrow for imu fan DeltaP// BFS only
	p_dps_sm_sys_summ1.imu_bfs_deltaP_value_arrow.enableUpdate();

	
	#Indicator subgroups for the ones that are linked by one variable (AC Voltage//Amps and DeltaV SS)//Either L or ""


	p_dps_sm_sys_summ1.arrow_group_AC1_subgroup = device.svg.getElementById("p_dps_sm_sys_summ1_arrow_group_AC1_subgroup");
	p_dps_sm_sys_summ1.arrow_group_AC2_subgroup = device.svg.getElementById("p_dps_sm_sys_summ1_arrow_group_AC2_subgroup");
	p_dps_sm_sys_summ1.arrow_group_AC3_subgroup = device.svg.getElementById("p_dps_sm_sys_summ1_arrow_group_AC3_subgroup");

	p_dps_sm_sys_summ1.arrow_group_DVSS1_subgroup = device.svg.getElementById("p_dps_sm_sys_summ1_arrow_group_DVSS1_subgroup");
	p_dps_sm_sys_summ1.arrow_group_DVSS2_subgroup = device.svg.getElementById("p_dps_sm_sys_summ1_arrow_group_DVSS2_subgroup");
	p_dps_sm_sys_summ1.arrow_group_DVSS3_subgroup = device.svg.getElementById("p_dps_sm_sys_summ1_arrow_group_DVSS3_subgroup");



	#All arrows in a group to have just one line for setcolor

	p_dps_sm_sys_summ1.arrow_group = device.svg.getElementById("p_dps_sm_sys_summ1_arrow_group");
	p_dps_sm_sys_summ1.arrow_group.setColor(1, 1, 0);
	


	#Labels that change with BFS ( IMU Fan, Fuel cell PH, O2 conc) (5-34 dps pictionnary)

	p_dps_sm_sys_summ1.o2_conc_label = device.svg.getElementById("p_dps_sm_sys_summ1_o2_conc_label");

	p_dps_sm_sys_summ1.imu_fan_label = device.svg.getElementById("p_dps_sm_sys_summ1_imu_fan_label");
	p_dps_sm_sys_summ1.imu_fan_label.enableUpdate();

	p_dps_sm_sys_summ1.imu_bfs_deltaP_value = device.svg.getElementById("p_dps_sm_sys_summ1_imu_bfs_deltaP_value");
	p_dps_sm_sys_summ1.imu_A_label = device.svg.getElementById("p_dps_sm_sys_summ1_imu_A_label");
    p_dps_sm_sys_summ1.imu_B_label = device.svg.getElementById("p_dps_sm_sys_summ1_imu_B_label");
    p_dps_sm_sys_summ1.imu_C_label = device.svg.getElementById("p_dps_sm_sys_summ1_imu_C_label");

	
	p_dps_sm_sys_summ1.fuel_cell_label = device.svg.getElementById("p_dps_sm_sys_summ1_fuel_cell_label");
	p_dps_sm_sys_summ1.fuel_cell_label.enableUpdate();
	



    p_dps_sm_sys_summ1.ondisplay = func
    {
        device.DPS_menu_title.setText("                  SM SYS SUMM 1");
        device.MEDS_menu_title.setText("      DPS MENU");
    
	p_dps_sm_sys_summ1.major_function = SpaceShuttle.idp_array[device.port_selected-1].get_major_function();

	if (p_dps_sm_sys_summ1.major_function == 4)
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
        var ops_string = major_mode~"1/"~spec_string~"/078";  
    
        device.DPS_menu_ops.setText(ops_string);

	# set defaults for values not yet implemented

   	#p_dps_sm_sys_summ1.cabin.setText("0.0");

    	#p_dps_sm_sys_summ1.lr_1.setText("0.0");
    	#p_dps_sm_sys_summ1.lr_2.setText("0.0");

    	#p_dps_sm_sys_summ1.avbay1_1.setText("0.0");
    	#p_dps_sm_sys_summ1.avbay1_2.setText("0.0");

    	#p_dps_sm_sys_summ1.avbay2_1.setText("0.0");
    	#p_dps_sm_sys_summ1.avbay2_2.setText("0.0");

    	#p_dps_sm_sys_summ1.avbay3_1.setText("0.0");
    	#p_dps_sm_sys_summ1.avbay3_2.setText("0.0");

	p_dps_sm_sys_summ1.eq.setText(" +0.000");


    }
    
    p_dps_sm_sys_summ1.update = func
    {

	p_dps_sm_sys_summ1.major_function = SpaceShuttle.idp_array[device.port_selected-1].get_major_function(); # For BFS differences (major function 4)

	# smoke detection

   	p_dps_sm_sys_summ1.cabin.updateText(sprintf("%4.1f", SpaceShuttle.fire_sim.smoke_cabin + 0.1 ));

    	p_dps_sm_sys_summ1.lr_1.updateText(sprintf("%4.1f", SpaceShuttle.fire_sim.smoke_flightdeck + 0.2 ));
    	p_dps_sm_sys_summ1.lr_2.updateText(sprintf("%4.1f", SpaceShuttle.fire_sim.smoke_flightdeck ));

    	p_dps_sm_sys_summ1.avbay1_1.updateText(sprintf("%4.1f", SpaceShuttle.fire_sim.smoke_avbay1 + 0.2 ));
    	p_dps_sm_sys_summ1.avbay1_2.updateText(sprintf("%4.1f", SpaceShuttle.fire_sim.smoke_avbay1 + 0.1));

    	p_dps_sm_sys_summ1.avbay2_1.updateText(sprintf("%4.1f", SpaceShuttle.fire_sim.smoke_avbay2 + 0.1));
    	p_dps_sm_sys_summ1.avbay2_2.updateText(sprintf("%4.1f", SpaceShuttle.fire_sim.smoke_avbay2 + 0.1));

    	p_dps_sm_sys_summ1.avbay3_1.updateText(sprintf("%4.1f", SpaceShuttle.fire_sim.smoke_avbay3 ));
    	p_dps_sm_sys_summ1.avbay3_2.updateText(sprintf("%4.1f", SpaceShuttle.fire_sim.smoke_avbay3 + 0.2));

	# fuel cell voltages    
		#Clamp for high values in case of shortcut to avoid display problem, plus addition of H( high) letters yellow right of the higher limit
		#No need for  lower limit as it will go to 0 anyway and not lower

	var fc_voltage1 = getprop("/fdm/jsbsim/systems/electrical/fc/voltage");
	var fc_voltage2 = getprop("/fdm/jsbsim/systems/electrical/fc[1]/voltage");
	var fc_voltage3 = getprop("/fdm/jsbsim/systems/electrical/fc[2]/voltage");

	#fc_voltage1 = SpaceShuttle.clamp(fc_voltage1, 0, 40);
	#fc_voltage2 = SpaceShuttle.clamp(fc_voltage2, 0, 40);
	#fc_voltage3 = SpaceShuttle.clamp(fc_voltage3, 0, 40);

	var bus_connector1 = getprop("/fdm/jsbsim/systems/electrical/fc/bus-connector-status");
	var bus_connector2 = getprop("/fdm/jsbsim/systems/electrical/fc[1]/bus-connector-status");
	var bus_connector3 = getprop("/fdm/jsbsim/systems/electrical/fc[2]/bus-connector-status");

	var power_usage1 = getprop("/fdm/jsbsim/systems/electrical/bus/power-demand-kW") * 1000.0;
	var power_usage2 = getprop("/fdm/jsbsim/systems/electrical/bus[1]/power-demand-kW") * 1000.0;
	var power_usage3 = getprop("/fdm/jsbsim/systems/electrical/bus[2]/power-demand-kW") * 1000.0;

	power_usage1 = SpaceShuttle.clamp(power_usage1, 0, 5000); #Watts
	power_usage2 = SpaceShuttle.clamp(power_usage2, 0, 5000);
	power_usage3 = SpaceShuttle.clamp(power_usage3, 0, 5000);

	var fc_amps1 = power_usage1/fc_voltage1 * bus_connector1;
	var fc_amps2 = power_usage2/fc_voltage2 * bus_connector2;
	var fc_amps3 = power_usage3/fc_voltage3 * bus_connector3;

	if (fc_voltage1 == 0.0) {fc_amps1 = 0.0;}
	if (fc_voltage2 == 0.0) {fc_amps2 = 0.0;}
	if (fc_voltage3 == 0.0) {fc_amps3 = 0.0;}

	

    	p_dps_sm_sys_summ1.volts_fc1.setText(sprintf("%4.1f", fc_voltage1 ));
    	p_dps_sm_sys_summ1.volts_fc2.setText(sprintf("%4.1f", fc_voltage2 ));
    	p_dps_sm_sys_summ1.volts_fc3.setText(sprintf("%4.1f", fc_voltage3 ));

    	p_dps_sm_sys_summ1.amps_fc1.setText(sprintf("%3.0f", SpaceShuttle.clamp(fc_amps1, 0, 500)));
    	p_dps_sm_sys_summ1.amps_fc2.setText(sprintf("%3.0f", SpaceShuttle.clamp(fc_amps2, 0, 500)));
    	p_dps_sm_sys_summ1.amps_fc3.setText(sprintf("%3.0f", SpaceShuttle.clamp(fc_amps3, 0, 500)));

	

	
	

	var voltage_mainA = getprop("/fdm/jsbsim/systems/electrical/bus/voltage");
	var voltage_mainB = getprop("/fdm/jsbsim/systems/electrical/bus[1]/voltage");
	var voltage_mainC = getprop("/fdm/jsbsim/systems/electrical/bus[2]/voltage");

	#voltage_mainA  = SpaceShuttle.clamp(voltage_mainA , 0, 40);
	#voltage_mainB  = SpaceShuttle.clamp(voltage_mainB , 0, 40);
	#voltage_mainC  = SpaceShuttle.clamp(voltage_mainC , 0, 40);

	var voltage_essential1 = getprop("/fdm/jsbsim/systems/electrical/ess/voltage");
	var voltage_essential2 = getprop("/fdm/jsbsim/systems/electrical/ess[1]/voltage");
	var voltage_essential3 = getprop("/fdm/jsbsim/systems/electrical/ess[2]/voltage");

	#voltage_essential1  = SpaceShuttle.clamp(voltage_essential1 , 0, 40);
	#voltage_essential2  = SpaceShuttle.clamp(voltage_essential2 , 0, 40);
	#voltage_essential3  = SpaceShuttle.clamp(voltage_essential3 , 0, 40);

	p_dps_sm_sys_summ1.volts_mn1.setText(sprintf("%4.1f", voltage_mainA ));
	p_dps_sm_sys_summ1.volts_mn2.setText(sprintf("%4.1f", voltage_mainB ));
	p_dps_sm_sys_summ1.volts_mn3.setText(sprintf("%4.1f", voltage_mainC ));

    	p_dps_sm_sys_summ1.volts_ess1.setText(sprintf("%4.1f", voltage_essential1 ));
    	p_dps_sm_sys_summ1.volts_ess2.setText(sprintf("%4.1f", voltage_essential2 ));
    	p_dps_sm_sys_summ1.volts_ess3.setText(sprintf("%4.1f", voltage_essential3 ));

	p_dps_sm_sys_summ1.volts_cntl1_1.setText(sprintf("%5.1f", voltage_essential1 * 0.991));
	p_dps_sm_sys_summ1.volts_cntl1_2.setText(sprintf("%5.1f", voltage_essential2 * 0.991));
	p_dps_sm_sys_summ1.volts_cntl1_3.setText(sprintf("%5.1f", voltage_essential3 * 0.991));

	p_dps_sm_sys_summ1.volts_cntl2_1.setText(sprintf("%5.1f", voltage_essential1 * 0.991));
	p_dps_sm_sys_summ1.volts_cntl2_2.setText(sprintf("%5.1f", voltage_essential2 * 0.991));
	p_dps_sm_sys_summ1.volts_cntl2_3.setText(sprintf("%5.1f", voltage_essential3 * 0.991));

	p_dps_sm_sys_summ1.volts_cntl3_1.setText(sprintf("%5.1f", voltage_essential1 * 0.991));
	p_dps_sm_sys_summ1.volts_cntl3_2.setText(sprintf("%5.1f", voltage_essential2 * 0.991));
	p_dps_sm_sys_summ1.volts_cntl3_3.setText(sprintf("%5.1f", voltage_essential3 * 0.991));


	


	



	var voltage_ac1 = getprop("/fdm/jsbsim/systems/electrical/ac/voltage");
	var voltage_ac2 = getprop("/fdm/jsbsim/systems/electrical/ac[1]/voltage");
	var voltage_ac3 = getprop("/fdm/jsbsim/systems/electrical/ac[2]/voltage");

	#voltage_ac1 = SpaceShuttle.clamp(voltage_ac1, 0, 140);
	#voltage_ac2 = SpaceShuttle.clamp(voltage_ac2, 0, 140);
	#voltage_ac3 = SpaceShuttle.clamp(voltage_ac3, 0, 140);

	var power_ac1 = getprop("/fdm/jsbsim/systems/electrical/ac/power-demand-kW");
	var power_ac2 = getprop("/fdm/jsbsim/systems/electrical/ac[1]/power-demand-kW");
	var power_ac3 = getprop("/fdm/jsbsim/systems/electrical/ac[2]/power-demand-kW");

	var amps_ac1 = power_ac1 * 1000.0 /voltage_ac1;
	var amps_ac2 = power_ac2 * 1000.0 /voltage_ac2;
	var amps_ac3 = power_ac3 * 1000.0 /voltage_ac3;

	if (voltage_ac1 == 0.0) {amps_ac1 = 0.0;}
	if (voltage_ac2 == 0.0) {amps_ac2 = 0.0;}
	if (voltage_ac3 == 0.0) {amps_ac3 = 0.0;}

	#amps_ac1 = SpaceShuttle.clamp(amps_ac1, 0, 20);
	#amps_ac2 = SpaceShuttle.clamp(amps_ac2, 0, 20);
	#amps_ac3 = SpaceShuttle.clamp(amps_ac3, 0, 20);

 	p_dps_sm_sys_summ1.volt_phiA_1.setText(sprintf("%3.0f", voltage_ac1));
 	p_dps_sm_sys_summ1.volt_phiA_2.setText(sprintf("%3.0f", voltage_ac2));
 	p_dps_sm_sys_summ1.volt_phiA_3.setText(sprintf("%3.0f", voltage_ac3));

 	p_dps_sm_sys_summ1.volt_phiB_1.setText(sprintf("%3.0f", voltage_ac1));
 	p_dps_sm_sys_summ1.volt_phiB_2.setText(sprintf("%3.0f", voltage_ac2));
 	p_dps_sm_sys_summ1.volt_phiB_3.setText(sprintf("%3.0f", voltage_ac3));

 	p_dps_sm_sys_summ1.volt_phiC_1.setText(sprintf("%3.0f", voltage_ac1));
 	p_dps_sm_sys_summ1.volt_phiC_2.setText(sprintf("%3.0f", voltage_ac2));
 	p_dps_sm_sys_summ1.volt_phiC_3.setText(sprintf("%3.0f", voltage_ac3));

 	p_dps_sm_sys_summ1.amps_phiA_1.setText(sprintf("%4.1f", amps_ac1/3.));
 	p_dps_sm_sys_summ1.amps_phiA_2.setText(sprintf("%4.1f", amps_ac2/3.));
 	p_dps_sm_sys_summ1.amps_phiA_3.setText(sprintf("%4.1f", amps_ac3/3.));

 	p_dps_sm_sys_summ1.amps_phiB_1.setText(sprintf("%4.1f", amps_ac1/3.));
 	p_dps_sm_sys_summ1.amps_phiB_2.setText(sprintf("%4.1f", amps_ac2/3.));
 	p_dps_sm_sys_summ1.amps_phiB_3.setText(sprintf("%4.1f", amps_ac3/3.));

 	p_dps_sm_sys_summ1.amps_phiC_1.setText(sprintf("%4.1f", amps_ac1/3.));
 	p_dps_sm_sys_summ1.amps_phiC_2.setText(sprintf("%4.1f", amps_ac2/3.));
 	p_dps_sm_sys_summ1.amps_phiC_3.setText(sprintf("%4.1f", amps_ac3/3.));

	




	var fc1_factor = fc_voltage1 / 30.0;
	var fc2_factor = fc_voltage2 / 30.0;
	var fc3_factor = fc_voltage3 / 30.0;


	p_dps_sm_sys_summ1.DVSS1_1.setText(sprintf("%3.0f", 15 * fc1_factor ));
	p_dps_sm_sys_summ1.DVSS2_1.setText(sprintf("%3.0f", 12 * fc1_factor ));
	p_dps_sm_sys_summ1.DVSS3_1.setText(sprintf("%3.0f", 21 * fc1_factor ));

	p_dps_sm_sys_summ1.DVSS1_2.setText(sprintf("%3.0f", 20 * fc2_factor ));
	p_dps_sm_sys_summ1.DVSS2_2.setText(sprintf("%3.0f", 16 * fc2_factor ));
	p_dps_sm_sys_summ1.DVSS3_2.setText(sprintf("%3.0f", 17 * fc2_factor ));

	p_dps_sm_sys_summ1.DVSS1_3.setText(sprintf("%3.0f", 14 * fc3_factor ));
	p_dps_sm_sys_summ1.DVSS2_3.setText(sprintf("%3.0f", 13 * fc3_factor ));
	p_dps_sm_sys_summ1.DVSS3_3.setText(sprintf("%3.0f", 16 * fc3_factor ));



	


 

	var stack_T1 = K_to_F (getprop("/fdm/jsbsim/systems/electrical/fc/stack-temperature-K"));
	var stack_T2 = K_to_F (getprop("/fdm/jsbsim/systems/electrical/fc[1]/stack-temperature-K"));
	var stack_T3 = K_to_F (getprop("/fdm/jsbsim/systems/electrical/fc[2]/stack-temperature-K"));

	stack_T1 = SpaceShuttle.clamp(stack_T1, -75, 300);
	stack_T2 = SpaceShuttle.clamp(stack_T2, -75, 300);
	stack_T3 = SpaceShuttle.clamp(stack_T3, -75, 300);

 	p_dps_sm_sys_summ1.stackT_1.setText(sprintf("%+4.0f", stack_T1 ));
 	p_dps_sm_sys_summ1.stackT_2.setText(sprintf("%+4.0f", stack_T2 ));
 	p_dps_sm_sys_summ1.stackT_3.setText(sprintf("%+4.0f", stack_T3 ));

	 





	var running1 = getprop("/fdm/jsbsim/systems/electrical/fc/fc-running");
	var running2 = getprop("/fdm/jsbsim/systems/electrical/fc[1]/fc-running");
	var running3 = getprop("/fdm/jsbsim/systems/electrical/fc[2]/fc-running");

	var condition1 = getprop("/fdm/jsbsim/systems/failures/fc1-coolant-pump-condition");
	var condition2 = getprop("/fdm/jsbsim/systems/failures/fc2-coolant-pump-condition");
	var condition3 = getprop("/fdm/jsbsim/systems/failures/fc3-coolant-pump-condition");
	
	var coolp1 = 61.0 * condition1 * running1;
	var coolp2 = 61.0 * condition2 * running2;
	var coolp3 = 61.0 * condition3 * running3;

	p_dps_sm_sys_summ1.coolp_1.setText(sprintf("%3.0f", coolp1));
	p_dps_sm_sys_summ1.coolp_2.setText(sprintf("%3.0f", coolp2));
	p_dps_sm_sys_summ1.coolp_3.setText(sprintf("%3.0f", coolp3));

	




	var coolant_T = K_to_F(getprop("/fdm/jsbsim/systems/thermal-distribution/freon-out-temperature-K"));

	if ((running1 == 1) and (coolant_T < (stack_T1 - 60.0)) and (stack_T1 != 300)) {exitT1 = 151.0;}  #If stack temp = 300 ( max temp, hence exit temp at limit also, FC out of control)
	else {exitT1 = stack_T1;}

	if ((running2 == 1) and (coolant_T < (stack_T2 - 60.0)) and (stack_T2 != 300)) {exitT2 = 153.0;}
	else {exitT2 = stack_T2;}

	if ((running3 == 1) and (coolant_T < (stack_T3 - 60.0)) and (stack_T3 != 300)) {exitT3 = 150.0;}
	else {exitT3 = stack_T3;}

	p_dps_sm_sys_summ1.exitT_1.setText(sprintf("%3.0f", SpaceShuttle.clamp(exitT1, 0, 250)));
	p_dps_sm_sys_summ1.exitT_2.setText(sprintf("%3.0f", SpaceShuttle.clamp(exitT2, 0, 250)));
	p_dps_sm_sys_summ1.exitT_3.setText(sprintf("%3.0f", SpaceShuttle.clamp(exitT3, 0, 250)));

	
	


	var reac_valve_1_status = getprop("/fdm/jsbsim/systems/electrical/fc/reactant-valve-status");
	var reac_valve_2_status = getprop("/fdm/jsbsim/systems/electrical/fc[1]/reactant-valve-status");
	var reac_valve_3_status = getprop("/fdm/jsbsim/systems/electrical/fc[2]/reactant-valve-status");

	p_dps_sm_sys_summ1.reac_vlv_1.setText(valve_status_to_string(reac_valve_1_status));
	p_dps_sm_sys_summ1.reac_vlv_2.setText(valve_status_to_string(reac_valve_2_status));
	p_dps_sm_sys_summ1.reac_vlv_3.setText(valve_status_to_string(reac_valve_3_status));

	
	#We do here some indicators to avoid to repeat those conditionnals
	#Indicators for Fc Coolant Pump 


	var string = "ΔP";
	if ((running1 == 1) and (condition1 > 0.3)) {string= ""; p_dps_sm_sys_summ1.pump1_arrow.updateText("");}
	else {p_dps_sm_sys_summ1.pump1_arrow.updateText("↓");}
 	p_dps_sm_sys_summ1.pump1.setText(string);

	string = "ΔP";
	if ((running2 == 1) and (condition2 > 0.3)) {string= ""; p_dps_sm_sys_summ1.pump2_arrow.updateText("");}
	else {p_dps_sm_sys_summ1.pump2_arrow.updateText("↓");}
 	p_dps_sm_sys_summ1.pump2.setText(string);

	string = "ΔP";
	if ((running3 == 1) and (condition3 > 0.3)) {string= ""; p_dps_sm_sys_summ1.pump3_arrow.updateText("");}
	else {p_dps_sm_sys_summ1.pump3_arrow.updateText("↓");}
 	p_dps_sm_sys_summ1.pump3.setText(string);

	


	var total_power_kw = getprop("/fdm/jsbsim/systems/electrical/total-power-demand-kW");
	total_power_kw = SpaceShuttle.clamp(total_power_kw, 0, 60);

	var total_amps = fc_amps1 + fc_amps2 + fc_amps3;
	total_amps = SpaceShuttle.clamp(total_amps, 0, 1500);

	p_dps_sm_sys_summ1.kW.setText(sprintf("%2.0f", total_power_kw)); 	
	p_dps_sm_sys_summ1.total_amps.setText(sprintf("%4.0f", total_amps));


	


	# oxygen system

	var airflow_in = getprop("/fdm/jsbsim/systems/eclss/cabin/air-gain-rate-lb_h");

	var o2_valve1 = getprop("/fdm/jsbsim/systems/eclss/oxygen/sys1-o2-supply-valve-status");
	var o2_valve2 = getprop("/fdm/jsbsim/systems/eclss/oxygen/sys2-o2-supply-valve-status");

	var oxygen_flow = getprop("/fdm/jsbsim/systems/eclss/cabin/oxygen-in-fraction-av") * airflow_in;
	
	if ((o2_valve1 == 1) and (o2_valve2 == 1)) {oxygen_flow = 0.5 * oxygen_flow;}

	var o2flow_1_value = oxygen_flow * o2_valve1;
	var o2flow_2_value = oxygen_flow * o2_valve2;

	o2flow_1_value = SpaceShuttle.clamp(o2flow_1_value, 0, 5);
	o2flow_2_value = SpaceShuttle.clamp(o2flow_2_value, 0, 5);

 	p_dps_sm_sys_summ1.o2flow_1.setText(sprintf("%4.1f", o2flow_1_value)); 	
	p_dps_sm_sys_summ1.o2flow_2.setText(sprintf("%4.1f", o2flow_2_value)); 

	


	# nitrogen system

	var n2_valve1 = getprop("/fdm/jsbsim/systems/eclss/nitrogen/sys1-pressurized");
	var n2_valve2 = getprop("/fdm/jsbsim/systems/eclss/nitrogen/sys2-pressurized");

	var nitrogen_flow = getprop("/fdm/jsbsim/systems/eclss/cabin/nitrogen-in-fraction-av") * airflow_in;

	if ((n2_valve1 == 1) and (n2_valve2 == 1)) {nitrogen_flow = 0.5 * nitrogen_flow;}

	var n2flow_1_value = nitrogen_flow * n2_valve1;
	var n2flow_2_value = nitrogen_flow * n2_valve2;

	n2flow_1_value = SpaceShuttle.clamp(n2flow_1_value, 0, 5);
	n2flow_2_value = SpaceShuttle.clamp(n2flow_2_value, 0, 5);

    p_dps_sm_sys_summ1.n2flow_1.setText(sprintf("%4.1f", n2flow_1_value));
    p_dps_sm_sys_summ1.n2flow_2.setText(sprintf("%4.1f", n2flow_2_value));

	


	# pressures

	var ppo2 = getprop("/fdm/jsbsim/systems/eclss/cabin/ppo2-psi"); #Lower limit reached when depress ( 2.7 ↓ and 0 L)

	p_dps_sm_sys_summ1.ppo2_1.setText(sprintf("%4.2f", ppo2));
	p_dps_sm_sys_summ1.ppo2_2.setText(sprintf("%4.2f", ppo2));

	

	p_dps_sm_sys_summ1.o2_conc.setText(sprintf("%4.1f", getprop("/fdm/jsbsim/systems/eclss/cabin/oxygen-fraction") * 100.0)); #Just high limit ( 26 %) never reached

	
	var press_cabin = getprop("/fdm/jsbsim/systems/eclss/cabin/air-pressure-psi");

	p_dps_sm_sys_summ1.press.setText(sprintf("%5.2f", press_cabin));

	

	# pressure change

	var dpdt_value = getprop("/fdm/jsbsim/systems/eclss/cabin/air-pressure-change-psi_s") * 60;
	dpdt_value = SpaceShuttle.clamp(dpdt_value, -0.55, 0.45);

 	p_dps_sm_sys_summ1.dPdt.setText(sprintf("%+5.2f", dpdt_value));

	 


	# IMU fans

	var imu_fanA_op = getprop("/fdm/jsbsim/systems/eclss/avbay/imu-fan-A-operational");
	var imu_fanB_op = getprop("/fdm/jsbsim/systems/eclss/avbay/imu-fan-B-operational");
	var imu_fanC_op = getprop("/fdm/jsbsim/systems/eclss/avbay/imu-fan-C-operational");

	var imu_fanA_sw = getprop("/fdm/jsbsim/systems/eclss/avbay/imu-fan-A-switch");
	var imu_fanB_sw = getprop("/fdm/jsbsim/systems/eclss/avbay/imu-fan-B-switch");
	var imu_fanC_sw = getprop("/fdm/jsbsim/systems/eclss/avbay/imu-fan-C-switch");

	var sym = "*";
	if (imu_fanA_op == 0){sym = "";}
	p_dps_sm_sys_summ1.imu_A.setText(sym);

	sym = "*";
	if (imu_fanB_op == 0){sym = "";}
	p_dps_sm_sys_summ1.imu_B.setText(sym);

	sym = "*";
	if (imu_fanC_op == 0){sym = "";}
	p_dps_sm_sys_summ1.imu_C.setText(sym);


	# IMU Delta P for BFS (avoid to call back var later on)

	var imu_dp = imu_fanA_op + imu_fanB_op + imu_fanC_op;

	if (imu_dp > 2.0) {imu_dp = 6.5;}
	else if (imu_dp > 1.0) {imu_dp = 5.3;}
	else if (imu_dp >0.0) {imu_dp = 4.5;}
	else imu_dp = 0;

	p_dps_sm_sys_summ1.imu_bfs_deltaP_value.setText(sprintf("%4.2f", imu_dp));


	# cabin fan dp

	var fan_A = getprop("/fdm/jsbsim/systems/eclss/cabin/fan-A-operational");
	var fan_B = getprop("/fdm/jsbsim/systems/eclss/cabin/fan-B-operational");

	var cabin_dp = fan_A + fan_B;
	
	if (cabin_dp > 1.0) {cabin_dp = 6.61;}
	else if (cabin_dp > 0.0) {cabin_dp = 5.54;}
	else {cabin_dp = 0.0;}
	
	p_dps_sm_sys_summ1.fan_dp.setText(sprintf("%4.2f", cabin_dp));

	



	# heat exchanger T
	
	var cabin_T =  K_to_F(getprop("/fdm/jsbsim/systems/thermal-distribution/interior-temperature-K"));
	p_dps_sm_sys_summ1.hx_out_T.setText(sprintf("%3.0f", cabin_T + 30.0));



	#SM realistic option with indicators

	if (SpaceShuttle.sm_simulation_detail_level == 1)
		{

		p_dps_sm_sys_summ1.arrow_group.setVisible(1);
		#Fc Amps higher limit indicator (H)

	if (fc_amps1 > 499) {p_dps_sm_sys_summ1.amps_fc1_arrow.updateText("H");}
	else if (fc_amps1 == 0) {p_dps_sm_sys_summ1.amps_fc1_arrow.updateText("L");}
	else {p_dps_sm_sys_summ1.amps_fc1_arrow.updateText("");}

	if (fc_amps2 > 499) {p_dps_sm_sys_summ1.amps_fc2_arrow.updateText("H");}
	else if (fc_amps2 == 0) {p_dps_sm_sys_summ1.amps_fc2_arrow.updateText("L");}
	else {p_dps_sm_sys_summ1.amps_fc2_arrow.updateText("");}

	if (fc_amps3 > 499) {p_dps_sm_sys_summ1.amps_fc3_arrow.updateText("H");}
	else if (fc_amps3 == 0) {p_dps_sm_sys_summ1.amps_fc3_arrow.updateText("L");}
	else {p_dps_sm_sys_summ1.amps_fc3_arrow.updateText("");}



		#Main bus volts lower indicator (L)

	if (voltage_mainA == 0) {p_dps_sm_sys_summ1.volts_mn1_arrow.updateText("L");}
	else if ((voltage_mainA > 0) and (voltage_mainA < 27)) {p_dps_sm_sys_summ1.volts_mn1_arrow.updateText("↓");}
	else if (voltage_mainA > 32) {p_dps_sm_sys_summ1.volts_mn1_arrow.updateText("↑");}
	else {p_dps_sm_sys_summ1.volts_mn1_arrow.updateText("");}

	if (voltage_mainB == 0) {p_dps_sm_sys_summ1.volts_mn2_arrow.updateText("L");}
	else if ((voltage_mainB > 0) and (voltage_mainB < 27)) {p_dps_sm_sys_summ1.volts_mn2_arrow.updateText("↓");}
	else if (voltage_mainB > 32) {p_dps_sm_sys_summ1.volts_mn2_arrow.updateText("↑");}
	else {p_dps_sm_sys_summ1.volts_mn2_arrow.updateText("");}

	if (voltage_mainC == 0) {p_dps_sm_sys_summ1.volts_mn3_arrow.updateText("L");}
	else if ((voltage_mainC > 0) and (voltage_mainC < 27)) {p_dps_sm_sys_summ1.volts_mn3_arrow.updateText("↓");}
	else if (voltage_mainC > 32) {p_dps_sm_sys_summ1.volts_mn3_arrow.updateText("↑");}
	else {p_dps_sm_sys_summ1.volts_mn3_arrow.updateText("");}


	#Ess buses always powered (no L/H relevant here), but can drop below 28 V in case of severe failures and cross tie (↓)

	if (voltage_essential1 < 28) {p_dps_sm_sys_summ1.volts_ess1_arrow.updateText("↓");}
	else {p_dps_sm_sys_summ1.volts_ess1_arrow.updateText("");}

	if (voltage_essential2 < 28) {p_dps_sm_sys_summ1.volts_ess2_arrow.updateText("↓");}
	else {p_dps_sm_sys_summ1.volts_ess2_arrow.updateText("");}

	if (voltage_essential3 < 28) {p_dps_sm_sys_summ1.volts_ess3_arrow.updateText("↓");}
	else {p_dps_sm_sys_summ1.volts_ess3_arrow.updateText("");}



		#Ac volts and amps lower values (L)

	if (voltage_ac1 == 0)
		{
		p_dps_sm_sys_summ1.arrow_group_AC1_subgroup.setVisible(1);
		}
	else	
		{
		p_dps_sm_sys_summ1.arrow_group_AC1_subgroup.setVisible(0);
		}

	if (voltage_ac2 == 0)
		{
		p_dps_sm_sys_summ1.arrow_group_AC2_subgroup.setVisible(1);
		}
	else	
		{
		p_dps_sm_sys_summ1.arrow_group_AC2_subgroup.setVisible(0);
		}

	if (voltage_ac3 == 0)
		{
		p_dps_sm_sys_summ1.arrow_group_AC3_subgroup.setVisible(1);
		}
	else	
		{
		p_dps_sm_sys_summ1.arrow_group_AC3_subgroup.setVisible(0);
		}


		#Delta Volt substacks lower limit (L)
	#FC Volts lower limit indicator (L)

	if (fc_voltage1 == 0)
		{
		p_dps_sm_sys_summ1.volts_fc_arrow.updateText("L");
		p_dps_sm_sys_summ1.arrow_group_DVSS1_subgroup.setVisible(1);
		}
	else if (fc_voltage1 > 32) 
		{
		p_dps_sm_sys_summ1.volts_fc_arrow.updateText("↑");
		}
	else if ((fc_voltage1 > 0) and (fc_voltage1 < 27.5)) 
		{
		p_dps_sm_sys_summ1.volts_fc_arrow.updateText("↓");
		}
	else
		{
		p_dps_sm_sys_summ1.volts_fc_arrow.updateText("");
		p_dps_sm_sys_summ1.arrow_group_DVSS1_subgroup.setVisible(0);
		}
	
	if (fc_voltage2 == 0)
		{
		p_dps_sm_sys_summ1.volts_fc2_arrow.updateText("L");
		p_dps_sm_sys_summ1.arrow_group_DVSS2_subgroup.setVisible(1);
		}
	else if (fc_voltage2 > 32) 
		{
		p_dps_sm_sys_summ1.volts_fc2_arrow.updateText("↑");
		}
	else if ((fc_voltage2 > 0) and (fc_voltage2 < 27.5)) 
		{
		p_dps_sm_sys_summ1.volts_fc2_arrow.updateText("↓");
		}
	else
		{
		p_dps_sm_sys_summ1.volts_fc2_arrow.updateText("");
		p_dps_sm_sys_summ1.arrow_group_DVSS2_subgroup.setVisible(0);
		}

	if (fc_voltage3 == 0)
		{
		p_dps_sm_sys_summ1.volts_fc3_arrow.updateText("L");
		p_dps_sm_sys_summ1.arrow_group_DVSS3_subgroup.setVisible(1);
		}
	else if (fc_voltage3 > 32) 
		{
		p_dps_sm_sys_summ1.volts_fc3_arrow.updateText("↑");
		}
	else if ((fc_voltage3 > 0) and (fc_voltage3 < 27.5)) 
		{
		p_dps_sm_sys_summ1.volts_fc3_arrow.updateText("↓");
		}
	else
		{
		p_dps_sm_sys_summ1.volts_fc3_arrow.updateText("");
		p_dps_sm_sys_summ1.arrow_group_DVSS3_subgroup.setVisible(0);
		}

		#Stack temp Higher limit indicator (H)

	 if (stack_T1 == 300) {p_dps_sm_sys_summ1.stackT_1_arrow.updateText("H");}
	 else if ((stack_T1 > 212) and (stack_T1 < 300)) {p_dps_sm_sys_summ1.stackT_1_arrow.updateText("↑");} #Temp depends on Kw normally// in Sim 212° is a good value for high stack temp leading to failures
	 else if (stack_T1 < 180) {p_dps_sm_sys_summ1.stackT_1_arrow.updateText("↓");}
	 else {p_dps_sm_sys_summ1.stackT_1_arrow.updateText("");}

	 if (stack_T2 == 300) {p_dps_sm_sys_summ1.stackT_2_arrow.updateText("H");}
	 else if ((stack_T2 > 212) and (stack_T2 < 300)) {p_dps_sm_sys_summ1.stackT_2_arrow.updateText("↑");}
	 else if (stack_T2 < 180) {p_dps_sm_sys_summ1.stackT_2_arrow.updateText("↓");}
	 else {p_dps_sm_sys_summ1.stackT_2_arrow.updateText("");}

	 if (stack_T3 == 300) {p_dps_sm_sys_summ1.stackT_3_arrow.updateText("H");}
	 else if ((stack_T3 > 212) and (stack_T3 < 300)) {p_dps_sm_sys_summ1.stackT_3_arrow.updateText("↑");}
	 else if (stack_T3 < 180) {p_dps_sm_sys_summ1.stackT_3_arrow.updateText("↓");}
	 else {p_dps_sm_sys_summ1.stackT_3_arrow.updateText("");}



	 	#Coolant Pump pressure lower value (L)

	if (coolp1 == 0) {p_dps_sm_sys_summ1.coolp_1_arrow.updateText("L");}
	else {p_dps_sm_sys_summ1.coolp_1_arrow.updateText("");}

	if (coolp2 == 0) {p_dps_sm_sys_summ1.coolp_2_arrow.updateText("L");}
	else {p_dps_sm_sys_summ1.coolp_2_arrow.updateText("");}

	if (coolp3 == 0) {p_dps_sm_sys_summ1.coolp_3_arrow.updateText("L");}
	else {p_dps_sm_sys_summ1.coolp_3_arrow.updateText("");}



		#Exit Temp higher value indicator (H) ( As it varies with stack T, we might merge the two to avoid an useless test)

	if (exitT1 > 240) {p_dps_sm_sys_summ1.exitT_1_arrow.updateText("H");}
	if (exitT1 < 131) {p_dps_sm_sys_summ1.exitT_1_arrow.updateText("↓");}
	else {p_dps_sm_sys_summ1.exitT_1_arrow.updateText("");}

	if (exitT2 > 240) {p_dps_sm_sys_summ1.exitT_2_arrow.updateText("H");}
	if (exitT2 < 131) {p_dps_sm_sys_summ1.exitT_2_arrow.updateText("↓");}
	else {p_dps_sm_sys_summ1.exitT_2_arrow.updateText("");}

	if (exitT3 > 240) {p_dps_sm_sys_summ1.exitT_3_arrow.updateText("H");}
	if (exitT3 < 131) {p_dps_sm_sys_summ1.exitT_3_arrow.updateText("↓");}
	else {p_dps_sm_sys_summ1.exitT_3_arrow.updateText("");}


		#Reac valve closed arrow ↓

	if (reac_valve_1_status == 0) {p_dps_sm_sys_summ1.reac_vlv_1_arrow.updateText("↓");}
	else {p_dps_sm_sys_summ1.reac_vlv_1_arrow.updateText("");}

	if (reac_valve_2_status == 0) {p_dps_sm_sys_summ1.reac_vlv_2_arrow.updateText("↓");}
	else {p_dps_sm_sys_summ1.reac_vlv_2_arrow.updateText("");}

	if (reac_valve_3_status == 0) {p_dps_sm_sys_summ1.reac_vlv_3_arrow.updateText("↓");}
	else {p_dps_sm_sys_summ1.reac_vlv_3_arrow.updateText("");}


	#Pump inop indicator (↓) (line 660)


	#Kw and total amps higher value indicator ( H)

	if (total_power_kw > 59) {p_dps_sm_sys_summ1.kW_arrow.updateText("H");}
	else if ((total_power_kw > 40) and (total_power_kw < 59)) {p_dps_sm_sys_summ1.kW_arrow.updateText("↑");}
	else {p_dps_sm_sys_summ1.kW_arrow.updateText("");}

	if (total_amps == 1500) {p_dps_sm_sys_summ1.total_amps_arrow.updateText("H");}
	else if ((total_amps > 1000) and (total_amps < 1500)) {p_dps_sm_sys_summ1.total_amps_arrow.updateText("↑");}
	else {p_dps_sm_sys_summ1.total_amps_arrow.updateText("");}



	#N2/O2 system

	if (o2flow_1_value == 0) {p_dps_sm_sys_summ1.o2flow_1_arrow.updateText("L");}
	else if (o2flow_1_value == 5) {p_dps_sm_sys_summ1.o2flow_1_arrow.updateText("H");}
	else {p_dps_sm_sys_summ1.o2flow_1_arrow.updateText("");}

	if (o2flow_2_value == 0) {p_dps_sm_sys_summ1.o2flow_2_arrow.updateText("L");}
	else if (o2flow_2_value == 5) {p_dps_sm_sys_summ1.o2flow_2_arrow.updateText("H");}
	else {p_dps_sm_sys_summ1.o2flow_2_arrow.updateText("");}



	if (n2flow_1_value == 0) {p_dps_sm_sys_summ1.n2flow_1_arrow.updateText("L");}
	else if (n2flow_1_value == 5) {p_dps_sm_sys_summ1.n2flow_1_arrow.updateText("H");}
	else {p_dps_sm_sys_summ1.n2flow_1_arrow.updateText("");}

	if (n2flow_2_value == 0) {p_dps_sm_sys_summ1.n2flow_2_arrow.updateText("L");}
	else if (n2flow_2_value == 5) {p_dps_sm_sys_summ1.n2flow_2_arrow.updateText("H");}
	else {p_dps_sm_sys_summ1.n2flow_2_arrow.updateText("");}



	#PPO2 and Cabin pressure

	if (ppo2 < 0.01)
		{
		p_dps_sm_sys_summ1.ppo2_1_arrow.updateText("L");
		p_dps_sm_sys_summ1.ppo2_2_arrow.updateText("L");
		}
	else if ((ppo2 > 0.01) and (ppo2 < 2.70))
		{
		p_dps_sm_sys_summ1.ppo2_1_arrow.updateText("↓");
		p_dps_sm_sys_summ1.ppo2_2_arrow.updateText("↓");
		}
	else 
		{
		p_dps_sm_sys_summ1.ppo2_1_arrow.updateText("");
		p_dps_sm_sys_summ1.ppo2_2_arrow.updateText("");
		}


	if (press_cabin < 0.05) {p_dps_sm_sys_summ1.press_arrow.updateText("L");}
	else if ((press_cabin > 0.05) and (press_cabin < 13.8)) {p_dps_sm_sys_summ1.press_arrow.updateText("↓");}
	else {p_dps_sm_sys_summ1.press_arrow.updateText("");}


	#Cabin fan DP

	if (cabin_dp == 0) {p_dps_sm_sys_summ1.fan_dp_arrow.updateText("L");}
	else {p_dps_sm_sys_summ1.fan_dp_arrow.updateText("");}
	
	#Pressure change

	if (dpdt_value == -0.55) {p_dps_sm_sys_summ1.dPdt_arrow.updateText("L");}
	else if ((dpdt_value > -0.55) and (dpdt_value < -0.12)) {p_dps_sm_sys_summ1.dPdt_arrow.updateText("↓");}
	else if (dpdt_value == 0.45) {p_dps_sm_sys_summ1.dPdt_arrow.updateText("H");}
	else {p_dps_sm_sys_summ1.dPdt_arrow.updateText("");}



		#IMU fans malfunction arrow ( switch on but not powered = ↓)

		if (imu_fanA_op != imu_fanA_sw) {p_dps_sm_sys_summ1.imu_A_arrow.updateText("↓");}
		else {p_dps_sm_sys_summ1.imu_A_arrow.updateText("");}

		if (imu_fanB_op != imu_fanB_sw) {p_dps_sm_sys_summ1.imu_B_arrow.updateText("↓");}
		else {p_dps_sm_sys_summ1.imu_B_arrow.updateText("");}

		if (imu_fanC_op != imu_fanC_sw) {p_dps_sm_sys_summ1.imu_C_arrow.updateText("↓");}
		else {p_dps_sm_sys_summ1.imu_C_arrow.updateText("");}


	
	#IMU Delta P BFS only

	if (imu_dp == 0) {p_dps_sm_sys_summ1.imu_bfs_deltaP_value_arrow.updateText("L");}
	else {p_dps_sm_sys_summ1.imu_bfs_deltaP_value_arrow.updateText("");}


		}
	
	else {p_dps_sm_sys_summ1.arrow_group.setVisible(0);}






	#BFS differences (PASS elements/arrows "only" in a subgroup )

	if (p_dps_sm_sys_summ1.major_function == 4)
		{
		#Hidden elements from PASS

		#p_dps_sm_sys_summ1.o2_conc_label.setVisible(0);
		#p_dps_sm_sys_summ1.o2_conc.setVisible(0);
		#p_dps_sm_sys_summ1.imu_A.setVisible(0);
		#p_dps_sm_sys_summ1.imu_B.setVisible(0);
		#p_dps_sm_sys_summ1.imu_C.setVisible(0);
		#p_dps_sm_sys_summ1.imu_A_label.setVisible(0);
		#p_dps_sm_sys_summ1.imu_B_label.setVisible(0);
		#p_dps_sm_sys_summ1.imu_C_label.setVisible(0);
		#p_dps_sm_sys_summ1.imu_A_arrow.setVisible(0);
		#p_dps_sm_sys_summ1.imu_B_arrow.setVisible(0);
		#p_dps_sm_sys_summ1.imu_C_arrow.setVisible(0);
		#p_dps_sm_sys_summ1.o2_conc_arrow.setVisible(0);
		

		p_dps_sm_sys_summ1.imu_fan_label.updateText("IMU FAN ΔP");
		p_dps_sm_sys_summ1.imu_bfs_deltaP_value.setVisible(1);
		p_dps_sm_sys_summ1.imu_bfs_deltaP_value_arrow.setVisible(1);
		
		p_dps_sm_sys_summ1.pass_only_element.setVisible(0);
		p_dps_sm_sys_summ1.pass_only_arrow.setVisible(0);
		

		p_dps_sm_sys_summ1.fuel_cell_label.updateText("FUEL CELL PH");
		}
	else
		{
		#p_dps_sm_sys_summ1.o2_conc_label.setVisible(1);
		#p_dps_sm_sys_summ1.o2_conc.setVisible(1);
		#p_dps_sm_sys_summ1.imu_A.setVisible(1);
		#p_dps_sm_sys_summ1.imu_B.setVisible(1);
		#p_dps_sm_sys_summ1.imu_C.setVisible(1);
		#p_dps_sm_sys_summ1.imu_A_label.setVisible(1);
		#p_dps_sm_sys_summ1.imu_B_label.setVisible(1);
		#p_dps_sm_sys_summ1.imu_C_label.setVisible(1);
		#p_dps_sm_sys_summ1.imu_A_arrow.setVisible(1);
		#p_dps_sm_sys_summ1.imu_B_arrow.setVisible(1);
		#p_dps_sm_sys_summ1.imu_C_arrow.setVisible(1);
		#p_dps_sm_sys_summ1.o2_conc_arrow.setVisible(1);
		

		p_dps_sm_sys_summ1.imu_fan_label.updateText("IMU FAN");
		p_dps_sm_sys_summ1.imu_bfs_deltaP_value.setVisible(0);
		p_dps_sm_sys_summ1.imu_bfs_deltaP_value_arrow.setVisible(0);

		p_dps_sm_sys_summ1.pass_only_element.setVisible(1);
		p_dps_sm_sys_summ1.pass_only_arrow.setVisible(1);
		

		p_dps_sm_sys_summ1.fuel_cell_label.updateText("FUEL CELL");
		}







        device.update_common_DPS();
    }
    
    
    
    return p_dps_sm_sys_summ1;
}
