"""Build assets/techstack.svg — tech stack card with inlined skillicons.

usage: python scripts/gen_techstack.py <out.svg>
"""
import html
import re
import sys
import urllib.request

OUT = sys.argv[1]
STACK = [
    ("Languages", "python,cs,java,js,ts,php,kotlin"),
    ("Frontend", "html,css,react,nextjs,tailwind"),
    ("Backend", "nodejs,flask,dotnet"),
    ("Databases", "mysql,postgres,mongodb,sqlite"),
    ("AI / ML", "tensorflow,pytorch"),
    ("Cloud & DevOps", "aws,azure,docker,kubernetes"),
    ("Tools", "git,github,vscode,figma"),
]
FONT = "'Segoe UI',Ubuntu,'Helvetica Neue',Arial,sans-serif"
MONO = "'JetBrains Mono','Fira Code',Consolas,monospace"
W, ICON, GAP = 900, 40, 10
COLX, ROW0, ROWH = (34, 470), 74, 86


def icon(name, uid):
    """Fetch one icon and namespace its ids so inlined icons don't collide."""
    req = urllib.request.Request(f"https://skillicons.dev/icons?i={name}&theme=dark",
                                 headers={"User-Agent": "profile-techstack"})
    s = urllib.request.urlopen(req, timeout=30).read().decode()
    inner = re.search(r"<g[^>]*>\s*(<svg.*</svg>)\s*</g>", s, re.S).group(1)
    for i in set(re.findall(r'id="([^"]+)"', inner)):
        inner = (inner.replace(f'id="{i}"', f'id="{uid}{i}"')
                 .replace(f"url(#{i})", f"url(#{uid}{i})")
                 .replace(f'href="#{i}"', f'href="#{uid}{i}"'))
    return inner


blocks, n = [], 0
for k, (label, names) in enumerate(STACK):
    cx, cy = COLX[k % 2], ROW0 + (k // 2) * ROWH
    parts = [f'<text class="lbl" x="{cx}" y="{cy}">{html.escape(label.upper())}</text>']
    for j, nm in enumerate(names.split(",")):
        x = cx + j * (ICON + GAP)
        svg = icon(nm, f"i{n}_")
        svg = re.sub(r'width="256" height="256"', f'width="{ICON}" height="{ICON}"', svg, count=1)
        parts.append(
            f'<g class="ic" style="animation-delay:{0.06 * n:.2f}s">'
            f'<g transform="translate({x},{cy + 12})">{svg}</g></g>')
        n += 1
    blocks.append("".join(parts))

# last free cell: what I'm learning now
lx, ly = COLX[1], ROW0 + 3 * ROWH
learning = (f'<text class="lbl" x="{lx}" y="{ly}">CURRENTLY LEARNING</text>'
            f'<text class="term" x="{lx}" y="{ly + 30}">$ learn --now</text>'
            f'<text class="term2" x="{lx}" y="{ly + 50}">ai · machine learning · cloud · k8s'
            f'<tspan class="cur">▌</tspan></text>')
H = ROW0 + 4 * ROWH - 8

out = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Tech stack">
<style>
.h{{font-family:{MONO};font-size:13px;fill:#60a5fa;letter-spacing:2px}}
.lbl{{font-family:{MONO};font-size:11px;fill:#64748b;letter-spacing:1.5px}}
.term{{font-family:{MONO};font-size:13px;fill:#60a5fa}}
.term2{{font-family:{MONO};font-size:13px;fill:#cbd5e1}}
.cur{{fill:#60a5fa;animation:blink 1s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
.ic{{opacity:0;animation:pop .6s cubic-bezier(.2,.9,.3,1.3) forwards}}
@keyframes pop{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
.sweep{{animation:sweep 7s ease-in-out infinite}}
@keyframes sweep{{0%{{transform:translateX(-300px)}}60%,100%{{transform:translateX({W + 300}px)}}}}
</style>
<defs>
  <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#131c2e"/></pattern>
  <linearGradient id="sw" x1="0" x2="1"><stop offset="0" stop-color="#3b82f6" stop-opacity="0"/><stop offset=".5" stop-color="#3b82f6" stop-opacity=".07"/><stop offset="1" stop-color="#3b82f6" stop-opacity="0"/></linearGradient>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>
</defs>
<rect width="{W}" height="{H}" rx="18" fill="#05070d"/>
<rect width="{W}" height="{H}" rx="18" fill="url(#grid)"/>
<g clip-path="url(#card)"><rect class="sweep" x="0" y="0" width="220" height="{H}" fill="url(#sw)"/></g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="#3b82f6" stroke-opacity=".35"/>
<text class="h" x="34" y="38">◆ TECH STACK</text>
{"".join(blocks)}
{learning}
</svg>'''
open(OUT, "w", encoding="utf-8").write(out)
print(f"{n} icons, {len(out) // 1024} KB")
