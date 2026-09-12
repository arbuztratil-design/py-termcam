from termcam.cli import _build_parser, main


def test_defaults() -> None:
    args = _build_parser().parse_args([])
    assert args.source == "camera"
    assert args.style == "ascii"
    assert args.fps == 24
    assert args.device == 0
    assert args.mirror is False


def test_overrides() -> None:
    args = _build_parser().parse_args(
        ["--source", "synth", "--style", "neon", "--fps", "12", "--mirror"]
    )
    assert args.source == "synth"
    assert args.style == "neon"
    assert args.fps == 12
    assert args.mirror is True


def test_invalid_style_rejected() -> None:
    import pytest

    with pytest.raises(SystemExit):
        _build_parser().parse_args(["--style", "nope"])


def test_url_source_requires_url() -> None:
    import pytest

    with pytest.raises(SystemExit):
        main(["--source", "url"])


def test_webcam_out_parses() -> None:
    args = _build_parser().parse_args(["--out", "webcam", "--webcam-size", "960x540"])
    assert args.out == "webcam"
    assert args.webcam_size == "960x540"


def test_window_and_backend_parse() -> None:
    args = _build_parser().parse_args(["--out", "window", "--backend", "obs"])
    assert args.out == "window"
    assert args.backend == "obs"


def test_bad_backend_rejected() -> None:
    import pytest

    with pytest.raises(SystemExit):
        _build_parser().parse_args(["--backend", "nope"])


def test_bad_webcam_size_exits() -> None:
    import pytest

    with pytest.raises(SystemExit):
        main(["--source", "synth", "--out", "webcam", "--webcam-size", "abc"])


def test_webcam_missing_package_exits(monkeypatch, capsys) -> None:
    import builtins

    import pytest

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "pyvirtualcam":
            raise ImportError("no pyvirtualcam")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(SystemExit) as exc_info:
        main(["--source", "synth", "--out", "webcam"])
    assert exc_info.value.code == 1
    err = capsys.readouterr().err
    assert "pyvirtualcam" in err