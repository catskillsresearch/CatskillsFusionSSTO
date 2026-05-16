import math
from typing import Any

import cadquery as cq

# Shared pose for reactor stack instances in ``orbitron_lab.yaml`` (CadQuery → world).
# Pivot Z matches ``arcjet_test_stand_cad.ENGINE_MOUNT_TOP_Z`` (mount plate on load cells).
try:
    from arcjet_test_stand_cad import ENGINE_MOUNT_PIVOT_Z, ENGINE_MOUNT_TOP_Z

    _ENGINE_PIVOT_Z = ENGINE_MOUNT_PIVOT_Z
    _FUSION_STACK_Z = 0.75 + (ENGINE_MOUNT_PIVOT_Z - 0.15)
    _ENGINE_MOUNT_TOP_Z = float(ENGINE_MOUNT_TOP_Z)
except ImportError:
    _ENGINE_PIVOT_Z = 0.32
    _FUSION_STACK_Z = 0.92
    _ENGINE_MOUNT_TOP_Z = 0.35

# H₂ / B₂H₆ trunk waypoints must stay at or above this Z over the thrust-sled deck /
# ``Engine_Mount_Frame`` (B₂H₆ path previously used z≈0.32 and clipped through the frame).
_SERVICE_ROUTING_DECK_CLEAR_Z = _ENGINE_MOUNT_TOP_Z + 0.23

# Outlet Z above tank roof for connector routing: must match ``lab_fuel_feed_valve``
# in arcjet_test_stand_cad.py (base extrude 0.04 + stem 0.055).
_LAB_TANK_VALVE_OUTLET_DZ = 0.095

_FUSION_STACK_TRANSFORMS: list[dict[str, object]] = [
    {"op": "translate", "xyz": [0.0, 0.0, _FUSION_STACK_Z]},
    {"op": "rotate_y_about_point", "pivot": [0.0, 0.0, _ENGINE_PIVOT_Z], "angle_deg": 90.0},
]

# Solenoid OD service layout after fusion-stack pose: (anchor_key, x_offset_m, phi_deg, inset_m, boss_r, boss_h).
# φ = 0° → +Y tank-farm normal; φ increases toward +Z “crown”. Shifts along +X pick distinct axial stations on the coil.
_MAGNET_SHELL_SERVICE_TABLE: tuple[tuple[str, float, float, float, float, float], ...] = (
    ("reactor_magnet_fuel_ch4_in", -0.26, -9.0, 0.018, 0.026, 0.038),
    ("reactor_magnet_cryo_ch4_tap", -0.18, 34.0, 0.018, 0.028, 0.044),
    ("reactor_magnet_hv_feed", 0.05, 52.0, 0.018, 0.026, 0.050),
)


def _magnet_od_inset_point(
    bb,
    *,
    x_offset: float,
    phi_deg: float,
    inset_m: float,
) -> tuple[float, float, float, float, float]:
    """Point on the solenoid OD inset slightly along −n̂, plus outward normal (0, ny, nz) in YZ.

    The posed ``Magnet`` is a long cylinder approx. on axis ‖ **+X**; OD in the YZ plane is a
    circle centred on the bbox YZ midline. Axis-aligned bbox “+Y face” points are **not** on
    that circle — hoses miss the mesh. See ``Magnet_Service_Bosses`` stubs for the visible story.
    """
    cx = (bb.xmin + bb.xmax) * 0.5
    cy_ax = (bb.ymin + bb.ymax) * 0.5
    cz_ax = (bb.zmin + bb.zmax) * 0.5
    r_od = (bb.ymax - bb.ymin) * 0.5
    phi = math.radians(phi_deg)
    ny = math.cos(phi)
    nz = math.sin(phi)
    y0 = cy_ax + r_od * ny
    z0 = cz_ax + r_od * nz
    x0 = cx + x_offset
    return (
        x0,
        y0 - inset_m * ny,
        z0 - inset_m * nz,
        ny,
        nz,
    )


