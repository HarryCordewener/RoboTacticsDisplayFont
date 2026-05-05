#!/usr/bin/env python3
"""
Generate ASCII punctuation, digits, and symbols for RoboTacticsDisplay.
Draws glyphs programmatically using the font's design parameters.

Design params:
  - Stem angle: 75.78° from vertical (italic slant)
  - Stem width: 3.4 SVG units → scaled to font units
  - Serif angle: 40.1°
  - Gap width: 1.7 SVG units
  - x-height: 570, cap height: 700, UPM: 1000
  - Ascent: 800, Descent: 200

Strategy: construct paths in font units directly using fontforge pen.
"""

import fontforge
import math
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.join(SCRIPT_DIR, "build")

# Design parameters in font units
X_HEIGHT = 570
CAP_HEIGHT = 700
ASCENT = 800
DESCENT = 200
UPM = 1000

# Italic angle (font leans right)
ITALIC_ANGLE = 12  # degrees
ITALIC_SLANT = math.tan(math.radians(ITALIC_ANGLE))

# Stem width scaled to font units (3.4 SVG units, SVG height ~51 maps to 570)
SCALE = 570 / 51.0
STEM_W = 3.4 * SCALE  # ~38 units
THIN_W = STEM_W * 0.6  # for thin strokes
DOT_SIZE = STEM_W * 1.4  # dot diameter

# Sidebearing for symbols
SB = 20


def slant(x, y):
    """Apply italic slant to a point. Origin at baseline."""
    return (x + y * ITALIC_SLANT, y)


def draw_line(pen, x1, y1, x2, y2, thickness):
    """Draw a line segment with given thickness, applying italic slant."""
    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx*dx + dy*dy)
    if length < 0.01:
        return
    # Perpendicular offset
    nx = -dy / length * thickness / 2
    ny = dx / length * thickness / 2
    p1 = slant(x1 + nx, y1 + ny)
    p2 = slant(x1 - nx, y1 - ny)
    p3 = slant(x2 - nx, y2 - ny)
    p4 = slant(x2 + nx, y2 + ny)
    pen.moveTo(p1)
    pen.lineTo(p2)
    pen.lineTo(p3)
    pen.lineTo(p4)
    pen.closePath()


def draw_rect(pen, x, y, w, h):
    """Draw a slanted rectangle (parallelogram) with given bottom-left, width, height."""
    p1 = slant(x, y)
    p2 = slant(x + w, y)
    p3 = slant(x + w, y + h)
    p4 = slant(x, y + h)
    pen.moveTo(p1)
    pen.lineTo(p2)
    pen.lineTo(p3)
    pen.lineTo(p4)
    pen.closePath()


def draw_circle(pen, cx, cy, r, segments=12):
    """Draw an italic-slanted circle (ellipse approximation)."""
    points = []
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        px = cx + r * math.cos(angle)
        py = cy + r * math.sin(angle)
        points.append(slant(px, py))
    pen.moveTo(points[0])
    for p in points[1:]:
        pen.lineTo(p)
    pen.closePath()


def draw_oval(pen, cx, cy, rx, ry, segments=16):
    """Draw a slanted oval."""
    points = []
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        px = cx + rx * math.cos(angle)
        py = cy + ry * math.sin(angle)
        points.append(slant(px, py))
    pen.moveTo(points[0])
    for p in points[1:]:
        pen.lineTo(p)
    pen.closePath()


def draw_ring(pen, cx, cy, r_outer, r_inner, segments=16):
    """Draw a ring (circle with hole) - outer clockwise, inner counter-clockwise."""
    # Outer path (clockwise)
    points = []
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        px = cx + r_outer * math.cos(angle)
        py = cy + r_outer * math.sin(angle)
        points.append(slant(px, py))
    pen.moveTo(points[0])
    for p in points[1:]:
        pen.lineTo(p)
    pen.closePath()

    # Inner path (counter-clockwise = hole)
    points = []
    for i in range(segments - 1, -1, -1):
        angle = 2 * math.pi * i / segments
        px = cx + r_inner * math.cos(angle)
        py = cy + r_inner * math.sin(angle)
        points.append(slant(px, py))
    pen.moveTo(points[0])
    for p in points[1:]:
        pen.lineTo(p)
    pen.closePath()


def draw_oval_ring(pen, cx, cy, rx_o, ry_o, rx_i, ry_i, segments=20):
    """Draw an oval ring (oval with oval hole)."""
    # Outer (clockwise)
    points = []
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        px = cx + rx_o * math.cos(angle)
        py = cy + ry_o * math.sin(angle)
        points.append(slant(px, py))
    pen.moveTo(points[0])
    for p in points[1:]:
        pen.lineTo(p)
    pen.closePath()

    # Inner (counter-clockwise)
    points = []
    for i in range(segments - 1, -1, -1):
        angle = 2 * math.pi * i / segments
        px = cx + rx_i * math.cos(angle)
        py = cy + ry_i * math.sin(angle)
        points.append(slant(px, py))
    pen.moveTo(points[0])
    for p in points[1:]:
        pen.lineTo(p)
    pen.closePath()


def draw_half_oval_top(pen, cx, cy, rx, ry, thickness, segments=10):
    """Draw top half of an oval ring."""
    # Outer arc (0 to pi)
    outer = []
    for i in range(segments + 1):
        angle = math.pi * i / segments
        px = cx + rx * math.cos(angle)
        py = cy + ry * math.sin(angle)
        outer.append(slant(px, py))
    # Inner arc (pi to 0)
    inner = []
    rx_i = rx - thickness
    ry_i = ry - thickness
    for i in range(segments, -1, -1):
        angle = math.pi * i / segments
        px = cx + rx_i * math.cos(angle)
        py = cy + ry_i * math.sin(angle)
        inner.append(slant(px, py))
    pen.moveTo(outer[0])
    for p in outer[1:]:
        pen.lineTo(p)
    for p in inner:
        pen.lineTo(p)
    pen.closePath()


