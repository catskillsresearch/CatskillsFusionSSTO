import glob
import sys

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import yt

# Hide YT's noisy command-line logs
yt.funcs.mylog.setLevel(50)

print("Searching for WarpX diagnostic files...")
plotfiles = sorted(glob.glob("diags/density_diag*"))

if not plotfiles:
    print("Error: No plotfiles found in the 'diags' folder!")
    sys.exit(1)

print(f"Found {len(plotfiles)} frames. Stitching animation...")


def combined_charge_density(ds):
    """Sum |rho_*| for all deposited species charge densities (WarpX boxlib)."""
    grid = ds.covering_grid(level=0, left_edge=ds.domain_left_edge, dims=ds.domain_dimensions)
    total = None
    for field in ds.field_list:
        if len(field) < 2:
            continue
        fname = field[1]
        if not fname.startswith("rho_"):
            continue
        try:
            arr = np.abs(grid[field].v.squeeze())
        except Exception:
            continue
        total = arr if total is None else (total + arr)
    if total is None:
        # Legacy single-species case
        total = np.abs(grid[("boxlib", "rho_electrons")].v.squeeze())
    return total


fig, ax = plt.subplots(figsize=(6, 6))


def update(frame_idx):
    ax.clear()
    filename = plotfiles[frame_idx]
    ds = yt.load(filename)
    rho = combined_charge_density(ds)
    im = ax.imshow(rho, cmap="magma", origin="lower", extent=[-5, 5, -5, 5])
    ax.set_title(f"Plasma density (|rho| sum) | {filename.split('/')[-1]}")
    ax.set_xlabel("X (cm)")
    ax.set_ylabel("Z (cm)")
    cathode = plt.Circle((0, 0), 0.5, color="cyan", fill=False, linewidth=2, linestyle="--")
    ax.add_patch(cathode)
    anode = plt.Circle((0, 0), 5.0, color="gray", fill=False, linewidth=4)
    ax.add_patch(anode)


ani = animation.FuncAnimation(fig, update, frames=len(plotfiles), repeat=False)

output_filename = "orbitron_plasma.gif"
print(f"Baking GIF to {output_filename}...")
ani.save(output_filename, writer="pillow", fps=5)

print("Done! Open orbitron_plasma.gif to see your reactor fire.")
