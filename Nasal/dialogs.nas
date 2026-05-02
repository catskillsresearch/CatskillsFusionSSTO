# Nasal scripts for Space Shuttle dialogs
# Thorsten Renk 2015 - 2016

var ascending_node_update = 0;

var description_string_soft = "Aerodynamical, structural and other limits are called out but not enforced, i.e. violating limits does not cause damage to the orbiter.";

var description_string_hard = "Warnings of the approach to aerodynamical and structural limits are called out, any violation of limits ends the simulation.";

var description_string_realistic = "Warnings as well as violations of aerodynamical and structural limits are called out, any violation may cause damage to orbiter systems. The damage is determined probabilistically and not necessarily reported. ";

var scenario_string_none = " ";

var scenario_string_single_engine_failure = "During ascent, a single main engine will fail. Dependent on payload, launch inclination and when the failure occurs, the Shuttle may no longer be able to reach orbit, requiring to follow an abort procedure.";

var scenario_string_single_engine_lockup = "During ascent, a condition occurs which makes one engine lock up, i.e. the engine can no longer be throttled. Anticipate to shut down the affected engine manually prior to MECO using the cutoff switches.";

var scenario_string_attitude = "The Shuttle GNC function has drifted off attitude to a degree that the star trackers no longer function - pitch, yaw and roll will all be off. Use a COAS procedure to fix inertial attitude and re-activate the star tracker.";

var scenario_string_rcs = "A thruster of the RCS system has failed. Use the RCS jet table management function to diagnose the fault and deselect the failed thruster and its counterpart to restore proper RCS functionality.";

var scenario_string_cam = "A GPC unit has failed to synchronize with the others and falls out of the redundant set.";

var scenario_string_stuck_speedbrake = "During the final aerodynamical glide phase, the speedbrake gets stuck. Dependent on when and in what position this happens, TAEM needs to be modified and the aim point for the final approach changed. Deploy gear early to make use of its high drag.";

var scenario_string_hydraulic_failure = "Two of the three hydraulics systems are damaged and priority rate limiting is used to best allocate the remaining hydraulic force to the airfoils. Expect the orbiter to react more sluggish in agressive maneuvers.";

var scenario_string_electric_failure = "There's a major problem with the electrical system, leading to power loss on at least one bus. You need to find the flaw, isolate it and re-configure the orbiter's system to continue the mission.";

var scenario_string_propellant_leakage = "There's a leak somewhere in the propellant distribution system, rapidly depleting available propellant. You need to isolate it and decide whether to continue the mission or whether to do an emergency de-orbit.";

var scenario_string_avionics_bay_fire = "A fire has started in one of the avionics bays and is starting to spread. Smoke is developing, and the fire needs to be quickly brought under control before the avionics is gone.";

var scenario_string_tire_failure = "The right gear tire is damaged. Anticipate to use rudder upon touchdown to correct and use elevons to reduce load on the damaged gear during coast.";

var scenario_string_bad_state_vector = "The navigation state of the Shuttle is bad during entry - expect that guidance and HUD symbols are to some degree misleading until you update the state vector.";

var scenario_string_navigation_problems = "After an avionics bay fire, there's damage to the navigation aids. Expect part of the equipment to be non-functioning or showing wrong data - you may need to solve dilemmas or fly by visual cues.";

var scenario_string_pass_failure = "The primary avionics software system (PASS) experiences a software bug that makes the state vector compute wrong. You need to engage the backup flight system (BFS) to save the Shuttle.";

var propellant_dlg = gui.Dialog.new("/sim/gui/dialogs/SpaceShuttle/propellant/dialog","Aircraft/SpaceShuttle/Dialogs/propellant.xml");

var entry_guidance_dlg = gui.Dialog.new("/sim/gui/dialogs/SpaceShuttle/entry_guidance/dialog","Aircraft/SpaceShuttle/Dialogs/entry_guidance.xml");

var autolaunch_dlg = gui.Dialog.new("/sim/gui/dialogs/SpaceShuttle/autolaunch/dialog","Aircraft/SpaceShuttle/Dialogs/auto_launch.xml");


var limits_dlg = gui.Dialog.new("/sim/gui/dialogs/SpaceShuttle/limits/dialog","Aircraft/SpaceShuttle/Dialogs/limits.xml");

var apu_dlg = gui.Dialog.new("/sim/gui/dialogs/SpaceShuttle/apu/dialog","Aircraft/SpaceShuttle/Dialogs/apu.xml");

var atcs_dlg = gui.Dialog.new("/sim/gui/dialogs/SpaceShuttle/atcs/dialog","Aircraft/SpaceShuttle/Dialogs/atcs.xml");

var rcs_oms_thermal_dlg = gui.Dialog.new("/sim/gui/dialogs/SpaceShuttle/rcs_oms_thermal/dialog","Aircraft/SpaceShuttle/Dialogs/rcs_oms_thermal.xml");

