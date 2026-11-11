"""C03 Instant transactions + swaps, C04 Portfolio chart, C05 Price alerts + trends."""
import math
import random
from fu import Anim, AnimXY
from kit import Kit, COL_W
from vx_common import (PHONE_RES, Scene, background, headline, card, pill, pop, icon, icon_solid, token, text_w, vf, gf,
                       phone_frame, PW, PH, SX0, SY0, SW, SH, shadow,
                       ACC, ACC_D, WHITE, GREY, GREY2, CARD, CARD2, EDGE, CHAR, RED, BG, DISPLAY)


def eyebrow(sc, name, num, label, x, y, t0, t_out=None, kit=None):
    """small '01  Send' label above a headline"""
    k = kit or sc.k
    k.section('Eyebrow_' + name)
    g = k.canvas(name + '_Eyebrow')
    n = k.text(name + '_Num', num, x, y, 22, ACC, 'Inter', 'Bold', 'left')
    ln = k.rect_mask(name + '_Rule', x + 40, y - 1, 36, 2)
    r = k.fill(name + '_RuleFill', GREY2, ln)
    lab = k.text(name + '_Label', label.upper(), x + 90, y, 20, GREY, 'Inter', 'SemiBold', 'left', track=1.12)
    g = k.over(name + '_AddNum', g, n)
    g = k.over(name + '_AddRule', g, r)
    g = k.over(name + '_AddLabel', g, lab)
    keys = [(t0, -30), (t0 + 14, 0)]
    eas = ['out']
    bk = [(t0, 0), (t0 + 10, 1)]
    be = ['out']
    if t_out is not None:
        keys += [(t_out, 0), (t_out + 8, -20)]
        eas += ['linear', 'in']
        bk += [(t_out, 1), (t_out + 8, 0)]
        be += ['linear', 'in']
    g = k.xf(name + '_Slide', g, dx=Anim(keys, eas), mb=True)
    return g, Anim(bk, be)


def sync(sc, pk):
    sc.k.end_section()
    pk.end_section()
    sc.k.x = pk.x + COL_W
    sc.k.sec_label = None


def num_expr(t0, t1, v0, v1, fmt='$%s', dec=2):
    """Text+ expression counting v0->v1 between local frames t0..t1 with ease-out and thousands separators."""
    return (':local t=math.min(1,math.max(0,(time-%d)/%d)); t=1-(1-t)^3; local v=%f+(%f)*t; '
            'local s=string.format("%%.%df",v); local int,frac=s:match("(%%d+)(.*)"); '
            'int=int:reverse():gsub("(%%d%%d%%d)","%%1,"):reverse():gsub("^,",""); return Text(string.format("%s", int..frac))'
            % (t0, max(t1 - t0, 1), v0, v1 - v0, dec, fmt.replace('%s', '%s')))


# ================================================================ phone screens
def ui_send(pk, n):
    k = pk
    k.section(n + '_SendUI')
    g = k.canvas(n + '_Send_Canvas')
    layers = []
    layers.append(icon(k, n + '_Back', 'back', 92, 172, 40, GREY))
    layers.append(k.text(n + '_Title', 'Send', 450, 172, 30, WHITE, 'Inter', 'SemiBold', 'center'))
    layers.append(card(k, n + '_TokenRow', 70, 250, 760, 130, 34, CARD2, EDGE))
    layers.append(token(k, n + '_EthCoin', 'ETH', 150, 315, 36))
    layers.append(k.text(n + '_EthName', 'Ethereum', 210, 297, 26, WHITE, 'Inter', 'SemiBold', 'left'))
    layers.append(k.text(n + '_EthBal', 'ETH  ·  Balance 4.20', 210, 340, 19, GREY, 'Inter', 'Medium', 'left'))
    amt = k.text(n + '_Amount', '0.85', 560, 560, 104, WHITE, 'Inter Display', 'Bold', 'right',
                 expr=num_expr(2, 18, 0, 0.85, '%s', 2))
    layers.append(k.text(n + '_AmountUnit', 'ETH', 585, 560, 42, GREY, 'Inter Display', 'SemiBold', 'left'))
    layers.append(k.text(n + '_AmountUsd', '≈ $2,846.10', 450, 660, 26, GREY, 'Inter', 'Medium', 'center'))
    layers.append(card(k, n + '_ToRow', 70, 740, 760, 130, 34, CARD2, EDGE))
    layers.append(k.text(n + '_ToLabel', 'To', 115, 778, 19, GREY, 'Inter', 'Medium', 'left'))
    layers.append(k.text(n + '_ToAddr', '0x8F3c…a91C', 115, 825, 27, WHITE, 'Inter', 'SemiBold', 'left'))
    av = k.ellipse_mask(n + '_Avatar', 760, 805, 34)
    layers.append(k.fill(n + '_AvatarFill', CHAR, av))
    layers.append(icon(k, n + '_AvatarIc', 'user', 760, 805, 36, WHITE))
    for i, (a, b, col) in enumerate([('Network fee', '$0.12', WHITE), ('Arrives in', '~0.4s', ACC)]):
        yy = 950 + i * 62
        layers.append(k.text('%s_Row%d_L' % (n, i), a, 115, yy, 22, GREY, 'Inter', 'Medium', 'left'))
        layers.append(k.text('%s_Row%d_R' % (n, i), b, 785, yy, 22, col, 'Inter', 'SemiBold', 'right'))
    for i, L_ in enumerate(layers):
        g = k.over('%s_SendAdd%02d' % (n, i + 1), g, L_)
    g = k.freeze(n + '_SendStatic', g)
    g = k.over(n + '_SendAddAmount', g, amt)
    return g


