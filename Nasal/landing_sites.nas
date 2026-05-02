
# define all Shuttle landing sites in one central location
# Thorsten Renk 2018






var landing_site_data = {

	array: [],

	entry_by_name: func (name) {

		foreach (l; me.array)
			{
			if (l.name == name)
				{
				return l;
				}
			}
		print ("No matching landing site found - using KSC.");
		return me.array[0];

	},

	entry_by_index: func (index) {

		foreach (l; me.array)
			{
			if (l.index == index)
				{
				return l;
				}
			}
		print ("No matching landing site found - using KSC.");
		return me.array[0];
	},



};

var landing_site_entry = {
	new: func (coord, name,  shortname, rwy_pri, rwy_sec, function, index) {
	 	var l = { parents: [landing_site_entry] };
		l.coord = coord;
		l.name = name;
		l.shortname = shortname;
		l.rwy_pri = rwy_pri;
		l.rwy_sec = rwy_sec;
		l.rwy_pri_name = l.shortname~l.rwy_pri;
		l.rwy_sec_name = l.shortname~l.rwy_sec;
		l.tacan = "";
		l.function = function;
		l.index = index;
		l.text_vertical_offset = 0.0;
		l.TAEM_pri_lat = 0.0;
		l.TAEM_pri_lon = 0.0;
		l.TAEM_pri_heading = 0.0;
		l.TAEM_pri_elevation = 0.0;
		l.TAEM_pri_MLS_flag = 0;
		l.TAEM_pri_MLS_channel = 0.0;
		l.TAEM_sec_lat = 0.0;
		l.TAEM_sec_lon = 0.0;
		l.TAEM_sec_heading = 0.0;
		l.TAEM_sec_elevation = 0.0;
		l.TAEM_sec_MLS_flag = 0;
		l.TAEM_sec_MLS_channel = 0.0;
		l.TAEM_rwy_length = 0.0;
		return l;
		},



};

# Kennedy Space Center

var coord1 = geo.Coord.new();
coord1.set_latlon(28.615, -80.695, 0.0);
var ls_entry1 = landing_site_entry.new(coord1, "Kennedy Space Center", "KSC", "15", "33", "regular", 1);
ls_entry1.tacan = "059";
ls_entry1.TAEM_pri_lat = 28.6315;
ls_entry1.TAEM_pri_lon = -80.7052;
ls_entry1.TAEM_pri_heading = 150.0;
ls_entry1.TAEM_pri_elevation = 0.0;
ls_entry1.TAEM_pri_MLS_flag = 1;
ls_entry1.TAEM_pri_MLS_channel = 8;
ls_entry1.TAEM_sec_lat = 28.5985;
ls_entry1.TAEM_sec_lon = -80.6836;
ls_entry1.TAEM_sec_heading = 330.0;
ls_entry1.TAEM_sec_elevation = 0.0;
ls_entry1.TAEM_sec_MLS_flag = 1;
ls_entry1.TAEM_sec_MLS_channel = 6;
ls_entry1.TAEM_rwy_length = 4572.0;
append(landing_site_data.array, ls_entry1);

# Vandenberg Air Force Base

var coord2 = geo.Coord.new();
coord2.set_latlon(34.722, -120.567, 0.0);
var ls_entry2 = landing_site_entry.new(coord2, "Vandenberg Air Force Base", "VBG", "12", "30", "regular", 2);
ls_entry2.text_vertical_offset = 6.0;
ls_entry2.tacan = "059";
ls_entry2.TAEM_pri_lat = 34.7502;
ls_entry2.TAEM_pri_lon = -120.5991;
ls_entry2.TAEM_pri_heading = 136.5;
ls_entry2.TAEM_pri_elevation = 362.0;
ls_entry2.TAEM_pri_MLS_flag = 1;
ls_entry2.TAEM_pri_MLS_channel = 8;
ls_entry2.TAEM_sec_lat = 34.7242;
ls_entry2.TAEM_sec_lon = -120.5692;
ls_entry2.TAEM_sec_heading = 316.5;
ls_entry2.TAEM_sec_elevation = 362.0;
ls_entry2.TAEM_sec_MLS_flag = 1;
ls_entry2.TAEM_sec_MLS_channel = 6;
ls_entry2.TAEM_rwy_length = 4572.0;
append(landing_site_data.array, ls_entry2);


