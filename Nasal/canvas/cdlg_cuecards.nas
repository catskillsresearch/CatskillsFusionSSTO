var cdlg_cuecards = {



	init: func {


		var width = 512;
		var height = 512;
		var img_path = "Aircraft/CatskillsFusionSSTO/Dialogs/Cuecards/cuecards.png";
						



		var window = canvas.Window.new([width,height],"dialog").set("title", "In-cockpit cue cards");

		

		var tempCanvas = window.createCanvas().set("background", canvas.style.getColor("bg_color"));
		me.root = tempCanvas.createGroup();
		var child=me.root.createChild("image")
				                   .setFile(img_path )
				                   .setTranslation(0,0)
				                   .setSize(width,height);


		me.index_cdr = SpaceShuttle.cue_card_binder_CDR.management_index;
		me.index_plt = SpaceShuttle.cue_card_binder_PLT.management_index;


		var string_cdr = "none";
		var string_plt = "none";

		if (me.index_cdr == 1)
			{
			string_cdr = "Systems procedures powered flight";
			}
		else if (me.index_cdr == 2)
			{
			string_cdr = "Systems procedures glided flight";
			}

		if (me.index_plt == 1)
			{
			string_plt = "Systems procedures powered flight";
			}
		else if (me.index_plt == 2)
			{
			string_plt = "Systems procedures glided flight";
			}

		var data = SpaceShuttle.draw_rect(100,40);

	 	me.cdr_bg = me.root.createChild("path", "CDR BG")
        	.setStrokeLineWidth(1.0)
        	.setColor(1.0, 1.0, 1.0, 1.0)
		.setColorFill(1.0, 1.0, 1.0)
		.moveTo(data[0][0], data[0][1]);

		me.symbol_draw (me.cdr_bg, data, 0);

		me.cdr_bg.setTranslation(70, 40);


		me.cdr_label = me.root.createChild("text")
			.setText("CDR binder")
			.setColor(0.0, 0.0, 0.0)
			.setFontSize(14)
			.setFont("LiberationFonts/LiberationMono-Regular.ttf")
			.setTranslation(70, 40)
			.setAlignment("center-center");


	 	me.plt_bg = me.root.createChild("path", "PLT BG")
        	.setStrokeLineWidth(1.0)
        	.setColor(1.0, 1.0, 1.0, 1.0)
		.setColorFill(1.0, 1.0, 1.0)
		.moveTo(data[0][0], data[0][1]);

		me.symbol_draw (me.plt_bg, data, 0);

		me.plt_bg.setTranslation(70, 140);


		me.plt_label = me.root.createChild("text")
			.setText("PLT binder")
			.setColor(0.0, 0.0, 0.0)
			.setFontSize(14)
			.setFont("LiberationFonts/LiberationMono-Regular.ttf")
			.setTranslation(70, 140)
			.setAlignment("center-center");

		data = SpaceShuttle.draw_rect(280,40);

		me.cdr_txt_bg = me.root.createChild("path", "CDR text BG")
        	.setStrokeLineWidth(1.0)
        	.setColor(1.0, 1.0, 1.0, 1.0)
		.setColorFill(1.0, 1.0, 1.0)
		.moveTo(data[0][0], data[0][1]);

		me.symbol_draw (me.cdr_txt_bg, data, 0);

		me.cdr_txt_bg.setTranslation(286, 40);


		me.cdr_text = me.root.createChild("text")
			.setText(string_cdr)
			.setColor(0.0, 0.0, 0.0)
			.setFontSize(14)
			.setFont("LiberationFonts/LiberationMono-Regular.ttf")
			.setTranslation(286, 40)
			.setAlignment("center-center");

		me.plt_txt_bg = me.root.createChild("path", "PLT text BG")
        	.setStrokeLineWidth(1.0)
        	.setColor(1.0, 1.0, 1.0, 1.0)
		.setColorFill(1.0, 1.0, 1.0)
		.moveTo(data[0][0], data[0][1]);

		me.symbol_draw (me.plt_txt_bg, data, 0);

		me.plt_txt_bg.setTranslation(286, 140);


		me.plt_text = me.root.createChild("text")
			.setText(string_plt)
			.setColor(0.0, 0.0, 0.0)
			.setFontSize(14)
			.setFont("LiberationFonts/LiberationMono-Regular.ttf")
			.setTranslation(286, 140)
			.setAlignment("center-center");





		# buttons


		var stack = [];
		append(stack, "Aircraft/CatskillsFusionSSTO/Dialogs/Cuecards/cuecards_next_0.png");
		me.button_cdr_next = cdlg_widget_img_stack.new(me.root, stack, 126, 42);
		me.button_cdr_next.setTranslation(350,70);

		me.button_cdr_next.f = func {

			SpaceShuttle.cdlg_cuecards.index_cdr += 1;
			if (SpaceShuttle.cdlg_cuecards.index_cdr > 2) {SpaceShuttle.cdlg_cuecards.index_cdr = 0;}

			if (SpaceShuttle.cdlg_cuecards.index_cdr == 0)
				{
				SpaceShuttle.cdlg_cuecards.cdr_text.setText("none");
				setprop("/sim/config/shuttle/cuecards/cdr-center-left",0);
				setprop("/sim/config/shuttle/cuecards/cdr-center-right",0);
 				SpaceShuttle.cue_card_binder_CDR.management_index = 0;
				}
			else if (SpaceShuttle.cdlg_cuecards.index_cdr == 1)
				{
				SpaceShuttle.cdlg_cuecards.cdr_text.setText("Systems procedures powered flight");
				setprop("/sim/config/shuttle/cuecards/cdr-center-left",1);
				setprop("/sim/config/shuttle/cuecards/cdr-center-right",1);
 				SpaceShuttle.cue_card_binder_CDR.management_index = 1;
				SpaceShuttle.cue_card_binder_CDR.change_set(0);
				}
			else if (SpaceShuttle.cdlg_cuecards.index_cdr == 2)
				{
				SpaceShuttle.cdlg_cuecards.cdr_text.setText("Systems procedures glided flight");
				setprop("/sim/config/shuttle/cuecards/cdr-center-left",1);
				setprop("/sim/config/shuttle/cuecards/cdr-center-right",1);
 				SpaceShuttle.cue_card_binder_CDR.management_index = 2;
				SpaceShuttle.cue_card_binder_CDR.change_set(1);
				}
			
			};


		me.button_plt_next = cdlg_widget_img_stack.new(me.root, stack, 126, 42);
		me.button_plt_next.setTranslation(350,170);

		me.button_plt_next.f = func {

			SpaceShuttle.cdlg_cuecards.index_plt += 1;
			if (SpaceShuttle.cdlg_cuecards.index_plt > 2) {SpaceShuttle.cdlg_cuecards.index_plt = 0;}

			if (SpaceShuttle.cdlg_cuecards.index_plt == 0)
				{
				SpaceShuttle.cdlg_cuecards.plt_text.setText("none");
				setprop("/sim/config/shuttle/cuecards/plt-center-left",0);
				setprop("/sim/config/shuttle/cuecards/plt-center-right",0);
 				SpaceShuttle.cue_card_binder_PLT.management_index = 0;
				}
			else if (SpaceShuttle.cdlg_cuecards.index_plt == 1)
				{
				SpaceShuttle.cdlg_cuecards.plt_text.setText("Systems procedures powered flight");
				setprop("/sim/config/shuttle/cuecards/plt-center-left",1);
				setprop("/sim/config/shuttle/cuecards/plt-center-right",1);
 				SpaceShuttle.cue_card_binder_PLT.management_index = 1;
				SpaceShuttle.cue_card_binder_PLT.change_set(0);
				}
			else if (SpaceShuttle.cdlg_cuecards.index_plt == 2)
				{
				SpaceShuttle.cdlg_cuecards.plt_text.setText("Systems procedures glided flight");
				setprop("/sim/config/shuttle/cuecards/plt-center-left",1);
				setprop("/sim/config/shuttle/cuecards/plt-center-right",1);
 				SpaceShuttle.cue_card_binder_PLT.management_index = 2;
				SpaceShuttle.cue_card_binder_PLT.change_set(1);
				}

			
			};


		
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