def ui_send_button(pk, n, t_tap):
    k = pk
    k.section(n + '_SendButton')
    b = card(k, n + '_SendBtn', 70, 1600, 760, 124, 62, ACC, None)
    t = k.text(n + '_SendBtnLabel', 'Send now', 450, 1662, 32, BG, 'Inter', 'Bold', 'center')
    b = k.over(n + '_SendBtnAddLabel', b, t)
    b = k.freeze(n + '_SendBtn', b)
    b = k.xf(n + '_SendBtnPress', b, scale=Anim([(t_tap, 1), (t_tap + 3, 0.95), (t_tap + 9, 1)], ['out', 'back']),
             pivot=(450, 1662))
    rm = k.ellipse_mask(n + '_TapRipple', 450, 1662, Anim([(t_tap, 10), (t_tap + 14, 170)], 'out'),
                        border=Anim([(t_tap, 14), (t_tap + 14, 2)], 'out'))
    rip = k.fill(n + '_TapRippleFill', WHITE, rm)
    dm = k.ellipse_mask(n + '_TapDot', 450, 1662, Anim([(t_tap - 6, 0), (t_tap - 2, 26), (t_tap + 6, 26), (t_tap + 10, 0)],
                                                      ['out', 'linear', 'in']))
    dot = k.fill(n + '_TapDotFill', WHITE, dm, 0.85)
    tap = k.over(n + '_TapRippleDot', rip, dot)
    b = k.over(n + '_SendBtnAddTap', b, tap, blend=Anim([(t_tap - 6, 0), (t_tap - 4, 1), (t_tap + 10, 1), (t_tap + 16, 0)],
                                                       ['out', 'linear', 'in']))
    return b


def ui_success(pk, n, t0):
    k = pk
    k.section(n + '_SuccessUI')
    g = k.canvas(n + '_Success_Canvas')
    cm = k.ellipse_mask(n + '_OkDisc', 450, 760, Anim([(t0, 0), (t0 + 12, 120)], 'back'))
    disc = k.fill(n + '_OkDiscFill', ACC, cm)
    ring = k.ellipse_mask(n + '_OkRing', 450, 760, Anim([(t0 + 4, 120), (t0 + 22, 240)], 'out'), border=3)
    ringf = k.fill(n + '_OkRingFill', ACC, ring)
    chk = icon(k, n + '_OkCheck', 'check', 450, 760, 150, BG, stroke=16, write_on=Anim([(t0 + 6, 0), (t0 + 18, 1)], 'out'))
    g = k.over(n + '_OkAddDisc', g, disc)
    g = k.over(n + '_OkAddRing', g, ringf, blend=Anim([(t0 + 3, 0), (t0 + 4, 0.8), (t0 + 22, 0)], ['linear', 'out']))
    g = k.over(n + '_OkAddCheck', g, chk)
    for i, (s, cap, col, y, d) in enumerate([('Sent', 64, WHITE, 980, 10), ('0.85 ETH to 0x8F3c…a91C', 24, GREY, 1060, 13),
                                             ('Confirmed in 0.4s', 26, ACC, 1112, 16)]):
        t = k.text('%s_OkText%d' % (n, i), s, 450, y, cap, col, 'Inter Display' if i == 0 else 'Inter',
                   'Bold' if i == 0 else 'SemiBold', 'center')
        t = k.xf('%s_OkText%d_Rise' % (n, i), t, dy=Anim([(t0 + d, 40), (t0 + d + 14, 0)], 'out'), mb=False)
        g = k.over('%s_OkAddText%d' % (n, i), g, t, blend=Anim([(t0 + d, 0), (t0 + d + 8, 1)], 'out'))
    return g


