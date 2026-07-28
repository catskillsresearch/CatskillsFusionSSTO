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


def _parse_named_verts(lines: list[str], names: set[str]) -> dict[str, list[tuple[float, float, float]]]:
    out: dict[str, list[tuple[float, float, float]]] = {n: [] for n in names}
    obj = None
    collecting = False
    left = 0
    for line in lines:
        if line.startswith("name "):
            obj = line.split('"')[1] if '"' in line else line.split()[1]
            collecting = False
            continue
        if line.startswith("numvert") and obj in names:
            left = int(line.split()[1])
            collecting = True
            continue
        if collecting and left > 0:
            parts = line.split()
            if len(parts) >= 3:
                try:
                    out[obj].append(tuple(map(float, parts[:3])))  # type: ignore[arg-type]
                except ValueError:
                    pass
            left -= 1
            if left == 0:
                collecting = False
    return out


def _elevon_le_samples(elev_verts: dict[str, list[tuple[float, float, float]]]) -> list[tuple[float, float]]:
    """(|z|, x_le) samples along both elevons — flap hinge line."""
    samples: list[tuple[float, float]] = []
    for verts in elev_verts.values():
        if not verts:
            continue
        xs = [v[0] for v in verts]
        xmin, xmax = min(xs), max(xs)
        thr = xmin + 0.18 * (xmax - xmin)
        for x, _y, z in verts:
            if x <= thr:
                samples.append((abs(z), x))
    samples.sort()
    # Bin by |z| and keep min x (true LE) per bin
    bins: dict[float, float] = {}
    for az, x in samples:
        key = round(az * 4.0) / 4.0
        bins[key] = x if key not in bins else min(bins[key], x)
    return sorted(bins.items())


def _interp_le(samples: list[tuple[float, float]], az: float) -> float | None:
    if not samples:
        return None
    if az <= samples[0][0]:
        return samples[0][1]
    if az >= samples[-1][0]:
        return samples[-1][1]
    for (z0, x0), (z1, x1) in zip(samples, samples[1:]):
        if z0 <= az <= z1:
            t = 0.0 if z1 <= z0 else (az - z0) / (z1 - z0)
            return x0 + t * (x1 - x0)
    return None


def pull_wing_te_to_flap_line(path: Path) -> None:
    """Pull wing TE aft to a straight elevon-LE flap line (no overlay 'tape').

    Plan A chord stretch leaves the TE short/curved inboard of the tip; the old
    fix laid scotch-tape skins over the gap. Instead, move the wing mesh's own
    trailing-edge verts aft onto the elevon leading-edge line.
    """
    lines = path.read_text(errors="ignore").splitlines(keepends=True)
    elev_names = {
        "inboard-elevon-left",
        "inboard-elevon-right",
        "outboard-elevon-left",
        "outboard-elevon-right",
    }
    wing_names = {"fuselage", "heatshield"}
    elev = _parse_named_verts(lines, elev_names)
    wing = _parse_named_verts(lines, wing_names)
    samples = _elevon_le_samples(elev)
    if len(samples) < 2:
        print("pull_wing_te_to_flap_line: no elevon LE samples — skipped")
        return

    # Per-|z| bin: aft-most x and chord. Keep bins that look like a real wing
    # section (decent aft TE, or enough chord that the aft lip is a cutout edge).
    bin_xs: dict[float, list[float]] = {}
    for verts in wing.values():
        for x, y, z in verts:
            az = abs(z)
            if az < 2.55 or az > 16.7:
                continue
            if y > -3.70 or y < -5.45:
                continue
            key = round(az * 4.0) / 4.0
            bin_xs.setdefault(key, []).append(x)
    local_te: dict[float, float] = {}
    for key, xs in bin_xs.items():
        te, x0 = max(xs), min(xs)
        chord = te - x0
        if te >= 4.0 or (chord >= 1.5 and te >= 0.8):
            local_te[key] = te

    def near_local_te(x: float, az: float) -> float | None:
        """Return local TE x if this vert sits on the TE lip."""
        best = None
        best_dz = 0.40
        for key, te in local_te.items():
            dz = abs(key - az)
            if dz <= best_dz and x >= te - 0.40:
                best_dz = dz
                best = te
        return best

    out: list[str] = []
    obj = None
    collecting = False
    left = 0
    n_fix = 0
    max_pull = 0.0
    for line in lines:
        if line.startswith("name "):
            obj = line.split('"')[1] if '"' in line else line.split()[1]
            collecting = False
            out.append(line)
            continue
        if line.startswith("numvert") and obj in wing_names:
            left = int(line.split()[1])
            collecting = True
            out.append(line)
            continue
        if collecting and left > 0:
            parts = line.split()
            if len(parts) >= 3:
                try:
                    x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
                    az = abs(z)
                    tgt = _interp_le(samples, az)
                    if (
                        tgt is not None
                        and 2.55 <= az <= 16.7
                        and -5.45 <= y <= -3.70
                        and x >= 0.5
                    ):
                        te = near_local_te(x, az)
                        # Only pull TE lip verts that fall short of the flap line.
                        if te is not None and x < tgt - 0.02:
                            new_x = tgt - 0.03
                            pull = new_x - x
                            # Real shortfalls are ~0.5–13 m (inboard cutout → flap).
                            if 0.02 < pull <= 13.0:
                                x = new_x
                                n_fix += 1
                                max_pull = max(max_pull, pull)
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
    z0, x0 = samples[0]
    z1, x1 = samples[-1]
    print(
        f"wing TE → flap line: moved {n_fix} TE verts (max pull {max_pull:.2f} m); "
        f"LE line |z|={z0:.2f}→{z1:.2f} x={x0:.2f}→{x1:.2f}"
    )


def main() -> None:
    src = ensure_heritage()
    rewrite(src, DST)
    pull_wing_te_to_flap_line(DST)
    hinge_report()
    print(f"heritage={SRC.name}  plan_a={DST.name}")


if __name__ == "__main__":
    main()