var electrical_dlg = gui.Dialog.new("/sim/gui/dialogs/SpaceShuttle/electrical/dialog","Aircraft/SpaceShuttle/Dialogs/electrical.xml");

var ku_dlg = gui.Dialog.new("/sim/gui/dialogs/SpaceShuttle/ku/dialog","Aircraft/SpaceShuttle/Dialogs/ku_antenna.xml");

var mechanical_dlg = gui.Dialog.new("/sim/gui/dialogs/SpaceShuttle/mechanical/dialog","Aircraft/SpaceShuttle/Dialogs/mechanical.xml");

var mps_dlg = gui.Dialog.new("/sim/gui/dialogs/SpaceShuttle/mps/dialog","Aircraft/SpaceShuttle/Dialogs/mps.xml");

var options_dlg = gui.Dialog.new("/sim/gui/dialogs/SpaceShuttle/options/dialog","Aircraft/SpaceShuttle/Dialogs/options.xml");

var rcs_dlg = gui.Dialog.new("/sim/gui/dialogs/SpaceShuttle/rcs/dialog","Aircraft/SpaceShuttle/Dialogs/rcs.xml");

var rms_deploy_dlg = gui.Dialog.new("/sim/gui/dialogs/SpaceShuttle/rms-deploy/dialog","Aircraft/SpaceShuttle/Dialogs/rms_deploy.xml");

var rms_pyro_dlg = gui.Dialog.new("/sim/gui/dialogs/SpaceShuttle/rms-pyro/dialog","Aircraft/SpaceShuttle/Dialogs/rms_pyro.xml");

var pb_floodlight_dlg = gui.Dialog.new("/sim/gui/dialogs/SpaceShuttle/pb-floodlight/dialog","Aircraft/SpaceShuttle/Dialogs/pb_floodlight.xml");

var rms_operation_dlg = gui.Dialog.new("/sim/gui/dialogs/SpaceShuttle/rms-operation/dialog","Aircraft/SpaceShuttle/Dialogs/rms_operation.xml");

var pl_retention_dlg = gui.Dialog.new("/sim/gui/dialogs/SpaceShuttle/payload-retention/dialog","Aircraft/SpaceShuttle/Dialogs/payload_retention.xml");

var flight_controls_dlg = gui.Dialog.new("/sim/gui/dialogs/SpaceShuttle/flight_controls/dialog","Aircraft/SpaceShuttle/Dialogs/flight_controls.xml");

var dps_keyboard_dlg = gui.Dialog.new("/sim/gui/dialogs/SpaceShuttle/dps_keyboard/dialog","Aircraft/SpaceShuttle/Dialogs/dps_keyboard.xml");

var idp_dlg = gui.Dialog.new("/sim/gui/dialogs/SpaceShuttle/idp/dialog","Aircraft/SpaceShuttle/Dialogs/idp_settings.xml");


var temperature_dlg = gui.Dialog.new("/sim/gui/dialogs/SpaceShuttle/temperature/dialog","Aircraft/SpaceShuttle/Dialogs/thermal_distribution.xml");

var propellant_fd_dlg = gui.Dialog.new("/sim/gui/dialogs/SpaceShuttle/propellant_fd/dialog","Aircraft/SpaceShuttle/Dialogs/propellant_fill_drain.xml");

var cabin_lighting_dlg = gui.Dialog.new("/sim/gui/dialogs/SpaceShuttle/cabin-lighting/dialog","Aircraft/SpaceShuttle/Dialogs/cabin_lighting.xml");

var switch_covers_dlg = gui.Dialog.new("/sim/gui/dialogs/SpaceShuttle/switch-covers/dialog","Aircraft/SpaceShuttle/Dialogs/switch_covers.xml");

var save_dlg = gui.Dialog.new("/sim/gui/dialogs/SpaceShuttle/save/dialog","Aircraft/SpaceShuttle/Dialogs/save.xml");

var mcc_status_dlg = gui.Dialog.new("/sim/gui/dialogs/SpaceShuttle/mcc-status/dialog","Aircraft/SpaceShuttle/Dialogs/mcc_status.xml");

var mcc_comm_dlg = gui.Dialog.new("/sim/gui/dialogs/SpaceShuttle/mcc-comm/dialog","Aircraft/SpaceShuttle/Dialogs/mcc_comm.xml");

var touchdown_dlg = gui.Dialog.new("/sim/gui/dialogs/SpaceShuttle/touchdown/dialog","Aircraft/SpaceShuttle/Dialogs/touchdown.xml");

var carrier_dlg = gui.Dialog.new("/sim/gui/dialogs/SpaceShuttle/carrier/dialog","Aircraft/SpaceShuttle/Dialogs/carrier_controls.xml");

