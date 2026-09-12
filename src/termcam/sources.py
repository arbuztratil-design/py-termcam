from __future__ import annotations

import math
import time

from .colors import NEON_STOPS, gradient
from .frame import Frame


def _plasma(x: int, y: int, w: int, h: int, t: float) -> tuple[int, int, int]:
    fx = x / max(w, 1)
    fy = y / max(h, 1)
    v = (
        math.sin(fx * 4.2 + t * 0.9)
        + math.sin(fy * 3.7 + t * 0.7)
        + math.sin((fx + fy) * 5.3 + t * 0.5)
        + math.sin(fx * fy * 9.0 - t * 0.9)
    )
    v = (v + 4.0) / 8.0
    return gradient(NEON_STOPS, v)


def synth_frame(width: int, height: int, t: float | None = None) -> Frame:
    clock = time.time() if t is None else t
    return Frame.build(width, height, lambda x, y: _plasma(x, y, width, height, clock))


class SynthSource:
    def __init__(self, cols: int, rows: int, start: float | None = None) -> None:
        self.cols = cols
        self.rows = rows
        self._t0 = time.time() if start is None else start

    def read(self) -> Frame:
        return synth_frame(self.cols, self.rows, time.time() - self._t0)