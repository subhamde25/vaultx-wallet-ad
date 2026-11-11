"""C06 Dashboard insights, C07 Security, C08 Investing/Trading/Holding, C09 End card + CTA."""
import math
import random
from fu import Anim, AnimXY
from kit import Kit, COL_W
from vx_common import (PHONE_RES, Scene, background, headline, card, pill, pop, icon, icon_solid, icon_masks, token, text_w,
                       logo, phone_frame, PW, PH, SX0, SY0, SW, SH, shadow, ICONS,
                       ACC, ACC_D, WHITE, GREY, GREY2, CARD, CARD2, EDGE, CHAR, RED, BG, DISPLAY,
                       BTC_C, ETH_C, SOL_C)
from scenes_b import eyebrow, sync, num_expr, smooth_nodes, chart_points


def arc_nodes(cx, cy, r, a0, a1, ry=None):
    """bezier nodes along a circular/elliptical arc from angle a0 to a1 (degrees, 0 = up, clockwise)."""
    ry = r if ry is None else ry
    segs = max(1, int(math.ceil(abs(a1 - a0) / 45.0)))
    da = (a1 - a0) / segs
    k_ = 4.0 / 3.0 * math.tan(math.radians(da) / 4.0)
    nodes = []
    for i in range(segs + 1):
        a = math.radians(a0 + i * da)
        x, y = cx + r * math.sin(a), cy - ry * math.cos(a)
        tx, ty = r * math.cos(a), ry * math.sin(a)    # derivative direction (clockwise)
        nodes.append({'p': (x, y), 'in': (x - tx * k_, y - ty * k_) if i > 0 else None,
                      'out': (x + tx * k_, y + ty * k_) if i < segs else None})
    return nodes


# ================================================================ phone dashboard screen
def ui_dashboard(pk, n, t0):
    k = pk
    k.section(n + '_DashHeader')
    g = k.canvas(n + '_Dash_Canvas')
    L = []
    av = k.ellipse_mask(n + '_DAvatar', 110, 180, 40)
    L.append(k.fill(n + '_DAvatarFill', CHAR, av))
    L.append(icon(k, n + '_DAvatarIc', 'user', 110, 180, 40, WHITE))
    L.append(k.text(n + '_DHello', 'Portfolio', 175, 162, 20, GREY, 'Inter', 'Medium', 'left'))
    L.append(k.text(n + '_DName', 'Main wallet', 175, 200, 26, WHITE, 'Inter', 'Bold', 'left'))
    L.append(icon(k, n + '_DBell', 'bell', 790, 180, 40, WHITE))
    L.append(k.text(n + '_DBalLab', 'Total balance', 450, 320, 22, GREY, 'Inter', 'Medium', 'center'))
    bal = k.text(n + '_DBal', '$48,256.80', 450, 400, 76, WHITE, 'Inter Display', 'Bold', 'center',
                 expr=num_expr(t0, t0 + 26, 41000, 48256.80, '$%s', 2))
    L.append(k.text(n + '_DChg', '+$5,312.40  (12.4%)', 450, 478, 24, ACC, 'Inter', 'SemiBold', 'center'))
    for i, L_ in enumerate(L):
        g = k.over('%s_DHeadAdd%02d' % (n, i + 1), g, L_)
    g = k.freeze(n + '_DashHeader', g)
    g = k.over(n + '_DAddBalance', g, bal)
    # mini chart
    k.section(n + '_DashChart')
    vals = chart_points(40, 11)
    lo, hi = min(vals), max(vals)
    pts = [(80 + i * 740 / 39, 760 - (v_ - lo) / (hi - lo) * 200) for i, v_ in enumerate(vals)]
    lm = k.poly_mask(n + '_DLine', smooth_nodes(pts), False, border=5, write_on=Anim([(t0, 0), (t0 + 30, 1)], 'inout'))
    g = k.over(n + '_DAddLine', g, k.fill(n + '_DLineFill', ACC, lm))
    am = k.poly_mask(n + '_DArea', smooth_nodes(pts) + [{'p': (820, 790), 'in': None, 'out': None},
                                                        {'p': (80, 790), 'in': None, 'out': None}], True)
    area = k.gradient(n + '_DAreaGrad', [(0, ACC, 0.22), (1, ACC, 0)], 'Linear', (0, 560), (0, 790), am)
    g = k.over(n + '_DAddArea', g, area, blend=Anim([(t0 + 10, 0), (t0 + 30, 1)], 'out'))
    # quick actions
    k.section(n + '_DashActions')
    st = k.canvas(n + '_DashStatic_Canvas')
    for i, (ic, lab) in enumerate([('send', 'Send'), ('download', 'Receive'), ('swap', 'Swap'), ('chart', 'Buy')]):
        x = 150 + i * 200
        dm = k.ellipse_mask('%s_DAct%d' % (n, i), x, 900, 52)
        st = k.over('%s_DAddAct%d' % (n, i), st, k.fill('%s_DActFill%d' % (n, i), '#22301A' if i else ACC, dm))
        st = k.over('%s_DAddActIc%d' % (n, i), st, icon(k, '%s_DActIc%d' % (n, i), ic, x, 900, 44, ACC if i else BG, stroke=4.5))
        st = k.over('%s_DAddActLab%d' % (n, i), st, k.text('%s_DActLab%d' % (n, i), lab, x, 990, 20, GREY, 'Inter', 'Medium', 'center'))
    # token rows
    k.section(n + '_DashTokens')
    st = k.over(n + '_DAddAssetsHdr', st, k.text(n + '_DAssets', 'Assets', 80, 1090, 26, WHITE, 'Inter', 'Bold', 'left'))
    rows = [('BTC', 'Bitcoin', '0.4182', '$28,412.07', '+2.4%'), ('ETH', 'Ethereum', '4.2010', '$14,066.12', '+5.1%'),
            ('SOL', 'Solana', '31.85', '$5,778.61', '+14.3%')]
    for i, (sym, name, amt, usd, chg) in enumerate(rows):
        y = 1180 + i * 150
        st = k.over('%s_DAddRow%d' % (n, i), st, card(k, '%s_DRow%d' % (n, i), 60, y - 60, 780, 124, 30, CARD2, None))
        st = k.over('%s_DAddCoin%d' % (n, i), st, token(k, '%s_DCoin%d' % (n, i), sym, 130, y, 36))
        st = k.over('%s_DAddName%d' % (n, i), st, k.text('%s_DName%d' % (n, i), name, 190, y - 18, 24, WHITE, 'Inter', 'SemiBold', 'left'))
        st = k.over('%s_DAddAmt%d' % (n, i), st, k.text('%s_DAmt%d' % (n, i), amt + ' ' + sym, 190, y + 22, 19, GREY, 'Inter', 'Medium', 'left'))
        st = k.over('%s_DAddUsd%d' % (n, i), st, k.text('%s_DUsd%d' % (n, i), usd, 800, y - 18, 24, WHITE, 'Inter', 'SemiBold', 'right'))
        st = k.over('%s_DAddChg%d' % (n, i), st, k.text('%s_DChg%d' % (n, i), chg, 800, y + 22, 19, ACC, 'Inter', 'SemiBold', 'right'))
    # tab bar
    k.section(n + '_DashTabBar')
    tb = k.rect_mask(n + '_DTabBar', SX0, 1650, SW, 190)
    st = k.over(n + '_DAddTabBar', st, k.fill(n + '_DTabBarFill', '#0F120F', tb))
    for i, ic in enumerate(['home', 'chart', 'swap', 'user']):
        x = 160 + i * 193
        st = k.over('%s_DAddTab%d' % (n, i), st, icon(k, '%s_DTab%d' % (n, i), ic, x, 1730, 46, ACC if i == 0 else GREY2, stroke=4))
    st = k.freeze(n + '_DashStatic', st)
    g = k.over(n + '_DAddStatic', g, st)
    return g


