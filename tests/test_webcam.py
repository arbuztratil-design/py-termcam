import numpy as np
import pytest

from termcam.styles.base import Cell
from termcam.webcam import ansi_to_rgb, rasterize


def _surface(nrows: int = 2, ncols: int = 2) -> list[list[Cell]]:
    return [
        [Cell("@", (255, 255, 255), (0, 0, 0)) for _ in range(ncols)]
        for _ in range(nrows)
    ]


def test_rasterize_dimensions() -> None:
    frame = rasterize(_surface(), 80, 28)
    assert isinstance(frame, np.ndarray)
    assert frame.dtype == np.uint8
    assert frame.shape == (28, 80, 3)


def test_rasterize_centers_and_draws_glyph() -> None:
    frame = rasterize(_surface(), 80, 28)
    assert not frame[0, 0].any()  # left letterbox is black
    assert frame[0, 32].tolist() == [255, 255, 255]  # '@' glyph col 1 at global x=32
    assert not frame[0, 31].any()  # glyph col 0 is empty


def test_rasterize_block_fills_top_half() -> None:
    surface = [[Cell("\u2580", (255, 255, 255), (0, 0, 0))]]
    frame = rasterize(surface, 20, 14)  # scale = min(20//5, 14//7) = 2
    assert frame[:7, :].sum() > 0  # top half fg
    assert frame[8:, :].sum() == 0  # bottom half bg


def test_rasterize_small_surface_scale_floor() -> None:
    frame = rasterize(_surface(ncols=1000, nrows=1000), 40, 40)
    assert frame.shape == (40, 40, 3)


def test_rasterize_rejects_empty_surface() -> None:
    with pytest.raises(ValueError):
        rasterize([], 80, 28)
    with pytest.raises(ValueError):
        rasterize([[]], 80, 28)


def test_ansi_to_rgb_bounds() -> None:
    assert ansi_to_rgb(0) == (0, 0, 0)
    assert ansi_to_rgb(15) == (255, 255, 255)
    assert ansi_to_rgb(196) == (255, 0, 0)
    assert ansi_to_rgb(46) == (0, 255, 0)
    assert ansi_to_rgb(21) == (0, 0, 255)
    assert ansi_to_rgb(231) == (255, 255, 255)
    assert ansi_to_rgb(232) == (8, 8, 8)