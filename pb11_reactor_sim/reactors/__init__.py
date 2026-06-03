"""Concrete reactor models (TAE FRC, HB11 laser, LPPFusion DPF)."""
from __future__ import annotations

from pb11_reactor_sim.engine.base import ReactorSimulation
from pb11_reactor_sim.reactors.hb11 import HB11Reactor
from pb11_reactor_sim.reactors.lpp import LPPReactor
from pb11_reactor_sim.reactors.tae import TAEReactor

#: Registry consumed by the GUI dropdown: display name -> class.
REACTOR_REGISTRY: dict[str, type[ReactorSimulation]] = {
    TAEReactor.display_name: TAEReactor,
    HB11Reactor.display_name: HB11Reactor,
    LPPReactor.display_name: LPPReactor,
}

__all__ = ["TAEReactor", "HB11Reactor", "LPPReactor", "REACTOR_REGISTRY"]