def _feedthrough_boss_stem(
    point: tuple[float, float, float],
    ny: float,
    nz: float,
    radius: float,
    height: float,
) -> cq.Workplane:
    """Short cylinder extruded **outward** from the shell (boss visible beyond tube cap)."""
    p = cq.Vector(point)
    n = cq.Vector(0.0, float(ny), float(nz)).normalized()
    zdir = n
    xdir = zdir.cross(cq.Vector(1.0, 0.0, 0.0))
    if xdir.Length < 1e-4:
        xdir = zdir.cross(cq.Vector(0.0, 1.0, 0.0))
    xdir = xdir.normalized()
    pl = cq.Plane(origin=p, xDir=xdir, normal=zdir)
    return cq.Workplane(inPlane=pl).circle(float(radius)).extrude(float(height))


def build_magnet_feedthrough_bosses() -> cq.Workplane:
    """World-space weld flanges / feedthrough bosses co-located with ``magnet_shell_connector_anchors``."""
    lab = LabInfrastructure()
    bb = lab._magnet_world_bbox()
    out: cq.Workplane | None = None
    for _key, xo, phi, ins, br, bh in _MAGNET_SHELL_SERVICE_TABLE:
        x, y, z, ny, nz = _magnet_od_inset_point(bb, x_offset=xo, phi_deg=phi, inset_m=ins)
        stem = _feedthrough_boss_stem((x, y, z), ny, nz, br, bh)
        out = stem if out is None else out.union(stem)
    if out is None:
        return cq.Workplane("XY")
    return out


def _hv_seg_along_x(y: float, z: float, x0: float, x1: float, radius: float = 0.02) -> cq.Workplane:
    lo, hi = (x0, x1) if x0 < x1 else (x1, x0)
    length = hi - lo
    if length < 1e-4:
        return cq.Workplane("XY")
    cx = (lo + hi) * 0.5
    return cq.Workplane("YZ").cylinder(length, radius).translate((cx, y, z))


def _hv_seg_along_y(x: float, z: float, y0: float, y1: float, radius: float = 0.02) -> cq.Workplane:
    lo, hi = (y0, y1) if y0 < y1 else (y1, y0)
    length = hi - lo
    if length < 1e-4:
        return cq.Workplane("XY")
    cy = (lo + hi) * 0.5
    return cq.Workplane("XZ").cylinder(length, radius).translate((x, cy, z))


def _hv_seg_along_z(x: float, y: float, z0: float, z1: float, radius: float = 0.02) -> cq.Workplane:
    lo, hi = (z0, z1) if z0 < z1 else (z1, z0)
    length = hi - lo
    if length < 1e-4:
        return cq.Workplane("XY")
    cz = (lo + hi) * 0.5
    return cq.Workplane("XY").cylinder(length, radius).translate((x, y, cz))


def fusion_exhaust_outlet_ring(
    outer_r: float = 0.082,
    inner_r: float = 0.055,
    thickness: float = 0.016,
) -> cq.Workplane:
    """Thin annular flange at the anode / bay exhaust plane (coarse commissioning mesh)."""
    disc = cq.Workplane("XY").circle(outer_r).extrude(thickness)
    bore = cq.Workplane("XY").circle(inner_r).extrude(thickness + 0.01)
    return disc.cut(bore)


