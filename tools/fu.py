"""Tiny Fusion .comp writer for the VaultX ad.

Builds Fusion node trees (Background, masks, Text+, Transform, Merge, Blur, SoftGlow, MediaOut, Underlay)
with eased BezierSpline keyframes and writes them as Fusion composition files that DaVinci Resolve can
import with TimelineItem:ImportFusionComp().

Coordinates: helpers take pixel positions in the frame they draw into (x right, y DOWN) and convert to
Fusion's normalised space (y up).
"""
import re
from collections import OrderedDict

# ---------------------------------------------------------------- easing (CSS cubic-bezier control points)
EASE = {
    'linear': (1 / 3, 1 / 3, 2 / 3, 2 / 3),
    'out': (0.16, 1.0, 0.3, 1.0),          # expo-ish ease out: fast start, long settle
    'in': (0.7, 0.0, 0.84, 0.0),           # ease in (exits)
    'inout': (0.65, 0.0, 0.35, 1.0),       # cubic in-out
    'soft': (0.45, 0.0, 0.25, 1.0),        # gentle in-out for camera drifts
    'back': (0.34, 1.45, 0.64, 1.0),       # overshoot pop
    'snap': (0.05, 0.9, 0.1, 1.0),         # very sharp ease out
}


def lua(v):
    """Python value -> Lua literal."""
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, (int, float)):
        r = round(float(v), 6)
        return str(int(r)) if r == int(r) and abs(r) < 1e9 else repr(r)
    if isinstance(v, str):
        return '"' + v.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'
    if isinstance(v, (tuple, list)):
        return '{ ' + ', '.join(lua(x) for x in v) + ' }'
    if isinstance(v, Raw):
        return v.s
    raise TypeError(type(v))


class Raw:
    def __init__(self, s):
        self.s = s


def FuID(s):
    return Raw('FuID { %s }' % lua(s))


WARN = []


class Anim:
    """Scalar animation: keys = [(frame, value), ...]; ease = name or list of names per segment."""

    def __init__(self, keys, ease='out'):
        ts = [t for t, _ in keys]
        if any(b < a for a, b in zip(ts, ts[1:])):
            import traceback
            WARN.append('keys out of order %s at %s' % (ts, traceback.extract_stack()[-3:-1]))
        self.keys = sorted(keys)
        self.ease = ease

    def seg_ease(self, i):
        return EASE[self.ease[i] if isinstance(self.ease, (list, tuple)) else self.ease]

    def keyframes(self):
        ks = self.keys
        kf = []
        for i, (t, v) in enumerate(ks):
            d = {'t': t, 'v': v}
            if i > 0:
                t0, v0 = ks[i - 1]
                x1, y1, x2, y2 = self.seg_ease(i - 1)
                d['LH'] = (t0 + x2 * (t - t0), v0 + y2 * (v - v0))
            if i < len(ks) - 1:
                t1, v1 = ks[i + 1]
                x1, y1, x2, y2 = self.seg_ease(i)
                d['RH'] = (t + x1 * (t1 - t), v + y1 * (v1 - v))
            kf.append(d)
        return kf

    def value_at(self, f):
        ks = self.keys
        if f <= ks[0][0]:
            return ks[0][1]
        if f >= ks[-1][0]:
            return ks[-1][1]
        for i in range(len(ks) - 1):
            (t0, v0), (t1, v1) = ks[i], ks[i + 1]
            if t0 <= f <= t1:
                x1, y1, x2, y2 = self.seg_ease(i)
                # solve bezier x(u) = (f-t0)/(t1-t0)
                X = (f - t0) / (t1 - t0) if t1 > t0 else 1
                lo, hi = 0.0, 1.0
                for _ in range(40):
                    u = (lo + hi) / 2
                    x = 3 * (1 - u) ** 2 * u * x1 + 3 * (1 - u) * u * u * x2 + u ** 3
                    lo, hi = (u, hi) if x < X else (lo, u)
                y = 3 * (1 - u) ** 2 * u * y1 + 3 * (1 - u) * u * u * y2 + u ** 3
                return v0 + (v1 - v0) * y


class AnimXY:
    """Point animation: two scalar Anims (x, y) combined into an XYPath."""

    def __init__(self, keys, ease='out'):
        keys = sorted(keys)
        self.x = Anim([(t, p[0]) for t, p in keys], ease)
        self.y = Anim([(t, p[1]) for t, p in keys], ease)


class Expr:
    def __init__(self, expr, value=0):
        self.expr, self.value = expr, value


class Conn:
    def __init__(self, op, src='Output'):
        self.op, self.src = op, src


SPLINE_COLORS = [(255, 128, 0), (0, 200, 255), (220, 220, 0), (255, 0, 160), (120, 255, 120)]


