#Thorsten 2015 // Gingin 2020

var update_vtraj_loop_flag = 0;
var traj_display_flag = 1;

var vertical_display_size = 512;
var horizontal_display_size = 512;

var traj_data = [];
var trajTAL_data = [];
var limit1_data = [];
var limit2_data = [];

var TAEM_nominal_trajectory = [];
var entry_nominal_trajectory = [];
var entry_nominal_trajectory_drag = [];

var sym_shuttle_asc = {};
var trajectory = {};


var ascent_predictors = [[0.0, 0.0, 0.0], [0.0,0.0, 0.0]];










var update_ascent_predictors = func {

var altitude = getprop("/position/altitude-ft");
var vspeed = getprop("/fdm/jsbsim/velocities/v-down-fps");

if (traj_display_flag == 1) #Stage 1
	{
	var speed = getprop("/fdm/jsbsim/velocities/ned-velocity-mag-fps");
	var time_base = 20.0;
	}
else if (traj_display_flag > 2) #OPS 3
	{
	var speed = getprop("/fdm/jsbsim/velocities/ned-velocity-mag-fps");
	var time_base = 30.0;
	}
else #Stage2 / PRTLS 
	{
	var speed = getprop("/fdm/jsbsim/velocities/eci-velocity-mag-fps");
	var time_base = 30.0;
	}

var pitch = getprop("/orientation/pitch-deg") * math.pi/180.0;
var roll = getprop("/orientation/roll-deg") * math.pi/180.0;

var ops = getprop("/fdm/jsbsim/systems/dps/ops");

if ((traj_display_flag == 2) or (ops == 6))
	{
	# SSME engines are pitched
	pitch = pitch - 16.0 * math.pi/180.0 * math.cos(roll); 
	}

var acc = getprop("/fdm/jsbsim/systems/navigation/acceleration-x") ;
var gravity = getprop("/fdm/jsbsim/accelerations/gravity-ft_sec2");
var centrifugal = getprop("/fdm/jsbsim/accelerations/a-centrifugal-ft_sec2");

var acc_vert = acc * math.sin(pitch) - gravity + centrifugal;
var acc_horiz = acc * math.cos(pitch);

var acc_eff = math.sqrt(acc_vert * acc_vert + acc_horiz * acc_horiz);

ascent_predictors[0][0] = speed + time_base * acc_eff;
ascent_predictors[0][1] = altitude - time_base * vspeed + 0.5 * acc_vert * time_base * time_base;
ascent_predictors[0][2] = time_base * acc_horiz;

ascent_predictors[1][0] = speed + 2.0 * time_base * acc_eff;
ascent_predictors[1][1] = altitude - 2.0 * time_base * vspeed + 2.0 * acc_vert * time_base * time_base;
ascent_predictors[1][2] = 2.0 * time_base * acc_horiz;
}




var ascent_traj_update_set = func {

var velocity = getprop("/fdm/jsbsim/velocities/vtrue-fps"); #Entry boundaries based on Vrel
var entry_range = getprop("/fdm/jsbsim/systems/entry_guidance/remaining-distance-nm"); #OPS 304
var range = getprop("/fdm/jsbsim/systems/taem-guidance/distance-to-runway-nm");# OPS 305

if (traj_display_flag == 0)
	{
	fill_traj1_data();
	traj_display_flag = 1;
	}


if (traj_display_flag == 1)
	{
	if (getprop("/controls/shuttle/SRB-static-model") == 0) # we have separated the SRBs
		{
		fill_traj2_data();
		#fill_traj_TAL_data();   # TAL trajectory
		traj_display_flag = 2;
		}
	}
if (traj_display_flag == 2)
	{
	#if (getprop("/fdm/jsbsim/systems/entry_guidance/guidance-mode") > 0) # we're preparing for de-orbit
	if (getprop("/fdm/jsbsim/systems/dps/ops") == 3)
		{
		fill_entry1_data();
		traj_display_flag = 3;
		}

	}
if (traj_display_flag == 3)
	{
	if (velocity < 17000.0)  #Warning : Some OI change from traj 1 to 2 at 19000 kfts (latest one at 17kfts// different shapes)
		{
		fill_entry2_data();
		traj_display_flag = 4;
		}
	}

if (traj_display_flag == 4)
	{
	if ((velocity < 14000.0) or (entry_range < 425))
		{
		fill_entry3_data();
		traj_display_flag = 5;
		}
	}

if (traj_display_flag == 5)
	{
	if ((velocity < 10500.0) or (entry_range < 315))
		{
		fill_entry4_data();
		traj_display_flag = 6;
		}
	}

if (traj_display_flag == 6)
	{
	if ((velocity < 6000.0) or (entry_range < 145))
		{
		fill_entry5_data();
		traj_display_flag = 7;
		}
	}



if (traj_display_flag == 8) 
	{
	if ((range > 0.0) and (range < 20.0))
		{
		fill_vert_sit2_nom_data();
		fill_vert_sit2_SB_data();
		fill_vert_sit2_maxLD_data();
		traj_display_flag = 9;
		}
	}

}


var rtls_traj_update_set = func {

var velocity = getprop("/fdm/jsbsim/velocities/eci-velocity-mag-fps");

#print ("Updating RTLS traj set");


fill_rtls2_data();
traj_display_flag = 2;

}


