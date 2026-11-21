# -*- coding: utf-8 -*-
"""Библиотека звуков: синтез SFX, эмбиент, музыка, микшер."""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dsp  # noqa: E402
from dsp import SR  # noqa: E402

RNG = np.random.default_rng(7)


def T(n):
    return np.arange(n) / SR


def env_ar(n, a, r):
    """Огибающая: атака a сек, экспоненциальный спад r сек."""
    t = T(n)
    e = np.exp(-np.maximum(0, t - a) / r)
    if a > 0:
        e = np.where(t < a, t / a, e)
    return e


# ----------------------------------------------------------------- SFX
def knock(strength=1.0, seed=0, dull=0.0):
    rng = np.random.default_rng(seed)
    n = int(0.7 * SR)
    t = T(n)
    exc = np.zeros(n)
    L = int(0.0025 * SR)
    exc[:L] = np.sin(np.pi * np.arange(L) / L)
    M = int(0.008 * SR)
    exc[:M] += 0.35 * rng.standard_normal(M) * np.exp(-np.arange(M) / (0.0018 * SR))
    modes = [(78, 7, 1.0), (112, 8, 0.9), (167, 10, 0.8), (231, 11, 0.65), (342, 13, 0.5),
             (488, 15, 0.38), (690, 18, 0.28), (1010, 20, 0.2), (1460, 22, 0.12), (2100, 24, 0.07)]
    y = np.zeros(n)
    for f, q, g in modes:
        f2 = f * rng.uniform(0.96, 1.04) * (1 - 0.15 * dull)
        y += g * dsp.resonator(exc, f2, q)
    y += 0.9 * np.sin(2 * np.pi * 52 * t) * np.exp(-t / 0.05) * (1 - np.exp(-t / 0.002))
    y += 0.25 * dsp.hp(exc, 2500)
    y = dsp.lp(y, 4200 - 2000 * dull)
    y = dsp.normalize_peak(y, 0.9) * strength
    return y


def rattle(n_clicks=6, seed=3, spread=0.22):
    rng = np.random.default_rng(seed)
    n = int((spread + 0.2) * SR)
    y = np.zeros(n)
    for k in range(n_clicks):
        p = int(rng.uniform(0.01, spread) * SR)
        m = int(0.004 * SR)
        burst = rng.standard_normal(m) * np.exp(-np.arange(m) / (0.0008 * SR))
        seg = np.zeros(int(0.08 * SR))
        seg[:m] = burst
        seg = dsp.resonator(seg, rng.uniform(2300, 2600), 25) + 0.7 * dsp.resonator(seg, rng.uniform(3600, 4100), 30)
        a = rng.uniform(0.3, 1.0) * (1 - k / (n_clicks + 2))
        y[p:p + len(seg)] += a * seg[: max(0, min(len(seg), n - p))]
    return dsp.normalize_peak(y, 0.5)


def sub_boom(dur=1.6, f0=62, f1=28, amp=1.0):
    n = int(dur * SR)
    t = T(n)
    f = f1 + (f0 - f1) * np.exp(-t / 0.25)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) * np.exp(-t / (dur * 0.35)) * (1 - np.exp(-t / 0.004))
    return amp * y


