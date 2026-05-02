# high level caution and warning system routines for the Space Shuttle
# Thorsten Renk 2015 // GinGin 2020

var inspection_group  = 0;

var cws_message_array = [];

var cws_message_array_long = ["","","","","","","","","","","","","","",""];

var cws_message_array_bfs = [];

var cws_message_array_long_bfs = ["","","","","","","","","","","","","","",""];

var cws_last_message_acknowledge = 0;
var cws_last_message_acknowledge_bfs = 0;
var meds_last_message_acknowledge = 0;

# the message hash stores the information what faults have already been announced

var cws_msg_hash = {
f1f : 0, f1l : 0, f1u : 0, f1d : 0, f2f : 0, f2r : 0, f2u : 0, f2d : 0, f3f : 0, f3l : 0, f3u : 0, f3d : 0, f4r : 0, f4d : 0, f5r : 0, f5l : 0,
l1a : 0, l1l : 0, l1u : 0, l2u: 0, l2l : 0, l2d : 0, l3l : 0, l3a : 0, l3d : 0, l4u : 0, l4l : 0, l4d : 0, l5d : 0, l5l : 0,
r1a : 0, r1r : 0, r1u : 0, r2u: 0, r2r : 0, r2d : 0, r3r : 0, r3a : 0, r3d : 0, r4u : 0, r4r : 0, r4d : 0, r5d : 0, r5r : 0,
fhep : 0, fpop : 0, fleak : 0, lhep: 0, lpop: 0, lleak: 0, rhep: 0, rpop: 0, rleak: 0, rcsftemp: 0,
omslg : 0, omsrg : 0, omslqty : 0, omsrqty : 0, omslpc : 0, omsrpc : 0, omsltkp: 0, omsrtkp: 0, omstemp: 0, xfeedtemp: 0,
acvolt1 : 0, acvolt2 : 0, acvolt3 : 0, acovld1 : 0, acovld2 : 0, acovld3 : 0, mnvolta : 0, mnvoltb : 0, mnvoltc : 0,
fcvolt1 : 0, fcvolt2 : 0, fcvolt3 : 0, fcamp1 : 0, fcamp2 : 0, fcamp3 : 0, stackt1 : 0, stackt2 : 0, stackt3 : 0, fcpump1 : 0, fcpump2 : 0, fcpump3 : 0, fcreac1 : 0, fcreac2 : 0, fcreac3 : 0,
rm_fail_tac: 0, rm_dlm_tac: 0, nav_edit_tac: 0, probes: 0, nav_edit_alt: 0, rm_fail_adta: 0, rm_dlma_adta: 0,
rm_fail_imu: 0, rm_dlma_imu: 0, imu_temp: 0,
ssme_fail_l: 0, ssme_fail_c: 0, ssme_fail_r: 0, mps_hyd_l: 0, mps_hyd_c: 0, mps_hyd_r: 0, ssme_repos: 0,
mps_elec_l: 0, mps_elec_c: 0, mps_elec_r: 0, mps_cmd_l: 0, mps_cmd_r:0, mps_cmd_c: 0, et_sep_inh: 0,
mps_he_p_l: 0, mps_he_p_r: 0, mps_he_p_c: 0, pneu_p_reg: 0, pneu_p_tk: 0, mps_data_l: 0, mps_manf: 0, 
me_shdn_sw_l: 0, me_shdn_sw_r: 0, me_shdn_sw_c: 0,
mps_data_r: 0, mps_data_c: 0, no_y_jet_switchover: 0, et_sep_auto: 0, et_sep_man : 0,
avbayt1 : 0, avbayt2 : 0, avbayt3 : 0, avbayfan1 : 0, avbayfan2 : 0, avbayfan3 : 0, cabinp : 0, cabindpdt : 0, ppo2 : 0, cabinfan : 0, imudp : 0,
freon_flow1 : 0, freon_flow2 : 0, evap_out_t : 0, h2o_pump_p : 0, top_heaters : 0, hild_heaters : 0, evap_fdln_heaters : 0,
apu_line_heaters : 0, apu_bfs1 : 0, apu_bfs2 : 0, apu_bfs3 : 0, apu_speed1 : 0, apu_speed2 : 0, apu_speed3 : 0, ggbedt_1 : 0, ggbedt_2 : 0, ggbedt_3 : 0, apu_fuel_qty : 0,
hyd_p1 : 0, hyd_p2 : 0, hyd_p3 : 0,
wsb_vent_t : 0, wsb_qty_1 : 0, wsb_qty_2 : 0, wsb_qty_3 : 0,
ott_stn_in : 0, mep : 0,
high_g : 0,
gpc_fail_1 : 0, gpc_fail_2 : 0, gpc_fail_3 : 0, gpc_fail_4 : 0, gpc_fail_5 : 0,
};


var meds_msg_hash = {
io : [0,0,0,0,0,0,0,0,0,0,0],
port_change: [0,0,0,0,0,0,0,0,0,0,0],
poll: [0,0,0,0],
};

var cws_inspect = func {

if (inspection_group == 0) 
	{cws_inspect_fwd_rcs_thrusters();}


if (inspection_group == 1) 
	{cws_inspect_left_rcs_thrusters();}

if (inspection_group == 2) 
	{cws_inspect_right_rcs_thrusters();}

if (inspection_group == 3)
	{cws_inspect_oms();}

if (inspection_group == 4)
	{cws_inspect_fc_electric();}

if (inspection_group == 5)
	{meds_inspect();}

if (inspection_group == 6)
	{cws_inspect_nav();}

if (inspection_group == 7)
	{SpaceShuttle.gpc_manager.check_cam_votes();}

if (inspection_group == 8)
	{cws_inspect_eclss();}

if (inspection_group == 9)
	{cws_inspect_apu_hyd();}

if (inspection_group == 10)
	{SpaceShuttle.master_alarm_mngr.inspect();}


inspection_group = inspection_group + 1;
if (inspection_group == 12) {inspection_group = 0;}
}


#################################################
# CWS checks of forward RCS
#################################################

