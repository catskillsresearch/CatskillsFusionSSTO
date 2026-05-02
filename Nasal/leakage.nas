# tank leakage simulation for the Space Shuttle
# Thorsten Renk 2018

var leakage_point = {
	new: func (tank, designation, system) {
 	var l = { parents: [leakage_point] };
	
	l.flow = 0.0;
	l.current_flow = 0.0;
	l.tank = tank;
	l.designation = designation;
	l.valve_property = [];
	l.valve_array = [];
	l.num_valves = 0;
	l.verbose = 0;
	l.system = system;
	return l;
	},

	
	add_leak: func (flow) {

	me.flow = flow;
	me.check_status();

	},

	add_valve: func (valve_property, listener_property) {

	me.num_valves = me.num_valves + 1;
	append(me.valve_property,valve_property);
	append(me.valve_array, getprop(valve_property));
	setlistener(listener_property, func 
		{
		settimer ( func { # needs to be delayed to give JSBSim a chance to update		
		me.check_status();
	
		}, 0.1);

		});

	},

	check_status: func {

	if (me.verbose == 1) {print ("Leakage status check");}

	var flag = 1;

	for (var i=0; i< me.num_valves;i=i+1)
		{
		if (me.verbose == 1)
			{print (me.valve_property[i], " ", getprop(me.valve_property[i]));}
		if (getprop(me.valve_property[i]) == 0)
			{flag = 0; break;}
		}
	me.current_flow = flag * me.flow;
		if (me.verbose == 1)
			{
			print ("Potential leakage: ", me.flow);
			print ("Current leakage: ", me.current_flow);
			}

	settimer ( func { # needs to be delayed to do all valve checks before manager loops

		if (me.system == "propellant")
			{SpaceShuttle.leakage_manager.update();}
		else if (me.system == "mps-helium")
			{SpaceShuttle.helium_leakage_manager.update();}
		}, 0.1);
	},

};

