"""Ensure CadQuery/Blender hero PNGs exist before report assembly staging."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Callable, TextIO

from ssto.orbitron.experiment.assembly_narrative import (
    ASSEMBLY_WALKTHROUGH,
    repo_root,
    stand_build_dir,
)


def _log_fn(log: TextIO | Callable[[str], None] | Path | None) -> Callable[[str], None]:
    if log is None:
        return lambda _msg: None
    if isinstance(log, Path):
        path = log

        def _append(msg: str) -> None:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as f:
                f.write(msg)

        return _append
    if hasattr(log, "write"):
        return lambda msg: log.write(msg)  # type: ignore[union-attr]
    return log  # type: ignore[return-value]


def required_assembly_basenames() -> tuple[str, ...]:
    names: list[str] = []
    seen: set[str] = set()
    for asm in ASSEMBLY_WALKTHROUGH:
        for name in asm.png_basenames:
            if name not in seen:
                seen.add(name)
                names.append(name)
    return tuple(names)


def missing_assembly_pngs(*, repo: Path | None = None) -> list[str]:
    source = stand_build_dir(repo)
    return [n for n in required_assembly_basenames() if not (source / f"{n}.png").is_file()]


def ensure_assembly_heroes(
    *,
    repo: Path | None = None,
    log: TextIO | Callable[[str], None] | Path | None = None,
    force: bool = False,
) -> bool:
    """
    Build report hero PNGs via ``make orbitron-lab-gltf orbitron-lab-pngs`` when missing.

    Config-independent lab CAD (``orbitron_lab.yaml``) — not tied to experiment YAML geometry.
    Does **not** run full ``./stand.sh`` / FlightGear surrogate closure.
    """
    repo = repo or repo_root()
    emit = _log_fn(log)
    missing = missing_assembly_pngs(repo=repo)
    if not missing and not force:
        return True

    emit("\n--- Assembly hero renders (make orbitron-lab-gltf orbitron-lab-pngs) ---\n")
    if missing:
        emit(f"  Missing PNGs: {', '.join(missing)}\n")

    try:
        subprocess.run(
            ["make", "orbitron-lab-gltf", "orbitron-lab-pngs"],
            cwd=repo,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        emit(f"  make failed (exit {exc.returncode}) — assembly figures may be incomplete\n")
        return False
    except FileNotFoundError:
        emit("  make not found — run from repo with GNU make installed\n")
        return False

    still = missing_assembly_pngs(repo=repo)
    if still:
        emit(f"  Still missing after make: {', '.join(still)}\n")
        return False
    emit("  Assembly hero PNGs ready\n")
    return True
