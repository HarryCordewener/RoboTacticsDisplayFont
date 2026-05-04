# SuperRoboTacticsFont

Hand-traced SVG display font for **Super Robo Tactics** — a thin italic typeface with angular, mechanical letterforms inspired by mecha game aesthetics.

## Structure

```
glyphs/          Hand-traced SVG source files (one per letter)
generate_font.py FontForge script to compile SVGs into font files
build/           Generated font files (TTF, OTF, WOFF2)
```

## Building

Requires [FontForge](https://fontforge.org/) with Python bindings:

```bash
# Ubuntu/Debian
sudo apt install fontforge python3-fontforge

# Then generate
python3 generate_font.py
```

Output goes to `build/`:
- `RoboTacticsDisplay-ThinItalic.ttf`
- `RoboTacticsDisplay-ThinItalic.otf`
- `RoboTacticsDisplay-ThinItalic.woff2`

## Font Metrics

- UPM: 1000
- Cap Height: 700
- x-Height: 570
- Ascent: 800
- Descent: 200
- Italic Angle: -12°
- Weight: Thin (100)

## Current Glyphs

S, a, b, c, d, e, h, i, l, n, o, p, r, t, u, v, w (17 letters)

## License

All rights reserved. This font is proprietary to the Super Robo Tactics project.