var ascent_traj_update_velocity = func {

if (traj_display_flag == 1)
	{
	return getprop("/fdm/jsbsim/velocities/ned-velocity-mag-fps");
	}
else
	{
	return getprop("/fdm/jsbsim/velocities/eci-velocity-mag-fps");
	}

var latitude = getprop("/position/latitude-deg");
var velocity = getprop("/fdm/jsbsim/velocities/eci-velocity-mag-fps");
var earth_rotation = 1420.0 * math.cos(latitude);



# the TRAJ 1 display shows relative rather than inertial velocity
if (traj_display_flag == 1)
	{velocity = math.sqrt(math.abs(velocity * velocity - earth_rotation * earth_rotation));}

return velocity;

}







# converter functions for trajectory data into the display format

var parameter_to_x = func (par, display) {

if (display == 1)
	{
	return (par / 5000.0 * 0.8 + 0.1) * 512.0;
	}
else if (display == 2)
	{
	return ((par - 5000.0) / 21000.0 * 0.8 + 0.1) * 512.0;
	}
else if (display == 3)
	{
	#Entry traj1
	##test with 17 kfts limitation OI 34// Nominal line matching 3rd line (3800 / 700)
	#Above 3800 Nm, original quadratic function is better
	#Below, slightly modified one to take into account in sim Shuttle entry dps scale and boundaries above mach 17

	if (par > 3800) {return (math.pow(par, 2) * -0.00005111111 + par * 0.38844444 - 228.0444444);} #Quadratic (C + C1*D + C2*D²) C -228.04444 
	else {return (math.pow(par, 2) * -0.000037792207 + par * 0.32866883 - 183.0636);} # C = 200

	}
else if (display == 4)
	{
	#Entry traj2
	return (math.pow(par,2) * - 0.00037578 + par * 1.0854212 -302.969942); #FG tunned

	}
else if (display == 5)
	{
	#Entry traj3
	return (math.pow(par,2) * -0.00143805 + par * 2.4982 - 585.265);
	}
else if (display == 6)
	{
	#Entry traj4
	return (math.pow(par,2) * -0.003597 + par * 3.49365 - 362.285714);
	}
else if (display == 7)
	{
	#Entry traj5
	return (math.pow(par,2) * -0.015 + par * 6.425 - 204.75); #170 130 50Nm
	}
else if (display == 8)
	{
	return (6.23501 * par - 32.63);
	}
else if (display == 9)
	{
	#Vert traj 2
	return (20 * par - 61);
	}
else if (display == 10)
	{
	return ((par + 8000.0)/18000. * 0.8 + 0.1) * 512.0;
	}
}

var parameter_to_y = func (par, display) {

if (display == 1)
	{
	return 512.0 - (par / 170000.0 * 0.6 + 0.2) * 512.0;
	}
else if (display == 2)
	{
	return 512.0 - ((par - 140000.0) / 385000.0 * 0.6 + 0.2) * 512.0;
	}
else if (display == 3)
	{
	#return 512.0 - ((par - 18500.0) / 7500.0 * 0.6 + 0.2) * 512.0;
	return (-0.03728 * par + 966.857 + 32.7);
	}
else if (display == 4)
	{
	#return 512.0 - ((par - 15800.0) / 2700.0 * 0.6 + 0.2) * 512.0;
	return (-0.089333 * par + 1578.6666 + 32.7);
	}
else if (display == 5)
	{
	#return 512.0 - ((par - 10000.0) / 5800.0 * 0.6 + 0.2) * 512.0;
	return (-0.07785 * par + 1150 + 32.7);
	}
else if (display == 6)
	{
	#return 512.0 - ((par - 5500.0) / 4500.0 * 0.6 + 0.2) * 512.0;
	return (-0.0593 * par + 689 + 32.7);
	}
else if (display == 7)
	{
	#return 512.0 - ((par - 4000.0) / 1500.0 * 0.6 + 0.2) * 512.0;
	return (-0.07828 * par + 535.714 + 32.7);
	}
else if (display == 8)
	{
	#return 512.0 - ((par - 30000.0) / 55000.0 * 0.52 + 0.2) * 512.0;
	#return (-0.002914 * par + 405.42857 + 32.7); #100kft
	return (-0.003375 * par + 419.25 + 32.7); #78kft
	}
else if (display == 9)
	{
	#return 512.0 - ((par - 8000.0) / 22000.0 * 0.52 + 0.2) * 512.0;
	return (-0.0116 * par + 406 + 32.7); 
	}
else if (display == 10)
	{
	return 512.0 - ((par - 150000)/450000. * 0.52 + 0.2) * 512.0;
	}
}


# trajectory data points, obtained from test flights - in reality, these would be mission-specific and 
# they may change in the future

