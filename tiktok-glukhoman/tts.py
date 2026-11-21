# -*- coding: utf-8 -*-
"""Озвучка всех реплик сценария через Piper + обработка голосов + тайминги слов."""
import json
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib  # noqa: E402
import dsp  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

EP = sys.argv[1] if len(sys.argv) > 1 else "ep1"
STORY = importlib.import_module(f"{EP}_story")
BEATS = STORY.BEATS
from piper import PiperVoice, SynthesisConfig  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(HERE, "models", "piper")
OUT = os.path.join(HERE, "build", EP, "voice")
os.makedirs(OUT, exist_ok=True)

# Исправления ударений/произношения: слово в субтитрах -> сырые фонемы для Piper
PRON_FIX = [
    (r"\bБез связи", "[[bʲɪs]] связи"),
    (r"\bБез двух", "[[bʲɪz]] двух"),
    (r"\bдо полуночи", "[[də]] полуночи"),
]

VOICES = {
    "N": dict(model="ruslan", length=1.17, noise=0.55, noise_w=0.65, pitch=0.94, pause=0.24, rms=-19.0, pan=0.0),
    "G": dict(model="irina", length=1.16, noise=0.6, noise_w=0.7, pitch=0.885, pause=0.3, rms=-20.0, pan=0.0),
    "F": dict(model="irina", length=1.18, noise=0.6, noise_w=0.7, pitch=0.885, pause=0.3, rms=-23.0, pan=0.25),
    "F2": dict(model="irina", length=1.2, noise=0.5, noise_w=0.6, pitch=0.87, pause=0.38, rms=-21.0, pan=0.25),
    "W": dict(model="irina", length=1.22, noise=0.6, noise_w=0.7, pitch=0.9, pause=0.34, rms=-23.0, pan=-0.35),
}

PUNCT = set(",.;:?!\"…—-«»()' ")
V_PH = set("aeiouyɑɐəɛɪʊʌɨɵæɔøœɤɯ")
V_TX = set("аеёиоуыэюяАЕЁИОУЫЭЮЯ")


def caption_tokens(text):
    words = []
    cur, cur_red, red = "", False, False
    for ch in text:
        if ch == "*":
            red = not red
            continue
        if ch == " ":
            if cur:
                words.append([cur, cur_red])
            cur, cur_red = "", False
            continue
        cur += ch
        cur_red = cur_red or red
    if cur:
        words.append([cur, cur_red])
    return words


def tts_text(text):
    t = text.replace("*", "")
    for pat, rep in PRON_FIX + list(getattr(STORY, "PRON_FIX", [])):
        t = re.sub(pat, rep, t)
    return t


def phon_words_from_chunk(chunk, offset):
    pos = offset
    words, cur = [], None
    for al in chunk.phoneme_alignments:
        ph, n = al.phoneme, int(al.num_samples)
        if ph in PUNCT or ph in ("^", "$", "_"):
            if cur:
                words.append(cur)
                cur = None
        else:
            if cur is None:
                cur = [pos, pos + n, 0]
            cur[1] = pos + n
            if ph in V_PH:
                cur[2] += 1
        pos += n
    if cur:
        words.append(cur)
    return words


def align(tokens, pwords):
    """DP: каждое фонемное слово покрывает 1..3 текстовых слова."""
    T, P = len(tokens), len(pwords)
    INF = 1e9
    dp = np.full((T + 1, P + 1), INF)
    bt = {}
    dp[0, 0] = 0
    for i in range(T + 1):
        for j in range(P):
            if dp[i, j] >= INF:
                continue
            for k in (1, 2, 3):
                if i + k > T:
                    break
                tv = sum(tokens[i + m][1] for m in range(k))
                c = dp[i, j] + abs(tv - pwords[j][2]) + 0.35 * (k - 1)
                if c < dp[i + k, j + 1]:
                    dp[i + k, j + 1] = c
                    bt[(i + k, j + 1)] = (i, k)
    if dp[T, P] >= INF:
        return None
    spans = [None] * T
    i, j = T, P
    while j > 0:
        pi, k = bt[(i, j)]
        s, e, _ = pwords[j - 1]
        lens = [max(1, len(tokens[pi + m][0])) for m in range(k)]
        tot = sum(lens)
        acc = s
        for m in range(k):
            d = (e - s) * lens[m] / tot
            spans[pi + m] = (acc, acc + d)
            acc += d
        i, j = pi, j - 1
    return spans


