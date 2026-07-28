#!/usr/bin/env python3
"""Build Grenadier propulsion AC meshes — petal nozzle, rounded aft fairing, internals.

AC axes match shuttle_o2.ac / LandingGears.ac:
  +X aft,  +Y up,  +Z right

Goal look (reference render): single opaque petal bell, rounded TPS fairing
covering the boxy Shuttle aft / SSME stubs, 3-cycle hardware visible in throat.
"""

from __future__ import annotations

import math
from pathlib import Path

from label_plates import top_label_quad, write_label_png

OUT = Path(__file__).resolve().parent

# Engine axis in AC (Y-up)
CY = -2.45
CZ = 0.0


def _v(x, y, z):
    return (float(x), float(y), float(z))


def _ring(x, r, segs, cy=CY, cz=CZ):
    """Circle in YZ at fixed x; index 0 at +Z."""
    return [
        _v(x, cy + r * math.sin(2 * math.pi * i / segs), cz + r * math.cos(2 * math.pi * i / segs))
        for i in range(segs)
    ]


class ACBuilder:
    def __init__(self):
        self.materials = []
        self.objects = []

    def add_mat(self, name, rgb, amb=0.35, emis=0.0, spec=0.35, shi=40, trans=0.0):
        self.materials.append(
            {
                "name": name,
                "rgb": rgb,
                "amb": amb,
                "emis": emis,
                "spec": spec,
                "shi": shi,
                "trans": trans,
            }
        )
        return len(self.materials) - 1

    def add_mesh(self, name, verts, faces, mat=0, loc=(0, 0, 0), twosided=False, texture=None, face_uvs=None):
        self.objects.append(
            {
                "name": name,
                "loc": loc,
                "verts": verts,
                "faces": faces,
                "mat": mat,
                "twosided": twosided,
                "texture": texture,
                "face_uvs": face_uvs,
            }
        )

    def lathe_shell(self, name, profile, segs, mat, outward=True, twosided=False):
        """profile: list of (x, r). Builds a tube; outward=True → outer surface normals."""
        rings = [_ring(x, r, segs) for x, r in profile]
        verts = []
        for ring in rings:
            verts.extend(ring)
        faces = []
        nprof = len(profile)
        for i in range(nprof - 1):
            for j in range(segs):
                a = i * segs + j
                b = i * segs + (j + 1) % segs
                c = (i + 1) * segs + (j + 1) % segs
                d = (i + 1) * segs + j
                if outward:
                    faces.append((a, b, c, d))
                else:
                    faces.append((a, d, c, b))
        self.add_mesh(name, verts, faces, mat=mat, twosided=twosided)

    def disk(self, name, r, x, segs, mat, normal="+x", cy=CY, cz=CZ, twosided=False):
        verts = [_v(x, cy, cz)]
        verts.extend(_ring(x, r, segs, cy, cz))
        faces = []
        for i in range(segs):
            i1 = i + 1
            i2 = 1 + ((i + 1) % segs)
            if normal == "+x":
                faces.append((0, i1, i2))
            else:
                faces.append((0, i2, i1))
        self.add_mesh(name, verts, faces, mat=mat, twosided=twosided)

    def solid_cylinder(self, name, x0, x1, r, segs, mat, cy=CY, cz=CZ):
        """Closed can (side + both caps). Kills see-through heritage holes."""
        ring0 = _ring(x0, r, segs, cy, cz)
        ring1 = _ring(x1, r, segs, cy, cz)
        c0 = _v(x0, cy, cz)
        c1 = _v(x1, cy, cz)
        verts = [c0, c1] + ring0 + ring1
        faces = []
        for i in range(segs):
            a = 2 + i
            b = 2 + ((i + 1) % segs)
            faces.append((0, a, b))
            c = 2 + segs + i
            d = 2 + segs + ((i + 1) % segs)
            faces.append((1, d, c))
        for i in range(segs):
            a = 2 + i
            b = 2 + ((i + 1) % segs)
            c = 2 + segs + ((i + 1) % segs)
            d = 2 + segs + i
            faces.append((a, d, c, b))
        self.add_mesh(name, verts, faces, mat=mat, twosided=True)

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
        slug = name.replace("grenadier-", "")
        tex_name = f"label_{slug}.png"
        write_label_png(tex_dir / tex_name, text)
        verts, faces, uvs = top_label_quad(x0, x1, y1, z0, z1)
        self.add_mesh(
            f"{name}-label",
            [_v(*p) for p in verts],
            faces,
            mat=label_mat,
            twosided=True,
            texture=f"textures/{tex_name}",
            face_uvs=uvs,
        )

    def label_at(self, name, text, x0, x1, y_top, z0, z1, label_mat, tex_dir: Path):
        """Standalone label plate (for lathed / non-box parts)."""
        slug = name.replace("grenadier-", "")
        tex_name = f"label_{slug}.png"
        write_label_png(tex_dir / tex_name, text)
        verts, faces, uvs = top_label_quad(x0, x1, y_top, z0, z1)
        self.add_mesh(
            f"{name}-label",
            [_v(*p) for p in verts],
            faces,
            mat=label_mat,
            twosided=True,
            texture=f"textures/{tex_name}",
            face_uvs=uvs,
        )

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