var fill_traj1_data = func {


setsize(traj_data,0);

if (getprop("/mission/ascent-traj-stage1/section-defined"))
	{
	var n_points = getprop("/mission/ascent-traj-stage1/num-points");

	print ("Reading i-loaded stage 1 trajectory display data.");

	for (var i=0; i< n_points; i=i+1)
		{
		var x = getprop("/mission/ascent-traj-stage1/point["~i~"]/x");
		var y = getprop("/mission/ascent-traj-stage1/point["~i~"]/y");
		append(traj_data, [x,y]);
	
		}

	}
else
	{

	#print ("Using default stage 1 trajectory display data.");

	var point = [0.0, 0.0];
	append(traj_data, point);

	var point = [300.0, 2000.0];
	append(traj_data, point);

	var point = [600.0, 6700.0];
	append(traj_data, point);

	var point = [900.0, 15000.0];
	append(traj_data, point);

	var point = [1000.0, 19000.0];
	append(traj_data, point);

	var point = [1350.0, 33700.0];
	append(traj_data, point);

	var point = [1560.0, 41200.0];
	append(traj_data, point);

	var point = [2100.0, 60000.0];
	append(traj_data, point);

	var point = [2400.0, 70000.0];
	append(traj_data, point);

	var point = [2700.0, 79000.0];
	append(traj_data, point);

	var point = [3000.0, 90000.0];
	append(traj_data, point);

	var point = [3300.0, 100000.0];
	append(traj_data, point);

	var point = [3600.0, 110000.0];
	append(traj_data, point);

	var point = [3900.0, 120000.0];
	append(traj_data, point);

	var point = [4200.0, 130000.0];
	append(traj_data, point);

	var point = [4300.0, 140000.0];
	append(traj_data, point);

	var point = [4500.0, 155000.0];
	append(traj_data, point);
	}

for (i=0; i< size(traj_data); i=i+1)
	{
	traj_data[i][0] = parameter_to_x(traj_data[i][0], 1);
	traj_data[i][1] = parameter_to_y(traj_data[i][1], 1); 
	}

}


var fill_traj2_data = func {

var point = [];
setsize(traj_data,0);


if (getprop("/mission/ascent-traj-stage2/section-defined"))
	{
	var n_points = getprop("/mission/ascent-traj-stage2/num-points");

	print ("Reading i-loaded stage 2 trajectory display data.");

	for (var i=0; i< n_points; i=i+1)
		{
		var x = getprop("/mission/ascent-traj-stage2/point["~i~"]/x");
		var y = getprop("/mission/ascent-traj-stage2/point["~i~"]/y");
		append(traj_data, [x,y]);
	
		}

	}
else
	{


	point = [5400.0, 160000.0];
	append(traj_data, point);

	point = [6000.0, 220000.0];
	append(traj_data, point);

	point = [7000.0, 280000.0];
	append(traj_data, point);

	point = [8000.0, 310000.0];
	append(traj_data, point);

	point = [9000.0, 333000.0];
	append(traj_data, point);

	point = [10000.0, 342000.0];
	append(traj_data, point);

	point = [12000.0, 350000.0];
	append(traj_data, point);

	point = [14000.0, 350000.0];
	append(traj_data, point);

	point = [16000.0, 345000.0];
	append(traj_data, point);

	point = [18000.0, 340000.0];
	append(traj_data, point);

	point = [20000.0, 335000.0];
	append(traj_data, point);

	point = [22000.0, 335000.0];
	append(traj_data, point);

	point = [24000.0, 337000.0];
	append(traj_data, point);

	point = [25000.0, 340000.0];
	append(traj_data, point);

	point = [25800.0, 343000.0];
	append(traj_data, point);
	}


for (i=0; i< size(traj_data); i=i+1)
	{
	traj_data[i][0] = parameter_to_x(traj_data[i][0], 2);
	traj_data[i][1] = parameter_to_y(traj_data[i][1], 2); 
	}

}


#Stage 2 TAL trajectory (above nominal, past ATO boundary, it ends earlier MECO < 25kfts)

var fill_traj_TAL_data = func {

var point = [];
setsize(trajTAL_data,0);


if (getprop("/mission/ascent-traj-stage2/section-defined"))
	{

	#If custom stage 2 shape, no TAL traj
	point = [0.0, 0.0];
	append(trajTAL_data, point);

	}
else
	{

	

	point = [14000.0, 370000.0];
	append(trajTAL_data, point);

	point = [16000.0, 365000.0];
	append(trajTAL_data, point);

	point = [18000.0, 360000.0];
	append(trajTAL_data, point);

	point = [20000.0, 358000.0];
	append(trajTAL_data, point);

	point = [22000.0, 357000.0];
	append(trajTAL_data, point);

	point = [24000.0, 356000.0];
	append(trajTAL_data, point);

	point = [25000.0, 356000.0];
	append(trajTAL_data, point);

	
	}


for (i=0; i< size(trajTAL_data); i=i+1)
	{
	trajTAL_data[i][0] = parameter_to_x(trajTAL_data[i][0], 2);
	trajTAL_data[i][1] = parameter_to_y(trajTAL_data[i][1], 2); 
	}

}

