# VaultX audio: VO clean-up, music edit (ZoneX "Innovation Needed", CC BY 3.0) with ducking + button ending,
# SFX cue sheet (each sound used at most twice), stems for Resolve and a reference mix.
# usage (from vaultx/): python -I tools/mix_audio.py
import collections
import json
import os
import shutil
import subprocess
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from vx_common import vf, VO_OFF, TOTAL, FPS

SR = 48000
N = int(TOTAL / FPS * SR)            # 45.0 s
ROOT = os.path.abspath('.')
UP = os.path.dirname(ROOT)
LIB = {'s': os.path.join(UP, 'story99-rahul/assets/audio/sfx'), 'b': os.path.join(UP, 'brainr-film/assets/audio/sfx'),
       'c': os.path.join(ROOT, 'assets/audio/sfx_custom')}
MUSIC_SRC = os.path.join(UP, 'brainr-film/assets/audio/bgm-cand/zonex-innovation-needed.mp3')
MUSIC = 'assets/audio/music/ZoneX - Innovation Needed (CC BY 3.0, Jamendo).mp3'
os.makedirs('assets/audio/sfx_used', exist_ok=True)
os.makedirs('assets/audio/music', exist_ok=True)
os.makedirs('build/audio/sfx_clips', exist_ok=True)
# The sound libraries above sit beside this project on the author's machine. The repo ships copies of
# every sound actually used (assets/audio/sfx_used) and the music, so the mix rebuilds without them.
if os.path.exists(MUSIC_SRC):
    shutil.copy2(MUSIC_SRC, MUSIC)


def load(path, af=None):
    cmd = ['ffmpeg', '-v', 'error', '-i', path]
    if af:
        cmd += ['-af', af]
    cmd += ['-ac', '2', '-ar', str(SR), '-f', 'f32le', '-']
    x = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).copy()
    return x


def save(path, x):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-',
                    '-c:a', 'pcm_s24le', path], input=np.asarray(x, np.float32).tobytes(), check=True)


def db(g):
    return 10 ** (g / 20.0)


def fsec(frame):
    return frame / FPS


# ---------------------------------------------------------------- VO
vo_raw = load('brandkit/voiceover.mp3', 'highpass=f=75,equalizer=f=220:t=q:w=1.0:g=-1.5,'
              'equalizer=f=3200:t=q:w=1.2:g=2.0,equalizer=f=8000:t=q:w=1.5:g=1.0,'
              'acompressor=threshold=-22dB:ratio=2.6:attack=6:release=90:makeup=1.5')
vo = np.zeros((N, 2), np.float32)
o = int(VO_OFF * SR)
vo[o:o + len(vo_raw)] = vo_raw[:N - o]