def ui_swap(pk, n, t_rot, t_bolt):
    k = pk
    k.section(n + '_SwapUI')
    g = k.canvas(n + '_Swap_Canvas')
    L = []
    L.append(icon(k, n + '_SwBack', 'back', 92, 172, 40, GREY))
    L.append(k.text(n + '_SwTitle', 'Swap', 450, 172, 30, WHITE, 'Inter', 'SemiBold', 'center'))
    for i, (lab, sym, tick, amt, usd, y) in enumerate([('You pay', 'BTC', 'BTC', '0.042', '$2,856.40', 250),
                                                        ('You receive', 'ETH', 'ETH', '0.8512', '$2,849.95', 580)]):
        L.append(card(k, '%s_SwCard%d' % (n, i), 70, y, 760, 270, 40, CARD2, EDGE))
        L.append(k.text('%s_SwLab%d' % (n, i), lab, 115, y + 52, 20, GREY, 'Inter', 'Medium', 'left'))
        L.append(token(k, '%s_SwCoin%d' % (n, i), sym, 150, y + 160, 40))
        L.append(k.text('%s_SwTick%d' % (n, i), tick, 210, y + 160, 34, WHITE, 'Inter', 'Bold', 'left'))
        L.append(k.text('%s_SwAmt%d' % (n, i), amt, 785, y + 148, 52, WHITE, 'Inter Display', 'Bold', 'right'))
        L.append(k.text('%s_SwUsd%d' % (n, i), usd, 785, y + 210, 21, GREY, 'Inter', 'Medium', 'right'))
    L.append(k.text(n + '_SwRate', '1 BTC = 20.27 ETH', 115, 925, 22, GREY, 'Inter', 'Medium', 'left'))
    L.append(pill(k, n + '_SwBest', 640, 902, 170, 48, '#22301A', 'Best rate', 19, ACC, ('Inter', 'SemiBold')))
    for i, L_ in enumerate(L):
        g = k.over('%s_SwAdd%02d' % (n, i + 1), g, L_)
    g = k.freeze(n + '_SwapStatic', g)
    # swap circle (rotates on "fast")
    k.section(n + '_SwapCircle')
    cm = k.ellipse_mask(n + '_SwCircle', 450, 565, 62)
    cb = k.ellipse_mask(n + '_SwCircleEdge', 450, 565, 66)
    ce = k.fill(n + '_SwCircleEdgeFill', BG, cb)
    cf = k.fill(n + '_SwCircleFill', ACC, cm)
    ic = icon(k, n + '_SwIcon', 'swap', 450, 565, 62, BG, stroke=6)
    ic = k.xf(n + '_SwIconRotate', ic, rot=Anim([(t_rot, 0), (t_rot + 16, -180)], 'back'), pivot=(450, 565))
    circ = k.over(n + '_SwCircleAddEdge', ce, cf)
    circ = k.over(n + '_SwCircleAddIcon', circ, ic)
    g = k.over(n + '_SwAddCircle', g, circ)
    # button with bolt
    k.section(n + '_SwapButton')
    b = card(k, n + '_SwBtn', 70, 1600, 760, 124, 62, ACC, None)
    bolt = icon_solid(k, n + '_SwBtnBolt', 'bolt', 300, 1662, 44, BG)
    bt = k.text(n + '_SwBtnLabel', 'Swap instantly', 470, 1662, 32, BG, 'Inter', 'Bold', 'center')
    b = k.over(n + '_SwBtnAddBolt', b, bolt)
    b = k.over(n + '_SwBtnAddLabel', b, bt)
    b = k.freeze(n + '_SwBtn', b)
    b = k.xf(n + '_SwBtnPress', b, scale=Anim([(t_bolt - 4, 1), (t_bolt - 1, 0.95), (t_bolt + 6, 1)], ['out', 'back']),
             pivot=(450, 1662))
    g = k.over(n + '_SwAddButton', g, b)
    return g


