# entry guidance computer for the Space Shuttle



# we ought to have an organized collection of site data, not everything scattered across the dialogs

io.include("landing_sites.nas");



####


var landing_site = geo.Coord.new();
landing_site.index = 0;
landing_site.rwy_pri = "";
landing_site.rwy_sec = "";
landing_site.tacan = "";
landing_site.rwy_sel = 0;

var entry_guidance_available = 0;

var entry_interface = geo.Coord.new();
var distance_last = 0.0;

var radius_set = [];

#Variable for entry history path (Might extend it to 6  plot)
var trailer_set = {

	entry: [[0,0], [0,0], [0,0], [0,0], [0,0], [0,0]],
	entry_box: [[0,0], [0,0], [0,0], [0,0], [0,0], [0,0]],
	timer: 0,
	time_limit: 29,
	update: func (distance) {

	
	if (me.timer == 0)
		{
		me.timer = me.timer + 1;
		me.create_entry(distance);
		}
	else
		{me.timer = me.timer + 1;}
	if (me.timer >= me.time_limit) {me.timer = 0;}
	
	},

	updatebox: func (distance) {

	
	if (me.timer == 0)
		{
		me.timer = me.timer + 1;
		me.create_entry_box(distance);
		}
	else
		{me.timer = me.timer + 1;}
	if (me.timer >= me.time_limit) {me.timer = 0;}
	
	},

	

	create_entry: func (distance) {
	
	var velocity = getprop("/fdm/jsbsim/velocities/vtrue-fps"); #Vrel for entry
		
	#6  markers for shuttle path history 

	me.entry[5][0] = me.entry[4][0];
	me.entry[5][1] = me.entry[4][1];

	me.entry[4][0] = me.entry[3][0];
	me.entry[4][1] = me.entry[3][1];

	me.entry[3][0] = me.entry[2][0];
	me.entry[3][1] = me.entry[2][1];

	me.entry[2][0] = me.entry[1][0];
	me.entry[2][1] = me.entry[1][1];

	me.entry[1][0] = me.entry[0][0];
	me.entry[1][1] = me.entry[0][1];

	me.entry[0][0] = distance;
	me.entry[0][1] = velocity;
	},

	create_entry_box: func (distance) {

	var velocity = getprop("/fdm/jsbsim/velocities/vtrue-fps"); #Vrel for entry

	#6  markers for guidance box history 

	me.entry_box[5][0] = me.entry_box[4][0];
	me.entry_box[5][1] = me.entry_box[4][1];

	me.entry_box[4][0] = me.entry_box[3][0];
	me.entry_box[4][1] = me.entry_box[3][1];

	me.entry_box[3][0] = me.entry_box[2][0];
	me.entry_box[3][1] = me.entry_box[2][1];

	me.entry_box[2][0] = me.entry_box[1][0];
	me.entry_box[2][1] = me.entry_box[1][1];

	me.entry_box[1][0] = me.entry_box[0][0];
	me.entry_box[1][1] = me.entry_box[0][1];

	me.entry_box[0][0] = distance;
	me.entry_box[0][1] = velocity;
	},

};

# this is Vandenberg  we update later upon selection

landing_site.set_latlon(34.722, -120.567);


