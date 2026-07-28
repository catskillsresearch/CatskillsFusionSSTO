#---------------------------------------
# SpaceShuttle PFD Page include:
#        Page: p_meds_oms_mps
# Description: the OMS/MPS MEDS page
#      Author: Gijs de Rooy, Thorsten Renk, 2016
#---------------------------------------

var PFD_addpage_p_meds_apu = func(device)
{
    var p_meds_apu = device.addPage("MEDSApu", "p_meds_apu");

    p_meds_apu.hyd_qty1 = device.svg.getElementById("p_meds_apu_hyd_qty1"); 
    p_meds_apu.hyd_qty2 = device.svg.getElementById("p_meds_apu_hyd_qty2"); 
    p_meds_apu.hyd_qty3 = device.svg.getElementById("p_meds_apu_hyd_qty3"); 

    p_meds_apu.tape_hyd_qty1 = device.svg.getElementById("p_meds_apu_tape_hyd_qty1"); 
    p_meds_apu.tape_hyd_qty2 = device.svg.getElementById("p_meds_apu_tape_hyd_qty2"); 
    p_meds_apu.tape_hyd_qty3 = device.svg.getElementById("p_meds_apu_tape_hyd_qty3"); 

    p_meds_apu.h2o_qty1 = device.svg.getElementById("p_meds_apu_h2o_qty1"); 
    p_meds_apu.h2o_qty2 = device.svg.getElementById("p_meds_apu_h2o_qty2"); 
    p_meds_apu.h2o_qty3 = device.svg.getElementById("p_meds_apu_h2o_qty3");

    p_meds_apu.tape_h2o_qty1 = device.svg.getElementById("p_meds_apu_tape_h2o_qty1"); 
    p_meds_apu.tape_h2o_qty2 = device.svg.getElementById("p_meds_apu_tape_h2o_qty2"); 
    p_meds_apu.tape_h2o_qty3 = device.svg.getElementById("p_meds_apu_tape_h2o_qty3"); 


    p_meds_apu.fuel_qty1 = device.svg.getElementById("p_meds_apu_fuel_qty1"); 
    p_meds_apu.fuel_qty2 = device.svg.getElementById("p_meds_apu_fuel_qty2"); 
    p_meds_apu.fuel_qty3 = device.svg.getElementById("p_meds_apu_fuel_qty3"); 

    p_meds_apu.tape_fuel_qty1 = device.svg.getElementById("p_meds_apu_tape_fuel_qty1"); 
    p_meds_apu.tape_fuel_qty2 = device.svg.getElementById("p_meds_apu_tape_fuel_qty2"); 
    p_meds_apu.tape_fuel_qty3 = device.svg.getElementById("p_meds_apu_tape_fuel_qty3"); 

    p_meds_apu.hyd_p1 = device.svg.getElementById("p_meds_apu_hyd_p1"); 
    p_meds_apu.hyd_p2 = device.svg.getElementById("p_meds_apu_hyd_p2"); 
    p_meds_apu.hyd_p3 = device.svg.getElementById("p_meds_apu_hyd_p3"); 

    p_meds_apu.tape_hyd_p1 = device.svg.getElementById("p_meds_apu_tape_hyd_p1");
    p_meds_apu.tape_hyd_p2 = device.svg.getElementById("p_meds_apu_tape_hyd_p2"); 
    p_meds_apu.tape_hyd_p3 = device.svg.getElementById("p_meds_apu_tape_hyd_p3");  

    p_meds_apu.oilT1 = device.svg.getElementById("p_meds_apu_oilT1"); 
    p_meds_apu.oilT2 = device.svg.getElementById("p_meds_apu_oilT2"); 
    p_meds_apu.oilT3 = device.svg.getElementById("p_meds_apu_oilT3"); 

    p_meds_apu.tape_oilT1 = device.svg.getElementById("p_meds_apu_tape_oilT1"); 
    p_meds_apu.tape_oilT2 = device.svg.getElementById("p_meds_apu_tape_oilT2"); 
    p_meds_apu.tape_oilT3 = device.svg.getElementById("p_meds_apu_tape_oilT3"); 


    p_meds_apu.fuelP1 = device.svg.getElementById("p_meds_apu_fuelP1"); 
    p_meds_apu.fuelP2 = device.svg.getElementById("p_meds_apu_fuelP2"); 
    p_meds_apu.fuelP3 = device.svg.getElementById("p_meds_apu_fuelP3"); 

    p_meds_apu.tape_fuelP1 = device.svg.getElementById("p_meds_apu_tape_fuelP1"); 
    p_meds_apu.tape_fuelP2 = device.svg.getElementById("p_meds_apu_tape_fuelP2"); 
    p_meds_apu.tape_fuelP3 = device.svg.getElementById("p_meds_apu_tape_fuelP3"); 
	 

    p_meds_apu.menu_item = device.svg.getElementById("MI_2"); 
    p_meds_apu.menu_item_frame = device.svg.getElementById("MI_2_frame"); 


	p_meds_apu.APU_label = device.svg.getElementById("APU_label"); 
	p_meds_apu.HYD_label = device.svg.getElementById("HYD_label");


	#SVG elements with different fonts (SSU B) APU and HYDRAULIC

	p_meds_apu.APU_label.setFont(p_pfd_font_2);
	p_meds_apu.HYD_label.setFont(p_pfd_font_2);
	


    p_meds_apu.ondisplay = func
    {
    
        device.set_DPS_off();
        device.MEDS_menu_title.setText("    SUBSYSTEM MENU");
	p_meds_apu.menu_item.setColor(1.0, 1.0, 1.0);
	p_meds_apu.menu_item_frame.setColor(1.0, 1.0, 1.0);
	p_meds_apu.APU_label.setText("CHARM");
	p_meds_apu.HYD_label.setText("PLANT");



    }
    
    p_meds_apu.update = func
    {
	# Grenadier CHARM / plant services — reuse APU/HYD tape layout.
	var C = "/fdm/jsbsim/systems/grenadier/charm/";
	var E = "/fdm/jsbsim/systems/grenadier/engine/";
	var mode = getprop(C ~ "mode");
	if (mode == nil) mode = "OFF";

	var cart = getprop(C ~ "ground-cart"); if (cart == nil) cart = 0;
	var batt = getprop(C ~ "battery-online"); if (batt == nil) batt = 0;
	var cryo = getprop(C ~ "cryo-enable"); if (cryo == nil) cryo = 0;
	var mag = getprop(C ~ "magnet-arm"); if (mag == nil) mag = 0;
	var fuel = getprop(C ~ "fuel-enable"); if (fuel == nil) fuel = 0;
	var rf = getprop(C ~ "rf-enable"); if (rf == nil) rf = 0;
	var light = getprop(C ~ "light-cmd"); if (light == nil) light = 0;
	var dec = getprop(C ~ "dec-online"); if (dec == nil) dec = 0;
	var vac = getprop(C ~ "vacuum-ready"); if (vac == nil) vac = 0;

	var batt_frac = getprop(C ~ "battery-kwh"); if (batt_frac == nil) batt_frac = 0;
	batt_frac = batt_frac / 500.0;
	if (batt_frac > 1) batt_frac = 1;
	var mi = getprop(C ~ "magnet-i-frac"); if (mi == nil) mi = 0;
	var pp = getprop(C ~ "plasma-proxy"); if (pp == nil) pp = 0;
	var bus = getprop(C ~ "bus-mw"); if (bus == nil) bus = 0;
	var aux = getprop(C ~ "aux-bus-v"); if (aux == nil) aux = 0;
	var tk = getprop(C ~ "magnet-t-k"); if (tk == nil) tk = 80;
	var water = getprop(E ~ "water-kg"); if (water == nil) water = 0;
	var water_frac = water / 44000.0;
	if (water_frac > 1) water_frac = 1;

	# Row: "fuel qty" tapes → batt / magnet I / plasma
	p_meds_apu.fuel_qty1.setText(sprintf("%03d", batt_frac * 100.0));
	p_meds_apu.fuel_qty2.setText(sprintf("%03d", mi * 100.0));
	p_meds_apu.fuel_qty3.setText(sprintf("%03d", pp * 100.0));
	set_tape(p_meds_apu.tape_fuel_qty1, batt_frac, 63.7+60.7);
	set_tape(p_meds_apu.tape_fuel_qty2, mi, 63.7+60.7);
	set_tape(p_meds_apu.tape_fuel_qty3, pp, 63.7+60.7);
	if (batt_frac < 0.6) {p_meds_apu.tape_fuel_qty1.setColorFill(1.0, 0.0, 0.0);} else {p_meds_apu.tape_fuel_qty1.setColorFill(0.0, 1.0, 0.0);}
	if (mi < 0.95) {p_meds_apu.tape_fuel_qty2.setColorFill(1.0, 0.0, 0.0);} else {p_meds_apu.tape_fuel_qty2.setColorFill(0.0, 1.0, 0.0);}
	p_meds_apu.tape_fuel_qty3.setColorFill(0.0, 1.0, 0.0);

	# "fuel P" → aux V, bus MW/10, mode index*100
	var midx = getprop(C ~ "mode-index"); if (midx == nil) midx = 0;
	p_meds_apu.fuelP1.setText(sprintf("%04d", aux));
	p_meds_apu.fuelP2.setText(sprintf("%04d", bus / 10.0));
	p_meds_apu.fuelP3.setText(sprintf("%04d", midx * 100));
	set_tape(p_meds_apu.tape_fuelP1, aux / 300.0, 60.7 + 63.7);
	set_tape(p_meds_apu.tape_fuelP2, (bus / 1000.0), 60.7 + 63.7);
	set_tape(p_meds_apu.tape_fuelP3, midx / 5.0, 60.7 + 63.7);

	# "h2o qty" → cart / batt / cryo as 0/100
	p_meds_apu.h2o_qty1.setText(sprintf("%03d", cart * 100));
	p_meds_apu.h2o_qty2.setText(sprintf("%03d", batt * 100));
	p_meds_apu.h2o_qty3.setText(sprintf("%03d", cryo * 100));
	set_tape(p_meds_apu.tape_h2o_qty1, cart, 60.7 + 170.4);
	set_tape(p_meds_apu.tape_h2o_qty2, batt, 60.7 + 170.4);
	set_tape(p_meds_apu.tape_h2o_qty3, cryo, 60.7 + 170.4);
	p_meds_apu.tape_h2o_qty1.setColorFill(0.0, 1.0, 0.0);
	p_meds_apu.tape_h2o_qty2.setColorFill(0.0, 1.0, 0.0);
	p_meds_apu.tape_h2o_qty3.setColorFill(0.0, 1.0, 0.0);

	# "oil T" → magnet T K, RF, LIGHT as coded ints
	p_meds_apu.oilT1.setText(sprintf("%04d", tk));
	p_meds_apu.oilT2.setText(sprintf("%04d", rf * 1000 + light * 100));
	p_meds_apu.oilT3.setText(sprintf("%04d", dec * 1000 + vac * 100));
	set_tape(p_meds_apu.tape_oilT1, (80.0 - tk) / 80.0, 170.4+60.7);
	var oil2 = 0.2; if (rf and light) oil2 = 1.0;
	var oil3 = 0.2; if (dec and vac) oil3 = 1.0;
	set_tape(p_meds_apu.tape_oilT2, oil2, 170.4+60.7);
	set_tape(p_meds_apu.tape_oilT3, oil3, 170.4+60.7);

	# "hyd qty" → mag / fuel / water inventory
	p_meds_apu.hyd_qty1.setText(sprintf("%03d", mag * 100));
	p_meds_apu.hyd_qty2.setText(sprintf("%03d", fuel * 100));
	p_meds_apu.hyd_qty3.setText(sprintf("%03d", water_frac * 100));
	set_tape(p_meds_apu.tape_hyd_qty1, mag, 60.7 + 295.8);
	set_tape(p_meds_apu.tape_hyd_qty2, fuel, 60.7 + 295.8);
	set_tape(p_meds_apu.tape_hyd_qty3, water_frac, 60.7 + 295.8);

	# "hyd press" → go-magnet / go-fuel / go-bus as 0 or 3000
	var gm = getprop(C ~ "go-magnet"); if (gm == nil) gm = 0;
	var gf = getprop(C ~ "go-fuel"); if (gf == nil) gf = 0;
	var gb = getprop(C ~ "go-bus"); if (gb == nil) gb = 0;
	p_meds_apu.hyd_p1.setText(sprintf("%04d", gm * 3000));
	p_meds_apu.hyd_p2.setText(sprintf("%04d", gf * 3000));
	p_meds_apu.hyd_p3.setText(sprintf("%04d", gb * 3000));
	set_tape(p_meds_apu.tape_hyd_p1, gm, 60.7 + 295.8);
	set_tape(p_meds_apu.tape_hyd_p2, gf, 60.7 + 295.8);
	set_tape(p_meds_apu.tape_hyd_p3, gb, 60.7 + 295.8);
	if (gm) {p_meds_apu.tape_hyd_p1.setColorFill(0.0, 1.0, 0.0);} else {p_meds_apu.tape_hyd_p1.setColorFill(1.0, 0.0, 0.0);}
	if (gf) {p_meds_apu.tape_hyd_p2.setColorFill(0.0, 1.0, 0.0);} else {p_meds_apu.tape_hyd_p2.setColorFill(1.0, 0.0, 0.0);}
	if (gb) {p_meds_apu.tape_hyd_p3.setColorFill(0.0, 1.0, 0.0);} else {p_meds_apu.tape_hyd_p3.setColorFill(1.0, 0.0, 0.0);}

    }

    p_meds_apu.offdisplay = func
    {
    
        p_meds_apu.menu_item.setColor(meds_r, meds_g, meds_b);
	p_meds_apu.menu_item_frame.setColor(meds_r, meds_g, meds_b);
    }
    
    
    
    return p_meds_apu;
}
