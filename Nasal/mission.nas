# support for i-loaded mission parameters for the Space Shuttle
# Thorsten Renk 2016

var predefined_failures = [];
var oTgt = {};
var n_orbital_targets = 0;

var launch_site_check = {

	launch_site_lat: 0,
	launch_site_lon: 0,
	launch_site_iata: "",
	launch_site_flag: 0,

};



var countdown = {

	defined: 0,
	fine_count_timer: 10,
	auto_ignition: 0,
	msg_flag: 0,
	fine_count_flag: 0,
	ignition_time: 0,
	ignition_cmd: 0,
	delay_to_liftoff: 7.0,

	check: func {

	if (me.defined == 0) {return;}
	if (me.fine_count_flag == 1) {return;}

	var elapsed_time = getprop("/sim/time/elapsed-sec");

	if ((me.msg_flag == 0) and (elapsed_time > (me.ignition_time - 60.0)))
		{
		SpaceShuttle.callout.make("T minus 60 seconds", "real");
		SpaceShuttle.callout.make("Check APUs running!", "help");
		me.msg_flag = 1;
		}

	if (elapsed_time > (me.ignition_time - 20.0))
		{
		me.fine_count_flag = 1;
		me.fine_count();
		}
	},

	fine_count: func {

		var ignition_delta_time = me.ignition_time - getprop("/sim/time/elapsed-sec");
		var delta_time = ignition_delta_time + me.delay_to_liftoff;

		if (delta_time < me.fine_count_timer)
			{
			if (me.fine_count_timer > 0)
				{SpaceShuttle.callout.make(sprintf("%d",me.fine_count_timer), "real");}
			else if (me.fine_count_timer == 0)
				{
				SpaceShuttle.callout.make("Liftoff!", "real");
				}
				
			me.fine_count_timer -= 1;
			}
		if ((ignition_delta_time < 0.0) and (me.ignition_cmd == 0))
			{
			SpaceShuttle.callout.make("Ignition!", "real");
			SpaceShuttle.ignition();
			me.ignition_cmd = 1;
			}
		if (delta_time < 0.0)
			{
			return;
			}
		

		settimer ( func {me.fine_count();}, 0.1);
	},

	

};


var failure_pre = {new: func (node, time, probability, value) {
 	var f = { parents: [failure_pre] };
	f.node = node;
	f.time = time;
	f.probability = probability;
	f.value = value;
	f.flag = 0;
	return f;
	},

	test: func (met) {

	if (me.flag == 1) {return;}
	if (met > me.time)
		{
		me.flag = 1;
		if (rand() < me.probability)
			{
			me.execute();

			}
		}
	},

	execute: func {

	setprop(me.node, me.value);

	},
		
};


