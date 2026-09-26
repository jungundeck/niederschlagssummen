#!/usr/bin/env python3
"""Erzeugt das App-Icon: stilisierte Karte, Radar-Kacheln in der Kurzzeit-Farbskala, Steinpilz.

    python3 tools/make_icon.py

Schreibt site/icon.svg und rendert daraus (per Chrome headless + Pillow) die PNG-Größen:
apple-touch-icon.png (180), icon-192.png, icon-512.png, icon-maskable-512.png.
"""
import math
import random
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

SITE = Path(__file__).resolve().parent.parent / "site"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Kurzzeit-Farbskala der Karte (Auswahl)
SCALE = ["#d4eece", "#b5e2c1", "#8fd2c4", "#66c0c8", "#43a8c8", "#2b8cbe", "#1f6aa8", "#2d2a7a", "#4b1d78"]


def radar_tiles(size=512, tile=32):
    """Kacheln eines 'Regengebiets' oben rechts, mit ausgefranstem Rand."""
    rnd = random.Random(7)
    out = []
    cx, cy = 440, 50
    for ty in range(size // tile):
        for tx in range(size // tile):
            x, y = tx * tile + tile / 2, ty * tile + tile / 2
            d = math.hypot((x - cx) * 0.9, (y - cy) * 1.25)
            v = 1 - d / 340 + rnd.uniform(-0.12, 0.12)
            if v <= 0.08:
                continue
            c = SCALE[min(int(v * len(SCALE) * 1.15), len(SCALE) - 1)]
            out.append(f'<rect x="{tx * tile + 1}" y="{ty * tile + 1}" width="{tile - 2}" height="{tile - 2}" '
                       f'rx="3" fill="{c}"/>')
    return "\n    ".join(out)


def svg():
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <radialGradient id="cap" cx="0.36" cy="0.28" r="0.85">
      <stop offset="0" stop-color="#c98a52"/>
      <stop offset="0.45" stop-color="#9a5a2c"/>
      <stop offset="0.85" stop-color="#6e3a1a"/>
      <stop offset="1" stop-color="#5a2e14"/>
    </radialGradient>
    <linearGradient id="pores" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#e9dca0"/>
      <stop offset="1" stop-color="#c9b064"/>
    </linearGradient>
    <linearGradient id="stem" x1="0" x2="1">
      <stop offset="0" stop-color="#fffaf0"/>
      <stop offset="0.55" stop-color="#f0e6cf"/>
      <stop offset="1" stop-color="#cbb991"/>
    </linearGradient>
    <linearGradient id="stemshade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#7a5a2a" stop-opacity="0.35"/>
      <stop offset="0.25" stop-color="#7a5a2a" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="moss" cx="0.5" cy="0.2" r="0.8">
      <stop offset="0" stop-color="#8fbf4f"/>
      <stop offset="1" stop-color="#4f7d2a"/>
    </radialGradient>
    <filter id="soft" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="10"/>
    </filter>
    <clipPath id="stemclip">
      <path d="M222 270 C216 316 186 342 186 392 C186 428 220 444 256 444 C292 444 326 428 326 392
               C326 342 296 316 290 270 Z"/>
    </clipPath>
  </defs>

  <!-- Karte -->
  <rect width="512" height="512" fill="#efe9da"/>
  <path d="M-10 120 C60 90 110 150 60 210 C20 260 70 300 20 360 L-10 380 Z" fill="#cfe2b3"/>
  <path d="M380 330 C440 300 520 330 520 330 L520 520 L330 520 C360 470 330 380 380 330 Z" fill="#cfe2b3"/>
  <path d="M180 -10 C170 40 230 60 220 110 L150 110 C140 60 120 20 130 -10 Z" fill="#dbe8c4"/>
  <path d="M-20 450 C80 400 140 470 230 440 S380 380 530 420" fill="none" stroke="#8ec5e8" stroke-width="22"
        stroke-linecap="round"/>
  <path d="M40 -20 C90 120 60 260 150 330 S330 380 360 530" fill="none" stroke="#e8b24a" stroke-width="15"/>
  <path d="M40 -20 C90 120 60 260 150 330 S330 380 360 530" fill="none" stroke="#fff6df" stroke-width="8"/>
  <path d="M-20 250 C120 240 300 220 530 150" fill="none" stroke="#fff" stroke-width="9"/>
  <path d="M300 -20 C290 80 330 150 300 230" fill="none" stroke="#fff" stroke-width="7"/>

  <!-- Radar-Kacheln -->
  <g opacity="0.78">
    {radar_tiles()}
  </g>

  <!-- Steinpilz im Emoji-Stil, verkleinert unten links -->
  <g transform="translate(-44 206) scale(0.6)">
    <ellipse cx="256" cy="452" rx="150" ry="26" fill="#3b2a14" opacity="0.28" filter="url(#soft)"/>
    <!-- Moospolster -->
    <path d="M110 452 C130 408 190 396 256 398 C322 396 382 408 402 452 C350 470 162 470 110 452 Z" fill="url(#moss)"/>
    <!-- Stiel -->
    <path d="M222 270 C216 316 186 342 186 392 C186 428 220 444 256 444 C292 444 326 428 326 392
             C326 342 296 316 290 270 Z" fill="url(#stem)"/>
    <g clip-path="url(#stemclip)">
      <rect x="190" y="262" width="132" height="190" fill="url(#stemshade)"/>
      <path d="M232 300 C240 296 250 302 258 298 M236 318 C246 314 256 320 266 316 M240 336 C250 332 262 338 272 334"
            fill="none" stroke="#c8b284" stroke-width="2.5" stroke-linecap="round" opacity="0.7"/>
    </g>
    <!-- Moos vor dem Stielfuß -->
    <path d="M176 446 C196 420 226 420 238 432 C250 418 276 418 288 432 C300 420 326 422 336 446
             C300 458 212 458 176 446 Z" fill="#6fa23c"/>
    <!-- Hut -->
    <path d="M142 268 C162 292 350 292 370 268 C350 280 162 280 142 268 Z" fill="url(#pores)"/>
    <path d="M142 268 C126 196 180 140 256 138 C332 140 386 196 370 268 C334 284 178 284 142 268 Z" fill="url(#cap)"/>
    <path d="M150 262 C190 276 322 276 362 262" fill="none" stroke="#b77a45" stroke-width="4"
          stroke-linecap="round" opacity="0.7"/>
    <ellipse cx="212" cy="178" rx="40" ry="18" fill="#fff" opacity="0.28" transform="rotate(-22 212 178)"/>
    <ellipse cx="190" cy="206" rx="8" ry="5" fill="#fff" opacity="0.2" transform="rotate(-30 190 206)"/>
  </g>
</svg>
"""


def render(svg_path, png_path, px):
    html = Path(tempfile.mkdtemp()) / "icon.html"
    html.write_text(f'<html><body style="margin:0"><img src="{svg_path.as_uri()}" width="{px}" height="{px}"></body></html>')
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    f"--window-size={px},{px}", f"--screenshot={png_path}", html.as_uri()],
                   check=True, capture_output=True)


def main():
    svg_path = SITE / "icon.svg"
    svg_path.write_text(svg())
    big = Path(tempfile.mkdtemp()) / "icon-1024.png"
    render(svg_path, big, 1024)
    master = Image.open(big).convert("RGB").crop((0, 0, 1024, 1024))
    for name, px in [("apple-touch-icon.png", 180), ("icon-192.png", 192), ("icon-512.png", 512)]:
        master.resize((px, px), Image.LANCZOS).save(SITE / name, optimize=True)
    # Maskierbar (Android): Motiv auf 80 % verkleinert, Rand mit Kartenfarbe aufgefüllt
    mask = Image.new("RGB", (1024, 1024), (239, 233, 218))
    inner = master.resize((820, 820), Image.LANCZOS)
    mask.paste(inner, (102, 102))
    mask.resize((512, 512), Image.LANCZOS).save(SITE / "icon-maskable-512.png", optimize=True)
    print("Icons geschrieben nach", SITE)


if __name__ == "__main__":
    main()