var update_entry_guidance =  func {

var pos = geo.aircraft_position();
var mm = getprop("/fdm/jsbsim/systems/dps/major-mode");

if (SpaceShuttle.bfs_in_control == 1)
	{
	mm = getprop("/fdm/jsbsim/systems/dps/major-mode-bfs");
	}

var course = pos.course_to(landing_site);
var v_eci = getprop("/fdm/jsbsim/velocities/eci-velocity-mag-fps");
var v_true_fps = getprop("/fdm/jsbsim/velocities/vtrue-fps");
var distance = pos.distance_to(landing_site);
var altitude = getprop("/position/altitude-ft");
var v_rel_fps = (distance - distance_last) /0.3048;
var drag_fps = getprop("fdm/jsbsim/systems/entry_guidance/aero-drag-deceleration-fts");
var drag_ratio = getprop("/fdm/jsbsim/systems/entry_guidance/drag-guidance-box");

setprop("/fdm/jsbsim/systems/entry_guidance/vrel-fps", v_rel_fps);
if (v_rel_fps > 0.0)
	{
	setprop("/fdm/jsbsim/systems/entry_guidance/vrel-sign", 1);
	}
else
	{
	setprop("/fdm/jsbsim/systems/entry_guidance/vrel-sign", -1);
	}

distance_last = distance;

distance = distance/ 1853.0;


setprop("/fdm/jsbsim/systems/entry_guidance/target-azimuth-deg", course);
setprop("/fdm/jsbsim/systems/entry_guidance/remaining-distance-nm", distance);


if (mm == 304)
	{
	var v_error = SpaceShuttle.get_entry_drag_deviation(v_true_fps, distance);
	#var v_error = SpaceShuttle.get_entry_drag_deviation(drag_fps, distance); #Delta drag done in xml
	setprop("/fdm/jsbsim/systems/entry_guidance/v-error-fps", v_error);

	trailer_set.update(distance);
	trailer_set.updatebox(drag_ratio * distance); #Guidance box
	roll_reversal_management();
	body_flap_management();

	#Trailer update speed goes to 15 seconds below 14000 ft/s (Entry traj 3) 
	if ((v_true_fps < 14000) and (trailer_set.time_limit == 29))
		{
		trailer_set.time_limit = 15;
		#trailer_set.update(distance);
		}

	#SB 81% at Mach 10 for Cm considerations (same SB logic than in TAEM guidance.nas)
	#DeadBand to keep the SB in a constant position
	var sb_state = getprop("/controls/shuttle/speedbrake");
	if ((v_true_fps < 10000) and (v_true_fps > 2500) and (sb_state < 0.75)) 
		{
		var sb_max = 0.80;

		if (getprop("/fdm/jsbsim/systems/ap/automatic-sb-control") == 1)	
			{
			if (sb_state > sb_max + 0.02) {SpaceShuttle.decrease_speedbrake();}
			else if (sb_state < sb_max - 0.02) {SpaceShuttle.increase_speedbrake();}
			}
		}


	# cease banking and alpha management in the transition to TAEM (Mid value, End of traj 5 between 50 and 70 Nm)
	#No bank, max L/D alpha at TAEM transition
	

	if (distance < 65.0) #or (v_true_fps < 3000) or (altitude < 90000))
		{
		if (getprop("/fdm/jsbsim/systems/ap/entry/taem-transit-init") == 0)
			{
			print("Preparing transition to TAEM guidance!");
			setprop("/fdm/jsbsim/systems/ap/entry/taem-transit-init",1);
			}
		}
	}
}


# manage roll reversals #################################################

var roll_reversal_management = func {

var current_bank = getprop("/orientation/roll-deg");
var roll_direction = getprop("/fdm/jsbsim/systems/ap/entry/roll-sign");
var v_true_fps = getprop("/fdm/jsbsim/velocities/vtrue-fps");

# if a roll reversal is on, we need to check whether to end it

if (getprop("/fdm/jsbsim/systems/ap/entry/roll-reversal-init") == 1)
	{
	var commanded_bank = getprop("/fdm/jsbsim/systems/ap/entry/reversal-bank-angle-target-deg");

	if (math.abs(current_bank - commanded_bank) < 5.0)
		{

		roll_direction = - roll_direction;
		setprop("/fdm/jsbsim/systems/ap/entry/roll-sign", roll_direction);
		setprop("/fdm/jsbsim/systems/ap/entry/roll-reversal-init", 0);
		print("Ending roll reversal!");
		return;
		}

	}


var delta_az = getprop("/fdm/jsbsim/systems/entry_guidance/delta-azimuth-deg");


var drag_bank = getprop("/fdm/jsbsim/systems/ap/entry/drag-bank-angle-target-deg");

if (getprop("/fdm/jsbsim/systems/ap/entry/roll-reversal-init") == 0)
{

#Roll reversal at Daz = 17 ° above mach 4 and 10 ° below

if (v_true_fps > 4000)
	{
	if (math.abs(delta_az) < 17.0) {return;}
	if (((delta_az > 17.0) and (roll_direction == 1)) or ((delta_az < -17.0) and (roll_direction == -1)))
		{
		
		setprop("/fdm/jsbsim/systems/ap/entry/reversal-bank-angle-target-deg", -current_bank);
		print("Initiating roll reversal!");
		setprop("/fdm/jsbsim/systems/ap/entry/roll-reversal-init", 1);
		}
	}

else 
	{
	if (math.abs(delta_az) < 10.0) {return;}
	if (((delta_az > 10.0) and (roll_direction == 1)) or ((delta_az < -10.0) and (roll_direction == -1)))
		{
		setprop("/fdm/jsbsim/systems/ap/entry/reversal-bank-angle-target-deg", -current_bank);
		print("Initiating roll reversal!");
		setprop("/fdm/jsbsim/systems/ap/entry/roll-reversal-init", 1);
		}
	}
}


}


