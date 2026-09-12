from termcam.frame import Frame
from termcam.renderer import RESET, render
from termcam.styles import AsciiStyle, NeonStyle


def test_render_contains_block_and_escape() -> None:
    style = NeonStyle()
    surface = style.process(Frame.build(2, 2, lambda _x, _y: (200, 50, 50)), 0)
    out = render(surface)
    assert "\u2580" in out
    assert "\x1b[" in out
    assert RESET in out


def test_render_ascii_no_bg() -> None:
    style = AsciiStyle()
    surface = style.process(Frame.build(2, 2, lambda _x, _y: (0, 0, 0)), 0)
    out = render(surface)
    assert "\x1b[38;5;" in out
    assert "\x1b[48;5;" not in out