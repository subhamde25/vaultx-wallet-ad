"""C01 Hook and C02 Logo reveal."""
from fu import Anim, AnimXY
from vx_common import (Scene, background, headline, logo, card, pill, pop, icon, text_w, vf, gf,
                       ACC, WHITE, GREY, GREY2, CARD, EDGE, DISPLAY)


def c01():
    sc = Scene(0)
    k = sc.k
    background(sc)
    v = sc.v

    # ticker ribbons (market energy behind the hook)
    k.section('Ticker_Ribbons')
    tick = '   '.join(['BTC  +4.21%', 'ETH  +2.87%', 'SOL  +6.12%', 'AVAX  -1.04%', 'LINK  +3.45%', 'DOT  +1.98%',
                       'ADA  -0.62%', 'MATIC  +5.30%'] * 2)
    t1 = k.text('Ticker_Top', tick, -40, 150, 22, GREY, 'Inter', 'SemiBold', 'left')
    t1 = k.xf('Ticker_Top_Scroll', t1, dx=Anim([(0, 0), (105, -1100)], 'linear'), mb=True)
    t2 = k.text('Ticker_Bottom', tick, -1500, 935, 22, GREY, 'Inter', 'SemiBold', 'left')
    t2 = k.xf('Ticker_Bottom_Scroll', t2, dx=Anim([(0, 0), (105, 1100)], 'linear'), mb=True)
    rib = k.over('Ticker_Both', t1, t2)
    sc.add_layer(rib, blend=Anim([(0, 0), (10, 0.55), (92, 0.55), (104, 0)], ['out', 'linear', 'in']))

    # speed streaks on "fast"
    k.section('Speed_Streaks')
    streaks = k.canvas('Streaks_Canvas')
    spec = [(318, 520, 3, 0), (392, 380, 2, 2), (676, 640, 3, 1), (742, 300, 2, 4), (230, 460, 2, 5),
            (808, 560, 3, 3), (455, 240, 2, 6), (610, 700, 2, 7)]
    for i, (y, ln, th, d) in enumerate(spec):
        m = k.rect_mask('Streak%d' % i, 0, y, ln, th, th / 2)
        f = k.fill('Streak%d_Fill' % i, ACC if i % 3 else WHITE, m, 0.7)
        t0 = v('fast', -3 + d * 2)
        f = k.xf('Streak%d_Fly' % i, f, dx=Anim([(t0, -ln - 50), (t0 + 13, 1920 + 80)], 'inout'), quality=6)
        streaks = k.over('Streak%d_Add' % i, streaks, f)
    sc.add_layer(streaks)

    # line 1: Crypto moves fast.
    cap1 = 118
    g1, c1 = headline(sc, 'L1_Crypto_Moves_Fast', ['Crypto moves fast.'], 960, 540, cap1, 0, t_out=v('your', -15),
                      align='center', word_times=[v('crypto', 3), v('moves', -1), v('fast', -2)], hl=('fast.',),
                      out_dur=9)
    sc.add_layer(g1, mask=c1)

    # line 2: Your wallet / should too.
    cap2 = 118
    pitch = cap2 * 1.62
    g2, c2 = headline(sc, 'L2_Your_Wallet_Should_Too', ['Your wallet', 'should too.'], 960, 540 - pitch / 2, cap2, 0,
                      t_out=94, align='center', gap=0.62, hl=('too.',), out_dur=8,
                      word_times=[v('your', -2), v('wallet', -2), v('should', -2), v('too', -2)])
    sc.add_layer(g2, mask=c2)

    # underline under "too."
    k.section('Too_Underline')
    sp = text_w(' ', cap2)
    w_sh, w_too = text_w('should', cap2), text_w('too.', cap2)
    total = w_sh + sp + w_too
    ux0 = 960 - total / 2 + w_sh + sp
    uy = 540 + pitch / 2 + cap2 * 0.78
    um = k.poly_mask('Too_Underline', [(ux0, uy), (ux0 + w_too * 0.92, uy - 6)], closed=False, border=9,
                     write_on=Anim([(v('too', 6), 0), (v('too', 16), 1)], 'out'))
    ul = k.fill('Too_Underline_Green', ACC, um)
    sc.add_layer(ul, blend=Anim([(93, 1), (100, 0)], 'in'))
    return sc.finish(camera={'Size': Anim([(0, 1.06), (105, 1.0)], 'soft'), 'Pivot': (0.5, 0.5)})