def draw_half_oval_bottom(pen, cx, cy, rx, ry, thickness, segments=10):
    """Draw bottom half of an oval ring."""
    # Outer arc (pi to 2pi)
    outer = []
    for i in range(segments + 1):
        angle = math.pi + math.pi * i / segments
        px = cx + rx * math.cos(angle)
        py = cy + ry * math.sin(angle)
        outer.append(slant(px, py))
    # Inner arc (2pi to pi)
    inner = []
    rx_i = rx - thickness
    ry_i = ry - thickness
    for i in range(segments, -1, -1):
        angle = math.pi + math.pi * i / segments
        px = cx + rx_i * math.cos(angle)
        py = cy + ry_i * math.sin(angle)
        inner.append(slant(px, py))
    pen.moveTo(outer[0])
    for p in outer[1:]:
        pen.lineTo(p)
    for p in inner:
        pen.lineTo(p)
    pen.closePath()


def draw_arc(pen, cx, cy, rx, ry, thickness, start_angle, end_angle, segments=10):
    """Draw an arc segment of an oval ring."""
    outer = []
    for i in range(segments + 1):
        angle = start_angle + (end_angle - start_angle) * i / segments
        px = cx + rx * math.cos(angle)
        py = cy + ry * math.sin(angle)
        outer.append(slant(px, py))
    inner = []
    rx_i = rx - thickness
    ry_i = ry - thickness
    for i in range(segments, -1, -1):
        angle = start_angle + (end_angle - start_angle) * i / segments
        px = cx + rx_i * math.cos(angle)
        py = cy + ry_i * math.sin(angle)
        inner.append(slant(px, py))
    pen.moveTo(outer[0])
    for p in outer[1:]:
        pen.lineTo(p)
    for p in inner:
        pen.lineTo(p)
    pen.closePath()


# ====== GLYPH DRAWING FUNCTIONS ======

def draw_digit_0(pen, w):
    """0 - narrow angular ring with diagonal slash"""
    cx = w / 2
    # Outer hexagonal shape (angular, not round)
    hw = w * 0.28  # half width
    hh = X_HEIGHT * 0.48  # half height
    cy = X_HEIGHT / 2
    flat = hh * 0.3  # flat top/bottom portion
    # Outer path
    p = [
        slant(cx - hw, cy - flat),
        slant(cx - hw * 0.6, cy - hh),
        slant(cx + hw * 0.6, cy + hh),
        slant(cx + hw, cy + flat),
        slant(cx + hw, cy - flat + hh*2 - flat*2),  # top right
    ]
    # Simpler: use a tall narrow diamond/hex
    # Outer (clockwise): bottom, bottom-right, top-right, top, top-left, bottom-left
    t = STEM_W
    out_pts = [
        slant(cx, cy - hh),          # bottom center
        slant(cx + hw, cy - flat),    # bottom right
        slant(cx + hw, cy + flat),    # top right
        slant(cx, cy + hh),           # top center
        slant(cx - hw, cy + flat),    # top left
        slant(cx - hw, cy - flat),    # bottom left
    ]
    pen.moveTo(out_pts[0])
    for p in out_pts[1:]:
        pen.lineTo(p)
    pen.closePath()
    # Inner (counter-clockwise = hole)
    inset = t
    hw_i = hw - inset
    hh_i = hh - inset
    flat_i = flat - inset * 0.3
    in_pts = [
        slant(cx - hw_i, cy - flat_i),
        slant(cx - hw_i, cy + flat_i),
        slant(cx, cy + hh_i),
        slant(cx + hw_i, cy + flat_i),
        slant(cx + hw_i, cy - flat_i),
        slant(cx, cy - hh_i),
    ]
    pen.moveTo(in_pts[0])
    for p in in_pts[1:]:
        pen.lineTo(p)
    pen.closePath()
    # Diagonal slash
    x1, y1 = cx + hw*0.15, cy + hh*0.6
    x2, y2 = cx - hw*0.15, cy - hh*0.6
    p1 = slant(x1, y1)
    p2 = slant(x1 + THIN_W*0.5, y1)
    p3 = slant(x2 + THIN_W*0.5, y2)
    p4 = slant(x2, y2)
    pen.moveTo(p1)
    pen.lineTo(p2)
    pen.lineTo(p3)
    pen.lineTo(p4)
    pen.closePath()
    return int(w)

def draw_digit_1(pen, w):
    """1 - vertical stem with base"""
    cx = w / 2
    # Main stem
    draw_rect(pen, cx - STEM_W/2, 0, STEM_W, X_HEIGHT)
    # Base
    draw_rect(pen, cx - w*0.25, 0, w*0.5, THIN_W)
    # Angled top serif
    x1, y1 = cx - STEM_W/2, X_HEIGHT - STEM_W
    x2, y2 = cx - w*0.3, X_HEIGHT * 0.7
    p1 = slant(x1, y1)
    p2 = slant(x1, y1 + THIN_W)
    p3 = slant(x2, y2 + THIN_W)
    p4 = slant(x2, y2)
    pen.moveTo(p1)
    pen.lineTo(p2)
    pen.lineTo(p3)
    pen.lineTo(p4)
    pen.closePath()
    return int(w)

