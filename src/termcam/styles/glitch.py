from __future__ import annotations

from ..colors import NEON_STOPS, gradient
from ..frame import Frame
from .base import Cell, Style, Surface

BLOCK = "\u2580"

PALETTES = [NEON_STOPS, NEON_STOPS[::-1], [(255, 255, 255), (0, 0, 0)], [(0, 0, 0), (255, 255, 255)]]


def _hash(x: int, y: int, seed: int) -> float:
    value = (x * 374761393 + y * 668265263 + seed * 1442695040888963407) % 288230376151711743
    return (value & 0xFFFFFFFF) / 0xFFFFFFFF


class GlitchStyle(Style):
    name = "glitch"
    variants = len(PALETTES)

    def process(self, frame: Frame, variant: int = 0, t: float = 0.0) -> Surface:
        palette = PALETTES[variant % len(PALETTES)]
        seed = int(t * 30)
        surface: Surface = []
        for y in range(0, frame.height - 1, 2):
            row: list[Cell] = []
            for x in range(frame.width):
                top = gradient(palette, _hash(x, y, seed))
                bot = gradient(palette, _hash(x, y + 1, seed * 7 + 3))
                row.append(Cell(BLOCK, top, bot))
            surface.append(row)
        return surface