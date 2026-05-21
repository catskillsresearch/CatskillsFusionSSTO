"""
WarpX / pywarpx environment for subprocess PIC runs.

Canonical shell setup: ``./stand.sh`` → ``tools/warpx_paths.sh`` (Poetry activate +
``PYTHONPATH`` / ``LD_LIBRARY_PATH`` under ``WarpX/build/lib``).

Launch Proof Suite the same way::

    ./scripts/run_orbitron_proof_suite.sh

This module mirrors ``tools/warpx_paths.sh`` for in-process and subprocess PIC runs.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _prepend(env: dict[str, str], key: str, path: str) -> None:
    if not path:
        return
    old = env.get(key, "")
    parts = [p for p in old.split(":") if p]
    if path in parts:
        return
    env[key] = f"{path}:{old}" if old else path


def discover_warpx_paths(root: Path | None = None) -> tuple[Path | None, Path | None]:
    """Return (site-packages dir, lib dir) for a repo-local WarpX build."""
    root = root or repo_root()
    pyver = f"{sys.version_info.major}.{sys.version_info.minor}"
    site_flat = root / "WarpX" / "build" / "lib" / "site-packages"
    site_ver = root / "WarpX" / "build" / "lib" / f"python{pyver}" / "site-packages"
    lib = root / "WarpX" / "build" / "lib"

    if os.environ.get("WARPX_PYTHONPATH"):
        custom = Path(os.environ["WARPX_PYTHONPATH"])
        return (custom if custom.is_dir() else None, lib if lib.is_dir() else None)
    if site_flat.is_dir():
        return site_flat, lib if lib.is_dir() else None
    if site_ver.is_dir():
        return site_ver, lib if lib.is_dir() else None
    if lib.is_dir():
        return None, lib
    return None, None


def warpx_python_executable() -> str:
    return os.environ.get("WARPX_PYTHON", sys.executable)


def apply_warpx_env(env: dict[str, str] | None = None) -> dict[str, str]:
    """Merge PYTHONPATH and LD_LIBRARY_PATH for pywarpx (does not mutate os.environ)."""
    out = dict(env if env is not None else os.environ)
    site, lib = discover_warpx_paths()
    if os.environ.get("WARPX_PYTHONPATH"):
        _prepend(out, "PYTHONPATH", os.environ["WARPX_PYTHONPATH"])
    elif site is not None:
        _prepend(out, "PYTHONPATH", str(site))
    if lib is not None:
        _prepend(out, "LD_LIBRARY_PATH", str(lib))
    return out


def ensure_warpx_env() -> dict[str, str | None]:
    """
    Configure the current process for WarpX child runs.

    Returns a short summary dict for logging (site_packages, lib, python).
    """
    site, lib = discover_warpx_paths()
    if os.environ.get("WARPX_PYTHONPATH"):
        _prepend(os.environ, "PYTHONPATH", os.environ["WARPX_PYTHONPATH"])
    elif site is not None:
        _prepend(os.environ, "PYTHONPATH", str(site))
    if lib is not None:
        _prepend(os.environ, "LD_LIBRARY_PATH", str(lib))
    return {
        "site_packages": str(site) if site else None,
        "lib": str(lib) if lib else None,
        "python": warpx_python_executable(),
    }


def warpx_env_summary() -> str:
    """One-line status for GUI logs."""
    info = ensure_warpx_env()
    lines = [f"WARPX_PYTHON={info['python']}"]
    if info["site_packages"]:
        lines.append(f"PYTHONPATH includes {info['site_packages']}")
    elif os.environ.get("WARPX_PYTHONPATH"):
        lines.append(f"WARPX_PYTHONPATH={os.environ['WARPX_PYTHONPATH']}")
    else:
        lines.append(
            "No repo WarpX site-packages found — build WarpX under "
            f"{repo_root() / 'WarpX'} or set WARPX_PYTHONPATH"
        )
    if info["lib"]:
        lines.append(f"LD_LIBRARY_PATH includes {info['lib']}")
    ok, detail = probe_pywarpx()
    lines.append("pywarpx: OK" if ok else f"pywarpx: MISSING ({detail})")
    return "\n".join(lines)


def probe_pywarpx() -> tuple[bool, str]:
    """Try importing pywarpx with the configured environment."""
    env = apply_warpx_env()
    py = warpx_python_executable()
    try:
        proc = subprocess.run(
            [py, "-c", "import pywarpx; print(pywarpx.__file__)"],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except OSError as exc:
        return False, str(exc)
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip().splitlines()
        return False, err[-1] if err else f"exit {proc.returncode}"
    return True, (proc.stdout or "").strip()
