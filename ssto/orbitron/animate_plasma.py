import yt
import glob
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

# Hide YT's noisy command-line logs
yt.funcs.mylog.setLevel(50)

print("Searching for WarpX diagnostic files...")
# Find all plotfiles, sorted chronologically
plotfiles = sorted(glob.glob("diags/density_diag*"))

if not plotfiles:
    print("Error: No plotfiles found in the 'diags' folder!")
    exit()

print(f"Found {len(plotfiles)} frames. Stitching animation...")

fig, ax = plt.subplots(figsize=(6, 6))

def update(frame_idx):
    ax.clear()
    filename = plotfiles[frame_idx]
    
    # Load the AMReX plotfile
    ds = yt.load(filename)
    
    # Extract the raw 2D array of electron charge density
    grid = ds.covering_grid(level=0, left_edge=ds.domain_left_edge, dims=ds.domain_dimensions)
    
    # AMReX outputs electron density as negative (since electrons have negative charge).
    # We take the absolute value so it plots brightly. squeeze() flattens it to 2D.
    rho = np.abs(grid[('boxlib', 'rho_electrons')].v.squeeze())
    
    # Plot the plasma! (extent is -5cm to +5cm)
    im = ax.imshow(rho, cmap='magma', origin='lower', extent=[-5, 5, -5, 5])
    
    ax.set_title(f"Plasma Density | {filename.split('/')[-1]}")
    ax.set_xlabel("X (cm)")
    ax.set_ylabel("Z (cm)")
    
    # Draw the -600kV Cathode wire in the center (0.5 cm radius)
    cathode = plt.Circle((0, 0), 0.5, color='cyan', fill=False, linewidth=2, linestyle='--')
    ax.add_patch(cathode)
    
    # Draw the Grounded Anode wall (5.0 cm radius)
    anode = plt.Circle((0, 0), 5.0, color='gray', fill=False, linewidth=4)
    ax.add_patch(anode)

# Generate the animation
ani = animation.FuncAnimation(fig, update, frames=len(plotfiles), repeat=False)

# Save as a GIF
output_filename = "orbitron_plasma.gif"
print(f"Baking GIF to {output_filename}...")
ani.save(output_filename, writer='pillow', fps=5)

print("Done! Open orbitron_plasma.gif to see your reactor fire.")
