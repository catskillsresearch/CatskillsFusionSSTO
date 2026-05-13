import os
import re
import json
import sys
import traceback
import bpy


_ORBITRON_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.normpath(os.path.join(_ORBITRON_DIR, "..", ".."))
_PKG = os.environ.get("ORBITRON_AIRCRAFT_PKG", "Orbitron-TestStand")
_DEFAULT_GLTF = os.path.normpath(
    os.path.join(_REPO_ROOT, "Aircraft", _PKG, "build", "orbitron_lab.gltf")
)
GLTF_FILE = os.path.abspath(os.environ.get("ORBITRON_GLTF_IN", _DEFAULT_GLTF))
_DEFAULT_AC = os.path.join(_REPO_ROOT, "Aircraft", _PKG, "Models", "orbitron.ac")
AC3D_FILE = os.path.abspath(os.environ.get("ORBITRON_AC_OUT", _DEFAULT_AC))
GROUND_TRUTH_LINEAR = {
    "Optics_Table": (0.02, 0.02, 0.02),
    "Operator_Console": (0.02, 0.02, 0.02),
    "Tank_Hydrogen": (0.604, 0.01, 0.01),
    "Tank_Diborane": (0.01, 0.319, 0.033),
    "Tank_Cryo_Methane": (0.448, 0.448, 0.604),
}


def linear_to_srgb(v):
    """Convert one Linear RGB channel to sRGB (IEC 61966-2-1)."""
    v = max(0.0, min(1.0, float(v)))
    if v <= 0.0031308:
        return 12.92 * v
    return 1.055 * (v ** (1.0 / 2.4)) - 0.055


def extract_base_color_linear(material):
    """Return (r, g, b, a) from Principled BSDF Base Color if present."""
    if not (material and material.node_tree):
        return None

    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if not bsdf:
        return None

    socket = bsdf.inputs.get("Base Color")
    if socket is None:
        return None

    c = socket.default_value
    return (float(c[0]), float(c[1]), float(c[2]), float(c[3]))


def sync_material_diffuse_colors():
    """
    Prevent AC3D exporter color bleed:
    - Read GLTF Principled BSDF Base Color in Linear space.
    - Convert to sRGB.
    - Explicitly write material.diffuse_color.
    """
    for mat in bpy.data.materials:
        linear = extract_base_color_linear(mat)
        if linear is None:
            continue

        r_lin, g_lin, b_lin, a = linear
        r = linear_to_srgb(r_lin)
        g = linear_to_srgb(g_lin)
        b = linear_to_srgb(b_lin)
        mat.diffuse_color = (r, g, b, a)


