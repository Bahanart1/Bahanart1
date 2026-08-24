#!/usr/bin/env python3
"""Dönen taramalı skill radarı: süpürge geçtikçe hedefler parlar. Stdlib."""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "radar.svg"

W, H = 430, 300
BG = "#0b0f14"
FG = "#c9d1d9"
DIM = "#8b949e"
ACC = "#3ddc84"
GRID = "#1d2a38"
MONO = "'SFMono-Regular','Fira Code',Consolas,'Liberation Mono',Menlo,monospace"

CX, CY = 215, 174
RMAX = 92
SWEEP_T = 5.0  # tam tur süresi

# (etiket, açı°, yarıçap)  — 0° sağda, saat yönünde
TARGETS = [
    ("react", 25, 78),
    ("next.js", 80, 52),
    ("gsap", 135, 72),
    ("laravel", 195, 80),
    ("postgres", 250, 58),
    ("docker", 305, 76),
]


def pol(a_deg, r):
    a = math.radians(a_deg)
    return CX + r * math.cos(a), CY + r * math.sin(a)


parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'role="img" aria-label="skill radar: react, next.js, gsap, laravel, postgres, docker">',
    '<style>@media (prefers-reduced-motion: reduce){circle,text{opacity:1 !important}'
    '.sweep{display:none}}</style>',
    f'<rect width="100%" height="100%" rx="8" fill="{BG}"/>',
    f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="8" fill="none" stroke="#1c2530"/>',
    '<circle cx="22" cy="20" r="5" fill="#ff5f56"/>',
    '<circle cx="40" cy="20" r="5" fill="#ffbd2e"/>',
    '<circle cx="58" cy="20" r="5" fill="#27c93f"/>',
    f'<g font-family="{MONO}">',
    f'<text x="24" y="56" font-size="12.5"><tspan fill="{ACC}">$</tspan>'
    f'<tspan fill="{FG}" dx="10">scan --skills</tspan></text>',
    f'<text x="{W - 24}" y="56" font-size="10.5" text-anchor="end" fill="{ACC}" opacity="0.7">'
    f'{len(TARGETS)} targets locked</text>',
]

# halkalar + eksen çizgileri
for r in (31, 61, RMAX):
    parts.append(f'<circle cx="{CX}" cy="{CY}" r="{r}" fill="none" stroke="{GRID}"/>')
parts.append(f'<line x1="{CX - RMAX}" y1="{CY}" x2="{CX + RMAX}" y2="{CY}" stroke="{GRID}"/>')
parts.append(f'<line x1="{CX}" y1="{CY - RMAX}" x2="{CX}" y2="{CY + RMAX}" stroke="{GRID}"/>')

# süpürge: parlak çizgi + ardında solan kama
wx, wy = pol(-28, RMAX)
parts.append(
    f'<g class="sweep">'
    f'<path d="M {CX} {CY} L {CX + RMAX} {CY} A {RMAX} {RMAX} 0 0 0 {wx:.1f} {wy:.1f} Z" '
    f'fill="{ACC}" opacity="0.10"/>'
    f'<line x1="{CX}" y1="{CY}" x2="{CX + RMAX}" y2="{CY}" stroke="{ACC}" stroke-width="1.5" opacity="0.8"/>'
    f'<animateTransform attributeName="transform" type="rotate" from="0 {CX} {CY}" to="360 {CX} {CY}" '
    f'dur="{SWEEP_T}s" repeatCount="indefinite"/></g>'
)
parts.append(f'<circle cx="{CX}" cy="{CY}" r="2.5" fill="{ACC}"/>')

# hedefler: süpürge geçince parlayıp söner
for label, ang, r in TARGETS:
    x, y = pol(ang, r)
    t_pass = (ang % 360) / 360 * SWEEP_T
    parts.append(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{ACC}" opacity="0.25">'
        f'<animate attributeName="opacity" values="1;0.25;0.25" keyTimes="0;0.45;1" '
        f'dur="{SWEEP_T}s" begin="{t_pass:.2f}s" repeatCount="indefinite"/></circle>'
    )
    # etiketi dış tarafa yaz
    lx, ly = pol(ang, r + 15)
    anchor = "start" if math.cos(math.radians(ang)) >= 0 else "end"
    parts.append(
        f'<text x="{lx:.1f}" y="{ly + 4:.1f}" font-size="10.5" text-anchor="{anchor}" '
        f'fill="{DIM}">{label}</text>'
    )

parts.append("</g></svg>")
OUT.write_text("\n".join(parts))
print(f"{OUT.name}: {W}x{H}px, {len(TARGETS)} hedef, tur {SWEEP_T}s")