def orbitron_anode_pressure_shell(r: float = 0.05, h: float = 2.0) -> cq.Workplane:
    """Thin-wall niobium shell with **asymmetric ends**: −Z = compressor / inlet clamp flange

    (+Z = exhaust boss toward ``fusion_exhaust_outlet_ring``), plus shallow OD jacket rings.

    Local **+Z** is the hot-gas outlet end after ``orbitron_lab.yaml`` fusion-stack rotation.
    """
    inner_r = r - 0.005  # legacy bore: hole diameter ``r*2 - 0.01``
    z_lo = -h * 0.5
    z_hi = h * 0.5

    outer = cq.Workplane("XY").cylinder(h, r)
    inner_bore = cq.Workplane("XY").cylinder(h + 0.08, inner_r)
    tube = outer.cut(inner_bore)

    # Inlet (−Z): wide bolted flange (reads as turbofan / duct mate, not a hose barb).
    flange_od = 0.10
    flange_t = 0.026
    bolt_circle_r = 0.068
    bolt_d = 0.011
    flange = cq.Workplane("XY").workplane(offset=z_lo - flange_t).circle(flange_od * 0.5).extrude(flange_t)
    flange = flange.faces(">Z").workplane().circle(inner_r + 0.0005).cutThruAll()

    bolts: cq.Workplane | None = None
    for k in range(6):
        ang = (math.tau / 6.0) * k
        bx, by = bolt_circle_r * math.cos(ang), bolt_circle_r * math.sin(ang)
        seg = (
            cq.Workplane("XY")
            .transformed(offset=(bx, by, z_lo - flange_t * 0.5))
            .circle(bolt_d * 0.5)
            .extrude(flange_t + 0.04)
        )
        bolts = seg if bolts is None else bolts.union(seg)
    flange = flange.cut(bolts)

    # Outlet (+Z): shorter, heavier lip (exhaust hardware narrative).
    boss_r = 0.075
    boss_t = 0.024
    boss = cq.Workplane("XY").workplane(offset=z_hi).circle(boss_r).extrude(boss_t)
    boss = boss.faces(">Z").workplane().circle(inner_r + 0.0005).cutThruAll()

    tube = tube.union(flange).union(boss)

    def _od_ring(zc: float, dro: float, rz: float) -> cq.Workplane:
        ro = r + dro
        ring_o = cq.Workplane("XY").transformed(offset=(0, 0, zc - rz * 0.5)).circle(ro).extrude(rz)
        ring_i = (
            cq.Workplane("XY")
            .transformed(offset=(0, 0, zc - rz * 0.5 - 0.001))
            .circle(r - 0.001)
            .extrude(rz + 0.002)
        )
        return ring_o.cut(ring_i)

    for i in range(5):
        zc = z_lo + 0.32 + i * 0.34
        if zc > z_hi - 0.18:
            break
        tube = tube.union(_od_ring(zc, 0.0045, 0.014))

    return tube


class IntegratedOrbitronTube:
    """The 3.5 MW p-B11 Reactor Core"""
    def build(self):
        r = 0.05
        h = 2.0
        anode = orbitron_anode_pressure_shell(r=r, h=h)
        dec = cq.Workplane("XY").cylinder(h, r-0.005).faces(">Z").workplane().hole((r-0.005)*2 - 0.002)
        cathode = cq.Workplane("XY").cylinder(h + 0.6, 0.005)
        
        ins = cq.Workplane("XY").cylinder(0.3, 0.03)
        for i in range(5):
            ins = ins.union(cq.Workplane("XY").workplane(offset=-0.1 + i*0.05).cylinder(0.02, 0.045))
        ins_top = ins.translate((0, 0, h/2 + 0.15))
        ins_bot = ins.translate((0, 0, -h/2 - 0.15))
        
        mag = cq.Workplane("XY").cylinder(h-0.5, 0.15).faces(">Z").workplane().hole(r*2 + 0.01)
        
        # NBI sticks out of the side
        nbi = cq.Workplane("XZ").cylinder(0.2, 0.04).translate((0, 0.1, 0))
        nbi_flange = cq.Workplane("XZ").cylinder(0.05, 0.06).translate((0, 0.2, 0))
        
        return anode, dec, cathode, ins_top.union(ins_bot), mag, nbi.union(nbi_flange)

