var cdlg_eileen = {



	init: func {


		var width = 512;
		var height = 512;
		var img_path = "Aircraft/SpaceShuttle/Dialogs/Eileen/eileen.png";
						



		var window = canvas.Window.new([width,height],"dialog").set("title", "Eileen");

		

		var tempCanvas = window.createCanvas().set("background", canvas.style.getColor("bg_color"));
		me.root = tempCanvas.createGroup();
		var child=me.root.createChild("image")
				                   .setFile(img_path )
				                   .setTranslation(0,0)
				                   .setSize(width,height);


		# buttons


		var stack = [];
		append(stack, "Aircraft/SpaceShuttle/Dialogs/Eileen/eileen_station_0.png");
		append(stack, "Aircraft/SpaceShuttle/Dialogs/Eileen/eileen_station_1.png");
		me.button_stationkeeping = cdlg_widget_img_stack.new(me.root, stack, 126, 42);
		me.button_stationkeeping.setTranslation(20,460);

		if (SpaceShuttle.eileen.stationkeeping_flag ==1)
			{
			me.button_stationkeeping.increment();
			}

		me.button_stationkeeping.f = func {
		
			if (me.index == 1)
				{
				SpaceShuttle.eileen.init_stationkeeping();
				SpaceShuttle.cdlg_eileen.button_reference.grey_out(1);
				}
			else
				{
				SpaceShuttle.eileen.end_stationkeeping();
				SpaceShuttle.cdlg_eileen.button_reference.grey_out(0);
				}
		};





		stack = [];
		append(stack, "Aircraft/SpaceShuttle/Dialogs/Eileen/eileen_reference_0.png");
		me.button_reference = cdlg_widget_img_stack.new(me.root, stack, 126, 42);
		me.button_reference.setTranslation(146,460);

		if (SpaceShuttle.eileen.stationkeeping_flag ==1)
			{
			me.button_reference.grey_out(1);
			}

		me.button_reference.f = func {
		
			if (SpaceShuttle.eileen.stationkeeping_flag == 0)
				{
				SpaceShuttle.proximity_manager.cycle_current_payload_reference();
				var obj_name = SpaceShuttle.proximity_manager.query_reference_name();
				SpaceShuttle.callout.make("Changing reference to "~obj_name~".", "essential"); 
				}
		};


		stack = [];
		append(stack, "Aircraft/SpaceShuttle/Dialogs/Eileen/eileen_precision_0.png");
		append(stack, "Aircraft/SpaceShuttle/Dialogs/Eileen/eileen_precision_1.png");
		append(stack, "Aircraft/SpaceShuttle/Dialogs/Eileen/eileen_precision_2.png");
		me.button_precision = cdlg_widget_img_stack.new(me.root, stack, 126, 42);
		me.button_precision.setTranslation(272,460);

		if (SpaceShuttle.eileen.precision_setting ==1)
			{
			me.button_precision.increment();
			}
		else if (SpaceShuttle.eileen.precision_setting == 2)
			{
			me.button_precision.increment();
			me.button_precision.increment();
			}

		me.button_precision.f = func {
		
			
			SpaceShuttle.eileen.cycle_precision_setting();
				
		};


		},
};