var leakage_manager = {

	leakage_points: [],
	oms_left_oxidizer_flow: 0.0,
	oms_left_fuel_flow: 0.0,
	oms_right_oxidizer_flow: 0.0,
	oms_right_fuel_flow: 0.0,
	rcs_left_fuel_flow: 0.0,
	rcs_left_oxidizer_flow: 0.0,
	rcs_right_fuel_flow: 0.0,
	rcs_right_oxidizer_flow: 0.0,
	rcs_fwd_fuel_flow: 0.0,
	rcs_fwd_oxidizer_flow: 0.0,

	gate: 1,

	verbose: 0,

	init: func {

	var path_o = "/fdm/jsbsim/systems/oms-hardware/";
	var path_r = "/fdm/jsbsim/systems/rcs-hardware/";

	# OMS left fuel tank

	var l = leakage_point.new("OMS-left-fuel", "OMS-left-fuel-tank", "propellant");
	append(me.leakage_points, l);

	l = leakage_point.new("OMS-left-fuel", "OMS-left-fuel-manifold", "propellant");
	l.add_valve(path_o~"tank-left-isolation-status", path_o~"tank-left-oms-valve-A-status");
	l.add_valve(path_o~"tank-left-isolation-status", path_o~"tank-left-oms-valve-B-status");
	append(me.leakage_points, l);



	# OMS left oxidizer tank

	l = leakage_point.new("OMS-left-oxidizer", "OMS-left-oxidizer-tank", "propellant");
	append(me.leakage_points, l);

	l = leakage_point.new("OMS-left-oxidizer", "OMS-left-oxidizer-manifold", "propellant");
	l.add_valve(path_o~"tank-left-isolation-status", path_o~"tank-left-oms-valve-A-status");
	l.add_valve(path_o~"tank-left-isolation-status", path_o~"tank-left-oms-valve-B-status");
	append(me.leakage_points, l);



	# OMS right fuel tank

	l = leakage_point.new("OMS-right-fuel", "OMS-right-fuel-tank", "propellant");
	append(me.leakage_points, l);

	l = leakage_point.new("OMS-right-fuel", "OMS-right-fuel-manifold", "propellant");
	l.add_valve(path_o~"tank-right-isolation-status", path_o~"tank-right-oms-valve-A-status");
	l.add_valve(path_o~"tank-right-isolation-status", path_o~"tank-right-oms-valve-B-status");
	append(me.leakage_points, l);



	# OMS right oxidizer tank

	l = leakage_point.new("OMS-right-oxidizer", "OMS-right-oxidizer-tank", "propellant");
	append(me.leakage_points, l);

	l = leakage_point.new("OMS-right-oxidizer", "OMS-right-oxidizer-manifold", "propellant");
	l.add_valve(path_o~"tank-right-isolation-status", path_o~"tank-right-oms-valve-A-status");
	l.add_valve(path_o~"tank-right-isolation-status", path_o~"tank-right-oms-valve-B-status");
	append(me.leakage_points, l);




	# OMS crossfeed fuel manifold

	l = leakage_point.new("OMS-left-fuel-crossfeed", "OMS-crossfeed-fuel-manifold", "propellant");
	l.add_valve(path_o~"crossfeed-left-open", path_o~"crossfeed-left-oms-valve-A-status");
	l.add_valve(path_o~"crossfeed-left-open", path_o~"crossfeed-left-oms-valve-B-status");
	l.add_valve(path_o~"tank-left-isolation-status", path_o~"tank-left-oms-valve-A-status");
	l.add_valve(path_o~"tank-left-isolation-status", path_o~"tank-left-oms-valve-B-status");
	append(me.leakage_points, l);

	l = leakage_point.new("OMS-right-fuel-crossfeed", "OMS-crossfeed-fuel-manifold", "propellant");
	l.add_valve(path_o~"crossfeed-right-open", path_o~"crossfeed-right-oms-valve-A-status");
	l.add_valve(path_o~"crossfeed-right-open", path_o~"crossfeed-right-oms-valve-B-status");
	l.add_valve(path_o~"tank-right-isolation-status", path_o~"tank-right-oms-valve-A-status");
	l.add_valve(path_o~"tank-right-isolation-status", path_o~"tank-right-oms-valve-B-status");
	append(me.leakage_points, l);

	# OMS crossfeed oxidizer manifold

	l = leakage_point.new("OMS-left-oxidizer-crossfeed", "OMS-crossfeed-oxidizer-manifold", "propellant");
	l.add_valve(path_o~"crossfeed-left-open", path_o~"crossfeed-left-oms-valve-A-status");
	l.add_valve(path_o~"crossfeed-left-open", path_o~"crossfeed-left-oms-valve-B-status");
	l.add_valve(path_o~"tank-left-isolation-status", path_o~"tank-left-oms-valve-A-status");
	l.add_valve(path_o~"tank-left-isolation-status", path_o~"tank-left-oms-valve-B-status");
	append(me.leakage_points, l);

	l = leakage_point.new("OMS-right-oxidizer-crossfeed", "OMS-crossfeed-oxidizer-manifold", "propellant");
	l.add_valve(path_o~"crossfeed-right-open", path_o~"crossfeed-right-oms-valve-A-status");
	l.add_valve(path_o~"crossfeed-right-open", path_o~"crossfeed-right-oms-valve-B-status");
	l.add_valve(path_o~"tank-right-isolation-status", path_o~"tank-right-oms-valve-A-status");
	l.add_valve(path_o~"tank-right-isolation-status", path_o~"tank-right-oms-valve-B-status");
	append(me.leakage_points, l);

	# RCS left fuel tank

	l = leakage_point.new("RCS-left-fuel", "RCS-left-fuel-tank", "propellant");
	append(me.leakage_points, l);


	l = leakage_point.new("RCS-left-fuel", "RCS-left-fuel-manifold-12", "propellant");
	l.add_valve(path_r~"tank-left-rcs-valve-12-status", path_r~"tank-left-rcs-valve-12-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-left-fuel", "RCS-left-fuel-manifold-345", "propellant");
	l.add_valve(path_r~"tank-left-345-isolation-status", path_r~"tank-left-rcs-valve-345A-status");
	l.add_valve(path_r~"tank-left-345-isolation-status", path_r~"tank-left-rcs-valve-345B-status");
	append(me.leakage_points, l);


	l = leakage_point.new("RCS-left-fuel", "RCS-left-fuel-manifold-1", "propellant");
	l.add_valve(path_r~"tank-left-rcs-valve-12-status", path_r~"tank-left-rcs-valve-12-status");
	l.add_valve(path_r~"mfold-left-rcs-valve-1-status", path_r~"mfold-left-rcs-valve-1-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-left-fuel", "RCS-left-fuel-manifold-2", "propellant");
	l.add_valve(path_r~"tank-left-rcs-valve-12-status", path_r~"tank-left-rcs-valve-12-status");
	l.add_valve(path_r~"mfold-left-rcs-valve-2-status", path_r~"mfold-left-rcs-valve-2-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-left-fuel", "RCS-left-fuel-manifold-3", "propellant");
	l.add_valve(path_r~"tank-left-345-isolation-status", path_r~"tank-left-rcs-valve-345A-status");
	l.add_valve(path_r~"tank-left-345-isolation-status", path_r~"tank-left-rcs-valve-345B-status");
	l.add_valve(path_r~"mfold-left-rcs-valve-3-status", path_r~"mfold-left-rcs-valve-3-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-left-fuel", "RCS-left-fuel-manifold-4", "propellant");
	l.add_valve(path_r~"tank-left-345-isolation-status", path_r~"tank-left-rcs-valve-345A-status");
	l.add_valve(path_r~"tank-left-345-isolation-status", path_r~"tank-left-rcs-valve-345B-status");
	l.add_valve(path_r~"mfold-left-rcs-valve-4-status", path_r~"mfold-left-rcs-valve-4-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-left-fuel", "RCS-left-fuel-manifold-5", "propellant");
	l.add_valve(path_r~"tank-left-345-isolation-status", path_r~"tank-left-rcs-valve-345A-status");
	l.add_valve(path_r~"tank-left-345-isolation-status", path_r~"tank-left-rcs-valve-345B-status");
	l.add_valve(path_r~"mfold-left-rcs-valve-5-status", path_r~"mfold-left-rcs-valve-5-status");
	append(me.leakage_points, l);

	# RCS left oxidizer tank

	l = leakage_point.new("RCS-left-oxidizer", "RCS-left-oxidizer-tank", "propellant");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-left-oxidizer", "RCS-left-oxidizer-manifold-12", "propellant");
	l.add_valve(path_r~"tank-left-rcs-valve-12-status", path_r~"tank-left-rcs-valve-12-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-left-oxidizer", "RCS-left-oxidizer-manifold-345", "propellant");
	l.add_valve(path_r~"tank-left-345-isolation-status", path_r~"tank-left-rcs-valve-345A-status");
	l.add_valve(path_r~"tank-left-345-isolation-status", path_r~"tank-left-rcs-valve-345B-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-left-oxidizer", "RCS-left-oxidizer-manifold-1", "propellant");
	l.add_valve(path_r~"tank-left-rcs-valve-12-status", path_r~"tank-left-rcs-valve-12-status");
	l.add_valve(path_r~"mfold-left-rcs-valve-1-status", path_r~"mfold-left-rcs-valve-1-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-left-oxidizer", "RCS-left-oxidizer-manifold-2", "propellant");
	l.add_valve(path_r~"tank-left-rcs-valve-12-status", path_r~"tank-left-rcs-valve-12-status");
	l.add_valve(path_r~"mfold-left-rcs-valve-2-status", path_r~"mfold-left-rcs-valve-2-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-left-oxidizer", "RCS-left-oxidizer-manifold-3", "propellant");
	l.add_valve(path_r~"tank-left-345-isolation-status", path_r~"tank-left-rcs-valve-345A-status");
	l.add_valve(path_r~"tank-left-345-isolation-status", path_r~"tank-left-rcs-valve-345B-status");
	l.add_valve(path_r~"mfold-left-rcs-valve-3-status", path_r~"mfold-left-rcs-valve-3-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-left-oxidizer", "RCS-left-oxidizer-manifold-4", "propellant");
	l.add_valve(path_r~"tank-left-345-isolation-status", path_r~"tank-left-rcs-valve-345A-status");
	l.add_valve(path_r~"tank-left-345-isolation-status", path_r~"tank-left-rcs-valve-345B-status");
	l.add_valve(path_r~"mfold-left-rcs-valve-4-status", path_r~"mfold-left-rcs-valve-4-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-left-oxidizer", "RCS-left-oxidizer-manifold-5", "propellant");
	l.add_valve(path_r~"tank-left-345-isolation-status", path_r~"tank-left-rcs-valve-345A-status");
	l.add_valve(path_r~"tank-left-345-isolation-status", path_r~"tank-left-rcs-valve-345B-status");
	l.add_valve(path_r~"mfold-left-rcs-valve-5-status", path_r~"mfold-left-rcs-valve-5-status");
	append(me.leakage_points, l);

	# RCS right fuel tank

	l = leakage_point.new("RCS-right-fuel", "RCS-right-fuel-tank", "propellant");
	append(me.leakage_points, l);


	l = leakage_point.new("RCS-right-fuel", "RCS-right-fuel-manifold-12", "propellant");
	l.add_valve(path_r~"tank-right-rcs-valve-12-status", path_r~"tank-right-rcs-valve-12-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-right-fuel", "RCS-right-fuel-manifold-345", "propellant");
	l.add_valve(path_r~"tank-right-345-isolation-status", path_r~"tank-right-rcs-valve-345A-status");
	l.add_valve(path_r~"tank-right-345-isolation-status", path_r~"tank-right-rcs-valve-345B-status");
	append(me.leakage_points, l);


	l = leakage_point.new("RCS-right-fuel", "RCS-right-fuel-manifold-1", "propellant");
	l.add_valve(path_r~"tank-right-rcs-valve-12-status", path_r~"tank-right-rcs-valve-12-status");
	l.add_valve(path_r~"mfold-right-rcs-valve-1-status", path_r~"mfold-right-rcs-valve-1-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-right-fuel", "RCS-right-fuel-manifold-2", "propellant");
	l.add_valve(path_r~"tank-right-rcs-valve-12-status", path_r~"tank-right-rcs-valve-12-status");
	l.add_valve(path_r~"mfold-right-rcs-valve-2-status", path_r~"mfold-right-rcs-valve-2-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-right-fuel", "RCS-right-fuel-manifold-3", "propellant");
	l.add_valve(path_r~"tank-right-345-isolation-status", path_r~"tank-right-rcs-valve-345A-status");
	l.add_valve(path_r~"tank-right-345-isolation-status", path_r~"tank-right-rcs-valve-345B-status");
	l.add_valve(path_r~"mfold-right-rcs-valve-3-status", path_r~"mfold-right-rcs-valve-3-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-right-fuel", "RCS-right-fuel-manifold-4", "propellant");
	l.add_valve(path_r~"tank-right-345-isolation-status", path_r~"tank-right-rcs-valve-345A-status");
	l.add_valve(path_r~"tank-right-345-isolation-status", path_r~"tank-right-rcs-valve-345B-status");
	l.add_valve(path_r~"mfold-right-rcs-valve-4-status", path_r~"mfold-right-rcs-valve-4-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-right-fuel", "RCS-right-fuel-manifold-5", "propellant");
	l.add_valve(path_r~"tank-right-345-isolation-status", path_r~"tank-right-rcs-valve-345A-status");
	l.add_valve(path_r~"tank-right-345-isolation-status", path_r~"tank-right-rcs-valve-345B-status");
	l.add_valve(path_r~"mfold-right-rcs-valve-5-status", path_r~"mfold-right-rcs-valve-5-status");
	append(me.leakage_points, l);

	# RCS right oxidizer tank

	l = leakage_point.new("RCS-right-oxidizer", "RCS-right-oxidizer-tank", "propellant");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-right-oxidizer", "RCS-right-oxidizer-manifold-12", "propellant");
	l.add_valve(path_r~"tank-right-rcs-valve-12-status", path_r~"tank-right-rcs-valve-12-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-right-oxidizer", "RCS-right-oxidizer-manifold-345", "propellant");
	l.add_valve(path_r~"tank-right-345-isolation-status", path_r~"tank-right-rcs-valve-345A-status");
	l.add_valve(path_r~"tank-right-345-isolation-status", path_r~"tank-right-rcs-valve-345B-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-right-oxidizer", "RCS-right-oxidizer-manifold-1", "propellant");
	l.add_valve(path_r~"tank-right-rcs-valve-12-status", path_r~"tank-right-rcs-valve-12-status");
	l.add_valve(path_r~"mfold-right-rcs-valve-1-status", path_r~"mfold-right-rcs-valve-1-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-right-oxidizer", "RCS-right-oxidizer-manifold-2", "propellant");
	l.add_valve(path_r~"tank-right-rcs-valve-12-status", path_r~"tank-right-rcs-valve-12-status");
	l.add_valve(path_r~"mfold-right-rcs-valve-2-status", path_r~"mfold-right-rcs-valve-2-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-right-oxidizer", "RCS-right-oxidizer-manifold-3", "propellant");
	l.add_valve(path_r~"tank-right-345-isolation-status", path_r~"tank-right-rcs-valve-345A-status");
	l.add_valve(path_r~"tank-right-345-isolation-status", path_r~"tank-right-rcs-valve-345B-status");
	l.add_valve(path_r~"mfold-right-rcs-valve-3-status", path_r~"mfold-right-rcs-valve-3-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-right-oxidizer", "RCS-right-oxidizer-manifold-4", "propellant");
	l.add_valve(path_r~"tank-right-345-isolation-status", path_r~"tank-right-rcs-valve-345A-status");
	l.add_valve(path_r~"tank-right-345-isolation-status", path_r~"tank-right-rcs-valve-345B-status");
	l.add_valve(path_r~"mfold-right-rcs-valve-4-status", path_r~"mfold-right-rcs-valve-4-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-right-oxidizer", "RCS-right-oxidizer-manifold-5", "propellant");
	l.add_valve(path_r~"tank-right-345-isolation-status", path_r~"tank-right-rcs-valve-345A-status");
	l.add_valve(path_r~"tank-right-345-isolation-status", path_r~"tank-right-rcs-valve-345B-status");
	l.add_valve(path_r~"mfold-right-rcs-valve-5-status", path_r~"mfold-right-rcs-valve-5-status");
	append(me.leakage_points, l);


	# RCS forward fuel tank

	l = leakage_point.new("RCS-fwd-fuel", "RCS-fwd-fuel-tank", "propellant");
	append(me.leakage_points, l);


	l = leakage_point.new("RCS-fwd-fuel", "RCS-fwd-fuel-manifold-12", "propellant");
	l.add_valve(path_r~"tank-fwd-rcs-valve-12-status", path_r~"tank-fwd-rcs-valve-12-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-fwd-fuel", "RCS-fwd-fuel-manifold-345", "propellant");
	l.add_valve(path_r~"tank-fwd-rcs-valve-345-status", path_r~"tank-fwd-rcs-valve-345-status");
	append(me.leakage_points, l);


	l = leakage_point.new("RCS-fwd-fuel", "RCS-fwd-fuel-manifold-1", "propellant");
	l.add_valve(path_r~"tank-fwd-rcs-valve-12-status", path_r~"tank-fwd-rcs-valve-12-status");
	l.add_valve(path_r~"mfold-fwd-rcs-valve-1-status", path_r~"mfold-fwd-rcs-valve-1-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-fwd-fuel", "RCS-fwd-fuel-manifold-2", "propellant");
	l.add_valve(path_r~"tank-fwd-rcs-valve-12-status", path_r~"tank-fwd-rcs-valve-12-status");
	l.add_valve(path_r~"mfold-fwd-rcs-valve-2-status", path_r~"mfold-fwd-rcs-valve-2-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-fwd-fuel", "RCS-fwd-fuel-manifold-3", "propellant");
	l.add_valve(path_r~"tank-fwd-rcs-valve-345-status", path_r~"tank-fwd-rcs-valve-345-status");
	l.add_valve(path_r~"mfold-fwd-rcs-valve-3-status", path_r~"mfold-fwd-rcs-valve-3-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-fwd-fuel", "RCS-fwd-fuel-manifold-4", "propellant");
	l.add_valve(path_r~"tank-fwd-rcs-valve-345-status", path_r~"tank-fwd-rcs-valve-345-status");
	l.add_valve(path_r~"mfold-fwd-rcs-valve-4-status", path_r~"mfold-fwd-rcs-valve-4-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-fwd-fuel", "RCS-fwd-fuel-manifold-5", "propellant");
	l.add_valve(path_r~"tank-fwd-rcs-valve-345-status", path_r~"tank-fwd-rcs-valve-345-status");
	l.add_valve(path_r~"mfold-fwd-rcs-valve-5-status", path_r~"mfold-fwd-rcs-valve-5-status");
	append(me.leakage_points, l);

	# RCS forward oxidizer tank

	l = leakage_point.new("RCS-fwd-oxidizer", "RCS-fwd-oxidizer-tank", "propellant");
	append(me.leakage_points, l);


	l = leakage_point.new("RCS-fwd-oxidizer", "RCS-fwd-oxidizer-manifold-12", "propellant");
	l.add_valve(path_r~"tank-fwd-rcs-valve-12-status", path_r~"tank-fwd-rcs-valve-12-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-fwd-oxidizer", "RCS-fwd-oxidizer-manifold-345", "propellant");
	l.add_valve(path_r~"tank-fwd-rcs-valve-345-status", path_r~"tank-fwd-rcs-valve-345-status");
	append(me.leakage_points, l);


	l = leakage_point.new("RCS-fwd-oxidizer", "RCS-fwd-oxidizer-manifold-1", "propellant");
	l.add_valve(path_r~"tank-fwd-rcs-valve-12-status", path_r~"tank-fwd-rcs-valve-12-status");
	l.add_valve(path_r~"mfold-fwd-rcs-valve-1-status", path_r~"mfold-fwd-rcs-valve-1-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-fwd-oxidizer", "RCS-fwd-oxidizer-manifold-2", "propellant");
	l.add_valve(path_r~"tank-fwd-rcs-valve-12-status", path_r~"tank-fwd-rcs-valve-12-status");
	l.add_valve(path_r~"mfold-fwd-rcs-valve-2-status", path_r~"mfold-fwd-rcs-valve-2-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-fwd-oxidizer", "RCS-fwd-oxidizer-manifold-3", "propellant");
	l.add_valve(path_r~"tank-fwd-rcs-valve-345-status", path_r~"tank-fwd-rcs-valve-345-status");
	l.add_valve(path_r~"mfold-fwd-rcs-valve-3-status", path_r~"mfold-fwd-rcs-valve-3-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-fwd-oxidizer", "RCS-fwd-oxidizer-manifold-4", "propellant");
	l.add_valve(path_r~"tank-fwd-rcs-valve-345-status", path_r~"tank-fwd-rcs-valve-345-status");
	l.add_valve(path_r~"mfold-fwd-rcs-valve-4-status", path_r~"mfold-fwd-rcs-valve-4-status");
	append(me.leakage_points, l);

	l = leakage_point.new("RCS-fwd-oxidizer", "RCS-fwd-oxidizer-manifold-5", "propellant");
	l.add_valve(path_r~"tank-fwd-rcs-valve-345-status", path_r~"tank-fwd-rcs-valve-345-status");
	l.add_valve(path_r~"mfold-fwd-rcs-valve-5-status", path_r~"mfold-fwd-rcs-valve-5-status");
	append(me.leakage_points, l);


	},


	update: func {

	if (me.gate == 0) {return;}

	me.gate = 0;
	settimer (func {me.gate = 1;}, 0.1);

	print ("Leakage manager update");

	me.oms_right_fuel_flow = 0.0;
	me.oms_right_oxidizer_flow = 0.0;

	me.oms_left_fuel_flow = 0.0;
	me.oms_left_oxidizer_flow = 0.0;

	me.oms_right_fuel_crossfeed_flow = 0.0;
	me.oms_left_fuel_crossfeed_flow = 0.0;

	me.oms_right_oxidizer_crossfeed_flow = 0.0;
	me.oms_left_oxidizer_crossfeed_flow = 0.0;


	me.rcs_right_fuel_flow = 0.0;
	me.rcs_right_oxidizer_flow = 0.0;

	me.rcs_left_fuel_flow = 0.0;
	me.rcs_left_oxidizer_flow = 0.0;

	me.rcs_fwd_fuel_flow = 0.0;
	me.rcs_fwd_oxidizer_flow = 0.0;


	foreach(l; me.leakage_points)
		{
		if (l.tank == "OMS-right-fuel")
			{
			me.oms_right_fuel_flow += l.current_flow;
			if (me.verbose == 1)
				{print ("OMS right fuel flow is ", me.oms_right_fuel_flow);}
			}

		if (l.tank == "OMS-left-fuel")
			{
			me.oms_left_fuel_flow += l.current_flow;
			if (me.verbose == 1)
				{print ("OMS left fuel flow is ", me.oms_left_fuel_flow);}
			}

		if (l.tank == "OMS-right-oxidizer")
			{
			me.oms_right_oxidizer_flow += l.current_flow;
			if (me.verbose == 1)
				{print ("OMS right oxidizer flow is ", me.oms_right_oxidizer_flow);}
			}

		if (l.tank == "OMS-left-oxidizer")
			{
			me.oms_left_oxidizer_flow += l.current_flow;
			if (me.verbose == 1)
				{print ("OMS left oxidizer flow is ", me.oms_left_oxidizer_flow);}
			}

		if (l.tank == "OMS-right-fuel-crossfeed")
			{
			me.oms_right_fuel_crossfeed_flow += l.current_flow;
			if (me.verbose == 1)
				{print ("OMS right fuel crossfeed flow is ", me.oms_right_fuel_crossfeed_flow);}
			}

		if (l.tank == "OMS-left-fuel-crossfeed")
			{
			me.oms_left_fuel_crossfeed_flow += l.current_flow;
			if (me.verbose == 1)
				{print ("OMS left fuel crossfeed flow is ", me.oms_left_fuel_crossfeed_flow);}
			}

		if (l.tank == "OMS-right-oxidizer-crossfeed")
			{
			me.oms_right_oxidizer_crossfeed_flow += l.current_flow;
			if (me.verbose == 1)
				{print ("OMS right oxidizer crossfeed flow is ", me.oms_right_oxidizer_crossfeed_flow);}
			}

		if (l.tank == "OMS-left-oxidizer-crossfeed")
			{
			me.oms_left_oxidizer_crossfeed_flow += l.current_flow;
			if (me.verbose == 1)
				{print ("OMS left oxidizer crossfeed flow is ", me.oms_left_oxidizer_crossfeed_flow);}
			}

		if (l.tank == "RCS-left-fuel")
			{
			me.rcs_left_fuel_flow += l.current_flow;
			if (me.verbose == 1)
				{print ("RCS left fuel flow is ", me.rcs_left_fuel_flow);}
			}

		if (l.tank == "RCS-left-oxidizer")
			{
			me.rcs_left_oxidizer_flow += l.current_flow;
			if (me.verbose == 1)
				{print ("RCS left oxidizer flow is ", me.rcs_left_oxidizer_flow);}
			}

		if (l.tank == "RCS-right-fuel")
			{
			me.rcs_right_fuel_flow += l.current_flow;
			if (me.verbose == 1)
				{print ("RCS right fuel flow is ", me.rcs_right_fuel_flow);}
			}

		if (l.tank == "RCS-right-oxidizer")
			{
			me.rcs_right_oxidizer_flow += l.current_flow;
			if (me.verbose == 1)
				{print ("RCS right oxidizer flow is ", me.rcs_right_oxidizer_flow);}
			}
		if (l.tank == "RCS-fwd-fuel")
			{
			me.rcs_fwd_fuel_flow += l.current_flow;
			if (me.verbose == 1)
				{print ("RCS fwd fuel flow is ", me.rcs_fwd_fuel_flow);}
			}

		if (l.tank == "RCS-fwd-oxidizer")
			{
			me.rcs_fwd_oxidizer_flow += l.current_flow;
			if (me.verbose == 1)
				{print ("RCS fwd oxidizer flow is ", me.rcs_fwd_oxidizer_flow);}
			}
		

		}

	if ((me.oms_right_fuel_crossfeed_flow < 0.0) and (me.oms_right_fuel_crossfeed_flow < 0.0))
		{
		me.oms_right_fuel_crossfeed_flow *= 0.5;
		me.oms_left_fuel_crossfeed_flow *= 0.5;
		}

	if ((me.oms_right_oxidizer_crossfeed_flow < 0.0) and (me.oms_right_oxidizer_crossfeed_flow < 0.0))
		{
		me.oms_right_oxidizer_crossfeed_flow *= 0.5;
		me.oms_left_oxidizer_crossfeed_flow *= 0.5;
		}
	
	me.oms_left_fuel_flow += me.oms_left_fuel_crossfeed_flow;
	me.oms_right_fuel_flow += me.oms_right_fuel_crossfeed_flow;

	me.oms_left_oxidizer_flow += me.oms_left_oxidizer_crossfeed_flow;
	me.oms_right_oxidizer_flow += me.oms_right_oxidizer_crossfeed_flow;

	if (me.verbose == 1)
		{
		print ("Final fuel flow left RCS: ", me.rcs_left_fuel_flow);
		print ("Final oxidizer flow left RCS: ", me.rcs_left_oxidizer_flow);
		print ("Final fuel flow right RCS: ", me.rcs_right_fuel_flow);
		print ("Final oxidizer flow right RCS: ", me.rcs_right_oxidizer_flow);
		print ("Final fuel flow fwd RCS: ", me.rcs_fwd_fuel_flow);
		print ("Final oxidizer flow fwd RCS: ", me.rcs_fwd_oxidizer_flow);
		}

	setprop("/fdm/jsbsim/systems/failures/leakage/oms-left-fuel-leak-flow", me.oms_left_fuel_flow);
	setprop("/fdm/jsbsim/systems/failures/leakage/oms-left-oxidizer-leak-flow", me.oms_left_oxidizer_flow);

	setprop("/fdm/jsbsim/systems/failures/leakage/oms-right-fuel-leak-flow", me.oms_right_fuel_flow);
	setprop("/fdm/jsbsim/systems/failures/leakage/oms-right-oxidizer-leak-flow", me.oms_right_oxidizer_flow);

	setprop("/fdm/jsbsim/systems/failures/leakage/rcs-left-fuel-leak-flow", me.rcs_left_fuel_flow);
	setprop("/fdm/jsbsim/systems/failures/leakage/rcs-left-oxidizer-leak-flow", me.rcs_left_oxidizer_flow);

	setprop("/fdm/jsbsim/systems/failures/leakage/rcs-right-fuel-leak-flow", me.rcs_right_fuel_flow);
	setprop("/fdm/jsbsim/systems/failures/leakage/rcs-right-oxidizer-leak-flow", me.rcs_right_oxidizer_flow);

	setprop("/fdm/jsbsim/systems/failures/leakage/rcs-fwd-fuel-leak-flow", me.rcs_fwd_fuel_flow);
	setprop("/fdm/jsbsim/systems/failures/leakage/rcs-fwd-oxidizer-leak-flow", me.rcs_fwd_oxidizer_flow);
	},


	add_leak: func (designation, flow) {

	if (flow > 0.0)
		{
		print ("Leakage flow must be negative!");
		return;
		}

	foreach(l; me.leakage_points)
		{
		if (l.designation == designation)
			{
			print ("Adding leak to ", l.designation);
			l.add_leak(flow);
			}

		}


	},

};