def draw_digit_2(pen, w):
    """2 - angular: flat top, angled right side, diagonal, flat base"""
    cx = w / 2
    hw = w * 0.32
    # Top horizontal bar
    draw_rect(pen, cx - hw, X_HEIGHT - THIN_W, hw * 2, THIN_W)
    # Short right vertical from top bar down
    draw_rect(pen, cx + hw - STEM_W, X_HEIGHT * 0.55, STEM_W, X_HEIGHT * 0.45 - THIN_W)
    # Diagonal from mid-right to bottom-left
    x1, y1 = cx + hw - STEM_W, X_HEIGHT * 0.55
    x2, y2 = cx - hw, THIN_W
    p1 = slant(x1, y1)
    p2 = slant(x1 + STEM_W, y1)
    p3 = slant(x2 + STEM_W, y2)
    p4 = slant(x2, y2)
    pen.moveTo(p1)
    pen.lineTo(p2)
    pen.lineTo(p3)
    pen.lineTo(p4)
    pen.closePath()
    # Base horizontal bar
    draw_rect(pen, cx - hw, 0, hw * 2, THIN_W)
    return int(w)

def draw_digit_3(pen, w):
    """3 - angular: top bar, middle bar, bottom bar, right verticals"""
    cx = w / 2
    hw = w * 0.32
    # Top bar
    draw_rect(pen, cx - hw, X_HEIGHT - THIN_W, hw * 2, THIN_W)
    # Middle bar
    draw_rect(pen, cx - hw * 0.4, X_HEIGHT * 0.47, hw * 1.5, THIN_W)
    # Bottom bar
    draw_rect(pen, cx - hw, 0, hw * 2, THIN_W)
    # Right vertical top half
    draw_rect(pen, cx + hw - STEM_W, X_HEIGHT * 0.47 + THIN_W, STEM_W, X_HEIGHT * 0.53 - THIN_W * 2)
    # Right vertical bottom half
    draw_rect(pen, cx + hw - STEM_W, THIN_W, STEM_W, X_HEIGHT * 0.47 - THIN_W)
    return int(w)

def draw_digit_4(pen, w):
    """4 - angular: right stem, horizontal crossbar at 1/3, diagonal from top of stem to left end of bar"""
    cx = w / 2
    hw = w * 0.38
    # Right vertical stem — from baseline to top
    stem_x = cx + hw * 0.45
    draw_rect(pen, stem_x - STEM_W/2, 0, STEM_W, X_HEIGHT)
    # Horizontal crossbar at 1/3 height, extends well left of stem
    bar_y = X_HEIGHT * 0.33
    bar_left = cx - hw
    draw_rect(pen, bar_left, bar_y, stem_x - bar_left + STEM_W/2, STEM_W)
    # Diagonal leg: from top of stem down to left end of crossbar
    draw_line(pen, stem_x, X_HEIGHT, bar_left, bar_y + STEM_W, STEM_W * 0.85)
    return int(w)

def draw_digit_5(pen, w):
    """5 - angular: top bar, left vertical upper, middle bar, right vertical lower, bottom bar"""
    cx = w / 2
    hw = w * 0.32
    # Top horizontal bar
    draw_rect(pen, cx - hw, X_HEIGHT - THIN_W, hw * 2, THIN_W)
    # Left vertical (top to middle)
    draw_rect(pen, cx - hw, X_HEIGHT * 0.47, STEM_W, X_HEIGHT * 0.53 - THIN_W)
    # Middle bar
    draw_rect(pen, cx - hw, X_HEIGHT * 0.47, hw * 2, THIN_W)
    # Right vertical (middle to bottom)
    draw_rect(pen, cx + hw - STEM_W, THIN_W, STEM_W, X_HEIGHT * 0.47 - THIN_W)
    # Bottom bar
    draw_rect(pen, cx - hw, 0, hw * 2, THIN_W)
    return int(w)

def draw_digit_6(pen, w):
    """6 - angular: top bar, left vertical full, middle bar, right vertical lower, bottom bar"""
    cx = w / 2
    hw = w * 0.32
    # Top bar
    draw_rect(pen, cx - hw, X_HEIGHT - THIN_W, hw * 2, THIN_W)
    # Left vertical (full height)
    draw_rect(pen, cx - hw, 0, STEM_W, X_HEIGHT)
    # Middle bar
    draw_rect(pen, cx - hw, X_HEIGHT * 0.47, hw * 2, THIN_W)
    # Right vertical (bottom half only)
    draw_rect(pen, cx + hw - STEM_W, THIN_W, STEM_W, X_HEIGHT * 0.47 - THIN_W)
    # Bottom bar
    draw_rect(pen, cx - hw, 0, hw * 2, THIN_W)
    return int(w)

def draw_digit_7(pen, w):
    """7 - top bar + diagonal"""
    cx = w / 2
    # Top bar
    draw_rect(pen, cx - w*0.35, X_HEIGHT - THIN_W, w*0.7, THIN_W)
    # Diagonal
    x1, y1 = cx + w*0.25, X_HEIGHT - THIN_W
    x2, y2 = cx - w*0.1, 0
    p1 = slant(x1, y1)
    p2 = slant(x1 + STEM_W*0.7, y1)
    p3 = slant(x2 + STEM_W*0.7, y2)
    p4 = slant(x2, y2)
    pen.moveTo(p1)
    pen.lineTo(p2)
    pen.lineTo(p3)
    pen.lineTo(p4)
    pen.closePath()
    return int(w)

def draw_digit_8(pen, w):
    """8 - angular: two stacked rectangular loops sharing middle bar"""
    cx = w / 2
    hw = w * 0.30
    # Top box
    draw_rect(pen, cx - hw, X_HEIGHT - THIN_W, hw * 2, THIN_W)  # top
    draw_rect(pen, cx - hw, X_HEIGHT * 0.47 + THIN_W, STEM_W, X_HEIGHT * 0.53 - THIN_W * 2)  # left
    draw_rect(pen, cx + hw - STEM_W, X_HEIGHT * 0.47 + THIN_W, STEM_W, X_HEIGHT * 0.53 - THIN_W * 2)  # right
    # Middle bar
    draw_rect(pen, cx - hw, X_HEIGHT * 0.47, hw * 2, THIN_W)
    # Bottom box
    draw_rect(pen, cx - hw, THIN_W, STEM_W, X_HEIGHT * 0.47 - THIN_W)  # left
    draw_rect(pen, cx + hw - STEM_W, THIN_W, STEM_W, X_HEIGHT * 0.47 - THIN_W)  # right
    draw_rect(pen, cx - hw, 0, hw * 2, THIN_W)  # bottom
    return int(w)