MAX_PAUSE = {"N": 0.4, "G": 0.5, "F": 0.5, "F2": 0.55, "W": 0.5}


def squeeze_pauses(x, sr, pwords, max_pause):
    """Укорачивает слишком длинные паузы внутри реплики, сдвигая тайминги слов."""
    hop = int(0.01 * sr)
    n = len(x) // hop
    e = np.array([np.sqrt(np.mean(x[i * hop:(i + 1) * hop] ** 2)) for i in range(n)])
    thr = max(e) * 10 ** (-38 / 20)
    quiet = e < thr
    cuts = []  # (start_sample, length)
    i = 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]:
                j += 1
            run = (j - i) * hop
            if run > max_pause * sr and i > 0 and j < n:
                cut = run - int(max_pause * sr)
                cuts.append((i * hop + int(max_pause * sr / 2), cut))
            i = j
        else:
            i += 1
    if not cuts:
        return x, pwords
    keep = np.ones(len(x), bool)
    for s, c in cuts:
        keep[s:s + c] = False
    y = x[keep]

    def remap(p):
        d = 0
        for s, c in cuts:
            if p >= s + c:
                d += c
            elif p > s:
                d += p - s
        return p - d
    pw = [[remap(a), remap(b), v] for a, b, v in pwords]
    return y, pw


def trim_bounds(x, sr, thr_db=-42):
    a = np.abs(x)
    thr = np.max(a) * 10 ** (thr_db / 20)
    idx = np.where(a > thr)[0]
    if len(idx) == 0:
        return 0, len(x)
    s = max(0, idx[0] - int(0.03 * sr))
    e = min(len(x), idx[-1] + int(0.06 * sr))
    return s, e


def process(spk, x, sr):
    """x — 22.05 кГц float. Возвращает 44.1 кГц моно."""
    cfg = VOICES[spk]
    x = dsp.pitch_shift(x, sr, cfg["pitch"])
    x = dsp.resample(x, sr, dsp.SR)
    S = dsp.SR
    if spk == "N":
        x = dsp.hp(x, 70)
        x = dsp.low_shelf(x, 180, 3.0)
        x = dsp.lp(x, 9500)
        x = dsp.compress(x, -22, 2.5)
        x = dsp.reverb(x, rt60=0.55, wet=0.09, seed=11, damp=4500)
    elif spk in ("G", "F", "F2"):
        x = dsp.hp(x, 95)
        t = np.arange(len(x)) / S
        x = x * (1.0 + 0.07 * np.sin(2 * np.pi * 5.3 * t))  # старческое дрожание
        x = dsp.compress(x, -22, 2.5)
        if spk == "G":
            x = dsp.reverb(x, rt60=0.6, wet=0.12, seed=12, damp=5000)
        else:
            # через дверь: глухо, гулко
            x = dsp.lp(x, 2000 if spk == "F" else 2600, order=4)
            x = dsp.hp(x, 140)
            if spk == "F2":
                sub = dsp.pitch_shift(x, S, 0.62)
                x = x + 0.22 * dsp.lp(sub, 1500)
            x = dsp.reverb(x, rt60=1.1 if spk == "F" else 1.4, wet=0.24 if spk == "F" else 0.24,
                           seed=13, damp=3000, predelay=0.02)
    elif spk == "W":
        w = dsp.whisperize(x, S, order=22)
        w = dsp.hp(w, 260)
        x = 0.7 * w + 0.6 * dsp.hp(x, 900)
        x = dsp.compress(x, -24, 2.0)
        x = dsp.reverb(x, rt60=0.45, wet=0.1, seed=14, damp=6000)
    x = dsp.hp(x, 40)
    # нормализация по RMS (по активной части)
    act = x[np.abs(x) > 0.02 * np.max(np.abs(x))]
    cur = 20 * np.log10(np.sqrt(np.mean(act ** 2)) + 1e-12)
    x = x * 10 ** ((cfg["rms"] - cur) / 20)
    pk = np.max(np.abs(x))
    if pk > 0.95:
        x = x * 0.95 / pk
    return x