# Edwards Air Force Base

var coord3 = geo.Coord.new();
coord3.set_latlon(34.949259, -117.866050, 0.0);
var ls_entry3 = landing_site_entry.new(coord3, "Edwards Air Force Base", "EDW", "06", "24", "regular", 3);
ls_entry3.text_vertical_offset = -6.0;
ls_entry3.tacan = "111";
ls_entry3.TAEM_pri_lat = 34.9497;
ls_entry3.TAEM_pri_lon = -117.8608;
ls_entry3.TAEM_pri_heading = 64.5;
ls_entry3.TAEM_pri_elevation = 2280.0;
ls_entry3.TAEM_pri_MLS_flag = 1;
ls_entry3.TAEM_pri_MLS_channel = 6;
ls_entry3.TAEM_sec_lat = 34.961;
ls_entry3.TAEM_sec_lon = -117.8310;
ls_entry3.TAEM_sec_heading = 244.5;
ls_entry3.TAEM_sec_elevation = 2280.0;
ls_entry3.TAEM_sec_MLS_flag = 1;
ls_entry3.TAEM_sec_MLS_channel = 8;
ls_entry3.TAEM_rwy_length = 5572.0;
append(landing_site_data.array, ls_entry3);

# White Sands Space Harbor

var coord4 = geo.Coord.new();
coord4.set_latlon(32.936, -106.416, 0.0);
var ls_entry4 = landing_site_entry.new(coord4, "White Sands Space Harbor", "NOR", "14", "32", "regular", 4);
ls_entry4.tacan = "100";
ls_entry4.TAEM_pri_lat = 32.9754;
ls_entry4.TAEM_pri_lon = -106.3313;
ls_entry4.TAEM_pri_heading = 142.0;
ls_entry4.TAEM_pri_elevation = 4450.0;
ls_entry4.TAEM_pri_MLS_flag = 1;
ls_entry4.TAEM_pri_MLS_channel = 6;
ls_entry4.TAEM_sec_lat = 32.8815;
ls_entry4.TAEM_sec_lon = -106.2477;
ls_entry4.TAEM_sec_heading = 322.0;
ls_entry4.TAEM_sec_elevation = 4450.0;
ls_entry4.TAEM_sec_MLS_flag = 1;
ls_entry4.TAEM_sec_MLS_channel = 8;
ls_entry4.TAEM_rwy_length = 4572.0;
append(landing_site_data.array, ls_entry4);


# Zaragoza Airport

var coord5 = geo.Coord.new();
coord5.set_latlon(41.666, -1.042, 0.0);
var ls_entry5 = landing_site_entry.new(coord5, "Zaragoza Airport", "ZZA", "12", "30", "TAL", 5);
ls_entry5.tacan = "064"; 
ls_entry5.TAEM_pri_lat = 41.6783;
ls_entry5.TAEM_pri_lon = -1.0781;
ls_entry5.TAEM_pri_heading = 120.0;
ls_entry5.TAEM_pri_elevation = 834.0;
ls_entry5.TAEM_pri_MLS_flag = 0;
ls_entry5.TAEM_pri_MLS_channel = -1;
ls_entry5.TAEM_sec_lat = 41.6647;
ls_entry5.TAEM_sec_lon = -1.0466;
ls_entry5.TAEM_sec_heading = 300.0;
ls_entry5.TAEM_sec_elevation = 866.0;
ls_entry5.TAEM_sec_MLS_flag = 1;
ls_entry5.TAEM_sec_MLS_channel = 6;
ls_entry5.TAEM_rwy_length = 3718.0;
append(landing_site_data.array, ls_entry5);

# RAF Fairford

