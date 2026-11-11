"""Shared design system for the VaultX Wallet ad (Fusion comps for DaVinci Resolve).

Global timeline: 1920x1080, 30 fps, 1350 frames (45 s). The voiceover sits at +0.2 s.
Every comp is generated with its global start frame (g0) so the background drift is continuous across cuts.
"""
import os
import re
from PIL import ImageFont

from fu import Comp, Anim, AnimXY, Conn, FuID, hexrgb, svg_subpaths
from kit import Kit, COL_W, ROW_H

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS = 30
VO_OFF = 0.20
TOTAL = 1350
PHONE_RES = 0.5      # phone canvas renders at half its authoring size (it never shows larger than ~450 px)

# ---------------------------------------------------------------- palette / type
BG = '#0B0E0B'
CARD = '#151A15'
CARD2 = '#1C221C'
EDGE = '#2B332B'
CHAR = '#3E433E'      # brand charcoal (from the logo files)
ACC = '#91C950'       # brand green
ACC_D = '#5E8A2E'
WHITE = '#FFFFFF'
GREY = '#8C968C'
GREY2 = '#5D665D'
RED = '#E5484D'
BTC_C, ETH_C, SOL_C = '#F7931A', '#8C9EF2', '#A26BFF'

DISPLAY = ('Inter Display', 'Bold')
FONT_FILES = {('Inter Display', 'Bold'): 'InterDisplay-Bold.ttf', ('Inter Display', 'SemiBold'): 'InterDisplay-SemiBold.ttf',
              ('Inter Display', 'ExtraBold'): 'InterDisplay-ExtraBold.ttf', ('Inter Display', 'Medium'): 'InterDisplay-Medium.ttf',
              ('Inter', 'Bold'): 'Inter-Bold.ttf', ('Inter', 'SemiBold'): 'Inter-SemiBold.ttf',
              ('Inter', 'Medium'): 'Inter-Medium.ttf', ('Inter', 'Regular'): 'Inter-Regular.ttf',
              ('Inter', 'ExtraBold'): 'Inter-ExtraBold.ttf'}
CAP_RATIO = 0.728
_fonts = {}


def text_w(s, cap, font=DISPLAY, track=1.0):
    """Approximate rendered width in px of string s at cap height cap."""
    if font not in _fonts:
        _fonts[font] = ImageFont.truetype(os.path.join(ROOT, 'assets', 'fonts', FONT_FILES[font]), 1000)
    em = cap / CAP_RATIO
    w = _fonts[font].getlength(s) * em / 1000
    if track != 1.0:
        w += (track - 1.0) * em * max(len(s) - 1, 0)
    return w


# ---------------------------------------------------------------- VO word times (seconds in the VO file)
W = dict(crypto=0.00, moves=0.38, fast=0.70, your=1.70, wallet=1.90, should=2.24, too=2.62,
         meet=3.52, vaultx=3.68, wallet2=4.24, the=4.92, smarter=5.02, way=5.38, manage=5.84, grow=6.44,
         protect=7.12, your2=7.56, digital=7.78, assets=8.18,
         instant=8.98, transactions=9.40, lightning=10.82, fast2=11.62, swaps=11.94,
         real=12.76, portfolio=13.36, tracking=14.02, interactive=14.74, performance=15.30, charts=15.86,
         set=17.00, price=17.24, alerts=17.72, analyze=18.66, trends=18.94,
         make=20.24, confident=20.44, decisions=21.02, powerful=21.88, insights=22.30, built=22.82,
         dashboard=23.98, and_=24.92, bank=25.22, level=25.48, encryption=25.78, biometric=26.84,
         security=27.36, your3=28.48, assets2=28.60, stay=28.98, protected=29.42, every=29.92, step=30.40,
         way2=31.04, whether=31.90, investing=32.60, trading=33.52, holding=34.30, long=34.68, term=35.02,
         vaultx2=36.30, keeps=36.80, you=37.16, ahead=37.40, download=38.54, vaultx3=39.00, wallet3=39.72,
         today=40.00, own=41.06, your4=41.26, crypto2=41.58, journey=41.98, end=42.55)

