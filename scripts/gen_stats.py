"""Build dist/stats.svg — contribution dot-grid, streaks and top languages.

Uses only public GitHub data (the contributions calendar page and the REST
API), so it runs locally or in Actions. GITHUB_TOKEN is used if present to
avoid REST rate limits.

usage: python scripts/gen_stats.py <username> <out.svg>
"""
import datetime as dt
import html
import json
import os
import re
import sys
import urllib.request

USER, OUT = sys.argv[1], sys.argv[2]
TOKEN = os.environ.get("GITHUB_TOKEN")


def get(url, api=False):
    req = urllib.request.Request(url, headers={"User-Agent": "profile-stats"})
    if api and TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode()


# ---- contributions -------------------------------------------------------
page = get(f"https://github.com/users/{USER}/contributions")
tips = {m[0]: m[1] for m in re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)<', page)}
days = []
for date, cid, level in re.findall(r'data-date="([\d-]+)"\s+id="([^"]+)"\s+data-level="(\d)"', page):
    n = re.match(r"(\d+)", tips.get(cid, ""))
    days.append((dt.date.fromisoformat(date), int(level), int(n.group(1)) if n else 0))
days.sort()

total = sum(c for _, _, c in days)
longest = run = 0
for _, _, c in days:
    run = run + 1 if c else 0
    longest = max(longest, run)
current = 0
rev = days[::-1]
if rev and rev[0][2] == 0:  # today not counted yet is fine
    rev = rev[1:]
for _, _, c in rev:
    if not c:
        break
    current += 1
best = max(days, key=lambda d: d[2]) if days else None

