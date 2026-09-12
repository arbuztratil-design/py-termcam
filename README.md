# termcam

![TermCam demo](docs/demo.gif)

Your webcam — live — rendered in the terminal as ASCII, neon, dither or
glitch art. One keystroke changes the style. No GUI windows, no browser, just
the console and you.

No webcam? **termcam** generates a procedural plasma that still reacts to
your keystrokes and serves as a screensaver-style demo.

## Install

```bash
pip install py-termcam              # terminal + window art
pip install "py-termcam[webcam]"    # + virtual camera (--out webcam)
```

## Quick start

```bash
termcam                 # uses webcam, ascii style, 24 fps
termcam --source synth  # no webcam needed — procedural plasma
termcam --source url --url "http://192.168.1.5:8080/video"  # phone via IP Webcam
termcam --out webcam --source synth   # art becomes a virtual camera device
termcam --out window --source synth   # art in a GUI window (OBS Window Capture)
```

### Hotkeys (while running)

| Key | Action                    |
|-----|---------------------------|
| a   | ASCII (luminance → chars) |
| s   | Neon (color gradient)     |
| d   | Dither (pixel noise)      |
| g   | Glitch (sparkling)        |
| e   | Sketch (edge detection)   |
| h   | Halftone (newsprint)      |
| t   | Thermal (heatmap)         |
| x   | Negative (film invert)    |
| m   | Mirror / un-mirror        |
| q   | Quit                      |

Press the style key repeatedly for palette variants.

## Styles

- **ASCII** — classic monochrome luminance ramp (`" .:-=+*#%@"`)
- **Neon** — full color, mapped through an ANSI 256 palette
- **Dither** — 4×4 Bayer matrix noise, retro pixel look
- **Glitch** — per-frame hash sparkle, chaotic but alive
- **Sketch** — edge detection (Sobel-like), pencil-look line art, light/dark paper
- **Halftone** — newspaper print: ink shades on paper-color background
- **Thermal** — heatmap palettes (fire, inferno, deep water, lava-pink)
- **Negative** — film negative, posterized, cyan/magenta/warm X-ray tints

Every style has palette/param variants — keep pressing its key to cycle.

## CLI options

```
termcam
  --source {camera,synth,url}  input source       (default: camera)
  --style {ascii,neon,dith,glitch,sketch,halftone,thermal,negative} (default: ascii)
  --out {terminal,webcam,window,both}             (default: terminal)
  --fps N                      frames per second  (default: 24)
  --cols N                     terminal width hint (auto-detected)
  --device N                   camera device index (default: 0)
  --url URL                    MJPEG stream for --source url
  --backend {auto,obs,unitycapture} virtual camera backend (default: auto)
  --webcam-size WxH            virtual camera resolution (default: 1280x720)
  --mirror                     flip horizontally
```

## Virtual camera & OBS

You can turn the art itself into a webcam device.

**As a real webcam in ANY app including OBS** (best: no OBS dependency):

```bash
pip install "py-termcam[webcam]"
termcam --source synth --out webcam --backend unitycapture
```

This uses the free, open-source [UnityCapture](https://github.com/schellingb/UnityCapture)
DirectShow filter as the virtual camera device **`Unity Video Capture`**. Install it
once as administrator:

1. Clone/download [UnityCapture](https://github.com/schellingb/UnityCapture).
2. From `UnityCapture/Install` run `Install.bat` as administrator (registers two
   DLLs via `regsvr32`). Keep that folder in place while installed.
3. In OBS: **Sources → + → Video Capture Device → Unity Video Capture**.
   The device appears even while termcam runs without OBS active.

Remove it later with `Uninstall.bat` (as administrator).

**As a webcam in other apps** (Zoom, Discord, …), using OBS's own virtual camera:

```bash
termcam --out webcam --source synth
```

With the `obs` backend, start **OBS Studio → Start Virtual Camera** once, then pick
`OBS Virtual Camera` as the camera in any other app. Cannot be consumed as an
input inside the same OBS instance.

**Preview window** (for OBS Window Capture if you prefer):

```bash
termcam --out window --source synth
```

A window titled `termcam` opens; in OBS add **Sources → Window Capture →
termcam**.

Hotkeys work in every output mode (`a/s/d/g/e/h/t/x`, `m`, `q`).

## Phone as a webcam

No USB webcam? Any Android phone with a WiFi connection works — termcam just
needs a URL. Tested target: a 2016 Samsung Galaxy J1 Mini (Android 5.1).

1. Install the free app **IP Webcam** on the phone (Play Store; works on
   Android 5.0+).
2. Connect the phone and your PC to the **same WiFi** network.
3. Open IP Webcam → tap **Start server** at the bottom. The app shows an
   address like `http://192.168.1.5:8080`.
4. Verify on the PC in a browser: open that address — you should see the
   camera preview. (Phone as a hotspot also works: connect the PC to the
   phone's hotspot instead.)
5. Point termcam at the MJPEG stream:

   ```bash
   termcam --source url --url "http://192.168.1.5:8080/video"
   ```

6. Hotkeys are the same — `a/s/d/g` switches styles, so the low-res J1 Mini
   camera becomes lo-fi neon/dither art.

If IP Webcam has a password set (Settings → Login), embed it in the URL:
`http://user:pass@192.168.1.5:8080/video`.

## Development

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT