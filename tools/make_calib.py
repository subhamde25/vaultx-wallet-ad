# Calibration comp: checks mask sizes, CornerRadius, Text+ Size, polyline coordinate space and eased motion blur.
# usage (from vaultx/): python -I tools/make_calib.py  -> build/comps/T00_Calibration.comp
import os
import re
import sys
sys.path.insert(0, os.path.dirname(__file__))
from fu import Comp, Anim, AnimXY, Conn, FuID, hexrgb, svg_subpaths, bbox, polyline_value

os.makedirs('build/comps', exist_ok=True)
c = Comp('T00_Calibration', 60)
W, H = 1920, 1080


def bg(name, col, mask=None, pos=None):
    r, g, b, a = hexrgb(col)
    return c.add('Background', name, {
        'UseFrameFormatSettings': 1, 'Width': W, 'Height': H,
        'TopLeftRed': r, 'TopLeftGreen': g, 'TopLeftBlue': b, 'TopLeftAlpha': a,
        'EffectMask': Conn(mask, 'Mask') if mask else None}, pos)


def merge(name, b, f, pos=None, **kw):
    d = {'Background': Conn(b), 'Foreground': Conn(f), 'PerformDepthMerge': 0}
    d.update(kw)
    return c.add('Merge', name, d, pos)


base = bg('BG', '#101410')
rm = c.add('RectangleMask', 'RectMask', {'UseFrameFormatSettings': 1, 'MaskWidth': W, 'MaskHeight': H,
                                         'Center': (0.25, 0.5), 'Width': 0.2, 'Height': 0.2, 'CornerRadius': 0.5})
card = bg('Card', '#FFFFFF', rm)
m = merge('M_Card', base, card)

t = c.add('TextPlus', 'Txt_H', {'UseFrameFormatSettings': 1, 'Width': W, 'Height': H, 'StyledText': 'HHxg',
                                'Font': 'Inter', 'Style': 'Bold', 'Size': 0.1, 'Center': (0.65, 0.75)})
m = merge('M_Txt', m, t)
t2 = c.add('TextPlus', 'Txt_Display', {'UseFrameFormatSettings': 1, 'Width': W, 'Height': H, 'StyledText': 'Display 72',
                                       'Font': 'Inter Display', 'Style': 'Bold', 'Size': 0.05, 'Center': (0.65, 0.92)})
m = merge('M_Txt2', m, t2)

tri = c.add('PolylineMask', 'Tri', {'UseFrameFormatSettings': 1, 'MaskWidth': W, 'MaskHeight': H,
                                    'Polyline': polyline_value([{'p': (0, 0), 'in': None, 'out': None},
                                                                {'p': (0.1, 0), 'in': None, 'out': None},
                                                                {'p': (0, 0.1), 'in': None, 'out': None}],
                                                               lambda x, y: (x, y))})
m = merge('M_Tri', m, bg('TriFill', '#91C950', tri))

# logo polygons, 600 px wide, top-left at (660, 820) px
svg = open('brandkit/Logo.svg', encoding='utf8').read()
paths = re.findall(r'<path class="(cls-\d)" d="([^"]+)"', svg)
S = 600 / 171.69
X0, Y0 = 660, 820


def to_norm(x, y):
    px, py = X0 + S * x, Y0 + S * y
    return (px - W / 2) / W, (H / 2 - py) / W


for pi, (cls, d) in enumerate(paths):
    subs = svg_subpaths(d)
    prev = None
    boxes = []
    for si, s in enumerate(subs):
        bb = bbox(s)
        inside = any(bb[0] >= o[0] and bb[1] >= o[1] and bb[2] <= o[2] and bb[3] <= o[3] for o in boxes)
        boxes.append(bb)
        prev = c.add('PolylineMask', 'Logo_p%d_s%d' % (pi, si), {
            'UseFrameFormatSettings': 1, 'MaskWidth': W, 'MaskHeight': H,
            'PaintMode': FuID('Subtract') if inside else None,
            'EffectMask': Conn(prev, 'Mask') if prev else None,
            'Polyline': polyline_value(s, to_norm)})
    m = merge('M_Logo%d' % pi, m, bg('LogoFill%d' % pi, '#91C950' if cls == 'cls-1' else '#FFFFFF', prev))

# eased moving bar with motion blur
bar_m = c.add('RectangleMask', 'BarMask', {'UseFrameFormatSettings': 1, 'MaskWidth': W, 'MaskHeight': H,
                                           'Center': (0.5, 0.5), 'Width': 0.02, 'Height': 0.15, 'CornerRadius': 0})
bar = bg('Bar', '#FFFFFF', bar_m)
xf = c.add('Transform', 'Bar_Move', {'Input': Conn(bar), 'Center': AnimXY([(0, (0.45, 0.62)), (20, (0.95, 0.62))], 'out'),
                                     'MotionBlur': 1, 'Quality': 8, 'ShutterAngle': 180})
m = merge('M_Bar', m, xf)
c.add('MediaOut', 'MediaOut1', {'Index': '0', 'Input': Conn(m)})
print(c.save('build/comps/T00_Calibration.comp'), len(c.tools), 'tools')
