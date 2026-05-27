"""Physical assembly walkthrough for experiment reports (CadQuery / Blender SSOT)."""
from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class AssemblyWalkthrough:
    """One logical assembly in report order."""

    designator: str
    title: str
    png_basenames: tuple[str, ...]
    yaml_group: str
    narrative: str
    physics_refs: tuple[str, ...]
    mesh_anchors: tuple[str, ...]


# Proof-chain analysis walkthrough (CadQuery → glTF → Blender hero PNG).
# ``png_basenames``: tried in order under ``Aircraft/<pkg>/build/``.
ASSEMBLY_WALKTHROUGH: tuple[AssemblyWalkthrough, ...] = (
    AssemblyWalkthrough(
        designator="LAB-01",
        title="Orbitron laboratory (full test stand)",
        png_basenames=("orbitron_lab",),
        yaml_group="test_stand",
        narrative=(
            "Full laboratory layout: Phase-1 benchtop fusion core, Phase-2 air-breathing engine train, "
            "operator station (**CTRL-01**), thrust measurement sled (**TS-01**), and cryogenic **H₂** / **CH₄** "
            "services. Propulsion axis **−X → +X**; tank farm on **+Y**."
        ),
        physics_refs=(),
        mesh_anchors=("fusion_arcjet_engine",),
    ),
    AssemblyWalkthrough(
        designator="TS-01",
        title="Thrust sled & load cells",
        png_basenames=("thrust_sled",),
        yaml_group="thrust_sled",
        narrative=(
            "Four corner load cells integrate thrust and moment for jet–shaft power bookkeeping. "
            "The engine mount frame sets the pivot height for the Brayton train relative to the pad deck."
        ),
        physics_refs=("plant_scales.thrust_lbf_at_full", "plant_scales.mass_flow_kgps_at_full"),
        mesh_anchors=("LoadCell_0", "LoadCell_1", "LoadCell_2", "LoadCell_3", "Engine_Mount_Frame"),
    ),
    AssemblyWalkthrough(
        designator="CTRL-01",
        title="Control panel & pad interlocks",
        png_basenames=("control_panel_stand",),
        yaml_group="control_panel_stand",
        narrative=(
            "Operator console for pad power, compressor bleed, vacuum interlock, laser arm, and high-voltage "
            "enable before ignition. The interlock chain mirrors a real hot-fire sequence; fueling and reaction "
            "physics stay off until the pad is in a safe steady-ready state."
        ),
        physics_refs=(
            "pad.pad_apu_online",
            "pad.starter_engage",
            "pad.bleed_air_open",
            "pad.vacuum_interlock_ok",
            "pad.laser_armed",
            "pad.hv_enabled",
            "pad.startup_trigger",
        ),
        mesh_anchors=("Operator_Panel", "Screen", "Big_Red_Button", "High_Voltage_Umbilical"),
    ),
    AssemblyWalkthrough(
        designator="CORE-01",
        title="Electrostatic Orbitron core (Phase 1)",
        png_basenames=(
            "subassembly_1_2_electrostatic_orbitron_core",
            "reactor_bay",
            "phase_1_benchtop",
        ),
        yaml_group="subassembly_1_2_electrostatic_orbitron_core",
        narrative=(
            "**Radial stack (inside → outside)** — normative layout for p-¹¹B; see **Benchmark "
            "Methodology — Radial thermal zoning** and level-1 thermal split in this report.\n\n"
            "1. **Cathode wire** (on-axis, **~−600 kV**) and **plasma vacuum bore** — keV **H⁺** / **B⁺** "
            "from tangential **NBI** and solid **¹¹B** laser ablation; **no** Brayton air in the bore. "
            "Energy leaves as **⁴He alphas**, **bremsstrahlung X-rays**, and **charge-exchange** — "
            "**not** a significant neutron flux.\n\n"
            "2. **First wall / anode sheath** (`Outer_Anode_Grid`) at **r ≈ 4 cm** — the **heat catcher**: "
            "absorbs α and X-ray / CX load (**~400 kW** class in the 0D model). Runs **hot** "
            "(~800–1000 °C class) on the plasma side.\n\n"
            "3. **Air annulus** — compressed **air** flows **between the hot first wall and the cryostat**, "
            "**inside** the magnet bore radius. It **heats** the air for the Brayton train; it does **not** "
            "wash or cool the HTS winding.\n\n"
            "4. **Cryostat** — vacuum gap + **MLI** (target ~1.5 cm radial in the zoning budget). "
            "Blocks conduction and convection from the hot air channel to the coil.\n\n"
            "5. **HTS solenoid** (`Magnet`, **~7.5–10 cm** outer radius) — **outside** the cryostat; "
            "**B ≈ 2 T** penetrates the bore through vacuum. **Liquid CH₄** (~113 K) removes **parasitic "
            "cryo leak only** — not the megawatt first-wall stream.\n\n"
            "**CAD honesty:** Phase-1 meshes export cathode, anode, magnet, injectors, and (in the "
            "full engine) `Reactor_Bay_Inlet_Shroud` as **separate coarse parts**. They do **not** yet "
            "model distinct solids for the **air-channel liner**, **cryostat shell**, and **MLI** — "
            "the stack above is the **design target**, not fully resolved in CadQuery/Blender yet."
        ),
        physics_refs=(
            "geometry.r_anode_m",
            "geometry.r_cathode_m",
            "geometry.length_m",
            "geometry.V_cathode_v",
            "geometry.B_axial_tesla",
            "pad.throttle",
            "pad.cathode_pulse",
        ),
        mesh_anchors=(
            "Central_Cathode_Wire",
            "Outer_Anode_Grid",
            "Magnet",
            "NBI_Injector",
            "Insulators",
            "Reactor_Bay_Inlet_Shroud",
            "Fusion_Hot_Gas_Outlet",
            "Magnet_Service_Bosses",
        ),
    ),
    AssemblyWalkthrough(
        designator="INJ-H2-01",
        title="Hydrogen proton feed",
        png_basenames=("proton_h2_feed", "proton_and_thermal_farm"),
        yaml_group="proton_h2_feed",
        narrative=(
            "Cryogenic **H₂** tank and trunk line feed the neutral-beam path for proton inventory. "
            "The benchmark fueling point targets strong mixing with the **¹¹B** ablation line near "
            "an **8:1 H₂:laser** duty ratio."
        ),
        physics_refs=("injectants.h2_sccm", "fusion_channel.h2_ref_sccm"),
        mesh_anchors=("Tank_Hydrogen", "Hydrogen_Trunk_Line", "Decal_H2"),
    ),
    AssemblyWalkthrough(
        designator="INJ-B11-01",
        title="Solid ¹¹B laser ablation",
        png_basenames=(
            "subassembly_1_3_laser_ablation_system",
            "boron_tank_assy",
        ),
        yaml_group="subassembly_1_3_laser_ablation_system",
        narrative=(
            "Q-switched **Nd:YAG** at **355 nm** cold-ablates solid **¹¹B** disks in the vacuum chamber "
            "viewport line. Repetition rate sets boron delivery into the electrostatic well alongside "
            "the hydrogen feed."
        ),
        physics_refs=("injectants.laser_ablation_hz", "injectants.b11_target_index", "fusion_channel.laser_ref_hz"),
        mesh_anchors=(
            "Q_Switched_NdYAG_Laser",
            "Solid_Boron_11_Target",
            "Solid_B11_Target_Holder",
            "UV_Fused_Silica_Viewport",
        ),
    ),
    AssemblyWalkthrough(
        designator="U2-CH4-01",
        title="CH₄ wall-thermal loop (Unobtanium U2)",
        png_basenames=("thermal_ch4_feed", "proton_and_thermal_farm"),
        yaml_group="thermal_ch4_feed",
        narrative=(
            "Two **CH₄** duties, not one: **(U2)** internal channels on the **first wall** remove the "
            "high-grade α / X-ray / CX load (~55% of `first_wall_kw` in the 0D split); **(U3)** a "
            "closed cryostat loop on the **HTS solenoid** removes **parasitic leak** through the vacuum "
            "gap. **CH₄ does not cool the Brayton air stream.**"
        ),
        physics_refs=(
            "unobtanium.max_wall_heat_flux_W_m2",
            "unobtanium.ch4_cooling_effectiveness",
            "plant_scales.heat_kw_at_full",
        ),
        mesh_anchors=("Tank_Cryo_Methane", "Cryo_Methane_Piping", "Magnet_Service_Bosses"),
    ),
    AssemblyWalkthrough(
        designator="AIR-01",
        title="Air-breathing Brayton train (−X intake → +X nozzle)",
        png_basenames=(
            "air_breathing_nozzle_train",
            "air_breathing_engine",
            "turbofan_intake",
            "propulsive_nozzle",
            "phase_2_wind_tunnel",
        ),
        yaml_group="air_breathing_nozzle_train",
        narrative=(
            "Bellmouth and S-duct intake on **−X** feed a co-axial **compressor–turbine** spool: pad "
            "**bleed** opens the path, an **electric starter** cranks the shaft, then after fusion "
            "light-off the **turbine** drives the compressor. Core-path air is heated in the **annulus "
            "around the hot first wall** (`Reactor_Bay_Inlet_Shroud` region) — **not** by flowing over "
            "the cryogenic **HTS** pack — then expands through the **+X** nozzle for thrust on the sled."
        ),
        physics_refs=(
            "pad.compressor",
            "pad.bleed_air_open",
            "plant_scales.jet_propulsive_efficiency",
        ),
        mesh_anchors=(
            "Bellmouth_Flare",
            "Compressor_Housing",
            "Compressor_Bleed_Port",
            "Turbine_Can",
            "Nozzle_CD_Contour",
            "Nozzle_Exit_Hardware",
            "Pad_Startup_Motor",
        ),
    ),
)

