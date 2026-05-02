#---------------------------------------
# SpaceShuttle PFD Page include:
#        Page: p_main
# Description: the main menu page showing just selection buttons
#      Author: Thorsten Renk, 2015
#---------------------------------------

var PFD_addpage_p_meds_autonomous = func(device)
{
    var p_meds_autonomous = device.addPage("AutonomousMenu", "p_meds_autonomous");

    
   

    #Arrow in one path instead of 5 in SVG to avoid rough angles
    #d="M 38, 494.0 v -20.0 h -15 L 48.0, 461 L 73.0, 474 h -15 v 20.0"
    
    p_meds_autonomous.up = device.svg.getElementById("meds_menu_up_global"); 

    p_meds_autonomous.ondisplay = func
    {
        device.set_DPS_off();
        device.MEDS_menu_title.setText("   MDU IS AUTONOMOUS");
	p_meds_autonomous.up.setVisible(0);
    }

   p_meds_autonomous.offdisplay = func 
    {
	p_meds_autonomous.up.setVisible(1);

    }
    
    
    
    return p_meds_autonomous;
}
