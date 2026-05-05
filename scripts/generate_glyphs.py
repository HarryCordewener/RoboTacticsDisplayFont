#!/usr/bin/env python3
"""Generate glyphs.svg — a visual table of all supported characters."""

import base64
import os

FONT_PATH = os.path.join(os.path.dirname(__file__), '..', 'build', 'RoboTacticsDisplay-ThinItalic.ttf')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'glyphs.svg')


def get_font_b64():
    with open(FONT_PATH, 'rb') as f:
        return base64.b64encode(f.read()).decode()


def make_rows(chars, cols):
    return [chars[i:i+cols] for i in range(0, len(chars), cols)]


def table_section(title, chars, y_start, cols=13):
    cell_w, cell_h, header_h = 58, 52, 30
    svg = f'<text x="10" y="{y_start + 18}" class="header">{title}</text>\n'
    y_start += header_h
    rows = make_rows(chars, cols)
    for ri, row in enumerate(rows):
        for ci, ch in enumerate(row):
            x = 10 + ci * cell_w
            y = y_start + ri * cell_h
            svg += f'<rect x="{x}" y="{y}" width="{cell_w-2}" height="{cell_h-2}" class="cell"/>\n'
            display = ch.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
            svg += f'<text x="{x + cell_w//2 - 1}" y="{y + 36}" class="glyph">{display}</text>\n'
    return svg, y_start + len(rows) * cell_h


def main():
    font_b64 = get_font_b64()
    cols = 13

    uppercase = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    lowercase = list("abcdefghijklmnopqrstuvwxyz")
    digits = list("0123456789")
    symbols = list("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")

    y = 10
    sections = []
    s, y = table_section("Uppercase", uppercase, y, cols)
    sections.append(s)
    s, y = table_section("Lowercase", lowercase, y + 10, cols)
    sections.append(s)
    s, y = table_section("Digits", digits, y + 10, 10)
    sections.append(s)
    s, y = table_section("Symbols", symbols, y + 10, cols)
    sections.append(s)

    total_w = 10 + cols * 58 + 10
    total_h = y + 10

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_w} {total_h}" width="{total_w}" height="{total_h}">
<defs>
<style>
@font-face {{
  font-family: 'RoboTacticsDisplay';
  font-weight: 100;
  font-style: italic;
  src: url('data:font/ttf;base64,{font_b64}') format('truetype');
}}
.glyph {{
  font-family: 'RoboTacticsDisplay', sans-serif;
  font-weight: 100;
  font-style: italic;
  font-size: 32px;
  fill: #e0e0e0;
  text-anchor: middle;
}}
.header {{
  font-family: sans-serif;
  font-size: 14px;
  fill: #888;
  font-weight: bold;
}}
.cell {{
  fill: #1a1a2e;
  stroke: #333;
  stroke-width: 1;
  rx: 4;
}}
rect.bg {{
  fill: #0d0d1a;
}}
</style>
</defs>
<rect class="bg" width="100%" height="100%"/>
{chr(10).join(sections)}
</svg>'''

    with open(OUTPUT_PATH, 'w') as f:
        f.write(svg)
    print(f"Written {OUTPUT_PATH} ({total_w}x{total_h})")


if __name__ == '__main__':
    main()
