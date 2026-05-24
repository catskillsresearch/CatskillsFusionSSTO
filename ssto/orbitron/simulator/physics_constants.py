"""Shared physical limits for Tier-1 gates (not placeholder values)."""
from __future__ import annotations

# Cathode surface field limit at margin=1.0 [V/m].
# 600 kV / 30 mm gap ≈ 2×10⁷ V/m — margin ~1 means “at program gradient”.
# (Legacy gate used 3×10⁹ V/m and never failed.)
EMISSION_FIELD_LIMIT_V_M: float = 2.0e7

# Minimum ion beam current for meaningful burn [mA].
BEAM_CURRENT_MIN_MA: float = 1.0

# Minimum log10 density proxy @ meaningful power.
LOG10_DENSITY_MIN: float = 11.0

# Hold-out: design ⟨σv⟩ must track literature within this factor at audit T points.
REACTIVITY_HOLDOUT_MAX_RATIO: float = 25.0
