#!/usr/bin/env python3
"""
List FlightGear parking spots from an airport groundnet.xml.

Examples:
  python3 tools/list_fg_parking.py BIKF
  python3 tools/list_fg_parking.py BIKF --style tree
  python3 tools/list_fg_parking.py BIKF --coords
  python3 tools/list_fg_parking.py BIKF --fg-root /path/to/fgdata
"""
from __future__ import annotations

import argparse
import math
import os
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict


def airport_path_fragment(icao: str) -> str:
    up = icao.upper()
    return os.path.join("Scenery", "Airports", up[0], up[1], up[2], f"{up}.groundnet.xml")


def candidate_roots(explicit_fg_root: str | None) -> list[str]:
    roots: list[str] = []
    if explicit_fg_root:
        roots.append(explicit_fg_root)

    env_fg_root = os.environ.get("FG_ROOT")
    if env_fg_root:
        roots.append(env_fg_root)

    # Common locations for apt, manual fgdata extract, and source checkouts.
    roots.extend(
        [
            "/usr/share/games/flightgear",
            os.path.expanduser("~/flightgear/fgdata"),
            os.path.expanduser("~/fgdata"),
            os.path.expanduser("~/Downloads/fgdata"),
            os.path.expanduser("~/.fgfs"),
            os.path.expanduser("~/.fgfs/fgdata_2024_1"),
        ]
    )

    # Pick up versioned fgdata directories commonly used by AppImage setups.
    fg_home = os.path.expanduser("~/.fgfs")
    if os.path.isdir(fg_home):
        for entry in os.listdir(fg_home):
            if entry.startswith("fgdata"):
                roots.append(os.path.join(fg_home, entry))

    seen = set()
    unique_roots = []
    for r in roots:
        rr = os.path.abspath(os.path.expanduser(r))
        if rr not in seen:
            seen.add(rr)
            unique_roots.append(rr)
    return unique_roots


def find_groundnet(icao: str, explicit_fg_root: str | None) -> str | None:
    frag = airport_path_fragment(icao)
    for root in candidate_roots(explicit_fg_root):
        p = os.path.join(root, frag)
        if os.path.isfile(p):
            return p
    return None


def normalize_label(name: str, number: str, index: str) -> str:
    name = (name or "").strip()
    number = (number or "").strip()
    if name and number:
        return f"{name}{number}"
    if name:
        return name
    if number:
        return number
    return f"index-{index}"


def parse_parkings(path: str) -> list[dict[str, str]]:
    root = ET.parse(path).getroot()
    rows: list[dict[str, str]] = []
    for p in root.findall(".//parkingList/Parking"):
        row = {k: p.attrib.get(k, "") for k in p.attrib.keys()}
        row["index"] = row.get("index", "")
        row["type"] = row.get("type", "")
        row["name"] = row.get("name", "")
        row["number"] = row.get("number", "")
        row["lat"] = row.get("lat", "")
        row["lon"] = row.get("lon", "")
        row["heading"] = row.get("heading", "")
        row["radius"] = row.get("radius", "")
        row["label"] = normalize_label(row["name"], row["number"], row["index"])
        rows.append(row)
    rows.sort(key=lambda r: (r["type"], r["name"], r["number"], r["index"]))
    return rows


def parse_dms_token(token: str) -> float | None:
    """Parse FG-style DMS token: e.g. 'N63 58.846' or 'W22 34.837'."""
    parts = (token or "").strip().split()
    if len(parts) != 2:
        return None
    hemi_deg, minutes_str = parts
    if len(hemi_deg) < 2:
        return None
    hemi = hemi_deg[0].upper()
    try:
        deg = float(hemi_deg[1:])
        minutes = float(minutes_str)
    except ValueError:
        return None
    value = deg + minutes / 60.0
    if hemi in ("S", "W"):
        value *= -1.0
    return value