class LabInfrastructure:
    """The Test Facility (Rigid Pipes + Decals)"""

    @staticmethod
    def fusion_stack_transforms() -> list[dict[str, object]]:
        return list(_FUSION_STACK_TRANSFORMS)

    def _magnet_world_bbox(self):
        """Axis-aligned bbox of the solenoid ``Magnet`` solid after the fusion stack pose."""
        from yaml_assembly.transform_ops import apply_transform_chain

        *_, mag, _ = IntegratedOrbitronTube().build()
        mag_w = apply_transform_chain(mag, _FUSION_STACK_TRANSFORMS)
        return mag_w.val().BoundingBox()

    def _nbi_world_bbox(self):
        """Axis-aligned bbox of ``NBI_Injector`` (tube + flange union) after the fusion stack pose."""
        from yaml_assembly.transform_ops import apply_transform_chain

        *_, nbi = IntegratedOrbitronTube().build()
        nbi_w = apply_transform_chain(nbi, _FUSION_STACK_TRANSFORMS)
        return nbi_w.val().BoundingBox()

    def nbi_feed_connector_anchors(self) -> dict[str, tuple[float, float, float]]:
        """H₂ / B₂H₆ bosses on the **NBI** feed flange (not the solenoid shell).

        After the lab’s fusion-stack rotation, the injectors protrude in **+X** with the
        farm-facing **+Y** flange normal toward the tank row. Trunks must terminate here so
        tubes meet the green injector mesh instead of floating on the magnet OD.
        """
        bb = self._nbi_world_bbox()
        _face_in = 0.012
        cx = (bb.xmin + bb.xmax) * 0.5
        cy = bb.ymax - _face_in
        cz = (bb.zmin + bb.zmax) * 0.5
        sep = 0.034
        return {
            "reactor_nbi_h2_in": (cx + sep * 0.5, cy, cz + 0.018),
            "reactor_nbi_b2h6_in": (cx - sep * 0.5, cy, cz - 0.012),
        }

    def magnet_shell_connector_anchors(self) -> dict[str, tuple[float, float, float]]:
        """Service points on the **magnet** OD plus matching bosses in ``Magnet_Service_Bosses``.

        **H₂ / B₂H₆** use :meth:`nbi_feed_connector_anchors`.

        The posed solenoid is a long cylinder ‖ **+X**. Ports lie on the **curved OD** via
        :func:`_magnet_od_inset_point` (φ from +Y toward +Z). **CH₄** → SSTO wall-thermal process
        boss on the yoke; **cryo CH₄** → jacket / boundary thermal conditioning stub; **HV** →
        ceramic feedthrough / yoke bushing (schematic) tying console bus to magnet potential.
        """
        bb = self._magnet_world_bbox()
        return {
            key: _magnet_od_inset_point(bb, x_offset=xo, phi_deg=phi, inset_m=ins)[:3]
            for key, xo, phi, ins, _br, _bh in _MAGNET_SHELL_SERVICE_TABLE
        }

    def build_table(self):
        legs = (cq.Workplane("XY").box(0.1, 0.1, 1.0).translate((0.6, 0.3, 0.5))
                .union(cq.Workplane("XY").box(0.1, 0.1, 1.0).translate((-0.6, 0.3, 0.5)))
                .union(cq.Workplane("XY").box(0.1, 0.1, 1.0).translate((0.6, -0.3, 0.5)))
                .union(cq.Workplane("XY").box(0.1, 0.1, 1.0).translate((-0.6, -0.3, 0.5))))
        top = cq.Workplane("XY").box(1.5, 0.8, 0.05).translate((0, 0, 1.0))
        mounts = (cq.Workplane("XY").box(0.1, 0.2, 0.25).translate((0.5, 0, 1.125))
                  .union(cq.Workplane("XY").box(0.1, 0.2, 0.25).translate((-0.5, 0, 1.125))))
        
        label = cq.Workplane("XZ").text("ORBITRON p-B11", 0.08, 0.001).translate((0, -0.401, 1.025))
        return legs.union(top).union(mounts), label

    def _panel_toggle(self, x: float, y: float, z: float) -> cq.Workplane:
        """Guarded toggle on the tilted operator panel (−30° about X)."""
        body = cq.Workplane("XY").box(0.09, 0.05, 0.04)
        lever = cq.Workplane("XY").box(0.02, 0.03, 0.05).translate((0.04, 0, 0.01))
        return body.union(lever).rotate((1, 0, 0), (0, 0, 0), -30).translate((x, y, z))

    def build_console(self):
        # Desk, screen, BRB, and three panel toggles as SEPARATE export meshes.
        base = cq.Workplane("XY").box(0.8, 0.8, 1.2).translate((0, -2.5, 0.6))
        panel = cq.Workplane("XY").box(0.8, 0.6, 0.05).rotate((1,0,0), (0,0,0), -30).translate((0, -2.6, 1.3))
        batt = cq.Workplane("XY").box(0.7, 0.6, 0.4).translate((0, -2.5, 0.2))
        desk = base.union(panel).union(batt)

        screen = cq.Workplane("XY").box(0.7, 0.05, 0.5).translate((0, -2.2, 1.6))
        brb = cq.Workplane("XY").cylinder(0.04, 0.05).rotate((1,0,0),(0,0,0),-30).translate((0.2, -2.65, 1.35))
        sw_apu = self._panel_toggle(-0.22, -2.58, 1.40)
        sw_starter = self._panel_toggle(-0.08, -2.58, 1.36)
        sw_bleed = self._panel_toggle(0.06, -2.58, 1.32)

        return desk, screen, brb, sw_apu, sw_starter, sw_bleed

    def build_fuel_farm(self):
        h2 = cq.Workplane("XY").circle(0.15).extrude(1.2).edges(">Z").fillet(0.1).translate((0.6, 1.2, 0))
        b2h6 = cq.Workplane("XY").circle(0.15).extrude(1.2).edges(">Z").fillet(0.1).translate((0.0, 1.2, 0))
        dewar = cq.Workplane("XY").circle(0.25).extrude(0.9).edges(">Z").fillet(0.1).translate((-0.7, 1.2, 0))
        
        txt_h2 = cq.Workplane("XZ").text("HYDROGEN", 0.05, 0.001).translate((0.6, 1.049, 0.8))
        txt_b2 = cq.Workplane("XZ").text("DIBORANE", 0.05, 0.001).translate((0.0, 1.049, 0.8))
        txt_ch4 = cq.Workplane("XZ").text("LIQUID METHANE", 0.05, 0.001).translate((-0.7, 0.949, 0.45))
        
        return h2, b2h6, dewar, txt_h2, txt_b2, txt_ch4

    def build_tank_farm_platform(self) -> cq.Workplane:
        """Skid deck + corner posts under the three ``build_fuel_farm()`` cylinders.

        Footprint is derived from the same centres and radii: H₂ at (0.6, 1.2) r=0.15,
        B₂H₆ at (0, 1.2) r=0.15, CH₄ dewar at (-0.7, 1.2) r=0.25. Deck top is z=0 so
        tank bases sit flush with the slab; legs extend downward for a pad-mounted read.
        """
        deck_t = 0.055
        deck_lx = 1.95
        deck_ly = 0.78
        cx, cy = -0.1, 1.2
        deck = cq.Workplane("XY").box(deck_lx, deck_ly, deck_t).translate((cx, cy, -deck_t / 2))

        leg_w = 0.065
        leg_h = 0.16
        z_leg_center = -deck_t - leg_h / 2
        inset = 0.055
        hx = deck_lx / 2 - inset
        hy = deck_ly / 2 - inset
        legs = cq.Workplane("XY")
        for x, y in (
            (cx - hx, cy - hy),
            (cx + hx, cy - hy),
            (cx - hx, cy + hy),
            (cx + hx, cy + hy),
        ):
            legs = legs.union(
                cq.Workplane("XY").box(leg_w, leg_w, leg_h).translate((x, y, z_leg_center))
            )
        return deck.union(legs)

    def fuel_line_connector_anchors(self) -> dict[str, tuple[float, float, float]]:
        """World-space points for fuel routing (tank tops + magnet-shell inlets).

        Tank tops match ``build_fuel_farm()``. **H₂** and **B₂H₆** reactor ends use
        :meth:`nbi_feed_connector_anchors` (injector flange). **CH₄** still uses the magnet
        +Y process inlet (wall-thermal leg).
        """
        z_trim = 0.035
        h2_roof = 1.2 - z_trim
        b2_roof = 1.2 - z_trim
        ch4_roof = 0.9 - z_trim
        h2_top = (0.6, 1.2, h2_roof + _LAB_TANK_VALVE_OUTLET_DZ)
        b2_top = (0.0, 1.2, b2_roof + _LAB_TANK_VALVE_OUTLET_DZ)
        ch4_top = (-0.7, 1.2, ch4_roof + _LAB_TANK_VALVE_OUTLET_DZ)

        mag_ports = self.magnet_shell_connector_anchors()
        nbi_ports = self.nbi_feed_connector_anchors()
        return {
            "fuel_farm_h2_tank_top": h2_top,
            "fuel_farm_b2h6_tank_top": b2_top,
            "fuel_farm_ch4_dewar_top": ch4_top,
            "reactor_fuel_h2_in": nbi_ports["reactor_nbi_h2_in"],
            "reactor_fuel_b2h6_in": nbi_ports["reactor_nbi_b2h6_in"],
            "reactor_fuel_ch4_in": mag_ports["reactor_magnet_fuel_ch4_in"],
        }

    def hv_connector_anchors(self) -> dict[str, tuple[float, float, float]]:
        """HV umbilical: operator console → magnet shell top (schematic feed; sim logic is XML/Nasal).

        ``console_hv_header`` is placed on the **shifted** console cluster (same basis as
        ``orbitron_lab.yaml`` instance translate for ``Operator_Console``): desk local
        centre (~0, -2.5, 0.6) plus stand offset (-1.4, -2.3, 0) → breakout toward +X / +Y
        toward the reactor.
        """
        mag_ports = self.magnet_shell_connector_anchors()
        # Operator_Console transform_chain in orbitron_lab.yaml: translate(-1.4, -2.3, 0)
        # Desk base local centre (build_console): (0, -2.5, 0.6) → world ~(-1.4, -4.8, 0.6).
        console_hv = (-1.05, -4.45, 1.28)
        return {
            "console_hv_header": console_hv,
            "reactor_magnet_hv_feed": mag_ports["reactor_magnet_hv_feed"],
        }

    def cryo_methane_connector_anchors(self) -> dict[str, tuple[float, float, float]]:
        """Cryostat / CH₄ fill path: dewar roof → magnet high-side tap (reference lab layout)."""
        z_trim = 0.035
        ch4_roof = 0.9 - z_trim
        dewar_top = (-0.7, 1.2, ch4_roof + _LAB_TANK_VALVE_OUTLET_DZ)
        mag_ports = self.magnet_shell_connector_anchors()
        return {
            "cryo_ch4_dewar_out": dewar_top,
            "reactor_magnet_cryo_ch4_tap": mag_ports["reactor_magnet_cryo_ch4_tap"],
        }

    def fusion_exhaust_connector_anchors(self) -> dict[str, tuple[float, float, float]]:
        """⁴He ash vent: core exhaust plane (+X after stack rotation) → CD nozzle inlet plenum."""
        bb = self._magnet_world_bbox()
        cy = (bb.ymin + bb.ymax) * 0.5
        cz = (bb.zmin + bb.zmax) * 0.5
        _exhaust_face_in = 0.012
        x_exhaust = bb.xmax - _exhaust_face_in
        return {
            "reactor_core_he_ash_out": (x_exhaust, cy, cz),
            "nozzle_plenum_he_ash_in": (x_exhaust + 0.74, cy, cz + 0.05),
        }

    def build_rigid_plumbing(self):
        """HV umbilical: hardwired path from ``console_hv_header`` to ``reactor_magnet_hv_feed``."""
        anchors = self.hv_connector_anchors()
        sx, sy, sz = anchors["console_hv_header"]
        ex, ey, ez = anchors["reactor_magnet_hv_feed"]
        rr = 0.02
        # Axis-aligned polyline: leave console cluster (+X), jog toward reactor (+Y),
        # run forward (+X), adjust Z, then descend to magnet crown feed.
        hv = _hv_seg_along_x(sy, sz, sx, -0.22, rr)
        hv = hv.union(_hv_seg_along_y(-0.22, sz, sy, -0.42, rr))
        hv = hv.union(_hv_seg_along_x(-0.42, sz, -0.22, 0.44, rr))
        hv = hv.union(_hv_seg_along_z(0.44, -0.42, sz, 1.18, rr))
        hv = hv.union(_hv_seg_along_y(0.44, 1.18, -0.42, 0.0, rr))
        hv = hv.union(_hv_seg_along_z(0.44, 0.0, 1.18, 0.62, rr))
        hv = hv.union(_hv_seg_along_x(0.0, 0.62, 0.44, ex, rr))
        hv = hv.union(_hv_seg_along_z(ex, ey, 0.62, ez, rr))

        h2_1 = cq.Workplane("XY").cylinder(0.4, 0.015).translate((0.6, 1.2, 1.4))  
        h2_2 = cq.Workplane("YZ").cylinder(0.5, 0.015).translate((0.35, 1.2, 1.6)) 
        h2_3 = cq.Workplane("XZ").cylinder(1.1, 0.015).translate((0.1, 0.65, 1.6)) 
        h2_4 = cq.Workplane("XY").cylinder(0.3, 0.015).translate((0.1, 0.1, 1.45)) 
        
        b2_1 = cq.Workplane("XY").cylinder(0.3, 0.015).translate((0.0, 1.2, 1.35))
        b2_2 = cq.Workplane("XZ").cylinder(1.1, 0.015).translate((0.0, 0.65, 1.5))
        b2_3 = cq.Workplane("YZ").cylinder(0.1, 0.015).translate((-0.05, 0.1, 1.5))
        b2_4 = cq.Workplane("XY").cylinder(0.2, 0.015).translate((-0.1, 0.1, 1.4))

        ch4_1 = cq.Workplane("XY").cylinder(0.5, 0.025).translate((-0.7, 1.2, 1.15))
        ch4_2 = cq.Workplane("XZ").cylinder(1.2, 0.025).translate((-0.7, 0.6, 1.4))
        ch4_3 = cq.Workplane("YZ").cylinder(0.65, 0.025).translate((-0.375, 0.0, 1.4))
        ch4_4 = cq.Workplane("XY").cylinder(0.15, 0.025).translate((-0.05, 0.0, 1.325))

        gas = h2_1.union(h2_2).union(h2_3).union(h2_4).union(b2_1).union(b2_2).union(b2_3).union(b2_4)
        meth = ch4_1.union(ch4_2).union(ch4_3).union(ch4_4)
        
        return hv, gas, meth


