### The p-¹¹B multi-step fusion reaction

The proton-boron ($p\text{-}^{11}\text{B}$) fusion reaction is a sequential, multi-step nuclear process that transitions through short-lived intermediate states rather than occurring simultaneously. The primary reaction pathway is written as:

$$
^{1}\text{H} + ^{11}\text{B} \rightarrow ^{12}\text{C}^* \rightarrow ^{4}\text{He} + ^{8}\text{Be}^* \rightarrow 3\ ^{4}\text{He}
$$

The step-by-step sequence is characterized by the following phases:

*   **Step 1: Proton Capture and Compound Nucleus Formation:** A proton ($^{1}\text{H}$) fuses with a boron-11 ($^{11}\text{B}$) nucleus, creating a highly unstable, excited compound carbon-12 ($^{12}\text{C}^*$) state. When formed via the dominant 675 keV resonance, the carbon-12 exists primarily in a $1^-$ quantum spin state.
*   **Step 2: Primary Alpha Emission ($\alpha_0$):** In approximately $10^{-21}$ seconds, the excited $^{12}\text{C}^*$ nucleus decays by ejecting a primary helium-4 nucleus (alpha particle, $\alpha_0$), leaving behind an excited beryllium-8 ($^{8}\text{Be}^*$) nucleus:

$$
^{12}\text{C}^* \rightarrow ^{4}\text{He} + ^{8}\text{Be}^*
$$

*   **Step 3: Beryllium Splitting ($\alpha_1, \alpha_2$):** The resulting $^{8}\text{Be}^*$ nucleus is highly unstable and splits within a fraction of a femtosecond into two secondary helium-4 nuclei ($\alpha_1$ and $\alpha_2$):

$$
^{8}\text{Be}^* \rightarrow 2\ ^{4}\text{He}
$$

This step-by-step mechanism explains why aneutronic reactor designs yield safely contained charged particles instead of high-energy neutrons.

#### Thermodynamic Threshold and the Coulomb Barrier

Initiating this reaction requires overcoming the electrostatic repulsion between the positive charges of the proton ($Z_1 = 1$) and the boron-11 nucleus ($Z_2 = 5$).

To calculate the classical Coulomb barrier ($V_c$)—the energy needed for the proton to touch the surface of the boron-11 nucleus—we use:

$$
V_c = \frac{1}{4\pi\varepsilon_0} \frac{q_1 q_2}{R_1 + R_2}
$$

With standard nuclear radii formulas ($R \approx 1.2 \times A^{1/3}\text{ fm}$):
*   Proton radius ($R_1$) $\approx 1.2\text{ fm}$
*   Boron-11 radius ($R_2 \approx 1.2 \times 11^{1/3}$) $\approx 2.67\text{ fm}$
*   Total separation distance ($R = R_1 + R_2$) $\approx 3.87\text{ fm}$

Using the electrostatic constant $k_e = \frac{e^2}{4\pi\varepsilon_0} \approx 1.44\text{ MeV}\cdot\text{fm}$:

$$
V_c \approx \frac{1.44 \times 1 \times 5}{3.87\text{ fm}} \approx 1.86\text{ MeV}
$$

According to classical mechanics, overcoming this barrier would require a kinetic energy of $1.86\text{ MeV}$ (equivalent to over 21 billion Kelvin).

However, quantum-mechanical tunneling allows the proton to penetrate the barrier at lower energies. The probability of tunneling (the reaction cross-section, $\sigma$) is highly dependent on the energy of the colliding particles and is dominated by two low-energy resonances in the center-of-mass frame:
1.  **The 148 keV Resonance:** A narrow peak where the cross-section reaches $\approx 0.1\text{ barns}$.
2.  **The 675 keV Resonance:** A much broader and higher peak where the cross-section reaches its absolute maximum of $\approx 1.4\text{ barns}$.

Because the 675 keV resonance is over ten times stronger and significantly broader, the absolute maximum rate of fusion occurs when the bulk of the colliding particles possess energies near this peak.

Using the Boltzmann relation, temperature ($T$) and average kinetic energy ($E$) are linked by:

$$
E = k_B T
$$

Given the conversion factor $1 \text{ eV} \approx 11,604 \text{ K}$, we can find the thermal equivalent of this peak energy:

$$
E = \frac{8,000,000,000\text{ K}}{11,604\text{ K/eV}} \approx 689,400\text{ eV} \approx 690\text{ keV}
$$

Because $675\text{ keV}$ translates directly to $\approx 7.8 \text{ billion Kelvin}$, a thermal plasma must be maintained at approximately **8 billion Kelvin** to align the average thermal motion of the ions with the optimal resonance peak.

#### Side-Channel Reactions

In a real operating reactor, minor side-channel reactions occur alongside the primary pathway, producing penetrating, unconfined "extra" particles:

1.  **Radiative Capture (occurrence rate $\approx 0.01\%$):** Occurs when the compound carbon-12 nucleus drops directly to its ground state instead of splitting, emitting a high-energy gamma-ray photon:

$$
^{1}\text{H} + {}^{11}\text{B} \rightarrow {}^{12}\text{C} + \gamma \ (15.9\text{ MeV})
$$

2.  **Alpha-Boron Interactions (occurrence rate $\approx 0.1\%$):** Fast alpha particles produced in the primary reaction collide with the boron-11 fuel, generating a minor neutron flux:

$$
\alpha + {}^{11}\text{B} \rightarrow {}^{14}\text{N} + n \ (157\text{ keV})
$$

3.  **High-Energy Endothermic Reaction:** Protons in the high-energy tail of the distribution trigger a reaction that produces an endothermic neutron and radioactive Carbon-11:

$$
p + {}^{11}\text{B} \rightarrow {}^{11}\text{C} + n \ (-2.8\text{ MeV})
$$

### Energy output of the p-11B fusion reaction

The primary $p\text{-}^{11}\text{B}$ reaction yields a total net energy of $8.7\ \mathrm{MeV}$ per reaction. This net energy is converted entirely into the kinetic energy of the three resulting helium-4 (alpha) particles:

*   The primary alpha particle ($\alpha_0$) carries approximately $3.76\ \mathrm{MeV}$.
*   The two secondary alpha particles ($\alpha_1$ and $\alpha_2$) split the remaining energy, carrying approximately $2.46\ \mathrm{MeV}$ each.

Because the energy is released as the kinetic energy of charged alpha particles rather than high-energy neutrons, the reaction is primarily aneutronic. These charged particles can theoretically be contained electromagnetically or converted directly into electrical energy, reducing reliance on conventional thermal cycles.

However, minor energy losses and alternative emissions occur via the side-channel reactions noted above, which release energy in the form of a $15.9\ \mathrm{MeV}$ gamma ray, a $157\ \mathrm{keV}$ neutron, or an endothermic loss of $2.8\ \mathrm{MeV}$ (accompanied by a neutron and Carbon-11).

### Can a practical aircraft operate in the presence of an 8GK reaction?

To evaluate whether a practical aircraft can operate in the presence of an 8 billion Kelvin (8 GK) reaction, we must distinguish between thermal and non-thermal (beam-like) plasma systems, and then assess the real-world thermal and radiation loads.

#### Thermal Heat vs. Directed Kinetic Energy (The Orbitron)

In a thermalized plasma system (such as a tokamak), particles collide constantly, randomizing their velocities into a Maxwell-Boltzmann distribution. In this configuration, an 8 GK temperature represents chaotic, high-density thermodynamic heat. If this plasma makes direct contact with a physical wall, it will instantly vaporize it.

An Orbitron-style reactor, however, is a **non-thermal system**. By utilizing a 600 kV central cathode, positive ions (protons and boron-11) are accelerated to a kinetic energy of 600 keV. While 600 keV mathematically equates to $\sim 7$ to $8$ billion Kelvin, the ions are locked in highly organized, directed orbits (which can be further organized using laminar flow techniques).

Because the velocity is directed rather than chaotic, this is directed kinetic energy rather than ambient thermal heat. In an ideal scenario with absolute vacuum and perfect confinement, the containment vessel walls would remain at room temperature.

#### Reality of Losses and Airborne Engineering Constraints

In a practical engineering design, confinement is imperfect, and three primary physical mechanisms transfer energy to the containment vessel, creating high-temperature thermal and radiation loads:

1.  **Bremsstrahlung (X-Ray) Radiation:** When energetic 600 keV electrons and boron ions ($Z=5$) interact, the electrons deflect and decelerate rapidly, releasing their kinetic energy as high-energy X-ray photons. Because these radiative losses scale with $Z^2$, the Bremsstrahlung losses in a $p\text{-}^{11}\text{B}$ reactor are 25 times higher than in a hydrogen-hydrogen system. These X-rays pass directly through electrostatic and magnetic confinement fields, presenting a continuous, high-intensity radiant energy flux that will rapidly heat the containment walls to their melting point without active cooling.
2.  **Charge-Exchange (CX) Losses:** Because an absolute vacuum is practically impossible to maintain, background neutral gas molecules will always be present. A fast, orbiting 600 keV ion can capture an electron from a cold neutral atom, instantly becoming a fast neutral. No longer bound by the cathode's electrostatic field or magnetic confinement, this fast neutral flies out in a straight tangent line, slamming into the containment wall and converting its kinetic energy into localized thermal heat and material sputtering.
3.  **Scattering and Grid/Cathode Collisions:** Ion-ion collisions cause scattering. Some scattered particles spiral outward to strike the containment walls, while others lose angular momentum and collide directly with the 600 kV central cathode, risking ablation or melting of the electrode.

#### Implications for Aircraft Integration

For an aircraft to operate with a $p\text{-}^{11}\text{B}$ reactor, the system must handle these high-temperature thermal loads and radiation fluxes. This introduces several severe engineering constraints:

*   **Active Cooling Systems:** Heavy shielding or active cooling (such as water-cooled copper jackets) is required to manage the intense Bremsstrahlung X-ray flux and prevent the containment vessel from melting.
*   **Vacuum Maintenance:** High-performance, robust vacuum systems are necessary to minimize charge-exchange losses and prevent localized wall damage.
*   **Radiation Shielding:** Effective shielding is required to protect the aircraft's crew, avionics, and airframe from continuous X-rays, as well as the minor neutron and gamma fluxes produced by side-channel reactions.
*   **Weight Constraints:** The weight of the active cooling systems, radiation shielding, and high-voltage power supplies must be balanced against the lift requirements of a practical aircraft.

While the non-thermal nature of an Orbitron prevents the reactor walls from melting via direct plasma contact, the secondary heat and radiation loads from Bremsstrahlung, charge-exchange, and particle scattering present significant engineering challenges for integration into a practical aircraft.
