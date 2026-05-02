


###########################################################################
# class to manage a payload as numerical simulation at close range
#
###########################################################################

var payload_manager = {


	state: {},
	coord: {},
	shuttleCoord: {},
	endEffectorCoord: {},	
	refCoord: {},
	plModel: {},
	plInitialState: [0,0,0,0,0,0],
	offset_vec: [0,0,0],
	Offset: [0,0,0],

	bearing: 0.0,
	distance: 0.0,
	hdistance: 0.0,
	prox_x: 0.0,
	prox_y: 0.0,
	prox_z: 0.0,
	prox_vx: 0.0,
	prox_vy: 0.0,
	prox_vz: 0.0,
	prox_x_last: 0.0,
	prox_y_last: 0.0,
	prox_z_last: 0.0,
	distance_last: 0.0,
	rdot: 0.0,

	dt: 0.0,	
	delta_lon: 0.0,

	docking_collar_dist_last: 0.0,

	dcbearing: 0.0,
	dchdistance: 0.0,
	dcprox_x: 0.0,
	dcprox_y: 0.0,
	dcprox_z: 0.0,
	ddot: 0.0,
	y: 0.0, 
	y_last: 0.0,
	ydot: 0.0,
	theta: 0.0,

	crash_force_z: 0.0,

	loop_flag: 0,
	placement_flag: 0,
	sensor_flag: 0,
	interaction_test_flag: 0,
	proximity_request: 0,
	tracking_request: 0,

	effector_x: 0.0,
	effector_y: 0.0, 
	effector_z: 0.0,



	new: func (name, model_path, index) {
	 	var p = { parents: [payload_manager] };

		p.name = name;

		p.index = index;
	
		p.ctrl_path = "/controls/shuttle/"~p.name~"/";
		p.model_path = model_path;
		
		var data = SpaceShuttle.payload_data.entry_by_index(index);

		p.solid_flag = data.solid_flag;
		p.center_offset = data.center_offset;
		p.deployment_sequence = data.deployment_sequence;
		p.deployment_sequence_time = data.deployment_sequence_time;
		
		var norm = math.sqrt(p.center_offset[0] * p.center_offset[0] + p.center_offset[1] * p.center_offset[1] + p.center_offset[2] * p.center_offset[2]);

		p.center_offset_normalized = [p.center_offset[0]/norm, p.center_offset[1]/norm, p.center_offset[2]/norm];

		p.solid_radius = data.solid_radius;
		p.mass = data.mass;

		p.nd_ref_effector_x = props.globals.getNode("/fdm/jsbsim/systems/rms/effector-x", 1);
		p.nd_ref_effector_y = props.globals.getNode("/fdm/jsbsim/systems/rms/effector-y", 1);
		p.nd_ref_effector_z = props.globals.getNode("/fdm/jsbsim/systems/rms/effector-z", 1);


		p.nd_ref_world_body_x0 = props.globals.getNode("/fdm/jsbsim/systems/pointing/world/body-x" ,1);
		p.nd_ref_world_body_x1 = props.globals.getNode("/fdm/jsbsim/systems/pointing/world/body-x[1]" ,1);
		p.nd_ref_world_body_x2 = props.globals.getNode("/fdm/jsbsim/systems/pointing/world/body-x[2]" ,1);
		
		p.nd_ref_world_body_y0 = props.globals.getNode("/fdm/jsbsim/systems/pointing/world/body-y" ,1);
		p.nd_ref_world_body_y1 = props.globals.getNode("/fdm/jsbsim/systems/pointing/world/body-y[1]" ,1);
		p.nd_ref_world_body_y2 = props.globals.getNode("/fdm/jsbsim/systems/pointing/world/body-y[2]" ,1);

		p.nd_ref_world_body_z0 = props.globals.getNode("/fdm/jsbsim/systems/pointing/world/body-z" ,1);
		p.nd_ref_world_body_z1 = props.globals.getNode("/fdm/jsbsim/systems/pointing/world/body-z[1]" ,1);
		p.nd_ref_world_body_z2 = props.globals.getNode("/fdm/jsbsim/systems/pointing/world/body-z[2]" ,1);

		return p;
		},


	copy_offsets: func {


		# copy current animation state of the payload

		var pitch1 = getprop("/fdm/jsbsim/systems/rms/sum-wrist-pitch-deg");
		setprop(me.ctrl_path~"payload-pitch-deg", pitch1);

		var yaw1 = getprop("/fdm/jsbsim/systems/rms/sum-wrist-yaw-deg");
		setprop(me.ctrl_path~"payload-yaw-deg", yaw1);

		var roll1 = getprop("/fdm/jsbsim/systems/rms/ang-wrist-roll-deg");
		setprop(me.ctrl_path~"payload-roll-deg", roll1);

		var x = -getprop("/fdm/jsbsim/systems/rms/effector-x") + 8.5;
		var y = getprop("/fdm/jsbsim/systems/rms/effector-y") - 2.1;
		var z = getprop("/fdm/jsbsim/systems/rms/effector-z") - 1.1;

		print ("Body coord offsets: ", x, " ", y, " ", z);

		me.compute_offset(x, y , z );

		},


	compute_offset: func (off_x, off_y, off_z) {


		var shuttleWorldX = [getprop("/fdm/jsbsim/systems/pointing/world/body-x"), getprop("/fdm/jsbsim/systems/pointing/world/body-x[1]"), getprop("/fdm/jsbsim/systems/pointing/world/body-x[2]")];

		var shuttleWorldY = [getprop("/fdm/jsbsim/systems/pointing/world/body-y"), getprop("/fdm/jsbsim/systems/pointing/world/body-y[1]"), getprop("/fdm/jsbsim/systems/pointing/world/body-y[2]")];

		var shuttleWorldZ = [getprop("/fdm/jsbsim/systems/pointing/world/body-z"), getprop("/fdm/jsbsim/systems/pointing/world/body-z[1]"), getprop("/fdm/jsbsim/systems/pointing/world/body-z[2]")];


		me.Offset = SpaceShuttle.add_vector(SpaceShuttle.scalar_product(off_x, shuttleWorldX), SpaceShuttle.scalar_product(off_z, shuttleWorldZ));
		me.Offset = SpaceShuttle.add_vector(me.Offset, SpaceShuttle.scalar_product(off_y, shuttleWorldY));


		print ("World coord offsets: ", me.Offset[0], " ", me.Offset[1], " ", me.Offset[2]);

	},



	init : func (prox_x, prox_y, prox_z, dvx, dvy, dvz)  {


		var basecoord = geo.aircraft_position() ;

		print ("Base coords: ", basecoord.x(),  " ", basecoord.y(), " ", basecoord.z());
		print ("World coord offsets: ", me.Offset[0], " ", me.Offset[1], " ", me.Offset[2]);

		me.coord = geo.Coord.new();
		me.coord.set_xyz (basecoord.x() + me.Offset[0], basecoord.y() + me.Offset[1],basecoord.z() + me.Offset[2]);

		print ("Offset coords: ", me.coord.x(),  " ", me.coord.y(), " ", me.coord.z());

		var alt_new = me.coord.alt() - prox_z;
		me.coord.set_alt(alt_new );

		var course = getprop("/fdm/jsbsim/velocities/course-deg");
		me.coord.apply_course_distance(course, prox_x);

		if (prox_y > 0) {course = course + 90.0;}
		else {course = course - 90.0;}
		me.coord.apply_course_distance(course, math.abs(prox_y));

		print ("Proximity offset coords: ", me.coord.x(),  " ", me.coord.y(), " ", me.coord.z());

		var lon = getprop("/position/longitude-deg");
		var pitch = getprop("/orientation/pitch-deg");
		var yaw = getprop("/orientation/heading-deg");
		var roll = getprop("/orientation/roll-deg");


		me.state = stateVector.new (me.coord.x(),me.coord.y(),me.coord.z(),0,0,0,  yaw, pitch - lon, roll);
		me.state.lvlh_flag = 0;

		me.plInitialState = [prox_x, prox_y, prox_z, dvx, dvy, dvz];



		me.plModel = place_model(me.name, me.model_path, me.coord.lat(), me.coord.lon(), me.coord.alt() * m_to_ft, yaw, pitch,roll);


		#var test_coord = geo.aircraft_position();
		#print ("Distance at placement: ", test_coord.direct_distance_to(me.coord));

		var lat = getprop("/position/latitude-deg") * math.pi/180.0;
		var lon = getprop("/position/longitude-deg") * math.pi/180.0;
		var dt = getprop("/sim/time/delta-sec");

		var vxoffset = 3.5 * math.cos(lon) * math.pow(dt/0.05,3.0);
		var vyoffset = 3.5 * math.sin(lon) * math.pow(dt/0.05,3.0);
		var vzoffset = 0.0;


		me.delta_lon = 0.0;

		SpaceShuttle.proximity_manager.announce_payload_state(1, me.index);


		# start deployment sequence if we release, deploy instantly if we encounter

		if (me.deployment_sequence == 1)
			{

			if (prox_x * prox_x +  prox_y * prox_y + prox_z * prox_z > 1000.0)
				{
				setprop(me.ctrl_path~"payload-deployment-stage", 1);
				}
			else
				{
				settimer(func { 
					setprop(me.ctrl_path~"payload-deployment-stage", 1);
						}, me.deployment_sequence_time);
				}
			}


		settimer(func { 
				me.state.vx = getprop("/fdm/jsbsim/velocities/eci-x-fps") * ft_to_m + vxoffset;
				me.state.vy = getprop("/fdm/jsbsim/velocities/eci-y-fps") * ft_to_m + vyoffset;
				me.state.vz = getprop("/fdm/jsbsim/velocities/eci-z-fps") * ft_to_m + vzoffset;
				me.loop_flag = 1;
				me.placement_flag = 1;
				me.update(); },0);
	},


	update: func () {

		me.shuttleCoord = geo.aircraft_position();
		me.dt = getprop("/sim/time/delta-sec");


		me.delta_lon = me.delta_lon + me.dt * earth_rotation_deg_s * 1.0039;

		var F = get_force (me.state, me.shuttleCoord);

		me.state.update(F[0], F[1], F[2], 0.0,0.0,0.0);
		me.coord.set_xyz(me.state.x, me.state.y, me.state.z);
		me.coord.set_lon(me.coord.lon() - me.delta_lon);


		if (me.loop_flag < 3)
			{
			me.manage_initial_placement();
			}

		set_coords(me.name, me.coord, me.state);

		me.compute_proximity();
		me.set_sensor_tracking();
		me.compute_relative_coordinates();

		if (me.proximity_request == 1) {me.provide_proximity();}
		if (me.sensor_flag == 1) {me.compute_sensor_data();}
		if (me.tracking_request == 1) {me.provide_tracking();}

		#print (me.distance);


		if (me.distance > 1.2 * SpaceShuttle.orbital_target_lod)  {me.unload();}
		


		if (me.loop_flag >0 ) 
			{
			settimer(func {me.update(); },0.0);
			}



	},

	compute_proximity: func {

		me.refCoord = geo.Coord.new(me.shuttleCoord);

			

		me.bearing = me.refCoord.course_to(me.coord);
		me.hdistance = me.refCoord.distance_to(me.coord);
		me.distance = me.refCoord.direct_distance_to(me.coord);
		me.prox_z = me.refCoord.alt() - me.coord.alt();
		var ground_course = getprop("/fdm/jsbsim/velocities/course-deg");
		me.prox_x = me.hdistance * math.cos((me.bearing - ground_course) * math.pi/180.0);
		me.prox_y = me.hdistance * math.sin((me.bearing - ground_course) * math.pi/180.0);

		me.prox_vx = (me.prox_x - me.prox_x_last)/me.dt;
		me.prox_vy = (me.prox_y - me.prox_y_last)/me.dt;
		me.prox_vz = (me.prox_z - me.prox_z_last)/me.dt;

		me.rdot = (me.distance - me.distance_last)/me.dt;

		me.prox_x_last = me.prox_x;
		me.prox_y_last = me.prox_y;
		me.prox_z_last = me.prox_z;

		me.distance_last = me.distance;


	},	

	list_proximity: func {

		print (me.name~" proximity coordinates: ");
		print ("x: ", me.prox_x);
		print ("y: ", me.prox_y);
		print ("z: ", me.prox_z);
		print ("r: ", me.distance);

	},

	list_proximity_v: func {

		print (me.name~" proximity velocities: ");
		print ("vx: ", me.prox_vx);
		print ("vy: ", me.prox_vy);
		print ("vz: ", me.prox_vz);
		print ("vr: ", me.rdot);

	},

	provide_proximity: func {


		SpaceShuttle.proximity_manager.target_prox_x = me.prox_x;
		SpaceShuttle.proximity_manager.target_prox_y = me.prox_y;
		SpaceShuttle.proximity_manager.target_prox_z = me.prox_z;
			

		SpaceShuttle.proximity_manager.target_prox_vx = me.prox_vx;
		SpaceShuttle.proximity_manager.target_prox_vy = me.prox_vy;
		SpaceShuttle.proximity_manager.target_prox_vz = me.prox_vz;

		me.proximity_request = 0;

	},

	request_proximity: func {
		
		me.proximity_request = 1;

	},

	
	provide_tracking: func {

		# provides tracking vectors for UNIV PTG


		var shuttle_pos_inertial = geo.Coord.new(me.shuttleCoord);
		var tgt_pos_inertial = geo.Coord.new(me.coord);

		# go to inertial coordinates

		var angle = -getprop("/fdm/jsbsim/systems/pointing/inertial/ecf-to-eci-rad-alt") * 180.0/math.pi;


		shuttle_pos_inertial.set_lon(shuttle_pos_inertial.lon() - angle);
		tgt_pos_inertial.set_lon(tgt_pos_inertial.lon() - angle);

		# pointing vector  in inertial coordinates

		var shuttle_inertial = shuttle_pos_inertial.xyz();
		var tgt_inertial = tgt_pos_inertial.xyz();

		var pointer = SpaceShuttle.normalize(SpaceShuttle.subtract_vector(tgt_inertial, shuttle_inertial));


		setprop("/fdm/jsbsim/systems/ap/track/target-vector[0]", pointer[0]);
		setprop("/fdm/jsbsim/systems/ap/track/target-vector[1]", pointer[1]);
		setprop("/fdm/jsbsim/systems/ap/track/target-vector[2]", pointer[2]);

		var body_vec_selection = getprop("/fdm/jsbsim/systems/ap/track/body-vector-selection");

		var ref_vector = [];

		if (body_vec_selection == 1)
			{
			ref_vec = [0.0, 0.0, 1.0];
			}
		else if (body_vec_selection == 2)
			{
			ref_vec = [0.0, 0.0, -1.0];
			}
		else if (body_vec_selection == 3)
			{
			ref_vec = [0.0, 0.0, 1.0];
			}

		var second = SpaceShuttle.orthonormalize(pointer, [0.0, 0.0, 1.0]);

		setprop("/fdm/jsbsim/systems/ap/track/target-sec[0]", second[0]);
		setprop("/fdm/jsbsim/systems/ap/track/target-sec[1]", second[1]);
		setprop("/fdm/jsbsim/systems/ap/track/target-sec[2]", second[2]);

		var third = SpaceShuttle.cross_product(pointer, second);

		setprop("/fdm/jsbsim/systems/ap/track/target-trd[0]", third[0]);
		setprop("/fdm/jsbsim/systems/ap/track/target-trd[1]", third[1]);
		setprop("/fdm/jsbsim/systems/ap/track/target-trd[2]", third[2]);


		me.tracking_request = 0;

	},


	request_tracking: func {

		me.tracking_request = 1;

	},

	
	set_sensor_tracking: func {


		if (SpaceShuttle.antenna_manager.function == "RDR PASSIVE") 
			{



			SpaceShuttle.antenna_manager.set_rr_target(me.coord);
			if ((SpaceShuttle.antenna_manager.rr_target_available == 1) and (SpaceShuttle.antenna_manager.rvdz_data == 1))
				{
				SpaceShuttle.antenna_manager.ku_antenna_track_target(me.coord, me.shuttleCoord);
				}		
			}
		if (SpaceShuttle.star_tracker_array[0].mode == 2)
			{
			SpaceShuttle.star_tracker_array[0].set_target(me.coord);
			}

		if (SpaceShuttle.star_tracker_array[1].mode == 2)
			{
			SpaceShuttle.star_tracker_array[1].set_target(me.coord);
			}

	},

	compute_tracking: func {


	},

	compute_end_effector: func {

		var x = -me.nd_ref_effector_x.getValue() + 8.5;
		var y = me.nd_ref_effector_y.getValue() - 2.1;
		var z = me.nd_ref_effector_z.getValue() - 1.1;

		me.effector_x = x;
		me.effector_y = y;
		me.effector_z = z;


		var shuttleWorldX = [getprop("/fdm/jsbsim/systems/pointing/world/body-x"), getprop("/fdm/jsbsim/systems/pointing/world/body-x[1]"), getprop("/fdm/jsbsim/systems/pointing/world/body-x[2]")];

		var shuttleWorldY = [getprop("/fdm/jsbsim/systems/pointing/world/body-y"), getprop("/fdm/jsbsim/systems/pointing/world/body-y[1]"), getprop("/fdm/jsbsim/systems/pointing/world/body-y[2]")];

		var shuttleWorldZ = [getprop("/fdm/jsbsim/systems/pointing/world/body-z"), getprop("/fdm/jsbsim/systems/pointing/world/body-z[1]"), getprop("/fdm/jsbsim/systems/pointing/world/body-z[2]")];

		var Offset = SpaceShuttle.add_vector(SpaceShuttle.scalar_product(x, shuttleWorldX), SpaceShuttle.scalar_product(z, shuttleWorldZ));
		Offset = SpaceShuttle.add_vector(Offset, SpaceShuttle.scalar_product(y, shuttleWorldY));


		me.endEffectorCoord = geo.Coord.new(me.shuttleCoord);

		me.endEffectorCoord.set_xyz (me.shuttleCoord.x() + Offset[0],me.shuttleCoord.y() + Offset[1],me.shuttleCoord.z() + Offset[2]);

	},


	compute_relative_coordinates: func {


		if (me.distance > 10.0)
			{
			me.refCoord = geo.Coord.new(me.shuttleCoord);
			me.interaction_test_flag = 0;
			}
		else
			{
			me.compute_end_effector();
			me.refCoord = geo.Coord.new(me.endEffectorCoord);
			me.interaction_test_flag = 1;
			}

		var shuttleLVLHZ = [-getprop("/fdm/jsbsim/systems/pointing/lvlh/body-z"), -getprop("/fdm/jsbsim/systems/pointing/lvlh/body-z[1]"), -getprop("/fdm/jsbsim/systems/pointing/lvlh/body-z[2]")];

		me.docking_collar_dist = me.refCoord.direct_distance_to(me.coord);
		me.ddot = (me.docking_collar_dist - me.docking_collar_dist_last)/me.dt;
		me.docking_collar_dist_last = me.docking_collar_dist;



		setprop("/fdm/jsbsim/systems/rendezvous/target/distance-m", me.docking_collar_dist);
		#setprop("/fdm/jsbsim/systems/rendezvous/target/ddot-m_s", me.ddot);

		var iss_roll = getprop(me.ctrl_path~"roll-deg");
		var iss_pitch = getprop(me.ctrl_path~"pitch-deg");
		var iss_yaw = getprop(me.ctrl_path~"heading-deg");

		var y_vec = orientTaitBryan(me.center_offset_normalized, iss_yaw, iss_pitch, iss_roll);
		var center_vec = orientTaitBryan(me.center_offset, iss_yaw, iss_pitch, iss_roll);

		var lat_to_m = 110952.0;
		var lon_to_m  = math.cos(me.coord.lat()*math.pi/180.0) * lat_to_m;

		var x_lvlh = (me.coord.lon() - me.refCoord.lon()) * lon_to_m;
		var y_lvlh = (me.coord.lat() - me.refCoord.lat()) * lat_to_m;
		var z_lvlh = (me.coord.alt() - me.refCoord.alt());

		var rel_vec = [x_lvlh, y_lvlh, z_lvlh];
		
		if ((me.interaction_test_flag == 1) and (me.solid_flag == 1))
			{
			var center_coord = geo.Coord.new(me.coord);

			center_coord.set_lon(center_coord.lon() + center_vec[0]/lon_to_m);
			center_coord.set_lat(center_coord.lat() + center_vec[1]/lat_to_m);
			center_coord.set_alt(center_coord.alt() + center_vec[2]);


			var center_dist = center_coord.direct_distance_to(me.refCoord);

			if (center_dist < me.solid_radius)
				{
				me.compute_interaction(center_coord);
				}

			#print ("Attach point dist.:   ",math.sqrt(rel_vec[0] * rel_vec[0] + rel_vec[1] * rel_vec[1] + rel_vec[2] * rel_vec[2])); 
			#print ("Interaction distance: ",center_dist);

			}

		me.y = -SpaceShuttle.dot_product(y_vec, rel_vec);
		me.ydot = (me.y - me.y_last)/me.dt;
		me.y_last = me.y;
		me.theta = 180.0/math.pi * math.acos(SpaceShuttle.dot_product(y_vec, shuttleLVLHZ));

	},


	compute_interaction: func (center_coord) {


		center_coord.set_lon(center_coord.lon() + me.delta_lon);
		me.refCoord.set_lon(me.refCoord.lon() + me.delta_lon);

		var center = [center_coord.x(), center_coord.y(), center_coord.z()];
		var effector = [me.refCoord.x(), me.refCoord.y(), me.refCoord.z()];

		var rel_vec = SpaceShuttle.normalize(SpaceShuttle.subtract_vector(center, effector));
		
		var force = me.solid_radius - center_coord.direct_distance_to(me.refCoord);
		if (force < 0.0) {force = 0.0;}
		force *=  5.0 * getprop("/sim/time/delta-sec");
	
		me.state.vx += force * rel_vec[0];
		me.state.vy += force * rel_vec[1];
		me.state.vz += force * rel_vec[2];

		var slowdown_factor = 1.0 - 10.0 * force;
		if (slowdown_factor < 0.5) {slowdown_factor = 0.5;}

		me.state.pitch_rate *= slowdown_factor;
		me.state.yaw_rate *= slowdown_factor;
		me.state.roll_rate *= slowdown_factor;
	
		#print ("Force: ", force, " Slowdown: ", slowdown_factor);

		#print ("Inertial dist.: ", center_coord.direct_distance_to(me.refCoord));
		
	},




	unload: func {

		print (me.name~" explicit simulation ends");
		me.plModel.remove();
		me.loop_flag = 0;
		#proximity_manager.iss_model = 0;
		proximity_manager.announce_payload_state(0, me.index);
	},


	manage_initial_placement: func {

		if (me.loop_flag ==1)
			{
			me.offset_vec = [me.coord.x()-me.shuttleCoord.x(), me.coord.y()-me.shuttleCoord.y(),me.coord.z()-me.shuttleCoord.z()];
			}
		if (me.loop_flag == 2)
			{
			var offset1_vec = [me.coord.x()-me.shuttleCoord.x(), me.coord.y()-me.shuttleCoord.y(),me.coord.z()-me.shuttleCoord.z()];
			var v_offset_vec = [(offset1_vec[0] - me.offset_vec[0]) / me.dt, (offset1_vec[1] - me.offset_vec[1]) / me.dt, (offset1_vec[2] - me.offset_vec[2]) / me.dt];
		


			me.state = compute_state_correction  (me.state, me.coord, me.shuttleCoord, v_offset_vec, me.delta_lon);
			if (me.placement_flag == 1)
				{
				var pl_placement = geo.Coord.new();
				pl_placement.set_xyz (me.state.x + me.Offset[0], me.state.y + me.Offset[1], me.state.z + me.Offset[2]);

				var prox_x = me.plInitialState[0];
				var prox_y = me.plInitialState[1];
				var prox_z = me.plInitialState[2];	

				print ("Coordinate differences proximity:");
				print (prox_x, " ", prox_y, " ", prox_z);		

				print (me.name~" alt2 before: ", pl_placement.alt(), " prox_z: ", prox_z); 
			
				var alt_new = pl_placement.alt() - prox_z;
				pl_placement.set_alt( alt_new);

				var course = getprop("/fdm/jsbsim/velocities/course-deg");
				pl_placement.apply_course_distance(course, prox_x);

				if (prox_y > 0) {course = course + 90.0;}
				else {course = course - 90.0;}
				pl_placement.apply_course_distance(course, math.abs(prox_y));
			
				print (me.name~" alt2 aft: ", pl_placement.alt()); 


				me.state.x = pl_placement.x();
				me.state.y = pl_placement.y();
				me.state.z = pl_placement.z();


				me.state.vx+= me.plInitialState[3];
				me.state.vy+= me.plInitialState[4];
				me.state.vz+= me.plInitialState[5];

				# need a distance-dependent down

				var norm_tmp = math.sqrt(me.state.x * me.state.x + me.state.y * me.state.y + me.state.z * me.state.z);
				var down = [-me.state.x/norm_tmp, -me.state.y/norm_tmp, -me.state.z/norm_tmp];

				var hdist = prox_x; #math.sqrt(prox_x * prox_x + prox_z * prox_z);


				me.state.vx += down[0]*6.0 * hdist/5000.0 * 0.96;
				me.state.vy += down[1]*6.0 * hdist/5000.0 * 0.96;
				me.state.vz += down[2]*6.0 * hdist/5000.0 * 0.96;


				}
			else if (me.placement_flag == 2)
				{
				var pl_placement = geo.Coord.new();
				pl_placement.set_xyz (me.state.x, me.state.y, me.state.z);

				var shuttleWorldX = [getprop("/fdm/jsbsim/systems/pointing/world/body-x"), getprop("/fdm/jsbsim/systems/pointing/world/body-x[1]"), getprop("/fdm/jsbsim/systems/pointing/world/body-x[2]")];

				var shuttleWorldZ = [getprop("/fdm/jsbsim/systems/pointing/world/body-z"), getprop("/fdm/jsbsim/systems/pointing/world/body-z[1]"), getprop("/fdm/jsbsim/systems/pointing/world/body-z[2]")];

				var shuttleLVLHZ = [-getprop("/fdm/jsbsim/systems/pointing/lvlh/body-z"), -getprop("/fdm/jsbsim/systems/pointing/lvlh/body-z[1]"), -getprop("/fdm/jsbsim/systems/pointing/lvlh/body-z[2]")];

				

				pl_placement.set_x( pl_placement.x()); 
				pl_placement.set_y( pl_placement.y()); 
				pl_placement.set_z( pl_placement.z()); 

				me.state.x = pl_placement.x();
				me.state.y = pl_placement.y();
				me.state.z = pl_placement.z();
				}
				}
		me.loop_flag = me.loop_flag + 1;
			




		},


};

var hst_manager = payload_manager.new("HST", "Aircraft/SpaceShuttle/Models/PayloadBay/HST/hst-disconnected.xml", 3);
var spartan_manager = payload_manager.new("SPARTAN-201", "Aircraft/SpaceShuttle/Models/PayloadBay/Spartan-201/SPARTAN-201-disconnected.xml", 2);
var TDRS_manager = payload_manager.new("TDRS-demo", "Aircraft/SpaceShuttle/Models/PayloadBay/TDRS/TDRS_disconnected.xml", 1);