# ================================================================ C03
def c03():
    sc = Scene(2)
    k = sc.k
    v = sc.v
    n = sc.n
    background(sc)
    t_push = 106

    # ---- headline column (left)
    e1, eb1 = eyebrow(sc, 'Eb_Send', '01', 'Send', 172, 330, v('instant', -6), t_out=v('lightning', -10))
    sc.add_layer(e1, blend=eb1)
    h1, c1 = headline(sc, 'HL_Instant_Transactions', ['Instant', 'transactions.'], 170, 430, 86, 0,
                      t_out=v('lightning', -9), gap=0.62, hl=('transactions.',),
                      word_times=[v('instant', -2), v('transactions', -2)])
    sc.add_layer(h1, mask=c1)
    e2, eb2 = eyebrow(sc, 'Eb_Swap', '02', 'Swap', 172, 330, v('lightning', -2))
    h2, c2 = headline(sc, 'HL_Lightning_Swaps', ['Lightning-fast', 'swaps.'], 170, 430, 86, 0,
                      gap=0.62, hl=('swaps.',), word_times=[v('lightning', -1), v('swaps', -3)])
    k.section('Push_Out_Left')
    PUSH = Anim([(t_push, 0), (n, -1500)], 'in')
    sc.add_layer(k.xf('Eb_Swap_PushOut', e2, dx=PUSH), blend=eb2)
    sc.add_layer(k.xf('HL_Lightning_Swaps_PushOut', h2, dx=PUSH))

    # ---- phone (own canvas)
    pk = Kit(sc.c, int(PW * PHONE_RES), int(PH * PHONE_RES), prefix='P_', x0=k.x + COL_W, y0=0, aw=PW, ah=PH)
    body, scr = phone_frame(pk, 'Phone')
    t_tap = v('transactions', 6)
    send = ui_send(pk, 'S')
    btn = ui_send_button(pk, 'S', t_tap)
    pk.section('Screen1_SendFlow')
    s1 = pk.over('S_Send_AddButton', send, btn)
    t_ok = t_tap + 8
    s1 = pk.xf('S_Send_FadeBack', s1, scale=Anim([(t_ok, 1), (t_ok + 10, 0.94)], 'out'), pivot=(450, 930), mb=False)
    ok = ui_success(pk, 'S', t_ok + 4)
    pk.section('Screen_Stack')
    flow1 = pk.over('S_Flow1_Send', pk.canvas('S_Flow1_Canvas'), s1, blend=Anim([(t_ok, 1), (t_ok + 8, 0)], 'out'))
    flow1 = pk.over('S_Flow1_Success', flow1, ok)
    t_sw = v('lightning', -6)
    flow1 = pk.xf('S_Flow1_SlideOut', flow1, dx=Anim([(t_sw, 0), (t_sw + 14, -PW)], 'inout'), mb=False)
    swap = ui_swap(pk, 'W', v('fast2', -2), v('swaps', 0))
    pk.section('Screen2_Swap')
    swap = pk.xf('W_Swap_SlideIn', swap, dx=Anim([(t_sw, PW), (t_sw + 14, 0)], 'inout'), mb=False)
    pk.section('Phone_Assemble')
    screen = pk.over('Screen_Flow1', pk.canvas('Screen_Canvas'), flow1)
    screen = pk.over('Screen_Flow2', screen, swap)
    phone = pk.over('Phone_AddScreenUI', body, screen, mask=scr)
    sync(sc, pk)

    # ---- place phone
    k.section('Phone_Place')
    sh = shadow(k, 'Phone', 1310, 1010, 520, 90, 0.6, 70)
    sc.add_layer(sh, blend=Anim([(0, 0), (16, 1), (t_push, 1), (n, 0)], ['out', 'linear', 'in']))
    pc = AnimXY([(0, (1310, 548 + 1020)), (16, (1310, 548)), (t_push, (1310, 548)), (n, (1310 - 1500, 548))],
                ['out', 'linear', 'in'])
    sc.add_layer(phone, center=pc, size=0.43 / PHONE_RES, mb=True)

    # ---- pop-out cards beside the phone
    def popcard(name, ic, solid, title, sub, t0, t1):
        k.section('Popout_' + name)
        c = card(k, name, 860, 690, 420, 112, 30, CARD2, EDGE)
        dm = k.ellipse_mask(name + '_IcDisc', 920, 746, 30)
        c = k.over(name + '_AddDisc', c, k.fill(name + '_IcDiscFill', '#22301A', dm))
        ic_ = icon_solid(k, name + '_Ic', ic, 920, 746, 30, ACC) if solid else icon(k, name + '_Ic', ic, 920, 746, 30, ACC, stroke=3.5)
        c = k.over(name + '_AddIcon', c, ic_)
        c = k.over(name + '_AddTitle', c, k.text(name + '_Title', title, 972, 728, 22, WHITE, 'Inter', 'SemiBold', 'left'))
        c = k.over(name + '_AddSub', c, k.text(name + '_Sub', sub, 972, 768, 18, GREY, 'Inter', 'Medium', 'left'))
        c = k.freeze(name, c)
        p, b = pop(k, name, c, t0, 1070, 746, dur=14, from_scale=0.5, dy=0, t_out=t1)
        p = k.xf(name + '_FromPhone', p, dx=Anim([(t0, 260), (t0 + 14, 0)], 'out'))
        return p, b
    p1, b1 = popcard('Toast_Confirmed', 'check', False, 'Transaction confirmed', '0.4s  ·  fee $0.12', t_ok + 6, t_sw + 2)
    sc.add_layer(p1, blend=b1)
    p2, b2 = popcard('Toast_Swapped', 'bolt', True, 'Swap complete', 'BTC → ETH in 1.2s', v('swaps', -5), None)
    sc.add_layer(k.xf('Toast_Swapped_PushOut', p2, dx=PUSH), blend=b2)

    # push everything left at the end (handled per layer above for the phone); headline pushes via t_out
    return sc.finish(camera={'Size': Anim([(0, 1.0), (n, 1.03)], 'soft'), 'Pivot': (0.5, 0.5)})


# ================================================================ C04
def chart_points(n=56, seed=7):
    random.seed(seed)
    vals = [36000]
    for i in range(1, n):
        drift = 230 + 120 * math.sin(i / 6.0)
        vals.append(vals[-1] + drift + random.uniform(-620, 620))
    # pin the last value
    span = vals[-1] - vals[0]
    vals = [vals[0] + (v_ - vals[0]) * (48256.8 - 36000) / span for v_ in vals]
    return vals


def smooth_nodes(pts, tension=0.18):
    nodes = []
    for i, p in enumerate(pts):
        p0 = pts[i - 1] if i > 0 else p
        p2 = pts[i + 1] if i < len(pts) - 1 else p
        tx, ty = (p2[0] - p0[0]) * tension, (p2[1] - p0[1]) * tension
        nodes.append({'p': p, 'in': (p[0] - tx, p[1] - ty) if i > 0 else None,
                      'out': (p[0] + tx, p[1] + ty) if i < len(pts) - 1 else None})
    return nodes


def poly_at(pts, frac):
    """point at arc-length fraction"""
    segs = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    tot = sum(segs)
    d = frac * tot
    for i, s in enumerate(segs):
        if d <= s or i == len(segs) - 1:
            u = d / s if s else 0
            return (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * u, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * u)
        d -= s


def y_at_x(pts, x):
    for i in range(len(pts) - 1):
        if pts[i][0] <= x <= pts[i + 1][0]:
            u = (x - pts[i][0]) / (pts[i + 1][0] - pts[i][0])
            return pts[i][1] + (pts[i + 1][1] - pts[i][1]) * u
    return pts[-1][1]


