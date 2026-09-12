from __future__ import annotations

import argparse
import sys

from .engine import DEFAULT_STYLE, STYLES, _use_utf8, build_source, run


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="termcam",
        description=(
            "Live webcam → terminal art. Keystrokes: a/s/d/g/e/h/t/x styles, "
            "m mirror, q quit."
        ),
    )
    parser.add_argument(
        "--source", choices=("camera", "synth", "url"), default="camera",
        help="input source (default: camera)",
    )
    parser.add_argument(
        "--style", choices=tuple(STYLES), default=DEFAULT_STYLE,
        help=f"initial style (default: {DEFAULT_STYLE})",
    )
    parser.add_argument(
        "--out",
        choices=("terminal", "webcam", "window", "both"),
        default="terminal",
        help="where to show art: terminal, virtual camera (webcam), preview window, or both",
    )
    parser.add_argument(
        "--backend",
        choices=("auto", "obs", "unitycapture"),
        default="auto",
        help="virtual camera backend (default: auto)",
    )
    parser.add_argument(
        "--webcam-size",
        default="1280x720",
        metavar="WxH",
        help="virtual camera resolution (default: 1280x720)",
    )
    parser.add_argument("--fps", type=int, default=24, help="frames per second (default: 24)")
    parser.add_argument("--device", type=int, default=0, help="camera device index (default: 0)")
    parser.add_argument(
        "--url", default="",
        help="MJPEG stream URL for --source url (e.g. http://192.168.1.5:8080/video)",
    )
    parser.add_argument("--cols", type=int, default=0, help="horizontal cells (0 = auto-detect)")
    parser.add_argument("--mirror", action="store_true", help="start mirrored")
    return parser


def main(argv: list[str] | None = None) -> None:
    _use_utf8()
    args = _build_parser().parse_args(argv)

    if args.source == "url" and not args.url:
        print("--source url requires --url http://<host>:<port>/video", file=sys.stderr)
        sys.exit(1)

    try:
        width_s, height_s = args.webcam_size.lower().split("x", 1)
        webcam_size = (int(width_s), int(height_s))
    except (ValueError, IndexError):
        print(f"Bad --webcam-size {args.webcam_size!r}; expected WxH like 1280x720", file=sys.stderr)
        sys.exit(1)
    if webcam_size[0] <= 0 or webcam_size[1] <= 0:
        print("Bad --webcam-size; width and height must be positive", file=sys.stderr)
        sys.exit(1)

    try:
        source = build_source(args.source, args.device, args.cols or 80, 40, args.url)
    except RuntimeError as exc:
        if args.source == "camera":
            print(f"Camera unavailable ({exc}). Falling back to synth.", file=sys.stderr)
            source = build_source("synth", 0, args.cols or 80, 40)
        else:
            print(f"{exc}. Try --source synth as a demo.", file=sys.stderr)
            sys.exit(1)

    print(
        "a/s/d/g/e/h/t/x = styles, m = mirror, q = quit. Pressing a style key again cycles variants.",
        file=sys.stderr,
    )
    try:
        run(
            source,
            fps=args.fps,
            initial_style=args.style,
            mirror=args.mirror,
            out=args.out,
            webcam_size=webcam_size,
            backend=args.backend,
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()