var mission_init = func {


# load the mission file

var filename = getprop("/mission/filename");

var target = props.globals.getNode("/mission");
var success = io.read_properties("Aircraft/SpaceShuttle/Mission/"~filename, target);

if (success == nil) 
	{
	print("Cannot open mission file ", filename, ", using defaults.");
	io.read_properties("Aircraft/SpaceShuttle/Mission/mission.xml", target);
	}

var stage = getprop("/sim/presets/stage");

# launch site check

if (getprop("/mission/launch-site/section-defined") and (stage == 0))
	{
	mission_launch_site_check();
	}

# launch targets

if (getprop("/mission/launch/section-defined") and (stage == 0))
	{
	var tgt_inclination = getprop("/mission/launch/target-inclination");
	var tgt_apoapsis = getprop("/mission/launch/target-apoapsis-miles");
	var lat = getprop("/position/latitude-deg");

	# set the menu items - the listener calls the computation of launch azimuth

	setprop("/sim/gui/dialogs/SpaceShuttle/auto_launch/apoapsis-target-miles", tgt_apoapsis);

	if (getprop("/mission/launch/select-north"))
		{
		setprop("/sim/gui/dialogs/SpaceShuttle/auto_launch/select-north", 1);
		setprop("/sim/gui/dialogs/SpaceShuttle/auto_launch/select-south", 0);
		}
	else
		{
		setprop("/sim/gui/dialogs/SpaceShuttle/auto_launch/select-north", 0);
		setprop("/sim/gui/dialogs/SpaceShuttle/auto_launch/select-south", 1);
		}

	var raw = (tgt_inclination - lat)/(90.0 - lat);

	setprop("/sim/gui/dialogs/SpaceShuttle/auto_launch/inclination", raw);


	# auto-launch guidance and autopilot on

	setprop("/fdm/jsbsim/systems/ap/launch/autolaunch-master", 1);

	setprop("/fdm/jsbsim/systems/ap/css-pitch-control", 0);
	setprop("/fdm/jsbsim/systems/ap/automatic-pitch-control", 1);

	setprop("/fdm/jsbsim/systems/ap/css-roll-control", 0);
	setprop("/fdm/jsbsim/systems/ap/automatic-roll-control", 1);

	# i-load TAL site

	var tal_site_index = getprop("/mission/launch/tal-site-index");
	setprop("/fdm/jsbsim/systems/entry_guidance/tal-site-iloaded", tal_site_index);

	# i-load RTLS site

	var rtls_site_index = getprop("/mission/launch/rtls-site-index");
	SpaceShuttle.update_site_by_index(rtls_site_index);

	# set roll to heads up

	var rthu_flag = getprop("/mission/launch/roll-to-heads-up");
	setprop("/fdm/jsbsim/systems/ap/launch/rthu-enable", rthu_flag);

	# set early ascent throttle times and level

	var throttle_down_time = getprop("/mission/launch/throttle-down-time-s");
	setprop("/fdm/jsbsim/systems/ap/launch/throttle-down-time-s", throttle_down_time);

	var throttle_up_time = getprop("/mission/launch/throttle-up-time-s");
	setprop("/fdm/jsbsim/systems/ap/launch/throttle-up-time-s", throttle_up_time);

	var throttle_down_to = (getprop("/mission/launch/throttle-down-to-percent") - 67.0)/33.0;
	if (throttle_down_to < 0.0) {throttle_down_to = 0.0;}

	setprop("/fdm/jsbsim/systems/ap/launch/throttle-down-to-fraction", throttle_down_to);

	var throttle_nominal_percent = getprop("/mission/launch/throttle-nominal-percent");

	if (throttle_nominal_percent > 106.0) {throttle_nominal_percent = 106.0;}
	if (throttle_nominal_percent < 95.0) {throttle_nominal_percent = 95.0;}

	setprop("/fdm/jsbsim/systems/throttle/throttle-nominal", throttle_nominal_percent * 0.01);


	# set OMS assist

	var oms_assist = getprop("/mission/launch/oms-assist-burn");
	setprop("/fdm/jsbsim/systems/ap/launch/oms-assist-burn", oms_assist);

	var oms_assist_duration_s = getprop("/mission/launch/oms-assist-duration-s");
	setprop("/fdm/jsbsim/systems/ap/launch/oms-assist-duration-s", oms_assist_duration_s);

	# set trajectory loft

	var srb_climbout_bias = getprop("/mission/launch/srb-climbout-ang-bias-deg");
	var mps_climbout_bias = getprop("/mission/launch/ballistic-climb-ang-bias-deg");

	setprop("/fdm/jsbsim/systems/ap/launch/srb-climbout-bias-deg", srb_climbout_bias);
	setprop("/fdm/jsbsim/systems/ap/launch/mps-climbout-bias-deg", mps_climbout_bias);

	var trajectory_loft = getprop("/mission/launch/trajectory-loft-ft");
	setprop("/fdm/jsbsim/systems/ap/launch/trajectory-loft-ft", trajectory_loft);

	# set inclination targeting

	var inc_targeting = getprop("/mission/launch/inclination-targeting");
	setprop("/fdm/jsbsim/systems/ap/launch/inc-targeting-flag", inc_targeting);

	# set flight path angle MECO target

	var gamma_meco = getprop("/mission/launch/gamma-meco");
	setprop("/fdm/jsbsim/systems/ap/launch/gamma-meco", gamma_meco);

	}

# countdown

if (getprop("/mission/countdown/section-defined") and (stage == 0))
	{
	countdown.defined = 1;
	countdown.ignition_time = getprop("/mission/countdown/ignition-time-s");
	
	if (getprop("/mission/countdown/automatic-ignition"))
		{
		countdown.auto_ignition = 1;
		}
	else
		{
		countdown.auto_ignition = 0;
		}
	}

# trajectory display init

if (getprop("/mission/ascent-traj-stage1/section-defined") and (stage == 0))
	{
	SpaceShuttle.traj_display_flag = 0;
	}

# aborts

if (getprop("/mission/abort/section-defined") and (stage == 0))
	{
	var yaw_steering = getprop("/mission/abort/enable-yaw-steering");
	setprop("/fdm/jsbsim/systems/abort/enable-yaw-steer", yaw_steering);

	var yaw_steer_tgt = getprop("/mission/abort/yaw-steering-target");
	setprop("/fdm/jsbsim/systems/abort/yaw-steer-target", yaw_steer_tgt);

	var ato_vcont = getprop("/mission/abort/ato-v-mssn-cntn");
	setprop("/fdm/jsbsim/systems/abort/ato-v-mssn-cntn", ato_vcont);

	var ato_vlin = getprop("/mission/abort/ato-v-lin");
	setprop("/fdm/jsbsim/systems/abort/ato-v-lin", ato_vlin);

	var ato_vzero = getprop("/mission/abort/ato-v-zero");
	setprop("/fdm/jsbsim/systems/abort/ato-v-zero", ato_vzero);
	}

# configuration

if (getprop("/mission/configuration/section-defined"))
	{
	var et_config = getprop("/mission/configuration/external-tank");
	setprop("/sim/config/shuttle/ET-config", et_config);

	if (getprop("/mission/configuration/payload-explicit"))
		{
		var payload = getprop("/mission/configuration/payload");
		setprop("/sim/config/shuttle/PL-selection", payload);
		SpaceShuttle.update_payload_selection();
		}
	else
		{
		var payload_weight = getprop("/mission/configuration/payload-weight-lbs");
		setprop("/fdm/jsbsim/inertia/pointmass-weight-lbs[5]", payload_weight);
		}

	

	var oms_kit = getprop("/mission/configuration/oms-kit");

	setprop("/sim/config/shuttle/OMS-kit-config", oms_kit);
	SpaceShuttle.update_oms_kit_selection();
	

	}

# DAP

if (getprop("/mission/dap/section-defined"))
	{
	var par = getprop("/mission/dap/dap-A-PRI-rot-rate");
	setprop("/fdm/jsbsim/systems/ap/spec20/dap-A-PRI-rot-rate", par);
	
	par = getprop("/mission/dap/dap-B-PRI-rot-rate");
	setprop("/fdm/jsbsim/systems/ap/spec20/dap-B-PRI-rot-rate", par);

	par = getprop("/mission/dap/dap-A-VRN-rot-rate");
	setprop("/fdm/jsbsim/systems/ap/spec20/dap-A-VRN-rot-rate", par);

	par = getprop("/mission/dap/dap-B-VRN-rot-rate");
	setprop("/fdm/jsbsim/systems/ap/spec20/dap-B-VRN-rot-rate", par);

	par = getprop("/mission/dap/dap-A-PRI-att-db");
	setprop("/fdm/jsbsim/systems/ap/spec20/dap-A-PRI-att-db", par);

	par = getprop("/mission/dap/dap-B-PRI-att-db");
	setprop("/fdm/jsbsim/systems/ap/spec20/dap-B-PRI-att-db", par);

	par = getprop("/mission/dap/dap-A-VRN-att-db");
	setprop("/fdm/jsbsim/systems/ap/spec20/dap-A-VRN-att-db", par);

	par = getprop("/mission/dap/dap-B-VRN-att-db");
	setprop("/fdm/jsbsim/systems/ap/spec20/dap-B-VRN-att-db", par);

	par = getprop("/mission/dap/dap-A-PRI-rate-db");
	setprop("/fdm/jsbsim/systems/ap/spec20/dap-A-PRI-rate-db", par);

	par = getprop("/mission/dap/dap-B-PRI-rate-db");
	setprop("/fdm/jsbsim/systems/ap/spec20/dap-B-PRI-rate-db", par);

	par = getprop("/mission/dap/dap-A-VRN-rate-db");
	setprop("/fdm/jsbsim/systems/ap/spec20/dap-A-VRN-rate-db", par);

	par = getprop("/mission/dap/dap-B-VRN-rate-db");
	setprop("/fdm/jsbsim/systems/ap/spec20/dap-B-VRN-rate-db", par);

	par = getprop("/mission/dap/dap-A-ALT-rate-db");
	setprop("/fdm/jsbsim/systems/ap/spec20/dap-A-ALT-rate-db", par);

	par = getprop("/mission/dap/dap-B-ALT-rate-db");
	setprop("/fdm/jsbsim/systems/ap/spec20/dap-B-ALT-rate-db", par);

	par = getprop("/mission/dap/dap-A-PRI-rot-pls");
	setprop("/fdm/jsbsim/systems/ap/spec20/dap-A-PRI-rot-pls", par);

	par = getprop("/mission/dap/dap-B-PRI-rot-pls");
	setprop("/fdm/jsbsim/systems/ap/spec20/dap-B-PRI-rot-pls", par);

	par = getprop("/mission/dap/dap-A-VRN-rot-pls");
	setprop("/fdm/jsbsim/systems/ap/spec20/dap-A-VRN-rot-pls", par);

	par = getprop("/mission/dap/dap-B-VRN-rot-pls");
	setprop("/fdm/jsbsim/systems/ap/spec20/dap-B-VRN-rot-pls", par);

	par = getprop("/mission/dap/dap-A-PRI-comp");
	setprop("/fdm/jsbsim/systems/ap/spec20/dap-A-PRI-comp", par);

	par = getprop("/mission/dap/dap-B-PRI-comp");
	setprop("/fdm/jsbsim/systems/ap/spec20/dap-B-PRI-comp", par);

	par = getprop("/mission/dap/dap-A-VRN-comp");
	setprop("/fdm/jsbsim/systems/ap/spec20/dap-A-VRN-comp", par);

	par = getprop("/mission/dap/dap-B-VRN-comp");
	setprop("/fdm/jsbsim/systems/ap/spec20/dap-B-VRN-comp", par);

	par = getprop("/mission/dap/dap-A-PRI-p-opt");
	setprop("/fdm/jsbsim/systems/ap/spec20/dap-A-PRI-p-opt", par);

	par = getprop("/mission/dap/dap-B-PRI-p-opt");
	setprop("/fdm/jsbsim/systems/ap/spec20/dap-B-PRI-p-opt", par);

	par = getprop("/mission/dap/dap-A-PRI-y-opt");
	setprop("/fdm/jsbsim/systems/ap/spec20/dap-A-PRI-y-opt", par);

	par = getprop("/mission/dap/dap-B-PRI-y-opt");
	setprop("/fdm/jsbsim/systems/ap/spec20/dap-B-PRI-y-opt", par);

	par = getprop("/mission/dap/dap-A-PRI-tran-pls");
	setprop("/fdm/jsbsim/systems/ap/spec20/dap-A-PRI-tran-pls", par);

	par = getprop("/mission/dap/dap-B-PRI-tran-pls");
	setprop("/fdm/jsbsim/systems/ap/spec20/dap-B-PRI-tran-pls", par);

	par = getprop("/mission/dap/dap-A-ALT-n-jets");
	setprop("/fdm/jsbsim/systems/ap/spec20/dap-A-ALT-n-jets", par);

	par = getprop("/mission/dap/dap-B-ALT-n-jets");
	setprop("/fdm/jsbsim/systems/ap/spec20/dap-B-ALT-n-jets", par);

	}

# predefined failures

if (getprop("/mission/failures/section-defined"))
	{

	var modes = props.globals.getNode("/mission/failures", 1).getChildren("mode");

	foreach (m; modes)
		{
		var nstring = m.getValue("node");
		var time = m.getValue("occurs-met-s");
		var probability = m.getValue("probability");
		var value = m.getValue("value");

		#print ("Failure: ", nstring);
		#print ("Time: ", time, " probability: ", probability, " value: ", value);


		var fpre = failure_pre.new(nstring, time, probability, value);
		append(predefined_failures, fpre);

		}

	}

# orbiting objects

if (getprop("/mission/orbital-targets/section-defined"))
	{

	var tgt_label = getprop("/mission/orbital-targets/object-label");
	var tgt_alt = getprop("/mission/orbital-targets/alt-km") * 1000.0;
	var tgt_inc = getprop("/mission/orbital-targets/inclination-deg");
	var tgt_node_lon = getprop("/mission/orbital-targets/node-lon-deg");
	var tgt_anomaly = getprop("/mission/orbital-targets/anomaly-deg");

	oTgt = orbital_target.orbitalTarget.new(tgt_alt, tgt_inc, tgt_node_lon, tgt_anomaly);
	oTgt.label = tgt_label;	
	oTgt.start();
	print("Adding ", tgt_label);

	SpaceShuttle.tgt_history_init();
	n_orbital_targets = 1;
	setprop("/fdm/jsbsim/systems/navigation/orbital-tgt/tgt-id", 1);

	}

# PDRS auto sequences

if (getprop("/mission/rms-auto-sequences/section-defined"))
	{
	var num_sequences = getprop("/mission/rms-auto-sequences/num-sequences");

	#print ("Reading in ", num_sequences, " RMS auto sequence(s)...");

	for (var i=0; i<num_sequences; i=i+1)
		{
		var num_points = getprop("/mission/rms-auto-sequences/sequence["~i~"]/num-points");

		#print ("Sequence ", i, " with ", num_points, " points.");

		var a = [];

		for (var j=0; j< num_points; j=j+1)
			{
			#print ("Processing point ", j, "...");

			var path = "/mission/rms-auto-sequences/sequence["~i~"]/point["~j~"]/";

			var x = getprop(path~"x");
			var y = getprop(path~"y");
			var z = getprop(path~"z");
			var pitch = getprop(path~"pitch");
			var yaw = getprop(path~"yaw");
			var roll = getprop(path~"roll");
			var delay = getprop(path~"delay");

			#print ("x: ", x, " y:", y, " z: ", z);
	
			var p = SpaceShuttle.pdrs_auto_seq_point.new(x,y,z,pitch,yaw,roll,delay);
			append(a, p);

			}

		SpaceShuttle.pdrs_auto_seq_manager.append_sequence_array(a);

		}
	

	}

# Notepad entries

if (getprop("/mission/notepad/section-defined"))
	{

	if (getprop("/mission/notepad/line1") != nil)
		{
		SpaceShuttle.cdlg_notepad.write_to_line(0, getprop("/mission/notepad/line1"));
		}
	if (getprop("/mission/notepad/line2") != nil)
		{
		SpaceShuttle.cdlg_notepad.write_to_line(1, getprop("/mission/notepad/line2"));
		}
	if (getprop("/mission/notepad/line3") != nil)
		{
		SpaceShuttle.cdlg_notepad.write_to_line(2, getprop("/mission/notepad/line3"));
		}	
	if (getprop("/mission/notepad/line4") != nil)
		{
		SpaceShuttle.cdlg_notepad.write_to_line(3, getprop("/mission/notepad/line4"));
		}
	if (getprop("/mission/notepad/line5") != nil)
		{
		SpaceShuttle.cdlg_notepad.write_to_line(4, getprop("/mission/notepad/line5"));
		}
	if (getprop("/mission/notepad/line6") != nil)
		{
		SpaceShuttle.cdlg_notepad.write_to_line(5, getprop("/mission/notepad/line6"));
		}
	if (getprop("/mission/notepad/line7") != nil)
		{
		SpaceShuttle.cdlg_notepad.write_to_line(6, getprop("/mission/notepad/line7"));
		}
	if (getprop("/mission/notepad/line8") != nil)
		{
		SpaceShuttle.cdlg_notepad.write_to_line(7, getprop("/mission/notepad/line8"));
		}

	}


}


