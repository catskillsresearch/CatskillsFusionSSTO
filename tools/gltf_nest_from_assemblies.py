#!/usr/bin/env python3
"""Rewrite orbitron_lab_v5.gltf node tree to match orbitron_logical_assemblies.json.

CadQuery emits one root with all mesh nodes as direct children. This script inserts
assembly empties so Blender (and other glTF viewers) show the same nesting as the
JSON: one root (default name fusion_arcjet_engine) and recursive assembly nodes,
with mesh leaves unchanged (same node indices, names, transforms).

Run after full_reactor_cad.py; before build_ac3d.py. Requires stdlib only.
"""
from __future__ import annotations

import argparse
import copy
import json
import shutil
import sys
from pathlib import Path
from typing import Any


def mesh_parts_list(spec: dict[str, Any]) -> list[str]:
    mp = spec.get("mesh_parts")
    if mp is not None:
        return [str(x) for x in mp]
    return [str(x) for x in spec.get("parts", [])]


def load_assemblies(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "groups" not in data or "root" not in data:
        raise ValueError("assemblies file needs root and groups")
    return data


def collect_mesh_names(groups: dict[str, Any], root_key: str) -> set[str]:
    found: set[str] = set()

    def visit(key: str) -> None:
        spec = groups[key]
        if spec.get("logical_only"):
            return
        for mk in spec.get("members", []):
            visit(mk)
        for p in mesh_parts_list(spec):
            found.add(p)

    visit(root_key)
    return found


def validate_assemblies_for_gltf(mesh_in_gltf: set[str], data: dict[str, Any]) -> None:
    root = str(data["root"])
    groups: dict[str, Any] = data["groups"]
    if root not in groups:
        raise ValueError(f"root {root!r} missing from groups")

    json_meshes = collect_mesh_names(groups, root)
    missing = sorted(mesh_in_gltf - json_meshes)
    extra = sorted(json_meshes - mesh_in_gltf)
    if missing:
        raise ValueError(
            "assemblies JSON missing mesh names present in glTF: " + ", ".join(missing)
        )
    if extra:
        raise ValueError(
            "assemblies JSON lists mesh names not in glTF: " + ", ".join(extra)
        )


def nest_gltf_nodes(
    gltf: dict[str, Any],
    groups: dict[str, Any],
    root_key: str,
    root_node_name: str,
) -> None:
    nodes: list[dict[str, Any]] = gltf["nodes"]
    name_to_mesh_node: dict[str, int] = {}
    for i, n in enumerate(nodes):
        if n.get("mesh") is not None and n.get("name"):
            name_to_mesh_node[str(n["name"])] = i

    def append_node(node: dict[str, Any]) -> int:
        idx = len(nodes)
        nodes.append(node)
        return idx

    def build_group(key: str) -> int:
        spec = groups[key]
        if spec.get("logical_only"):
            return append_node({"name": key})

        idx = append_node({"name": key, "children": []})
        child_indices: list[int] = []
        for mk in spec.get("members", []):
            child_indices.append(build_group(str(mk)))
        for pname in mesh_parts_list(spec):
            mi = name_to_mesh_node.get(pname)
            if mi is None:
                raise ValueError(f"mesh {pname!r} not found in glTF nodes")
            child_indices.append(mi)
        nodes[idx]["children"] = child_indices
        return idx

    # Scene root: reuse node 0 (keeps rotation etc.), replace name + children.
    if nodes[0].get("mesh") is not None:
        raise ValueError("expected glTF root node 0 to be a group (no mesh)")
    root_spec = groups[root_key]
    top_members = [str(m) for m in root_spec.get("members", [])]
    if not top_members:
        raise ValueError("root group has no members")

    top_indices = [build_group(mk) for mk in top_members]
    nodes[0]["name"] = root_node_name
    nodes[0]["children"] = top_indices

    # Sanity: each mesh node appears exactly once as a child.
    seen_mesh_parents: set[int] = set()

    def walk_children(parent_idx: int, ch: list[int] | None) -> None:
        if not ch:
            return
        for c in ch:
            if c < 0 or c >= len(nodes):
                raise ValueError(f"invalid child index {c} under parent {parent_idx}")
            cn = nodes[c]
            if cn.get("mesh") is not None:
                if c in seen_mesh_parents:
                    raise ValueError(f"mesh node {c} ({cn.get('name')}) parented twice")
                seen_mesh_parents.add(c)
            walk_children(c, cn.get("children"))

    walk_children(0, nodes[0].get("children"))
    if seen_mesh_parents != set(name_to_mesh_node.values()):
        missing = set(name_to_mesh_node.values()) - seen_mesh_parents
        raise RuntimeError(f"some mesh nodes never attached under new tree: {missing}")


def align_sidecar_bin_to_stem(gltf_path: Path, gltf: dict[str, Any]) -> None:
    """If buffer URI basename != <stem>.bin, copy buffer file and fix URI (Makefile cp rename)."""
    stem = gltf_path.stem
    want = f"{stem}.bin"
    parent = gltf_path.parent
    for buf in gltf.get("buffers") or []:
        uri = buf.get("uri")
        if not uri or not isinstance(uri, str) or uri.startswith("data:"):
            continue
        if uri == want:
            return
        src = parent / uri
        dst = parent / want
        if not src.is_file():
            raise FileNotFoundError(f"glTF buffer file missing: {src}")
        shutil.copy2(src, dst)
        buf["uri"] = want
        return
    return


def main() -> int:
    ap = argparse.ArgumentParser(description="Nest glTF nodes from orbitron_logical_assemblies.json")
    ap.add_argument("--gltf", type=Path, required=True, help="Path to orbitron_lab_v5.gltf (rewritten in place)")
    ap.add_argument(
        "--assemblies-json",
        type=Path,
        required=True,
        help="orbitron_logical_assemblies.json",
    )
    ap.add_argument(
        "--root-name",
        default="fusion_arcjet_engine",
        help="glTF scene root node name (default: fusion_arcjet_engine)",
    )
    ap.add_argument(
        "--root-group",
        default="test_stand",
        help="JSON groups key for the scene root (default: test_stand)",
    )
    args = ap.parse_args()

    gltf_path = args.gltf.resolve()
    asm_path = args.assemblies_json.resolve()
    if not gltf_path.is_file():
        print(f"error: glTF not found: {gltf_path}", file=sys.stderr)
        return 1
    if not asm_path.is_file():
        print(f"error: assemblies JSON not found: {asm_path}", file=sys.stderr)
        return 1

    data = load_assemblies(asm_path)
    groups: dict[str, Any] = data["groups"]
    root_g = str(args.root_group)

    gltf = json.loads(gltf_path.read_text(encoding="utf-8"))
    if "nodes" not in gltf or not gltf["nodes"]:
        raise ValueError("glTF has no nodes")

    mesh_names = {
        str(n["name"])
        for n in gltf["nodes"]
        if n.get("mesh") is not None and n.get("name")
    }
    validate_assemblies_for_gltf(mesh_names, data)

    gltf = copy.deepcopy(gltf)
    align_sidecar_bin_to_stem(gltf_path, gltf)
    nest_gltf_nodes(gltf, groups, root_g, str(args.root_name))

    gltf_path.write_text(json.dumps(gltf, separators=(",", ":")), encoding="utf-8")
    n_nodes = len(gltf["nodes"])
    print(f"Wrote nested glTF: {gltf_path} ({n_nodes} nodes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
