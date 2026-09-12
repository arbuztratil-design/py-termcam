from __future__ import annotations

from dataclasses import dataclass

from ..colors import RGB


@dataclass(frozen=True)
class Cell:
    char: str
    fg: RGB
    bg: RGB | None = None


Surface = list[list[Cell]]


class Style:
    name = "style"
    variants = 1

    def process(self, frame, variant: int = 0, t: float = 0.0) -> Surface:
        raise NotImplementedError