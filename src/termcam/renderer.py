from __future__ import annotations

from .colors import to_ansi256
from .styles.base import Surface

RESET = "\x1b[0m"
BLOCK = "\u2580"
HIDE_CURSOR = "\x1b[?25l"
SHOW_CURSOR = "\x1b[?25h"
HOME = "\x1b[H"


def _fg(red: int, green: int, blue: int) -> str:
    return f"\x1b[38;5;{to_ansi256(red, green, blue)}m"


def _bg(red: int, green: int, blue: int) -> str:
    return f"\x1b[48;5;{to_ansi256(red, green, blue)}m"


def render(surface: Surface) -> str:
    out: list[str] = []
    for row in surface:
        for cell in row:
            out.append(_fg(*cell.fg))
            if cell.bg is not None:
                out.append(_bg(*cell.bg))
            out.append(cell.char)
        out.append(RESET)
        out.append("\n")
    return "".join(out)