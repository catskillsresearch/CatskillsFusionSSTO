The propulsion thermodynamic cycle is an **open-loop, externally heated Brayton cycle** on a **single compressor–turbine spool**. Conventional jets add heat by burning fuel in the working fluid [1, 3]; here enthalpy is added when compressed air passes through a **hot annulus around the fusion first wall** (and mixes with a small **⁴He ash** stream) — **not** by flowing over the cryogenic HTS magnet. The working fluid remains atmospheric air; there is no combustion chemistry in the main path.

**Pad start:** an electric starter (APU cart) drives the shaft; **bleed air** opens the bellmouth → compressor annulus so the machine can ingest and compress air before fusion is armed. **Cruise / light-off:** after the hot section raises gas enthalpy, a **turbine** expands part of the flow to supply compressor shaft work; the pad motor disengages. **Nozzle expansion** of the core stream produces thrust.

### Cycle Configuration and the Dorsal Intake

A dorsal S-duct scoop (727-style fuselage intake) captures ambient air. With bleed open, a fraction of ingested air may be routed through a **compressor bleed path** (parasitic flow that does not pass through the fusion jacket) while the **core path** supplies the heated stream to the turbine and nozzle. Bleed establishes minimum compressor flow during ground start and reduces the effective core mass flow available for thrust.

### The Four Stages of the Cycle

In air-standard notation:

1. **Isentropic Compression ($1 \rightarrow 2$):** Air enters the S-duct and is compressed in the rotary compressor. **Before turbine takeover:** shaft work is supplied by the **pad electric starter** ($W_{\text{shaft,in}} = W_{c,\text{elec}}$). **After takeover:** shaft work is supplied by the **turbine** ($W_{\text{shaft,in}} = W_t$). Compression raises $P$ and $T$.
2. **Isobaric Heat Addition ($2 \rightarrow 3$):** Core-path air passes through the **first-wall annulus** (hot metal at ~800–1000 °C class) at nearly constant pressure. No fuel is mixed into the air stream; the HTS magnet sits **outside** a vacuum cryostat and is not the heat-exchanger surface.
3. **Split Expansion ($3 \rightarrow 4_t$, $4_t \rightarrow 4$):** Hot gas first expands through the **turbine** ($3 \rightarrow 4_t$) to deliver $w_t$ per unit mass to the shaft. The remaining enthalpy expands through the **nozzle** ($4_t \rightarrow 4$) to exhaust velocity and thrust. Before takeover, the starter still provides $w_c$ and only the nozzle branch carries net propulsive acceleration for the core stream.
4. **Isobaric Heat Rejection ($4 \rightarrow 1$):** Exhaust and bleed dump to the atmosphere; fresh air enters the scoop [1, 2].

```
       [1] Intake Scoop (S-duct) + bleed tap
               │
               ▼
       [2] Compressor  ←── shaft ──→  [3t] Turbine (post light-off)
          ↑  (starter motor)              │
          │  pad APU                      ▼
          │                         [3] Fusion jacket heating (core path)
                                          │
                                          ▼
                                   [4] Nozzle (thrust)
```

### Bleed Air and Effective Mass Flow

Let $\dot{m}_{\text{in}}$ be total corrected inlet mass flow (compressor command × spool capability), and $\beta$ the **bleed mass fraction** when the bleed valve is open ($0 \le \beta < 1$):

$$
\dot{m}_{\text{bleed}} = \beta \, \dot{m}_{\text{in}}, \qquad
\dot{m}_{\text{core}} = (1 - \beta) \, \dot{m}_{\text{in}}
$$

Only $\dot{m}_{\text{core}}$ passes through the fusion jacket, turbine, and nozzle thrust bookkeeping. Compressor shaft work is evaluated on $\dot{m}_{\text{in}}$ (the machine pumps the bleed stream as well).

Pad / surrogate effective compressor command (steps 03–07):

$$
c_{\mathrm{eff}} = c \cdot \mathbb{1}_{\mathrm{bleed}} \cdot s_{\mathrm{spool}}
$$

with $s_{\mathrm{spool}} = 0.12$ (bleed only), $0.42$ (starter engaged), or $1.0$ (fusion armed and starter off — **turbine takeover**).

### Mathematical Efficiency and Power Balance

Ideal-cycle thermal efficiency vs pressure ratio $r_p = P_2/P_1$ and $\gamma \approx 1.4$ [1]:

$$
\eta_{\text{th}} = 1 - \frac{1}{r_p^{(\gamma - 1)/\gamma}}
$$

**Compressor shaft work** per unit mass (on total inlet flow):

$$
w_c = \frac{C_p (T_2 - T_1)}{\eta_c}
$$

**Pad start (electric drive):** $W_{c,\text{elec}} = \dot{m}_{\text{in}} \, w_c / \eta_{\text{motor}}$.

**Turbine takeover:** turbine specific work $w_t$ must balance $w_c$ (mechanical efficiency $\eta_{\text{mech}}$ on the spool):

$$
w_t \approx w_c / \eta_{\text{mech}}, \qquad W_t = \dot{m}_{\text{core}} \, w_t
$$

**External heating** on the core path:

$$
q_{\text{in}} = C_p (T_3 - T_2), \qquad Q_{\text{in}} = \dot{m}_{\text{core}} \, q_{\text{in}}
$$

**Nozzle / jet power** (core stream):

$$
w_j = \eta_n \, C_p (T_{4_t} - T_4), \qquad
P_{\text{jet}} \approx \tfrac{1}{2} \dot{m}_{\text{core}} \, v_e^2
$$

**Closure check (step 07):** with thrust $F$ and $\dot{m}_{\text{core}}$ used in $F^2/(2\dot{m}) \approx P_{\text{jet}}$.

At takeover, net propulsive power must exceed pad electrical draw; in steady cruise the compressor is sustained by $W_t$ from fusion-heated gas, not ship battery.

### Engineering Notes

- **Bleed** is required for ground start and is modeled as a reduction in $\dot{m}_{\text{core}}$; closing bleed interlocks fusion ignite in the pad sequence.
- **Turbine takeover** is procedural in FlightGear (starter off after light-off); the 0D plant uses $s_{\mathrm{spool}}=1$ only when armed and starter is disengaged.
- **Externally heated** operation avoids combustion product chemistry in the core path [1, 8] while retaining a conventional shaft-coupled turbomachine [3, 9].

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