# ================================================================ C06
def donut(k, name, cx, cy, r, th, t0):
    parts = [(0.45, BTC_C, 'BTC'), (0.30, ETH_C, 'ETH'), (0.15, SOL_C, 'SOL'), (0.10, GREY2, 'Other')]
    g = k.canvas(name + '_Canvas')
    tm = k.ellipse_mask(name + '_Track', cx, cy, r, border=th)
    g = k.over(name + '_AddTrack', g, k.fill(name + '_TrackFill', '#232A22', tm))
    a = 0
    for i, (frac, col, lab) in enumerate(parts):
        a1 = a + frac * 360 - 3
        ts = t0 + i * 5
        m = k.poly_mask('%s_Seg%d' % (name, i), arc_nodes(cx, cy, r, a + 1.5, a1), False, border=th,
                        write_on=Anim([(ts, 0), (ts + 14, 1)], 'out'))
        g = k.over('%s_AddSeg%d' % (name, i), g, k.fill('%s_SegFill%d' % (name, i), col, m))
        a += frac * 360
    return g, parts


def c06():
    sc = Scene(5)
    k = sc.k
    v = sc.v
    n = sc.n
    background(sc)
    t_ex = 128
    hl1, hc1 = headline(sc, 'HL_Confident_Decisions', ['Make confident decisions.'], 960, 118, 50, 0, align='center',
                        t_out=v('powerful', -10), hl=('decisions.',),
                        word_times=[v('make', -2), v('confident', -2), v('decisions', -2)])
    sc.add_layer(hl1, mask=hc1)
    hl2, hc2 = headline(sc, 'HL_Powerful_Insights', ['Powerful insights, built in.'], 960, 118, 50, 0, align='center',
                        t_out=t_ex, hl=('insights,',),
                        word_times=[v('powerful', -2), v('insights', -2), v('built', -2), v('built', 4)])
    sc.add_layer(hl2, mask=hc2)

    # phone
    pk = Kit(sc.c, int(PW * PHONE_RES), int(PH * PHONE_RES), prefix='P_', x0=k.x + COL_W, y0=0, aw=PW, ah=PH)
    body, scr = phone_frame(pk, 'Phone')
    dash = ui_dashboard(pk, 'D', 6)
    pk.section('Phone_Assemble')
    phone = pk.over('Phone_AddDashboard', body, dash, mask=scr)
    sync(sc, pk)
    k.section('Phone_Place')
    sh = shadow(k, 'Phone', 960, 1010, 500, 80, 0.6, 70)
    sc.add_layer(sh, blend=Anim([(0, 0), (16, 1)], 'out'))
    td = v('dashboard', -2)
    pc = AnimXY([(0, (960, 600 + 1020)), (18, (960, 600)), (td, (960, 600)), (td + 18, (960, 640))], ['out', 'linear', 'inout'])
    sc.add_layer(phone, center=pc, size=Anim([(0, 0.44 / PHONE_RES), (td, 0.44 / PHONE_RES), (td + 18, 0.5 / PHONE_RES)], ['linear', 'linear', 'inout']), mb=True)

    # floating insight cards
    def float_card(name, node, t0, cx, cy, side):
        p, b = pop(k, name, node, t0, cx, cy, dur=16, from_scale=0.6, dy=0, t_out=t_ex, out_dur=12)
        p = k.xf(name + '_FromPhone', p, dx=Anim([(t0, -260 * side), (t0 + 16, 0), (td, 0), (td + 20, 40 * side)],
                                                  ['out', 'linear', 'inout']), mb=True)
        sc.add_layer(p, blend=b)

    k.section('Card_Allocation')
    AX, AY, AW, AH = 230, 300, 470, 330
    ac = card(k, 'Alloc', AX, AY, AW, AH, 32, CARD, EDGE)
    ac = k.over('Alloc_AddTitle', ac, k.text('Alloc_Title', 'Allocation', AX + 36, AY + 50, 22, GREY, 'Inter', 'SemiBold', 'left'))
    parts = [(0.45, BTC_C, 'BTC'), (0.30, ETH_C, 'ETH'), (0.15, SOL_C, 'SOL'), (0.10, GREY2, 'Other')]
    for i, (frac, col, lab) in enumerate(parts):
        yy = AY + 120 + i * 46
        dm = k.ellipse_mask('Alloc_Leg%d' % i, AX + 262, yy, 8)
        ac = k.over('Alloc_AddLegDot%d' % i, ac, k.fill('Alloc_LegDot%d' % i, col, dm))
        ac = k.over('Alloc_AddLeg%d' % i, ac, k.text('Alloc_LegLab%d' % i, lab, AX + 284, yy, 20, WHITE, 'Inter', 'SemiBold', 'left'))
        ac = k.over('Alloc_AddPct%d' % i, ac, k.text('Alloc_LegPct%d' % i, '%d%%' % round(frac * 100), AX + AW - 36, yy, 20,
                                                     GREY, 'Inter', 'Medium', 'right'))
    ac = k.freeze('Alloc', ac)
    dn, parts = donut(k, 'Alloc_Donut', AX + 130, AY + 190, 82, 26, v('decisions', 2))
    ac = k.over('Alloc_AddDonut', ac, dn)
    float_card('Card_Allocation', ac, v('decisions', -4), AX + AW / 2, AY + AH / 2, 1)

    k.section('Card_Insight')
    IX, IY, IW, IH = 1220, 300, 470, 220
    ic_ = card(k, 'Insight', IX, IY, IW, IH, 32, CARD, EDGE)
    ic_ = k.over('Insight_AddSpark', ic_, icon_solid(k, 'Insight_Spark', 'spark', IX + 52, IY + 52, 34, ACC))
    ic_ = k.over('Insight_AddTag', ic_, k.text('Insight_Tag', 'AI insight', IX + 84, IY + 52, 22, ACC, 'Inter', 'SemiBold', 'left'))
    ic_ = k.over('Insight_AddL1', ic_, k.text('Insight_L1', 'ETH momentum is', IX + 36, IY + 114, 28, WHITE, 'Inter', 'Bold', 'left'))
    ic_ = k.over('Insight_AddL2', ic_, k.text('Insight_L2', 'strengthening', IX + 36, IY + 156, 28, WHITE, 'Inter', 'Bold', 'left'))
    ic_ = k.over('Insight_AddPct', ic_, k.text('Insight_Pct', '+8.2%  7d', IX + IW - 36, IY + 52, 20, ACC, 'Inter', 'SemiBold', 'right'))
    ic_ = k.freeze('Insight', ic_)
    float_card('Card_Insight', ic_, v('insights', -4), IX + IW / 2, IY + IH / 2, -1)

    k.section('Card_Risk')
    RX, RY, RW, RH = 1220, 560, 470, 170
    rc = card(k, 'Risk', RX, RY, RW, RH, 32, CARD, EDGE)
    rc = k.over('Risk_AddLab', rc, k.text('Risk_Lab', 'Risk level', RX + 36, RY + 48, 22, GREY, 'Inter', 'SemiBold', 'left'))
    rc = k.over('Risk_AddVal', rc, k.text('Risk_Val', 'Low', RX + RW - 36, RY + 48, 26, ACC, 'Inter', 'Bold', 'right'))
    trk = k.rect_mask('Risk_Track', RX + 36, RY + 110, RW - 72, 16, 8)
    rc = k.over('Risk_AddTrack', rc, k.fill('Risk_TrackFill', '#263022', trk))
    rc = k.freeze('Risk', rc)
    tr0 = v('insights', 8)
    fw = Anim([(tr0, 1), (tr0 + 18, (RW - 72) * 0.28)], 'out')
    fm = k.rect_mask('Risk_Bar', RX + 36, RY + 110, fw, 16, 8,
                     center=AnimXY([(tr0, (RX + 36, RY + 118)), (tr0 + 18, (RX + 36 + (RW - 72) * 0.14, RY + 118))], 'out'))
    rc = k.over('Risk_AddBar', rc, k.fill('Risk_BarFill', ACC, fm))
    float_card('Card_Risk', rc, v('insights', 4), RX + RW / 2, RY + RH / 2, -1)

    k.section('Card_TopMover')
    MX, MY, MW, MH = 230, 670, 470, 150
    mc = card(k, 'Mover', MX, MY, MW, MH, 32, CARD, EDGE)
    mc = k.over('Mover_AddCoin', mc, token(k, 'Mover_Coin', 'SOL', MX + 76, MY + MH / 2, 36))
    mc = k.over('Mover_AddLab', mc, k.text('Mover_Lab', 'Top mover', MX + 136, MY + 52, 20, GREY, 'Inter', 'Medium', 'left'))
    mc = k.over('Mover_AddName', mc, k.text('Mover_Name', 'Solana', MX + 136, MY + 96, 28, WHITE, 'Inter', 'Bold', 'left'))
    mc = k.over('Mover_AddPct', mc, pill(k, 'Mover_Pct', MX + MW - 176, MY + 50, 140, 50, '#22301A', '+14.3%', 21, ACC,
                                         ('Inter', 'Bold')))
    mc = k.freeze('Mover', mc)
    float_card('Card_TopMover', mc, v('built', -4), MX + MW / 2, MY + MH / 2, 1)

    # exit: collapse toward the centre and darken (into the security scene)
    k.section('Exit_Darken')
    dk = k.fill('Exit_Dark', '#000000', None, 1.0)
    sc.add_layer(dk, blend=Anim([(t_ex, 0), (n, 0.65)], 'in'))
    return sc.finish(camera={'Size': Anim([(0, 1.0), (td, 1.02), (n, 1.1)], ['soft', 'in']), 'Pivot': (0.5, 0.52)})