var earthview_flag = getprop("/sim/config/shuttle/rendering/use-earthview");
var earthview_transition_alt = getprop("/sim/config/shuttle/rendering/earthview-transition-alt-ft");
var orbital_target_lod = getprop("/sim/config/shuttle/rendering/orbital-target-lod-m");


setprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/site", "Vandenberg Air Force Base");
setprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/runway", "12");
setprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/available-runways/value", "12");
setprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/available-runways/value[1]", "30");
setprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/entry-mode", "normal");
setprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/site-lat",34.722);
setprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/site-lon",-120.567);
setprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/site-string", "inactive");
setprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/EI-radius", 4100.0);

setprop("/sim/gui/dialogs/SpaceShuttle/limits/limit-mode", "realistic");
setprop("/sim/gui/dialogs/SpaceShuttle/limits/limit-mode-description", description_string_realistic);

setprop("/sim/gui/dialogs/SpaceShuttle/limits/failure-scenario", "none");
setprop("/sim/gui/dialogs/SpaceShuttle/limits/failure-scenario-description", " ");
setprop("/fdm/jsbsim/systems/failures/failure-scenario-ID", 0);

setprop("/sim/gui/dialogs/SpaceShuttle/ku-antenna/function", "COMM");
setprop("/sim/gui/dialogs/SpaceShuttle/ku-antenna/control", "GPC");
setprop("/sim/gui/dialogs/SpaceShuttle/S-antenna/mode", "S-HI");

#gui.menuBind("fuel-and-payload", "SpaceShuttle.propellant_dlg.open(); ");
gui.menuBind("fuel-and-payload",  "SpaceShuttle.cdlg_propellant.init();");
gui.menuEnable("fuel-and-payload", 1);



var update_description = func {

var mode_string = getprop("/sim/gui/dialogs/SpaceShuttle/limits/limit-mode");

if (mode_string == "soft")
	{
	setprop("/sim/gui/dialogs/SpaceShuttle/limits/limit-mode-description", description_string_soft);
	setprop("/fdm/jsbsim/systems/failures/limit-simulation-mode", 0);
	}
else if (mode_string == "realistic")
	{
	setprop("/sim/gui/dialogs/SpaceShuttle/limits/limit-mode-description", description_string_realistic);
	setprop("/fdm/jsbsim/systems/failures/limit-simulation-mode", 1);
	}
if (mode_string == "hard")
	{
	setprop("/sim/gui/dialogs/SpaceShuttle/limits/limit-mode-description", description_string_hard);
	setprop("/fdm/jsbsim/systems/failures/limit-simulation-mode", 2);
	}

}


var update_scenario = func {

var scenario_string = getprop("/sim/gui/dialogs/SpaceShuttle/limits/failure-scenario");


if (scenario_string == "none")
	{
	setprop("/sim/gui/dialogs/SpaceShuttle/limits/failure-scenario-description", scenario_string_none);
	setprop("/fdm/jsbsim/systems/failures/failure-scenario-ID", 0);
	}
else if (scenario_string == "ascent single engine failure")
	{
	setprop("/sim/gui/dialogs/SpaceShuttle/limits/failure-scenario-description", scenario_string_single_engine_failure);
	setprop("/fdm/jsbsim/systems/failures/failure-scenario-ID", 1);
	}
else if (scenario_string == "ascent single engine lockup")
	{
	setprop("/sim/gui/dialogs/SpaceShuttle/limits/failure-scenario-description", scenario_string_single_engine_lockup);
	setprop("/fdm/jsbsim/systems/failures/failure-scenario-ID", 2);
	}
else if (scenario_string == "PASS failure")
	{
	setprop("/sim/gui/dialogs/SpaceShuttle/limits/failure-scenario-description", scenario_string_pass_failure);
	setprop("/fdm/jsbsim/systems/failures/failure-scenario-ID", 3);
	}
else if (scenario_string == "off attitude")
	{
	setprop("/sim/gui/dialogs/SpaceShuttle/limits/failure-scenario-description", scenario_string_attitude);
	setprop("/fdm/jsbsim/systems/failures/failure-scenario-ID", 20);
	}
else if (scenario_string == "RCS failure")
	{
	setprop("/sim/gui/dialogs/SpaceShuttle/limits/failure-scenario-description", scenario_string_rcs);
	setprop("/fdm/jsbsim/systems/failures/failure-scenario-ID", 21);
	}
else if (scenario_string == "electric failure")
	{
	setprop("/sim/gui/dialogs/SpaceShuttle/limits/failure-scenario-description", scenario_string_electric_failure);
	setprop("/fdm/jsbsim/systems/failures/failure-scenario-ID", 22);
	}
else if (scenario_string == "propellant leak")
	{
	setprop("/sim/gui/dialogs/SpaceShuttle/limits/failure-scenario-description", scenario_string_propellant_leakage);
	setprop("/fdm/jsbsim/systems/failures/failure-scenario-ID", 23);
	}
else if (scenario_string == "avionics bay fire")
	{
	setprop("/sim/gui/dialogs/SpaceShuttle/limits/failure-scenario-description", scenario_string_avionics_bay_fire);
	setprop("/fdm/jsbsim/systems/failures/failure-scenario-ID", 24);
	}
else if (scenario_string == "GPC sync failure")
	{
	setprop("/sim/gui/dialogs/SpaceShuttle/limits/failure-scenario-description", scenario_string_cam);
	setprop("/fdm/jsbsim/systems/failures/failure-scenario-ID", 25);
	}
else if (scenario_string == "stuck speedbrake")
	{
	setprop("/sim/gui/dialogs/SpaceShuttle/limits/failure-scenario-description", scenario_string_stuck_speedbrake);
	setprop("/fdm/jsbsim/systems/failures/failure-scenario-ID", 31);
	}
else if (scenario_string == "burst tire")
	{
	setprop("/sim/gui/dialogs/SpaceShuttle/limits/failure-scenario-description", scenario_string_tire_failure);
	setprop("/fdm/jsbsim/systems/failures/failure-scenario-ID", 32);
	}
else if (scenario_string == "hydraulic failure")
	{
	setprop("/sim/gui/dialogs/SpaceShuttle/limits/failure-scenario-description", scenario_string_hydraulic_failure);
	setprop("/fdm/jsbsim/systems/failures/failure-scenario-ID", 33);
	}
else if (scenario_string == "bad state vector at TAEM")
	{
	setprop("/sim/gui/dialogs/SpaceShuttle/limits/failure-scenario-description", scenario_string_bad_state_vector);
	setprop("/fdm/jsbsim/systems/failures/failure-scenario-ID", 34);
	}
else if (scenario_string == "navigation problems")
	{
	setprop("/sim/gui/dialogs/SpaceShuttle/limits/failure-scenario-description", scenario_string_navigation_problems);
	setprop("/fdm/jsbsim/systems/failures/failure-scenario-ID", 35);
	}


}


