#!/usr/bin/env python3
"""
Generate RoboTacticsDisplay font from hand-traced SVG letterforms.
Uses FontForge Python bindings to import SVGs with proper typographic metrics.

Source: glyphs/Letter_X.svg
Output: build/RoboTacticsDisplay-ThinItalic.{ttf,otf,woff2}

Metrics (1000 UPM):
  - Cap height (S): full glyph height maps to ~700 units above baseline
  - x-height (lowercase): maps to ~570 units above baseline
  - Baseline: y=0
  - Descent: -200 (room for descenders if added later)
  - Ascent: 800
"""

import fontforge
import os
import sys

# --- Configuration ---
FONT_FAMILY = "Robo Tactics Display"
STYLE_NAME = "Thin Italic"
OUTPUT_BASE = "RoboTacticsDisplay-ThinItalic"

UNITS_PER_EM = 1000
ASCENT = 800
DESCENT = 200  # FontForge uses positive descent

# Source SVG directory (relative to this script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SVG_DIR = os.path.join(SCRIPT_DIR, "glyphs")
BUILD_DIR = os.path.join(SCRIPT_DIR, "build")

# Letter definitions: (filename, unicode_codepoint, is_uppercase)
LETTERS = [
    ("Letter_S.svg", ord('S'), True),
    ("Letter_a.svg", ord('a'), False),
    ("Letter_b.svg", ord('b'), False),
    ("Letter_c.svg", ord('c'), False),
    ("Letter_d.svg", ord('d'), False),
    ("Letter_e.svg", ord('e'), False),
    ("Letter_h.svg", ord('h'), False),
    ("Letter_i.svg", ord('i'), False),
    ("Letter_l.svg", ord('l'), False),
    ("Letter_n.svg", ord('n'), False),
    ("Letter_o.svg", ord('o'), False),
    ("Letter_p.svg", ord('p'), False),
    ("Letter_r.svg", ord('r'), False),
    ("Letter_t.svg", ord('t'), False),
    ("Letter_u.svg", ord('u'), False),
    ("Letter_v.svg", ord('v'), False),
    ("Letter_w.svg", ord('w'), False),
]

# SVG coordinate bounds (from AllLetters.svg analysis)
# Lowercase letters: top ~30.55, bottom ~81.55 → height ~51 SVG units
# Uppercase S: top ~29.47, bottom ~82.97 → height ~53.5 SVG units
# All share roughly the same bottom (baseline position in SVG space)

SVG_BOTTOM = 81.55   # approximate bottom of lowercase glyphs (= baseline in font)
SVG_CAP_TOP = 29.47  # top of S
SVG_LC_TOP = 30.55   # top of lowercase

# Target font metrics
CAP_HEIGHT = 700     # S top in font units above baseline
X_HEIGHT = 570       # lowercase top in font units above baseline


