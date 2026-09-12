from __future__ import annotations

import numpy as np

from .colors import to_ansi256
from .font import glyph_rows
from .styles.base import Surface

BLOCK = "\u2580"

SYSTEM_16 = [
    (0, 0, 0),
    (128, 0, 0),
    (0, 128, 0),
    (128, 128, 0),
    (0, 0, 128),
    (128, 0, 128),
    (0, 128, 128),
    (192, 192, 192),
    (128, 128, 128),
    (255, 0, 0),
    (0, 255, 0),
    (255, 255, 0),
    (0, 0, 255),
    (255, 0, 255),
    (0, 255, 255),
    (255, 255, 255),
]


def _cube(factor: int) -> int:
    return 0 if factor == 0 else 55 + 40 * factor


def ansi_to_rgb(index: int) -> tuple[int, int, int]:
    if index < 16:
        return SYSTEM_16[index]
    if index < 232:
        rem = index - 16
        r, g, b = rem // 36, rem % 36 // 6, rem % 36 % 6
        return (_cube(r), _cube(g), _cube(b))
    gray = 8 + (index - 232) * 10
    return (gray, gray, gray)


def rasterize(surface: Surface, out_width: int = 1280, out_height: int = 720) -> np.ndarray:
    nrows = len(surface)
    if nrows == 0:
        raise ValueError("empty surface")
    ncols = len(surface[0])
    if ncols == 0:
        raise ValueError("empty surface row")

    scale = max(1, min(out_width // (ncols * 5), out_height // (nrows * 7)))
    tile_w, tile_h = 5 * scale, 7 * scale
    canvas_w = ncols * tile_w
    canvas_h = nrows * tile_h
    ox = (out_width - canvas_w) // 2
    oy = (out_height - canvas_h) // 2

    frame = np.zeros((out_height, out_width, 3), dtype=np.uint8)
    tile_cache: dict[tuple[str, int, int], np.ndarray] = {}

    for r, row in enumerate(surface):
        y0 = oy + r * tile_h
        if y0 >= out_height:
            break
        for c, cell in enumerate(row):
            x0 = ox + c * tile_w
            if x0 >= out_width:
                break
            y1 = min(y0 + tile_h, out_height)
            x1 = min(x0 + tile_w, out_width)
            if x0 < 0 or y0 < 0:
                continue
            fg_rgb = cell.fg
            bg_rgb = cell.bg if cell.bg is not None else (0, 0, 0)
            key = (cell.char, to_ansi256(*fg_rgb), to_ansi256(*bg_rgb))
            tile = tile_cache.get(key)
            if tile is None:
                tile = _make_tile(cell.char, *key[1:], scale)
                tile_cache[key] = tile
            frame[y0:y1, x0:x1] = tile[: y1 - y0, : x1 - x0]

    return frame


def _make_tile(char: str, fg_index: int, bg_index: int, scale: int) -> np.ndarray:
    fg = np.array(ansi_to_rgb(fg_index), dtype=np.uint8)
    bg = np.array(ansi_to_rgb(bg_index), dtype=np.uint8)
    if char == BLOCK:
        tile = np.empty((7 * scale, 5 * scale, 3), dtype=np.uint8)
        tile[:, :] = bg
        tile[: 7 * scale // 2, :] = fg
        return tile
    tile = np.empty((7 * scale, 5 * scale, 3), dtype=np.uint8)
    tile[:, :] = bg
    for gy, bits in enumerate(glyph_rows(char)):
        for gx in range(5):
            if bits[gx] == "1":
                tile[gy * scale : (gy + 1) * scale, gx * scale : (gx + 1) * scale] = fg
    return tile


class VirtualCamera:
    def __init__(self, width: int, height: int, fps: int, backend: str | None = None) -> None:
        self.width = width
        self.height = height
        self.fps = fps
        self.backend = backend
        self._cam = None

    def open(self) -> None:
        try:
            import pyvirtualcam as pv
        except ImportError as exc:
            raise RuntimeError(
                "pyvirtualcam is not installed; run: pip install 'termcam[webcam]'"
            ) from exc
        kwargs = {} if self.backend in (None, "auto") else {"backend": self.backend}
        try:
            self._cam = pv.Camera(width=self.width, height=self.height, fps=self.fps, **kwargs)
        except Exception as exc:
            raise RuntimeError(
                "Could not open a virtual camera; start OBS Studio with "
                "its Virtual Camera, or install the MediaFoundation backend"
            ) from exc

    def send(self, rgb: np.ndarray) -> None:
        if self._cam is None:
            raise RuntimeError("virtual camera is not open")
        fmt = getattr(self._cam, "fmt", None)
        name = getattr(fmt, "name", "")
        height, width = rgb.shape[0], rgb.shape[1]
        if name == "RGB":
            self._cam.send(rgb)
        elif name == "BGRA":
            bgra = np.empty((height, width, 4), dtype=np.uint8)
            bgra[:, :, 0] = rgb[:, :, 2]
            bgra[:, :, 1] = rgb[:, :, 1]
            bgra[:, :, 2] = rgb[:, :, 0]
            bgra[:, :, 3] = 255
            self._cam.send(bgra)
        elif name == "RGBA":
            rgba = np.empty((height, width, 4), dtype=np.uint8)
            rgba[:, :, 0:3] = rgb
            rgba[:, :, 3] = 255
            self._cam.send(rgba)
        else:
            raise RuntimeError(f"unsupported virtual camera format: {fmt}")

    def close(self) -> None:
        if self._cam is not None:
            try:
                self._cam.close()
            finally:
                self._cam = None