def distance_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine distance in nautical miles."""
    r_nm = 3440.065
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2.0) ** 2
    return 2.0 * r_nm * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))


def print_menu_style(rows: list[dict[str, str]], show_coords: bool) -> None:
    print("Parking entries (menu-like list):")
    for r in rows:
        base = f"[{r['index']:>3}] {r['label']:<24} type={r['type']:<11} heading={r['heading'] or '?':>6} radius={r['radius'] or '?'}"
        if show_coords:
            base += f"  lat={r['lat']} lon={r['lon']}"
        print(base)


def print_tree_style(rows: list[dict[str, str]], show_coords: bool) -> None:
    grouped: dict[str, dict[str, list[dict[str, str]]]] = defaultdict(lambda: defaultdict(list))
    for r in rows:
        branch = (r["name"] or "(unnamed)").strip()
        grouped[r["type"]][branch].append(r)

    print("Parking tree (type -> area/name -> spots):")
    for ptype in sorted(grouped.keys()):
        print(f"- {ptype}")
        for branch in sorted(grouped[ptype].keys()):
            items = grouped[ptype][branch]
            labels = ", ".join(i["label"] for i in items)
            print(f"  - {branch}: {labels}")
            if show_coords:
                for i in items:
                    print(f"      [{i['index']}] {i['label']}  {i['lat']}  {i['lon']}")


def cluster_rows(rows: list[dict[str, str]], threshold_nm: float) -> list[list[dict[str, str]]]:
    """Single-link clustering by great-circle distance."""
    points: list[tuple[int, float, float]] = []
    for idx, r in enumerate(rows):
        lat = parse_dms_token(r.get("lat", ""))
        lon = parse_dms_token(r.get("lon", ""))
        if lat is None or lon is None:
            continue
        points.append((idx, lat, lon))

    # Build adjacency graph.
    adj: dict[int, set[int]] = defaultdict(set)
    for i in range(len(points)):
        idx_i, lat_i, lon_i = points[i]
        for j in range(i + 1, len(points)):
            idx_j, lat_j, lon_j = points[j]
            if distance_nm(lat_i, lon_i, lat_j, lon_j) <= threshold_nm:
                adj[idx_i].add(idx_j)
                adj[idx_j].add(idx_i)

    # Connected components.
    visited: set[int] = set()
    clusters: list[list[dict[str, str]]] = []
    for idx, _, _ in points:
        if idx in visited:
            continue
        stack = [idx]
        visited.add(idx)
        comp: list[int] = []
        while stack:
            cur = stack.pop()
            comp.append(cur)
            for nxt in adj.get(cur, set()):
                if nxt not in visited:
                    visited.add(nxt)
                    stack.append(nxt)
        clusters.append([rows[k] for k in sorted(comp, key=lambda z: int(rows[z]["index"] or 0))])

    # Include rows without parseable coordinates as singletons.
    with_coords = {idx for idx, _, _ in points}
    for idx, r in enumerate(rows):
        if idx not in with_coords:
            clusters.append([r])

    # Sort by size (largest first), then by min index.
    def cluster_key(group: list[dict[str, str]]) -> tuple[int, int]:
        min_idx = min(int(x.get("index") or 999999) for x in group)
        return (-len(group), min_idx)

    return sorted(clusters, key=cluster_key)


def print_clusters_style(rows: list[dict[str, str]], show_coords: bool, threshold_nm: float) -> None:
    clusters = cluster_rows(rows, threshold_nm=threshold_nm)
    print(f"Parking clusters (<= {threshold_nm:.2f} NM single-link):")
    for i, group in enumerate(clusters, start=1):
        type_counts: dict[str, int] = defaultdict(int)
        labels = []
        for r in group:
            type_counts[r["type"]] += 1
            labels.append(r["label"])
        kinds = ", ".join(f"{k}:{v}" for k, v in sorted(type_counts.items()))
        preview = ", ".join(labels[:6]) + (" ..." if len(labels) > 6 else "")
        print(f"- Cluster {i:02d} ({len(group)} spots; {kinds})")
        print(f"  {preview}")
        if show_coords:
            for r in group:
                print(f"    [{r['index']}] {r['label']:<24} {r['lat']:<14} {r['lon']}")


def main() -> int:
    ap = argparse.ArgumentParser(description="List FlightGear airport parking stands from groundnet.xml")
    ap.add_argument("icao", help="Airport ICAO code, e.g. BIKF")
    ap.add_argument("--fg-root", help="FGData root path if auto-discovery fails")
    ap.add_argument("--style", choices=["menu", "tree", "clusters"], default="menu", help="Output style")
    ap.add_argument("--coords", action="store_true", help="Include lat/lon coordinates")
    ap.add_argument(
        "--cluster-nm",
        type=float,
        default=0.25,
        help="Cluster link distance in NM when --style=clusters",
    )
    args = ap.parse_args()

    icao = args.icao.upper()
    groundnet = find_groundnet(icao, args.fg_root)
    if not groundnet:
        print(
            f"Could not find {icao}.groundnet.xml.\n"
            "Try passing --fg-root to your 2024 fgdata folder.",
            file=sys.stderr,
        )
        return 1

    rows = parse_parkings(groundnet)
    print(f"Airport: {icao}")
    print(f"Source:  {groundnet}")
    print(f"Total parking entries: {len(rows)}\n")
    if args.style == "tree":
        print_tree_style(rows, args.coords)
    elif args.style == "clusters":
        print_clusters_style(rows, args.coords, threshold_nm=args.cluster_nm)
    else:
        print_menu_style(rows, args.coords)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
