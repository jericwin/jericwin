"""Generate an animated dot-portrait hero SVG for the GitHub profile README.

usage: python make_svg.py <photo.png> <out.svg> [cutout.png]
"""
import random
import sys

import numpy as np
from PIL import Image, ImageFilter

photo, out = sys.argv[1], sys.argv[2]
cut = sys.argv[3] if len(sys.argv) > 3 else None

W, H = 900, 420           # whole banner
PX, PY, PW, PH = 30, 20, 330, 380   # portrait box
STEP = 5.0                # dot grid pitch
RMAX = STEP * 0.5

im = Image.open(photo).convert("RGB")
w0, h0 = im.size
# head-and-shoulders crop, matching the portrait box aspect ratio
cx, top = w0 * 0.5, h0 * 0.10
ch = h0 * 0.62
cw = ch * PW / PH
box = (int(cx - cw / 2), int(top), int(cx + cw / 2), int(top + ch))

cols, rows = int(PW / STEP), int(PH / STEP)
lum = np.asarray(im.crop(box).convert("L").filter(ImageFilter.UnsharpMask(4, 160, 2))
                 .resize((cols, rows), Image.LANCZOS), dtype=float) / 255

if cut:
    alpha = Image.open(cut).convert("RGBA").split()[-1]
    alpha = alpha.resize(im.size)
    mask = np.asarray(alpha.crop(box).resize((cols, rows), Image.LANCZOS), dtype=float) / 255
else:
    mask = np.ones_like(lum)

# stretch levels so skin pops and the backdrop falls away
lo, hi = np.percentile(lum[mask > 0.5], [8, 99.8])
v = np.clip((lum - lo) / (hi - lo), 0, 1) ** 1.7

random.seed(7)
dots = []
for j in range(rows):
    for i in range(cols):
        m = mask[j, i]
        if m < 0.35:
            continue
        b = v[j, i]
        r = RMAX * (0.18 + 0.82 * b)  # silhouette always shows faint dots
        x = PX + (i + 0.5) * STEP + (STEP / 2 if j % 2 else 0) * 0.5
        y = PY + (j + 0.5) * STEP
        dots.append((x, y, r, b))

def blue(b):
    # deep navy -> ice blue
    c0, c1 = np.array([23, 37, 84]), np.array([199, 225, 255])
    c = c0 + (c1 - c0) * (b ** 0.9)
    return "#%02x%02x%02x" % tuple(int(t) for t in c)

ccx, ccy = PX + PW / 2, PY + PH / 2
parts = []
for x, y, r, b in dots:
    ang = random.uniform(0, 6.283)
    dist = random.uniform(120, 420)
    dx, dy = np.cos(ang) * dist, np.sin(ang) * dist
    # assemble from the centre outwards, brighter dots a touch earlier
    d = (((x - ccx) ** 2 + (y - ccy) ** 2) ** 0.5) / 260 * 1.4 + random.uniform(0, 0.35)
    parts.append(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{blue(b)}" '
        f'style="--x:{dx:.0f}px;--y:{dy:.0f}px;animation-delay:{d:.2f}s"/>'
    )

FONT = "'Segoe UI',Ubuntu,'Helvetica Neue',Arial,sans-serif"
MONO = "'JetBrains Mono','Fira Code',Consolas,monospace"
roles = ["Data Analyst", "Software Developer", "AI Enthusiast"]
role_svg = "".join(
    f'<text class="role r{k}" x="400" y="232">&gt; {t}</text>' for k, t in enumerate(roles)
)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Jeric Punay — animated dot portrait">
<style>
.d circle{{transform-box:fill-box;transform-origin:center;opacity:0;
  animation:form 12s cubic-bezier(.2,.8,.2,1) infinite}}
@keyframes form{{
  0%{{opacity:0;transform:translate(var(--x),var(--y)) scale(.2)}}
  22%{{opacity:1;transform:none}}
  84%{{opacity:1;transform:none}}
  100%{{opacity:0;transform:translate(var(--x),var(--y)) scale(.2)}}}}
.scan{{animation:scan 4s linear infinite}}
@keyframes scan{{0%{{transform:translateY(0)}}100%{{transform:translateY({PH}px)}}}}
.t{{font-family:{FONT};fill:#e6edf3}}
.hi{{font-size:22px;fill:#94a3b8}}
.name{{font-size:52px;font-weight:700}}
.role{{font-family:{MONO};font-size:22px;fill:#60a5fa;opacity:0;animation:role 9s infinite}}
.r1{{animation-delay:3s}}.r2{{animation-delay:6s}}
@keyframes role{{0%,2%{{opacity:0;transform:translateY(8px)}}6%,30%{{opacity:1;transform:none}}34%,100%{{opacity:0;transform:translateY(-8px)}}}}
.tag{{font-size:16px;fill:#94a3b8;font-style:italic}}
.fade{{opacity:0;animation:in 1s ease-out .4s forwards}}
@keyframes in{{to{{opacity:1}}}}
.pulse{{animation:pulse 2s ease-in-out infinite}}
@keyframes pulse{{50%{{opacity:.25}}}}
</style>
<defs>
  <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
    <circle cx="1" cy="1" r="1" fill="#172033"/>
  </pattern>
  <linearGradient id="beam" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#60a5fa" stop-opacity="0"/>
    <stop offset="1" stop-color="#60a5fa" stop-opacity=".14"/>
  </linearGradient>
  <clipPath id="pbox"><rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="14"/></clipPath>
</defs>
<rect width="{W}" height="{H}" rx="18" fill="#05070d"/>
<rect width="{W}" height="{H}" rx="18" fill="url(#grid)"/>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="18" fill="none" stroke="#3b82f6" stroke-opacity=".35"/>
<g class="d">{"".join(parts)}</g>
<g clip-path="url(#pbox)"><rect class="scan" x="{PX}" y="{PY-40}" width="{PW}" height="40" fill="url(#beam)"/></g>
<g class="fade">
  <text class="t hi" x="400" y="132">Hi 👋, I'm</text>
  <text class="t name" x="398" y="190">Jeric Punay</text>
  {role_svg}
  <rect class="pulse" x="400" y="248" width="60" height="3" rx="1.5" fill="#3b82f6"/>
  <text class="t tag" x="400" y="296">Turning data into insights</text>
  <text class="t tag" x="400" y="320">and ideas into impactful software.</text>
  <circle class="pulse" cx="406" cy="366" r="5" fill="#3b82f6"/>
  <text class="t" x="420" y="371" style="font-size:14px;fill:#94a3b8;font-family:{MONO}">open to collaborate</text>
</g>
</svg>'''

open(out, "w", encoding="utf-8").write(svg)
print(f"{len(dots)} dots, {len(svg)/1024:.0f} KB")