def create_font():
    font = fontforge.font()

    # Basic font info
    font.familyname = FONT_FAMILY
    font.fontname = FONT_FAMILY.replace(" ", "") + "-" + STYLE_NAME
    font.fullname = f"{FONT_FAMILY} {STYLE_NAME}"
    font.weight = "Thin"
    font.italicangle = -12
    font.os2_weight = 100  # Thin
    font.macstyle = 2  # Italic bit

    # Metrics
    font.em = UNITS_PER_EM
    font.ascent = ASCENT
    font.descent = DESCENT

    # OS/2 table metrics
    font.os2_typoascent = ASCENT
    font.os2_typodescent = -DESCENT
    font.os2_typolinegap = 0
    font.os2_winascent = ASCENT
    font.os2_windescent = DESCENT
    font.os2_xheight = X_HEIGHT
    font.os2_capheight = CAP_HEIGHT

    # Import each letter
    for svg_file, codepoint, is_upper in LETTERS:
        svg_path = os.path.join(SVG_DIR, svg_file)
        if not os.path.exists(svg_path):
            print(f"  WARNING: {svg_path} not found, skipping")
            continue

        glyph = font.createChar(codepoint)
        glyph.clear()

        # Import the SVG outline
        glyph.importOutlines(svg_path)

        letter = chr(codepoint)
        print(f"  Imported {letter} from {svg_file}")

        # After import, FontForge places the glyph based on SVG coordinates.
        # We need to scale and position it properly.
        #
        # The SVG y-axis is flipped by FontForge on import (SVG y-down → font y-up).
        # So SVG bottom (81.55) becomes font y=0-ish area, SVG top (29.47) becomes high.
        #
        # Let's check the bounding box after import and adjust.
        bbox = glyph.boundingBox()  # (xmin, ymin, xmax, ymax) in font units
        if bbox == (0, 0, 0, 0):
            print(f"    WARNING: empty glyph for {letter}")
            continue

        xmin, ymin, xmax, ymax = bbox
        glyph_height = ymax - ymin
        glyph_width = xmax - xmin

        print(f"    BBox after import: x=[{xmin:.1f}, {xmax:.1f}] y=[{ymin:.1f}, {ymax:.1f}] h={glyph_height:.1f}")

        # Determine target height based on upper/lowercase
        if is_upper:
            target_height = CAP_HEIGHT
        else:
            target_height = X_HEIGHT

        # Scale to target height
        if glyph_height > 0:
            scale_factor = target_height / glyph_height
            glyph.transform([scale_factor, 0, 0, scale_factor, 0, 0])

            # Recalculate bbox after scale
            bbox = glyph.boundingBox()
            xmin, ymin, xmax, ymax = bbox
            glyph_height = ymax - ymin
            glyph_width = xmax - xmin

        # Position: xmin = sidebearing, vertical depends on case
        sidebearing = 30
        dx = sidebearing - xmin
        if is_upper:
            # Center the S vertically on the middle of x-height
            # Lowercase center = X_HEIGHT / 2, so S sits from (center - h/2) to (center + h/2)
            lc_center = X_HEIGHT / 2.0
            dy = (lc_center - glyph_height / 2.0) - ymin
        else:
            dy = 0 - ymin  # sit on baseline
        glyph.transform([1, 0, 0, 1, dx, dy])

        # Set advance width (glyph width + sidebearings on both sides)
        glyph.width = int(glyph_width + sidebearing * 2)

        print(f"    Final: width={glyph.width}, height={target_height}, scale={scale_factor:.3f}")

    # Add .notdef and space
    notdef = font.createChar(-1, ".notdef")
    notdef.width = 500

    space = font.createChar(ord(' '), "space")
    space.width = 250

    # Auto-hint for better rendering
    font.autoHint()

    # Ensure build directory exists
    os.makedirs(BUILD_DIR, exist_ok=True)

    # Generate multiple formats
    ttf_path = os.path.join(BUILD_DIR, f"{OUTPUT_BASE}.ttf")
    otf_path = os.path.join(BUILD_DIR, f"{OUTPUT_BASE}.otf")
    woff2_path = os.path.join(BUILD_DIR, f"{OUTPUT_BASE}.woff2")

    font.generate(ttf_path)
    print(f"\n  Generated: {ttf_path}")

    font.generate(otf_path)
    print(f"  Generated: {otf_path}")

    font.generate(woff2_path)
    print(f"  Generated: {woff2_path}")

    print(f"\nGlyphs: {len(LETTERS)} letters + space + .notdef")
    print(f"Metrics: UPM={UNITS_PER_EM}, Ascent={ASCENT}, Descent={DESCENT}")
    print(f"         Cap Height={CAP_HEIGHT}, x-Height={X_HEIGHT}")

    font.close()


if __name__ == "__main__":
    print(f"Generating {FONT_FAMILY} {STYLE_NAME}...")
    print(f"SVG source: {SVG_DIR}")
    print()
    create_font()
