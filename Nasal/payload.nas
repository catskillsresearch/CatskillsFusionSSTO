# payload management for the Space Shuttle


var rms_toggle_payload = func {

if (getprop("/fdm/jsbsim/systems/rms/effector-attached") == 1)
	{rms_release_payload();}
else
	{rms_grab_payload();}

}


var rms_grab_payload = func {


if (getprop("/fdm/jsbsim/systems/rms/effector-attached") == 1) {return;}

# get the position and orientation of the effector tip

var effector_x = getprop("/fdm/jsbsim/systems/rms/effector-x");
var effector_y = getprop("/fdm/jsbsim/systems/rms/effector-y");
var effector_z = getprop("/fdm/jsbsim/systems/rms/effector-z");


var effector_yaw = getprop("/fdm/jsbsim/systems/rms/sum-wrist-yaw-deg");
var effector_pitch = getprop("/fdm/jsbsim/systems/rms/sum-wrist-pitch-deg");
var effector_roll = getprop("/fdm/jsbsim/systems/rms/ang-wrist-roll-deg");

var payload_from_bay_flag = 0;

# get the payload position in the bay

var payload_x = getprop("/fdm/jsbsim/systems/rms/payload/payload-attach-x");
var payload_y = getprop("/fdm/jsbsim/systems/rms/payload/payload-attach-y");
var payload_z = getprop("/fdm/jsbsim/systems/rms/payload/payload-attach-z");

var payload_pitch = getprop("/fdm/jsbsim/systems/rms/payload/payload-attach-pitch");
var payload_yaw = getprop("/fdm/jsbsim/systems/rms/payload/payload-attach-yaw");
var payload_roll = getprop("/fdm/jsbsim/systems/rms/payload/payload-attach-roll");

# require agreement in position

var flag = 1;

if (math.abs(effector_x - payload_x) > 0.15) {flag = 0;}
if (math.abs(effector_y - payload_y) > 0.15) {flag = 0;}
if (math.abs(effector_z - payload_z) > 0.15) {flag = 0;}

# require agreement in attitude

if (math.abs(effector_pitch - payload_pitch) > 15.0) {flag = 0;}
if (math.abs(effector_yaw - payload_yaw) > 15.0) {flag = 0;}
if (math.abs(effector_roll - payload_roll) > 15.0) {flag = 0;}

if (flag == 1) {payload_from_bay_flag = 1;}

var index = 0;

if ((flag == 0) and (SpaceShuttle.proximity_manager.num_payloads_proximity > 0))# check grab for floating payload
	{

	var x = -effector_x + 8.5;
	var y = effector_y - 2.1;
	var z = effector_z - 1.1;

	var shuttleWorldX = [getprop("/fdm/jsbsim/systems/pointing/world/body-x"), getprop("/fdm/jsbsim/systems/pointing/world/body-x[1]"), getprop("/fdm/jsbsim/systems/pointing/world/body-x[2]")];

	var shuttleWorldY = [getprop("/fdm/jsbsim/systems/pointing/world/body-y"), getprop("/fdm/jsbsim/systems/pointing/world/body-y[1]"), getprop("/fdm/jsbsim/systems/pointing/world/body-y[2]")];

	var shuttleWorldZ = [getprop("/fdm/jsbsim/systems/pointing/world/body-z"), getprop("/fdm/jsbsim/systems/pointing/world/body-z[1]"), getprop("/fdm/jsbsim/systems/pointing/world/body-z[2]")];

	var shuttleCoord = geo.aircraft_position();

	var Offset = SpaceShuttle.add_vector(SpaceShuttle.scalar_product(x, shuttleWorldX), SpaceShuttle.scalar_product(z, shuttleWorldZ));
	Offset = SpaceShuttle.add_vector(Offset, SpaceShuttle.scalar_product(y, shuttleWorldY));
	

	effector_x = shuttleCoord.x() + Offset[0];
	effector_y = shuttleCoord.y() + Offset[1];
	effector_z = shuttleCoord.z() + Offset[2];

	index = SpaceShuttle.proximity_manager.check_rms_grab (effector_x, effector_y, effector_z);

	if (index > 0) {flag = 1;}

	}


#print ("x difference: ", math.abs(effector_x - payload_x));
#print ("y difference: ", math.abs(effector_y - payload_y));
#print ("z difference: ", math.abs(effector_z - payload_z));

#if (math.abs(effector_yaw ) > 20.0) {flag = 0;}
#if ((math.abs(effector_pitch ) > 10.0) and (math.abs(effector_pitch) < 80.0)) {flag = 0;}

print ("yaw: ", math.abs(effector_yaw ));
print ("pitch: ", math.abs(effector_yaw ));

if (flag == 0)
	{
	setprop("/sim/messages/copilot", "Failed to grab payload!");
	return;
	}
else
	{
	setprop("/sim/messages/copilot", "Payload successfully attached!");
	setprop("/fdm/jsbsim/systems/rms/effector-attached", 1);


	if (payload_from_bay_flag == 0)
		{

		var data = payload_data.entry_by_index(index);

		setprop("/fdm/jsbsim/systems/rms/attached-from-orbit", 1);
		setprop("/sim/config/shuttle/PL-selection-flag", index);
		setprop("/fdm/jsbsim/systems/rms/payload/payload-attach-x", data.attach_x);
		setprop("/fdm/jsbsim/systems/rms/payload/payload-attach-y", data.attach_y);
		setprop("/fdm/jsbsim/systems/rms/payload/payload-attach-z", data.attach_z);
		setprop("/fdm/jsbsim/systems/rms/payload/payload-attach-pitch", data.attach_pitch);
		setprop("/fdm/jsbsim/systems/rms/payload/payload-attach-yaw", data.attach_yaw);
		setprop("/fdm/jsbsim/systems/rms/payload/payload-attach-roll", data.attach_roll);
    		setprop("/fdm/jsbsim/systems/rms/payload/payload-released", data.released);
		setprop("/fdm/jsbsim/inertia/pointmass-weight-lbs[5]", data.mass);
		setprop("/sim/config/shuttle/PL-model-path", data.model_path);
		setprop("/lighting/effects/payload-x", data.lighting_x);
		setprop("/lighting/effects/payload-y", data.lighting_y);
		setprop("/lighting/effects/payload-z", data.lighting_z);
		setprop("/lighting/effects/payload-r", data.lighting_r);

    if (index == 1)
      {SpaceShuttle.TDRS_manager.unload();}
    else if (index == 2)
      {SpaceShuttle.spartan_manager.unload();}
    else if (index == 3)
      {SpaceShuttle.hst_manager.unload();}
		}
	}

setprop("/fdm/jsbsim/systems/rms/effector-closed", 1);
setprop("/fdm/jsbsim/systems/rms/effector-rigid", 1);

}