def lab_h2_injectant_trunk_params() -> dict[str, Any]:
    """H₂ trunk to tangential keV injectors (p-¹¹B proton / stability leg; D₂ Orbitron-class hardware)."""
    return {
        "include_port_markers": False,
        "connectivity_spec": {
            "physical_story": "Hydrogen trunk from H₂ cylinder to tangential keV ion beam injectors (p-¹¹B).",
            "links": [
                {
                    "link_id": "h2_service",
                    "service": "process_h2",
                    "from_region": "fuel_farm_h2_tank",
                    "to_region": "reactor_nbi_manifold",
                    "routing_intent": "arc_over_deck_then_nbi_flange",
                }
            ],
        },
        "connector_ports": [
            {
                "id": "tank_h2_out",
                "anchor": "fuel_farm_h2_tank_top",
                "offset": [0.0, 0.0, 0.0],
                "description": "H2 cylinder top centre (matches CadQuery fuel farm).",
            },
            {
                "id": "reactor_h2_in",
                "anchor": "reactor_fuel_h2_in",
                "offset": [0.0, 0.0, 0.0],
                "description": "NBI feed flange (+Y farm-facing boss) after fusion-stack pose.",
            },
        ],
        "connector_links": [
            {
                "id": "h2_service",
                "service": "process_h2",
                "from_port": "tank_h2_out",
                "to_port": "reactor_h2_in",
                "radius": 0.02,
                "description": "Hydrogen — over deck, then slopes to the green NBI manifold (not the magnet OD).",
                # Stay above thrust sled + engine mount (see _SERVICE_ROUTING_DECK_CLEAR_Z); approach injectors from +Y.
                "waypoints": [
                    [0.62, 0.82, 0.98],
                    [0.64, 0.42, 0.58],
                    [0.66, 0.30, 0.38],
                ],
            }
        ],
    }


