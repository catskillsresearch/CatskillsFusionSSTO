This report is inspired by a fusion device called the Orbitron developed by Avalanche Energy. It explores the feasibility of an air-breathing jet propulsion system powered directly by a proton-boron ($p\text{-}^{11}\text{B}$) Orbitron-style fusion reactor designed to produce approximately 3.5 megawatts (MW) of total raw power.

We report **three scenarios** (see [`BENCHMARK_METHODOLOGY.md`](BENCHMARK_METHODOLOGY.md)):

1. **(a) Pretend — design target:** design-calibrated ⟨σv⟩, 600 kV class, unity unobtanium. The proof chain (steps 0–8) runs on this path. Tier-1 closure is **not** measured fusion yield.
2. **(b) Today — COTS + experiment:** literature ⟨σv⟩, Avalanche-class **300 kV**, same pad fueling as (a), wall/HTS at published limits. No tuning to recover MW.
3. **(c) Minimum — stress inverse:** literature ⟨σv⟩ with optimizer free to raise `fusion_reactivity_scale` (~10³×) to approach target; margin inverse checks back-solve ≈ (a).

The physical geometry was modeled using CadQuery and Blender. **WarpX PIC (step 01)** validates electron loading at the **design-point (a)** — prescribed E×B; not fusion Q. FlightGear integrates the test stand for operations simulation.

In this design, a fuselage-integrated dorsal S-duct scoop feeds a single-spool **compressor–turbine** train with **externally heated Brayton** air (no combustion in the core path).

Under **(a)** the simulated plant reaches the **3.5 MW** headline while satisfying Tier-1 gates. Under **(b)** expect a large shortfall — that is the quantitative “mountain.” Under **(c)** the inverse states what effective reactivity and knobs would be required on literature σv.