var rms_release_payload = func {

	# first check whether a payload is attached

	if (getprop("/fdm/jsbsim/systems/rms/effector-attached") != 1)
		{
		return;
		}


	# first check whether we release into space or put into the payload bay

	var status = getprop("/fdm/jsbsim/systems/rms/payload-ready-to-latch");
	
	if (status == 1)
		{
		# we require at least one latch closed to attach the payload firmly

		var is_released = getprop("/fdm/jsbsim/systems/rms/payload-released");

		if (is_released == 0)
			{
			setprop("/sim/messages/copilot", "Payload latched to bay!");
			setprop("/fdm/jsbsim/systems/rms/effector-attached", 0);
			}
	
		}
	else
		{
		  setprop("/sim/messages/copilot", "Payload released!");
		  setprop("/fdm/jsbsim/systems/rms/effector-attached", 2);
		  #SpaceShuttle.init_payload();

      var index = getprop("sim/config/shuttle/PL-selection-flag");

      if (index == 2)
        {
          SpaceShuttle.spartan_manager.copy_offsets();
          SpaceShuttle.spartan_manager.init(0,0,0,0,0,0);
        }
      else if (index == 3)
        {
          SpaceShuttle.hst_manager.copy_offsets();
          SpaceShuttle.hst_manager.init(0,0,0,0,0,0);
          setprop("/fdm/jsbsim/systems/rms/payload/payload-released", 1);
        }
		}

setprop("/fdm/jsbsim/systems/rms/effector-closed", 0);
setprop("/fdm/jsbsim/systems/rms/effector-rigid", 0);
setprop("/fdm/jsbsim/systems/rms/attached-from-orbit", 0);

}

