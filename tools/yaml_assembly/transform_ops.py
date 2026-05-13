"""Apply declarative transform chains from assembly YAML to CadQuery solids."""

from __future__ import annotations

from typing import Any

import cadquery as cq


def apply_transform_chain(obj: cq.Workplane, chain: list[dict[str, Any]] | None) -> cq.Workplane:
    """Apply ordered ops: translate, rotate_y_about_point (degrees, RH rule per assembly YAML)."""
    if not chain:
        return obj
    out = obj
    for step in chain:
        op = step.get("op")
        if op == "translate":
            out = out.translate(tuple(float(x) for x in step["xyz"]))
        elif op == "rotate_y_about_point":
            p = tuple(float(x) for x in step["pivot"])
            p1 = (p[0], p[1] + 1.0, p[2])
            out = out.rotate(p, p1, float(step["angle_deg"]))
        else:
            raise ValueError(f"Unknown transform op: {op!r} in {step!r}")
    return out