var coord6 = geo.Coord.new();
coord6.set_latlon(51.682, -1.79, 0.0);
var ls_entry6 = landing_site_entry.new(coord6, "RAF Fairford", "FFA", "09", "27", "TAL", 6);
ls_entry6.tacan = "081"; 
ls_entry6.TAEM_pri_lat = 51.6831;
ls_entry6.TAEM_pri_lon = -1.8049;
ls_entry6.TAEM_pri_heading = 87.0;
ls_entry6.TAEM_pri_elevation = 316.0;
ls_entry6.TAEM_pri_MLS_flag = 0;
ls_entry6.TAEM_pri_MLS_channel = -1;
ls_entry6.TAEM_sec_lat = 51.6838;
ls_entry6.TAEM_sec_lon = -1.7723;
ls_entry6.TAEM_sec_heading = 267.0;
ls_entry6.TAEM_sec_elevation = 256.0;
ls_entry6.TAEM_sec_MLS_flag = 0;
ls_entry6.TAEM_sec_MLS_channel = -1;
ls_entry6.TAEM_rwy_length = 3045.0;
append(landing_site_data.array, ls_entry6);

# Banjul International Airport

var coord7 = geo.Coord.new();
coord7.set_latlon(13.337, -16.652, 0.0);
var ls_entry7 = landing_site_entry.new(coord7, "Banjul International Airport", "BYD", "14", "32", "TAL", 7);
ls_entry7.tacan = "076";
ls_entry7.TAEM_pri_lat = 13.3451;
ls_entry7.TAEM_pri_lon = -16.6608;
ls_entry7.TAEM_pri_heading = 131.0;
ls_entry7.TAEM_pri_elevation = 102.0;
ls_entry7.TAEM_pri_MLS_flag = 0;
ls_entry7.TAEM_pri_MLS_channel = -1;
ls_entry7.TAEM_sec_lat = 13.3301;
ls_entry7.TAEM_sec_lon = -16.6428;
ls_entry7.TAEM_sec_heading = 311.0;
ls_entry7.TAEM_sec_elevation = 102.0;
ls_entry7.TAEM_sec_MLS_flag = 0;
ls_entry7.TAEM_sec_MLS_channel = -1;
ls_entry7.TAEM_rwy_length = 3600.0;
append(landing_site_data.array, ls_entry7);

var coord8 = geo.Coord.new();
coord8.set_latlon(37.178, -5.614, 0.0);
var ls_entry8 = landing_site_entry.new(coord8, "Moron Air Base", "MRN", "02", "20", "TAL", 8);
ls_entry8.tacan = "100";
ls_entry8.TAEM_pri_lat = 37.1633;
ls_entry8.TAEM_pri_lon = -5.6212;
ls_entry8.TAEM_pri_heading = 20.0;
ls_entry8.TAEM_pri_elevation = 300.0;
ls_entry8.TAEM_pri_MLS_flag = 0;
ls_entry8.TAEM_pri_MLS_channel = -1;
ls_entry8.TAEM_sec_lat = 37.1863;
ls_entry8.TAEM_sec_lon = -5.6106;
ls_entry8.TAEM_sec_heading = 200.0;
ls_entry8.TAEM_sec_elevation = 280.0;
ls_entry8.TAEM_sec_MLS_flag = 1;
ls_entry8.TAEM_sec_MLS_channel = 6;
ls_entry8.TAEM_rwy_length = 3597.0;
append(landing_site_data.array, ls_entry8);

# Istres Le Tube

var coord9 = geo.Coord.new();
coord9.set_latlon(43.52, 4.92, 0.0);
var ls_entry9 = landing_site_entry.new(coord9, "Le Tube", "FMI", "15", "33", "TAL", 9);
ls_entry9.text_vertical_offset = -6.0;
ls_entry9.tacan = "104";
ls_entry9.TAEM_pri_lat = 43.5341;
ls_entry9.TAEM_pri_lon = 4.9158;
ls_entry9.TAEM_pri_heading = 152.0;
ls_entry9.TAEM_pri_elevation = 80.0;
ls_entry9.TAEM_pri_MLS_flag = 0;
ls_entry9.TAEM_pri_MLS_channel = -1;
ls_entry9.TAEM_sec_lat = 43.5104;
ls_entry9.TAEM_sec_lon = 4.9327;
ls_entry9.TAEM_sec_heading = 332.0;
ls_entry9.TAEM_sec_elevation = 80.0;
ls_entry9.TAEM_sec_MLS_flag = 1;
ls_entry9.TAEM_sec_MLS_channel = 6;
ls_entry9.TAEM_rwy_length = 5000.0;
append(landing_site_data.array, ls_entry9);

# Bermuda