# payload bay slot manager ###############################################

var payload_bay_slot = {

	new: func (index) {
		 var p = { parents: [payload_bay_slot] };

		p.index = index;
		p.occupied = 0;
		p.load_description = "none";
		p.load_id = 0;
		
		return p;
		},

	check_occupied: func () {

		return me.occupied;
		},

	occupy: func (description, id) {
	
		me.occupied = 1;
		me.load_id = id;
		me.load_description = description;
		
		},
		
	free: func {

		me.occupied = 0;
		me.load_id = 0;
		me.load_description = "none";

		},
};


var payload_bay_manager = {

	slot_array: [],

	init: func {

		var slot1 = payload_bay_slot.new(0);
		append(me.slot_array, slot1);

		var slot2 = payload_bay_slot.new(1);
		append(me.slot_array, slot2);

		var slot3 = payload_bay_slot.new(2);
		append(me.slot_array, slot3);

	},



};


payload_bay_manager.init();


# payload data definition ###########################################

var payload_data_entry = {

	new: func (name, index) {
			 var p = { parents: [payload_data_entry] };

			p.name = name;
			p.index = index;
			p.attach_x = 0.0;
			p.attach_y = 0.0;
			p.attach_z = 0.0;
			p.attach_pitch = 0.0;
			p.attach_yaw = 0.0;
			p.attach_roll = 0.0;
			p.mass = 0.0;
			p.model_path = "";
			p.lighting_x = 0.0;
			p.lighting_y = 0.0;
			p.lighting_z = 0.0;
			p.lighting_r = 0.0;
			p.requires_pallet = 0;
			p.requires_slot1 = 0;
			p.requires_slot2 = 0;
			p.requires_slot3 = 0;
			p.center_offset = [-1.0, 0.0, 0.0];
			p.solid_flag = 0;
			p.solid_radius = 0.0;
		 	p.released = 0;
			p.deployment_sequence = 0;
			p.deployment_sequence_time = 0.0; 

			return p;
			},

};

