#!/usr/bin/env python3
"""Strip OMS engine bells/bases from OMSPods.ac — keep pod shells + RCS only.

Preserves the AC3D kids hierarchy. A prior flat rewrite left omsLeft kids=13
after dropping the engine objects, so loaders parented omsRight under omsLeft
and double-applied its loc offset (right pod wrecked in FG and Blender).
"""

from __future__ import annotations

from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "OMSPods.ac"
DST = Path(__file__).resolve().parents[1] / "OMSPods_grenadier.ac"

DROP = {"omsLeft.001", "omsRight.001", "omsLeftBase", "omsRightBase"}


def obj_name(block: list[str]) -> str | None:
    for line in block:
        if line.startswith("name "):
            if '"' in line:
                return line.split('"')[1]
            return line.split()[1]
    return None


def obj_kids(block: list[str]) -> int:
    for line in block:
        if line.startswith("kids "):
            return int(line.split()[1])
    return 0


def set_kids(block: list[str], n: int) -> list[str]:
    return [f"kids {n}" if line.startswith("kids ") else line for line in block]


def split_file(lines: list[str]) -> tuple[list[str], list[list[str]]]:
    i = 0
    while i < len(lines) and not lines[i].startswith("OBJECT"):
        i += 1
    if i >= len(lines):
        raise SystemExit("no OBJECT in OMSPods.ac")
    header = lines[:i]
    objs: list[list[str]] = []
    k = i
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


def prune_forest(objs: list[list[str]], start: int, count: int) -> tuple[list[list[str]], int]:
    """Keep `count` siblings from `start`, dropping DROP nodes (and their subtrees)."""
    kept: list[list[str]] = []
    i = start
    for _ in range(count):
        if i >= len(objs):
            break
        block = objs[i]
        name = obj_name(block)
        n_kids = obj_kids(block)
        i += 1
        children, i = prune_forest(objs, i, n_kids)
        if name in DROP:
            continue
        kept.append(set_kids(block, len(children)))
        kept.extend(children)
    return kept, i


def main() -> None:
    lines = SRC.read_text(errors="ignore").splitlines()
    header, objs = split_file(lines)
    if not objs:
        raise SystemExit("empty OMSPods.ac")

    world = objs[0]
    forest, _ = prune_forest(objs, 1, obj_kids(world))

    # Count world-direct children from updated kids on preorder roots.
    roots = 0
    i = 0
    while i < len(forest):
        roots += 1
        n = obj_kids(forest[i])
        i += 1
        # skip descendants via their own kids counts
        stack = [n]
        while stack:
            left = stack.pop()
            for _ in range(left):
                if i >= len(forest):
                    break
                stack.append(obj_kids(forest[i]))
                i += 1

    out = header + set_kids(world, roots)
    for block in forest:
        out.extend(block)
    DST.write_text("\n".join(out) + "\n")

    print(f"wrote {DST.name}: {len(forest)} objs, world kids={roots}")
    i = 0
    while i < len(forest):
        nm = obj_name(forest[i])
        nk = obj_kids(forest[i])
        print(f"  root {nm} kids={nk}")
        # advance past this root's subtree
        i += 1
        stack = [nk]
        while stack:
            left = stack.pop()
            for _ in range(left):
                if i >= len(forest):
                    break
                stack.append(obj_kids(forest[i]))
                i += 1


if __name__ == "__main__":
    main()
