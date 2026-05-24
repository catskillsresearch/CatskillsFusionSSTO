#!/usr/bin/env python3
"""Headless assembly PNG from an Orbitron lab glTF (Makefile / stand.sh).

Invoked as:
  blender --background --factory-startup --python tools/blender_render_orbitron_gltf.py -- \\
    IN.gltf OUT.png [BG_HEX] [W H]

Scene: empty factory startup (no default cube), solid world background, key/fill
sun lights added so shading reads as 3D, perspective camera at a 3/4 hero angle
framed to the mesh bounding sphere with margin so the whole assembly is in shot.
EEVEE still render.
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

DEFAULT_BG_HEX = "#ECECEC"
DEFAULT_SIZE = (1920, 1080)

# Hero-shot camera: 3/4 view from front-starboard, slightly elevated. Azimuth is
# rotation around +Z away from +X (lab propulsion axis), elevation lifts the
# camera above the horizon. Lens/sensor pick a mild perspective (~40 deg HFOV).
CAM_AZIMUTH_DEG = 35.0
CAM_ELEVATION_DEG = 22.0
CAM_LENS_MM = 50.0
CAM_SENSOR_WIDTH_MM = 36.0
# Multiplier on bounding-sphere radius before fitting; >1 leaves padding so the
# whole part sits comfortably inside the frame at any aspect ratio.
FRAME_MARGIN = float(os.environ.get("ORBITRON_FRAME_MARGIN", "1.04"))
# Percentile window for camera framing (ignores checklist ink / label text outliers).
FRAME_PERCENTILE_LO = float(os.environ.get("ORBITRON_FRAME_PCT_LO", "3"))
FRAME_PERCENTILE_HI = float(os.environ.get("ORBITRON_FRAME_PCT_HI", "97"))
# Mesh names containing these substrings are omitted from camera bounds only.
_BOUNDS_EXCLUDE_SUBSTR = tuple(
    s.strip()
    for s in os.environ.get(
        "ORBITRON_FRAME_EXCLUDE",
        "Operator_Checklist_Ink,Panel_Label_,Decal_",
    ).split(",")
    if s.strip()
)
# Drop pad peripherals far from the engine cluster (blower cart, long ducts, …).
_BOUNDS_EXCLUDE_SUBSTR += tuple(
    s.strip()
    for s in os.environ.get("ORBITRON_FRAME_EXCLUDE_EXTRA", "").split(",")
    if s.strip()
)


def _argv_paths() -> tuple[Path, Path]:
    if "--" not in sys.argv:
        print(
            "usage: blender --background --factory-startup --python "
            "blender_render_orbitron_gltf.py -- IN.gltf OUT.png",
            file=sys.stderr,
        )
        raise SystemExit(2)
    rest = sys.argv[sys.argv.index("--") + 1 :]
    if len(rest) < 2:
        print("error: need glTF path and output PNG after --", file=sys.stderr)
        raise SystemExit(2)
    return Path(rest[0]).resolve(), Path(rest[1]).resolve()


def _hex_to_rgb01(hex_color: str) -> tuple[float, float, float]:
    s = hex_color.strip().lstrip("#")
    if len(s) != 6:
        raise ValueError(f"expected #RRGGBB, got {hex_color!r}")
    return tuple(int(s[i : i + 2], 16) / 255.0 for i in (0, 2, 4))


def _view_layer_unexclude_all(layer_coll) -> None:
    try:
        layer_coll.exclude = False
    except AttributeError:
        return
    for child in getattr(layer_coll, "children", ()) or ():
        _view_layer_unexclude_all(child)


def _bounds_exclude(name: str) -> bool:
    return any(sub in name for sub in _BOUNDS_EXCLUDE_SUBSTR)


def _mesh_world_bounds():
    """Robust world AABB: vertex percentiles, optional cluster radius from mesh centroids."""
    import bpy

    import numpy as np

    verts: list[tuple[float, float, float]] = []
    centroids: list[np.ndarray] = []
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH" or _bounds_exclude(obj.name):
            continue
        mesh = obj.data
        if not mesh.vertices:
            continue
        mw = obj.matrix_world
        obj_verts: list[tuple[float, float, float]] = []
        for v in mesh.vertices:
            w = mw @ v.co
            obj_verts.append((w.x, w.y, w.z))
        verts.extend(obj_verts)
        arr_o = np.asarray(obj_verts, dtype=np.float64)
        centroids.append(arr_o.mean(axis=0))
    if not verts:
        return (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)
    arr = np.asarray(verts, dtype=np.float64)
    cluster_m = float(os.environ.get("ORBITRON_FRAME_CLUSTER_M", "0"))
    if cluster_m > 0 and centroids:
        med = np.median(np.stack(centroids), axis=0)
        keep = [
            obj
            for obj in bpy.context.scene.objects
            if obj.type == "MESH" and not _bounds_exclude(obj.name) and obj.data.vertices
        ]
        near_verts: list[tuple[float, float, float]] = []
        for obj in keep:
            mw = obj.matrix_world
            c = np.mean([mw @ v.co for v in obj.data.vertices], axis=0)
            if float(np.linalg.norm(c - med)) > cluster_m:
                continue
            for v in obj.data.vertices:
                w = mw @ v.co
                near_verts.append((w.x, w.y, w.z))
        if near_verts:
            arr = np.asarray(near_verts, dtype=np.float64)
    lo = float(FRAME_PERCENTILE_LO)
    hi = float(FRAME_PERCENTILE_HI)
    mins = tuple(float(np.percentile(arr[:, i], lo)) for i in range(3))
    maxs = tuple(float(np.percentile(arr[:, i], hi)) for i in range(3))
    return mins, maxs


def _trim_output_png(out_path: Path) -> None:
    """Post-render crop; best-effort (Pillow may be absent in bare Blender env)."""
    try:
        repo = Path(__file__).resolve().parents[1]
        if str(repo) not in sys.path:
            sys.path.insert(0, str(repo))
        from tools.trim_assembly_png import trim_png

        trim_png(out_path, padding_px=12)
    except BaseException:
        pass


def _setup_world(bg_rgb: tuple[float, float, float]) -> None:
    import bpy

    scene = bpy.context.scene
    if scene.world is None:
        scene.world = bpy.data.worlds.new("OrbitronRenderWorld")
    world = scene.world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    bg = nodes.new(type="ShaderNodeBackground")
    bg.inputs["Color"].default_value = (*bg_rgb, 1.0)
    bg.inputs["Strength"].default_value = 1.0
    out = nodes.new(type="ShaderNodeOutputWorld")
    links.new(bg.outputs["Background"], out.inputs["Surface"])


def _setup_render(size: tuple[int, int], out_path: Path) -> None:
    import bpy

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = int(size[0])
    scene.render.resolution_y = int(size[1])
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.filepath = str(out_path)
    scene.render.film_transparent = False

    eevee = getattr(scene, "eevee", None)
    if eevee is not None:
        if hasattr(eevee, "use_gtao"):
            eevee.use_gtao = True
        if hasattr(eevee, "use_bloom"):
            eevee.use_bloom = False


def _frame_perspective_camera(mins, maxs, size: tuple[int, int]) -> None:
    """Place a perspective camera at a 3/4 hero angle, fitting the whole part.

    Distance is solved from the camera's actual horizontal and vertical FOV so
    the bounding sphere (half-diagonal of the bbox * ``FRAME_MARGIN``) is fully
    inside the frame at the current render aspect ratio. The view direction is
    a fixed 3/4 angle in world space (lab axis ``+X`` is the propulsion axis,
    ``+Z`` is up); the camera ends up looking from front-starboard-above.
    """
    import bpy
    from mathutils import Vector

    cx = 0.5 * (mins[0] + maxs[0])
    cy = 0.5 * (mins[1] + maxs[1])
    cz = 0.5 * (mins[2] + maxs[2])
    dx = maxs[0] - mins[0]
    dy = maxs[1] - mins[1]
    dz = maxs[2] - mins[2]
    half_diag = 0.5 * math.sqrt(dx * dx + dy * dy + dz * dz)
    radius = max(half_diag * FRAME_MARGIN, 0.05)

    aspect = float(size[0]) / float(max(size[1], 1))
    half_hfov = math.atan((CAM_SENSOR_WIDTH_MM * 0.5) / CAM_LENS_MM)
    half_vfov = math.atan(math.tan(half_hfov) / aspect)
    half_fov = min(half_hfov, half_vfov)
    distance = radius / math.sin(half_fov)

    az = math.radians(CAM_AZIMUTH_DEG)
    el = math.radians(CAM_ELEVATION_DEG)
    # Camera direction expressed in world space: az rotates from +Y toward +X
    # (so the lab nose points slightly toward the viewer), el tips upward.
    dir_x = math.sin(az) * math.cos(el)
    dir_y = math.cos(az) * math.cos(el)
    dir_z = math.sin(el)
    cam_loc = Vector(
        (
            cx + distance * dir_x,
            cy + distance * dir_y,
            cz + distance * dir_z,
        )
    )
    target = Vector((cx, cy, cz))

    cam_data = bpy.data.cameras.new("OrbitronHero")
    cam_data.type = "PERSP"
    cam_data.lens = CAM_LENS_MM
    cam_data.sensor_fit = "HORIZONTAL"
    cam_data.sensor_width = CAM_SENSOR_WIDTH_MM
    # Generous clip range so very small or very large assemblies both render.
    cam_data.clip_start = max(distance * 1e-4, 1e-3)
    cam_data.clip_end = max(distance * 10.0, 1000.0)

    cam_obj = bpy.data.objects.new("OrbitronHeroCam", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    cam_obj.location = cam_loc
    cam_obj.rotation_euler = (target - cam_loc).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam_obj


def _setup_lights(mins, maxs) -> None:
    """Add key + fill sun lamps so the assembly reads as 3D, not a flat decal."""
    import bpy
    from mathutils import Vector

    cx = 0.5 * (mins[0] + maxs[0])
    cy = 0.5 * (mins[1] + maxs[1])
    cz = 0.5 * (mins[2] + maxs[2])
    span = max(
        maxs[0] - mins[0], maxs[1] - mins[1], maxs[2] - mins[2], 0.01
    )
    center = Vector((cx, cy, cz))

    def _add_sun(name: str, offset: Vector, energy: float) -> None:
        light_data = bpy.data.lights.new(name=name, type="SUN")
        light_data.energy = energy
        light_obj = bpy.data.objects.new(name=name, object_data=light_data)
        bpy.context.scene.collection.objects.link(light_obj)
        light_obj.location = center + offset * span
        direction = center - light_obj.location
        light_obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

    _add_sun("OrbitronKey", Vector((0.8, 1.0, 1.2)), 4.0)
    _add_sun("OrbitronFill", Vector((-1.2, 0.4, 0.6)), 1.5)
    _add_sun("OrbitronRim", Vector((0.2, -1.4, 0.9)), 1.0)


def _import_and_clean(gltf_path: Path) -> None:
    import bpy

    if bpy.context.active_object and bpy.context.active_object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    bpy.ops.import_scene.gltf(filepath=str(gltf_path))
    _view_layer_unexclude_all(bpy.context.view_layer.layer_collection)

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    for obj in list(bpy.context.scene.objects):
        if obj.type != "MESH":
            bpy.data.objects.remove(obj, do_unlink=True)


def main() -> None:
    import bpy

    gltf_path, out_path = _argv_paths()
    if not gltf_path.is_file():
        print(f"error: glTF not found: {gltf_path}", file=sys.stderr)
        raise SystemExit(1)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    bg = DEFAULT_BG_HEX
    size = DEFAULT_SIZE
    if os.environ.get("ORBITRON_HERO_SQUARE", "").lower() in ("1", "true", "yes"):
        size = (1280, 1280)
    if "--" in sys.argv:
        rest = sys.argv[sys.argv.index("--") + 1 :]
        if len(rest) >= 3:
            bg = rest[2]
        if len(rest) >= 5:
            size = (int(rest[3]), int(rest[4]))
    stem = gltf_path.stem
    if stem == "orbitron_lab":
        # Full test_stand export — frame entire pad (no cluster crop).
        os.environ.setdefault("ORBITRON_FRAME_CLUSTER_M", "0")
        os.environ.setdefault("ORBITRON_FRAME_MARGIN", "1.05")
        os.environ.setdefault("ORBITRON_FRAME_PCT_LO", "2")
        os.environ.setdefault("ORBITRON_FRAME_PCT_HI", "98")
        size = (1600, 900)
    elif stem == "phase_2_wind_tunnel":
        os.environ.setdefault("ORBITRON_FRAME_CLUSTER_M", "1.9")
        os.environ.setdefault(
            "ORBITRON_FRAME_EXCLUDE_EXTRA",
            "Industrial_Blower,Pad_Startup,S_Duct,Exhaust_Silencer,Pneumatic_Air",
        )

    _import_and_clean(gltf_path)
    mins, maxs = _mesh_world_bounds()
    _setup_world(_hex_to_rgb01(bg))
    _setup_render(size, out_path)
    _setup_lights(mins, maxs)
    _frame_perspective_camera(mins, maxs, size)
    bpy.ops.render.render(write_still=True)
    _trim_output_png(out_path)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback

        traceback.print_exc()
        raise SystemExit(1) from None
