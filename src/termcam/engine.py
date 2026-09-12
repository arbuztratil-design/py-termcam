from __future__ import annotations

import ctypes
import os
import sys
import time

from .camera import CameraSource, UrlSource
from .keys import KeyReader, enable_raw_input, restore_terminal
from .renderer import HIDE_CURSOR, HOME, SHOW_CURSOR, render
from .sources import SynthSource
from .styles import (
    AsciiStyle,
    DitherStyle,
    GlitchStyle,
    HalftoneStyle,
    NegativeStyle,
    NeonStyle,
    SketchStyle,
    Style,
    ThermalStyle,
)

STYLES: dict[str, type[Style]] = {
    "ascii": AsciiStyle,
    "neon": NeonStyle,
    "dither": DitherStyle,
    "glitch": GlitchStyle,
    "sketch": SketchStyle,
    "halftone": HalftoneStyle,
    "thermal": ThermalStyle,
    "negative": NegativeStyle,
}
DEFAULT_STYLE = "ascii"

KEY_MAP = {
    "a": "ascii",
    "s": "neon",
    "d": "dither",
    "g": "glitch",
    "e": "sketch",
    "h": "halftone",
    "t": "thermal",
    "x": "negative",
}

ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004


def _enable_vt() -> None:
    if os.name != "nt":
        return
    try:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)
    except OSError:
        pass


def _use_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass


def build_source(kind: str, device: int, cols: int, rows: int, url: str = ""):
    if kind == "synth":
        return SynthSource(cols, rows)
    if kind == "url":
        return UrlSource(url, cols, rows)
    return CameraSource(device, cols, rows)


def _resized(source, cols: int, rows: int):
    if isinstance(source, SynthSource):
        return SynthSource(cols, rows)
    if isinstance(source, UrlSource):
        return UrlSource(source.url, cols, rows)
    return CameraSource(source.device, cols, rows)


def run(
    source,
    fps: int = 24,
    initial_style: str = DEFAULT_STYLE,
    mirror: bool = False,
    out: str = "terminal",
    webcam_size: tuple[int, int] = (1280, 720),
    backend: str | None = "auto",
) -> None:
    _use_utf8()
    _enable_vt()

    cam = None
    _cv2 = None
    if out in ("webcam", "both"):
        from .webcam import VirtualCamera, rasterize

        cam = VirtualCamera(webcam_size[0], webcam_size[1], fps, backend=backend)
        try:
            cam.open()
        except RuntimeError as exc:
            if out == "webcam":
                raise
            print(str(exc), file=sys.stderr)
            print("Falling back to terminal output.", file=sys.stderr)
            out = "terminal"
            cam = None
    elif out == "window":
        try:
            import cv2 as _cv2

            from .webcam import rasterize

            _cv2.namedWindow("termcam")
            _cv2.destroyWindow("termcam")
        except ImportError as exc:
            raise RuntimeError("Window output needs OpenCV: pip install 'termcam'") from exc
        except Exception as exc:
            raise RuntimeError(
                "OpenCV GUI is unavailable (a headless build is installed). "
                "Reinstall with: pip install --force-reinstall opencv-python"
            ) from exc

    show_terminal = out in ("terminal", "both")
    show_window = out == "window"
    webcam_output = cam is not None

    try:
        cols, rows = os.get_terminal_size()
    except (OSError, ValueError):
        cols, rows = 80, 24
    rows = max(2, int(rows) - 1)
    if source.cols != cols or source.rows != rows:
        source = _resized(source, cols, rows)

    enable_raw_input()
    keys = KeyReader()
    keys.start()

    style_key = initial_style if initial_style in STYLES else DEFAULT_STYLE
    style = STYLES[style_key]()
    variant = 0
    flip = mirror

    frame_interval = 1.0 / max(1, fps)
    frame = None
    sys.stdout.write(HIDE_CURSOR)
    sys.stdout.flush()

    try:
        while True:
            started = time.perf_counter()
            frame = source.read()
            if flip:
                frame = frame.flip_h()
            clock = time.perf_counter()
            surface = style.process(frame, variant=variant, t=clock)
            if webcam_output:
                cam.send(rasterize(surface, webcam_size[0], webcam_size[1]))
            if show_window:
                _cv2.imshow("termcam", rasterize(surface, webcam_size[0], webcam_size[1]))
                if _cv2.waitKey(1) & 0xFF == 27:
                    break
            if show_terminal:
                sys.stdout.write(HOME)
                sys.stdout.write(render(surface))
                sys.stdout.flush()

            key = keys.poll()
            if key is not None:
                key = key.lower()
                if key in KEY_MAP:
                    target = KEY_MAP[key]
                    if target == style.name:
                        variant = (variant + 1) % style.variants
                    else:
                        style = STYLES[target]()
                        variant = 0
                elif key == "m":
                    flip = not flip
                elif key in ("q", "\x1b"):
                    break

            elapsed = time.perf_counter() - started
            remaining = frame_interval - elapsed
            if remaining > 0:
                time.sleep(remaining)
    except (KeyboardInterrupt, RuntimeError, OSError):
        pass
    finally:
        sys.stdout.write(SHOW_CURSOR + "\x1b[0m")
        sys.stdout.flush()
        if _cv2 is not None:
            _cv2.destroyAllWindows()
        if cam is not None:
            cam.close()
        close = getattr(source, "close", None)
        if close is not None:
            close()
        restore_terminal()