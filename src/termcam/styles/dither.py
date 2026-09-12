from __future__ import annotations

from ..colors import RGB, luminance
from ..frame import Frame
from .base import Cell, Style, Surface

BLOCK = "\u2580"

BAYER_4 = [
    [0, 8, 2, 10],
    [12, 4, 14, 6],
    [3, 11, 1, 9],
    [15, 7, 13, 5],
]

DARK_STOPS = [(0, 0, 20), (8, 0, 40), (0, 40, 120)]
LIGHT_STOPS = [(0, 200, 255), (0, 255, 160), (255, 0, 255)]


def _snap(lum: float, dark: list[RGB], light: list[RGB]) -> RGB:
    if lum > 0.5:
        t = (lum - 0.5) * 2
        return light[min(int(t * (len(light) - 1)), len(light) - 1)]
    t = lum * 2
    return dark[min(int(t * (len(dark) - 1)), len(dark) - 1)]


class DitherStyle(Style):
    name = "dither"
    variants = 2

    def process(self, frame: Frame, variant: int = 0, t: float = 0.0) -> Surface:
        dark = DARK_STOPS[::-1] if variant % 2 else DARK_STOPS
        light = LIGHT_STOPS[::-1] if variant % 2 else LIGHT_STOPS
        surface: Surface = []
        for y in range(0, frame.height - 1, 2):
            row: list[Cell] = []
            for x in range(frame.width):
                top_l = luminance(*frame.pixel(x, y))
                top_d = top_l > (BAYER_4[y % 4][x % 4] / 16.0)
                bot_l = luminance(*frame.pixel(x, y + 1))
                bot_d = bot_l > (BAYER_4[(y + 1) % 4][x % 4] / 16.0)
                top_c = _snap(top_l, dark, light) if top_d else (0, 0, 0)
                bot_c = _snap(bot_l, dark, light) if bot_d else (0, 0, 0)
                row.append(Cell(BLOCK, top_c, bot_c))
            surface.append(row)
        return surface