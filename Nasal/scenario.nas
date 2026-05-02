# support for training scenarios for the Space Shuttle
# Thorsten Renk 2019

var scenario_init = func {


# load the scenario file

var filename = getprop("/scenario/filename");

var target = props.globals.getNode("/scenario");
var success = io.read_properties("Aircraft/SpaceShuttle/Scenario/"~filename, target);

if (success == nil) # try absolute path
	{

	success = io.read_properties(filename, target);

	if (success == nil) # give up
		{
		print("Cannot open scenario file ", filename, ", aborting.");
		return;
		}
	}

# check metadata

if (getprop("/scenario/metadata/mission-stage") != getprop("/sim/presets/stage"))
	{
	print ("Scenario incompatibe with mission stage.");
	return;
	}


# co-orbiting objects 

if (getprop("/scenario/proximity-object/name") != nil)
	{
	var name = getprop("/scenario/proximity-object/name");
	var prox_x = getprop("/scenario/proximity-object/prox-x");
	var prox_y = getprop("/scenario/proximity-object/prox-y");
	var prox_z = getprop("/scenario/proximity-object/prox-z");

	if (prox_x == nil) {prox_x = (rand() - 0.5) * 1000.0;}
	if (prox_y == nil) {prox_y = (rand() - 0.5) * 1000.0;}
	if (prox_z == nil) {prox_z = (rand() - 0.5) * 1000.0;}
	

	if (name == "Spartan-201")
		{
		SpaceShuttle.spartan_manager.init(prox_x, prox_y, prox_z, 0,0,0);
		}
	else if (name == "ISS")
		{
		SpaceShuttle.iss_manager.init(prox_x, prox_y, prox_z, 0,0,0);
		}
	#else if (name == "HST")
	#	{
	#	SpaceShuttle.hst_manager.init(prox_x, prox_y, prox_z, 0,0,0);
	#	}

	}

# orbital target

if (getprop("/scenario/orbital-target/object-label") != nil)
	{
	if (SpaceShuttle.n_orbital_targets == 1)
		{
		SpaceShuttle.n_orbital_targets = 0;
		print("Removing ", oTgt.label);
		oTgt.stop();
		}
		

		var tgt_label = getprop("/scenario/orbital-target/object-label");
		var tgt_alt = getprop("/scenario/orbital-target/alt-km") * 1000.0;
		var tgt_inc = getprop("/scenario/orbital-target/inclination-deg");
		var tgt_node_lon = getprop("/scenario/orbital-target/node-lon-deg");
		var tgt_anomaly = getprop("/scenario/orbital-target/anomaly-deg");
		var elapsed_time = getprop("/sim/time/elapsed-sec");

		tgt_node_lon += elapsed_time * 0.00418333333333327;

		oTgt = orbital_target.orbitalTarget.new(tgt_alt, tgt_inc, tgt_node_lon, tgt_anomaly);
		oTgt.label = tgt_label;	
		SpaceShuttle.oTgt.delta_time = elapsed_time;
		oTgt.start();
		print("Adding ", tgt_label);

		SpaceShuttle.n_orbital_targets = 1;

	}


# state



if (getprop("/scenario/state/lat") != nil)
	{

	setprop("/position/latitude-deg", getprop("/scenario/state/lat"));
	setprop("/position/longitude-deg", getprop("/scenario/state/lon"));
	setprop("/position/altitude-ft", getprop("/scenario/state/alt"));

	setprop("/orientation/heading-deg", getprop("/scenario/state/heading"));
	setprop("/orientation/pitch-deg", getprop("/scenario/state/pitch"));
	setprop("/orientation/roll-deg", getprop("/scenario/state/roll"));

	setprop("/velocities/uBody-fps", getprop("/scenario/state/u-body"));
	setprop("/velocities/vBody-fps", getprop("/scenario/state/v-body"));
	setprop("/velocities/wBody-fps", getprop("/scenario/state/w-body"));


	SpaceShuttle.history_reset();
	}

# guidance
	
if (getprop("/scenario/guidance/landing-site-index") != nil)
	{
	SpaceShuttle.update_site_by_index(getprop("/scenario/guidance/landing-site-index"));
	}

if (getprop("/scenario/guidance/entry-guidance-on") == 1)
	{
	SpaceShuttle.compute_entry_guidance_target();
	}




if (getprop("/scenario/guidance/peg7-dvx") != nil)
	{
	var value = getprop("/scenario/guidance/peg7-dvx");
	setprop("/fdm/jsbsim/systems/ap/oms-plan/dvx",num(value)); 
	SpaceShuttle.oms_burn_target.dvx_plan = num(value);
	SpaceShuttle.blank_peg4(); 
	}

if (getprop("/scenario/guidance/peg7-dvy") != nil)
	{
	var value = getprop("/scenario/guidance/peg7-dvy");
	setprop("/fdm/jsbsim/systems/ap/oms-plan/dvy",num(value)); 
	SpaceShuttle.oms_burn_target.dvy_plan = num(value);
	SpaceShuttle.blank_peg4(); 
	}

if (getprop("/scenario/guidance/peg7-dvz") != nil)
	{
	var value = getprop("/scenario/guidance/peg7-dvz");
	setprop("/fdm/jsbsim/systems/ap/oms-plan/dvz",num(value)); 
	SpaceShuttle.oms_burn_target.dvz_plan = num(value);
	SpaceShuttle.blank_peg4(); 
	}

if (getprop("/scenario/guidance/tig-days") != nil)
	{
	var value = getprop("/scenario/guidance/tig-days");
	setprop("/fdm/jsbsim/systems/ap/oms-plan/tig-days", int(value)); 
	SpaceShuttle.set_oms_mnvr_timer();
	}

if (getprop("/scenario/guidance/tig-hours") != nil)
	{
	var value = getprop("/scenario/guidance/tig-hours");
	setprop("/fdm/jsbsim/systems/ap/oms-plan/tig-hours", int(value)); 
	SpaceShuttle.set_oms_mnvr_timer();
	}

if (getprop("/scenario/guidance/tig-minutes") != nil)
	{
	var value = getprop("/scenario/guidance/tig-minutes");
	setprop("/fdm/jsbsim/systems/ap/oms-plan/tig-minutes", int(value)); 
	SpaceShuttle.set_oms_mnvr_timer();
	}

if (getprop("/scenario/guidance/tig-seconds") != nil)
	{
	var value = getprop("/scenario/guidance/tig-seconds");
	setprop("/fdm/jsbsim/systems/ap/oms-plan/tig-seconds", int(value)); 
	SpaceShuttle.set_oms_mnvr_timer();
	}


# predefined failures

if (getprop("/scenario/failures/mode/node") != nil)
	{

	var modes = props.globals.getNode("/scenario/failures", 1).getChildren("mode");

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


# settings

var nd_settings = props.globals.getNode("/scenario/settings");

if (nd_settings != nil)
	{
	var nd_property = nd_settings.getChildren("property");
	var nd_value = nd_settings.getChildren("value");

	var i=0;

	foreach(n; nd_property)
		{
		setprop(n.getValue(), nd_value[i].getValue());


		i=i+1;
		}

	}


# notepad entries

if (getprop("/scenario/notepad/line1") != nil)
	{
	SpaceShuttle.cdlg_notepad.write_to_line(0, getprop("/scenario/notepad/line1"));
	}
if (getprop("/scenario/notepad/line2") != nil)
	{
	SpaceShuttle.cdlg_notepad.write_to_line(1, getprop("/scenario/notepad/line2"));
	}
if (getprop("/scenario/notepad/line3") != nil)
	{
	SpaceShuttle.cdlg_notepad.write_to_line(2, getprop("/scenario/notepad/line3"));
	}	
if (getprop("/scenario/notepad/line4") != nil)
	{
	SpaceShuttle.cdlg_notepad.write_to_line(3, getprop("/scenario/notepad/line4"));
	}
if (getprop("/scenario/notepad/line5") != nil)
	{
	SpaceShuttle.cdlg_notepad.write_to_line(4, getprop("/scenario/notepad/line5"));
	}
if (getprop("/scenario/notepad/line6") != nil)
	{
	SpaceShuttle.cdlg_notepad.write_to_line(5, getprop("/scenario/notepad/line6"));
	}
if (getprop("/scenario/notepad/line7") != nil)
	{
	SpaceShuttle.cdlg_notepad.write_to_line(6, getprop("/scenario/notepad/line7"));
	}
if (getprop("/scenario/notepad/line8") != nil)
	{
	SpaceShuttle.cdlg_notepad.write_to_line(7, getprop("/scenario/notepad/line8"));
	}


}




