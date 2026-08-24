#!/usr/bin/env python3
"""Neofetch tarzı animasyonlu bilgi kartı SVG'si üretir. Tek seferlik, stdlib."""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "info-card.svg"

W, H = 430, 444
BG = "#0b0f14"
FG = "#c9d1d9"
DIM = "#8b949e"
ACC = "#3ddc84"
KEY = "#58a6ff"

# CV'den; kişisel iletişim bilgileri bilinçli olarak dışarıda bırakıldı
FIELDS = [
    ("Name", "Muammer Baha Şenel"),
    ("Role", "Software Engineer"),
    ("Company", "Befior Soft · co-founder"),
    ("Edu", "İstinye Üniv. · SE 2026"),
    ("Frontend", "React · Next.js · TypeScript"),
    ("Backend", "ASP.NET Core · Laravel · Node"),
    ("UI", "Tailwind · Framer Motion · GSAP"),
    ("DB", "PostgreSQL · MySQL · Supabase"),
    ("Web", "befior.com"),
]

PALETTE = ["#ff5f56", "#ffbd2e", "#3ddc84", "#58a6ff", "#bc8cff", "#39d3c8", "#c9d1d9", "#8b949e"]

MONO = "'SFMono-Regular','Fira Code',Consolas,'Liberation Mono',Menlo,monospace"

# hareket azaltma tercihinde animasyonsuz tam görünüm
REDUCED_STYLE = (
    '<style>@media (prefers-reduced-motion: reduce){'
    'text,g,rect{opacity:1 !important;transform:none !important}'
    '.cur{opacity:0 !important}'
    '}</style>'
)

LINE_H = 26
TOP = 78          # "$ neofetch" satırından sonra içerik başlangıcı
TYPE_END = 1.0    # komutun yazılması biten an
STAGGER = 0.16


def fade_line(y, begin, inner):
    return (
        f'<g opacity="0" transform="translate(-8 0)">'
        f'<animate attributeName="opacity" values="0;1" dur="0.4s" begin="{begin:.2f}s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" from="-8 0" to="0 0" '
        f'dur="0.4s" begin="{begin:.2f}s" fill="freeze"/>'
        f'{inner}</g>'
    )


parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'role="img" aria-label="Muammer Baha Şenel — software engineer info card">',
    REDUCED_STYLE,
    f'<rect width="100%" height="100%" rx="8" fill="{BG}"/>',
    f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="8" fill="none" stroke="#1c2530"/>',
    # pencere başlığı noktaları
    '<circle cx="22" cy="20" r="5" fill="#ff5f56"/>',
    '<circle cx="40" cy="20" r="5" fill="#ffbd2e"/>',
    '<circle cx="58" cy="20" r="5" fill="#27c93f"/>',
    f'<g font-family="{MONO}" font-size="13.5">',
]

# $ neofetch — karakter karakter yazılır
cmd = "neofetch"
parts.append(f'<text x="24" y="56" fill="{ACC}">$</text>')
for i, ch in enumerate(cmd):
    b = 0.25 + i * 0.08
    parts.append(
        f'<text x="{40 + i * 8.2:.1f}" y="56" fill="{FG}" opacity="0">{ch}'
        f'<animate attributeName="opacity" values="0;1" dur="0.02s" begin="{b:.2f}s" fill="freeze"/></text>'
    )

# başlık + ayraç
y = TOP + 22
parts.append(fade_line(y, TYPE_END, (
    f'<text x="24" y="{y}"><tspan fill="{ACC}" font-weight="bold">bahanart1</tspan>'
    f'<tspan fill="{DIM}">@</tspan><tspan fill="{KEY}" font-weight="bold">github</tspan></text>'
)))
y += 18
parts.append(fade_line(y, TYPE_END + STAGGER, f'<text x="24" y="{y}" fill="{DIM}">-----------------------------</text>'))

# alanlar
for i, (k, v) in enumerate(FIELDS):
    y += LINE_H
    b = TYPE_END + (i + 2) * STAGGER
    dots = "." * (8 - len(k))
    parts.append(fade_line(y, b, (
        f'<text x="24" y="{y}"><tspan fill="{KEY}">{k}</tspan><tspan fill="#2d3844">{dots}:</tspan>'
        f'<tspan fill="{FG}" dx="8">{v}</tspan></text>'
    )))

# palet blokları
py = y + 34
pb = TYPE_END + (len(FIELDS) + 3) * STAGGER
for i, c in enumerate(PALETTE):
    parts.append(
        f'<rect x="{24 + i * 24}" y="{py}" width="20" height="12" rx="2" fill="{c}" opacity="0">'
        f'<animate attributeName="opacity" values="0;1" dur="0.3s" begin="{pb + i * 0.06:.2f}s" fill="freeze"/></rect>'
    )

# yanıp sönen imleç en altta
cy = py + 34
parts.append(
    f'<text x="24" y="{cy}" fill="{ACC}">$</text>'
    f'<rect class="cur" x="40" y="{cy - 11}" width="8" height="14" fill="{FG}" opacity="0">'
    f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;0.01;0.02;0.5;0.51" dur="2.4s" '
    f'begin="{pb + 0.6:.2f}s" repeatCount="indefinite"/></rect>'
)

parts.append("</g></svg>")
OUT.write_text("\n".join(parts))
print(f"{OUT.name}: {W}x{H}px, {len(FIELDS)} alan")