def draw_digit_9(pen, w):
    """9 - angular: top bar, right vertical full, middle bar, left vertical upper, bottom bar"""
    cx = w / 2
    hw = w * 0.32
    # Top bar
    draw_rect(pen, cx - hw, X_HEIGHT - THIN_W, hw * 2, THIN_W)
    # Right vertical (full height)
    draw_rect(pen, cx + hw - STEM_W, 0, STEM_W, X_HEIGHT)
    # Middle bar
    draw_rect(pen, cx - hw, X_HEIGHT * 0.47, hw * 2, THIN_W)
    # Left vertical (top half only)
    draw_rect(pen, cx - hw, X_HEIGHT * 0.47 + THIN_W, STEM_W, X_HEIGHT * 0.53 - THIN_W * 2)
    # Bottom bar
    draw_rect(pen, cx - hw, 0, hw * 2, THIN_W)
    return int(w)

def draw_exclaim(pen, w):
    """! - vertical stroke + dot"""
    cx = w / 2
    # Stem
    draw_rect(pen, cx - STEM_W/2, DOT_SIZE * 1.8, STEM_W, X_HEIGHT - DOT_SIZE * 1.8)
    # Dot
    draw_circle(pen, cx, DOT_SIZE/2, DOT_SIZE/2)
    return int(w)

def draw_question(pen, w):
    """? - angular: top bar, right vertical, middle bar stub, vertical stem, dot"""
    cx = w / 2
    hw = w * 0.28
    # Top bar
    draw_rect(pen, cx - hw, X_HEIGHT - THIN_W, hw * 2, THIN_W)
    # Right vertical (top to mid)
    draw_rect(pen, cx + hw - STEM_W, X_HEIGHT * 0.55, STEM_W, X_HEIGHT * 0.45 - THIN_W)
    # Middle stub bar
    draw_rect(pen, cx - STEM_W/2, X_HEIGHT * 0.55, hw + STEM_W/2, THIN_W)
    # Short vertical stem below middle
    draw_rect(pen, cx - STEM_W/2, X_HEIGHT * 0.25, STEM_W, X_HEIGHT * 0.30)
    # Dot
    draw_circle(pen, cx, DOT_SIZE/2, DOT_SIZE/2)
    return int(w)

def draw_period(pen, w):
    """."""
    cx = w / 2
    draw_circle(pen, cx, DOT_SIZE/2, DOT_SIZE/2)
    return int(w)

def draw_comma(pen, w):
    ""","""
    cx = w / 2
    draw_circle(pen, cx, DOT_SIZE/2, DOT_SIZE/2)
    # Tail
    x1, y1 = cx, 0
    x2, y2 = cx - DOT_SIZE*0.5, -DOT_SIZE*1.2
    p1 = slant(x1 + THIN_W*0.4, y1)
    p2 = slant(x1 - THIN_W*0.4, y1)
    p3 = slant(x2, y2)
    p4 = slant(x2 + THIN_W*0.5, y2)
    pen.moveTo(p1)
    pen.lineTo(p2)
    pen.lineTo(p3)
    pen.lineTo(p4)
    pen.closePath()
    return int(w)

def draw_semicolon(pen, w):
    """;"""
    cx = w / 2
    # Top dot
    draw_circle(pen, cx, X_HEIGHT * 0.5, DOT_SIZE/2)
    # Bottom comma
    draw_circle(pen, cx, DOT_SIZE/2, DOT_SIZE/2)
    x1, y1 = cx, 0
    x2, y2 = cx - DOT_SIZE*0.5, -DOT_SIZE*1.2
    p1 = slant(x1 + THIN_W*0.4, y1)
    p2 = slant(x1 - THIN_W*0.4, y1)
    p3 = slant(x2, y2)
    p4 = slant(x2 + THIN_W*0.5, y2)
    pen.moveTo(p1)
    pen.lineTo(p2)
    pen.lineTo(p3)
    pen.lineTo(p4)
    pen.closePath()
    return int(w)

def draw_colon(pen, w):
    """:"""
    cx = w / 2
    draw_circle(pen, cx, X_HEIGHT * 0.5, DOT_SIZE/2)
    draw_circle(pen, cx, DOT_SIZE/2, DOT_SIZE/2)
    return int(w)

def draw_hyphen(pen, w):
    """-"""
    cx = w / 2
    draw_rect(pen, cx - w*0.3, X_HEIGHT*0.45, w*0.6, THIN_W)
    return int(w)

def draw_underscore(pen, w):
    """_"""
    cx = w / 2
    draw_rect(pen, cx - w*0.4, -DESCENT*0.3, w*0.8, THIN_W)
    return int(w)

def draw_equals(pen, w):
    """="""
    cx = w / 2
    gap = STEM_W * 1.2
    draw_rect(pen, cx - w*0.3, X_HEIGHT*0.45 + gap/2, w*0.6, THIN_W)
    draw_rect(pen, cx - w*0.3, X_HEIGHT*0.45 - gap/2 - THIN_W, w*0.6, THIN_W)
    return int(w)

