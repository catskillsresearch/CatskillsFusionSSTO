
# class to manage the Eileen simulated pilot function

var eileen = {

	holding_tgt_x: 0.0,
	holding_tgt_y: 0.0,
	holding_tgt_z: 0.0,

	tgt_vx: 0.0,
	tgt_vy: 0.0,
	tgt_vz: 0.0,

	error_x: 0.0,
	error_y: 0.0,
	error_z: 0.0,

	error_vx: 0.0,
	error_vy: 0.0,
	error_vz: 0.0,

	limit_x: 0.1,
	limit_y: 0.1,
	limit_z: 0.1,

	limit_vx: 0.01,
	limit_vy: 0.01,
	limit_vz: 0.01,

	firing_prograde: 0.0,
	firing_radial: 0.0,
	firing_normal: 0.0,

	firing_x: 0.0,
	firing_y: 0.0,
	firing_z: 0.0,

	prograde_inertial: [],
	radial_inertial: [],
	normal_inertial: [],

	stationkeeping_flag: 0,
	firing_flag: 0,
	precision_setting: 0,

	

	init_stationkeeping: func {

		if (SpaceShuttle.proximity_manager.iss_model == 0)
			{
			SpaceShuttle.callout.make("I'm unable to comply - no target in visual range.", "essential");
			return;
			}

		orbital_dap_manager.control_select("LVLH");
		orbital_dap_manager.input_device_select("THC");

		me.holding_tgt_x = SpaceShuttle.proximity_manager.target_prox_x;
		me.holding_tgt_y = SpaceShuttle.proximity_manager.target_prox_y;
		me.holding_tgt_z = SpaceShuttle.proximity_manager.target_prox_z;

		setprop("/fdm/jsbsim/fcs/eileen-in-control", 1);

		me.stationkeeping_flag = 1;
		me.stationkeeping_loop();

		var obj_name = SpaceShuttle.proximity_manager.query_reference_name();

		SpaceShuttle.callout.make("Starting stationkeeping with respect to "~obj_name~".", "essential");

		print ("Stationkeeping init.");		

	},

	stationkeeping_loop: func {

		
		me.error_x = SpaceShuttle.proximity_manager.target_prox_x - me.holding_tgt_x;
		me.error_y = SpaceShuttle.proximity_manager.target_prox_y - me.holding_tgt_y;
		me.error_z = SpaceShuttle.proximity_manager.target_prox_z - me.holding_tgt_z;

		if (me.error_x > 3.0 * me.limit_x)  
			{me.tgt_vx = -3.0 * me.limit_vx;}
		else if (me.error_x >  me.limit_x)  
			{me.tgt_vx = -0.5 * me.limit_vx;}
		else if (me.error_x < -me.limit_x)
			{me.tgt_vx = 0.5 * me.limit_vx;}
		else if (me.error_x < -3.0 *me.limit_x)
			{me.tgt_vx = 3.0 * me.limit_vx;}
		else
			{me.tgt_vx = 0.0;}

		if (me.error_y > me.limit_y) 
			{me.tgt_vy = -0.5 * me.limit_vy;}
		else if (me.error_y > 3.0 * me.limit_y) 
			{me.tgt_vy = -3.0 * me.limit_vy;}
		else if (me.error_y < -me.limit_y)
			{me.tgt_vy = 0.5 * me.limit_vy;}
		else if (me.error_y < -3.0 * me.limit_y)
			{me.tgt_vy = 3.0 * me.limit_vy;}
		else
			{me.tgt_vy = 0.0;}

		if (me.error_z > me.limit_z) 
			{me.tgt_vz = -0.5 * me.limit_vz;}
		else if (me.error_z > 3.0 * me.limit_z) 
			{me.tgt_vz = -3.0 * me.limit_vz;}
		else if (me.error_z < -me.limit_z)
			{me.tgt_vz = 0.5 * me.limit_vz;}
		else if (me.error_z < -3.0 * me.limit_z)
			{me.tgt_vz = 3.0 * me.limit_vz;}
		else
			{me.tgt_vz = 0.0;}


		me.error_vx = SpaceShuttle.proximity_manager.target_prox_vx - me.tgt_vx;
		me.error_vy = SpaceShuttle.proximity_manager.target_prox_vy - me.tgt_vy;
		me.error_vz = SpaceShuttle.proximity_manager.target_prox_vz - me.tgt_vz;

		#print ("Pos: ", me.error_x, " ", me.error_y, " ", me.error_z);
		#print ("Vel: ", me.error_vx, " ", me.error_vy, " ", me.error_vz);
		#print ("Tgt: ", me.tgt_vx, " ", me.tgt_vy, " ", me.tgt_vz);

		me.firing_flag = 0;

		if ((math.abs(me.error_x) > me.limit_x) or (math.abs(me.error_y) > me.limit_y) or (me.error_z < me.limit_z))
			{me.firing_flag = 1;}	

		if ((math.abs(me.error_vx) > me.limit_vx) or (math.abs(me.error_vy) > me.limit_vy) or (me.error_vz < me.limit_vz))
			{me.firing_flag = 1;}

		if (me.firing_flag == 1)
			{	


			me.prograde_inertial = [getprop("/fdm/jsbsim/systems/pointing/inertial/prograde[0]"), getprop("/fdm/jsbsim/systems/pointing/inertial/prograde[1]"), getprop("/fdm/jsbsim/systems/pointing/inertial/prograde[2]")];

			me.radial_inertial = [getprop("/fdm/jsbsim/systems/pointing/inertial/radial[0]"), getprop("/fdm/jsbsim/systems/pointing/inertial/radial[1]"), getprop("/fdm/jsbsim/systems/pointing/inertial/radial[2]")];

			me.normal_inertial = [getprop("/fdm/jsbsim/systems/pointing/inertial/normal[0]"), getprop("/fdm/jsbsim/systems/pointing/inertial/normal[1]"), getprop("/fdm/jsbsim/systems/pointing/inertial/normal[2]")];


			me.body_x_inertial = [getprop("/fdm/jsbsim/systems/pointing/inertial/body-x[0]"), getprop("/fdm/jsbsim/systems/pointing/inertial/body-x[1]"), getprop("/fdm/jsbsim/systems/pointing/inertial/body-x[2]")];
		
			me.body_y_inertial = [getprop("/fdm/jsbsim/systems/pointing/inertial/body-y[0]"), getprop("/fdm/jsbsim/systems/pointing/inertial/body-y[1]"), getprop("/fdm/jsbsim/systems/pointing/inertial/body-y[2]")];

			me.body_z_inertial = [getprop("/fdm/jsbsim/systems/pointing/inertial/body-z[0]"), getprop("/fdm/jsbsim/systems/pointing/inertial/body-z[1]"), getprop("/fdm/jsbsim/systems/pointing/inertial/body-z[2]")];

			
			

			#var body_x_fraction = SpaceShuttle.dot_product(me.prograde_inertial, me.body_x_inertial);
			 

			if (me.error_vx > me.limit_vx) {me.firing_prograde = 0.3;} 
			else if (me.error_vx > 3.0 * me.limit_vx) {me.firing_prograde = 0.6;} 
			else if  (me.error_vx < -me.limit_vx) {me.firing_prograde = -0.3;} 
			else if (me.error_vx < -3.0 * me.limit_vx) {me.firing_prograde = -0.6;} 
			else {me.firing_prograde = 0;}

			if (me.error_vy > me.limit_vy) {me.firing_normal = 0.3;} 
			else if (me.error_vy > 3.0 * me.limit_vy) {me.firing_normal = 0.6;} 
			else if  (me.error_vy < -me.limit_vy) {me.firing_normal = -0.3;} 
			else if (me.error_vy < -3.0 * me.limit_vy) {me.firing_normal = -0.6;} 
			else {me.firing_normal = 0;}

			if (me.error_vz > me.limit_vz) {me.firing_radial = -0.3;} 
			else if (me.error_vz > 3.0 * me.limit_vz) {me.firing_radial = -0.6;} 
			else if  (me.error_vz < -me.limit_vz) {me.firing_radial = 0.3;} 
			else if (me.error_vz < -3.0 * me.limit_vz) {me.firing_radial = 0.6;} 
			else {me.firing_radial = 0;}

			me.firing_x = me.firing_prograde * SpaceShuttle.dot_product(me.prograde_inertial, me.body_x_inertial);
			me.firing_x += me.firing_normal * SpaceShuttle.dot_product(me.normal_inertial, me.body_x_inertial);
			me.firing_x += me.firing_radial * SpaceShuttle.dot_product(me.radial_inertial, me.body_x_inertial);

			me.firing_y = me.firing_prograde * SpaceShuttle.dot_product(me.prograde_inertial, me.body_y_inertial);
			me.firing_y += me.firing_normal * SpaceShuttle.dot_product(me.normal_inertial, me.body_y_inertial);
			me.firing_y += me.firing_radial * SpaceShuttle.dot_product(me.radial_inertial, me.body_y_inertial);

			me.firing_z = me.firing_prograde * SpaceShuttle.dot_product(me.prograde_inertial, me.body_z_inertial);
			me.firing_z += me.firing_normal * SpaceShuttle.dot_product(me.normal_inertial, me.body_z_inertial);
			me.firing_z += me.firing_radial * SpaceShuttle.dot_product(me.radial_inertial, me.body_z_inertial);

			setprop("/fdm/jsbsim/fcs/rudder-cmd-norm-eileen", -me.firing_x);
			setprop("/fdm/jsbsim/fcs/elevator-cmd-norm-eileen", me.firing_z);
			setprop("/fdm/jsbsim/fcs/aileron-cmd-norm-eileen", me.firing_y);

			#setprop("/controls/flight/rudder", me.firing_x);
			#setprop("/controls/flight/elevator", me.firing_z);
			#setprop("/controls/flight/aileron", me.firing_y);

			}
		else
			{
			#setprop("/controls/flight/elevator", 0);
			#setprop("/controls/flight/aileron", 0);
			#setprop("/controls/flight/rudder", 0);

			setprop("/fdm/jsbsim/fcs/rudder-cmd-norm-eileen", 0);
			setprop("/fdm/jsbsim/fcs/elevator-cmd-norm-eileen", 0);
			setprop("/fdm/jsbsim/fcs/aileron-cmd-norm-eileen", 0);

			}


		if (me.stationkeeping_flag == 0)
			{
			#setprop("/controls/flight/elevator", 0);
			#setprop("/controls/flight/aileron", 0);
			#setprop("/controls/flight/rudder", 0);

			setprop("/fdm/jsbsim/fcs/rudder-cmd-norm-eileen", 0);
			setprop("/fdm/jsbsim/fcs/elevator-cmd-norm-eileen", 0);
			setprop("/fdm/jsbsim/fcs/aileron-cmd-norm-eileen", 0);
			return;
			}

		settimer (func {me.stationkeeping_loop();}, 0.5);
	},

	cycle_precision_setting: func {


		me.precision_setting = me.precision_setting + 1;
		if (me.precision_setting == 3) {me.precision_setting = 0;}

		if (me.precision_setting == 0)
			{
			me.limit_x = 0.1;
			me.limit_y = 0.1;
			me.limit_z = 0.1;

			me.limit_vx = 0.01;
			me.limit_vy = 0.01;
			me.limit_vz = 0.01;
			}
		else if (me.precision_setting == 1)
			{
			me.limit_x = 0.5;
			me.limit_y = 0.5;
			me.limit_z = 0.5;

			me.limit_vx = 0.02;
			me.limit_vy = 0.02;
			me.limit_vz = 0.02;
			}
		else if (me.precision_setting == 2)
			{
			me.limit_x = 2.5;
			me.limit_y = 2.5;
			me.limit_z = 2.5;

			me.limit_vx = 0.03;
			me.limit_vy = 0.03;
			me.limit_vz = 0.03;
			}

	},


	report_stationkeeping: func {

		print ("Current position errors: ");
		print ("x: ", me.error_x, " y: ", me.error_y, " z: ", me.error_z);
		print ("Current velocity errors: ");
		print ("vx: ", me.error_vx, " vy: ", me.error_vy, " vz: ", me.error_vz);
	},

	end_stationkeeping: func {

		setprop("/fdm/jsbsim/fcs/eileen-in-control", 0);
		me.stationkeeping_flag = 0;

		SpaceShuttle.callout.make("Roger - ending stationkeeping.", "essential");
		print ("Stationkeeping stop.");		
	},

};