var update_runway_by_flag = func (flag) {

var site_string = getprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/site");


var data = SpaceShuttle.landing_site_data.entry_by_name(site_string);

if (flag == 0)
	{
	setprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/runway", data.rwy_pri);
	}
else
	{
	setprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/runway", data.rwy_sec);
	}



}

var update_runway = func {


var site_string = getprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/site");
var runway_string = getprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/runway");

var data = SpaceShuttle.landing_site_data.entry_by_name(site_string);

if (runway_string == data.rwy_pri) {SpaceShuttle.landing_site.rwy_sel = 0;}
else {SpaceShuttle.landing_site.rwy_sel = 1;}


}



var update_site_by_index = func (index) {

var data = landing_site_data.entry_by_index (index);

setprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/site", data.name);

update_site();


}

var update_site = func {

#print("Hello!");

var site_string = getprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/site");

var lat = 0.0;
var lon = 0.0;
var index = 0;
var rwy_pri = "";
var rwy_sec = "";
var tacan = "";

#setprop("/fdm/jsbsim/systems/entry_guidance/guidance-mode",0);
#setprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/site-string", "inactive");


var data = landing_site_data.entry_by_name (site_string);

lat = data.coord.lat();
lon = data.coord.lon();
index = data.index;
rwy_pri = data.rwy_pri_name;
rwy_sec = data.rwy_sec_name;
tacan = data.tacan;

setprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/runway", data.rwy_pri);
setprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/available-runways/value", data.rwy_pri);
setprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/available-runways/value[1]", data.rwy_sec);



setprop("/fdm/jsbsim/systems/taem-guidance/approach-mode-string", "OVHD");

setprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/site-lat", lat);
setprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/site-lon", lon);
SpaceShuttle.landing_site.set_latlon(lat,lon);
SpaceShuttle.landing_site.index = index;
SpaceShuttle.landing_site.rwy_pri = rwy_pri;
SpaceShuttle.landing_site.rwy_sec = rwy_sec;
SpaceShuttle.landing_site.tacan = tacan;

}


var update_entry_mode = func {


var mode_string = getprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/entry-mode");

if (getprop("/fdm/jsbsim/systems/entry_guidance/guidance-mode") == 0)
	{
	return;
	}

if (mode_string == "normal")
	{
	setprop("/fdm/jsbsim/systems/entry_guidance/guidance-mode", 1);
	SpaceShuttle.entry_guidance_available = 1;
	}
else if (mode_string == "TAL")
	{
	setprop("/fdm/jsbsim/systems/entry_guidance/guidance-mode", 2);
	SpaceShuttle.entry_guidance_available = 1;
	}
else if (mode_string == "RTLS")
	{
	#setprop("/fdm/jsbsim/systems/entry_guidance/guidance-mode", 3);
	#setprop("/controls/shuttle/hud-mode",2);
	#setprop("/fdm/jsbsim/systems/dps/major-mode", 601);
	#setprop("/fdm/jsbsim/systems/dps/ops", 6);
	#SpaceShuttle.ops_transition_auto("p_dps_rtls");
	#SpaceShuttle.prtls_loop();
	SpaceShuttle.init_rtls();
	}

}