var payload_data = {

	payload_data_array: [],
	num_entries: 0,

	init: func {



		var p0 = payload_data_entry.new ("none" , me.num_entries);
		append(me.payload_data_array, p0);
		me.num_entries += 1;

		var p1 = payload_data_entry.new("TDRS demo", me.num_entries);
		p1.attach_x = 11.50;
		p1.attach_y = 2.0;
		p1.attach_z = -1.8;
		p1.mass = 20000.0;
		p1.requires_slot3 = 1;
		p1.model_path = "Aircraft/CatskillsFusionSSTO/Models/PayloadBay/TDRS/TDRS_disconnected.xml";		
		append(me.payload_data_array, p1);
		me.num_entries += 1;

		var p2 = payload_data_entry.new("SPARTAN-201", me.num_entries);
		p2.attach_x = 9.85;
		p2.attach_y = 1.9;
		p2.attach_z = -0.6;
		p2.attach_pitch = 90.0;
		p2.mass = 2998.2;
		p2.model_path = "Aircraft/CatskillsFusionSSTO/Models/PayloadBay/Spartan-201/SPARTAN-201-disconnected.xml";
		p2.lighting_x = 1.5;		
		p2.lighting_y = 0.0;
		p2.lighting_z = 0.0;
		p2.lighting_r = 2.4;
		p2.requires_pallet = 1;
		p2.requires_slot2 = 1;
		p2.center_offset = [-1.0, 0.0, 0.0];
		p2.solid_flag = 1;
		p2.solid_radius = 0.5;
		append(me.payload_data_array, p2);
		me.num_entries += 1;

		var p3 = payload_data_entry.new("HST", me.num_entries);
		p3.attach_x = 8.43;
		p3.attach_y = 0.76;
		p3.attach_z = 0.60;
		p3.attach_pitch = 90.0;
		p3.attach_roll = 180.0;
		p3.mass = 24500;
		p3.model_path = "Aircraft/CatskillsFusionSSTO/Models/PayloadBay/HST/hst-disconnected.xml";
		p3.lighting_x = 1.5;
		p3.lighting_y = 0.0;
		p3.lighting_z = 0.0;
		p3.lighting_r = 2.4;
		p3.requires_pallet = 0;
		p3.requires_slot1 = 1;
		p3.requires_slot2 = 1;
		p3.requires_slot3 = 1;
		p3.center_offset = [-1.0, 0.0, 0.0];
		p3.solid_flag = 1;
		p3.solid_radius = 0.5;
		p3.deployment_sequence = 1;
		p3.deployment_sequence_time = 120.0;
		append(me.payload_data_array, p3);
		me.num_entries += 1;
	},


	list: func {

		print ("Payload data list");

		for (var i=0; i< me.num_entries; i=i+1)
			{
			
			print(me.payload_data_array[i].name);
			print("Mass: ", me.payload_data_array[i].mass);
			print("Attach point: ", me.payload_data_array[i].attach_x, " ", me.payload_data_array[i].attach_y, " ", me.payload_data_array[i].attach_z);
			print ("Model path: ", me.payload_data_array[i].model_path);
			
			}

	},

	entry_by_index: func (index) {

		return me.payload_data_array[index];

	},

	entry_by_name: func (name) {

		for (var i=0; i< me.num_entries; i=i+1)
			{
			if (me.payload_data_array[i].name == name)
				{
				var p = {};
				p.name = me.payload_data_array[i].name;
				p.index = me.payload_data_array[i].index;
				p.attach_x = me.payload_data_array[i].attach_x;
				p.attach_y = me.payload_data_array[i].attach_y;
				p.attach_z = me.payload_data_array[i].attach_z;
				p.attach_pitch = me.payload_data_array[i].attach_pitch;
				p.attach_yaw = me.payload_data_array[i].attach_yaw;
				p.attach_roll = me.payload_data_array[i].attach_roll;
				p.mass = me.payload_data_array[i].mass;
				p.model_path = me.payload_data_array[i].model_path;
				p.lighting_x = me.payload_data_array[i].lighting_x;
				p.lighting_y = me.payload_data_array[i].lighting_y;
				p.lighting_z = me.payload_data_array[i].lighting_z;
				p.lighting_r = me.payload_data_array[i].lighting_r;
				p.requires_pallet = me.payload_data_array[i].requires_pallet;
				p.requires_slot1 = me.payload_data_array[i].requires_slot1;
				p.requires_slot2 = me.payload_data_array[i].requires_slot2;
				p.requires_slot3 = me.payload_data_array[i].requires_slot3;
				p.center_offset = me.payload_data_array[i].center_offset;
				p.solid_flag = me.payload_data_array[i].solid_flag;
				p.solid_radius = me.payload_data_array[i].solid_radius;
				p.released = me.payload_data_array[i].released;
				p.deployment_sequence =me.payload_data_array[i].deployment_sequence;
				p.deployment_sequence_time = me.payload_data_array[i].deployment_sequence_time;
				
				#return me.payload_data_array[i];
				return p;
				}
			}
		print ("No payload with the name ", name, " defined!");
		return me.payload_data_array[0];

	},
	

};

payload_data.init();


# initial payload selection

