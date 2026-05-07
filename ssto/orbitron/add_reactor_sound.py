import numpy as np
from scipy.io import wavfile
import subprocess
import os

print("Synthesizing Heavy Industrial Orbitron Audio...")

sample_rate = 44100
duration = 10.0
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

# ---------------------------------------------------------
# 1. THE TRANSFORMER HUM (0 - 10s)
# ---------------------------------------------------------
# Instead of a pure sine, we use multiple harmonics and overdrive them 
# to create an aggressive, electrical "buzz".
hum = (1.0 * np.sin(2 * np.pi * 60 * t) + 
       0.5 * np.sin(2 * np.pi * 120 * t) + 
       0.25 * np.sin(2 * np.pi * 240 * t))
# Overdrive/Clip the hum to make it sound harsh
hum = np.clip(hum * 2.0, -0.6, 0.6) 

# ---------------------------------------------------------
# 2. THE MAGNET SPIN-UP (0 - 2s)
# ---------------------------------------------------------
# A distinct, rising whine from 60Hz up to 800Hz.
ramp_freq = np.interp(t, [0, 2], [60, 800])
ramp_phase = np.cumsum(ramp_freq) / sample_rate * 2 * np.pi
spin_up = np.sin(ramp_phase)
# Fade it out exactly at 2.0 seconds
spin_envelope = np.interp(t,[0, 1.8, 2.0, 2.1],[0.0, 0.8, 0.0, 0.0])
spin_up = spin_up * spin_envelope

# ---------------------------------------------------------
# 3. THE PNEUMATIC CLACK (Exactly at 2.0s)
# ---------------------------------------------------------
# A violent, low-frequency thud with a millisecond decay.
clack_env = np.where(t >= 2.0, np.exp(-50 * (t - 2.0)), 0)
clack_tone = np.sin(2 * np.pi * 40 * t) # Deep 40Hz punch
# Add high-frequency noise for the mechanical "snap"
clack_snap = np.random.uniform(-1, 1, len(t)) * np.exp(-500 * np.maximum(0, t - 2.0))
clack = (clack_tone + clack_snap) * clack_env * 3.0 # Boosted volume

# ---------------------------------------------------------
# 4. THE PLASMA ROAR (2.0 - 10s)
# ---------------------------------------------------------
# Raw white noise is "hiss". We use a moving average to create a low-pass 
# filter, turning the hiss into a deep, rocket-like "Rumble".
raw_noise = np.random.uniform(-1, 1, len(t))
window = np.ones(40) / 40.0 # 40-sample moving average smooths out the highs
rumble = np.convolve(raw_noise, window, mode='same')

# Modulate the rumble with a low 15Hz wave so it "chugs" and vibrates
chug = 1.0 + 0.5 * np.sin(2 * np.pi * 15 * t)
roar = rumble * chug

# Envelope: Fades in violently from 2s to 3s
roar_envelope = np.clip((t - 2.0), 0, 1.0)
roar = roar * roar_envelope * 4.0 # Boosted volume

# ---------------------------------------------------------
# 5. THE 4MV CORONA CRACKLE (4.0 - 10s)
# ---------------------------------------------------------
# Tearing electricity. We generate random spikes, but gate them so only 
# the most violent peaks get through, simulating electrical arcs.
arcing = np.random.uniform(-1, 1, len(t))
arcing[np.abs(arcing) < 0.95] = 0 # Gate out the quiet noise

# Give the arcs a 120Hz electrical stutter
electric_stutter = np.sin(2 * np.pi * 120 * t)
crackle = arcing * electric_stutter

# Envelope: Snaps on exactly at 4.0 seconds (Breakeven)
crackle_env = np.where(t >= 4.0, 1.0, 0.0)
crackle = crackle * crackle_env * 2.5 # Boosted volume

# ---------------------------------------------------------
# MASTER MIXDOWN & COMPRESSION
# ---------------------------------------------------------
master_audio = hum + spin_up + clack + roar + crackle

# SOFT-CLIPPING: This is the secret. Using the hyperbolic tangent (tanh)
# squashes the massive peaks down smoothly. It makes the audio sound 
# incredibly LOUD and aggressive without digital distortion.
master_audio = np.tanh(master_audio * 1.5)

# Convert to 16-bit PCM WAV
audio_16bit = np.int16(master_audio * 32767)
wav_filename = "reactor_audio_heavy.wav"
wavfile.write(wav_filename, sample_rate, audio_16bit)

# ---------------------------------------------------------
# FFMPEG MUXING
# ---------------------------------------------------------
video_filename = "orbitron_startup_sequence.mp4"
output_filename = "FINAL_ORBITRON_TEST.mp4"

if os.path.exists(video_filename):
    print("Muxing Heavy Audio to Video...")
    cmd =[
        "ffmpeg", "-y", 
        "-i", video_filename, 
        "-i", wav_filename, 
        "-c:v", "copy", 
        "-c:a", "aac", 
        "-b:a", "192k",
        "-strict", "experimental", 
        output_filename
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("==================================================")
    print(f"SUCCESS! Play '{output_filename}'. Warning: Turn your volume down slightly.")
    print("==================================================")
else:
    print(f"Video {video_filename} not found. Audio saved as {wav_filename}.")