var update_MDU_speed = func {


var setting = getprop("/sim/config/shuttle/mdu-update-speed");

if (setting == 0)
	{SpaceShuttle.MDU_update_time = 0.2; SpaceShuttle.MDU_update_number = 1;}
else if (setting == 1)
	{SpaceShuttle.MDU_update_time = 0.1; SpaceShuttle.MDU_update_number = 1;}
else if (setting == 2)
	{SpaceShuttle.MDU_update_time = 0.05; SpaceShuttle.MDU_update_number = 1;}
else if (setting == 3)
	{SpaceShuttle.MDU_update_time = 0.025; SpaceShuttle.MDU_update_number = 1;}
else
	{SpaceShuttle.MDU_update_time = 0.0; SpaceShuttle.MDU_update_number = 2;}

}

var update_ET_config = func{

var ET_string = getprop("/sim/config/shuttle/ET-config");

# do nothing if we don't have an ET connected, otherwise we'll add weight

var tank_status = getprop("/controls/shuttle/ET-static-model");

if (tank_status == 0) {return;}

if (ET_string == "super lightweight")
	{
	setprop("/fdm/jsbsim/inertia/pointmass-weight-lbs[1]", 29250.0);
	setprop("/fdm/jsbsim/inertia/pointmass-weight-lbs[2]", 29250.0);
	}

else if (ET_string == "lightweight")
	{
	setprop("/fdm/jsbsim/inertia/pointmass-weight-lbs[1]", 33000.0);
	setprop("/fdm/jsbsim/inertia/pointmass-weight-lbs[2]", 33000.0);
	}
else if (ET_string == "standard weight")
	{
	setprop("/fdm/jsbsim/inertia/pointmass-weight-lbs[1]", 38500.0);
	setprop("/fdm/jsbsim/inertia/pointmass-weight-lbs[2]", 38500.0);
	}

}

var update_TC_config = func {

var TC_string = getprop("/sim/config/shuttle/TC-config");


var flag = 1;

if (getprop("/controls/shuttle/ET-static-model") == 1)
	{flag = 0;}

if (getprop("/position/altitude-ft") > 40000.0)
	{flag = 0;}

if (flag == 0)
	{return;}

if (TC_string == "none")
	{
	setprop("/sim/config/shuttle/approach-and-landing-test-config", 0);
	}
else if (TC_string == "use tailcone")
	{
	setprop("/sim/config/shuttle/approach-and-landing-test-config", 1);
	}



}


var pb_door_manager = func {

var mode = getprop("/fdm/jsbsim/systems/mechanical/pb-door-mode-auto");

if (mode == 0) {return;}

var switch_condition = getprop("/fdm/jsbsim/systems/failures/payload-bay-switch-condition");

if (switch_condition < 1.0)
	{
	return;
	}



var cmd = getprop("/fdm/jsbsim/systems/mechanical/pb-door-auto-switch");



if (cmd == -1)
	{
	SpaceShuttle.payload_bay_door_close_auto(0);
	}
else if (cmd == 1)
	{
	SpaceShuttle.payload_bay_door_open_auto(0);
	}

}


var thermal_speed_manager = func {

var cmd = getprop("/sim/config/shuttle/thermal-system-computation-speed");

if (cmd == 0)
	{
	setprop("/fdm/jsbsim/systems/thermal-distribution/computation-timestep-s", 10.0);
	}
else if (cmd == 1)
	{
	setprop("/fdm/jsbsim/systems/thermal-distribution/computation-timestep-s", 1.0);
	}
else if (cmd == 2)
	{
	setprop("/fdm/jsbsim/systems/thermal-distribution/computation-timestep-s", 0.1);
	}

}

var update_earthview_manager = func {

earthview_flag = getprop("/sim/config/shuttle/rendering/use-earthview");
earthview_transition_alt = getprop("/sim/config/shuttle/rendering/earthview-transition-alt-ft");

}


var update_rms_joint_selection = func {

var joint_string = getprop("/fdm/jsbsim/systems/rms/joint-selection-string");

var joint = 0;

if (joint_string == "SHOULDER YAW") {joint = 1;}
else if (joint_string == "SHOULDER PITCH") {joint = 2;}
else if (joint_string == "ELBOW PITCH") {joint = 3;}
else if (joint_string == "WRIST PITCH") {joint = 4;}
else if (joint_string == "WRIST YAW") {joint = 5;}
else if (joint_string == "WRIST ROLL") {joint = 6;}
else if (joint_string == "END EFF") {joint = 7;}

setprop("/fdm/jsbsim/systems/rms/joint-selection-mode", joint);
setprop("/fdm/jsbsim/systems/rms/joint-sel-mode", joint -1);

}


