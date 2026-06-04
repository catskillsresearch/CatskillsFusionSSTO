"""
Operator callout scripts for ChatTTS narration on exported MP4s.

Keys match :class:`~pb11_reactor_sim.engine.shot_sequence.FirePhase` ``key``
strings and high-level shot states (``quiescent``).
"""
from __future__ import annotations

# reactor display_name -> phase_key -> spoken line
PHASE_NARRATION: dict[str, dict[str, str]] = {
    "TAE FRC": {
        "gas_fill": "T minus five. Gas fill. Fuel inventory rising.",
        "field_ramp": "T minus three. Coil ramp. Magnetic field rising.",
        "formation": "T minus two. F R C formation. Plasma appearing in the chamber.",
        "nbi_heat": "T minus one. Neutral beams on. Beam heating begins.",
        "flat_top": "T zero. Flat-top discharge. Fusion and I C C collection at full power.",
        "ramp_down": "Ramp-down. Beams off. Field falling.",
        "quiescent": "Shot complete. Plasma quiescing.",
    },
    "HB11 Laser": {
        "grid_charge": "Grid at voltage. Stand by for laser chain.",
        "laser_countdown": "T minus three. Two. One. Laser chain armed.",
        "main_pulse": "Fire. Main laser pulse. Block ignition on target.",
        "afterglow": "Afterglow. Plasma cooling on the collector grid.",
        "quiescent": "Pulse complete. Chamber returning to standby.",
    },
    "LPP DPF": {
        "gas_fill": "Gas fill. Hydrogen and boron inventory in the gap.",
        "trigger": "T minus one. Switch closes. Trigger pulse.",
        "rundown": "Run-down. Plasma sheath accelerating toward the axis.",
        "pinch": "Pinch. Focus on axis. Fusion conditions.",
        "disrupt": "Disrupt. Anode hit. Energy release.",
        "recovery": "Recovery. Bank depleted. Gas cooling.",
        "quiescent": "Shot complete. Pinch chamber quiescing.",
    },
}
