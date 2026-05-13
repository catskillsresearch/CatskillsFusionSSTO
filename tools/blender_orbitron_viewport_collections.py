# Run with Blender's Python (not system python3).
# Example:
#   blender --background --python tools/blender_orbitron_viewport_collections.py -- \
#     /path/to/Aircraft/<aircraft.package_dir>/build/orbitron_lab.gltf
#
# Imports the nested glTF (from make + gltf_nest_from_assemblies.py), then creates
# four VIEW__* collections matching the top-level children of fusion_arcjet_engine
# and moves each branch's meshes into its collection. Toggle collection visibility
# in the Outliner to isolate one assembly at a time (meshes unlinked from the default
# Scene Collection so they only appear under VIEW__*).

from __future__ import annotations

import sys

import bpy


def _argv_gltf_path() -> str:
    if "--" in sys.argv:
        rest = sys.argv[sys.argv.index("--") + 1 :]
        if rest:
            return rest[0]
    for a in sys.argv:
        if a.endswith(".gltf"):
            return a
    print(
        "Usage: blender ... --python tools/blender_orbitron_viewport_collections.py -- FILE.gltf",
        file=sys.stderr,
    )
    raise SystemExit(2)


def mesh_descendants(ob) -> list:
    if ob.type == "MESH":
        out.append(ob)
    for ch in ob.children:
        out.extend(mesh_descendants(ch))
    return out


def main() -> None:
    path = _argv_gltf_path()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=path)

    root = bpy.data.objects.get("fusion_arcjet_engine")
    if root is None:
        empties = [o for o in bpy.data.objects if o.type == "EMPTY" and o.parent is None]
        if len(empties) == 1:
            root = empties[0]
        else:
            raise RuntimeError(
                "Expected root empty fusion_arcjet_engine (nested glTF from make)."
            )

    scene = bpy.context.scene
    base = scene.collection

    for ch in root.children:
        cname = f"VIEW__{ch.name}"
        col = bpy.data.collections.get(cname)
        if col is None:
            col = bpy.data.collections.new(cname)
            base.children.link(col)
        for ob in mesh_descendants(ch):
            if ob.name not in col.objects:
                col.objects.link(ob)
            if base in ob.users_collection:
                base.objects.unlink(ob)

    print(
        "Linked meshes into VIEW__* collections; toggle them in the Outliner to isolate assemblies."
    )


if __name__ == "__main__":
    main()
