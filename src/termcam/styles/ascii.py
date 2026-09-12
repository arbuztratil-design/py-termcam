from __future__ import annotations

from ..colors import RGB, luminance
from ..frame import Frame
from .base import Cell, Style, Surface

RAMP_SETS = [
    " .:-=+*#%@",
    " .:-=+*#%@",
    " `.-':_,^=;><+!rc*/z?s7vJL|{}[]lI1tueoZx4u83ahkbdpqwmWOCU*HNM0YG%#@",
]

RAMP_COLORS = [False, True, False, True]


class AsciiStyle(Style):
    name = "ascii"
    variants = len(RAMP_SETS)

    def process(self, frame: Frame, variant: int = 0, t: float = 0.0) -> Surface:
        ramp = RAMP_SETS[variant % len(RAMP_SETS)]
        colorize = RAMP_COLORS[variant % len(RAMP_SETS)]
        surface: Surface = []
        for y in range(0, frame.height, 2):
            row: list[Cell] = []
            for x in range(frame.width):
                rgb = frame.pixel(x, y)
                lum = luminance(*rgb)
                char = ramp[min(round(lum * (len(ramp) - 1)), len(ramp) - 1)]
                fg: RGB = rgb if colorize else (255, 255, 255)
                row.append(Cell(char, fg, None))
            surface.append(row)
        return surface