var update_payload_selection = func {

var payload_string = getprop("/sim/config/shuttle/PL-selection");


var data = payload_data.entry_by_name(payload_string);

var occupy_flag = 1;

if (data.requires_slot1 == 1)
	{
	if (payload_bay_manager.slot_array[0].check_occupied() == 1) {occupy_flag = 0;}
	}
if (data.requires_slot2 == 1)
	{
	if (payload_bay_manager.slot_array[1].check_occupied() == 1) {occupy_flag = 0;}
	}
if (data.requires_slot3 == 1)
	{
	if (payload_bay_manager.slot_array[2].check_occupied() == 1) {occupy_flag = 0;}
	}

if (occupy_flag == 0)
	{
	SpaceShuttle.callout.make("No space for selected payload.", "essential");
	return;
	}

if (data.requires_slot1 == 1) {payload_bay_manager.slot_array[0].occupy(data.name, data.index);}
if (data.requires_slot2 == 1) {payload_bay_manager.slot_array[1].occupy(data.name, data.index);}
if (data.requires_slot3 == 1) {payload_bay_manager.slot_array[2].occupy(data.name, data.index);}


if (data.name == "none")
	{
	payload_bay_manager.slot_array[0].free();
	payload_bay_manager.slot_array[1].free();
	
	if (getprop("/sim/config/shuttle/OMS-kit-config") == "none")
		{payload_bay_manager.slot_array[2].free();}
	}

setprop("/sim/config/shuttle/PL-selection-flag", data.index);
setprop("/fdm/jsbsim/systems/rms/payload/payload-attach-x", data.attach_x);
setprop("/fdm/jsbsim/systems/rms/payload/payload-attach-y", data.attach_y);
setprop("/fdm/jsbsim/systems/rms/payload/payload-attach-z", data.attach_z);
setprop("/fdm/jsbsim/systems/rms/payload/payload-attach-pitch", data.attach_pitch);
setprop("/fdm/jsbsim/systems/rms/payload/payload-attach-yaw", data.attach_yaw);
setprop("/fdm/jsbsim/systems/rms/payload/payload-attach-roll", data.attach_roll);
setprop("/fdm/jsbsim/systems/rms/payload/payload-released", data.released);
setprop("/fdm/jsbsim/inertia/pointmass-weight-lbs[5]", data.mass);
setprop("/sim/config/shuttle/PL-model-path", data.model_path);
setprop("/lighting/effects/payload-x", data.lighting_x);
setprop("/lighting/effects/payload-y", data.lighting_y);
setprop("/lighting/effects/payload-z", data.lighting_z);
setprop("/lighting/effects/payload-r", data.lighting_r);


if (data.name == "none")
	{
	SpaceShuttle.cdlg_notepad.write_to_line(7, "");
	SpaceShuttle.cdlg_notepad.write_to_line(8, "");	
	}
else
	{

	SpaceShuttle.cdlg_notepad.write_to_line(7, "Payload "~data.name);
	SpaceShuttle.cdlg_notepad.write_to_line(8, "Attachment point x:"~sprintf("%3.1f", data.attach_x)~" y: "~sprintf("%3.1f", data.attach_y)~" z: "~sprintf("%3.1f", data.attach_z));
	}


if (data.requires_pallet == 1)
	{
	setprop("/sim/config/shuttle/PL-pallet-flag", 1);
	}
else
	{
	setprop("/sim/config/shuttle/PL-pallet-flag", 0);
	}

}


# OMS kit install

