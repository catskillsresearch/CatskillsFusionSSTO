# support for training scenarios for the Space Shuttle
# Thorsten Renk 2019


var training_manager = {

	verbose: 1,
	breakpoint_1: 0.0,
	breakpoint_2: 0.0,
	breakpoint_3: 0.0,
	endpoint: 0.0,

	scenario_running: 0,

	init_ascent_easy: func {


		if (getprop("/sim/config/shuttle/prelaunch-flag") == 0)
			{
			SpaceShuttle.callout.make("Ascent training scenario can only be selected before ignition!", "essential");
			return;
			}

		if (me.scenario_running == 1)
			{
			SpaceShuttle.callout.make("Another training scenario is already running", "essential");
			return;
			}

		srand();

		me.breakpoint_1 = 150.0 + rand() * 200.0;
		me.endpoint = me.breakpoint_1 + 10.0;

		if (me.verbose == 1)
			{
			print("Init easy ascent failure training");
			print("Failure time is ", me.breakpoint_1);
			}

		me.scenario_running = 1;
		me.run_ascent_easy();

	},


	run_ascent_easy: func {

		var met = SpaceShuttle.get_MET();
	
		if (met > me.endpoint) 
			{
			if (me.verbose == 1) {print ("Training manager signing off...");}
			return;
			}

		if ((met > me.breakpoint_1) and (me.breakpoint_1 > 0.0)) 
			{
			if (rand() < 0.5)
				{me.failure_ascent_minor();}
			else
				{me.failure_ascent_medium();}
			me.breakpoint_1 = 0.0;

			} 


		settimer (func {me.run_ascent_easy();}, 5.0);

	},

	init_ascent_medium: func {


		if (getprop("/sim/config/shuttle/prelaunch-flag") == 0)
			{
			SpaceShuttle.callout.make("Ascent training scenario can only be selected before ignition!", "essential");
			return;
			}

		if (me.scenario_running == 1)
			{
			SpaceShuttle.callout.make("Another training scenario is already running", "essential");
			return;
			}

		srand();

		me.breakpoint_1 = 10.0 + rand() * 200.0;
		me.breakpoint_2 = me.breakpoint_1 + rand() * 200.0;
		me.endpoint = me.breakpoint_2 + 10.0;

		if (me.verbose == 1)
			{
			print("Init medium ascent failure training");
			print("Failure time 1 is ", me.breakpoint_1);
			print("Failure time 2 is ", me.breakpoint_2);
			}

		me.scenario_running = 1;
		me.run_ascent_medium();

	},


	run_ascent_medium: func {

		var met = SpaceShuttle.get_MET();
	
		if (met > me.endpoint) 
			{
			if (me.verbose == 1) {print ("Training manager signing off...");}
			return;
			}

		if ((met > me.breakpoint_1) and (me.breakpoint_1 > 0.0)) 
			{
			if (rand() < 0.3)
				{me.failure_ascent_minor();}
			else
				{me.failure_ascent_medium();}
			me.breakpoint_1 = 0.0;

			} 

		if ((met > me.breakpoint_2) and (me.breakpoint_2 > 0.0)) 
			{
			if (rand() < 0.5)
				{me.failure_ascent_minor();}
			else
				{me.failure_ascent_medium();}
			me.breakpoint_2 = 0.0;

			} 


		settimer (func {me.run_ascent_medium();}, 5.0);

	},


	init_ascent_hard: func {


		if (getprop("/sim/config/shuttle/prelaunch-flag") == 0)
			{
			SpaceShuttle.callout.make("Ascent training scenario can only be selected before ignition!", "essential");
			return;
			}

		if (me.scenario_running == 1)
			{
			SpaceShuttle.callout.make("Another training scenario is already running", "essential");
			return;
			}

		srand();

		me.breakpoint_1 = 10.0 + rand() * 150.0;
		me.breakpoint_2 = me.breakpoint_1 + rand() * 150.0;
		me.breakpoint_3 = me.breakpoint_2 + rand() * 200.0;
		me.endpoint = me.breakpoint_3 + 10.0;

		if (me.verbose == 1)
			{
			print("Init hard ascent failure training");
			print("Failure time 1 is ", me.breakpoint_1);
			print("Failure time 2 is ", me.breakpoint_2);
			print("Failure time 2 is ", me.breakpoint_3);
			}

		me.scenario_running = 1;
		me.run_ascent_hard();

	},


	run_ascent_hard: func {

		var met = SpaceShuttle.get_MET();
	
		if (met > me.endpoint) 
			{
			if (me.verbose == 1) {print ("Training manager signing off...");}
			return;
			}

		if ((met > me.breakpoint_1) and (me.breakpoint_1 > 0.0)) 
			{
			if (rand() < 0.6)
				{me.failure_ascent_severe();}
			else
				{me.failure_ascent_medium();}
			me.breakpoint_1 = 0.0;

			} 

		if ((met > me.breakpoint_2) and (me.breakpoint_2 > 0.0)) 
			{
			if (rand() < 0.5)
				{me.failure_ascent_subtle();}
			else
				{me.failure_ascent_medium();}
			me.breakpoint_2 = 0.0;

			} 

		if ((met > me.breakpoint_3) and (me.breakpoint_3 > 0.0)) 
			{
			if (rand() < 0.5)
				{me.failure_ascent_minor();}
			else
				{me.failure_ascent_medium();}
			me.breakpoint_2 = 0.0;

			}


		settimer (func {me.run_ascent_hard();}, 5.0);

	},



	failure_ascent_minor: func {

		if (me.verbose == 1)
			{
			print("Creating minor category failure...");
			}

		var rn = rand();

		if (rn < 0.1)
			{
			setprop("/fdm/jsbsim/systems/mps/engine/electric-lockup", 1);
			}
		else if (rn < 0.1)
			{
			setprop("/fdm/jsbsim/systems/mps/engine[1]/electric-lockup", 1);
			}
		else if (rn < 0.2)
			{
			setprop("/fdm/jsbsim/systems/mps/engine[2]/electric-lockup", 1);
			}
		else if (rn < 0.3)
			{
			setprop("/fdm/jsbsim/systems/mps/engine[1]/electric-lockup", 1);
			}
		else if (rn < 0.4)
			{
			setprop("/fdm/jsbsim/systems/failures/apu1-condition", 0);
			}
		else if (rn < 0.5)
			{
			setprop("/fdm/jsbsim/systems/failures/apu2-condition", 0);
			}
		else if (rn < 0.6)
			{
			setprop("/fdm/jsbsim/systems/failures/apu3-condition", 0);
			}
		else
			{
			var rn2 = rand();
	
			if (rn2 < 0.25)
				{
				SpaceShuttle.gpc_array[0].rs_sync_failure = 1;
				}
			else if (rn2 < 0.5)
				{
				SpaceShuttle.gpc_array[1].rs_sync_failure = 1;
				}
			else if (rn2 < 0.75)
				{
				SpaceShuttle.gpc_array[2].rs_sync_failure = 1;
				}
			else
				{
				SpaceShuttle.gpc_array[3].rs_sync_failure = 1;
				}

			}




	},

	failure_ascent_medium: func {


		if (me.verbose == 1)
			{
			print("Creating medium category failure...");
			}

		var rn = rand();

		if (rn < 0.1)
			{
			setprop("/fdm/jsbsim/systems/failures/ssme1-condition", 0);
			}
		else if (rn < 0.2)
			{
			setprop("/fdm/jsbsim/systems/failures/ssme2-condition", 0);
			}
		else if (rn < 0.3)
			{
			setprop("/fdm/jsbsim/systems/failures/ssme3-condition", 0);
			}
		else if (rn < 0.4)
			{
			setprop("/fdm/jsbsim/systems/mps/engine[0]/redline", 1);
			}
		else if (rn < 0.5)
			{
			setprop("/fdm/jsbsim/systems/mps/engine[1]/redline", 1);
			}
		else if (rn < 0.6)
			{
			setprop("/fdm/jsbsim/systems/mps/engine[2]/redline", 1);
			}
		else if (rn < 0.7)
			{
			var leak_flow = -0.003 * rand() -0.0005;
			var rn2 = rand();
			if (rn2 < 0.25)
				{SpaceShuttle.helium_leakage_manager.add_leak("left-helium-manifold-A", leak_flow);}
			else if (rn2 < 0.5)
				{SpaceShuttle.helium_leakage_manager.add_leak("left-helium-manifold-B", leak_flow);}
			else if (rn2 < 0.75)
				{SpaceShuttle.helium_leakage_manager.add_leak("left-helium-manifold", leak_flow);}
			else
				{SpaceShuttle.helium_leakage_manager.add_leak("left-helium-tank", leak_flow);}

			}
		else if (rn < 0.8)
			{
			var leak_flow = -0.003 * rand() -0.0005;
			var rn2 = rand();
			if (rn2 < 0.25)
				{SpaceShuttle.helium_leakage_manager.add_leak("right-helium-manifold-A", leak_flow);}
			else if (rn2 < 0.5)
				{SpaceShuttle.helium_leakage_manager.add_leak("right-helium-manifold-B", leak_flow);}
			else if (rn2 < 0.75)
				{SpaceShuttle.helium_leakage_manager.add_leak("right-helium-manifold", leak_flow);}
			else
				{SpaceShuttle.helium_leakage_manager.add_leak("right-helium-tank", leak_flow);}

			}
		else if (rn < 0.9)
			{
			var leak_flow = -0.003 * rand() -0.0005;
			var rn2 = rand();
			if (rn2 < 0.25)
				{SpaceShuttle.helium_leakage_manager.add_leak("center-helium-manifold-A", leak_flow);}
			else if (rn2 < 0.5)
				{SpaceShuttle.helium_leakage_manager.add_leak("center-helium-manifold-B", leak_flow);}
			else if (rn2 < 0.75)
				{SpaceShuttle.helium_leakage_manager.add_leak("center-helium-manifold", leak_flow);}
			else
				{SpaceShuttle.helium_leakage_manager.add_leak("center-helium-tank", leak_flow);}

			}
		else
			{
			SpaceShuttle.init_pass_failure();
			}

	},


	failure_ascent_severe : func {

		if (me.verbose == 1)
			{
			print("Creating severe category failure...");
			}

		var rn = rand();

		if (rn < 0.2) # simultaneous twin engine redline
			{
			var rn2 = rand();

			if (rn2 < 0.3)		
				{
				setprop("/fdm/jsbsim/systems/mps/engine[0]/redline", 1);

				settimer( func {
					setprop("/fdm/jsbsim/systems/mps/engine[1]/redline", 1);
						}, 1.0);
				}
			else if (rn2 < 0.6)
				{
				setprop("/fdm/jsbsim/systems/mps/engine[1]/redline", 1);

				settimer( func {
					setprop("/fdm/jsbsim/systems/mps/engine[2]/redline", 1);
						}, 1.0);

				}
			else 
				{
				setprop("/fdm/jsbsim/systems/mps/engine[2]/redline", 1);

				settimer( func {
					setprop("/fdm/jsbsim/systems/mps/engine[0]/redline", 1);
						}, 1.0);

				}

			}
		else if (rn < 0.4) # twin hydraulic failure
			{
			var rn2 = rand();			

			if (rn2 < 0.3)		
				{
				setprop("/fdm/jsbsim/systems/failures/apu1-condition", 0);

				settimer( func {
					setprop("/fdm/jsbsim/systems/failures/apu2-condition", 0);
						}, 1.0);
				}
			else if (rn2 < 0.6)
				{
				setprop("/fdm/jsbsim/systems/failures/apu2-condition", 0);

				settimer( func {
					setprop("/fdm/jsbsim/systems/failures/apu3-condition", 0);
						}, 1.0);

				}
			else 
				{
				setprop("/fdm/jsbsim/systems/failures/apu3-condition", 0);

				settimer( func {
					setprop("/fdm/jsbsim/systems/failures/apu1-condition", 0);
						}, 1.0);

				}


			}
		else if (rn < 0.6) # massive helium issues
			{
			var rn2 = rand();
			var rn3 = rand();

			var leak_flow = -0.005 * rand() -0.001;

			if (rn2 < 0.3)
				{
				if (rn3 < 0.25)
					{SpaceShuttle.helium_leakage_manager.add_leak("left-helium-manifold-A", leak_flow);}
				else if (rn3 < 0.5)
					{SpaceShuttle.helium_leakage_manager.add_leak("left-helium-manifold-B", leak_flow);}
				else if (rn3 < 0.75)
					{SpaceShuttle.helium_leakage_manager.add_leak("left-helium-manifold", leak_flow);}
				else
					{SpaceShuttle.helium_leakage_manager.add_leak("left-helium-tank", leak_flow);}
				}
			else if (rn2 < 0.6)
				{
				if (rn3 < 0.25)
					{SpaceShuttle.helium_leakage_manager.add_leak("right-helium-manifold-A", leak_flow);}
				else if (rn3 < 0.5)
					{SpaceShuttle.helium_leakage_manager.add_leak("right-helium-manifold-B", leak_flow);}
				else if (rn3 < 0.75)
					{SpaceShuttle.helium_leakage_manager.add_leak("right-helium-manifold", leak_flow);}
				else
					{SpaceShuttle.helium_leakage_manager.add_leak("right-helium-tank", leak_flow);}

				}
			else 
				{
				if (rn3 < 0.25)
					{SpaceShuttle.helium_leakage_manager.add_leak("center-helium-manifold-A", leak_flow);}
				else if (rn3 < 0.5)
					{SpaceShuttle.helium_leakage_manager.add_leak("center-helium-manifold-B", leak_flow);}
				else if (rn3 < 0.75)
					{SpaceShuttle.helium_leakage_manager.add_leak("center-helium-manifold", leak_flow);}
				else
					{SpaceShuttle.helium_leakage_manager.add_leak("center-helium-tank", leak_flow);}

				}

			leak_flow =  -0.001 * rand() -0.0002;
			rn2 = rand();
			rn3 = rand();

			if (rn2 < 0.3)
				{
				if (rn3 < 0.25)
					{SpaceShuttle.helium_leakage_manager.add_leak("left-helium-manifold-A", leak_flow);}
				else if (rn3 < 0.5)
					{SpaceShuttle.helium_leakage_manager.add_leak("left-helium-manifold-B", leak_flow);}
				else if (rn3 < 0.75)
					{SpaceShuttle.helium_leakage_manager.add_leak("left-helium-manifold", leak_flow);}
				else
					{SpaceShuttle.helium_leakage_manager.add_leak("left-helium-tank", leak_flow);}
				}
			else if (rn2 < 0.6)
				{
				if (rn3 < 0.25)
					{SpaceShuttle.helium_leakage_manager.add_leak("right-helium-manifold-A", leak_flow);}
				else if (rn3 < 0.5)
					{SpaceShuttle.helium_leakage_manager.add_leak("right-helium-manifold-B", leak_flow);}
				else if (rn3 < 0.75)
					{SpaceShuttle.helium_leakage_manager.add_leak("right-helium-manifold", leak_flow);}
				else
					{SpaceShuttle.helium_leakage_manager.add_leak("right-helium-tank", leak_flow);}

				}
			else 
				{
				if (rn3 < 0.25)
					{SpaceShuttle.helium_leakage_manager.add_leak("center-helium-manifold-A", leak_flow);}
				else if (rn3 < 0.5)
					{SpaceShuttle.helium_leakage_manager.add_leak("center-helium-manifold-B", leak_flow);}
				else if (rn3 < 0.75)
					{SpaceShuttle.helium_leakage_manager.add_leak("center-helium-manifold", leak_flow);}
				else
					{SpaceShuttle.helium_leakage_manager.add_leak("center-helium-tank", leak_flow);}

				}


			}
		else if (rn < 0.6) # electric bus and BFS engage
			{

			var rn2 = rand();

			if (rn2 < 0.33)
				{
				setprop("/fdm/jsbsim/systems/failures/electrical/main-A-condition", 0);
				}
			else if (rn2 < 0.66)
				{
				setprop("/fdm/jsbsim/systems/failures/electrical/main-B-condition", 0);
				}
			else
				{
				setprop("/fdm/jsbsim/systems/failures/electrical/main-C-condition", 0);
				}
			SpaceShuttle.init_pass_failure();

			}

		else if (rn < 0.8) # fire
			{
			var rn2 = rand();

			if (rn2 < 0.33)
				{
				SpaceShuttle.fire_sim.start_fire("avbay1");
				}
			else if (rn < 0.66)
				{
				SpaceShuttle.fire_sim.start_fire("avbay2");
				}
			else
				{
				SpaceShuttle.fire_sim.start_fire("avbay2");
				}


			}
		else	# data path failure hides engine failure
			{

			var rn2 = rand();
			var rn3 = rand();

			if (rn2 < 0.33)
				{
				SpaceShuttle.ssme_array[0].data_path = 0;
		
				if (rn3 < 0.2)
					{
					settimer ( func {SpaceShuttle.ssme_array[0].command_path = 0;}, 1.0);
					}
				else if (rn3 < 0.8)
					{
					settimer ( func {setprop("/fdm/jsbsim/systems/failures/ssme1-condition", 0);}, 1.0);
					}
				}
			else if (rn2 < 0.66)
				{
				SpaceShuttle.ssme_array[1].data_path = 0;
		
				if (rn3 < 0.2)
					{
					settimer ( func {SpaceShuttle.ssme_array[1].command_path = 0;}, 1.0);
					}
				else if (rn3 < 0.8)
					{
					settimer ( func {setprop("/fdm/jsbsim/systems/failures/ssme2-condition", 0);}, 1.0);
					}
				}
			else 
				{
				SpaceShuttle.ssme_array[2].data_path = 0;
		
				if (rn3 < 0.2)
					{
					settimer ( func {SpaceShuttle.ssme_array[2].command_path = 0;}, 1.0);
					}
				else if (rn3 < 0.8)
					{
					settimer ( func {setprop("/fdm/jsbsim/systems/failures/ssme3-condition", 0);}, 1.0);
					}
				}

			}

	},


	failure_ascent_subtle : func {

		if (me.verbose == 1)
			{
			print("Creating subtle category failure...");
			}

		var rn = rand();

		if (rn < 0.25) # cutoff pushbuttons
			{
			var rn2 = rand();

			if (rn2 < 0.33)
				{SpaceShuttle.failure_cmd.ssme_pb1a = 0;}
			else if (rn2 < 0.66)
				{SpaceShuttle.failure_cmd.ssme_pb2a = 0;}
			else
				{SpaceShuttle.failure_cmd.ssme_pb3a = 0;}
			}
		else if (rn < 0.5) # data path failures
			{
			var rn2 = rand();

			if (rn2 < 0.33)
				{
				SpaceShuttle.ssme_array[0].data_path = 0;
		
				if (rand() < 0.5)
					{
					settimer ( func {SpaceShuttle.ssme_array[0].command_path = 0;}, 1.0);
					}
				}
			else if (rn2 < 0.66)
				{
				SpaceShuttle.ssme_array[1].data_path = 0;
		
				if (rand() < 0.5)
					{
					settimer ( func {SpaceShuttle.ssme_array[1].command_path = 0;}, 1.0);
					}
				}
			else 
				{
				SpaceShuttle.ssme_array[2].data_path = 0;
		
				if (rand() < 0.5)
					{
					settimer ( func {SpaceShuttle.ssme_array[2].command_path = 0;}, 1.0);
					}
				}

			}

		else if (rn < 0.5) # command path failures
			{
			var rn2 = rand();

			if (rn2 < 0.33)
				{
				SpaceShuttle.ssme_array[0].command_path = 0;
				}
			else if (rn2 < 0.66)
				{
				SpaceShuttle.ssme_array[1].command_path = 0;
				}
			else
				{
				SpaceShuttle.ssme_array[2].command_path = 0;
				}
			}

		else
			{			
			var rn2 = rand();
	
			if (rn2 < 0.25)
				{
				SpaceShuttle.gpc_array[0].rs_sync_failure = 1;
				}
			else if (rn2 < 0.5)
				{
				SpaceShuttle.gpc_array[1].rs_sync_failure = 1;
				}
			else if (rn2 < 0.75)
				{
				SpaceShuttle.gpc_array[2].rs_sync_failure = 1;
				}
			else
				{
				SpaceShuttle.gpc_array[3].rs_sync_failure = 1;
				}


			}
		
			
		


	},



};
