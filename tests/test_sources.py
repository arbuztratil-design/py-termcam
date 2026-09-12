from termcam.sources import SynthSource, synth_frame


def test_synth_frame_dimensions() -> None:
    frame = synth_frame(10, 4, 0.0)
    assert frame.width == 10
    assert frame.height == 4


def test_synth_animates() -> None:
    a = synth_frame(10, 4, 1.0)
    b = synth_frame(10, 4, 2.0)
    assert a.pixels != b.pixels


def test_synth_source_cols_rows() -> None:
    source = SynthSource(12, 6, start=0.0)
    frame = source.read()
    assert frame.width == 12
    assert frame.height == 6