var cws_inspect_fwd_rcs_thrusters = func {

var ops =  getprop("/fdm/jsbsim/systems/dps/ops");

# FWD manifold 1
# Different messages for PASS/BFS RCS failure on/off 
# Class 2 hardware ( RCS light F7) and software ( Backup and fault message)

var f1f = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-F1F-condition");
var f1l = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-F1L-condition");
var f1u = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-F1U-condition");
var f1d = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-F1D-condition");

if (f1f + f1l + f1u + f1d < 4.0) # we have a manifold 1 fail off condition
	{
	setprop("/fdm/jsbsim/systems/cws/jet-fail-f1", 1);
	

	if ((f1f < 1.0) and (cws_msg_hash.f1f == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "FJET", "12   ", 2, "PASS");
		create_fault_message("    F RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.f1f = 1;
		}
	if ((f1l < 1.0) and (cws_msg_hash.f1l == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "LJET", "12   ", 2, "PASS");
		create_fault_message("    F RCS     ", " JET", "    5", 2, "BFS");	
		cws_msg_hash.f1l = 1;
		}
	if ((f1u < 1.0) and (cws_msg_hash.f1u == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "UJET", "12   ", 2, "PASS");
		create_fault_message("    F RCS     ", " JET", "    5", 2, "BFS");	
		cws_msg_hash.f1u = 1;
		}
	if ((f1d < 1.0) and (cws_msg_hash.f1d == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "DJET", "12   ", 2, "PASS");
		create_fault_message("    F RCS     ", " JET", "    5", 2, "BFS");	
		cws_msg_hash.f1d = 1;
		}
	}
else if (f1f + f1l + f1u + f1d > 4.0) # we have a manifold 1 fail on condition
	{
	setprop("/fdm/jsbsim/systems/cws/jet-fail-f1", 2);
	

	if ((f1f > 1.0) and (cws_msg_hash.f1f == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "FJET", "12   ", 2, "PASS");
		create_fault_message("    F RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.f1f = 1;
		}
	if ((f1l > 1.0) and (cws_msg_hash.f1l == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "LJET", "12   ", 2, "PASS");
		create_fault_message("    F RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.f1l = 1;
		}
	if ((f1u > 1.0) and (cws_msg_hash.f1u == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "UJET", "12   ", 2, "PASS");
		create_fault_message("    F RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.f1u = 1;
		}
	if ((f1d > 1.0) and (cws_msg_hash.f1d == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "DJET", "12   ", 2, "PASS");
		create_fault_message("    F RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.f1d = 1;
		}

	}


# FWD manifold 2

var f2f = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-F2F-condition");
var f2r = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-F2R-condition");
var f2u = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-F2U-condition");
var f2d = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-F2D-condition");

if (f2f + f2r + f2u + f2d < 4.0) # we have a manifold 2 fail off condition
	{
	setprop("/fdm/jsbsim/systems/cws/jet-fail-f2", 1);
	

	if ((f2f < 1.0) and (cws_msg_hash.f2f == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "FJET", "12   ", 2, "PASS");
		create_fault_message("    F RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.f2f = 1;
		}
	if ((f2r < 1.0) and (cws_msg_hash.f2r == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "RJET", "12   ", 2, "PASS");
		create_fault_message("    F RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.f2r = 1;
		}
	if ((f2u < 1.0) and (cws_msg_hash.f2u == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "UJET", "12   ", 2, "PASS");
		create_fault_message("    F RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.f2u = 1;
		}
	if ((f2d < 1.0) and (cws_msg_hash.f2d == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "DJET", "12   ", 2, "PASS");
		create_fault_message("    F RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.f2d = 1;
		}
	}
else if (f2f + f2r + f2u + f2d > 4.0) # we have a manifold 2 fail on condition
	{
	setprop("/fdm/jsbsim/systems/cws/jet-fail-f2", 2);
	

	if ((f2f > 1.0) and (cws_msg_hash.f2f == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "FJET", "12   ", 2, "PASS");
		create_fault_message("    F RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.f2f = 1;
		}
	if ((f2r > 1.0) and (cws_msg_hash.f2r == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "RJET", "12   ", 2, "PASS");
		create_fault_message("    F RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.f2r = 1;
		}
	if ((f2u > 1.0) and (cws_msg_hash.f2u == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "UJET", "12   ", 2, "PASS");
		create_fault_message("    F RCS     ", " JET", "    5", 2, "BFS");;
		cws_msg_hash.f2u = 1;
		}
	if ((f2d > 1.0) and (cws_msg_hash.f2d == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "DJET", "12   ", 2, "PASS");
		create_fault_message("    F RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.f2d = 1;
		}
	}

# FWD manifold 3

var f3f = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-F3F-condition");
var f3l = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-F3L-condition");
var f3u = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-F3U-condition");
var f3d = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-F3D-condition");

if (f3f + f3l + f3u + f3d < 4.0) # we have a manifold 3 fail off condition
	{
	setprop("/fdm/jsbsim/systems/cws/jet-fail-f3", 1);
	

	if ((f3f < 1.0) and (cws_msg_hash.f3f == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "FJET", "12   ", 2, "PASS");
		create_fault_message("    F RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.f3f = 1;
		}
	if ((f3l < 1.0) and (cws_msg_hash.f3l == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "LJET", "12   ", 2, "PASS");
		create_fault_message("    F RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.f3l = 1;
		}
	if ((f3u < 1.0) and (cws_msg_hash.f3u == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "UJET", "12   ", 2, "PASS");
		create_fault_message("    F RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.f3u = 1;
		}
	if ((f3d < 1.0) and (cws_msg_hash.f3d == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "DJET", "12   ", 2, "PASS");
		create_fault_message("    F RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.f3d = 1;
		}
	}
else if (f3f + f3l + f3u + f3d > 4.0) # we have a manifold 3 fail on condition
	{
	setprop("/fdm/jsbsim/systems/cws/jet-fail-f3", 2);
	

	if ((f3f > 1.0) and (cws_msg_hash.f3f == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "FJET", "12   ", 2, "PASS");
		create_fault_message("    F RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.f3f = 1;
		}
	if ((f3l > 1.0) and (cws_msg_hash.f3l == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "LJET", "12   ", 2, "PASS");
		create_fault_message("    F RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.f3l = 1;
		}
	if ((f3u > 1.0) and (cws_msg_hash.f3u == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "UJET", "12   ", 2, "PASS");
		create_fault_message("    F RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.f3u = 1;
		}
	if ((f3d > 1.0) and (cws_msg_hash.f3d == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "DJET", "12   ", 2, "PASS");
		create_fault_message("    F RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.f3d = 1;
		}
	}

# FWD manifold 4

var f4r = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-F4R-condition");
var f4d = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-F4D-condition");


if (f4r + f4d < 2.0) # we have a manifold 4 fail off condition
	{
	setprop("/fdm/jsbsim/systems/cws/jet-fail-f4", 1);
	

	if ((f4r < 1.0) and (cws_msg_hash.f4r == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "RJET", "12   ", 2, "PASS");
		create_fault_message("    F RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.f4r = 1;
		}
	if ((f4d < 1.0) and (cws_msg_hash.f4d == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "DJET", "12   ", 2, "PASS");
		create_fault_message("    F RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.f4d = 1;
		}
	}
else if (f4r + f4d > 2.0) # we have a manifold 4 fail on condition
	{
	setprop("/fdm/jsbsim/systems/cws/jet-fail-f4", 2);
	

	if ((f4r > 1.0) and (cws_msg_hash.f4r == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "RJET", "12   ", 2, "PASS");
		create_fault_message("    F RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.f4r = 1;
		}
	if ((f4d > 1.0) and (cws_msg_hash.f4d == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "DJET", "12   ", 2, "PASS");
		create_fault_message("    F RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.f4d = 1;
		}
	}

# FWD manifold 5 ( No BFS monitoring and fault for Vernier jets as not used when ops !=2)

var f5r = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-F5R-condition");
var f5l = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-F5L-condition");


if (f5r + f5l < 2.0) # we have a manifold 5 fail off condition
	{
	setprop("/fdm/jsbsim/systems/cws/jet-fail-f5", 1);
	

	if ((f5r < 1.0) and (cws_msg_hash.f5r == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "RJET", "12   ", 2, "PASS");
		cws_msg_hash.f5r = 1;
		}
	if ((f5l < 1.0) and (cws_msg_hash.f5l == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "FJET", "12   ", 2, "PASS");
		cws_msg_hash.f5l = 1;
		}
	}
else if (f5r + f5l > 2.0) # we have a manifold 5 fail on condition
	{
	setprop("/fdm/jsbsim/systems/cws/jet-fail-f5", 2);
	

	if ((f5r > 1.0) and (cws_msg_hash.f5r == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "RJET", "12   ", 2, "PASS");
		cws_msg_hash.f5r = 1;
		}
	if ((f5l > 1.0) and (cws_msg_hash.f5l == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    F RCS     ", "LJET", "12   ", 2, "PASS");
		cws_msg_hash.f5l = 1;
		}
	}


# Helium pressure
# Only in OPS 2 for PASS // OPS 1,3,6 for BFS
# Class 3 ( Sm Alert)

var fhep1 = getprop("/fdm/jsbsim/systems/rcs-hardware/helium-fwd-rcs-pressure-1-psia");
var fhep2 = getprop("/fdm/jsbsim/systems/rcs-hardware/helium-fwd-rcs-pressure-2-psia");


if ((fhep1 < 500.0) or (fhep2 < 500.0)) # helium pressure problem
	{
		
		if (ops == 2)
			{
			if (cws_msg_hash.fhep == 0)
				{
				create_fault_message("    F RCS     ", "He P", "12   ", 3, "PASS");
				cws_msg_hash.fhep = 1;
				}
			}
		else
			{	
			if (cws_msg_hash.fhep == 0)
				{
				create_fault_message("    F RCS     ", "He P", "    5", 3, "BFS");
				cws_msg_hash.fhep = 1;
				}
			}
	}

# propellant and oxidizer pressure
# Only in OPS 2 for PASS // OPS 1,3,6 for BFS
# Class 3 ( Sm Alert)

var fpp = getprop("/fdm/jsbsim/systems/rcs-hardware/tanks-fwd-rcs-blowdown-psia");
var fop = getprop("/fdm/jsbsim/systems/rcs-hardware/tanks-fwd-rcs-blowdown-psia");

if ((fpp < 200.0) or (fpp > 312.0) or (fop < 200.0) or (fop > 312.0))
	{
		
		if (ops == 2)
			{
			if (cws_msg_hash.fpop == 0)
				{
				create_fault_message("    F RCS     ", "TK P", "12   ", 3, "PASS");
				cws_msg_hash.fpop = 1;
				}
			}
		else
			{	
			if (cws_msg_hash.fpop == 0)
				{
				create_fault_message("    F RCS     ", "TK P", "    5", 3, "BFS");
				cws_msg_hash.fpop = 1;
				}
			}
	
	}

# leak detection
#PASS OPS 2,3 // BFS OPS 1,3,6
# Class 2 Hardware ( F,L,R RCS F7 light) and Soft (Backup alarm)

var foxidizer = getprop("/consumables/fuel/tank[12]/level-lbs")/1477.0;
var fpropellant = getprop("/consumables/fuel/tank[13]/level-lbs")/928.0;

if (math.abs(foxidizer - fpropellant) > 0.095) # we have a leak
	{
		#set a flag to link LEAK to F(L,R) RCS C/W F7 light in .xml
		setprop("/fdm/jsbsim/systems/cws/forward-leak", 1);

		
		if (ops == 2)  #OPS 2
			{
			if (cws_msg_hash.fleak == 0)
				{
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
				create_fault_message("    F RCS     ", "LEAK", "12   ", 2, "PASS");
				cws_msg_hash.fleak = 1;
				}
			}
		else if (ops == 3) # OPS 3
			{	
			if (cws_msg_hash.fleak == 0)
				{
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
				create_fault_message("    F RCS     ", "LEAK", "12   ", 2, "PASS");
				create_fault_message("    F RCS     ", "LEAK", "    5", 2, "BFS");
				cws_msg_hash.fleak = 1;
				}
			}
		else  #OPS 1/6
			{	
			if (cws_msg_hash.fleak == 0)
				{
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
				create_fault_message("    F RCS     ", "LEAK", "    5", 2, "BFS");
				cws_msg_hash.fleak = 1;
				}
			}
	}

#F RCS TEMP alert (T < 45° F// 280° K)
#PASS SM only
#Class 3 Sm Alert

var T_fwd = getprop("/fdm/jsbsim/systems/thermal-distribution/nose-temperature-K");
var heater_RCS_fwd = getprop("/fdm/jsbsim/systems/rcs-hardware/heater-fwd-operational");
    

if (ops == 2)
	{	
	if ((T_fwd < 280) and (heater_RCS_fwd == 0)) 
		{
		
		if (cws_msg_hash.rcsftemp == 0)
				{
				create_fault_message("S89 PRPLTTHERM", " RCS", "   4 ", 2, "PASS");
				cws_msg_hash.rcsftemp = 1;
				}
		}
	}

}


#################################################
# CWS checks of left RCS
#################################################

var cws_inspect_left_rcs_thrusters = func {

var ops =  getprop("/fdm/jsbsim/systems/dps/ops");

# LEFT manifold 1

var l1a = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-L1A-condition");
var l1l = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-L1L-condition");
var l1u = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-L1U-condition");


if (l1a + l1l + l1u < 3.0) # we have a manifold 1 fail off condition
	{
	setprop("/fdm/jsbsim/systems/cws/jet-fail-l1", 1);
	

	if ((l1a < 1.0) and (cws_msg_hash.l1a == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    L RCS     ", "AJET", "12   ", 2, "PASS");
		create_fault_message("    L RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.l1a = 1;
		}
	if ((l1l < 1.0) and (cws_msg_hash.l1l == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    L RCS     ", "LJET", "12   ", 2, "PASS");
		create_fault_message("    L RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.l1l = 1;
		}
	if ((l1u < 1.0) and (cws_msg_hash.l1u == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    L RCS     ", "UJET", "12   ", 2, "PASS");
		create_fault_message("    L RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.l1u = 1;
		}
	}
else if (l1a + l1l + l1u > 3.0) # we have a manifold 1 fail on condition
	{
	setprop("/fdm/jsbsim/systems/cws/jet-fail-l1", 2);
	

	if ((l1a > 1.0) and (cws_msg_hash.l1a == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    L RCS     ", "AJET", "12   ", 2, "PASS");
		create_fault_message("    L RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.l1a = 1;
		}
	if ((l1l > 1.0) and (cws_msg_hash.l1l == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    L RCS     ", "LJET", "12   ", 2, "PASS");
		create_fault_message("    L RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.l1l = 1;
		}
	if ((l1u > 1.0) and (cws_msg_hash.l1u == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    L RCS     ", "UJET", "12   ", 2, "PASS");
		create_fault_message("    L RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.l1u = 1;
		}
	}

# LEFT manifold 2

var l2u = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-L2U-condition");
var l2l = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-L2L-condition");
var l2d = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-L2D-condition");


if (l2u + l2l + l2d < 3.0) # we have a manifold 2 fail off condition
	{
	setprop("/fdm/jsbsim/systems/cws/jet-fail-l2", 1);
	

	if ((l2u < 1.0) and (cws_msg_hash.l2u == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    L RCS     ", "UJET", "12   ", 2, "PASS");
		create_fault_message("    L RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.l2u = 1;
		}
	if ((l2l < 1.0) and (cws_msg_hash.l2l == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    L RCS     ", "LJET", "12   ", 2, "PASS");
		create_fault_message("    L RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.l2l = 1;
		}
	if ((l2d < 1.0) and (cws_msg_hash.l2d == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    L RCS     ", "DJET", "12   ", 2, "PASS");
		create_fault_message("    L RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.l2d = 1;
		}
	}
else if (l2u + l2l + l2d > 3.0) # we have a manifold 2 fail on condition
	{
	setprop("/fdm/jsbsim/systems/cws/jet-fail-l2", 2);
	

	if ((l2u > 1.0) and (cws_msg_hash.l2u == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    L RCS     ", "UJET", "12   ", 2, "PASS");
		create_fault_message("    L RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.l2u = 1;
		}
	if ((l2l > 1.0) and (cws_msg_hash.l2l == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    L RCS     ", "LJET", "12   ", 2, "PASS");
		create_fault_message("    L RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.l2l = 1;
		}
	if ((l2d > 1.0) and (cws_msg_hash.l2d == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    L RCS     ", "DJET", "12   ", 2, "PASS");
		create_fault_message("    L RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.l2d = 1;
		}
	}

# LEFT manifold 3

var l3l = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-L3L-condition");
var l3a = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-L3A-condition");
var l3d = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-L3D-condition");


if (l3l + l3a + l3d < 3.0) # we have a manifold 3 fail off condition
	{
	setprop("/fdm/jsbsim/systems/cws/jet-fail-l3", 1);
	

	if ((l3l < 1.0) and (cws_msg_hash.l3l == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    L RCS     ", "LJET", "12   ", 2, "PASS");
		create_fault_message("    L RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.l3l = 1;
		}
	if ((l3a < 1.0) and (cws_msg_hash.l3a == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    L RCS     ", "AJET", "12   ", 2, "PASS");
		create_fault_message("    L RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.l3a = 1;
		}
	if ((l3d < 1.0) and (cws_msg_hash.l3d == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    L RCS     ", "DJET", "12   ", 2, "PASS");
		create_fault_message("    L RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.l3d = 1;
		}
	}
else if (l3l + l3a + l3d > 3.0) # we have a manifold 3 fail on condition
	{
	setprop("/fdm/jsbsim/systems/cws/jet-fail-l3", 2);
	

	if ((l3l > 1.0) and (cws_msg_hash.l3l == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    L RCS     ", "LJET", "12   ", 2, "PASS");
		create_fault_message("    L RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.l3l = 1;
		}
	if ((l3a > 1.0) and (cws_msg_hash.l3a == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    L RCS     ", "AJET", "12   ", 2, "PASS");
		create_fault_message("    L RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.l3a = 1;
		}
	if ((l3d > 1.0) and (cws_msg_hash.l3d == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    L RCS     ", "DJET", "12   ", 2, "PASS");
		create_fault_message("    L RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.l3d = 1;
		}
	}

# LEFT manifold 4

var l4u = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-L4U-condition");
var l4l = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-L4L-condition");
var l4d = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-L4D-condition");


if (l4u + l4l + l4d < 3.0) # we have a manifold 4 fail off condition
	{
	setprop("/fdm/jsbsim/systems/cws/jet-fail-l4", 1);
	

	if ((l4u < 1.0) and (cws_msg_hash.l4u == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    L RCS     ", "UJET", "12   ", 2, "PASS");
		create_fault_message("    L RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.l4u = 1;
		}
	if ((l4l < 1.0) and (cws_msg_hash.l4l == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    L RCS     ", "LJET", "12   ", 2, "PASS");
		create_fault_message("    L RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.l4l = 1;
		}
	if ((l4d < 1.0) and (cws_msg_hash.l4d == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    L RCS     ", "DJET", "12   ", 2, "PASS");
		create_fault_message("    L RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.l4d = 1;
		}
	}
else if (l4u + l4l + l4d > 3.0) # we have a manifold 4 fail on condition
	{
	setprop("/fdm/jsbsim/systems/cws/jet-fail-l4", 2);
	

	if ((l4u > 1.0) and (cws_msg_hash.l4u == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    L RCS     ", "UJET", "12   ", 2, "PASS");
		create_fault_message("    L RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.l4u = 1;
		}
	if ((l4l > 1.0) and (cws_msg_hash.l4l == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    L RCS     ", "LJET", "12   ", 2, "PASS");
		create_fault_message("    L RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.l4l = 1;
		}
	if ((l4d > 1.0) and (cws_msg_hash.l4d == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    L RCS     ", "DJET", "12   ", 2, "PASS");
		create_fault_message("    L RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.l4d = 1;
		}
	}

# LEFT manifold 5 ( No BFS monitoring and fault for Vernier jets as not used when ops !=2)

var l5d = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-L5D-condition");
var l5l = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-L5L-condition");



if (l5d + l5l < 2.0) # we have a manifold 5 fail off condition
	{
	setprop("/fdm/jsbsim/systems/cws/jet-fail-l5", 1);
	

	if ((l5d < 1.0) and (cws_msg_hash.l5d == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    L RCS     ", "DJET", "12   ", 2, "PASS");
		cws_msg_hash.l5d = 1;
		}
	if ((l5l < 1.0) and (cws_msg_hash.l5l == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    L RCS     ", "LJET", "12   ", 2, "PASS");
		cws_msg_hash.l5l = 1;
		}
	}
else if (l5d + l5l > 2.0) # we have a manifold 5 fail on condition
	{
	setprop("/fdm/jsbsim/systems/cws/jet-fail-l5", 2);
	

	if ((l5d > 1.0) and (cws_msg_hash.l5d == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    L RCS     ", "DJET", "12   ", 2, "PASS");
		cws_msg_hash.l5d = 1;
		}
	if ((l5l > 1.0) and (cws_msg_hash.l5l == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    L RCS     ", "LJET", "12   ", 2, "PASS");
		cws_msg_hash.l5l = 1;
		}
	}


# Helium pressure
# Only in OPS 2 for PASS // OPS 1,3,6 for BFS

var lhep1 = getprop("/fdm/jsbsim/systems/rcs-hardware/helium-left-rcs-pressure-1-psia");
var lhep2 = getprop("/fdm/jsbsim/systems/rcs-hardware/helium-left-rcs-pressure-2-psia");


if ((lhep1 < 500.0) or (lhep2 < 500.0)) # helium pressure problem
	{
		
		if (ops == 2)
			{
			if (cws_msg_hash.lhep == 0)
				{
				create_fault_message("    L RCS     ", "He P", "12   ", 3, "PASS");
				cws_msg_hash.lhep = 1;
				}
			}
		else
			{	
			if (cws_msg_hash.lhep == 0)
				{
				create_fault_message("    L RCS     ", "He P", "    5", 3, "BFS");
				cws_msg_hash.lhep = 1;
				}
			}
	}

# propellant and oxidizer pressure
# Only in OPS 2 for PASS // OPS 1,3,6 for BFS

var lpp = getprop("/fdm/jsbsim/systems/rcs-hardware/tanks-left-rcs-blowdown-psia");
var lop = getprop("/fdm/jsbsim/systems/rcs-hardware/tanks-left-rcs-blowdown-psia");


if ((lpp < 200.0) or (lpp > 312.0) or (lop < 200.0) or (lop > 312.0))
	{
		
		if (ops == 2)
			{
			if (cws_msg_hash.lpop == 0)
				{
				create_fault_message("    L RCS     ", "TK P", "12   ", 3, "PASS");
				cws_msg_hash.lpop = 1;
				}
			}
		else
			{	
			if (cws_msg_hash.lpop == 0)
				{
				create_fault_message("    L RCS     ", "TK P", "    5", 3, "BFS");
				cws_msg_hash.lpop = 1;
				}
			}
	
	}

# leak detection
#PASS OPS 2,3 // BFS OPS 1,3,6

var loxidizer = getprop("/consumables/fuel/tank[8]/level-lbs")/1477.0;
var lpropellant = getprop("/consumables/fuel/tank[9]/level-lbs")/928.0;


if (math.abs(loxidizer - lpropellant) > 0.095) # we have a leak
	{
		setprop("/fdm/jsbsim/systems/cws/aft-left-leak", 1);
		

		if (ops == 2)  #OPS 2
			{
			if (cws_msg_hash.lleak == 0)
				{
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
				create_fault_message("    L RCS     ", "LEAK", "12   ", 2, "PASS");
				cws_msg_hash.lleak = 1;
				}
			}
		else if (ops == 3) # OPS 3
			{	
			if (cws_msg_hash.lleak == 0)
				{
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
				create_fault_message("    L RCS     ", "LEAK", "12   ", 2, "PASS");
				create_fault_message("    L RCS     ", "LEAK", "    5", 2, "BFS");
				cws_msg_hash.lleak = 1;
				}
			}
		else  #OPS 1/6
			{	
			if (cws_msg_hash.lleak == 0)
				{
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
				create_fault_message("    L RCS     ", "LEAK", "    5", 2, "BFS");
				cws_msg_hash.lleak = 1;
				}
			}
	}


# automatic switch to NO Y JET in case of multiple yaw jet failures

if ((l1l + l2l + l3l + l4l) < 2.0)
	{
	if (cws_msg_hash.no_y_jet_switchover == 0)
		{
		var ops = getprop("/fdm/jsbsim/systems/dps/ops");
		var qbar = getprop("/fdm/jsbsim/aero/qbar-psf");
		var switch = getprop("/fdm/jsbsim/systems/fcs/entry-mode-switch");
		var mach = getprop("/fdm/jsbsim/velocities/mach");

		if ((ops ==3) and (qbar > 10.0) and (switch == 0) and (mach > 3.5))		
			{
			setprop("/fdm/jsbsim/systems/fcs/rcs-yaw-mode", 0);
			setprop("/fdm/jsbsim/systems/fcs/no-y-jet", 1);
			print("Switching entry mode to NO Y JET"); 
			cws_msg_hash.no_y_jet_switchover = 1;
			}
		}

	}


}  		



#################################################
# CWS checks of right RCS
#################################################

var cws_inspect_right_rcs_thrusters = func {

var ops =  getprop("/fdm/jsbsim/systems/dps/ops");

# RIGHT manifold 1

var r1a = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-R1A-condition");
var r1r = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-R1R-condition");
var r1u = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-R1U-condition");


if (r1a + r1r + r1u < 3.0) # we have a manifold 1 fail off condition
	{
	setprop("/fdm/jsbsim/systems/cws/jet-fail-r1", 1);
	

	if ((r1a < 1.0) and (cws_msg_hash.r1a == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    R RCS     ", "AJET", "12   ", 2, "PASS");
		create_fault_message("    R RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.r1a = 1;
		}
	if ((r1r < 1.0) and (cws_msg_hash.r1r == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    R RCS     ", "RJET", "12   ", 2, "PASS");
		create_fault_message("    R RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.r1r = 1;
		}
	if ((r1u < 1.0) and (cws_msg_hash.r1u == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    R RCS     ", "UJET", "12   ", 2, "PASS");
		create_fault_message("    R RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.r1u = 1;
		}
	}
else if (r1a + r1r + r1u > 3.0) # we have a manifold 1 fail on condition
	{
	setprop("/fdm/jsbsim/systems/cws/jet-fail-r1", 2);
	

	if ((r1a > 1.0) and (cws_msg_hash.r1a == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    R RCS     ", "AJET", "12   ", 2, "PASS");
		create_fault_message("    R RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.r1a = 1;
		}
	if ((r1r > 1.0) and (cws_msg_hash.r1r == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    R RCS     ", "RJET", "12   ", 2, "PASS");
		create_fault_message("    R RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.r1r = 1;
		}
	if ((r1u > 1.0) and (cws_msg_hash.r1u == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    R RCS     ", "UJET", "12   ", 2, "PASS");
		create_fault_message("    R RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.r1u = 1;
		}
	}

# RIGHT manifold 2

var r2u = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-R2U-condition");
var r2r = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-R2R-condition");
var r2d = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-R2D-condition");


if (r2u + r2r + r2d < 3.0) # we have a manifold 2 fail off condition
	{
	setprop("/fdm/jsbsim/systems/cws/jet-fail-r2", 1);
	

	if ((r2u < 1.0) and (cws_msg_hash.r2u == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    R RCS     ", "UJET", "12   ", 2, "PASS");
		create_fault_message("    R RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.r2u = 1;
		}
	if ((r2r < 1.0) and (cws_msg_hash.r2r == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    R RCS     ", "RJET", "12   ", 2, "PASS");
		create_fault_message("    R RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.r2r = 1;
		}
	if ((r2d < 1.0) and (cws_msg_hash.r2d == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    R RCS     ", "DJET", "12   ", 2, "PASS");
		create_fault_message("    R RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.r2d = 1;
		}
	}
else if (r2u + r2r + r2d > 3.0) # we have a manifold 2 fail on condition
	{
	setprop("/fdm/jsbsim/systems/cws/jet-fail-r2", 2);
	

	if ((r2u > 1.0) and (cws_msg_hash.r2u == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    R RCS     ", "UJET", "12   ", 2, "PASS");
		create_fault_message("    R RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.r2u = 1;
		}
	if ((r2r > 1.0) and (cws_msg_hash.r2r == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    R RCS     ", "RJET", "12   ", 2, "PASS");
		create_fault_message("    R RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.r2r = 1;
		}
	if ((r2d > 1.0) and (cws_msg_hash.r2d == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    R RCS     ", "DJET", "12   ", 2, "PASS");
		create_fault_message("    R RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.r2d = 1;
		}
	}

# RIGHT manifold 3

var r3r = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-R3R-condition");
var r3a = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-R3A-condition");
var r3d = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-R3D-condition");


if (r3r + r3a + r3d < 3.0) # we have a manifold 3 fail off condition
	{
	setprop("/fdm/jsbsim/systems/cws/jet-fail-r3", 1);
	

	if ((r3r < 1.0) and (cws_msg_hash.r3r == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    R RCS     ", "RJET", "12   ", 2, "PASS");
		create_fault_message("    R RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.r3r = 1;
		}
	if ((r3a < 1.0) and (cws_msg_hash.r3a == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    R RCS     ", "AJET", "12   ", 2, "PASS");
		create_fault_message("    R RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.r3a = 1;
		}
	if ((r3d < 1.0) and (cws_msg_hash.r3d == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    R RCS     ", "DJET", "12   ", 2, "PASS");
		create_fault_message("    R RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.r3d = 1;
		}
	}
else if (r3r + r3a + r3d > 3.0) # we have a manifold 3 fail on condition 
	{
	setprop("/fdm/jsbsim/systems/cws/jet-fail-r3", 2);
	

	if ((r3r > 1.0) and (cws_msg_hash.r3r == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    R RCS     ", "RJET", "12   ", 2, "PASS");
		create_fault_message("    R RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.r3r = 1;
		}
	if ((r3a > 1.0) and (cws_msg_hash.r3a == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    R RCS     ", "AJET", "12   ", 2, "PASS");
		create_fault_message("    R RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.r3a = 1;
		}
	if ((r3d > 1.0) and (cws_msg_hash.r3d == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    R RCS     ", "DJET", "12   ", 2, "PASS");
		create_fault_message("    R RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.r3d = 1;
		}
	}

# RIGHT manifold 4

var r4u = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-R4U-condition");
var r4r = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-R4R-condition");
var r4d = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-R4D-condition");


if (r4u + r4r + r4d < 3.0) # we have a manifold 4 fail off condition
	{
	setprop("/fdm/jsbsim/systems/cws/jet-fail-r4", 1);
	

	if ((r4u < 1.0) and (cws_msg_hash.r4u == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    R RCS     ", "UJET", "12   ", 2, "PASS");
		create_fault_message("    R RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.r4u = 1;
		}
	if ((r4r < 1.0) and (cws_msg_hash.r4r == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    R RCS     ", "RJET", "12   ", 2, "PASS");
		create_fault_message("    R RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.r4r = 1;
		}
	if ((r4d < 1.0) and (cws_msg_hash.r4d == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    R RCS     ", "DJET", "12   ", 2, "PASS");
		create_fault_message("    R RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.r4d = 1;
		}
	}
else if (r4u + r4r + r4d > 3.0) # we have a manifold 4 fail on condition
	{
	setprop("/fdm/jsbsim/systems/cws/jet-fail-r4", 2);
	

	if ((r4u > 1.0) and (cws_msg_hash.r4u == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    R RCS     ", "UJET", "12   ", 2, "PASS");
		create_fault_message("    R RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.r4u = 1;
		}
	if ((r4r > 1.0) and (cws_msg_hash.r4r == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    R RCS     ", "RJET", "12   ", 2, "PASS");
		create_fault_message("    R RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.r4r = 1;
		}
	if ((r4d > 1.0) and (cws_msg_hash.r4d == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    R RCS     ", "DJET", "12   ", 2, "PASS");
		create_fault_message("    R RCS     ", " JET", "    5", 2, "BFS");
		cws_msg_hash.r4d = 1;
		}
	}

# RIGHT manifold 5 ( No BFS monitoring and fault for Vernier jets as not used when ops !=2)

var r5d = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-R5D-condition");
var r5r = getprop("/fdm/jsbsim/systems/failures/rcs/rcs-R5R-condition");



if (r5d + r5r < 2.0) # we have a manifold 5 fail off condition
	{
	setprop("/fdm/jsbsim/systems/cws/jet-fail-r5", 1);
	

	if ((r5d < 1.0) and (cws_msg_hash.r5d == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    R RCS     ", "DJET", "12   ", 2, "PASS");
		cws_msg_hash.r5d = 1;
		}
	if ((r5r < 1.0) and (cws_msg_hash.r5r == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    R RCS     ", "RJET", "12   ", 2, "PASS");
		cws_msg_hash.r5r = 1;
		}
	}
else if (r5d + r5r > 2.0) # we have a manifold 5 fail on condition
	{
	setprop("/fdm/jsbsim/systems/cws/jet-fail-r5", 2);
	

	if ((r5d > 1.0) and (cws_msg_hash.r5d == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    R RCS     ", "DJET", "12   ", 2, "PASS");
		cws_msg_hash.r5d = 1;
		}
	if ((r5r > 1.0) and (cws_msg_hash.r5r == 0))
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    R RCS     ", "RJET", "12   ", 2, "PASS");
		cws_msg_hash.r5r = 1;
		}
	}

		
# Helium pressure
# Only in OPS 2 for PASS // OPS 1,3,6 for BFS

var rhep1 = getprop("/fdm/jsbsim/systems/rcs-hardware/helium-right-rcs-pressure-1-psia");
var rhep2 = getprop("/fdm/jsbsim/systems/rcs-hardware/helium-right-rcs-pressure-2-psia");



if ((rhep1 < 500.0) or (rhep2 < 500.0)) # helium pressure problem
	{
		
		if (ops == 2)
			{
			if (cws_msg_hash.rhep == 0)
				{
				create_fault_message("    R RCS     ", "He P", "12   ", 3, "PASS");
				cws_msg_hash.rhep = 1;
				}
			}
		else
			{	
			if (cws_msg_hash.rhep == 0)
				{
				create_fault_message("    R RCS     ", "He P", "    5", 3, "BFS");
				cws_msg_hash.rhep = 1;
				}
			}
	}

# propellant and oxidizer pressure
# Only in OPS 2 for PASS // OPS 1,3,6 for BFS

var rpp = getprop("/fdm/jsbsim/systems/rcs-hardware/tanks-right-rcs-blowdown-psia");
var rop = getprop("/fdm/jsbsim/systems/rcs-hardware/tanks-right-rcs-blowdown-psia");


if ((rpp < 200.0) or (rpp > 312.0) or (rop < 200.0) or (rop > 312.0))
	{
		
		if (ops == 2)
			{
			if (cws_msg_hash.rpop == 0)
				{
				create_fault_message("    R RCS     ", "TK P", "12   ", 3, "PASS");
				cws_msg_hash.rpop = 1;
				}
			}
		else
			{	
			if (cws_msg_hash.rpop == 0)
				{
				create_fault_message("    R RCS     ", "TK P", "    5", 3, "BFS");
				cws_msg_hash.rpop = 1;
				}
			}
	
	}

# leak detection
#PASS OPS 2,3 // BFS OPS 1,3,6

var roxidizer = getprop("/consumables/fuel/tank[10]/level-lbs")/1477.0;
var rpropellant = getprop("/consumables/fuel/tank[11]/level-lbs")/928.0;



if (math.abs(roxidizer - rpropellant) > 0.095) # we have a leak
	{
		setprop("/fdm/jsbsim/systems/cws/aft-right-leak", 1);
		

		if (ops == 2)  #OPS 2
			{
			if (cws_msg_hash.rleak == 0)
				{
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
				create_fault_message("    R RCS     ", "LEAK", "12   ", 2, "PASS");
				cws_msg_hash.rleak = 1;
				}
			}
		else if (ops == 3) # OPS 3
			{	
			if (cws_msg_hash.rleak == 0)
				{
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
				create_fault_message("    R RCS     ", "LEAK", "12   ", 2, "PASS");
				create_fault_message("    R RCS     ", "LEAK", "    5", 2, "BFS");
				cws_msg_hash.rleak = 1;
				}
			}
		else  #OPS 1/6
			{	
			if (cws_msg_hash.rleak == 0)
				{
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
				create_fault_message("    R RCS     ", "LEAK", "    5", 2, "BFS");
				cws_msg_hash.rleak = 1;
				}
			}
	}


# automatic switch to NO Y JET in case of multiple yaw jet failures

if ((r1r + r2r + r3r + r4r) < 2.0)
	{
	if (cws_msg_hash.no_y_jet_switchover == 0)
		{
		var ops = getprop("/fdm/jsbsim/systems/dps/ops");
		var qbar = getprop("/fdm/jsbsim/aero/qbar-psf");
		var switch = getprop("/fdm/jsbsim/systems/fcs/entry-mode-switch");
		var mach = getprop("/fdm/jsbsim/velocities/mach");

		if ((ops ==3) and (qbar > 10.0) and (switch == 0) and (mach > 3.5))		
			{
			setprop("/fdm/jsbsim/systems/fcs/rcs-yaw-mode", 0);
			setprop("/fdm/jsbsim/systems/fcs/no-y-jet", 1);
			print("Switching entry mode to NO Y JET"); 
			cws_msg_hash.no_y_jet_switchover = 1;
			}
		}

	}


}  		




#################################################
# CWS checks of OMS
#################################################

var cws_inspect_oms = func {

#Only Class 2 hardware (F7 lights) and class 3 Sm alert for OMS  C/W

var mm =  getprop("/fdm/jsbsim/systems/dps/major-mode");


if ((mm == 304) or (mm == 305)) {return;}

var left_engine_throttle = getprop("/fdm/jsbsim/fcs/throttle-cmd-norm[5]");
var right_engine_throttle = getprop("/fdm/jsbsim/fcs/throttle-cmd-norm[6]");

var left_engine_on = 0;
var right_engine_on = 0;

if (left_engine_throttle > 0.8) {left_engine_on = 1;}
if (right_engine_throttle > 0.8) {right_engine_on = 1;}

# OMS gimbal

var gimbal_left_pri = getprop("/fdm/jsbsim/systems/oms-hardware/gimbal-left-pri-selected");
var gimbal_left_sec = getprop("/fdm/jsbsim/systems/oms-hardware/gimbal-left-sec-selected");
var gimbal_right_pri = getprop("/fdm/jsbsim/systems/oms-hardware/gimbal-right-pri-selected");
var gimbal_right_sec = getprop("/fdm/jsbsim/systems/oms-hardware/gimbal-right-sec-selected");

var gimbal_check = getprop("/fdm/jsbsim/systems/oms-hardware/gimbal-chk-cmd");

#gimbal-left-pri-selected
#Same message for PASS and BFS// OPS1 -> 6 GNC

if (gimbal_left_pri == 1)
	{var omslg = getprop("/fdm/jsbsim/systems/failures/oms/oms-left-pri-gimbal-condition");}
else
	{var omslg = getprop("/fdm/jsbsim/systems/failures/oms/oms-left-sec-gimbal-condition");}

if (gimbal_right_pri == 1)
	{var omsrg = getprop("/fdm/jsbsim/systems/failures/oms/oms-right-pri-gimbal-condition");}
else
	{var omsrg = getprop("/fdm/jsbsim/systems/failures/oms/oms-right-sec-gimbal-condition");}

if ((omslg < 0.8) and ((left_engine_on == 1) or (gimbal_check == 1)))
	{
		
		if (cws_msg_hash.omslg == 0)
		{
		create_fault_message("    L OMS     ", "GMBL", "12   ", 3, "PASS");
		create_fault_message("    L OMS     ", "GMBL", "    5", 3, "BFS");
		cws_msg_hash.omslg = 1;
		}
	}

if ((omsrg < 0.8) and ((right_engine_on == 1)or (gimbal_check == 1)))
	{
		
		if (cws_msg_hash.omsrg == 0)
		{
		create_fault_message("    R OMS     ", "GMBL", "12   ", 3, "PASS");
		create_fault_message("    R OMS     ", "GMBL", "    5", 3, "BFS");
		cws_msg_hash.omslg = 1;
		cws_msg_hash.omsrg = 1;
		}
	}


# inspect remaining OMS fuel quantity
# PASS GNC Only



var omsloqty =  getprop("/consumables/fuel/tank[4]/level-lbs")/7773.0;
var omslpqty =  getprop("/consumables/fuel/tank[5]/level-lbs")/4718.0;

var omsroqty =  getprop("/consumables/fuel/tank[6]/level-lbs")/7773.0;
var omsrpqty =  getprop("/consumables/fuel/tank[7]/level-lbs")/4718.0;

if ((omsloqty < 0.05) or (omslpqty < 0.05))
	{
		
		if (cws_msg_hash.omslqty == 0)
		{
		create_fault_message("    L OMS     ", " QTY", "12   ", 3, "PASS");
		cws_msg_hash.omslqty = 1;
		}
	}

if ((omsroqty < 0.05) or (omsrpqty < 0.05))
	{
		
		if (cws_msg_hash.omsrqty == 0)
		{
		create_fault_message("    R OMS     ", " QTY", "12   ", 3, "PASS");
		cws_msg_hash.omsrqty = 1;
		}
	}

# OMS chamber pressure
#Same message for PASS and BFS// OPS1 -> 6 GNC

var left_oms_pc = getprop("/fdm/jsbsim/systems/oms-hardware/chamber-left-pc-percent");
var right_oms_pc = getprop("/fdm/jsbsim/systems/oms-hardware/chamber-right-pc-percent");

if ((left_oms_pc < 80.0) and (left_engine_on == 1))
	{
		
		if (cws_msg_hash.omslpc == 0)
		{
		create_fault_message("    L OMS     ", "  PC", "12   ", 2, "PASS");
		create_fault_message("    L OMS     ", "  PC", "    5", 2, "BFS");
		cws_msg_hash.omslpc = 1;
		}
	}

if ((right_oms_pc < 80.0) and (right_engine_on == 1))
	{
		
		if (cws_msg_hash.omsrpc == 0)
		{
		create_fault_message("    R OMS     ", "  PC", "12   ", 2, "PASS");
		create_fault_message("    R OMS     ", "  PC", "    5", 2, "BFS");
		cws_msg_hash.omsrpc = 1;
		}
	}

# OMS tank pressures
#PASS GNC only for OPS 2 // BFS only elsewhere

var left_oms_N2_p = getprop("/fdm/jsbsim/systems/oms-hardware/n2-left-oms-pressure-psia");
var left_oms_N2_reg_p = getprop("/fdm/jsbsim/systems/oms-hardware/n2-left-reg-pressure-psia");
var left_oms_He_p = getprop("/fdm/jsbsim/systems/oms-hardware/helium-left-oms-pressure-sh-psia");
var left_oms_tank_p = getprop("/fdm/jsbsim/systems/oms-hardware/tanks-left-oms-blowdown-psia");


var right_oms_N2_p = getprop("/fdm/jsbsim/systems/oms-hardware/n2-right-oms-pressure-psia");
var right_oms_N2_reg_p = getprop("/fdm/jsbsim/systems/oms-hardware/n2-right-reg-pressure-psia");
var right_oms_He_p = getprop("/fdm/jsbsim/systems/oms-hardware/helium-right-oms-pressure-sh-psia");
var right_oms_tank_p = getprop("/fdm/jsbsim/systems/oms-hardware/tanks-right-oms-blowdown-psia");

if ((left_oms_N2_p < 1200.0) or (left_oms_N2_reg_p < 299.0) or (left_oms_N2_reg_p > 434) or (left_oms_He_p < 1500.0) or (left_oms_tank_p > 288.0) or (left_oms_tank_p < 234.0))
	{
		
		if ((mm == 201) or (mm == 202))
			{
			if (cws_msg_hash.omsltkp == 0)
				{
				create_fault_message("    L OMS     ", "TK P", "12   ", 3, "PASS");
				cws_msg_hash.omsltkp = 1;
				}
			}
		else
			{
			if (cws_msg_hash.omsltkp == 0)
				{
				create_fault_message("    L OMS     ", "TK P", "    5", 3, "BFS");
				cws_msg_hash.omsltkp = 1;
				}
			}

	}

if ((right_oms_N2_p < 1200.0) or (right_oms_N2_reg_p < 299.0) or (right_oms_N2_reg_p > 434) or (right_oms_He_p < 1500.0) or (right_oms_tank_p > 288.0) or (right_oms_tank_p < 234.0))
	{
		
		if ((mm == 201) or (mm == 202))
			{
			if (cws_msg_hash.omsrtkp == 0)
				{
				create_fault_message("    R OMS     ", "TK P", "12   ", 3, "PASS");
				cws_msg_hash.omsrtkp = 1;
				}
			}
		else
			{
			if (cws_msg_hash.omsrtkp == 0)
				{
				create_fault_message("    R OMS     ", "TK P", "    5", 3, "BFS");
				cws_msg_hash.omsrtkp = 1;
				}
			}
	}


# OMS POD and AFT RCS temperature alert ( < 45 °F // 280 ° K) (OMS POD and AFT RCS triggered by same heater switches)
# 
#PASS SM only

	#OMS POD and AFT RCS temp

var T_left_raw = getprop("/fdm/jsbsim/systems/thermal-distribution/left-pod-temperature-K");
var T_right_raw = getprop("/fdm/jsbsim/systems/thermal-distribution/right-pod-temperature-K");
var heater_OMS_left = getprop("/fdm/jsbsim/systems/oms-hardware/heater-left-operational");
var heater_OMS_right = getprop("/fdm/jsbsim/systems/oms-hardware/heater-right-operational");

	#Crossfeed lines temp

var T_aft = getprop("/fdm/jsbsim/systems/thermal-distribution/aft-temperature-K");
var heater_OMS_crossfeed = getprop("/fdm/jsbsim/systems/oms-hardware/heater-crossfeed-operational");
T_left = (T_left_raw + T_aft)/2.0;
T_right = (T_right_raw + T_aft)/2.0;
    

if ((mm == 201) or (mm == 202))
	{
	#OMS POD and AFT² RCS thermal limits
	if (((T_left_raw < 280) and (heater_OMS_left == 0)) or ((T_right_raw < 280) and (heater_OMS_right == 0)))
		{
		
		if (cws_msg_hash.omstemp == 0)
				{
				create_fault_message("S89 PRPLTTHERM", " POD", "   4 ", 2, "PASS");
				create_fault_message("S89 PRPLTTHERM", " RCS", "   4 ", 2, "PASS");
				cws_msg_hash.omstemp = 1;
				}
		}

	#Crossfeed lines thermal limits

	if (((T_aft < 280) or (T_left < 280) or (T_right < 280)) and (heater_OMS_crossfeed == 0))
		{
		
		if (cws_msg_hash.xfeedtemp == 0)
				{
				create_fault_message("S89 PRPLTTHERM", " OMS", "   4 ", 2, "PASS");
				cws_msg_hash.xfeedtemp = 1;
				}
		}

	}


else #BFS
	{
	#OMS POD thermal limits
	if (((T_left_raw < 280) and (heater_OMS_left == 0)) or ((T_right_raw < 280) and (heater_OMS_right == 0)))
		{
		
		if (cws_msg_hash.omstemp == 0)
				{
				create_fault_message("SM0 THRM PRPLT", " POD", "    5", 2, "BFS");
				cws_msg_hash.omstemp = 1;
				}
		}

	#Crossfeed lines thermal limits

	if (((T_aft < 280) or (T_left < 280) or (T_right < 280)) and (heater_OMS_crossfeed == 0))
		{
		
		if (cws_msg_hash.xfeedtemp == 0)
				{
				create_fault_message("SM0 THRM PRPLT", " OMS", "    5", 2, "BFS");
				cws_msg_hash.xfeedtemp = 1;
				}
		}
	}
	


}



#################################################
# CWS checks of fuel cell and electric systems
#################################################

var cws_inspect_fc_electric = func {

var init_phase = getprop("/fdm/jsbsim/systems/electrical/init-electrical-on");
var ops = getprop("/fdm/jsbsim/systems/dps/ops");

if (init_phase > 0.0) {init_phase = 1.0;} else {init_phase = 0.0;}




#Electric variables

var voltage_ac1 = getprop("/fdm/jsbsim/systems/electrical/ac/voltage");
var voltage_ac2 = getprop("/fdm/jsbsim/systems/electrical/ac[1]/voltage");
var voltage_ac3 = getprop("/fdm/jsbsim/systems/electrical/ac[2]/voltage");

var power_ac1 = getprop("/fdm/jsbsim/systems/electrical/ac/power-demand-kW");
var power_ac2 = getprop("/fdm/jsbsim/systems/electrical/ac[1]/power-demand-kW");
var power_ac3 = getprop("/fdm/jsbsim/systems/electrical/ac[2]/power-demand-kW");

var fc_voltage1 = getprop("/fdm/jsbsim/systems/electrical/fc/voltage");
var fc_voltage2 = getprop("/fdm/jsbsim/systems/electrical/fc[1]/voltage");
var fc_voltage3 = getprop("/fdm/jsbsim/systems/electrical/fc[2]/voltage");

var voltage_mainA = getprop("/fdm/jsbsim/systems/electrical/bus/voltage");
var voltage_mainB = getprop("/fdm/jsbsim/systems/electrical/bus[1]/voltage");
var voltage_mainC = getprop("/fdm/jsbsim/systems/electrical/bus[2]/voltage");

var power_usage1 = getprop("/fdm/jsbsim/systems/electrical/bus/power-demand-kW") * 1000;
var power_usage2 = getprop("/fdm/jsbsim/systems/electrical/bus[1]/power-demand-kW") * 1000;
var power_usage3 = getprop("/fdm/jsbsim/systems/electrical/bus[2]/power-demand-kW") * 1000;

var bus_connector1 = getprop("/fdm/jsbsim/systems/electrical/fc/bus-connector-status");
var bus_connector2 = getprop("/fdm/jsbsim/systems/electrical/fc[1]/bus-connector-status");
var bus_connector3 = getprop("/fdm/jsbsim/systems/electrical/fc[2]/bus-connector-status");

var amps1 = power_usage1/fc_voltage1 * bus_connector1;
var amps2 = power_usage2/fc_voltage2 * bus_connector2;
var amps3 = power_usage3/fc_voltage3 * bus_connector3;
if (fc_voltage1 == 0.0) {amps1 = 0.0;}
if (fc_voltage2 == 0.0) {amps2 = 0.0;}
if (fc_voltage3 == 0.0) {amps3 = 0.0;}

var ac_bus_sensor1 =  getprop("/fdm/jsbsim/systems/electrical/ac/ac-bus-snsr");
var ac_bus_sensor2 =  getprop("/fdm/jsbsim/systems/electrical/ac[1]/ac-bus-snsr");
var ac_bus_sensor3 =  getprop("/fdm/jsbsim/systems/electrical/ac[2]/ac-bus-snsr");

#FC element variables

var stack_T1 = getprop("/fdm/jsbsim/systems/electrical/fc/stack-temperature-K");
var stack_T2 = getprop("/fdm/jsbsim/systems/electrical/fc[1]/stack-temperature-K");
var stack_T3 = getprop("/fdm/jsbsim/systems/electrical/fc[2]/stack-temperature-K");

var running1 = getprop("/fdm/jsbsim/systems/electrical/fc/fc-running");
var running2 = getprop("/fdm/jsbsim/systems/electrical/fc[1]/fc-running");
var running3 = getprop("/fdm/jsbsim/systems/electrical/fc[2]/fc-running");

var condition1 = getprop("/fdm/jsbsim/systems/failures/fc1-coolant-pump-condition");
var condition2 = getprop("/fdm/jsbsim/systems/failures/fc2-coolant-pump-condition");
var condition3 = getprop("/fdm/jsbsim/systems/failures/fc3-coolant-pump-condition");

var coolp1_pump = condition1 * running1;
var coolp2_pump = condition2 * running2;
var coolp3_pump = condition3 * running3;

var fc1_reac_valve = getprop("/fdm/jsbsim/systems/electrical/fc/reactant-valve-status");
var fc2_reac_valve = getprop("/fdm/jsbsim/systems/electrical/fc[1]/reactant-valve-status");
var fc3_reac_valve = getprop("/fdm/jsbsim/systems/electrical/fc[2]/reactant-valve-status");





	

if (init_phase == 0) # general condition for elec failure
	{	
	#PASS SM failure (OPS2)
	if (ops == 2)
		{	


		###AC VOLTAGE ( 108 V < ACv < 123 V) 3AC routine checks (F7 light and soft class2 Back up) // No overvoltage in sim
		#3 differents Ac hash to have multiple failures of the same type ( 2 or 3 AC down )

		if (voltage_ac1 < 108.0) 
			{
			
			if (cws_msg_hash.acvolt1 == 0) 
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("S67 AC VOLTS  ", "   1", "   4 ", 2, "PASS");
				cws_msg_hash.acvolt1 = 1;
				}
			}
		if (voltage_ac2 < 108.0)
			{
				if (cws_msg_hash.acvolt2 == 0)
				{	
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);		
				create_fault_message("S67 AC VOLTS  ", "   2", "   4 ", 2, "PASS");
				cws_msg_hash.acvolt2 = 1;
				}
			}
		if (voltage_ac3 < 108.0)
			{
				if (cws_msg_hash.acvolt3 == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("S67 AC VOLTS  ", "   3", "   4 ", 2, "PASS");
				cws_msg_hash.acvolt3 = 1;
				}
			}


		###AC overload ( to link to F7 C/W red OVLD light)
		#Trigger for that is Ac power demand that goes crazy in case of Ac shortcut

		if (power_ac1 > 7.0)
			{
			if (cws_msg_hash.acovld1 == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("S67 AC OVLD   ", "   1", "   4 ", 2, "PASS");
				cws_msg_hash.acovld1 = 1;
				if (ac_bus_sensor1 == 1) {setprop("/fdm/jsbsim/systems/electrical/ac/inv-ac-switch", 0);} #Autotrip ---> disconnect
				}
			}
		if (power_ac2 > 7.0)
			{
			if (cws_msg_hash.acovld2 == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("S67 AC OVLD   ", "   2", "   4 ", 2, "PASS");
				cws_msg_hash.acovld2 = 1;
				if (ac_bus_sensor2 == 1) {setprop("/fdm/jsbsim/systems/electrical/ac[1]/inv-ac-switch", 0);}
				}
			}
		if (power_ac3 > 7.0)
			{
			if (cws_msg_hash.acovld3 == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("S67 AC OVLD   ", "   3", "   4 ", 2, "PASS");
				cws_msg_hash.acovld3 = 1;
				if (ac_bus_sensor3 == 1) {setprop("/fdm/jsbsim/systems/electrical/ac[2]/inv-ac-switch", 0);}
				}
			}
			

		###FC Volt // Class 3

		if ((fc_voltage1 < 27.5) or (fc_voltage1 > 32))
			{
			if (cws_msg_hash.fcvolt1 == 0)
				{			
				create_fault_message("S69 FC VOLTS  ", "   1", "   4 ", 2, "PASS");
				cws_msg_hash.fcvolt1 = 1;
				}
			}

		if ((fc_voltage2 < 27.5) or (fc_voltage2 > 32))
			{
			if (cws_msg_hash.fcvolt2 == 0)
				{			
				create_fault_message("S69 FC VOLTS  ", "   2", "   4 ", 2, "PASS");
				cws_msg_hash.fcvolt2 = 1;
				}
			}

		if ((fc_voltage3 < 27.5) or (fc_voltage3 > 32))
			{
			if (cws_msg_hash.fcvolt3 == 0)
				{			
				create_fault_message("S69 FC VOLTS  ", "   3", "   4 ", 2, "PASS");
				cws_msg_hash.fcvolt3 = 1;
				}
			}


		###Main Bus Volt // Class 2 Hardware and Software// F7 light

		if ((voltage_mainA < 27) or (voltage_mainA > 32))
			{
			if (cws_msg_hash.mnvolta == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("S67 MAIN BUS V", "   A", "   4 ", 2, "PASS");
				cws_msg_hash.mnvolta = 1;
				}
			}

		if ((voltage_mainB < 27) or (voltage_mainB > 32))
			{
			if (cws_msg_hash.mnvoltb == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("S67 MAIN BUS V", "   B", "   4 ", 2, "PASS");
				cws_msg_hash.mnvoltb = 1;
				}
			}

		if ((voltage_mainC < 27) or (voltage_mainC > 32))
			{
			if (cws_msg_hash.mnvoltc == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("S67 MAIN BUS V", "   C", "   4 ", 2, "PASS");
				cws_msg_hash.mnvoltc = 1;
				}
			}

		
		###FC AMPS // Class 3 // Associated with O2/H2 Flow and H2Pump satus ( same variation tendency, high for short// low for no power from fc)
		#Mix messages 

		if ((amps1 < 50) or (amps1 > 350))
			{
			if (cws_msg_hash.fcamp1 == 0)
				{			
				create_fault_message("S69 FC AMPS   ", "   1", "   4 ", 2, "PASS");
				#create_fault_message("S69 FC H2 FLOW", "   1", "   4 ", 2, "PASS");
				create_fault_message("S69 FC FLOW   ", "   1", "   4 ", 2, "PASS");
				#create_fault_message("S69 FC H2 PUMP", "   1", "   4 ", 2, "PASS");
				cws_msg_hash.fcamp1 = 1;
				}
			}

		if ((amps2 < 50) or (amps2 > 350))
			{
			if (cws_msg_hash.fcamp2 == 0)
				{			
				create_fault_message("S69 FC AMPS   ", "   2", "   4 ", 2, "PASS");
				#create_fault_message("S69 FC H2 FLOW", "   2", "   4 ", 2, "PASS");
				create_fault_message("S69 FC FLOW   ", "   2", "   4 ", 2, "PASS");
				#create_fault_message("S69 FC H2 PUMP", "   2", "   4 ", 2, "PASS");
				cws_msg_hash.fcamp2 = 1;
				}
			}

		if ((amps3 < 50) or (amps3 > 350))
			{
			if (cws_msg_hash.fcamp3 == 0)
				{			
				create_fault_message("S69 FC AMPS   ", "   3", "   4 ", 2, "PASS");
				#create_fault_message("S69 FC H2 FLOW", "   3", "   4 ", 2, "PASS");
				create_fault_message("S69 FC FLOW   ", "   3", "   4 ", 2, "PASS");
				#create_fault_message("S69 FC H2 PUMP", "   3", "   4 ", 2, "PASS");
				cws_msg_hash.fcamp3 = 1;
				}
			}
			

		###Stack temp (F7/ Backup) + Exit temp ( same tendency) // Temp in Kelvin to avoid conversion function ( same as cws.xml)
		#No need for several messages

		if ((stack_T1 < 350) or (stack_T1 > 390)) 
			{
			if (cws_msg_hash.stackt1 == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("S69 FC STACK T", "   1", "   4 ", 2, "PASS");
				#create_fault_message("S69 FC EXIT T ", "   1", "   4 ", 2, "PASS");
				cws_msg_hash.stackt1 = 1;
				}
			}

		if ((stack_T2 < 350) or (stack_T2 > 390)) 
			{
			if (cws_msg_hash.stackt2 == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("S69 FC STACK T", "   2", "   4 ", 2, "PASS");
				#create_fault_message("S69 FC EXIT T ", "   2", "   4 ", 2, "PASS");
				cws_msg_hash.stackt2 = 1;
				}
			}

		if ((stack_T3 < 350) or (stack_T3 > 390)) 
			{
			if (cws_msg_hash.stackt3 == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("S69 FC STACK T", "   3", "   4 ", 2, "PASS");
				#create_fault_message("S69 FC EXIT T ", "   3", "   4 ", 2, "PASS");
				cws_msg_hash.stackt3 = 1;
				}
			}
				
			
		###Coolant Pump (linked to Coolant pressure down, just one message is enough) // F7 and backup

		if (coolp1_pump < 0.8)
			{
			if (cws_msg_hash.fcpump1 == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("S69 FC PUMP   ", "   1", "   4 ", 3, "PASS");
				cws_msg_hash.fcpump1 = 1;
				}
			}

		if (coolp2_pump < 0.8)
			{
			if (cws_msg_hash.fcpump2 == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("S69 FC PUMP   ", "   2", "   4 ", 3, "PASS");
				cws_msg_hash.fcpump2 = 1;
				}
			}

		if (coolp3_pump < 0.8)
			{
			if (cws_msg_hash.fcpump3 == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("S69 FC PUMP   ", "   3", "   4 ", 3, "PASS");
				cws_msg_hash.fcpump3 = 1;
				}
			}


		###FC reactant valves (F7 and backup)

		if (fc1_reac_valve == 0)
			{
			if (cws_msg_hash.fcreac1 == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("S69 FC REAC   ", "   1", "   4 ", 3, "PASS");
				cws_msg_hash.fcreac1 = 1;
				}
			}

		if (fc2_reac_valve == 0)
			{
			if (cws_msg_hash.fcreac2 == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("S69 FC REAC   ", "   2", "   4 ", 3, "PASS");
				cws_msg_hash.fcreac2 = 1;
				}
			}

		if (fc3_reac_valve == 0)
			{
			if (cws_msg_hash.fcreac3 == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("S69 FC REAC   ", "   3", "   4 ", 3, "PASS");
				cws_msg_hash.fcreac3 = 1;
				}
			}




		}




	#BFS SM failure (Outside OPS 2 SM)
	else
		{	


		###AC Voltage failures

		if (voltage_ac1 < 108.0) 
			{
			if (cws_msg_hash.acvolt1 == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
				create_fault_message("SM1 AC VOLTS  ", "   1", "    5", 2, "BFS");
				cws_msg_hash.acvolt1 = 1;
				}
			}
		if (voltage_ac2 < 108.0)
			{
				if (cws_msg_hash.acvolt2 == 0)
				{	
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
				create_fault_message("SM1 AC VOLTS  ", "   2", "    5", 2, "BFS");
				cws_msg_hash.acvolt2 = 1;
				}
			}
		if (voltage_ac3 < 108.0)
			{
				if (cws_msg_hash.acvolt3 == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
				create_fault_message("SM1 AC VOLTS  ", "   3", "    5", 2, "BFS");
				cws_msg_hash.acvolt3 = 1;
				}
			}	


		###AC overload ( to link to F7 C/W red OVLD light)

		if (power_ac1 > 7.0)
			{
			if (cws_msg_hash.acovld1 == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("SM1 AC OVLD   ", "   1", "    5", 2, "BFS");
				cws_msg_hash.acovld1 = 1;
				if (ac_bus_sensor1 == 1) {setprop("/fdm/jsbsim/systems/electrical/ac/inv-ac-switch", 0);}
				}
			}
		if (power_ac2 > 7.0)
			{
			if (cws_msg_hash.acovld2 == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("SM1 AC OVLD   ", "   2", "    5", 2, "BFS");
				cws_msg_hash.acovld2 = 1;
				if (ac_bus_sensor2 == 1) {setprop("/fdm/jsbsim/systems/electrical/ac[1]/inv-ac-switch", 0);}
				}
			}
		if (power_ac3 > 7.0)
			{
			if (cws_msg_hash.acovld3 == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("SM1 AC OVLD   ", "   3", "    5", 2, "BFS");
				cws_msg_hash.acovld3 = 1;
				if (ac_bus_sensor3 == 1) {setprop("/fdm/jsbsim/systems/electrical/ac[2]/inv-ac-switch", 0);}
				}
			}

		###FC Volt

		if ((fc_voltage1 < 27.5) or (fc_voltage1 > 32))
			{
			if (cws_msg_hash.fcvolt1 == 0)
				{			
				create_fault_message("SM1 DC VOLT FC", "   1", "    5", 2, "BFS");
				cws_msg_hash.fcvolt1 = 1;
				}
			}

		if ((fc_voltage2 < 27.5) or (fc_voltage2 > 32))
			{
			if (cws_msg_hash.fcvolt2 == 0)
				{			
				create_fault_message("SM1 DC VOLT FC", "   2", "    5", 2, "BFS");
				cws_msg_hash.fcvolt2 = 1;
				}
			}

		if ((fc_voltage3 < 27.5) or (fc_voltage3 > 32))
			{
			if (cws_msg_hash.fcvolt3 == 0)
				{			
				create_fault_message("SM1 DC VOLT FC", "   3", "    5", 2, "BFS");
				cws_msg_hash.fcvolt3 = 1;
				}
			}


		###Main Bus Volt // Class 2 Hardware and Software// F7 light

		if ((voltage_mainA < 27) or (voltage_mainA > 32))
			{
			if (cws_msg_hash.mnvolta == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("SM1 MAIN BUS V", "   A", "    5", 2, "BFS");
				cws_msg_hash.mnvolta = 1;
				}
			}

		if ((voltage_mainB < 27) or (voltage_mainB > 32))
			{
			if (cws_msg_hash.mnvoltb == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("SM1 MAIN BUS V", "   B", "    5", 2, "BFS");
				cws_msg_hash.mnvoltb = 1;
				}
			}

		if ((voltage_mainC < 27) or (voltage_mainC > 32))
			{
			if (cws_msg_hash.mnvoltc == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("SM1 MAIN BUS V", "   C", "    5", 2, "BFS");
				cws_msg_hash.mnvoltc = 1;
				}
			}


		###FC AMPS // Class 3 

		if ((amps1 < 50) or (amps1 > 350))
			{
			if (cws_msg_hash.fcamp1 == 0)
				{			
				create_fault_message("SM1 FC AMPS   ", "   1", "    5", 2, "BFS");
				cws_msg_hash.fcamp1 = 1;
				}
			}

		if ((amps2 < 50) or (amps2 > 350))
			{
			if (cws_msg_hash.fcamp2 == 0)
				{			
				create_fault_message("SM1 FC AMPS   ", "   2", "    5", 2, "BFS");
				cws_msg_hash.fcamp2 = 1;
				}
			}

		if ((amps3 < 50) or (amps3 > 350))
			{
			if (cws_msg_hash.fcamp3 == 0)
				{			
				create_fault_message("SM1 FC AMPS   ", "   3", "    5", 2, "BFS");
				cws_msg_hash.fcamp3 = 1;
				}
			}


		###Stack T

		if ((stack_T1 < 350) or (stack_T1 > 390)) 
			{
			if (cws_msg_hash.stackt1 == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("SM1 FC STACK T", "   1", "    5", 2, "BFS");
				#create_fault_message("SM1 FC EXIT T ", "   1", "   4 ", 2, "PASS");
				cws_msg_hash.stackt1 = 1;
				}
			}

		if ((stack_T2 < 350) or (stack_T2 > 390)) 
			{
			if (cws_msg_hash.stackt2 == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("SM1 FC STACK T", "   2", "    5", 2, "BFS");
				#create_fault_message("SM1 FC EXIT T ", "   2", "   4 ", 2, "PASS");
				cws_msg_hash.stackt2 = 1;
				}
			}

		if ((stack_T3 < 350) or (stack_T3 > 390)) 
			{
			if (cws_msg_hash.stackt3 == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("SM1 FC STACK T", "   3", "    5", 2, "BFS");
				#create_fault_message("SM1 FC EXIT T ", "   3", "   4 ", 2, "PASS");
				cws_msg_hash.stackt3 = 1;
				}
			}


		###Coolant Pump (linked to Coolant pressure down, just one message is enough) // F7 and backup

		if (coolp1_pump < 0.8)
			{
			if (cws_msg_hash.fcpump1 == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("SM1 FC PUMP   ", "   1", "    5", 3, "BFS");
				cws_msg_hash.fcpump1 = 1;
				}
			}

		if (coolp2_pump < 0.8)
			{
			if (cws_msg_hash.fcpump2 == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("SM1 FC PUMP   ", "   2", "    5", 3, "BFS");
				cws_msg_hash.fcpump2 = 1;
				}
			}

		if (coolp3_pump < 0.8)
			{
			if (cws_msg_hash.fcpump3 == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("SM1 FC PUMP   ", "   3", "    5", 3, "BFS");
				cws_msg_hash.fcpump3 = 1;
				}
			}


		###FC reactant valves (F7 and backup)

		if (fc1_reac_valve == 0)
			{
			if (cws_msg_hash.fcreac1 == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("SM1 FC REAC   ", "   1", "    5", 3, "BFS");
				cws_msg_hash.fcreac1 = 1;
				}
			}

		if (fc2_reac_valve == 0)
			{
			if (cws_msg_hash.fcreac2 == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("SM1 FC REAC   ", "   2", "    5", 3, "BFS");
				cws_msg_hash.fcreac2 = 1;
				}
			}

		if (fc3_reac_valve == 0)
			{
			if (cws_msg_hash.fcreac3 == 0)
				{		
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("SM1 FC REAC   ", "   3", "    5", 3, "BFS");
				cws_msg_hash.fcreac3 = 1;
				}
			}

		

		}		

	}	
}



#################################################
# CWS checks of navigation
#################################################

var cws_inspect_nav = func {

var ops =  getprop("/fdm/jsbsim/systems/dps/ops");

#IMU Fail (No F7 light)
#PASS and BFS same message/OPS
# Class 3 SM alert

if ((SpaceShuttle.imu_system.imu[0].soft_failed == 1) or (SpaceShuttle.imu_system.imu[1].soft_failed == 1) or (SpaceShuttle.imu_system.imu[2].soft_failed == 1))
	{
	if (cws_msg_hash.rm_fail_imu == 0)
		{
		create_fault_message("    RM FAIL   ", " IMU", "12   ", 3,"PASS");
		create_fault_message("    RM FAIL   ", " IMU", "    5", 3,"BFS");	
		cws_msg_hash.rm_fail_imu = 1;
		}
	}


#IMU Dilemma (IMU F7 light and soft class 2 Back Up) 
#PASS GNC ONLY
#Class 3 SM alert


if ((SpaceShuttle.imu_system.imu[0].dilemma == 1) or (SpaceShuttle.imu_system.imu[1].dilemma == 1) or (SpaceShuttle.imu_system.imu[2].dilemma == 1))
	{
	if (cws_msg_hash.rm_dlma_imu == 0)
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    RM DLMA   ", " IMU", "12   ", 2,"PASS");
		cws_msg_hash.rm_dlma_imu = 1;

		SpaceShuttle.orbital_dap_manager.load_dap("IMU_FAIL");
		}
	}



#IMU Overheat ( same than Built In Test)
#PASS only all G // No C/W

var imutemp = getprop("/fdm/jsbsim/systems/eclss/avbay/imu-temp");

if (imutemp != 0)
	{
	if (cws_msg_hash.imu_temp == 0)
		{
		create_fault_message("    IMU BITE/T", "    ", "12    ", 3,"PASS");
		cws_msg_hash.imu_temp = 1;
		}
	}



#TACAN Dilemma
#PASS G3,6 ONLY

var mm =  getprop("/fdm/jsbsim/systems/dps/major-mode");

if ((mm != 304) and (mm != 305) and (mm != 602) and (mm != 603)) {return;}

if (SpaceShuttle.tacan_system.dilemma == 1)
	{
	if (cws_msg_hash.rm_dlm_tac == 0)
		{
		create_fault_message("    RM DLMA   ", " TAC", "1234 ", 3,"PASS");
		cws_msg_hash.rm_dlm_tac = 1;
		}
	}


#TACAN Fail
#PASS G3,6 ONLY

if ((SpaceShuttle.tacan_system.receiver[0].soft_failed == 1) or (SpaceShuttle.tacan_system.receiver[1].soft_failed == 1) or (SpaceShuttle.tacan_system.receiver[2].soft_failed == 1))
	{
	if (cws_msg_hash.rm_fail_tac == 0)
		{
		create_fault_message("    RM FAIL   ", " TAC", "1234 ", 2,"PASS");	
		cws_msg_hash.rm_fail_tac = 1;
		}
	}

#NAV EDIT TAC/ALT for PASS G3,6
#Not type for BFS 3, 6


if ((getprop("/position/altitude-ft") < 140000.0) and (SpaceShuttle.area_nav_set.TACAN_inh == 1))
	{
	if (cws_msg_hash.nav_edit_tac == 0)
		{
		create_fault_message("    NAV EDIT  "," TAC", "1234 ", 3,"PASS");
		create_fault_message("    NAV EDIT  ","    ", "    5", 3,"BFS");	
		cws_msg_hash.nav_edit_tac = 1;

		}

	}

var mach = getprop("/velocities/mach");

if ((mach < 2.5) and (SpaceShuttle.area_nav_set.air_data_h_inh == 1))
	{
	if (cws_msg_hash.nav_edit_alt == 0)
		{
		create_fault_message("    NAV EDIT  "," ALT", "1234 ", 3,"PASS");
		create_fault_message("    NAV EDIT  ","    ", "    5", 3,"BFS");	
		cws_msg_hash.nav_edit_alt = 1;	
		}

	}



#PROBES not deployed below M = 2.5
#PASS G3,6 only



if ((mach < 2.5) and (getprop("/fdm/jsbsim/systems/navigation/air-data-left-pos-kin") == 1.0) and (getprop("/fdm/jsbsim/systems/navigation/air-data-left-pos") < 1))
	{
	if (cws_msg_hash.probes == 0)
		{
		create_fault_message("    PROBES    ", "    ", "1234 ", 3,"PASS");	
		cws_msg_hash.probes = 1;	
		}
	}

if ((mach < 2.5) and (getprop("/fdm/jsbsim/systems/navigation/air-data-right-pos-kin") == 1.0) and (getprop("/fdm/jsbsim/systems/navigation/air-data-right-pos") < 1.0))
	{
	if (cws_msg_hash.probes == 0)
		{
		create_fault_message("    PROBES    ", "    ", "1234 ", 3,"PASS");	
		cws_msg_hash.probes = 1;	
		}
	}



#ADTA Fail
#PASS/SM G3,6 


if ((SpaceShuttle.air_data_system.adta[0].soft_failed == 1) or (SpaceShuttle.air_data_system.adta[1].soft_failed == 1) or (SpaceShuttle.air_data_system.adta[2].soft_failed == 1) or (SpaceShuttle.air_data_system.adta[3].soft_failed == 1))
	{
	if (cws_msg_hash.rm_fail_adta == 0)
		{
		create_fault_message("    RM FAIL   ", "ADTA", "1234 ", 3,"PASS");
		create_fault_message("    RM FAIL   ", "ADTA", "    5", 3,"BFS");
		cws_msg_hash.rm_fail_adta = 1;
		}
	}


#ADTA Dilemma (AIR DATA F7 light already implemented and class 2 back up alarm)
#PASS G3,6 ONLY

if ((SpaceShuttle.air_data_system.adta[0].dilemma == 1) or (SpaceShuttle.air_data_system.adta[1].dilemma == 1) or (SpaceShuttle.air_data_system.adta[2].dilemma == 1) or (SpaceShuttle.air_data_system.adta[3].dilemma == 1))
	{
	if (cws_msg_hash.rm_dlma_adta == 0)
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    RM DLMA   ", "ADTA", "1234 ", 2,"PASS");	
		cws_msg_hash.rm_dlma_adta = 1;
		}
	}


#TAEM Energy Downmode suggestion
#PASS/BFS G3/6

#At least two messages, hence the variables
var EW_act = getprop("/fdm/jsbsim/systems/entry_guidance/taem-EW-actual-ratio-ft");
var EW_stin = getprop("/fdm/jsbsim/systems/entry_guidance/taem-EW-stin-ratio-ft");
var EW_mep = getprop("/fdm/jsbsim/systems/entry_guidance/taem-EW-mep-ratio-ft");
var distance_rwy = getprop("/fdm/jsbsim/systems/taem-guidance/distance-to-runway-nm");

	
#No TAEM energy alerts if Shuttle is coonected to the 747
if (getprop("/fdm/jsbsim/systems/carrier/connected") == 0)
	{

	#OTT (other targeting target) suggesting reverting to Stin approach above 45 Nm// datas for a 270 ° hac to 90 ° hac (average value)
	if ((EW_act < EW_stin) and (distance_rwy > 45))
		{
		if (cws_msg_hash.ott_stn_in == 0)
			{
			create_fault_message("    OTT ST IN ", "    ", "1234 ", 3, "PASS");	
			create_fault_message("    OTT ST IN ", "    ", "    5", 3, "BFS");	
			cws_msg_hash.ott_stn_in = 1;
			}
		}

	#MEP (minimal entry point) suggesting reverting to mep (Approaching minimum qbar boundary) // up to 90 ° HAC (12Nm ish)
	if ((EW_act < EW_mep) and (distance_rwy > 12))
		{
		if (cws_msg_hash.mep == 0)
			{
			create_fault_message("    SW TO MEP ", "    ", "1234 ", 3, "PASS");	
			create_fault_message("    SW TO MEP ", "    ", "    5", 3, "BFS");	
			cws_msg_hash.mep = 1;
			}
		}
	}

#High G message (PASS OPS3/6) SCOM 4.9-1 // 2.5 G between 200 and 400 EAS // 2.2 G warning limit for a safe margin

var Nz = getprop("/fdm/jsbsim/accelerations/Nz");

if ((Nz > 2.2) and ((ops == 3) or (ops == 6)))
	{
	if (cws_msg_hash.high_g == 0)
		{
		create_fault_message("    HIGH G    ", "    ", "1234 ", 3, "PASS");		
		cws_msg_hash.high_g = 1;
		}
	}




}



#################################################
# CWS checks of MPS
#################################################

var cws_inspect_mps = func {

#Class 3 SM Alert for elec,hyd,data,path

if (getprop("/fdm/jsbsim/systems/mps/engine/electric-lockup") == 1)
	{
	if (cws_msg_hash.mps_elec_l == 0)
		{
		create_fault_message("    MPS ELEC  ","   L", "1234 ", 3,"PASS");
		create_fault_message("    MPS ELEC  ","   L", "    5", 3,"BFS");	
		cws_msg_hash.mps_elec_l = 1;
		}
	}

if (getprop("/fdm/jsbsim/systems/mps/engine[1]/electric-lockup") == 1)
	{
	if (cws_msg_hash.mps_elec_r == 0)
		{
		create_fault_message("    MPS ELEC  ","   R", "1234 ", 3,"PASS");
		create_fault_message("    MPS ELEC  ","   R", "    5", 3,"BFS");	
		cws_msg_hash.mps_elec_r = 1;
		}
	}

if (getprop("/fdm/jsbsim/systems/mps/engine[2]/electric-lockup") == 1)
	{
	if (cws_msg_hash.mps_elec_c == 0)
		{
		create_fault_message("    MPS ELEC  ","   C", "1234 ", 3,"PASS");
		create_fault_message("    MPS ELEC  ","   C", "    5", 3,"BFS");	
		cws_msg_hash.mps_elec_c = 1;
		}
	}

if (getprop("/fdm/jsbsim/systems/mps/engine/hydraulic-power") == 0)
	{
	if (cws_msg_hash.mps_hyd_l == 0)
		{
		create_fault_message("    MPS HYD   ","   L", "1234 ", 3,"PASS");
		create_fault_message("    MPS HYD   ","   L", "    5", 3,"BFS");	
		cws_msg_hash.mps_hyd_l = 1;
		}
	}

if (getprop("/fdm/jsbsim/systems/mps/engine[1]/hydraulic-power") == 0)
	{
	if (cws_msg_hash.mps_hyd_r == 0)
		{
		create_fault_message("    MPS HYD   ","   R", "1234 ", 3,"PASS");
		create_fault_message("    MPS HYD   ","   R", "    5", 3,"BFS");	
		cws_msg_hash.mps_hyd_r = 1;
		}
	}

if (getprop("/fdm/jsbsim/systems/mps/engine[2]/hydraulic-power") == 0)
	{
	if (cws_msg_hash.mps_hyd_c == 0)
		{
		create_fault_message("    MPS HYD   ","   C", "1234 ", 3,"PASS");
		create_fault_message("    MPS HYD   ","   C", "    5", 3,"BFS");	
		cws_msg_hash.mps_hyd_c = 1;
		}
	}



#MPS Helium messages only BFS G1,6
#Class2 Backup for MPS F7 failures ( He < 1150 and Manifold LO2/LH2 )


	#LH2/LO2 manifold overpressure ( F7 C/W MPS light) // Triggered 20seconds after Liftoff to avoid alarm during intial Pitchdown and High G transient condition
	var elapsed_time = getprop("/sim/time/elapsed-sec") + getprop("/fdm/jsbsim/systems/timer/delta-MET");

if (((getprop("/fdm/jsbsim/systems/mps/lh2-manifold-pressure-psia") > 65.0) or (getprop("/fdm/jsbsim/systems/mps/lo2-manifold-pressure-psia") > 249.0)) and (elapsed_time > 20.0))
	{
	if (cws_msg_hash.mps_manf == 0)
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    MPS LH2/O2","MANF","    5", 2, "BFS");	
		cws_msg_hash.mps_manf = 1;
		}
	}

if ((getprop("/fdm/jsbsim/systems/mps/helium/pressure-psia") < 1150.0) or (getprop("/fdm/jsbsim/systems/mps/helium/reg-pressure-psia") < 679.0))
	{
	if (cws_msg_hash.mps_he_p_l == 0)
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    MPS HE P  ","   L","    5", 2, "BFS");	
		cws_msg_hash.mps_he_p_l = 1;
		}
	}

if ((getprop("/fdm/jsbsim/systems/mps/helium[1]/pressure-psia") < 1150.0) or (getprop("/fdm/jsbsim/systems/mps/helium[1]/reg-pressure-psia") < 679.0))
	{
	if (cws_msg_hash.mps_he_p_r == 0)
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    MPS HE P  ","   R","    5", 2, "BFS");	
		cws_msg_hash.mps_he_p_r = 1;
		}
	}

if ((getprop("/fdm/jsbsim/systems/mps/helium[2]/pressure-psia") < 1150.0) or (getprop("/fdm/jsbsim/systems/mps/helium[2]/reg-pressure-psia") < 679.0))
	{
	if (cws_msg_hash.mps_he_p_c == 0)
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    MPS HE P  ","   C","    5", 2, "BFS");	
		cws_msg_hash.mps_he_p_c = 1;
		}
	}

if (getprop("/fdm/jsbsim/systems/mps/helium[3]/pressure-psia") < 3800.0) 
	{
	if (cws_msg_hash.pneu_p_tk == 0)
		{
		create_fault_message("    MPSPNEUREG","   ", "    5", 3, "BFS");	
		cws_msg_hash.pneu_p_tk = 1;
		}
	}

if (getprop("/fdm/jsbsim/systems/mps/helium[3]/reg-pressure-psia") < 700.0) 
	{
	if (cws_msg_hash.pneu_p_tk == 0)
		{
		create_fault_message("    MPSPNEU TK","   ", "    5", 3, "BFS");	
		cws_msg_hash.pneu_p_tk = 1;
		}
	}


if (ssme_array[0].command_path != 1)
	{
	if ((cws_msg_hash.mps_cmd_l == 0) and (cws_msg_hash.mps_data_l == 0))
		{
		create_fault_message("    MPS CMD   ","   L", "1234 ", 3,"PASS");
		create_fault_message("    MPS CMD   ","   L", "    5", 3,"BFS");	
		setprop("/fdm/jsbsim/systems/mps/engine/data-path", 0);
		cws_msg_hash.mps_cmd_l = 1;
		}
	}

if (ssme_array[1].command_path != 1)
	{
	if ((cws_msg_hash.mps_cmd_r == 0) and (cws_msg_hash.mps_data_r == 0))
		{
		create_fault_message("    MPS CMD   ","   R", "1234 ", 3,"PASS");
		create_fault_message("    MPS CMD   ","   R", "    5", 3,"BFS");	
		setprop("/fdm/jsbsim/systems/mps/engine[1]/data-path", 0);
		cws_msg_hash.mps_cmd_r = 1;
		}
	}

if (ssme_array[2].command_path != 1)
	{
	if ((cws_msg_hash.mps_cmd_c == 0)  and (cws_msg_hash.mps_data_c == 0))
		{
		create_fault_message("    MPS CMD   ","   C", "1234 ", 3,"PASS");
		create_fault_message("    MPS CMD   ","   C", "    5", 3,"BFS");	
		setprop("/fdm/jsbsim/systems/mps/engine[2]/data-path", 0);
		cws_msg_hash.mps_cmd_c = 1;
		}
	}

if (ssme_array[0].data_path != 1)
	{
	if (cws_msg_hash.mps_data_l == 0)
		{
		create_fault_message("    MPS DATA  ","   L", "1234 ", 3,"PASS");
		create_fault_message("    MPS DATA  ","   L", "    5", 3,"BFS");	
		setprop("/fdm/jsbsim/systems/mps/engine/data-path", 0);
		cws_msg_hash.mps_data_l = 1;
		}
	}

if (ssme_array[1].data_path != 1)
	{
	if (cws_msg_hash.mps_data_r == 0)
		{
		create_fault_message("    MPS DATA  ","   R", "1234 ", 3,"PASS");
		create_fault_message("    MPS DATA  ","   R", "    5", 3,"BFS");	
		setprop("/fdm/jsbsim/systems/mps/engine[1]/data-path", 0);
		cws_msg_hash.mps_data_r = 1;
		}
	}

if (ssme_array[2].data_path != 1)
	{
	if (cws_msg_hash.mps_data_c == 0)
		{
		create_fault_message("    MPS DATA  ","   C", "1234 ", 3,"PASS");
		create_fault_message("    MPS DATA  ","   C", "    5", 3,"BFS");	
		setprop("/fdm/jsbsim/systems/mps/engine[2]/data-path", 0);
		cws_msg_hash.mps_data_c = 1;
		}
	}

# don't notify engine shutdown after regular MECO or if we don't know MECO
# No F7 light, but soft Back Up C/W class 2 alarm and hardware Master Caution light/alarm

if (getprop("/fdm/jsbsim/systems/ap/launch/regular-meco-condition") == 1) {return;}

if (getprop("/fdm/jsbsim/systems/mps/engine/engine-operational") == 0)
	{
	if (cws_msg_hash.ssme_fail_l == 0)
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    SSME FAIL ","   L", "1234 ", 2,"PASS");
		create_fault_message("    SSME FAIL ","   L", "    5", 2,"BFS");	
		cws_msg_hash.ssme_fail_l = 1;
		}

	}

if (getprop("/fdm/jsbsim/systems/mps/engine[1]/engine-operational") == 0)
	{
	if (cws_msg_hash.ssme_fail_r == 0)
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    SSME FAIL ","   R", "1234 ", 2,"PASS");
		create_fault_message("    SSME FAIL ","   R", "    5", 2,"BFS");	
		cws_msg_hash.ssme_fail_r = 1;
		}

	}

if (getprop("/fdm/jsbsim/systems/mps/engine[2]/engine-operational") == 0)
	{
	if (cws_msg_hash.ssme_fail_c == 0)
		{
		setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);
		create_fault_message("    SSME FAIL ","   C", "1234 ", 2,"PASS");
		create_fault_message("    SSME FAIL ","   C", "    5", 2,"BFS");	
		cws_msg_hash.ssme_fail_c = 1;
		}

	}

# redline testing isn't really part of CWS, but we do it here anyway

var limit_shutdown_enable = getprop("/fdm/jsbsim/systems/mps/limit-shutdown-enable");

if (getprop("/fdm/jsbsim/systems/mps/engine/engine-running-redline") == 1)
	{
	if (limit_shutdown_enable == 2)	
		{
		SpaceShuttle.ssme_array[0].cutoff();
		}
	else if ((limit_shutdown_enable == 1) and (getprop("/fdm/jsbsim/systems/mps/number-engines-operational") == 3))
		{
		SpaceShuttle.ssme_array[0].cutoff();
		}
	}

if (getprop("/fdm/jsbsim/systems/mps/engine[1]/engine-running-redline") == 1)
	{
	if (limit_shutdown_enable == 2)	
		{
		SpaceShuttle.ssme_array[1].cutoff();
		}
	else if ((limit_shutdown_enable == 1) and (getprop("/fdm/jsbsim/systems/mps/number-engines-operational") == 3))
		{
		SpaceShuttle.ssme_array[1].cutoff();
		}
	}

if (getprop("/fdm/jsbsim/systems/mps/engine[2]/engine-running-redline") == 1)
	{
	if (limit_shutdown_enable == 2)	
		{
		SpaceShuttle.ssme_array[2].cutoff();
		}
	else if ((limit_shutdown_enable == 1) and (getprop("/fdm/jsbsim/systems/mps/number-engines-operational") == 3))
		{
		SpaceShuttle.ssme_array[2].cutoff();
		}
	}


}



#################################################
# CWS checks of ECLSS 
#################################################

var cws_inspect_eclss = func {

var ops =  getprop("/fdm/jsbsim/systems/dps/ops");

#S66 variables (Environment)

var avbay1_t = getprop("/fdm/jsbsim/systems/eclss/avbay/temperature-K");
var avbay2_t = getprop("/fdm/jsbsim/systems/eclss/avbay[1]/temperature-K");
var avbay3_t = getprop("/fdm/jsbsim/systems/eclss/avbay[2]/temperature-K");

var avbay1_fan = getprop("/fdm/jsbsim/systems/eclss/avbay/fan-cooling-effect") * 3.80;
var avbay2_fan = getprop("/fdm/jsbsim/systems/eclss/avbay[1]/fan-cooling-effect") * 3.77;
var avbay3_fan = getprop("/fdm/jsbsim/systems/eclss/avbay[2]/fan-cooling-effect") * 3.92;

var cabin_p = getprop("/fdm/jsbsim/systems/eclss/cabin/air-pressure-psi");
var dpdt_value = getprop("/fdm/jsbsim/systems/eclss/cabin/air-pressure-change-psi_s") * 60;
var ppo2_value = getprop("/fdm/jsbsim/systems/eclss/cabin/ppo2-psi");

var imu_fanA_op = getprop("/fdm/jsbsim/systems/eclss/avbay/imu-fan-A-operational");
var imu_fanB_op = getprop("/fdm/jsbsim/systems/eclss/avbay/imu-fan-B-operational");
var imu_fanC_op = getprop("/fdm/jsbsim/systems/eclss/avbay/imu-fan-C-operational");
var imu_dp = imu_fanA_op + imu_fanB_op + imu_fanC_op;

var fan_A = getprop("/fdm/jsbsim/systems/eclss/cabin/fan-A-operational");
var fan_B = getprop("/fdm/jsbsim/systems/eclss/cabin/fan-B-operational");
var cabin_dp = fan_A + fan_B;

var o2_valve1 = getprop("/fdm/jsbsim/systems/eclss/oxygen/sys1-o2-supply-valve-status");
var o2_valve2 = getprop("/fdm/jsbsim/systems/eclss/oxygen/sys2-o2-supply-valve-status");
var n2_sys1 = getprop("/fdm/jsbsim/systems/eclss/nitrogen/sys1-pressurized");
var n2_sys2 = getprop("/fdm/jsbsim/systems/eclss/nitrogen/sys2-pressurized");


#S88 variables (Thermal// Apu line heaters//Evap heaters)

var freon_flow_1 = getprop("/fdm/jsbsim/systems/atcs/freon-pump-1-active");
var freon_flow_2 = getprop("/fdm/jsbsim/systems/atcs/freon-pump-2-active");
var evap_out = getprop("/fdm/jsbsim/systems/thermal-distribution/freon-out-temperature-K");
var h2o_loop = getprop("/fdm/jsbsim/systems/cws/h2o-loop");

var T_aft = getprop("/fdm/jsbsim/systems/thermal-distribution/aft-temperature-K"); #45°F = 280°K

var apu_heater_1 = getprop("/fdm/jsbsim/systems/apu/apu/heater-tank-operational");
var apu_heater_2 = getprop("/fdm/jsbsim/systems/apu/apu[1]/heater-tank-operational");
var apu_heater_3 = getprop("/fdm/jsbsim/systems/apu/apu[2]/heater-tank-operational");

var heater_top_duct = getprop("/fdm/jsbsim/systems/atcs/fes-topping-duct-heater-active");
var heater_hild = getprop("/fdm/jsbsim/systems/atcs/fes-hiload-duct-heater-active");
var fdln_A_status = getprop("/fdm/jsbsim/systems/atcs/fes-feedline-A-heater-active");
var fdln_B_status = getprop("/fdm/jsbsim/systems/atcs/fes-feedline-B-heater-active");


#PASS SM failure (OPS2)
if (ops == 2)
	{
	
	###Av Bay temp (F7 hardware and SM light) // T > 130°F

	if (avbay1_t > 328)
		{
		if (cws_msg_hash.avbayt1 == 0)
			{		
			create_fault_message("S66 AV BAY 1  ", "TEMP", "   4 ", 2, "PASS");
			cws_msg_hash.avbayt1 = 1;
			}
		}

	if (avbay2_t > 328)
		{
		if (cws_msg_hash.avbayt2 == 0)
			{		
			create_fault_message("S66 AV BAY 2  ", "TEMP", "   4 ", 2, "PASS");
			cws_msg_hash.avbayt2 = 1;
			}
		}

	if (avbay3_t > 328)
		{
		if (cws_msg_hash.avbayt3 == 0)
			{		
			create_fault_message("S66 AV BAY 3  ", "TEMP", "   4 ", 2, "PASS");
			cws_msg_hash.avbayt3 = 1;
			}
		}

	###Av Bay fan DP lost (class 3)

	if (avbay1_fan < 3.20)
		{
		if (cws_msg_hash.avbayfan1 == 0)
			{		
			create_fault_message("S66 AV BAY 1  ", " FAN", "   4 ", 2, "PASS");
			cws_msg_hash.avbayfan1 = 1;
			}
		}

	if (avbay2_fan < 3.20)
		{
		if (cws_msg_hash.avbayfan2 == 0)
			{		
			create_fault_message("S66 AV BAY 2  ", " FAN", "   4 ", 2, "PASS");
			cws_msg_hash.avbayfan2 = 1;
			}
		}

	if (avbay3_fan < 3.20)
		{
		if (cws_msg_hash.avbayfan3 == 0)
			{		
			create_fault_message("S66 AV BAY 3  ", " FAN", "   4 ", 2, "PASS");
			cws_msg_hash.avbayfan3 = 1;
			}
		}

	###Cabin Pressure (F7 and backup) ( Plus O2/N2 Flow as it will be max then// to avoid to call back 10 variables for Flow message fault)

	if (cabin_p < 13.8) 
		{
		if (cws_msg_hash.cabinp == 0)
			{		
			setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
			create_fault_message("S66 CABIN     ", "PRES", "   4 ", 2, "PASS");
			create_fault_message("S66 CABIN     ", "FLOW", "   4 ", 2, "PASS");
			create_fault_message("S66 CAB AIRLK ", "PRES", "   4 ", 2, "PASS");
			cws_msg_hash.cabinp = 1;
			}
		}


	###Cabin dP/dT (class 3)

	if (dpdt_value < -0.12)
		{
		if (cws_msg_hash.cabindpdt == 0)
			{			
			create_fault_message("S78 CABIN     ", "DPDT", "   4 ", 2, "PASS");
			cws_msg_hash.cabindpdt = 1;
			}
		}

	###PPO2 (F7 Backup)

	if (ppo2_value < 2.7)
		{
		if (cws_msg_hash.ppo2 == 0)
			{		
			setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
			create_fault_message("S66 CABIN PPO2", " ABC", "   4 ", 2, "PASS");
			cws_msg_hash.ppo2 = 1;
			}
		}


	###Cabin fan (lead to too much CO2) F7 backup

	if (cabin_dp == 0)
		{
		if (cws_msg_hash.cabinfan == 0)
			{		
			setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
			create_fault_message("S66 CABIN     ", " FAN", "   4 ", 2, "PASS");
			cws_msg_hash.cabinfan = 1;
			}
		}


	###IMU delta pressure (As only one IMU fan is on normally, loss of this one will lead to delta P fault// No need for Imu fan fault specific hash) // class 3

	if (imu_dp == 0)
		{
		if (cws_msg_hash.imudp == 0)
			{			
			create_fault_message("S66 IMU FAN   ", "  DP", "   4 ", 2, "PASS");
			create_fault_message("S66 IMU FN SPD", "    ", "   4 ", 2, "PASS");
			cws_msg_hash.imudp = 1;
			}
		}

	###Freon Flow (F7 and backup)

	if (freon_flow_1 == 0) 
		{
		if (cws_msg_hash.freon_flow1 == 0)
			{		
			setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
			create_fault_message("S88 FREON FLOW", "   1", "   4 ", 2, "PASS");
			create_fault_message("S88 FRN AFT CP", "   1", "   4 ", 2, "PASS");
			create_fault_message("S88 FRN PL HX ", "   1", "   4 ", 2, "PASS");
			cws_msg_hash.freon_flow1 = 1;
			}
		}

	if (freon_flow_2 == 0) 
		{
		if (cws_msg_hash.freon_flow2 == 0)
			{		
			setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
			create_fault_message("S88 FREON FLOW", "   2", "   4 ", 2, "PASS");
			create_fault_message("S88 FRN AFT CP", "   2", "   4 ", 2, "PASS");
			create_fault_message("S88 FRN PL HX ", "   2", "   4 ", 2, "PASS");
			cws_msg_hash.freon_flow2 = 1;
			}
		}


	###Evap Out T (F7 and backup) // Low at 20°F// High !=ascent at 65°F

	if ((evap_out < 266) or (evap_out > 292))
		{
		if (cws_msg_hash.evap_out_t == 0)
			{		
			setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
			create_fault_message("S88 EVAP OUT T", "  12", "   4 ", 2, "PASS");
			cws_msg_hash.evap_out_t = 1;
			}
		}

	
	###Water Loop ( F7 and backup) // Linked directly to the cws.xml condition (only one loop is active normally/not both)

	if (h2o_loop == 1)
		{
		if (cws_msg_hash.h2o_pump_p == 0)
			{		
			setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
			create_fault_message("S88 H2O PUMP P", "  12", "   4 ", 2, "PASS");
			create_fault_message("S88 H2O LOOP  ", "FLOW", "   4 ", 2, "PASS");
			cws_msg_hash.h2o_pump_p = 1;
			}
		}


	###Heaters intial condition ( T_aft < 45°F // 280°K)

	if (T_aft < 280)
		{
		
		###Apu line heaters ( just one hash for the three APU )

		if ((apu_heater_1 == 0)  or (apu_heater_2 == 0) or (apu_heater_3 == 0))
			{
			if (cws_msg_hash.apu_line_heaters == 0)
				{			
				create_fault_message("S88 APU FU LN ", "TEMP", "   4 ", 2, "PASS");
				create_fault_message("S88 APU FU PMP", "TEMP", "   4 ", 2, "PASS");
				cws_msg_hash.apu_line_heaters = 1;
				}
			}


		###FES heaters

		if (heater_top_duct == 0)
			{
			if (cws_msg_hash.top_heaters == 0)
				{			
				create_fault_message("S88 EVAP TOP  ", "TEMP", "   4 ", 2, "PASS");
				cws_msg_hash.top_heaters = 1;
				}

			}

		if (heater_hild == 0)
			{
			if (cws_msg_hash.hild_heaters == 0)
				{			
				create_fault_message("S88 EVAP HI LD", "TEMP", "   4 ", 2, "PASS");
				cws_msg_hash.hild_heaters = 1;
				}
			}


		if ((fdln_A_status == 0) or (fdln_B_status == 0))
			{
			if (cws_msg_hash.evap_fdln_heaters == 0)
				{			
				create_fault_message("S88 EVAP FDLN ", "TEMP", "   4 ", 2, "PASS");
				cws_msg_hash.evap_fdln_heaters = 1;
				}
			}

		}
	}



#BFS SM failure (Outside OPS 2 SM)
else 
	{
	
	###Av Bay temp (F7 hardware and SM light) // T > 130°F // One message for all bays 

	if ((avbay1_t > 328) or (avbay2_t > 328) or (avbay3_t > 328))
		{
		if (cws_msg_hash.avbayt1 == 0)
			{		
			create_fault_message("SM2 AVBAY TEMP", "    ", "    5", 2, "BFS");
			cws_msg_hash.avbayt1 = 1;
			}
		}


	###Av Bay fan (class 3) // One message for all fans

	if ((avbay1_fan < 3.20) or (avbay2_fan < 3.20) or (avbay3_fan < 3.20))
		{
		if (cws_msg_hash.avbayfan1 == 0)
			{		
			create_fault_message("SM2 AV BAY FAN", "    ", "    5", 2, "BFS");
			cws_msg_hash.avbayfan1 = 1;
			}
		}


	###Cabin Pressure (F7 and backup) ( Plus O2/N2 Flow as it will be max then// to avoid to call back 10 variables for Flow message fault)

	if (cabin_p < 13.8) 
		{
		if (cws_msg_hash.cabinp == 0)
			{		
			setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
			create_fault_message("SM1 CABIN     ", "PRES", "    5", 2, "BFS");
			create_fault_message("SM1 CABIN     ", "FLOW", "    5", 2, "BFS");
			cws_msg_hash.cabinp = 1;
			}
		}

	###Cabin dP/dT (class 3)

	if (dpdt_value < -0.12)
		{
		if (cws_msg_hash.cabindpdt == 0)
			{			
			create_fault_message("SM1 CABN DP/DT", "  BU", "    5", 2, "BFS");
			cws_msg_hash.cabindpdt = 1;
			}
		}

	###PPO2 (F7 Backup)

	if (ppo2_value < 2.7)
		{
		if (cws_msg_hash.ppo2 == 0)
			{		
			setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
			create_fault_message("SM1 CABIN PPO2", "    ", "    5", 2, "BFS");
			cws_msg_hash.ppo2 = 1;
			}
		}

	###Cabin fan (lead to too much CO2) F7 backup

	if (cabin_dp == 0)
		{
		if (cws_msg_hash.cabinfan == 0)
			{		
			setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
			create_fault_message("SM1 CABIN FAN ", "    ", "    5", 2, "BFS");
			cws_msg_hash.cabinfan = 1;
			}
		}

	###IMU delta pressure (As one IMU fan is on normally, loss of this one will lead to that fault// No need for Imu fan fault messages) // class 3

	if (imu_dp == 0)
		{
		if (cws_msg_hash.imudp == 0)
			{			
			create_fault_message("SM1 CABIN IMU ", "    ", "    5", 2, "BFS");
			cws_msg_hash.imudp = 1;
			}
		}


	###Freon Flow (F7 and backup)

	if (freon_flow_1 == 0) 
		{
		if (cws_msg_hash.freon_flow1 == 0)
			{		
			setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
			create_fault_message("SM2 FREON FLOW", "   1", "    5", 2, "BFS");
			cws_msg_hash.freon_flow1 = 1;
			}
		}

	if (freon_flow_2 == 0) 
		{
		if (cws_msg_hash.freon_flow2 == 0)
			{		
			setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
			create_fault_message("SM2 FREON FLOW", "   2", "    5", 2, "BFS");
			cws_msg_hash.freon_flow2 = 1;
			}
		}


	###Evap Out T (F7 and backup) // Low at 20°F// High 80°F (mean to avoid fault during ascent where is normally 115°F)

	if ((evap_out < 266) or (evap_out > 300))
		{
		if (cws_msg_hash.evap_out_t == 0)
			{		
			setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
			create_fault_message("SM2 EVAP OUT T", "  12", "    5", 2, "BFS");
			create_fault_message("SM0 THRM FRN  ", "    ", "    5", 2, "BFS"); #Rad out
			cws_msg_hash.evap_out_t = 1;
			}
		}


	###Water Loop ( F7 and backup) // Linked directly to the cws.xml condition

	if (h2o_loop == 1)
		{
		if (cws_msg_hash.h2o_pump_p == 0)
			{		
			setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
			create_fault_message("SM2 H2O PUMP P", "  12", "    5", 2, "BFS");
			cws_msg_hash.h2o_pump_p = 1;
			}
		}

	}

}




#################################################
# CWS checks of APU/HYD 
#################################################

var cws_inspect_apu_hyd = func {

var ops =  getprop("/fdm/jsbsim/systems/dps/ops");
var mm =  getprop("/fdm/jsbsim/systems/dps/major-mode");

# S86/SM2 variables ( Apu line heaters in ECLSS)

var apu1_fuel = getprop("/consumables/fuel/tank[14]/level-lbs")/3.5;
var apu2_fuel = getprop("/consumables/fuel/tank[15]/level-lbs")/3.5;
var apu3_fuel = getprop("/consumables/fuel/tank[16]/level-lbs")/3.5;

var oil_T1 = getprop("/fdm/jsbsim/systems/thermal-distribution/apu1-temperature-K");
var oil_T2 = getprop("/fdm/jsbsim/systems/thermal-distribution/apu2-temperature-K");
var oil_T3 = getprop("/fdm/jsbsim/systems/thermal-distribution/apu3-temperature-K");

var apu1_speed = 100.0 * getprop("/fdm/jsbsim/systems/apu/apu/apu-rpm-fraction");
var apu2_speed = 100.0 * getprop("/fdm/jsbsim/systems/apu/apu[1]/apu-rpm-fraction");
var apu3_speed = 100.0 * getprop("/fdm/jsbsim/systems/apu/apu[2]/apu-rpm-fraction");

var ggbed_T1 = getprop("/fdm/jsbsim/systems/apu/apu/gg-bed-T-K");
var ggbed_T2 = getprop("/fdm/jsbsim/systems/apu/apu[1]/gg-bed-T-K");
var ggbed_T3 = getprop("/fdm/jsbsim/systems/apu/apu[2]/gg-bed-T-K");

var hyd1_p = getprop("/fdm/jsbsim/systems/apu/apu/hyd-pressure-psia");
var hyd2_p = getprop("/fdm/jsbsim/systems/apu/apu[1]/hyd-pressure-psia");
var hyd3_p = getprop("/fdm/jsbsim/systems/apu/apu[2]/hyd-pressure-psia");

var h2o_1 = getprop("/fdm/jsbsim/propulsion/tank[20]/contents-lbs")/1.42;
var h2o_2 = getprop("/fdm/jsbsim/propulsion/tank[21]/contents-lbs")/1.42;
var h2o_3 = getprop("/fdm/jsbsim/propulsion/tank[22]/contents-lbs")/1.42;

var vent_t_1 = getprop("/fdm/jsbsim/systems/apu/apu/steam-vent-T-K");
var vent_t_2 = getprop("/fdm/jsbsim/systems/apu/apu[1]/steam-vent-T-K");
var vent_t_3 = getprop("/fdm/jsbsim/systems/apu/apu[2]/steam-vent-T-K");



if (ops == 2) #PASS SM
	{
	
	#No interest in Orbit to have many APU fault messages ( mainly used in OPS1/3/6) compared to BFS
	
	#GG bed temp (100°F/310K PASS )

	if (ggbed_T1 < 310)
		{
		if (cws_msg_hash.ggbedt_1 == 0)
			{			
			create_fault_message("S86 GG/FU PMP ", "   1", "   4 ", 2, "PASS");
			cws_msg_hash.ggbedt_1 = 1;
			}
		}

	if (ggbed_T2 < 310)
		{
		if (cws_msg_hash.ggbedt_2 == 0)
			{			
			create_fault_message("S86 GG/FU PMP ", "   2", "   4 ", 2, "PASS");
			cws_msg_hash.ggbedt_2 = 1;
			}
		}

	if (ggbed_T3 < 310)
		{
		if (cws_msg_hash.ggbedt_3 == 0)
			{			
			create_fault_message("S86 GG/FU PMP ", "   3", "   4 ", 2, "PASS");
			cws_msg_hash.ggbedt_3 = 1;
			}
		}

	#APU fuel (just one message in case APU not shut down after OPS 2 transition, as a reminder)

	if ((apu1_fuel < 35) or (apu2_fuel < 35) or (apu3_fuel < 35))
		{
		if (cws_msg_hash.apu_fuel_qty == 0)
			{			
			create_fault_message("S86 APU FUEL  ", " 123", "   4 ", 2, "PASS");
			cws_msg_hash.apu_fuel_qty = 1;
			}
		}

	
	#Hyd P ( F7 // backup for BFS only)

	if (hyd1_p < 1930)
		{
		if (cws_msg_hash.hyd_p1 == 0)
			{			
			create_fault_message("S86 HYD PRESS ", "   1", "   4 ", 2, "PASS");
			cws_msg_hash.hyd_p1 = 1;
			}
		}

	if (hyd2_p < 1930)
		{
		if (cws_msg_hash.hyd_p2 == 0)
			{			
			create_fault_message("S86 HYD PRESS ", "   2", "   4 ", 2, "PASS");
			cws_msg_hash.hyd_p2 = 1;
			}
		}

	if (hyd3_p < 1930)
		{
		if (cws_msg_hash.hyd_p3 == 0)
			{			
			create_fault_message("S86 HYD PRESS ", "   3", "   4 ", 2, "PASS");
			cws_msg_hash.hyd_p3 = 1;
			}
		}


	}

else #Outside of PASS // BFS SM
	{
	
	#GG bed temp (258°F/398K in BFS ) // thermal ops 0// Low temp means no heater and no restart available

	if ((ggbed_T1 < 398) or (ggbed_T2 < 398) or (ggbed_T3 < 398))
		{
		if (cws_msg_hash.ggbedt_1 == 0)
			{			
			create_fault_message("SM0 THRM APU  ", "    ", "    5", 2, "BFS");
			cws_msg_hash.ggbedt_1 = 1;
			}
		}

	#h2o qty

	
	if (h2o_1 < 50)
		{
		if (cws_msg_hash.wsb_qty_1 == 0)
			{			
			create_fault_message("SM2 W/B QTY   ", "   1", "    5", 2, "BFS");
			cws_msg_hash.wsb_qty_1 = 1;
			}
		}

	if (h2o_2 < 50)
		{
		if (cws_msg_hash.wsb_qty_2 == 0)
			{			
			create_fault_message("SM2 W/B QTY   ", "   2", "    5", 2, "BFS");
			cws_msg_hash.wsb_qty_2 = 1;
			}
		}

	if (h2o_3 < 50)
		{
		if (cws_msg_hash.wsb_qty_3 == 0)
			{			
			create_fault_message("SM2 W/B QTY   ", "   3", "    5", 2, "BFS");
			cws_msg_hash.wsb_qty_3 = 1;
			}
		}

	
	#Hyd P ( F7 // backup for BFS only < 2400 PSI)

	if (hyd1_p < 2400)
		{
		if (cws_msg_hash.hyd_p1 == 0)
			{			
			setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
			create_fault_message("SM2 HYD PRESS ", "   1", "    5", 2, "BFS");
			cws_msg_hash.hyd_p1 = 1;
			}
		}

	if (hyd2_p < 2400)
		{
		if (cws_msg_hash.hyd_p2 == 0)
			{			
			setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
			create_fault_message("SM2 HYD PRESS ", "   2", "    5", 2, "BFS");
			cws_msg_hash.hyd_p2 = 1;
			}
		}

	if (hyd3_p < 2400)
		{
		if (cws_msg_hash.hyd_p3 == 0)
			{			
			setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
			create_fault_message("SM2 HYD PRESS ", "   3", "    5", 2, "BFS");
			cws_msg_hash.hyd_p3 = 1;
			}
		}


	#APU BFS (Oil temp high 416°K//290°F or fuel quantity low < 35%)

	if ((apu1_fuel < 35) or (oil_T1 > 416))
		{
		if (cws_msg_hash.apu_bfs1 == 0)
			{			
			setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
			create_fault_message("SM2 APU       ", "   1", "    5", 2, "BFS");
			cws_msg_hash.apu_bfs1 = 1;
			}
		}

	if ((apu2_fuel < 35) or (oil_T2 > 416))
		{
		if (cws_msg_hash.apu_bfs2 == 0)
			{			
			setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
			create_fault_message("SM2 APU       ", "   2", "    5", 2, "BFS");
			cws_msg_hash.apu_bfs2 = 1;
			}
		}

	if ((apu3_fuel < 35) or (oil_T3 > 416))
		{
		if (cws_msg_hash.apu_bfs3 == 0)
			{			
			setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
			create_fault_message("SM2 APU       ", "   3", "    5", 2, "BFS");
			cws_msg_hash.apu_bfs3 = 1;
			}
		}


	#APU over/underspeed (better intial condition)

	if (getprop("fdm/jsbsim/systems/cws/apu-underspeed") == 1) #Initial condition is apu under/overspeed while apu is operating
		{

		if (apu1_speed < 80)
			{
			if (cws_msg_hash.apu_speed1 == 0)
				{			
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("SM2 APU SPD LO", "   1", "    5", 2, "BFS");
				cws_msg_hash.apu_speed1 = 1;
				}
			}

		if (apu2_speed < 80)
			{
			if (cws_msg_hash.apu_speed2 == 0)
				{			
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("SM2 APU SPD LO", "   2", "    5", 2, "BFS");
				cws_msg_hash.apu_speed2 = 1;
				}
			}

		if (apu3_speed < 80)
			{
			if (cws_msg_hash.apu_speed3 == 0)
				{			
				setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 1);	
				create_fault_message("SM2 APU SPD LO", "   3", "    5", 2, "BFS");
				cws_msg_hash.apu_speed3 = 1;
				}
			}
		}

	#SSME repositionning in OPS 3 (SM alert if MPS TVC valves or Hyd not opened/available leading to bad nozzle position)
	#OPS 3 PASS and BFS only

	if (mm == 304)
		{
		if ((getprop("/fdm/jsbsim/propulsion/engine[0]/pitch-angle-rad-cmd") == 0.0) or (getprop("/fdm/jsbsim/propulsion/engine[1]/pitch-angle-rad-cmd") == 0.0) or (getprop("/fdm/jsbsim/propulsion/engine[2]/pitch-angle-rad-cmd") == 0.0))
			{
			if (cws_msg_hash.ssme_repos == 0)
				{
				create_fault_message("SSME REPOSFAIL","    ", "1234 ", 2,"PASS");
				create_fault_message("SSME REPOSFAIL","    ", "    5", 2,"BFS");	
				cws_msg_hash.ssme_repos = 1;
				}

			}
		}

	}

}


#################################################
# MEDS inspection
#################################################

var meds_inspect = func {

for (var i=0; i< size(SpaceShuttle.MDU_array); i=i+1)
	{
	var mdu = SpaceShuttle.MDU_array[i];

	var idp_index = mdu.PFD.port_selected - 1;

	if ((mdu.operational == 0) and (meds_msg_hash.io[i] == 0))
		{
		meds_msg_hash.io[i] = 1;
		var message_long = create_meds_message_long("MEDS I/O ERROR", mdu.designation);
		var message_short = create_meds_message_short("MEDS I/O ERROR", mdu.designation);

		SpaceShuttle.idp_array[idp_index].current_fault_string = message_long;
		#print (message);	

		insert_meds_message(message_short, idp_index);
		}

	if ((mdu.PFD.polling_status == 0) and (meds_msg_hash.poll[idp_index] == 0))
		{
		meds_msg_hash.poll[idp_index] = 1;

		var message_long = create_meds_message_long("MEDS POLL FAIL", "IDP"~(idp_index+1));
		var message_short = create_meds_message_short("MEDS POLL FAIL", "IDP"~(idp_index+1));

		SpaceShuttle.idp_array[idp_index].current_fault_string = message_long;

		insert_meds_message(message_short, idp_index);

		}


	if ((mdu.PFD.auto_reconf_flag == 1) and (meds_msg_hash.port_change[i] == 0))
		{
		meds_msg_hash.port_change[i] = 1;

		var message_long = create_meds_message_long("MEDS PORT CHANGE", mdu.designation);
		var message_short = create_meds_message_short("MEDS PORT CHANGE", mdu.designation);

		mdu.PFD.auto_reconf_flag = 0;

		SpaceShuttle.idp_array[idp_index].current_fault_string = message_long;

		insert_meds_message(message_short, idp_index);

		}
	
	#GPC hardware failure, all OPS in PASS // Class F7 GPC yellow light and no Backup C/W light

	if (getprop("/fdm/jsbsim/systems/failures/dps/gpc-1-condition") == 0)
		{
		if (cws_msg_hash.gpc_fail_1 == 0)
			{
			create_fault_message("    GPC       ", "   1", " 234 ", 2, "PASS");		
			cws_msg_hash.gpc_fail_1 = 1;
			}
		}

	if (getprop("/fdm/jsbsim/systems/failures/dps/gpc-2-condition") == 0)
		{
		if (cws_msg_hash.gpc_fail_2 == 0)
			{
			create_fault_message("    GPC       ", "   2", "1 34 ", 2, "PASS");		
			cws_msg_hash.gpc_fail_2 = 1;
			}
		}

	if (getprop("/fdm/jsbsim/systems/failures/dps/gpc-3-condition") == 0)
		{
		if (cws_msg_hash.gpc_fail_3 == 0)
			{
			create_fault_message("    GPC       ", "   3", "12 4 ", 2, "PASS");		
			cws_msg_hash.gpc_fail_3 = 1;
			}
		}

	if (getprop("/fdm/jsbsim/systems/failures/dps/gpc-4-condition") == 0)
		{
		if (cws_msg_hash.gpc_fail_4 == 0)
			{
			create_fault_message("    GPC       ", "   4", "123  ", 2, "PASS");		
			cws_msg_hash.gpc_fail_4 = 1;
			}
		}

	if (getprop("/fdm/jsbsim/systems/failures/dps/gpc-5-condition") == 0)
		{
		if (cws_msg_hash.gpc_fail_5 == 0)
			{
			create_fault_message("    GPC       ", "   5", "1234 ", 2, "PASS");		
			cws_msg_hash.gpc_fail_5 = 1;
			}
		}
		

	}

}





var insert_fault_message_long = func (message) {

# shift all messages in the array such that zero becomes available

for (var i = 0; i<14; i=i+1)
	{
	cws_message_array_long[14-i] = cws_message_array_long[13-i];
	}
cws_message_array_long[0] = message;


}


var insert_fault_message_long_bfs = func (message) {

# shift all messages in the array such that zero becomes available

for (var i = 0; i<14; i=i+1)
	{
	cws_message_array_long_bfs[14-i] = cws_message_array_long_bfs[13-i];
	}
cws_message_array_long_bfs[0] = message;


}

var insert_meds_message = func (message, idp_index) {


for (var i = 0; i<14; i=i+1)
	{
	SpaceShuttle.idp_array[idp_index].fault_array[14-i] = SpaceShuttle.idp_array[idp_index].fault_array[13-i];
	}
SpaceShuttle.idp_array[idp_index].fault_array[0] = message;

}

#New function item ( type), need to add that in every fault messages ( if not, nasal fault too few arg 3 instead of 4)
#It allows to add a message to better identify the fault (Coming from Reference Data Book)

#Sys_string : 14 space
#Type: 4 space
#Back up marker: 1 space 
#GPC type: 5 space
#Rest is unchanged and constant space wise with new font width (680 for SSU A)


var create_fault_message = func (sys_string, type, gpc_id, class, sw = "ALL"){

#MET displayed for fault

var time_string = getprop("/fdm/jsbsim/systems/timer/MET-string");
var time_string_minimised = substr(time_string, 4);
var ops =  getprop("/fdm/jsbsim/systems/dps/ops");

var backup_marker = " ";
if (class == 2) {backup_marker = "*";}

var msg_string = sys_string~"  "~type~" "~backup_marker~""~gpc_id~"            "~time_string_minimised;
var msg_string_long = sys_string~" "~type~"  "~backup_marker~"   "~gpc_id~" "~time_string;

if (sw == "ALL")
	{
	
	#If No SM in GPC for OPS2, no fault messages in Orbit 
	if (SpaceShuttle.gpc_check_available("SM") == 0) 
		{
		if (ops == 2) {return;}
		else
			{
			insert_fault_message_long(msg_string_long);
			append(cws_message_array, msg_string);
			setprop("/fdm/jsbsim/systems/dps/error-string", msg_string);
			cws_last_message_acknowledge = 1;
			}
		}
	else
		{
		insert_fault_message_long(msg_string_long);
		append(cws_message_array, msg_string);
		setprop("/fdm/jsbsim/systems/dps/error-string", msg_string);
		cws_last_message_acknowledge = 1;
		}

	#If No BFS in GPC, no BFS SM fault messages 
	if (SpaceShuttle.gpc_check_available("BFS") == 1)
	 	{
		insert_fault_message_long_bfs(msg_string_long);
		append(cws_message_array_bfs, msg_string);
		setprop("/fdm/jsbsim/systems/dps/bfs-error-string", msg_string);
		cws_last_message_acknowledge_bfs = 1;
		}
	}
else if (sw == "BFS")
	{

	#If No BFS in GPC, no BFS SM fault messages 
	if (SpaceShuttle.gpc_check_available("BFS") == 0) {return;}

	insert_fault_message_long_bfs(msg_string_long);
	append(cws_message_array_bfs, msg_string);

	setprop("/fdm/jsbsim/systems/dps/bfs-error-string", msg_string);
	cws_last_message_acknowledge_bfs = 1;
	}
else if (sw == "PASS")
	{

	#If No SM in GPC for OPS2, no fault messages in Orbit
	if ((SpaceShuttle.gpc_check_available("SM") == 0) and (ops == 2)) {return;}

	insert_fault_message_long(msg_string_long);
	append(cws_message_array, msg_string);

	setprop("/fdm/jsbsim/systems/dps/error-string", msg_string);
	cws_last_message_acknowledge = 1;
	}




#Specifically set either class 2 Backup alert or class 3 Sm alert depending on failures, instead of a general sm alert when there is a failure somewhere
#setprop("/fdm/jsbsim/systems/cws/sm-alert-on", 1);


#Either Class 2 Backup fault message or class 3 Sm Alert fault message and tone (class 3 no * in message)
#For Class 2 F7 Backup C/W (software), either BFS or SM in OPS 2 is needed, else just the normal F7 primary light will be triggered (hardware)
#SM alert needs also a dependency to a SM soft

var backup_alarm_trigger = getprop("/fdm/jsbsim/systems/cws/backup-alarm-on");
 
if (ops == 2) #PASS SM
	{
	if (SpaceShuttle.gpc_check_available("SM") == 1) 
		{
		if (backup_alarm_trigger == 1) {setprop("/fdm/jsbsim/systems/cws/sm-alert-on", 0);}
		else {setprop("/fdm/jsbsim/systems/cws/sm-alert-on", 1);}
		}
	else {setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 0);} #No alarms if no SM
	}

else #BFS SM
	{
	if (SpaceShuttle.gpc_check_available("BFS") == 1) 
		{
		if (backup_alarm_trigger == 1) {setprop("/fdm/jsbsim/systems/cws/sm-alert-on", 0);}
		else {setprop("/fdm/jsbsim/systems/cws/sm-alert-on", 1);}
		}
	else {setprop("/fdm/jsbsim/systems/cws/backup-alarm-on", 0);} #No alarms if no SM
	}
		


}



# Long message for fault display on MEDS screen
# Short message for display on MEDS fault page

var create_meds_message_long = func (text, origin) {

var time_string = getprop("/fdm/jsbsim/systems/timer/MET-string");
meds_last_message_acknowledge = 1;

return (" "~text~" "~origin~"               "~time_string);

}

var create_meds_message_short = func (text, origin) {

var time_string = getprop("/fdm/jsbsim/systems/timer/MET-string");
meds_last_message_acknowledge = 1;

return (" "~text~" "~origin~"          "~time_string);

}


#################################################
# I/O reset
#################################################

# (this re-triggers search for 'fixable' faults)
#August2020: Oms/RCS/IMU temperature
#November 2020
	#Elec: Ac ovld/Fc Volt/ Mn Volt/ Fc Amp /StackT/Fc Pump/Fc reac valve
	#Apu/hyd: Temp, Qty, Hyd pressure, gg bed temp, h2o qty, apu speed
	#ECLSS: Avbay Temp/Avbay fan/Cabin P/Cabin dPdT/ppo2/cabin fan/imu dp/freon flow/evap t/h2o p/Heaters
#December 2020
	#Engines: SSME repos in OPS 3
#February 2021
	#Nav TAEM: Downmode to Stin/ MEP
	#Aero: High Radial Gs

var io_reset = func {

cws_msg_hash.xfeedtemp = 0;
cws_msg_hash.omstemp = 0;
cws_msg_hash.rcsftemp = 0;
cws_msg_hash.acvolt1 = 0;
cws_msg_hash.acvolt2 = 0;
cws_msg_hash.acvolt3 = 0;
cws_msg_hash.acovld1 = 0;
cws_msg_hash.acovld2 = 0;
cws_msg_hash.acovld3 = 0;
cws_msg_hash.fcvolt1 = 0;
cws_msg_hash.fcvolt2 = 0;
cws_msg_hash.fcvolt3 = 0;
cws_msg_hash.mnvolta = 0;
cws_msg_hash.mnvoltb = 0;
cws_msg_hash.mnvoltc = 0;
cws_msg_hash.fcamp1 = 0;
cws_msg_hash.fcamp2 = 0;
cws_msg_hash.fcamp3 = 0;
cws_msg_hash.stackt1 = 0;
cws_msg_hash.stackt2 = 0;
cws_msg_hash.stackt3 = 0;
cws_msg_hash.fcpump1 = 0;
cws_msg_hash.fcpump2 = 0;
cws_msg_hash.fcpump3 = 0;
cws_msg_hash.fcreac1 = 0;
cws_msg_hash.fcreac2 = 0;
cws_msg_hash.fcreac3 = 0;
cws_msg_hash.rm_fail_tac = 0;
cws_msg_hash.rm_dlm_tac = 0;
cws_msg_hash.nav_edit_tac = 0;
cws_msg_hash.nav_edit_alt = 0;
cws_msg_hash.rm_fail_adta = 0;
cws_msg_hash.rm_dlma_adta = 0;
cws_msg_hash.rm_fail_imu = 0;
cws_msg_hash.rm_dlma_imu = 0;
cws_msg_hash.imu_temp = 0;
cws_msg_hash.mps_manf = 0;
cws_msg_hash.avbayt1 = 0;
cws_msg_hash.avbayt2 = 0;
cws_msg_hash.avbayt3 = 0;
cws_msg_hash.avbayfan1 = 0;
cws_msg_hash.avbayfan2 = 0;
cws_msg_hash.avbayfan3 = 0;
cws_msg_hash.cabinp = 0;
cws_msg_hash.cabindpdt = 0;
cws_msg_hash.ppo2 = 0;
cws_msg_hash.cabinfan = 0;
cws_msg_hash.imudp = 0;
cws_msg_hash.freon_flow1 = 0;
cws_msg_hash.freon_flow2 = 0;
cws_msg_hash.evap_out_t = 0;
cws_msg_hash.h2o_pump_p = 0;
cws_msg_hash.top_heaters = 0;
cws_msg_hash.hild_heaters = 0;
cws_msg_hash.apu_line_heaters = 0;
cws_msg_hash.evap_fdln_heaters = 0;
cws_msg_hash.apu_bfs1 = 0;
cws_msg_hash.apu_bfs2 = 0;
cws_msg_hash.apu_bfs3 = 0;
cws_msg_hash.apu_speed1 = 0;
cws_msg_hash.apu_speed2 = 0;
cws_msg_hash.apu_speed3 = 0;
cws_msg_hash.ggbedt_1 = 0;
cws_msg_hash.ggbedt_2 = 0;
cws_msg_hash.ggbedt_3 = 0;
cws_msg_hash.hyd_p1 = 0;
cws_msg_hash.hyd_p2 = 0;
cws_msg_hash.hyd_p3 = 0;
#cws_msg_hash.wsb_vent_t = 0;
#cws_msg_hash.wsb_qty_1 = 0;
#cws_msg_hash.wsb_qty_2 = 0;
#cws_msg_hash.wsb_qty_3 = 0;
cws_msg_hash.ssme_repos = 0;
cws_msg_hash.ott_stn_in = 0;
cws_msg_hash.mep = 0;
cws_msg_hash.high_g = 0;

}


var io_reset_bfs = func {

setprop("/fdm/jsbsim/systems/dps/bfs/bfs-transient-error", 0);

if (SpaceShuttle.bfs_in_control == 1)
	{
	setprop("/fdm/jsbsim/systems/dps/bfs/bfc-light-status",1);
	}
else
	{
	setprop("/fdm/jsbsim/systems/dps/bfs/bfc-light-status",0);
	}

}


#################################################
# BFS/PASS discrepancies
#################################################


var compare_bfs_pass = func {

if (SpaceShuttle.bfs_in_control == 1) {return;}

var error_pitch = getprop("/fdm/jsbsim/systems/navigation/state-vector/pass/error-pitch");
var error_roll = getprop("/fdm/jsbsim/systems/navigation/state-vector/pass/error-roll");
var error_yaw = getprop("/fdm/jsbsim/systems/navigation/state-vector/pass/error-yaw");
var transient_error = 0;

if (SpaceShuttle.dps_simulation_detail_level == 1)
	{transient_error = getprop("/fdm/jsbsim/systems/dps/bfs/bfs-transient-error");}

if ((math.abs(error_pitch) > 0.0) or (math.abs(error_roll) > 0.0) or (math.abs(error_yaw) > 0.0) or (transient_error == 1))
	{
	SpaceShuttle.toggle_property("/fdm/jsbsim/systems/dps/bfs/bfc-light-status");
	}
}


#################################################
# Master Alarm
#################################################


var master_alarm_mngr = {

	# 0: no issue 1: light and alarm on 2: light on, alarm tone ended

	left_oms_flag: 0,
	right_oms_flag: 0,
	kit_oms_flag: 0,
	oms_tvc_flag: 0,
	fwd_rcs_flag: 0,
	left_rcs_flag: 0,
	right_rcs_flag: 0,
	fc_stack_temp_flag: 0,
	fc_pump_flag: 0,
	fc_reac_flag: 0,
	main_bus_undervolt_flag: 0,
	ac_voltage_flag: 0,
	ac_overload_flag: 0,
	h2o_loop_flag: 0,
	freon_loop_flag: 0,
	cabin_atm_flag: 0,
	avbay_cabin_air_flag: 0,
	hyd_press_flag: 0,
	apu_overspeed_flag: 0,
	apu_underspeed_flag: 0,
	apu_temp_flag: 0,	
	mps_flag: 0,
	depressurize_flag: 0,
	smoke_flag: 0,
	engine_fail_flag: 0,
	imu_dlma_flag: 0,
	gpc_hardware_fail_flag: 0,


	mode: 0, # -1: ASCENT 0: NORM 1: ACK


	init: func {
		
		me.nd_ref_left_oms = props.globals.getNode("/fdm/jsbsim/systems/cws/left-oms", 1);
		me.nd_ref_right_oms = props.globals.getNode("/fdm/jsbsim/systems/cws/right-oms", 1);
		me.nd_ref_kit_oms = props.globals.getNode("/fdm/jsbsim/systems/cws/kit-oms", 1);
		me.nd_ref_oms_tvc = props.globals.getNode("/fdm/jsbsim/systems/cws/oms-tvc", 1);
		me.nd_ref_rcs_jet = props.globals.getNode("/fdm/jsbsim/systems/cws/rcs-jet", 1);
		me.nd_ref_fwd_rcs = props.globals.getNode("/fdm/jsbsim/systems/cws/fwd-rcs", 1);
		me.nd_ref_left_rcs = props.globals.getNode("/fdm/jsbsim/systems/cws/left-rcs", 1);
		me.nd_ref_right_rcs = props.globals.getNode("/fdm/jsbsim/systems/cws/right-rcs", 1);
		me.nd_ref_fuel_cell_stack_temp = props.globals.getNode("/fdm/jsbsim/systems/cws/fuel-cell-stack-temp", 1);
		me.nd_ref_fuel_cell_pump = props.globals.getNode("/fdm/jsbsim/systems/cws/fuel-cell-pump", 1);
		me.nd_ref_fuel_cell_reac = props.globals.getNode("/fdm/jsbsim/systems/cws/fuel-cell-reac", 1);
		me.nd_ref_main_bus_undervolt = props.globals.getNode("/fdm/jsbsim/systems/cws/main-bus-undervolt", 1);
		me.nd_ref_ac_voltage = props.globals.getNode("/fdm/jsbsim/systems/cws/ac-voltage", 1);
		me.nd_ref_ac_overload = props.globals.getNode("/fdm/jsbsim/systems/cws/ac-overload", 1);
		me.nd_ref_h2o_loop = props.globals.getNode("/fdm/jsbsim/systems/cws/h2o-loop", 1);
		me.nd_ref_freon_loop = props.globals.getNode("/fdm/jsbsim/systems/cws/freon-loop", 1);
		me.nd_ref_cabin_atm = props.globals.getNode("/fdm/jsbsim/systems/cws/cabin-atm", 1);
		me.nd_ref_avbay_cabin_air = props.globals.getNode("/fdm/jsbsim/systems/cws/avbay-cabin-air", 1);
		me.nd_ref_hyd_press = props.globals.getNode("/fdm/jsbsim/systems/cws/hyd-press", 1);
		me.nd_ref_apu_overspeed = props.globals.getNode("/fdm/jsbsim/systems/cws/apu-overspeed", 1);
		me.nd_ref_apu_underspeed = props.globals.getNode("/fdm/jsbsim/systems/cws/apu-underspeed", 1);
		me.nd_ref_apu_temp = props.globals.getNode("/fdm/jsbsim/systems/cws/apu-temp", 1);
		me.nd_ref_mps = props.globals.getNode("/fdm/jsbsim/systems/cws/mps", 1);
		me.nd_ref_depressurize = props.globals.getNode("/fdm/jsbsim/systems/cws/emergency-depressurization", 1);
		me.nd_ref_engine_fail = props.globals.getNode("/fdm/jsbsim/systems/mps/number-engines-operational", 1);
		me.nd_ref_imu_dlma = props.globals.getNode("/fdm/jsbsim/systems/cws/imu-dlma", 1);
		me.nd_ref_gpc_hardware_fail = props.globals.getNode("/fdm/jsbsim/systems/cws/gpc-hardware-fault", 1);
		},


	inspect: func {


		var flag = 0;


		#IMU Dilemma
		if (me.nd_ref_imu_dlma.getValue() == 1) 
			{
			if (me.imu_dlma_flag == 0)
				{
				me.set_class2_alarm();
				me.imu_dlma_flag = 1;
				}
			}
		else
			{
			me.imu_dlma_flag = 0;
			}


		#MPS engine failure (No F7 light but Master Caution light and alarm) No Alarm for MECO Shutdown
		if ((me.nd_ref_engine_fail.getValue() < 3) and (getprop("/fdm/jsbsim/systems/ap/launch/regular-meco-condition") != 1.0))
			{
			if (me.engine_fail_flag == 0)
				{
				me.set_class2_alarm();
				me.engine_fail_flag = 1;
				}
			}
		else
			{
			me.engine_fail_flag = 0;
			}


		# left OMS
		if (me.nd_ref_left_oms.getValue() == 1) 
			{
			if (me.left_oms_flag == 0)
				{
				me.set_class2_alarm();
				me.left_oms_flag = 1;
				}
			}
		else
			{
			me.left_oms_flag = 0;
			}

		# right OMS
		if (me.nd_ref_right_oms.getValue() == 1) 
			{
			if (me.right_oms_flag == 0)
				{
				me.set_class2_alarm();
				me.right_oms_flag = 1;
				}
			}
		else
			{
			me.right_oms_flag = 0;
			}

		#  OMS KIT
		if (me.nd_ref_kit_oms.getValue() == 1) 
			{
			if (me.kit_oms_flag == 0)
				{
				me.set_class2_alarm();
				me.kit_oms_flag = 1;
				}
			}
		else
			{
			me.kit_oms_flag = 0;
			}

		# OMS TVC
		if (me.nd_ref_oms_tvc.getValue() == 1) 
			{
			if (me.oms_tvc_flag == 0)
				{
				me.set_class2_alarm();
				me.oms_tvc_flag = 1;
				}
			}
		else
			{
			me.oms_tvc_flag = 0;
			}

		# RCS JET (Fail On/Off)

		if (me.nd_ref_rcs_jet.getValue() == 1) 
			{
			if (me.rcs_jet_flag == 0)
				{
				me.set_class2_alarm();
				me.rcs_jet_flag = 1;
				}
			}
		else
			{
			me.rcs_jet_flag = 0;
			}

		# FWD RCS

		if (me.nd_ref_fwd_rcs.getValue() == 1) 
			{
			if (me.fwd_rcs_flag == 0)
				{
				me.set_class2_alarm();
				me.fwd_rcs_flag = 1;
				}
			}
		else
			{
			me.fwd_rcs_flag = 0;
			}

		# LEFT RCS

		if (me.nd_ref_left_rcs.getValue() == 1) 
			{
			if (me.left_rcs_flag == 0)
				{
				me.set_class2_alarm();
				me.left_rcs_flag = 1;
				}
			}
		else
			{
			me.left_rcs_flag = 0;
			}

		# RIGHT RCS

		if (me.nd_ref_right_rcs.getValue() == 1) 
			{
			if (me.right_rcs_flag == 0)
				{
				me.set_class2_alarm();
				me.right_rcs_flag = 1;
				}
			}
		else
			{
			me.right_rcs_flag = 0;
			}

		# GPC FAIL

		if (me.nd_ref_gpc_hardware_fail.getValue() == 1) 
			{
			if (me.gpc_hardware_fail_flag == 0)
				{
				me.set_class2_alarm();
				me.gpc_hardware_fail_flag = 1;
				}
			}
		else
			{
			me.gpc_hardware_fail_flag = 0;
			}

		# FUEL CELL STACK TEMP

		if (me.nd_ref_fuel_cell_stack_temp.getValue() == 1) 
			{
			if (me.fc_stack_temp_flag == 0)
				{
				me.set_class2_alarm();
				me.fc_stack_temp_flag = 1;
				}
			}
		else
			{
			me.fc_stack_temp_flag = 0;
			}

		# FUEL CELL PUMP

		if (me.nd_ref_fuel_cell_pump.getValue() == 1) 
			{
			if (me.fc_pump_flag == 0)
				{
				me.set_class2_alarm();
				me.fc_pump_flag = 1;
				}
			}
		else
			{
			me.fc_pump_flag = 0;
			}

		# FUEL CELL REACTANT

		if (me.nd_ref_fuel_cell_reac.getValue() == 1) 
			{
			if (me.fc_reac_flag == 0)
				{
				me.set_class2_alarm();
				me.fc_reac_flag = 1;
				}
			}
		else
			{
			me.fc_reac_flag = 0;
			}

		# MAIN BUS UNDERVOLT

		if (me.nd_ref_main_bus_undervolt.getValue() == 1) 
			{
			if (me.main_bus_undervolt_flag == 0)
				{
				me.set_class2_alarm();
				me.main_bus_undervolt_flag = 1;
				}
			}
		else
			{
			me.main_bus_undervolt_flag = 0;
			}

		# AC VOLTAGE

		if (me.nd_ref_ac_voltage.getValue() == 1) 
			{
			if (me.ac_voltage_flag == 0)
				{
				me.set_class2_alarm();
				me.ac_voltage_flag = 1;
				}
			}
		else
			{
			me.ac_voltage_flag = 0;
			}

		# AC OVERLOAD

		if (me.nd_ref_ac_overload.getValue() == 1) 
			{
			if (me.ac_overload_flag == 0)
				{
				me.set_class2_alarm();
				me.ac_overload_flag = 1;
				}
			}
		else
			{
			me.ac_overload_flag = 0;
			}

		# H2O LOOP

		if (me.nd_ref_h2o_loop.getValue() == 1) 
			{
			if (me.h2o_loop_flag == 0)
				{
				me.set_class2_alarm();
				me.h2o_loop_flag = 1;
				}
			}
		else
			{
			me.h2o_loop_flag = 0;
			}

		# FREON LOOP

		if (me.nd_ref_freon_loop.getValue() == 1) 
			{
			if (me.freon_loop_flag == 0)
				{
				me.set_class2_alarm();
				me.freon_loop_flag = 1;
				}
			}
		else
			{
			me.freon_loop_flag = 0;
			}

		# CABIN ATM

		if (me.nd_ref_cabin_atm.getValue() == 1) 
			{
			if (me.cabin_atm_flag == 0)
				{
				me.set_class2_alarm();
				me.cabin_atm_flag = 1;
				}
			}
		else
			{
			me.cabin_atm_flag = 0;
			}

		# AVBAY CABIN AIR

		if (me.nd_ref_avbay_cabin_air.getValue() == 1) 
			{
			if (me.avbay_cabin_air_flag == 0)
				{
				me.set_class2_alarm();
				me.avbay_cabin_air_flag = 1;
				}
			}
		else
			{
			me.avbay_cabin_air_flag = 0;
			}

		# HYD PRESS

		if (me.nd_ref_hyd_press.getValue() == 1) 
			{
			if (me.hyd_press_flag == 0)
				{
				#me.set_class2_alarm();
				me.hyd_press_flag = 1;
				}
			}
		else
			{
			me.hyd_press_flag = 0;
			}

		# APU OVERSPEED

		if (me.nd_ref_apu_overspeed.getValue() == 1) 
			{
			if (me.apu_overspeed_flag == 0)
				{
				me.set_class2_alarm();
				me.apu_overspeed_flag = 1;
				}
			}
		else
			{
			me.apu_overspeed_flag = 0;
			}

		# APU UNDERSPEED

		if (me.nd_ref_apu_underspeed.getValue() == 1) 
			{
			if (me.apu_underspeed_flag == 0)
				{
				me.set_class2_alarm();
				me.apu_underspeed_flag = 1;
				}
			}
		else
			{
			me.apu_underspeed_flag = 0;
			}

		# APU TEMP

		if (me.nd_ref_apu_temp.getValue() == 1) 
			{
			if (me.apu_temp_flag == 0)
				{
				me.set_class2_alarm();
				me.apu_temp_flag = 1;
				}
			}
		else
			{
			me.apu_temp_flag = 0;
			}

		# MPS

		if (me.nd_ref_mps.getValue() == 1) 
			{
			if (me.mps_flag == 0)
				{
				me.set_class2_alarm();
				me.mps_flag = 1;
				}
			}
		else
			{
			me.mps_flag = 0;
			}

		# EMERGENCY DEPRESSURIZATION

		if (me.nd_ref_depressurize.getValue() == 1) 
			{
			if (me.depressurize_flag == 0)
				{
				me.set_class1_alarm();
				me.depressurize_flag = 1;
				}
			}
		else
			{
			me.depressurize_flag = 0;
			}


		# SMOKE DETECTION

		if (SpaceShuttle.fire_sim.smoke_avbay1 > 2.0)
			{	
			if (me.smoke_flag == 0)
				{
				me.set_fire_alarm("avbay1");
				me.smoke_flag = 1;
				}

			}
		else if (SpaceShuttle.fire_sim.smoke_avbay2 > 2.0)
			{	
			if (me.smoke_flag == 0)
				{
				me.set_fire_alarm("avbay2");
				me.smoke_flag = 1;
				}

			}
		if (SpaceShuttle.fire_sim.smoke_avbay3 > 2.0)
			{	
			if (me.smoke_flag == 0)
				{
				me.set_fire_alarm("avbay3");
				me.smoke_flag = 1;
				}

			}







	},


	set_fire_alarm: func (location) {


		var cb_avbay_1A2B = getprop("/fdm/jsbsim/systems/circuit-breakers/smoke-detn-bay-1A2B");
		var cb_avbay_1B3A = getprop("/fdm/jsbsim/systems/circuit-breakers/smoke-detn-bay-1B3A");
		var cb_avbay_2A3B = getprop("/fdm/jsbsim/systems/circuit-breakers/smoke-detn-bay-2A3B");



		if (location == "avbay1")
			{
			if ((cb_avbay_1A2B == 0) and (cb_avbay_1B3A == 0)) {return;}
			}
		else if (location == "avbay2")
			{
			if ((cb_avbay_1A2B == 0) and (cb_avbay_2A3B == 0)) {return;}
			}
		else if (location == "avbay3")
			{
			if ((cb_avbay_1B3A == 0) and (cb_avbay_2A3B == 0)) {return;}
			}


		if (me.mode > -1)
			{setprop("/fdm/jsbsim/systems/cws/master-alarm-cdr-on", 1);}
		setprop("/fdm/jsbsim/systems/cws/master-alarm-plt-on", 1);
		setprop("/fdm/jsbsim/systems/cws/master-alarm-aft-on", 1);

		setprop("/fdm/jsbsim/systems/cws/fire-alarm-sound-on", 1);

		if (location == "avbay1")
			{
			if (cb_avbay_1A2B == 1)
				{
				setprop("/fdm/jsbsim/systems/fire-suppression/sd-avbay1-light-l",1);
				}
			if (cb_avbay_1B3A == 1)
				{
				setprop("/fdm/jsbsim/systems/fire-suppression/sd-avbay1-light-r",1);
				}
			}

		else if (location == "avbay2")
			{
			if (cb_avbay_2A3B == 1)
				{
				setprop("/fdm/jsbsim/systems/fire-suppression/sd-avbay2-light-l",1);	
				}
			if (cb_avbay_1A2B == 1)
				{
				setprop("/fdm/jsbsim/systems/fire-suppression/sd-avbay2-light-r",1);
				}
			}
		else if (location == "avbay3")
			{
			if (cb_avbay_1B3A == 1)
				{
				setprop("/fdm/jsbsim/systems/fire-suppression/sd-avbay3-light-l",1);
				}
			if (cb_avbay_2A3B == 1)
				{
				setprop("/fdm/jsbsim/systems/fire-suppression/sd-avbay3-light-r",1);
				}
			}

	},


	set_class1_alarm: func {


		if (me.mode > -1)
			{setprop("/fdm/jsbsim/systems/cws/master-alarm-cdr-on", 1);}
		setprop("/fdm/jsbsim/systems/cws/master-alarm-plt-on", 1);
		setprop("/fdm/jsbsim/systems/cws/master-alarm-aft-on", 1);

		setprop("/fdm/jsbsim/systems/cws/class-1-sound-on", 1);

	},

	set_class2_alarm: func {

		if (me.mode > -1)
			{setprop("/fdm/jsbsim/systems/cws/master-alarm-cdr-on", 1);}
		setprop("/fdm/jsbsim/systems/cws/master-alarm-plt-on", 1);
		setprop("/fdm/jsbsim/systems/cws/master-alarm-aft-on", 1);

		setprop("/fdm/jsbsim/systems/cws/class-2-sound-on", 1);

	},


	set_mode: func (mode) {

		me.mode = mode;

		if (me.mode == -1)
			{
			setprop("/fdm/jsbsim/systems/cws/master-alarm-cdr-on", 0);
			}

	},

	unset_alarm: func {

		setprop("/fdm/jsbsim/systems/cws/class-1-sound-on", 0);
		setprop("/fdm/jsbsim/systems/cws/class-2-sound-on", 0);
		setprop("/fdm/jsbsim/systems/cws/fire-alarm-sound-on", 0);
		setprop("/fdm/jsbsim/systems/cws/master-alarm-cdr-on", 0);
		setprop("/fdm/jsbsim/systems/cws/master-alarm-plt-on", 0);
		setprop("/fdm/jsbsim/systems/cws/master-alarm-aft-on", 0);

		if (me.left_oms_flag == 1) {me.left_oms_flag = 2;}
		if (me.right_oms_flag == 1) {me.right_oms_flag = 2;}
		if (me.kit_oms_flag == 1) {me.kit_oms_flag = 2;}
		if (me.oms_tvc_flag == 1) {me.oms_tvc_flag = 2;}
		if (me.rcs_jet_flag == 1) {me.rcs_jet_flag = 2;}
		if (me.fwd_rcs_flag == 1) {me.fwd_rcs_flag = 2;}
		if (me.left_rcs_flag == 1) {me.left_rcs_flag = 2;}
		if (me.right_rcs_flag == 1) {me.right_rcs_flag = 2;}
		if (me.fc_stack_temp_flag == 1) {me.fc_stack_temp_flag = 2;}
		if (me.fc_pump_flag == 1) {me.fc_pump_flag = 2;}
		if (me.fc_reac_flag == 1) {me.fc_reac_flag = 2;}
		if (me.main_bus_undervolt_flag == 1) {me.main_bus_undervolt_flag = 2;}
		if (me.ac_voltage_flag == 1) {me.ac_voltage_flag = 2;}
		if (me.ac_overload_flag == 1) {me.ac_overload_flag = 2;}
		if (me.h2o_loop_flag == 1) {me.h2o_loop_flag = 2;}
		if (me.freon_loop_flag == 1) {me.freon_loop_flag = 2;}
		if (me.cabin_atm_flag == 1) {me.cabin_atm_flag = 2;}
		if (me.avbay_cabin_air_flag == 1) {me.avbay_cabin_air_flag = 2;}
		if (me.hyd_press_flag == 1) {me.hyd_press_flag = 2;}
		if (me.apu_overspeed_flag == 1) {me.apu_overspeed_flag = 2;}
		if (me.apu_underspeed_flag == 1) {me.apu_underspeed_flag = 2;}
		if (me.apu_temp_flag == 1) {me.apu_temp_flag = 2;}
		if (me.mps_flag == 1) {me.mps_flag = 2;}
		if (me.depressurize_flag == 1) {me.depressurize_flag = 2;}
		if (me.engine_fail_flag == 1) {me.engine_fail_flag = 2;}
		if (me.imu_dlma_flag == 1) {me.imu_dlma_flag = 2;}
		if (me.gpc_hardware_fail_flag == 1) {me.gpc_hardware_fail_flag = 2;}
		

	},

	unlock_smoke_detection: func {

		print ("Resetting smoke detector");

		me.smoke_flag = 0;
		setprop("/fdm/jsbsim/systems/fire-suppression/sd-avbay1-light-l",0);	
		setprop("/fdm/jsbsim/systems/fire-suppression/sd-avbay1-light-r",0);	

		setprop("/fdm/jsbsim/systems/fire-suppression/sd-avbay2-light-l",0);	
		setprop("/fdm/jsbsim/systems/fire-suppression/sd-avbay2-light-r",0);

		setprop("/fdm/jsbsim/systems/fire-suppression/sd-avbay3-light-l",0);	
		setprop("/fdm/jsbsim/systems/fire-suppression/sd-avbay3-light-r",0);		
	},
	

};

master_alarm_mngr.init();