var update_oms_kit_selection = func () {

var cfg = getprop("/sim/config/shuttle/OMS-kit-config");


if ((cfg != "none") and (payload_bay_manager.slot_array[2].check_occupied() == 1))
	{
	SpaceShuttle.callout.make("No space for OMS kit.", "essential");
	return;
	}


var num_tanks = 0;

if (cfg == "OMS kit 500 fps") {num_tanks = 1;} 
else if (cfg == "OMS kit 1000 fps") {num_tanks = 2;} 
else if (cfg == "OMS kit 1500 fps") {num_tanks = 3;} 

if (num_tanks == 0)
	{
	setprop("/fdm/jsbsim/systems/oms-hardware/oms-kit-installed", 0);
	setprop("/fdm/jsbsim/systems/oms-hardware/oms-kit-num-tanks", 0);
	setprop("/consumables/fuel/tank[26]/level-lbs", 0.0);
	setprop("/consumables/fuel/tank[27]/level-lbs", 0.0);
	setprop("/fdm/jsbsim/inertia/pointmass-weight-lbs[7]", 0.0);
	payload_bay_manager.slot_array[2].free();
	} 
else if (num_tanks == 1)
	{
	setprop("/fdm/jsbsim/systems/oms-hardware/oms-kit-installed", 1);
	setprop("/fdm/jsbsim/systems/oms-hardware/oms-kit-num-tanks", 1);
	setprop("/consumables/fuel/tank[26]/level-lbs", 7773.0);
	setprop("/consumables/fuel/tank[27]/level-lbs", 4718.0);
	setprop("/fdm/jsbsim/inertia/pointmass-weight-lbs[7]", 3378.0);
	payload_bay_manager.slot_array[2].occupy(cfg, 0);
	}
else if (num_tanks == 2)
	{
	setprop("/fdm/jsbsim/systems/oms-hardware/oms-kit-installed", 1);
	setprop("/fdm/jsbsim/systems/oms-hardware/oms-kit-num-tanks", 2);
	setprop("/consumables/fuel/tank[26]/level-lbs", 15546.0);
	setprop("/consumables/fuel/tank[27]/level-lbs", 9436.0);
	setprop("/fdm/jsbsim/inertia/pointmass-weight-lbs[7]", 4355.0);
	payload_bay_manager.slot_array[2].occupy(cfg, 0);
	}
else if (num_tanks == 3)
	{
	setprop("/fdm/jsbsim/systems/oms-hardware/oms-kit-installed", 1);
	setprop("/fdm/jsbsim/systems/oms-hardware/oms-kit-num-tanks", 3);
	setprop("/consumables/fuel/tank[26]/level-lbs", 23319.0);
	setprop("/consumables/fuel/tank[27]/level-lbs", 14154.0);
	setprop("/fdm/jsbsim/inertia/pointmass-weight-lbs[7]", 5657.0);
	payload_bay_manager.slot_array[2].occupy(cfg, 0);
	}


}




# checks the reach limit of the RMS arm for an operator-specified command - very simplistic still

var check_rms_reach_limit = func {


	#var tgt_x = getprop("/fdm/jsbsim/systems/rms/software/tgt-pos-x");
	#var tgt_y = getprop("/fdm/jsbsim/systems/rms/software/tgt-pos-y");
	#var tgt_z = getprop("/fdm/jsbsim/systems/rms/software/tgt-pos-z");

	var tgt_x = pdrs_auto_seq_manager.opr_cmd_tgt[0];
	var tgt_y = pdrs_auto_seq_manager.opr_cmd_tgt[1];
	var tgt_z = pdrs_auto_seq_manager.opr_cmd_tgt[2];

	var length = math.sqrt(tgt_x * tgt_x + tgt_y * tgt_y + tgt_z * tgt_z);

	if ((length < 0.5) or (length > 14.5)) 
		{
		setprop("/fdm/jsbsim/systems/rms/software/reach-limit-string", "FAIL");
		}
	else
		{
		setprop("/fdm/jsbsim/systems/rms/software/reach-limit-string", "GOOD");
		}
}


# PDRS AUTO sequences ###########################################

# sequence point hash

var pdrs_auto_seq_point = {
	new: func (x, y, z, pitch, yaw, roll, delay) {
 		var p = { parents: [pdrs_auto_seq_point] };
		p.x = x;
		p.y = y;
		p.z = z;
		p.pitch = pitch;
		p.yaw = yaw;
		p.roll = roll;
		p.delay = delay;	
		return p;
	},
};

