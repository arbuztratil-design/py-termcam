import pytest

from termcam.frame import Frame


def test_build_dimensions() -> None:
    frame = Frame.build(3, 2, lambda x, y: (x, y, 0))
    assert frame.width == 3
    assert frame.height == 2
    assert frame.pixel(2, 1) == (2, 1, 0)


def test_build_validates() -> None:
    with pytest.raises(ValueError):
        Frame(2, 2, [[(0, 0, 0)]])
    with pytest.raises(ValueError):
        Frame(1, 2, [[(0, 0, 0)], [(0, 0, 0), (0, 0, 0)]])
    with pytest.raises(ValueError):
        Frame(2, 1, [[(0, 0, 0)], [(0, 0, 0)]])


def test_flip_h() -> None:
    frame = Frame.build(2, 1, lambda x, _y: (x, 0, 0))
    flipped = frame.flip_h()
    assert flipped.pixel(0, 0) == (1, 0, 0)
    assert flipped.pixel(1, 0) == (0, 0, 0)