var cdlg_notepad = {

	update_flag:  0,
	
	lines: [],
	line_content: ["","","","","","","","","","","","","","","",""],
	

	init: func {




		var width = 800;
		var height = 1000;
		var img_path = "Aircraft/CatskillsFusionSSTO/Dialogs/Notepad/notepad.png";

		if (me.update_flag == 1) {return;}	



		var window = canvas.Window.new([width,height],"dialog").set("title", "Notepad");

		window.del = func()
		{
		  SpaceShuttle.cdlg_notepad.update_flag = 0;
		  call(canvas.Window.del, [], me);
		};

		var notepadCanvas = window.createCanvas().set("background", canvas.style.getColor("bg_color"));
		me.root = notepadCanvas.createGroup();
		var child=me.root.createChild("image")
				                   .setFile(img_path )
				                   .setTranslation(0,0)
				                   .setSize(width,height);

		
		var line1 = me.root.createChild("text")
      	.setText(me.line_content[0])
		.setColor(0,0,0)
		.setFontSize(15)
		.setFont("LiberationFonts/LiberationSans-Bold.ttf")
		.setAlignment("left-bottom")
		.setRotation(0.0)
		.setTranslation(30, 80.0);

		append(me.lines, line1);

		var line2 = me.root.createChild("text")
      		.setText(me.line_content[1])
		.setColor(0,0,0)
		.setFontSize(15)
		.setFont("LiberationFonts/LiberationSans-Bold.ttf")
		.setAlignment("left-bottom")
		.setRotation(0.0)
		.setTranslation(30, 110.0);

		append(me.lines, line2);

		var line3 = me.root.createChild("text")
      	.setText(me.line_content[2])
		.setColor(0,0,0)
		.setFontSize(15)
		.setFont("LiberationFonts/LiberationSans-Bold.ttf")
		.setAlignment("left-bottom")
		.setRotation(0.0)
		.setTranslation(30, 140.0);

		append(me.lines, line3);

		var line4 = me.root.createChild("text")
      		.setText(me.line_content[3])
		.setColor(0,0,0)
		.setFontSize(15)
		.setFont("LiberationFonts/LiberationSans-Bold.ttf")
		.setAlignment("left-bottom")
		.setRotation(0.0)
		.setTranslation(30, 170.0);

		append(me.lines, line4);
		
		var line5 = me.root.createChild("text")
      	.setText(me.line_content[4])
		.setColor(0,0,0)
		.setFontSize(15)
		.setFont("LiberationFonts/LiberationSans-Bold.ttf")
		.setAlignment("left-bottom")
		.setRotation(0.0)
		.setTranslation(30, 200.0);

		append(me.lines, line5);
		
		var line6 = me.root.createChild("text")
      	.setText(me.line_content[5])
		.setColor(0,0,0)
		.setFontSize(15)
		.setFont("LiberationFonts/LiberationSans-Bold.ttf")
		.setAlignment("left-bottom")
		.setRotation(0.0)
		.setTranslation(30, 230.0);

		append(me.lines, line6);
		
		var line7 = me.root.createChild("text")
      	.setText(me.line_content[6])
		.setColor(0,0,0)
		.setFontSize(15)
		.setFont("LiberationFonts/LiberationSans-Bold.ttf")
		.setAlignment("left-bottom")
		.setRotation(0.0)
		.setTranslation(30, 260.0);

		append(me.lines, line7);		

		var line8 = me.root.createChild("text")
      	.setText(me.line_content[7])
		.setColor(0,0,0)
		.setFontSize(15)
		.setFont("LiberationFonts/LiberationSans-Bold.ttf")
		.setAlignment("left-bottom")
		.setRotation(0.0)
		.setTranslation(30, 290.0);

		append(me.lines, line8);
		
		var line9 = me.root.createChild("text")
      	.setText(me.line_content[8])
		.setColor(0,0,0)
		.setFontSize(15)
		.setFont("LiberationFonts/LiberationSans-Bold.ttf")
		.setAlignment("left-bottom")
		.setRotation(0.0)
		.setTranslation(30, 320.0);

		append(me.lines, line9);		

		var line10 = me.root.createChild("text")
      	.setText(me.line_content[9])
		.setColor(0,0,0)
		.setFontSize(15)
		.setFont("LiberationFonts/LiberationSans-Bold.ttf")
		.setAlignment("left-bottom")
		.setRotation(0.0)
		.setTranslation(30, 350.0);

		append(me.lines, line10);		

		var line11 = me.root.createChild("text")
      	.setText(me.line_content[10])
		.setColor(0,0,0)
		.setFontSize(15)
		.setFont("LiberationFonts/LiberationSans-Bold.ttf")
		.setAlignment("left-bottom")
		.setRotation(0.0)
		.setTranslation(30, 380.0);

		append(me.lines, line11);	
		
		var line12 = me.root.createChild("text")
      	.setText(me.line_content[11])
		.setColor(0,0,0)
		.setFontSize(15)
		.setFont("LiberationFonts/LiberationSans-Bold.ttf")
		.setAlignment("left-bottom")
		.setRotation(0.0)
		.setTranslation(30, 410.0);

		append(me.lines, line12);	

		var line13 = me.root.createChild("text")
      	.setText(me.line_content[12])
		.setColor(0,0,0)
		.setFontSize(15)
		.setFont("LiberationFonts/LiberationSans-Bold.ttf")
		.setAlignment("left-bottom")
		.setRotation(0.0)
		.setTranslation(30, 440.0);

		append(me.lines, line13);

		var line14 = me.root.createChild("text")
      	.setText(me.line_content[13])
		.setColor(0,0,0)
		.setFontSize(15)
		.setFont("LiberationFonts/LiberationSans-Bold.ttf")
		.setAlignment("left-bottom")
		.setRotation(0.0)
		.setTranslation(30, 470.0);

		append(me.lines, line14);			

		var line15 = me.root.createChild("text")
      	.setText(me.line_content[14])
		.setColor(0,0,0)
		.setFontSize(15)
		.setFont("LiberationFonts/LiberationSans-Bold.ttf")
		.setAlignment("left-bottom")
		.setRotation(0.0)
		.setTranslation(30, 500.0);

		append(me.lines, line15);			

		var line16 = me.root.createChild("text")
      	.setText(me.line_content[15])
		.setColor(0,0,0)
		.setFontSize(15)
		.setFont("LiberationFonts/LiberationSans-Bold.ttf")
		.setAlignment("left-bottom")
		.setRotation(0.0)
		.setTranslation(30, 530.0);

		append(me.lines, line16);			
		
		me.update_flag = 1;

		},

	write_to_line: func (i, text) {

		me.line_content[i] = text;
		
		if (me.update_flag == 1)
			{me.lines[i].setText(text);}

		},
	
	# notes are inserted dynamically from line 10-16
	take_note: func (text) {
	
		for (var i=0; i< 6; i=i+1)
			{
			#print ("Copying to line", 9+i);
			#print (me.line_content[9+i]);
			me.line_content[9+i] = me.line_content[9+i+1];
			if (me.update_flag == 1)
				{
				me.lines[9+i].setText(me.line_content[9+i]);
				}
			}
		me.line_content[15] = text;
		
		if (me.update_flag == 1)
			{
			me.lines[15].setText(text);
			}
		},
		

};


