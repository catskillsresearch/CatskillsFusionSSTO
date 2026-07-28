#!/usr/bin/env python3
"""Bay plant from assembly.json (heritage FG scale).

Wing TE: pulled to the elevon flap line inside build_plan_a_wings.py
(no overlay closeout / "scotch tape").

Was:
1) grenadier_wing_te_closeout.ac — retired; do not reload in FG.
2) grenadier_bay_plant.ac — fusion plant skid contents only (battery, water,
   fuel, CHARM chamber string + racks). No assembly-name boxes. No fake
   engine poke — 3-cycle lives in nozzle/OMS; aft bulkhead gets a bus hole.
"""

from __future__ import annotations

import math
from pathlib import Path

from label_plates import top_label_quad, write_label_png

OUT = Path(__file__).resolve().parent

# AC axes: +X aft, +Y up, +Z right (same as shuttle_o2)


def _v(x, y, z):
    return (float(x), float(y), float(z))


class ACBuilder:
    def __init__(self):
        self.materials = []
        self.objects = []

    def add_mat(self, name, rgb, amb=0.35, emis=0.0, spec=0.3, shi=30, trans=0.0):
        self.materials.append(
            dict(name=name, rgb=rgb, amb=amb, emis=emis, spec=spec, shi=shi, trans=trans)
        )
        return len(self.materials) - 1

    def add_mesh(self, name, verts, faces, mat=0, twosided=True, texture=None, face_uvs=None):
        self.objects.append(
            dict(
                name=name,
                loc=(0, 0, 0),
                verts=verts,
                faces=faces,
                mat=mat,
                twosided=twosided,
                texture=texture,
                face_uvs=face_uvs,
            )
        )

    def box(self, name, x0, x1, y0, y1, z0, z1, mat=0):
        v = [
            _v(x0, y0, z0),
            _v(x1, y0, z0),
            _v(x1, y1, z0),
            _v(x0, y1, z0),
            _v(x0, y0, z1),
            _v(x1, y0, z1),
            _v(x1, y1, z1),
            _v(x0, y1, z1),
        ]
        f = [
            (0, 1, 2, 3),
            (4, 7, 6, 5),
            (0, 4, 5, 1),
            (1, 5, 6, 2),
            (2, 6, 7, 3),
            (3, 7, 4, 0),
        ]
        self.add_mesh(name, v, f, mat=mat)

    def labeled_box(self, name, text, x0, x1, y0, y1, z0, z1, mat, label_mat, tex_dir: Path):
        self.box(name, x0, x1, y0, y1, z0, z1, mat=mat)
        self.label_plate(name, text, x0, x1, y1, z0, z1, label_mat, tex_dir)

    def label_plate(self, name, text, x0, x1, y_top, z0, z1, label_mat, tex_dir: Path):
        slug = name.replace("grenadier-", "").replace("bay-", "")
        tex_name = f"label_{slug}.png"
        write_label_png(tex_dir / tex_name, text)
        verts, faces, uvs = top_label_quad(x0, x1, y_top, z0, z1)
        self.add_mesh(
            f"{name}-label",
            verts,
            faces,
            mat=label_mat,
            twosided=True,
            texture=f"textures/{tex_name}",
            face_uvs=uvs,
        )

    def cylinder_x(self, name, x0, x1, cy, cz, r, mat, segs=20):
        """Closed can along +X (chamber / magnet coil stand-in)."""
        ring0 = [
            _v(x0, cy + r * math.sin(2 * math.pi * i / segs), cz + r * math.cos(2 * math.pi * i / segs))
            for i in range(segs)
        ]
        ring1 = [
            _v(x1, cy + r * math.sin(2 * math.pi * i / segs), cz + r * math.cos(2 * math.pi * i / segs))
            for i in range(segs)
        ]
        c0, c1 = _v(x0, cy, cz), _v(x1, cy, cz)
        verts = [c0, c1] + ring0 + ring1
        faces = []
        for i in range(segs):
            a, bb = 2 + i, 2 + (i + 1) % segs
            faces.append((0, a, bb))
            c, d = 2 + segs + i, 2 + segs + (i + 1) % segs
            faces.append((1, d, c))
            faces.append((a, d, c, bb))
        self.add_mesh(name, verts, faces, mat=mat, twosided=True)

    def labeled_cylinder_x(self, name, text, x0, x1, cy, cz, r, mat, label_mat, tex_dir, segs=20):
        self.cylinder_x(name, x0, x1, cy, cz, r, mat, segs=segs)
        self.label_plate(name, text, x0, x1, cy + r, cz - r * 0.35, cz + r * 0.35, label_mat, tex_dir)

    def write(self, path: Path):
        lines = ["AC3Db"]
        for m in self.materials:
            r, g, b = m["rgb"]
            lines.append(
                f'MATERIAL "{m["name"]}" '
                f"rgb {r:.4f} {g:.4f} {b:.4f}  "
                f'amb {m["amb"]:.4f} {m["amb"]:.4f} {m["amb"]:.4f}  '
                f'emis {m["emis"]:.4f} {m["emis"]:.4f} {m["emis"]:.4f}  '
                f'spec {m["spec"]:.4f} {m["spec"]:.4f} {m["spec"]:.4f}  '
                f'shi {m["shi"]} trans {m["trans"]:.4f}'
            )
        lines.append("OBJECT world")
        lines.append('name "world"')
        lines.append(f"kids {len(self.objects)}")
        for obj in self.objects:
            lines.append("OBJECT poly")
            lines.append(f'name "{obj["name"]}"')
            lx, ly, lz = obj["loc"]
            lines.append(f"loc {lx:.6f} {ly:.6f} {lz:.6f}")
            if obj.get("texture"):
                lines.append(f'texture "{obj["texture"]}"')
                lines.append("texrep 1 1")
            lines.append("crease 40.0")
            lines.append(f"numvert {len(obj['verts'])}")
            for x, y, z in obj["verts"]:
                lines.append(f"{x:.6f} {y:.6f} {z:.6f}")
            lines.append(f"numsurf {len(obj['faces'])}")
            surf = "0x30" if obj.get("twosided") else "0x10"
            face_uvs = obj.get("face_uvs")
            for fi, face in enumerate(obj["faces"]):
                lines.append(f"SURF {surf}")
                lines.append(f"mat {obj['mat']}")
                lines.append(f"refs {len(face)}")
                uvs = face_uvs[fi] if face_uvs else None
                for j, idx in enumerate(face):
                    if uvs:
                        u, vv = uvs[j]
                        lines.append(f"{idx} {u:.6f} {vv:.6f}")
                    else:
                        lines.append(f"{idx} 0 0")
            lines.append("kids 0")
        path.write_text("\n".join(lines) + "\n")
        print(f"wrote {path} ({len(self.objects)} objects)")


