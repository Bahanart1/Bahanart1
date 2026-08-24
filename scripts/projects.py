#!/usr/bin/env python3
"""CV'deki projeleri 'ls -la ~/projects' çıktısı gibi 3x2 grid'de çizer. Stdlib."""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "projects.svg"

W, H = 795, 236
BG = "#0b0f14"
FG = "#c9d1d9"
DIM = "#8b949e"
ACC = "#3ddc84"
KEY = "#58a6ff"
MONO = "'SFMono-Regular','Fira Code',Consolas,'Liberation Mono',Menlo,monospace"

# (dizin adı, kısa etiket, site)
PROJECTS = [
    ("befior/", "Laravel CRM · SaaS", "befior.com"),
    ("daiet/", "AI diet & health app", "daiet.com"),
    ("yorumarat/", "business reviews platform", "yorumarat.com"),
    ("vellichor-games/", "motion-first studio site", "vellichorgames.com"),
    ("modadora/", "corporate textile site", "modadora.com"),
    ("bisavunma/", "defense industry site", "bisavunma.com"),
]

COLS, ROWS = 3, 2
CELL_W = (W - 48) // COLS   # 249
TOP = 92
ROW_H = 68

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'role="img" aria-label="selected projects of Muammer Baha Şenel">',
    '<style>@media (prefers-reduced-motion: reduce){text,g{opacity:1 !important;transform:none !important}'
    '.cur{opacity:0 !important}}</style>',
    f'<rect width="100%" height="100%" rx="8" fill="{BG}"/>',
    f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="8" fill="none" stroke="#1c2530"/>',
    '<circle cx="22" cy="20" r="5" fill="#ff5f56"/>',
    '<circle cx="40" cy="20" r="5" fill="#ffbd2e"/>',
    '<circle cx="58" cy="20" r="5" fill="#27c93f"/>',
    f'<g font-family="{MONO}">',
    f'<text x="24" y="56" font-size="12.5"><tspan fill="{ACC}">$</tspan>'
    f'<tspan fill="{FG}" dx="10">ls -la ~/projects</tspan></text>',
]

def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


for i, (name, tag, url) in enumerate(PROJECTS):
    name, tag, url = esc(name), esc(tag), esc(url)
    cx = 24 + (i % COLS) * CELL_W
    cy = TOP + (i // COLS) * ROW_H
    b = 0.4 + i * 0.14
    parts.append(
        f'<g opacity="0" transform="translate(0 6)">'
        f'<animate attributeName="opacity" values="0;1" dur="0.35s" begin="{b:.2f}s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" from="0 6" to="0 0" '
        f'dur="0.35s" begin="{b:.2f}s" fill="freeze"/>'
        f'<text x="{cx}" y="{cy}" font-size="13.5" font-weight="bold" fill="{KEY}">{name}</text>'
        f'<text x="{cx}" y="{cy + 18}" font-size="11" fill="{DIM}">{tag}</text>'
        f'<text x="{cx}" y="{cy + 36}" font-size="11" fill="{ACC}">&#8599; {url}</text>'
        f'</g>'
    )

# altta bekleyen prompt + imleç
py = TOP + ROWS * ROW_H + 6
pb = 0.4 + len(PROJECTS) * 0.14 + 0.3
parts.append(
    f'<text x="24" y="{py}" font-size="12.5" fill="{ACC}" opacity="0">$'
    f'<animate attributeName="opacity" values="0;1" dur="0.2s" begin="{pb:.2f}s" fill="freeze"/></text>'
    f'<rect class="cur" x="40" y="{py - 11}" width="8" height="14" fill="{FG}" opacity="0">'
    f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;0.01;0.02;0.5;0.51" dur="2.4s" '
    f'begin="{pb:.2f}s" repeatCount="indefinite"/></rect>'
)

parts.append("</g></svg>")
OUT.write_text("\n".join(parts))
print(f"{OUT.name}: {W}x{H}px, {len(PROJECTS)} proje")
