# Orbitron test stand — operator instructions

FlightGear operator guide for the **Orbitron-TestStand** rig. Canonical machine-readable
sequence: [`assembly_specs/orbitron_operator_console_spec.yaml`](assembly_specs/orbitron_operator_console_spec.yaml).
Gas path and plant mechanism: [`../../gas_flow.md`](../../gas_flow.md),
[`assembly_specs/orbitron_reference_plant.yaml`](assembly_specs/orbitron_reference_plant.yaml).

---

## Before you launch FlightGear

From the repo root, build the aircraft package (glTF, `orbitron.ac`, sounds, Nasal, JSBSim):

```bash
./stand.sh
```

Launch the stand (example — adjust paths to your FG install):

```bash
./stand.sh run-fgfs
```

Use **Operator View** (defined in `orbitron_aircraft_flightgear.yaml`). The **Screen** on the
control panel shows live thrust, airflow, and thrust-sled load cells.

---

## Startup sequence (panel or keyboard)

Perform these steps **in order**. The simulator enforces basic interlocks in `orbitron_ops.nas`.

| Step | Panel (click) | Key | When ON |
|------|-----------------|-----|---------|
| **1** | `Panel_Switch_APU` | **1** | Pad cart energizes starter bus (`Pad_Startup_Cart` → cable → motor) |
| **2** | `Panel_Switch_Starter` | **2** | Electric starter cranks compressor spool (requires step 1); crank sound plays |
| **3** | `Panel_Switch_Bleed` | **3** | Bellmouth → compressor annulus path open |
| **4** | `Big_Red_Button` | **SPACE** | Fusion **armed** — thrust and power outputs enabled (requires step 3) |

After step 3, raise compressor command with **U** (see run controls below). You should see
**Airflow (mdot)** on the Screen increase before ignite.

After step 4, use **W/S** to raise ion beam from ignition level toward full power.

**Procedure:** Turn **starter off** (key **2** or panel) once the spool is stable and the
turbine is driving the compressor (not modeled automatically — operator judgment).

---

## Run controls (after bleed is open)

| Keys | Property | Effect |
|------|----------|--------|
| **W** / **S** | `/controls/reactor/throttle` | Ion beam command → mA, thrust, mdot (full effect after ignite) |
| **U** / **J** | `/controls/orbitron/compressor` | Compressor / air-path command (effective only with bleed + spool drive) |
| **I** / **K** | `/controls/orbitron/cathode-pulse` | Cathode pulse / shear stability proxy |
| **M** | `/sim/model/reactor/debug-ui-window` | Extra telemetry window |

Compressor command is scaled in JSBSim as
`/fdm/jsbsim/systems/orbitron/compressor-effective` (bleed × spool factor × command).

---

## Interlocks (automatic)

| Rule | Behavior |
|------|----------|
| Starter without APU | Starter is forced **off**; message in log |
| Ignite without bleed | Ignite is forced **off**; message in log |
| Starter engage + APU | One-shot pad crank sound (`orbitron_pad_starter_crank.wav`) |

---

## Screen telemetry

The operator **Screen** (10 Hz, `reactor_ui.nas`) shows:

- Pad APU, starter, bleed, reactor ignite state
- Ion beam (mA), cathode kV, compressor command
- Gross power, DEC current/bias, Brem. heat, Q-factor
- Thrust (lbf / kN), jet equivalent exhaust speed, jet kinetic power
- Airflow (mdot), sled load total, four corner load cells (+X±Y)

Sequence hint line at top of screen:
`SEQ: 1 APU  2 START  3 BLEED  SPACE IGNITE  W/S U/J`

---

## Quick first-run checklist

1. **1** — Pad APU ON  
2. **2** — Starter ON (listen for crank)  
3. **3** — Bleed OPEN  
4. **U** — Raise compressor; confirm mdot on Screen  
5. **SPACE** — Ignite (red button)  
6. **W** — Increase throttle toward desired burn level  
7. **2** — Starter OFF when spool is stable (procedure)  

---

## What the sim does *not* model yet

- Spool RPM, clutch, or automatic turbine takeover  
- Automatic starter drop-out on light-off  
- Fuel valve interlocks (H₂ / B₂H₆) beyond the 0D surrogate  

Those steps are documented in the reference plant for design intent; FlightGear uses a
**0D bilinear surrogate** gated by the switches above.

---

## Related files

| File | Role |
|------|------|
| `assembly_specs/orbitron_operator_console_spec.yaml` | Switch properties, picks, interlock flags |
| `assembly_specs/orbitron_aircraft_flightgear.yaml` | FG set.xml, keyboard, Nasal load list |
| `assembly_specs/orbitron_nasal.yaml` | Generated `orbitron_ops.nas`, `reactor_ui.nas` |
| `assembly_specs/orbitron_lab.yaml` | Panel mesh instances and colors |
| `../../Aircraft/Orbitron-TestStand/` | Built FG aircraft package (after `./stand.sh`) |