# ---------------------------------------------------------------- music edit
T_START = 26.82          # track second that plays at film 0 (puts the breakdown under security, drop on "keeps you ahead")
END_FILM = 43.72         # bar downbeat for the button ending
mus_full = load(MUSIC)
a = int(T_START * SR)
cut = int(END_FILM * SR)
hold = int(0.42 * SR)    # let the final downbeat ring briefly
m = np.zeros((N, 2), np.float32)
seg = mus_full[a:a + cut + hold].copy()
seg[:int(0.03 * SR)] *= np.linspace(0, 1, int(0.03 * SR))[:, None]
fo = int(0.12 * SR)
seg[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 2
m[:len(seg)] = seg
# reverb tail from the final downbeat (synthetic decaying noise IR, decorrelated L/R)
rng = np.random.default_rng(7)
irn = int(1.6 * SR)
tt = np.arange(irn) / SR
ir = rng.standard_normal((irn, 2)) * np.exp(-tt / 0.42)[:, None]
src = mus_full[a + cut:a + cut + int(0.30 * SR)]
tail = np.stack([np.convolve(src[:, c], ir[:, c])[:int(1.9 * SR)] for c in range(2)], 1)
tail = tail / (np.abs(tail).max() + 1e-9) * np.abs(src).max() * 0.55
ts = cut + int(0.05 * SR)
m[ts:ts + len(tail)] += tail[:N - ts]
# ducking under the VO (smoothed sidechain)
lvl = np.abs(vo).mean(1)
win = int(0.03 * SR)
env_ = np.sqrt(np.convolve(lvl ** 2, np.ones(win) / win, 'same'))
active = (20 * np.log10(env_ + 1e-9) > -38).astype(np.float32)
g = np.zeros(N, np.float32)
att, rel = np.exp(-1 / (0.04 * SR)), np.exp(-1 / (0.6 * SR))
cur = 0.0
for i in range(N):
    tgt = active[i]
    cur = (att if tgt > cur else rel) * cur + (1 - (att if tgt > cur else rel)) * tgt
    g[i] = cur
duck_db = -11.0 * g
music_gain = -11.0
m *= db(music_gain + duck_db)[:, None]
# lift the breakdown + drop a touch (music carries the security section)
bd0, bd1 = int(23.87 * SR), int(36.5 * SR)
m[bd0:bd1] *= db(1.5)

# ---------------------------------------------------------------- SFX cue sheet
CUES = [  # (global frame, lib, file, gain dB, note)
    (2, 's', 'subhit', -8, 'open: low hit'),
    (vf('fast') - 3, 's', 'low_flyby', -7, 'speed streaks'),
    (43, 's', 'silk_swipe', -7, 'line 1 out'),
    (vf('too') + 6, 's', 'pen_sweep', -4, 'underline "too."'),
    (94, 's', 'snap_whip', -10, 'hook whip out'),
    (105, 's', 'bass_bloom', -14, 'logo burst ring'),
    (121, 'b', 'brand-twinkle', -9, 'logo mark dots'),
    (vf('the') - 2, 's', 'air_suck', -12, 'logo moves up'),
    (vf('manage') - 3, 's', 'soft_pop', -4, 'chip Manage'),
    (vf('grow') - 3, 'b', 'pop', -6, 'chip Grow'),
    (vf('protect') - 3, 's', 'felt_tap', -4, 'chip Protect'),
    (253, 'b', 'dive-whoosh', -10, 'drop into phone'),
    (267, 's', 'slider_glide', -4, 'phone rises'),
    (269, 's', 'data_morph', -16, 'amount count'),
    (vf('transactions') + 6, 'b', 'click-soft', -6, 'tap Send'),
    (306, 's', 'chime', -6, 'sent'),
    (314, 's', 'blip_two', -6, 'toast confirmed'),
    (vf('lightning') - 6, 'b', 'push-whoosh', -10, 'screen to swap'),
    (vf('fast2') - 2, 's', 'reverse_snap', -12, 'swap arrows rotate'),
    (vf('swaps'), 'b', 'light-shimmer', -13, 'swap instantly'),
    (vf('swaps') + 2, 'b', 'glass-ting', -9, 'toast swapped'),
    (367, 'b', 'swoosh-air', -10, 'push to chart'),
    (vf('real'), 's', 'data_morph', -16, 'balance count'),
    (vf('portfolio') - 4, 's', 'line_glide', -14, 'chart draws'),
    (vf('tracking') - 2, 'b', 'key-press', -6, 'tab 1M'),
    (vf('interactive') + 6, 's', 'felt_tap', -4, 'cursor lands'),
    (vf('interactive') + 14, 's', 'slider_glide', -4, 'scrub drag'),
    (493, 's', 'zoom_fly', -10, 'zoom through'),
    (vf('set') - 4, 's', 'soft_pop', -4, 'alert card'),
    (vf('price'), 's', 'latch', -6, 'toggle on'),
    (vf('alerts') - 4, 's', 'kalimba', -3, 'notification'),
    (vf('alerts') + 4, 's', 'marimba', -5, 'bell shake'),
    (vf('analyze') + 2, 's', 'rise_sweep', -15, 'bars grow'),
    (592, 'b', 'pop', -7, '+8.6% pill'),
    (597, 's', 'air_suck', -12, 'trend exit'),
    (606, 's', 'low_flyby', -10, 'dashboard phone'),
    (vf('decisions') - 4, 's', 'glass_bloom', -6, 'allocation card'),
    (vf('decisions') + 2, 's', 'shutter_roll', -6, 'donut segments'),
    (vf('insights') - 4, 's', 'warm_shimmer', -5, 'AI insight card'),
    (vf('insights') + 4, 's', 'blip_two', -6, 'risk card'),
    (vf('built') - 4, 's', 'wood_knock', -4, 'top mover card'),
    (vf('dashboard') - 2, 'b', 'rise-into-drop', -15, 'push into dashboard'),
    (734, 's', 'dark_sweep', -22, 'darken to security'),
    (vf('and_') - 4, 's', 'sonar_bloom', -7, 'shield draws'),
    (vf('bank') + 4, 's', 'tom_thud', -7, 'lock appears'),
    (vf('bank'), 's', 'typing', -16, 'encryption stream'),
    (vf('encryption') + 4, 's', 'latch', -3, 'shackle locks'),
    (vf('encryption') + 8, 'b', 'impact-bass-1', -15, 'lock flash'),
    (vf('biometric') - 6, 's', 'silk_swipe', -3, 'shield slides left'),
    (vf('biometric') + 6, 'c', 'scan_sweep', -12, 'fingerprint scan'),
    (vf('biometric') + 40, 's', 'chime', -7, 'verified'),
    (vf('your3'), 's', 'reverse_snap', -13, 'fingerprint into shield'),
    (vf('your3') + 6, 's', 'flood_shimmer', -10, 'coins orbit'),
    (vf('your3') + 14, 's', 'bass_bloom', -12, 'pulse rings'),
    (937, 'b', 'iris-whoosh', -9, 'security out'),
    (vf('investing') - 9, 'b', 'panel-flick', -7, 'card investing in'),
    (vf('investing') - 3, 'c', 'ui_tick_a', -10, 'investing active'),
    (vf('trading') - 9, 'b', 'panel-paper1', -10, 'card trading in'),
    (vf('trading') - 3, 'c', 'ui_tick_b', -10, 'trading active'),
    (vf('holding') - 9, 'b', 'panel-paper3', -10, 'card holding in'),
    (vf('holding') - 3, 'c', 'ui_tick_c', -10, 'holding active'),
    (vf('vaultx2') - 10, 'b', 'dive-whoosh', -14, 'cards drop'),
    (vf('vaultx2'), 'b', 'impact-bass-1', -11, 'drop: keeps you ahead'),
    (vf('keeps'), 's', 'rise_sweep', -15, 'arrow draws'),
    (vf('keeps') + 22, 's', 'snap_whip', -12, 'arrow head'),
    (1136, 'b', 'swoosh-air', -10, 'ahead out'),
    (1146, 's', 'zoom_fly', -12, 'end phone rises'),
    (vf('today') + 4, 'c', 'ui_pop_c', -10, 'App Store badge'),
    (vf('today') + 8, 'c', 'ui_pop_d', -10, 'Google Play badge'),
    (vf('own') - 10, 'b', 'rise-into-logo', -8, 'into final lockup'),
    (vf('own') + 13, 'b', 'brand-twinkle', -9, 'final logo mark'),
    (vf('end'), 's', 'glass_bloom', -6, 'CTA'),
    (int(round(END_FILM * FPS)), 's', 'subhit', -10, 'button ending'),
]
cnt = collections.Counter((lib, f) for _, lib, f, _, _ in CUES)
over = {k: v for k, v in cnt.items() if v > 2}
assert not over, over
sfx = np.zeros((N, 2), np.float32)
clips = []
for i, (fr, lib, name, gdb, note) in enumerate(CUES):
    ext = '.wav' if lib == 'c' else '.mp3'
    src = os.path.join(LIB[lib], name + ext)
    used = 'assets/audio/sfx_used/' + name + ext
    if os.path.exists(src):
        shutil.copy2(src, used)
    else:
        src = used
    x = load(src)
    mono = np.abs(x).mean(1)
    act = mono[mono > np.abs(x).max() * 0.05]
    rms = np.sqrt(np.mean(act ** 2)) + 1e-9          # loudness of the sound's body, not its peak
    x = x / rms * db(-26 + gdb)
    x = np.tanh(x / 0.6) * 0.6                        # soft ceiling ~ -4.4 dBFS per sound
    s0 = int(fr / FPS * SR)
    n_ = min(len(x), N - s0)
    sfx[s0:s0 + n_] += x[:n_]
    cname = 'SFX_%02d_%s.wav' % (i + 1, name)
    save('build/audio/sfx_clips/' + cname, x[:n_])
    clips.append({'file': cname, 'frame': fr, 'frames': int(np.ceil(n_ / SR * FPS)), 'note': note, 'src': name + ext})

# ---------------------------------------------------------------- loudness + stems
sfx_bus = -4.0
sfx *= db(sfx_bus)
mix = vo + m + sfx


def lufs(x, tag):
    p = subprocess.run(['ffmpeg', '-hide_banner', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', '-af',
                        'ebur128=peak=true', '-f', 'null', '-'], input=np.asarray(x, np.float32).tobytes(),
                       capture_output=True)
    txt = p.stderr.decode('utf8', 'ignore')
    I = float(txt.split('I:')[-1].split('LUFS')[0])
    tp = float(txt.split('Peak:')[-1].split('dBFS')[0])
    return I, tp


I0, tp0 = lufs(mix, 'mix')
gain = -14.0 - I0
if tp0 + gain > -1.2:
    gain = -1.2 - tp0
for x in (vo, m, sfx):
    x *= db(gain)
mix = vo + m + sfx
I1, tp1 = lufs(mix, 'mix')
Iv, _ = lufs(vo, 'vo')
Im, _ = lufs(m, 'music')
Is, _ = lufs(sfx, 'sfx')
os.makedirs('build/audio', exist_ok=True)
save('build/audio/A1_VO_VaultX.wav', vo)
save('build/audio/A2_Music_ZoneX_InnovationNeeded_edit.wav', m)
save('build/audio/A3_SFX_bus_reference.wav', sfx)
save('build/audio/MIX_reference.wav', mix)
for c in clips:   # apply the same overall gain to the individual SFX clips placed in Resolve
    y = load('build/audio/sfx_clips/' + c['file'])
    save('build/audio/sfx_clips/' + c['file'], y * db(sfx_bus + gain))
json.dump({'gain_db': gain, 'clips': clips}, open('build/audio/sfx_cues.json', 'w'), indent=1)
print('mix I=%.1f LUFS TP=%.1f dBTP | VO %.1f  music %.1f  sfx %.1f | gain %.1f dB | %d cues, %d sounds' % (
    I1, tp1, Iv, Im, Is, gain, len(CUES), len(cnt)))
