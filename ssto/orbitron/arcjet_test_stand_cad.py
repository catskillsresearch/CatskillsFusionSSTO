"""
Arcjet / outdoor test-stand **geometry builders** (used by ``tools/yaml_assembly/templates_registry``).

Lab layout and export are **only** via ``orbitron_lab.yaml`` → ``make orbitron-lab-gltf``; this module
does not write glTF on its own.
"""
from __future__ import annotations

import math

import cadquery as cq


def bellmouth_flare(inlet_r: float = 0.18, throat_r: float = 0.05, length: float = 0.35) -> cq.Workplane:
    """Single lofted frustum as a coarse bellmouth."""
    return cq.Workplane("XY").circle(inlet_r).workplane(offset=length).circle(throat_r).loft(combine=True)


def compressor_housing(od: float = 0.14, length: float = 0.25) -> cq.Workplane:
    """Simple compressor can on the −X intake train (coarse single-stage spool)."""
    shell = cq.Workplane("XY").circle(od / 2).extrude(length)
    bore = cq.Workplane("XY").circle(od / 2 - 0.02).extrude(length + 0.01)
    return shell.cut(bore)


def turbine_housing(od: float = 0.16, length: float = 0.18) -> cq.Workplane:
    """Coarse turbine can on the +X hot-gas train (same spool as ``compressor_housing``)."""
    shell = cq.Workplane("XY").circle(od / 2).extrude(length)
    bore = cq.Workplane("XY").circle(od / 2 - 0.025).extrude(length + 0.01)
    return shell.cut(bore)


def pad_startup_cart(
    deck_lx: float = 0.58,
    deck_ly: float = 0.44,
    deck_h: float = 0.055,
    box_lx: float = 0.40,
    box_ly: float = 0.34,
    box_h: float = 0.38,
    wheel_r: float = 0.055,
) -> cq.Workplane:
    """Ground **APU cart** (battery / inverter skid) beside the −X intake — pad-only, not flight mass."""
    deck = cq.Workplane("XY").box(deck_lx, deck_ly, deck_h).translate((0, 0, deck_h / 2))
    box = cq.Workplane("XY").box(box_lx, box_ly, box_h).translate((0, 0, deck_h + box_h / 2))
    hx, hy = deck_lx / 2 - 0.07, deck_ly / 2 - 0.07
    wheels = cq.Workplane("XY")
    for x, y in ((-hx, -hy), (hx, -hy), (-hx, hy), (hx, hy)):
        wheels = wheels.union(
            cq.Workplane("XY").transformed(offset=(x, y, -wheel_r + 0.01)).circle(wheel_r).extrude(wheel_r * 2)
        )
    # Power post / receptacle toward the engine (+Y side of cart top).
    post = (
        cq.Workplane("XY")
        .transformed(offset=(box_lx * 0.22, box_ly * 0.32, deck_h + box_h))
        .circle(0.035)
        .extrude(0.09)
    )
    return deck.union(box).union(wheels).union(post)


def pad_startup_connector_anchors() -> dict[str, tuple[float, float, float]]:
    """World anchors for ``Pad_Startup_Power_Cable`` (tuned to cart + motor poses in ``orbitron_lab.yaml``)."""
    return {
        "pad_cart_power_out": (-1.50, -0.18, 0.46),
        "pad_motor_power_in": (-1.23, 0.12, 0.04),
    }


def pad_startup_cable_params() -> dict:
    """YAML-mergeable connector spec for cart → starter motor."""
    return {
        "include_port_markers": False,
        "connectivity_spec": {
            "physical_story": "Pad ground cart feeds the electric starter on the compressor spool.",
            "links": [
                {
                    "link_id": "starter_power",
                    "service": "pad_apu_starter_bus",
                    "from_region": "pad_startup_cart",
                    "to_region": "pad_startup_motor",
                    "routing_intent": "deck_cable_to_intake_starter",
                }
            ],
        },
        "connector_ports": [
            {
                "id": "pad_cart_power_out",
                "anchor": "pad_cart_power_out",
                "offset": [0.0, 0.0, 0.0],
                "description": "APU cart roof receptacle toward the engine.",
            },
            {
                "id": "pad_motor_power_in",
                "anchor": "pad_motor_power_in",
                "offset": [0.0, 0.0, 0.0],
                "description": "Starter motor power inlet on the −X spool pod.",
            },
        ],
        "connector_links": [
            {
                "id": "starter_power",
                "service": "pad_apu_starter_bus",
                "from_port": "pad_cart_power_out",
                "to_port": "pad_motor_power_in",
                "radius": 0.014,
                "description": "Heavy-gauge starter cable along the deck to the intake motor.",
                "waypoints": [
                    [-1.42, -0.02, 0.32],
                    [-1.34, 0.06, 0.18],
                ],
            }
        ],
    }


