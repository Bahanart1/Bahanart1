#!/usr/bin/env python3
"""Kendini karakter karakter yazan sözdizimi renkli kod editörü paneli. Stdlib."""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "editor.svg"

W, H = 444, 300
BG = "#0b0f14"
FG = "#c9d1d9"
DIM = "#8b949e"
ACC = "#3ddc84"
MONO = "'SFMono-Regular','Fira Code',Consolas,'Liberation Mono',Menlo,monospace"

# GitHub dark sözdizimi renkleri
KW = "#ff7b72"     # anahtar kelime
STR = "#a5d6ff"    # string
CONST = "#79c0ff"  # sabit / sayı
ENT = "#d2a8ff"    # sınıf / fonksiyon
PUNC = "#8b949e"

# satırlar: (renk, metin) parçaları
LINES = [
    [(KW, "import"), (FG, " { "), (ENT, "Engineer"), (FG, " } "), (KW, "from"), (STR, ' "@befior/core"'), (PUNC, ";")],
    [],
    [(KW, "const"), (FG, " baha "), (PUNC, "= "), (KW, "new"), (FG, " "), (ENT, "Engineer"), (PUNC, "({")],
    [(FG, "  stack"), (PUNC, ": ["), (STR, '"next.js"'), (PUNC, ", "), (STR, '"laravel"'), (PUNC, ", "), (STR, '"gsap"'), (PUNC, "],")],
    [(FG, "  focus"), (PUNC, ": "), (STR, '"ui that feels alive"'), (PUNC, ",")],
    [(FG, "  coffee"), (PUNC, ": "), (CONST, "Infinity"), (PUNC, ",")],
    [(PUNC, "});")],
    [],
    [(KW, "await"), (FG, " baha"), (PUNC, "."), (ENT, "ship"), (PUNC, "("), (STR, '"something cool"'), (PUNC, ");")],
]

CHAR_W = 7.3
FONT = 12
TOP = 78
LINE_H = 21
CODE_X = 52
TYPE_DT = 0.028


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'role="img" aria-label="code editor typing a snippet about Muammer Baha Şenel">',
    '<style>@media (prefers-reduced-motion: reduce){text{opacity:1 !important}'
    '.cur{opacity:0 !important}}</style>',
    f'<rect width="100%" height="100%" rx="8" fill="{BG}"/>',
    f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="8" fill="none" stroke="#1c2530"/>',
    '<circle cx="22" cy="20" r="5" fill="#ff5f56"/>',
    '<circle cx="40" cy="20" r="5" fill="#ffbd2e"/>',
    '<circle cx="58" cy="20" r="5" fill="#27c93f"/>',
    # sekme
    f'<rect x="86" y="8" width="108" height="24" rx="6" fill="#121a24"/>',
    f'<circle cx="102" cy="20" r="3" fill="#3178c6"/>',
    f'<text x="112" y="24" font-family="{MONO}" font-size="11" fill="{FG}">engineer.ts</text>',
    f'<line x1="1" y1="40" x2="{W - 1}" y2="40" stroke="#1c2530"/>',
    f'<g font-family="{MONO}" font-size="{FONT}">',
]

# satır numaraları
for i in range(len(LINES)):
    parts.append(f'<text x="34" y="{TOP + i * LINE_H}" text-anchor="end" fill="#3a4654">{i + 1}</text>')

# karakter karakter yazım (global sıra)
gi = 0
cursor_moves = []  # (zaman, x, y) — imleç yazıyla birlikte ilerler
for li, spans in enumerate(LINES):
    y = TOP + li * LINE_H
    col = 0
    for color, txt in spans:
        for ch in txt:
            if ch != " ":
                t = 0.6 + gi * TYPE_DT
                parts.append(
                    f'<text x="{CODE_X + col * CHAR_W:.1f}" y="{y}" fill="{color}" opacity="0">{esc(ch)}'
                    f'<animate attributeName="opacity" values="0;1" dur="0.01s" begin="{t:.2f}s" fill="freeze"/></text>'
                )
            gi += 1
            col += 1
    cursor_moves.append((0.6 + gi * TYPE_DT, CODE_X + col * CHAR_W, y))

total_t = 0.6 + gi * TYPE_DT

# yazan imleç: her satırın sonuna atlar, bitince durum çubuğuna iner
cx, cy = cursor_moves[0][1], cursor_moves[0][2]
parts.append(f'<rect class="cur" x="0" y="0" width="7" height="14" fill="{ACC}" opacity="0.85" transform="translate({CODE_X} {TOP - 11})">')
prev_t = 0.6
for t, x, y in cursor_moves:
    parts.append(
        f'<animateTransform attributeName="transform" type="translate" to="{x:.0f} {y - 11}" '
        f'dur="0.01s" begin="{t:.2f}s" fill="freeze"/>'
    )
parts.append(
    f'<animate attributeName="opacity" values="0.85;0" dur="0.3s" begin="{total_t + 0.4:.2f}s" fill="freeze"/></rect>'
)

# durum çubuğu
sy = H - 16
parts.append(f'<line x1="1" y1="{H - 32}" x2="{W - 1}" y2="{H - 32}" stroke="#1c2530"/>')
parts.append(
    f'<text x="24" y="{sy}" font-size="11" fill="{ACC}" opacity="0">&#10003; no type errors'
    f'<animate attributeName="opacity" values="0;1" dur="0.3s" begin="{total_t + 0.5:.2f}s" fill="freeze"/></text>'
)
parts.append(
    f'<text x="{W - 24}" y="{sy}" font-size="11" text-anchor="end" fill="{DIM}" opacity="0">TypeScript · UTF-8 · &#9889; vercel'
    f'<animate attributeName="opacity" values="0;1" dur="0.3s" begin="{total_t + 0.7:.2f}s" fill="freeze"/></text>'
)

parts.append("</g></svg>")
OUT.write_text("\n".join(parts))
print(f"{OUT.name}: {W}x{H}px, {gi} karakter, yazım ~{total_t:.1f}s")