def lab_d2_injectant_trunk_params() -> dict[str, Any]:
    """Backward-compatible alias (historical D₂ naming)."""
    return lab_h2_injectant_trunk_params()


def lab_helium_ash_vent_params() -> dict[str, Any]:
    """⁴He fusion ash bleed from core exhaust plane into the propulsive nozzle plenum (+X train)."""
    return {
        "include_port_markers": False,
        "connectivity_spec": {
            "physical_story": (
                "⁴He fusion ash (¹H + ¹¹B → 3 ⁴He) leaves the core exhaust plane into the "
                "CD nozzle plenum to join the jet / hot-gas mix."
            ),
            "links": [
                {
                    "link_id": "he_ash_vent",
                    "service": "fusion_helium_ash",
                    "from_region": "reactor_core_exhaust",
                    "to_region": "propulsive_nozzle_plenum",
                    "routing_intent": "along_core_axis_to_nozzle_adapter",
                }
            ],
        },
        "connector_ports": [
            {
                "id": "core_he_ash_out",
                "anchor": "reactor_core_he_ash_out",
                "offset": [0.0, 0.0, 0.0],
                "description": "Anode / fusion hot-gas exhaust plane (+X shell face after stack pose).",
            },
            {
                "id": "nozzle_he_ash_in",
                "anchor": "nozzle_plenum_he_ash_in",
                "offset": [0.0, 0.0, 0.0],
                "description": "Nozzle inlet plenum — helium ash enters the jet mix here.",
            },
        ],
        "connector_links": [
            {
                "id": "he_ash_vent",
                "service": "fusion_helium_ash",
                "from_port": "core_he_ash_out",
                "to_port": "nozzle_he_ash_in",
                "radius": 0.016,
                "description": "⁴He ash vent — parallel to main +X exhaust path into nozzle.",
                "waypoints": [[0.12, 0.0, 0.0], [0.38, 0.0, 0.02]],
            }
        ],
    }