def stinger(dur=2.2, seed=5, base=880.0):
    """Диссонантный «визг» струнных + гул — джамп-скейр."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = T(n)
    y = np.zeros(n)
    for f in (base, base * 1.0595, base * 1.414, base * 0.75, base * 2.12):
        vib = 1 + 0.006 * np.sin(2 * np.pi * rng.uniform(5, 7) * t + rng.uniform(0, 6))
        ph = 2 * np.pi * np.cumsum(f * vib) / SR
        saw = sum(np.sin(k * ph) / k for k in range(1, 7))
        y += saw * rng.uniform(0.5, 1.0)
    y = dsp.lp(y, 5000) * env_ar(n, 0.015, dur * 0.3)
    y += 0.4 * dsp.hp(RNG.standard_normal(n), 3000) * env_ar(n, 0.005, 0.12)
    return dsp.normalize_peak(y, 0.6)


def riser(dur=2.0, seed=9):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = T(n)
    x = rng.standard_normal(n)
    # полосовой шум с растущей частотой: смешиваем несколько полос
    y = np.zeros(n)
    bands = [(200, 500), (500, 1200), (1200, 3000), (3000, 7000)]
    for i, (a, b) in enumerate(bands):
        w = np.clip(t / dur * len(bands) - i + 0.5, 0, 1)
        y += dsp.bp(x, a, b) * w
    f = 90 * 2 ** (t / dur * 2.5)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.6 * np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR)
    y = 0.6 * y + 0.25 * tone
    y *= (t / dur) ** 2.2
    return dsp.normalize_peak(y, 0.55)


def creak(dur=0.9, seed=11, f_start=40, f_end=95):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = T(n)
    rate = f_start + (f_end - f_start) * (t / dur) + 12 * np.sin(2 * np.pi * 1.7 * t) + rng.standard_normal(n).cumsum() / np.sqrt(n) * 30
    rate = np.clip(rate, 15, 200)
    ph = np.cumsum(rate) / SR
    pulses = np.zeros(n)
    idx = np.where(np.diff(np.floor(ph)) > 0)[0]
    pulses[idx] = rng.uniform(0.6, 1.0, len(idx))
    y = (dsp.resonator(pulses, 620, 12) + 0.8 * dsp.resonator(pulses, 1150, 14) +
         0.6 * dsp.resonator(pulses, 2300, 16) + 0.3 * dsp.resonator(pulses, 3400, 18))
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 0.6
    return dsp.normalize_peak(y * e, 0.45)


def bolt_slide(dur=0.75, seed=13):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = T(n)
    x = dsp.bp(rng.standard_normal(n), 350, 2600)
    grain = np.abs(dsp.lp(rng.standard_normal(n), 40)) * 3
    e = np.clip(t / 0.05, 0, 1) * np.clip((dur - 0.12 - t) / 0.05, 0, 1)
    y = x * grain * e * 0.5
    cr = creak(dur * 0.8, seed=seed + 1, f_start=70, f_end=55)
    y[: len(cr)] += 0.25 * cr[: n]
    clunk = knock(0.7, seed=21, dull=0.6)
    p = int((dur - 0.12) * SR)
    out = np.zeros(n + len(clunk))
    out[:n] += y
    out[p:p + len(clunk)] += clunk
    return out


def tick(high=True, seed=0):
    rng = np.random.default_rng(seed)
    n = int(0.06 * SR)
    m = int(0.002 * SR)
    exc = np.zeros(n)
    exc[:m] = rng.standard_normal(m)
    if high:
        y = dsp.resonator(exc, 3300, 30) + 0.6 * dsp.resonator(exc, 5200, 35)
    else:
        y = dsp.resonator(exc, 1900, 25) + 0.6 * dsp.resonator(exc, 2850, 30)
    return dsp.normalize_peak(y, 1.0)


def heartbeat_one(amp=1.0):
    n = int(0.45 * SR)
    t = T(n)
    def thump(dl, a):
        tt = np.maximum(0, t - dl)
        return a * np.sin(2 * np.pi * 48 * tt) * np.exp(-tt / 0.07) * (t >= dl) * (1 - np.exp(-tt / 0.003))
    y = thump(0, 1.0) + thump(0.16, 0.7)
    return amp * y


def music_box_note(freq, dur=2.4, seed=0):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = T(n)
    det = 2 ** (rng.uniform(-14, 14) / 1200)
    f = freq * det
    wow = 1 + 0.004 * np.sin(2 * np.pi * 0.6 * t + rng.uniform(0, 6))
    ph = 2 * np.pi * np.cumsum(f * wow) / SR
    y = (np.sin(ph) * np.exp(-t / 0.9) + 0.35 * np.sin(2 * ph) * np.exp(-t / 0.4) +
         0.18 * np.sin(3.01 * ph) * np.exp(-t / 0.25) + 0.12 * np.sin(4.17 * ph) * np.exp(-t / 0.12))
    y *= (1 - np.exp(-t / 0.002))
    y[: int(0.004 * SR)] += 0.2 * rng.standard_normal(int(0.004 * SR))
    return y


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


# Оригинальная мелодия-«шкатулка» (ре минор)
MELODY = [(69, 0.5), (74, 0.5), (77, 0.5), (76, 0.5), (74, 0.75), (73, 0.25), (74, 1.0),
          (70, 0.5), (74, 0.5), (77, 0.5), (79, 0.5), (77, 0.75), (76, 0.25), (73, 1.0),
          (69, 0.5), (74, 0.5), (77, 0.5), (81, 0.5), (80, 0.75), (77, 0.25), (74, 1.5)]


def music_box(dur, beat=0.46, seed=1, detune_drift=0.0):
    n = int(dur * SR)
    y = np.zeros(n + int(3 * SR))
    t = 0.0
    k = 0
    while t < dur:
        m, d = MELODY[k % len(MELODY)]
        drift = 2 ** (-detune_drift * t / dur / 12)
        note = music_box_note(midi(m) * drift, seed=seed + k)
        p = int(t * SR)
        y[p:p + len(note)] += note * (0.9 if k % 7 else 1.0)
        # иногда — тихая нижняя нота
        if k % 4 == 0:
            low = music_box_note(midi(m - 12) * drift, seed=seed + 100 + k) * 0.45
            y[p:p + len(low)] += low
        t += d * beat
        k += 1
    y = y[:n]
    y = dsp.reverb(y, rt60=2.2, wet=0.35, seed=31, damp=4000)[:n]
    return dsp.normalize_peak(y, 0.5)


def drone(dur, notes=(38, 45), cutoff=(300, 300), seed=2, dissonance=None):
    """Мрачный пэд: аддитивная «пила» с плавающим фильтром."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = T(n)
    fc = np.interp(t, [0, dur], cutoff)
    y = np.zeros(n)
    voices = [(midi(m), 1.0) for m in notes]
    if dissonance is not None:
        voices.append((midi(dissonance[0]), dissonance[1]))
    for f0, amp in voices:
        for det in (-4, 3.5):
            f = f0 * 2 ** (det / 1200)
            ph0 = rng.uniform(0, 6.28)
            for h in range(1, 12):
                g = (1.0 / h) / (1 + (h * f / fc) ** 4)
                if np.max(g) < 1e-3:
                    continue
                lfo = 1 + 0.25 * np.sin(2 * np.pi * rng.uniform(0.03, 0.12) * t + rng.uniform(0, 6))
                y += amp * g * lfo * np.sin(2 * np.pi * f * h * t + ph0 * h)
    return dsp.normalize_peak(y, 0.5)


