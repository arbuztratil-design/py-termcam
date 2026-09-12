from termcam.frame import Frame
from termcam.styles import (
    AsciiStyle,
    DitherStyle,
    GlitchStyle,
    HalftoneStyle,
    NegativeStyle,
    NeonStyle,
    SketchStyle,
    ThermalStyle,
)


def _frame(width: int, height: int) -> Frame:
    return Frame.build(width, height, lambda x, y: (255 if x % 2 else 0, 0, 20))


def test_ascii_black_to_space_white_to_at() -> None:
    style = AsciiStyle()
    black = Frame.build(1, 2, lambda _x, _y: (0, 0, 0))
    white = Frame.build(1, 2, lambda _x, _y: (255, 255, 255))
    assert style.process(black, 0)[0][0].char == " "
    assert style.process(white, 0)[0][0].char == "@"


def test_ascii_surface_size() -> None:
    style = AsciiStyle()
    surface = style.process(_frame(4, 4), 0)
    assert len(surface) == 2  # half vertical resolution
    assert all(len(row) == 4 for row in surface)


def test_neon_uses_half_blocks() -> None:
    style = NeonStyle()
    surface = style.process(_frame(4, 4), 0)
    assert style.variants == 4
    assert surface[0][0].char == "\u2580"
    assert surface[0][0].bg is not None


def test_neon_variants_differ() -> None:
    style = NeonStyle()
    a = style.process(_frame(4, 4), 0)[0][0]
    b = style.process(_frame(4, 4), 1)[0][0]
    assert a.fg != b.fg


def test_dither_deterministic() -> None:
    style = DitherStyle()
    a = style.process(_frame(4, 4), 0, t=1.0)
    b = style.process(_frame(4, 4), 0, t=1.0)
    assert a == b


def test_dither_matches() -> None:
    style = DitherStyle()
    black = Frame.build(2, 2, lambda _x, _y: (0, 0, 0))
    surface = style.process(black, 0, t=0.0)
    assert surface[0][0].fg == (0, 0, 0)


def test_glitch_deterministic() -> None:
    style = GlitchStyle()
    a = style.process(_frame(4, 4), 0, t=2.0)
    b = style.process(_frame(4, 4), 0, t=2.0)
    assert a == b


def test_glitch_changes_over_time() -> None:
    style = GlitchStyle()
    a = style.process(_frame(4, 4), 0, t=1.0)
    b = style.process(_frame(4, 4), 0, t=100.0)
    assert a != b


def test_sketch_surface_size_and_deterministic() -> None:
    style = SketchStyle()
    a = style.process(_frame(4, 4), 0, t=1.0)
    b = style.process(_frame(4, 4), 0, t=1.0)
    assert len(a) == 2
    assert all(len(row) == 4 for row in a)
    assert a == b


def test_sketch_invert_uses_paper_bg() -> None:
    style = SketchStyle()
    surface = style.process(_frame(4, 4), 2)
    assert surface[0][0].bg is not None


def test_halftone_uses_shades_and_paper() -> None:
    style = HalftoneStyle()
    surface = style.process(_frame(4, 4), 0)
    assert style.variants == 4
    assert surface[0][0].char in " .:-=+*#%@"
    assert surface[0][0].bg is not None


def test_halftone_deterministic() -> None:
    style = HalftoneStyle()
    a = style.process(_frame(4, 4), 1, t=0.5)
    b = style.process(_frame(4, 4), 1, t=0.5)
    assert a == b


def test_thermal_half_blocks_and_variants() -> None:
    style = ThermalStyle()
    white = Frame.build(2, 2, lambda _x, _y: (255, 255, 255))
    surface = style.process(white, 0)
    assert surface[0][0].char == "\u2580"
    assert surface[0][0].bg is not None
    a = style.process(_frame(4, 4), 0)
    b = style.process(_frame(4, 4), 1)
    assert a[0][0].fg != b[0][0].fg


def test_negative_inverts_colors() -> None:
    style = NegativeStyle()
    black = Frame.build(2, 2, lambda _x, _y: (0, 0, 0))
    white = Frame.build(2, 2, lambda _x, _y: (255, 255, 255))
    invert_black = style.process(black, 0)[0][0]
    invert_white = style.process(white, 0)[0][0]
    assert invert_black.fg == (255, 255, 255)
    assert invert_white.fg == (0, 0, 0)


def test_negative_deterministic() -> None:
    style = NegativeStyle()
    a = style.process(_frame(4, 4), 2, t=3.0)
    b = style.process(_frame(4, 4), 2, t=3.0)
    assert a == b