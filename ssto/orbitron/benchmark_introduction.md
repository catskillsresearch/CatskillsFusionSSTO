This report is inspired by a fusion device called the Orbitron developed by Avalanche Energy. It explores the feasibility of an air-breathing jet propulsion system powered directly by a proton-boron ($p\text{-}^{11}\text{B}$) Orbitron-style fusion reactor designed to produce approximately 3.5 megawatts (MW) of total raw power.

Here $⟨σv⟩$ denotes the **fusion reactivity**: the fusion cross section $σ(E)$ multiplied by ion relative speed $v$, then averaged over the ion velocity distribution at the operating ion temperature. In this notation, $E$ is center-of-mass collision energy, $n_1$ and $n_2$ are the reacting-ion number densities (for p-¹¹B, proton and boron-ion density), and $R$ is volumetric fusion reaction rate (reactions per m³ per s). The model scaling is $R \propto n_1 n_2⟨σv⟩$, so $⟨σv⟩$ is the key bridge from plasma conditions to predicted fusion power. In this benchmark, changing from the design-calibrated branch to the literature branch changes $⟨σv⟩$ by about three orders of magnitude near the operating point, which is why the same geometry and fueling can move from MW-class closure to a strong shortfall.

**HTS** means **high-temperature superconductor** — here, the liquid-methane-cooled solenoid that sets the axial magnetic field in the plasma bore (U3 in the unobtanium gates).

We report **three scenarios** (definitions and rules in **Benchmark Methodology** below):

1. **(a) Pretend — design target:** design-calibrated ⟨σv⟩, 600 kV class, unity unobtanium. The proof chain (steps 0–8) runs on this path. Level-1 plant closure is **not** measured fusion yield.
2. **(b) Today — COTS (Commercial Off The Shelf) + experiment:** literature ⟨σv⟩, Avalanche-class **300 kV**, same pad fueling as (a), wall and HTS limits at published values. No tuning to recover MW.
3. **(c) Minimum — stress inverse:** literature ⟨σv⟩ with optimizer free to raise `fusion_reactivity_scale` (~10³×) to approach target; margin inverse checks back-solve ≈ (a).

The physical geometry was modeled using CadQuery and Blender. **WarpX PIC (step 01)** validates electron loading at the **design-point (a)** under prescribed crossed fields $E \times B$, where $E$ is the imposed electric field and $B$ is the imposed magnetic field; this stage checks charged-particle confinement behavior, not fusion gain (here $Q = P_{\mathrm{fusion}} / P_{\mathrm{input}}$). A separate operations simulator integrates the test stand for pad procedures.

In this design, a fuselage-integrated dorsal S-duct scoop feeds a single-spool **compressor–turbine** train with **externally heated Brayton** air (no combustion in the core path).

Under **(a)** the simulated plant reaches the **3.5 MW** headline while satisfying level-1 gates (0D plant + U1–U4; see **Benchmark Methodology**). Under **(b)** expect a large shortfall — that is the quantitative “mountain.” Under **(c)** the inverse states what effective reactivity and knobs would be required on literature σv.
