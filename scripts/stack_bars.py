#!/usr/bin/env python3
"""Public repolardaki dil dağılımını çekip animasyonlu bar grafiği SVG'si üretir.

Sadece stdlib; GitHub Actions'ta günlük çalışır. GH_TOKEN/GITHUB_TOKEN varsa kullanır.
"""
import json
import os
import urllib.request
from pathlib import Path

USER = "Bahanart1"
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "languages.json"
OUT = ROOT / "assets" / "stack.svg"

W, H = 430, 300
BG = "#0b0f14"
FG = "#c9d1d9"
DIM = "#8b949e"
ACC = "#3ddc84"
MONO = "'SFMono-Regular','Fira Code',Consolas,'Liberation Mono',Menlo,monospace"

# GitHub linguist renkleri
COLORS = {
    "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "HTML": "#e34c26",
    "CSS": "#663399", "Python": "#3572A5", "C#": "#178600", "PHP": "#4F5D95",
    "Blade": "#f7523f", "SCSS": "#c6538c", "Shell": "#89e051",
    "C++": "#f34b7d", "C": "#555555", "PLpgSQL": "#336790",
    "PHP · Laravel": "#FF2D20",
}
TOP_N = 5

# HTML şablon gürültüsü, grafikte istenmiyor
EXCLUDE = {"HTML"}
# Private repolardaki iş (Befior CRM) linguist'te görünmüyor; sabit ağırlıkla temsil et
MANUAL = {"PHP · Laravel": 250_000}


def api(path):
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={"User-Agent": "profile-readme", "Accept": "application/vnd.github+json"},
    )
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    return json.load(urllib.request.urlopen(req, timeout=30))


def fetch():
    totals = {}
    for repo in api(f"/users/{USER}/repos?per_page=100"):
        if repo["name"] == USER or repo.get("fork"):
            continue  # profil reposunu ve fork'ları sayma
        for lang, n in api(f"/repos/{USER}/{repo['name']}/languages").items():
            if lang not in EXCLUDE:
                totals[lang] = totals.get(lang, 0) + n
    if not totals:
        raise SystemExit("dil verisi alınamadı")
    for lang, n in MANUAL.items():
        totals[lang] = totals.get(lang, 0) + n
    return totals


def render(totals):
    grand = sum(totals.values())
    top = sorted(totals.items(), key=lambda kv: -kv[1])[:TOP_N]
    other = grand - sum(n for _, n in top)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-label="language breakdown across public repos">',
        '<style>@media (prefers-reduced-motion: reduce){text{opacity:1 !important}'
        'rect.bar{opacity:1 !important}}</style>',
        f'<rect width="100%" height="100%" rx="8" fill="{BG}"/>',
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="8" fill="none" stroke="#1c2530"/>',
        '<circle cx="22" cy="20" r="5" fill="#ff5f56"/>',
        '<circle cx="40" cy="20" r="5" fill="#ffbd2e"/>',
        '<circle cx="58" cy="20" r="5" fill="#27c93f"/>',
        f'<g font-family="{MONO}" font-size="12.5">',
        f'<text x="24" y="56"><tspan fill="{ACC}">$</tspan><tspan fill="{FG}" dx="10">linguist --breakdown</tspan></text>',
    ]

    top_y = 92
    row_h = 38
    bar_x = 24
    bar_max = W - 48 - 52   # sağda yüzde etiketi için pay
    for i, (lang, n) in enumerate(top):
        pct = 100 * n / grand
        y = top_y + i * row_h
        w = max(4, bar_max * n / top[0][1])   # en büyük dile göre ölçekle
        c = COLORS.get(lang, "#6e7681")
        b = 0.3 + i * 0.15
        parts.append(f'<text x="{bar_x}" y="{y}" fill="{FG}">{lang}</text>')
        parts.append(
            f'<text x="{W - 24}" y="{y}" text-anchor="end" fill="{DIM}" opacity="0">{pct:.1f}%'
            f'<animate attributeName="opacity" values="0;1" dur="0.3s" begin="{b + 0.5:.2f}s" fill="freeze"/></text>'
        )
        parts.append(f'<rect x="{bar_x}" y="{y + 8}" width="{bar_max}" height="8" rx="4" fill="#151b23"/>')
        parts.append(
            f'<rect class="bar" x="{bar_x}" y="{y + 8}" width="{w:.1f}" height="8" rx="4" fill="{c}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0.95" dur="0.01s" begin="{b:.2f}s" fill="freeze"/>'
            f'<animate attributeName="width" from="0" to="{w:.1f}" dur="0.9s" begin="{b:.2f}s" fill="freeze" '
            f'calcMode="spline" keyTimes="0;1" keySplines="0.22 1 0.36 1"/></rect>'
        )

    fy = top_y + TOP_N * row_h + 6
    kb = grand / 1024
    size = f"{kb / 1024:.1f} MB" if kb > 1024 else f"{kb:.0f} KB"
    note = f"{size} of code · +{100 * other / grand:.1f}% other" if other else f"{size} of code"
    parts.append(f'<text x="24" y="{fy}" font-size="11" fill="{DIM}">{note}</text>')

    parts.append("</g></svg>")
    OUT.write_text("\n".join(parts))
    print(f"{OUT.name}: {len(top)} dil, toplam {size}")


if __name__ == "__main__":
    totals = fetch()
    DATA.parent.mkdir(exist_ok=True)
    DATA.write_text(json.dumps(totals, indent=1, sort_keys=True))
    render(totals)