var fill_rtls2_data = func {

#var point = [];

setsize(traj_data,0);

var point = [4400, 160000.0];
append(traj_data, point);

point = [5000, 220000.0];
append(traj_data, point);

point = [6000, 280000.0];
append(traj_data, point);

point = [7000, 315000.0];
append(traj_data, point);

point = [8000, 333000.0];
append(traj_data, point);

point = [9000, 342000.0];
append(traj_data, point);

point = [10000, 350000.0];
append(traj_data, point);


#print ("Processing traj data.");

for (i=0; i< size(traj_data); i=i+1)
	{
	traj_data[i][0] = parameter_to_x(traj_data[i][0], 10);
	traj_data[i][1] = parameter_to_y(traj_data[i][1], 10); 
	}

setsize(limit1_data,0);

point = [6000.0, 400000.0];
append(limit1_data, point);

point = [5000.0, 395000.0];
append(limit1_data, point);

point = [4000.0, 380000.0];
append(limit1_data, point);

point = [3000.0, 365000.0];
append(limit1_data, point);

point = [2000.0, 350000.0];
append(limit1_data, point);

point = [0.0, 320000.0];
append(limit1_data, point);

for (i=0; i< size(limit1_data); i=i+1)
	{
	limit1_data[i][0] = parameter_to_x(limit1_data[i][0], 10);
	limit1_data[i][1] = parameter_to_y(limit1_data[i][1], 10); 
	}

setsize(limit2_data,0);

point = [3600.0, 190000.0];
append(limit2_data, point);

point = [3800.0, 265000.0];
append(limit2_data, point);

point = [4140.0, 296000.0];
append(limit2_data, point);

point = [0.0, 267000.0];
append(limit2_data, point);

point = [-2000.0, 240000.0];
append(limit2_data, point);

point = [-4000.0, 250000.0];
append(limit2_data, point);

point = [-5000.0, 255000.0];
append(limit2_data, point);

point = [-6000.0, 263000.0];
append(limit2_data, point);

point = [-7300.0, 265000.0];
append(limit2_data, point);

point = [-7350.0, 266000.0];
append(limit2_data, point);

for (i=0; i< size(limit2_data); i=i+1)
	{
	limit2_data[i][0] = parameter_to_x(limit2_data[i][0], 10);
	limit2_data[i][1] = parameter_to_y(limit2_data[i][1], 10); 
	}

}









#Nominal path for scale fine tunning

var fill_entry1_data = func {

var point = [];
setsize(traj_data,0);




#Nominal path (third line)

#point = [3700, 25500];
#append(traj_data, point);

#point = [3300, 25000];
#append(traj_data, point);

#point = [2910, 24500];
#append(traj_data, point);

point = [3700, 24000];
append(traj_data, point);#2640

point = [2390, 23500];
append(traj_data, point);

point = [2160, 23000];
append(traj_data, point);

point = [1990, 22500];
append(traj_data, point);

point = [1800, 22000];
append(traj_data, point);

point = [1650, 21500];
append(traj_data, point);

point = [1520, 21000];
append(traj_data, point);

point = [1400, 20500];
append(traj_data, point);

point = [1300, 20000];
append(traj_data, point);
   
point = [1200, 19500];
append(traj_data, point);

point = [1120, 19000];
append(traj_data, point);

point = [1040, 18500];
append(traj_data, point);

point = [970, 18000];
append(traj_data, point);

point = [910, 17500];
append(traj_data, point);

point = [750, 17000];
append(traj_data, point);#861

#point = [750, 16000];
#append(traj_data, point);










for (i=0; i< size(traj_data); i=i+1)
	{
	traj_data[i][0] = parameter_to_x(traj_data[i][0], 3);
	traj_data[i][1] = parameter_to_y(traj_data[i][1], 3); 
	}

}


var fill_entry2_data = func {

var point = [];
setsize(traj_data,0);

#Nominal path (second line)


#point = [1300, 17500];
#append(traj_data, point);

point = [1300, 17000];
append(traj_data, point);#861

point = [830, 16750];
append(traj_data, point);

point = [810, 16500];
append(traj_data, point);

point = [780, 16250];
append(traj_data, point);

point = [760, 16000];
append(traj_data, point);

point = [740, 15750];
append(traj_data, point);

point = [710, 15500];
append(traj_data, point);

point = [700, 15250];
append(traj_data, point);

point = [680, 15000];
append(traj_data, point);

point = [660, 14750];
append(traj_data, point);

point = [640, 14500];
append(traj_data, point);

point = [620, 14250];
append(traj_data, point);

point = [425, 14000];
append(traj_data, point);#600

#point = [425, 13500];
#append(traj_data, point);










for (i=0; i< size(traj_data); i=i+1)
	{
	traj_data[i][0] = parameter_to_x(traj_data[i][0], 4);
	traj_data[i][1] = parameter_to_y(traj_data[i][1], 4); 
	}

}


var fill_entry3_data = func {

var point = [];
setsize(traj_data,0);


#Nominal path (second line)

#point = [800, 14500];
#append(traj_data, point);

point = [800, 14000];
append(traj_data, point);#600

point = [590, 13750];
append(traj_data, point);

point = [570, 13500];
append(traj_data, point);

point = [550, 13250];
append(traj_data, point);

point = [540, 13000];
append(traj_data, point);

point = [520, 12750];
append(traj_data, point);

point = [500, 12500];
append(traj_data, point);

point = [490, 12250];
append(traj_data, point);

point = [480, 12000];
append(traj_data, point);

point = [460, 11750];
append(traj_data, point);

point = [450, 11500];
append(traj_data, point);

point = [430, 11250];
append(traj_data, point);

point = [420, 11000];
append(traj_data, point);

point = [410, 10750];
append(traj_data, point);

point = [315, 10500];
append(traj_data, point);#400

#point = [315, 10000];
#append(traj_data, point);







for (i=0; i< size(traj_data); i=i+1)
	{
	traj_data[i][0] = parameter_to_x(traj_data[i][0], 5);
	traj_data[i][1] = parameter_to_y(traj_data[i][1], 5); 
	}

}