# Flat lookup: chain_config dotted path → (designator, short label)
PHYSICS_DESIGNATORS: dict[str, tuple[str, str]] = {}
for _asm in ASSEMBLY_WALKTHROUGH:
    for _ref in _asm.physics_refs:
        PHYSICS_DESIGNATORS[_ref] = (_asm.designator, _asm.title)


def repo_root() -> Path:
    return _REPO


def aircraft_package_dir(repo: Path | None = None) -> str:
    repo = repo or repo_root()
    script = repo / "tools" / "orbitron_aircraft_paths.py"
    if script.is_file():
        try:
            out = subprocess.run(
                ["python3", str(script), "package_dir", "--repo-root", str(repo)],
                check=True,
                capture_output=True,
                text=True,
            )
            return out.stdout.strip() or "Orbitron-TestStand"
        except subprocess.CalledProcessError:
            pass
    return "Orbitron-TestStand"


def stand_build_dir(repo: Path | None = None) -> Path:
    repo = repo or repo_root()
    return repo / "Aircraft" / aircraft_package_dir(repo) / "build"


def compose_lab01_hero(source_build: Path) -> Path | None:
    """
    Report overview: engine train + thrust sled side-by-side (readable, not scattered Phase 2 parts).
    """
    engine_p = source_build / "air_breathing_nozzle_train.png"
    sled_p = source_build / "thrust_sled.png"
    if not engine_p.is_file() or not sled_p.is_file():
        return None
    try:
        from PIL import Image
    except ImportError:
        return None
    out = source_build / "lab01_hero.png"
    target_h = 720
    gap = 16
    bg = (236, 236, 236)
    panels: list[Image.Image] = []
    for path in (engine_p, sled_p):
        im = Image.open(path).convert("RGB")
        scale = target_h / im.height
        panels.append(
            im.resize((max(1, int(im.width * scale)), target_h), Image.Resampling.LANCZOS)
        )
    w = sum(p.width for p in panels) + gap * (len(panels) - 1)
    canvas = Image.new("RGB", (w, target_h), bg)
    x = 0
    for p in panels:
        canvas.paste(p, (x, 0))
        x += p.width + gap
    canvas.save(out)
    _trim_assembly_png(out)
    return out