var coord11 = geo.Coord.new();
coord11.set_latlon(32.363, -64.67, 0.0);
var ls_entry11 = landing_site_entry.new(coord11, "Bermuda", "BER", "12", "30", "ECAL", 11);
ls_entry11.tacan = "086";
ls_entry11.TAEM_pri_lat = 32.3659;
ls_entry11.TAEM_pri_lon = -64.6899;
ls_entry11.TAEM_pri_heading = 102.0;
ls_entry11.TAEM_pri_elevation = 25.0;
ls_entry11.TAEM_pri_MLS_flag = 0;
ls_entry11.TAEM_pri_MLS_channel = -1;
ls_entry11.TAEM_sec_lat = 32.3619;
ls_entry11.TAEM_sec_lon = -64.6667;
ls_entry11.TAEM_sec_heading = 282.0;
ls_entry11.TAEM_sec_elevation = 25.0;
ls_entry11.TAEM_sec_MLS_flag = 0;
ls_entry11.TAEM_sec_MLS_channel = -1;
ls_entry11.TAEM_rwy_length = 2947.0;
append(landing_site_data.array, ls_entry11);

# Halifax

var coord12 = geo.Coord.new();
coord12.set_latlon(44.875, -63.51, 0.0);
var ls_entry12 = landing_site_entry.new(coord12, "Halifax", "YHZ", "05", "23", "ECAL", 12);
ls_entry12.tacan = "110";
ls_entry12.TAEM_pri_lat = 44.8712;
ls_entry12.TAEM_pri_lon = -63.5224;
ls_entry12.TAEM_pri_heading = 35.0;
ls_entry12.TAEM_pri_elevation = 460.0;
ls_entry12.TAEM_pri_MLS_flag = 0;
ls_entry12.TAEM_pri_MLS_channel = -1;
ls_entry12.TAEM_sec_lat = 44.88645;
ls_entry12.TAEM_sec_lon = -63.5074;
ls_entry12.TAEM_sec_heading = 215.0;
ls_entry12.TAEM_sec_elevation = 460.0;
ls_entry12.TAEM_sec_MLS_flag = 0;
ls_entry12.TAEM_sec_MLS_channel = -1;
ls_entry12.TAEM_rwy_length = 3200.0;
append(landing_site_data.array, ls_entry12);


# Wilmington


var coord13 = geo.Coord.new();
coord13.set_latlon(34.272, -77.896, 0.0);
var ls_entry13 = landing_site_entry.new(coord13, "Wilmington", "ILM", "06", "24", "ECAL", 13);
ls_entry13.tacan = "117";
ls_entry13.TAEM_pri_lat = 34.263878;
ls_entry13.TAEM_pri_lon = -77.90763;
ls_entry13.TAEM_pri_heading = 48.5;
ls_entry13.TAEM_pri_elevation = 25.0;
ls_entry13.TAEM_pri_MLS_flag = 0;
ls_entry13.TAEM_pri_MLS_channel = -1;
ls_entry13.TAEM_sec_lat = 34.274647;
ls_entry13.TAEM_sec_lon = -77.89300;
ls_entry13.TAEM_sec_heading = 228.0;
ls_entry13.TAEM_sec_elevation = 25.0;
ls_entry13.TAEM_sec_MLS_flag = 0;
ls_entry13.TAEM_sec_MLS_channel = -1;
ls_entry13.TAEM_rwy_length = 2440.0;
append(landing_site_data.array, ls_entry13);

# Atlantic City

var coord14 = geo.Coord.new();
coord14.set_latlon(39.454, -74.568, 0.0);
var ls_entry14 = landing_site_entry.new(coord14, "Atlantic City", "ACY", "13", "31", "ECAL", 14);
ls_entry14.tacan = "081";
ls_entry14.TAEM_pri_lat = 39.463004;
ls_entry14.TAEM_pri_lon = -74.587947;
ls_entry14.TAEM_pri_heading = 118.0;
ls_entry14.TAEM_pri_elevation = 60.0;
ls_entry14.TAEM_pri_MLS_flag = 0;
ls_entry14.TAEM_pri_MLS_channel = -1;
ls_entry14.TAEM_sec_lat = 39.452876;
ls_entry14.TAEM_sec_lon = -74.563379;
ls_entry14.TAEM_sec_heading = 298.0;
ls_entry14.TAEM_sec_elevation = 60.0;
ls_entry14.TAEM_sec_MLS_flag = 0;
ls_entry14.TAEM_sec_MLS_channel = -1;
ls_entry14.TAEM_rwy_length = 3048.0;
append(landing_site_data.array, ls_entry14);

