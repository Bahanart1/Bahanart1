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
LEVELS = ["#151b23", "#0e4429", "#006d32", "#26a641", "#39d353"]

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
        f'<rect width="100%" height="100%" rx="8" fill="{BG}"/>',
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
