from termcam.colors import (
    NEON_STOPS,
    clamp,
    gradient,
    lerp,
    luminance,
    to_ansi256,
)


def test_luminance_bounds() -> None:
    assert luminance(0, 0, 0) == 0.0
    assert 0.999 < luminance(255, 255, 255) <= 1.0
    assert luminance(255, 0, 0) > luminance(0, 0, 128)


def test_clamp() -> None:
    assert clamp(-5) == 0
    assert clamp(300) == 255
    assert clamp(100) == 100


def test_to_ansi256_known_cube() -> None:
    assert to_ansi256(0, 0, 0) == 16
    assert to_ansi256(255, 255, 255) == 231
    assert to_ansi256(255, 0, 0) == 196
    assert to_ansi256(0, 255, 0) == 46
    assert to_ansi256(0, 0, 255) == 21


def test_gradient_edges() -> None:
    assert gradient(NEON_STOPS, 0.0) == NEON_STOPS[0]
    assert gradient(NEON_STOPS, 1.0) == NEON_STOPS[-1]


def test_lerp_between() -> None:
    assert lerp((0, 0, 0), (100, 0, 0), 0.5) == (50, 0, 0)
    assert lerp((0, 0, 0), (100, 0, 0), 0.0) == (0, 0, 0)