var pdrs_auto_seq_manager = {

	n_auto_sequences: 0,
	auto_sequence_array: [],
	sequence_slot_array: [-1, -1, -1, -1],

	opr_cmd_loop_flag: 0,
	opr_cmd_tgt: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],

	auto_seq_loop_flag: 0,

	current_index: -1,
	start_index: 0,

	assign_slot: func (slot, index) {

	me.sequence_slot_array[slot] = index;

	},

	append_sequence_array: func (array) {

	append(me.auto_sequence_array, array);

	},

	# operator commanded routine to go to the target point defined on SPEC 94

	opr_cmd_goto_point: func {

		# set target
		setprop("/fdm/jsbsim/systems/rms/software/tgt-pos-x", me.opr_cmd_tgt[0]);
		setprop("/fdm/jsbsim/systems/rms/software/tgt-pos-y", me.opr_cmd_tgt[1]);
		setprop("/fdm/jsbsim/systems/rms/software/tgt-pos-z", me.opr_cmd_tgt[2]);

		setprop("/fdm/jsbsim/systems/rms/software/tgt-att-p", me.opr_cmd_tgt[3]);
		setprop("/fdm/jsbsim/systems/rms/software/tgt-att-y", me.opr_cmd_tgt[4]);
		setprop("/fdm/jsbsim/systems/rms/software/tgt-att-r", me.opr_cmd_tgt[5]);

		# first adjust angle

		setprop("/fdm/jsbsim/systems/rms/drive-selection-mode", 5);
		
		# init management loop

		me.opr_cmd_loop_flag = 1;
		settimer(func me.opr_cmd_loop(), 0.2);
	},


	opr_cmd_loop : func {
	
		if (me.opr_cmd_loop_flag == 0) {return;}

		var att_reached = getprop("/fdm/jsbsim/systems/rms/software/effector-att-reached-flag");
		var pos_reached = getprop("/fdm/jsbsim/systems/rms/software/effector-pos-reached-flag");

		# acquire position once attitude is done

		if ((att_reached == 1) and (pos_reached == 0)) 
			{	

			if (getprop("/fdm/jsbsim/systems/rms/drive-selection-mode") == 5)
				{
				print("PDRS: Attitude acquired, moving into position");	
				setprop("/fdm/jsbsim/systems/rms/drive-selection-mode", 4);
				}
			}

		# correct attitude drift if we are in position

		if ((att_reached == 0) and (pos_reached == 1)) 
			{	
			if (getprop("/fdm/jsbsim/systems/rms/drive-selection-mode") == 4)
				{
				print("PDRS: Position acquired, correcting attitude");		
				setprop("/fdm/jsbsim/systems/rms/drive-selection-mode", 5);
				}
			}

		if ((att_reached == 1) and (pos_reached == 1))
			{
			print("PDRS: Operator commanded point reached");	
			me.opr_cmd_loop_flag = 0;
			setprop("/fdm/jsbsim/systems/rms/drive-selection-mode", 0);
			return;
			}

		settimer( func me.opr_cmd_loop (), 1.0);
	},


	# auto sequence of multiple points

	set_start_index: func (num) {

		me.start_index = num;

	},


	start_sequence: func (slot) {

		me.current_sequence_index = me.sequence_slot_array[slot]-1;

		if (me.current_sequence_index < 0) {return;}
		if (me.current_sequence_index > size(me.auto_sequence_array)-1)
			{
			print ("PDRS: No i-loaded auto sequence of that number available");
			return;
			}
		

		me.current_sequence = me.auto_sequence_array[me.current_sequence_index];
		me.current_sequence_size = size(me.current_sequence);

		if (me.current_sequence_size == 0) {return;}

		me.current_index = me.start_index;

		if (me.current_index > me.current_sequence_size-1)
			{
			print ("PDRS: Point number exceeds points in sequence");
			return;
			}

		print("PDRS: Auto sequence ", me.current_sequence_index, " with ", me.current_sequence_size, " points loaded.");

		# push first point

		var point = me.current_sequence[me.current_index];
		me.sequence_target_point(point);	


		# init management loop

		me.auto_seq_loop_flag = 1;
		setprop("/fdm/jsbsim/systems/rms/drive-selection-mode", 5);
		settimer(func me.auto_sequence_loop(), 0.2);

		
	},

	auto_sequence_loop: func {

		if (me.auto_seq_loop_flag == 0) {return;}


		if (me.current_index > me.current_sequence_size - 1) 
			{
			me.auto_seq_loop_flag = 0;
			print ("PDRS: Auto sequence finished");
			me.current_index = me.current_index -1; # show last point on SPEC 94
			setprop("/fdm/jsbsim/systems/rms/drive-selection-mode", 0);
			return;
			} 

		var att_reached = getprop("/fdm/jsbsim/systems/rms/software/effector-att-reached-flag");
		var pos_reached = getprop("/fdm/jsbsim/systems/rms/software/effector-pos-reached-flag");

		# acquire position once attitude is done

		if ((att_reached == 1) and (pos_reached == 0)) 
			{	

			if (getprop("/fdm/jsbsim/systems/rms/drive-selection-mode") == 5)
				{
				print("PDRS: Attitude acquired, moving into position");	
				setprop("/fdm/jsbsim/systems/rms/drive-selection-mode", 4);
				}
			}

		# correct attitude drift if we are in position

		if ((att_reached == 0) and (pos_reached == 1)) 
			{	
			if (getprop("/fdm/jsbsim/systems/rms/drive-selection-mode") == 4)
				{
				print("PDRS: Position acquired, correcting attitude");		
				setprop("/fdm/jsbsim/systems/rms/drive-selection-mode", 5);
				}
			}

		if ((att_reached == 1) and (pos_reached == 1))
			{
			print("PDRS: Commanded point reached");	

			me.current_index = me.current_index + 1;
			#print("Index is now: ",me.current_index, " size: ", me.current_sequence_size);

			if (me.current_index < me.current_sequence_size)
				{
				print ("PDRS: Pushing target point ", me.current_index);
				var point = me.current_sequence[me.current_index];
				me.sequence_target_point(point);
				}
			
			}


		settimer( func me.auto_sequence_loop (), 1.0);
	},

	
	sequence_target_point: func (point) {

		# set target
		setprop("/fdm/jsbsim/systems/rms/software/tgt-pos-x", point.x);
		setprop("/fdm/jsbsim/systems/rms/software/tgt-pos-y", point.y);
		setprop("/fdm/jsbsim/systems/rms/software/tgt-pos-z", point.z);

		setprop("/fdm/jsbsim/systems/rms/software/tgt-att-p", point.pitch);
		setprop("/fdm/jsbsim/systems/rms/software/tgt-att-y", point.yaw);
		setprop("/fdm/jsbsim/systems/rms/software/tgt-att-r", point.roll);

		# first adjust angle

		setprop("/fdm/jsbsim/systems/rms/drive-selection-mode", 5);
		


	},

};


var add_test_seq = func {


var a = [];
var p = pdrs_auto_seq_point.new(12.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0);
append(a, p);

p = pdrs_auto_seq_point.new(10.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0);
append(a, p);

p = pdrs_auto_seq_point.new(10.0, 2.0, 0.0, 30.0, 0.0, 0.0, 0.0);
append(a, p);

p = pdrs_auto_seq_point.new(13.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0);
append(a, p);

pdrs_auto_seq_manager.append_sequence_array(a);

var b = [];
p = pdrs_auto_seq_point.new(13.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0);
append(b, p);

p = pdrs_auto_seq_point.new(12.0, 1.5, 1.0, 30.0, 0.0, 0.0, 0.0);
append(b, p);

p = pdrs_auto_seq_point.new(12.0, 2.0, 1.0, 30.0, 0.0, 0.0, 0.0);
append(b, p);

pdrs_auto_seq_manager.append_sequence_array(b);

#pdrs_auto_seq_manager.assign_slot(0,0);
}

#add_test_seq();
