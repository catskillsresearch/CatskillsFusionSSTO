import yt
import glob
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.gridspec as gridspec
import numpy as np

# Suppress YT logs
yt.funcs.mylog.setLevel(50)

print("Loading WarpX Plasma Frames into RAM...")
plotfiles = sorted(glob.glob("diags/density_diag*"))
if not plotfiles:
    print("Error: No diags/ folder found! Run WarpX first.")
    exit()

# Pre-load the frames so the animation renders fast
frames_data =[]
for f in plotfiles:
    ds = yt.load(f)
    grid = ds.covering_grid(level=0, left_edge=ds.domain_left_edge, dims=ds.domain_dimensions)
    rho = np.abs(grid[('boxlib', 'rho_electrons')].v.squeeze())
    frames_data.append(rho)

print(f"Loaded {len(frames_data)} plasma frames. Assembling Movie...")

# --- SETUP THE MOVIE CANVAS ---
fig = plt.figure(figsize=(12, 6))
fig.patch.set_facecolor('black')
gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1])

# Left: The Plasma Visual
ax_plasma = plt.subplot(gs[0])
ax_plasma.set_facecolor('black')
ax_plasma.set_title("p-B11 Orbitron Core | 2D Cross-Section", color='white', pad=15)
ax_plasma.axis('off')

# Right: The Telemetry Dashboard
ax_telemetry = plt.subplot(gs[1])
ax_telemetry.set_facecolor('#111111')
ax_telemetry.axis('off')

# Initialize the Plasma Image
im_plasma = ax_plasma.imshow(np.zeros_like(frames_data[0]), cmap='magma', origin='lower', extent=[-6, 6, -6, 6], vmin=0, vmax=np.max(frames_data[-1]))

# --- DRAW THE HARDWARE & UNOBTAINIUM LABELS ---
# 1. Cathode (-600kV)
ax_plasma.add_patch(plt.Circle((0, 0), 0.5, color='cyan', fill=False, lw=2))
ax_plasma.text(0.6, 0.6, "Cathode (-600kV)\n[UNOBTAINIUM 1]", color='cyan', fontsize=8)

# 2. DEC Grid (+4MV)
ax_plasma.add_patch(plt.Circle((0, 0), 4.5, color='orange', fill=False, lw=1, ls=':'))
ax_plasma.text(-5.5, -4.5, "DEC Alpha Grid\n[UNOBTAINIUM 2]", color='orange', fontsize=8)

# 3. Anode Wall (Niobium) & X-Ray Shield (Tungsten)
ax_plasma.add_patch(plt.Circle((0, 0), 5.0, color='silver', fill=False, lw=3))
ax_plasma.add_patch(plt.Circle((0, 0), 5.3, color='gray', fill=False, lw=5)) # X-Ray Shield
ax_plasma.text(3.5, -5.5, "Niobium Wall +\nTungsten X-Ray Shield\n[UNOBTAINIUM 3]", color='silver', fontsize=8)

# --- SETUP THE DIGITAL GAUGES ---
txt_time = ax_telemetry.text(0.05, 0.9, "", color='white', fontsize=14, fontfamily='monospace')
txt_status = ax_telemetry.text(0.05, 0.8, "", color='yellow', fontsize=16, fontweight='bold')

txt_battery = ax_telemetry.text(0.05, 0.6, "", color='lime', fontsize=12, fontfamily='monospace')
txt_injection = ax_telemetry.text(0.05, 0.5, "", color='lightblue', fontsize=12, fontfamily='monospace')

txt_fusion_events = ax_telemetry.text(0.05, 0.35, "", color='magenta', fontsize=12, fontfamily='monospace')
txt_heat = ax_telemetry.text(0.05, 0.25, "", color='red', fontsize=12, fontfamily='monospace')

txt_power = ax_telemetry.text(0.05, 0.1, "", color='cyan', fontsize=18, fontweight='bold', fontfamily='monospace')

# --- THE SYSTEMS ENGINEERING MATH MODEL ---
TOTAL_FRAMES = 150 # 10 second movie at 15 fps
FPS = 15

