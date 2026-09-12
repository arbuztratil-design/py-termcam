from __future__ import annotations

from ..colors import RGB, luminance
from ..frame import Frame
from .base import Cell, Style, Surface

BLOCK = "\u2580"

PALETTES: list[list[RGB]] = [
    [(0, 0, 0), (128, 0, 0), (255, 60, 0), (255, 180, 0), (255, 252, 220)],
    [(10, 0, 0), (180, 0, 0), (255, 80, 0), (255, 200, 80), (255, 255, 255)],
    [(0, 0, 0), (0, 0, 120), (0, 90, 255), (0, 220, 255), (220, 250, 255)],
    [(0, 0, 0), (40, 10, 90), (200, 0, 200), (255, 120, 40), (255, 240, 230)],
]

GAMMA_VARIANTS = [1.0, 0.6, 1.5, 1.2]


def _hot(lum: float, stops: list[RGB]) -> RGB:
    t = min(1.0, max(0.0, lum))
    index = min(int(t * (len(stops) - 1)), len(stops) - 2)
    frac = t * (len(stops) - 1) - index
    a, b = stops[index], stops[index + 1]
    return (
        round(a[0] + (b[0] - a[0]) * frac),
        round(a[1] + (b[1] - a[1]) * frac),
        round(a[2] + (b[2] - a[2]) * frac),
    )


class ThermalStyle(Style):
    name = "thermal"
    variants = len(PALETTES)

    def process(self, frame: Frame, variant: int = 0, t: float = 0.0) -> Surface:
        palette = PALETTES[variant % len(PALETTES)]
        gamma = GAMMA_VARIANTS[variant % len(GAMMA_VARIANTS)]
        surface: Surface = []
        for y in range(0, frame.height - 1, 2):
            row: list[Cell] = []
            for x in range(frame.width):
                tl = luminance(*frame.pixel(x, y)) ** gamma
                bl = luminance(*frame.pixel(x, y + 1)) ** gamma
                row.append(Cell(BLOCK, _hot(tl, palette), _hot(bl, palette)))
            surface.append(row)
        return surface