class Comp:
    def __init__(self, name, frames, w=1920, h=1080, fps=30):
        self.name, self.frames, self.w, self.h, self.fps = name, frames, w, h, fps
        self.tools = OrderedDict()   # name -> text
        self.underlays = []
        self.col = 0
        self.names = set()

    # ------------------------------------------------------------- core emit
    def uniq(self, name):
        name = re.sub(r'[^A-Za-z0-9_]', '_', name)
        if name[0].isdigit():
            name = 'N' + name
        base, i = name, 2
        while name in self.names:
            name = '%s_%d' % (base, i)
            i += 1
        self.names.add(name)
        return name

    def _input(self, tool, key, v):
        if isinstance(v, Conn):
            return 'Input { SourceOp = %s, Source = %s, }' % (lua(v.op), lua(v.src))
        if isinstance(v, Anim):
            sp = self.uniq(tool + key.replace('.', '_'))
            self._spline(sp, v)
            return 'Input { SourceOp = %s, Source = "Value", }' % lua(sp)
        if isinstance(v, AnimXY):
            p = self.uniq(tool + key + 'Path')
            sx, sy = self.uniq(p + 'X'), self.uniq(p + 'Y')
            self._spline(sx, v.x)
            self._spline(sy, v.y)
            self.tools[p] = ('%s = XYPath {\n\t\t\tShowKeyPoints = false,\n\t\t\tDrawMode = "ModifyOnly",\n\t\t\t'
                             'Inputs = {\n\t\t\t\tX = Input { SourceOp = %s, Source = "Value", },\n\t\t\t\t'
                             'Y = Input { SourceOp = %s, Source = "Value", },\n\t\t\t},\n\t\t}') % (p, lua(sx), lua(sy))
            return 'Input { SourceOp = %s, Source = "Value", }' % lua(p)
        if isinstance(v, Expr):
            return 'Input { Value = %s, Expression = %s, }' % (lua(v.value), lua(v.expr))
        return 'Input { Value = %s, }' % lua(v)

    def _spline(self, name, a):
        c = SPLINE_COLORS[len(self.tools) % len(SPLINE_COLORS)]
        kfs = []
        for k in a.keyframes():
            parts = [lua(k['v'])]
            if 'LH' in k:
                parts.append('LH = %s' % lua(k['LH']))
            if 'RH' in k:
                parts.append('RH = %s' % lua(k['RH']))
            kfs.append('\t\t\t\t[%s] = { %s },' % (lua(k['t']), ', '.join(parts)))
        self.tools[name] = ('%s = BezierSpline {\n\t\t\tSplineColor = { Red = %d, Green = %d, Blue = %d },\n\t\t\t'
                            'NameSet = true,\n\t\t\tKeyFrames = {\n%s\n\t\t\t}\n\t\t}') % (name, c[0], c[1], c[2], '\n'.join(kfs))

    def add(self, typ, name, inputs, pos=None, extra=''):
        name = self.uniq(name)
        body = []
        for k, v in inputs.items():
            if v is None:
                continue
            key = k if re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', k) else '[%s]' % lua(k)
            body.append('\t\t\t\t%s = %s' % (key, self._input(name, k, v)))
        if pos is None:
            pos = (self.col * 110, len(self.tools) % 7 * 33)
        self.tools[name] = ('%s = %s {\n\t\t\tNameSet = true,\n%s\t\t\tInputs = {\n%s\n\t\t\t},\n\t\t\t'
                            'ViewInfo = OperatorInfo { Pos = { %s, %s } },\n\t\t}') % (
            name, typ, extra, ',\n'.join(body), lua(pos[0]), lua(pos[1]))
        return name

    def underlay(self, label, x, y, w, h, color=(0.26, 0.31, 0.2)):
        n = self.uniq('UL_' + label)
        self.tools[n] = ('%s = Underlay {\n\t\t\tNameSet = true,\n\t\t\tInputs = {\n\t\t\t\tComments = Input { Value = %s, },\n'
                         '\t\t\t},\n\t\t\tViewInfo = UnderlayInfo {\n\t\t\t\tPos = { %s, %s },\n\t\t\t\tSize = { %s, %s }\n\t\t\t},\n'
                         '\t\t\tColors = { TileColor = { R = %s, G = %s, B = %s }, }\n\t\t}') % (
            n, lua(label), lua(x), lua(y), lua(w), lua(h), lua(color[0]), lua(color[1]), lua(color[2]))
        return n

    def text(self):
        hdr = ('Composition {\n\tCurrentTime = 0,\n\tRenderRange = { 0, %d },\n\tGlobalRange = { 0, %d },\n\tCurrentID = %d,\n'
               '\tHiQ = true,\n\tPlaybackUpdateMode = 0,\n\tVersion = "DaVinci Resolve Fusion 21.2",\n\tSavedOutputs = 0,\n'
               '\tHeldTools = 0,\n\tDisabledTools = 0,\n\tLockedTools = 0,\n\tAudioOffset = 0,\n\tAutoRenderRange = true,\n'
               '\tResumable = true,\n\tOutputClips = {\n\t},\n\tTools = ordered() {\n') % (
            self.frames - 1, self.frames - 1, len(self.tools) + 10)
        body = ',\n'.join('\t\t' + t for t in self.tools.values())
        ftr = ('\n\t},\n\tFrames = {\n\t},\n\tPrefs = {\n\t\tComp = {\n\t\t\tFrameFormat = {\n\t\t\t\tName = "HD 1080",\n'
               '\t\t\t\tWidth = %d,\n\t\t\t\tHeight = %d,\n\t\t\t\tRate = %d,\n\t\t\t\tAspectX = 1,\n\t\t\t\tAspectY = 1,\n'
               '\t\t\t\tGuideRatio = 1.77777777777778,\n\t\t\t\tDepthFull = 2,\n\t\t\t\tDepthPreview = 2,\n'
               '\t\t\t\tDepthInteractive = 2,\n\t\t\t},\n\t\t\tUnsorted = {\n\t\t\t\tGlobalEnd = %d\n\t\t\t},\n\t\t}\n\t},\n}\n') % (
            self.w, self.h, self.fps, self.frames - 1)
        return hdr + body + ftr

    def save(self, path):
        open(path, 'w', encoding='utf8', newline='\n').write(self.text())
        return path


