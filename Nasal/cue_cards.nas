
# display of cue cards in a canvas window

var show_cue_card = func (path) {

var size = [0,0];
var title = "Cue card";

if (path == "Cuecards/ascent_nominal.png")
	{
	size = [217, 549];
	title = "Ascent ADI - Nominal";
	}

else if (path == "Cuecards/contingency_abort.png")
	{
	size = [659, 650];
	title = "Contingency Aborts";
	}
else if (path == "Cuecards/rtls_contingency.png")
	{
	size = [692, 666];
	title = "RTLS Contingency";
	}
else if (path == "Cuecards/rtls_cdr.png")
	{
	size = [450, 673];
	title = "RTLS Commander";
	}
else if (path == "Cuecards/rtls_plt.png")
	{
	size = [470, 727];
	title = "RTLS Pilot";
	}
else if (path == "Cuecards/tal_redesignation_zza.png")
	{
	size = [632, 500];
	title = "ZZA TAL Redesignation";
	}
else if (path == "Cuecards/oms_part1.png")
	{
	size = [455, 513];
	title = "OMS Burn Part 1";
	}
else if (path == "Cuecards/oms_part2.png")
	{
	size = [423, 377];
	title = "OMS Burn Part 2";
	}
else if (path == "Cuecards/entry_nominal.png")
	{
	size = [214, 550];
	title = "Entry Alpha";
	}

var window = canvas.Window.new(size,"dialog").set("title", title);
var cueCanvas = window.createCanvas().set("background", canvas.style.getColor("bg_color"));
var root = cueCanvas.createGroup();

var child=root.createChild("image")
                                   .setFile( path )
                                   .setTranslation(0,0)
                                   .setSize(size);
}



var cue_card_binder_manager = {


	new: func (node_left, node_right) {
	 	var c = { parents: [cue_card_binder_manager] };
		c.base_file_string = "powered_flight";
		c.num_pages = 26;
		c.current_page = 1;	
		c.management_index = 0;

		c.node_left = node_left;
		c.node_right = node_right;	

		return c;
		},

	init: func {

		me.canvas_left = canvas.new({
                "name": "page-left",
                    "size": [1024,1024], 
                    "view": [1024,1024],                        
                    "mipmapping": 0     
                    });

		me.canvas_right = canvas.new({
                "name": "page-right",
                    "size": [1024,1024], 
                    "view": [1024,1024],                        
                    "mipmapping": 0     
                    });


		me.canvas_left.addPlacement({"node": me.node_left});
		me.canvas_right.addPlacement({"node": me.node_right});

		me.root_left = me.canvas_left.createGroup();
		me.root_right = me.canvas_right.createGroup();

		me.img_left = me.root_left.createChild("image")
				.setFile("Aircraft/CatskillsFusionSSTO/Cuecards/"~me.base_file_string~"-L-01.jpg")
				.setTranslation(200,0)
				.setSize(620, 1024);

		me.img_right = me.root_right.createChild("image")
				.setFile("Aircraft/CatskillsFusionSSTO/Cuecards/"~me.base_file_string~"-R-01.jpg")
				.setTranslation(200,0)
				.setSize(620, 1024);



	},


	change_set: func (set_index) {


		if (set_index == 0)
			{
			me.base_file_string = "powered_flight";
			me.num_pages = 26;
			}
		else if (set_index == 1)
			{
			me.base_file_string = "glided_flight";
			me.num_pages = 34;
			}

		me.img_left.setFile("Aircraft/CatskillsFusionSSTO/Cuecards/"~me.base_file_string~"-L-01.jpg");
		me.img_right.setFile("Aircraft/CatskillsFusionSSTO/Cuecards/"~me.base_file_string~"-R-01.jpg");
		me.current_page = 1;

	},


	next_page: func (increment) {


		me.current_page += increment;

		if (me.current_page == 0) {me.current_page = me.num_pages;}
		else if (me.current_page > me.num_pages) {me.current_page = 1;}
			
		var string = me.base_file_string;
		var numstring = "";
		if (me.current_page < 10) {numstring = "0";}
		numstring = numstring~me.current_page;


		me.img_left.setFile("Aircraft/CatskillsFusionSSTO/Cuecards/"~string~"-L-"~numstring~".jpg");
		me.img_right.setFile("Aircraft/CatskillsFusionSSTO/Cuecards/"~string~"-R-"~numstring~".jpg");


			


	},


	popup_left_page: func {

		var size = [495, 660];

		var window = canvas.Window.new(size,"dialog").set("title", "Cue card");
		var cueCanvas = window.createCanvas().set("background", canvas.style.getColor("bg_color"));
		var root = cueCanvas.createGroup();

		var string = me.base_file_string;
		var numstring = "";
		if (me.current_page < 10) {numstring = "0";}
		numstring = numstring~me.current_page;

		var child=root.createChild("image")
				                   .setFile("Aircraft/CatskillsFusionSSTO/Cuecards/"~string~"-L-"~numstring~".jpg")
				                   .setTranslation(0,0)
				                   .setSize(size);


	},

	popup_right_page: func {

		var size = [495, 660];

		var window = canvas.Window.new(size,"dialog").set("title", "Cue card");
		var cueCanvas = window.createCanvas().set("background", canvas.style.getColor("bg_color"));
		var root = cueCanvas.createGroup();

		var string = me.base_file_string;
		var numstring = "";
		if (me.current_page < 10) {numstring = "0";}
		numstring = numstring~me.current_page;

		var child=root.createChild("image")
				                   .setFile("Aircraft/CatskillsFusionSSTO/Cuecards/"~string~"-R-"~numstring~".jpg")
				                   .setTranslation(0,0)
				                   .setSize(size);


	},


};

var cue_card_binder_CDR = cue_card_binder_manager.new("Cuecard-CDR-center-left", "Cuecard-CDR-center-right");
cue_card_binder_CDR.init();

var cue_card_binder_PLT = cue_card_binder_manager.new("Cuecard-PLT-center-left", "Cuecard-PLT-center-right");
cue_card_binder_PLT.init();