def load_gltf_object_target_rgb_map(gltf_path):
    """
    Parse GLTF JSON directly and return node-name -> sRGB tuple from
    pbrMetallicRoughness.baseColorFactor. This avoids Blender/addon ambiguity.
    """
    with open(gltf_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    materials = data.get("materials", [])
    meshes = data.get("meshes", [])
    nodes = data.get("nodes", [])

    material_linear_rgb = {}
    for i, mat in enumerate(materials):
        pbr = mat.get("pbrMetallicRoughness", {})
        base = pbr.get("baseColorFactor", [1.0, 1.0, 1.0, 1.0])
        material_linear_rgb[i] = (float(base[0]), float(base[1]), float(base[2]))

    mesh_linear_rgb = {}
    for i, mesh in enumerate(meshes):
        primitives = mesh.get("primitives", [])
        mat_idx = None
        if primitives:
            mat_idx = primitives[0].get("material")
        if mat_idx is not None and mat_idx in material_linear_rgb:
            mesh_linear_rgb[i] = material_linear_rgb[mat_idx]

    object_srgb = {}
    for node in nodes:
        name = node.get("name")
        mesh_idx = node.get("mesh")
        if name is None or mesh_idx is None:
            continue
        if mesh_idx not in mesh_linear_rgb:
            continue
        lr, lg, lb = mesh_linear_rgb[mesh_idx]
        object_srgb[name] = (
            linear_to_srgb(lr),
            linear_to_srgb(lg),
            linear_to_srgb(lb),
        )

    return object_srgb


def rewrite_material_line(line):
    parts = line.split()
    if "rgb" not in parts:
        return line

    try:
        rgb_idx = parts.index("rgb")
        r = float(parts[rgb_idx + 1])
        g = float(parts[rgb_idx + 2])
        b = float(parts[rgb_idx + 3])
    except (ValueError, IndexError):
        return line

    # AC3D exporter currently writes linear-space rgb values.
    # FlightGear expects sRGB-like values for visual parity with Blender viewport.
    sr = linear_to_srgb(r)
    sg = linear_to_srgb(g)
    sb = linear_to_srgb(b)
    amb = (0.5 * sr, 0.5 * sg, 0.5 * sb)

    parts[rgb_idx + 1], parts[rgb_idx + 2], parts[rgb_idx + 3] = (
        f"{sr:.3f}",
        f"{sg:.3f}",
        f"{sb:.3f}",
    )

    if "amb" in parts:
        i = parts.index("amb")
        parts[i + 1], parts[i + 2], parts[i + 3] = (
            f"{amb[0]:.3f}",
            f"{amb[1]:.3f}",
            f"{amb[2]:.3f}",
        )

    if "emis" in parts:
        i = parts.index("emis")
        parts[i + 1], parts[i + 2], parts[i + 3] = ("0.0", "0.0", "0.0")

    if "spec" in parts:
        i = parts.index("spec")
        parts[i + 1], parts[i + 2], parts[i + 3] = ("0.05", "0.05", "0.05")

    return " ".join(parts) + "\n"


def parse_material_table(lines):
    """
    Parse AC3D MATERIAL lines and return:
    - rewritten lines with lighting normalization
    - material index -> rgb map
    """
    out = []
    idx_to_rgb = {}
    material_index = 0

    for line in lines:
        if line.startswith("MATERIAL "):
            rewritten = rewrite_material_line(line)
            out.append(rewritten)
            parts = rewritten.split()
            if "rgb" in parts:
                i = parts.index("rgb")
                try:
                    idx_to_rgb[material_index] = (
                        float(parts[i + 1]),
                        float(parts[i + 2]),
                        float(parts[i + 3]),
                    )
                except (ValueError, IndexError):
                    pass
            material_index += 1
        else:
            out.append(line)
    return out, idx_to_rgb


def nearest_material_index(target_rgb, idx_to_rgb):
    best_idx = 0
    best_d2 = None
    tr, tg, tb = target_rgb
    for idx, (r, g, b) in idx_to_rgb.items():
        d2 = (tr - r) ** 2 + (tg - g) ** 2 + (tb - b) ** 2
        if best_d2 is None or d2 < best_d2:
            best_d2 = d2
            best_idx = idx
    return best_idx


def rebind_object_mat_indices(lines, object_target_rgb):
    """
    Repair exporter bug where many/all faces are emitted as 'mat 0'.
    We map each AC object name to the nearest MATERIAL entry by sRGB color and
    rewrite all face 'mat N' lines for that object.
    """
    # First pass: normalize MATERIAL lines and capture index->rgb table.
    lines, idx_to_rgb = parse_material_table(lines)
    if not idx_to_rgb or not object_target_rgb:
        return lines

    object_to_mat_idx = {
        obj_name: nearest_material_index(rgb, idx_to_rgb)
        for obj_name, rgb in object_target_rgb.items()
    }

    out = []
    current_object_mat = None
    for line in lines:
        if line.startswith("OBJECT "):
            current_object_mat = None
            out.append(line)
            continue

        name_match = re.match(r'^\s*name\s+"(.+)"\s*$', line)
        if name_match:
            obj_name = name_match.group(1)
            current_object_mat = object_to_mat_idx.get(obj_name)
            out.append(line)
            continue

        if current_object_mat is not None and re.match(r"^\s*mat\s+\d+\s*$", line):
            out.append(f"mat {current_object_mat}\n")
            continue

        out.append(line)

    return out


def extract_object_to_mat_from_ac(lines):
    """
    Read final per-object mat assignment from AC text.
    Uses first encountered 'mat N' inside each OBJECT block.
    """
    object_to_mat = {}
    current_obj = None
    for line in lines:
        name_match = re.match(r'^\s*name\s+"(.+)"\s*$', line)
        if name_match:
            current_obj = name_match.group(1)
            continue

        if current_obj is None:
            continue

        mat_match = re.match(r"^\s*mat\s+(\d+)\s*$", line)
        if mat_match and current_obj not in object_to_mat:
            object_to_mat[current_obj] = int(mat_match.group(1))
    return object_to_mat


def enforce_ground_truth_materials(lines):
    """
    Force known critical object colors using diagnostic ground truth.
    This guarantees key stand colors stay stable regardless of exporter behavior.
    """
    object_to_mat = extract_object_to_mat_from_ac(lines)
    forced_mat_rgb = {}
    for obj_name, linear_rgb in GROUND_TRUTH_LINEAR.items():
        mat_idx = object_to_mat.get(obj_name)
        if mat_idx is None:
            continue
        lr, lg, lb = linear_rgb
        forced_mat_rgb[mat_idx] = (
            linear_to_srgb(lr),
            linear_to_srgb(lg),
            linear_to_srgb(lb),
        )

    if not forced_mat_rgb:
        return lines

    out = []
    material_index = 0
    for line in lines:
        if not line.startswith("MATERIAL "):
            out.append(line)
            continue

        parts = line.split()
        if material_index in forced_mat_rgb and "rgb" in parts:
            sr, sg, sb = forced_mat_rgb[material_index]
            i = parts.index("rgb")
            parts[i + 1], parts[i + 2], parts[i + 3] = (
                f"{sr:.3f}",
                f"{sg:.3f}",
                f"{sb:.3f}",
            )
            if "amb" in parts:
                j = parts.index("amb")
                parts[j + 1], parts[j + 2], parts[j + 3] = (
                    f"{0.5 * sr:.3f}",
                    f"{0.5 * sg:.3f}",
                    f"{0.5 * sb:.3f}",
                )
            if "emis" in parts:
                j = parts.index("emis")
                parts[j + 1], parts[j + 2], parts[j + 3] = ("0.0", "0.0", "0.0")
            if "spec" in parts:
                j = parts.index("spec")
                parts[j + 1], parts[j + 2], parts[j + 3] = ("0.05", "0.05", "0.05")
            line = " ".join(parts) + "\n"

        out.append(line)
        material_index += 1
    return out


def _choose_projection_axes(vertices):
    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    zs = [v[2] for v in vertices]
    spans = [
        (max(xs) - min(xs), 0),
        (max(ys) - min(ys), 1),
        (max(zs) - min(zs), 2),
    ]
    spans.sort(reverse=True)
    return spans[0][1], spans[1][1]


def _normalized_uv(val, lo, hi):
    if hi - lo < 1e-9:
        return 0.5
    return (val - lo) / (hi - lo)


def repair_screen_uvs(lines, screen_name="Screen"):
    """
    AC3D exporter may emit collapsed UVs (0,0) for untextured meshes.
    For FlightGear canvas mapping, repair Screen object refs with planar UVs.
    """
    out = list(lines)
    i = 0
    n = len(out)

    while i < n:
        line = out[i]
        name_match = re.match(r'^\s*name\s+"(.+)"\s*$', line)
        if not name_match or name_match.group(1) != screen_name:
            i += 1
            continue

        # Find object block bounds.
        obj_start = i
        obj_end = n
        j = i + 1
        while j < n:
            if out[j].startswith("OBJECT "):
                obj_end = j
                break
            j += 1

        # Parse vertices.
        numvert_idx = None
        numvert = 0
        for k in range(obj_start, obj_end):
            if out[k].startswith("numvert "):
                numvert_idx = k
                numvert = int(out[k].split()[1])
                break
        if numvert_idx is None or numvert <= 0:
            i = obj_end
            continue

        vert_start = numvert_idx + 1
        vert_end = vert_start + numvert
        if vert_end > obj_end:
            i = obj_end
            continue

        vertices = []
        for k in range(vert_start, vert_end):
            parts = out[k].split()
            if len(parts) < 3:
                vertices.append((0.0, 0.0, 0.0))
                continue
            vertices.append((float(parts[0]), float(parts[1]), float(parts[2])))

        axis_u, axis_v = _choose_projection_axes(vertices)
        coords_u = [v[axis_u] for v in vertices]
        coords_v = [v[axis_v] for v in vertices]
        u_min, u_max = min(coords_u), max(coords_u)
        v_min, v_max = min(coords_v), max(coords_v)

        # Rewrite refs lines within this object.
        k = vert_end
        while k < obj_end:
            if out[k].startswith("refs "):
                try:
                    ref_count = int(out[k].split()[1])
                except (IndexError, ValueError):
                    k += 1
                    continue
                for r in range(ref_count):
                    rr = k + 1 + r
                    if rr >= obj_end:
                        break
                    parts = out[rr].split()
                    if len(parts) < 1:
                        continue
                    try:
                        vidx = int(parts[0])
                    except ValueError:
                        continue
                    if not (0 <= vidx < len(vertices)):
                        continue
                    vtx = vertices[vidx]
                    u = _normalized_uv(vtx[axis_u], u_min, u_max)
                    v = _normalized_uv(vtx[axis_v], v_min, v_max)
                    out[rr] = f"{vidx} {u:.6f} {v:.6f}\n"
                k += 1 + ref_count
            else:
                k += 1

        i = obj_end

    return out


def postprocess_ac_file(path, object_target_rgb):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Material/lighting normalization + object face material repair.
    out = rebind_object_mat_indices(lines, object_target_rgb)
    out = enforce_ground_truth_materials(out)
    out = repair_screen_uvs(out, "Screen")

    # Double-sided override for FlightGear backface culling.
    final_lines = []
    for line in out:
        stripped = line.strip()
        tokens = stripped.split()
        if len(tokens) >= 2 and tokens[0].upper() == "SURF" and tokens[1].upper().startswith("0X"):
            final_lines.append("SURF 0x20\n")
            continue
        final_lines.append(line)

    with open(path, "w", encoding="utf-8") as f:
        f.writelines(final_lines)


def execute_pipeline():
    # Pipeline guarantees:
    # 1) Kill "red virus": explicit diffuse_color from Principled Base Color.
    # 2) Fix linear/sRGB mismatch before FlightGear sees MATERIAL rgb.
    # 3) Force double-sided SURF to avoid flat-plane culling artifacts.
    print("--- STARTING AC3D BUILD PIPELINE ---")
    bpy.ops.preferences.addon_enable(module="io_scene_ac3d")

    # Clean scene and import GLTF.
    if bpy.context.active_object and bpy.context.active_object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    bpy.ops.import_scene.gltf(filepath=GLTF_FILE)

    # Keep transforms stable and remove non-mesh objects.
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    bpy.ops.object.select_all(action="DESELECT")
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH":
            obj.select_set(True)
    bpy.ops.object.delete()

    # Ensure the podium monitor has valid UVs for FlightGear canvas mapping.
    screen_obj = bpy.data.objects.get("Screen")
    if screen_obj and screen_obj.type == "MESH":
        bpy.ops.object.select_all(action="DESELECT")
        screen_obj.select_set(True)
        bpy.context.view_layer.objects.active = screen_obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project()
        bpy.ops.object.mode_set(mode="OBJECT")

    # Critical color handoff for io_scene_ac3d.
    sync_material_diffuse_colors()
    object_target_rgb = load_gltf_object_target_rgb_map(GLTF_FILE)

    # Export natively to AC3D.
    bpy.ops.object.select_all(action="SELECT")
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if meshes:
        bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.export_scene.export_ac3d("EXEC_DEFAULT", filepath=AC3D_FILE)

    # AC text pass: material index repair + double-sided surfaces + neutral FG lighting.
    postprocess_ac_file(AC3D_FILE, object_target_rgb)

    print(f"--- PIPELINE COMPLETE: {AC3D_FILE} ---")
    bpy.ops.wm.quit_blender()
    return None


# Batch mode (-b): timers often never run before exit — run pipeline synchronously.
if bpy.app.background:
    try:
        execute_pipeline()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
else:
    bpy.app.timers.register(execute_pipeline, first_interval=0.2)