def build_wing_te_closeout():
    """Retired: overlay TE skins looked like scotch tape.

    Wing TE is corrected in build_plan_a_wings.pull_wing_te_to_flap_line().
    Writes an empty world so stale XML cannot resurrect the patches.
    """
    path = OUT / "grenadier_wing_te_closeout.ac"
    path.write_text(
        "AC3Db\n"
        "MATERIAL \"empty\" rgb 0.5 0.5 0.5  amb 0.2 0.2 0.2  emis 0 0 0  "
        "spec 0.1 0.1 0.1  shi 10  trans 0\n"
        "OBJECT world\n"
        "kids 0\n"
    )
    print(f"wrote empty {path.name} (TE closeout retired)")


def build_bay_plant():
    """assembly.json fusion plant → heritage bay. Part labels only (no assembly boxes).

    Station map (FG +X aft), mirroring build_fusion_plant_skid_blender.py:
      battery | water | fuel | shield | L-chamber | HEX | R-chamber
    3-cycle is NOT in the bay — aft bulkhead keeps a bus pass-through only.
    """
    b = ACBuilder()
    mat_skid = b.add_mat("skid", (0.28, 0.30, 0.32), amb=0.35, spec=0.35, shi=35)
    mat_deck = b.add_mat("deck", (0.22, 0.23, 0.24), amb=0.3, spec=0.15, shi=18)
    mat_batt = b.add_mat("battery", (0.55, 0.70, 0.55), amb=0.4, spec=0.25, shi=25)
    mat_water = b.add_mat("water-tank", (0.45, 0.65, 0.90), amb=0.4, spec=0.45, shi=50)
    mat_fuel = b.add_mat("fuel", (0.70, 0.65, 0.85), amb=0.4, spec=0.35, shi=35)
    mat_shield = b.add_mat("shield", (0.88, 0.88, 0.80), amb=0.4, spec=0.2, shi=20)
    mat_chamber = b.add_mat("chamber", (0.90, 0.55, 0.45), amb=0.4, spec=0.35, shi=35)
    mat_hex = b.add_mat("hex", (0.80, 0.42, 0.34), amb=0.4, spec=0.35, shi=35)
    mat_magnet = b.add_mat("magnet", (0.30, 0.35, 0.75), amb=0.4, spec=0.4, shi=40)
    mat_cryo = b.add_mat("cryo", (0.45, 0.80, 0.85), amb=0.4, spec=0.3, shi=30)
    mat_psu = b.add_mat("psu", (0.90, 0.75, 0.30), amb=0.4, spec=0.3, shi=30)
    mat_rf = b.add_mat("rf", (0.40, 0.75, 0.45), amb=0.4, spec=0.3, shi=30)
    mat_dec = b.add_mat("dec", (0.85, 0.35, 0.55), amb=0.4, spec=0.3, shi=30)
    mat_drive = b.add_mat("drive", (0.55, 0.50, 0.45), amb=0.35, spec=0.4, shi=40)
    mat_thermal = b.add_mat("thermal", (0.35, 0.55, 0.70), amb=0.35, spec=0.35, shi=35)
    mat_bus = b.add_mat("bus", (0.15, 0.15, 0.16), amb=0.3, spec=0.2, shi=20)
    mat_vac = b.add_mat("vacuum", (0.40, 0.40, 0.42), amb=0.35, spec=0.25, shi=25)
    mat_backbone = b.add_mat("backbone", (0.32, 0.33, 0.34), amb=0.35, spec=0.3, shi=28)
    mat_bulk = b.add_mat("aft-bulk", (0.25, 0.26, 0.27), amb=0.3, spec=0.15, shi=18)
    mat_label = b.add_mat("label-plate", (0.95, 0.95, 0.97), amb=0.5, spec=0.1, shi=10)

    tex_dir = OUT / "textures"
    tex_dir.mkdir(exist_ok=True)
    L = mat_label

    x0 = -9.5
    battery_x0, battery_x1 = x0, x0 + 2.2
    water_x0, water_x1 = battery_x1, battery_x1 + 4.0
    fuel_x0, fuel_x1 = water_x1, water_x1 + 2.0
    island_x0, island_x1 = fuel_x1, 6.2
    shield_t = 0.55
    shield_x0, shield_x1 = island_x0, island_x0 + shield_t
    reactor_x0, reactor_x1 = shield_x1, island_x1
    island_len = reactor_x1 - reactor_x0
    lf_x0 = reactor_x0
    lf_x1 = reactor_x0 + island_len * 0.347
    hex_x0, hex_x1 = lf_x1, lf_x1 + island_len * 0.306
    rfc_x0, rfc_x1 = hex_x1, reactor_x1

    y_floor, y_top = -4.20, -1.55
    y_mid = -2.70
    z_half = 1.85
    lf_r, hex_r, rfc_r = 0.95, 0.82, 0.95

    b.box("grenadier-bay-deck", x0, island_x1, -4.45, -4.25, -z_half, z_half, mat=mat_deck)
    b.labeled_box(
        "grenadier-bay-rail-L", "SKID", x0 + 0.1, island_x1 - 0.1, -4.25, -3.90, 1.55, 1.85, mat_skid, L, tex_dir
    )
    b.labeled_box(
        "grenadier-bay-rail-R", "SKID", x0 + 0.1, island_x1 - 0.1, -4.25, -3.90, -1.85, -1.55, mat_skid, L, tex_dir
    )

    b.labeled_box(
        "grenadier-bay-battery",
        "BATTERY",
        battery_x0 + 0.15,
        battery_x1 - 0.15,
        y_floor,
        y_floor + 1.6,
        -1.30,
        1.30,
        mat_batt,
        L,
        tex_dir,
    )

    for i, zc in enumerate((-0.95, 0.95)):
        side = "L" if zc > 0 else "R"
        b.labeled_box(
            f"grenadier-bay-water-{i}",
            f"WATER {side}",
            water_x0 + 0.15,
            water_x1 - 0.15,
            y_floor,
            y_floor + 2.3,
            zc - 0.65,
            zc + 0.65,
            mat_water,
            L,
            tex_dir,
        )

    b.labeled_box(
        "grenadier-bay-proton-tank",
        "PROTON",
        fuel_x0 + 0.1,
        fuel_x1 - 0.1,
        y_floor,
        y_floor + 1.5,
        0.35,
        1.40,
        mat_fuel,
        L,
        tex_dir,
    )
    b.labeled_box(
        "grenadier-bay-boron11",
        "B11",
        fuel_x0 + 0.25,
        fuel_x0 + 0.95,
        y_floor,
        y_floor + 1.2,
        -1.35,
        -0.45,
        mat_fuel,
        L,
        tex_dir,
    )
    b.labeled_box(
        "grenadier-bay-boron-injector",
        "B11 INJ",
        fuel_x0 + 1.05,
        fuel_x1 - 0.15,
        y_floor + 0.2,
        y_floor + 1.0,
        -1.20,
        -0.55,
        mat_fuel,
        L,
        tex_dir,
    )

    b.labeled_box(
        "grenadier-bay-shield",
        "SHIELD",
        shield_x0,
        shield_x1,
        y_floor,
        y_top,
        -z_half + 0.1,
        z_half - 0.1,
        mat_shield,
        L,
        tex_dir,
    )

    b.labeled_box(
        "grenadier-bay-backbone",
        "BACKBONE",
        reactor_x0,
        reactor_x1,
        y_floor,
        y_floor + 0.25,
        -0.35,
        0.35,
        mat_backbone,
        L,
        tex_dir,
    )

    b.labeled_cylinder_x(
        "grenadier-bay-chamber-L", "CHAMBER L", lf_x0 + 0.05, lf_x1 - 0.05, y_mid, 0.0, lf_r, mat_chamber, L, tex_dir
    )
    b.labeled_cylinder_x(
        "grenadier-bay-hex", "HEX", hex_x0 + 0.05, hex_x1 - 0.05, y_mid, 0.0, hex_r, mat_hex, L, tex_dir
    )
    b.labeled_cylinder_x(
        "grenadier-bay-chamber-R", "CHAMBER R", rfc_x0 + 0.05, rfc_x1 - 0.05, y_mid, 0.0, rfc_r, mat_chamber, L, tex_dir
    )
    b.labeled_cylinder_x(
        "grenadier-bay-axis", "AXIS", reactor_x0, reactor_x1, y_mid, 0.0, 0.12, mat_drive, L, tex_dir, segs=12
    )

    coil_xs = [
        lf_x0 + (lf_x1 - lf_x0) * 0.16,
        lf_x1 - (lf_x1 - lf_x0) * 0.10,
        hex_x0 + (hex_x1 - hex_x0) * 0.18,
        hex_x1 - (hex_x1 - hex_x0) * 0.18,
        rfc_x0 + (rfc_x1 - rfc_x0) * 0.10,
        rfc_x1 - (rfc_x1 - rfc_x0) * 0.16,
    ]
    coil_rs = [lf_r, lf_r, hex_r, hex_r, rfc_r, rfc_r]
    for i, (xc, rc) in enumerate(zip(coil_xs, coil_rs)):
        b.labeled_cylinder_x(
            f"grenadier-bay-magnet-{i}",
            f"MAG {i}",
            xc - 0.12,
            xc + 0.12,
            y_mid,
            0.0,
            rc + 0.14,
            mat_magnet,
            L,
            tex_dir,
            segs=16,
        )
        zc = 1.35 if i % 2 == 0 else -1.35
        b.labeled_box(
            f"grenadier-bay-cryostat-{i}",
            f"CRYOSTAT {i}",
            xc - 0.28,
            xc + 0.28,
            y_floor + 0.15,
            y_floor + 0.85,
            zc - 0.28,
            zc + 0.28,
            mat_cryo,
            L,
            tex_dir,
        )

    for i, xc in enumerate((coil_xs[1] + 0.2, coil_xs[4] - 0.2)):
        b.labeled_box(
            f"grenadier-bay-rf-launcher-{i}",
            f"RF LAUNCH {i}",
            xc - 0.30,
            xc + 0.30,
            y_floor + 0.2,
            y_floor + 1.1,
            1.05,
            1.55,
            mat_rf,
            L,
            tex_dir,
        )
        b.labeled_box(
            f"grenadier-bay-rf-amp-{i}",
            f"RF AMP {i}",
            xc - 0.35,
            xc + 0.35,
            y_floor + 0.2,
            y_floor + 1.0,
            0.45,
            0.95,
            mat_rf,
            L,
            tex_dir,
        )

    b.labeled_box(
        "grenadier-bay-rotation-drive",
        "DRIVE",
        hex_x0 + 0.2,
        hex_x1 - 0.2,
        y_floor + 0.1,
        y_floor + 0.9,
        -1.55,
        -1.05,
        mat_drive,
        L,
        tex_dir,
    )
    b.labeled_box(
        "grenadier-bay-coolant-bath",
        "COOLANT",
        hex_x0,
        hex_x1,
        y_floor,
        y_floor + 0.55,
        -0.95,
        -0.40,
        mat_thermal,
        L,
        tex_dir,
    )
    b.labeled_box(
        "grenadier-bay-dec",
        "DEC",
        hex_x0 + 0.15,
        hex_x1 - 0.15,
        y_floor + 0.15,
        y_floor + 1.2,
        1.05,
        1.70,
        mat_dec,
        L,
        tex_dir,
    )
    b.labeled_box(
        "grenadier-bay-magnet-psu",
        "MAG PSU",
        reactor_x0 + island_len * 0.2,
        reactor_x0 + island_len * 0.75,
        y_floor,
        y_floor + 1.0,
        -1.70,
        -1.05,
        mat_psu,
        L,
        tex_dir,
    )

    cryo_x0 = reactor_x0 + 0.35
    cryo_x1 = reactor_x1 - 0.35
    for i in range(6):
        xc = cryo_x0 + i * (cryo_x1 - cryo_x0) / 5.0
        b.labeled_box(
            f"grenadier-bay-cryocooler-{i}",
            f"CRYO {i}",
            xc - 0.28,
            xc + 0.28,
            y_floor,
            y_floor + 0.75,
            -z_half + 0.05,
            -z_half + 0.55,
            mat_cryo,
            L,
            tex_dir,
        )

    b.labeled_box(
        "grenadier-bay-vacuum",
        "VACUUM",
        rfc_x0 + 0.2,
        rfc_x1 - 0.3,
        y_floor + 0.1,
        y_floor + 0.9,
        0.55,
        1.05,
        mat_vac,
        L,
        tex_dir,
    )

    # plant_electrical_bus → aft wall hole (3-cycle stays in nozzle/OMS)
    b.labeled_box(
        "grenadier-bay-plant-bus",
        "PLANT BUS",
        island_x1 - 1.2,
        island_x1 + 0.6,
        y_mid - 0.15,
        y_mid + 0.15,
        -0.18,
        0.18,
        mat_bus,
        L,
        tex_dir,
    )
    b.box("grenadier-bay-aft-bulkhead", 6.85, 7.05, y_floor - 0.05, -0.40, -z_half, z_half, mat=mat_bulk)
    b.labeled_box(
        "grenadier-bay-bus-hole",
        "BUS HOLE",
        6.80,
        7.15,
        y_mid - 0.28,
        y_mid + 0.28,
        -0.28,
        0.28,
        mat_bus,
        L,
        tex_dir,
    )

    b.write(OUT / "grenadier_bay_plant.ac")


def main():
    build_wing_te_closeout()
    build_bay_plant()


if __name__ == "__main__":
    main()