# Myrtle Beach

var coord15 = geo.Coord.new();
coord15.set_latlon(33.675, -78.926, 0.0);
var ls_entry15 = landing_site_entry.new(coord15, "Myrtle Beach", "MYR", "18", "36", "ECAL", 15);
ls_entry15.tacan = "117";
ls_entry15.TAEM_pri_lat = 33.68989;
ls_entry15.TAEM_pri_lon = -78.9308498;
ls_entry15.TAEM_pri_heading = 169.0;
ls_entry15.TAEM_pri_elevation = 30.0;
ls_entry15.TAEM_pri_MLS_flag = 0;
ls_entry15.TAEM_pri_MLS_channel = -1;
ls_entry15.TAEM_sec_lat = 33.669623;
ls_entry15.TAEM_sec_lon = -78.9258308;
ls_entry15.TAEM_sec_heading = 349.0;
ls_entry15.TAEM_sec_elevation = 30.0;
ls_entry15.TAEM_sec_MLS_flag = 0;
ls_entry15.TAEM_sec_MLS_channel = -1;
ls_entry15.TAEM_rwy_length = 2897.0;
append(landing_site_data.array, ls_entry15);

# Gander

var coord16 = geo.Coord.new();
coord16.set_latlon(48.947, -54.560, 0.0);
var ls_entry16 = landing_site_entry.new(coord16, "Gander", "YQX", "03", "21", "ECAL", 16);
ls_entry16.tacan = "074";
ls_entry16.TAEM_pri_lat = 48.922472;
ls_entry16.TAEM_pri_lon = -54.567853;
ls_entry16.TAEM_pri_heading = 11.0;
ls_entry16.TAEM_pri_elevation = 420.0;
ls_entry16.TAEM_pri_MLS_flag = 0;
ls_entry16.TAEM_pri_MLS_channel = -1;
ls_entry16.TAEM_sec_lat = 48.946827;
ls_entry16.TAEM_sec_lon = -54.560682;
ls_entry16.TAEM_sec_heading = 191.0;
ls_entry16.TAEM_sec_elevation = 450.0;
ls_entry16.TAEM_sec_MLS_flag = 0;
ls_entry16.TAEM_sec_MLS_channel = -1;
ls_entry16.TAEM_rwy_length = 3109.0;
append(landing_site_data.array, ls_entry16);

# Pease

var coord17 = geo.Coord.new();
coord17.set_latlon(43.0742, -70.820, 0.0);
var ls_entry17 = landing_site_entry.new(coord17, "Pease", "PSM", "16", "34", "ECAL", 17);
ls_entry17.tacan = "118";
ls_entry17.TAEM_pri_lat = 43.0870822;
ls_entry17.TAEM_pri_lon = -70.83065635;
ls_entry17.TAEM_pri_heading = 149.0;
ls_entry17.TAEM_pri_elevation = 100.0;
ls_entry17.TAEM_pri_MLS_flag = 0;
ls_entry17.TAEM_pri_MLS_channel = -1;
ls_entry17.TAEM_sec_lat = 43.0671732;
ls_entry17.TAEM_sec_lon = -70.814452883;
ls_entry17.TAEM_sec_heading = 329.0;
ls_entry17.TAEM_sec_elevation = 70.0;
ls_entry17.TAEM_sec_MLS_flag = 0;
ls_entry17.TAEM_sec_MLS_channel = -1;
ls_entry17.TAEM_rwy_length = 3451.0;
append(landing_site_data.array, ls_entry17);

# Oceana Naval Air Station

