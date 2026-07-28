#!/usr/bin/env python3
"""Stretch Shuttle wing mesh to Plan A span/area (visual matches FDM).

Heritage OV: b≈23.79 m, S≈250 m². Plan A: b≈33 m, S≈480 m².
  k_span  = 33/23.79 ≈ 1.387
  k_chord = (480/250)/k_span ≈ 1.385

AC axes (shuttle_o2.ac): +X aft, +Y up, +Z right.

Only wing-bearing objects are warped. Fuselage half-width (|Z|≲3.6 m)
and bay doors stay put. Span map is continuous from the body wall so
the glove does not tear. Chord grows about the root LE station.
"""

from __future__ import annotations

import math
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # Models/
SRC = ROOT / "shuttle_o2_heritage.ac"
DST = ROOT / "shuttle_o2_plan_a.ac"
FALLBACK = ROOT / "shuttle_o2.ac"

# Plan A / heritage
K_SPAN = 33.0 / 23.79
K_CHORD = (480.0 / 249.9) / K_SPAN
Z_BODY = 3.60  # fuselage half-width (upper body |z|max ≈ 3.62)
Z_TIP = 11.93  # outboard elevon tip
X_PIVOT = -1.50  # root LE-ish (heatshield wing min x ≈ -1.52)

# Objects whose vertices participate in the wing warp.
WING_OBJECTS = {
    "fuselage",
    "heatshield",
    "inboard-elevon-left",
    "inboard-elevon-right",
    "outboard-elevon-left",
    "outboard-elevon-right",
    "GearDoorL",
    "GearDoorR",
}

# Elevons / tips: always full wing weight (no body blend).
FULL_WING = {
    "inboard-elevon-left",
    "inboard-elevon-right",
    "outboard-elevon-left",
    "outboard-elevon-right",
}


def k_outboard() -> float:
    """Outboard stretch so tip maps to tip * K_SPAN with body wall fixed."""
    return (Z_TIP * K_SPAN - Z_BODY) / (Z_TIP - Z_BODY)


def map_span(az: float) -> float:
    if az <= Z_BODY:
        return az
    return Z_BODY + k_outboard() * (az - Z_BODY)


def wing_weight(x: float, y: float, z: float, obj: str) -> float:
    """0 = body (unchanged), 1 = full wing (span+chord)."""
    if obj in FULL_WING:
        return 1.0
    az = abs(z)
    # Soft ramp across the wing glove
    if az <= Z_BODY:
        return 0.0
    if az >= 5.5:
        w = 1.0
    else:
        w = (az - Z_BODY) / (5.5 - Z_BODY)
    # Keep tall fuselage sides / OMS shoulders from chord-stretching
    if y > -1.5 and az < 6.0:
        w *= max(0.0, (-y - 0.5) / 2.0)  # fade above belly/wing
    return max(0.0, min(1.0, w))


def transform(x: float, y: float, z: float, obj: str) -> tuple[float, float, float]:
    w = wing_weight(x, y, z, obj)
    az = abs(z)
    # Span: continuous map for outboard structure; blend near body via weight
    if az > Z_BODY:
        az2 = map_span(az)
        # Blend: at w=0 keep az, at w=1 use az2 (elevons always w=1)
        az_new = az + w * (az2 - az)
        z_new = math.copysign(az_new, z)
    else:
        z_new = z

    if w <= 0.0:
        return x, y, z_new

    x_stretched = X_PIVOT + (x - X_PIVOT) * K_CHORD
    x_new = x + w * (x_stretched - x)
    return x_new, y, z_new


def ensure_heritage() -> Path:
    """Keep an untouched heritage copy; seed from shuttle_o2.ac once."""
    if SRC.exists():
        return SRC
    if not FALLBACK.exists():
        raise SystemExit(f"missing {FALLBACK}")
    shutil.copy2(FALLBACK, SRC)
    print(f"seeded heritage copy → {SRC.name}")
    return SRC


def rewrite(src: Path, dst: Path) -> None:
    lines = src.read_text(errors="ignore").splitlines(keepends=True)
    out = []
    obj = None
    collecting = False
    left = 0
    n_vert = 0
    n_changed = 0
    tip_before = 0.0
    tip_after = 0.0

    for line in lines:
        if line.startswith("name "):
            # name "foo" or name foo
            if '"' in line:
                obj = line.split('"')[1]
            else:
                obj = line.split()[1]
            collecting = False
            out.append(line)
            continue

        if line.startswith("numvert") and obj in WING_OBJECTS:
            left = int(line.split()[1])
            collecting = True
            out.append(line)
            continue

        if collecting and left > 0:
            parts = line.split()
            if len(parts) >= 3:
                try:
                    x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
                    tip_before = max(tip_before, abs(z))
                    x2, y2, z2 = transform(x, y, z, obj)
                    tip_after = max(tip_after, abs(z2))
                    if (x2, y2, z2) != (x, y, z):
                        n_changed += 1
                    rest = " ".join(parts[3:])
                    line = f"{x2:.6f} {y2:.6f} {z2:.6f}" + (f" {rest}" if rest else "") + (
                        "\n" if line.endswith("\n") else ""
                    )
                    if not line.endswith("\n") and lines:  # preserve newline style
                        pass
                    n_vert += 1
                except ValueError:
                    pass
            left -= 1
            if left == 0:
                collecting = False
            out.append(line)
            continue

        out.append(line)

    dst.write_text("".join(out))
    print(
        f"wrote {dst.name}: verts_touched≈{n_vert}, changed={n_changed}, "
        f"|z| tip {tip_before:.2f} → {tip_after:.2f} m "
        f"(span≈{2*tip_after:.2f} m), k_span={K_SPAN:.3f}, k_chord={K_CHORD:.3f}"
    )


