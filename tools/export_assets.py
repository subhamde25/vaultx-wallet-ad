# Export the custom design assets used in the VaultX comps: stroke icons (SVG), token glyphs (SVG),
# colour/type tokens (JSON) and an icon contact sheet (PNG).
# usage (from vaultx/): python -I tools/export_assets.py -> deliverables/assets/...
import json
import os
import sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
import vx_common as V
from fu import svg_subpaths

OUT = 'deliverables/assets'
os.makedirs(OUT + '/icons', exist_ok=True)
os.makedirs(OUT + '/tokens', exist_ok=True)

SOLID = {'bolt', 'spark', 'play'}
for key, paths in V.ICONS.items():
    fill = V.ACC if key in SOLID else 'none'
    stroke = 'none' if key in SOLID else V.ACC
    body = '\n'.join('  <path d="%s"/>' % d for d in paths)
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96" viewBox="0 0 24 24" fill="%s" stroke="%s" '
           'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">\n<title>VaultX icon: %s</title>\n%s\n</svg>\n'
           % (fill, stroke, key, body))
    open('%s/icons/vx_icon_%s.svg' % (OUT, key), 'w', encoding='utf8').write(svg)

# token glyph badges (own drawings)
tok = {
    'ETH': ('#8C9EF2', '<path d="M12 3 L17.5 12.5 L12 15.2 L6.5 12.5 Z M12 16.6 L17.5 13.9 L12 21 L6.5 13.9 Z" fill="#fff"/>'),
    'SOL': ('#A26BFF', '<path d="M8.2 6.5h11l-2.2 3h-11z M5.8 10.5h11l2.2 3h-11z M8.2 14.5h11l-2.2 3h-11z" fill="#fff"/>'),
    'BTC': ('#F7931A', '<text x="12" y="16.6" font-family="Inter" font-weight="700" font-size="13" text-anchor="middle" fill="#fff">₿</text>'),
}
for k, (col, glyph) in tok.items():
    open('%s/tokens/vx_token_%s.svg' % (OUT, k), 'w', encoding='utf8').write(
        '<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96" viewBox="0 0 24 24">\n'
        '  <circle cx="12" cy="12" r="12" fill="%s"/>\n  %s\n</svg>\n' % (col, glyph))

tokens = {'colors': {'background': V.BG, 'card': V.CARD, 'card_raised': V.CARD2, 'edge': V.EDGE, 'brand_charcoal': V.CHAR,
                     'brand_green': V.ACC, 'white': V.WHITE, 'grey': V.GREY, 'grey_dim': V.GREY2, 'negative': V.RED},
          'type': {'display': 'Inter Display Bold / SemiBold', 'ui': 'Inter Bold / SemiBold / Medium'},
          'radii_px': {'card': 28, 'chart_card': 40, 'pill': 'height / 2', 'phone': 132},
          'motion': {'ease_out': 'cubic-bezier(0.16, 1, 0.3, 1)', 'ease_in_out': 'cubic-bezier(0.65, 0, 0.35, 1)',
                     'pop': 'cubic-bezier(0.34, 1.45, 0.64, 1)', 'fps': 30, 'motion_blur': '180 deg shutter while moving'}}
json.dump(tokens, open(OUT + '/vaultx_design_tokens.json', 'w'), indent=2)

# contact sheet of the icons (drawn with PIL by sampling the bezier paths)
keys = list(V.ICONS)
cols = 7
cell = 150
rows = (len(keys) + cols - 1) // cols
sheet = Image.new('RGB', (cols * cell, rows * cell + 10), '#0B0E0B')
d = ImageDraw.Draw(sheet)


def bez(p0, p1, p2, p3, n=16):
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append(tuple((1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t * t * c + t ** 3 * e
                         for a, b, c, e in zip(p0, p1, p2, p3)))
    return pts


for i, key in enumerate(keys):
    ox, oy = (i % cols) * cell + 27, (i // cols) * cell + 14
    s = 4.0
    for dstr in V.ICONS[key]:
        closed = dstr.strip().upper().endswith('Z')
        for sub in svg_subpaths(dstr):
            pts = []
            nodes = sub + ([sub[0]] if closed else [])
            for a, b in zip(nodes, nodes[1:]):
                if a['out'] is None and b['in'] is None:
                    seg = [a['p'], b['p']]
                else:
                    seg = bez(a['p'], a['out'] or a['p'], b['in'] or b['p'], b['p'])
                pts += seg
            pts = [(ox + x * s, oy + y * s) for x, y in pts]
            if key in SOLID and closed:
                d.polygon(pts, fill=V.ACC)
            else:
                d.line(pts, fill=V.ACC, width=7, joint='curve')
    d.text((ox, oy + 102), key, fill='#8C968C')
sheet.save(OUT + '/vaultx_icons_contact_sheet.png')
print(len(keys), 'icons,', len(tok), 'tokens ->', OUT)