var coord18 = geo.Coord.new();
coord18.set_latlon(36.81, -76.012, 0.0);
var ls_entry18 = landing_site_entry.new(coord18, "Oceana NAS", "NTU", "05", "23", "ECAL", 18);
ls_entry18.tacan = "086";
ls_entry18.TAEM_pri_lat = 36.807229;
ls_entry18.TAEM_pri_lon = -76.04794;
ls_entry18.TAEM_pri_heading = 42.0;
ls_entry18.TAEM_pri_elevation = 23.0;
ls_entry18.TAEM_pri_MLS_flag = 0;
ls_entry18.TAEM_pri_MLS_channel = -1;
ls_entry18.TAEM_sec_lat = 36.827660;
ls_entry18.TAEM_sec_lon = -76.024951;
ls_entry18.TAEM_sec_heading = 222.0;
ls_entry18.TAEM_sec_elevation = 23.0;
ls_entry18.TAEM_sec_MLS_flag = 0;
ls_entry18.TAEM_sec_MLS_channel = -1;
ls_entry18.TAEM_rwy_length = 3651.0;
append(landing_site_data.array, ls_entry18);


# Mataveri Airport


var coord30 = geo.Coord.new();
coord30.set_latlon(-27.165, -109.415, 0.0);
var ls_entry30 = landing_site_entry.new(coord30, "Easter Island", "IPC", "10", "28", "TAL", 30);
ls_entry30.tacan = "118";
ls_entry30.TAEM_pri_lat = -27.1592;
ls_entry30.TAEM_pri_lon = -109.4337;
ls_entry30.TAEM_pri_heading = 117.0;
ls_entry30.TAEM_pri_elevation = 163.0;
ls_entry30.TAEM_pri_MLS_flag = 0;
ls_entry30.TAEM_pri_MLS_channel = -1;
ls_entry30.TAEM_sec_lat = -27.1707;
ls_entry30.TAEM_sec_lon = -109.4088;
ls_entry30.TAEM_sec_heading = 297.0;
ls_entry30.TAEM_sec_elevation = 224.0;
ls_entry30.TAEM_sec_MLS_flag = 0;
ls_entry30.TAEM_sec_MLS_channel = -1;
ls_entry30.TAEM_rwy_length = 3318.0;
append(landing_site_data.array, ls_entry30);


# Diego Garcia

var coord32 = geo.Coord.new();
coord32.set_latlon(-7.313, 72.411, 0.0);
var ls_entry32 = landing_site_entry.new(coord32, "Diego Garcia", "JDG", "13", "31", "emergency", 32);
ls_entry32.tacan = "057";
ls_entry32.TAEM_pri_lat = -7.30548;
ls_entry32.TAEM_pri_lon = 72.39848;
ls_entry32.TAEM_pri_heading = 121.5;
ls_entry32.TAEM_pri_elevation = 5.0;
ls_entry32.TAEM_pri_MLS_flag = 0;
ls_entry32.TAEM_pri_MLS_channel = -1;
ls_entry32.TAEM_sec_lat = -7.320205;
ls_entry32.TAEM_sec_lon = 72.42238;
ls_entry32.TAEM_sec_heading = 301.5;
ls_entry32.TAEM_sec_elevation = 10.0;
ls_entry32.TAEM_sec_MLS_flag = 0;
ls_entry32.TAEM_sec_MLS_channel = -1;
ls_entry32.TAEM_rwy_length = 3659.0;
append(landing_site_data.array, ls_entry32);


# Honolulu Intl.

var coord33 = geo.Coord.new();
coord33.set_latlon(21.307, -157.929, 0.0);
var ls_entry33 = landing_site_entry.new(coord33, "Honolulu", "HNL", "08", "26", "emergency", 33);
ls_entry33.tacan = "095";
ls_entry33.TAEM_pri_lat = 21.3068015;
ls_entry33.TAEM_pri_lon = -157.942542;
ls_entry33.TAEM_pri_heading = 90.0;
ls_entry33.TAEM_pri_elevation = 0.0;
ls_entry33.TAEM_pri_MLS_flag = 0;
ls_entry33.TAEM_pri_MLS_channel = -1;
ls_entry33.TAEM_sec_lat = 21.3067945;
ls_entry33.TAEM_sec_lon = -157.914083;
ls_entry33.TAEM_sec_heading = 270.0;
ls_entry33.TAEM_sec_elevation = 0.0;
ls_entry33.TAEM_sec_MLS_flag = 0;
ls_entry33.TAEM_sec_MLS_channel = -1;
ls_entry33.TAEM_rwy_length = 3753.0;
append(landing_site_data.array, ls_entry33);

