#---------------------------------------
# SpaceShuttle PFD Page include:
#        Page: p_main
# Description: the main menu page showing just selection buttons
#      Author: Thorsten Renk, 2015 // GinGin, 2020
#---------------------------------------

var PFD_addpage_p_main = func(device)
{
    var p_main = device.addPage("MainMenu", "p_main");

    #Arrow in one path instead of 5 in SVG to avoid rough angles
    #d="M 38, 494.0 v -20.0 h -15 L 48.0, 461 L 73.0, 474 h -15 v 20.0"
    
    p_main.up = device.svg.getElementById("meds_menu_up_global"); 

    p_main.ondisplay = func
    {
        device.set_DPS_off();
        device.MEDS_menu_title.setText("      MAIN MENU");
	p_main.up.setVisible(0);
    }

   p_main.offdisplay = func 
    {
	p_main.up.setVisible(1);
    }
    
    
    
    return p_main;
}