SCENES = [
    ('C01_Hook_Crypto_Moves_Fast', 0, 105),
    ('C02_Logo_Reveal_Value_Prop', 105, 267),
    ('C03_Instant_Transactions_Swaps', 267, 381),
    ('C04_Portfolio_Chart', 381, 507),
    ('C05_Price_Alerts_Trends', 507, 606),
    ('C06_Dashboard_Insights', 606, 747),
    ('C07_Security_Encryption_Biometric', 747, 948),
    ('C08_Investing_Trading_Holding', 948, 1146),
    ('C09_EndCard_CTA', 1146, 1350),
]


def gf(sec):
    """global frame for a global time in seconds"""
    return int(round(sec * FPS))


def vf(word):
    """global frame where a VO word starts"""
    return gf(W[word] + VO_OFF)


# ---------------------------------------------------------------- scene wrapper
class Scene:
    def __init__(self, idx):
        self.name, self.g0, self.g1 = SCENES[idx]
        self.n = self.g1 - self.g0
        self.c = Comp(self.name, self.n)
        self.k = Kit(self.c, x0=0, y0=0)
        self.spine_y = 1500
        self.spine_x = None
        self.layers = []

    def L(self, g):
        """local frame for a global frame"""
        return g - self.g0

    def v(self, word, d=0):
        """local frame of a VO word (+d frames)"""
        return vf(word) - self.g0 + d

    def A(self, keys, ease='out'):
        """Anim with GLOBAL frames"""
        return Anim([(self.L(t), v) for t, v in keys], ease)

    def add_layer(self, node, **kw):
        self.layers.append((node, kw))

    def finish(self, camera=None):
        k = self.k
        k.end_section()
        # spine: merge all layers in order under the last columns
        cur = self.layers[0][0]
        x = 0
        for i, (node, kw) in enumerate(self.layers[1:]):
            kw = dict(kw)
            cur = k.over('Comp_%02d' % (i + 1), cur, node, pos=(x, self.spine_y), **kw)
            x += COL_W
        if camera:
            cur = self.c.add('Transform', 'CAMERA', dict(Input=Conn(cur), **camera), (x, self.spine_y))
            x += COL_W
        cur = grain(self, cur, (x, self.spine_y))
        x += COL_W
        self.c.add('MediaOut', 'MediaOut1', {'Index': '0', 'Input': Conn(cur)}, (x + COL_W, self.spine_y))
        self.c.underlay('OUTPUT SPINE - layers merged left to right, then camera, grain, MediaOut',
                        -55, self.spine_y - 40, x + COL_W * 2 + 20, 90, (0.35, 0.2, 0.2))
        path = os.path.join(ROOT, 'build', 'comps', self.name + '.comp')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.c.save(path)
        return path


