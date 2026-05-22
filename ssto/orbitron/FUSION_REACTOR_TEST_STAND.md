# The Orbitron Fusion Reactor Test Stand — From Pad Foundation to First Hot Run

*A walk through every lab assembly that ships with a hero render (`Aircraft/Orbitron-TestStand/build/*.png`), in the order those pieces come together on the pad, followed by how an operator brings the rig to life in FlightGear.*

---

## What this rig is

The **Orbitron fusion arcjet laboratory** is a pad-credible ground article: a **p-¹¹B** Orbitron-class magneto-electrostatic core (topology inspired by Avalanche’s public **D₂** machine—they have not published p-¹¹B) embedded in a **single-spool, fusion-heated Brayton** duct. Ambient **air** is the reaction mass—scooped at the bellmouth, compressed, heated in an annulus around the hot plasma hardware and in a downstream plenum mixer, expanded through a turbine that drives the same shaft as the compressor, and finally accelerated out a convergent–divergent nozzle to produce measurable thrust on a four-corner load-cell sled.

After dissociation in the discharge, the headline channel is **¹H + ¹¹B → 3 ⁴He**. **H₂** and **solid ¹¹B** feed tangential keV ion beam injectors; **⁴He ash** vents into the nozzle plenum. Design cathode class **~−600 kV** (not Avalanche’s **~300 kV D₂** milestone). **Liquid CH₄** routes to the anode wall-thermal jacket (see [`UNOBTANIUM.md`](UNOBTANIUM.md)). No DEC grid, grid tie, or multi-MV arc in the intake duct.

Propulsion axis runs **−X → +X** (intake to nozzle). The tank farm sits on **+Y**. Hero PNGs are generated headless from each assembly glTF (`make orbitron-lab-pngs` or `./stand.sh`) on a factory-gray backdrop with a three-quarter hero camera—one image per sub-assembly plus the full lab.

---

## Assembly in order — part by part

### 1. Thrust sled — the measurable foundation

![Thrust sled](../../Aircraft/Orbitron-TestStand/build/thrust_sled.png)

Everything that follows needs a place to stand and a way to prove thrust happened. The **thrust sled** is that place: longitudinal rails, cross ties, and a deck slab sized so the engine inlet pivot height matches the bellmouth pose used in CAD. Four **load-cell pucks** sit at the deck corners—**+X+Y**, **−X+Y**, **+X−Y**, **−X−Y**—not as finite-element strain gauges but as pad bookkeeping for how thrust and compressor command redistribute weight across the corners.

Above the cells, an **engine mount frame** rises: four posts on the cell tops and a shared plate. The entire air-breathing engine stack will pivot on that plate at `ENGINE_MOUNT_TOP_Z`, giving a continuous load path from jet reaction force → nozzle flange → engine structure → mount plate → posts → cells → rails → the ground. In simulation, the same corners feed the operator **Screen**; in the shop, they are where you trust your thrust accounting.

*Build narrative:* Lay rails, tie the frame, set cells, torque the mount posts, level the deck. Until this is right, nothing else on the pad is calibrated.

---

### 2. Hydrogen tank assembly — proton inventory and beam stability

![Hydrogen tank assembly](../../Aircraft/Orbitron-TestStand/build/hydrogen_tank_assy.png)

The **hydrogen tank assembly** is the first of three coherent fuel packages on the farm. A green **H₂** cylinder, stencil, roof valve boss, flex jumper, and **hydrogen trunk** route toward the tangential **NBI injectors** on the core. This is **not** bottled fusion helium—**⁴He** is a product that leaves through the **helium ash vent** after burn. Here, hydrogen supplies proton inventory and stability co-injection for the p-¹¹B leap on the same Orbitron injection geometry Avalanche describes for D₂.

*Build narrative:* Set the cylinder on the farm skid footprint, dress the decal, land the roof boss, and run the trunk along **+X** with clearance for the propulsive train. Pressure-test the jumper before the trunk is hard-connected at the bay.

---

### 3. Boron tank assembly — the gaseous boron carrier

![Boron tank assembly](../../Aircraft/Orbitron-TestStand/build/boron_tank_assy.png)