def draw_plus(pen, w):
    """+"""
    cx = w / 2
    cy = X_HEIGHT * 0.45
    arm = w * 0.3
    # Horizontal
    draw_rect(pen, cx - arm, cy - THIN_W/2, arm*2, THIN_W)
    # Vertical
    draw_rect(pen, cx - THIN_W/2, cy - arm, THIN_W, arm*2)
    return int(w)

def draw_asterisk(pen, w):
    """*"""
    cx = w / 2
    cy = X_HEIGHT * 0.75
    arm = w * 0.22
    # 6 arms at 30° intervals
    for i in range(6):
        angle = math.pi * i / 6
        x1 = cx + arm * math.cos(angle)
        y1 = cy + arm * math.sin(angle)
        x2 = cx - arm * math.cos(angle)
        y2 = cy - arm * math.sin(angle)
        hw = THIN_W * 0.4
        perp = angle + math.pi/2
        dx = hw * math.cos(perp)
        dy = hw * math.sin(perp)
        p1 = slant(x1 + dx, y1 + dy)
        p2 = slant(x1 - dx, y1 - dy)
        p3 = slant(x2 - dx, y2 - dy)
        p4 = slant(x2 + dx, y2 + dy)
        pen.moveTo(p1)
        pen.lineTo(p2)
        pen.lineTo(p3)
        pen.lineTo(p4)
        pen.closePath()
    return int(w)

def draw_at(pen, w):
    """@ - angular: outer box with opening at bottom-right, inner angular 'a'"""
    cx = w / 2
    hw = w * 0.40
    hh = X_HEIGHT * 0.45
    cy = X_HEIGHT * 0.45
    # Outer box (open at bottom-right)
    # Top bar
    draw_rect(pen, cx - hw, cy + hh - THIN_W, hw * 2, THIN_W)
    # Left vertical
    draw_rect(pen, cx - hw, cy - hh, STEM_W, hh * 2)
    # Bottom bar (only left portion)
    draw_rect(pen, cx - hw, cy - hh, hw * 1.5, THIN_W)
    # Right vertical (top to mid only)
    draw_rect(pen, cx + hw - STEM_W, cy, STEM_W, hh)
    # Inner small box (the 'a' part)
    iw = hw * 0.45
    ih = hh * 0.5
    draw_rect(pen, cx - iw, cy - ih, iw * 2, THIN_W)  # bottom
    draw_rect(pen, cx - iw, cy + ih - THIN_W, iw * 2, THIN_W)  # top
    draw_rect(pen, cx - iw, cy - ih, STEM_W * 0.7, ih * 2)  # left
    draw_rect(pen, cx + iw - STEM_W * 0.7, cy - ih, STEM_W * 0.7, ih * 2)  # right
    return int(w)

def draw_hash(pen, w):
    """#"""
    cx = w / 2
    gap = w * 0.15
    # Two vertical strokes
    draw_rect(pen, cx - gap - THIN_W/2, X_HEIGHT*0.1, THIN_W, X_HEIGHT*0.8)
    draw_rect(pen, cx + gap - THIN_W/2, X_HEIGHT*0.1, THIN_W, X_HEIGHT*0.8)
    # Two horizontal strokes
    draw_rect(pen, cx - w*0.32, X_HEIGHT*0.55, w*0.64, THIN_W)
    draw_rect(pen, cx - w*0.32, X_HEIGHT*0.35, w*0.64, THIN_W)
    return int(w)

def draw_dollar(pen, w):
    """$ - angular S (like 5 but mirrored bottom) + vertical through-line"""
    cx = w / 2
    hw = w * 0.28
    # Vertical line through center
    draw_rect(pen, cx - THIN_W/2, -DESCENT*0.15, THIN_W, X_HEIGHT + DESCENT*0.3)
    # Top bar
    draw_rect(pen, cx - hw, X_HEIGHT - THIN_W, hw * 2, THIN_W)
    # Left vertical (top half)
    draw_rect(pen, cx - hw, X_HEIGHT * 0.47 + THIN_W, STEM_W, X_HEIGHT * 0.53 - THIN_W * 2)
    # Middle bar
    draw_rect(pen, cx - hw, X_HEIGHT * 0.47, hw * 2, THIN_W)
    # Right vertical (bottom half)
    draw_rect(pen, cx + hw - STEM_W, THIN_W, STEM_W, X_HEIGHT * 0.47 - THIN_W)
    # Bottom bar
    draw_rect(pen, cx - hw, 0, hw * 2, THIN_W)
    return int(w)

def draw_percent(pen, w):
    """%"""
    cx = w / 2
    # Top-left circle
    r = w * 0.12
    draw_ring(pen, cx - w*0.2, X_HEIGHT*0.75, r, r - THIN_W*0.7)
    # Bottom-right circle
    draw_ring(pen, cx + w*0.2, X_HEIGHT*0.25, r, r - THIN_W*0.7)
    # Diagonal
    x1, y1 = cx + w*0.3, X_HEIGHT*0.9
    x2, y2 = cx - w*0.3, X_HEIGHT*0.1
    p1 = slant(x1, y1)
    p2 = slant(x1 + THIN_W*0.5, y1)
    p3 = slant(x2 + THIN_W*0.5, y2)
    p4 = slant(x2, y2)
    pen.moveTo(p1)
    pen.lineTo(p2)
    pen.lineTo(p3)
    pen.lineTo(p4)
    pen.closePath()
    return int(w)

