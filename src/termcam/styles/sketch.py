from __future__ import annotations

from ..colors import RGB, luminance
from ..frame import Frame
from .base import Cell, Style, Surface

EDGE_RAMP = " .:-=+*#%@"
INK_RAMP = " .,:;irsXA253hMHGS#9B&@"

_VARIANTS = [
    {"color": False, "invert": False},
    {"color": True, "invert": False},
    {"color": False, "invert": True},
    {"color": True, "invert": True},
]

PAPER: RGB = (246, 246, 242)


class SketchStyle(Style):
    name = "sketch"
    variants = len(_VARIANTS)

    def process(self, frame: Frame, variant: int = 0, t: float = 0.0) -> Surface:
        params = _VARIANTS[variant % len(_VARIANTS)]
        width, height = frame.width, frame.height
        lum = [
            [luminance(*frame.pixel(x, y)) for x in range(width)]
            for y in range(height)
        ]
        ramp = EDGE_RAMP if not params["invert"] else INK_RAMP
        bg: RGB | None = PAPER if params["invert"] else None
        surface: Surface = []
        for y in range(0, height - 1, 2):
            row: list[Cell] = []
            for x in range(width):
                gx = abs(lum[y][min(x + 1, width - 1)] - lum[y][max(x - 1, 0)])
                gy = abs(
                    lum[min(y + 1, height - 1)][x] - lum[max(y - 1, 0)][x]
                )
                edge = min(1.0, (gx + gy) * 1.4)
                depth = 1.0 - edge if not params["invert"] else edge
                index = min(round(depth * (len(ramp) - 1)), len(ramp) - 1)
                if params["color"]:
                    top = frame.pixel(x, y)
                    fg: RGB = tuple(round(c * depth) for c in top)
                else:
                    shade = round(255 * depth)
                    fg = (shade, shade, shade)
                row.append(Cell(ramp[index], fg, bg))
            surface.append(row)
        return surface