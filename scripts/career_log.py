#!/usr/bin/env python3
"""Kariyer zaman çizelgesini 'git log --oneline' çıktısı gibi çizer. Stdlib."""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "career.svg"

W, H = 444, 300
BG = "#0b0f14"
FG = "#c9d1d9"
DIM = "#8b949e"
ACC = "#3ddc84"
KEY = "#58a6ff"
HASH = "#d29922"
MONO = "'SFMono-Regular','Fira Code',Consolas,'Liberation Mono',Menlo,monospace"

# (hash, ref, mesaj)
COMMITS = [
    ("e5f2a1c", "HEAD -> now", "co-founder @ Befior Soft"),
    ("9b21e04", "", "build: Laravel CRM panel"),
    ("5d7f3a2", "", "intern @ Uyumsoft"),
    ("c81d29b", "", "enroll: SE @ İstinye Üniv. '22"),
    ("a0d42c8", "", "init: first line of code"),
]

LINE_H = 30
TOP = 96

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'role="img" aria-label="career timeline of Muammer Baha Şenel as git log">',
    '<style>@media (prefers-reduced-motion: reduce){text,g,line{opacity:1 !important;transform:none !important}'
    '.cur{opacity:0 !important}}</style>',
    f'<rect width="100%" height="100%" rx="8" fill="{BG}"/>',
    f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="8" fill="none" stroke="#1c2530"/>',
    '<circle cx="22" cy="20" r="5" fill="#ff5f56"/>',
    '<circle cx="40" cy="20" r="5" fill="#ffbd2e"/>',
    '<circle cx="58" cy="20" r="5" fill="#27c93f"/>',
    f'<g font-family="{MONO}" font-size="12.5">',
    f'<text x="24" y="56"><tspan fill="{ACC}">$</tspan><tspan fill="{FG}" dx="10">git log --oneline career</tspan></text>',
]

# commit düğümlerini birleştiren dikey dal çizgisi (yukarı doğru büyür)
x_node = 29
y_first = TOP + 0 * LINE_H - 4
y_last = TOP + (len(COMMITS) - 1) * LINE_H - 4
parts.append(
    f'<line x1="{x_node}" y1="{y_last}" x2="{x_node}" y2="{y_last}" stroke="#1f2a36" stroke-width="2">'
    f'<animate attributeName="y2" from="{y_last}" to="{y_first}" dur="0.9s" begin="0.5s" fill="freeze"/></line>'
)

for i, (sha, ref, msg) in enumerate(COMMITS):
    # en eski commit en altta; yeni satırlar alttan yukarı belirir
    y = TOP + i * LINE_H
    begin = 0.6 + (len(COMMITS) - 1 - i) * 0.28
    ref_ts = ""
    if ref:
        head, _, branch = ref.partition(" -> ")
        ref_ts = (
            f'<tspan fill="{DIM}" dx="8">(</tspan><tspan fill="#39d3c8">{head}</tspan>'
            f'<tspan fill="{DIM}"> -&gt; </tspan><tspan fill="{ACC}">{branch}</tspan>'
            f'<tspan fill="{DIM}">)</tspan>'
        )
    parts.append(
        f'<g opacity="0" transform="translate(0 6)">'
        f'<animate attributeName="opacity" values="0;1" dur="0.35s" begin="{begin:.2f}s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" from="0 6" to="0 0" '
        f'dur="0.35s" begin="{begin:.2f}s" fill="freeze"/>'
        f'<text x="24" y="{y}"><tspan fill="{ACC}">*</tspan>'
        f'<tspan fill="{HASH}" dx="8">{sha}</tspan>{ref_ts}'
        f'<tspan fill="{FG}" dx="8">{msg}</tspan></text></g>'
    )

# altta bekleyen prompt + imleç
cy = TOP + len(COMMITS) * LINE_H + 14
pb = 0.6 + len(COMMITS) * 0.28 + 0.3
parts.append(
    f'<text x="24" y="{cy}" fill="{ACC}" opacity="0">$'
    f'<animate attributeName="opacity" values="0;1" dur="0.2s" begin="{pb:.2f}s" fill="freeze"/></text>'
    f'<rect class="cur" x="40" y="{cy - 11}" width="8" height="14" fill="{FG}" opacity="0">'
    f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;0.01;0.02;0.5;0.51" dur="2.4s" '
    f'begin="{pb:.2f}s" repeatCount="indefinite"/></rect>'
)

parts.append("</g></svg>")
OUT.write_text("\n".join(parts))
print(f"{OUT.name}: {W}x{H}px, {len(COMMITS)} commit")
