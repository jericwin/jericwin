"""Put the Platane/snk snake inside the same dark card as the other assets.

usage: python scripts/wrap_snake.py <snake.svg>   (rewrites in place)
"""
import re
import sys

path = sys.argv[1]
s = open(path, encoding="utf-8").read()
m = re.match(r'\s*<svg([^>]*)>(.*)</svg>\s*$', s, re.S)
attrs, body = m.group(1), m.group(2)
vb = re.search(r'viewBox="([^"]+)"', attrs).group(1)
_, _, vw, vh = (float(v) for v in vb.split())

W = 900
iw = W - 40
ih = iw * vh / vw
H = ih + 64

out = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H:.0f}" viewBox="0 0 {W} {H:.0f}">
<style>.h{{font-family:'JetBrains Mono','Fira Code',Consolas,monospace;font-size:13px;fill:#60a5fa;letter-spacing:2px}}</style>
<rect width="{W}" height="{H:.0f}" rx="18" fill="#05070d"/>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1:.0f}" rx="18" fill="none" stroke="#3b82f6" stroke-opacity=".35"/>
<text class="h" x="34" y="38">◆ CONTRIBUTION SNAKE</text>
<svg x="20" y="44" width="{iw}" height="{ih:.0f}" viewBox="{vb}">{body}</svg>
</svg>'''
open(path, "w", encoding="utf-8").write(out)