# ---------------------------------------------------------------- colour helpers
def hexrgb(h, a=1.0):
    h = h.lstrip('#')
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)


# ---------------------------------------------------------------- SVG path -> polylines
_tok = re.compile(r'[MmLlHhVvCcSsQqZz]|-?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?')


def svg_subpaths(d):
    """Parse an SVG path 'd' into subpaths: list of list of segments.
    Each subpath: list of nodes {'p':(x,y), 'in':(x,y)|None, 'out':(x,y)|None} (absolute coords), closed."""
    toks = _tok.findall(d)
    i = 0
    subs, cur = [], None
    x = y = 0.0
    sx = sy = 0.0
    cmd = None
    last_c2 = None

    def num():
        nonlocal i
        v = float(toks[i])
        i += 1
        return v

    while i < len(toks):
        if re.match(r'[A-Za-z]', toks[i]):
            cmd = toks[i]
            i += 1
        rel = cmd.islower()
        C = cmd.upper()
        if C == 'Z':
            if cur:
                subs.append(cur)
            cur = None
            x, y = sx, sy
            last_c2 = None
            continue
        if C == 'M':
            nx, ny = num(), num()
            if rel:
                nx, ny = x + nx, y + ny
            if cur:
                subs.append(cur)
            cur = [{'p': (nx, ny), 'in': None, 'out': None}]
            x, y, sx, sy = nx, ny, nx, ny
            cmd = 'l' if rel else 'L'
            last_c2 = None
            continue
        if C in 'LHV':
            if C == 'L':
                nx, ny = num(), num()
                if rel:
                    nx, ny = x + nx, y + ny
            elif C == 'H':
                nx = num()
                nx, ny = (x + nx if rel else nx), y
            else:
                ny = num()
                nx, ny = x, (y + ny if rel else ny)
            cur.append({'p': (nx, ny), 'in': None, 'out': None})
            x, y = nx, ny
            last_c2 = None
            continue
        if C in 'CS':
            if C == 'C':
                c1 = (num(), num())
                if rel:
                    c1 = (x + c1[0], y + c1[1])
            else:
                c1 = (2 * x - last_c2[0], 2 * y - last_c2[1]) if last_c2 else (x, y)
            c2 = (num(), num())
            p = (num(), num())
            if rel:
                c2 = (x + c2[0], y + c2[1])
                p = (x + p[0], y + p[1])
            cur[-1]['out'] = c1
            cur.append({'p': p, 'in': c2, 'out': None})
            x, y = p
            last_c2 = c2
            continue
        raise ValueError('unsupported path command ' + cmd)
    if cur:
        subs.append(cur)
    # merge closing duplicate point
    for s in subs:
        if len(s) > 1 and abs(s[-1]['p'][0] - s[0]['p'][0]) < 1e-6 and abs(s[-1]['p'][1] - s[0]['p'][1]) < 1e-6:
            s[0]['in'] = s[-1]['in']
            s.pop()
    return subs


def bbox(sub):
    xs = [n['p'][0] for n in sub]
    ys = [n['p'][1] for n in sub]
    return min(xs), min(ys), max(xs), max(ys)


def polyline_value(sub, to_norm, closed=True):
    """Fusion Polyline literal from a subpath; to_norm(x,y) maps svg coords -> fusion polyline coords."""
    pts = []
    for n in sub:
        X, Y = to_norm(*n['p'])
        d = {'X': X, 'Y': Y}
        if n['in'] is not None:
            ix, iy = to_norm(*n['in'])
            d['LX'], d['LY'] = ix - X, iy - Y
        if n['out'] is not None:
            ox, oy = to_norm(*n['out'])
            d['RX'], d['RY'] = ox - X, oy - Y
        lin = n['in'] is None and n['out'] is None
        items = (['Linear = true'] if lin else []) + ['%s = %s' % (k, lua(v)) for k, v in d.items()]
        pts.append('{ ' + ', '.join(items) + ' }')
    return Raw('Polyline {\n\t\t\t\t\t\tClosed = %s,\n\t\t\t\t\t\tPoints = {\n\t\t\t\t\t\t\t%s\n\t\t\t\t\t\t}\n\t\t\t\t\t}' % (
        'true' if closed else 'false', ',\n\t\t\t\t\t\t\t'.join(pts)))