# ---------------------------------------------------------------- background (continuous across comps)
def background(sc, dim=None):
    """Cheap, continuous background: radial-gradient glows (no soft masks), line grid, radial vignette."""
    k = sc.k
    k.section('BG_Base_Glows')
    base = k.canvas('BG_Base', BG, 1.0)
    g0 = -sc.g0
    g1 = TOTAL - sc.g0

    def moving(p0, p1, r):
        return (AnimXY([(g0, p0), (g1, p1)], 'linear'),
                AnimXY([(g0, (p0[0] + r, p0[1])), (g1, (p1[0] + r, p1[1]))], 'linear'))
    sA, eA = moving((620, 330), (1330, 700), 980)
    glowA = k.gradient('BG_GlowA_Green', [(0, ACC, 0.15), (0.45, ACC, 0.05), (1, ACC, 0.0)], 'Radial', sA, eA)
    sB, eB = moving((1560, 930), (420, 260), 900)
    glowB = k.gradient('BG_GlowB_Charcoal', [(0, CHAR, 0.6), (1, CHAR, 0.0)], 'Radial', sB, eB)
    cur = k.over('BG_AddGlowA', base, glowA)
    cur = k.over('BG_AddGlowB', cur, glowB)

    k.section('BG_Grid')
    step = 96
    xs = list(range(48, 1920, step))
    ys = list(range(12, 1080, step))
    vpts = []
    for i, x in enumerate(xs):
        a, b = (-20, 1100) if i % 2 == 0 else (1100, -20)
        vpts += [(x, a), (x, b)]
    hpts = []
    for i, y in enumerate(ys):
        a, b = (-20, 1960) if i % 2 == 0 else (1960, -20)
        hpts += [(a, y), (b, y)]
    vm = k.poly_mask('BG_GridV', vpts, closed=False, border=1.2)
    hm = k.poly_mask('BG_GridH', hpts, closed=False, border=1.2, inp=vm)
    grid = k.gradient('BG_Grid_Lines', [(0, WHITE, 0.055), (0.7, WHITE, 0.02), (1, WHITE, 0.0)], 'Radial',
                      (960, 470), (960 + 1000, 470), hm)
    grid = k.freeze('BG_Grid', grid)
    gridm = k.xf('BG_Grid_Drift', grid, dx=Anim([(g0, 0), (g1, -step)], 'linear'),
                 dy=Anim([(g0, 0), (g1, -step / 2)], 'linear'), mb=False)
    cur = k.over('BG_AddGrid', cur, gridm)

    k.section('BG_Vignette')
    vig = k.gradient('BG_Vignette_Dark', [(0, '#000000', 0.0), (0.55, '#000000', 0.0), (1, '#000000', 0.7)], 'Radial',
                     (960, 540), (960 + 1150, 540))
    cur = k.over('BG_AddVignette', cur, vig)
    if dim is not None:
        dm = k.fill('BG_Dim', '#000000', None, 1.0)
        cur = k.over('BG_DimForSecurity', cur, dm, blend=dim)
    sc.add_layer(cur)
    return cur


def grain(sc, inp, pos):
    c = sc.c
    n = c.add('FastNoise', 'GRAIN_Noise', {'UseFrameFormatSettings': 1, 'Width': 1920, 'Height': 1080,
                                           'Detail': 1, 'Contrast': 2.2, 'XScale': 220, 'SeetheRate': 4.0},
              (pos[0], pos[1] - 66))
    return c.add('Merge', 'GRAIN_Overlay', {'Background': Conn(inp), 'Foreground': Conn(n), 'PerformDepthMerge': 0,
                                            'ApplyMode': FuID('Overlay'), 'Blend': 0.035}, pos)


# ---------------------------------------------------------------- kinetic headline
def headline(sc, name, lines, x, y, cap, t_in, t_out=None, align='left', font=DISPLAY, hl=(), stagger=3,
             rise=1.55, dur=16, out_dur=10, color=WHITE, gap=1.18, word_times=None, kit=None, track=1.0):
    """Word-by-word masked rise. t_in/t_out are LOCAL frames. word_times: optional list of local frames per word.
    Each line is clipped by its own window (cap top .. descender), so waiting words stay hidden.
    Returns (group_node, None) - the group is already clipped."""
    k = kit or sc.k
    k.section('HL_' + name)
    grp = k.canvas(name + '_Canvas')
    idx = 0
    for li, line in enumerate(lines):
        words = line.split(' ')
        yl = y + li * cap * (1 + gap)
        sp = text_w(' ', cap, font) * 0.82          # Fusion kerns tighter than the PIL measure
        widths = [text_w(w_, cap, font, track) for w_ in words]
        total = sum(widths) + sp * (len(words) - 1)
        x0 = {'left': x, 'center': x - total / 2, 'right': x - total}[align]
        clip = k.rect_mask('%s_Clip%d' % (name, li), x0 - cap * 0.5, yl - cap * 0.66, total + cap * 1.0, cap * 1.52)
        lg = k.canvas('%s_Line%d' % (name, li))
        cx = x0
        for wi, (word, ww) in enumerate(zip(words, widths)):
            t0 = word_times[idx] if word_times else t_in + idx * stagger
            col = ACC if (word in hl or word.strip('.,') in hl) else color
            t = k.text('%s_W%02d_%s' % (name, idx + 1, re.sub(r'\W', '', word) or 'w'), word, cx, yl, cap, col,
                       font[0], font[1], 'left', track)
            r = cap * rise
            d_ = dur if t_out is None else max(5, min(dur, t_out + idx - t0 - 2))
            keys = [(t0, r), (t0 + d_, 0)]
            ease = ['out']
            if t_out is not None:
                to = max(t_out + idx, t0 + d_ + 1)
                keys += [(to, 0), (to + out_dur, -r)]
                ease += ['linear', 'in']
            mv = k.xf('%s_W%02d_Rise' % (name, idx + 1), t, dy=Anim(keys, ease))
            lg = k.over('%s_W%02d_Add' % (name, idx + 1), lg, mv)
            cx += ww + sp
            idx += 1
        grp = k.over('%s_Line%d_Clipped' % (name, li), grp, lg, mask=clip)
    return grp, None