def update(frame):
    # Calculate virtual time (0 to 10 seconds)
    t = frame / FPS
    
    # 1. Loop the WarpX plasma frames to keep it spinning
    pic_idx = frame % len(frames_data)
    
    # --- PHASE LOGIC ---
    status = "PHASE 1: MAGNET SPIN-UP"
    status_col = "yellow"
    battery_kwh = 50.0 - (t * 0.5) # Draining 0.5 kWh per sec to charge magnet
    injection_sccm = 0.0
    fusion_rate = 0.0
    power_mw = 0.0
    heat_kw = 0.0
    q_factor = 0.0
    plasma_brightness = 0.0
    
    if t > 2.0:
        status = "PHASE 2: FUEL INJECTION & IGNITION"
        status_col = "orange"
        battery_kwh = 49.0 - ((t-2) * 0.1) # Draining 100kW for NBI
        injection_sccm = min(100.0, (t-2) * 50) # Ramps up to 100 sccm
        
        # Plasma fades in as gas is injected
        plasma_brightness = min(1.0, (t-2) / 2.0)
        
        # Fusion rate scales non-linearly with injection
        fusion_rate = (injection_sccm / 100.0)**2 * 2.5e18 
        power_mw = (fusion_rate * 8.7e6 * 1.602e-19) / 1e6 # 8.7 MeV per reaction to MW
        heat_kw = (injection_sccm / 100.0) * 400.0
        
    if t > 4.0:
        status = "PHASE 3: BREAKEVEN (Q > 1)"
        status_col = "lime"
        battery_kwh = 48.8 + ((t-4) * 0.05) # Battery is RECHARGING now!
        injection_sccm = 100.0
        plasma_brightness = 1.0
        
        fusion_rate = 2.51e18 # Steady state events per second
        power_mw = 3.50        # Steady State 3.5 MW
        heat_kw = 400.0        # Steady State X-ray heat
        q_factor = 3.5 / 0.13  # 3.5 MW out / 130 kW parasitic BOP drain
        
    # --- UPDATE VISUALS ---
    # Apply brightness mask to the plasma
    im_plasma.set_array(frames_data[pic_idx] * plasma_brightness)
    
    # Update Texts
    txt_time.set_text(f"VIRTUAL TIME : {t:.1f} s")
    txt_status.set_text(status)
    txt_status.set_color(status_col)
    
    txt_battery.set_text(f"BATTERY STATE: {battery_kwh:.2f} kWh (50 Max)")
    txt_injection.set_text(f"NBI INJECTION: {injection_sccm:.1f} sccm p-B11")
    
    txt_fusion_events.set_text(f"FUSION EVENTS: {fusion_rate:.2e} / sec")
    txt_heat.set_text(f"X-RAY WALL HEAT: {heat_kw:.1f} kW")
    
    if q_factor > 1:
        txt_power.set_text(f"NET DEC OUTPUT: {power_mw:.2f} MW\nQ-FACTOR: {q_factor:.1f} (BREAKEVEN)")
        txt_power.set_color('lime')
    else:
        txt_power.set_text(f"NET DEC OUTPUT: {power_mw:.2f} MW\nQ-FACTOR: < 1.0")
        txt_power.set_color('cyan')

    return[im_plasma, txt_time, txt_status, txt_battery, txt_injection, txt_fusion_events, txt_heat, txt_power]

print("Rendering Movie (This will take a few seconds)...")
ani = animation.FuncAnimation(fig, update, frames=TOTAL_FRAMES, blit=True)

# Save as GIF
output_file = "orbitron_startup_sequence.gif"
ani.save(output_file, writer='pillow', fps=FPS)
print(f"Movie saved successfully as '{output_file}'!")

# OPTIONAL: If you have ffmpeg installed on your Linux machine, you can save as MP4 by uncommenting this:
ani.save("orbitron_startup_sequence.mp4", writer='ffmpeg', fps=FPS, dpi=200)
