#!/usr/bin/env python3
"""
Generate RoboTacticsDisplay font from hand-traced SVG letterforms.
Uses FontForge Python bindings to import SVGs with proper typographic metrics,
then applies category-based sidebearings and GPOS kern pairs via fontTools.

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

# Letter definitions: (filename, unicode_codepoint, is_uppercase, has_descender)
# has_descender is optional (defaults to False)
LETTERS = [
    ("Letter_S.svg", ord('S'), True),
    ("Letter_a.svg", ord('a'), False),
    ("Letter_b.svg", ord('b'), False),
    ("Letter_c.svg", ord('c'), False),
    ("Letter_d.svg", ord('d'), False),
    ("Letter_e.svg", ord('e'), False),
    ("Letter_f.svg", ord('f'), False),
    ("Letter_g.svg", ord('g'), False),
    ("Letter_h.svg", ord('h'), False),
    ("Letter_i.svg", ord('i'), False),
    ("Letter_j.svg", ord('j'), False),
    ("Letter_k.svg", ord('k'), False),
    ("Letter_l.svg", ord('l'), False),
    ("Letter_m.svg", ord('m'), False),
    ("Letter_n.svg", ord('n'), False),
    ("Letter_o.svg", ord('o'), False),
    ("Letter_p.svg", ord('p'), False),
    ("Letter_q.svg", ord('q'), False),
    ("Letter_r.svg", ord('r'), False),
    ("Letter_s.svg", ord('s'), False),
    ("Letter_t.svg", ord('t'), False),
    ("Letter_u.svg", ord('u'), False),
    ("Letter_v.svg", ord('v'), False),
    ("Letter_w.svg", ord('w'), False),
    ("Letter_x.svg", ord('x'), False),
    ("Letter_y.svg", ord('y'), False),
    ("Letter_z.svg", ord('z'), False),
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

# --- Category-based sidebearings ---
# Shape categories determine sidebearing values for optical evenness
SHAPE_CATEGORIES = {
    'straight': 30,   # letters with straight vertical sides: h, l, n, d, b, k, i
    'round': 18,      # letters with round sides: o, c, e, s
    'open': 12,       # letters with open/angled sides: r, t, f, j
    'diagonal': 15,   # letters with diagonal strokes: v, w, x, z, y
    'mixed': 24,      # letters with one straight + one other: a, u, p, q, g, m
}

# Map each letter to its category
LETTER_CATEGORIES = {
    'S': 'round',
    'a': 'mixed', 'b': 'straight', 'c': 'round', 'd': 'straight',
    'e': 'round', 'f': 'open', 'g': 'mixed', 'h': 'straight',
    'i': 'straight', 'j': 'open', 'k': 'straight', 'l': 'straight',
    'm': 'mixed', 'n': 'straight', 'o': 'round', 'p': 'mixed',
    'q': 'mixed', 'r': 'open', 's': 'round', 't': 'open',
    'u': 'mixed', 'v': 'diagonal', 'w': 'diagonal', 'x': 'diagonal',
    'y': 'diagonal', 'z': 'diagonal',
}

# --- GPOS Kern pairs ---
# Negative = tighter, positive = looser
KERN_PAIRS = [
    ('o', 'b', -18),
    ('u', 'p', -24),
    ('c', 't', 8),
    ('S', 'u', -28),
    ('t', 'a', -15),
    ('t', 'i', -15),
    ('i', 'c', -12),
    ('a', 'c', -12),
    ('c', 'S', -15),
    ('e', 'r', -12),
]


def get_sidebearing(letter):
    """Get the sidebearing for a letter based on its shape category."""
    cat = LETTER_CATEGORIES.get(letter, 'straight')
    return SHAPE_CATEGORIES[cat]


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
    for entry in LETTERS:
        if len(entry) == 4:
            svg_file, codepoint, is_upper, has_descender = entry
        else:
            svg_file, codepoint, is_upper = entry
            has_descender = False
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
        # The SVG y-axis is flipped by FontForge on import (SVG y-down → font y-up).
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
            if has_descender:
                # Scale so x-height portion = X_HEIGHT (descender hangs below)
                xheight_ratio = 51.001 / 68.896
                scale_factor = target_height / (glyph_height * xheight_ratio)
            else:
                scale_factor = target_height / glyph_height
            glyph.transform([scale_factor, 0, 0, scale_factor, 0, 0])

            # Recalculate bbox after scale
            bbox = glyph.boundingBox()
            xmin, ymin, xmax, ymax = bbox
            glyph_height = ymax - ymin
            glyph_width = xmax - xmin

        # Position: category-based sidebearing, vertical depends on case
        sidebearing = get_sidebearing(letter)
        dx = sidebearing - xmin
        if is_upper:
            # Center S vertically on the middle of x-height
            lc_center = X_HEIGHT / 2.0
            dy = (lc_center - glyph_height / 2.0) - ymin
        elif has_descender:
            # Position so top of glyph = X_HEIGHT (descender hangs below baseline)
            dy = X_HEIGHT - ymax
        else:
            dy = 0 - ymin  # sit on baseline
        glyph.transform([1, 0, 0, 1, dx, dy])

        # Set advance width (glyph width + sidebearings on both sides)
        glyph.width = int(glyph_width + sidebearing * 2)

        print(f"    Final: width={glyph.width}, sidebearing={sidebearing}, scale={scale_factor:.3f}")

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

    return ttf_path


def apply_kerning(ttf_path):
    """Apply GPOS kern pairs to the generated TTF using fontTools."""
    from fontTools.ttLib import TTFont
    from fontTools.feaLib.builder import addOpenTypeFeatures
    import tempfile

    # Build .fea content
    fea_lines = [
        "feature kern {",
        "  lookup kern_pairs {",
        "    lookupflag 0;",
    ]
    for left, right, value in KERN_PAIRS:
        left_name = "S" if left == 'S' else left
        right_name = "S" if right == 'S' else right
        fea_lines.append(f"    pos {left_name} {right_name} {value};")
    fea_lines.append("  } kern_pairs;")
    fea_lines.append("} kern;")
    fea_content = "\n".join(fea_lines)

    # Write temp .fea file and apply
    fea_path = os.path.join(BUILD_DIR, "kern.fea")
    with open(fea_path, 'w') as f:
        f.write(fea_content)

    font = TTFont(ttf_path)
    addOpenTypeFeatures(font, fea_path)
    font.save(ttf_path)
    font.close()

    print(f"\n  Applied {len(KERN_PAIRS)} kern pairs via GPOS")
    print(f"  Feature file: {fea_path}")


def install_font(ttf_path):
    """Install font to ~/.local/share/fonts for system use."""
    import shutil
    dest_dir = os.path.expanduser("~/.local/share/fonts")
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, os.path.basename(ttf_path))
    shutil.copy2(ttf_path, dest)
    os.system("fc-cache -f")
    print(f"  Installed to: {dest}")


if __name__ == "__main__":
    print(f"Generating {FONT_FAMILY} {STYLE_NAME}...")
    print(f"SVG source: {SVG_DIR}")
    print()
    ttf_path = create_font()
    apply_kerning(ttf_path)
    install_font(ttf_path)
