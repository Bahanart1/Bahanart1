#!/usr/bin/env python3
"""GitHub'ın public katkı takvimini çeker ve animasyonlu heatmap SVG'si üretir.

Token gerekmez: github.com/users/<user>/contributions HTML endpoint'i parse edilir.
Sadece stdlib kullanır; GitHub Actions'ta günlük çalışır.
"""
import json
import re
import urllib.request
from datetime import date
from pathlib import Path

USER = "Bahanart1"
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "assets" / "contrib-heatmap.svg"

BG = "#0b0f14"
TEXT = "#8b949e"
TITLE = "#c9d1d9"
LEVELS = ["#1e2833", "#0e4429", "#006d32", "#26a641", "#39d353"]

# yılan animasyonu zamanlaması
SNAKE_START = 2.6   # giriş dalgası bittikten sonra başla
T_EAT = 19.0        # grid'i baştan sona dolaşma süresi
T_CYCLE = 22.0      # bekleme dahil tam döngü
TRAIL = 2.6         # yenen hücrenin karanlık kalma süresi (sn)
SNAKE_BODY = ["#3ddc84", "#2fbf72", "#27a563", "#1f8b54", "#1a7547", "#15613b", "#104d30"]

CELL = 11
GAP = 3
PAD_L = 34   # gün etiketleri için
PAD_T = 40   # başlık + ay etiketleri