**Boron (solid ¹¹B)** is the core fuel leg: a dedicated cylinder, **solid ¹¹B** marking, feed pipe, and **boron trunk** to the same tangential keV injectors that receive hydrogen. Decaborane dissociates in the discharge; natural boron is ~80% **¹¹B** unless enriched. Same Orbitron class as a deuterium machine—only the species and ash handling change.

*Build narrative:* Mirror the hydrogen package on the shared **tank farm platform**—decal, boss, trunk—with segregated routing so boron and hydrogen services never share a confused manifold label.

---

### 4. Methane tank assembly — SSTO wall thermal, not core fuel

![Methane tank assembly](../../Aircraft/Orbitron-TestStand/build/methane_tank_assy.png)

The **methane tank assembly** is deliberately optional for the core p-¹¹B story. A cryogenic **CH₄** dewar, markings, feed boss, and **cryo methane piping** serve **anode and boundary Bremsstrahlung cooling** on a spaceplane article. It is **not** the boron carrier and not part of the headline fusion channel. On the lab pad it completes the visual of a full SSTO services farm.

*Build narrative:* Mount the dewar, run cryo piping toward **magnet service bosses** and compressor intercooling ties (conceptual on this coarse mesh), and keep labels honest so operators do not confuse CH₄ with beam fuel.

---

### 5. Tank farm — one skid, three species

![Tank farm assembly](../../Aircraft/Orbitron-TestStand/build/tank_assy.png)

With the three packages placed, the **tank farm assembly** reads as a single pad-mounted cluster: shared **tank farm platform** spanning the cylinder footprints, **methane**, **boron**, and **hydrogen** children each carrying tank + decal + boss + trunk as exportable sub-glTF units. From the operator’s chair on **+Y**, the color coding tells the story—green hydrogen, marked solid B-11, pale methane for cryo services.

*Build narrative:* Align the platform, tie down all three vessels, verify trunk exit azimuths toward the reactor bay, and only then accept the farm as “fuel ready” for integrated leak checks.

---

### 6. Turbofan intake — air and the pad starter land on −X

![Turbofan intake](../../Aircraft/Orbitron-TestStand/build/turbofan_intake.png)

The **−X** end of the engine is where the outside world enters. A coarse **bellmouth** captures and diffuses air into a **compressor can** on the spool shaft. Propulsive air is destined for the **outer jacket and annulus** around the plasma hardware—not through the plasma bore, which remains a sealed electrostatic volume. Co-axial with this inlet, on the completed engine, lives the **turbine** on **+X**; between them will sit the hot reactor bay.

Pad-only hardware also anchors here: **pad startup cart**, **power cable**, and **orange starter motor** on the compressor spool (grouped as pad startup services in the logical tree, riding on the sled deck). They are excluded from flight mass—rig power to spin the shaft until the turbine can drive the compressor after fusion heats the duct gas.

*Build narrative:* Hang the bellmouth, mate the compressor housing, land the starter pod and cable tray from the cart on the deck, and rotate the spool by hand before any HV or fuel is armed.

---

### 7. Reactor bay — the Orbitron inside the duct

![Reactor bay](../../Aircraft/Orbitron-TestStand/build/reactor_bay.png)

The **reactor bay** is the moral center of the machine. Inside it:

- **Fusion reactor:** gridless **anode** shell, on-axis **cathode** (~600 kV design class), **magnet** for **2 T** axial **B**, tangential **NBI injectors** for keV **H⁺ / B⁺**, **insulators**, and **magnet service bosses** for CH₄ wall thermal, cryo jacket tap, and HV feedthrough. One anode channel in the lab mesh stands in for a thousand-channel flight article.
- **Reactor inlet jacket:** **reactor bay inlet shroud**—compressor discharge washes the niobium pressure boundary in an annulus, then flows toward the hot duct.
- **Reactor duct shielding:** a coarse **blast detuner** module (annulus sleeve, shock-conditioning insert, brackets/seals) that softens bypass-stream shocks—not acoustic silencing, and not the fusion exhaust path, which uses **fusion hot gas outlet** and **helium ash vent line** instead.

