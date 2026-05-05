#!/usr/bin/env python3
"""Generate logo.svg for RoboTacticsDisplay font."""
import base64
import os
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
FONT_PATH = os.path.join(REPO_ROOT, "build", "RoboTacticsDisplay-ThinItalic.ttf")
SVG_OUT = os.path.join(REPO_ROOT, "logo.svg")
PNG_OUT = os.path.join(REPO_ROOT, "logo.png")

TEXT = "Super robo fontS"


def generate_svg():
    with open(FONT_PATH, "rb") as f:
        font_b64 = base64.b64encode(f.read()).decode()

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="415 -60 390 340">
  <defs>
    <style>
      @font-face {{
        font-family: "Robo Tactics Display";
        font-style: italic;
        font-weight: 100;
        src: url("data:font/ttf;base64,{font_b64}");
      }}
    </style>

    <linearGradient id="goldGrad" gradientUnits="userSpaceOnUse" x1="0" y1="100" x2="0" y2="220">
      <stop offset="0%" stop-color="#fffff0"/>
      <stop offset="5%" stop-color="#fff8cc"/>
      <stop offset="12%" stop-color="#f0d860"/>
      <stop offset="22%" stop-color="#e0b830"/>
      <stop offset="32%" stop-color="#c89010"/>
      <stop offset="42%" stop-color="#a06800"/>
      <stop offset="46%" stop-color="#e0c040"/>
      <stop offset="50%" stop-color="#f0d860"/>
      <stop offset="58%" stop-color="#d4a820"/>
      <stop offset="68%" stop-color="#b07808"/>
      <stop offset="78%" stop-color="#8a5500"/>
      <stop offset="88%" stop-color="#6a3800"/>
      <stop offset="100%" stop-color="#4a2200"/>
    </linearGradient>

    <linearGradient id="silverGrad" gradientUnits="userSpaceOnUse" x1="0" y1="100" x2="0" y2="220">
      <stop offset="0%" stop-color="#f0f0ff"/>
      <stop offset="15%" stop-color="#d0d0e0"/>
      <stop offset="35%" stop-color="#b0b0c0"/>
      <stop offset="50%" stop-color="#a0a0a8"/>
      <stop offset="65%" stop-color="#b0b0c0"/>
      <stop offset="85%" stop-color="#d0d0e0"/>
      <stop offset="100%" stop-color="#f0f0ff"/>
    </linearGradient>

    <pattern id="stripes" patternUnits="userSpaceOnUse" x="0" y="0" width="1200" height="3.2">
      <rect x="0" y="0" width="1200" height="1.6" fill="rgba(0,0,0,0.4)"/>
    </pattern>

    <filter id="goldGlow" x="-15%" y="-15%" width="130%" height="130%">
      <feGaussianBlur stdDeviation="1.5" result="blur"/>
      <feFlood flood-color="rgba(255,200,60,0.6)" result="color"/>
      <feComposite in="color" in2="blur" operator="in" result="glow"/>
      <feMerge>
        <feMergeNode in="glow"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <linearGradient id="specGrad" gradientUnits="userSpaceOnUse" x1="0" y1="100" x2="0" y2="220">
      <stop offset="0%" stop-color="white" stop-opacity="0"/>
      <stop offset="30%" stop-color="white" stop-opacity="0"/>
      <stop offset="42%" stop-color="white" stop-opacity="0.25"/>
      <stop offset="47%" stop-color="white" stop-opacity="0.4"/>
      <stop offset="52%" stop-color="white" stop-opacity="0.25"/>
      <stop offset="60%" stop-color="white" stop-opacity="0"/>
      <stop offset="100%" stop-color="white" stop-opacity="0"/>
    </linearGradient>

    <linearGradient id="redAccent" gradientUnits="userSpaceOnUse" x1="0" y1="100" x2="0" y2="220">
      <stop offset="0%" stop-color="#ff4444" stop-opacity="0"/>
      <stop offset="85%" stop-color="#cc2200" stop-opacity="0"/>
      <stop offset="95%" stop-color="#ff3300" stop-opacity="0.4"/>
      <stop offset="100%" stop-color="#ff6600" stop-opacity="0.3"/>
    </linearGradient>
  </defs>

  <g>
    <text x="600" y="190" text-anchor="middle" font-family="Robo Tactics Display" font-style="italic" font-weight="100" font-size="140" letter-spacing="-21" fill="none" stroke="url(#silverGrad)" stroke-width="26" stroke-linejoin="miter">{TEXT}</text>
    <text x="600" y="190" text-anchor="middle" font-family="Robo Tactics Display" font-style="italic" font-weight="100" font-size="140" letter-spacing="-21" fill="#020204" stroke="#020204" stroke-width="23" stroke-linejoin="miter">{TEXT}</text>
    <text x="600" y="190" text-anchor="middle" font-family="Robo Tactics Display" font-style="italic" font-weight="100" font-size="140" letter-spacing="-21" fill="rgb(80,35,5)" dx="1.3" dy="1.8">{TEXT}</text>
    <text x="600" y="190" text-anchor="middle" font-family="Robo Tactics Display" font-style="italic" font-weight="100" font-size="140" letter-spacing="-21" fill="rgb(100,50,12)" dx="0.9" dy="1.2">{TEXT}</text>
    <text x="600" y="190" text-anchor="middle" font-family="Robo Tactics Display" font-style="italic" font-weight="100" font-size="140" letter-spacing="-21" fill="rgb(130,70,20)" dx="0.45" dy="0.65">{TEXT}</text>
    <text x="600" y="190" text-anchor="middle" font-family="Robo Tactics Display" font-style="italic" font-weight="100" font-size="140" letter-spacing="-21" fill="url(#goldGrad)" filter="url(#goldGlow)">{TEXT}</text>
    <text x="600" y="190" text-anchor="middle" font-family="Robo Tactics Display" font-style="italic" font-weight="100" font-size="140" letter-spacing="-21" fill="url(#stripes)">{TEXT}</text>
    <text x="600" y="190" text-anchor="middle" font-family="Robo Tactics Display" font-style="italic" font-weight="100" font-size="140" letter-spacing="-21" fill="url(#specGrad)" opacity="0.7">{TEXT}</text>
    <text x="600" y="190" text-anchor="middle" font-family="Robo Tactics Display" font-style="italic" font-weight="100" font-size="140" letter-spacing="-21" fill="url(#redAccent)" opacity="0.5">{TEXT}</text>
  </g>
</svg>'''

    with open(SVG_OUT, "w") as f:
        f.write(svg)
    print(f"Generated {SVG_OUT}")


def generate_png():
    """Convert SVG to PNG using rsvg-convert or Inkscape."""
    try:
        subprocess.run(
            ["rsvg-convert", "-w", "1200", "-b", "transparent", SVG_OUT, "-o", PNG_OUT],
            check=True,
        )
    except FileNotFoundError:
        subprocess.run(
            ["inkscape", SVG_OUT, "--export-type=png", f"--export-filename={PNG_OUT}",
             "--export-width=1200", "--export-background-opacity=0"],
            check=True,
        )
    print(f"Generated {PNG_OUT}")


if __name__ == "__main__":
    generate_svg()
    generate_png()