var mission_automatic_mps_dump = func {

	setprop("/fdm/jsbsim/systems/mps/LO2-manifold-valve-status", 1);
	setprop("/fdm/jsbsim/systems/propellant/LH2-inboard-status", 1);
	setprop("/fdm/jsbsim/systems/propellant/LH2-outboard-status", 1);
		
	settimer( func {SpaceShuttle.fuel_dump_start();}, 20.0);

	settimer( func {setprop("/fdm/jsbsim/systems/mps/LO2-manifold-valve-status", 0);}, 130.0);

}


var mission_post_meco = func {

if (getprop("/mission/post-meco/section-defined"))
	{
	if (getprop("/mission/post-meco/automatic-fuel-dump"))
		{
		mission_automatic_mps_dump ();
		}

	




	}

	# i-load landing site, we have to do it post-MECO to not interfere with RTLS

if (getprop("/mission/entry/section-defined"))
	{ 
	var landing_site_index = getprop("/mission/entry/landing-site-index");
	SpaceShuttle.update_site_by_index(landing_site_index);
	}

}



var mission_auto_OMS1 = func {

if (getprop("/mission/post-meco/section-defined"))
	{

if (getprop("/mission/post-meco/auto-oms1-burn"))
		{

		#var orbiter_weight = getprop("/mission/post-meco/orbiter-weight");
		#setprop("/fdm/jsbsim/systems/ap/oms-plan/weight", orbiter_weight);

		if (getprop("/mission/launch/section-defined") and getprop("/mission/launch/roll-to-heads-up"))
			{
			setprop("/fdm/jsbsim/systems/ap/oms-plan/tv-roll", 0);
			}

		var tig_s = getprop("/mission/post-meco/oms1-tig-s");
		setprop("/fdm/jsbsim/systems/timer/count-to-seconds", tig_s); 

		var tig_m = int (tig_s/60.0);
		tig_s = tig_s - tig_m * 60.0;

		setprop("/fdm/jsbsim/systems/ap/oms-plan/tig-minutes", tig_m);
		setprop("/fdm/jsbsim/systems/ap/oms-plan/tig-seconds", tig_s);
		SpaceShuttle.set_oms_mnvr_timer();


		SpaceShuttle.update_start_count(2);
		SpaceShuttle.blank_start_at();

		#OMS trim preset (2 eng burn)

		var oms_trim_p = getprop("/mission/post-meco/oms-trim-p");
		var oms_trim_ly = getprop("/mission/post-meco/oms-trim-ly");
		var oms_trim_ry = getprop("/mission/post-meco/oms-trim-ry");

		setprop("/fdm/jsbsim/systems/ap/oms-plan/trim-pitch", oms_trim_p);
		setprop("/fdm/jsbsim/systems/ap/oms-plan/trim-yaw-left", oms_trim_ly);
		setprop("/fdm/jsbsim/systems/ap/oms-plan/trim-yaw-right", oms_trim_ry);


		if (getprop("/mission/post-meco/auto-oms1-burn-peg4"))
			{
			var thetaT = getprop("/mission/post-meco/oms1-theta-T");
			var H =  getprop("/mission/post-meco/oms1-H");

			#Peg4 hash global variables from_oms burn_logic.nas
			SpaceShuttle.oms_burn_target.ht = H;
			SpaceShuttle.oms_burn_target.thetaT = thetaT;

			setprop("/fdm/jsbsim/systems/ap/oms-plan/peg4-entered", 1);

				settimer( func {
				SpaceShuttle.create_oms_burn_vector_peg4();

				},  0.2);
			}
		else
			{

			var dvx = getprop("/mission/post-meco/oms1-dvx");
			var dvy = getprop("/mission/post-meco/oms1-dvy");
			var dvz = getprop("/mission/post-meco/oms1-dvz");

			setprop("/fdm/jsbsim/systems/ap/oms-plan/dvx", dvx);
			setprop("/fdm/jsbsim/systems/ap/oms-plan/dvy", dvy);
			setprop("/fdm/jsbsim/systems/ap/oms-plan/dvz", dvz);

			#Peg7 hash global variables from oms burn_logic.nas for mnvr dps display
			SpaceShuttle.oms_burn_target.dvx_plan = dvx;
			SpaceShuttle.oms_burn_target.dvy_plan = dvy;
			SpaceShuttle.oms_burn_target.dvz_plan = dvz;

			
				# burn plan needs to be computed a frame later to pick up the properties
				settimer( func {
				SpaceShuttle.create_oms_burn_vector();
					setprop("/fdm/jsbsim/systems/ap/oms-mnvr-flag", 0);
					setprop("/fdm/jsbsim/systems/ap/oms-plan/burn-plan-available", 1);
					setprop("/fdm/jsbsim/systems/ap/oms-plan/state-extrapolated-flag", 0);
					SpaceShuttle.tracking_loop_flag = 0; }, 0.2);
			}			
		
		}

	}


}

