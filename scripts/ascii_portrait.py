#!/usr/bin/env python3
"""Avatar fotoğrafını satır satır 'yazılan' animasyonlu ASCII SVG portresine çevirir.

Kullanım: python scripts/ascii_portrait.py <girdi.jpg> <çıktı.svg> [--variant a|b|c]
Tek seferlik çalışır (CI'da değil); Pillow gerektirir.
"""
import sys
from PIL import Image, ImageEnhance, ImageOps

COLS = 84
CHAR_W = 5.0          # px, monospace hücre genişliği
LINE_H = 10.0         # px, satır yüksekliği
FONT_SIZE = 8.4
ASPECT = 0.5          # mono karakterler ~2x uzun; dikey örnekleme oranı

# koyu zeminde açık metin: parlak piksel -> yoğun karakter
RAMP = " .`':,;i+*xmXNM@"

BG = "#0b0f14"
FG = "#3ddc84"


def segment_grid(path: str):
    """Arka planı (deniz/gökyüzü) renk sezgiseliyle sil, sadece figürü bırak.

    Kural: mavi kanalı kırmızıya baskın pikseller (deniz) ve parlak-düşük
    doygunluklu pikseller (soluk gökyüzü) arka plandır. Grid çözünürlüğünde
    en büyük bağlı bileşen dışındaki adacıklar da temizlenir.
    """
    rgb = Image.open(path).convert("RGB")
    rows = int(COLS * rgb.height / rgb.width * ASPECT)
    small = rgb.resize((COLS, rows), Image.LANCZOS)
    px = small.load()

    fg = [[False] * COLS for _ in range(rows)]
    for y in range(rows):
        for x in range(COLS):
            r, g, b = px[x, y]
            # düz mavi stüdyo arka planı: mavi kanal kırmızıdan çok baskın
            fg[y][x] = (b - r) < 100

    # ince yatay şeritleri (ufuk çizgisi, uzak sahil) ele:
    # dikey kalınlığı 3 hücreden az olan bölgeler figüre ait değildir
    vthick = [[0] * COLS for _ in range(rows)]
    for x in range(COLS):
        y = 0
        while y < rows:
            if fg[y][x]:
                y0 = y
                while y < rows and fg[y][x]:
                    y += 1
                for yy in range(y0, y):
                    vthick[yy][x] = y - y0
            else:
                y += 1
    for y in range(rows):
        for x in range(COLS):
            if fg[y][x] and vthick[y][x] < 3:
                fg[y][x] = False

    # en büyük bağlı bileşeni bul (4-komşuluk, iteratif flood fill)
    seen = [[False] * COLS for _ in range(rows)]
    best = set()
    for sy in range(rows):
        for sx in range(COLS):
            if fg[sy][sx] and not seen[sy][sx]:
                comp, stack = set(), [(sx, sy)]
                seen[sy][sx] = True
                while stack:
                    x, y = stack.pop()
                    comp.add((x, y))
                    for nx, ny in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
                        if 0 <= nx < COLS and 0 <= ny < rows and fg[ny][nx] and not seen[ny][nx]:
                            seen[ny][nx] = True
                            stack.append((nx, ny))
                if len(comp) > len(best):
                    best = comp

    # figürün çekirdek sütun aralığı dışındaki sarkıntıları (deniz parıltısı vb.) kırp
    col_count = [0] * COLS
    for x, _y in best:
        col_count[x] += 1
    if best:
        peak = max(range(COLS), key=lambda x: col_count[x])
        thr = max(2, int(col_count[peak] * 0.22))
        lo = peak
        while lo > 0 and col_count[lo - 1] >= thr:
            lo -= 1
        hi = peak
        while hi < COLS - 1 and col_count[hi + 1] >= thr:
            hi += 1
        best = {(x, y) for x, y in best if lo - 1 <= x <= hi + 1}

    # figür parlaklığı: otokontrastlı gri görüntüden al
    gray = ImageOps.autocontrast(rgb.convert("L"), cutoff=1).resize((COLS, rows), Image.LANCZOS)
    gp = gray.load()
    grid = []
    for y in range(rows):
        line = []
        for x in range(COLS):
            if (x, y) in best:
                v = gp[x, y] / 255.0
                # gölgeleri yukarı çek, parlak yüz bölgesinde detay bırak (gamma)
                v = min(1.0, 0.22 + (v ** 1.25) * 0.82)
                line.append(RAMP[min(int(v * len(RAMP)), len(RAMP) - 1)])
            else:
                line.append(" ")
        grid.append("".join(line))

    # figürü yatayda ortala
    cols_used = [x for row in grid for x, ch in enumerate(row) if ch != " "]
    if cols_used:
        lo, hi = min(cols_used), max(cols_used)
        shift = (COLS - (hi - lo + 1)) // 2 - lo
        if shift:
            grid = [
                (" " * max(shift, 0) + row[max(-shift, 0):])[:COLS].ljust(COLS)
                for row in grid
            ]
    return grid