var fill_entry4_data = func {

var point = [];
setsize(traj_data,0);

#point = [480, 10750];
#append(traj_data, point);

point = [480, 10500];
append(traj_data, point); #390

point = [380, 10275];
append(traj_data, point);

point = [365, 10000];
append(traj_data, point);

point = [350, 9750];
append(traj_data, point);

point = [340, 9500];
append(traj_data, point);

point = [330, 9250];
append(traj_data, point);

point = [320, 9000];
append(traj_data, point);

point = [310, 8750];
append(traj_data, point);

point = [290, 8500];
append(traj_data, point);

point = [280, 8250];
append(traj_data, point);

point = [270, 8000];
append(traj_data, point);

point = [255, 7750];
append(traj_data, point);

point = [245, 7500];
append(traj_data, point);

point = [230, 7250];
append(traj_data, point);

point = [220, 7000];
append(traj_data, point);

point = [210, 6750];
append(traj_data, point);

point = [200, 6500];
append(traj_data, point);

point = [145, 6000];
append(traj_data, point); #180

#point = [145, 5800];
#append(traj_data, point);



for (i=0; i< size(traj_data); i=i+1)
	{
	traj_data[i][0] = parameter_to_x(traj_data[i][0], 6);
	traj_data[i][1] = parameter_to_y(traj_data[i][1], 6); 
	}

}


var fill_entry5_data = func {

var point = [];
setsize(traj_data,0);

#╗point = [220, 6500];
#append(traj_data, point);


point = [180, 6000]; #180
append(traj_data, point);

point = [170, 5800];
append(traj_data, point);

#point = [160, 5700];
#append(traj_data, point);

#point = [150, 5460];
#append(traj_data, point);

#point = [140, 5220];
#append(traj_data, point);

point = [130, 4950];
append(traj_data, point);

#point = [120, 4710];
#append(traj_data, point);

point = [110, 4410];
append(traj_data, point);

point = [100, 4100];
append(traj_data, point);

point = [90, 3800];
append(traj_data, point);

point = [80, 3520];
append(traj_data, point);

point = [70, 3210];
append(traj_data, point);


point = [60, 2850];
 append(traj_data, point);

point = [50, 2500];
append(traj_data, point);



for (i=0; i< size(traj_data); i=i+1)
	{
	traj_data[i][0] = parameter_to_x(traj_data[i][0], 7);
	traj_data[i][1] = parameter_to_y(traj_data[i][1], 7); 
	}

}


var fill_vert_sit1_nom_data_test = func {

var point = [];
setsize(traj_data,0);



point = [58, 78000.0];
append(traj_data, point);





point = [16.3, 30000.0];
append(traj_data, point);

point = [10.0, 30000.0];
append(traj_data, point);








for (i=0; i< size(traj_data); i=i+1)
	{
	traj_data[i][0] = parameter_to_x(traj_data[i][0], 8);
	traj_data[i][1] = parameter_to_y(traj_data[i][1], 8); 
	}

}

var fill_vert_sit1_nom_data = func {

var point = [];
setsize(traj_data,0);

point = [70, 90000.0];
append(traj_data, point);

point = [60, 80000.0];
append(traj_data, point);

point = [58, 78000.0];
append(traj_data, point);

point = [55.0, 76000.0];
append(traj_data, point);

point = [50.0, 74000.0];
append(traj_data, point);

point = [45.0, 71000.0];
append(traj_data, point);

point = [42.0, 69000.0];
append(traj_data, point);

point = [40.0, 67000.0];
append(traj_data, point);

point = [35.0, 61000.0];
append(traj_data, point);

point = [30.0, 54000.0];
append(traj_data, point);

point = [25.0, 46000.0];
append(traj_data, point);

#HAC 270 °
point = [20.0, 37000.0];
append(traj_data, point);

point = [16.3, 30000.0];
append(traj_data, point);

point = [12.0, 30000.0];
append(traj_data, point);








for (i=0; i< size(traj_data); i=i+1)
	{
	traj_data[i][0] = parameter_to_x(traj_data[i][0], 8);
	traj_data[i][1] = parameter_to_y(traj_data[i][1], 8); 
	}

}


var fill_vert_sit1_SB_data = func {

var point = [];
setsize(limit1_data,0);

point = [86.0, 87000.0];
append(limit1_data, point);

point = [66.0, 83000.0];
append(limit1_data, point);

point = [46.0, 69000.0];
append(limit1_data, point);

point = [26.0, 49000.0];
append(limit1_data, point);

point = [16.0, 34000.0];
append(limit1_data, point);

for (i=0; i< size(limit1_data); i=i+1)
	{
	limit1_data[i][0] = parameter_to_x(limit1_data[i][0], 8);
	limit1_data[i][1] = parameter_to_y(limit1_data[i][1], 8); 
	}

}

var fill_vert_sit1_maxLD_data = func {

var point = [];
setsize(limit2_data,0);


point = [89.0, 80000.0];
append(limit2_data, point);

point = [70.0, 68000.0];
append(limit2_data, point);

point = [48.0, 50000.0];
append(limit2_data, point);

point = [35.0, 40000.0];
append(limit2_data, point);

point = [25.0, 30000.0];
append(limit2_data, point);

for (i=0; i< size(limit2_data); i=i+1)
	{
	limit2_data[i][0] = parameter_to_x(limit2_data[i][0], 8);
	limit2_data[i][1] = parameter_to_y(limit2_data[i][1], 8); 
	}

}


