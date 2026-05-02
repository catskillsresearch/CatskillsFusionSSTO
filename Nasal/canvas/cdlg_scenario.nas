var cdlg_scenario = {

	current_index: 0,
	custom_flag: 0,

	init: func {


		var width = 512;
		var height = 384;
		var img_path = "Aircraft/CatskillsFusionSSTO/Pics/orbit-splash03.png";
						
		me.parse_custom_scenario();


		me.window = canvas.Window.new([width,height],"dialog").set("title", "Scenario");

		

		var tempCanvas = me.window.createCanvas().set("background", canvas.style.getColor("bg_color"));
		me.root = tempCanvas.createGroup();
		me.picture = me.root.createChild("image")
				                   .setFile(img_path )
				                   .setTranslation(0,0)
				                   .setSize(width,height);

		var data = SpaceShuttle.draw_rect(350,50);

	 	me.an_bg = me.root.createChild("path", "Alphanumerics background")
        	.setStrokeLineWidth(1.0)
        	.setColor(1.0, 1.0, 1.0, 1.0)
		.setColorFill(1.0, 1.0, 1.0)
		.moveTo(data[0][0], data[0][1]);

		me.symbol_draw (me.an_bg, data, 0);

		me.an_bg.setTranslation(256, 40);


		me.an_scenario_name = me.root.createChild("text")
			.setText("No scenario selected")
			.setColor(0.0, 0.0, 0.0)
			.setFontSize(14)
			.setFont("LiberationFonts/LiberationMono-Regular.ttf")
			.setTranslation(256, 40)
			.setAlignment("center-center");


		# buttons


		var stack = [];
		append(stack, "Aircraft/CatskillsFusionSSTO/Dialogs/Scenario/scenario_next_0.png");
		me.button_next = cdlg_widget_img_stack.new(me.root, stack, 126, 42);
		me.button_next.setTranslation(20,320);

		me.button_next.f = func {

			SpaceShuttle.cdlg_scenario.select_next_scenario();
			
			};

		stack = [];
		append(stack, "Aircraft/CatskillsFusionSSTO/Dialogs/Scenario/scenario_select_0.png");
		me.button_select = cdlg_widget_img_stack.new(me.root, stack, 126, 42);
		me.button_select.setTranslation(370 ,320);

		me.button_select.f = func {

			SpaceShuttle.scenario_init();
			SpaceShuttle.cdlg_scenario.current_index = 0;
			SpaceShuttle.cdlg_scenario.window.del();
		
			};


		if (me.custom_flag == 1)
			{
			stack = [];
			append(stack, "Aircraft/CatskillsFusionSSTO/Dialogs/Scenario/scenario_predef_0.png");
			me.button_select = cdlg_widget_img_stack.new(me.root, stack, 126, 42);
			me.button_select.setTranslation(195 ,320);

			me.button_select.f = func {

	
				SpaceShuttle.cdlg_scenario.an_scenario_name.setText(getprop("/scenario/metadata/title"));
				SpaceShuttle.cdlg_scenario.picture.setFile(SpaceShuttle.cdlg_scenario.custom_img_path);
				setprop("/scenario/filename", getprop("/sim/presets/scenario-file"));
				};
			}


		},

	select_next_scenario: func {

		var stage = getprop("/sim/presets/stage");

		if (stage == 6) # mission
			{


			if (me.current_index == 0)
				{
				me.current_index = 1;
				me.an_scenario_name.setText("Satellite capture");
				me.picture.setFile("Aircraft/CatskillsFusionSSTO/Pics/mission-splash02.png");
				setprop("/scenario/filename", "satellite-retrieval.xml");
			
				}
			else if (me.current_index == 1)
				{
				me.current_index = 2;
				me.an_scenario_name.setText("ISS docking");
				me.picture.setFile("Aircraft/CatskillsFusionSSTO/Pics/iss-splash01.png");
				setprop("/scenario/filename", "iss-docking.xml");
			
				}
			else if (me.current_index == 2)
				{
				me.current_index = 3;
				me.an_scenario_name.setText("ISS terminal intercept T1 burn");
				me.picture.setFile("Aircraft/CatskillsFusionSSTO/Dialogs/Scenario/scenario_ISS_T1.png");
				setprop("/scenario/filename", "iss-TI-T1.xml");
			
				}
			else if (me.current_index == 3)
				{
				me.current_index = 4;
				me.an_scenario_name.setText("De-orbit burn");
				me.picture.setFile("Aircraft/CatskillsFusionSSTO/Dialogs/Scenario/scenario_de_orbit.png");
				setprop("/scenario/filename", "de-orbit.xml");
			
				}
			else
				{
				me.current_index = 0;
				me.an_scenario_name.setText("No scenario selected");
				me.picture.setFile("Aircraft/CatskillsFusionSSTO/Pics/orbit-splash03.png");
				}
			}
		else if (stage == 2)
			{
			if (me.current_index == 0)
				{
				me.current_index = 1;
				me.an_scenario_name.setText("4200 nm to KSC");
				me.picture.setFile("Aircraft/CatskillsFusionSSTO/Pics/entry-splash01.png");
				setprop("/scenario/filename", "ksc-4200.xml");
			
				}
			else if (me.current_index == 1)
				{
				me.current_index = 2;
				me.an_scenario_name.setText("Low energy entry to KSC");
				me.picture.setFile("Aircraft/CatskillsFusionSSTO/Dialogs/Scenario/scenario_low_energy_entry.png");
				setprop("/scenario/filename", "ksc-low-energy.xml");
			
				}
			else if (me.current_index == 2)
				{
				me.current_index = 3;
				me.an_scenario_name.setText("High energy entry to KSC");
				me.picture.setFile("Aircraft/CatskillsFusionSSTO/Dialogs/Scenario/scenario_high_energy_entry.png");
				setprop("/scenario/filename", "ksc-high-energy.xml");
			
				}
			else if (me.current_index == 3)
				{
				me.current_index = 4;
				me.an_scenario_name.setText("Lakebed landing");
				me.picture.setFile("Aircraft/CatskillsFusionSSTO/Dialogs/Scenario/scenario_lakebed.png");
				setprop("/scenario/filename", "lakebed-landing.xml");
			
				}


			else
				{
				me.current_index = 0;
				me.an_scenario_name.setText("No scenario selected");
				me.picture.setFile("Aircraft/CatskillsFusionSSTO/Pics/orbit-splash03.png");
				}
			}
		else if (stage == 0)
			{
			if (me.current_index == 0)
				{
				me.current_index = 1;
				me.an_scenario_name.setText("Single engine failure in RTLS region");
				me.picture.setFile("Aircraft/CatskillsFusionSSTO/Dialogs/Scenario/scenario_rtls.png");
				setprop("/scenario/filename", "launch-rtls.xml");
				}
			else if (me.current_index == 1)
				{
				me.current_index = 2;
				me.an_scenario_name.setText("Single engine failure in TAL region");
				me.picture.setFile("Aircraft/CatskillsFusionSSTO/Dialogs/Scenario/scenario_tal.png");
				setprop("/scenario/filename", "launch-tal.xml");
				}
			else if (me.current_index == 2)
				{
				me.current_index = 3;
				me.an_scenario_name.setText("Debris strike during SRB separation");
				me.picture.setFile("Aircraft/CatskillsFusionSSTO/Dialogs/Scenario/scenario_debris.png");
				setprop("/scenario/filename", "launch-debris.xml");
				}
			else
				{
				me.current_index = 0;
				me.an_scenario_name.setText("No scenario selected");
				me.picture.setFile("Aircraft/CatskillsFusionSSTO/Pics/orbit-splash03.png");
				}
			}


		},


	parse_custom_scenario: func {


		var filename = getprop("/sim/presets/scenario-file");

		if (filename == "empty.xml")
			{
			me.custom_flag = 0;
			return;
			}	
		else
			{
			var target = props.globals.getNode("/scenario");
			var success = io.read_properties("Aircraft/CatskillsFusionSSTO/Scenario/"~filename, target);

			if (success == nil) # try absolute path
				{

				success = io.read_properties(filename, target);

				if (success == nil) # give up
					{
					print("Cannot open scenario file ", filename, ", aborting.");
					me.custom_flag = 0;
					return;
					}
				}

			me.custom_flag = 1;
			me.custom_img_path = getprop("/scenario/metadata/splash");
			
			if (me.custom_img_path == nil)
			 	{
				me.custom_img_path = "Aircraft/CatskillsFusionSSTO/Pics/orbit-splash01.png";
				}


			}

		},



	symbol_draw: func (plot, data) # symbols are drawn as continuous shape
		{

		for (var i = 0; i< size(data) - 1; i=i+1)
			{
			var set = data[i+1]; 
			plot.lineTo(set[0], set[1]);
			}

		},


	};