def hinge_report() -> None:
    """Print updated elevon hinge suggestions (FG: x aft, y lateral=AC z, z up=AC y)."""
    # Heritage hinges
    hinges = [
        ("left", 9.2, 0.0, -4.1, 8.5, 10.0, -4.1),
        ("right", 9.2, 0.0, -4.1, 8.5, -10.0, -4.1),
    ]
    print("elevon hinge suggestions (animation y = AC z):")
    for name, x1, y1, z1, x2, y2, z2 in hinges:
        # Transform as elevon (full wing). Animation y ↔ AC z, z ↔ AC y.
        ax1, ay1, az1 = transform(x1, z1, y1, "outboard-elevon-left")  # careful mapping
        # Better: treat (x, anim_z as AC_y, anim_y as AC_z)
        def map_hinge(x, anim_y, anim_z):
            ac_x, ac_y, ac_z = x, anim_z, anim_y
            nx, ny, nz = transform(ac_x, ac_y, ac_z, "outboard-elevon-left")
            return nx, nz, ny  # back to anim x,y,z

        x1n, y1n, z1n = map_hinge(x1, y1, z1)
        x2n, y2n, z2n = map_hinge(x2, y2, z2)
        print(
            f"  {name}: "
            f"({x1n:.2f},{y1n:.2f},{z1n:.2f}) → ({x2n:.2f},{y2n:.2f},{z2n:.2f})"
        )


def close_elevon_seams(path: Path) -> None:
    """Pull elevon LE forward onto wing TE where stretch left a gap (IB root ~0.3 m)."""
    lines = path.read_text(errors="ignore").splitlines(keepends=True)
    # Parse elevon LE targets and wing TE after stretch is already in file.
    elev_names = {
        "inboard-elevon-left",
        "inboard-elevon-right",
        "outboard-elevon-left",
        "outboard-elevon-right",
    }
    # First pass: collect wing TE candidates from fuselage+heatshield
    wing_verts = []
    obj = None
    collecting = False
    left = 0
    for line in lines:
        if line.startswith("name "):
            obj = line.split('"')[1] if '"' in line else line.split()[1]
            collecting = False
            continue
        if line.startswith("numvert") and obj in ("fuselage", "heatshield"):
            left = int(line.split()[1])
            collecting = True
            continue
        if collecting and left > 0:
            parts = line.split()
            if len(parts) >= 3:
                try:
                    wing_verts.append(tuple(map(float, parts[:3])))
                except ValueError:
                    pass
            left -= 1
            if left == 0:
                collecting = False

    def wing_te_x(z: float, y: float) -> float | None:
        cands = [
            w
            for w in wing_verts
            if abs(w[2] - z) < 0.45 and abs(w[1] - y) < 1.2 and w[1] < -2.0
        ]
        if not cands:
            cands = [w for w in wing_verts if abs(w[2] - z) < 0.6 and w[1] < -2.5]
        if not cands:
            return None
        # Prefer verts near elevon hinge station (x ~ 12–15 after stretch)
        near = [w for w in cands if 12.0 < w[0] < 15.5]
        pool = near if near else cands
        return max(w[0] for w in pool)

    out = []
    obj = None
    collecting = False
    left = 0
    n_fix = 0
    for line in lines:
        if line.startswith("name "):
            obj = line.split('"')[1] if '"' in line else line.split()[1]
            collecting = False
            out.append(line)
            continue
        if line.startswith("numvert") and obj in elev_names:
            left = int(line.split()[1])
            collecting = True
            out.append(line)
            continue
        if collecting and left > 0:
            parts = line.split()
            if len(parts) >= 3:
                try:
                    x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
                    # LE-ish: forward half of this elevon (smaller x)
                    # Pull forward if wing TE is ahead of elevon (gap)
                    te = wing_te_x(z, y)
                    if te is not None and x > te + 0.05:
                        # Only adjust verts that are on the LE (not TE of elevon)
                        # Heuristic: if x is within 0.4 of the object's min we'll
                        # handle via comparing to local — use absolute: LE < 15.2
                        if x < 15.2:
                            x = te - 0.04  # slight overlap onto wing
                            n_fix += 1
                    rest = " ".join(parts[3:])
                    nl = "\n" if line.endswith("\n") else ""
                    line = f"{x:.6f} {y:.6f} {z:.6f}" + (f" {rest}" if rest else "") + nl
                except ValueError:
                    pass
            left -= 1
            if left == 0:
                collecting = False
            out.append(line)
            continue
        out.append(line)

    path.write_text("".join(out))
    print(f"elevon seam close: adjusted {n_fix} LE verts in {path.name}")


def main() -> None:
    src = ensure_heritage()
    rewrite(src, DST)
    close_elevon_seams(DST)
    hinge_report()
    print(f"heritage={SRC.name}  plan_a={DST.name}")


if __name__ == "__main__":
    main()