def c02():
    sc = Scene(1)
    k = sc.k
    v = sc.v
    background(sc)

    # ring burst that opens the reveal
    k.section('Burst_Ring')
    rm = k.ellipse_mask('Burst_Ring', 960, 470, Anim([(0, 10), (22, 1150)], 'out'),
                        border=Anim([(0, 30), (22, 2)], 'out'))
    ring = k.fill('Burst_Ring_Green', ACC, rm)
    dm = k.ellipse_mask('Burst_Dot', 960, 470, Anim([(0, 0), (5, 46), (12, 0)], ['out', 'in']))
    dot = k.fill('Burst_Dot_Green', ACC, dm)
    burst = k.over('Burst_RingDot', ring, dot)
    sc.add_layer(burst, blend=Anim([(0, 1), (20, 0)], 'out'))

    content_k = k
    # logo build
    lw = 820
    lg, lclip = logo(sc, 'Hero', 960, 450, lw, v('meet', -5), stagger=2, mark_delay=9)
    k.section('Logo_Group')
    grp = k.canvas('LogoGroup_Canvas')
    grp = k.over('LogoGroup_AddLogo', grp, lg, mask=lclip)
    wg, wclip = headline(sc, 'Sub_Wallet', ['W A L L E T'], 960, 600, 30, v('wallet2', -4), align='center',
                         font=('Inter', 'SemiBold'), color=GREY, stagger=1, dur=14)
    k.section('Logo_Group_Move')
    grp = k.over('LogoGroup_AddWallet', grp, wg, mask=wclip)
    t_up = v('the', -2)
    grp = k.xf('LogoGroup_MoveUp', grp, dy=Anim([(t_up, 0), (t_up + 18, -170)], 'inout'),
               scale=Anim([(t_up, 1), (t_up + 18, 0.6)], 'inout'), pivot=(960, 470), mb=False)

    # tagline
    tg, tclip = headline(sc, 'Tagline_Smarter_Way', ['The smarter way to'], 960, 452, 40, 0, align='center',
                         font=('Inter Display', 'SemiBold'), color=GREY,
                         word_times=[v('the', 6), v('smarter', 4), v('way', 3), v('way', 6)])

    # chips: Manage / Grow / Protect
    chips = []
    cw, ch, gap = 270, 92, 32
    x0 = 960 - (3 * cw + 2 * gap) / 2
    for i, (lab, ic, w_) in enumerate([('Manage', 'wallet', 'manage'), ('Grow', 'chart', 'grow'),
                                        ('Protect', 'shield', 'protect')]):
        k.section('Chip_' + lab)
        x = x0 + i * (cw + gap)
        c = card(k, 'Chip_' + lab, x, 548, cw, ch, ch / 2, '#161C15', EDGE)
        isz = 34
        icn = icon(k, 'Chip_' + lab, ic, x + 52, 548 + ch / 2, isz, ACC)
        c = k.over('Chip_%s_AddIcon' % lab, c, icn)
        t = k.text('Chip_%s_Label' % lab, lab, x + 86, 548 + ch / 2, 28, WHITE, 'Inter Display', 'SemiBold', 'left')
        c = k.over('Chip_%s_AddLabel' % lab, c, t)
        c = k.freeze('Chip_' + lab, c)
        t0 = v(w_, -3)
        p, b = pop(k, 'Chip_' + lab, c, t0, x + cw / 2, 548 + ch / 2, dur=16, from_scale=0.6, dy=30)
        chips.append((p, b))

    # "your digital assets."
    ag, aclip = headline(sc, 'Line_Digital_Assets', ['your digital assets.'], 960, 735, 46, 0, align='center',
                         font=DISPLAY, hl=('assets.',),
                         word_times=[v('your2', -2), v('digital', -2), v('assets', -3)])

    # assemble content + exit move
    k.section('Content_Assemble')
    content = k.canvas('Content_Canvas')
    content = k.over('Content_AddLogo', content, grp)
    content = k.over('Content_AddTagline', content, tg, mask=tclip)
    for i, (p, b) in enumerate(chips):
        content = k.over('Content_AddChip%d' % (i + 1), content, p, blend=b)
    content = k.over('Content_AddAssets', content, ag, mask=aclip)
    t_ex = 148
    content = k.xf('Content_Exit_ToPhone', content, dy=Anim([(t_ex, 0), (sc.n, 140)], 'in'),
                   scale=Anim([(t_ex, 1), (sc.n, 0.86)], 'in'), pivot=(960, 600), mb=False)
    sc.add_layer(content, blend=Anim([(t_ex + 4, 1), (sc.n, 0)], 'in'))
    return sc.finish(camera={'Size': Anim([(0, 1.0), (sc.n, 1.035)], 'soft'), 'Pivot': (0.5, 0.5)})


if __name__ == '__main__':
    print(c01())
    print(c02())
