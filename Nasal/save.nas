# write the Shuttle state to file
# and resume 
# Thorsten Renk 2016 - 2017

var save_state = func {


var lat = getprop("/position/latitude-deg");
setprop("/save/latitude-deg", lat);

var lon = getprop("/position/longitude-deg");
setprop("/save/longitude-deg", lon);

var alt = getprop("/position/altitude-ft");
setprop("/save/altitude-ft", alt);

var heading = getprop("/orientation/heading-deg");
setprop("/save/heading-deg", heading);

var pitch = getprop("/orientation/pitch-deg");
setprop("/save/pitch-deg", pitch);

var roll = getprop("/orientation/roll-deg");
setprop("/save/roll-deg", roll);

var uBody = getprop("/velocities/uBody-fps");
setprop("/save/uBody-fps", uBody);

var vBody = getprop("/velocities/vBody-fps");
setprop("/save/vBody-fps", vBody);

var wBody = getprop("/velocities/wBody-fps");
setprop("/save/wBody-fps", wBody);

var tank1 = getprop("/consumables/fuel/tank[0]/level-lbs");
setprop("/save/tank1-level-lbs", tank1);

var tank2 = getprop("/consumables/fuel/tank[1]/level-lbs");
setprop("/save/tank2-level-lbs", tank2);

var tank3 = getprop("/consumables/fuel/tank[2]/level-lbs");
setprop("/save/tank3-level-lbs", tank3);

var tank4 = getprop("/consumables/fuel/tank[3]/level-lbs");
setprop("/save/tank4-level-lbs", tank4);

var tank5 = getprop("/consumables/fuel/tank[4]/level-lbs");
setprop("/save/tank5-level-lbs", tank5);

var tank6 = getprop("/consumables/fuel/tank[5]/level-lbs");
setprop("/save/tank6-level-lbs", tank6);

var tank7 = getprop("/consumables/fuel/tank[6]/level-lbs");
setprop("/save/tank7-level-lbs", tank7);

var tank8 = getprop("/consumables/fuel/tank[7]/level-lbs");
setprop("/save/tank8-level-lbs", tank8);

var tank9 = getprop("/consumables/fuel/tank[8]/level-lbs");
setprop("/save/tank9-level-lbs", tank9);

var tank10 = getprop("/consumables/fuel/tank[9]/level-lbs");
setprop("/save/tank10-level-lbs", tank10);

var tank11 = getprop("/consumables/fuel/tank[10]/level-lbs");
setprop("/save/tank11-level-lbs", tank11);

var tank12 = getprop("/consumables/fuel/tank[11]/level-lbs");
setprop("/save/tank12-level-lbs", tank12);

var tank13 = getprop("/consumables/fuel/tank[12]/level-lbs");
setprop("/save/tank13-level-lbs", tank13);

var tank14 = getprop("/consumables/fuel/tank[13]/level-lbs");
setprop("/save/tank14-level-lbs", tank14);

var tank15 = getprop("/consumables/fuel/tank[14]/level-lbs");
setprop("/save/tank15-level-lbs", tank15);

var tank16 = getprop("/consumables/fuel/tank[15]/level-lbs");
setprop("/save/tank16-level-lbs", tank16);

var tank17 = getprop("/consumables/fuel/tank[16]/level-lbs");
setprop("/save/tank17-level-lbs", tank17);

var tank18 = getprop("/consumables/fuel/tank[17]/level-lbs");
setprop("/save/tank18-level-lbs", tank18);

var tank19 = getprop("/consumables/fuel/tank[18]/level-lbs");
setprop("/save/tank19-level-lbs", tank19);

var tank20 = getprop("/consumables/fuel/tank[26]/level-lbs");
setprop("/save/tank20-level-lbs", tank20);

var tank21 = getprop("/consumables/fuel/tank[27]/level-lbs");
setprop("/save/tank21-level-lbs", tank21);

var throttle0 = getprop("/controls/engines/engine[0]/throttle");
setprop("/save/throttle[0]", throttle0);

var throttle1 = getprop("/controls/engines/engine[1]/throttle");
setprop("/save/throttle[1]", throttle1);

var throttle2 = getprop("/controls/engines/engine[2]/throttle");
setprop("/save/throttle[2]", throttle2);

var run0 = getprop("/fdm/jsbsim/systems/mps/engine[0]/run-cmd");
setprop("/save/engine-run[0]", run0);

var run1 = getprop("/fdm/jsbsim/systems/mps/engine[1]/run-cmd");
setprop("/save/engine-run[1]", run1);

var run2 = getprop("/fdm/jsbsim/systems/mps/engine[2]/run-cmd");
setprop("/save/engine-run[2]", run2);

var elapsed = getprop("/sim/time/elapsed-sec");
var MET = elapsed + getprop("/fdm/jsbsim/systems/timer/delta-MET");

setprop("/save/MET", MET);

var state = 0;

if (getprop("/controls/shuttle/SRB-static-model") == 0)
	{
	state = 1;
	}
if (getprop("/controls/shuttle/ET-static-model") == 0)
	{
	state = 2;
	}
if ((getprop("/fdm/jsbsim/systems/mechanical/pb-door-left-pos") == 1.0) and (getprop("/fdm/jsbsim/systems/mechanical/pb-door-right-pos") == 1.0))
	{
	state = 3;
	}
if (getprop("/fdm/jsbsim/systems/mechanical/ku-antenna-pos") == 1)
	{
	state = 4;
	}

setprop("/save/state", state);

var umbilical_state = 0;

if ((getprop("/fdm/jsbsim/systems/mechanical/et-door-right-pos") == 1) and (getprop("/fdm/jsbsim/systems/mechanical/et-door-left-pos") == 1))
	{
	umbilical_state = 1;
	}

setprop("/save/umbilical-state", umbilical_state);

var radiator_state = 0;

if (getprop("/fdm/jsbsim/systems/atcs/rad-heat-dump-capacity") > 0.0)
	{
	radiator_state = 1;
	}

setprop("/save/radiator-state", radiator_state);

var hydraulics_state = getprop("/fdm/jsbsim/systems/apu/hyd-pressure-available");
setprop("/save/hydraulics-state", hydraulics_state);


# OMS kit

var oms_kit_cfg = getprop("/sim/config/shuttle/OMS-kit-config");
setprop("/save/OMS-kit-config", oms_kit_cfg);



# assume that if TACAN is on, the whole area nav set is on
var area_nav_state = getprop("/fdm/jsbsim/systems/navigation/tacan-sys1-switch");
if (area_nav_state > 0) {area_nav_state = 1;}
setprop("/save/area-nav-state", area_nav_state);

var air_data_state = getprop("/fdm/jsbsim/systems/navigation/air-data-deploy-left-switch");
if (air_data_state > 0) {air_data_state = 1;}
setprop("/save/air-data-state", air_data_state);


var control_mode = getprop("/fdm/jsbsim/systems/fcs/control-mode");
var control_string = getprop("/controls/shuttle/control-system-string");

var orbital_dap_sel = 0;

if (getprop("/fdm/jsbsim/systems/ap/orbital-dap-auto") == 1)
	{orbital_dap_sel = 1;}
else if (getprop("/fdm/jsbsim/systems/ap/orbital-dap-lvlh") == 1)
	{orbital_dap_sel = 2;}
else if (getprop("/fdm/jsbsim/systems/ap/orbital-dap-free") == 1)
	{orbital_dap_sel = 3;}

setprop("/save/control-mode", control_mode);
setprop("/save/orbital-dap-sel", orbital_dap_sel);

var css_pitch = getprop("/fdm/jsbsim/systems/ap/css-pitch-control");
var css_roll = getprop("/fdm/jsbsim/systems/ap/css-roll-control");

setprop("/save/css-pitch", css_pitch);
setprop("/save/css-roll", css_roll);

var rcs_roll = getprop("/fdm/jsbsim/systems/fcs/rcs-roll-mode");
var rcs_pitch = getprop("/fdm/jsbsim/systems/fcs/rcs-pitch-mode");

setprop("/save/rcs-mode-roll", rcs_roll);
setprop("/save/rcs-mode-pitch", rcs_pitch);

var sense_switch_pos = getprop("/fdm/jsbsim/systems/fcs/sense-switch");
var sense_X = getprop("/fdm/jsbsim/systems/fcs/sense-X");
var sense_minus_X = getprop("/fdm/jsbsim/systems/fcs/sense-minus-X");
var sense_minus_Z = getprop("/fdm/jsbsim/systems/fcs/sense-minus-Z");

setprop("/save/sense_switch_pos", sense_switch_pos);
setprop("/save/sense_X", sense_X);
setprop("/save/sense_minus_X", sense_minus_X);
setprop("/save/sense_minus_Z", sense_minus_Z);

var ops = getprop("/fdm/jsbsim/systems/dps/ops");
var major_mode = getprop("/fdm/jsbsim/systems/dps/major-mode");
var major_mode_sm = getprop("/fdm/jsbsim/systems/dps/major-mode-sm");

var ops_bfs = getprop("/fdm/jsbsim/systems/dps/ops-bfs");
var major_mode_bfs = getprop("/fdm/jsbsim/systems/dps/major-mode-bfs");

var guidance_mode = getprop("/fdm/jsbsim/systems/entry_guidance/guidance-mode");
var landing_site = getprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/site");
var runway = getprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/runway");

setprop("/save/ops", ops);
setprop("/save/major-mode", major_mode);
setprop("/save/major-mode-sm", major_mode_sm);
setprop("/save/ops-bfs", ops_bfs);
setprop("/save/major-mode-bfs", major_mode_bfs);
setprop("/save/control-string", control_string);
setprop("/save/guidance-mode", guidance_mode);
setprop("/save/landing-site", landing_site);
setprop("/save/runway", runway);


var auto_launch = getprop("/fdm/jsbsim/systems/ap/launch/autolaunch-master");
setprop("/save/auto-launch", auto_launch);

var auto_launch_stage = getprop("/fdm/jsbsim/systems/ap/launch/stage");
setprop("/save/auto-launch-stage", auto_launch_stage);

# IDP settings

var idp1_function_switch = getprop("/fdm/jsbsim/systems/dps/idp-function-switch[0]");
setprop("/save/idp1-switch-pos", idp1_function_switch);
setprop("/save/idp1-bfs-major-function", SpaceShuttle.idp_array[0].bfs_major_function);

var idp2_function_switch = getprop("/fdm/jsbsim/systems/dps/idp-function-switch[1]");
setprop("/save/idp2-switch-pos", idp2_function_switch);
setprop("/save/idp2-bfs-major-function", SpaceShuttle.idp_array[1].bfs_major_function);

var idp3_function_switch = getprop("/fdm/jsbsim/systems/dps/idp-function-switch[2]");
setprop("/save/idp3-switch-pos", idp3_function_switch);
setprop("/save/idp3-bfs-major-function", SpaceShuttle.idp_array[2].bfs_major_function);

var idp4_function_switch = getprop("/fdm/jsbsim/systems/dps/idp-function-switch[3]");
setprop("/save/idp4-switch-pos", idp4_function_switch);
setprop("/save/idp4-bfs-major-function", SpaceShuttle.idp_array[3].bfs_major_function);

# GPC config

setprop("/save/gpc1-mcc", SpaceShuttle.gpc_array[0].mcc);
setprop("/save/gpc2-mcc", SpaceShuttle.gpc_array[1].mcc);
setprop("/save/gpc3-mcc", SpaceShuttle.gpc_array[2].mcc);
setprop("/save/gpc4-mcc", SpaceShuttle.gpc_array[3].mcc);
setprop("/save/gpc5-mcc", SpaceShuttle.gpc_array[4].mcc);

setprop("/save/gpc1-mode", SpaceShuttle.gpc_array[0].mode);
setprop("/save/gpc2-mode", SpaceShuttle.gpc_array[1].mode);
setprop("/save/gpc3-mode", SpaceShuttle.gpc_array[2].mode);
setprop("/save/gpc4-mode", SpaceShuttle.gpc_array[3].mode);
setprop("/save/gpc5-mode", SpaceShuttle.gpc_array[4].mode);

var gpc1_mode_switch = getprop("/fdm/jsbsim/systems/dps/gpc1-mode-switch");
var gpc2_mode_switch = getprop("/fdm/jsbsim/systems/dps/gpc2-mode-switch");
var gpc3_mode_switch = getprop("/fdm/jsbsim/systems/dps/gpc3-mode-switch");
var gpc4_mode_switch = getprop("/fdm/jsbsim/systems/dps/gpc4-mode-switch");
var gpc5_mode_switch = getprop("/fdm/jsbsim/systems/dps/gpc5-mode-switch");

setprop("/save/gpc1-mode-switch", gpc1_mode_switch);
setprop("/save/gpc2-mode-switch", gpc2_mode_switch);
setprop("/save/gpc3-mode-switch", gpc3_mode_switch);
setprop("/save/gpc4-mode-switch", gpc4_mode_switch);
setprop("/save/gpc5-mode-switch", gpc5_mode_switch);

setprop("/save/nbat-string1", SpaceShuttle.nbat.string1_gnc);
setprop("/save/nbat-string2", SpaceShuttle.nbat.string2_gnc);
setprop("/save/nbat-string3", SpaceShuttle.nbat.string3_gnc);
setprop("/save/nbat-string4", SpaceShuttle.nbat.string4_gnc);

setprop("/save/nbat-launch1", SpaceShuttle.nbat.launch1);
setprop("/save/nbat-launch2", SpaceShuttle.nbat.launch2);

setprop("/save/nbat-pl1", SpaceShuttle.nbat.pl1);
setprop("/save/nbat-pl2", SpaceShuttle.nbat.pl2);

setprop("/save/nbat-mm1", SpaceShuttle.nbat.mm1);
setprop("/save/nbat-mm2", SpaceShuttle.nbat.mm2);

setprop("/save/nbat-crt1", SpaceShuttle.nbat.crt[0]);
setprop("/save/nbat-crt2", SpaceShuttle.nbat.crt[1]);
setprop("/save/nbat-crt3", SpaceShuttle.nbat.crt[2]);
setprop("/save/nbat-crt4", SpaceShuttle.nbat.crt[3]);

setprop("/save/nbat-crt-sm1", SpaceShuttle.nbat.crt_sm[0]);
setprop("/save/nbat-crt-sm2", SpaceShuttle.nbat.crt_sm[1]);
setprop("/save/nbat-crt-sm3", SpaceShuttle.nbat.crt_sm[2]);
setprop("/save/nbat-crt-sm4", SpaceShuttle.nbat.crt_sm[3]);

setprop("/save/bfs-in-control", SpaceShuttle.bfs_in_control);



# thermal distribution

var n = size (SpaceShuttle.thermal_array);

for (var i =0; i< n; i=i+1 )
	{
	var T = SpaceShuttle.thermal_array[i].temperature;
	setprop("/save/temperature["~i~"]",T);
	}

# hydraulic circulation pumps

var circ_pump1 = getprop("/fdm/jsbsim/systems/apu/apu/hyd-circ-pump-cmd");
var circ_pump2 = getprop("/fdm/jsbsim/systems/apu/apu[1]/hyd-circ-pump-cmd");
var circ_pump3 = getprop("/fdm/jsbsim/systems/apu/apu[2]/hyd-circ-pump-cmd");

setprop("/save/hyd-circ-pump1", circ_pump1);
setprop("/save/hyd-circ-pump2", circ_pump2);
setprop("/save/hyd-circ-pump3", circ_pump3);


# RCS and OMS heaters

var heater_fwd_A = getprop("/fdm/jsbsim/systems/rcs-hardware/heater-fwd-A-status");
var heater_fwd_B = getprop("/fdm/jsbsim/systems/rcs-hardware/heater-fwd-B-status");

setprop("/save/heater-fwd-A", heater_fwd_A);
setprop("/save/heater-fwd-B", heater_fwd_B);

#var heater_left_A = getprop("/fdm/jsbsim/systems/rcs-hardware/heater-left-A-status");
#var heater_left_B = getprop("/fdm/jsbsim/systems/rcs-hardware/heater-left-B-status");

#setprop("/save/heater-left-A", heater_left_A);
#setprop("/save/heater-left-B", heater_left_B);

#var heater_right_A = getprop("/fdm/jsbsim/systems/rcs-hardware/heater-right-A-status");
#var heater_right_B = getprop("/fdm/jsbsim/systems/rcs-hardware/heater-right-B-status");

#setprop("/save/heater-right-A", heater_right_A);
#setprop("/save/heater-right-B", heater_right_B);

var heater_oms_left_A = getprop("/fdm/jsbsim/systems/oms-hardware/heater-left-A-status");
var heater_oms_left_B = getprop("/fdm/jsbsim/systems/oms-hardware/heater-left-B-status");

setprop("/save/heater-oms-left-A", heater_oms_left_A);
setprop("/save/heater-oms-left-B", heater_oms_left_B);

var heater_oms_right_A = getprop("/fdm/jsbsim/systems/oms-hardware/heater-right-A-status");
var heater_oms_right_B = getprop("/fdm/jsbsim/systems/oms-hardware/heater-right-B-status");

setprop("/save/heater-oms-right-A", heater_oms_right_A);
setprop("/save/heater-oms-right-B", heater_oms_right_B);

var heater_xfeed_A = getprop("/fdm/jsbsim/systems/oms-hardware/heater-crossfeed-A-status");
var heater_xfeed_B = getprop("/fdm/jsbsim/systems/oms-hardware/heater-crossfeed-B-status");

setprop("/save/heater-oms-xfeed-A", heater_oms_left_A);
setprop("/save/heater-oms-xfeed-B", heater_oms_left_B);


# propellant valve configuration

var helium_left_oms_A = getprop("/fdm/jsbsim/systems/oms-hardware/helium-left-oms-valve-A-status");
var helium_left_oms_B = getprop("/fdm/jsbsim/systems/oms-hardware/helium-left-oms-valve-B-status");

setprop("/save/valve-helium-left-oms-A", helium_left_oms_A);
setprop("/save/valve-helium-left-oms-B", helium_left_oms_B);

var helium_right_oms_A = getprop("/fdm/jsbsim/systems/oms-hardware/helium-right-oms-valve-A-status");
var helium_right_oms_B = getprop("/fdm/jsbsim/systems/oms-hardware/helium-right-oms-valve-B-status");

setprop("/save/valve-helium-right-oms-A", helium_right_oms_A);
setprop("/save/valve-helium-right-oms-B", helium_right_oms_B);

var helium_kit_oms_A = getprop("/fdm/jsbsim/systems/oms-hardware/helium-kit-oms-valve-A-status");
var helium_kit_oms_B = getprop("/fdm/jsbsim/systems/oms-hardware/helium-kit-oms-valve-B-status");

setprop("/save/valve-helium-kit-oms-A", helium_kit_oms_A);
setprop("/save/valve-helium-kit-oms-B", helium_kit_oms_B);

var tank_left_oms_A = getprop("/fdm/jsbsim/systems/oms-hardware/tank-left-oms-valve-A-status");
var tank_left_oms_B = getprop("/fdm/jsbsim/systems/oms-hardware/tank-left-oms-valve-B-status");

setprop("/save/valve-tank-left-oms-A", tank_left_oms_A);
setprop("/save/valve-tank-left-oms-B", tank_left_oms_B);

var tank_right_oms_A = getprop("/fdm/jsbsim/systems/oms-hardware/tank-right-oms-valve-A-status");
var tank_right_oms_B = getprop("/fdm/jsbsim/systems/oms-hardware/tank-right-oms-valve-B-status");

setprop("/save/valve-tank-right-oms-A", tank_right_oms_A);
setprop("/save/valve-tank-right-oms-B", tank_right_oms_B);

var tank_kit_oms_A = getprop("/fdm/jsbsim/systems/oms-hardware/tank-kit-oms-valve-A-status");
var tank_kit_oms_B = getprop("/fdm/jsbsim/systems/oms-hardware/tank-kit-oms-valve-B-status");

setprop("/save/valve-tank-kit-oms-A", tank_kit_oms_A);
setprop("/save/valve-tank-kit-oms-B", tank_kit_oms_B);

var xfeed_left_oms_A = getprop("/fdm/jsbsim/systems/oms-hardware/crossfeed-left-oms-valve-A-status");
var xfeed_left_oms_B = getprop("/fdm/jsbsim/systems/oms-hardware/crossfeed-left-oms-valve-B-status");

setprop("/save/valve-xfeed-left-oms-A", xfeed_left_oms_A);
setprop("/save/valve-xfeed-left-oms-B", xfeed_left_oms_B);

var xfeed_right_oms_A = getprop("/fdm/jsbsim/systems/oms-hardware/crossfeed-right-oms-valve-A-status");
var xfeed_right_oms_B = getprop("/fdm/jsbsim/systems/oms-hardware/crossfeed-right-oms-valve-B-status");

setprop("/save/valve-xfeed-right-oms-A", xfeed_right_oms_A);
setprop("/save/valve-xfeed-right-oms-B", xfeed_right_oms_B);

var helium_left_rcs_A = getprop("/fdm/jsbsim/systems/rcs-hardware/helium-left-rcs-valve-A-status");
var helium_left_rcs_B = getprop("/fdm/jsbsim/systems/rcs-hardware/helium-left-rcs-valve-B-status");

setprop("/save/valve-helium-left-rcs-A", helium_left_rcs_A);
setprop("/save/valve-helium-left-rcs-B", helium_left_rcs_B);

var helium_right_rcs_A = getprop("/fdm/jsbsim/systems/rcs-hardware/helium-right-rcs-valve-A-status");
var helium_right_rcs_B = getprop("/fdm/jsbsim/systems/rcs-hardware/helium-right-rcs-valve-B-status");

setprop("/save/valve-helium-right-rcs-A", helium_right_rcs_A);
setprop("/save/valve-helium-right-rcs-B", helium_right_rcs_B);

var tank_left_rcs_12 = getprop("/fdm/jsbsim/systems/rcs-hardware/tank-left-rcs-valve-12-status");
var tank_left_rcs_345A = getprop("/fdm/jsbsim/systems/rcs-hardware/tank-left-rcs-valve-345A-status");
var tank_left_rcs_345B = getprop("/fdm/jsbsim/systems/rcs-hardware/tank-left-rcs-valve-345B-status");

setprop("/save/valve-tank-left-rcs-12", tank_left_rcs_12);
setprop("/save/valve-tank-left-rcs-345A", tank_left_rcs_345A);
setprop("/save/valve-tank-left-rcs-345B", tank_left_rcs_345B);

var tank_left_rcs_mfold_1 = getprop("/fdm/jsbsim/systems/rcs-hardware/mfold-left-rcs-valve-1-status");
var tank_left_rcs_mfold_2 = getprop("/fdm/jsbsim/systems/rcs-hardware/mfold-left-rcs-valve-2-status");
var tank_left_rcs_mfold_3 = getprop("/fdm/jsbsim/systems/rcs-hardware/mfold-left-rcs-valve-3-status");
var tank_left_rcs_mfold_4 = getprop("/fdm/jsbsim/systems/rcs-hardware/mfold-left-rcs-valve-4-status");
var tank_left_rcs_mfold_5 = getprop("/fdm/jsbsim/systems/rcs-hardware/mfold-left-rcs-valve-5-status");

setprop("/save/valve-tank-left-rcs-mfold-1", tank_left_rcs_mfold_1);
setprop("/save/valve-tank-left-rcs-mfold-2", tank_left_rcs_mfold_2);
setprop("/save/valve-tank-left-rcs-mfold-3", tank_left_rcs_mfold_3);
setprop("/save/valve-tank-left-rcs-mfold-4", tank_left_rcs_mfold_4);
setprop("/save/valve-tank-left-rcs-mfold-5", tank_left_rcs_mfold_5);

var tank_left_rcs_xfeed_12 = getprop("/fdm/jsbsim/systems/rcs-hardware/crossfeed-left-rcs-valve-12-status");
var tank_left_rcs_xfeed_345 = getprop("/fdm/jsbsim/systems/rcs-hardware/crossfeed-left-rcs-valve-345-status");

setprop("/save/tank-left-rcs-xfeed-12", tank_left_rcs_xfeed_12);
setprop("/save/tank-left-rcs-xfeed-345", tank_left_rcs_xfeed_345);

var tank_right_rcs_12 = getprop("/fdm/jsbsim/systems/rcs-hardware/tank-right-rcs-valve-12-status");
var tank_right_rcs_345A = getprop("/fdm/jsbsim/systems/rcs-hardware/tank-right-rcs-valve-345A-status");
var tank_right_rcs_345B = getprop("/fdm/jsbsim/systems/rcs-hardware/tank-right-rcs-valve-345B-status");

setprop("/save/valve-tank-right-rcs-12", tank_right_rcs_12);
setprop("/save/valve-tank-right-rcs-345A", tank_right_rcs_345A);
setprop("/save/valve-tank-right-rcs-345B", tank_right_rcs_345B);


var tank_right_rcs_mfold_1 = getprop("/fdm/jsbsim/systems/rcs-hardware/mfold-right-rcs-valve-1-status");
var tank_right_rcs_mfold_2 = getprop("/fdm/jsbsim/systems/rcs-hardware/mfold-right-rcs-valve-2-status");
var tank_right_rcs_mfold_3 = getprop("/fdm/jsbsim/systems/rcs-hardware/mfold-right-rcs-valve-3-status");
var tank_right_rcs_mfold_4 = getprop("/fdm/jsbsim/systems/rcs-hardware/mfold-right-rcs-valve-4-status");
var tank_right_rcs_mfold_5 = getprop("/fdm/jsbsim/systems/rcs-hardware/mfold-right-rcs-valve-5-status");

setprop("/save/valve-tank-right-rcs-mfold-1", tank_right_rcs_mfold_1);
setprop("/save/valve-tank-right-rcs-mfold-2", tank_right_rcs_mfold_2);
setprop("/save/valve-tank-right-rcs-mfold-3", tank_right_rcs_mfold_3);
setprop("/save/valve-tank-right-rcs-mfold-4", tank_right_rcs_mfold_4);
setprop("/save/valve-tank-right-rcs-mfold-5", tank_right_rcs_mfold_5);


var tank_right_rcs_xfeed_12 = getprop("/fdm/jsbsim/systems/rcs-hardware/crossfeed-right-rcs-valve-12-status");
var tank_right_rcs_xfeed_345 = getprop("/fdm/jsbsim/systems/rcs-hardware/crossfeed-right-rcs-valve-345-status");

setprop("/save/tank-right-rcs-xfeed-12", tank_right_rcs_xfeed_12);
setprop("/save/tank-right-rcs-xfeed-345", tank_right_rcs_xfeed_345);

# engine controller power switches

var engine1_controller_A_switch = getprop("/fdm/jsbsim/systems/mps/engine/controller-A-power-switch-status");
var engine1_controller_B_switch = getprop("/fdm/jsbsim/systems/mps/engine/controller-B-power-switch-status");

setprop("/save/engine1_controller-A-power-switch-status", engine1_controller_A_switch);
setprop("/save/engine1_controller-B-power-switch-status", engine1_controller_B_switch);

var engine2_controller_A_switch = getprop("/fdm/jsbsim/systems/mps/engine[1]/controller-A-power-switch-status");
var engine2_controller_B_switch = getprop("/fdm/jsbsim/systems/mps/engine[1]/controller-B-power-switch-status");

setprop("/save/engine2_controller-A-power-switch-status", engine2_controller_A_switch);
setprop("/save/engine2_controller-B-power-switch-status", engine2_controller_B_switch);

var engine3_controller_A_switch = getprop("/fdm/jsbsim/systems/mps/engine[2]/controller-A-power-switch-status");
var engine3_controller_B_switch = getprop("/fdm/jsbsim/systems/mps/engine[2]/controller-B-power-switch-status");

setprop("/save/engine3_controller-A-power-switch-status", engine3_controller_A_switch);
setprop("/save/engine3_controller-B-power-switch-status", engine3_controller_B_switch);


# helium isolation switches

var engine1_helium_isolation_A_switch = getprop("/fdm/jsbsim/systems/mps/engine/helium-isolation-valve-A-status");
var engine1_helium_isolation_B_switch = getprop("/fdm/jsbsim/systems/mps/engine/helium-isolation-valve-B-status");

setprop("/save/engine1_helium-isolation-valve-A-status", engine1_helium_isolation_A_switch);
setprop("/save/engine1_helium-isolation-valve-B-status", engine1_helium_isolation_B_switch);

var engine2_helium_isolation_A_switch = getprop("/fdm/jsbsim/systems/mps/engine[1]/helium-isolation-valve-A-status");
var engine2_helium_isolation_B_switch = getprop("/fdm/jsbsim/systems/mps/engine[1]/helium-isolation-valve-B-status");

setprop("/save/engine2_helium-isolation-valve-A-status", engine2_helium_isolation_A_switch);
setprop("/save/engine2_helium-isolation-valve-B-status", engine2_helium_isolation_B_switch);


var engine3_helium_isolation_A_switch = getprop("/fdm/jsbsim/systems/mps/engine[2]/helium-isolation-valve-A-status");
var engine3_helium_isolation_B_switch = getprop("/fdm/jsbsim/systems/mps/engine[2]/helium-isolation-valve-B-status");

setprop("/save/engine3_helium-isolation-valve-A-status", engine3_helium_isolation_A_switch);
setprop("/save/engine3_helium-isolation-valve-B-status", engine3_helium_isolation_B_switch);


var engine1_helium_interconnect_status = getprop("/fdm/jsbsim/systems/mps/engine[0]/helium-interconnect-valve-status");
var engine2_helium_interconnect_status = getprop("/fdm/jsbsim/systems/mps/engine[1]/helium-interconnect-valve-status");
var engine3_helium_interconnect_status = getprop("/fdm/jsbsim/systems/mps/engine[2]/helium-interconnect-valve-status");


setprop("/save/engine1_helium-interconnect-valve-status", engine1_helium_interconnect_status);
setprop("/save/engine2_helium-interconnect-valve-status", engine2_helium_interconnect_status);
setprop("/save/engine3_helium-interconnect-valve-status", engine3_helium_interconnect_status);

var pneumatic_helium_Px_switch = getprop("/fdm/jsbsim/systems/mps/helium-isolation-valve-Px-status");
var pneumatic_helium_P_switch = getprop("/fdm/jsbsim/systems/mps/helium-isolation-valve-P-status");

setprop("/save/pneumatic_helium-isolation-valve-Px-status", pneumatic_helium_Px_switch);
setprop("/save/pneumatic_helium-isolation-valve-P-status", pneumatic_helium_P_switch);


# TVC isolation valves

var sys1_tvc_isolation_valve = getprop("/fdm/jsbsim/systems/apu/apu/tvc-isolation-valve-status");
var sys2_tvc_isolation_valve = getprop("/fdm/jsbsim/systems/apu/apu[1]/tvc-isolation-valve-status");
var sys3_tvc_isolation_valve = getprop("/fdm/jsbsim/systems/apu/apu[2]/tvc-isolation-valve-status");

setprop("/save/sys1-tvc-isolation-valve", sys1_tvc_isolation_valve);
setprop("/save/sys2-tvc-isolation-valve", sys2_tvc_isolation_valve);
setprop("/save/sys3-tvc-isolation-valve", sys3_tvc_isolation_valve);

# ADI attitude reference switch

var adi_attitude_switch = getprop("/fdm/jsbsim/systems/adi/attitude-select");
setprop("/save/adi-attitude-switch", adi_attitude_switch);

# CRT selection switch

var crt_select_left_switch = getprop("/fdm/jsbsim/systems/dps/crtl-sel");
setprop("/save/crt-select-left-switch", crt_select_left_switch);

var crt_select_right_switch = getprop("/fdm/jsbsim/systems/dps/crtr-sel");
setprop("/save/crt-select-right-switch", crt_select_right_switch);


# display power switches

var display_L1_pwr_switch = getprop("/fdm/jsbsim/systems/electrical/display/L1-pwr-switch");
setprop("/save/display-L1-pwr-switch", display_L1_pwr_switch);

var display_L2_pwr_switch = getprop("/fdm/jsbsim/systems/electrical/display/L2-pwr-switch");
setprop("/save/display-L2-pwr-switch", display_L2_pwr_switch);

var display_C1_pwr_switch = getprop("/fdm/jsbsim/systems/electrical/display/C1-pwr-switch");
setprop("/save/display-C1-pwr-switch", display_C1_pwr_switch);

var display_C2_pwr_switch = getprop("/fdm/jsbsim/systems/electrical/display/C2-pwr-switch");
setprop("/save/display-C2-pwr-switch", display_C2_pwr_switch);

var display_C3_pwr_switch = getprop("/fdm/jsbsim/systems/electrical/display/C3-pwr-switch");
setprop("/save/display-C3-pwr-switch", display_C3_pwr_switch);

var display_C4_pwr_switch = getprop("/fdm/jsbsim/systems/electrical/display/C4-pwr-switch");
setprop("/save/display-C4-pwr-switch", display_C4_pwr_switch);

var display_C5_pwr_switch = getprop("/fdm/jsbsim/systems/electrical/display/C5-pwr-switch");
setprop("/save/display-C5-pwr-switch", display_C5_pwr_switch);

var display_R1_pwr_switch = getprop("/fdm/jsbsim/systems/electrical/display/R1-pwr-switch");
setprop("/save/display-R1-pwr-switch", display_R1_pwr_switch);

var display_R2_pwr_switch = getprop("/fdm/jsbsim/systems/electrical/display/R2-pwr-switch");
setprop("/save/display-R2-pwr-switch", display_R2_pwr_switch);

var display_A6_pwr_switch = getprop("/fdm/jsbsim/systems/electrical/display/A6-pwr-switch");
setprop("/save/display-A6-pwr-switch", display_A6_pwr_switch);

var display_R11_pwr_switch = getprop("/fdm/jsbsim/systems/electrical/display/R11-pwr-switch");
setprop("/save/display-R11-pwr-switch", display_R11_pwr_switch);

# BFS switches

var bfs_display_switch = getprop("/fdm/jsbsim/systems/dps/bfs/display-switch");
setprop("/save/bfs-display-switch", bfs_display_switch);

var bfs_crt_select_switch = getprop("/fdm/jsbsim/systems/dps/bfs/crt-select-switch");
setprop("/save/bfs-crt-select-switch", bfs_crt_select_switch);


# FES switches

var fes_heater_left_switch = getprop("/fdm/jsbsim/systems/atcs/fes-heater-left-status");
setprop("/save/fes-heater-left-switch", fes_heater_left_switch);

var fes_heater_right_switch = getprop("/fdm/jsbsim/systems/atcs/fes-heater-right-status");
setprop("/save/fes-heater-right-switch", fes_heater_right_switch);

# IMU errors

for (var i=0; i< SpaceShuttle.imu_system.num_units; i=i+1)
	{
	setprop("/save/imu["~i~"]/pitch-error", SpaceShuttle.imu_system.imu[i].pitch_error);
	setprop("/save/imu["~i~"]/yaw-error", SpaceShuttle.imu_system.imu[i].yaw_error);
	setprop("/save/imu["~i~"]/roll-error", SpaceShuttle.imu_system.imu[i].roll_error);
	}

# fuel cell efficiency

var fc1_efficiency = getprop("/fdm/jsbsim/systems/electrical/fc/fc-efficiency");
var fc2_efficiency = getprop("/fdm/jsbsim/systems/electrical/fc[1]/fc-efficiency");
var fc3_efficiency = getprop("/fdm/jsbsim/systems/electrical/fc[2]/fc-efficiency");

setprop("/save/fc1-efficiency", fc1_efficiency);
setprop("/save/fc2-efficiency", fc2_efficiency);
setprop("/save/fc3-efficiency", fc3_efficiency);

# the orbital target

if (SpaceShuttle.n_orbital_targets > 0)
	{

	setprop("/save/otgt-elapsed-time", elapsed);

	var anomaly = SpaceShuttle.oTgt.anomaly_rad;
	setprop("/save/otgt-anomaly", anomaly);

	var initial_nl_rad = SpaceShuttle.oTgt.initial_nl_rad;
	setprop("/save/otgt-initial-node-lon", initial_nl_rad);

	var initial_anomaly_rad = SpaceShuttle.oTgt.initial_anomaly_rad;
	setprop("/save/otgt-initial-anomaly", initial_anomaly_rad);

	var node_lon = SpaceShuttle.oTgt.node_longitude;
	setprop("/save/otgt-node-lon", node_lon);

	var delta_lon = SpaceShuttle.oTgt.delta_lon;
	setprop("/save/otgt-delta-lon", delta_lon);
	}

# the payload

var payload_string = getprop("/sim/config/shuttle/PL-selection");

setprop("/save/payload-string", payload_string);


# the scenario description

var timestring = getprop("/sim/time/real/year");
timestring = timestring~ "-"~getprop("/sim/time/real/month");
timestring = timestring~ "-"~getprop("/sim/time/real/day");
timestring = timestring~ "-"~getprop("/sim/time/real/hour");

var minute = getprop("/sim/time/real/minute");
if (minute < 10) {minute = "0"~minute;}
timestring = timestring~ ":"~minute;

var description = getprop("/sim/gui/dialogs/SpaceShuttle/save/description");

setprop("/save/description", description);
setprop("/save/timestring", timestring);

# now try to save it to a specified file

#var filename = "save1.xml";

var filename = getprop("/sim/gui/dialogs/SpaceShuttle/save/filename");
var path = getprop("/sim/fg-home") ~ "/aircraft-data/SpaceShuttleSave/"~filename;

var nodeSave = props.globals.getNode("/save", 0);
io.write_properties(path, nodeSave); 

print("Current state written to ", filename, " !");

}