# ================================================================ C07 security
def fingerprint_arcs(cx, cy, s):
    """own fingerprint drawing: nested arcs with gaps (s = scale px per unit)."""
    arcs = []
    spec = [(1.0, -60, 70), (1.0, 95, 160), (1.8, -110, 25), (1.8, 50, 175), (2.6, -150, -30), (2.6, 0, 120),
            (3.4, -165, -10), (3.4, 20, 150), (4.2, -150, 140), (5.0, -135, 0), (5.0, 25, 125), (5.8, -120, 115),
            (6.6, -105, 100)]
    for i, (r, a0, a1) in enumerate(spec):
        arcs.append(arc_nodes(cx, cy + 0.6 * s, r * s, a0, a1, r * s * 1.22))
    return arcs


def c07():
    sc = Scene(6)
    k = sc.k
    v = sc.v
    n = sc.n
    background(sc, dim=Anim([(0, 0.45), (10, 0.35), (n - 12, 0.35), (n, 0.5)], ['out', 'linear', 'in']))
    SXC, SYC = 960, 455
    t_bank = v('bank', 0)
    t_enc = v('encryption', 0)
    t_bio = v('biometric', 0)
    t_pro = v('your3', 0)
    t_ex = n - 10

    # encryption stream (hex columns)
    k.section('Encryption_Stream')
    random.seed(3)
    st = k.canvas('Hex_Canvas')
    for i, x in enumerate([250, 420, 590, 1330, 1500, 1670]):
        rows = '\n'.join(' '.join('%02X' % random.randint(0, 255) for _ in range(3)) for _ in range(26))
        t = k.freeze('Hex_Col%d' % (i + 1), k.text('Hex_Col%d' % (i + 1), rows, x, 540, 20, ACC, 'Inter', 'Medium', 'center'))
        t = k.xf('Hex_Col%d_Scroll' % (i + 1), t, dy=Anim([(0, 120 + i * 30), (n, -260 - i * 20)], 'linear'), mb=False)
        st = k.over('Hex_AddCol%d' % (i + 1), st, t)
    fm = k.ellipse_mask('Hex_Fade', 960, 520, 900, 420, soft=320)
    st = k.over('Hex_Masked', k.canvas('Hex_MaskCanvas'), st, mask=fm)
    sc.add_layer(st, blend=Anim([(2, 0), (t_bank, 0.14), (t_enc, 0.22), (t_bio, 0.22), (t_bio + 14, 0.08), (t_pro, 0.08), (t_ex, 0)],
                                ['out', 'out', 'linear', 'out', 'linear', 'in']))

    # shield + lock group
    k.section('Shield_Outline')
    S = 430 / 24.0
    shp = ICONS['shield'][0]
    from fu import svg_subpaths
    sub = svg_subpaths(shp)[0]
    T = lambda q: None if q is None else (SXC + (q[0] - 12) * S, SYC + (q[1] - 12) * S)
    snodes = [{'p': T(nn['p']), 'in': T(nn['in']), 'out': T(nn['out'])} for nn in sub]
    fillm = k.poly_mask('Shield_Body', snodes, True)
    sfill = k.gradient('Shield_BodyFill', [(0, '#1E2A18', 0.95), (1, '#0E120D', 0.95)], 'Linear', (SXC, SYC - 200),
                       (SXC, SYC + 220), fillm)
    sfill = k.freeze('Shield_Body', sfill)
    om = k.poly_mask('Shield_Stroke', snodes, True, border=9, write_on=Anim([(0, 0), (t_enc, 1)], 'out'))
    sline = k.fill('Shield_StrokeFill', ACC, om)
    sline = k.glow('Shield_StrokeGlow', sline, 0.9, 22)
    shield = k.over('Shield_AddBody', k.canvas('Shield_Canvas'), sfill, blend=Anim([(4, 0), (t_enc, 1)], 'out'))
    shield = k.over('Shield_AddStroke', shield, sline)
    k.section('Lock')
    lk = k.rect_mask('Lock_Body', SXC - 78, SYC + 6, 156, 124, 26)
    lock = k.fill('Lock_BodyFill', ACC, lk)
    kh = k.ellipse_mask('Lock_Keyhole', SXC, SYC + 56, 15)
    kh2 = k.rect_mask('Lock_KeySlot', SXC - 6, SYC + 60, 12, 36, 4, inp=kh)
    lock = k.over('Lock_AddKeyhole', lock, k.fill('Lock_KeyholeFill', '#16200F', kh2))
    lock = k.freeze('Lock_Body', lock)
    shk = k.poly_mask('Lock_Shackle', [{'p': (SXC - 50, SYC + 8), 'in': None, 'out': None},
                                       {'p': (SXC - 50, SYC - 40), 'in': None, 'out': (SXC - 50, SYC - 72)},
                                       {'p': (SXC, SYC - 92), 'in': (SXC - 30, SYC - 92), 'out': (SXC + 30, SYC - 92)},
                                       {'p': (SXC + 50, SYC - 40), 'in': (SXC + 50, SYC - 72), 'out': None},
                                       {'p': (SXC + 50, SYC + 8), 'in': None, 'out': None}], False, border=18)
    shk_f = k.fill('Lock_ShackleFill', ACC, shk)
    shk_f = k.xf('Lock_ShackleClose', shk_f, dy=Anim([(t_enc - 2, -46), (t_enc + 8, 0)], 'back'))
    lockg = k.over('Lock_AddShackle', lock, shk_f)
    lockg = k.xf('Lock_PopIn', lockg, scale=Anim([(t_bank + 4, 0.3), (t_bank + 18, 1)], 'back'), pivot=(SXC, SYC + 40), mb=False)
    shield = k.over('Shield_AddLock', shield, lockg, blend=Anim([(t_bank + 4, 0), (t_bank + 10, 1)], 'out'))
    # click flash
    k.section('Lock_ClickFlash')
    fr = k.ellipse_mask('Click_Ring', SXC, SYC + 30, Anim([(t_enc + 8, 80), (t_enc + 26, 330)], 'out'),
                        border=Anim([(t_enc + 8, 10), (t_enc + 26, 1)], 'out'))
    flash = k.fill('Click_RingFill', ACC, fr)
    shield = k.over('Shield_AddClick', shield, flash, blend=Anim([(t_enc + 7, 0), (t_enc + 8, 0.9), (t_enc + 26, 0)], ['linear', 'out']))
    # fingerprint badge that lands on the shield at the end
    # move shield: centre -> left for biometric -> centre for "protected"
    k.section('Shield_Move')
    shield = k.xf('Shield_Move', shield, dx=Anim([(t_bio - 6, 0), (t_bio + 10, -360), (t_pro, -360), (t_pro + 16, 0)],
                                                 ['inout', 'linear', 'inout']),
                  scale=Anim([(t_bio - 6, 1), (t_bio + 10, 0.82), (t_pro, 0.82), (t_pro + 16, 0.92)], ['inout', 'linear', 'inout']),
                  pivot=(SXC, SYC), mb=False)
    sc.add_layer(shield)

    # chips
    def chip(name, label, sub, ic, cx, cy, t0, t1):
        k.section('Chip_' + name)
        w = max(text_w(label, 26, ('Inter', 'Bold')) + 130, 360)
        c = card(k, name, cx - w / 2, cy - 44, w, 88, 44, CARD2, EDGE)
        c = k.over(name + '_AddIc', c, icon(k, name + '_Ic', ic, cx - w / 2 + 50, cy, 34, ACC, stroke=3.6))
        c = k.over(name + '_AddLab', c, k.text(name + '_Lab', label, cx - w / 2 + 88, cy, 26, WHITE, 'Inter', 'Bold', 'left'))
        c = k.freeze(name, c)
        p, b = pop(k, name, c, t0, cx, cy, dur=14, from_scale=0.7, dy=30, t_out=t1)
        sc.add_layer(p, blend=b)
        if sub:
            s = k.text(name + '_Sub', sub, cx, cy + 78, 19, GREY, 'Inter', 'Medium', 'center', track=1.08)
            s = k.xf(name + '_SubRise', s, dy=Anim([(t0 + 8, 16), (t0 + 20, 0)], 'out'))
            sc.add_layer(s, blend=Anim([(t0 + 8, 0), (t0 + 16, 1), (t1, 1), (t1 + 8, 0)], ['out', 'linear', 'in']))
    chip('Chip_Encryption', 'Bank-level encryption', 'AES-256  ·  END-TO-END', 'lock', SXC, 790, t_bank, t_bio - 8)

    # fingerprint
    k.section('Fingerprint')
    FX, FY, FS = 1280, 440, 30
    fp = k.canvas('FP_Canvas')
    for i, nodes in enumerate(fingerprint_arcs(FX, FY, FS)):
        ts = t_bio + 2 + i * 2
        m = k.poly_mask('FP_Ridge%02d' % (i + 1), nodes, False, border=8, write_on=Anim([(ts, 0), (ts + 16, 1)], 'out'))
        fp = k.over('FP_AddRidge%02d' % (i + 1), fp, k.fill('FP_Ridge%02d_Fill' % (i + 1), ACC, m))
    fp = k.glow('FP_Glow', fp, 0.5, 12)
    k.section('Fingerprint_Scan')
    scan_y = Anim([(t_bio + 6, FY - 250), (t_bio + 40, FY + 260)], 'inout')
    sm = k.rect_mask('FP_ScanLine', 0, 0, 380, 6, 3, center=AnimXY([(f, (FX, y)) for f, y in scan_y.keys], 'inout'))
    scan = k.fill('FP_ScanFill', WHITE, sm)
    scan = k.glow('FP_ScanGlow', scan, 1.4, 24)
    fpg = k.over('FP_AddScan', fp, scan, blend=Anim([(t_bio + 4, 0), (t_bio + 8, 1), (t_bio + 38, 1), (t_bio + 44, 0)],
                                                    ['out', 'linear', 'out']))
    vb = k.ellipse_mask('FP_Verified', FX + 150, FY + 190, 38)
    vbf = k.fill('FP_VerifiedFill', ACC, vb)
    vbc = icon(k, 'FP_VerifiedCheck', 'check', FX + 150, FY + 190, 46, BG, stroke=6)
    badge = k.over('FP_VerifiedAddCheck', vbf, vbc)
    bp, bb = pop(k, 'FP_Verified', badge, t_bio + 40, FX + 150, FY + 190, dur=12, from_scale=0.2, dy=0)
    fpg = k.over('FP_AddVerified', fpg, bp, blend=bb)
    fpg = k.xf('FP_ToShield', fpg, dx=Anim([(t_pro, 0), (t_pro + 16, -320)], 'inout'),
               scale=Anim([(t_pro, 1), (t_pro + 16, 0.0)], 'in'), pivot=(FX, FY), mb=False)
    sc.add_layer(fpg, blend=Anim([(t_bio, 0), (t_bio + 4, 1), (t_pro + 10, 1), (t_pro + 16, 0)], ['out', 'linear', 'in']))
    chip('Chip_Biometric', 'Biometric security', 'FINGERPRINT  ·  FACE UNLOCK', 'user', FX, 790, t_bio + 4, t_pro - 6)

    # protected: pulse rings + orbiting coins
    k.section('Protected_Rings')
    rings = k.canvas('Rings_Canvas')
    for i in range(3):
        t0 = t_pro + 14 + i * 18
        rm = k.ellipse_mask('Pulse%d' % (i + 1), SXC, SYC, Anim([(t0, 230), (t0 + 30, 620)], 'out'), border=3)
        rings = k.over('Pulse%d_Add' % (i + 1), rings, k.fill('Pulse%d_Fill' % (i + 1), ACC, rm),
                       blend=Anim([(t0 - 1, 0), (t0, 0.7), (t0 + 30, 0)], ['linear', 'out']))
    sc.add_layer(rings)
    k.section('Protected_Orbit')
    orb = k.canvas('Orbit_Canvas')
    om_ = k.ellipse_mask('Orbit_Path', SXC, SYC + 10, 420, 120, border=1.5)
    orb = k.over('Orbit_AddPath', orb, k.fill('Orbit_PathFill', ACC, om_), blend=0.25)
    for i, sym in enumerate(['BTC', 'ETH', 'SOL']):
        coin = token(k, 'Orbit_%s' % sym, sym, SXC, SYC, 34)
        keys, skeys = [], []
        for f in range(t_pro, n + 1, 3):
            ang = (f - t_pro) * 2.4 + i * 120
            a = math.radians(ang)
            keys.append((f, (420 * math.sin(a), 10 + 120 * math.cos(a))))
            skeys.append((f, 0.8 + 0.25 * math.cos(a)))
        cm = k.xf('Orbit_%s_Move' % sym, coin, dx=Anim([(f, p[0]) for f, p in keys], 'linear'),
                  dy=Anim([(f, p[1]) for f, p in keys], 'linear'), scale=Anim(skeys, 'linear'), pivot=(SXC, SYC), mb=False)
        orb = k.over('Orbit_Add%s' % sym, orb, cm)
    sc.add_layer(orb, blend=Anim([(t_pro + 6, 0), (t_pro + 20, 1), (t_ex, 1), (n, 0)], ['out', 'linear', 'in']))

    hl, hc = headline(sc, 'HL_Protected', ['Your assets stay protected', 'every step of the way.'], 960, 820, 44, 0,
                      align='center', gap=0.55, hl=('protected',),
                      word_times=[v('your3', -2), v('assets2', -2), v('stay', -2), v('protected', -2), v('every', -2),
                                  v('step', -2), v('step', 6), v('way2', -6), v('way2', -2)])
    sc.add_layer(hl, mask=hc)
    k.section('Exit_Dip_To_Dark')
    sc.add_layer(k.fill('Exit_Dip', '#000000', None, 1.0), blend=Anim([(n - 5, 0), (n, 0.8)], 'in'))
    return sc.finish(camera={'Size': Anim([(0, 1.08), (16, 1.0), (t_ex, 1.03), (n, 1.15)], ['out', 'soft', 'in']),
                             'Pivot': (0.5, 0.52)})


