This report is inspired by a fusion device called the Orbitron developed by Avalanche Energy. It explores the feasibility of an air-breathing jet propulsion system powered directly by a proton-boron ($p\text{-}^{11}\text{B}$) Orbitron-style fusion reactor designed to produce approximately 3.5 megawatts (MW) of total raw power.

To evaluate this concept, we performed a series of numerical simulations and analyses:

1. **The Ideal Test:** First, we simulated the system using target fusion reaction rates, assuming ideal materials and conditions (referred to as "Unobtanium" levels U1 through U4).
2. **The Stress Test:** Next, we conducted a conservative simulation based on reaction rates documented in existing scientific literature to establish the minimum baseline performance required for viability.
3. **The Technology Review:** Finally, we mapped out the materials science and engineering advancements required to bridge the gap between current technology and the ideal parameters.

The physical geometry of the propulsion system was modeled using CadQuery and Blender, and the electron behavior within the reactor was simulated using WarpX Particle-In-Cell (PIC) software. The 3D models from Blender and control input reaction surfaces saved from multiple WarpX runs with parameter variations also serve as inputs for "real world" operating simulation in FlightGear.

In this design, an intake scoop (resembling the dorsal S-duct on a Boeing 727) draws in ambient atmospheric air. This air is compressed by an electrically driven rotary compressor (turbofan blades powered by an electric motor). Rather than utilizing internal chemical combustion, the compressed air is routed over the high-temperature external jacket of the proton-boron fusion reactor. This process heats and excites the air via indirect thermal contact before it is propelled through a compressing and focusing nozzle to act as a jet engine. This configuration represents an **open-loop, externally heated, electrically driven Brayton cycle**.

The primary objective of this study is to determine whether a **3.5 MW** power plant can sustain operation while remaining within safe engineering limits. Specifically, we evaluate the thermal and mechanical limits of the reactor's inner walls, electrical dielectric strength (to prevent sparking and leakage), high-temperature superconducting (HTS) magnets, and reaction kinetics.

This report is self-contained and details the governing equations, material properties, simulation results, and technology gap analyses below. Under ideal material assumptions, the simulated system achieves the target 3.5 MW power output while satisfying the primary design constraints. Under more realistic parameters, the analysis outlines the critical development pathways required for key components.