# ---------------------------------------------------------------- icons (own 24-unit stroke drawings)
ICONS = {
    'wallet': ['M3.5,8 C3.5,6.6 4.6,5.5 6,5.5 L18,5.5 C19.4,5.5 20.5,6.6 20.5,8 L20.5,17 C20.5,18.4 19.4,19.5 18,19.5 L6,19.5 C4.6,19.5 3.5,18.4 3.5,17 Z',
               'M20.5,10.5 L16,10.5 C14.9,10.5 14,11.4 14,12.5 C14,13.6 14.9,14.5 16,14.5 L20.5,14.5'],
    'send': ['M6.5,17.5 L17.5,6.5', 'M9,6.5 L17.5,6.5 L17.5,15'],
    'swap': ['M4,8.5 L19,8.5', 'M15,4.5 L19,8.5 L15,12.5', 'M20,15.5 L5,15.5', 'M9,11.5 L5,15.5 L9,19.5'],
    'chart': ['M3.5,16.5 L9,11 L13,14.5 L20.5,7', 'M15,7 L20.5,7 L20.5,12.5'],
    'shield': ['M12,2.8 L19.5,5.8 L19.5,11.3 C19.5,16 16.4,19.8 12,21.2 C7.6,19.8 4.5,16 4.5,11.3 L4.5,5.8 Z'],
    'shieldcheck': ['M12,2.8 L19.5,5.8 L19.5,11.3 C19.5,16 16.4,19.8 12,21.2 C7.6,19.8 4.5,16 4.5,11.3 L4.5,5.8 Z',
                    'M8.6,12 L11,14.4 L15.6,9.6'],
    'bell': ['M6.5,16.5 L6.5,11 C6.5,7.9 9,5.5 12,5.5 C15,5.5 17.5,7.9 17.5,11 L17.5,16.5 L19.5,18.3 L4.5,18.3 Z',
             'M10.2,20.6 C10.6,21.4 11.2,21.8 12,21.8 C12.8,21.8 13.4,21.4 13.8,20.6', 'M12,3 L12,5.5'],
    'bars': ['M5,20 L5,13', 'M10,20 L10,8', 'M15,20 L15,11', 'M20,20 L20,5'],
    'check': ['M5.5,12.5 L10,17 L18.5,7.5'],
    'lock': ['M6,11 L18,11 C19.1,11 20,11.9 20,13 L20,19 C20,20.1 19.1,21 18,21 L6,21 C4.9,21 4,20.1 4,19 L4,13 C4,11.9 4.9,11 6,11 Z',
             'M8,11 L8,7.5 C8,5.3 9.8,3.5 12,3.5 C14.2,3.5 16,5.3 16,7.5 L16,11'],
    'bolt': ['M13,2.5 L5.5,13.5 L11.5,13.5 L10.5,21.5 L18.5,10 L12.5,10 Z'],
    'spark': ['M12,3 C12.6,8.2 15.8,11.4 21,12 C15.8,12.6 12.6,15.8 12,21 C11.4,15.8 8.2,12.6 3,12 C8.2,11.4 11.4,8.2 12,3 Z'],
    'trend': ['M3.5,17.5 L9,12 L13,15 L20.5,7.5', 'M15.5,7.5 L20.5,7.5 L20.5,12.5'],
    'candles': ['M7,4.5 L7,19.5', 'M5,8 L9,8 L9,15 L5,15 Z', 'M17,3.5 L17,17.5', 'M15,6 L19,6 L19,14 L15,14 Z'],
    'vault': ['M4,5.5 C4,4.4 4.9,3.5 6,3.5 L18,3.5 C19.1,3.5 20,4.4 20,5.5 L20,18.5 C20,19.6 19.1,20.5 18,20.5 L6,20.5 C4.9,20.5 4,19.6 4,18.5 Z',
              'M12,8 C14.2,8 16,9.8 16,12 C16,14.2 14.2,16 12,16 C9.8,16 8,14.2 8,12 C8,9.8 9.8,8 12,8 Z', 'M12,12 L14.5,9.5'],
    'download': ['M12,3.5 L12,15', 'M7.5,10.5 L12,15 L16.5,10.5', 'M4.5,19.5 L19.5,19.5'],
    'arrowup': ['M12,19 L12,5', 'M6.5,10.5 L12,5 L17.5,10.5'],
    'arrowright': ['M5,12 L19,12', 'M13,6 L19,12 L13,18'],
    'back': ['M14.5,6 L8.5,12 L14.5,18'],
    'home': ['M4,11 L12,4.5 L20,11', 'M6.5,9.5 L6.5,19.5 L17.5,19.5 L17.5,9.5'],
    'grid': ['M4,4 L10,4 L10,10 L4,10 Z', 'M14,4 L20,4 L20,10 L14,10 Z', 'M4,14 L10,14 L10,20 L4,20 Z', 'M14,14 L20,14 L20,20 L14,20 Z'],
    'user': ['M12,4 C14.2,4 16,5.8 16,8 C16,10.2 14.2,12 12,12 C9.8,12 8,10.2 8,8 C8,5.8 9.8,4 12,4 Z',
             'M4.5,20 C5.2,16.4 8.2,14 12,14 C15.8,14 18.8,16.4 19.5,20'],
    'play': ['M8,5 L19,12 L8,19 Z'],
    'phone': ['M8,2.5 L16,2.5 C17.1,2.5 18,3.4 18,4.5 L18,19.5 C18,20.6 17.1,21.5 16,21.5 L8,21.5 C6.9,21.5 6,20.6 6,19.5 L6,4.5 C6,3.4 6.9,2.5 8,2.5 Z', 'M10.5,18.5 L13.5,18.5'],
}