Fusion adds enthalpy by **wall convection** on hot metal and by **mixing** hot core exhaust and ash at the downstream plenum. It does not “push air through the plasma.”

*Build narrative:* Lower the core into the shroud, torq the detuner flanges, connect H₂ and solid ¹¹B trunks to the injector manifold, dress the HV umbilical from the console side, and verify the ash vent aims at the nozzle plenum route before the +X train is closed.

---

### 8. Propulsive nozzle — turbine work and expansion on +X

![Propulsive nozzle](../../Aircraft/Orbitron-TestStand/build/propulsive_nozzle.png)

Downstream of the hot bay, the **propulsive nozzle assembly** completes the Brayton spine: **nozzle inlet plenum** (mixer and structural adapter), **turbine can** (shaft power back to the compressor), **CD contour** (throat and divergent segment), and **nozzle exit hardware** (flange to the thrust frame, tail bosses). The turbine’s job is to extract enough shaft work to balance compressor demand after light-off; what remains expands to produce the axial force the load cells sum.

*Build narrative:* Mate plenum to bay outlet, clock the turbine to the shaft, install the CD segments, and bolt the exit flange to the mount frame posts you prepared on the sled.

---

### 9. Air-breathing engine — intake, bay, and nozzle as one duct

![Air-breathing engine](../../Aircraft/Orbitron-TestStand/build/air_breathing_engine.png)

The three trains become one **air-breathing engine**: **turbofan intake** + **reactor bay** + **propulsive nozzle**, posed so the bellmouth pivot sits on the **engine mount frame** plate. This is the article you hang on the thrust sled when you speak about “the engine” as a single stack—fusion-heated Brayton with an embedded Orbitron, not a separate reactor bolted beside a pipe.

*Build narrative:* Lift the integrated duct as a unit, pin it to the mount plate, connect pad starter cable service, and confirm −X intake and +X nozzle clearances relative to tank trunks and console umbilical.

---

### 10. Control panel stand — eyes, hands, and the red button

![Control panel stand](../../Aircraft/Orbitron-TestStand/build/control_panel_stand.png)

Across the pad from the hot hardware, the **control panel stand** is the human interface: operator console, checklist plaque, **screen** for live telemetry, Space Shuttle–style **APU / starter / bleed** toggles (merged into `orbitron.ac` at build time), labels for beam and compressor axes, and the **big red button** for fusion ignite. A **high-voltage umbilical** runs schematically from the desk toward the cathode feed.

The screen is not decoration—it is the 10 Hz face of `reactor_ui`: pad states, ion beam milliamps, cathode kilovolts, compressor command, gross power, wall-heat proxy, thrust in lbf and kN, jet equivalent exhaust speed, airflow mdot, sled total load, and four corner cell readings. A sequence hint line reminds you: **1 APU → 2 START → 3 BLEED → SPACE IGNITE → W/S U/J**.

*Build narrative:* Set the desk, aim the screen toward the operator sightline, terminate HV and control harnesses, load the checklist plaque, and function-test picks before energizing the bay.

---

### 11. Orbitron laboratory — the finished test stand

![Orbitron laboratory complete](../../Aircraft/Orbitron-TestStand/build/orbitron_lab.png)

**Orbitron laboratory** is the full **`test_stand`** logical root: control panel, thrust sled with engine mounted, tank farm, pad startup services, methane wall-thermal services, and the complete air-breathing engine. Scene export root for FlightGear is **`fusion_arcjet_engine`**, wrapping this stand for visualization and integration discipline—the end product is the physical pad, not the simulator, but the same YAML drives both.

At this stage the pad story is complete: rails under cells under engine under tanks beside console, orange starter cable from cart to motor, trunks from farm to injectors, ash path from core to plenum, HV from desk to cathode, and a nozzle pointed so thrust fights the sled instead of the hangar doors.

*Build narrative:* Walk the pad, update the checklist plaque, run a cold integrated fit-up, and only then schedule first power.

---

## Operating the test stand — a narrative run sequence

With hardware built, operation on the **Orbitron-TestStand** FlightGear package follows the same story the panel engravings tell. Build the aircraft first from the repo root (`./stand.sh`), then launch (`./stand.sh run-fgfs`) in **Operator View** so the **Screen** and shuttle-style switches are in front of you.

