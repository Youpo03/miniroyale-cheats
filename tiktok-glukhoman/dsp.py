# -*- coding: utf-8 -*-
"""Небольшая DSP-библиотека: фильтры, реверб, компрессор, питч через rubberband."""
import os
import subprocess
import tempfile
import wave

import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve, lfilter, resample_poly

SR = 44100


def write_wav(path, x, sr=SR):
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1:
        ch = 1
        data = x
    else:
        ch = x.shape[1]
        data = x.reshape(-1)
    data = np.clip(data, -1.0, 1.0)
    with wave.open(path, "wb") as w:
        w.setnchannels(ch)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((data * 32767.0).astype(np.int16).tobytes())


def read_wav(path):
    with wave.open(path) as w:
        sr = w.getframerate()
        ch = w.getnchannels()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768.0
    if ch > 1:
        x = x.reshape(-1, ch)
    return x, sr


def hp(x, f, sr=SR, order=2):
    return sosfilt(butter(order, f, "highpass", fs=sr, output="sos"), x, axis=0)


def lp(x, f, sr=SR, order=2):
    return sosfilt(butter(order, f, "lowpass", fs=sr, output="sos"), x, axis=0)


def bp(x, f1, f2, sr=SR, order=2):
    return sosfilt(butter(order, [f1, f2], "bandpass", fs=sr, output="sos"), x, axis=0)


def resonator(x, f, q, sr=SR):
    """Двухполюсный резонатор (полосовой с высокой добротностью)."""
    w0 = 2 * np.pi * f / sr
    r = np.exp(-w0 / (2 * q))
    a = [1.0, -2 * r * np.cos(w0), r * r]
    b = [(1 - r * r) / 2.0, 0.0, -(1 - r * r) / 2.0]
    return lfilter(b, a, x)


def low_shelf(x, f, gain_db, sr=SR):
    g = 10 ** (gain_db / 20.0) - 1.0
    return x + g * lp(x, f, sr, order=1)


def make_ir(rt60=0.8, sr=SR, predelay=0.012, damp=5500, seed=1, stereo=False, early=True):
    rng = np.random.default_rng(seed)
    n = int(sr * (rt60 * 1.15 + predelay))
    t = np.arange(n) / sr
    env = np.exp(-6.9 * t / rt60)
    chans = []
    for c in range(2 if stereo else 1):
        ir = rng.standard_normal(n) * env
        ir = lp(ir, damp, sr, order=1)
        if early:
            for k in range(6):
                d = int(sr * (predelay + rng.uniform(0.004, 0.035)))
                if d < n:
                    ir[d] += rng.uniform(0.6, 1.4) * (0.7 ** k) * 3.0
        ir[: int(predelay * sr)] = 0
        ir /= np.sqrt(np.sum(ir ** 2)) + 1e-12
        chans.append(ir)
    return np.stack(chans, axis=1) if stereo else chans[0]


def reverb(x, rt60=0.8, wet=0.15, sr=SR, seed=1, damp=5500, predelay=0.012):
    ir = make_ir(rt60, sr, predelay=predelay, damp=damp, seed=seed)
    y = fftconvolve(x, ir)[: len(x) + len(ir)]
    out = np.zeros(len(y))
    out[: len(x)] += x * (1 - wet * 0.5)
    out += y * wet
    return out


def compress(x, thresh_db=-18, ratio=3.0, attack=0.005, release=0.08, sr=SR, makeup_db=0):
    env = np.abs(x)
    a_att = np.exp(-1.0 / (attack * sr))
    a_rel = np.exp(-1.0 / (release * sr))
    # огибающая: быстрая атака, медленный спад (векторно через lfilter с двумя проходами приближённо)
    e = lfilter([1 - a_rel], [1, -a_rel], env)
    e = np.maximum(e, lfilter([1 - a_att], [1, -a_att], env))
    e_db = 20 * np.log10(e + 1e-9)
    over = np.maximum(0, e_db - thresh_db)
    gain_db = -over * (1 - 1.0 / ratio) + makeup_db
    return x * 10 ** (gain_db / 20.0)


def normalize_peak(x, peak=0.9):
    m = np.max(np.abs(x)) + 1e-12
    return x * (peak / m)


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)


def ffmpeg_af(x, sr, af):
    """Прогоняет моно-сигнал через фильтр ffmpeg (например, rubberband)."""
    with tempfile.TemporaryDirectory() as d:
        a = os.path.join(d, "a.wav")
        b = os.path.join(d, "b.wav")
        write_wav(a, normalize_peak(x, 0.95), sr)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a, "-af", af, "-ar", str(sr), b], check=True)
        y, _ = read_wav(b)
    return y


def pitch_shift(x, sr, ratio, formant="shifted"):
    if abs(ratio - 1.0) < 1e-4:
        return x
    y = ffmpeg_af(x, sr, f"rubberband=pitch={ratio}:pitchq=quality:formant={formant}:transients=smooth")
    # выравниваем длину
    if len(y) > len(x):
        y = y[: len(x)]
    elif len(y) < len(x):
        y = np.pad(y, (0, len(x) - len(y)))
    return y


def levinson(r, order):
    a = np.zeros(order + 1)
    a[0] = 1.0
    e = r[0]
    for i in range(1, order + 1):
        acc = r[i] + np.dot(a[1:i], r[i - 1:0:-1])
        k = -acc / (e + 1e-12)
        a_new = a.copy()
        a_new[1:i] = a[1:i] + k * a[i - 1:0:-1]
        a_new[i] = k
        a = a_new
        e *= (1 - k * k)
        if e <= 0:
            break
    return a


def whisperize(x, sr, order=20, seed=3):
    """LPC-вокодер с шумовым возбуждением: превращает голос в шёпот."""
    rng = np.random.default_rng(seed)
    pre = lfilter([1, -0.95], [1], x)
    N = int(0.03 * sr)
    H = N // 2
    win = np.hanning(N)
    out = np.zeros(len(x) + N)
    norm = np.zeros(len(x) + N)
    for i in range(0, len(x) - N, H):
        seg = pre[i:i + N] * win
        en = np.sum(seg ** 2)
        if en < 1e-7:
            norm[i:i + N] += win ** 2
            continue
        r = np.correlate(seg, seg, "full")[N - 1:N + order]
        r[0] *= 1.0001
        a = levinson(r, order)
        noise = rng.standard_normal(N)
        y = lfilter([1.0], a, noise) * win
        y *= np.sqrt(en / (np.sum(y ** 2) + 1e-12))
        out[i:i + N] += y * win
        norm[i:i + N] += win ** 2
    out = out / np.maximum(norm, 1e-3)
    out = lfilter([1], [1, -0.95], out[: len(x)])
    return out


def to_stereo(x, pan=0.0):
    """pan: -1 лево, +1 право (равномощное панорамирование)."""
    ang = (pan + 1) * np.pi / 4
    return np.stack([x * np.cos(ang), x * np.sin(ang)], axis=1)


def resample(x, sr_from, sr_to):
    from math import gcd
    g = gcd(sr_from, sr_to)
    return resample_poly(x, sr_to // g, sr_from // g, axis=0)


def soft_clip(x, drive=1.0):
    return np.tanh(x * drive) / np.tanh(drive)