leakage_manager.init();



var helium_leakage_manager = {

	leakage_points: [],
	he_left_flow: 0.0,
	he_right_flow: 0.0,
	he_center_flow: 0.0,
	he_pneu_flow: 0.0,
	
	left_reg_A_reduction: 0.0,
	left_reg_B_reduction: 0.0,
	right_reg_A_reduction: 0.0,
	right_reg_B_reduction: 0.0,
	center_reg_A_reduction: 0.0,
	center_reg_B_reduction: 0.0,

	gate: 1,

	verbose: 1,

	init: func {

		var path = "/fdm/jsbsim/systems/mps/";

		# left Helium reservoir

		var l = leakage_point.new("left-helium", "left-helium-tank", "mps-helium");
		append(me.leakage_points, l);

		l = leakage_point.new("left-helium", "left-helium-manifold", "mps-helium");
		l.add_valve(path~"helium/pressurized", path~"engine/helium-isolation-valve-A-status");
		l.add_valve(path~"helium/pressurized", path~"engine/helium-isolation-valve-B-status");
		append(me.leakage_points, l);

		l = leakage_point.new("left-helium", "left-helium-manifold-A", "mps-helium");
		l.add_valve(path~"engine/helium-isolation-valve-A-status", path~"engine/helium-isolation-valve-A-status");
		append(me.leakage_points, l);

		l = leakage_point.new("left-helium", "left-helium-manifold-B", "mps-helium");
		l.add_valve(path~"engine/helium-isolation-valve-B-status", path~"engine/helium-isolation-valve-B-status");
		append(me.leakage_points, l);

		l = leakage_point.new("center-helium", "center-helium-tank", "mps-helium");
		append(me.leakage_points, l);

		l = leakage_point.new("center-helium", "center-helium-manifold", "mps-helium");
		l.add_valve(path~"helium[2]/pressurized", path~"engine[2]/helium-isolation-valve-A-status");
		l.add_valve(path~"helium[2]/pressurized", path~"engine[2]/helium-isolation-valve-B-status");
		append(me.leakage_points, l);

		l = leakage_point.new("center-helium", "center-helium-manifold-A", "mps-helium");
		l.add_valve(path~"engine[2]/helium-isolation-valve-A-status", path~"engine[2]/helium-isolation-valve-A-status");
		append(me.leakage_points, l);

		l = leakage_point.new("center-helium", "center-helium-manifold-B", "mps-helium");
		l.add_valve(path~"engine[2]/helium-isolation-valve-B-status", path~"engine[2]/helium-isolation-valve-B-status");
		append(me.leakage_points, l);

		var l = leakage_point.new("right-helium", "right-helium-tank", "mps-helium");
		append(me.leakage_points, l);

		l = leakage_point.new("right-helium", "right-helium-manifold", "mps-helium");
		l.add_valve(path~"helium[1]/pressurized", path~"engine[1]/helium-isolation-valve-A-status");
		l.add_valve(path~"helium[1]/pressurized", path~"engine[1]/helium-isolation-valve-B-status");
		append(me.leakage_points, l);

		l = leakage_point.new("right-helium", "right-helium-manifold-A", "mps-helium");
		l.add_valve(path~"engine[1]/helium-isolation-valve-A-status", path~"engine[1]/helium-isolation-valve-A-status");
		append(me.leakage_points, l);

		l = leakage_point.new("right-helium", "right-helium-manifold-B", "mps-helium");
		l.add_valve(path~"engine[1]/helium-isolation-valve-B-status", path~"engine[1]/helium-isolation-valve-B-status");
		append(me.leakage_points, l);

		var l = leakage_point.new("pneu-helium", "pneu-helium-tank", "mps-helium");
		append(me.leakage_points, l);

		l = leakage_point.new("pneu-helium", "pneu-helium-manifold", "mps-helium");
		l.add_valve(path~"helium-isolation-valve-P-status", path~"helium-isolation-valve-P-status");
		append(me.leakage_points, l);

	},

	update: func {

		if (me.gate == 0) {return;}

		me.gate = 0;
		settimer (func {me.gate = 1;}, 0.1);

		print ("Helium leakage manager update");

		me.he_left_flow = 0.0;
		me.he_right_flow = 0.0;
		me.he_center_flow = 0.0;
		me.he_pneu_flow = 0.0;
		me.he_inct_flow = 0.0;

		me.left_reg_A_reduction = 0.0;
		me.left_reg_B_reduction = 0.0;
		me.right_reg_A_reduction = 0.0;
		me.right_reg_B_reduction = 0.0;
		me.center_reg_A_reduction = 0.0;
		me.center_reg_B_reduction = 0.0;

		foreach(l; me.leakage_points)
			{
			if (l.designation == "left-helium-tank")
				{
				me.he_left_flow += l.current_flow;
				if (me.verbose == 1)
					{print ("Left Helium tank flow is ", me.he_left_flow);}
				}
			if (l.designation == "left-helium-manifold")
				{
				me.left_reg_A_reduction = -2000.0 * l.current_flow;
				me.left_reg_B_reduction = -2000.0 * l.current_flow;

				if (getprop("/fdm/jsbsim/systems/mps/helium[0]/demand-status") == 1)
					{
					me.he_inct_flow += l.current_flow;
					}
				else
					{
					me.he_left_flow += l.current_flow;
					}
				if (me.verbose == 1)
					{print ("Left Helium manifold flow is ", me.he_left_flow);}
				}
			if (l.designation == "left-helium-manifold-A")
				{
				me.left_reg_A_reduction = -4000.0 * l.current_flow;

				if (getprop("/fdm/jsbsim/systems/mps/helium[0]/demand-status") == 1)
					{
					me.he_inct_flow += l.current_flow;
					}
				else
					{
					me.he_left_flow += l.current_flow;
					}
				if (me.verbose == 1)
					{print ("Left Helium manifold A flow is ", me.he_left_flow);}
				}
			if (l.designation == "left-helium-manifold-B")
				{
				me.left_reg_B_reduction = -4000.0 * l.current_flow;

				if (getprop("/fdm/jsbsim/systems/mps/helium[0]/demand-status") == 1)
					{
					me.he_inct_flow += l.current_flow;
					}
				else
					{
					me.he_left_flow += l.current_flow;
					}
				if (me.verbose == 1)
					{print ("Left Helium manifold B flow is ", me.he_left_flow);}
				}
			if (l.designation == "right-helium-tank")
				{
				me.he_right_flow += l.current_flow;
				if (me.verbose == 1)
					{print ("Right Helium tank flow is ", me.he_center_flow);}
				}
			if (l.designation == "right-helium-manifold")
				{
				me.right_reg_A_reduction = -2000.0 * l.current_flow;
				me.right_reg_B_reduction = -2000.0 * l.current_flow;

				if (getprop("/fdm/jsbsim/systems/mps/helium[1]/demand-status") == 1)
					{
					me.he_inct_flow += l.current_flow;
					}
				else
					{
					me.he_right_flow += l.current_flow;
					}
				if (me.verbose == 1)
					{print ("Right Helium manifold flow is ", me.he_right_flow);}
				}
			if (l.designation == "right-helium-manifold-A")
				{
				me.right_reg_A_reduction = -4000.0 * l.current_flow;

				if (getprop("/fdm/jsbsim/systems/mps/helium[1]/demand-status") == 1)
					{
					me.he_inct_flow += l.current_flow;
					}
				else
					{
					me.he_right_flow += l.current_flow;
					}
				if (me.verbose == 1)
					{print ("Right Helium manifold A flow is ", me.he_right_flow);}
				}
			if (l.designation == "right-helium-manifold-B")
				{
				me.right_reg_B_reduction = -4000.0 * l.current_flow;

				if (getprop("/fdm/jsbsim/systems/mps/helium[1]/demand-status") == 1)
					{
					me.he_inct_flow += l.current_flow;
					}
				else
					{
					me.he_right_flow += l.current_flow;
					}
				if (me.verbose == 1)
					{print ("Right Helium manifold B flow is ", me.he_right_flow);}
				}
			if (l.designation == "center-helium-tank")
				{
				me.he_center_flow += l.current_flow;
				if (me.verbose == 1)
					{print ("Center Helium tank flow is ", me.he_center_flow);}
				}
			if (l.designation == "center-helium-manifold")
				{
				me.center_reg_A_reduction = -2000.0 * l.current_flow;
				me.center_reg_B_reduction = -2000.0 * l.current_flow;

				if (getprop("/fdm/jsbsim/systems/mps/helium[2]/demand-status") == 1)
					{
					me.he_inct_flow += l.current_flow;
					}
				else
					{
					me.he_center_flow += l.current_flow;
					}
				if (me.verbose == 1)
					{print ("Center Helium manifold flow is ", me.he_center_flow);}
				}
			if (l.designation == "center-helium-manifold-A")
				{
				me.center_reg_A_reduction = -4000.0 * l.current_flow;

				if (getprop("/fdm/jsbsim/systems/mps/helium[2]/demand-status") == 1)
					{
					me.he_inct_flow += l.current_flow;
					}
				else
					{
					me.he_center_flow += l.current_flow;
					}
				if (me.verbose == 1)
					{print ("Center Helium manifold A flow is ", me.he_center_flow);}
				}
			if (l.designation == "center-helium-manifold-B")
				{
				me.center_reg_B_reduction = -4000.0 * l.current_flow;

				if (getprop("/fdm/jsbsim/systems/mps/helium[2]/demand-status") == 1)
					{
					me.he_inct_flow += l.current_flow;
					}
				else
					{
					me.he_center_flow += l.current_flow;
					}
				if (me.verbose == 1)
					{print ("Center Helium manifold B flow is ", me.he_center_flow);}
				}
			if (l.designation == "pneu-helium-tank")
				{
				me.he_pneu_flow += l.current_flow;
				if (me.verbose == 1)
					{print ("Pneumatic Helium flow is ", me.he_pneu_flow);}
				}



			}

		if (me.verbose == 1)
			{
			print ("Final left helium flow: ", me.he_left_flow);
			print ("Final center helium flow: ", me.he_center_flow);
			print ("Final right helium flow: ", me.he_right_flow);
			print ("Final pneumatic helium flow: ", me.he_pneu_flow);
			print ("Final interconnect helium flow: ", me.he_inct_flow);
			}

		

		setprop("/fdm/jsbsim/systems/failures/leakage/mps-left-helium-leak-flow", me.he_left_flow);
		setprop("/fdm/jsbsim/systems/failures/leakage/mps-center-helium-leak-flow", me.he_center_flow);
		setprop("/fdm/jsbsim/systems/failures/leakage/mps-right-helium-leak-flow", me.he_right_flow);
		setprop("/fdm/jsbsim/systems/failures/leakage/mps-pneu-helium-leak-flow", me.he_pneu_flow);
		setprop("/fdm/jsbsim/systems/failures/leakage/mps-inct-helium-leak-flow", me.he_inct_flow);
	},

	add_leak: func (designation, flow) {

		if (flow > 0.0)
			{
			print ("Leakage flow must be negative!");
			return;
			}

		foreach(l; me.leakage_points)
			{
			if (l.designation == designation)
				{
				print ("Adding leak to ", l.designation);
				l.add_leak(flow);
				}

			}


	},

};

helium_leakage_manager.init();


# listeners for the interconnect valves

setlistener("/fdm/jsbsim/systems/mps/engine[0]/helium-interconnect-valve-status", func 
		{
		settimer ( func { # needs to be delayed to give JSBSim a chance to update		
		helium_leakage_manager.update();
	
		}, 0.1);

		});

setlistener("/fdm/jsbsim/systems/mps/engine[1]/helium-interconnect-valve-status", func 
		{
		settimer ( func { # needs to be delayed to give JSBSim a chance to update		
		helium_leakage_manager.update();
	
		}, 0.1);

		});

setlistener("/fdm/jsbsim/systems/mps/engine[2]/helium-interconnect-valve-status", func 
		{
		settimer ( func { # needs to be delayed to give JSBSim a chance to update		
		helium_leakage_manager.update();
	
		}, 0.1);

		});
