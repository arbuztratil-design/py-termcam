from __future__ import annotations

import cv2

from .frame import Frame


def _read_and_resize(cap, cols: int, rows: int) -> Frame:
    ok, frame = cap.read()
    if not ok:
        raise RuntimeError("Source returned no frame")
    resized = cv2.resize(
        frame,
        (cols, rows * 2),
        interpolation=cv2.INTER_AREA,
    )
    pixels = [
        [(int(p[2]), int(p[1]), int(p[0])) for p in row] for row in resized
    ]
    return Frame(cols, rows * 2, pixels)


class CameraSource:
    def __init__(self, device: int = 0, cols: int = 80, rows: int = 40) -> None:
        self.device = device
        self.cols = cols
        self.rows = rows
        self._cap = cv2.VideoCapture(device)
        if not self._cap.isOpened():
            raise RuntimeError(f"Could not open camera device {device}")

    def read(self) -> Frame:
        try:
            return _read_and_resize(self._cap, self.cols, self.rows)
        except RuntimeError:
            raise RuntimeError("Camera returned no frame") from None

    def close(self) -> None:
        self._cap.release()


class UrlSource:
    def __init__(self, url: str, cols: int = 80, rows: int = 40) -> None:
        self.url = url
        self.cols = cols
        self.rows = rows
        self._cap = cv2.VideoCapture(url)
        if not self._cap.isOpened():
            raise RuntimeError(f"Could not open stream at {url}")

    def read(self) -> Frame:
        try:
            return _read_and_resize(self._cap, self.cols, self.rows)
        except RuntimeError:
            raise RuntimeError(f"Stream returned no frame: {self.url}") from None

    def close(self) -> None:
        self._cap.release()