def _trim_assembly_png(path: Path) -> None:
    """Best-effort crop of factory-gray margins after copy."""
    try:
        import sys

        if str(_REPO) not in sys.path:
            sys.path.insert(0, str(_REPO))
        from tools.trim_assembly_png import trim_png

        trim_png(path, tolerance=20, padding_px=12, lum_delta=40)
    except Exception:
        pass


def _resolve_png(source_build: Path, basenames: tuple[str, ...]) -> Path | None:
    for name in basenames:
        p = source_build / f"{name}.png"
        if p.is_file():
            return p
    return None


def stage_assembly_figures(
    report_dir: Path,
    *,
    repo: Path | None = None,
) -> dict[str, str | None]:
    """
    Copy hero PNGs into ``report_dir/figures/assemblies/``.

    Returns map designator → relative path under report (or None if PNG missing).
    """
    source = stand_build_dir(repo)
    dest_dir = report_dir / "figures" / "assemblies"
    dest_dir.mkdir(parents=True, exist_ok=True)
    staged: dict[str, str | None] = {}
    for asm in ASSEMBLY_WALKTHROUGH:
        src = _resolve_png(source, asm.png_basenames)
        if src is None:
            staged[asm.designator] = None
            continue
        dest = dest_dir / f"{asm.designator}_{src.name}"
        shutil.copy2(src, dest)
        _trim_assembly_png(dest)
        staged[asm.designator] = f"figures/assemblies/{dest.name}"
    return staged