var update_rms_parameter_selection = func {

var parameter_string = getprop("/fdm/jsbsim/systems/rms/parameter-selection-string");

var par = 0;

if (parameter_string == "TEST") {par = 0;}
else if (parameter_string == "POSITION X/Y/Z") {par = 1;}
else if (parameter_string == "ATTITUDE P/Y/R") {par = 2;}
else if (parameter_string == "JOINT ANGLE") {par = 3;}

setprop("/fdm/jsbsim/systems/rms/parameter-selection-mode", par);

}


var update_rms_drive_selection_hw = func {

# we need to catch the case that the software override is active which disables
# the cockpit hardware controls but not the GUI

if (getprop("/fdm/jsbsim/systems/rms/software/mode-sw-override") == 1)
	{return;}

update_rms_drive_selection();

}

var update_rms_drive_selection = func {

var drive_string = getprop("/fdm/jsbsim/systems/rms/drive-selection-string");

var par = 0;
var seq_slot = 0;
var act = 0;

if (drive_string == "SINGLE") {par = 1; act = 10;}
else if (drive_string == "DIRECT") {par = 1; act = 11;}
else if (drive_string == "ORB UNL X/Y/Z") {par = 2; act = 6;}
else if (drive_string == "ORB UNL P/Y/R") {par = 3; act = 6;}
else if (drive_string == "AUTO OPR CMD") {par = 4; act = 1;}
else if (drive_string == "AUTO 1") {par = 5; seq_slot = 0; act = 2;}
else if (drive_string == "AUTO 2") {par = 5; seq_slot = 1; act = 3;}
else if (drive_string == "AUTO 3") {par = 5; seq_slot = 2; act = 4;}
else if (drive_string == "AUTO 4") {par = 5; seq_slot = 3; act = 5;}


#print ("Drive selection is now: ", par);

setprop("/fdm/jsbsim/systems/rms/drive-selection-actual", act );
setprop("/fdm/jsbsim/systems/rms/drive-selection-mode", par);

# switch over to the auto mode manager when needed

if (par == 4)
	{
	SpaceShuttle.pdrs_auto_seq_manager.opr_cmd_goto_point();
	return;
	}
else if (par == 5)
	{
	SpaceShuttle.pdrs_auto_seq_manager.start_sequence(seq_slot);
	setprop("/fdm/jsbsim/systems/rms/auto-sequence-slot", seq_slot);
	return;
	}


}


var update_rms_drive_selection_by_par = func (par) {

# par encodes both actual selections on dial and the fact that we have THC and RHC

var drive_string = "";
var drive_mode = 0;
var seq_slot = 0;
var act = 0;

if (par == 0) {drive_string = "SINGLE"; drive_mode = 1; act = 10;}
else if (par == 1) {drive_string = "DIRECT"; drive_mode = 1; act = 11;}
else if (par == 2) {drive_string = "ORB UNL X/Y/Z";  drive_mode = 2; act = 6;}
else if (par == 3) {drive_string = "ORB UNL P/Y/R"; drive_mode = 3; act = 6;}
else if (par == 4) {drive_string = "AUTO OPR CMD"; drive_mode = 4; act = 1;}
else if (par == 5) {drive_string = "AUTO 1"; drive_mode = 5;  seq_slot = 0; act = 2;}
else if (par == 6) {drive_string = "AUTO 2"; drive_mode = 5;  seq_slot = 1; act = 3;}
else if (par == 7) {drive_string = "AUTO 3"; drive_mode = 5;  seq_slot = 2; act = 4;}
else if (par == 8) {drive_string = "AUTO 4"; drive_mode = 5;  seq_slot = 3; act = 5;}

setprop("/fdm/jsbsim/systems/rms/drive-selection-actual", act );

if (drive_mode == 4)
	{
	setprop("/fdm/jsbsim/systems/rms/drive-selection-string", drive_string);
	SpaceShuttle.pdrs_auto_seq_manager.opr_cmd_goto_point();
	return;
	}
else if (drive_mode == 5)
	{
	setprop("/fdm/jsbsim/systems/rms/drive-selection-string", drive_string);
	setprop("/fdm/jsbsim/systems/rms/auto-sequence-slot", seq_slot);
	SpaceShuttle.pdrs_auto_seq_manager.start_sequence(seq_slot);
	return;
	}

setprop("/fdm/jsbsim/systems/rms/drive-selection-mode", drive_mode);
setprop("/fdm/jsbsim/systems/rms/drive-selection-string", drive_string);

}