def pad_starter_motor_pod(
    motor_length: float = 0.14,
    motor_od: float = 0.10,
    shaft_radius: float = 0.02,
    shaft_length: float = 0.07,
) -> cq.Workplane:
    """Pad **electric starter** on the −X spool end (APU — rig power, not flight mass).

    Built along **+Z** in local coords; ``orbitron_lab.yaml`` poses it beside the bellmouth /
    compressor train with the same Y-rotation as the intake hardware.
    """
    motor = cq.Workplane("XY").circle(motor_od / 2).extrude(motor_length)
    stub = (
        cq.Workplane("XY")
        .workplane(offset=motor_length)
        .circle(shaft_radius)
        .extrude(shaft_length)
    )
    return motor.union(stub)


def bay_inlet_annulus_shroud(
    x0: float = -0.31,
    length: float = 0.175,
    outer_r: float = 0.149,
    inner_r: float = 0.088,
) -> cq.Workplane:
    """Hollow shell along +X bridging compressor housing and solenoid OD.

    Coarse stand-in for **compressor discharge into the reactor-bay annulus** (working
    air outside the niobium plasma boundary). Built in lab axes: bore clears the
    anode + inlet flange; OD matches the magnet shell radius band used in
    ``IntegratedOrbitronTube``.
    """
    shell = cq.Workplane("YZ").workplane(offset=x0).circle(outer_r).extrude(length)
    bore = cq.Workplane("YZ").workplane(offset=x0 - 0.001).circle(inner_r).extrude(length + 0.02)
    return shell.cut(bore)


def thrust_sled_frame(
    length: float = 2.2, width: float = 1.0, rail_h: float = 0.08
) -> cq.Workplane:
    """Open frame from long rails, short cross ties, and a thin deck."""
    long1 = cq.Workplane("XY").box(length, rail_h, rail_h).translate((0, width / 2, rail_h / 2))
    long2 = cq.Workplane("XY").box(length, rail_h, rail_h).translate((0, -width / 2, rail_h / 2))
    ties = long1.union(long2)
    z_tie = rail_h * 2
    for x in (-length / 2 + 0.25, 0.0, length / 2 - 0.25):
        tie = cq.Workplane("XY").box(width, rail_h, rail_h).translate((x, 0, z_tie))
        ties = ties.union(tie)
    deck = cq.Workplane("XY").box(length * 0.85, width * 0.75, 0.06).translate((0, 0, rail_h * 3))
    return ties.union(deck)


def rail_beam(span: float = 3.5) -> cq.Workplane:
    return cq.Workplane("XY").box(span, 0.12, 0.06).edges("|Z").fillet(0.015)


def load_cell_puck() -> cq.Workplane:
    return cq.Workplane("XY").cylinder(0.04, 0.06)


# World-Z thrust-sled load path (matches ``Thrust_Sled_Frame`` at z=-0.12, rail_h=0.08).
THRUST_SLED_FRAME_Z = -0.12
RAIL_H_DEFAULT = 0.08
DECK_TOP_Z = THRUST_SLED_FRAME_Z + RAIL_H_DEFAULT * 3 + 0.06  # upper face of deck slab
LOAD_CELL_HEIGHT = 0.04
LOAD_CELL_TOP_Z = DECK_TOP_Z + LOAD_CELL_HEIGHT
MOUNT_LEG_H_DEFAULT = 0.09
MOUNT_DECK_T_DEFAULT = 0.04
ENGINE_MOUNT_TOP_Z = LOAD_CELL_TOP_Z + MOUNT_LEG_H_DEFAULT + MOUNT_DECK_T_DEFAULT
# Legacy bell / fusion pivot was 0.15 (deck-top story); lift engine stack onto mount plate.
ENGINE_MOUNT_PIVOT_Z = ENGINE_MOUNT_TOP_Z
ENGINE_MOUNT_Z_LIFT = ENGINE_MOUNT_PIVOT_Z - 0.15