def designator_table_md() -> str:
    lines = [
        "| Config path | Designator | Assembly | Mesh anchors |",
        "|-------------|------------|----------|--------------|",
    ]
    for asm in ASSEMBLY_WALKTHROUGH:
        if not asm.physics_refs:
            continue
        anchors = ", ".join(f"`{m}`" for m in asm.mesh_anchors[:3])
        if len(asm.mesh_anchors) > 3:
            anchors += ", …"
        for ref in asm.physics_refs:
            lines.append(f"| `{ref}` | **{asm.designator}** | {asm.title} | {anchors} |")
    return "\n".join(lines) + "\n"


def render_assembly_section_md(
    *,
    staged: dict[str, str | None],
    stand_build: Path,
    parameters: dict[str, Any],
) -> str:
    """Initial report section: assemblies, images, designator glossary."""
    lines: list[str] = []
    lines.append("## Physical assemblies (CadQuery → Blender)\n\n")
    lines.append(
        "Meshes and hierarchy are authored in "
        "`ssto/orbitron/assembly_specs/orbitron_lab.yaml` "
        "(schema v2 `logical.groups` + `instances`). "
        "CadQuery builds solids via `tools/yaml_assembly/`; Blender renders hero PNGs from glTF "
        "(`make orbitron-lab-pngs` or the experiment runner). "
        "**INJ-H2-01** and **U2-CH4-01** use tank-farm slices only (not `integrated_pad_services`, "
        "which includes **CTRL-01**). "
        "Throughout this report, **designators** (e.g. **CORE-01**, **K1**) tie analysis parameters "
        "to these assemblies.\n\n"
    )

    any_missing = any(v is None for v in staged.values())
    if any_missing:
        lines.append(
            f"> Some hero PNGs were not found under `{stand_build}/`. "
            "Regenerate with `./stand.sh` or `make orbitron-lab-pngs`, then re-run the experiment.\n\n"
        )

    for asm in ASSEMBLY_WALKTHROUGH:
        lines.append(f"### {asm.designator} — {asm.title}\n\n")
        rel = staged.get(asm.designator)
        if rel:
            lines.append(f"![{asm.designator} — {asm.title}]({rel})\n\n")
        else:
            tried = ", ".join(f"`{n}.png`" for n in asm.png_basenames)
            lines.append(f"*(Hero render not staged — expected one of {tried} in `{stand_build}`.)*\n\n")
        lines.append(f"{asm.narrative}\n\n")
        if asm.physics_refs:
            refs = ", ".join(f"`{r}`" for r in asm.physics_refs)
            lines.append(f"**Analysis parameters:** {refs}  \n")
        if asm.mesh_anchors:
            meshes = ", ".join(f"`{m}`" for m in asm.mesh_anchors)
            lines.append(f"**Key meshes:** {meshes}  \n")
        lines.append(f"**YAML group:** `{asm.yaml_group}`\n\n")

    lines.append("### Designator reference (used in later sections)\n\n")
    lines.append(
        "When this report cites geometry, fueling, pad, or unobtanium values, use these designators "
        "to locate the physical component in CAD. Numeric values are in **Parameter settings**.\n\n"
    )
    lines.append(designator_table_md())
    lines.append("\n")
    return "".join(lines)


def designator_for(config_path: str) -> str | None:
    """Return designator string for a dotted config path, e.g. ``geometry.r_anode_m`` → ``CORE-01``."""
    hit = PHYSICS_DESIGNATORS.get(config_path)
    return hit[0] if hit else None