# manage body flap trim #################################################

var body_flap_management = func {

var q_bar = getprop("/fdm/jsbsim/aero/qbar-psf");
var pod_pitch_up = getprop("/fdm/jsbsim/systems/rcs/pod2-up-raw-pitch");
var pod_pitch_down = getprop("/fdm/jsbsim/systems/rcs/pod2-down-raw-pitch");



if (getprop("/fdm/jsbsim/systems/ap/automatic-bodyflap-control") == 0) {return;}


var elevator_trim = getprop("/fdm/jsbsim/fcs/elevator-pos-deg");
var altitude = getprop("/position/altitude-ft");
var roll_velocity_rad = getprop("/fdm/jsbsim/velocities/p-rad_sec");
var roll_reversal = getprop("/fdm/jsbsim/systems/ap/entry/roll-reversal-init");


#For q bar below 20 in ops 3, Body flaps trims the RCS pitch up/down (based on Up/Down firing) to alleviate RCS pitch load ( and excessive fuel consumption)
#Then above q bar of 20 , Body flaps trim the elevons when Pitch Jets are deactivated

#Q bar 0.5, start of aerosurfaces trim
if (q_bar < 0.5) {return;}

else if ((q_bar > 0.5) and (q_bar < 20)) #Pitch jets trimming outside roll reversal to avoid BF oscillations
	{
	#if (roll_velocity_rad < 0.0087)
	if (roll_reversal == 0)
		{
		if (pod_pitch_up > 0) {SpaceShuttle.bodyflap_up();}
		else if (pod_pitch_down > 0) {SpaceShuttle.bodyflap_down();}
		}
	else {return;}
	}
else
	{
	if (altitude > 10000) #Elevons trimming
		{ 
		if (elevator_trim < -5.0) {SpaceShuttle.bodyflap_up();}
		else if (elevator_trim > 3.0) {SpaceShuttle.bodyflap_down();}
		}

	#Bodyflap in Trail position in final (0° on final // 0 of CmBF) // Neutral Cl/Cd/Cm BF 
	else if (altitude < 10000) 
		{
		var bodyflap_state = getprop("/controls/shuttle/bodyflap-pos-rad");
		if (bodyflap_state != 0.0) 
			{
			bodyflap_state = 0.0;
			setprop("/controls/shuttle/bodyflap-pos-rad", bodyflap_state);
			SpaceShuttle.callout.make("Body Flaps Trail.", "info");
			return;
			}
		}
	}
}


var create_radius_set = func {

var base = geo.Coord.new();
var dist = getprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/EI-radius") * 1853.0;
var point = [];

var npoints = 20;

var course = 330;
var step = (course -180.0)/(npoints-1);

for (var i = 0; i< npoints; i=i+1)
	{
	base.set_xyz(landing_site.x(), landing_site.y(), landing_site.z());
	base.apply_course_distance(course - i*step, dist);
	point = [SpaceShuttle.lon_to_x(base.lon()), SpaceShuttle.lat_to_y(base.lat())];
	append(radius_set, point);
	}


}

var compute_entry_guidance_target = func {

var pos = geo.aircraft_position();

var distance = pos.distance_to(landing_site)/ 1853.0;
var course = pos.course_to(landing_site);

setprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/site-dist", 0.0);


# now we compute the desired entry interface
# make that 4100 miles to site

setsize(radius_set, 0);
create_radius_set();

setprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/site-dist", distance);
setprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/site-string", "active");


var mode_string = getprop("/sim/gui/dialogs/SpaceShuttle/entry_guidance/entry-mode");

if (mode_string == "normal")
	{
	setprop("/fdm/jsbsim/systems/entry_guidance/guidance-mode",1);
	}
else if (mode_string == "TAL")
	{
	setprop("/fdm/jsbsim/systems/entry_guidance/guidance-mode",2);
	}
else if (mode_string == "RTLS")
	{
	SpaceShuttle.init_rtls();
	}

entry_guidance_available = 1;

# usually we would compute a TAEM guidance target at TAEM interface, but if the Shuttle is
# initialized at TAEM interface, no target is selected yet, so if distance to site is
# within TAEM range, we compute it now

if ((distance < 100.0) and (mode_string != "RTLS")){SpaceShuttle.compute_TAEM_guidance_targets();}


}