var predict_asc_nd_lon = func (inc) {

# interpolation of measured empirics

#print ("Numerical interpolation!");

var data = [];

var point = [28.6, 191.4];
append(data, point);

point = [29.41,207.16];
append(data, point);

point = [30.24,213.52];
append(data, point);

point = [31.87, 221.41];
append(data, point);

point = [32.5,223.57];
append(data, point);

point = [35.15,	231.03];
append(data, point);

point = [37.6,236.73];
append(data, point);

point = [38.42,238.26];
append(data, point);

point = [40.06,241.11];
append(data, point);

point = [42.52,	244.99];
append(data, point);

point = [43.44,246.22];
append(data, point);

point = [46.61, 250.38];
append(data, point);

point = [50.7,254.9];
append(data, point);

point = [56.43,260.05];
append(data, point);

point = [60.53,263.09];
append(data, point);

point = [71.17,270.43];
append(data, point);

point = [76.90,273.72];
append(data, point);


for (var i=1; i< size(data); i=i+1)
	{
	if (inc < data[i][0])
		{
		return data[i-1][1] + (inc - data[i-1][0])/(data[i][0] - data[i-1][0]) * (data[i][1] - data[i-1][1]);
		}

	}



}


var update_entry_guidance_target = func {


if (getprop("/fdm/jsbsim/systems/entry_guidance/guidance-mode") == 1)
	{SpaceShuttle.compute_entry_guidance_target();}
}


var update_inclination = func {

# do not accept updates if guidance is running

if (getprop("/fdm/jsbsim/systems/ap/launch/autolaunch-master") == 1) {return;}

var raw = getprop("/sim/gui/dialogs/SpaceShuttle/auto_launch/inclination");
var lat = getprop("/position/latitude-deg");
var lon = getprop("/position/longitude-deg");

var inc = lat + (90 - lat) * raw;


# fix impossible inclination requests

if (lat > inc)
	{
	print ("Impossible target inclination for launch site - setting lowest possible!"); 
	inc = lat;
	}

setprop("/fdm/jsbsim/systems/ap/launch/inclination-target", inc);

#Update Abort Boundary Velocities when Inc changes before LiftOff
SpaceShuttle.abort_boundary_update();



var la_raw =  math.asin(math.cos(inc * math.pi/180.0) / math.cos (lat * math.pi/180.0));

#print ("Raw: ", la_raw * 180/math.pi);

# approx correction due to Earth's rotation
var v_orbit = 7700; # 300 km orbit
var v_earth = 465;
var v_xe = v_orbit * math.sin(la_raw) - v_earth * math.cos(lat * math.pi/180.0);
var v_ye = v_orbit * math.cos(la_raw);

#print("vx: ", v_xe, "vy: ", v_ye);

var la_north = math.atan2(v_xe,v_ye);

la_north = 180.0/math.pi * la_north;

var la_south = 180.0 - la_north;

setprop("/sim/gui/dialogs/SpaceShuttle/auto_launch/azimuth-north", la_north);
setprop("/sim/gui/dialogs/SpaceShuttle/auto_launch/azimuth-south", la_south);

var direction = getprop("/sim/gui/dialogs/SpaceShuttle/auto_launch/select-north");

if (direction == 1)
	{
	var launch_azimuth = la_north;
	setprop("/fdm/jsbsim/systems/ap/launch/inc-acquire-sign", -1);
	}
else
	{
	var launch_azimuth = la_south;
	setprop("/fdm/jsbsim/systems/ap/launch/inc-acquire-sign", 1);
	}

setprop("/fdm/jsbsim/systems/ap/launch/launch-azimuth", launch_azimuth);
launch_azimuth = launch_azimuth * math.pi/180.0;


# bias the crosstrack error by the empirical offset

xtrack_refloc.correction = 8.7966 - 0.5417 * (inc - lat) + 0.005430 * math.pow((inc-lat), 2.0);

print ("Assumed xtrack deviation: ", xtrack_refloc.correction);

# add a dogleg correction to the initial azimuth



var asc_nd_lon_bias = getprop("/fdm/jsbsim/systems/ap/launch/asc-nd-lon-bias");

var asc_nd_lon_tgt = 0;

if ((inc > 28.6) and (inc <76.9))
	{
 	asc_nd_lon_tgt = predict_asc_nd_lon(inc);
	}
else
	{
	asc_nd_lon_tgt = 191.4 + 19.868685 * math.pow((inc - lat), 0.369777) + asc_nd_lon_bias - 0.25; # empirics for KSC
	}



asc_nd_lon_tgt += lon + 80.68; # shift for launches not from KSC

var elapsed = getprop("/sim/time/elapsed-sec") - 100.0; # empirics is measured for 100 s
asc_nd_lon_tgt += elapsed/60. * 0.25;

setprop("/fdm/jsbsim/systems/ap/launch/asc-nd-lon-tgt", asc_nd_lon_tgt);

if(ascending_node_update == 0) {update_asc_nd_lon_loop(elapsed); ascending_node_update = 1;}

var dl_angle = 0.0;

#print ("Hello World");

if ((math.abs(asc_nd_lon_bias) > 0.0) and (getprop("/fdm/jsbsim/systems/ap/launch/asc-node-lon-tgt-flag") == 1))
	{
	var shuttle_pos = geo.aircraft_position();
	var refloc = geo.Coord.new();
	refloc.set_latlon(shuttle_pos.lat(), shuttle_pos.lon() + asc_nd_lon_bias);

	print ("Asc. nd. lon. bias is now: ", asc_nd_lon_bias);
	print ("Launch azimuth is now: ", launch_azimuth);

	var actual_course = refloc.course_to(shuttle_pos);
	var dist = refloc.distance_to(shuttle_pos);

	var xtrack = SpaceShuttle.sgeo_crosstrack(actual_course, launch_azimuth * 180.0/math.pi, dist)  * 0.0005399568;

	print ("Initial cross-track distance is now: ", xtrack);

	dl_angle = -2.0 * xtrack;
	dl_angle = SpaceShuttle.clamp(dl_angle, -20.0, 20.0);
	
	print ("Initial dl_angle: ", dl_angle);
	dl_angle *= math.pi/180.0;
	}



setprop("/fdm/jsbsim/systems/ap/launch/course-vector", -math.cos(launch_azimuth + dl_angle));
setprop("/fdm/jsbsim/systems/ap/launch/course-vector[1]", -math.sin(launch_azimuth + dl_angle) );
setprop("/fdm/jsbsim/systems/ap/launch/course-vector[2]", 0.0);


var apoapsis_target = getprop("/sim/gui/dialogs/SpaceShuttle/auto_launch/apoapsis-target-miles");
apoapsis_target = apoapsis_target * 1.852;

setprop("/fdm/jsbsim/systems/ap/launch/apoapsis-target", apoapsis_target);

#print ("Apoapsis target in km is now: ", apoapsis_target);

}

