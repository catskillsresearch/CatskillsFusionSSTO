# Invoked by bl.sh:  blender --factory-startup --python this_file -- /path/to/orbitron_lab.gltf
# Imports the nested lab glTF into an empty factory scene (GUI or background).

from __future__ import annotations

import sys


def _path_after_dashdash() -> str:
    if "--" not in sys.argv:
        print("usage: blender ... --python blender_open_orbitron_lab_gltf.py -- FILE.gltf", file=sys.stderr)
        raise SystemExit(2)
    rest = sys.argv[sys.argv.index("--") + 1 :]
    if not rest:
        print("error: pass glTF path after --", file=sys.stderr)
        raise SystemExit(2)
    return rest[0]


def _import() -> None:
    import bpy

    path = _path_after_dashdash()
    bpy.ops.import_scene.gltf(filepath=path)


def main() -> None:
    import bpy

    if bpy.app.background:
        _import()
        return

    def _timer() -> None:
        _import()
        return None

    bpy.app.timers.register(_timer, first_interval=0.15)


if __name__ == "__main__":
    main()
