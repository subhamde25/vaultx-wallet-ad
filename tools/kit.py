"""Design kit on top of fu.py: pixel-space shapes, text, transforms and merges for the VaultX comps.

Calibrated in Resolve 21.2 (T00/T01 calibration comps, 2026-11-11):
- Rectangle mask Center/Width/Height are fractions of the frame per axis; CornerRadius = r / (min(w,h)/2)
- Ellipse mask Width AND Height are fractions of the frame WIDTH
- polyline points: X = (px - W/2)/W, Y = (H/2 - py)/H; BorderWidth is a fraction of the frame width
- Text+ cap height (Inter) ~ 920 * Size px at 1920 wide; vertical Center sits on the cap-height middle
- Transform/Merge motion blur works (MotionBlur=1, Quality, ShutterAngle)
- Merge EffectMask clips the foreground (used for masked word reveals)

Node-graph layout: every element is built in its own labelled column ("section"); finished elements are
merged along a horizontal spine row underneath, which ends in MediaOut1.
"""
from fu import Comp, Anim, AnimXY, Conn, FuID, Raw, Expr, hexrgb, svg_subpaths, bbox, polyline_value, lua

CAP_PER_SIZE = 920.0   # Inter cap-height px per unit of Text+ Size on a 1920-wide frame
COL_W = 130
ROW_H = 33


def moving_quality(anims, q=4):
    """Quality spline that is 1 (no extra samples) except while any of the given anims is changing."""
    iv = []
    for a in anims:
        if isinstance(a, AnimXY):
            a_list = [a.x, a.y]
        elif isinstance(a, Anim):
            a_list = [a]
        else:
            continue
        for an in a_list:
            ks = an.keys
            for (t0, v0), (t1, v1) in zip(ks, ks[1:]):
                if abs(v1 - v0) > 1e-9 and t1 > t0:
                    iv.append([t0, t1])
    if not iv:
        return None
    iv.sort()
    merged = [iv[0]]
    for a, b in iv[1:]:
        if a <= merged[-1][1] + 2:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    keys = []
    for a, b in merged:
        keys += [(a - 1, 1), (a, q), (b, q), (b + 1, 1)]
    return Anim(keys, 'linear')



