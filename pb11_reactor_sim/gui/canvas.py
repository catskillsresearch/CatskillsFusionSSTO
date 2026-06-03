"""
Primary 2D spatial canvas.

Renders the selected reactor core as layered pyqtgraph items, bottom to top:

1. a dark gas/vacuum background,
2. a live colormap of the plasma field (potential ``Phi`` or magnetic ``B``),
3. a high-contrast overlay marking solid conductor structures,
4. macroparticle scatter overlays colored by species, and
5. persistent text labels naming each structural element.

The view uses data (metre) coordinates with a locked 1:1 aspect ratio so the
geometry is never distorted.
"""
from __future__ import annotations

import numpy as np
import numpy.typing as npt
import pyqtgraph as pg
from PySide6 import QtCore, QtGui, QtWidgets

from pb11_reactor_sim.engine.base import ReactorSimulation

pg.setConfigOption("imageAxisOrder", "row-major")
pg.setConfigOption("background", "#0a0a12")
pg.setConfigOption("foreground", "#cccccc")

FloatArray = npt.NDArray[np.float64]

#: Maximum macroparticles drawn per species (subsampled for render speed).
_MAX_DRAW = 1200


class ReactorCanvas(QtWidgets.QWidget):
    """Layered 2D visualization of the active reactor core."""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._glw = pg.GraphicsLayoutWidget()
        layout.addWidget(self._glw)

        self._plot: pg.PlotItem = self._glw.addPlot()
        self._plot.setAspectLocked(True)
        self._plot.showGrid(x=True, y=True, alpha=0.15)
        self._plot.setLabel("bottom", "x", units="m")
        self._plot.setLabel("left", "y", units="m")

        # Field image (plasma colormap). Keep an explicit LUT so the very first
        # (paused) frame is colored deterministically, independent of the
        # ColorBarItem update timing.
        self._cmap = pg.colormap.get("inferno")
        self._lut = self._cmap.getLookupTable(0.0, 1.0, 256)
        self._field_img = pg.ImageItem()
        self._field_img.setColorMap(self._cmap)
        self._field_img.setLookupTable(self._lut)
        self._plot.addItem(self._field_img)

        # Conductor overlay (RGBA, transparent except solid cells).
        self._conductor_img = pg.ImageItem()
        self._plot.addItem(self._conductor_img)

        # Color bar for the field.
        self._cbar = pg.ColorBarItem(colorMap=pg.colormap.get("inferno"), width=12)
        self._cbar.setImageItem(self._field_img, insert_in=self._plot)

        # One scatter item per species (created lazily).
        self._scatters: dict[str, pg.ScatterPlotItem] = {}

        # Persistent structure labels.
        self._label_items: list[pg.TextItem] = []

        self._backend_text = pg.TextItem(anchor=(0, 0), color=(150, 255, 200))
        self._plot.addItem(self._backend_text)

        self._current_reactor: ReactorSimulation | None = None

    # -- lifecycle ----------------------------------------------------------
    def attach(self, reactor: ReactorSimulation, backend_label: str) -> None:
        """Bind a reactor: rebuild static layers (geometry, labels, scatters)."""
        self._current_reactor = reactor
        g = reactor.grid
        x0, x1, y0, y1 = g.extent

        # Position field + conductor images on the data rect.
        rect = QtCore.QRectF(x0, y0, g.Lx, g.Ly)
        self._field_img.setRect(rect)
        self._conductor_img.setRect(rect)

        self._draw_conductors(reactor)
        self._rebuild_labels(reactor, backend_label)
        self._rebuild_scatters(reactor)

        self._plot.setXRange(x0, x1, padding=0.02)
        self._plot.setYRange(y0, y1, padding=0.02)

    def _draw_conductors(self, reactor: ReactorSimulation) -> None:
        """Render the conductor mask as a high-contrast cyan-white overlay."""
        mask = reactor.conductor_mask
        ny, nx = mask.shape
        rgba = np.zeros((ny, nx, 4), dtype=np.ubyte)
        # Solid structures drawn as bright cyan-white, fully opaque.
        rgba[mask] = (180, 230, 255, 235)
        self._conductor_img.setImage(rgba, autoLevels=False)

    def _rebuild_labels(self, reactor: ReactorSimulation, backend_label: str) -> None:
        for item in self._label_items:
            self._plot.removeItem(item)
        self._label_items.clear()
        for lab in reactor.labels:
            ti = pg.TextItem(lab.text, color=lab.color, anchor=(0, 0.5))
            ti.setPos(lab.x, lab.y)
            font = QtGui.QFont()
            font.setPointSize(8)
            font.setBold(True)
            ti.setFont(font)
            self._plot.addItem(ti)
            self._label_items.append(ti)

        g = reactor.grid
        self._backend_text.setText(f"Engine: {backend_label}")
        self._backend_text.setPos(g.x0 + 0.01 * g.Lx, g.y0 + 0.02 * g.Ly)

    def _rebuild_scatters(self, reactor: ReactorSimulation) -> None:
        for s in self._scatters.values():
            self._plot.removeItem(s)
        self._scatters.clear()
        for sym, sp in reactor.species.items():
            color = sp.species.color
            scatter = pg.ScatterPlotItem(
                size=3.0,
                pen=None,
                brush=pg.mkBrush(*color, 200),
                name=sp.species.name,
            )
            self._plot.addItem(scatter)
            self._scatters[sym] = scatter

    # -- per-frame refresh --------------------------------------------------
    def refresh(self) -> None:
        """Update the field image and particle scatters from the reactor state."""
        reactor = self._current_reactor
        if reactor is None:
            return

        field, label = reactor.display_field()
        finite = np.isfinite(field)
        if np.any(finite):
            lo = float(np.min(field[finite]))
            hi = float(np.max(field[finite]))
            if hi <= lo:
                hi = lo + 1.0e-12
            self._field_img.setImage(field, autoLevels=False, levels=(lo, hi))
            self._field_img.setLookupTable(self._lut)
            self._cbar.setLevels((lo, hi))
        self._cbar.setLabel("right", label)

        for sym, scatter in self._scatters.items():
            sp = reactor.species.get(sym)
            if sp is None or sp.count == 0:
                scatter.setData([], [])
                continue
            x, y = sp.x, sp.y
            if x.size > _MAX_DRAW:
                idx = np.random.default_rng(sp.count).choice(x.size, _MAX_DRAW, replace=False)
                x, y = x[idx], y[idx]
            scatter.setData(x, y)
