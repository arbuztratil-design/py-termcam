from __future__ import annotations

from ..colors import RGB, luminance
from ..frame import Frame
from .base import Cell, Style, Surface

SHADES = " .:-=+*#%@"

PAPERS: list[tuple[int, int, int]] = [
    (18, 18, 22),
    (28, 24, 20),
    (40, 40, 40),
    (17, 26, 28),
]


class HalftoneStyle(Style):
    name = "halftone"
    variants = len(PAPERS)

    def process(self, frame: Frame, variant: int = 0, t: float = 0.0) -> Surface:
        paper = PAPERS[variant % len(PAPERS)]
        surface: Surface = []
        for y in range(0, frame.height - 1, 2):
            row: list[Cell] = []
            for x in range(frame.width):
                top = frame.pixel(x, y)
                bot = frame.pixel(x, y + 1)
                avg = (luminance(*top) + luminance(*bot)) / 2.0
                density = min(round(avg * (len(SHADES) - 1)), len(SHADES) - 1)
                mix = tuple((top[i] + bot[i]) // 2 for i in range(3))
                fg: RGB = tuple(min(255, mix[i] + 24) for i in range(3))
                row.append(Cell(SHADES[density], fg, paper))
            surface.append(row)
        return surface