var fill_vert_sit2_nom_data = func {

var point = [];
setsize(traj_data,0);

#point = [23, 30000.0];
#append(traj_data, point);

point = [16.3, 30000.0];
append(traj_data, point);

point = [15, 27000.0];
append(traj_data, point);

#90 ° HAC
point = [12, 21000.0];
append(traj_data, point);

#MLS
point = [10.0, 17000.0];
append(traj_data, point);

point = [9.0, 15000.0];
append(traj_data, point);

point = [8.0, 13000.0];
append(traj_data, point);

#End of Sit Vert 2 (Limit left)
point = [7, 11000.0];
append(traj_data, point);

point = [6, 9000.0];
append(traj_data, point);

point = [5, 7500.0];
append(traj_data, point);

point = [4, 5500.0];
append(traj_data, point);

#point = [3, 3400.0];
append(traj_data, point);

#GS Flag below 1500 QFE
point = [1.9, 1500.0];
append(traj_data, point);



for (i=0; i< size(traj_data); i=i+1)
	{
	traj_data[i][0] = parameter_to_x(traj_data[i][0], 9);
	traj_data[i][1] = parameter_to_y(traj_data[i][1], 9); 
	}

}


var fill_vert_sit2_SB_data = func {

var point = [];
setsize(limit1_data,0);

point = [15.0, 30000.0];
append(limit1_data, point);

point = [10.0, 19300.0];
append(limit1_data, point);

point = [5.0, 9200.0];
append(limit1_data, point);


for (i=0; i< size(limit1_data); i=i+1)
	{
	limit1_data[i][0] = parameter_to_x(limit1_data[i][0], 9);
	limit1_data[i][1] = parameter_to_y(limit1_data[i][1], 9); 
	}

}

var fill_vert_sit2_maxLD_data = func {

var point = [];
setsize(limit2_data,0);


point = [25.3, 30000.0];
append(limit2_data, point);

point = [20.0, 24300.0];
append(limit2_data, point);

point = [15.0, 18000.0];
append(limit2_data, point);

point = [10.0, 12000.0];
append(limit2_data, point);

point = [5.6, 8000.0];
append(limit2_data, point);

for (i=0; i< size(limit2_data); i=i+1)
	{
	limit2_data[i][0] = parameter_to_x(limit2_data[i][0], 9);
	limit2_data[i][1] = parameter_to_y(limit2_data[i][1], 9); 
	}

}

var plot_traj = func (trajectory) {


var plot = trajectory.createChild("path", "data")
                                   .setStrokeLineWidth(2)
                                   .setColor(dps_r, dps_g, dps_b) #Same color than hard coded lines
                                   .moveTo(traj_data[0][0],traj_data[0][1]); 

		for (var i = 1; i< (size(traj_data)-1); i=i+1)
			{
			var set = traj_data[i+1];
			plot.lineTo(set[0], set[1]);	
			}

}

#Data for Path deviation
#AP driven by delta drag bias mainly, path deviation helps as a correction factor if very low in energy or close to thermal/G's boundaries
var fill_entry_nom_data = func {

var point = [];

#point = [4000, 25000];
#append(entry_nominal_trajectory, point);

#point = [3300, 24510];
#append(entry_nominal_trajectory, point);

#point = [2910, 24400];
#append(entry_nominal_trajectory, point);

point = [2640, 24000];
append(entry_nominal_trajectory, point);

point = [2390, 23500];
append(entry_nominal_trajectory, point);


#First part of entry handled only by drag bias to catch the path firmly( up to 23kfps)

point = [2160, 23000];
append(entry_nominal_trajectory, point);

#point = [1990, 22500];
#append(entry_nominal_trajectory, point);

point = [1800, 22000];
append(entry_nominal_trajectory, point);

#point = [1650, 21500];
#append(entry_nominal_trajectory, point);

point = [1520, 21000];
append(entry_nominal_trajectory, point);

#point = [1400, 20500];
#append(entry_nominal_trajectory, point);

point = [1300, 20000];
append(entry_nominal_trajectory, point);
   
#point = [1200, 19500];
#append(entry_nominal_trajectory, point);

point = [1120, 19000];
append(entry_nominal_trajectory, point);

#point = [1040, 18500];
#append(entry_nominal_trajectory, point);

point = [970, 18000];
append(entry_nominal_trajectory, point);

#point = [910, 17500];
#append(entry_nominal_trajectory, point);

point = [861, 17000];
append(entry_nominal_trajectory, point);

#point = [830, 16750];
#append(entry_nominal_trajectory, point);

#point = [810, 16500];
#append(entry_nominal_trajectory, point);

#point = [780, 16250];
#append(entry_nominal_trajectory, point);

point = [760, 16000];
append(entry_nominal_trajectory, point);

#point = [740, 15750];
#append(entry_nominal_trajectory, point);

#point = [710, 15500];
#append(entry_nominal_trajectory, point);

#point = [700, 15250];
#append(entry_nominal_trajectory, point);

point = [680, 15000];
append(entry_nominal_trajectory, point);

#point = [660, 14750];
#append(entry_nominal_trajectory, point);

#point = [640, 14500];
#append(entry_nominal_trajectory, point);

#point = [620, 14250];
#append(entry_nominal_trajectory, point);

point = [600, 14000];
append(entry_nominal_trajectory, point);

#point = [590, 13750];
#append(entry_nominal_trajectory, point);

#point = [570, 13500];
#append(entry_nominal_trajectory, point);

#point = [550, 13250];
#append(entry_nominal_trajectory, point);

point = [540, 13000];
append(entry_nominal_trajectory, point);

#point = [520, 12750];
#append(entry_nominal_trajectory, point);

#point = [500, 12500];
#append(entry_nominal_trajectory, point);

#point = [490, 12250];
#append(entry_nominal_trajectory, point);

point = [480, 12000];
append(entry_nominal_trajectory, point);

#point = [460, 11750];
#append(entry_nominal_trajectory, point);

#point = [450, 11500];
#append(entry_nominal_trajectory, point);

#point = [430, 11250];
#append(entry_nominal_trajectory, point);

point = [420, 11000];
append(entry_nominal_trajectory, point);

#point = [410, 10750];
#append(entry_nominal_trajectory, point);

point = [400, 10500];
append(entry_nominal_trajectory, point);

#point = [380, 10275];
#append(entry_nominal_trajectory, point);

point = [365, 10000];
append(entry_nominal_trajectory, point);

#point = [350, 9750];
#append(entry_nominal_trajectory, point);

#point = [340, 9500];
#append(entry_nominal_trajectory, point);

#point = [330, 9250];
#append(entry_nominal_trajectory, point);

point = [320, 9000];
append(entry_nominal_trajectory, point);

#point = [310, 8750];
#append(entry_nominal_trajectory, point);

point = [290, 8500];
append(entry_nominal_trajectory, point);

#point = [280, 8250];
#append(entry_nominal_trajectory, point);

point = [270, 8000];
append(entry_nominal_trajectory, point);

#point = [255, 7750];
#append(entry_nominal_trajectory, point);

point = [245, 7500];
append(entry_nominal_trajectory, point);

#point = [230, 7250];
#append(entry_nominal_trajectory, point);

point = [220, 7000];
append(entry_nominal_trajectory, point);

#point = [210, 6750];
#append(entry_nominal_trajectory, point);

#point = [200, 6500];
#append(entry_nominal_trajectory, point);


point = [180, 6000];
append(entry_nominal_trajectory, point);

#point = [170, 5800];
#append(entry_nominal_trajectory, point);

#point = [160, 5700];
#append(entry_nominal_trajectory, point);

point = [150, 5460];
append(entry_nominal_trajectory, point);

#point = [140, 5220];
append(entry_nominal_trajectory, point);

#point = [130, 4950];
append(entry_nominal_trajectory, point);

point = [120, 4710];
append(entry_nominal_trajectory, point);

#point = [110, 4410];
#append(entry_nominal_trajectory, point);

#point = [100, 4100];
#append(entry_nominal_trajectory, point);

point = [90, 3800];
append(entry_nominal_trajectory, point);

#point = [80, 3520];
#append(entry_nominal_trajectory, point);

#point = [70, 3210];
#append(entry_nominal_trajectory, point);


point = [60, 2850];; #55
append(entry_nominal_trajectory, point);

point = [50, 2500]; #50
append(entry_nominal_trajectory, point);




}