# ---- repos & languages ---------------------------------------------------
repos = json.loads(get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner", api=True))
repos = [r for r in repos if not r["fork"]]
stars = sum(r["stargazers_count"] for r in repos)
langs = {}
for r in repos:
    try:
        for k, v in json.loads(get(r["languages_url"], api=True)).items():
            langs[k] = langs.get(k, 0) + v
    except Exception:
        pass
lt = sum(langs.values()) or 1
top = sorted(langs.items(), key=lambda kv: -kv[1])[:6]

# ---- render --------------------------------------------------------------
W, H = 900, 300
BLUES = ["#111a2e", "#1e3a8a", "#2563eb", "#60a5fa", "#bfdbfe"]
RAD = [1.7, 3.0, 3.6, 4.2, 4.8]
FONT = "'Segoe UI',Ubuntu,'Helvetica Neue',Arial,sans-serif"
MONO = "'JetBrains Mono','Fira Code',Consolas,monospace"

# calendar grid: columns are weeks starting Sunday
start = days[0][0] - dt.timedelta(days=(days[0][0].weekday() + 1) % 7) if days else dt.date.today()
GX, GY, P = 34, 170, 11.6
cells, months, seen = [], [], set()
for d, lvl, c in days:
    col, row = (d - start).days // 7, (d.weekday() + 1) % 7
    x, y = GX + col * P, GY + row * P
    cells.append(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{RAD[lvl]}" fill="{BLUES[lvl]}" '
        f'style="animation-delay:{col * 0.045:.2f}s"><title>{c} on {d:%b %d}</title></circle>')
    if d.day <= 7 and (d.year, d.month) not in seen and row == 0:
        seen.add((d.year, d.month))
        months.append(f'<text class="m" x="{x - 3:.1f}" y="{GY - 14}">{d:%b}</text>')

tiles = [
    (f"{total:,}", "contributions · last year"),
    (f"{current}", "day current streak"),
    (f"{longest}", "day longest streak"),
    (f"{len(repos)}", f"public repos · {stars}★"),
]
tile_svg = []
for k, (num, label) in enumerate(tiles):
    x = 34 + k * 156
    tile_svg.append(
        f'<g class="tile" style="animation-delay:{0.15 * k:.2f}s">'
        f'<rect x="{x}" y="58" width="144" height="68" rx="10" fill="#0b1324" stroke="#1e3a8a"/>'
        f'<text class="num" x="{x + 14}" y="94">{num}</text>'
        f'<text class="lbl" x="{x + 14}" y="114">{html.escape(label)}</text></g>')

lang_svg = []
for k, (name, b) in enumerate(top):
    pct = b / lt * 100
    y = 82 + k * 34
    lang_svg.append(
        f'<g class="tile" style="animation-delay:{0.3 + 0.12 * k:.2f}s">'
        f'<text class="ln" x="680" y="{y}">{html.escape(name)}</text>'
        f'<text class="lp" x="866" y="{y}" text-anchor="end">{pct:.1f}%</text>'
        f'<rect x="680" y="{y + 8}" width="186" height="5" rx="2.5" fill="#111a2e"/>'
        f'<rect class="bar" x="680" y="{y + 8}" width="{max(186 * pct / 100, 4):.1f}" height="5" rx="2.5" '
        f'fill="url(#lg)" style="animation-delay:{0.5 + 0.12 * k:.2f}s"/></g>')

best_txt = f"best day: {best[2]} on {best[0]:%b %d, %Y}" if best and best[2] else ""
updated = dt.datetime.now(dt.timezone.utc).strftime("%b %d, %Y")

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{USER}: {total} contributions in the last year, {current} day current streak, {longest} day longest streak">
<style>
.t{{font-family:{FONT}}}
.h{{font-family:{MONO};font-size:13px;fill:#60a5fa;letter-spacing:2px}}
.num{{font-family:{FONT};font-size:26px;font-weight:700;fill:#e2e8f0}}
.lbl{{font-family:{FONT};font-size:11.5px;fill:#64748b}}
.m{{font-family:{MONO};font-size:10px;fill:#475569}}
.ln{{font-family:{FONT};font-size:13px;fill:#cbd5e1}}
.lp{{font-family:{MONO};font-size:12px;fill:#60a5fa}}
.foot{{font-family:{MONO};font-size:10.5px;fill:#334155}}
.tile{{opacity:0;animation:up .7s cubic-bezier(.2,.8,.2,1) forwards}}
@keyframes up{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:none}}}}
.bar{{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:grow 1.1s cubic-bezier(.2,.8,.2,1) forwards}}
@keyframes grow{{to{{transform:scaleX(1)}}}}
.g circle{{transform-box:fill-box;transform-origin:center;animation:wave 5s ease-in-out infinite}}
@keyframes wave{{0%,100%{{transform:scale(1);filter:none}}8%{{transform:scale(1.45);filter:brightness(1.8)}}16%{{transform:scale(1)}}}}
</style>
<defs>
  <linearGradient id="lg" x1="0" x2="1"><stop offset="0" stop-color="#1d4ed8"/><stop offset="1" stop-color="#22d3ee"/></linearGradient>
  <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#131c2e"/></pattern>
</defs>
<rect width="{W}" height="{H}" rx="18" fill="#05070d"/>
<rect width="{W}" height="{H}" rx="18" fill="url(#grid)"/>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="#3b82f6" stroke-opacity=".35"/>
<text class="h" x="34" y="38">◆ GITHUB ACTIVITY</text>
<text class="h" x="680" y="38">◆ TOP LANGUAGES</text>
<line x1="656" y1="58" x2="656" y2="262" stroke="#1e293b"/>
{"".join(tile_svg)}
{"".join(months)}
<g class="g">{"".join(cells)}</g>
{"".join(lang_svg)}
<text class="foot" x="34" y="{H - 14}">{html.escape(best_txt)}</text>
<text class="foot" x="866" y="{H - 14}" text-anchor="end">updated {updated}</text>
</svg>'''

os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
open(OUT, "w", encoding="utf-8").write(svg)
print(f"{len(days)} days, {total} contributions, streak {current}/{longest}, {len(repos)} repos, langs {[k for k, _ in top]}")