def lab_b2h6_injectant_trunk_params() -> dict[str, Any]:
    """Single-service connector spec for B₂H₆ injectant (subset of former ``Fuel_Gas_Lines``)."""
    return {
        "include_port_markers": False,
        "connectivity_spec": {
            "physical_story": "Diborane gaseous boron carrier trunk from B₂H₆ cylinder to the NBI flange.",
            "links": [
                {
                    "link_id": "b2h6_service",
                    "service": "diborane_nbi_boron_carrier",
                    "from_region": "fuel_farm_b2h6_tank",
                    "to_region": "reactor_nbi_manifold",
                    "routing_intent": "arc_over_deck_then_nbi_flange",
                }
            ],
        },
        "connector_ports": [
            {
                "id": "tank_b2h6_out",
                "anchor": "fuel_farm_b2h6_tank_top",
                "offset": [0.0, 0.0, 0.0],
                "description": "Diborane cylinder top centre.",
            },
            {
                "id": "reactor_b2h6_in",
                "anchor": "reactor_fuel_b2h6_in",
                "offset": [0.0, 0.0, 0.0],
                "description": "Second boss on the NBI feed flange (paired with H₂).",
            },
        ],
        "connector_links": [
            {
                "id": "b2h6_service",
                "service": "diborane_nbi_boron_carrier",
                "from_port": "tank_b2h6_out",
                "to_port": "reactor_b2h6_in",
                "radius": 0.02,
                "description": "Diborane — gaseous boron carrier to NBI / injector manifold.",
                "waypoints": [
                    [0.04, 0.82, 0.96],
                    [0.22, 0.42, 0.55],
                    [0.50, 0.30, 0.34],
                ],
            }
        ],
    }


if __name__ == "__main__":
    raise SystemExit(
        "Lab glTF is built only via Makefile: assembly YAML → tools/compile_assembly_yaml.py. "
        "This file supplies CadQuery templates for the YAML compiler."
    )