def _icon_paths(key):
    out = []
    for d in ICONS[key]:
        closed = d.strip().upper().endswith('Z')
        for s in svg_subpaths(d):
            out.append((s, closed))
    return out


def icon_masks(k, name, key, cx, cy, size, stroke=None, write_on=None):
    """Stroke icon centred at (cx,cy) px, size px. Returns chained mask."""
    sc_ = size / 24.0
    stroke = stroke if stroke is not None else 2.0 * sc_
    prev = None
    T = lambda q: None if q is None else (cx + (q[0] - 12) * sc_, cy + (q[1] - 12) * sc_)
    for i, (s, closed) in enumerate(_icon_paths(key)):
        nodes = [{'p': T(n['p']), 'in': T(n['in']), 'out': T(n['out'])} for n in s]
        prev = k.poly_mask('%s_%s%d' % (name, key, i), nodes, closed, inp=prev, border=stroke, write_on=write_on)
    return prev


def icon(k, name, key, cx, cy, size, color=ACC, stroke=None, write_on=None, alpha=1.0):
    m = icon_masks(k, name, key, cx, cy, size, stroke, write_on)
    return k.fill(name + '_Icon', color, m, alpha)


def icon_solid(k, name, key, cx, cy, size, color=ACC):
    """Filled version (for bolt / spark / play)."""
    sc_ = size / 24.0
    prev = None
    T = lambda q: None if q is None else (cx + (q[0] - 12) * sc_, cy + (q[1] - 12) * sc_)
    for i, (s, closed) in enumerate(_icon_paths(key)):
        nodes = [{'p': T(n['p']), 'in': T(n['in']), 'out': T(n['out'])} for n in s]
        prev = k.poly_mask('%s_%s_fill%d' % (name, key, i), nodes, True, inp=prev)
    return k.fill(name + '_Solid', color, prev)