#Nominal datas for Dref instead of Vrel ( used in entry.xml as a table and Drag Bias instead of here)

var fill_entry_nom_data_off = func {

var point = [];



#point = [2910, 24500];
#append(entry_nominal_trajectory, point);

point = [3270, 4.3];
append(entry_nominal_trajectory_drag, point);

point = [2820, 6];
append(entry_nominal_trajectory_drag, point);

point = [2680, 7];
append(entry_nominal_trajectory_drag, point);

point = [2460, 8];
append(entry_nominal_trajectory_drag, point);

point = [2270, 9];
append(entry_nominal_trajectory_drag, point);

point = [2140, 10];
append(entry_nominal_trajectory_drag, point);

point = [2000, 11];
append(entry_nominal_trajectory_drag, point);

point = [1870, 12];
append(entry_nominal_trajectory_drag, point);

point = [1750, 13];
append(entry_nominal_trajectory_drag, point);
   
point = [1650, 14];
append(entry_nominal_trajectory_drag, point);

point = [1550, 15];
append(entry_nominal_trajectory_drag, point);

point = [1460, 16];
append(entry_nominal_trajectory_drag, point);

point = [1400, 16.6];
append(entry_nominal_trajectory_drag, point);

point = [1300, 18];
append(entry_nominal_trajectory_drag, point);

point = [1210, 19.4];
append(entry_nominal_trajectory_drag, point);

point = [1110, 20.8];
append(entry_nominal_trajectory_drag, point);

point = [1040, 22.2];
append(entry_nominal_trajectory_drag, point);

point = [980, 23.5];
append(entry_nominal_trajectory_drag, point);

point = [910, 24.9];
append(entry_nominal_trajectory_drag, point);

point = [860, 26.3];
append(entry_nominal_trajectory_drag, point);

point = [830, 27.1];
append(entry_nominal_trajectory_drag, point);

point = [750, 29.3];
append(entry_nominal_trajectory_drag, point);

point = [720, 30.4];
append(entry_nominal_trajectory_drag, point);

point = [680, 31.7];
append(entry_nominal_trajectory_drag, point);

point = [640, 33];
append(entry_nominal_trajectory_drag, point);

point = [600, 33];
append(entry_nominal_trajectory_drag, point);

point = [570, 33];
append(entry_nominal_trajectory_drag, point);

point = [530, 33];
append(entry_nominal_trajectory_drag, point);

point = [510, 33];
append(entry_nominal_trajectory_drag, point);

point = [480, 33];
append(entry_nominal_trajectory_drag, point);

point = [440, 33];
append(entry_nominal_trajectory_drag, point);

point = [420, 33];
append(entry_nominal_trajectory_drag, point);

point = [390, 32.9];
append(entry_nominal_trajectory_drag, point);

point = [370, 32.1];
append(entry_nominal_trajectory_drag, point);

point = [340, 31];
append(entry_nominal_trajectory_drag, point);

point = [320, 30.3];
append(entry_nominal_trajectory_drag, point);

point = [300, 29.7];
append(entry_nominal_trajectory_drag, point);

point = [270, 28.8];
append(entry_nominal_trajectory_drag, point);

point = [250, 28];
append(entry_nominal_trajectory_drag, point);

point = [220, 27.2];
append(entry_nominal_trajectory_drag, point);

point = [200, 26.5];
append(entry_nominal_trajectory_drag, point);

point = [180, 25.7];
append(entry_nominal_trajectory_drag, point);

point = [160, 24.8];
append(entry_nominal_trajectory_drag, point);

point = [130, 24];
append(entry_nominal_trajectory_drag, point);

point = [120, 23.2];
append(entry_nominal_trajectory_drag, point);

point = [100, 22.4];
append(entry_nominal_trajectory_drag, point);

point = [80, 21];
append(entry_nominal_trajectory_drag, point);

point = [70, 20.7];
append(entry_nominal_trajectory_drag, point);

point = [60, 20];
append(entry_nominal_trajectory_drag, point);

point = [50, 20];
append(entry_nominal_trajectory_drag, point);


}


