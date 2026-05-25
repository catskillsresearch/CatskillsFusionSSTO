The **air-breathing Brayton cycle** is an open-loop thermodynamic cycle that models the operation of gas turbine engines and jet propulsion systems [1, 3]. Unlike a closed Brayton cycle—which recirculates a fixed working fluid (such as helium or carbon dioxide) using heat exchangers [2]—an air-breathing Brayton cycle continuously draws in ambient atmospheric air to serve as both the working fluid and the oxidizer for internal combustion [3, 4]. It acts as the foundational thermodynamic model behind modern aviation jet engines (including turbojets, turbofans, and turboprops), high-speed ramjets, and land-based gas turbines used in utility power generation [5, 6].

### The Four Stages of the Ideal Cycle

While a physical engine is open to the atmosphere, classical thermodynamic analysis models it as a closed "air-standard" cycle where the exhaust and intake are connected by an imaginary isobaric heat-rejection process to complete the loop [1, 2]. The ideal cycle consists of four distinct stages:

1. **Isentropic Compression ($1 \rightarrow 2$):** Ambient air is drawn into the engine and compressed. In standard gas turbines, this is achieved mechanically using a rotary compressor (axial or centrifugal) [3]. In high-speed propulsion (like ramjets), compression is achieved through the "ram effect" of incoming supersonic air [6, 7]. This process significantly increases both the pressure and temperature of the working fluid.
2. **Isobaric Heat Addition ($2 \rightarrow 3$):** The compressed air enters the combustion chamber (or combustor), where fuel is injected and continuously burned [12]. Because the combustion chamber is open to flow, this process occurs at a nearly constant pressure. The chemical energy of the fuel is converted into thermal energy, dramatically increasing the gas temperature [8].
3. **Isentropic Expansion ($3 \rightarrow 4$):** The hot, high-pressure gas expands.
- In **shaft-power engines** (such as turboprops or power-generation turbines), the gas expands through a turbine, which extracts mechanical energy to drive the compressor and generate external rotational work [3, 9].
- In **pure jet propulsion engines** (such as turbojets), the gas expands through a turbine just enough to power the compressor, and the remaining high-pressure gas is expanded through a nozzle to accelerate the flow and generate thrust [6, 7].
4. **Isobaric Heat Rejection ($4 \rightarrow 1$):** The hot exhaust gases are expelled into the ambient atmosphere, which acts as an infinite heat sink [1, 2]. Fresh, cool atmospheric air is simultaneously drawn into the inlet to repeat the cycle.

### Mathematical Efficiency

For an ideal, cold air-standard Brayton cycle, the thermal efficiency ($\eta_{\text{th}}$) is derived as a function of the **pressure ratio** ($r_p = P_2/P_1$) and the specific heat ratio of the gas ($\gamma$, which is approximately $1.4$ for air at standard atmospheric conditions) [1]:

$$
\eta_{\text{th}} = 1 - \frac{1}{r_p^{(\gamma - 1)/\gamma}}
$$

According to this relationship, increasing the pressure ratio ($r_p$) directly increases the theoretical thermal efficiency of the cycle [9]. However, in physical engines, metallurgic limits restrict the maximum turbine inlet temperature, which in turn limits how high the pressure ratio can practically go without damaging the turbine blades [3].

### Real-World Deviations (Non-Ideal Cycles)

In actual air-breathing engines, several factors deviate from the ideal cycle [10]:

- **Isentropic Inefficiencies:** Real compressors and turbines suffer from aerodynamic drag, friction, and flow separation. This means compression requires more work than the ideal scenario, and expansion yields less work [3, 13].
- **Pressure Drops:** Friction in the intake duct, combustor, and exhaust nozzle causes pressure drops, meaning heat addition and heat rejection are not perfectly isobaric [10, 13].
- **Variable Specific Heats:** The thermodynamic properties of air change at extremely high temperatures, and the mass flow rate increases slightly in the combustor due to the addition of fuel [1, 8].

### Primary Applications

- **Aviation Propulsion:** Turbofans power commercial airliners due to high bypass efficiency, while turbojets and ramjets are utilized for supersonic military and high-speed flight [5, 7].
- **Power Generation:** Stationary gas turbines run on the air-breathing Brayton cycle. They are highly valued for their quick startup times and are often paired with a steam Rankine cycle (forming a Combined Cycle Gas Turbine, or CCGT) to capture waste exhaust heat and boost overall efficiency [9, 10].
- **Marine Propulsion:** Naval vessels use aeroderivative gas turbines for their high power-to-weight ratio and compact footprint [3, 11].

### References

[1] Çengel, Y. A., & Boles, M. A. (2015). *Thermodynamics: An Engineering Approach* (8th ed.). McGraw-Hill Education.
[2] Moran, M. J., Shapiro, H. N., Boettner, D. D., & Bailey, M. B. (2014). *Fundamentals of Engineering Thermodynamics* (8th ed.). Wiley.
[3] Saravanamuttoo, H. I. H., Rogers, G. F. C., Cohen, H., & Straznicky, P. V. (2009). *Gas Turbine Theory* (6th ed.). Pearson Education.
[4] Mattingly, J. D. (1996). *Elements of Gas Turbine Propulsion*. McGraw-Hill.
[5] Oates, G. C. (1997). *Aerothermodynamics of Gas Turbine and Rocket Propulsion* (3rd ed.). AIAA Education Series.
[6] Hill, P. G., & Peterson, C. R. (1992). *Mechanics and Thermodynamics of Propulsion* (2nd ed.). Addison-Wesley.
[7] Kerrebrock, J. L. (1992). *Aircraft Engines and Gas Turbines* (2nd ed.). MIT Press.
[8] Oates, G. C. (Ed.). (1978). *The Aerothermodynamics of Aircraft Gas Turbine Engines* (Report AFAPL-TR-78-52). Air Force Aero Propulsion Laboratory.
[9] Boyce, M. P. (2012). *Gas Turbine Engineering Handbook* (4th ed.). Butterworth-Heinemann.
[10] Horlock, J. H. (2003). *Advanced Gas Turbine Cycles*. Elsevier Science.
[11] Glassman, A. J. (Ed.). (1972). *Turbine Design and Application* (NASA SP-290). National Aeronautics and Space Administration.
[12] Bathie, W. W. (1996). *Fundamentals of Gas Turbines* (2nd ed.). Wiley.
[13] Walsh, P. P., & Fletcher, P. (2004). *Gas Turbine Performance* (2nd ed.). Blackwell Science.