var mission_auto_OMS2 = func {

if (getprop("/mission/post-meco/section-defined"))
	{

if (getprop("/mission/post-meco/auto-oms2-burn"))
		{
		
		
		#var orbiter_weight = getprop("/mission/post-meco/orbiter-weight");
		#setprop("/fdm/jsbsim/systems/ap/oms-plan/weight", orbiter_weight);

		#OMS 2 burn normal tv roll ( time to roll 180° after OMS1)
		setprop("/fdm/jsbsim/systems/ap/oms-plan/tv-roll", 180);

		var tig_s = getprop("/mission/post-meco/oms2-tig-s");
		setprop("/fdm/jsbsim/systems/timer/count-to-seconds", tig_s); 

		var tig_m = int (tig_s/60.0);
		tig_s = tig_s - tig_m * 60.0;

		setprop("/fdm/jsbsim/systems/ap/oms-plan/tig-minutes", tig_m);
		setprop("/fdm/jsbsim/systems/ap/oms-plan/tig-seconds", tig_s);
		SpaceShuttle.set_oms_mnvr_timer();


		SpaceShuttle.update_start_count(2);
		SpaceShuttle.blank_start_at();

		#OMS trim preset (2 eng burn)

		var oms_trim_p = getprop("/mission/post-meco/oms-trim-p");
		var oms_trim_ly = getprop("/mission/post-meco/oms-trim-ly");
		var oms_trim_ry = getprop("/mission/post-meco/oms-trim-ry");

		setprop("/fdm/jsbsim/systems/ap/oms-plan/trim-pitch", oms_trim_p);
		setprop("/fdm/jsbsim/systems/ap/oms-plan/trim-yaw-left", oms_trim_ly);
		setprop("/fdm/jsbsim/systems/ap/oms-plan/trim-yaw-right", oms_trim_ry);


		if (getprop("/mission/post-meco/auto-oms2-burn-peg4"))
			{
			var thetaT = getprop("/mission/post-meco/oms2-theta-T");
			var H =  getprop("/mission/post-meco/oms2-H");

			#Peg4 hash global variables from_oms burn_logic.nas
			SpaceShuttle.oms_burn_target.ht = H;
			SpaceShuttle.oms_burn_target.thetaT = thetaT;

			setprop("/fdm/jsbsim/systems/ap/oms-plan/peg4-entered", 1);


			settimer( func {
			SpaceShuttle.create_oms_burn_vector_peg4();

				},  0.2);
			}
		else
			{

			var dvx = getprop("/mission/post-meco/oms2-dvx");
			var dvy = getprop("/mission/post-meco/oms2-dvy");
			var dvz = getprop("/mission/post-meco/oms2-dvz");

			setprop("/fdm/jsbsim/systems/ap/oms-plan/dvx", dvx);
			setprop("/fdm/jsbsim/systems/ap/oms-plan/dvy", dvy);
			setprop("/fdm/jsbsim/systems/ap/oms-plan/dvz", dvz);

			#Peg7 hash global variables from_oms burn_logic.nas for mnvr dps display
			SpaceShuttle.oms_burn_target.dvx_plan = dvx;
			SpaceShuttle.oms_burn_target.dvy_plan = dvy;
			SpaceShuttle.oms_burn_target.dvz_plan = dvz;

			# burn plan needs to be computed a frame later to pick up the properties
			settimer( func {
				SpaceShuttle.create_oms_burn_vector();
				setprop("/fdm/jsbsim/systems/ap/oms-mnvr-flag", 0);
				setprop("/fdm/jsbsim/systems/ap/oms-plan/burn-plan-available", 1);
				setprop("/fdm/jsbsim/systems/ap/oms-plan/state-extrapolated-flag", 0);
				SpaceShuttle.tracking_loop_flag = 0; }, 0.2);
			}			
		
		}

	}


}



