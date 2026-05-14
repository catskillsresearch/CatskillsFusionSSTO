"""Build CadQuery solids from YAML ``connector_ports`` + ``connector_links`` specs.

Optional ``connectivity_spec`` (inside the same ``params`` mapping passed here) ties
human narratives to link ids so the compiler can cross-check intent vs geometry::

  connectivity_spec:
    physical_story: |
      Free-text design intent (operators, commissioning).
    links:
      - link_id: h2_service          # must match a connector_links[].id
        service: process_h2
        from_region: fuel_farm
        to_region: reactor_magnet_shell
        routing_intent: arc_over_deck_then_farm_side
"""

from __future__ import annotations

from typing import Any

import cadquery as cq


def _validate_connectivity_spec(params: dict[str, Any], raw_links: list[Any]) -> None:
    spec = params.get("connectivity_spec")
    if spec is None:
        return
    if not isinstance(spec, dict):
        raise TypeError("connectivity_spec must be a mapping")
    rows = spec.get("links")
    if rows is None:
        return
    if not isinstance(rows, list):
        raise TypeError("connectivity_spec.links must be a list")
    link_ids: set[str] = set()
    for i, L in enumerate(raw_links):
        if not isinstance(L, dict):
            continue
        lid = L.get("id")
        if isinstance(lid, str) and lid.strip():
            link_ids.add(lid)
    for j, row in enumerate(rows):
        if not isinstance(row, dict):
            raise TypeError(f"connectivity_spec.links[{j}] must be a mapping")
        lid = row.get("link_id")
        if lid is None:
            continue
        if not isinstance(lid, str) or not lid.strip():
            raise ValueError(f"connectivity_spec.links[{j}].link_id must be a non-empty string")
        if link_ids and lid not in link_ids:
            raise ValueError(
                f"connectivity_spec.links[{j}].link_id {lid!r} not found in connector_links "
                f"(have {sorted(link_ids)})"
            )


def _as_vec3(v: Any, *, ctx: str) -> tuple[float, float, float]:
    if not isinstance(v, (list, tuple)) or len(v) != 3:
        raise ValueError(f"{ctx}: expected [x, y, z], got {v!r}")
    return (float(v[0]), float(v[1]), float(v[2]))


def _add_vec3(
    a: tuple[float, float, float], b: tuple[float, float, float]
) -> tuple[float, float, float]:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _resolve_ports(
    raw: list[dict[str, Any]],
    anchors: dict[str, tuple[float, float, float]],
) -> dict[str, tuple[float, float, float]]:
    out: dict[str, tuple[float, float, float]] = {}
    for i, p in enumerate(raw):
        if not isinstance(p, dict):
            raise TypeError(f"connector_ports[{i}] must be a mapping")
        pid = p.get("id")
        if not isinstance(pid, str) or not pid.strip():
            raise ValueError(f"connector_ports[{i}] needs non-empty string id")
        if pid in out:
            raise ValueError(f"duplicate connector port id: {pid!r}")
        off_raw = p.get("offset", [0.0, 0.0, 0.0])
        off = _as_vec3(off_raw, ctx=f"connector_ports[{i}].{pid!r}.offset")
        if "position" in p:
            base = _as_vec3(p.get("position"), ctx=f"connector_ports[{i}].{pid!r}.position")
        elif "anchor" in p:
            key = p.get("anchor")
            if not isinstance(key, str) or not key.strip():
                raise ValueError(f"connector_ports[{i}] needs non-empty anchor string")
            if key not in anchors:
                raise ValueError(
                    f"connector_ports[{i}] unknown anchor {key!r}; known: {sorted(anchors)}"
                )
            base = anchors[key]
        else:
            raise ValueError(
                f"connector_ports[{i}] ({pid!r}) needs either position: [x,y,z] or anchor: <key>"
            )
        out[pid] = _add_vec3(base, off)
    return out