# ---------------------------------------------------------------- tokens
def token(k, name, sym, cx, cy, r):
    """coin badge: coloured disc with glyph"""
    col = {'BTC': BTC_C, 'ETH': ETH_C, 'SOL': SOL_C}[sym]
    m = k.ellipse_mask(name + '_Disc', cx, cy, r)
    disc = k.fill(name + '_DiscFill', col, m)
    if sym == 'BTC':
        g = k.text(name + '_Glyph', '₿', cx, cy, r * 0.95, WHITE, 'Inter', 'Bold', 'center')
    elif sym == 'ETH':
        s = r / 12.0
        top = [(cx, cy - 9 * s), (cx + 5.5 * s, cy + 0.5 * s), (cx, cy + 3.2 * s), (cx - 5.5 * s, cy + 0.5 * s)]
        bot = [(cx, cy + 4.6 * s), (cx + 5.5 * s, cy + 1.9 * s), (cx, cy + 9 * s), (cx - 5.5 * s, cy + 1.9 * s)]
        m1 = k.poly_mask(name + '_EthTop', top)
        m2 = k.poly_mask(name + '_EthBot', bot, inp=m1)
        g = k.fill(name + '_EthGlyph', WHITE, m2)
    else:
        s = r / 12.0
        prev = None
        for j, yy in enumerate((-5, 0, 5)):
            sk = 2.2 * s * (1 if j != 1 else -1)
            pts = [(cx - 6 * s + sk, cy + (yy - 1.5) * s), (cx + 6.5 * s + sk, cy + (yy - 1.5) * s),
                   (cx + 6 * s - sk, cy + (yy + 1.5) * s), (cx - 6.5 * s - sk, cy + (yy + 1.5) * s)]
            prev = k.poly_mask('%s_SolBar%d' % (name, j), pts, inp=prev)
        g = k.fill(name + '_SolGlyph', WHITE, prev)
    return k.over(name + '_Coin', disc, g)


# ---------------------------------------------------------------- logo (from brandkit/Logo.svg, unmodified)
def logo_paths():
    svg = open(os.path.join(ROOT, 'brandkit', 'Logo.svg'), encoding='utf8').read()
    return re.findall(r'<path class="(cls-\d)" d="([^"]+)"', svg)


LOGO_W, LOGO_H = 171.69, 38.59
LOGO_LETTERS = ['V', 'a', 'l', 'u', 't']   # white paths in file order; the 6th path is the green mark