def crickets(dur, seed=4, n_crickets=4):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = T(n)
    out = np.zeros((n, 2))
    for c in range(n_crickets):
        fc = rng.uniform(4200, 5200)
        period = rng.uniform(0.42, 0.75)
        pulses = rng.integers(2, 5)
        prate = rng.uniform(28, 40)
        carrier = np.sin(2 * np.pi * fc * t + rng.uniform(0, 6))
        amp = np.zeros(n)
        tt = rng.uniform(0, period)
        while tt < dur:
            for p in range(pulses):
                s = int((tt + p / prate) * SR)
                L = int(0.6 / prate * SR)
                if s + L < n:
                    amp[s:s + L] += np.sin(np.pi * np.arange(L) / L) ** 2
            tt += period * rng.uniform(0.9, 1.1)
        y = carrier * amp * rng.uniform(0.4, 1.0)
        out += dsp.to_stereo(y, rng.uniform(-0.8, 0.8))
    return out / max(1e-9, np.max(np.abs(out))) * 0.5


def wind(dur, seed=6):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = T(n)
    br = np.cumsum(rng.standard_normal(n))
    br = dsp.hp(br, 20)
    y = dsp.bp(br, 120, 700)
    lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t + 1) * np.sin(2 * np.pi * 0.023 * t)
    return dsp.normalize_peak(y * lfo, 0.5)