var get_entry_drag_deviation = func (v, distance) {

# bias the distance to get better match to TAEM
#distance = distance - 20.0;

var t = entry_nominal_trajectory;

var n = size(t);

if (n==0) {return 0.0;}

var i_ref = 0;

for (var i=0; i<n; i=i+1)
	{
	if (distance > t[i][0]) {i_ref = i;  break;}
	}

i = i_ref;

if (i==n) {i=n-1;}
var tgt_v = 0.0;

if ((i==0) or (i == (n-1))) {return 0.0;}
else
	{
	tgt_v = t[i][1] + (t[i-1][1] - t[i][1]) * ((distance - t[i][0]) / (t[i-1][0] - t[i][0]));
	}

#var interpolation_factor =  ((distance - t[i][0]) / (t[i-1][0] - t[i][0]));

return tgt_v - v;

}


var fill_TAEM_nom_data = func {

var point = [];

#Distance between 142 and 74 Nm is for GRTLS TAEM guidance( Early Sturn in case of RTLS)
point = [142, 117000.0];
append(TAEM_nominal_trajectory, point);

point = [106, 105000.0];
append(TAEM_nominal_trajectory, point);

point = [74, 88000.0];
append(TAEM_nominal_trajectory, point);

point = [61, 81000.0];
append(TAEM_nominal_trajectory, point);

point = [58, 78000.0];
append(TAEM_nominal_trajectory, point);

point = [55.0, 76000.0];
append(TAEM_nominal_trajectory, point);

point = [50.0, 74000.0];
append(TAEM_nominal_trajectory, point);

point = [45.0, 71000.0];
append(TAEM_nominal_trajectory, point);

point = [40.0, 67000.0];
append(TAEM_nominal_trajectory, point);

point = [35.0, 61000.0];
append(TAEM_nominal_trajectory, point);

point = [30.0, 54000.0];
append(TAEM_nominal_trajectory, point);

point = [25.0, 46000.0];
append(TAEM_nominal_trajectory, point);

#HAC 270 °
point = [20.0, 37000.0];
append(TAEM_nominal_trajectory, point);

point = [16.3, 30000.0];
append(TAEM_nominal_trajectory, point);

point = [15, 27000.0];
append(TAEM_nominal_trajectory, point);

#90 ° HAC
point = [12.5, 22000.0];
append(TAEM_nominal_trajectory, point);

#MLS
point = [10.0, 17000.0];
append(TAEM_nominal_trajectory, point);

point = [9.0, 15000.0];
append(TAEM_nominal_trajectory, point);

point = [8.0, 13000.0];
append(TAEM_nominal_trajectory, point);

#End of Sit Vert 2 (Limit left)
point = [7, 11000.0];
append(TAEM_nominal_trajectory, point);

point = [6, 9000.0];
append(TAEM_nominal_trajectory, point);

point = [5, 7275.0];
append(TAEM_nominal_trajectory, point);

point = [4, 5225.0];
append(TAEM_nominal_trajectory, point);

point = [3, 3310.0];
append(TAEM_nominal_trajectory, point);

#GS Flag below 1500 QFE
point = [1.9, 1020.0];
append(TAEM_nominal_trajectory, point);

}


var get_glideslope_deviation = func (alt, distance) {

var t = TAEM_nominal_trajectory;

var n = size(t);

if (n==0) {return 0.0;}

var i_ref = 0;

for (var i=0; i<n; i=i+1)
	{
	if (distance > t[i][0]) {i_ref = i;  break;}
	}

i = i_ref;

if (i==n) {i=n-1;}
var tgt_alt = 0.0;

if ((i==0) or (i == (n-1))) {return 0.0;}
else
	{
	tgt_alt = t[i][1] + (t[i-1][1] - t[i][1]) * ((distance - t[i][0]) / (t[i-1][0] - t[i][0]));
	}

#var interpolation_factor =  ((distance - t[i][0]) / (t[i-1][0] - t[i][0]));

return tgt_alt - alt;

}

# initialize the entry and TAEM nominal trajectories for guidance upon startup

fill_TAEM_nom_data ();
fill_entry_nom_data ();
