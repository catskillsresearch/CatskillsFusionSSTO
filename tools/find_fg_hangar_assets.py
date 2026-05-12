#!/usr/bin/env python3
"""
Scan FlightGear scenery paths for hangar-related model assets.
Usage (from repo root):
  python3 tools/find_fg_hangar_assets.py
  python3 tools/find_fg_hangar_assets.py -m           # drop .png etc. (~291 → ~few dozen)
  python3 tools/find_fg_hangar_assets.py -m --summary # counts by folder only

Checks, in order:
  1) ./FlightGear  symlink (typically ~/.fgfs) — TerraSync subdir if populated
  2) /usr/share/games/flightgear/Scenery  — Ubuntu apt package stock data

Note: These are 3D models used *in* airport .stg layouts. Whether a given airport
places an "open" hangar is in per-airport scenery, often TerraSync (yours may be empty).
"""
from __future__ import annotations

import argparse
import os
import sys
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FG_LINK = os.path.join(REPO, "FlightGear")
SYSTEM_SCENERY = "/usr/share/games/flightgear/Scenery"

KEYWORDS = ("hangar", "hangars", "hush-house", "hush_house", "shed_airport")
MODEL_SUFFIXES = {".ac", ".xml"}


def iter_files(root: str, models_only: bool):
    if not os.path.isdir(root):
        return
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            low = name.lower()
            if models_only:
                stem, ext = os.path.splitext(low)
                if ext not in MODEL_SUFFIXES:
                    continue
            if any(k in low for k in KEYWORDS):
                yield os.path.join(dirpath, name)


def summarize_dirs(root: str, paths: list[str]):
    rel_dirs = Counter()
    for p in paths:
        d = os.path.dirname(os.path.relpath(p, root))
        rel_dirs[d] += 1
    for d, n in sorted(rel_dirs.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {n:4}  {d}")


def main():
    ap = argparse.ArgumentParser(description="List FlightGear scenery files related to hangars.")
    ap.add_argument(
        "-m",
        "--models-only",
        action="store_true",
        help="Only .ac and .xml (skip textures — much shorter list).",
    )
    ap.add_argument(
        "--summary",
        action="store_true",
        help="Print per-folder counts instead of full paths.",
    )
    args = ap.parse_args()

    roots = []
    terrasync = os.path.join(FG_LINK, "TerraSync")
    if os.path.isdir(terrasync):
        roots.append(("TerraSync (via ./FlightGear)", terrasync))
    if os.path.isdir(SYSTEM_SCENERY):
        roots.append(("system Scenery (apt)", SYSTEM_SCENERY))

    if not roots:
        print("No scenery roots found. Install flightgear-data or sync TerraSync.", file=sys.stderr)
        sys.exit(1)

    total = 0
    for label, root in roots:
        print(f"\n### {label}: {root}\n")
        paths = sorted(iter_files(root, models_only=args.models_only))
        if not paths:
            print("  (no matching filenames — empty tree is normal for TerraSync until you download.)")
            continue

        if args.summary:
            summarize_dirs(root, paths)
        else:
            for p in paths:
                print(p)
        total += len(paths)

    print(f"\nTotal matching files ({'models only' if args.models_only else 'all'}): {total}")
    print(
        "\nInterior note: stock hangar .ac models are usually shells; "
        "true interiors are rare. Use ramp parking near hangar models, or place your own model."
    )


if __name__ == "__main__":
    main()