def logo(sc, name, cx, cy, width, t_in, stagger=2, kit=None, mark_delay=10, letters_rise=True, word_wallet=None):
    """Animated logo build: letters rise from a mask line, green mark wipes on and its dots pop.
    t_in local frame. Returns (group node, clip mask)."""
    k = kit or sc.k
    k.section('LOGO_' + name)
    s = width / LOGO_W
    x0, y0 = cx - width / 2, cy - LOGO_H * s / 2
    grp = k.canvas(name + '_LogoCanvas')
    paths = logo_paths()
    white = [d for c_, d in paths if c_ == 'cls-2']
    green = [d for c_, d in paths if c_ == 'cls-1']
    for i, d in enumerate(white):
        m = k.svg_mask('%s_%s' % (name, LOGO_LETTERS[i]), d, x0, y0, s)
        f = k.freeze('%s_%s' % (name, LOGO_LETTERS[i]), k.fill('%s_%s_White' % (name, LOGO_LETTERS[i]), WHITE, m))
        if letters_rise:
            t0 = t_in + i * stagger
            f = k.xf('%s_%s_Rise' % (name, LOGO_LETTERS[i]), f,
                     dy=Anim([(t0, LOGO_H * s * 1.3), (t0 + 16, 0)], 'out'))
        grp = k.over('%s_%s_Add' % (name, LOGO_LETTERS[i]), grp, f)
    # green mark: split subpaths -> dot, slash, dot
    subs = svg_subpaths(green[0])
    tm = t_in + mark_delay
    for j, sub in enumerate(subs):
        T = lambda q: None if q is None else (x0 + s * q[0], y0 + s * q[1])
        nodes = [{'p': T(n['p']), 'in': T(n['in']), 'out': T(n['out'])} for n in sub]
        xs = [n['p'][0] for n in nodes]
        ys = [n['p'][1] for n in nodes]
        bx, by = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        m = k.poly_mask('%s_Mark%d' % (name, j), nodes)
        f = k.fill('%s_Mark%d_Green' % (name, j), ACC, m)
        if j == 1:   # the long stroke: wipe down from the top with a growing rectangle
            hh = max(ys) - min(ys) + 4
            wm = k.rect_mask('%s_MarkWipe' % name, min(xs) - 4, min(ys) - 2, max(xs) - min(xs) + 8,
                             Anim([(tm, 0.01), (tm + 12, hh)], 'out'),
                             center=AnimXY([(tm, (bx, min(ys))), (tm + 12, (bx, (min(ys) + max(ys)) / 2))], 'out'))
            f = k.over('%s_MarkSlash' % name, k.canvas('%s_SlashCanvas' % name), f, mask=wm)
        else:
            td = tm + (6 if j == 0 else 12)
            f = k.xf('%s_Dot%d_Pop' % (name, j), f, scale=Anim([(td, 0), (td + 12, 1)], 'back'), pivot=(bx, by))
        grp = k.over('%s_Mark%d_Add' % (name, j), grp, f)
    clip = k.rect_mask(name + '_LetterClip', x0 - 20, y0 - 30, width + 40, LOGO_H * s + 60)
    return grp, clip


# ---------------------------------------------------------------- cards / chips
def card(k, name, x, y, w, h, r=28, fill=CARD, edge=EDGE, alpha=1.0, edge_w=1.5):
    m = k.rect_mask(name + '_Shape', x, y, w, h, r)
    f = k.fill(name + '_Fill', fill, m, alpha)
    if edge:
        bm = k.rect_mask(name + '_Edge', x, y, w, h, r, border=edge_w)
        ef = k.fill(name + '_EdgeFill', edge, bm)
        f = k.over(name + '_Bordered', f, ef)
    return f


def pop(k, name, node, t0, cx, cy, dur=14, from_scale=0.7, dy=24, t_out=None, out_dur=10, out_dy=-20):
    """scale + rise in with back ease (and optional fall out). Returns transformed node + blend anim."""
    sk = [(t0, from_scale), (t0 + dur, 1.0)]
    se = ['back']
    yk = [(t0, dy), (t0 + dur, 0)]
    ye = ['out']
    bk = [(t0, 0.0), (t0 + dur * 0.5, 1.0)]
    be = ['out']
    if t_out is not None:
        sk += [(t_out, 1.0), (t_out + out_dur, 0.9)]
        se += ['linear', 'in']
        yk += [(t_out, 0), (t_out + out_dur, out_dy)]
        ye += ['linear', 'in']
        bk += [(t_out, 1.0), (t_out + out_dur, 0.0)]
        be += ['linear', 'in']
    x = k.xf(name + '_Pop', node, dy=Anim(yk, ye), scale=Anim(sk, se), pivot=(cx, cy))
    return x, Anim(bk, be)


