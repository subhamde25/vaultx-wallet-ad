# Custom synthesized SFX for the VaultX ad (no third-party audio): scan sweep, UI ticks, UI pops.
# usage (from vaultx/): python -I tools/make_sfx.py  -> assets/audio/sfx_custom/*.wav
import os
import subprocess
import numpy as np

SR = 48000
OUT = 'assets/audio/sfx_custom'
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(42)


def save(name, x):
    x = np.asarray(x, np.float32)
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    x = x / (np.abs(x).max() + 1e-9) * 0.7
    p = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-',
                        '-c:a', 'pcm_s24le', os.path.join(OUT, name + '.wav')], input=x.tobytes())
    assert p.returncode == 0


def env(n, a, d):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / d)
    return e


def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.zeros_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


# fingerprint scan: rising digital sweep with 32 Hz gating and a soft noise bed
n = int(1.5 * SR)
t = np.arange(n) / SR
f = 500 + 2200 * (t / t[-1]) ** 1.6
ph = 2 * np.pi * np.cumsum(f) / SR
gate = 0.55 + 0.45 * (np.sin(2 * np.pi * 32 * t) > 0)
tone = np.sin(ph) * gate + 0.35 * np.sin(2 * ph)
bed = lowpass(rng.standard_normal(n), 3000) * 0.25
shape = np.minimum(1, t / 0.08) * np.minimum(1, (t[-1] - t) / 0.25)
L = (tone + bed) * shape
R = (np.roll(tone, 90) + bed) * shape
save('scan_sweep', np.stack([L, R], 1))

# UI ticks: short tonal clicks
for name, fc in [('ui_tick_a', 1850), ('ui_tick_b', 2250), ('ui_tick_c', 2700)]:
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    click = rng.standard_normal(n) * env(n, 0.0005, 0.004)
    tone = np.sin(2 * np.pi * fc * t) * env(n, 0.001, 0.025) + 0.4 * np.sin(2 * np.pi * fc * 1.5 * t) * env(n, 0.001, 0.012)
    save(name, 0.5 * click + tone)

# UI pops: pitch-drop bubble with a tiny transient
for name, (f0, f1) in [('ui_pop_c', (1100, 380)), ('ui_pop_d', (1350, 470))]:
    n = int(0.16 * SR)
    t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t / 0.02)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * env(n, 0.001, 0.04)
    tr = rng.standard_normal(n) * env(n, 0.0003, 0.002)
    save(name, body + 0.3 * tr)
print('custom sfx ->', OUT, sorted(os.listdir(OUT)))