def draw_caret(pen, w):
    """^ - sharp angular chevron pointing up"""
    cx = w / 2
    cy = X_HEIGHT * 0.85
    arm = w * 0.28
    drop = arm * 0.7
    # Left arm
    x1, y1 = cx, cy
    x2, y2 = cx - arm, cy - drop
    p1 = slant(x1, y1)
    p2 = slant(x1 + THIN_W * 0.5, y1 - THIN_W * 0.5)
    p3 = slant(x2 + THIN_W * 0.5, y2 - THIN_W * 0.5)
    p4 = slant(x2, y2)
    pen.moveTo(p1)
    pen.lineTo(p2)
    pen.lineTo(p3)
    pen.lineTo(p4)
    pen.closePath()
    # Right arm
    x2, y2 = cx + arm, cy - drop
    p1 = slant(x1, y1)
    p2 = slant(x1 - THIN_W * 0.5, y1 - THIN_W * 0.5)
    p3 = slant(x2 - THIN_W * 0.5, y2 - THIN_W * 0.5)
    p4 = slant(x2, y2)
    pen.moveTo(p1)
    pen.lineTo(p2)
    pen.lineTo(p3)
    pen.lineTo(p4)
    pen.closePath()
    return int(w)

def draw_ampersand(pen, w):
    """& - two stacked diamonds (rotated squares) + V-tail extending right.
    Upper diamond smaller and higher, lower diamond larger, tail forms a V from right vertex."""
    cx = w / 2
    t = STEM_W * 0.8
    # Upper diamond — small, high, centered
    ud_cx = cx - w * 0.02
    ud_cy = X_HEIGHT * 0.78
    ud_r = X_HEIGHT * 0.17
    draw_line(pen, ud_cx, ud_cy + ud_r, ud_cx - ud_r, ud_cy, t)
    draw_line(pen, ud_cx - ud_r, ud_cy, ud_cx, ud_cy - ud_r, t)
    draw_line(pen, ud_cx, ud_cy - ud_r, ud_cx + ud_r, ud_cy, t)
    draw_line(pen, ud_cx + ud_r, ud_cy, ud_cx, ud_cy + ud_r, t)
    # Lower diamond — larger, slightly left
    ld_cx = cx - w * 0.06
    ld_cy = X_HEIGHT * 0.30
    ld_r = X_HEIGHT * 0.27
    draw_line(pen, ld_cx, ld_cy + ld_r, ld_cx - ld_r, ld_cy, t)
    draw_line(pen, ld_cx - ld_r, ld_cy, ld_cx, ld_cy - ld_r, t)
    draw_line(pen, ld_cx, ld_cy - ld_r, ld_cx + ld_r, ld_cy, t)
    draw_line(pen, ld_cx + ld_r, ld_cy, ld_cx, ld_cy + ld_r, t)
    # V-tail from lower diamond's right vertex — extends further right
    tail_x = ld_cx + ld_r
    tail_y = ld_cy
    draw_line(pen, tail_x, tail_y, w * 0.88, tail_y + X_HEIGHT * 0.28, t)
    draw_line(pen, tail_x, tail_y, w * 0.88, tail_y - X_HEIGHT * 0.22, t)
    return int(w)

def draw_tilde(pen, w):
    """~"""
    cx = w / 2
    cy = X_HEIGHT * 0.55
    amp = X_HEIGHT * 0.06
    # Approximate with two arcs
    segments = 12
    points_top = []
    points_bot = []
    for i in range(segments + 1):
        t = i / segments
        x = cx - w*0.3 + w*0.6 * t
        y = cy + amp * math.sin(t * 2 * math.pi)
        points_top.append(slant(x, y + THIN_W/2))
        points_bot.append(slant(x, y - THIN_W/2))
    pen.moveTo(points_top[0])
    for p in points_top[1:]:
        pen.lineTo(p)
    for p in reversed(points_bot):
        pen.lineTo(p)
    pen.closePath()
    return int(w)

def draw_paren_left(pen, w):
    """("""
    cx = w * 0.65
    draw_arc(pen, cx, X_HEIGHT*0.45, w*0.5, X_HEIGHT*0.55, STEM_W*0.8, math.radians(130), math.radians(230))
    return int(w)

def draw_paren_right(pen, w):
    """)"""
    cx = w * 0.35
    draw_arc(pen, cx, X_HEIGHT*0.45, w*0.5, X_HEIGHT*0.55, STEM_W*0.8, math.radians(-50), math.radians(50))
    return int(w)

def draw_bracket_left(pen, w):
    """["""
    cx = w / 2
    x = cx - w*0.1
    # Vertical
    draw_rect(pen, x, -DESCENT*0.3, STEM_W*0.8, X_HEIGHT + DESCENT*0.3 + ASCENT*0.05)
    # Top bar
    draw_rect(pen, x, X_HEIGHT + ASCENT*0.02, w*0.35, THIN_W)
    # Bottom bar
    draw_rect(pen, x, -DESCENT*0.3, w*0.35, THIN_W)
    return int(w)

def draw_bracket_right(pen, w):
    """]"""
    cx = w / 2
    x = cx + w*0.1 - STEM_W*0.8
    draw_rect(pen, x, -DESCENT*0.3, STEM_W*0.8, X_HEIGHT + DESCENT*0.3 + ASCENT*0.05)
    draw_rect(pen, x - w*0.25, X_HEIGHT + ASCENT*0.02, w*0.35, THIN_W)
    draw_rect(pen, x - w*0.25, -DESCENT*0.3, w*0.35, THIN_W)
    return int(w)

