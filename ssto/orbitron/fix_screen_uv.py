import os
import re
import sys
from pathlib import Path

_ORBITRON_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.normpath(os.path.join(_ORBITRON_DIR, "..", ".."))
_REPO_ROOT_PATH = Path(_REPO_ROOT)
_TOOLS = str(_REPO_ROOT_PATH / "tools")
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)
from orbitron_aircraft_pkg import aircraft_package_dir

_PKG = os.environ.get("ORBITRON_AIRCRAFT_PKG") or aircraft_package_dir(
    _REPO_ROOT_PATH
)
_DEFAULT_AC = os.path.join(_REPO_ROOT, "Aircraft", _PKG, "Models", "orbitron.ac")
AC3D_FILE = os.path.abspath(os.environ.get("ORBITRON_AC_OUT", _DEFAULT_AC))
SCREEN_NAME = "Screen"
# AC material references this basename; place the PNG next to orbitron.ac (e.g. under Aircraft/…/Models) if used.
SCREEN_TEXTURE = 'texture "warpx_frame.png"\n'


def choose_projection_axes(vertices):
    spans = []
    for axis in range(3):
        vals = [v[axis] for v in vertices]
        spans.append((max(vals) - min(vals), axis))
    spans.sort(reverse=True)
    return spans[0][1], spans[1][1]


def normalize(v, lo, hi):
    if hi - lo < 1e-9:
        return 0.5
    return (v - lo) / (hi - lo)


def fix_screen_uvs(lines):
    out = list(lines)
    i = 0
    n = len(out)
    changed = 0

    screen_mat_index = None

    while i < n:
        name_match = re.match(r'^\s*name\s+"(.+)"\s*$', out[i])
        if not name_match or name_match.group(1) != SCREEN_NAME:
            i += 1
            continue

        obj_start = i
        obj_end = n
        for j in range(i + 1, n):
            if out[j].startswith("OBJECT "):
                obj_end = j
                break

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

        # Ensure Screen is treated as textured geometry for canvas mapping.
        block = out[obj_start:obj_end]
        texture_idx = None
        for kk in range(obj_start, obj_end):
            if out[kk].startswith("texture "):
                texture_idx = kk
                break
        has_texture = texture_idx is not None
        if not has_texture:
            insert_at = numvert_idx
            out.insert(insert_at, 'texoff 0 0\n')
            out.insert(insert_at, 'texrep 1 1\n')
            out.insert(insert_at, SCREEN_TEXTURE)
            changed += 3
            # Recompute bounds after insertion.
            obj_end += 3
            n += 3
            numvert_idx += 3
        elif out[texture_idx] != SCREEN_TEXTURE:
            out[texture_idx] = SCREEN_TEXTURE
            changed += 1

        vert_start = numvert_idx + 1
        vert_end = vert_start + numvert
        if vert_end > obj_end:
            i = obj_end
            continue

        vertices = []
        for k in range(vert_start, vert_end):
            p = out[k].split()
            vertices.append((float(p[0]), float(p[1]), float(p[2])))

        axis_u, axis_v = choose_projection_axes(vertices)
        u_vals = [v[axis_u] for v in vertices]
        v_vals = [v[axis_v] for v in vertices]
        u_min, u_max = min(u_vals), max(u_vals)
        v_min, v_max = min(v_vals), max(v_vals)

        k = vert_end
        while k < obj_end:
            if out[k].startswith("refs "):
                ref_count = int(out[k].split()[1])
                if screen_mat_index is None and k > 0 and out[k - 1].startswith("mat "):
                    try:
                        screen_mat_index = int(out[k - 1].split()[1])
                    except (ValueError, IndexError):
                        pass
                for r in range(ref_count):
                    rr = k + 1 + r
                    parts = out[rr].split()
                    vidx = int(parts[0])
                    vtx = vertices[vidx]
                    u = normalize(vtx[axis_u], u_min, u_max)
                    v = normalize(vtx[axis_v], v_min, v_max)
                    new_line = f"{vidx} {u:.6f} {v:.6f}\n"
                    if out[rr] != new_line:
                        out[rr] = new_line
                        changed += 1
                k += 1 + ref_count
            else:
                k += 1

        i = obj_end

    # Make the screen material bright so canvas content is visible under FG lighting.
    if screen_mat_index is not None:
        mat_seen = 0
        for idx, line in enumerate(out):
            if not line.startswith("MATERIAL "):
                continue
            if mat_seen != screen_mat_index:
                mat_seen += 1
                continue

            parts = line.split()
            if "rgb" in parts:
                i = parts.index("rgb")
                parts[i + 1], parts[i + 2], parts[i + 3] = ("1.000", "1.000", "1.000")
            if "amb" in parts:
                i = parts.index("amb")
                parts[i + 1], parts[i + 2], parts[i + 3] = ("0.500", "0.500", "0.500")
            if "emis" in parts:
                i = parts.index("emis")
                parts[i + 1], parts[i + 2], parts[i + 3] = ("0.800", "0.800", "0.800")
            if "spec" in parts:
                i = parts.index("spec")
                parts[i + 1], parts[i + 2], parts[i + 3] = ("0.000", "0.000", "0.000")
            new_line = " ".join(parts) + "\n"
            if new_line != out[idx]:
                out[idx] = new_line
                changed += 1
            break

    return out, changed


def main():
    with open(AC3D_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    fixed, changed = fix_screen_uvs(lines)
    if changed > 0:
        with open(AC3D_FILE, "w", encoding="utf-8") as f:
            f.writelines(fixed)
    print(f"Screen UV fix applied: {changed} refs updated")


if __name__ == "__main__":
    main()