# Keflavik

var coord34 = geo.Coord.new();
coord34.set_latlon(63.985, -22.618, 0.0);
var ls_entry34 = landing_site_entry.new(coord34, "Keflavik", "IKF", "10", "28", "emergency", 34);
ls_entry34.tacan = "057";
ls_entry34.TAEM_pri_lat = 63.985050;
ls_entry34.TAEM_pri_lon = -22.648608;
ls_entry34.TAEM_pri_heading = 90.0;
ls_entry34.TAEM_pri_elevation = 110.0;
ls_entry34.TAEM_pri_MLS_flag = 0;
ls_entry34.TAEM_pri_MLS_channel = -1;
ls_entry34.TAEM_sec_lat = 63.9850472;
ls_entry34.TAEM_sec_lon = -22.5986417;
ls_entry34.TAEM_sec_heading = 270.0;
ls_entry34.TAEM_sec_elevation = 175.0;
ls_entry34.TAEM_sec_MLS_flag = 0;
ls_entry34.TAEM_sec_MLS_channel = -1;
ls_entry34.TAEM_rwy_length = 3753.0;
append(landing_site_data.array, ls_entry34);

# Anderson Airforce Base Guam

var coord35 = geo.Coord.new();
coord35.set_latlon(13.584, 144.934, 0.0);
var ls_entry35 = landing_site_entry.new(coord35, "Andersen Air Force Base", "UAM", "06", "24", "emergency", 35);
ls_entry35.tacan = "078";
ls_entry35.TAEM_pri_lat = 13.5765189;
ls_entry35.TAEM_pri_lon = 144.91921413;
ls_entry35.TAEM_pri_heading = 66.0;
ls_entry35.TAEM_pri_elevation = 540.0;
ls_entry35.TAEM_pri_MLS_flag = 0;
ls_entry35.TAEM_pri_MLS_channel = -1;
ls_entry35.TAEM_sec_lat = 13.58715568;
ls_entry35.TAEM_sec_lon = 144.9434987;
ls_entry35.TAEM_sec_heading = 246.0;
ls_entry35.TAEM_sec_elevation = 590.0;
ls_entry35.TAEM_sec_MLS_flag = 0;
ls_entry35.TAEM_sec_MLS_channel = -1;
ls_entry35.TAEM_rwy_length = 3409.0;
append(landing_site_data.array, ls_entry35);

# Amilcar Cabral Capo Verde

var coord36 = geo.Coord.new();
coord36.set_latlon(16.73, -22.94, 0.0);
var ls_entry36 = landing_site_entry.new(coord36, "Amilcar Cabral", "CVS", "01", "19", "emergency", 36);
ls_entry36.tacan = "078";
ls_entry36.TAEM_pri_lat = 16.72694;
ls_entry36.TAEM_pri_lon = -22.94886;
ls_entry36.TAEM_pri_heading = 0.0;
ls_entry36.TAEM_pri_elevation = 185.0;
ls_entry36.TAEM_pri_MLS_flag = 0;
ls_entry36.TAEM_pri_MLS_channel = -1;
ls_entry36.TAEM_sec_lat = 16.745990;
ls_entry36.TAEM_sec_lon = -22.9489702;
ls_entry36.TAEM_sec_heading = 180.0;
ls_entry36.TAEM_sec_elevation = 178.0;
ls_entry36.TAEM_sec_MLS_flag = 0;
ls_entry36.TAEM_sec_MLS_channel = -1;
ls_entry36.TAEM_rwy_length = 3272.0;
append(landing_site_data.array, ls_entry36);

# Ascension Island

var coord37 = geo.Coord.new();
coord37.set_latlon(-7.97, -14.39, 0.0);
var ls_entry37 = landing_site_entry.new(coord37, "Ascension", "HAW", "13", "31", "emergency", 37);
ls_entry37.tacan = "059";
ls_entry37.TAEM_pri_lat = -7.96408717;
ls_entry37.TAEM_pri_lon = -14.4046994;
ls_entry37.TAEM_pri_heading = 117.0;
ls_entry37.TAEM_pri_elevation = 277.0;
ls_entry37.TAEM_pri_MLS_flag = 0;
ls_entry37.TAEM_pri_MLS_channel = -1;
ls_entry37.TAEM_sec_lat = -7.9751031;
ls_entry37.TAEM_sec_lon = -14.382679;
ls_entry37.TAEM_sec_heading = 297.0;
ls_entry37.TAEM_sec_elevation = 243.0;
ls_entry37.TAEM_sec_MLS_flag = 0;
ls_entry37.TAEM_sec_MLS_channel = -1;
ls_entry37.TAEM_rwy_length = 3054.0;
append(landing_site_data.array, ls_entry37);

