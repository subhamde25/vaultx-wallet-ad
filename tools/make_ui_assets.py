# Full-resolution UI screen comps (900x1860 phone canvas) used to export the "UI screens" assets as PNG.
# usage (from vaultx/): python -I tools/make_ui_assets.py -> build/comps/UI_*.comp
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from fu import Comp, Conn
from kit import Kit
from vx_common import phone_frame, PW, PH
from scenes_b import ui_send, ui_send_button, ui_success, ui_swap
from scenes_c import ui_dashboard, ui_splash


def build(name, fn):
    c = Comp(name, 90, PW, PH)
    k = Kit(c, PW, PH, prefix='', x0=0, y0=0)
    body, scr = phone_frame(k, 'Phone')
    ui = fn(k)
    k.section('Assemble')
    out = k.over('Phone_AddUI', body, ui, mask=scr)
    k.end_section()
    c.add('MediaOut', 'MediaOut1', {'Index': '0', 'Input': Conn(out)}, (k.x + 260, 300))
    path = os.path.join('build', 'comps', name + '.comp')
    c.save(path)
    return path


def send(k):
    s = ui_send(k, 'S')
    b = ui_send_button(k, 'S', 400)
    return k.over('S_AddBtn', s, b)


screens = {
    'UI_01_Send': send,
    'UI_02_Sent': lambda k: ui_success(k, 'S', 0),
    'UI_03_Swap': lambda k: ui_swap(k, 'W', 0, 400),
    'UI_04_Dashboard': lambda k: ui_dashboard(k, 'D', 0),
    'UI_05_Splash': lambda k: ui_splash(k, 'E'),
}
for n, f in screens.items():
    print(build(n, f))