class Kit:
    def __init__(self, comp, W=1920, H=1080, prefix='', x0=0, y0=0, spine_y=None, aw=None, ah=None):
        self.c, self.W, self.H, self.pre = comp, W, H, prefix
        self.AW, self.AH = aw or W, ah or H     # authoring coordinate space (px values passed in are in this space)
        full = (W, H) == (1920, 1080)
        self.ff = {'UseFrameFormatSettings': 1 if full else 0, 'Width': W, 'Height': H}
        self.mf = {'UseFrameFormatSettings': 1 if full else 0, 'MaskWidth': W, 'MaskHeight': H}
        self.x, self.y = x0, y0
        self.sec_x0, self.sec_y0 = x0, y0
        self.sec_label = None
        self.max_y = y0
        self.spine_y = spine_y
        self.sections = []

    # ------------------------------------------------------------ node layout
    def place(self):
        p = (self.x, self.y)
        self.y += ROW_H
        self.max_y = max(self.max_y, self.y)
        return p

    def section(self, label, color=(0.22, 0.27, 0.18)):
        """Start a new labelled column for one design element."""
        self.end_section()
        if self.sec_label is not None or self.sections:
            self.x += COL_W
        self.y = self.sec_y0
        self.sec_label = label
        self.sec_start = (self.x, self.y)
        self.sec_color = color

    def end_section(self):
        if self.sec_label is None:
            return
        x, y = self.sec_start
        h = max(self.y - y, ROW_H)
        self.c.underlay(self.pre + self.sec_label, x - 55, y - 30, 120, h + 30, self.sec_color)
        self.sections.append(self.sec_label)
        self.sec_label = None

    def n(self, s):
        return self.pre + s

    # ------------------------------------------------------------ coordinates
    def pt(self, px, py):
        return (px / self.AW, 1 - py / self.AH)

    def pnorm(self, px, py):
        return ((px - self.AW / 2) / self.AW, (self.AH / 2 - py) / self.AH)

    def freeze(self, name, node):
        """Static branch: TimeSpeed at speed 0 so Fusion renders it once and reuses it on every frame."""
        return self.c.add('TimeSpeed', self.n(name + '_Static'), {'Input': Conn(node), 'Speed': 0, 'Delay': 0,
                                                                  'InterpolateBetweenFrames': 0}, self.place())

    @staticmethod
    def amap(v, f):
        if isinstance(v, Anim):
            return Anim([(t, f(x)) for t, x in v.keys], v.ease)
        return f(v)

    # ------------------------------------------------------------ primitives
    def canvas(self, name, color='#000000', alpha=0.0):
        r, g, b, _ = hexrgb(color)
        d = dict(self.ff)
        d.update({'TopLeftRed': r * alpha, 'TopLeftGreen': g * alpha, 'TopLeftBlue': b * alpha, 'TopLeftAlpha': alpha})
        return self.c.add('Background', self.n(name), d, self.place())

    def fill(self, name, color, mask=None, alpha=1.0):
        r, g, b, _ = hexrgb(color)
        d = dict(self.ff)
        # Fusion's Background does not premultiply: scale RGB by alpha ourselves
        d.update({'TopLeftRed': r * alpha, 'TopLeftGreen': g * alpha, 'TopLeftBlue': b * alpha, 'TopLeftAlpha': alpha,
                  'EffectMask': Conn(mask, 'Mask') if mask else None})
        return self.c.add('Background', self.n(name), d, self.place())

    def gradient(self, name, stops, kind='Linear', start=(0, 0), end=(0, 100), mask=None):
        """stops: list of (pos, '#hex', alpha). start/end in px."""
        cols = ', '.join('[%s] = { %s, %s, %s, %s }' % (lua(p), *[lua(x * a) for x in hexrgb(c)[:3]], lua(a))
                         for p, c, a in stops)
        d = dict(self.ff)
        def P(v):
            if isinstance(v, AnimXY):
                a = AnimXY([(0, (0, 0))])
                a.x = Anim([(t, q / self.AW) for t, q in v.x.keys], v.x.ease)
                a.y = Anim([(t, 1 - q / self.AH) for t, q in v.y.keys], v.y.ease)
                return a
            return self.pt(*v)
        d.update({'Type': FuID('Gradient'), 'GradientType': FuID(kind), 'Start': P(start), 'End': P(end),
                  'Gradient': Raw('Gradient {\n\t\t\t\t\t\tColors = { %s }\n\t\t\t\t\t}' % cols),
                  'EffectMask': Conn(mask, 'Mask') if mask else None})
        return self.c.add('Background', self.n(name), d, self.place())

    def rect_mask(self, name, x, y, w, h, r=0, soft=0, center=None, inp=None, paint=None, invert=False,
                  border=None, level=None):
        """x,y = top-left px (static). w/h may be Anim (px) -> pass center (px) for animated sizes.
        center may also be AnimXY in px."""
        ww = w.keys[-1][1] if isinstance(w, Anim) else w
        hh = h.keys[-1][1] if isinstance(h, Anim) else h
        if center is None:
            ctr = self.pt(x + ww / 2, y + hh / 2)
        elif isinstance(center, AnimXY):
            a = AnimXY([(0, (0, 0))])
            a.x = Anim([(t, v / self.AW) for t, v in center.x.keys], center.x.ease)
            a.y = Anim([(t, 1 - v / self.AH) for t, v in center.y.keys], center.y.ease)
            ctr = a
        else:
            ctr = self.pt(*center)

        def rad(v):
            m = min(ww, hh)
            return min(1.0, v / (m / 2)) if m > 0 else 0
        d = dict(self.mf)
        d.update({'SoftEdge': soft / self.AW if soft else None, 'Center': ctr,
                  'Width': self.amap(w, lambda v: v / self.AW), 'Height': self.amap(h, lambda v: v / self.AH),
                  'CornerRadius': self.amap(r, rad) if r else None, 'Invert': 1 if invert else None,
                  'PaintMode': FuID(paint) if paint else None, 'EffectMask': Conn(inp, 'Mask') if inp else None,
                  'Level': level})
        if border is not None:
            d['Solid'] = 0
            d['BorderWidth'] = border / self.AW
        return self.c.add('RectangleMask', self.n(name + '_M'), d, self.place())

    def ellipse_mask(self, name, cx, cy, rw, rh=None, soft=0, inp=None, paint=None, border=None, invert=False,
                     level=None, center=None):
        rh = rw if rh is None else rh
        if isinstance(center, AnimXY):
            a = AnimXY([(0, (0, 0))])
            a.x = Anim([(t, v / self.AW) for t, v in center.x.keys], center.x.ease)
            a.y = Anim([(t, 1 - v / self.AH) for t, v in center.y.keys], center.y.ease)
            ctr = a
        else:
            ctr = self.pt(cx, cy)
        d = dict(self.mf)
        d.update({'SoftEdge': soft / self.AW if soft else None, 'Center': ctr,
                  'Width': self.amap(rw, lambda v: 2 * v / self.AW), 'Height': self.amap(rh, lambda v: 2 * v / self.AW),
                  'PaintMode': FuID(paint) if paint else None, 'EffectMask': Conn(inp, 'Mask') if inp else None,
                  'Invert': 1 if invert else None, 'Level': level})
        if border is not None:
            d['Solid'] = 0
            d['BorderWidth'] = self.amap(border, lambda v: v / self.AW)
        return self.c.add('EllipseMask', self.n(name + '_M'), d, self.place())

    def poly_mask(self, name, nodes, closed=True, inp=None, paint=None, border=None, write_on=None, write_start=None,
                  soft=0, level=None):
        """nodes: list of {'p':(px,py),'in':..,'out':..} or plain (px,py) tuples (linear)."""
        nn = [n if isinstance(n, dict) else {'p': n, 'in': None, 'out': None} for n in nodes]
        d = dict(self.mf)
        d.update({'SoftEdge': soft / self.AW if soft else None, 'Level': level,
                  'PaintMode': FuID(paint) if paint else None, 'EffectMask': Conn(inp, 'Mask') if inp else None,
                  'Polyline': polyline_value(nn, self.pnorm, closed)})
        if border is not None:
            d['Solid'] = 0
            d['BorderWidth'] = border / self.AW
        if write_on is not None:
            d['WriteOnEnd'] = write_on
            # a stroke with WriteOnEnd = 0 still draws its round cap as a dot: keep the mask off until it starts
            if isinstance(write_on, Anim) and write_on.keys[0][1] == 0 and level is None:
                t0 = write_on.keys[0][0]
                d['Level'] = Anim([(t0, 0), (t0 + 1, 1)], 'linear')
        if write_start is not None:
            d['WriteOnStart'] = write_start
        return self.c.add('PolylineMask', self.n(name + '_M'), d, self.place())

    def svg_mask(self, name, d_attr, x, y, scale, inp=None):
        """Filled SVG path (all subpaths) placed with its (0,0) at px (x,y), scaled. Counters subtract."""
        subs = svg_subpaths(d_attr)
        prev = inp
        boxes = []
        for i, s in enumerate(subs):
            bb = bbox(s)
            inside = any(bb[0] >= o[0] and bb[1] >= o[1] and bb[2] <= o[2] and bb[3] <= o[3] for o in boxes)
            boxes.append(bb)
            T = lambda q: None if q is None else (x + scale * q[0], y + scale * q[1])
            nodes = [{'p': T(n['p']), 'in': T(n['in']), 'out': T(n['out'])} for n in s]
            prev = self.poly_mask('%s_%d' % (name, i), nodes, True, inp=prev, paint='Subtract' if inside else None)
        return prev

    def text(self, name, s, x, y, cap, color='#FFFFFF', font='Inter', style='Bold', align='left', track=1.0,
             alpha=1.0, expr=None):
        """x,y px: y = cap-height middle; x = left/centre/right edge per align. cap = cap height px."""
        r, g, b, _ = hexrgb(color)
        size = cap / CAP_PER_SIZE * (1920 / self.AW)
        d = dict(self.ff)
        d.update({'StyledText': Expr(expr, s) if expr else s, 'Font': font, 'Style': style,
                  'Size': size, 'Center': self.pt(x, y), 'CharacterSpacing': track if track != 1.0 else None,
                  'HorizontalLeftCenterRight': {'left': -1, 'center': 0, 'right': 1}[align],
                  'Red1': r, 'Green1': g, 'Blue1': b, 'Alpha1': alpha if alpha != 1.0 else None})
        return self.c.add('TextPlus', self.n(name), d, self.place())

    # ------------------------------------------------------------ operators
    def xf(self, name, inp, dx=0, dy=0, scale=1, rot=0, pivot=None, mb=True, quality=4):
        """Offset in px (dx right, dy down); dx/dy/scale/rot may be Anim. pivot px for scale/rotation."""
        if isinstance(dx, Anim) or isinstance(dy, Anim):
            ax = dx if isinstance(dx, Anim) else Anim([(0, dx), (1, dx)], 'linear')
            ay = dy if isinstance(dy, Anim) else Anim([(0, dy), (1, dy)], 'linear')
            ctr = AnimXY([(0, (0, 0))])
            ctr.x = Anim([(t, 0.5 + v / self.AW) for t, v in ax.keys], ax.ease)
            ctr.y = Anim([(t, 0.5 - v / self.AH) for t, v in ay.keys], ay.ease)
        else:
            ctr = (0.5 + dx / self.AW, 0.5 - dy / self.AH) if (dx or dy) else None
        d = {'Input': Conn(inp), 'Center': ctr, 'Pivot': self.pt(*pivot) if pivot else None,
             'Size': scale if (isinstance(scale, Anim) or scale != 1) else None,
             'Angle': rot if (isinstance(rot, Anim) or rot != 0) else None}
        if mb:
            qa = moving_quality([dx, dy, scale, rot], quality)
            if qa is not None:
                d.update({'MotionBlur': 1, 'Quality': qa, 'ShutterAngle': 180})
        return self.c.add('Transform', self.n(name), d, self.place())

    def over(self, name, bg, fg, blend=1.0, mode=None, mask=None, center=None, size=None, angle=None, mb=False,
             pos=None):
        """center: (px,py) or AnimXY in px of the BACKGROUND frame (self.W x self.H); size may be Anim."""
        if isinstance(center, AnimXY):
            a = AnimXY([(0, (0, 0))])
            a.x = Anim([(t, v / self.AW) for t, v in center.x.keys], center.x.ease)
            a.y = Anim([(t, 1 - v / self.AH) for t, v in center.y.keys], center.y.ease)
            ctr = a
        elif center is not None:
            ctr = self.pt(*center)
        else:
            ctr = None
        d = {'Background': Conn(bg), 'Foreground': Conn(fg), 'PerformDepthMerge': 0,
             'Blend': blend if (isinstance(blend, Anim) or blend != 1.0) else None,
             'ApplyMode': FuID(mode) if mode else None, 'EffectMask': Conn(mask, 'Mask') if mask else None,
             'Center': ctr, 'Size': size, 'Angle': angle}
        if mb:
            qa = moving_quality([center, size, angle], 4)
            if qa is not None:
                d.update({'MotionBlur': 1, 'Quality': qa, 'ShutterAngle': 180})
        return self.c.add('Merge', self.n(name), d, pos or self.place())

    def blur(self, name, inp, size, mask=None):
        return self.c.add('Blur', self.n(name), {'Input': Conn(inp), 'XBlurSize': size,
                                                 'EffectMask': Conn(mask, 'Mask') if mask else None}, self.place())

    def glow(self, name, inp, gain=1.0, size=20, threshold=0.0):
        return self.c.add('SoftGlow', self.n(name), {'Input': Conn(inp), 'Gain': gain, 'XGlowSize': size,
                                                     'Threshold': threshold}, self.place())

    def stack(self, name, base, layers):
        cur = base
        for i, l in enumerate(layers):
            if isinstance(l, tuple):
                cur = self.over('%s_%02d' % (name, i + 1), cur, l[0], **l[1])
            else:
                cur = self.over('%s_%02d' % (name, i + 1), cur, l)
        return cur

    # ------------------------------------------------------------ composite helpers
    def shape_rect(self, name, x, y, w, h, r, color, alpha=1.0, border=None, border_color='#2C332C'):
        m = self.rect_mask(name, x, y, w, h, r)
        f = self.fill(name + '_Fill', color, m, alpha)
        if border:
            bm = self.rect_mask(name + '_Edge', x, y, w, h, r, border=border)
            bf = self.fill(name + '_EdgeFill', border_color, bm)
            f = self.over(name + '_Card', f, bf)
        return f
