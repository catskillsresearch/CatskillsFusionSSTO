#!/usr/bin/env python3
"""Copy a .gltf and its external .bin buffer(s), rewriting buffer URIs to match the destination stem.

Utility for renaming glTF sidecars so buffer filenames match the new file prefix (some
tools expect consistent stems). The main Orbitron lab build writes ``orbitron_lab.gltf`` directly.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--src", type=Path, required=True, help="Source .gltf path")
    ap.add_argument("--dst", type=Path, required=True, help="Destination .gltf path")
    args = ap.parse_args()
    src = args.src.resolve()
    dst = args.dst.resolve()
    if not src.is_file():
        print(f"error: missing source glTF: {src}", file=sys.stderr)
        return 1
    dst.parent.mkdir(parents=True, exist_ok=True)
    gltf = json.loads(src.read_text(encoding="utf-8"))
    buffers = gltf.get("buffers") or []
    ext: list[tuple[int, Path]] = []
    for bi, buf in enumerate(buffers):
        uri = buf.get("uri")
        if not uri or not isinstance(uri, str) or uri.startswith("data:"):
            continue
        bin_path = src.parent / uri
        if not bin_path.is_file():
            print(f"error: buffer file missing: {bin_path}", file=sys.stderr)
            return 1
        ext.append((bi, bin_path))

    if not ext:
        print("error: no external buffer URIs to copy", file=sys.stderr)
        return 1

    for j, (buf_index, bin_path) in enumerate(ext):
        new_uri = f"{dst.stem}.bin" if j == 0 else f"{dst.stem}_{j}.bin"
        shutil.copy2(bin_path, dst.parent / new_uri)
        buffers[buf_index]["uri"] = new_uri

    dst.write_text(json.dumps(gltf, separators=(",", ":")), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
