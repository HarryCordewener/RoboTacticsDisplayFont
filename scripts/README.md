# Scripts

All scripts should be run from the repository root.

## Font generation

| Script | Description |
|--------|-------------|
| `generate_font.py` | Builds letter glyphs (A–Z, a–z) from SVGs in `glyphs/`. Outputs `.ttf`, `.otf`, `.woff2` to `build/`. Requires FontForge Python bindings. |
| `generate_symbols.py` | Builds digit and symbol glyphs procedurally. Merges into the existing `.ttf` in `build/`. Requires FontForge Python bindings. |

## Asset generation

| Script | Description |
|--------|-------------|
| `generate_logo.py` | Produces `logo.svg` — the styled title banner with embedded base64 font. |
| `generate_glyphs.py` | Produces `glyphs.svg` — a dark-themed table showing all supported characters with embedded base64 font. |

## Usage

```bash
# Full rebuild
python3 scripts/generate_font.py
python3 scripts/generate_symbols.py
python3 scripts/generate_logo.py
python3 scripts/generate_glyphs.py
```

Run `generate_font.py` before `generate_symbols.py` (symbols merges into the font built by the first script). The logo/glyphs scripts read the final `.ttf` from `build/`.