def build_nozzle():
    """Rounded aft fairing + opaque petal bell covering SSME stubs."""
    b = ACBuilder()
    mat_tps = b.add_mat("aft-tps", (0.42, 0.43, 0.44), amb=0.45, spec=0.18, shi=22)
    mat_tps_dk = b.add_mat("aft-tps-dark", (0.18, 0.18, 0.19), amb=0.35, spec=0.12, shi=18)
    mat_blank = b.add_mat("stub-blank", (0.12, 0.12, 0.13), amb=0.3, spec=0.1, shi=15)
    mat_bell = b.add_mat("nozzle-metal", (0.28, 0.30, 0.33), amb=0.35, spec=0.55, shi=70, trans=0.0)
    mat_petal = b.add_mat("nozzle-petal", (0.16, 0.17, 0.19), amb=0.30, spec=0.45, shi=55, trans=0.0)
    mat_heat = b.add_mat("nozzle-heat", (0.32, 0.24, 0.18), amb=0.35, spec=0.35, shi=40, trans=0.0)
    mat_liner = b.add_mat("ceramic-liner", (0.55, 0.52, 0.48), amb=0.4, spec=0.2, shi=20, trans=0.0)
    mat_shadow = b.add_mat("throat-shadow", (0.05, 0.05, 0.06), amb=0.2, spec=0.05, shi=10, trans=0.0)

    segs = 48

    # --- Rounded fairing: boxy Shuttle aft → circular nozzle collar ---
    # Start further forward + larger radius so heritage fuselage SSME mount
    # rings (stubs) are fully blanked before the petal bell.
    fairing_profile = [
        (11.90, 3.95),  # ahead of stub circles
        (12.40, 3.80),
        (12.90, 3.45),
        (13.40, 3.05),
        (13.85, 2.65),
        (14.20, 2.35),
        (14.50, 2.20),  # meets bell outer
    ]
    b.lathe_shell("grenadier-aft-fairing", fairing_profile, segs, mat_tps, outward=True)
    # Forward bay wall
    b.disk("grenadier-aft-bulkhead", 3.95, 11.90, segs, mat_tps_dk, normal="-x", twosided=True)

    # Heritage fuselage still has three SSME cutouts at x≈13.0–13.45 (triangle
    # around CY). Thin disks lost the depth fight; use closed cans + a throat
    # bulkhead AFT of the hole plane so looking into the bell never sees them.
    for name, cy_i, cz_i in (
        ("grenadier-stub-can-U", CY + 1.55, 0.0),
        ("grenadier-stub-can-L", CY - 1.05, -1.50),
        ("grenadier-stub-can-R", CY - 1.05, 1.50),
    ):
        b.solid_cylinder(name, 12.85, 13.55, 1.20, 28, mat_blank, cy=cy_i, cz=cz_i)

    # Opaque throat bulkhead just aft of the hole plane (holes end ≈13.45).
    # Visible 3-cycle hardware sits aft of this in build_internals().
    b.disk("grenadier-throat-bulkhead", 1.90, 13.52, segs, mat_blank, normal="+x", twosided=True)
    b.disk("grenadier-throat-bulkhead-face", 1.75, 13.55, segs, mat_tps_dk, normal="+x", twosided=True)

    # --- Outer bell (opaque) ---
    bell_outer = [
        (14.45, 2.15),
        (14.75, 2.25),
        (15.15, 2.40),
        (15.60, 2.55),
        (16.05, 2.65),
        (16.40, 2.72),
    ]
    b.lathe_shell("grenadier-nozzle-outer", bell_outer, segs, mat_bell, outward=True, twosided=False)

    # --- Inner bell (heat-stained, normals face inward so throat reads solid) ---
    bell_inner = [
        (14.50, 2.00),
        (14.80, 2.10),
        (15.20, 2.25),
        (15.65, 2.40),
        (16.10, 2.50),
        (16.37, 2.55),
    ]
    b.lathe_shell("grenadier-nozzle-inner", bell_inner, segs, mat_heat, outward=False, twosided=False)

    # Exit lip ring
    lip = [
        (16.35, 2.55),
        (16.43, 2.74),
        (16.50, 2.70),
    ]
    b.lathe_shell("grenadier-nozzle-lip", lip, segs, mat_petal, outward=True)

    # Throat liner (open — internals show through)
    b.lathe_shell(
        "grenadier-nozzle-throat-tube",
        [(13.70, 1.60), (14.50, 2.00)],
        segs,
        mat_liner,
        outward=False,
    )
    # Thin entrance ring only (not a solid plug)
    b.lathe_shell(
        "grenadier-nozzle-throat-ring",
        [(13.65, 1.50), (13.75, 1.60)],
        segs,
        mat_shadow,
        outward=True,
    )

    # --- Longitudinal petals / cooling channels on outer bell ---
    n_petals = 20
    for i in range(n_petals):
        a0 = 2 * math.pi * (i / n_petals) - 0.04
        a1 = 2 * math.pi * (i / n_petals) + 0.04
        verts = []
        faces = []
        # strip along outer profile, slightly proud
        xs = [14.45, 15.0, 15.6, 16.2, 16.38]
        rs = [2.18, 2.38, 2.55, 2.68, 2.74]
        for x, r in zip(xs, rs):
            verts.append(_v(x, CY + r * math.sin(a0), CZ + r * math.cos(a0)))
            verts.append(_v(x, CY + r * math.sin(a1), CZ + r * math.cos(a1)))
        for k in range(len(xs) - 1):
            a = 2 * k
            b_i = 2 * k + 1
            c = 2 * (k + 1) + 1
            d = 2 * (k + 1)
            faces.append((a, d, c, b_i))
        b.add_mesh(f"grenadier-nozzle-petal-{i}", verts, faces, mat=mat_petal)

    # Collar where fairing meets bell
    b.lathe_shell(
        "grenadier-nozzle-collar",
        [(14.20, 2.25), (14.45, 2.20), (14.55, 2.15)],
        segs,
        mat_bell,
        outward=True,
    )
    mat_label = b.add_mat("label-plate", (0.95, 0.95, 0.97), amb=0.5, spec=0.1, shi=10)
    tex_dir = OUT / "textures"
    tex_dir.mkdir(exist_ok=True)
    b.label_at("grenadier-nozzle", "NOZZLE", 14.0, 15.2, CY + 2.35, -0.55, 0.55, mat_label, tex_dir)

    b.write(OUT / "grenadier_nozzle.ac")


