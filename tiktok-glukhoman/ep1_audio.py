# -*- coding: utf-8 -*-
"""Эпизод 1 «Третий стук»: звуковой дизайн и сведение."""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dsp  # noqa: E402,F401
from sfx import *  # noqa: E402,F401,F403
from sfx import SR  # noqa: E402

EP = "ep1"


def build():
    tl = load_timeline(EP)
    total = tl["total"]
    cues = tl["cues"]
    sc = {s["name"]: s for s in tl["scenes"]}
    mx = Mix(total)

    # ---- голос
    add_voices(mx, tl, EP)

    # ---- стуки
    for k, kn in enumerate(tl["knocks"]):
        big = kn["s"] > 1.5
        y = knock(min(1.0, 0.75 * kn["s"]), seed=40 + k, dull=0.0)
        y = dsp.reverb(y, rt60=0.9 if not big else 1.6, wet=0.22 if not big else 0.3, seed=41)
        gain = -4.0 + (3.0 if big else 0.0) + (1.5 if kn["grp"] == "end" else 0)
        mx.add("sfx", kn["t"], y, gain, pan=0.15)
        if kn["grp"] in ("door", "end"):
            mx.add("sfx", kn["t"] + 0.02, rattle(4 if not big else 9, seed=50 + k, spread=0.15 if not big else 0.3), -14 + (6 if big else 0), pan=0.2)
        if big:
            mx.add("sfx", kn["t"], sub_boom(2.0, 70, 26), -3.0)
            mx.add("music", kn["t"], stinger(2.4, seed=5, base=932), -9.0)
        if kn["grp"] == "title" and kn["n"] == 3:
            mx.add("sfx", kn["t"], sub_boom(1.4, 60, 30), -8.0)

    # ---- засов
    if "bolt_sfx" in cues:
        y = dsp.reverb(bolt_slide(0.75), rt60=0.7, wet=0.15, seed=42)
        mx.add("sfx", cues["bolt_sfx"], y, -7.0, pan=0.1)
    # нарастание к третьему стуку
    if "knock3" in cues and "bolt" in cues:
        d = cues["knock3"] + 0.1 - cues["bolt"]
        mx.add("music", cues["bolt"], riser(d), -10.0)

    # ---- дверь закрывается (бабушка ушла)
    s = sc["leave"]
    mx.add("sfx", s["t0"] + 0.05, dsp.reverb(creak(1.1, seed=12, f_start=35, f_end=70), 0.8, 0.2), -12.0, pan=0.3)
    if "door_close" in cues:
        tc = cues["door_close"]
        mx.add("sfx", tc, dsp.reverb(creak(0.6, seed=14, f_start=80, f_end=40), 0.8, 0.2), -12.0, pan=0.3)
        y = dsp.reverb(knock(1.0, seed=60, dull=0.3), 1.2, 0.25, seed=43)
        mx.add("sfx", tc + 0.55, y, -3.0, pan=0.3)
        mx.add("sfx", tc + 0.6, rattle(5, seed=61, spread=0.2), -14, pan=0.3)
        mx.add("sfx", tc + 0.55, sub_boom(0.9, 55, 30), -12)

    # ---- часы-ходики: тикают в правилах (тихо), громко на крупном плане, тихо в начале сцены двери
    t_clock0 = sc["rules"]["t0"]
    t_clock1 = tl["knocks"][3]["t"] if len(tl["knocks"]) > 3 else sc["door"]["t0"]  # смолкают на первом стуке в дверь
    tt, k = t_clock0, 0
    while tt < t_clock1:
        loud = sc["clock"]["t0"] - 0.2 <= tt < sc["clock"]["t1"]
        g = -13 if loud else -29
        if sc["leave"]["t0"] <= tt < sc["clock"]["t0"] - 0.2:
            g = -27
        mx.add("sfx", tt, dsp.reverb(tick(k % 2 == 0, seed=k), 0.5, 0.15, seed=44), g, pan=-0.3 if not loud else 0.0)
        tt += 0.5
        k += 1

    # ---- эмбиент
    # сверчки: деревня (громко), дом (глухо), смолкают перед первым стуком
    t_quiet = tl["knocks"][3]["t"] - 1.2 if len(tl["knocks"]) > 3 else sc["door"]["t0"]
    cr = crickets(t_quiet - sc["village"]["t0"] + 1.0, seed=4)
    t0 = sc["village"]["t0"]
    seg_out = int((sc["rules"]["t0"] - t0) * SR)
    cr_in = cr.copy()
    cr_in[:seg_out] *= 1.0
    gain_curve = np.ones(len(cr))
    gain_curve[seg_out:] = 0.22
    # дверь открыта в начале сцены leave — сверчки громче, после закрытия — тише
    lo = int((sc["leave"]["t0"] - t0) * SR)
    hi = int((cues.get("door_close", sc["leave"]["t1"]) + 0.55 - t0) * SR)
    gain_curve[lo:hi] = 0.6
    gain_curve = dsp.lp(gain_curve, 3)  # сгладить
    mx.add("amb", t0, cr * gain_curve[:, None], -12.0, fade_in=0.6, fade_out=1.0)
    # ветер — на улице и тихо фоном везде
    mx.add("amb", sc["village"]["t0"], wind(sc["village"]["t1"] - sc["village"]["t0"] + 0.5, seed=6), -20, fade_in=0.4, fade_out=0.5)
    mx.add("amb", 0, wind(total + 1, seed=16), -33, fade_in=1.0, fade_out=2.0)
    mx.add("amb", sc["rules"]["t0"], roomtone(total - sc["rules"]["t0"], seed=8), -40, fade_in=0.5, fade_out=1.0)

    # ---- музыка
    # титр: низкий гул
    mx.add("music", 0, drone(sc["village"]["t0"] + 1.0, notes=(38, 45), cutoff=(250, 500), seed=2), -17, fade_in=0.05, fade_out=1.0)
    # шкатулка: деревня + правила
    mb_t0 = sc["village"]["t0"] - 0.3
    mb_t1 = sc["leave"]["t1"]
    mx.add("music", mb_t0, music_box(mb_t1 - mb_t0, beat=0.5, seed=1, detune_drift=0.6), -16, fade_in=0.4, fade_out=2.5)
    mx.add("music", sc["village"]["t0"], drone(mb_t1 - sc["village"]["t0"], notes=(38, 50), cutoff=(220, 380), seed=3), -24, fade_in=1.5, fade_out=2.0)
    # напряжение: часы → дверь → лицо → окно → печь
    t_ten = sc["clock"]["t0"]
    t_ten1 = sc["split"]["t1"]
    mx.add("music", t_ten, drone(t_ten1 - t_ten, notes=(38, 45), cutoff=(180, 650), seed=5, dissonance=(51, 0.6)), -19, fade_in=1.5, fade_out=0.8)
    # высокий тревожный тон в окне
    w = sc["window"]
    mx.add("music", w["t0"], stinger(w["t1"] - w["t0"] + 1.0, seed=8, base=1244) * 0.6, -21, fade_in=1.5, fade_out=1.0)
    sm = [b for b in tl["beats"] if b.get("cue") == "smile"]
    if sm:
        t_st = sm[0]["t0"] + sm[0]["words"][3]["s"]
        mx.add("music", t_st, stinger(2.2, seed=9, base=740), -11)
        mx.add("sfx", t_st, sub_boom(1.6, 64, 28), -7)
    # сердцебиение: от второго стука до конца печи
    hb0 = tl["knocks"][4]["t"] + 0.6 if len(tl["knocks"]) > 4 else sc["door"]["t0"]
    hb1 = sc["stove"]["t1"]
    tt = hb0
    while tt < hb1:
        prog = (tt - hb0) / max(1e-6, hb1 - hb0)
        bpm = 72 + 40 * prog
        mx.add("sfx", tt, heartbeat_one(), -15 + 3 * prog)
        tt += 60.0 / bpm
    # печь: шёпот-подложка
    st = sc["stove"]
    mx.add("amb", st["t0"], dsp.hp(wind(st["t1"] - st["t0"], seed=26), 1500), -30, fade_in=1.0, fade_out=0.5)
    # развилка/выбор: пульс + шкатулка медленнее и ниже
    ch = sc["choice"]
    mx.add("music", sc["split"]["t0"], music_box(ch["t1"] - sc["split"]["t0"], beat=0.62, seed=7, detune_drift=1.5), -19, fade_in=0.3, fade_out=0.3)
    mx.add("music", sc["split"]["t0"], drone(ch["t1"] - sc["split"]["t0"] + 0.3, notes=(38, 44), cutoff=(200, 420), seed=9), -20, fade_in=0.5, fade_out=0.2)
    # финал: тишина → удар на логотипе
    en = sc["end"]
    mx.add("sfx", en["t0"], sub_boom(2.0, 58, 24), -4)
    mx.add("music", en["t0"], stinger(1.8, seed=12, base=622), -13)

    # переходы между сценами — лёгкий свист
    for s in tl["scenes"][1:]:
        if s["name"] in ("village", "rules", "leave", "window", "stove", "split", "choice"):
            mx.add("sfx", s["t0"] - 0.25, whoosh(0.5, seed=int(s["t0"] * 10)), -24)

    finish(mx, total, EP)


if __name__ == "__main__":
    build()