def pill(k, name, x, y, w, h, fill, label=None, cap=22, color=WHITE, font=('Inter', 'SemiBold'), edge=None,
         icon_key=None, icon_color=None, alpha=1.0):
    f = card(k, name, x, y, w, h, h / 2, fill, edge, alpha)
    if icon_key:
        isz = h * 0.46
        ic = icon(k, name + '_Ic', icon_key, x + h * 0.55, y + h / 2, isz, icon_color or color)
        f = k.over(name + '_AddIcon', f, ic)
        tx = x + h * 0.55 + isz * 0.5 + h * 0.22
        if label:
            t = k.text(name + '_Label', label, tx, y + h / 2, cap, color, font[0], font[1], 'left')
            f = k.over(name + '_AddLabel', f, t)
    elif label:
        t = k.text(name + '_Label', label, x + w / 2, y + h / 2, cap, color, font[0], font[1], 'center')
        f = k.over(name + '_AddLabel', f, t)
    return f


# ---------------------------------------------------------------- phone mockup
PW, PH = 900, 1860
SX0, SY0, SW, SH = 22, 22, 856, 1816   # screen rect inside the phone canvas


def phone_kit(sc, prefix):
    k = Kit(sc.c, PW, PH, prefix=prefix, x0=sc.k.x + COL_W, y0=0)
    return k


def phone_frame(k, name='Phone'):
    """Body + screen base. Returns (body_node, screen_mask)."""
    k.section(name + '_Body')
    body = card(k, name + '_Frame', 0, 0, PW, PH, 132, '#0A0C0A', '#4A524A', edge_w=4)
    inner = k.rect_mask(name + '_Screen', SX0, SY0, SW, SH, 112)
    scr = k.gradient(name + '_ScreenBG', [(0, '#151A14', 1), (1, '#0D100D', 1)], 'Linear', (450, 0), (450, PH), inner)
    body = k.over(name + '_AddScreen', body, scr)
    isl = k.rect_mask(name + '_Island', PW / 2 - 92, 44, 184, 52, 26)
    body = k.over(name + '_AddIsland', body, k.fill(name + '_IslandFill', '#000000', isl))
    t = k.text(name + '_Time', '9:41', 128, 72, 24, WHITE, 'Inter', 'SemiBold', 'center')
    body = k.over(name + '_AddTime', body, t)
    prev = None
    for i in range(4):
        hh = 8 + i * 5
        prev = k.rect_mask('%s_Sig%d' % (name, i), 676 + i * 11, 84 - hh, 7, hh, 2, inp=prev)
    bat = k.rect_mask(name + '_Bat', 728, 62, 44, 22, 6, border=2, inp=prev)
    batf = k.rect_mask(name + '_BatFill', 732, 66, 32, 14, 3, inp=bat)
    body = k.over(name + '_AddStatus', body, k.fill(name + '_StatusFill', WHITE, batf))
    hm = k.rect_mask(name + '_HomeBar', PW / 2 - 130, PH - 46, 260, 9, 4.5)
    body = k.over(name + '_AddHomeBar', body, k.fill(name + '_HomeBarFill', WHITE, hm, 0.85))
    body = k.freeze(name + '_Body', body)
    return body, inner


def place_phone(sc, name, phone_img, cx, cy, scale, dy_anim=None, scale_anim=None, angle=None, blend=1.0):
    """Merge the phone canvas onto the 1920 frame (Merge Center/Size with motion blur). Returns spec for add_layer."""
    if dy_anim is not None:
        ctr = AnimXY([(0, (0, 0))])
        ctr.x = Anim([(t, cx) for t, _ in dy_anim.keys], dy_anim.ease)
        ctr.y = Anim([(t, cy + v) for t, v in dy_anim.keys], dy_anim.ease)
    else:
        ctr = (cx, cy)
    return phone_img, dict(center=ctr, size=scale_anim if scale_anim is not None else scale, angle=angle, mb=True,
                           blend=blend)


def shadow(k, name, cx, cy, w, h, alpha=0.55, soft=80):
    m = k.ellipse_mask(name + '_Shadow', cx, cy, w / 2, h / 2, soft=soft)
    return k.fill(name + '_ShadowFill', '#000000', m, alpha)
