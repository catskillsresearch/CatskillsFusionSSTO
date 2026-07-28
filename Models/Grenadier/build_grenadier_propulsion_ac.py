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

    def add_mesh(self, name, verts, faces, mat=0, loc=(0, 0, 0), twosided=False):
        self.objects.append(
            {
                "name": name,
                "loc": loc,
                "verts": verts,
                "faces": faces,
                "mat": mat,
                "twosided": twosided,
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

    def disk(self, name, r, x, segs, mat, normal="+x", cy=CY, cz=CZ):
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
        self.add_mesh(name, verts, faces, mat=mat)

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
            lines.append("crease 40.0")
            lines.append(f"numvert {len(obj['verts'])}")
            for x, y, z in obj["verts"]:
                lines.append(f"{x:.6f} {y:.6f} {z:.6f}")
            lines.append(f"numsurf {len(obj['faces'])}")
            surf = "0x30" if obj.get("twosided") else "0x10"
            for face in obj["faces"]:
                lines.append(f"SURF {surf}")
                lines.append(f"mat {obj['mat']}")
                lines.append(f"refs {len(face)}")
                for idx in face:
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
    # Forward + mid plugs — kill sightlines into old engine bay / stub rings
    b.disk("grenadier-aft-bulkhead", 3.95, 11.90, segs, mat_tps_dk, normal="-x")
    b.disk("grenadier-aft-stub-plate", 3.40, 13.10, segs, mat_blank, normal="+x")

    # Explicit blanks over the three heritage SSME mount centers.
    # FG model offsets: xml y→AC Z, xml z→AC Y. SSME1 @ (0,0,0); SSME2/3
    # offset (±1.5, −2.5) → AC (y≈−0.9, z≈±1.5). Disks sit on stub-plate plane.
    for name, cy_i, cz_i, r in (
        ("grenadier-stub-blank-C", 1.60, 0.0, 1.20),
        ("grenadier-stub-blank-L", -0.90, -1.50, 1.10),
        ("grenadier-stub-blank-R", -0.90, 1.50, 1.10),
    ):
        verts = _ring(13.15, r, 24, cy=cy_i, cz=cz_i)
        c = _v(13.15, cy_i, cz_i)
        faces = []
        all_verts = [c] + verts
        for i in range(24):
            faces.append((0, 1 + i, 1 + ((i + 1) % 24)))
        b.add_mesh(name, all_verts, faces, mat=mat_blank)

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

    b.write(OUT / "grenadier_nozzle.ac")


def build_scoop():
    """Forward scoop mouths on heritage OMS pods (pods + RCS stay in OMSPods.ac).

    Do NOT replace the whole pod with boxes (that hid the RCS '4 dots' and made
    planar white slices). Only the forward face becomes an intake; aft RCS remain.
    """
    b = ACBuilder()
    mat_lip = b.add_mat("scoop-lip", (0.35, 0.38, 0.42), amb=0.4, spec=0.45, shi=50)
    mat_dark = b.add_mat("scoop-cavity", (0.04, 0.04, 0.05), amb=0.2, spec=0.08, shi=10)
    mat_door = b.add_mat("scoop-door", (0.55, 0.56, 0.58), amb=0.4, spec=0.35, shi=40)
    mat_duct = b.add_mat("scoop-duct", (0.32, 0.34, 0.38), amb=0.35, spec=0.25, shi=28)
    mat_hinge = b.add_mat("scoop-hinge", (0.22, 0.22, 0.24), amb=0.3, spec=0.3, shi=30)

    # Left (+Z): mouth at forward OMS face (~x=11.9), clearly recessed
    b.box("grenadier-scoop-L-lip", 11.35, 11.95, -0.85, 0.55, 1.35, 2.85, mat=mat_lip)
    b.box("grenadier-scoop-L-cavity", 11.45, 12.55, -0.65, 0.35, 1.50, 2.70, mat=mat_dark)
    # Re-entry doors (close when inlet-sealed) — two leaves
    b.box("grenadier-scoop-L-door-A", 11.38, 11.55, -0.80, -0.05, 1.40, 2.80, mat=mat_door)
    b.box("grenadier-scoop-L-door-B", 11.38, 11.55, 0.05, 0.80, 1.40, 2.80, mat=mat_door)
    b.box("grenadier-scoop-L-hinge", 11.55, 11.70, -0.10, 0.10, 1.45, 2.75, mat=mat_hinge)
    b.box("grenadier-scoop-L-duct", 12.20, 13.50, -0.95, -0.15, 0.40, 1.85, mat=mat_duct)

    # Right (−Z)
    b.box("grenadier-scoop-R-lip", 11.35, 11.95, -0.85, 0.55, -2.85, -1.35, mat=mat_lip)
    b.box("grenadier-scoop-R-cavity", 11.45, 12.55, -0.65, 0.35, -2.70, -1.50, mat=mat_dark)
    b.box("grenadier-scoop-R-door-A", 11.38, 11.55, -0.80, -0.05, -2.80, -1.40, mat=mat_door)
    b.box("grenadier-scoop-R-door-B", 11.38, 11.55, 0.05, 0.80, -2.80, -1.40, mat=mat_door)
    b.box("grenadier-scoop-R-hinge", 11.55, 11.70, -0.10, 0.10, -2.75, -1.45, mat=mat_hinge)
    b.box("grenadier-scoop-R-duct", 12.20, 13.50, -0.95, -0.15, -1.85, -0.40, mat=mat_duct)

    b.box("grenadier-scoop-plenum", 12.20, 13.60, -1.05, -0.05, -0.50, 0.50, mat=mat_duct)

    b.write(OUT / "grenadier_scoop.ac")


def build_internals():
    """Chunky 3-cycle buildout — readable looking forward through the throat.

    Looking into the bell you should read, aft→forward:
      σ1 EDF rotor (silver blades) → stator → σ2 MW farm (green) → σ3 vaporizer.
    The vaned ring is intentional EDF stator hardware, not leftover Shuttle junk.
    """
    b = ACBuilder()
    mat_fan = b.add_mat("edf-fan", (0.78, 0.82, 0.88), amb=0.45, spec=0.6, shi=60, emis=0.03)
    mat_stator = b.add_mat("edf-stator", (0.55, 0.42, 0.22), amb=0.4, spec=0.35, shi=35)
    mat_hub = b.add_mat("edf-hub", (0.20, 0.21, 0.23), amb=0.35, spec=0.4, shi=40)
    mat_duct = b.add_mat("duct", (0.40, 0.42, 0.45), amb=0.4, spec=0.3, shi=30)
    mat_rack = b.add_mat("mw-rack", (0.25, 0.28, 0.32), amb=0.35, spec=0.35, shi=35)
    mat_box = b.add_mat("mw-box", (0.18, 0.55, 0.42), amb=0.4, spec=0.3, shi=30, emis=0.08)
    mat_tube = b.add_mat("plasma-tube", (0.70, 0.55, 0.25), amb=0.4, spec=0.5, shi=50, emis=0.1)
    mat_vap = b.add_mat("vaporizer", (0.55, 0.58, 0.62), amb=0.4, spec=0.45, shi=45)
    mat_cable = b.add_mat("bus-cable", (0.06, 0.06, 0.07), amb=0.25, spec=0.15, shi=12)
    mat_frame = b.add_mat("skid-frame", (0.32, 0.33, 0.34), amb=0.35, spec=0.3, shi=28)
    mat_glow = b.add_mat("stage-glow", (0.35, 0.75, 0.95), amb=0.3, spec=0.2, shi=20, emis=0.3)

    segs = 28

    # Rails
    b.box("grenadier-skid-rail-L", 10.5, 13.9, CY - 0.65, CY - 0.35, CZ - 1.70, CZ - 1.40, mat=mat_frame)
    b.box("grenadier-skid-rail-R", 10.5, 13.9, CY - 0.65, CY - 0.35, CZ + 1.40, CZ + 1.70, mat=mat_frame)

    # Inlet duct — fills view behind throat
    b.lathe_shell(
        "grenadier-edf-duct",
        [(10.5, 1.50), (12.0, 1.50), (13.2, 1.40), (13.85, 1.30)],
        segs,
        mat_duct,
        outward=False,
    )

    # σ1 EDF — pushed aft so it fills the throat when looking forward
    b.lathe_shell("grenadier-edf-hub", [(12.85, 0.40), (13.35, 0.40)], 16, mat_hub, outward=True)
    for i in range(12):
        a0 = 2 * math.pi * i / 12
        a1 = a0 + 0.20
        r0, r1 = 0.40, 1.35
        x0, x1 = 13.00, 13.25
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
    b.disk("grenadier-edf-face", 1.40, 12.80, segs, mat_fan, normal="-x")

    # EDF stator (bronze) — the vaned ring visible in the throat
    for i in range(10):
        a = 2 * math.pi * i / 10
        y0, z0 = CY + 0.35 * math.sin(a), CZ + 0.35 * math.cos(a)
        y1, z1 = CY + 1.30 * math.sin(a), CZ + 1.30 * math.cos(a)
        t = 0.12
        verts = [
            _v(13.40, y0, z0),
            _v(13.40, y1, z1),
            _v(13.75, y1, z1),
            _v(13.75, y0, z0),
            _v(13.40, y0 + t * math.cos(a), z0 - t * math.sin(a)),
            _v(13.40, y1 + t * math.cos(a), z1 - t * math.sin(a)),
            _v(13.75, y1 + t * math.cos(a), z1 - t * math.sin(a)),
            _v(13.75, y0 + t * math.cos(a), z0 - t * math.sin(a)),
        ]
        faces = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
        b.add_mesh(f"grenadier-stator-{i}", verts, faces, mat=mat_stator)

    # σ2 MW farm — green CRC boxes, just ahead of EDF (visible past blades)
    b.box("grenadier-mw-rack", 11.2, 12.7, CY - 1.15, CY + 0.85, CZ - 1.35, CZ + 1.35, mat=mat_rack)
    for i, z in enumerate((-0.85, 0.0, 0.85)):
        b.box(
            f"grenadier-mw-magnetron-{i}",
            11.35,
            12.55,
            CY + 0.70,
            CY + 1.35,
            CZ + z - 0.32,
            CZ + z + 0.32,
            mat=mat_box,
        )
    b.lathe_shell(
        "grenadier-plasma-duct",
        [(11.5, 0.42), (13.5, 0.50)],
        16,
        mat_tube,
        outward=True,
    )
    b.lathe_shell("grenadier-plasma-glow", [(13.0, 0.58), (13.45, 0.72)], 20, mat_glow, outward=True)

    # σ3 vaporizer
    b.lathe_shell("grenadier-vaporizer", [(12.5, 0.55), (13.2, 0.55)], 18, mat_vap, outward=True)
    b.box("grenadier-water-accumulator", 11.4, 12.4, CY - 1.55, CY - 0.95, CZ - 0.45, CZ + 0.45, mat=mat_vap)
    b.box("grenadier-water-feed-run", 10.5, 12.5, CY - 1.25, CY - 1.05, CZ + 0.75, CZ + 0.95, mat=mat_cable)

    b.box("grenadier-bus-coupler", 10.5, 11.2, CY - 1.45, CY - 0.75, CZ - 0.45, CZ + 0.45, mat=mat_hub)
    b.box("grenadier-bus-cable", 9.5, 10.5, CY - 1.20, CY - 0.95, CZ - 0.15, CZ + 0.15, mat=mat_cable)

    b.write(OUT / "grenadier_internals.ac")



def main():
    build_nozzle()
    build_scoop()
    build_internals()


if __name__ == "__main__":
    main()