var read_state_from_file = func (filename) {

    var path = getprop("/sim/fg-home") ~ "/aircraft-data/SpaceShuttleSave/"~filename;
    var readNode = props.globals.getNode("/save", 0);

    io.read_properties(path, readNode);

}






var resume_state = func {

# just in case disable prelaunch flag
# with a delay to allow flame visuals to adjust

settimer ( func {setprop("/sim/config/shuttle/prelaunch-flag", 0);}, 3.0);

# set SSME flame colors to ignited state

setprop("/fdm/jsbsim/systems/various/ssme-ignition-density-target", 0.1);
setprop("/fdm/jsbsim/systems/various/ssme-flame-base-density-target", 2.0);
setprop("/fdm/jsbsim/systems/various/ssme-noise-strength-target", 0.15);

setprop("/fdm/jsbsim/systems/various/ssme-flame-r-base-target", 0.9);
setprop("/fdm/jsbsim/systems/various/ssme-flame-g-base-target", 1.0);
setprop("/fdm/jsbsim/systems/various/ssme-flame-b-base-target", 1.0);

setprop("/fdm/jsbsim/systems/various/ssme-flame-r-high-target", 0.7);
setprop("/fdm/jsbsim/systems/various/ssme-flame-g-high-target", 0.7);
setprop("/fdm/jsbsim/systems/various/ssme-flame-b-high-target", 1.0);

setprop("/fdm/jsbsim/systems/various/ssme-flame-r-low-target", 0.6);
setprop("/fdm/jsbsim/systems/various/ssme-flame-g-low-target", 0.4);
setprop("/fdm/jsbsim/systems/various/ssme-flame-b-low-target", 0.4);

setprop("/fdm/jsbsim/systems/various/ssme-ignition-density-target2", 0.1);
setprop("/fdm/jsbsim/systems/various/ssme-flame-base-density-target2", 2.0);
setprop("/fdm/jsbsim/systems/various/ssme-noise-strength-target2", 0.15);

setprop("/fdm/jsbsim/systems/various/ssme-flame-r-base-target2", 0.9);
setprop("/fdm/jsbsim/systems/various/ssme-flame-g-base-target2", 1.0);
setprop("/fdm/jsbsim/systems/various/ssme-flame-b-base-target2", 1.0);

setprop("/fdm/jsbsim/systems/various/ssme-flame-r-high-target2", 0.7);
setprop("/fdm/jsbsim/systems/various/ssme-flame-g-high-target2", 0.7);
setprop("/fdm/jsbsim/systems/various/ssme-flame-b-high-target2", 1.0);

setprop("/fdm/jsbsim/systems/various/ssme-flame-r-low-target2", 0.6);
setprop("/fdm/jsbsim/systems/various/ssme-flame-g-low-target2", 0.4);
setprop("/fdm/jsbsim/systems/various/ssme-flame-b-low-target2", 0.4);

setprop("/fdm/jsbsim/systems/various/ssme-ignition-density-target1", 0.1);
setprop("/fdm/jsbsim/systems/various/ssme-flame-base-density-target1", 2.0);
setprop("/fdm/jsbsim/systems/various/ssme-noise-strength-target1", 0.15);

setprop("/fdm/jsbsim/systems/various/ssme-flame-r-base-target1", 0.9);
setprop("/fdm/jsbsim/systems/various/ssme-flame-g-base-target1", 1.0);
setprop("/fdm/jsbsim/systems/various/ssme-flame-b-base-target1", 1.0);

setprop("/fdm/jsbsim/systems/various/ssme-flame-r-high-target1", 0.7);
setprop("/fdm/jsbsim/systems/various/ssme-flame-g-high-target1", 0.7);
setprop("/fdm/jsbsim/systems/various/ssme-flame-b-high-target1", 1.0);

setprop("/fdm/jsbsim/systems/various/ssme-flame-r-low-target1", 0.6);
setprop("/fdm/jsbsim/systems/various/ssme-flame-g-low-target1", 0.4);
setprop("/fdm/jsbsim/systems/various/ssme-flame-b-low-target1", 0.4);

# state vector resume

var lat = getprop("/save/latitude-deg");
setprop("/position/latitude-deg", lat);

var lon = getprop("/save/longitude-deg");
setprop("/position/longitude-deg", lon);

var alt = getprop("/save/altitude-ft");
setprop("/position/altitude-ft", alt);

var heading = getprop("/save/heading-deg");
setprop("/orientation/heading-deg", heading);

var pitch = getprop("/save/pitch-deg");
setprop("/orientation/pitch-deg", pitch);

var roll = getprop("/save/roll-deg");
setprop("/orientation/roll-deg", roll);

var uBody = getprop("/save/uBody-fps");
setprop("/velocities/uBody-fps", uBody);

var vBody = getprop("/save/vBody-fps");
setprop("/velocities/vBody-fps", vBody);

var wBody = getprop("/save/wBody-fps");
setprop("/velocities/wBody-fps", wBody);

var tank1 = getprop("/save/tank1-level-lbs");
setprop("/consumables/fuel/tank[0]/level-lbs", tank1);

var tank2 = getprop("/save/tank2-level-lbs");
setprop("/consumables/fuel/tank[1]/level-lbs", tank2);

var tank3 = getprop("/save/tank3-level-lbs");
setprop("/consumables/fuel/tank[2]/level-lbs", tank3);

var tank4 = getprop("/save/tank4-level-lbs");
setprop("/consumables/fuel/tank[3]/level-lbs", tank4);

var tank5 = getprop("/save/tank5-level-lbs");
setprop("/consumables/fuel/tank[4]/level-lbs", tank5);

var tank6 = getprop("/save/tank6-level-lbs");
setprop("/consumables/fuel/tank[5]/level-lbs", tank6);

var tank7 = getprop("/save/tank7-level-lbs");
setprop("/consumables/fuel/tank[6]/level-lbs", tank7);

var tank8 = getprop("/save/tank8-level-lbs");
setprop("/consumables/fuel/tank[7]/level-lbs", tank8);

var tank9 = getprop("/save/tank9-level-lbs");
setprop("/consumables/fuel/tank[8]/level-lbs", tank9);

var tank10 = getprop("/save/tank10-level-lbs");
setprop("/consumables/fuel/tank[9]/level-lbs", tank10);

var tank11 = getprop("/save/tank11-level-lbs");
setprop("/consumables/fuel/tank[10]/level-lbs", tank11);

var tank12 = getprop("/save/tank12-level-lbs");
setprop("/consumables/fuel/tank[11]/level-lbs", tank12);

var tank13 = getprop("/save/tank13-level-lbs");
setprop("/consumables/fuel/tank[12]/level-lbs", tank13);

var tank14 = getprop("/save/tank14-level-lbs");
setprop("/consumables/fuel/tank[13]/level-lbs", tank14);

var tank15 = getprop("/save/tank15-level-lbs");
setprop("/consumables/fuel/tank[14]/level-lbs", tank15);

var tank16 = getprop("/save/tank16-level-lbs");
setprop("/consumables/fuel/tank[15]/level-lbs", tank16);

var tank17 = getprop("/save/tank17-level-lbs");
setprop("/consumables/fuel/tank[16]/level-lbs", tank17);

var tank18 = getprop("/save/tank18-level-lbs");
setprop("/consumables/fuel/tank[17]/level-lbs", tank18);

var tank19 = getprop("/save/tank19-level-lbs");
setprop("/consumables/fuel/tank[18]/level-lbs", tank19);



var elapsed = getprop("/sim/time/elapsed-sec");
var MET = getprop("/save/MET");

var delta_MET = MET - elapsed;
setprop("/fdm/jsbsim/systems/timer/delta-MET", delta_MET);

SpaceShuttle.gear_up();

var state = getprop("/save/state");

if (state > 0)
	{
	print("Separating SRBs");
	SpaceShuttle.SRB_separate_silent();
	setprop("/controls/shuttle/SRB-attach", 0);
	setprop("/ai/models/ballistic[0]/controls/slave-to-ac",0);
	setprop("/ai/models/ballistic[1]/controls/slave-to-ac",0);
	}
if (state > 1)
	{
	print("Separating ET");
	SpaceShuttle.external_tank_separate_silent();
	}
if (state > 2)
	{
	SpaceShuttle.pb_door_open();
	}
if (state > 3)
	{
	SpaceShuttle.ku_antenna_deploy();
	}




if (getprop("/save/umbilical-state") == 1)
	{
	SpaceShuttle.et_umbilical_door_close();
	}

if (getprop("/save/radiator-state") == 1)
	{
	SpaceShuttle.radiator_activate();
	SpaceShuttle.thermal_control_on();
	}

if (getprop("/save/hydraulics-state") == 1)
	{
	SpaceShuttle.hydraulics_on();
	}

if (getprop("/save/area-nav-state") == 1)
	{
	SpaceShuttle.area_nav_on();
	}
if (getprop("/save/air-data-state") == 1)
	{
	SpaceShuttle.air_data_on();
	}


# OMS kit

var oms_kit_cfg = getprop("/save/OMS-kit-config");
setprop("/sim/config/shuttle/OMS-kit-config", oms_kit_cfg);

SpaceShuttle.update_oms_kit_selection();

var tank20 = getprop("/save/tank20-level-lbs");
setprop("/consumables/fuel/tank[26]/level-lbs", tank20);

var tank21 = getprop("/save/tank21-level-lbs");
setprop("/consumables/fuel/tank[27]/level-lbs", tank21);

# throttles for powered flight


var throttle0 = getprop("/save/throttle[0]");
setprop("/controls/engines/engine[0]/throttle", throttle0);

var throttle1 = getprop("/save/throttle[1]");
setprop("/controls/engines/engine[1]/throttle", throttle1);

var throttle2 = getprop("/save/throttle[2]");
setprop("/controls/engines/engine[2]/throttle", throttle2);

var run0 = getprop("/save/engine-run[0]");
setprop("/fdm/jsbsim/systems/mps/engine[0]/run-cmd", run0);

var run1 = getprop("/save/engine-run[1]");
setprop("/fdm/jsbsim/systems/mps/engine[1]/run-cmd", run1);

var run2 = getprop("/save/engine-run[2]");
setprop("/fdm/jsbsim/systems/mps/engine[2]/run-cmd", run2);



var control_mode = getprop("/save/control-mode");
var orbital_dap_sel = getprop("/save/orbital-dap-sel");

setprop("/fdm/jsbsim/systems/fcs/control-mode", control_mode);

if (orbital_dap_sel == 0)
	{
	setprop("/fdm/jsbsim/systems/ap/orbital-dap-inertial", 1);
	setprop("/fdm/jsbsim/systems/ap/orbital-dap-auto", 0);
	setprop("/fdm/jsbsim/systems/ap/orbital-dap-lvlh", 0);
	setprop("/fdm/jsbsim/systems/ap/orbital-dap-free", 0);
	}
else if (orbital_dap_sel == 1)
	{
	setprop("/fdm/jsbsim/systems/ap/orbital-dap-inertial", 0);
	setprop("/fdm/jsbsim/systems/ap/orbital-dap-auto", 1);
	setprop("/fdm/jsbsim/systems/ap/orbital-dap-lvlh", 0);
	setprop("/fdm/jsbsim/systems/ap/orbital-dap-free", 0);
	}
else if (orbital_dap_sel == 2)
	{
	setprop("/fdm/jsbsim/systems/ap/orbital-dap-inertial", 0);
	setprop("/fdm/jsbsim/systems/ap/orbital-dap-auto", 0);
	setprop("/fdm/jsbsim/systems/ap/orbital-dap-lvlh", 1);
	setprop("/fdm/jsbsim/systems/ap/orbital-dap-free", 0);
	}
else if (orbital_dap_sel == 3)
	{
	setprop("/fdm/jsbsim/systems/ap/orbital-dap-inertial", 0);
	setprop("/fdm/jsbsim/systems/ap/orbital-dap-auto", 0);
	setprop("/fdm/jsbsim/systems/ap/orbital-dap-lvlh", 0);
	setprop("/fdm/jsbsim/systems/ap/orbital-dap-free", 1);
	}

var control_string = getprop("/save/control-string");

setprop("/controls/shuttle/control-system-string", control_string);


var css_pitch = getprop("/save/css-pitch");
var css_roll = getprop("/save/css-roll");

if (css_pitch == 1)
	{
	setprop("/fdm/jsbsim/systems/ap/css-pitch-control", 1);
	setprop("/fdm/jsbsim/systems/ap/automatic-pitch-control",0);
	}
else
	{
	setprop("/fdm/jsbsim/systems/ap/css-pitch-control", 0);
	setprop("/fdm/jsbsim/systems/ap/automatic-pitch-control",1);
	}

if (css_roll == 1)
	{
	setprop("/fdm/jsbsim/systems/ap/css-roll-control", 1);
	setprop("/fdm/jsbsim/systems/ap/automatic-roll-control",0);
	}
else
	{
	setprop("/fdm/jsbsim/systems/ap/css-roll-control", 0);
	setprop("/fdm/jsbsim/systems/ap/automatic-roll-control",1);
	}


var sense_switch_pos = getprop("/save/sense_switch_pos");
var sense_X = getprop("/save/sense_X");
var sense_minus_X = getprop("/save/sense_minus_X");
var sense_minus_Z = getprop("/save/sense_minus_Z");


setprop("/fdm/jsbsim/systems/fcs/sense-switch", sense_switch_pos);
setprop("/fdm/jsbsim/systems/fcs/sense-X", sense_X);
setprop("/fdm/jsbsim/systems/fcs/sense-minus-X", sense_minus_X);
setprop("/fdm/jsbsim/systems/fcs/sense-minus-Z", sense_minus_Z);


var rcs_roll = getprop("/save/rcs-mode-roll");
var rcs_pitch = getprop("/save/rcs-mode-pitch");

setprop("/fdm/jsbsim/systems/fcs/rcs-roll-mode", rcs_roll);
setprop("/fdm/jsbsim/systems/fcs/rcs-pitch-mode", rcs_pitch);


var ops = getprop("/save/ops");
var major_mode = getprop("/save/major-mode");
var major_mode_sm = getprop("/save/major-mode-sm");

var ops_bfs = getprop("/save/ops-bfs");
var major_mode_bfs = getprop("/save/major-mode-bfs");



setprop("/fdm/jsbsim/systems/dps/ops", ops);
setprop("/fdm/jsbsim/systems/dps/major-mode", major_mode);
setprop("/fdm/jsbsim/systems/dps/major-mode-sm", major_mode_sm);

setprop("/fdm/jsbsim/systems/dps/ops-bfs", ops_bfs);
setprop("/fdm/jsbsim/systems/dps/major-mode-bfs", major_mode_bfs);



# IDP settings

var idp1_function_switch = getprop("/save/idp1-switch-pos");
var idp1_major_function_bfs = getprop("/save/idp1-bfs-major-function");

setprop("/fdm/jsbsim/systems/dps/idp-function-switch[0]", idp1_function_switch);
SpaceShuttle.idp_array[0].set_bfs_major_function(idp1_major_function_bfs);

var idp2_function_switch = getprop("/save/idp2-switch-pos");
var idp2_major_function_bfs = getprop("/save/idp2-bfs-major-function");

setprop("/fdm/jsbsim/systems/dps/idp-function-switch[1]", idp2_function_switch);
SpaceShuttle.idp_array[1].set_bfs_major_function(idp2_major_function_bfs);

var idp3_function_switch = getprop("/save/idp3-switch-pos");
var idp3_major_function_bfs = getprop("/save/idp3-bfs-major-function");

setprop("/fdm/jsbsim/systems/dps/idp-function-switch[2]", idp3_function_switch);
SpaceShuttle.idp_array[2].set_bfs_major_function(idp3_major_function_bfs);

var idp4_function_switch = getprop("/save/idp4-switch-pos");
var idp4_major_function_bfs = getprop("/save/idp4-bfs-major-function");

setprop("/fdm/jsbsim/systems/dps/idp-function-switch[3]", idp4_function_switch);
SpaceShuttle.idp_array[3].set_bfs_major_function(idp4_major_function_bfs);

# GPC config

SpaceShuttle.gpc_array[0].set_memory(getprop("/save/gpc1-mcc"));
SpaceShuttle.gpc_array[1].set_memory(getprop("/save/gpc2-mcc"));
SpaceShuttle.gpc_array[2].set_memory(getprop("/save/gpc3-mcc"));
SpaceShuttle.gpc_array[3].set_memory(getprop("/save/gpc4-mcc"));
SpaceShuttle.gpc_array[4].set_memory(getprop("/save/gpc5-mcc"));

SpaceShuttle.gpc_array[0].set_mode(getprop("/save/gpc1-mode"));
SpaceShuttle.gpc_array[1].set_mode(getprop("/save/gpc2-mode"));
SpaceShuttle.gpc_array[2].set_mode(getprop("/save/gpc3-mode"));
SpaceShuttle.gpc_array[3].set_mode(getprop("/save/gpc4-mode"));
SpaceShuttle.gpc_array[4].set_mode(getprop("/save/gpc5-mode"));

var gpc1_mode_switch = getprop("/save/gpc1-mode-switch");
var gpc2_mode_switch = getprop("/save/gpc2-mode-switch");
var gpc3_mode_switch = getprop("/save/gpc3-mode-switch");
var gpc4_mode_switch = getprop("/save/gpc4-mode-switch");
var gpc5_mode_switch = getprop("/save/gpc5-mode-switch");

setprop("/fdm/jsbsim/systems/dps/gpc1-mode-switch", gpc1_mode_switch);
setprop("/fdm/jsbsim/systems/dps/gpc2-mode-switch", gpc2_mode_switch);
setprop("/fdm/jsbsim/systems/dps/gpc3-mode-switch", gpc3_mode_switch);
setprop("/fdm/jsbsim/systems/dps/gpc4-mode-switch", gpc4_mode_switch);
setprop("/fdm/jsbsim/systems/dps/gpc5-mode-switch", gpc5_mode_switch);

SpaceShuttle.nbat.string1 = getprop("/save/nbat-string1");
SpaceShuttle.nbat.string2 = getprop("/save/nbat-string2");
SpaceShuttle.nbat.string3 = getprop("/save/nbat-string3");
SpaceShuttle.nbat.string4 = getprop("/save/nbat-string4");


SpaceShuttle.nbat.launch1 = getprop("/save/nbat-launch1");
SpaceShuttle.nbat.launch2 = getprop("/save/nbat-launch2");

SpaceShuttle.nbat.pl1 = getprop("/save/nbat-pl1");
SpaceShuttle.nbat.pl2 = getprop("/save/nbat-pl2");

SpaceShuttle.nbat.pl1 = getprop("/save/nbat-mm1");
SpaceShuttle.nbat.pl2 = getprop("/save/nbat-mm2");

SpaceShuttle.nbat.crt[0] = getprop("/save/nbat-crt1");
SpaceShuttle.nbat.crt[1] = getprop("/save/nbat-crt2");
SpaceShuttle.nbat.crt[2] = getprop("/save/nbat-crt3");
SpaceShuttle.nbat.crt[3] = getprop("/save/nbat-crt4");

SpaceShuttle.nbat.crt_sm[0] = getprop("/save/nbat-crt-sm1");
SpaceShuttle.nbat.crt_sm[1] = getprop("/save/nbat-crt-sm2");
SpaceShuttle.nbat.crt_sm[2] = getprop("/save/nbat-crt-sm3");
SpaceShuttle.nbat.crt_sm[3] = getprop("/save/nbat-crt-sm4");

SpaceShuttle.nbat.ops = ops;

SpaceShuttle.nbat.init_string();

if (getprop("/save/bfs-in-control") == 1)
	{
	major_mode = major_mode_bfs;
	SpaceShuttle.bfs_takeover();
	}


# launch guidance

var auto_launch = getprop("/save/auto-launch");
setprop("/fdm/jsbsim/systems/ap/launch/autolaunch-master", auto_launch);

var auto_launch_laststage = getprop("/save/auto-launch-stage");
setprop("/fdm/jsbsim/systems/ap/launch/stage", auto_launch_laststage);


if ((auto_launch == 1) and ((major_mode == 101) or (major_mode == 102) or (major_mode == 103)))
	{
	SpaceShuttle.auto_launch_stage = auto_launch_laststage;
	SpaceShuttle.auto_launch_loop();
	}


var guidance_mode = getprop("/save/guidance-mode");
var landing_site = getprop("/save/landing-site");
var runway = getprop("/save/runway");

setprop("/fdm/jsbsim/systems/entry_guidance/guidance-mode", guidance_mode);

if (guidance_mode > 0) {SpaceShuttle.entry_guidance_available = 1;}

setprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/site", landing_site);
SpaceShuttle.update_site();

setprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/runway", runway);
SpaceShuttle.update_runway();

if (major_mode == 101)
		{SpaceShuttle.ops_transition_auto("p_ascent");}
else if (major_mode == 102)
		{SpaceShuttle.ops_transition_auto("p_ascent");}
else if (major_mode == 103)
		{SpaceShuttle.ops_transition_auto("p_ascent");}
else if (major_mode == 104) 
		{SpaceShuttle.ops_transition_auto("p_dps_mnvr"); SpaceShuttle.orbital_loop_init();}
else if (major_mode == 105)
		{SpaceShuttle.ops_transition_auto("p_dps_mnvr"); SpaceShuttle.orbital_loop_init();}
else if (major_mode == 106) 
		{SpaceShuttle.ops_transition_auto("p_dps_mnvr"); SpaceShuttle.orbital_loop_init();}
else if (major_mode == 201)
		{SpaceShuttle.ops_transition_auto("p_dps_univ_ptg"); SpaceShuttle.orbital_loop_init();}
else if (major_mode == 202)
		{SpaceShuttle.ops_transition_auto("p_dps_mnvr"); SpaceShuttle.orbital_loop_init();}
else if (major_mode == 301)
		{SpaceShuttle.ops_transition_auto("p_dps_mnvr"); SpaceShuttle.orbital_loop_init();}
else if (major_mode == 302)
		{SpaceShuttle.ops_transition_auto("p_dps_mnvr"); SpaceShuttle.orbital_loop_init();}
else if (major_mode == 303) 
		{SpaceShuttle.ops_transition_auto("p_dps_mnvr"); SpaceShuttle.orbital_loop_init();}
else if (major_mode == 304)
		{
		SpaceShuttle.traj_display_flag = 3;
		SpaceShuttle.fill_entry1_data();
		SpaceShuttle.ops_transition_auto("p_entry");
		}
else if (major_mode == 305)
		{
		SpaceShuttle.traj_display_flag = 8;
		SpaceShuttle.ops_transition_auto("p_vert_sit");
		SpaceShuttle.compute_TAEM_guidance_targets();
		}
else if (major_mode == 601)
		{
		setprop("/controls/shuttle/hud-mode",2);
		SpaceShuttle.ops_transition_auto("p_dps_rtls");
		SpaceShuttle.prtls_loop();
		}
else if (major_mode == 602)
		{
		SpaceShuttle.traj_display_flag = 8;
		setprop("/controls/shuttle/hud-mode",2);
		SpaceShuttle.ops_transition_auto("p_vert_sit");
		SpaceShuttle.grtls_loop();
		}
else if (major_mode == 603)
		{
		SpaceShuttle.traj_display_flag = 8;
		setprop("/controls/shuttle/hud-mode",2);
		SpaceShuttle.ops_transition_auto("p_vert_sit");
		SpaceShuttle.compute_TAEM_guidance_targets();
		}



# thermal distribution

var n = size (SpaceShuttle.thermal_array);

for (var i =0; i< n; i=i+1 )
	{
	var T = getprop("/save/temperature["~i~"]");
	SpaceShuttle.thermal_array[i].temperature = T;
	var C_heat = SpaceShuttle.thermal_array[i].mass * SpaceShuttle.thermal_array[i].heat_capacity;
	SpaceShuttle.thermal_array[i].thermal_energy = T * C_heat;
	}


# hydraulic circulation pumps

var circ_pump1 = getprop("/save/hyd-circ-pump1");
var circ_pump2 = getprop("/save/hyd-circ-pump2");
var circ_pump3 = getprop("/save/hyd-circ-pump3");

setprop("/fdm/jsbsim/systems/apu/apu/hyd-circ-pump-cmd", circ_pump1);
setprop("/fdm/jsbsim/systems/apu/apu[1]/hyd-circ-pump-cmd", circ_pump2);
setprop("/fdm/jsbsim/systems/apu/apu[2]/hyd-circ-pump-cmd", circ_pump3);

if (circ_pump1 == 0) {setprop("/fdm/jsbsim/systems/apu/apu/hyd-circ-pump-cmd-dlg", 1);}
else {setprop("/fdm/jsbsim/systems/apu/apu/hyd-circ-pump-cmd-dlg", 0);}

if (circ_pump2 == 0) {setprop("/fdm/jsbsim/systems/apu/apu[1]/hyd-circ-pump-cmd-dlg", 1);}
else {setprop("/fdm/jsbsim/systems/apu/apu[1]/hyd-circ-pump-cmd-dlg", 0);}

if (circ_pump3 == 0) {setprop("/fdm/jsbsim/systems/apu/apu[2]/hyd-circ-pump-cmd-dlg", 1);}
else {setprop("/fdm/jsbsim/systems/apu/apu[2]/hyd-circ-pump-cmd-dlg", 0);}


# RCS and OMS heaters

var heater_fwd_A = getprop("/save/heater-fwd-A");
var heater_fwd_B = getprop("/save/heater-fwd-B");

setprop("/fdm/jsbsim/systems/rcs-hardware/heater-fwd-A-status", heater_fwd_A);
setprop("/fdm/jsbsim/systems/rcs-hardware/heater-fwd-B-status", heater_fwd_B);

#var heater_left_A = getprop("/save/heater-left-A");
#var heater_left_B = getprop("/save/heater-left-B");

#setprop("/fdm/jsbsim/systems/rcs-hardware/heater-left-A-status", heater_left_A);
#setprop("/fdm/jsbsim/systems/rcs-hardware/heater-left-B-status", heater_left_B);

#var heater_right_A = getprop("/save/heater-right-A");
#var heater_right_B = getprop("/save/heater-right-B");

#setprop("/fdm/jsbsim/systems/rcs-hardware/heater-right-A-status", heater_right_A);
#setprop("/fdm/jsbsim/systems/rcs-hardware/heater-right-B-status", heater_right_B);

var heater_oms_left_A = getprop("/save/heater-oms-left-A");
var heater_oms_left_B = getprop("/save/heater-oms-left-B");

setprop("/fdm/jsbsim/systems/oms-hardware/heater-left-A-status", heater_oms_left_A);
setprop("/fdm/jsbsim/systems/oms-hardware/heater-left-B-status", heater_oms_left_B);

var heater_oms_right_A = getprop("/save/heater-oms-right-A");
var heater_oms_right_B = getprop("/save/heater-oms-right-B");

setprop("/fdm/jsbsim/systems/oms-hardware/heater-right-A-status", heater_oms_right_A);
setprop("/fdm/jsbsim/systems/oms-hardware/heater-right-B-status", heater_oms_right_B);

var heater_xfeed_A = getprop("/save/heater-oms-xfeed-A");
var heater_xfeed_B = getprop("/save/heater-oms-xfeed-B");

setprop("/fdm/jsbsim/systems/oms-hardware/heater-crossfeed-A-status", heater_xfeed_A);
setprop("/fdm/jsbsim/systems/oms-hardware/heater-crossfeed-B-status", heater_xfeed_B);



# propellant valve configuration

var helium_left_oms_A = getprop("/save/valve-helium-left-oms-A");
var helium_left_oms_B = getprop("/save/valve-helium-left-oms-B");

setprop("/fdm/jsbsim/systems/oms-hardware/helium-left-oms-valve-A-status", helium_left_oms_A);
setprop("/fdm/jsbsim/systems/oms-hardware/helium-left-oms-valve-B-status", helium_left_oms_B);

var helium_right_oms_A = getprop("/save/valve-helium-right-oms-A");
var helium_right_oms_B = getprop("/save/valve-helium-right-oms-B");

setprop("/fdm/jsbsim/systems/oms-hardware/helium-right-oms-valve-A-status", helium_right_oms_A);
setprop("/fdm/jsbsim/systems/oms-hardware/helium-right-oms-valve-B-status", helium_right_oms_B);

var helium_kit_oms_A = getprop("/save/valve-helium-kit-oms-A");
var helium_kit_oms_B = getprop("/save/valve-helium-kit-oms-B");

setprop("/fdm/jsbsim/systems/oms-hardware/helium-kit-oms-valve-A-status", helium_kit_oms_A);
setprop("/fdm/jsbsim/systems/oms-hardware/helium-kit-oms-valve-B-status", helium_kit_oms_B);

var tank_left_oms_A = getprop("/save/valve-tank-left-oms-A");
var tank_left_oms_B = getprop("/save/valve-tank-left-oms-B");

setprop("/fdm/jsbsim/systems/oms-hardware/tank-left-oms-valve-A-status", tank_left_oms_A);
setprop("/fdm/jsbsim/systems/oms-hardware/tank-left-oms-valve-B-status", tank_left_oms_B);

var tank_right_oms_A = getprop("/save/valve-tank-right-oms-A");
var tank_right_oms_B = getprop("/save/valve-tank-right-oms-B");

setprop("/fdm/jsbsim/systems/oms-hardware/tank-right-oms-valve-A-status", tank_right_oms_A);
setprop("/fdm/jsbsim/systems/oms-hardware/tank-right-oms-valve-B-status", tank_right_oms_B);

var tank_kit_oms_A = getprop("/save/valve-tank-kit-oms-A");
var tank_kit_oms_B = getprop("/save/valve-tank-kit-oms-B");

setprop("/fdm/jsbsim/systems/oms-hardware/tank-kit-oms-valve-A-status", tank_kit_oms_A);
setprop("/fdm/jsbsim/systems/oms-hardware/tank-kit-oms-valve-B-status", tank_kit_oms_B);

var xfeed_left_oms_A = getprop("/save/valve-xfeed-left-oms-A");
var xfeed_left_oms_B = getprop("/save/valve-xfeed-left-oms-B");

setprop("/fdm/jsbsim/systems/oms-hardware/crossfeed-left-oms-valve-A-status", xfeed_left_oms_A);
setprop("/fdm/jsbsim/systems/oms-hardware/crossfeed-left-oms-valve-B-status", xfeed_left_oms_B);

var xfeed_right_oms_A = getprop("/save/valve-xfeed-right-oms-A");
var xfeed_right_oms_B = getprop("/save/valve-xfeed-right-oms-B");

setprop("/fdm/jsbsim/systems/oms-hardware/crossfeed-right-oms-valve-A-status", xfeed_right_oms_A);
setprop("/fdm/jsbsim/systems/oms-hardware/crossfeed-right-oms-valve-B-status", xfeed_right_oms_B);



var helium_left_rcs_A = getprop("/save/valve-helium-left-rcs-A");
var helium_left_rcs_B = getprop("/save/valve-helium-left-rcs-B");

setprop("/fdm/jsbsim/systems/rcs-hardware/helium-left-rcs-valve-A-status", helium_left_rcs_A);
setprop("/fdm/jsbsim/systems/rcs-hardware/helium-left-rcs-valve-B-status", helium_left_rcs_B);


var helium_right_rcs_A = getprop("/save/valve-helium-right-rcs-A");
var helium_right_rcs_B = getprop("/save/valve-helium-right-rcs-B");

setprop("/fdm/jsbsim/systems/rcs-hardware/helium-right-rcs-valve-A-status", helium_right_rcs_A);
setprop("/fdm/jsbsim/systems/rcs-hardware/helium-right-rcs-valve-B-status", helium_right_rcs_B);

var tank_left_rcs_12 = getprop("/save/valve-tank-left-rcs-12");
var tank_left_rcs_345A = getprop("/save/valve-tank-left-rcs-345A");
var tank_left_rcs_345B = getprop("/save/valve-tank-left-rcs-345B");

setprop("/fdm/jsbsim/systems/rcs-hardware/tank-left-rcs-valve-12-status", tank_left_rcs_12);
setprop("/fdm/jsbsim/systems/rcs-hardware/tank-left-rcs-valve-345A-status", tank_left_rcs_345A);
setprop("/fdm/jsbsim/systems/rcs-hardware/tank-left-rcs-valve-345B-status", tank_left_rcs_345B);

var tank_left_rcs_mfold_1 = getprop("/save/valve-tank-left-rcs-mfold-1");
var tank_left_rcs_mfold_2 = getprop("/save/valve-tank-left-rcs-mfold-2");
var tank_left_rcs_mfold_3 = getprop("/save/valve-tank-left-rcs-mfold-3");
var tank_left_rcs_mfold_4 = getprop("/save/valve-tank-left-rcs-mfold-4");
var tank_left_rcs_mfold_5 = getprop("/save/valve-tank-left-rcs-mfold-5");


setprop("/fdm/jsbsim/systems/rcs-hardware/mfold-left-rcs-valve-1-status", tank_left_rcs_mfold_1);
setprop("/fdm/jsbsim/systems/rcs-hardware/mfold-left-rcs-valve-2-status", tank_left_rcs_mfold_2);
setprop("/fdm/jsbsim/systems/rcs-hardware/mfold-left-rcs-valve-3-status", tank_left_rcs_mfold_3);
setprop("/fdm/jsbsim/systems/rcs-hardware/mfold-left-rcs-valve-4-status", tank_left_rcs_mfold_4);
setprop("/fdm/jsbsim/systems/rcs-hardware/mfold-left-rcs-valve-5-status", tank_left_rcs_mfold_5);


var tank_left_rcs_xfeed_12 = getprop("/save/tank-left-rcs-xfeed-12");
var tank_left_rcs_xfeed_345 = getprop("/save/tank-left-rcs-xfeed-345");

setprop("/fdm/jsbsim/systems/rcs-hardware/crossfeed-left-rcs-valve-12-status", tank_left_rcs_xfeed_12);
setprop("/fdm/jsbsim/systems/rcs-hardware/crossfeed-left-rcs-valve-345-status", tank_left_rcs_xfeed_345);


var tank_right_rcs_12 = getprop("/save/valve-tank-right-rcs-12");
var tank_right_rcs_345A = getprop("/save/valve-tank-right-rcs-345A");
var tank_right_rcs_345B = getprop("/save/valve-tank-right-rcs-345B");

setprop("/fdm/jsbsim/systems/rcs-hardware/tank-right-rcs-valve-12-status", tank_right_rcs_12);
setprop("/fdm/jsbsim/systems/rcs-hardware/tank-right-rcs-valve-345A-status", tank_right_rcs_345A);
setprop("/fdm/jsbsim/systems/rcs-hardware/tank-right-rcs-valve-345B-status", tank_right_rcs_345B);


var tank_right_rcs_mfold_1 = getprop("/save/valve-tank-right-rcs-mfold-1");
var tank_right_rcs_mfold_2 = getprop("/save/valve-tank-right-rcs-mfold-2");
var tank_right_rcs_mfold_3 = getprop("/save/valve-tank-right-rcs-mfold-3");
var tank_right_rcs_mfold_4 = getprop("/save/valve-tank-right-rcs-mfold-4");
var tank_right_rcs_mfold_5 = getprop("/save/valve-tank-right-rcs-mfold-5");

setprop("/fdm/jsbsim/systems/rcs-hardware/mfold-right-rcs-valve-1-status", tank_right_rcs_mfold_1);
setprop("/fdm/jsbsim/systems/rcs-hardware/mfold-right-rcs-valve-2-status", tank_right_rcs_mfold_2);
setprop("/fdm/jsbsim/systems/rcs-hardware/mfold-right-rcs-valve-3-status", tank_right_rcs_mfold_3);
setprop("/fdm/jsbsim/systems/rcs-hardware/mfold-right-rcs-valve-4-status", tank_right_rcs_mfold_4);
setprop("/fdm/jsbsim/systems/rcs-hardware/mfold-right-rcs-valve-5-status", tank_right_rcs_mfold_5);


var tank_right_rcs_xfeed_12 = getprop("/save/tank-right-rcs-xfeed-12");
var tank_right_rcs_xfeed_345 = getprop("/save/tank-right-rcs-xfeed-345");

setprop("/fdm/jsbsim/systems/rcs-hardware/crossfeed-right-rcs-valve-12-status", tank_right_rcs_xfeed_12);
setprop("/fdm/jsbsim/systems/rcs-hardware/crossfeed-right-rcs-valve-345-status", tank_right_rcs_xfeed_345);

# display power switches

var display_L1_pwr_switch = getprop("/save/display-L1-pwr-switch");
setprop("/fdm/jsbsim/systems/electrical/display/L1-pwr-switch", display_L1_pwr_switch);

var display_L2_pwr_switch = getprop("/save/display-L2-pwr-switch");
setprop("/fdm/jsbsim/systems/electrical/display/L2-pwr-switch", display_L2_pwr_switch);

var display_C1_pwr_switch = getprop("/save/display-C1-pwr-switch");
setprop("/fdm/jsbsim/systems/electrical/display/C1-pwr-switch", display_C1_pwr_switch);

var display_C2_pwr_switch = getprop("/save/display-C2-pwr-switch");
setprop("/fdm/jsbsim/systems/electrical/display/C2-pwr-switch", display_C2_pwr_switch);

var display_C3_pwr_switch = getprop("/save/display-C3-pwr-switch");
setprop("/fdm/jsbsim/systems/electrical/display/C3-pwr-switch", display_C3_pwr_switch);

var display_C4_pwr_switch = getprop("/save/display-C4-pwr-switch");
setprop("/fdm/jsbsim/systems/electrical/display/C4-pwr-switch", display_C4_pwr_switch);

var display_C5_pwr_switch = getprop("/save/display-C5-pwr-switch");
setprop("/fdm/jsbsim/systems/electrical/display/C5-pwr-switch", display_C5_pwr_switch);

var display_R1_pwr_switch = getprop("/save/display-R1-pwr-switch");
setprop("/fdm/jsbsim/systems/electrical/display/R1-pwr-switch", display_R1_pwr_switch);

var display_R2_pwr_switch = getprop("/save/display-R2-pwr-switch");
setprop("/fdm/jsbsim/systems/electrical/display/R2-pwr-switch", display_R2_pwr_switch);

var display_A6_pwr_switch = getprop("/save/display-A6-pwr-switch");
setprop("/fdm/jsbsim/systems/electrical/display/A6-pwr-switch", display_A6_pwr_switch);

var display_R11_pwr_switch = getprop("/save/display-R11-pwr-switch");
setprop("/fdm/jsbsim/systems/electrical/display/R11-pwr-switch", display_R11_pwr_switch);



# BFS switches

var bfs_display_switch = getprop("/save/bfs-display-switch");
setprop("/fdm/jsbsim/systems/dps/bfs/display-switch", bfs_display_switch);

var bfs_crt_select_switch = getprop("/save/bfs-crt-select-switch");
setprop("/fdm/jsbsim/systems/dps/bfs/crt-select-switch", bfs_crt_select_switch);


# FES switches

var fes_heater_left_switch = getprop("/save/fes-heater-left-switch");
setprop("/fdm/jsbsim/systems/atcs/fes-heater-left-status", fes_heater_left_switch);

var fes_heater_right_switch = getprop("/save/fes-heater-right-switch");
setprop("/fdm/jsbsim/systems/atcs/fes-heater-right-status", fes_heater_right_switch);


# IMU errors

for (var i=0; i< SpaceShuttle.imu_system.num_units; i=i+1)
	{

	SpaceShuttle.imu_system.imu[i].pitch_error = getprop("/save/imu["~i~"]/pitch-error");
	SpaceShuttle.imu_system.imu[i].yaw_error = getprop("/save/imu["~i~"]/yaw-error");
	SpaceShuttle.imu_system.imu[i].roll_error = getprop("/save/imu["~i~"]/roll-error");
	}


# fuel cell efficiency

var fc1_efficiency = getprop("/save/fc1-efficiency");
var fc2_efficiency = getprop("/save/fc2-efficiency");
var fc3_efficiency = getprop("/save/fc3-efficiency");

setprop("/fdm/jsbsim/systems/electrical/fc/fc-efficiency", fc1_efficiency);
setprop("/fdm/jsbsim/systems/electrical/fc[1]/fc-efficiency", fc2_efficiency);
setprop("/fdm/jsbsim/systems/electrical/fc[2]/fc-efficiency", fc3_efficiency);


# engine controller power switches

var engine1_controller_A_switch = getprop("/save/engine1_controller-A-power-switch-status");
var engine1_controller_B_switch = getprop("/save/engine1_controller-B-power-switch-status");

setprop("/fdm/jsbsim/systems/mps/engine/controller-A-power-switch-status", engine1_controller_A_switch);
setprop("/fdm/jsbsim/systems/mps/engine/controller-B-power-switch-status", engine1_controller_B_switch);


var engine2_controller_A_switch = getprop("/save/engine2_controller-A-power-switch-status");
var engine2_controller_B_switch = getprop("/save/engine2_controller-B-power-switch-status");

setprop("/fdm/jsbsim/systems/mps/engine[1]/controller-A-power-switch-status", engine2_controller_A_switch);
setprop("/fdm/jsbsim/systems/mps/engine[1]/controller-B-power-switch-status", engine2_controller_B_switch);

var engine3_controller_A_switch = getprop("/save/engine3_controller-A-power-switch-status");
var engine3_controller_B_switch = getprop("/save/engine3_controller-B-power-switch-status");

setprop("/fdm/jsbsim/systems/mps/engine[2]/controller-A-power-switch-status", engine3_controller_A_switch);
setprop("/fdm/jsbsim/systems/mps/engine[2]/controller-B-power-switch-status", engine3_controller_B_switch);




# helium isolation switches

var engine1_helium_isolation_A_switch = getprop("/save/engine1_helium-isolation-valve-A-status");
var engine1_helium_isolation_B_switch = getprop("/save/engine1_helium-isolation-valve-B-status");

setprop("/fdm/jsbsim/systems/mps/engine/helium-isolation-valve-A-status", engine1_helium_isolation_A_switch);
setprop("/fdm/jsbsim/systems/mps/engine/helium-isolation-valve-B-status", engine1_helium_isolation_B_switch);

var engine2_helium_isolation_A_switch = getprop("/save/engine2_helium-isolation-valve-A-status");
var engine2_helium_isolation_B_switch = getprop("/save/engine2_helium-isolation-valve-B-status");

setprop("/fdm/jsbsim/systems/mps/engine[1]/helium-isolation-valve-A-status", engine2_helium_isolation_A_switch);
setprop("/fdm/jsbsim/systems/mps/engine[1]/helium-isolation-valve-B-status", engine2_helium_isolation_B_switch);

var engine3_helium_isolation_A_switch = getprop("/save/engine3_helium-isolation-valve-A-status");
var engine3_helium_isolation_B_switch = getprop("/save/engine3_helium-isolation-valve-B-status");

setprop("/fdm/jsbsim/systems/mps/engine[2]/helium-isolation-valve-A-status", engine3_helium_isolation_A_switch);
setprop("/fdm/jsbsim/systems/mps/engine[2]/helium-isolation-valve-B-status", engine3_helium_isolation_B_switch);


var engine1_helium_interconnect_status = getprop("/save/engine1_helium-interconnect-valve-status");
var engine2_helium_interconnect_status = getprop("/save/engine2_helium-interconnect-valve-status");
var engine3_helium_interconnect_status = getprop("/save/engine3_helium-interconnect-valve-status");

setprop("/fdm/jsbsim/systems/mps/engine/helium-interconnect-valve-status", engine1_helium_interconnect_status);
setprop("/fdm/jsbsim/systems/mps/engine[1]/helium-interconnect-valve-status", engine2_helium_interconnect_status);
setprop("/fdm/jsbsim/systems/mps/engine[2]/helium-interconnect-valve-status", engine3_helium_interconnect_status);

var pneumatic_helium_Px_switch = getprop("/save/pneumatic_helium-isolation-valve-Px-status");
setprop("/fdm/jsbsim/systems/mps/helium-isolation-valve-Px-status", pneumatic_helium_Px_switch);

var pneumatic_helium_P_switch = getprop("/save/pneumatic_helium-isolation-valve-P-status");
setprop("/fdm/jsbsim/systems/mps/helium-isolation-valve-P-status", pneumatic_helium_P_switch);

# TVC isolation valves

var sys1_tvc_isolation_valve = getprop("/save/sys1-tvc-isolation-valve");
var sys2_tvc_isolation_valve = getprop("/save/sys2-tvc-isolation-valve");
var sys3_tvc_isolation_valve = getprop("/save/sys3-tvc-isolation-valve");


setprop("/fdm/jsbsim/systems/apu/apu/tvc-isolation-valve-status", sys1_tvc_isolation_valve);
setprop("/fdm/jsbsim/systems/apu/apu[1]/tvc-isolation-valve-status", sys2_tvc_isolation_valve);
setprop("/fdm/jsbsim/systems/apu/apu[2]/tvc-isolation-valve-status", sys3_tvc_isolation_valve);



# ADI attitude reference switch

var adi_attitude_switch = getprop("/save/adi-attitude-switch");
setprop("/fdm/jsbsim/systems/adi/attitude-select", adi_attitude_switch);



# CRT selection switch

var crt_select_left_switch = getprop("/save/crt-select-left-switch");
setprop("/fdm/jsbsim/systems/dps/crtl-sel", crt_select_left_switch);


var crt_select_right_switch = getprop("/save/crt-select-right-switch");
setprop("/fdm/jsbsim/systems/dps/crtr-sel", crt_select_right_switch);


# the orbital target

if (SpaceShuttle.n_orbital_targets > 0)
	{
	var elapsed_time = getprop("/save/otgt-elapsed-time");
	var delta_time = elapsed - elapsed_time;

	SpaceShuttle.oTgt.delta_time = delta_time;

	var anomaly = getprop("/save/otgt-anomaly");
	SpaceShuttle.oTgt.anomaly_rad = anomaly;

	print ("Setting oTgt anomaly to ", anomaly);

	var initial_nl_rad = getprop("/save/otgt-initial-node-lon");
	SpaceShuttle.oTgt.initial_nl_rad = initial_nl_rad + delta_time  * 0.00417807416313755 * math.pi/180.0;

	#print ("New initial NL should be:");
	#print (initial_nl_rad + delta_time  * 0.00417807416313755 * math.pi/180.0);
	

	var initial_anomaly_rad = getprop("/save/otgt-initial-anomaly");
	SpaceShuttle.oTgt.initial_anomaly_rad = initial_anomaly_rad;

	print ("Setting oTgt initial anomaly to ", initial_anomaly_rad);

	var delta_lon = getprop("/save/otgt-delta-lon");
	SpaceShuttle.oTgt.delta_lon = 0.0; # this is covered by the shift in node lognitude

	var node_lon = getprop("/save/otgt-node-lon");
	SpaceShuttle.oTgt.node_longitude = node_lon + delta_time * 0.00417807416313755;

	#print ("Delta lon, node lon");
	#print (delta_lon, " ", node_lon);

	SpaceShuttle.proximity_manager.history_available = 0;
	}


# the payload - first clear existing payload


setprop("/sim/config/shuttle/PL-selection", "none");
SpaceShuttle.update_payload_selection();

var payload_string = getprop("/save/payload-string");
setprop("/sim/config/shuttle/PL-selection", payload_string);

SpaceShuttle.update_payload_selection();


# automatically switch Earthview on if the user has this selected

if ((SpaceShuttle.earthview_flag == 1) and (earthview.earthview_running_flag == 0))
	{
	var alt = getprop("/position/altitude-ft");
	if (alt > SpaceShuttle.earthview_transition_alt)
		{
		if (getprop("/nasal/local_weather/enabled") == 1)
			{
			local_weather.clear_all();
			setprop("/environment/visibility-m", 80000.0);
			}
		earthview.start();
		}

	}

# remove any light manager info 

SpaceShuttle.light_manager.set_theme("CLEAR");

# reset trajectory history

SpaceShuttle.history_reset();

print("State resumed!");
}