def build_scoop():
    """variable_inlets + inlet_duct + MW farm halves jammed into OMS pod volume."""
    b = ACBuilder()
    mat_lip = b.add_mat("scoop-lip", (0.42, 0.44, 0.46), amb=0.4, spec=0.35, shi=40)
    mat_dark = b.add_mat("scoop-cavity", (0.01, 0.01, 0.012), amb=0.08, spec=0.02, shi=5)
    mat_door = b.add_mat("scoop-door", (0.08, 0.08, 0.09), amb=0.15, spec=0.1, shi=20)
    mat_duct = b.add_mat("scoop-duct", (0.22, 0.23, 0.25), amb=0.3, spec=0.2, shi=25)
    mat_hinge = b.add_mat("scoop-hinge", (0.18, 0.18, 0.19), amb=0.25, spec=0.25, shi=28)
    mat_pre = b.add_mat("precompressor", (0.55, 0.50, 0.40), amb=0.4, spec=0.4, shi=40)
    mat_mw = b.add_mat("mw-box", (0.18, 0.55, 0.42), amb=0.4, spec=0.3, shi=30, emis=0.08)
    mat_label = b.add_mat("label-plate", (0.95, 0.95, 0.97), amb=0.5, spec=0.1, shi=10)
    tex_dir = OUT / "textures"
    tex_dir.mkdir(exist_ok=True)
    L = mat_label

    b.labeled_box("grenadier-scoop-L-lip", "INLET L", 11.40, 11.72, -0.70, 0.45, 1.40, 2.80, mat_lip, L, tex_dir)
    b.box("grenadier-scoop-L-cavity", 11.50, 13.10, -0.55, 0.30, 1.55, 2.65, mat=mat_dark)
    b.box("grenadier-scoop-L-door-A", 11.70, 11.95, -0.50, -0.02, 1.58, 2.62, mat=mat_door)
    b.box("grenadier-scoop-L-door-B", 11.70, 11.95, 0.02, 0.50, 1.58, 2.62, mat=mat_door)
    b.box("grenadier-scoop-L-hinge", 11.95, 12.10, -0.08, 0.08, 1.60, 2.60, mat=mat_hinge)
    b.labeled_box("grenadier-scoop-L-duct", "DUCT L", 12.40, 13.70, -0.85, -0.10, 0.45, 1.90, mat_duct, L, tex_dir)

    b.labeled_box("grenadier-scoop-R-lip", "INLET R", 11.40, 11.72, -0.70, 0.45, -2.80, -1.40, mat_lip, L, tex_dir)
    b.box("grenadier-scoop-R-cavity", 11.50, 13.10, -0.55, 0.30, -2.65, -1.55, mat=mat_dark)
    b.box("grenadier-scoop-R-door-A", 11.70, 11.95, -0.50, -0.02, -2.62, -1.58, mat=mat_door)
    b.box("grenadier-scoop-R-door-B", 11.70, 11.95, 0.02, 0.50, -2.62, -1.58, mat=mat_door)
    b.box("grenadier-scoop-R-hinge", 11.95, 12.10, -0.08, 0.08, -2.60, -1.60, mat=mat_hinge)
    b.labeled_box("grenadier-scoop-R-duct", "DUCT R", 12.40, 13.70, -0.85, -0.10, -1.90, -0.45, mat_duct, L, tex_dir)

    b.labeled_box("grenadier-scoop-plenum", "PLENUM", 12.40, 13.80, -0.95, 0.0, -0.45, 0.45, mat_duct, L, tex_dir)

    b.labeled_box(
        "grenadier-precompressor", "PRECOMP", 12.6, 14.2, -1.70, -0.85, 1.55, 2.45, mat_pre, L, tex_dir
    )
    for i, zc in enumerate((1.95, 2.25, 1.70)):
        b.labeled_box(
            f"grenadier-mw-pod-L-{i}", f"MW L{i}", 12.9, 14.1, -1.55, -0.95, zc - 0.18, zc + 0.18, mat_mw, L, tex_dir
        )
    for i, zc in enumerate((-1.95, -2.25, -1.70)):
        b.labeled_box(
            f"grenadier-mw-pod-R-{i}", f"MW R{i}", 12.9, 14.1, -1.55, -0.95, zc - 0.18, zc + 0.18, mat_mw, L, tex_dir
        )

    mat_oms_blank = b.add_mat("oms-engine-blank", (0.16, 0.16, 0.17), amb=0.3, spec=0.12, shi=18)
    for name, cy_i, cz_i in (
        ("grenadier-oms-blank-L", -1.35, 2.03),
        ("grenadier-oms-blank-R", -1.35, -2.03),
    ):
        b.disk(name, 0.55, 14.52, 28, mat_oms_blank, normal="+x", cy=cy_i, cz=cz_i)
        b.disk(f"{name}-under", 0.48, 14.40, 28, mat_oms_blank, normal="+x", cy=cy_i, cz=cz_i)

    b.write(OUT / "grenadier_scoop.ac")