def draw_brace_left(pen, w):
    """{  - angular: vertical with angled middle point and top/bottom bars"""
    cx = w / 2
    mid_y = X_HEIGHT * 0.5
    # Top horizontal stub
    draw_rect(pen, cx, X_HEIGHT - THIN_W, w * 0.25, THIN_W)
    # Upper vertical
    draw_rect(pen, cx - STEM_W * 0.4, mid_y + THIN_W, STEM_W * 0.8, X_HEIGHT * 0.5 - THIN_W * 2)
    # Middle point (chevron left)
    px = cx - w * 0.2
    p1 = slant(cx - STEM_W * 0.4, mid_y + THIN_W)
    p2 = slant(cx + STEM_W * 0.4, mid_y + THIN_W)
    p3 = slant(px + STEM_W * 0.4, mid_y)
    p4 = slant(px - STEM_W * 0.4, mid_y)
    p5 = slant(cx - STEM_W * 0.4, mid_y - THIN_W)
    p6 = slant(cx + STEM_W * 0.4, mid_y - THIN_W)
    pen.moveTo(p2)
    pen.lineTo(p3)
    pen.lineTo(p5)
    pen.closePath()
    pen.moveTo(p1)
    pen.lineTo(p4)
    pen.lineTo(p6)
    pen.closePath()
    # Lower vertical
    draw_rect(pen, cx - STEM_W * 0.4, THIN_W, STEM_W * 0.8, X_HEIGHT * 0.5 - THIN_W * 2)
    # Bottom horizontal stub
    draw_rect(pen, cx, 0, w * 0.25, THIN_W)
    return int(w)

def draw_brace_right(pen, w):
    """}  - angular: vertical with angled middle point and top/bottom bars"""
    cx = w / 2
    mid_y = X_HEIGHT * 0.5
    # Top horizontal stub
    draw_rect(pen, cx - w * 0.25, X_HEIGHT - THIN_W, w * 0.25, THIN_W)
    # Upper vertical
    draw_rect(pen, cx - STEM_W * 0.4, mid_y + THIN_W, STEM_W * 0.8, X_HEIGHT * 0.5 - THIN_W * 2)
    # Middle point (chevron right)
    px = cx + w * 0.2
    p1 = slant(cx - STEM_W * 0.4, mid_y + THIN_W)
    p2 = slant(cx + STEM_W * 0.4, mid_y + THIN_W)
    p3 = slant(px + STEM_W * 0.4, mid_y)
    p4 = slant(px - STEM_W * 0.4, mid_y)
    p5 = slant(cx - STEM_W * 0.4, mid_y - THIN_W)
    p6 = slant(cx + STEM_W * 0.4, mid_y - THIN_W)
    pen.moveTo(p1)
    pen.lineTo(p4)
    pen.lineTo(p6)
    pen.closePath()
    pen.moveTo(p2)
    pen.lineTo(p3)
    pen.lineTo(p5)
    pen.closePath()
    # Lower vertical
    draw_rect(pen, cx - STEM_W * 0.4, THIN_W, STEM_W * 0.8, X_HEIGHT * 0.5 - THIN_W * 2)
    # Bottom horizontal stub
    draw_rect(pen, cx - w * 0.25, 0, w * 0.25, THIN_W)
    return int(w)

def draw_slash(pen, w):
    """/"""
    cx = w / 2
    x1, y1 = cx + w*0.25, X_HEIGHT
    x2, y2 = cx - w*0.25, 0
    p1 = slant(x1, y1)
    p2 = slant(x1 + THIN_W*0.7, y1)
    p3 = slant(x2 + THIN_W*0.7, y2)
    p4 = slant(x2, y2)
    pen.moveTo(p1)
    pen.lineTo(p2)
    pen.lineTo(p3)
    pen.lineTo(p4)
    pen.closePath()
    return int(w)

def draw_backslash(pen, w):
    """\\"""
    cx = w / 2
    # Need steeper diagonal to overcome italic slant
    x1, y1 = cx - w*0.35, X_HEIGHT
    x2, y2 = cx + w*0.35, 0
    p1 = slant(x1, y1)
    p2 = slant(x1 + THIN_W*0.7, y1)
    p3 = slant(x2 + THIN_W*0.7, y2)
    p4 = slant(x2, y2)
    pen.moveTo(p1)
    pen.lineTo(p2)
    pen.lineTo(p3)
    pen.lineTo(p4)
    pen.closePath()
    return int(w)

def draw_pipe(pen, w):
    """|"""
    cx = w / 2
    draw_rect(pen, cx - THIN_W/2, -DESCENT*0.3, THIN_W, X_HEIGHT + DESCENT*0.6)
    return int(w)

def draw_quote_single(pen, w):
    """'"""
    cx = w / 2
    draw_rect(pen, cx - THIN_W/2, X_HEIGHT*0.65, THIN_W, X_HEIGHT*0.3)
    return int(w)

def draw_quote_double(pen, w):
    '''"'''
    cx = w / 2
    gap = STEM_W * 1.0
    draw_rect(pen, cx - gap/2 - THIN_W, X_HEIGHT*0.65, THIN_W, X_HEIGHT*0.3)
    draw_rect(pen, cx + gap/2, X_HEIGHT*0.65, THIN_W, X_HEIGHT*0.3)
    return int(w)

def draw_backtick(pen, w):
    """`"""
    cx = w / 2
    x1, y1 = cx - THIN_W, X_HEIGHT * 0.95
    x2, y2 = cx + THIN_W*0.5, X_HEIGHT * 0.7
    p1 = slant(x1, y1)
    p2 = slant(x1 + THIN_W*0.6, y1)
    p3 = slant(x2 + THIN_W*0.6, y2)
    p4 = slant(x2, y2)
    pen.moveTo(p1)
    pen.lineTo(p2)
    pen.lineTo(p3)
    pen.lineTo(p4)
    pen.closePath()
    return int(w)

