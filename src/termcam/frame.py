from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

RGB = tuple[int, int, int]


@dataclass
class Frame:
    width: int
    height: int
    pixels: list[list[RGB]] = field(repr=False)

    def __post_init__(self) -> None:
        if len(self.pixels) != self.height:
            raise ValueError("pixel rows do not match height")
        if any(len(row) != self.width for row in self.pixels):
            raise ValueError("pixel columns do not match width")

    def pixel(self, x: int, y: int) -> RGB:
        return self.pixels[y][x]

    def flip_h(self) -> Frame:
        return Frame(
            self.width,
            self.height,
            [list(reversed(row)) for row in self.pixels],
        )

    @classmethod
    def build(cls, width: int, height: int, fn: Callable[[int, int], RGB]) -> Frame:
        return cls(width, height, [[fn(x, y) for x in range(width)] for y in range(height)])