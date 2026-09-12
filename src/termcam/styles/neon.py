from __future__ import annotations

from ..colors import NEON_ALT_STOPS, NEON_STOPS, luminance
from ..frame import Frame
from .base import Cell, Style, Surface

BLOCK = "\u2580"

STOP_SETS = [NEON_STOPS, NEON_ALT_STOPS, NEON_STOPS[::-1], NEON_ALT_STOPS[::-1]]


class NeonStyle(Style):
    name = "neon"
    variants = len(STOP_SETS)

    def _color(self, lum: float, stops: list) -> tuple[int, int, int]:
        t = lum
        if t >= 1.0:
            return stops[-1]
        scaled = t * (len(stops) - 1)
        index = int(scaled)
        a, b = stops[index], stops[index + 1]
        frac = scaled - index
        return (
            round(a[0] + (b[0] - a[0]) * frac),
            round(a[1] + (b[1] - a[1]) * frac),
            round(a[2] + (b[2] - a[2]) * frac),
        )

    def process(self, frame: Frame, variant: int = 0, t: float = 0.0) -> Surface:
        stops = STOP_SETS[variant % len(STOP_SETS)]
        surface: Surface = []
        for y in range(0, frame.height - 1, 2):
            row: list[Cell] = []
            for x in range(frame.width):
                top = self._color(luminance(*frame.pixel(x, y)), stops)
                bot = self._color(luminance(*frame.pixel(x, y + 1)), stops)
                row.append(Cell(BLOCK, top, bot))
            surface.append(row)
        return surface