def build_internals():
    """3-cycle jammed aft of bay bulkhead + in throat. Part labels only."""
    b = ACBuilder()
    mat_fan = b.add_mat("edf-fan", (0.78, 0.82, 0.88), amb=0.45, spec=0.6, shi=60, emis=0.03)
    mat_stator = b.add_mat("edf-stator", (0.55, 0.42, 0.22), amb=0.4, spec=0.35, shi=35)
    mat_hub = b.add_mat("edf-hub", (0.20, 0.21, 0.23), amb=0.35, spec=0.4, shi=40)
    mat_duct = b.add_mat("duct", (0.40, 0.42, 0.45), amb=0.4, spec=0.3, shi=30)
    mat_app = b.add_mat("applicator", (0.70, 0.55, 0.25), amb=0.4, spec=0.5, shi=50, emis=0.1)
    mat_vap = b.add_mat("vaporizer", (0.55, 0.58, 0.62), amb=0.4, spec=0.45, shi=45)
    mat_s3 = b.add_mat("stage3-plasma", (0.45, 0.70, 0.85), amb=0.4, spec=0.4, shi=45, emis=0.12)
    mat_inj = b.add_mat("injector", (0.35, 0.55, 0.70), amb=0.35, spec=0.35, shi=35)
    mat_cable = b.add_mat("bus-cable", (0.06, 0.06, 0.07), amb=0.25, spec=0.15, shi=12)
    mat_frame = b.add_mat("skid-frame", (0.32, 0.33, 0.34), amb=0.35, spec=0.3, shi=28)
    mat_mw = b.add_mat("mw-box", (0.18, 0.55, 0.42), amb=0.4, spec=0.3, shi=30, emis=0.08)
    mat_label = b.add_mat("label-plate", (0.95, 0.95, 0.97), amb=0.5, spec=0.1, shi=10)

    tex_dir = OUT / "textures"
    tex_dir.mkdir(exist_ok=True)
    L = mat_label
    segs = 28

    b.labeled_box(
        "grenadier-eng-rail-L", "RAIL", 9.8, 13.5, CY - 0.55, CY - 0.30, CZ - 1.55, CZ - 1.30, mat_frame, L, tex_dir
    )
    b.labeled_box(
        "grenadier-eng-rail-R", "RAIL", 9.8, 13.5, CY - 0.55, CY - 0.30, CZ + 1.30, CZ + 1.55, mat_frame, L, tex_dir
    )

    b.labeled_box(
        "grenadier-bus-coupler", "BUS COUPLER", 7.1, 8.2, CY - 0.35, CY + 0.05, -0.25, 0.25, mat_hub, L, tex_dir
    )
    b.labeled_box(
        "grenadier-bus-cable", "BUS CABLE", 8.2, 11.0, CY - 0.20, CY + 0.0, -0.12, 0.12, mat_cable, L, tex_dir
    )

    b.lathe_shell(
        "grenadier-edf-duct", [(13.55, 1.35), (13.90, 1.30), (14.35, 1.25)], segs, mat_duct, outward=False
    )
    b.label_at("grenadier-edf-duct", "EDF DUCT", 13.55, 14.35, CY + 1.50, -0.45, 0.45, L, tex_dir)

    b.lathe_shell("grenadier-edf-hub", [(13.70, 0.40), (14.20, 0.40)], 16, mat_hub, outward=True)
    for i in range(12):
        a0 = 2 * math.pi * i / 12
        a1 = a0 + 0.20
        r0, r1 = 0.40, 1.30
        x0, x1 = 13.75, 14.05
        verts = [
            _v(x0, CY + r0 * math.sin(a0), CZ + r0 * math.cos(a0)),
            _v(x0, CY + r1 * math.sin(a0), CZ + r1 * math.cos(a0)),
            _v(x0, CY + r1 * math.sin(a1), CZ + r1 * math.cos(a1)),
            _v(x0, CY + r0 * math.sin(a1), CZ + r0 * math.cos(a1)),
            _v(x1, CY + r0 * math.sin(a0), CZ + r0 * math.cos(a0)),
            _v(x1, CY + r1 * math.sin(a0), CZ + r1 * math.cos(a0)),
            _v(x1, CY + r1 * math.sin(a1), CZ + r1 * math.cos(a1)),
            _v(x1, CY + r0 * math.sin(a1), CZ + r0 * math.cos(a1)),
        ]
        faces = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
        b.add_mesh(f"grenadier-edf-blade-{i}", verts, faces, mat=mat_fan)
    b.disk("grenadier-edf-face", 1.35, 13.70, segs, mat_fan, normal="+x", twosided=True)
    b.label_at("grenadier-edf", "EDF", 13.65, 14.25, CY + 1.55, -0.55, 0.55, L, tex_dir)

    for i in range(10):
        a = 2 * math.pi * i / 10
        y0, z0 = CY + 0.35 * math.sin(a), CZ + 0.35 * math.cos(a)
        y1, z1 = CY + 1.25 * math.sin(a), CZ + 1.25 * math.cos(a)
        t = 0.12
        verts = [
            _v(14.15, y0, z0),
            _v(14.15, y1, z1),
            _v(14.45, y1, z1),
            _v(14.45, y0, z0),
            _v(14.15, y0 + t * math.cos(a), z0 - t * math.sin(a)),
            _v(14.15, y1 + t * math.cos(a), z1 - t * math.sin(a)),
            _v(14.45, y1 + t * math.cos(a), z1 - t * math.sin(a)),
            _v(14.45, y0 + t * math.cos(a), z0 - t * math.sin(a)),
        ]
        faces = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
        b.add_mesh(f"grenadier-stator-{i}", verts, faces, mat=mat_stator)
    b.label_at("grenadier-stator", "STATOR", 14.10, 14.50, CY + 1.50, -0.50, 0.50, L, tex_dir)

    for i, z in enumerate((-0.55, 0.0, 0.55)):
        b.labeled_box(
            f"grenadier-mw-core-{i}",
            f"MW {i}",
            11.0,
            12.8,
            CY + 0.55,
            CY + 1.15,
            CZ + z - 0.22,
            CZ + z + 0.22,
            mat_mw,
            L,
            tex_dir,
        )
    b.lathe_shell("grenadier-mw-applicator", [(12.9, 0.55), (13.7, 0.85), (14.2, 1.05)], 20, mat_app, outward=True)
    b.label_at("grenadier-mw-applicator", "MW APP", 12.9, 14.0, CY + 1.15, -0.40, 0.40, L, tex_dir)

    b.labeled_box(
        "grenadier-water-injector", "H2O INJ", 9.5, 10.8, CY - 1.40, CY - 0.85, -0.35, 0.35, mat_inj, L, tex_dir
    )
    b.labeled_box(
        "grenadier-water-feed", "H2O FEED", 7.2, 9.5, CY - 1.25, CY - 1.05, 0.55, 0.75, mat_cable, L, tex_dir
    )
    b.lathe_shell("grenadier-vaporizer", [(11.0, 0.48), (12.2, 0.52)], 18, mat_vap, outward=True)
    b.label_at("grenadier-vaporizer", "VAPORIZER", 11.0, 12.2, CY + 0.65, -0.40, 0.40, L, tex_dir)
    b.lathe_shell("grenadier-stage3-plasma", [(12.3, 0.60), (13.5, 0.95)], 20, mat_s3, outward=True)
    b.label_at("grenadier-stage3-plasma", "S3 PLASMA", 12.3, 13.4, CY + 1.10, -0.45, 0.45, L, tex_dir)

    b.write(OUT / "grenadier_internals.ac")