# the ascending node longitude moves with Earth's rotation

var update_asc_nd_lon_loop = func (elapsed_last) {


var mm = getprop("/fdm/jsbsim/systems/dps/major-mode");

if (mm == 101)
	{

	var elapsed = getprop("/sim/time/elapsed-sec");
	var delta_t = elapsed - elapsed_last;	

	#print ("Delta is now ", delta_t);

	var asc_nd_lon_tgt = getprop("/fdm/jsbsim/systems/ap/launch/asc-nd-lon-tgt");
	setprop("/fdm/jsbsim/systems/ap/launch/asc-nd-lon-tgt", asc_nd_lon_tgt + delta_t/60.0 * 0.25);


	SpaceShuttle.countdown.check();

	settimer ( func {update_asc_nd_lon_loop(elapsed); }, 5.0);
	}	

}




var update_loose_items = func {

var state = getprop("/sim/config/shuttle/loose-items");

if (state == 1)
	{
	SpaceShuttle.scom_float.init();
	}
else
	{
	SpaceShuttle.scom_float.remove();
	}

}


setlistener("/sim/gui/dialogs/SpaceShuttle/auto_launch/apoapsis-target-miles", update_inclination);
setlistener("/sim/gui/dialogs/SpaceShuttle/auto_launch/inclination", update_inclination);
setlistener("/fdm/jsbsim/systems/ap/launch/asc-nd-lon-bias", update_inclination);
setlistener("/fdm/jsbsim/systems/ap/launch/asc-node-lon-tgt-flag", update_inclination);
setlistener("/sim/gui/dialogs/SpaceShuttle/entry_guidance/site", update_site);
setlistener("/sim/gui/dialogs/SpaceShuttle/entry_guidance/runway", update_runway);
setlistener("/sim/gui/dialogs/SpaceShuttle/entry_guidance/entry-mode", update_entry_mode);
setlistener("/sim/config/shuttle/mdu-update-speed", update_MDU_speed);
setlistener("/sim/config/shuttle/ET-config", update_ET_config);
setlistener("/sim/config/shuttle/TC-config", update_TC_config);
setlistener("/sim/gui/dialogs/SpaceShuttle/limits/limit-mode", update_description);
#setlistener("/sim/gui/dialogs/SpaceShuttle/limits/failure-scenario", update_scenario);
setlistener("/fdm/jsbsim/systems/mechanical/pb-door-auto-switch", pb_door_manager,0,0);
setlistener("/sim/config/shuttle/thermal-system-computation-speed", thermal_speed_manager,0,0);
setlistener("/sim/config/shuttle/rendering/use-earthview", update_earthview_manager,0,0);
setlistener("/sim/config/shuttle/rendering/earthview-transition-alt-ft", update_earthview_manager,0,0);
setlistener("/sim/gui/dialogs/SpaceShuttle/entry_guidance/EI-radius", update_entry_guidance_target ,0,0);
setlistener("/sim/config/shuttle/loose-items", update_loose_items, 0,0);


