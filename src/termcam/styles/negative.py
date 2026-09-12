from __future__ import annotations

from ..colors import RGB, luminance
from ..frame import Frame
from .base import Cell, Style, Surface

BLOCK = "\u2580"

TINTS: list[tuple[int, int, int]] = [
    (255, 255, 255),
    (120, 200, 255),
    (255, 160, 220),
    (255, 220, 190),
]


def _invert(c: int) -> int:
    return 255 - c


def _poster(c: int) -> int:
    return (c // 43) * 43


class NegativeStyle(Style):
    name = "negative"
    variants = len(TINTS)

    def _pixel(self, rgb: RGB, mode: int) -> RGB:
        if mode == 0:
            return tuple(_invert(c) for c in rgb)
        if mode == 1:
            return tuple(_poster(_invert(c)) for c in rgb)
        lum = luminance(*rgb)
        gray = round((1.0 - lum) * 255)
        tint = TINTS[mode - 1]
        return tuple(round((gray * 2 + tint[i]) / 3) for i in range(3))

    def process(self, frame: Frame, variant: int = 0, t: float = 0.0) -> Surface:
        mode = variant % len(TINTS)
        surface: Surface = []
        for y in range(0, frame.height - 1, 2):
            row: list[Cell] = []
            for x in range(frame.width):
                top = self._pixel(frame.pixel(x, y), mode)
                bot = self._pixel(frame.pixel(x, y + 1), mode)
                row.append(Cell(BLOCK, top, bot))
            surface.append(row)
        return surface