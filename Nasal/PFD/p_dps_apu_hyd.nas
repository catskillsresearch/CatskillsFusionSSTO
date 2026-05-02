#---------------------------------------
# SpaceShuttle PFD Page include:
#        Page: p_dps_apu_hyd
# Description: the APU/HYD page
#      Author: Thorsten Renk, 2015 // GinGin, 2020
#---------------------------------------

var PFD_addpage_p_dps_apu_hyd = func(device)
{
    var p_dps_apu_hyd = device.addPage("CRTApuHyd", "p_dps_apu_hyd");
    
    p_dps_apu_hyd.group = device.svg.getElementById("p_dps_apu_hyd");
    p_dps_apu_hyd.group.setColor(dps_r, dps_g, dps_b);

    p_dps_apu_hyd.speed_pct_1 = device.svg.getElementById("p_dps_apu_hyd_speed_pct_1");
    p_dps_apu_hyd.speed_pct_2 = device.svg.getElementById("p_dps_apu_hyd_speed_pct_2");
    p_dps_apu_hyd.speed_pct_3 = device.svg.getElementById("p_dps_apu_hyd_speed_pct_3");
    
    p_dps_apu_hyd.fuel_qty_1 = device.svg.getElementById("p_dps_apu_hyd_fuel_qty_1");
    p_dps_apu_hyd.fuel_qty_2 = device.svg.getElementById("p_dps_apu_hyd_fuel_qty_2");
    p_dps_apu_hyd.fuel_qty_3 = device.svg.getElementById("p_dps_apu_hyd_fuel_qty_3");
    
    p_dps_apu_hyd.vlv_a_1 = device.svg.getElementById("p_dps_apu_hyd_vlv_a_1");
    p_dps_apu_hyd.vlv_a_2 = device.svg.getElementById("p_dps_apu_hyd_vlv_a_2");
    p_dps_apu_hyd.vlv_a_3 = device.svg.getElementById("p_dps_apu_hyd_vlv_a_3");
    
    p_dps_apu_hyd.vlv_b_1 = device.svg.getElementById("p_dps_apu_hyd_vlv_b_1");
    p_dps_apu_hyd.vlv_b_2 = device.svg.getElementById("p_dps_apu_hyd_vlv_b_2");
    p_dps_apu_hyd.vlv_b_3 = device.svg.getElementById("p_dps_apu_hyd_vlv_b_3");
    
    p_dps_apu_hyd.oil_t_1 = device.svg.getElementById("p_dps_apu_hyd_oil_t_1");
    p_dps_apu_hyd.oil_t_2 = device.svg.getElementById("p_dps_apu_hyd_oil_t_2");
    p_dps_apu_hyd.oil_t_3 = device.svg.getElementById("p_dps_apu_hyd_oil_t_3");
    
    p_dps_apu_hyd.oil_outt_1 = device.svg.getElementById("p_dps_apu_hyd_oil_outt_1");
    p_dps_apu_hyd.oil_outt_2 = device.svg.getElementById("p_dps_apu_hyd_oil_outt_2");
    p_dps_apu_hyd.oil_outt_3 = device.svg.getElementById("p_dps_apu_hyd_oil_outt_3");
    
    p_dps_apu_hyd.bu_p_1 = device.svg.getElementById("p_dps_apu_hyd_bu_p_1");
    p_dps_apu_hyd.bu_p_2 = device.svg.getElementById("p_dps_apu_hyd_bu_p_2");
    p_dps_apu_hyd.bu_p_3 = device.svg.getElementById("p_dps_apu_hyd_bu_p_3");
    
    p_dps_apu_hyd.h2o_1 = device.svg.getElementById("p_dps_apu_hyd_h2o_1");
    p_dps_apu_hyd.h2o_2 = device.svg.getElementById("p_dps_apu_hyd_h2o_2");
    p_dps_apu_hyd.h2o_3 = device.svg.getElementById("p_dps_apu_hyd_h2o_3");
    
    p_dps_apu_hyd.cntlr_1 = device.svg.getElementById("p_dps_apu_hyd_cntlr_1");
    p_dps_apu_hyd.cntlr_2 = device.svg.getElementById("p_dps_apu_hyd_cntlr_2");
    p_dps_apu_hyd.cntlr_3 = device.svg.getElementById("p_dps_apu_hyd_cntlr_3");
    
    p_dps_apu_hyd.bu_egt_1 = device.svg.getElementById("p_dps_apu_hyd_bu_egt_1");
    p_dps_apu_hyd.bu_egt_2 = device.svg.getElementById("p_dps_apu_hyd_bu_egt_2");
    p_dps_apu_hyd.bu_egt_3 = device.svg.getElementById("p_dps_apu_hyd_bu_egt_3");
    
    p_dps_apu_hyd.egt_1 = device.svg.getElementById("p_dps_apu_hyd_egt_1");
    p_dps_apu_hyd.egt_2 = device.svg.getElementById("p_dps_apu_hyd_egt_2");
    p_dps_apu_hyd.egt_3 = device.svg.getElementById("p_dps_apu_hyd_egt_3");
    
    p_dps_apu_hyd.n2_p_1 = device.svg.getElementById("p_dps_apu_hyd_n2_p_1");
    p_dps_apu_hyd.n2_p_2 = device.svg.getElementById("p_dps_apu_hyd_n2_p_2");
    p_dps_apu_hyd.n2_p_3 = device.svg.getElementById("p_dps_apu_hyd_n2_p_3");
    
    p_dps_apu_hyd.wsb_n2_p_1 = device.svg.getElementById("p_dps_apu_hyd_wsb_n2_p_1");
    p_dps_apu_hyd.wsb_n2_p_2 = device.svg.getElementById("p_dps_apu_hyd_wsb_n2_p_2");
    p_dps_apu_hyd.wsb_n2_p_3 = device.svg.getElementById("p_dps_apu_hyd_wsb_n2_p_3");
    
    p_dps_apu_hyd.accum_p_1 = device.svg.getElementById("p_dps_apu_hyd_accum_p_1");
    p_dps_apu_hyd.accum_p_2 = device.svg.getElementById("p_dps_apu_hyd_accum_p_2");
    p_dps_apu_hyd.accum_p_3 = device.svg.getElementById("p_dps_apu_hyd_accum_p_3");
    
    p_dps_apu_hyd.vlv_at_1 = device.svg.getElementById("p_dps_apu_hyd_vlv_at_1");
    p_dps_apu_hyd.vlv_at_2 = device.svg.getElementById("p_dps_apu_hyd_vlv_at_2");
    p_dps_apu_hyd.vlv_at_3 = device.svg.getElementById("p_dps_apu_hyd_vlv_at_3");
    
    p_dps_apu_hyd.vlv_bt_1 = device.svg.getElementById("p_dps_apu_hyd_vlv_bt_1");
    p_dps_apu_hyd.vlv_bt_2 = device.svg.getElementById("p_dps_apu_hyd_vlv_bt_2");
    p_dps_apu_hyd.vlv_bt_3 = device.svg.getElementById("p_dps_apu_hyd_vlv_bt_3");
    
    p_dps_apu_hyd.rsvr_t_1 = device.svg.getElementById("p_dps_apu_hyd_rsvr_t_1");
    p_dps_apu_hyd.rsvr_t_2 = device.svg.getElementById("p_dps_apu_hyd_rsvr_t_2");
    p_dps_apu_hyd.rsvr_t_3 = device.svg.getElementById("p_dps_apu_hyd_rsvr_t_3");
    
    p_dps_apu_hyd.ggbed_t_1 = device.svg.getElementById("p_dps_apu_hyd_ggbed_t_1");
    p_dps_apu_hyd.ggbed_t_2 = device.svg.getElementById("p_dps_apu_hyd_ggbed_t_2");
    p_dps_apu_hyd.ggbed_t_3 = device.svg.getElementById("p_dps_apu_hyd_ggbed_t_3");
    
    p_dps_apu_hyd.tank_t_1 = device.svg.getElementById("p_dps_apu_hyd_tank_t_1");
    p_dps_apu_hyd.tank_t_2 = device.svg.getElementById("p_dps_apu_hyd_tank_t_2");
    p_dps_apu_hyd.tank_t_3 = device.svg.getElementById("p_dps_apu_hyd_tank_t_3");
    
    p_dps_apu_hyd.blr_t_1 = device.svg.getElementById("p_dps_apu_hyd_blr_t_1");
    p_dps_apu_hyd.blr_t_2 = device.svg.getElementById("p_dps_apu_hyd_blr_t_2");
    p_dps_apu_hyd.blr_t_3 = device.svg.getElementById("p_dps_apu_hyd_blr_t_3");
    
    p_dps_apu_hyd.reg_p_1 = device.svg.getElementById("p_dps_apu_hyd_reg_p_1");
    p_dps_apu_hyd.reg_p_2 = device.svg.getElementById("p_dps_apu_hyd_reg_p_2");
    p_dps_apu_hyd.reg_p_3 = device.svg.getElementById("p_dps_apu_hyd_reg_p_3");
    
    p_dps_apu_hyd.n2_t_1 = device.svg.getElementById("p_dps_apu_hyd_n2_t_1");
    p_dps_apu_hyd.n2_t_2 = device.svg.getElementById("p_dps_apu_hyd_n2_t_2");
    p_dps_apu_hyd.n2_t_3 = device.svg.getElementById("p_dps_apu_hyd_n2_t_3");
    
    p_dps_apu_hyd.vent_t_1 = device.svg.getElementById("p_dps_apu_hyd_vent_t_1");
    p_dps_apu_hyd.vent_t_2 = device.svg.getElementById("p_dps_apu_hyd_vent_t_2");
    p_dps_apu_hyd.vent_t_3 = device.svg.getElementById("p_dps_apu_hyd_vent_t_3");
    
    p_dps_apu_hyd.rsvr_qty_1 = device.svg.getElementById("p_dps_apu_hyd_rsvr_qty_1");
    p_dps_apu_hyd.rsvr_qty_2 = device.svg.getElementById("p_dps_apu_hyd_rsvr_qty_2");
    p_dps_apu_hyd.rsvr_qty_3 = device.svg.getElementById("p_dps_apu_hyd_rsvr_qty_3");
    
    p_dps_apu_hyd.rsvr_p_1 = device.svg.getElementById("p_dps_apu_hyd_rsvr_p_1");
    p_dps_apu_hyd.rsvr_p_2 = device.svg.getElementById("p_dps_apu_hyd_rsvr_p_2");
    p_dps_apu_hyd.rsvr_p_3 = device.svg.getElementById("p_dps_apu_hyd_rsvr_p_3");
    
    p_dps_apu_hyd.tk_p_1 = device.svg.getElementById("p_dps_apu_hyd_tk_p_1");
    p_dps_apu_hyd.tk_p_2 = device.svg.getElementById("p_dps_apu_hyd_tk_p_2");
    p_dps_apu_hyd.tk_p_3 = device.svg.getElementById("p_dps_apu_hyd_tk_p_3");
    
    p_dps_apu_hyd.out_p_1 = device.svg.getElementById("p_dps_apu_hyd_out_p_1");
    p_dps_apu_hyd.out_p_2 = device.svg.getElementById("p_dps_apu_hyd_out_p_2");
    p_dps_apu_hyd.out_p_3 = device.svg.getElementById("p_dps_apu_hyd_out_p_3");
    
    p_dps_apu_hyd.pmp_t_1 = device.svg.getElementById("p_dps_apu_hyd_pmp_t_1");
    p_dps_apu_hyd.pmp_t_2 = device.svg.getElementById("p_dps_apu_hyd_pmp_t_2");
    p_dps_apu_hyd.pmp_t_3 = device.svg.getElementById("p_dps_apu_hyd_pmp_t_3");
    
    p_dps_apu_hyd.vlv_t_1 = device.svg.getElementById("p_dps_apu_hyd_vlv_t_1");
    p_dps_apu_hyd.vlv_t_2 = device.svg.getElementById("p_dps_apu_hyd_vlv_t_2");
    p_dps_apu_hyd.vlv_t_3 = device.svg.getElementById("p_dps_apu_hyd_vlv_t_3");
    
    p_dps_apu_hyd.oil_outp_1 = device.svg.getElementById("p_dps_apu_hyd_oil_outp_1");
    p_dps_apu_hyd.oil_outp_2 = device.svg.getElementById("p_dps_apu_hyd_oil_outp_2");
    p_dps_apu_hyd.oil_outp_3 = device.svg.getElementById("p_dps_apu_hyd_oil_outp_3");
    
    p_dps_apu_hyd.gbx_p_1 = device.svg.getElementById("p_dps_apu_hyd_gbx_p_1");
    p_dps_apu_hyd.gbx_p_2 = device.svg.getElementById("p_dps_apu_hyd_gbx_p_2");
    p_dps_apu_hyd.gbx_p_3 = device.svg.getElementById("p_dps_apu_hyd_gbx_p_3");
    
    p_dps_apu_hyd.byp_vlv_1 = device.svg.getElementById("p_dps_apu_hyd_byp_vlv_1");
    p_dps_apu_hyd.byp_vlv_2 = device.svg.getElementById("p_dps_apu_hyd_byp_vlv_2");
    p_dps_apu_hyd.byp_vlv_3 = device.svg.getElementById("p_dps_apu_hyd_byp_vlv_3");
    
    p_dps_apu_hyd.brg_t_1 = device.svg.getElementById("p_dps_apu_hyd_brg_t_1");
    p_dps_apu_hyd.brg_t_2 = device.svg.getElementById("p_dps_apu_hyd_brg_t_2");
    p_dps_apu_hyd.brg_t_3 = device.svg.getElementById("p_dps_apu_hyd_brg_t_3");

    #Indicators

    p_dps_apu_hyd.speed_pct_1_arrow = device.svg.getElementById("p_dps_apu_hyd_speed_pct_1_arrow");
    p_dps_apu_hyd.speed_pct_2_arrow = device.svg.getElementById("p_dps_apu_hyd_speed_pct_2_arrow");
    p_dps_apu_hyd.speed_pct_3_arrow = device.svg.getElementById("p_dps_apu_hyd_speed_pct_3_arrow");
    
    p_dps_apu_hyd.fuel_qty_1_arrow = device.svg.getElementById("p_dps_apu_hyd_fuel_qty_1_arrow");
    p_dps_apu_hyd.fuel_qty_2_arrow = device.svg.getElementById("p_dps_apu_hyd_fuel_qty_2_arrow");
    p_dps_apu_hyd.fuel_qty_3_arrow = device.svg.getElementById("p_dps_apu_hyd_fuel_qty_3_arrow");
    
    p_dps_apu_hyd.oil_t_1_arrow = device.svg.getElementById("p_dps_apu_hyd_oil_t_1_arrow");
    p_dps_apu_hyd.oil_t_2_arrow = device.svg.getElementById("p_dps_apu_hyd_oil_t_2_arrow");
    p_dps_apu_hyd.oil_t_3_arrow = device.svg.getElementById("p_dps_apu_hyd_oil_t_3_arrow");
    
    p_dps_apu_hyd.oil_outt_1_arrow = device.svg.getElementById("p_dps_apu_hyd_oil_outt_1_arrow");
    p_dps_apu_hyd.oil_outt_2_arrow = device.svg.getElementById("p_dps_apu_hyd_oil_outt_2_arrow");
    p_dps_apu_hyd.oil_outt_3_arrow = device.svg.getElementById("p_dps_apu_hyd_oil_outt_3_arrow");

    p_dps_apu_hyd.bu_p_1_arrow = device.svg.getElementById("p_dps_apu_hyd_bu_p_1_arrow");
    p_dps_apu_hyd.bu_p_2_arrow = device.svg.getElementById("p_dps_apu_hyd_bu_p_2_arrow");
    p_dps_apu_hyd.bu_p_3_arrow = device.svg.getElementById("p_dps_apu_hyd_bu_p_3_arrow");
    
    p_dps_apu_hyd.h2o_1_arrow = device.svg.getElementById("p_dps_apu_hyd_h2o_1_arrow");
    p_dps_apu_hyd.h2o_2_arrow = device.svg.getElementById("p_dps_apu_hyd_h2o_2_arrow");
    p_dps_apu_hyd.h2o_3_arrow = device.svg.getElementById("p_dps_apu_hyd_h2o_3_arrow");

    p_dps_apu_hyd.bu_egt_1_arrow = device.svg.getElementById("p_dps_apu_hyd_bu_egt_1_arrow");
    p_dps_apu_hyd.bu_egt_2_arrow = device.svg.getElementById("p_dps_apu_hyd_bu_egt_2_arrow");
    p_dps_apu_hyd.bu_egt_3_arrow = device.svg.getElementById("p_dps_apu_hyd_bu_egt_3_arrow");
    
    p_dps_apu_hyd.egt_1_arrow = device.svg.getElementById("p_dps_apu_hyd_egt_1_arrow");
    p_dps_apu_hyd.egt_2_arrow = device.svg.getElementById("p_dps_apu_hyd_egt_2_arrow");
    p_dps_apu_hyd.egt_3_arrow = device.svg.getElementById("p_dps_apu_hyd_egt_3_arrow");

    p_dps_apu_hyd.accum_p_1_arrow = device.svg.getElementById("p_dps_apu_hyd_accum_p_1_arrow");
    p_dps_apu_hyd.accum_p_2_arrow = device.svg.getElementById("p_dps_apu_hyd_accum_p_2_arrow");
    p_dps_apu_hyd.accum_p_3_arrow = device.svg.getElementById("p_dps_apu_hyd_accum_p_3_arrow");

    p_dps_apu_hyd.rsvr_t_1_arrow = device.svg.getElementById("p_dps_apu_hyd_rsvr_t_1_arrow");
    p_dps_apu_hyd.rsvr_t_2_arrow = device.svg.getElementById("p_dps_apu_hyd_rsvr_t_2_arrow");
    p_dps_apu_hyd.rsvr_t_3_arrow = device.svg.getElementById("p_dps_apu_hyd_rsvr_t_3_arrow");
    
    p_dps_apu_hyd.ggbed_t_1_arrow = device.svg.getElementById("p_dps_apu_hyd_ggbed_t_1_arrow");
    p_dps_apu_hyd.ggbed_t_2_arrow = device.svg.getElementById("p_dps_apu_hyd_ggbed_t_2_arrow");
    p_dps_apu_hyd.ggbed_t_3_arrow = device.svg.getElementById("p_dps_apu_hyd_ggbed_t_3_arrow");
    
    
    p_dps_apu_hyd.vent_t_1_arrow = device.svg.getElementById("p_dps_apu_hyd_vent_t_1_arrow");
    p_dps_apu_hyd.vent_t_2_arrow = device.svg.getElementById("p_dps_apu_hyd_vent_t_2_arrow");
    p_dps_apu_hyd.vent_t_3_arrow = device.svg.getElementById("p_dps_apu_hyd_vent_t_3_arrow");
    
    p_dps_apu_hyd.rsvr_qty_1_arrow = device.svg.getElementById("p_dps_apu_hyd_rsvr_qty_1_arrow");
    p_dps_apu_hyd.rsvr_qty_2_arrow = device.svg.getElementById("p_dps_apu_hyd_rsvr_qty_2_arrow");
    p_dps_apu_hyd.rsvr_qty_3_arrow = device.svg.getElementById("p_dps_apu_hyd_rsvr_qty_3_arrow");

    p_dps_apu_hyd.brg_t_1_arrow = device.svg.getElementById("p_dps_apu_hyd_brg_t_1_arrow");
    p_dps_apu_hyd.brg_t_2_arrow = device.svg.getElementById("p_dps_apu_hyd_brg_t_2_arrow");
    p_dps_apu_hyd.brg_t_3_arrow = device.svg.getElementById("p_dps_apu_hyd_brg_t_3_arrow");

    p_dps_apu_hyd.gbx_p_1_arrow = device.svg.getElementById("p_dps_apu_hyd_gbx_p_1_arrow");
    p_dps_apu_hyd.gbx_p_2_arrow = device.svg.getElementById("p_dps_apu_hyd_gbx_p_2_arrow");
    p_dps_apu_hyd.gbx_p_3_arrow = device.svg.getElementById("p_dps_apu_hyd_gbx_p_3_arrow");

    p_dps_apu_hyd.oil_outp_1_arrow = device.svg.getElementById("p_dps_apu_hyd_oil_outp_1_arrow");
    p_dps_apu_hyd.oil_outp_2_arrow = device.svg.getElementById("p_dps_apu_hyd_oil_outp_2_arrow");
    p_dps_apu_hyd.oil_outp_3_arrow = device.svg.getElementById("p_dps_apu_hyd_oil_outp_3_arrow");

    #enableUpdate for indicators

    p_dps_apu_hyd.speed_pct_1_arrow.enableUpdate();
    p_dps_apu_hyd.speed_pct_2_arrow.enableUpdate();
    p_dps_apu_hyd.speed_pct_3_arrow.enableUpdate();
    
    p_dps_apu_hyd.fuel_qty_1_arrow.enableUpdate();
    p_dps_apu_hyd.fuel_qty_2_arrow.enableUpdate();
    p_dps_apu_hyd.fuel_qty_3_arrow.enableUpdate();
    
    p_dps_apu_hyd.oil_t_1_arrow.enableUpdate();
    p_dps_apu_hyd.oil_t_2_arrow.enableUpdate();
    p_dps_apu_hyd.oil_t_3_arrow.enableUpdate();
    
    p_dps_apu_hyd.oil_outt_1_arrow.enableUpdate();
    p_dps_apu_hyd.oil_outt_2_arrow.enableUpdate();
    p_dps_apu_hyd.oil_outt_3_arrow.enableUpdate();

    p_dps_apu_hyd.bu_p_1_arrow.enableUpdate();
    p_dps_apu_hyd.bu_p_2_arrow.enableUpdate();
    p_dps_apu_hyd.bu_p_3_arrow.enableUpdate();
    
    p_dps_apu_hyd.h2o_1_arrow.enableUpdate();
    p_dps_apu_hyd.h2o_2_arrow.enableUpdate();
    p_dps_apu_hyd.h2o_3_arrow.enableUpdate();

    p_dps_apu_hyd.bu_egt_1_arrow.enableUpdate();
    p_dps_apu_hyd.bu_egt_2_arrow.enableUpdate();
    p_dps_apu_hyd.bu_egt_3_arrow.enableUpdate();
    
    p_dps_apu_hyd.egt_1_arrow.enableUpdate();
    p_dps_apu_hyd.egt_2_arrow.enableUpdate();
    p_dps_apu_hyd.egt_3_arrow.enableUpdate();

    p_dps_apu_hyd.accum_p_1_arrow.enableUpdate();
    p_dps_apu_hyd.accum_p_2_arrow.enableUpdate();
    p_dps_apu_hyd.accum_p_3_arrow.enableUpdate();

    p_dps_apu_hyd.rsvr_t_1_arrow.enableUpdate();
    p_dps_apu_hyd.rsvr_t_2_arrow.enableUpdate();
    p_dps_apu_hyd.rsvr_t_3_arrow.enableUpdate();
    
    p_dps_apu_hyd.ggbed_t_1_arrow.enableUpdate();
    p_dps_apu_hyd.ggbed_t_2_arrow.enableUpdate();
    p_dps_apu_hyd.ggbed_t_3_arrow.enableUpdate();
    
    

    p_dps_apu_hyd.vent_t_1_arrow.enableUpdate();
    p_dps_apu_hyd.vent_t_2_arrow.enableUpdate();
    p_dps_apu_hyd.vent_t_3_arrow.enableUpdate();
    
    p_dps_apu_hyd.rsvr_qty_1_arrow.enableUpdate();
    p_dps_apu_hyd.rsvr_qty_2_arrow.enableUpdate();
    p_dps_apu_hyd.rsvr_qty_3_arrow.enableUpdate();

    p_dps_apu_hyd.brg_t_1_arrow.enableUpdate();
    p_dps_apu_hyd.brg_t_2_arrow.enableUpdate();
    p_dps_apu_hyd.brg_t_3_arrow.enableUpdate();

    p_dps_apu_hyd.gbx_p_1_arrow.enableUpdate();
    p_dps_apu_hyd.gbx_p_2_arrow.enableUpdate();
    p_dps_apu_hyd.gbx_p_3_arrow.enableUpdate();

    p_dps_apu_hyd.oil_outp_1_arrow.enableUpdate();
    p_dps_apu_hyd.oil_outp_2_arrow.enableUpdate();
    p_dps_apu_hyd.oil_outp_3_arrow.enableUpdate();

    #Indicators color

    p_dps_apu_hyd.arrow_group = device.svg.getElementById("p_dps_apu_hyd_arrow_group");
    p_dps_apu_hyd.arrow_group.setColor(1, 1, 0);
    
    
    
    
    p_dps_apu_hyd.ondisplay = func
    {
        device.DPS_menu_title.setText("                     APU/HYD");
        device.MEDS_menu_title.setText("      DPS MENU");
    
        var major_mode = getprop("/fdm/jsbsim/systems/dps/major-mode-sm");
	var spec =  getprop("/fdm/jsbsim/systems/dps/spec-sm");
	var spec_string = assemble_spec_string(spec);
    
        var ops_string = major_mode~"1/"~spec_string~"/086";  
    
        device.DPS_menu_ops.setText(ops_string);
    
    # set a few things we don't model explicitly to reasonable values
    
        p_dps_apu_hyd.n2_p_1.setText(sprintf("140"));
        p_dps_apu_hyd.n2_p_2.setText(sprintf("142"));
        p_dps_apu_hyd.n2_p_3.setText(sprintf("141")); 
    
        p_dps_apu_hyd.wsb_n2_p_1.setText(sprintf("2499"));
        p_dps_apu_hyd.wsb_n2_p_2.setText(sprintf("2505"));
        p_dps_apu_hyd.wsb_n2_p_3.setText(sprintf("2501")); 
    
        p_dps_apu_hyd.vlv_at_1.setText(sprintf(" 62"));
        p_dps_apu_hyd.vlv_at_2.setText(sprintf(" 60"));
        p_dps_apu_hyd.vlv_at_3.setText(sprintf(" 61"));
    
        p_dps_apu_hyd.vlv_bt_1.setText(sprintf(" 61"));
        p_dps_apu_hyd.vlv_bt_2.setText(sprintf(" 61"));
        p_dps_apu_hyd.vlv_bt_3.setText(sprintf(" 60"));
    
        p_dps_apu_hyd.tank_t_1.setText(sprintf(" +59"));
        p_dps_apu_hyd.tank_t_2.setText(sprintf(" +60"));
        p_dps_apu_hyd.tank_t_3.setText(sprintf(" +57"));
    
        p_dps_apu_hyd.blr_t_1.setText(sprintf(" +65")); 
        p_dps_apu_hyd.blr_t_2.setText(sprintf(" +64")); 
        p_dps_apu_hyd.blr_t_3.setText(sprintf(" +65"));
    
        p_dps_apu_hyd.reg_p_1.setText(sprintf(" 25")); 
        p_dps_apu_hyd.reg_p_2.setText(sprintf(" 27")); 
        p_dps_apu_hyd.reg_p_3.setText(sprintf(" 26")); 
    
        p_dps_apu_hyd.n2_t_1.setText(sprintf(" 59")); 
        p_dps_apu_hyd.n2_t_2.setText(sprintf(" 61")); 
        p_dps_apu_hyd.n2_t_3.setText(sprintf(" 61")); 
    
    
        p_dps_apu_hyd.rsvr_p_1.setText(sprintf(" 65")); 
        p_dps_apu_hyd.rsvr_p_2.setText(sprintf(" 66")); 
        p_dps_apu_hyd.rsvr_p_3.setText(sprintf(" 66")); 
    
        p_dps_apu_hyd.tk_p_1.setText(sprintf("210")); 
        p_dps_apu_hyd.tk_p_2.setText(sprintf("214")); 
        p_dps_apu_hyd.tk_p_3.setText(sprintf("211")); 
    
        p_dps_apu_hyd.out_p_1.setText(sprintf("210")); 
        p_dps_apu_hyd.out_p_2.setText(sprintf("214")); 
        p_dps_apu_hyd.out_p_3.setText(sprintf("211")); 
    
    }
    
    p_dps_apu_hyd.update = func
    {
    
    #Apu speed

    var apu1_speed = 100.0 * getprop("/fdm/jsbsim/systems/apu/apu/apu-rpm-fraction");
    var apu2_speed = 100.0 * getprop("/fdm/jsbsim/systems/apu/apu[1]/apu-rpm-fraction");
    var apu3_speed = 100.0 * getprop("/fdm/jsbsim/systems/apu/apu[2]/apu-rpm-fraction");

        p_dps_apu_hyd.speed_pct_1.setText(sprintf("%3.0f", apu1_speed));
        p_dps_apu_hyd.speed_pct_2.setText(sprintf("%3.0f", apu2_speed));
        p_dps_apu_hyd.speed_pct_3.setText(sprintf("%3.0f", apu3_speed));


    #Apu Fuel quantity

    var apu1_fuel = getprop("/consumables/fuel/tank[14]/level-lbs")/3.5;
    var apu2_fuel = getprop("/consumables/fuel/tank[15]/level-lbs")/3.5;
    var apu3_fuel = getprop("/consumables/fuel/tank[16]/level-lbs")/3.5;
    
    
        p_dps_apu_hyd.fuel_qty_1.setText(sprintf("%3.0f", apu1_fuel));
        p_dps_apu_hyd.fuel_qty_2.setText(sprintf("%3.0f", apu2_fuel));
        p_dps_apu_hyd.fuel_qty_3.setText(sprintf("%3.0f", apu3_fuel));


    
        p_dps_apu_hyd.vlv_a_1.setText(sprintf("%s", valve_status_to_string(getprop("/fdm/jsbsim/systems/apu/apu/fuel-valve-status"))));
        p_dps_apu_hyd.vlv_a_2.setText(sprintf("%s", valve_status_to_string(getprop("/fdm/jsbsim/systems/apu/apu[1]/fuel-valve-status"))));
        p_dps_apu_hyd.vlv_a_3.setText(sprintf("%s", valve_status_to_string(getprop("/fdm/jsbsim/systems/apu/apu[2]/fuel-valve-status"))));
    
        p_dps_apu_hyd.vlv_b_1.setText(sprintf("%s", valve_status_to_string(getprop("/fdm/jsbsim/systems/apu/apu/fuel-valve-status"))));
        p_dps_apu_hyd.vlv_b_2.setText(sprintf("%s", valve_status_to_string(getprop("/fdm/jsbsim/systems/apu/apu[1]/fuel-valve-status"))));
        p_dps_apu_hyd.vlv_b_3.setText(sprintf("%s", valve_status_to_string(getprop("/fdm/jsbsim/systems/apu/apu[2]/fuel-valve-status"))));
    


    #APU oil temp

	var oil_T1 = K_to_F(getprop("/fdm/jsbsim/systems/apu/apu/oil-in-T-K"));
    var oil_out_T1 = K_to_F(getprop("/fdm/jsbsim/systems/thermal-distribution/apu1-temperature-K"));
	if (math.abs(getprop("/fdm/jsbsim/systems/apu/apu/lube-line-heater-status")) == 1)
		{
        if (oil_T1 < 57.0) {oil_T1 = 57.0;}
        if (oil_out_T1 < 57.0) {oil_out_T1 = 57.0;}
        }
    

	var oil_T2 = K_to_F(getprop("/fdm/jsbsim/systems/apu/apu[1]/oil-in-T-K"));
    var oil_out_T2 = K_to_F(getprop("/fdm/jsbsim/systems/thermal-distribution/apu2-temperature-K"));
	if (math.abs(getprop("/fdm/jsbsim/systems/apu/apu[1]/lube-line-heater-status")) == 1)
		{
        if (oil_T2 < 58.0) {oil_T2 = 58.0;}
        if (oil_out_T2 < 58.0) {oil_out_T2 = 58.0;}
        }

	var oil_T3 = K_to_F(getprop("/fdm/jsbsim/systems/apu/apu[2]/oil-in-T-K"));
    var oil_out_T3 = K_to_F(getprop("/fdm/jsbsim/systems/thermal-distribution/apu3-temperature-K"));
	if (math.abs(getprop("/fdm/jsbsim/systems/apu/apu[2]/lube-line-heater-status")) == 1)
		{
        if (oil_T3 < 60.0) {oil_T3 = 60.0;}
        if (oil_out_T3 < 60.0) {oil_out_T3 = 60.0;}
        }

        p_dps_apu_hyd.oil_t_1.setText(sprintf("%3.0f", math.max(oil_T1, 0)));
        p_dps_apu_hyd.oil_t_2.setText(sprintf("%3.0f", math.max(oil_T2, 0)));
        p_dps_apu_hyd.oil_t_3.setText(sprintf("%3.0f", math.max(oil_T3, 0)));
    
        p_dps_apu_hyd.oil_outt_1.setText(sprintf("%3.0f", math.max(oil_out_T1, 0)));
        p_dps_apu_hyd.oil_outt_2.setText(sprintf("%3.0f", math.max(oil_out_T2, 0)));
        p_dps_apu_hyd.oil_outt_3.setText(sprintf("%3.0f", math.max(oil_out_T3, 0)));


    #Hyd pressure

        var hyd1_p = getprop("/fdm/jsbsim/systems/apu/apu/hyd-pressure-psia");
        var hyd2_p = getprop("/fdm/jsbsim/systems/apu/apu[1]/hyd-pressure-psia");
        var hyd3_p = getprop("/fdm/jsbsim/systems/apu/apu[2]/hyd-pressure-psia");
    
        p_dps_apu_hyd.bu_p_1.setText(sprintf("%4.0f", hyd1_p));
        p_dps_apu_hyd.bu_p_2.setText(sprintf("%4.0f", hyd2_p));
        p_dps_apu_hyd.bu_p_3.setText(sprintf("%4.0f", hyd3_p));

        p_dps_apu_hyd.accum_p_1.setText(sprintf("%4.0f", hyd1_p));
        p_dps_apu_hyd.accum_p_2.setText(sprintf("%4.0f", hyd2_p));
        p_dps_apu_hyd.accum_p_3.setText(sprintf("%4.0f", hyd3_p));


    #Water boilers h2o

        var h2o_1 = getprop("/fdm/jsbsim/propulsion/tank[20]/contents-lbs")/1.42;
        var h2o_2 = getprop("/fdm/jsbsim/propulsion/tank[21]/contents-lbs")/1.42;
        var h2o_3 = getprop("/fdm/jsbsim/propulsion/tank[22]/contents-lbs")/1.42;
    
        p_dps_apu_hyd.h2o_1.setText(sprintf("%3.0f", h2o_1)); 
        p_dps_apu_hyd.h2o_2.setText(sprintf("%3.0f", h2o_2)); 
        p_dps_apu_hyd.h2o_3.setText(sprintf("%3.0f", h2o_3));  


    
        p_dps_apu_hyd.cntlr_1.setText(sprintf("%s", wsb_ctrl_to_string(getprop("/fdm/jsbsim/systems/apu/apu/boiler-power-status"))));
        p_dps_apu_hyd.cntlr_2.setText(sprintf("%s", wsb_ctrl_to_string(getprop("/fdm/jsbsim/systems/apu/apu[1]/boiler-power-status"))));
        p_dps_apu_hyd.cntlr_3.setText(sprintf("%s", wsb_ctrl_to_string(getprop("/fdm/jsbsim/systems/apu/apu[2]/boiler-power-status"))));


    #APU EGT (mini 0°F)

        var apu1_egt = K_to_F(getprop("/fdm/jsbsim/systems/apu/apu/egt-K"));
        var apu2_egt = K_to_F(getprop("/fdm/jsbsim/systems/apu/apu[1]/egt-K"));
        var apu3_egt = K_to_F(getprop("/fdm/jsbsim/systems/apu/apu[2]/egt-K"));

        apu1_egt = math.max(apu1_egt, 0);
        apu2_egt = math.max(apu2_egt, 0);
        apu3_egt = math.max(apu3_egt, 0); 
    
        p_dps_apu_hyd.bu_egt_1.setText(sprintf("%4.0f", apu1_egt+3.0));
        p_dps_apu_hyd.bu_egt_2.setText(sprintf("%4.0f", apu2_egt+1.0));
        p_dps_apu_hyd.bu_egt_3.setText(sprintf("%4.0f", apu3_egt+4.0));
    
        p_dps_apu_hyd.egt_1.setText(sprintf("%4.0f", apu1_egt+1.0));
        p_dps_apu_hyd.egt_2.setText(sprintf("%4.0f", apu2_egt+1.0));
        p_dps_apu_hyd.egt_3.setText(sprintf("%4.0f", apu3_egt));
    
    #Hyd/GBX temp (mini 0°F)
        
        var rsvr_t1 = math.max(K_to_F(getprop("/fdm/jsbsim/systems/apu/apu/hyd-rsvr-T-K")), 0);
        var rsvr_t2 = math.max(K_to_F(getprop("/fdm/jsbsim/systems/apu/apu[1]/hyd-rsvr-T-K")), 0);
        var rsvr_t3 = math.max(K_to_F(getprop("/fdm/jsbsim/systems/apu/apu[2]/hyd-rsvr-T-K")), 0);

        p_dps_apu_hyd.rsvr_t_1.setText(sprintf("%3.0f", rsvr_t1 + 1)); 
        p_dps_apu_hyd.rsvr_t_2.setText(sprintf("%3.0f", rsvr_t2)); 
        p_dps_apu_hyd.rsvr_t_3.setText(sprintf("%3.0f", rsvr_t3)); 

    #GG bed temp
    
        var ggbed_T1 = K_to_F(getprop("/fdm/jsbsim/systems/apu/apu/gg-bed-T-K"));
        var ggbed_T2 = K_to_F(getprop("/fdm/jsbsim/systems/apu/apu[1]/gg-bed-T-K")) - 1;
        var ggbed_T3 = K_to_F(getprop("/fdm/jsbsim/systems/apu/apu[2]/gg-bed-T-K")) + 3;

        ggbed_T1 = SpaceShuttle.clamp(ggbed_T1, 0, 500);
        ggbed_T2 = SpaceShuttle.clamp(ggbed_T2, 0, 500);
        ggbed_T3 = SpaceShuttle.clamp(ggbed_T3, 0, 500);
       
        p_dps_apu_hyd.ggbed_t_1.setText(sprintf("%3.0f", ggbed_T1));
        p_dps_apu_hyd.ggbed_t_2.setText(sprintf("%3.0f", ggbed_T2));
        p_dps_apu_hyd.ggbed_t_3.setText(sprintf("%3.0f", ggbed_T3));
    
    #WB vent temp ( heater)

        var vent_t_1 = math.max(K_to_F(getprop("/fdm/jsbsim/systems/apu/apu/steam-vent-T-K"))-3.0, 122);
        var vent_t_2 = math.max(K_to_F(getprop("/fdm/jsbsim/systems/apu/apu[1]/steam-vent-T-K")), 122);
        var vent_t_3 = math.max(K_to_F(getprop("/fdm/jsbsim/systems/apu/apu[2]/steam-vent-T-K"))+1.0, 122);

    
        p_dps_apu_hyd.vent_t_1.setText(sprintf("%+4.0f", vent_t_1)); 
        p_dps_apu_hyd.vent_t_2.setText(sprintf("%+4.0f", vent_t_2)); 
        p_dps_apu_hyd.vent_t_3.setText(sprintf("%+4.0f", vent_t_3)); 


    #Pump and Valves stay above 0° ( no clamp)
    
        p_dps_apu_hyd.pmp_t_1.setText(sprintf("%3.0f", K_to_F(getprop("/fdm/jsbsim/systems/apu/apu/fuel-pump-T-K")-1.0))); 
        p_dps_apu_hyd.pmp_t_2.setText(sprintf("%3.0f", K_to_F(getprop("/fdm/jsbsim/systems/apu/apu[1]/fuel-pump-T-K")+3.0))); 
        p_dps_apu_hyd.pmp_t_3.setText(sprintf("%3.0f", K_to_F(getprop("/fdm/jsbsim/systems/apu/apu[2]/fuel-pump-T-K")+2.0))); 
    
        p_dps_apu_hyd.vlv_t_1.setText(sprintf("%3.0f", K_to_F(getprop("/fdm/jsbsim/systems/apu/apu/fuel-pump-T-K")+2.0))); 
        p_dps_apu_hyd.vlv_t_2.setText(sprintf("%3.0f", K_to_F(getprop("/fdm/jsbsim/systems/apu/apu[1]/fuel-pump-T-K")-1.0))); 
        p_dps_apu_hyd.vlv_t_3.setText(sprintf("%3.0f", K_to_F(getprop("/fdm/jsbsim/systems/apu/apu[2]/fuel-pump-T-K")-1.0)));


    #Oil out P

        var oil_out_p1 = getprop("/fdm/jsbsim/systems/apu/apu/oil-p-psia");
        var oil_out_p2 = getprop("/fdm/jsbsim/systems/apu/apu[1]/oil-p-psia");
        var oil_out_p3 = getprop("/fdm/jsbsim/systems/apu/apu[2]/oil-p-psia");

        p_dps_apu_hyd.oil_outp_1.setText(sprintf("%3.0f", oil_out_p1));
        p_dps_apu_hyd.oil_outp_2.setText(sprintf("%3.0f", oil_out_p2));
        p_dps_apu_hyd.oil_outp_3.setText(sprintf("%3.0f", oil_out_p3));
    
        p_dps_apu_hyd.gbx_p_1.setText(sprintf("%3.0f", oil_out_p1-1.0));
        p_dps_apu_hyd.gbx_p_2.setText(sprintf("%3.0f", oil_out_p2-2.0));
        p_dps_apu_hyd.gbx_p_3.setText(sprintf("%3.0f", oil_out_p3-1.0));


    
        p_dps_apu_hyd.byp_vlv_1.setText(sprintf("%s", wsb_vlv_to_string(getprop("/fdm/jsbsim/systems/thermal-distribution/spray-boiler-1-switch"))));
        p_dps_apu_hyd.byp_vlv_2.setText(sprintf("%s", wsb_vlv_to_string(getprop("/fdm/jsbsim/systems/thermal-distribution/spray-boiler-2-switch"))));
        p_dps_apu_hyd.byp_vlv_3.setText(sprintf("%s", wsb_vlv_to_string(getprop("/fdm/jsbsim/systems/thermal-distribution/spray-boiler-3-switch"))));
    
        p_dps_apu_hyd.brg_t_1.setText(sprintf("%3.0f", rsvr_t1 +3.0));
        p_dps_apu_hyd.brg_t_2.setText(sprintf("%3.0f", rsvr_t2 + 4.0));
        p_dps_apu_hyd.brg_t_3.setText(sprintf("%3.0f", rsvr_t3 + 1.0));
    
	var mission_time = getprop("/fdm/jsbsim/systems/timer/delta-MET") + getprop("/sim/time/elapsed-sec");
	var qty = (1.0 - 0.4 * (mission_time/(86400.0 * 12.0))) * 100.0;
	if (qty < 3.0) {qty = 3.0;}

    var hyd_rsvr_qty = int(qty);


        p_dps_apu_hyd.rsvr_qty_1.setText(sprintf("%3d", hyd_rsvr_qty + 1));  
        p_dps_apu_hyd.rsvr_qty_2.setText(sprintf("%3d", hyd_rsvr_qty)); 
        p_dps_apu_hyd.rsvr_qty_3.setText(sprintf("%3d", hyd_rsvr_qty + 3)); 



    #SM realistic option with indicators ( as APU/HYD not used in Orbit outside OPS 8, basic indicators compared to sum sys 2 for BFS)

	if (SpaceShuttle.sm_simulation_detail_level == 1)
		{
        
        p_dps_apu_hyd.arrow_group.setVisible(1);

        #Apu speed

        if (apu1_speed == 0) {p_dps_apu_hyd.speed_pct_1_arrow.updateText("L");}
        else {p_dps_apu_hyd.speed_pct_1_arrow.updateText("");}

        if (apu2_speed == 0) {p_dps_apu_hyd.speed_pct_2_arrow.updateText("L");}
        else {p_dps_apu_hyd.speed_pct_2_arrow.updateText("");}

        if (apu3_speed == 0) {p_dps_apu_hyd.speed_pct_3_arrow.updateText("L");}
        else {p_dps_apu_hyd.speed_pct_3_arrow.updateText("");}


        #APU fuel qty

        if (apu1_fuel > 99.4) {p_dps_apu_hyd.fuel_qty_1_arrow.updateText("H");}
        else {p_dps_apu_hyd.fuel_qty_1_arrow.updateText("");}

        if (apu2_fuel > 99.4) {p_dps_apu_hyd.fuel_qty_2_arrow.updateText("H");}
        else {p_dps_apu_hyd.fuel_qty_2_arrow.updateText("");}

        if (apu3_fuel > 99.4) {p_dps_apu_hyd.fuel_qty_3_arrow.updateText("H");}
        else {p_dps_apu_hyd.fuel_qty_3_arrow.updateText("");}


        #Apu oil temp in/out (L)

        if (oil_T1 == 0) {p_dps_apu_hyd.oil_t_1_arrow.updateText("L");}
        else {p_dps_apu_hyd.oil_t_1_arrow.updateText("");}

        if (oil_T2 == 0) {p_dps_apu_hyd.oil_t_2_arrow.updateText("L");}
        else {p_dps_apu_hyd.oil_t_2_arrow.updateText("");}

        if (oil_T3 == 0) {p_dps_apu_hyd.oil_t_3_arrow.updateText("L");}
        else {p_dps_apu_hyd.oil_t_3_arrow.updateText("");}

        if (oil_out_T1 == 0) {p_dps_apu_hyd.oil_outt_1_arrow.updateText("L");}
        else {p_dps_apu_hyd.oil_outt_1_arrow.updateText("");}

        if (oil_out_T2 == 0) {p_dps_apu_hyd.oil_outt_2_arrow.updateText("L");}
        else {p_dps_apu_hyd.oil_outt_2_arrow.updateText("");}

        if (oil_out_T3 == 0) {p_dps_apu_hyd.oil_outt_3_arrow.updateText("L");}
        else {p_dps_apu_hyd.oil_outt_3_arrow.updateText("");}


        #Hyd pressure

        if (hyd1_p < 10) 
            {
            p_dps_apu_hyd.bu_p_1_arrow.updateText("L");
            p_dps_apu_hyd.accum_p_1_arrow.updateText("L");
            }
        else if ((hyd1_p > 10) and (hyd1_p < 1930))
            {
            p_dps_apu_hyd.bu_p_1_arrow.updateText("↓");
            p_dps_apu_hyd.accum_p_1_arrow.updateText("↓");
            }
        else
            {
            p_dps_apu_hyd.bu_p_1_arrow.updateText("");
            p_dps_apu_hyd.accum_p_1_arrow.updateText("");
            }

        if (hyd2_p < 10) 
            {
            p_dps_apu_hyd.bu_p_2_arrow.updateText("L");
            p_dps_apu_hyd.accum_p_2_arrow.updateText("L");
            }
        else if ((hyd2_p > 10) and (hyd2_p < 1930))
            {
            p_dps_apu_hyd.bu_p_2_arrow.updateText("↓");
            p_dps_apu_hyd.accum_p_2_arrow.updateText("↓");
            }
        else
            {
            p_dps_apu_hyd.bu_p_2_arrow.updateText("");
            p_dps_apu_hyd.accum_p_2_arrow.updateText("");
            }

        if (hyd3_p < 10) 
            {
            p_dps_apu_hyd.bu_p_3_arrow.updateText("L");
            p_dps_apu_hyd.accum_p_3_arrow.updateText("L");
            }
        else if ((hyd3_p > 10) and (hyd3_p < 1930))
            {
            p_dps_apu_hyd.bu_p_3_arrow.updateText("↓");
            p_dps_apu_hyd.accum_p_3_arrow.updateText("↓");
            }
        else
            {
            p_dps_apu_hyd.bu_p_3_arrow.updateText("");
            p_dps_apu_hyd.accum_p_3_arrow.updateText("");
            }

        #WB h2o

        if (h2o_1 > 99.4) {p_dps_apu_hyd.h2o_1_arrow.updateText("H");}
        else {p_dps_apu_hyd.h2o_1_arrow.updateText("");}

        if (h2o_2 > 99.4) {p_dps_apu_hyd.h2o_2_arrow.updateText("H");}
        else {p_dps_apu_hyd.h2o_2_arrow.updateText("");}

        if (h2o_3 > 99.4) {p_dps_apu_hyd.h2o_3_arrow.updateText("H");}
        else {p_dps_apu_hyd.h2o_3_arrow.updateText("");}


        #APU EGT

        if (apu1_egt == 0)
            {
            p_dps_apu_hyd.bu_egt_1_arrow.updateText("L");
            p_dps_apu_hyd.egt_1_arrow.updateText("L");
            }
        else
            {
            p_dps_apu_hyd.bu_egt_1_arrow.updateText("");
            p_dps_apu_hyd.egt_1_arrow.updateText("");
            }
        
        if (apu2_egt == 0)
            {
            p_dps_apu_hyd.bu_egt_2_arrow.updateText("L");
            p_dps_apu_hyd.egt_2_arrow.updateText("L");
            }
        else
            {
            p_dps_apu_hyd.bu_egt_2_arrow.updateText("");
            p_dps_apu_hyd.egt_2_arrow.updateText("");
            }

        if (apu3_egt == 0)
            {
            p_dps_apu_hyd.bu_egt_3_arrow.updateText("L");
            p_dps_apu_hyd.egt_3_arrow.updateText("L");
            }
        else
            {
            p_dps_apu_hyd.bu_egt_3_arrow.updateText("");
            p_dps_apu_hyd.egt_3_arrow.updateText("");
            }


        #Hyd rsvrt and GBX temp

        if (rsvr_t1 == 0) 
            {
            p_dps_apu_hyd.rsvr_t_1_arrow.updateText("L");
            p_dps_apu_hyd.brg_t_1_arrow.updateText("L");
            }
        else
            {
            p_dps_apu_hyd.rsvr_t_1_arrow.updateText("");
            p_dps_apu_hyd.brg_t_1_arrow.updateText("");
            }

        if (rsvr_t2 == 0) 
            {
            p_dps_apu_hyd.rsvr_t_2_arrow.updateText("L");
            p_dps_apu_hyd.brg_t_2_arrow.updateText("L");
            }
        else
            {
            p_dps_apu_hyd.rsvr_t_2_arrow.updateText("");
            p_dps_apu_hyd.brg_t_2_arrow.updateText("");
            }

        if (rsvr_t3 == 0) 
            {
            p_dps_apu_hyd.rsvr_t_3_arrow.updateText("L");
            p_dps_apu_hyd.brg_t_3_arrow.updateText("L");
            }
        else
            {
            p_dps_apu_hyd.rsvr_t_3_arrow.updateText("");
            p_dps_apu_hyd.brg_t_3_arrow.updateText("");
            }

        
        #GG bed Temp (↓ below 100° for PASS)

        if (ggbed_T1 == 0) {p_dps_apu_hyd.ggbed_t_1_arrow.updateText("L");}
        else if ((ggbed_T1 > 0) and (ggbed_T1 < 100)) {p_dps_apu_hyd.ggbed_t_1_arrow.updateText("↓");}
        else {p_dps_apu_hyd.ggbed_t_1_arrow.updateText("");}

        if (ggbed_T2 == 0) {p_dps_apu_hyd.ggbed_t_2_arrow.updateText("L");}
        else if ((ggbed_T2 > 0) and (ggbed_T2 < 100)) {p_dps_apu_hyd.ggbed_t_2_arrow.updateText("↓");}
        else {p_dps_apu_hyd.ggbed_t_2_arrow.updateText("");}

        if (ggbed_T3 == 0) {p_dps_apu_hyd.ggbed_t_3_arrow.updateText("L");}
        else if ((ggbed_T3 > 0) and (ggbed_T3 < 100)) {p_dps_apu_hyd.ggbed_t_3_arrow.updateText("↓");}
        else {p_dps_apu_hyd.ggbed_t_3_arrow.updateText("");}

        #W/B vent heaters

        if (vent_t_1 == 122) {p_dps_apu_hyd.vent_t_1_arrow.updateText("L");}
        else {p_dps_apu_hyd.vent_t_1_arrow.updateText("");}

        if (vent_t_2 == 122) {p_dps_apu_hyd.vent_t_2_arrow.updateText("L");}
        else {p_dps_apu_hyd.vent_t_2_arrow.updateText("");}

        if (vent_t_3 == 122) {p_dps_apu_hyd.vent_t_3_arrow.updateText("L");}
        else {p_dps_apu_hyd.vent_t_3_arrow.updateText("");}


        #Oil out // GBX P (↓ below 25)

        if (oil_out_p1 < 25) 
            {
            p_dps_apu_hyd.oil_outp_1_arrow.updateText("↓");
            p_dps_apu_hyd.gbx_p_1_arrow.updateText("↓");
            }
        else
            {
            p_dps_apu_hyd.oil_outp_1_arrow.updateText("");
            p_dps_apu_hyd.gbx_p_1_arrow.updateText("");
            }

        if (oil_out_p2 < 25) 
            {
            p_dps_apu_hyd.oil_outp_2_arrow.updateText("↓");
            p_dps_apu_hyd.gbx_p_2_arrow.updateText("↓");
            }
        else
            {
            p_dps_apu_hyd.oil_outp_2_arrow.updateText("");
            p_dps_apu_hyd.gbx_p_2_arrow.updateText("");
            }

        if (oil_out_p3 < 25) 
            {
            p_dps_apu_hyd.oil_outp_3_arrow.updateText("↓");
            p_dps_apu_hyd.gbx_p_3_arrow.updateText("↓");
            }
        else
            {
            p_dps_apu_hyd.oil_outp_3_arrow.updateText("");
            p_dps_apu_hyd.gbx_p_3_arrow.updateText("");
            }


        #Hyd quantity (between 40 and 90 ↓↑)

        if (hyd_rsvr_qty > 90) 
            {
            p_dps_apu_hyd.rsvr_qty_1_arrow.updateText("↑");
            p_dps_apu_hyd.rsvr_qty_2_arrow.updateText("↑");
            p_dps_apu_hyd.rsvr_qty_3_arrow.updateText("↑");
            }
        else
            {
            p_dps_apu_hyd.rsvr_qty_1_arrow.updateText("");
            p_dps_apu_hyd.rsvr_qty_2_arrow.updateText("");
            p_dps_apu_hyd.rsvr_qty_3_arrow.updateText("");
            }
        
        }

    else {p_dps_apu_hyd.arrow_group.setVisible(0);}


        device.update_common_DPS();
    
    
    }
    
    
    
    return p_dps_apu_hyd;
}
