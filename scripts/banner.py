#!/usr/bin/env python3
"""Üstte tam genişlik 'whoami' bandı: cevaplar sırayla yazılır, silinir, döner. Stdlib."""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "banner.svg"

W, H = 795, 96
BG = "#0b0f14"
FG = "#c9d1d9"
ACC = "#3ddc84"
KEY = "#58a6ff"
MONO = "'SFMono-Regular','Fira Code',Consolas,'Liberation Mono',Menlo,monospace"

PHRASES = [
    "muammer baha şenel",
    "software engineer · full-stack",
    "co-founder @ befior soft",
    "react · next.js · laravel · gsap",
]

CHAR_W = 9.0      # font 15 mono
TYPE_DT = 0.07    # karakter başına yazma süresi
SLOT = 4.5        # her ifadeye ayrılan süre
T = SLOT * len(PHRASES)

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'role="img" aria-label="whoami: muammer baha şenel, software engineer">',
    '<style>@media (prefers-reduced-motion: reduce){text{opacity:1 !important}'
    'rect.cur{opacity:0 !important}.alt{display:none}}</style>',
    f'<rect width="100%" height="100%" rx="8" fill="{BG}"/>',
    f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="8" fill="none" stroke="#1c2530"/>',
    '<circle cx="22" cy="20" r="5" fill="#ff5f56"/>',
    '<circle cx="40" cy="20" r="5" fill="#ffbd2e"/>',
    '<circle cx="58" cy="20" r="5" fill="#27c93f"/>',
    f'<g font-family="{MONO}" font-size="15">',
    f'<text x="24" y="46"><tspan fill="{ACC}">$</tspan><tspan fill="{FG}" dx="10">whoami</tspan></text>',
    f'<text x="24" y="76" fill="{KEY}">&#10095;</text>',
]

# hareket azaltmada yalnızca ilk ifade görünür; diğerleri .alt ile gizlenir
for i, phrase in enumerate(PHRASES):
    s = i * SLOT           # ifadenin başlangıcı
    e = s + SLOT - 0.35    # görünürlüğün bittiği an
    cls = ' class="alt"' if i > 0 else ""
    parts.append(f'<g{cls}>')
    for j, ch in enumerate(phrase):
        if ch == " ":
            continue
        t_on = (s + 0.25 + j * TYPE_DT) / T
        t_off = e / T
        kt = f"0;{max(t_on - 0.001, 0):.4f};{t_on:.4f};{t_off:.4f};{min(t_off + 0.004, 1):.4f};1"
        parts.append(
            f'<text x="{44 + j * CHAR_W:.1f}" y="76" fill="{FG}" opacity="0">{ch}'
            f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{kt}" '
            f'calcMode="discrete" dur="{T}s" repeatCount="indefinite"/></text>'
        )
    # ifade yazılıp bittikten sonra sonunda yanıp sönen imleç
    x_end = 44 + len(phrase) * CHAR_W + 3
    t_typed = (s + 0.25 + len(phrase) * TYPE_DT) / T
    t_off = e / T
    blink, t = ["0"], [0.0]
    cur = t_typed
    vis = True
    while cur < t_off:
        t.append(cur)
        blink.append("1" if vis else "0")
        vis = not vis
        cur += 0.55 / T
    t.append(t_off)
    blink.append("0")
    t.append(1.0)
    blink.append("0")
    kt = ";".join(f"{x:.4f}" for x in t)
    parts.append(
        f'<rect class="cur" x="{x_end:.1f}" y="64" width="9" height="16" fill="{ACC}" opacity="0">'
        f'<animate attributeName="opacity" values="{";".join(blink)}" keyTimes="{kt}" '
        f'calcMode="discrete" dur="{T}s" repeatCount="indefinite"/></rect>'
    )
    parts.append("</g>")

parts.append("</g></svg>")
OUT.write_text("\n".join(parts))
print(f"{OUT.name}: {W}x{H}px, {len(PHRASES)} ifade, döngü {T}s")