var mission_post_meco_TAL = func {

if (getprop("/mission/post-meco/section-defined"))
	{
	if (getprop("/mission/post-meco/automatic-fuel-dump"))
		{
		mission_automatic_mps_dump ();
		}
	}

}


var mission_predefined_failures = func {

var elapsed = getprop("/sim/time/elapsed-sec");
var MET = elapsed + getprop("/fdm/jsbsim/systems/timer/delta-MET");

#print ("MET: ", MET);

foreach (var fail;  predefined_failures)
	{
	fail.test(MET);
	}


}

var mission_launch_site_check = func {

var launch_site_string = getprop("/mission/launch-site/launch-site-iata");

#Check of the mission file Launch site (Automatic coordinates for KSC or VBG // user defined lat and lon otherwise)

if (launch_site_string == "KSC")
	{
	launch_site_check.launch_site_lat = 28.627;
	launch_site_check.launch_site_lon = -80.6210;
	launch_site_check.launch_site_iata = "KSC";
	}

else if (launch_site_string == "VBG")
	{
	launch_site_check.launch_site_lat = 34.581;
	launch_site_check.launch_site_lon = -120.627;
	launch_site_check.launch_site_iata = "VBG";
	}

else
	{
	launch_site_check.launch_site_lat = getprop("/mission/launch-site/launch-site-lat");
	launch_site_check.launch_site_lon = getprop("/mission/launch-site/launch-site-lon");
	}


#Current Location when fdm is initialized
var pos = geo.Coord.new();
pos.set_latlon(getprop("/position/latitude-deg"),getprop("/position/longitude-deg"));

#Expected Launch Site 
var launch_site_pos = geo.Coord.new();
launch_site_pos.set_latlon(launch_site_check.launch_site_lat,launch_site_check.launch_site_lon);

#Distance between Current end Expected pos
var delta_distance = pos.distance_to(launch_site_pos);
#print ("Delta distance: ", delta_distance);

#Wrong site flag (distance > 20Nm)
if (delta_distance > 37000) {launch_site_check.launch_site_flag = 1;}
	
#Delayed the message by 15 seconds to be sure to have everything initialized
settimer( func { launch_site_warning(); }, 15.0);

}


var launch_site_warning = func {

#Wrong Location
if (launch_site_check.launch_site_flag == 1)
	{
	if (launch_site_check.launch_site_iata != "") {SpaceShuttle.callout.make("Wrong Launch Site, Expected Launch site is "~(launch_site_check.launch_site_iata), "help");}
	else {SpaceShuttle.callout.make("Wrong Launch Site, Expected Launch site Latitude is "~sprintf("%5.2f",launch_site_check.launch_site_lat)~" and Longitude is "~sprintf("%5.2f",launch_site_check.launch_site_lon), "help");}
	}

#Correct Location
else {SpaceShuttle.callout.make("Correct Launch Site, Let's Proceed with Pre Launch Actions", "help");}

}



setlistener("/sim/signals/fdm-initialized", func { mission_init(); },0,0);