def load_grid(path: str, variant: str):
    if variant == "d":
        return segment_grid(path)
    img = Image.open(path).convert("L")
    if variant == "a":          # otokontrast
        img = ImageOps.autocontrast(img, cutoff=1)
    elif variant == "b":        # otokontrast + hafif eşitleme karışımı
        base = ImageOps.autocontrast(img, cutoff=1)
        eq = ImageOps.equalize(img)
        img = Image.blend(base, eq, 0.35)
        img = ImageEnhance.Contrast(img).enhance(1.15)
    elif variant == "c":        # ters çevrilmiş (figür parlak)
        img = ImageOps.invert(ImageOps.autocontrast(img, cutoff=1))
        img = ImageEnhance.Contrast(img).enhance(1.2)
    rows = int(COLS * img.height / img.width * ASPECT)
    img = img.resize((COLS, rows), Image.LANCZOS)
    px = img.load()
    grid = []
    for y in range(rows):
        line = []
        for x in range(COLS):
            v = px[x, y] / 255.0
            line.append(RAMP[min(int(v * len(RAMP)), len(RAMP) - 1)])
        grid.append("".join(line))
    return grid


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render(grid, out_path: str):
    rows = len(grid)
    w = COLS * CHAR_W + 24
    h = rows * LINE_H + 24
    per_row = 2.4 / rows  # toplam ~2.4 sn'de yazılsın
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" '
        f'viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="ASCII portrait of bahanart1">',
        # hareket azaltma tercihinde animasyonsuz tam görünüm
        '<style>@media (prefers-reduced-motion: reduce){'
        'text{opacity:1 !important}.cur{opacity:0 !important}}</style>',
        f'<rect width="100%" height="100%" rx="8" fill="{BG}"/>',
        f'<g font-family="\'SFMono-Regular\',\'Fira Code\',Consolas,\'Liberation Mono\',Menlo,monospace" '
        f'font-size="{FONT_SIZE}" fill="{FG}" xml:space="preserve">',
    ]
    # boşluklar tarayıcıda güvenilmez: satırı boşluksuz segmentlere böl,
    # her segmenti kendi x konumu + textLength ile sabitle
    import re as _re
    for i, line in enumerate(grid):
        y = 12 + (i + 1) * LINE_H - 2
        begin = i * per_row
        spans = []
        for m in _re.finditer(r"\S+", line):
            x = 12 + m.start() * CHAR_W
            spans.append(
                f'<tspan x="{x:.1f}" textLength="{len(m.group()) * CHAR_W:.1f}">{esc(m.group())}</tspan>'
            )
        if not spans:
            continue
        parts.append(
            f'<text y="{y:.1f}" opacity="0">{"".join(spans)}'
            f'<animate attributeName="opacity" values="0;1" dur="0.05s" begin="{begin:.2f}s" fill="freeze"/></text>'
        )
    # yazım imleci: satırlarla birlikte aşağı iner, sonda söner
    total = rows * per_row
    parts.append(
        f'<rect class="cur" x="12" y="12" width="{CHAR_W * 2:.0f}" height="{LINE_H:.0f}" fill="{FG}" opacity="0.9">'
        f'<animate attributeName="y" from="12" to="{12 + rows * LINE_H:.0f}" dur="{total:.2f}s" fill="freeze"/>'
        f'<animate attributeName="opacity" values="0.9;0" dur="0.3s" begin="{total:.2f}s" fill="freeze"/></rect>'
    )
    parts.append("</g></svg>")
    with open(out_path, "w") as f:
        f.write("\n".join(parts))
    print(f"{out_path}: {rows} satır x {COLS} sütun, {w:.0f}x{h:.0f}px")


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    variant = sys.argv[4] if len(sys.argv) > 4 else (sys.argv[3].split("=")[-1] if len(sys.argv) > 3 else "a")
    if variant not in ("a", "b", "c", "d"):
        variant = "a"
    render(load_grid(src, variant), dst)