### Before lights and fuel

You are confirming simulation assets, not replacing mechanical interlocks: glTF meshes, `orbitron.ac`, sounds, Nasal ops, JSBSim surrogate, and set XML must be current. Missing panel switch geometry fails loudly at load time—regenerate the shuttle panel AC if mounts move.

### Step 1 — Pad APU online

You throw **Pad APU** (**key 1** or `Panel_Switch_APU`). On the mesh, the **pad startup cart** on the sled deck energizes the starter bus; the heavy cable to the **pad startup motor** is live. Nothing cranks yet—you have only told the rig that ground power is allowed to reach the starter circuit.

### Step 2 — Starter engage

With APU proven, **Starter** (**key 2**). The electric motor on the **−X** compressor spool cranks the shaft; crank sound plays in sim. Interlocks force starter off if APU was skipped—listen for the crank, watch for spool response on your judgment, not an RPM gauge (the 0D surrogate does not solve spool RPM yet).

### Step 3 — Bleed air open

**Bleed** (**key 3**) opens the bellmouth → compressor annulus path. Now **U** (raise compressor command) begins to mean something: **airflow mdot** on the **Screen** should climb before you arm fusion. You are pumping reaction mass without asking the plasma to carry thrust.

### Step 4 — Spin-up before fire

Hold bleed, raise compressor with **U/J**, confirm mdot and corner loads twitch as commanded. Compressor effectiveness in JSBSim is **bleed × spool factor × command**—on a static pad you are still pretending the starter contributed shaft work until you procedurally release it.

### Step 5 — Ignite

When mdot looks honest, **SPACE** or the **big red button**. **Reactor ignite** sets fusion armed; thrust and power outputs gate on in the surrogate. Interlocks block ignite without bleed. Ion beam command (**W/S**) now moves you from ignition level toward full burn; **I/K** shapes cathode pulse / shear stability proxy against the rotating mode.

### Step 6 — Run and release the starter

Increase throttle (**W**) to the desired beam current milestone band. Watch **thrust lbf**, **sled total**, and the four corners shift with compressor (**U/J**) and throttle moments per `thrust_sled_load_cells`. When you believe turbine shaft work is balancing compressor demand—procedure, not automation—turn **starter off** (**key 2** again). The pad motor is meant to clutch out after takeover; the sim will not do that for you yet.

### Step 7 — Steady pad run and shutdown discipline

In steady run you are holding **H₂ / solid ¹¹B** injectants (not fully valve-interlocked in FG), cathode program, compressor schedule, and bleed state while the hot annulus and plenum mixer pour enthalpy into the air stream. **M** opens a debug telemetry window duplicating many **Screen** fields. Shutdown is the reverse consciousness: throttle down, disarm ignite, close bleed, drop compressor, starter off, APU off—mechanical fuel and HV isolation follow your real pad rules even when the sim is forgiving.

---

## What the simulator honors—and what remains procedure

The stand teaches a **fusion-heated air-breathing Brayton** with **Orbitron** core physics levers (tangential keV beams, cathode pulse, E×B electrons, ash vent) and pad-credible **thrust bookkeeping** on four cells. It does **not** yet model spool RPM, clutch, automatic turbine takeover, automatic starter dropout on light-off, or full fuel-valve interlocks beyond the 0D surrogate gates.

For machine-readable switches and properties, see [`assembly_specs/orbitron_operator_console_spec.yaml`](assembly_specs/orbitron_operator_console_spec.yaml). For the shorter checklist, [`OPERATOR.md`](OPERATOR.md). For gas paths and plant mechanism, [`../../gas_flow.md`](../../gas_flow.md) and [`assembly_specs/orbitron_reference_plant.yaml`](assembly_specs/orbitron_reference_plant.yaml). For core plasma basis, [`assembly_specs/orbitron_avalanche_core.yaml`](assembly_specs/orbitron_avalanche_core.yaml).

Hero renders regenerate with:

```bash
./stand.sh
# or: make orbitron-lab-pngs
```

Each PNG beside its glTF under `Aircraft/Orbitron-TestStand/build/`—the illustrations in this article.