def c04():
    sc = Scene(3)
    k = sc.k
    v = sc.v
    n = sc.n
    background(sc)
    t_ex = 112
    # card geometry
    CX, CY, CW, CH = 200, 262, 1520, 676
    e, eb = eyebrow(sc, 'Eb_Track', '03', 'Track', 204, 170, v('real', -8), t_out=t_ex)
    sc.add_layer(e, blend=eb)
    hl, hc = headline(sc, 'HL_Realtime_Portfolio', ['Real-time portfolio tracking'], 1716, 172, 40, 0, align='right',
                      t_out=t_ex, hl=('portfolio',), font=('Inter Display', 'SemiBold'),
                      word_times=[v('real', -3), v('portfolio', -3), v('tracking', -3)])
    sc.add_layer(hl, mask=hc)

    k.section('Chart_Card')
    cardn = card(k, 'ChartCard', CX, CY, CW, CH, 40, CARD, EDGE)
    layers = []
    layers.append(k.text('Bal_Label', 'Total balance', CX + 60, CY + 70, 22, GREY, 'Inter', 'Medium', 'left'))
    bal = k.text('Bal_Value', '$48,256.80', CX + 60, CY + 150, 70, WHITE, 'Inter Display', 'Bold', 'left',
                 expr=num_expr(v('real', 0), v('real', 34), 36000, 48256.80, '$%s', 2))
    bw = text_w('$48,256.80', 70)
    layers.append(pill(k, 'Bal_Change', CX + 60 + bw + 30, CY + 124, 150, 52, '#22301A', '+12.4%', 22, ACC,
                       ('Inter', 'Bold')))
    # timeframe tabs
    tabs = ['1D', '1W', '1M', '3M', '1Y', 'ALL']
    tx0 = CX + CW - 60 - 6 * 84
    for i, t in enumerate(tabs):
        layers.append(k.text('Tab_' + t, t, tx0 + i * 84 + 42, CY + 74, 20, GREY, 'Inter', 'SemiBold', 'center'))
    for L_ in layers:
        cardn = k.over('ChartCard_Add_' + L_, cardn, L_)
    cardn = k.freeze('ChartCard', cardn)
    cardn = k.over('ChartCard_AddBalance', cardn, bal)
    k.section('Tab_Highlight')
    hlx = AnimXY([(0, (tx0 + 1 * 84 + 42, CY + 74)), (v('tracking', -2), (tx0 + 1 * 84 + 42, CY + 74)),
                  (v('tracking', 10), (tx0 + 2 * 84 + 42, CY + 74))], ['linear', 'inout'])
    tm = k.rect_mask('Tab_Pill', 0, 0, 74, 44, 22, center=hlx)
    tabp = k.fill('Tab_PillFill', ACC, tm, 0.16)
    tme = k.rect_mask('Tab_PillEdge', 0, 0, 74, 44, 22, center=hlx, border=1.5)
    tabe = k.fill('Tab_PillEdgeFill', ACC, tme)
    cardn = k.over('ChartCard_AddTabPill', cardn, tabp)
    cardn = k.over('ChartCard_AddTabEdge', cardn, tabe)

    # chart area
    k.section('Chart_Grid')
    ax0, ay0, ax1, ay1 = CX + 60, CY + 250, CX + CW - 150, CY + CH - 60
    prev = None
    labels = []
    for i in range(5):
        yy = ay0 + i * (ay1 - ay0) / 4
        prev = k.rect_mask('Grid%d' % i, ax0, yy, ax1 - ax0, 1.2, inp=prev)
        labels.append(k.text('YLabel%d' % i, '$%dK' % (50 - i * 4), CX + CW - 60, yy, 17, GREY2, 'Inter', 'Medium', 'right'))
    grid = k.fill('Grid_Lines', WHITE, prev, 0.06)
    for i, L_ in enumerate(labels):
        grid = k.over('Grid_AddLabel%d' % i, grid, L_)
    grid = k.freeze('Chart_Grid', grid)
    cardn = k.over('ChartCard_AddGrid', cardn, grid)

    vals = chart_points()
    lo, hi = 34000, 50000
    pts = [(ax0 + i * (ax1 - ax0) / (len(vals) - 1), ay1 - (val - lo) / (hi - lo) * (ay1 - ay0)) for i, val in enumerate(vals)]
    t_d0, t_d1 = v('portfolio', -4), v('interactive', -4)
    k.section('Chart_Line')
    wo = Anim([(t_d0, 0), (t_d1, 1)], 'inout')
    lm = k.poly_mask('Chart_Line', smooth_nodes(pts), closed=False, border=5, write_on=wo)
    line = k.fill('Chart_LineGreen', ACC, lm)
    line = k.glow('Chart_LineGlow', line, 0.6, 14)
    # area fill revealed left->right following the tip
    k.section('Chart_Area')
    area_nodes = smooth_nodes(pts) + [{'p': (ax1, ay1), 'in': None, 'out': None}, {'p': (ax0, ay1), 'in': None, 'out': None}]
    am = k.poly_mask('Chart_AreaShape', area_nodes, closed=True)
    samples = []
    for f in range(t_d0, t_d1 + 1, 3):
        frac = wo.value_at(f)
        samples.append((f, poly_at(pts, frac)))
    if samples[-1][0] != t_d1:
        samples.append((t_d1, pts[-1]))
    wkeys = [(f, max(p[0] - ax0, 1)) for f, p in samples]
    ckeys = [(f, (ax0 + max(p[0] - ax0, 1) / 2, (ay0 + ay1) / 2 - 40)) for f, p in samples]
    rv = k.rect_mask('Chart_AreaReveal', 0, 0, Anim(wkeys, 'linear'), ay1 - ay0 + 120,
                     center=AnimXY(ckeys, 'linear'), inp=am, paint='Multiply')
    area = k.gradient('Chart_AreaGradient', [(0, ACC, 0.30), (1, ACC, 0.0)], 'Linear', (0, ay0), (0, ay1), rv)
    # tip dot
    k.section('Chart_TipDot')
    tip = AnimXY(samples, 'linear')
    dm = k.ellipse_mask('Chart_Tip', 0, 0, 9, center=tip)
    gm = k.ellipse_mask('Chart_TipHalo', 0, 0, Anim([(t_d1, 22), (t_d1 + 10, 30), (t_d1 + 20, 22)], 'soft'), center=tip)
    halo = k.fill('Chart_TipHaloFill', ACC, gm, 0.28)
    dot = k.fill('Chart_TipFill', WHITE, dm)
    tipn = k.over('Chart_TipAddDot', halo, dot)
    chart = k.over('Chart_AreaPlusLine', area, line)
    chart = k.over('Chart_AddTip', chart, tipn, blend=Anim([(t_d0, 0), (t_d0 + 4, 1)], 'out'))
    cardn = k.over('ChartCard_AddChart', cardn, chart)

    # interactive scrub: cursor + crosshair + tooltip with live value
    k.section('Chart_Scrub')
    ti = v('interactive', 0)
    xA, xB = ax0 + (ax1 - ax0) * 0.80, ax0 + (ax1 - ax0) * 0.52
    cur_keys = [(ti - 6, (xA + 260, ay1 + 120)), (ti + 6, (xA, y_at_x(pts, xA))), (ti + 12, (xA, y_at_x(pts, xA)))]
    for f in range(ti + 14, ti + 33, 2):
        u = (f - (ti + 14)) / 18.0
        u = u * u * (3 - 2 * u)
        x_ = xA + (xB - xA) * u
        cur_keys.append((f, (x_, y_at_x(pts, x_))))
    cur = AnimXY(cur_keys, 'linear')
    cxk = [(f, p[0]) for f, p in cur_keys]
    cross = k.rect_mask('Scrub_Crosshair', 0, 0, 2, ay1 - ay0,
                        center=AnimXY([(f, (x_, (ay0 + ay1) / 2)) for f, x_ in cxk], 'linear'))
    crossf = k.fill('Scrub_CrosshairFill', WHITE, cross, 0.35)
    ring = k.ellipse_mask('Scrub_Cursor', 0, 0, 16, center=cur, border=3)
    ringf = k.fill('Scrub_CursorFill', WHITE, ring)
    pdot = k.ellipse_mask('Scrub_Point', 0, 0, 7, center=cur)
    pdf = k.fill('Scrub_PointFill', ACC, pdot)
    tip_keys = [(f, (p[0], p[1] - 92)) for f, p in cur_keys]
    tipc = AnimXY(tip_keys, 'linear')
    tb = k.rect_mask('Scrub_Tooltip', 0, 0, 236, 88, 20, center=tipc)
    tbf = k.fill('Scrub_TooltipFill', CARD2, tb)
    tbe = k.rect_mask('Scrub_TooltipEdge', 0, 0, 236, 88, 20, center=tipc, border=1.5)
    tbef = k.fill('Scrub_TooltipEdgeFill', EDGE, tbe)
    # value text follows the cursor and shows the value under it
    vals_by_frame = []
    for f, p in cur_keys:
        frac = (p[0] - ax0) / (ax1 - ax0)
        val = lo + (ay1 - p[1]) / (ay1 - ay0) * (hi - lo)
        vals_by_frame.append((f, val))
    vk = Anim(vals_by_frame, 'linear')
    tbl = ','.join('%.2f' % vk.value_at(f) for f in range(ti - 6, ti + 34))
    expr = (':local v={%s}; local i=math.max(1,math.min(%d,math.floor(time)-%d+1)); local s=string.format("%%.2f",v[i]); '
            'local a,b=s:match("(%%d+)(.*)"); a=a:reverse():gsub("(%%d%%d%%d)","%%1,"):reverse():gsub("^,",""); '
            'return Text("$"..a..b)') % (tbl, len(tbl.split(',')), ti - 6)
    tv = k.text('Scrub_TooltipValue', '$46,912.40', 0, 0, 24, WHITE, 'Inter', 'Bold', 'center', expr=expr)
    tv = k.xf('Scrub_TooltipValueFollow', tv, dx=Anim([(f, p[0]) for f, p in tip_keys], 'linear'),
              dy=Anim([(f, p[1] + 14 - 1080 / 2 + 540) for f, p in tip_keys], 'linear'), mb=False)
    td = k.text('Scrub_TooltipDate', 'NOV 04  ·  14:20', 0, 0, 15, GREY, 'Inter', 'SemiBold', 'center')
    td = k.xf('Scrub_TooltipDateFollow', td, dx=Anim([(f, p[0]) for f, p in tip_keys], 'linear'),
              dy=Anim([(f, p[1] - 18) for f, p in tip_keys], 'linear'), mb=False)
    scrub = k.over('Scrub_AddCross', crossf, tbf)
    scrub = k.over('Scrub_AddTipEdge', scrub, tbef)
    scrub = k.over('Scrub_AddValue', scrub, tv)
    scrub = k.over('Scrub_AddDate', scrub, td)
    scrub = k.over('Scrub_AddPoint', scrub, pdf)
    # tooltip + crosshair appear once the cursor has landed on the line; the cursor itself flies in first
    cardn = k.over('ChartCard_AddScrub', cardn, scrub,
                   blend=Anim([(ti + 5, 0), (ti + 9, 1), (t_ex, 1), (t_ex + 6, 0)], ['out', 'linear', 'in']))
    cardn = k.over('ChartCard_AddCursor', cardn, ringf,
                   blend=Anim([(ti - 6, 0), (ti - 2, 1), (t_ex, 1), (t_ex + 6, 0)], ['out', 'linear', 'in']))

    # card motion: slide in from right (push), zoom through at the end
    k.section('Chart_Card_Move')
    cm = k.xf('ChartCard_Move', cardn, dx=Anim([(0, 1700), (18, 0)], 'out'),
              scale=Anim([(t_ex, 1), (n, 1.18)], 'in'), pivot=(960, 600), mb=False)
    sc.add_layer(cm, blend=Anim([(t_ex + 2, 1), (n, 0)], 'in'))
    return sc.finish(camera={'Size': Anim([(0, 1.0), (n, 1.025)], 'soft'), 'Pivot': (0.5, 0.5)})