def fetch():
    url = f"https://github.com/users/{USER}/contributions"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")

    days = {}       # date -> gün kaydı
    by_id = {}      # td id -> gün kaydı (tooltip eşlemesi için)
    for m in re.finditer(r'<td\b[^>]*\bdata-date="(\d{4}-\d{2}-\d{2})"[^>]*>', html):
        tag = m.group(0)
        lvl = re.search(r'data-level="(\d)"', tag)
        tid = re.search(r'\bid="([^"]+)"', tag)
        if lvl and tid:
            rec = {"level": int(lvl.group(1)), "count": 0}
            days[m.group(1)] = rec
            by_id[tid.group(1)] = rec

    # tool-tip elemanlarındaki "N contributions on ..." metinlerinden sayıları eşle
    for m in re.finditer(r'<tool-tip\b[^>]*\bfor="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        rec = by_id.get(m.group(1))
        n = re.match(r"(\d+)", m.group(2).strip())
        if rec and n:
            rec["count"] = int(n.group(1))

    result = sorted(
        ({"date": k, "level": v["level"], "count": v["count"]} for k, v in days.items()),
        key=lambda x: x["date"],
    )
    if not result:
        raise SystemExit("katkı verisi parse edilemedi")
    return result


def render(days):
    # haftalara böl (GitHub grid'i pazar başlangıçlı; veri zaten takvim sıralı)
    weeks = []
    week = []
    for d in days:
        wd = date.fromisoformat(d["date"]).isoweekday() % 7  # pazar=0
        if wd == 0 and week:
            weeks.append(week)
            week = []
        week.append((wd, d))
    if week:
        weeks.append(week)

    n_weeks = len(weeks)
    w = PAD_L + n_weeks * (CELL + GAP) + 12
    h = PAD_T + 7 * (CELL + GAP) + 30
    total = sum(d["count"] for d in days)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="Contribution heatmap of {USER}: {total} contributions in the last year">',
        # hareket azaltma tercihinde animasyonsuz tam görünüm (yılan ve iz gizlenir)
        '<style>@media (prefers-reduced-motion: reduce){rect{opacity:1 !important}'
        '.snake,.eat{display:none}}</style>',
        f'<rect width="100%" height="100%" rx="8" fill="{BG}"/>',
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="8" fill="none" stroke="#1c2530"/>',
        f'<g font-family="\'SFMono-Regular\',\'Fira Code\',Consolas,\'Liberation Mono\',Menlo,monospace">',
        f'<text x="{PAD_L}" y="22" font-size="12" fill="{TITLE}">$ git log --graph --author={USER}</text>',
        f'<text x="{w - 12}" y="22" font-size="11" text-anchor="end" fill="{LEVELS[3]}">{total} contributions · last year</text>',
    ]

    # ay etiketleri: ayın ilk görüldüğü hafta sütununa yaz
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    seen = set()
    for wi, wk in enumerate(weeks):
        mth = date.fromisoformat(wk[0][1]["date"]).month
        if mth not in seen:
            seen.add(mth)
            if wi > 0 or len(weeks[0]) > 3:  # kenarda sıkışmasın
                x = PAD_L + wi * (CELL + GAP)
                parts.append(f'<text x="{x}" y="{PAD_T - 6}" font-size="9" fill="{TEXT}">{months[mth - 1]}</text>')

    for lbl, row in (("Mon", 1), ("Wed", 3), ("Fri", 5)):
        y = PAD_T + row * (CELL + GAP) + CELL - 2
        parts.append(f'<text x="6" y="{y}" font-size="9" fill="{TEXT}">{lbl}</text>')

    # hücreler: diyagonal dalga halinde belirir
    for wi, wk in enumerate(weeks):
        for wd, d in wk:
            x = PAD_L + wi * (CELL + GAP)
            y = PAD_T + wd * (CELL + GAP)
            begin = wi * 0.028 + wd * 0.055
            c = LEVELS[d["level"]]
            cell = (
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}" opacity="0">'
                f'<animate attributeName="opacity" values="0;1" dur="0.35s" begin="{begin:.2f}s" fill="freeze"/>'
            )
            if d["level"] >= 3:  # yoğun günler girişte hafifçe parlar
                cell += (
                    f'<animate attributeName="opacity" values="1;0.55;1" dur="3.2s" '
                    f'begin="{begin + 2.2:.2f}s" repeatCount="indefinite"/>'
                )
            parts.append(cell + "</rect>")

    # --- yılan: boustrophedon hücre dizisi boyunca x/y animasyonu ---
    # (animateMotion bazı ortamlarda takılıyor; eşit adımlı düz animate güvenilir)
    pitch = CELL + GAP
    waypoints = []  # ziyaret sırasıyla (hafta, gün)
    for wi in range(n_weeks):
        rows = range(7) if wi % 2 == 0 else range(6, -1, -1)
        waypoints.extend((wi, wd) for wd in rows)
    n_wp = len(waypoints)

    # yenen hücre izi: yılan geçince kararır, TRAIL sn sonra geri gelir
    for idx, (wi, wd) in enumerate(waypoints):
        x = PAD_L + wi * pitch
        y = PAD_T + wd * pitch
        te = max(idx / (n_wp - 1), 0.001)
        te2 = min(te + TRAIL / T_EAT, 0.998)
        parts.append(
            f'<rect class="eat" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
            f'fill="{BG}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0.9;0" keyTimes="0;{te:.4f};{te2:.4f}" '
            f'calcMode="discrete" dur="{T_EAT}s" begin="{SNAKE_START}s" repeatCount="indefinite"/></rect>'
        )

    def seg_rect(size, color, opacity, delay, cls_extra=""):
        off = (CELL - size) / 2
        xs = ";".join(f"{PAD_L + wi * pitch + off:.0f}" for wi, _ in waypoints)
        ys = ";".join(f"{PAD_T + wd * pitch + off:.0f}" for _, wd in waypoints)
        b = SNAKE_START + delay
        return (
            f'<rect class="snake{cls_extra}" x="{PAD_L + off:.0f}" y="{PAD_T + off:.0f}" '
            f'width="{size}" height="{size}" rx="3" fill="{color}" opacity="0">'
            f'<animate attributeName="opacity" values="0;{opacity}" dur="0.01s" begin="{b:.2f}s" fill="freeze"/>'
            f'<animate attributeName="x" values="{xs}" dur="{T_EAT}s" begin="{b:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="y" values="{ys}" dur="{T_EAT}s" begin="{b:.2f}s" repeatCount="indefinite"/>'
            f'</rect>'
        )

    # baş parıltısı altta, gövde kuyruktan başa doğru üstte
    parts.append(seg_rect(19, LEVELS[4], "0.16", 0.0))
    for k in range(len(SNAKE_BODY) - 1, -1, -1):
        size = CELL - (0 if k < 2 else 1 if k < 4 else 2)
        parts.append(seg_rect(size, SNAKE_BODY[k], "0.96", k * 0.065))

    # alt lejant
    ly = PAD_T + 7 * (CELL + GAP) + 16
    parts.append(f'<text x="{w - 12 - 5 * (CELL + GAP) - 34}" y="{ly + 9}" font-size="9" text-anchor="end" fill="{TEXT}">Less</text>')
    for i, c in enumerate(LEVELS):
        x = w - 12 - (5 - i) * (CELL + GAP) - 28
        parts.append(f'<rect x="{x}" y="{ly}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>')
    parts.append(f'<text x="{w - 12}" y="{ly + 9}" font-size="9" text-anchor="end" fill="{TEXT}">More</text>')

    parts.append("</g></svg>")
    OUT.write_text("\n".join(parts))
    print(f"{OUT.name}: {n_weeks} hafta, toplam {total} katkı, {w}x{h}px")


if __name__ == "__main__":
    days = fetch()
    DATA.parent.mkdir(exist_ok=True)
    DATA.write_text(json.dumps(days, indent=1))
    render(days)
