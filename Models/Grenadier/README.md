# Grenadier propulsion meshes

Paper-faithful 3-cycle string for CATSKILLS-SSTO-TA-GRENADIER:

`twin shoulder scoops → cross-duct plenum → σ1 EDF + σ2 MW plasma → σ3 vaporizer → shared flared nozzle`

- **Scoops** sit in the former OMS-pod bulges (both sides of the tail). Not on the belly.
- **Belly TPS** stays a solid boat — no ventral intake.
- **No bulk water tanks** on this skid (feed from CHARM plant tanks only).
- Rebuild AC: `python3 Models/Grenadier/build_grenadier_propulsion_ac.py`
- **Plan A wings:** `python3 Models/Grenadier/build_plan_a_wings.py` → `shuttle_o2_plan_a.ac` (span ≈33 m, area-class chord). See `PLAN_A_FDM.md`.
- **Wing TE:** `build_plan_a_wings.py` pulls the wing mesh TE aft to the elevon flap line (no overlay tape).
- **Bay plant:** `python3 Models/Grenadier/build_grenadier_bay_and_te.py` (water/CHARM in bay). Bay doors: `Documentation/grenadier/bay_doors.md`.
- **AC axes** match `shuttle_o2.ac`: **+X aft, +Y up, +Z right**.
- Wired from `Models/SpaceShuttle.xml` when `/sim/model/grenadier/enabled`.
- Scoop shutters close on `engine/inlet-sealed` (σ3).

Reference: `charm_p11b_ssto/research/figures/combined_cycle_engine_skid.png`.