# ================================================================ C08
def c08():
    sc = Scene(7)
    k = sc.k
    v = sc.v
    n = sc.n
    background(sc)
    t_drop = v('vaultx2', -10)
    k.section('Intro_From_Dark')
    sc.add_layer(k.fill('Intro_Dip', '#000000', None, 1.0), blend=Anim([(0, 0.8), (5, 0)], 'out'))
    t_ex = n - 10
    wh, whc = headline(sc, 'HL_Whether', ["Whether you're"], 960, 190, 38, 0, align='center', color=GREY,
                       font=('Inter Display', 'SemiBold'), t_out=t_drop, word_times=[v('whether', -2), v('whether', 4)])
    sc.add_layer(wh, mask=whc)
    CW_, CH_, GAP = 480, 460, 40
    X0 = 960 - (3 * CW_ + 2 * GAP) / 2
    CY0 = 290
    words = ['investing', 'trading', 'holding']
    act = [v('investing', -3), v('trading', -3), v('holding', -3), t_drop]
    specs = [('Investing', 'trend', 'Auto-invest & DCA plans'), ('Trading', 'candles', 'Real-time markets, 24/7'),
             ('Holding long-term', 'vault', 'Secure vault storage')]
    for i, (title, ic, sub) in enumerate(specs):
        k.section('Card_' + title.split()[0])
        x = X0 + i * (CW_ + GAP)
        c = card(k, 'Mode%d' % (i + 1), x, CY0, CW_, CH_, 36, CARD, EDGE)
        im = k.rect_mask('Mode%d_IcBox' % (i + 1), x + 40, CY0 + 40, 76, 76, 22)
        c = k.over('Mode%d_AddIcBox' % (i + 1), c, k.fill('Mode%d_IcBoxFill' % (i + 1), '#22301A', im))
        c = k.over('Mode%d_AddIc' % (i + 1), c, icon(k, 'Mode%d_Ic' % (i + 1), ic, x + 78, CY0 + 78, 42, ACC, stroke=4))
        c = k.over('Mode%d_AddTitle' % (i + 1), c, k.text('Mode%d_Title' % (i + 1), title, x + 40, CY0 + 168, 34, WHITE,
                                                          'Inter Display', 'Bold', 'left'))
        c = k.over('Mode%d_AddSub' % (i + 1), c, k.text('Mode%d_Sub' % (i + 1), sub, x + 40, CY0 + 214, 21, GREY,
                                                        'Inter', 'Medium', 'left'))
        c = k.freeze('Mode%d' % (i + 1), c)
        # mini viz
        vy0, vy1 = CY0 + 270, CY0 + CH_ - 40
        ta = act[i] + 4
        if i == 0:
            random.seed(5)
            vals = [0.2]
            for j in range(1, 24):
                vals.append(min(0.95, max(0.05, vals[-1] + 0.035 + random.uniform(-0.07, 0.07))))
            pts = [(x + 40 + j * (CW_ - 80) / 23, vy1 - vals[j] * (vy1 - vy0)) for j in range(24)]
            lm = k.poly_mask('Mode1_Spark', smooth_nodes(pts), False, border=5, write_on=Anim([(ta, 0), (ta + 18, 1)], 'inout'))
            c = k.over('Mode1_AddSpark', c, k.fill('Mode1_SparkFill', ACC, lm))
            c = k.over('Mode1_AddPct', c, k.text('Mode1_Pct', '+24.6%', x + CW_ - 40, CY0 + 70, 24, ACC, 'Inter', 'Bold', 'right'))
        elif i == 1:
            random.seed(9)
            base = vy1 - 40
            for j in range(9):
                cx = x + 64 + j * (CW_ - 128) / 8
                o = base - j * 9 + random.uniform(-14, 14)
                cl = o + random.choice([-1, 1]) * random.uniform(14, 34)
                up = cl < o
                top, bot = min(o, cl), max(o, cl)
                col = ACC if up else RED
                wm = k.rect_mask('Mode2_Wick%d' % j, cx - 1.5, top - 14, 3, bot - top + 28)
                bm = k.rect_mask('Mode2_Body%d' % j, cx - 11, top, 22, bot - top, 4, inp=wm)
                cd = k.fill('Mode2_Candle%d' % j, col, bm)
                cd = k.xf('Mode2_Candle%d_Grow' % j, cd, scale=Anim([(ta + j * 2, 0), (ta + j * 2 + 10, 1)], 'back'),
                          pivot=(cx, (top + bot) / 2), mb=False)
                c = k.over('Mode2_AddCandle%d' % j, c, cd)
            c = k.over('Mode2_AddLive', c, pill(k, 'Mode2_Live', x + CW_ - 136, CY0 + 50, 96, 42, '#3A1F1F', 'LIVE', 17, RED,
                                                ('Inter', 'Bold')))
        else:
            rcx, rcy = x + 110, (vy0 + vy1) / 2
            tm = k.ellipse_mask('Mode3_RingTrack', rcx, rcy, 58, border=12)
            c = k.over('Mode3_AddTrack', c, k.fill('Mode3_RingTrackFill', '#263022', tm))
            am = k.poly_mask('Mode3_Ring', arc_nodes(rcx, rcy, 58, 0, 300), False, border=12,
                             write_on=Anim([(ta, 0), (ta + 22, 1)], 'out'))
            c = k.over('Mode3_AddRing', c, k.fill('Mode3_RingFill', ACC, am))
            c = k.over('Mode3_AddYears', c, k.text('Mode3_Years', '4y 2m', x + 200, rcy - 18, 34, WHITE, 'Inter Display', 'Bold', 'left'))
            c = k.over('Mode3_AddHeld', c, k.text('Mode3_Held', 'held in vault', x + 200, rcy + 24, 20, GREY, 'Inter', 'Medium', 'left'))
        # active state: accent border + lift while its word plays
        em = k.rect_mask('Mode%d_Active' % (i + 1), x, CY0, CW_, CH_, 36, border=3)
        ef = k.fill('Mode%d_ActiveFill' % (i + 1), ACC, em)
        on, off = act[i], act[i + 1]
        c = k.over('Mode%d_AddActive' % (i + 1), c, ef, blend=Anim([(on, 0), (on + 6, 1), (off, 1), (off + 8, 0.0)],
                                                                    ['out', 'linear', 'out']))
        t_in = act[i] - 12
        keys, eas = [(t_in, 840), (t_in + 11, 0)], ['out']

        def push(t, val, e):
            t = max(t, keys[-1][0] + 1)
            keys.append((t, val))
            eas.append(e)
        push(on, 0, 'linear')
        push(on + 8, -18, 'out')
        if i < 2:
            push(off, -18, 'linear')
            push(off + 8, 0, 'out')
        push(t_drop + i * 3, keys[-1][1], 'linear')
        push(t_drop + i * 3 + 14, 900, 'in')
        c = k.xf('Mode%d_Motion' % (i + 1), c, dy=Anim(keys, eas))
        sc.add_layer(c)

    # ahead arrow + headline
    k.section('Ahead_Arrow')
    ta = v('keeps', 0)
    pts = [(120, 1000), (520, 800), (760, 870), (1180, 745), (1420, 800), (1770, 230)]
    am = k.poly_mask('Ahead_Line', pts, False, border=10, write_on=Anim([(ta, 0), (ta + 24, 1)], 'inout'))
    arrow = k.fill('Ahead_LineFill', ACC, am)
    hm = k.poly_mask('Ahead_Head', [(1773, 225), (1766, 282), (1725, 257)], True)
    head = k.fill('Ahead_HeadFill', ACC, hm)
    hp, hb = pop(k, 'Ahead_Head', head, ta + 22, 1770, 230, dur=10, from_scale=0, dy=0)
    arrow = k.over('Ahead_AddHead', arrow, hp, blend=hb)
    arrow = k.glow('Ahead_Glow', arrow, 0.8, 26)
    sc.add_layer(arrow, blend=Anim([(ta, 0.0), (ta + 2, 0.55), (t_ex, 0.55), (n, 0)], ['out', 'linear', 'in']))
    hl, hc = headline(sc, 'HL_Keeps_You_Ahead', ['VaultX keeps', 'you ahead.'], 960, 470, 116, 0, align='center', gap=0.55,
                      hl=('ahead.',), word_times=[v('vaultx2', -2), v('keeps', -2), v('you', -2), v('ahead', -2)])
    k.section('Ahead_Whip_Up')
    hl = k.xf('HL_Keeps_You_Ahead_WhipUp', hl, dy=Anim([(n - 7, 0), (n, -420)], 'in'))
    sc.add_layer(hl, blend=Anim([(n - 4, 1), (n, 0)], 'in'))
    return sc.finish(camera={'Size': Anim([(0, 1.0), (t_drop, 1.02), (t_drop + 20, 1.0), (n, 1.04)], ['soft', 'out', 'soft']),
                             'Pivot': (0.5, 0.5)})


