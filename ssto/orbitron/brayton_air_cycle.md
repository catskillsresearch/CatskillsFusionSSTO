The thermodynamic cycle of this propulsion system is modeled as an **open-loop, externally heated, electrically driven Brayton cycle**. While conventional jet engines rely on internal combustion—where fuel is mixed directly with the working fluid (air) and ignited [1, 3]—this design decouples the compression and heating mechanisms. It relies on indirect thermal transfer and electric turbomachinery, eliminating chemical emissions and bypassing several traditional metallurgical limitations of gas turbines.

### Cycle Configuration and the Dorsal Intake

Instead of a traditional nose or wing intake, the engine utilizes a fuselage-integrated dorsal scoop (resembling the S-duct intake found above the tail of a Boeing 727) to capture ambient air. The air-breathing Brayton cycle operates continuously, using atmospheric air as the working fluid. However, because the heat is added externally through the reactor's hot jacket, there is no combustion and no mixing of fuel or combustion products into the air stream.

### The Four Stages of the Cycle

In an air-standard thermodynamic analysis, the open cycle is modeled with the following stages:

1. **Isentropic Compression ($1 \rightarrow 2$):** Ambient air enters the S-duct intake and is mechanically compressed by a rotary compressor. In this architecture, the compressor consists of turbofan blades driven by an electric motor rather than a mechanical shaft connected to an exhaust turbine. This compression stage increases both the pressure ($P$) and temperature ($T$) of the air.
2. **Isobaric Heat Addition ($2 \rightarrow 3$):** The compressed air is channeled over the hot external jacket of the proton-boron ($p\text{-}^{11}\text{B}$) fusion reactor. Heat transfer occurs conductively and convectively through the jacket walls, heating and exciting the air at nearly constant pressure. Because there is no fuel injection or combustion, the chemical composition of the working fluid remains unchanged.
3. **Isentropic Expansion ($3 \rightarrow 4$):** The highly excited, high-pressure air expands as it is propelled through a compressing and focusing nozzle. In a traditional Brayton cycle, a portion of this expansion must occur across a turbine to extract the shaft work needed to run the compressor [3, 9]. Because the compressor in this system is driven by an independent electric motor, the entirety of the expansion process is utilized in the nozzle to maximize exhaust velocity and generate forward thrust.
4. **Isobaric Heat Rejection ($4 \rightarrow 1$):** The hot exhaust air is discharged into the atmosphere, which acts as an infinite heat sink, while fresh ambient air is continuously drawn into the intake to sustain the cycle [1, 2].

```
       [1] Intake Scoop (S-duct)
               │
               ▼
       [2] Electric Compressor (Turbofan driven by motor)
               │
               ▼
       [3] Fusion Reactor Hot Jacket (Isobaric External Heating)
               │
               ▼
       [4] Compressing/Focusing Nozzle (Expansion & Thrust)
```

### Mathematical Efficiency and Power Balance

In a standard ideal Brayton cycle, the thermal efficiency ($\eta_{\text{th}}$) is a function of the compressor pressure ratio ($r_p = P_2/P_1$) and the specific heat ratio of air ($\gamma \approx 1.4$):

$$
\eta_{\text{th}} = 1 - \frac{1}{r_p^{(\gamma - 1)/\gamma}}
$$

For an electrically driven, externally heated cycle, the overall system energy balance must account for the electrical work input to the compressor ($W_c$) and the thermal energy input from the reactor ($Q_{\text{in}}$).

The electrical work required by the compressor per unit mass flow rate ($\dot{m}$) is:

$$
w_c = \frac{W_c}{\dot{m}} = \frac{C_p (T_2 - T_1)}{\eta_c}
$$

where $C_p$ is the specific heat of air and $\eta_c$ is the isentropic efficiency of the compressor.

The thermal energy added to the air by the fusion reactor's jacket is:

$$
q_{\text{in}} = \frac{Q_{\text{in}}}{\dot{m}} = C_p (T_3 - T_2)
$$

The kinetic energy of the exhaust jet ($w_j$) generated through the nozzle expansion is:

$$
w_j = C_p (T_3 - T_4) \cdot \eta_n
$$

where $\eta_n$ is the nozzle efficiency. For the cycle to produce net thrust, the total thermal energy converted to kinetic energy must exceed the electrical work required to run the compressor, taking into account the efficiency of the electric motor and the reactor's electrical power generation system.

### Engineering Advantages and Deviations

By utilizing an externally heated, electrically driven configuration, this cycle departs from traditional jet engines in several key areas [10]:

- **Bypassing Turbine Inlet Temperature (TIT) Limits:** In standard gas turbines, the maximum operating temperature is strictly limited by the metallurgical limits of the turbine blades, which are subject to extreme centripetal stress in the hot gas path [3]. Because this design drives the compressor electrically and does not require an exhaust turbine, the peak cycle temperature ($T_3$) is limited only by the thermal tolerances of the reactor jacket and the nozzle materials.
- **Constant Working Fluid Composition:** Traditional combustion changes the chemical composition of the gas (adding water vapor, carbon dioxide, and other combustion products), which alters its thermodynamic properties [1, 8]. In this externally heated cycle, the working fluid remains pure atmospheric air, simplifying aerodynamic and thermodynamic modeling.
- **Decoupled Turbomachinery:** The use of an electric motor to drive the compressor allows the compression ratio and mass flow rate to be controlled independently of the reactor's thermal output, offering greater operational flexibility across different altitudes and flight speeds [13].

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
