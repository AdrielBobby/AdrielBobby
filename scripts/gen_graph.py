"""Render the public GitHub contribution calendar as themed SVGs (dark + light)."""
import re
import sys
import urllib.request
from datetime import date

USER = sys.argv[1] if len(sys.argv) > 1 else "AdrielBobby"
THEMES = {
    "dark": {"bg": "#161b22", "border": "#30363d", "text": "#8b949e",
             "levels": ["#21262d", "#0e4429", "#006d32", "#26a641", "#00e676"]},
    "light": {"bg": "#f6f8fa", "border": "#d0d7de", "text": "#57606a",
              "levels": ["#e6eaee", "#b7ebc6", "#6fd58f", "#26a65b", "#00a152"]},
}
CELL, GAP, LEFT, TOP = 11, 3, 34, 34

html = urllib.request.urlopen(
    urllib.request.Request(f"https://github.com/users/{USER}/contributions",
                           headers={"User-Agent": "Mozilla/5.0"}), timeout=30
).read().decode()
cells = sorted((date.fromisoformat(d), int(l)) for d, l in
               re.findall(r'data-date="([\d-]+)"[^>]*data-level="(\d)"', html))
m = re.search(r"([\d,]+)\s+contributions", html)
total = m.group(1) if m else "?"
start = cells[0][0]
offset = (start.weekday() + 1) % 7  # Sunday-first grid
weeks = ((cells[-1][0] - start).days + offset) // 7 + 1
width = LEFT + weeks * (CELL + GAP) + 16
height = TOP + 7 * (CELL + GAP) + 34

for name, t in THEMES.items():
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
           f'viewBox="0 0 {width} {height}" font-family="ui-monospace,Consolas,monospace" font-size="11">',
           f'<rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="6" fill="{t["bg"]}" stroke="{t["border"]}"/>',
           f'<text x="16" y="22" fill="{t["levels"][4]}" font-size="12">$ git log --contributions --graph'
           f'  ({total} in the last year)</text>']
    last_month = None
    for d, lvl in cells:
        wk, wd = ((d - start).days + offset) // 7, (d.weekday() + 1) % 7
        x, y = LEFT + wk * (CELL + GAP), TOP + wd * (CELL + GAP)
        out.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{t["levels"][lvl]}"/>')
        if wd == 0 and d.month != last_month and d.day <= 7:
            out.append(f'<text x="{x}" y="{TOP-6}" fill="{t["text"]}" font-size="10">{d.strftime("%b")}</text>')
            last_month = d.month
    for wd, lab in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out.append(f'<text x="8" y="{TOP + wd*(CELL+GAP) + 9}" fill="{t["text"]}" font-size="9">{lab}</text>')
    lx = width - 16 - 5 * (CELL + 3) - 60
    ly = height - 14
    out.append(f'<text x="{lx}" y="{ly}" fill="{t["text"]}" font-size="10">Less</text>')
    for i, c in enumerate(t["levels"]):
        out.append(f'<rect x="{lx+30+i*(CELL+3)}" y="{ly-9}" width="{CELL}" height="{CELL}" rx="2" fill="{c}"/>')
    out.append(f'<text x="{lx+34+5*(CELL+3)}" y="{ly}" fill="{t["text"]}" font-size="10">More</text></svg>')
    open(f"contributions-{name}.svg", "w", encoding="utf-8").write("\n".join(out))
print(f"wrote contributions-dark.svg / contributions-light.svg ({len(cells)} days, {total} contributions)")
