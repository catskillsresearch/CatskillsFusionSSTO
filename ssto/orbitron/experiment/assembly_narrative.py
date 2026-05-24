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
            "Complete **test_stand** logical root from `orbitron_lab.yaml`: Phase 1 benchtop, Phase 2 "
            "wind-tunnel engine, **CTRL-01** operator console, **TS-01** thrust sled, and **INJ-H2-01** / "
            "**U2-CH4-01** tank farm. Propulsion axis **−X → +X** (bellmouth to nozzle); tank farm on **+Y**. "
            "FlightGear scene root: `fusion_arcjet_engine`. Subsections below zoom individual assemblies."
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
            "Four corner **LoadCell_0…3** pucks on the deck feed pad thrust bookkeeping "
            "(step 07 jet closure, operator Screen). **Engine_Mount_Frame** posts carry the "
            "engine pivot at `ENGINE_MOUNT_TOP_Z`. Compressor/throttle moments split corner loads."
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
            "Operator **Screen**, APU/starter/bleed switches, and **Big_Red_Button** map to "
            "`pad.*` interlocks in the experiment YAML (APU → starter → bleed → vacuum → laser → HV → ignite). "
            "Until **CTRL-01** sequence completes, step 03 fuel injection and reaction rate stay gated."
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
            "**Central_Cathode_Wire (K1)** and **Outer_Anode_Grid (A1)** define the electrostatic bore "
            "used in chain geometry (`r_cathode_m`, `r_anode_m`, `length_m`). **Magnet (M1)** provides "
            "axial **B** (`B_axial_tesla`). WarpX step 01 models the electron ring in this annulus only "
            "(τ = `pad.throttle`, p = `pad.cathode_pulse`). **NBI_Injector** is tangential keV fuel entry."
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
        ),
    ),
    AssemblyWalkthrough(
        designator="INJ-H2-01",
        title="Hydrogen proton feed",
        png_basenames=("hydrogen_tank_assy",),
        yaml_group="proton_and_thermal_farm",
        narrative=(
            "**Tank_Hydrogen** and **Hydrogen_Trunk_Line** route **H₂** to **NBI_Injector** for proton "
            "inventory (`injectants.h2_sccm`). Optimal mixing with boron delivery peaks near "
            "H₂:laser ≈ 8:1 in the 0D fuel model."
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
            "**Q_Switched_NdYAG_Laser** (355 nm) ablates **Solid_Boron_11_Target** disks in "
            "**Solid_B11_Target_Holder** (`injectants.laser_ablation_hz`, `b11_target_index`). "
            "Requires **CTRL-01** vacuum + laser arm interlocks."
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
        png_basenames=("methane_tank_assy", "integrated_pad_services"),
        yaml_group="proton_and_thermal_farm",
        narrative=(
            "**Tank_Cryo_Methane** and **Cryo_Methane_Piping** size the first-wall / anode jacket loop "
            "checked in step 06 (**U2a** heat flux, **U2c** mdot). Knobs: `max_wall_heat_flux_W_m2`, "
            "`ch4_cooling_effectiveness`."
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
            "**Bellmouth** and **Compressor_Housing** on **−X** set Brayton **`pad.compressor`** "
            "effective mdot (step 06 **PLANT**, step 07 closure). **Nozzle_CD_Contour** and exit hardware "
            "on **+X** convert **P_gross** to measurable thrust on **TS-01**."
        ),
        physics_refs=("pad.compressor", "plant_scales.jet_propulsive_efficiency"),
        mesh_anchors=(
            "Bellmouth_Flare",
            "Compressor_Housing",
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
        "(`make orbitron-lab-pngs` or `./stand.sh`). "
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