def _write_simple_xml(ac_name: str, object_names: list[str], comment: str) -> None:
    lines = [
        '<?xml version="1.0"?>',
        f"<!-- {comment} -->",
        "<PropertyList>",
        f"  <path>Aircraft/CatskillsFusionSSTO/Models/Grenadier/{ac_name}</path>",
        "  <effect>",
        "    <inherits-from>Aircraft/CatskillsFusionSSTO/Models/Effects/shuttle-main</inherits-from>",
    ]
    for n in object_names:
        lines.append(f"    <object-name>{n}</object-name>")
    lines += ["  </effect>", "</PropertyList>", ""]
    (OUT / ac_name.replace(".ac", ".xml")).write_text("\n".join(lines))


def build_rcs():
    """LMP-103S green RCS tankage + manifold + bank labels (heritage nozzles stay on OMSPods)."""
    b = ACBuilder()
    mat_tank = b.add_mat("rcs-tank", (0.22, 0.55, 0.32), amb=0.4, spec=0.35, shi=40, emis=0.04)
    mat_he = b.add_mat("rcs-he", (0.55, 0.58, 0.72), amb=0.4, spec=0.4, shi=45)
    mat_man = b.add_mat("rcs-manifold", (0.35, 0.36, 0.38), amb=0.35, spec=0.3, shi=30)
    mat_bank = b.add_mat("rcs-bank", (0.45, 0.48, 0.42), amb=0.4, spec=0.25, shi=28)
    mat_label = b.add_mat("label-plate", (0.95, 0.95, 0.97), amb=0.5, spec=0.1, shi=10)
    tex_dir = OUT / "textures"
    tex_dir.mkdir(exist_ok=True)
    L = mat_label
    names: list[str] = []

    def track(name: str) -> str:
        names.append(name)
        return name

    # Aft pods — co-located with scoop MW farm (L uses +Z like grenadier-mw-pod-L-*)
    for side, z_sign in (("L", 1.0), ("R", -1.0)):
        z0 = z_sign * 2.55
        z1 = z_sign * 2.95
        if z0 > z1:
            z0, z1 = z1, z0
        b.labeled_box(
            track(f"grenadier-rcs-tank-{side}"),
            f"LMP {side}",
            13.05,
            14.15,
            -0.55,
            0.15,
            z0,
            z1,
            mat_tank,
            L,
            tex_dir,
        )
        names.append(f"grenadier-rcs-tank-{side}-label")
        zh0, zh1 = z_sign * 2.35, z_sign * 2.55
        if zh0 > zh1:
            zh0, zh1 = zh1, zh0
        b.labeled_box(
            track(f"grenadier-rcs-press-{side}"),
            f"He {side}",
            13.20,
            13.70,
            0.15,
            0.45,
            zh0,
            zh1,
            mat_he,
            L,
            tex_dir,
        )
        names.append(f"grenadier-rcs-press-{side}-label")
        zm0, zm1 = z_sign * 2.15, z_sign * 2.45
        if zm0 > zm1:
            zm0, zm1 = zm1, zm0
        b.labeled_box(
            track(f"grenadier-rcs-manifold-{side}"),
            f"RCS MAN {side}",
            13.50,
            14.20,
            -0.95,
            -0.55,
            zm0,
            zm1,
            mat_man,
            L,
            tex_dir,
        )
        names.append(f"grenadier-rcs-manifold-{side}-label")
        zb0, zb1 = z_sign * 2.90, z_sign * 3.15
        if zb0 > zb1:
            zb0, zb1 = zb1, zb0
        b.labeled_box(
            track(f"grenadier-rcs-primary-{side}"),
            f"PRI {side}",
            14.35,
            14.55,
            -0.40,
            0.20,
            zb0,
            zb1,
            mat_bank,
            L,
            tex_dir,
        )
        names.append(f"grenadier-rcs-primary-{side}-label")
        b.labeled_box(
            track(f"grenadier-rcs-vernier-{side}"),
            f"VER {side}",
            14.20,
            14.45,
            0.25,
            0.45,
            zb0,
            zb1,
            mat_bank,
            L,
            tex_dir,
        )
        names.append(f"grenadier-rcs-vernier-{side}-label")

    # Forward nose module (near heritage nose RCS)
    b.labeled_box(
        track("grenadier-rcs-tank-FWD"),
        "LMP FWD",
        -16.2,
        -15.2,
        -1.55,
        -0.85,
        -0.35,
        0.35,
        mat_tank,
        L,
        tex_dir,
    )
    names.append("grenadier-rcs-tank-FWD-label")
    b.labeled_box(
        track("grenadier-rcs-press-FWD"),
        "He FWD",
        -15.9,
        -15.4,
        -0.85,
        -0.55,
        -0.25,
        0.25,
        mat_he,
        L,
        tex_dir,
    )
    names.append("grenadier-rcs-press-FWD-label")
    b.labeled_box(
        track("grenadier-rcs-manifold-FWD"),
        "RCS MAN FWD",
        -15.5,
        -14.9,
        -1.70,
        -1.35,
        -0.30,
        0.30,
        mat_man,
        L,
        tex_dir,
    )
    names.append("grenadier-rcs-manifold-FWD-label")
    b.labeled_box(
        track("grenadier-rcs-primary-FWD"),
        "PRI FWD",
        -17.05,
        -16.75,
        -1.40,
        -0.90,
        -0.45,
        0.45,
        mat_bank,
        L,
        tex_dir,
    )
    names.append("grenadier-rcs-primary-FWD-label")
    b.labeled_box(
        track("grenadier-rcs-vernier-FWD"),
        "VER FWD",
        -16.70,
        -16.45,
        -0.70,
        -0.45,
        -0.25,
        0.25,
        mat_bank,
        L,
        tex_dir,
    )
    names.append("grenadier-rcs-vernier-FWD-label")

    b.write(OUT / "grenadier_rcs.ac")
    # labeled_box already creates -label children; track only base names above — rebuild name list from AC
    ac_names = [
        ln.split('"')[1]
        for ln in (OUT / "grenadier_rcs.ac").read_text().splitlines()
        if ln.startswith('name "') and ln.split('"')[1] != "world"
    ]
    _write_simple_xml("grenadier_rcs.ac", ac_names, "Green RCS LMP-103S tankage / manifolds / bank markers")


def main():
    build_nozzle()
    build_scoop()
    build_internals()
    build_rcs()


if __name__ == "__main__":
    main()