def roomtone(dur, seed=8):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    y = dsp.lp(rng.standard_normal(n), 900)
    return dsp.normalize_peak(y, 0.5)


def whoosh(dur=0.5, seed=10):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = T(n)
    x = rng.standard_normal(n)
    y = dsp.bp(x, 300, 2500) * np.sin(np.pi * t / dur) ** 2
    return dsp.normalize_peak(y, 0.4)


# ----------------------------------------------------------------- сведение
class Mix:
    def __init__(self, dur):
        self.n = int((dur + 4) * SR)
        self.bus = {k: np.zeros((self.n, 2)) for k in ("voice", "sfx", "music", "amb")}

    def add(self, bus, t, x, gain_db=0.0, pan=0.0, fade_in=0.0, fade_out=0.0):
        g = 10 ** (gain_db / 20)
        x = np.asarray(x, dtype=np.float64)
        if x.ndim == 1:
            x = dsp.to_stereo(x, pan)
        x = x.copy()
        if fade_in > 0:
            k = min(len(x), int(fade_in * SR))
            x[:k] *= np.linspace(0, 1, k)[:, None]
        if fade_out > 0:
            k = min(len(x), int(fade_out * SR))
            x[-k:] *= np.linspace(1, 0, k)[:, None]
        p = int(round(t * SR))
        if p < 0:
            x = x[-p:]
            p = 0
        m = min(len(x), self.n - p)
        if m > 0:
            self.bus[bus][p:p + m] += x[:m] * g


def load_timeline(ep):
    with open(os.path.join(HERE, "build", ep, "timeline.json"), encoding="utf-8") as f:
        return json.load(f)


def add_voices(mx, tl, ep):
    for b in tl["beats"]:
        if b["kind"] == "line":
            y = np.load(os.path.join(HERE, "build", ep, "voice", f"{b['i']:03d}.npy")).astype(np.float64)
            mx.add("voice", b["t0"], y, 0.0, pan=b["pan"])


def finish(mx, total, ep, music_duck=0.45, amb_duck=0.3, gains=(1.0, 0.9, 0.85, 1.4)):
    """Дакинг музыки под голос, сумма шин, мягкий лимитер, запись mix.wav."""
    from scipy.signal import lfilter
    v = np.abs(mx.bus["voice"]).max(axis=1)
    a_r = np.exp(-1.0 / (0.35 * SR))
    e = lfilter([1 - a_r], [1, -a_r], v)
    e = np.minimum(1.0, e / (np.percentile(e[e > 1e-4], 90) + 1e-9))
    mx.bus["music"] *= (1.0 - music_duck * e)[:, None]
    mx.bus["amb"] *= (1.0 - amb_duck * e)[:, None]
    gv, gs, gm, ga = gains
    out = mx.bus["voice"] * gv + mx.bus["sfx"] * gs + mx.bus["music"] * gm + mx.bus["amb"] * ga
    n_total = int(total * SR)
    out = out[:n_total]
    pk = np.max(np.abs(out))
    out = out / max(pk, 1e-9) * 0.98
    out = dsp.soft_clip(out * 1.4, 1.4) * 0.92
    dsp.write_wav(os.path.join(HERE, "build", ep, "mix.wav"), out)
    for k in mx.bus:
        print(k, "peak %.2f rms %.1f dB" % (np.max(np.abs(mx.bus[k])), dsp.rms_db(mx.bus[k][:n_total])))
    print("mix written", out.shape, "%.2fs" % (len(out) / SR))