# Wake Island

var coord38 = geo.Coord.new();
coord38.set_latlon(19.282, 166.63, 0.0);
var ls_entry38 = landing_site_entry.new(coord38, "Wake Island", "WAK", "10", "28", "emergency", 38);
ls_entry38.tacan = "082";
ls_entry38.TAEM_pri_lat = 19.2844870;
ls_entry38.TAEM_pri_lon = 166.6243612;
ls_entry38.TAEM_pri_heading = 102.0;
ls_entry38.TAEM_pri_elevation = 20.0;
ls_entry38.TAEM_pri_MLS_flag = 0;
ls_entry38.TAEM_pri_MLS_channel = -1;
ls_entry38.TAEM_sec_lat = 19.27952525;
ls_entry38.TAEM_sec_lon = 166.649126;
ls_entry38.TAEM_sec_heading = 282.0;
ls_entry38.TAEM_sec_elevation = 35.0;
ls_entry38.TAEM_sec_MLS_flag = 0;
ls_entry38.TAEM_sec_MLS_channel = -1;
ls_entry38.TAEM_rwy_length = 3000.0;
append(landing_site_data.array, ls_entry38);

# Lajes Air Base

var coord39 = geo.Coord.new();
coord39.set_latlon(38.761, -27.09, 0.0);
var ls_entry39 = landing_site_entry.new(coord39, "Lajes Air Base", "LAJ", "15", "33", "emergency", 39);
ls_entry39.tacan = "109";
ls_entry39.TAEM_pri_lat = 38.77373704;
ls_entry39.TAEM_pri_lon = -27.103272055;
ls_entry39.TAEM_pri_heading = 141.0;
ls_entry39.TAEM_pri_elevation = 170.0;
ls_entry39.TAEM_pri_MLS_flag = 0;
ls_entry39.TAEM_pri_MLS_channel = -1;
ls_entry39.TAEM_sec_lat = 38.75501808;
ls_entry39.TAEM_sec_lon = -27.08362772;
ls_entry39.TAEM_sec_heading = 321.0;
ls_entry39.TAEM_sec_elevation = 187.0;
ls_entry39.TAEM_sec_MLS_flag = 0;
ls_entry39.TAEM_sec_MLS_channel = -1;
ls_entry39.TAEM_rwy_length = 3314.0;
append(landing_site_data.array, ls_entry39);


# Edwards Air Force Base Lakebed STS 1 Rwy 23L (11° East declinaison)

var coord90 = geo.Coord.new();
coord90.set_latlon(34.949259, -117.866050, 0.0);
var ls_entry90 = landing_site_entry.new(coord90, "Edwards Air Force Base Lakebed", "EDW", "23", "05", "regular", 90);
#ls_entry90.text_vertical_offset = -6.0;
ls_entry90.tacan = "111";
ls_entry90.TAEM_pri_lat = 34.966945;
ls_entry90.TAEM_pri_lon = -117.817116;
ls_entry90.TAEM_pri_heading = 244.6;
ls_entry90.TAEM_pri_elevation = 2270.0;
ls_entry90.TAEM_pri_MLS_flag = 1;
ls_entry90.TAEM_pri_MLS_channel = 8;
ls_entry90.TAEM_sec_lat = 34.949173;
ls_entry90.TAEM_sec_lon = -117.862192;
ls_entry90.TAEM_sec_heading = 064.6;
ls_entry90.TAEM_sec_elevation = 2270.0;
ls_entry90.TAEM_sec_MLS_flag = 1;
ls_entry90.TAEM_sec_MLS_channel = 6;
ls_entry90.TAEM_rwy_length = 5572.0;
append(landing_site_data.array, ls_entry90);





