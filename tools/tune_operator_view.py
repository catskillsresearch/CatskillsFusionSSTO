#!/usr/bin/env python3
"""Launch Orbitron-TestStand, screenshot Operator View, score, search for best eye/aim.

Usage:
  python3 tools/tune_operator_view.py --quick
  python3 tools/tune_operator_view.py --apply-best

Requires: fgfs, DISPLAY or xvfb-run, Pillow, BIKF scenery (same as fs.sh).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
NASAL_SPEC = REPO / "ssto/orbitron/assembly_specs/orbitron_nasal.yaml"
AIRCRAFT_SPEC = REPO / "ssto/orbitron/assembly_specs/orbitron_aircraft_flightgear.yaml"
PHYSICS_SPEC = REPO / "ssto/orbitron/assembly_specs/orbitron_physics_surrogate.yaml"
OUT_DIR = REPO / "Aircraft/Orbitron-TestStand/build/view_tune"
PKG = (
    subprocess.check_output(
        ["python3", str(REPO / "tools/orbitron_aircraft_paths.py"), "package_dir", "--repo-root", str(REPO)],
        text=True,
    )
    .strip()
)
STAND = REPO / "Aircraft" / PKG

# Mesh centres (orbitron.ac, metres).
SCREEN = (-1.4, 1.6, 4.5)
CONSOLE = (-1.4, 0.96, 4.83)
H2_TANK = (0.60, 1.04, -1.2)


def _mesh_candidates() -> list[tuple[tuple[float, float, float], tuple[float, float, float], str]]:
    """Seed grid from AC layout: operator on −Y side, eye at console height, aim at Screen."""
    ex, ey, ez = CONSOLE[0], -0.35, CONSOLE[2]
    seeds: list[tuple[tuple[float, float, float], tuple[float, float, float], str]] = [
        ((ex, ey, ez), SCREEN, "console_height_aim_screen"),
        ((ex, -0.55, ez), SCREEN, "port_055"),
        ((ex, -0.85, ez), SCREEN, "port_085"),
        ((ex, -0.25, 4.85), SCREEN, "low_port"),
        ((CONSOLE[0], -0.45, 4.5), (-1.4, 1.6, 4.5), "mid_height"),
        ((ex, ey, 4.5), SCREEN, "eye_at_screen_z"),
    ]
    # Avoid aim through H₂ cluster (low z, +X).
    extra = []
    for ey2 in (-0.25, -0.45, -0.65, -0.85):
        for ez2 in (4.75, 4.9, 5.05):
            extra.append(((ex, ey2, ez2), SCREEN, f"grid_{ey2}_{ez2}"))
    return seeds + extra


def _patch_yaml_operator(eye: tuple[float, float, float], target: tuple[float, float, float]) -> None:
    text = NASAL_SPEC.read_text()
    block = (
        "  operator_view:\n"
        "    # AC frame (+X fwd toward rig, +Y right, +Z up). Port side of desk, level look at screen.\n"
        f"    eye: [{eye[0]}, {eye[1]}, {eye[2]}]\n"
        f"    target: [{target[0]}, {target[1]}, {target[2]}]\n"
    )
    text = re.sub(
        r"  operator_view:\n(?:    .*\n)*?(?=  startup_view_number:)",
        block,
        text,
        count=1,
    )
    NASAL_SPEC.write_text(text)

    atext = AIRCRAFT_SPEC.read_text()
    ablock = (
        "  view_operator:\n"
        "    name: Operator View\n"
        "    # Body lookat — tuned by tools/tune_operator_view.py\n"
        "    type: lookat\n"
        "    # use_ac_lookat_direct: false — compiler maps AC → FG (X, Y, Z)\n"
        f"    eye_offset_m: [{eye[0]}, {eye[1]}, {eye[2]}]\n"
        f"    aim_offset_m: [{target[0]}, {target[1]}, {target[2]}]\n"
        "    view_index: 2\n"
        "    internal: false\n"
        "    limits_enabled: false\n"
        "    ground_level_nearplane_m: 0.05\n"
        "    field_of_view_deg: 52.0\n"
    )
    atext = re.sub(
        r"  view_operator:\n(?:    .*\n)*?(?=  view_pad_overview:)",
        ablock,
        atext,
        count=1,
    )
    AIRCRAFT_SPEC.write_text(atext)


def _compile() -> None:
    subprocess.run(
        [
            "python3",
            str(REPO / "tools/compile_orbitron_nasal.py"),
            "--spec",
            str(NASAL_SPEC),
            "--out-dir",
            str(STAND / "Nasal"),
            "--surrogate-json",
            str(STAND / "engine_surrogate.json"),
        ],
        check=True,
        cwd=REPO,
    )
    subprocess.run(
        [
            "python3",
            str(REPO / "tools/compile_orbitron_aircraft_runtime.py"),
            "--aircraft-spec",
            str(AIRCRAFT_SPEC),
            "--physics-spec",
            str(PHYSICS_SPEC),
            "--out-dir",
            str(STAND),
        ],
        check=True,
        cwd=REPO,
    )


def _fg_env() -> dict[str, str]:
    env = os.environ.copy()
    fg_home = Path.home() / ".fgfs"
    fgdata = Path(os.environ.get("FG_ROOT", fg_home / "fgdata_2024_1"))
    env["FG_SCENERY"] = os.environ.get("FG_SCENERY", str(fgdata / "Scenery"))
    return env


def _latest_png(directory: Path) -> Path | None:
    pngs = sorted(directory.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
    return pngs[0] if pngs else None


def _telnet_set(port: int, path: str, value: float | int) -> None:
    msg = f"set {path} {value}\r\n".encode()
    with socket.create_connection(("127.0.0.1", port), timeout=2.0) as sock:
        sock.sendall(msg)
        time.sleep(0.05)


def _run_fg_screenshot(
    png: Path,
    telnet_port: int,
    wait_s: float,
    use_xvfb: bool,
) -> bool:
    subprocess.run(["pkill", "-f", f"fgfs.*{PKG}"], stderr=subprocess.DEVNULL)
    time.sleep(0.5)
    fg_home = Path.home() / ".fgfs"
    (fg_home / "fgfs_lock.pid").unlink(missing_ok=True)

    env = _fg_env()
    scenery = env["FG_SCENERY"]
    terr = Path(scenery) / "Terrain/w030n60/w022n63"
    if not terr.is_dir():
        print(f"error: missing BIKF scenery at {terr}", file=sys.stderr)
        return False

    shot_dir = png.parent
    shot_dir.mkdir(parents=True, exist_ok=True)
    props = [
        f"--prop:/sim/model/orbitron/view-tune/screenshot-path={shot_dir}",
        "--prop:/sim/model/orbitron/view-tune/trigger=0",
        "--prop:/sim/current-view/view-number=2",
    ]
    cmd = [
        "fgfs",
        f"--fg-aircraft={REPO / 'Aircraft'}",
        f"--aircraft={PKG}",
        "--composite-viewer=0",
        "--lat=63.98187",
        "--lon=-22.5884",
        "--altitude=158",
        "--heading=0",
        "--timeofday=noon",
        f"--fg-scenery={scenery}",
        "--disable-terrasync",
        "--terrasync-dir=/tmp/fg-terrasync-unused",
        "--splash-screen=0",
        "--ai-traffic=0",
        "--ai-models=0",
        "--real-weather-fetch=0",
        "--clouds3d=0",
        f"--telnet=socket,bi,60,localhost,{telnet_port},tcp",
        "--prop:/sim/presets/trim=false",
        "--prop:/sim/presets/latitude-deg=63.98187",
        "--prop:/sim/presets/longitude-deg=-22.5884",
        "--prop:/sim/presets/heading-deg=0",
        "--prop:/sim/presets/onground=false",
        "--prop:/sim/presets/altitude-ft=158",
        "--prop:/sim/ai/enabled=false",
        "--prop:/sim/ai/scenarios-enabled=false",
        "--prop:/sim/atc/enabled=false",
        "--prop:/sim/mp-carriers/enabled=false",
        "--prop:/sim/model/reactor/debug-ui-window=false",
        *props,
    ]
    if use_xvfb:
        cmd = ["xvfb-run", "-a", *cmd]

    proc = subprocess.Popen(cmd, cwd=REPO, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    ok = False
    deadline = time.time() + wait_s + 12.0
    while time.time() < deadline:
        if proc.poll() is not None:
            break
        found = _latest_png(shot_dir)
        if found and found.stat().st_size > 50_000:
            shutil.copy2(found, png)
            ok = True
            break
        time.sleep(0.5)
    if not ok and proc.poll() is None:
        try:
            _telnet_set(telnet_port, "/sim/model/orbitron/view-tune/trigger", 0)
        except OSError:
            pass
        for _ in range(24):
            time.sleep(0.5)
            found = _latest_png(shot_dir)
            if found and found.stat().st_size > 50_000:
                shutil.copy2(found, png)
                ok = True
                break
    if not ok and shutil.which("scrot") and proc.poll() is None:
        try:
            subprocess.run(["scrot", "-u", str(png)], timeout=5, check=False)
            ok = png.is_file() and png.stat().st_size > 10_000
        except (subprocess.SubprocessError, OSError):
            pass
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    return ok and png.is_file()


def _score_png(path: Path) -> float:
    try:
        from PIL import Image
    except ImportError:
        print("warning: Pillow not installed — using file size only", file=sys.stderr)
        return float(path.stat().st_size)

    im = Image.open(path).convert("RGB")
    w, h = im.size
    px = im.load()
    green = sky = ground = dark = 0
    n = 0
    for y in range(int(h * 0.15), int(h * 0.85), max(1, h // 80)):
        for x in range(int(w * 0.2), int(w * 0.8), max(1, w // 80)):
            r, g, b = px[x, y]
            n += 1
            if g > 80 and g > r * 1.2 and g > b * 1.1:
                green += 1
            if b > 150 and b > r and g < b * 0.95:
                sky += 1
            if 90 < r < 140 and 90 < g < 140 and 90 < b < 140:
                ground += 1
            if r < 40 and g < 40 and b < 40:
                dark += 1
    if n == 0:
        return -1e9
    gr, sr, dr = green / n, sky / n, dark / n
  # Want green screen visible; penalize empty horizon (sky + grey ground, no structure).
    structure = 1.0 - min(sr + ground / n * 0.5, 1.0)
    return gr * 200.0 + structure * 40.0 - sr * 80.0 - max(0.0, 0.45 - dr) * 20.0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quick", action="store_true", help="Fewer candidates")
    ap.add_argument("--apply-best", action="store_true", help="Write best from last run to YAML")
    ap.add_argument("--xvfb", action="store_true", help="Force xvfb-run")
    ap.add_argument("--wait", type=float, default=18.0, help="Seconds before screenshot")
    ap.add_argument("--port", type=int, default=5509)
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results_path = OUT_DIR / "results.json"

    if args.apply_best:
        if not results_path.is_file():
            print("No results.json — run tune first", file=sys.stderr)
            return 1
        data = json.loads(results_path.read_text())
        best = data["best"]
        eye = tuple(best["eye"])
        tgt = tuple(best["target"])
        _patch_yaml_operator(eye, tgt)
        _compile()
        print(f"Applied best ({best['label']}) score={best['score']:.2f}")
        print(f"  eye={eye} target={tgt}")
        return 0

    cands = _mesh_candidates()
    if args.quick:
        cands = cands[:6]

    use_xvfb = args.xvfb or not os.environ.get("DISPLAY")
    results: list[dict[str, Any]] = []

    for i, (eye, tgt, label) in enumerate(cands):
        print(f"[{i + 1}/{len(cands)}] {label} eye={eye} tgt={tgt}")
        _patch_yaml_operator(eye, tgt)
        _compile()
        png = OUT_DIR / f"{i:02d}_{label}.png"
        png.unlink(missing_ok=True)
        if not _run_fg_screenshot(png, args.port, args.wait, use_xvfb):
            print("  screenshot failed")
            results.append({"label": label, "eye": eye, "target": tgt, "score": -1e9, "png": str(png)})
            continue
        sc = _score_png(png)
        print(f"  score={sc:.2f} -> {png.name}")
        results.append({"label": label, "eye": list(eye), "target": list(tgt), "score": sc, "png": str(png)})

    best = max(results, key=lambda r: r["score"])
    payload = {"best": best, "all": results, "screen": list(SCREEN), "console": list(CONSOLE)}
    results_path.write_text(json.dumps(payload, indent=2))
    print(f"\nBest: {best['label']} score={best['score']:.2f}")
    print(f"  eye={tuple(best['eye'])} target={tuple(best['target'])}")
    print(f"Run: python3 tools/tune_operator_view.py --apply-best")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