NTAKES = 4
_ASR = None


def asr(y):
    global _ASR
    from faster_whisper import WhisperModel
    if _ASR is None:
        _ASR = WhisperModel("small", device="cpu", compute_type="int8",
                            download_root=os.path.join(HERE, "models", "whisper"))
    x16 = dsp.resample(y, dsp.SR, 16000).astype(np.float32)
    segs, _ = _ASR.transcribe(x16, language="ru", beam_size=5, vad_filter=False)
    return " ".join(s.text.strip() for s in segs)


NUMS = {"1": "один", "2": "два", "3": "три", "4": "четыре", "5": "пять", "10": "десять", "12": "двенадцать",
        "30": "тридцать"}


def _norm(s):
    s = s.lower().replace("ё", "е").replace("*", "")
    s = re.sub(r"\d+", lambda m: NUMS.get(m.group(0), m.group(0)), s)
    s = re.sub(r"[^а-яa-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def cer(ref, hyp):
    a, b = _norm(ref), _norm(hyp)
    d = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        prev, d[0] = d[0], i
        for j in range(1, len(b) + 1):
            cur = d[j]
            d[j] = min(d[j] + 1, d[j - 1] + 1, prev + (a[i - 1] != b[j - 1]))
            prev = cur
    return d[len(b)] / max(1, len(a))


def line_key(spk, text):
    import hashlib
    cfg = VOICES[spk]
    fixes = PRON_FIX + list(getattr(STORY, "PRON_FIX", []))
    return hashlib.md5(json.dumps([spk, text, cfg, MAX_PAUSE[spk], fixes], ensure_ascii=False).encode()).hexdigest()[:12]


def load_previous():
    """Уже готовая и проверенная озвучка из прошлой сборки: переиспользуем, если текст и настройки не менялись."""
    path = os.path.join(HERE, "build", EP, "voice_meta.json")
    reuse, audio = {}, {}
    if os.path.exists(path) and "--fresh" not in sys.argv:
        with open(path, encoding="utf-8") as f:
            for m in json.load(f):
                npy = os.path.join(OUT, f"{m['beat']:03d}.npy")
                if m.get("key") and os.path.exists(npy):
                    reuse[m["key"]] = m
                    audio[m["beat"]] = np.load(npy).astype(np.float64)
    return reuse, audio


def main():
    voices = {}
    meta = []
    reuse, reuse_audio = load_previous()
    for bi, b in enumerate(BEATS):
        if b["kind"] != "line":
            continue
        spk = b["spk"]
        cfg = VOICES[spk]
        syn = SynthesisConfig(length_scale=cfg["length"], noise_scale=cfg["noise"], noise_w_scale=cfg["noise_w"])
        tokens = caption_tokens(b["text"])
        speak = [(t[0], sum(1 for c in t[0] if c in V_TX)) for t in tokens if re.search(r"[А-Яа-яЁёA-Za-z]", t[0])]
        import hashlib, pickle
        key = line_key(spk, b["text"])
        if key in reuse:
            m = dict(reuse[key])
            y = reuse_audio[m["beat"]]
            m["beat"] = bi
            np.save(os.path.join(OUT, f"{bi:03d}.npy"), y.astype(np.float32))
            dsp.write_wav(os.path.join(OUT, f"{bi:03d}_{spk}.wav"), y)
            meta.append(m)
            print(f"{bi:3d} {spk:2s} (готовая озвучка) {m['text']}")
            continue
        if cfg["model"] not in voices:
            voices[cfg["model"]] = PiperVoice.load(os.path.join(MODELS, cfg["model"] + ".onnx"), include_alignments=True)
        voice = voices[cfg["model"]]
        cpath = os.path.join(HERE, "build", EP, "voice_cache", key + ".pkl")
        os.makedirs(os.path.dirname(cpath), exist_ok=True)
        best = None
        if os.path.exists(cpath):
            with open(cpath, "rb") as f:
                best = pickle.load(f)
            sr = 22050
        for attempt in range(0 if best is not None and best[0] <= 0.05 else NTAKES):
            chunks = list(voice.synthesize(tts_text(b["text"]), syn, include_alignments=True))
            sr = chunks[0].sample_rate
            parts, pwords, pos = [], [], 0
            for ci, ch in enumerate(chunks):
                a = ch.audio_float_array.astype(np.float64)
                s, e = trim_bounds(a, sr)
                if ci > 0:
                    gap = np.zeros(int(cfg["pause"] * sr))
                    parts.append(gap)
                    pos += len(gap)
                pw = phon_words_from_chunk(ch, pos - s)
                parts.append(a[s:e])
                pos += e - s
                pwords += [w for w in pw if w[1] > pos - (e - s) - 1]
            raw = np.concatenate(parts)
            raw, pwords = squeeze_pauses(raw, sr, pwords, MAX_PAUSE[spk])
            y = process(spk, raw, sr)
            heard = asr(y)
            err = cer(b["text"], heard)
            print(f"   take {attempt}: err={err:.3f}  «{heard}»", flush=True)
            if best is None or err < best[0]:
                best = (err, raw, pwords, y, heard)
            if err <= 0.02:
                break
        with open(cpath, "wb") as f:
            pickle.dump(best, f)
        err, raw, pwords, y, heard = best
        spans = align(speak, pwords)
        if spans is None:
            print("!! fallback alignment for", b["text"], len(speak), len(pwords))
            tot = sum(len(w) for w, _ in speak)
            acc, spans = 0.0, []
            for w, _ in speak:
                d = len(raw) * len(w) / tot
                spans.append((acc, acc + d))
                acc += d
        # раздаём тайминги токенам (пунктуационные токены приклеиваются к предыдущему слову)
        words = []
        k = 0
        for t in tokens:
            if re.search(r"[А-Яа-яЁёA-Za-z]", t[0]):
                s, e = spans[k]
                k += 1
                words.append(dict(w=t[0], red=t[1], s=max(0.0, s / sr), e=min(len(raw), e) / sr))
            elif words:
                words[-1]["w"] += " " + t[0]
            else:
                words.append(dict(w=t[0], red=t[1], s=0.0, e=0.05))
        dur = len(y) / dsp.SR
        speech_dur = len(raw) / sr
        # огибающая для липсинка (30 к/с), по сухому сигналу
        hop = sr // 30
        env = [float(np.sqrt(np.mean(raw[i:i + hop] ** 2))) for i in range(0, len(raw), hop)]
        m = max(env) + 1e-9
        env = [round(min(1.0, v / m * 1.3), 3) for v in env]
        np.save(os.path.join(OUT, f"{bi:03d}.npy"), y.astype(np.float32))
        dsp.write_wav(os.path.join(OUT, f"{bi:03d}_{spk}.wav"), y)
        meta.append(dict(beat=bi, key=key, spk=spk, text=b["text"], asr=heard, asr_err=round(err, 3), dur=dur, speech_dur=speech_dur, words=words, env=env, pan=cfg["pan"]))
        print(f"{bi:3d} {spk:2s} {speech_dur:5.2f}s  " + " ".join(f"{w['w']}[{w['s']:.2f}-{w['e']:.2f}]" for w in words))
    with open(os.path.join(HERE, "build", EP, "voice_meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
