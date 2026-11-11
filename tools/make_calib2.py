# Calibration 2: gradient, stroke width + write-on, text alignment, counter expression, masked reveal, glow.
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from fu import Comp, Anim, AnimXY
from kit import Kit
os.makedirs('build/comps', exist_ok=True)
c = Comp('T01_Calibration2', 40)
k = Kit(c)
bg = k.gradient('BG', [(0, '#1B2A14', 1), (1, '#0B0E0B', 1)], 'Radial', start=(960, 540), end=(1920, 1080))
L = []
# strokes
st = k.poly_mask('Stroke4', [(100, 400), (400, 300), (700, 420)], closed=False, border=4, write_on=Anim([(0, 0), (20, 1)], 'linear'))
L.append(k.fill('StrokeFill', '#91C950', st))
st2 = k.poly_mask('Stroke12', [(100, 500), (700, 500)], closed=False, border=12)
L.append(k.fill('Stroke12Fill', '#FFFFFF', st2))
# texts
L.append(k.text('TL', 'Left 60', 100, 150, 60, align='left'))
L.append(k.text('TR', 'Right 60', 1820, 150, 60, align='right'))
L.append(k.text('TC', 'Center 40', 960, 150, 40, align='center', font='Inter Display', style='SemiBold'))
expr = (':local t=math.min(1,math.max(0,(time-0)/20)); t=1-(1-t)^3; local v=48256.80*t; '
        'local s=string.format("%.2f",v); local int,frac=s:match("(%d+)(%.%d+)"); '
        'int=int:reverse():gsub("(%d%d%d)","%1,"):reverse():gsub("^,",""); return Text("$"..int..frac)')
L.append(k.text('Counter', '$0.00', 960, 300, 50, align='center', expr=expr))
# masked reveal: word slides up inside a mask window
w = k.text('RevealWord', 'Reveal', 1200, 650, 80, align='left')
wx = k.xf('RevealMove', w, dy=Anim([(0, 120), (20, 0)], 'out'))
rm = k.rect_mask('RevealWin', 1150, 590, 600, 120)
# outline rect
o = k.rect_mask('Outline', 1150, 800, 400, 160, 32, border=2)
L.append(k.fill('OutlineFill', '#91C950', o))
# glow circle
e = k.ellipse_mask('Dot', 400, 800, 60)
dot = k.fill('DotFill', '#91C950', e)
L.append(k.glow('DotGlow', dot, gain=1.5, size=30))
cur = k.stack('Stack', bg, L)
cur = k.over('RevealMerge', cur, wx, mask=rm)
c.add('MediaOut', 'MediaOut1', {'Index': '0', 'Input': __import__('fu').Conn(cur)})
print(c.save('build/comps/T01_Calibration2.comp'), len(c.tools))
