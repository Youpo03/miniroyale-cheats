# -*- coding: utf-8 -*-
"""Собирает таймлайн: абсолютные времена битов, сцен, субтитров и меток (cue)."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, HERE)
import importlib  # noqa: E402

EP = sys.argv[1] if len(sys.argv) > 1 else "ep1"
BEATS = importlib.import_module(f"{EP}_story").BEATS

START_PAD = 0.0   # видео начинается сразу с хука (первый кадр = обложка)
END_PAD = 0.0


SHORT = {"в", "к", "с", "у", "о", "и", "а", "на", "не", "из", "за", "до", "по", "от", "же", "что", "мне", "я"}


def chunk_words(words, max_chars=17, max_words=4):
    """Группирует слова в фразы по 1–4 слова для субтитров (рвём по пунктуации)."""
    chunks, cur = [], []
    for w in words:
        txt = " ".join(x["w"] for x in cur + [w])
        if cur and (len(txt) > max_chars or len(cur) >= max_words or (len(cur) >= 2 and w["red"] != cur[-1]["red"])):
            chunks.append(cur)
            cur = []
        cur.append(w)
        if w["w"][-1] in ".?!:…—,":
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    # не оставляем предлог/частицу висеть в конце фразы
    for k in range(len(chunks) - 1):
        while len(chunks[k]) > 1 and chunks[k][-1]["w"].lower() in SHORT:
            chunks[k + 1].insert(0, chunks[k].pop())
    # одиночное короткое слово в конце — приклеиваем к предыдущей фразе
    if len(chunks) > 1 and len(chunks[-1]) == 1 and len(chunks[-1][0]["w"]) <= 3:
        prev = " ".join(x["w"] for x in chunks[-2] + chunks[-1])
        if len(prev) <= 22 and chunks[-2][-1]["w"][-1] not in ".?!:":
            chunks[-2] += chunks.pop()
    return chunks


def build():
    with open(os.path.join(HERE, "build", EP, "voice_meta.json"), encoding="utf-8") as f:
        vmeta = {m["beat"]: m for m in json.load(f)}
    t = START_PAD
    beats = []
    for bi, b in enumerate(BEATS):
        t += b.get("pre", 0.0)
        e = dict(b)
        e["i"] = bi
        e["t0"] = t
        if b["kind"] == "line":
            m = vmeta[bi]
            e["dur"] = m["speech_dur"]
            e["audio_dur"] = m["dur"]
            e["words"] = m["words"]
            e["env"] = m["env"]
            e["pan"] = m["pan"]
            t += m["speech_dur"] + b.get("gap", 0.2)
        else:
            t += b["dur"]
        e["t1"] = t
        beats.append(e)
    total = t + END_PAD

    # сцены
    scenes = []
    for e in beats:
        if not scenes or scenes[-1]["name"] != e["scene"]:
            scenes.append(dict(name=e["scene"], t0=e["t0"], beats=[]))
        scenes[-1]["beats"].append(e["i"])
    for k, s in enumerate(scenes):
        s["t1"] = scenes[k + 1]["t0"] if k + 1 < len(scenes) else total

    # метки
    cues = {}
    for e in beats:
        if "cue" in e:
            cues[e["cue"]] = e["t0"]
            cues[e["cue"] + "_end"] = e["t1"]

    # стуки (для визуала и звука)
    knocks = []
    for e in beats:
        if e["kind"] != "sfx":
            continue
        if e["sfx"] == "knock_triple":
            knocks += [dict(t=e["t0"] + d, s=0.85, n=k + 1, grp="title") for k, d in enumerate((0.05, 0.47, 0.89))]
        elif e["sfx"] == "knock":
            knocks.append(dict(t=e["t0"] + 0.06, s=1.0, n=None, grp="door"))
        elif e["sfx"] == "knock_big":
            knocks.append(dict(t=e["t0"] + 0.10, s=1.9, n=None, grp="door"))
        elif e["sfx"] == "knock_triple_end":
            knocks += [dict(t=e["t0"] + d, s=1.25, n=k + 1, grp="end") for k, d in enumerate((0.15, 0.6, 1.05))]
    dn = 0
    for k in knocks:
        if k["grp"] == "door":
            dn += 1
            k["n"] = dn

    # субтитры
    caps = []
    for e in beats:
        if e["kind"] != "line":
            continue
        chs = chunk_words(e["words"])
        for k, ch in enumerate(chs):
            s = e["t0"] + ch[0]["s"]
            if k + 1 < len(chs):
                end = e["t0"] + chs[k + 1][0]["s"]
            else:
                end = min(e["t1"], e["t0"] + e["dur"] + 0.35)
            caps.append(dict(t0=s - 0.04, t1=end, spk=e["spk"], scene=e["scene"],
                             words=[dict(w=w["w"], red=w["red"], t=e["t0"] + w["s"]) for w in ch]))
    # хвосты: каждая фраза висит до следующей, если пауза короткая
    for k in range(len(caps) - 1):
        if 0 < caps[k + 1]["t0"] - caps[k]["t1"] < 0.25:
            caps[k]["t1"] = caps[k + 1]["t0"]

    tl = dict(total=total, beats=beats, scenes=scenes, cues=cues, captions=caps, knocks=knocks)
    with open(os.path.join(HERE, "build", EP, "timeline.json"), "w", encoding="utf-8") as f:
        json.dump(tl, f, ensure_ascii=False, indent=1)
    return tl


if __name__ == "__main__":
    tl = build()
    print("total %.2fs" % tl["total"])
    for s in tl["scenes"]:
        print(f"  {s['name']:8s} {s['t0']:6.2f} – {s['t1']:6.2f}  ({s['t1'] - s['t0']:.2f}s)")
    print("cues:", {k: round(v, 2) for k, v in tl["cues"].items() if not k.endswith("_end")})
    for c in tl["captions"]:
        print(f"  {c['t0']:.2f}-{c['t1']:.2f} {c['spk']}: " + " ".join(w["w"] for w in c["words"]))