# ================================================================ C09 end card
def ui_splash(pk, n):
    k = pk
    k.section(n + '_Splash')
    g = k.canvas(n + '_Splash_Canvas')
    gm = k.rect_mask(n + '_SplashBG', SX0, SY0, SW, SH)
    g = k.over(n + '_AddBG', g, k.gradient(n + '_SplashGrad', [(0, '#24301C', 1), (1, '#0C0F0C', 1)], 'Linear', (450, 300), (450, 1500), gm))
    from vx_common import logo_paths, LOGO_W, LOGO_H
    s = 560 / LOGO_W
    x0, y0 = 450 - 280, 760 - LOGO_H * s / 2
    for i, (cls, d) in enumerate(logo_paths()):
        m = k.svg_mask('%s_SplashLogo%d' % (n, i), d, x0, y0, s)
        g = k.over('%s_AddSplashLogo%d' % (n, i), g, k.fill('%s_SplashLogo%d_Fill' % (n, i), ACC if cls == 'cls-1' else WHITE, m))
    g = k.over(n + '_AddTag', g, k.text(n + '_SplashTag', 'Own your crypto journey.', 450, 900, 26, GREY, 'Inter', 'Medium', 'center'))
    g = k.over(n + '_AddBtn', g, pill(k, n + '_SplashBtn', 90, 1560, 720, 120, ACC, 'Get started', 32, BG, ('Inter', 'Bold')))
    g = k.over(n + '_AddLogin', g, k.text(n + '_SplashLogin', 'I already have a wallet', 450, 1745, 22, GREY, 'Inter', 'SemiBold', 'center'))
    return k.freeze(n + '_Splash', g)


