#!/usr/bin/env python3
"""Strip OMS engine bells/bases from OMSPods.ac — keep pod shells + RCS only."""

from __future__ import annotations

from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "OMSPods.ac"
DST = Path(__file__).resolve().parents[1] / "OMSPods_grenadier.ac"

DROP = {"omsLeft.001", "omsRight.001", "omsLeftBase", "omsRightBase"}


def split_objects(lines: list[str]) -> tuple[list[str], list[list[str]]]:
    """Return (header_lines including world opener), list of object blocks."""
    # Header = everything through world object's kids line
    i = 0
    while i < len(lines) and not lines[i].startswith("OBJECT"):
        i += 1
    # include world OBJECT … kids N
    if i >= len(lines):
        raise SystemExit("no OBJECT in OMSPods.ac")
    header_end = i
    # world block until kids
    j = i + 1
    while j < len(lines) and not lines[j].startswith("kids "):
        if lines[j].startswith("OBJECT") and j > i:
            break
        j += 1
    if j < len(lines) and lines[j].startswith("kids "):
        header = lines[: j + 1]
        rest_start = j + 1
    else:
        header = lines[: i + 1]
        rest_start = i + 1

    objs: list[list[str]] = []
    k = rest_start
    while k < len(lines):
        if not lines[k].startswith("OBJECT"):
            k += 1
            continue
        start = k
        k += 1
        while k < len(lines) and not lines[k].startswith("OBJECT"):
            k += 1
        objs.append(lines[start:k])
    return header, objs


def obj_name(block: list[str]) -> str | None:
    for line in block:
        if line.startswith("name "):
            if '"' in line:
                return line.split('"')[1]
            return line.split()[1]
    return None


def main() -> None:
    lines = SRC.read_text(errors="ignore").splitlines()
    header, objs = split_objects(lines)
    kept = []
    dropped = []
    for block in objs:
        nm = obj_name(block)
        if nm in DROP:
            dropped.append(nm)
            continue
        kept.append(block)

    # Fix world kids count
    out_header = list(header)
    for i, line in enumerate(out_header):
        if line.startswith("kids "):
            out_header[i] = f"kids {len(kept)}"
            break

    out_lines = out_header + [ln for block in kept for ln in block]
    DST.write_text("\n".join(out_lines) + "\n")
    print(f"wrote {DST.name}: kept {len(kept)} objs, dropped {dropped}")


if __name__ == "__main__":
    main()
