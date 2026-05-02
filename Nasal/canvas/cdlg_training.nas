var cdlg_training = {

	current_index: 0,
	custom_flag: 0,

	init: func {


		var width = 512;
		var height = 384;
		var img_path = "Aircraft/SpaceShuttle/Pics/orbit-splash03.png";
						


		me.window = canvas.Window.new([width,height],"dialog").set("title", "Training Scenario");

		

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
		append(stack, "Aircraft/SpaceShuttle/Dialogs/Scenario/scenario_next_0.png");
		me.button_next = cdlg_widget_img_stack.new(me.root, stack, 126, 42);
		me.button_next.setTranslation(20,320);

		me.button_next.f = func {

			SpaceShuttle.cdlg_training.select_next_scenario();
			
			};

		stack = [];
		append(stack, "Aircraft/SpaceShuttle/Dialogs/Scenario/scenario_select_0.png");
		me.button_select = cdlg_widget_img_stack.new(me.root, stack, 126, 42);
		me.button_select.setTranslation(370 ,320);

		me.button_select.f = func {

			var stage = getprop("/sim/presets/stage");

			if ((stage == 0) and (SpaceShuttle.cdlg_training.current_index == 1))
				{
				SpaceShuttle.training_manager.init_ascent_easy();
				}
			else if ((stage == 0) and (SpaceShuttle.cdlg_training.current_index == 2))
				{
				SpaceShuttle.training_manager.init_ascent_medium();
				}
			if ((stage == 0) and (SpaceShuttle.cdlg_training.current_index == 3))
				{
				SpaceShuttle.training_manager.init_ascent_hard();
				}
			

			SpaceShuttle.cdlg_training.window.del();
		
			};


		},

	select_next_scenario: func {

		var stage = getprop("/sim/presets/stage");

		if (stage == 6) # mission
			{


			
			}
		else if (stage == 2)
			{
			

			}
		else if (stage == 0)
			{
			if (me.current_index == 0)
				{
				me.current_index = 1;
				me.an_scenario_name.setText("Ascent failures difficulty level: easy");
				me.picture.setFile("Aircraft/SpaceShuttle/Dialogs/Training/ascent_easy.png");
				}
			else if (me.current_index == 1)
				{
				me.current_index = 2;
				me.an_scenario_name.setText("Ascent failures difficulty level: medium");
				me.picture.setFile("Aircraft/SpaceShuttle/Dialogs/Training/ascent_medium.png");
				}
			else if (me.current_index == 2)
				{
				me.current_index = 3;
				me.an_scenario_name.setText("Ascent failures difficulty level: hard");
				me.picture.setFile("Aircraft/SpaceShuttle/Dialogs/Training/ascent_hard.png");
				}
			else
				{
				me.current_index = 0;
				me.an_scenario_name.setText("No scenario selected");
				me.picture.setFile("Aircraft/SpaceShuttle/Pics/orbit-splash03.png");
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