def store_badge(k, name, x, y, w, h, ic, top, bottom):
    c = card(k, name, x, y, w, h, 22, '#050605', '#4A524A', edge_w=2)
    if ic == 'play':
        c = k.over(name + '_AddIc', c, icon_solid(k, name + '_Ic', 'play', x + 52, y + h / 2, 40, WHITE))
    else:
        c = k.over(name + '_AddIc', c, icon(k, name + '_Ic', ic, x + 52, y + h / 2, 42, WHITE, stroke=3.6))
    c = k.over(name + '_AddTop', c, k.text(name + '_Top', top, x + 96, y + h / 2 - 15, 15, GREY, 'Inter', 'Medium', 'left'))
    c = k.over(name + '_AddBot', c, k.text(name + '_Bot', bottom, x + 96, y + h / 2 + 15, 26, WHITE, 'Inter', 'Bold', 'left'))
    return k.freeze(name, c)


def c09():
    sc = Scene(8)
    k = sc.k
    v = sc.v
    n = sc.n
    background(sc)
    t_b = v('own', -8)

    # part A: phone + download headline + store badges
    pk = Kit(sc.c, int(PW * PHONE_RES), int(PH * PHONE_RES), prefix='P_', x0=k.x + COL_W, y0=0, aw=PW, ah=PH)
    body, scr = phone_frame(pk, 'Phone')
    spl = ui_splash(pk, 'E')
    pk.section('Phone_Assemble')
    phone = pk.over('Phone_AddSplash', body, spl, mask=scr)
    sync(sc, pk)
    k.section('Phone_Place')
    sh = shadow(k, 'Phone', 600, 1010, 480, 80, 0.6, 70)
    sc.add_layer(sh, blend=Anim([(0, 0), (16, 1), (t_b, 1), (t_b + 10, 0)], ['out', 'linear', 'in']))
    pc = AnimXY([(0, (600, 560 + 1020)), (18, (600, 560)), (t_b, (600, 560)), (t_b + 14, (600, 560 + 1000))],
                ['out', 'linear', 'in'])
    sc.add_layer(phone, center=pc, size=Anim([(0, 0.44 / PHONE_RES), (18, 0.44 / PHONE_RES)], 'linear'), angle=Anim([(0, 8), (18, 0)], 'out'), mb=True)

    e, eb = eyebrow(sc, 'Eb_Get', '06', 'Get the app', 1004, 300, v('download', -6), t_out=t_b)
    sc.add_layer(e, blend=eb)
    hl, hc = headline(sc, 'HL_Download', ['Download', 'VaultX Wallet', 'today.'], 1000, 400, 82, 0, gap=0.5,
                      hl=('today.',), t_out=t_b,
                      word_times=[v('download', -2), v('vaultx3', -2), v('wallet3', -3), v('today', -2)])
    sc.add_layer(hl, mask=hc)
    k.section('Store_Badges')
    # badge width from the widest label (Text+ renders ~12% wider than the PIL measure) + 34 px right padding
    bw = round(96 + 1.12 * max(text_w('App Store', 26, ('Inter', 'Bold')), text_w('Google Play', 26, ('Inter', 'Bold')),
                               text_w('Download on the', 15, ('Inter', 'Medium'))) + 34)
    bx1, bx2 = 1004, 1004 + bw + 24
    b1 = store_badge(k, 'Badge_AppStore', bx1, 760, bw, 96, 'phone', 'Download on the', 'App Store')
    b2 = store_badge(k, 'Badge_GooglePlay', bx2, 760, bw, 96, 'play', 'Get it on', 'Google Play')
    p1, bb1 = pop(k, 'Badge_AppStore', b1, v('today', 4), bx1 + bw / 2, 808, dur=14, from_scale=0.7, dy=30, t_out=t_b)
    p2, bb2 = pop(k, 'Badge_GooglePlay', b2, v('today', 8), bx2 + bw / 2, 808, dur=14, from_scale=0.7, dy=30, t_out=t_b)
    sc.add_layer(p1, blend=bb1)
    sc.add_layer(p2, blend=bb2)

    # part B: final lockup
    k.section('Final_Glow')
    gm = k.ellipse_mask('Final_Glow', 960, 430, Anim([(t_b, 200), (t_b + 30, 560), (n, 620)], ['out', 'soft']), soft=300)
    glow = k.fill('Final_GlowFill', ACC, gm, 0.16)
    sc.add_layer(glow, blend=Anim([(t_b, 0), (t_b + 20, 1)], 'out'))
    lg, lclip = logo(sc, 'Final', 960, 430, 900, t_b + 6, stagger=2, mark_delay=10)
    sc.add_layer(lg, mask=lclip)
    tg, tclip = headline(sc, 'HL_Own_Journey', ['Own your crypto journey.'], 960, 600, 50, 0, align='center',
                         font=('Inter Display', 'SemiBold'), hl=('journey.',),
                         word_times=[v('own', 2), v('your4', 2), v('crypto2', 1), v('journey', 0)])
    sc.add_layer(tg, mask=tclip)
    k.section('Final_CTA')
    ctx = text_w('Download VaultX Wallet', 30, ('Inter', 'Bold')) * 1.1   # rendered Text+ runs ~10% wider
    gap_, arrow_ = 18, 34
    cta_w = ctx + gap_ + arrow_ + 2 * 58
    tcx = 960 - (gap_ + arrow_) / 2
    cta = pill(k, 'Final_CTA', 960 - cta_w / 2, 704, cta_w, 100, ACC, None)
    cta = k.over('Final_CTA_AddText', cta, k.text('Final_CTA_Text', 'Download VaultX Wallet', tcx, 754, 30, BG,
                                                   'Inter', 'Bold', 'center'))
    cta = k.over('Final_CTA_AddArrow', cta, icon(k, 'Final_CTA_Arrow', 'arrowright', tcx + ctx / 2 + gap_ + arrow_ / 2, 754,
                                                  arrow_, BG, stroke=4.5))
    cta = k.freeze('Final_CTA', cta)
    tc = v('end', 0)
    cp, cb = pop(k, 'Final_CTA', cta, tc, 960, 754, dur=16, from_scale=0.7, dy=40)
    cp = k.xf('Final_CTA_Breathe', cp, scale=Anim([(tc + 20, 1), (tc + 38, 1.03), (tc + 56, 1)], 'soft'), pivot=(960, 754),
              mb=False)
    sc.add_layer(cp, blend=cb)
    av = k.text('Final_Available', 'AVAILABLE ON iOS & ANDROID', 960, 858, 18, GREY, 'Inter', 'SemiBold', 'center', track=1.15)
    av = k.xf('Final_Available_Rise', av, dy=Anim([(tc + 8, 18), (tc + 22, 0)], 'out'))
    sc.add_layer(av, blend=Anim([(tc + 8, 0), (tc + 18, 1)], 'out'))
    return sc.finish(camera={'Size': Anim([(0, 1.0), (t_b, 1.02), (t_b + 20, 1.0), (n, 1.03)], ['soft', 'out', 'soft']),
                             'Pivot': (0.5, 0.5)})


if __name__ == '__main__':
    for f in (c06, c07, c08, c09):
        print(f())