def _tube_segment(p0: tuple[float, float, float], p1: tuple[float, float, float], radius: float) -> cq.Workplane:
    p0v = cq.Vector(p0)
    p1v = cq.Vector(p1)
    v = p1v - p0v
    length = v.Length
    if length < 1e-6:
        r = max(radius, 0.002)
        return cq.Workplane("XY").sphere(r).translate(p0v.toTuple())
    z = v.normalized()
    x = z.cross(cq.Vector(0.0, 1.0, 0.0))
    if x.Length < 1e-4:
        x = z.cross(cq.Vector(1.0, 0.0, 0.0))
    x = x.normalized()
    pl = cq.Plane(origin=p0v, xDir=x, normal=z)
    wp = cq.Workplane(inPlane=pl)
    return wp.circle(radius).extrude(length)


def _port_marker(center: tuple[float, float, float], radius: float) -> cq.Workplane:
    r = max(radius * 1.6, 0.004)
    return cq.Workplane("XY").sphere(r).translate(center)


def build_connector_routing(
    params: dict[str, Any],
    anchors: dict[str, tuple[float, float, float]] | None = None,
) -> cq.Workplane:
    """
    Union tube segments along polylines defined by ``connector_links``.

    Port locations may be given as ``position: [x,y,z]`` **or** ``anchor: <key>`` plus
    optional ``offset: [dx,dy,dz]``. Anchors are resolved in Python (same source as
    ``LabInfrastructure.build_fuel_farm()``) so tubes meet the tank meshes.

    Optional ``include_port_markers: true`` adds small spheres at port positions
    (default **false**).
    """
    raw_ports = params.get("connector_ports")
    raw_links = params.get("connector_links")
    if raw_ports is None or raw_links is None:
        raise ValueError("build_connector_routing requires connector_ports and connector_links in params")
    if not isinstance(raw_ports, list) or not raw_ports:
        raise ValueError("connector_ports must be a non-empty list")
    if not isinstance(raw_links, list) or not raw_links:
        raise ValueError("connector_links must be a non-empty list")

    _validate_connectivity_spec(params, raw_links)

    ports = _resolve_ports(raw_ports, anchors or {})
    show_markers = bool(params.get("include_port_markers"))

    solids: list[cq.Workplane] = []
    if show_markers:
        port_rmax: dict[str, float] = {pid: 0.01 for pid in ports}
        for i, link in enumerate(raw_links):
            if not isinstance(link, dict):
                raise TypeError(f"connector_links[{i}] must be a mapping")
            r0 = link.get("radius", 0.015)
            if not isinstance(r0, (int, float)) or float(r0) <= 0:
                raise ValueError(f"connector_links[{i}] needs positive numeric radius")
            r0 = float(r0)
            for end in (link.get("from_port"), link.get("to_port")):
                if isinstance(end, str) and end in port_rmax:
                    port_rmax[end] = max(port_rmax[end], r0)
        for pid, pos in ports.items():
            solids.append(_port_marker(pos, port_rmax.get(pid, 0.01)))

    for i, link in enumerate(raw_links):
        if not isinstance(link, dict):
            raise TypeError(f"connector_links[{i}] must be a mapping")
        a = link.get("from_port")
        b = link.get("to_port")
        if not isinstance(a, str) or not isinstance(b, str):
            raise ValueError(f"connector_links[{i}] needs string from_port and to_port")
        if a not in ports:
            raise ValueError(f"connector_links[{i}] unknown from_port {a!r}")
        if b not in ports:
            raise ValueError(f"connector_links[{i}] unknown to_port {b!r}")
        rad = link.get("radius", 0.015)
        if not isinstance(rad, (int, float)) or float(rad) <= 0:
            raise ValueError(f"connector_links[{i}] needs positive numeric radius")
        r = float(rad)
        wps = link.get("waypoints") or []
        if not isinstance(wps, list):
            raise TypeError(f"connector_links[{i}].waypoints must be a list")
        chain: list[tuple[float, float, float]] = [ports[a]]
        for j, wp in enumerate(wps):
            chain.append(_as_vec3(wp, ctx=f"connector_links[{i}].waypoints[{j}]"))
        chain.append(ports[b])
        for k in range(len(chain) - 1):
            solids.append(_tube_segment(chain[k], chain[k + 1], r))

    if not solids:
        raise ValueError("no connector geometry produced (empty links?)")

    out = solids[0]
    for s in solids[1:]:
        out = out.union(s)
    return out
