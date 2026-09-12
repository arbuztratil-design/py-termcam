from __future__ import annotations

RGB = tuple[int, int, int]


def luminance(r: int, g: int, b: int) -> float:
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0


def clamp(v: int) -> int:
    return max(0, min(255, v))


def to_ansi256(r: int, g: int, b: int) -> int:
    r, g, b = clamp(r), clamp(g), clamp(b)
    if r == g == b:
        if r < 8:
            return 16
        if r > 248:
            return 231
        return round((r - 8) / 10) * 36 + 232
    r_i = round(r / 51)
    g_i = round(g / 51)
    b_i = round(b / 51)
    return 16 + 36 * r_i + 6 * g_i + b_i


def lerp(a: RGB, b: RGB, t: float) -> RGB:
    t = max(0.0, min(1.0, t))
    return (
        round(a[0] + (b[0] - a[0]) * t),
        round(a[1] + (b[1] - a[1]) * t),
        round(a[2] + (b[2] - a[2]) * t),
    )


NEON_STOPS = [
    (12, 12, 60),
    (0, 255, 255),
    (255, 0, 255),
    (255, 255, 0),
    (255, 255, 255),
]

NEON_ALT_STOPS = [
    (0, 0, 0),
    (255, 0, 128),
    (255, 140, 0),
    (255, 255, 255),
]


def gradient(stops: list[RGB], t: float) -> RGB:
    t = max(0.0, min(1.0, t))
    if t >= 1.0:
        return stops[-1]
    scaled = t * (len(stops) - 1)
    index = int(scaled)
    return lerp(stops[index], stops[index + 1], scaled - index)