# ================================================================ C05
def c05():
    sc = Scene(4)
    k = sc.k
    v = sc.v
    n = sc.n
    background(sc)
    t_sw = v('analyze', -9)
    t_ex = 90
    e1, eb1 = eyebrow(sc, 'Eb_Alerts', '04', 'Alerts', 172, 360, 2, t_out=t_sw)
    sc.add_layer(e1, blend=eb1)
    h1, c1 = headline(sc, 'HL_Price_Alerts', ['Set price', 'alerts.'], 170, 460, 92, 0, t_out=t_sw, gap=0.62,
                      hl=('alerts.',), word_times=[v('set', -2), v('price', -2), v('alerts', -3)])
    sc.add_layer(h1, mask=c1)
    e2, eb2 = eyebrow(sc, 'Eb_Trends', '05', 'Trends', 172, 360, v('analyze', -2), t_out=t_ex)
    sc.add_layer(e2, blend=eb2)
    h2, c2 = headline(sc, 'HL_Analyze_Trends', ['Analyze', 'trends.'], 170, 460, 92, 0, t_out=t_ex, gap=0.62,
                      hl=('trends.',), word_times=[v('analyze', -2), v('trends', -2)])
    sc.add_layer(h2, mask=c2)

    # alert setup card
    X0 = 980
    k.section('Alert_Setup_Card')
    sc_ = card(k, 'AlertSetup', X0, 470, 760, 210, 36, CARD, EDGE)
    sc_ = k.over('AlertSetup_AddBell', sc_, icon(k, 'AlertSetup_Bell', 'bell', X0 + 70, 540, 40, ACC))
    sc_ = k.over('AlertSetup_AddLabel', sc_, k.text('AlertSetup_Label', 'Price alert', X0 + 112, 540, 22, GREY, 'Inter', 'Medium', 'left'))
    sc_ = k.over('AlertSetup_AddRule', sc_, k.text('AlertSetup_Rule', 'BTC  ≥  $68,000', X0 + 50, 618, 40, WHITE,
                                                     'Inter Display', 'Bold', 'left'))
    sc_ = k.freeze('AlertSetup', sc_)
    tg = v('price', 0)
    trk = k.rect_mask('Toggle_Track', X0 + 610, 590, 104, 56, 28)
    trk_off = k.fill('Toggle_TrackOff', '#2E352E', trk)
    trk_on = k.fill('Toggle_TrackOn', ACC, trk)
    tog = k.over('Toggle_TrackSwitch', trk_off, trk_on, blend=Anim([(tg, 0), (tg + 8, 1)], 'out'))
    kn = k.ellipse_mask('Toggle_Knob', 0, 0, 22, center=AnimXY([(tg, (X0 + 638, 618)), (tg + 10, (X0 + 686, 618))], 'back'))
    tog = k.over('Toggle_AddKnob', tog, k.fill('Toggle_KnobFill', WHITE, kn))
    sc_ = k.over('AlertSetup_AddToggle', sc_, tog)
    p, b = pop(k, 'AlertSetup', sc_, v('set', -4), X0 + 380, 575, dur=16, from_scale=0.8, dy=60, t_out=t_sw, out_dur=10,
               out_dy=-80)
    sc.add_layer(p, blend=b)

    # notification banner (drops in on "alerts")
    k.section('Alert_Notification')
    na = v('alerts', -4)
    nb = card(k, 'Notif', X0, 250, 760, 170, 38, CARD2, EDGE)
    ab = k.rect_mask('Notif_AppIcon', X0 + 36, 285, 72, 72, 18)
    nb = k.over('Notif_AddAppIcon', nb, k.fill('Notif_AppIconFill', CHAR, ab))
    mk = icon_solid(k, 'Notif_AppMark', 'bolt', X0 + 72, 321, 40, ACC)
    nb = k.over('Notif_AddAppMark', nb, mk)
    nb = k.over('Notif_AddApp', nb, k.text('Notif_App', 'VAULTX', X0 + 132, 296, 17, GREY, 'Inter', 'SemiBold', 'left', track=1.1))
    nb = k.over('Notif_AddNow', nb, k.text('Notif_Now', 'now', X0 + 724, 296, 17, GREY, 'Inter', 'Medium', 'right'))
    nb = k.over('Notif_AddTitle', nb, k.text('Notif_Title', 'BTC just crossed $68,000', X0 + 132, 340, 28, WHITE,
                                             'Inter', 'Bold', 'left'))
    nb = k.over('Notif_AddBody', nb, k.text('Notif_Body', 'Your price alert triggered  ·  +3.1% today', X0 + 132, 384,
                                            20, GREY, 'Inter', 'Medium', 'left'))
    nb = k.freeze('Notif', nb)
    nb = k.xf('Notif_Drop', nb, dy=Anim([(na, -320), (na + 16, 0), (t_sw, 0), (t_sw + 10, -360)], ['back', 'linear', 'in']))
    sc.add_layer(nb, blend=Anim([(na, 0), (na + 6, 1), (t_sw + 4, 1), (t_sw + 10, 0)], ['out', 'linear', 'in']))
    # bell shake badge
    k.section('Alert_Bell_Badge')
    bm = k.ellipse_mask('BellBadge', X0 + 740, 256, 34)
    bb = k.fill('BellBadgeFill', ACC, bm)
    bi = icon(k, 'BellBadge', 'bell', X0 + 740, 256, 38, BG, stroke=3.6)
    bi = k.xf('BellBadge_Shake', bi, rot=Anim([(na + 8, 0), (na + 11, 16), (na + 14, -14), (na + 17, 10), (na + 20, -6),
                                                (na + 24, 0)], 'soft'), pivot=(X0 + 740, 236))
    badge = k.over('BellBadge_AddIcon', bb, bi)
    bp, bbb = pop(k, 'BellBadge', badge, na + 6, X0 + 740, 256, dur=12, from_scale=0.2, dy=0, t_out=t_sw, out_dur=8)
    sc.add_layer(bp, blend=bbb)

    # weekly trend bars (second data viz)
    k.section('Trend_Card')
    TX, TY, TW, TH = X0, 250, 760, 600
    tc = card(k, 'TrendCard', TX, TY, TW, TH, 40, CARD, EDGE)
    tc = k.over('TrendCard_AddTitle', tc, k.text('TrendCard_Title', 'Weekly trend', TX + 50, TY + 66, 28, WHITE, 'Inter', 'Bold', 'left'))
    tc = k.over('TrendCard_AddSub', tc, k.text('TrendCard_Sub', 'BTC  ·  7 days', TX + 50, TY + 108, 20, GREY, 'Inter', 'Medium', 'left'))
    tc = k.over('TrendCard_AddPill', tc, pill(k, 'TrendCard_Bull', TX + TW - 220, TY + 46, 170, 50, '#22301A', 'Bullish', 21, ACC,
                                              ('Inter', 'Bold'), icon_key='arrowup', icon_color=ACC))
    tc = k.freeze('TrendCard', tc)
    heights = [0.38, 0.52, 0.44, 0.63, 0.58, 0.79, 0.92]
    days = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
    by1 = TY + TH - 90
    bmax = 330
    bw_ = 62
    gap_ = (TW - 100 - 7 * bw_) / 6
    ta = v('analyze', 2)
    tops = []
    for i, (h_, d_) in enumerate(zip(heights, days)):
        k.section('Trend_Bar%d' % (i + 1))
        x = TX + 50 + i * (bw_ + gap_)
        hh = bmax * h_
        bm_ = k.rect_mask('Bar%d' % (i + 1), x, by1 - hh, bw_, hh, 14)
        col = ACC if i == 6 else '#3C4A33'
        bar = k.fill('Bar%d_Fill' % (i + 1), col, bm_)
        t0 = ta + i * 3
        bar = k.xf('Bar%d_Grow' % (i + 1), bar, scale=Anim([(t0, 0.0), (t0 + 14, 1.0)], 'back'), pivot=(x + bw_ / 2, by1),
                   mb=False)
        tc = k.over('TrendCard_AddBar%d' % (i + 1), tc, bar)
        tc = k.over('TrendCard_AddDay%d' % (i + 1), tc, k.text('Day%d' % (i + 1), d_, x + bw_ / 2, by1 + 44, 18, GREY,
                                                              'Inter', 'SemiBold', 'center'))
        tops.append((x + bw_ / 2, by1 - hh - 26))
    k.section('Trend_Line')
    tl0 = ta + 10
    trm = k.poly_mask('TrendLine', smooth_nodes(tops, 0.2), closed=False, border=4,
                      write_on=Anim([(tl0, 0), (tl0 + 16, 1)], 'inout'))
    trl = k.fill('TrendLine_Fill', WHITE, trm, 0.9)
    tc = k.over('TrendCard_AddLine', tc, trl)
    ex = tops[-1]
    lab = pill(k, 'TrendGain', ex[0] - 180, ex[1] - 76, 150, 46, ACC, '+8.6%', 21, BG, ('Inter', 'Bold'))
    lp, lb = pop(k, 'TrendGain', lab, tl0 + 14, ex[0] - 105, ex[1] - 53, dur=12, from_scale=0.4, dy=10)
    tc = k.over('TrendCard_AddGain', tc, lp, blend=lb)
    tcm = k.xf('TrendCard_Move', tc, dy=Anim([(t_sw + 2, 900), (t_sw + 18, 0)], 'out'),
               scale=Anim([(t_ex, 1), (n, 0.7)], 'in'), pivot=(TX + TW / 2, TY + TH / 2), mb=False)
    sc.add_layer(tcm, blend=Anim([(t_sw + 1, 0), (t_sw + 6, 1), (t_ex + 2, 1), (n, 0)], ['out', 'linear', 'in']))
    return sc.finish(camera={'Size': Anim([(0, 1.06), (12, 1.0), (n, 1.02)], ['out', 'soft']), 'Pivot': (0.5, 0.5)})


if __name__ == '__main__':
    print(c03())
    print(c04())
    print(c05())