def engine_mount_frame(
    corner_x: float = 0.7,
    corner_y: float = 0.35,
    cell_top_z: float = LOAD_CELL_TOP_Z,
    leg_h: float = MOUNT_LEG_H_DEFAULT,
    deck_t: float = MOUNT_DECK_T_DEFAULT,
    post_r: float = 0.048,
) -> cq.Workplane:
    """Four posts on load-cell corners + top plate; engine bell flange sits on the plate."""
    z_leg_bot = cell_top_z
    z_leg_ctr = z_leg_bot + leg_h / 2
    z_deck_ctr = z_leg_bot + leg_h + deck_t / 2
    frame = cq.Workplane("XY")
    for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        x, y = sx * corner_x, sy * corner_y
        pad = (
            cq.Workplane("XY")
            .circle(post_r * 1.15)
            .extrude(0.012)
            .translate((x, y, z_leg_bot + 0.006))
        )
        leg = cq.Workplane("XY").circle(post_r).extrude(leg_h).translate((x, y, z_leg_ctr))
        frame = frame.union(pad).union(leg)
    lx = corner_x * 2 + 0.12
    ly = corner_y * 2 + 0.12
    deck = cq.Workplane("XY").box(lx, ly, deck_t).translate((0, 0, z_deck_ctr))
    return frame.union(deck)


def blast_detuner(inner_r: float = 0.35, wall: float = 0.04, length: float = 4.0) -> cq.Workplane:
    outer = cq.Workplane("XY").circle(inner_r + wall).extrude(length)
    inner = cq.Workplane("XY").circle(inner_r).extrude(length + 0.01)
    return outer.cut(inner)


def nozzle_stub(throat_r: float = 0.045, exit_r: float = 0.09, length: float = 0.2) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .circle(throat_r)
        .workplane(offset=length)
        .circle(exit_r)
        .loft(combine=True)
    )


def nozzle_inlet_plenum(
    inlet_r: float = 0.056, mid_r: float = 0.048, length: float = 0.07
) -> cq.Workplane:
    """Converging adapter / plenum stub ahead of the throat segment."""
    return cq.Workplane("XY").circle(inlet_r).workplane(offset=length).circle(mid_r).loft(combine=True)


def nozzle_cd_contour(r0: float = 0.048, throat_r: float = 0.045, length: float = 0.05) -> cq.Workplane:
    """Throat-forward CD segment (coarse stand-in for contoured wall)."""
    return cq.Workplane("XY").circle(r0).workplane(offset=length).circle(throat_r).loft(combine=True)


def nozzle_exit_hardware(throat_r: float = 0.045, exit_r: float = 0.09, length: float = 0.08) -> cq.Workplane:
    """Divergent section plus implicit exit plane / flange bosses (simplified)."""
    return cq.Workplane("XY").circle(throat_r).workplane(offset=length).circle(exit_r).loft(combine=True)


def bd_annulus_sleeve(
    inner_flow_r: float = 0.34,
    annulus_gap: float = 0.048,
    wall: float = 0.042,
    length: float = 0.75,
) -> cq.Workplane:
    """Outer annulus shell: gas in the gap between inner bore and outer duct wall."""
    outer_r = inner_flow_r + annulus_gap + wall
    shell = cq.Workplane("XY").circle(outer_r).extrude(length)
    bore = cq.Workplane("XY").circle(inner_flow_r + annulus_gap - 0.002).extrude(length + 0.02)
    return shell.cut(bore)


def bd_shock_core_insert(radius: float = 0.29, length: float = 0.9) -> cq.Workplane:
    """Central porous / insert volume represented as a short dense plug."""
    return cq.Workplane("XY").circle(radius).extrude(length)


def bd_bracket_seal_flange(
    outer_r: float = 0.42, inner_r: float = 0.33, thickness: float = 0.06, n_bolts: int = 8
) -> cq.Workplane:
    """Mounting flange with bolt bosses — load path + seal land to nozzle / duct."""
    disc = cq.Workplane("XY").circle(outer_r).extrude(thickness)
    hole = cq.Workplane("XY").circle(inner_r).extrude(thickness + 0.02)
    base = disc.cut(hole)
    bolt_circle_r = outer_r - 0.028
    bosses: cq.Workplane | None = None
    for i in range(n_bolts):
        ang = math.radians((360.0 / n_bolts) * i)
        x, y = bolt_circle_r * math.cos(ang), bolt_circle_r * math.sin(ang)
        b = cq.Workplane("XY").circle(0.012).extrude(thickness).translate((x, y, 0.0))
        bosses = b if bosses is None else bosses.union(b)
    return base if bosses is None else base.union(bosses)


def lab_fuel_feed_valve(body_r: float = 0.045, stem_r: float = 0.018, stem_h: float = 0.055) -> cq.Workplane:
    """Compact service valve / flex-jumper boss at a tank top (one mesh per species)."""
    base = cq.Workplane("XY").circle(body_r).extrude(0.04)
    stem = cq.Workplane("XY").circle(stem_r).extrude(stem_h).translate((0.0, 0.0, 0.04))
    return base.union(stem)