def draw_less_than(pen, w):
    """<"""
    cx = w / 2
    cy = X_HEIGHT * 0.45
    # Top arm
    x1, y1 = cx + w*0.28, cy + X_HEIGHT*0.25
    x2, y2 = cx - w*0.28, cy
    p1 = slant(x1, y1)
    p2 = slant(x1, y1 - THIN_W)
    p3 = slant(x2, y2 - THIN_W/2)
    p4 = slant(x2, y2 + THIN_W/2)
    pen.moveTo(p1)
    pen.lineTo(p2)
    pen.lineTo(p3)
    pen.lineTo(p4)
    pen.closePath()
    # Bottom arm
    x1, y1 = cx + w*0.28, cy - X_HEIGHT*0.25
    p1 = slant(x1, y1)
    p2 = slant(x1, y1 + THIN_W)
    p3 = slant(x2, y2 + THIN_W/2)
    p4 = slant(x2, y2 - THIN_W/2)
    pen.moveTo(p1)
    pen.lineTo(p2)
    pen.lineTo(p3)
    pen.lineTo(p4)
    pen.closePath()
    return int(w)

def draw_greater_than(pen, w):
    """>"""
    cx = w / 2
    cy = X_HEIGHT * 0.45
    x2 = cx + w*0.28
    x1 = cx - w*0.28
    # Top arm
    y1 = cy + X_HEIGHT*0.25
    p1 = slant(x1, y1)
    p2 = slant(x1, y1 - THIN_W)
    p3 = slant(x2, cy - THIN_W/2)
    p4 = slant(x2, cy + THIN_W/2)
    pen.moveTo(p1)
    pen.lineTo(p2)
    pen.lineTo(p3)
    pen.lineTo(p4)
    pen.closePath()
    # Bottom arm
    y1 = cy - X_HEIGHT*0.25
    p1 = slant(x1, y1)
    p2 = slant(x1, y1 + THIN_W)
    p3 = slant(x2, cy + THIN_W/2)
    p4 = slant(x2, cy - THIN_W/2)
    pen.moveTo(p1)
    pen.lineTo(p2)
    pen.lineTo(p3)
    pen.lineTo(p4)
    pen.closePath()
    return int(w)


# ====== GLYPH REGISTRY ======

# (codepoint, name, draw_function, width)
SYMBOL_GLYPHS = [
    # Digits
    (ord('0'), 'zero', draw_digit_0, 340),
    (ord('1'), 'one', draw_digit_1, 260),
    (ord('2'), 'two', draw_digit_2, 320),
    (ord('3'), 'three', draw_digit_3, 320),
    (ord('4'), 'four', draw_digit_4, 340),
    (ord('5'), 'five', draw_digit_5, 320),
    (ord('6'), 'six', draw_digit_6, 320),
    (ord('7'), 'seven', draw_digit_7, 320),
    (ord('8'), 'eight', draw_digit_8, 320),
    (ord('9'), 'nine', draw_digit_9, 320),
    # Punctuation
    (ord('!'), 'exclam', draw_exclaim, 180),
    (ord('?'), 'question', draw_question, 300),
    (ord('.'), 'period', draw_period, 160),
    (ord(','), 'comma', draw_comma, 160),
    (ord(';'), 'semicolon', draw_semicolon, 170),
    (ord(':'), 'colon', draw_colon, 160),
    (ord('-'), 'hyphen', draw_hyphen, 240),
    (ord('_'), 'underscore', draw_underscore, 320),
    (ord('='), 'equal', draw_equals, 300),
    (ord('+'), 'plus', draw_plus, 300),
    (ord('*'), 'asterisk', draw_asterisk, 260),
    (ord('@'), 'at', draw_at, 420),
    (ord('#'), 'numbersign', draw_hash, 340),
    (ord('$'), 'dollar', draw_dollar, 320),
    (ord('%'), 'percent', draw_percent, 380),
    (ord('^'), 'asciicircum', draw_caret, 280),
    (ord('&'), 'ampersand', draw_ampersand, 440),
    (ord('~'), 'asciitilde', draw_tilde, 300),
    (ord('('), 'parenleft', draw_paren_left, 200),
    (ord(')'), 'parenright', draw_paren_right, 200),
    (ord('['), 'bracketleft', draw_bracket_left, 200),
    (ord(']'), 'bracketright', draw_bracket_right, 200),
    (ord('{'), 'braceleft', draw_brace_left, 220),
    (ord('}'), 'braceright', draw_brace_right, 220),
    (ord('/'), 'slash', draw_slash, 240),
    (ord('\\'), 'backslash', draw_backslash, 240),
    (ord('|'), 'bar', draw_pipe, 180),
    (ord("'"), 'quotesingle', draw_quote_single, 140),
    (ord('"'), 'quotedbl', draw_quote_double, 220),
    (ord('`'), 'grave', draw_backtick, 200),
    (ord('<'), 'less', draw_less_than, 280),
    (ord('>'), 'greater', draw_greater_than, 280),
]


def add_symbols_to_font(font_path):
    """Open the generated font and add symbol glyphs."""
    import fontforge
    font = fontforge.open(font_path)

    for codepoint, name, draw_fn, width in SYMBOL_GLYPHS:
        glyph = font.createChar(codepoint, name)
        glyph.clear()
        pen = glyph.glyphPen()
        draw_fn(pen, width)
        pen = None  # finalize
        glyph.width = width
        print(f"  Drew {chr(codepoint)} ({name}) width={width}")

    # Re-generate
    font.generate(font_path)
    print(f"\n  Saved: {font_path}")
    font.close()


if __name__ == "__main__":
    ttf_path = os.path.join(BUILD_DIR, "RoboTacticsDisplay-ThinItalic.ttf")
    if not os.path.exists(ttf_path):
        print(f"ERROR: {ttf_path} not found. Run generate_font.py first.")
        sys.exit(1)
    print("Adding symbols and digits...")
    add_symbols_to_font(ttf_path)

    # Also install
    import shutil
    dest = os.path.expanduser("~/.local/share/fonts/RoboTacticsDisplay-ThinItalic.ttf")
    shutil.copy2(ttf_path, dest)
    os.system("fc-cache -f")
    print(f"  Installed to: {dest}")
