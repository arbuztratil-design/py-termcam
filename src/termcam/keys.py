from __future__ import annotations

import os
import sys
import threading

try:
    import msvcrt
except ImportError:  # pragma: no cover
    msvcrt = None
    import termios as _termios
    import tty as _tty


def _read_char() -> str | None:
    if msvcrt is not None:
        try:
            return msvcrt.getwch()
        except KeyboardInterrupt:
            return "q"
    fd = sys.stdin.fileno()
    return os.read(fd, 1).decode("utf-8", "ignore")


class KeyReader(threading.Thread):
    def __init__(self) -> None:
        super().__init__(daemon=True)
        self._chars: list[str] = []
        self._cond = threading.Condition()
        self._enabled = True

    def run(self) -> None:
        try:
            while self._enabled:
                char = _read_char()
                if char is None:
                    continue
                with self._cond:
                    self._chars.append(char)
                    self._cond.notify()
        except Exception:  # noqa: S110, BLE001
            pass

    def poll(self) -> str | None:
        with self._cond:
            if not self._chars:
                return None
            return self._chars.pop(0)


_saved_termios = None


def enable_raw_input() -> None:
    if sys.platform.startswith("win"):
        return
    global _saved_termios
    fd = sys.stdin.fileno()
    _saved_termios = _termios.tcgetattr(fd)
    _tty.setcbreak(fd)


def restore_terminal() -> None:
    if not sys.platform.startswith("win"):
        if _saved_termios is not None:
            try:
                _tty.tcsetattr(sys.stdin.fileno(), _tty.TCSADRAIN, _saved_termios)
            except Exception:  # noqa: S110, BLE001
                pass