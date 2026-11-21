# -*- coding: utf-8 -*-
"""Общий рендер: камера, свет, субтитры, HUD, комната, кадр → ffmpeg. Сцены — в epN_render.py."""
import json
import math
import os
import subprocess
import sys
import time

import skia

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import chars  # noqa: E402
import world  # noqa: E402
from gfx import (BLACK, BOLD, HAND, RUSLAN, XBOLD, C, Style, back_out, circle, clamp, ease_in_out, ease_out,  # noqa: E402
                 ellipse, fill, fillp, font, glow, kf, lerp, lin_grad, line_path, poly, rad_grad, rrect, shape, smooth,
                 stroke, strokep, text, arc_path)
from world import BOLT_Y, DOOR, FLOOR_Y, LAMP  # noqa: E402

W, H, FPS = 1080, 1920, 30
EP = None
TL = BEATS = SCENES = CUES = KNOCKS = CAPS = None
TOTAL = 0.0
ROOM = VIL = None
SCENE_FN = {}
CAP_Y = {}
POST = []   # дополнительные эффекты эпизода поверх кадра: fn(cv, t)


def load(ep):
    """Загружает таймлайн эпизода и общие миры."""
    global EP, TL, BEATS, SCENES, CUES, KNOCKS, CAPS, TOTAL, ROOM, VIL
    EP = ep
    with open(os.path.join(HERE, "build", ep, "timeline.json"), encoding="utf-8") as f:
        TL = json.load(f)
    BEATS, SCENES, CUES = TL["beats"], TL["scenes"], TL["cues"]
    KNOCKS, CAPS, TOTAL = TL["knocks"], TL["captions"], TL["total"]
    ROOM = world.Room()
    VIL = world.Village()


def beat_by_text(prefix):
    for b in BEATS:
        if b["kind"] == "line" and b["text"].replace("*", "").startswith(prefix):
            return b
    raise KeyError(prefix)


def wt(b, k, end=False):
    """Глобальное время начала (или конца) k-го слова реплики."""
    w = b["words"][k]
    return b["t0"] + (w["e"] if end else w["s"])




def scene_at(t):
    for s in SCENES:
        if s["t0"] <= t < s["t1"]:
            return s
    return SCENES[-1]


def beat_at(t):
    cur = BEATS[0]
    for b in BEATS:
        if b["t0"] <= t:
            cur = b
        else:
            break
    return cur


def mouth(t, spks):
    for b in BEATS:
        if b["kind"] == "line" and b["spk"] in spks and b["t0"] <= t < b["t0"] + b["dur"]:
            i = int((t - b["t0"]) * 30)
            env = b["env"]
            if 0 <= i < len(env):
                v = (env[i] + (env[i + 1] if i + 1 < len(env) else env[i])) / 2
                return clamp((v - 0.1) / 0.75)
    return 0.0


def blink(t, seed=0.0, period=3.4):
    ph = (t + seed) % period
    k = ph / 0.16
    return math.sin(math.pi * k) if k < 1 else 0.0


def flicker(t, seed=0.0):
    return 1.0 + 0.05 * math.sin(t * 13 + seed) * math.sin(t * 5.3 + seed * 2) + 0.03 * math.sin(t * 31 + seed)


# ------------------------------------------------------------------ стуки
def shake(t, groups, amp=16.0):
    sx = sy = 0.0
    for k in KNOCKS:
        if k["grp"] not in groups:
            continue
        dt = t - k["t"]
        if 0 <= dt < 0.8:
            a = amp * k["s"] * math.exp(-dt * 8.0)
            sx += a * math.sin(dt * 95 + k["t"] * 3)
            sy += a * 0.6 * math.cos(dt * 83 + k["t"] * 5)
    return sx, sy


def door_kick(t, groups):
    v = 0.0
    for k in KNOCKS:
        if k["grp"] in groups:
            dt = t - k["t"]
            if 0 <= dt < 0.5:
                v += k["s"] * 7.0 * math.exp(-dt * 13) * math.sin(dt * 70)
    return v


def knock_env(t, groups, decay=7.0, big_only=False):
    v = 0.0
    for k in KNOCKS:
        if k["grp"] in groups and (not big_only or k["s"] > 1.5):
            dt = t - k["t"]
            if 0 <= dt < 2.0:
                v = max(v, k["s"] * math.exp(-dt * decay))
    return v


def knocks_done(t, grp):
    return sum(1 for k in KNOCKS if k["grp"] == grp and k["t"] <= t)


def knock_time(grp, n):
    for k in KNOCKS:
        if k["grp"] == grp and k["n"] == n:
            return k["t"]
    return 1e9


# ------------------------------------------------------------------ камера/свет
def cam(cv, cx, cy, z, rot=0.0, ox=0.0, oy=0.0, px=W / 2, py=H / 2):
    cv.translate(px + ox, py + oy)
    cv.scale(z, z)
    if rot:
        cv.rotate(rot)
    cv.translate(-cx, -cy)


def lighting(cv, lights, ambient):
    cv.saveLayer(None, skia.Paint(BlendMode=skia.BlendMode.kMultiply))
    cv.drawColor(C(ambient))
    for (x, y, r, col, a) in lights:
        if a <= 0.002:
            continue
        sh = rad_grad((x, y), r, [(col, min(1.0, a)), (col, min(1.0, a) * 0.55), (col, 0.0)], [0.0, 0.42, 1.0])
        cv.drawCircle(x, y, r, skia.Paint(Shader=sh, BlendMode=skia.BlendMode.kPlus))
    cv.restore()


def vignette(cv, strength=0.6):
    sh = rad_grad((W / 2, H / 2), 1200, [("#000000", 0.0), ("#000000", 0.0), ("#000000", strength)], [0.0, 0.5, 1.0])
    cv.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=sh))


def under_door_light(cv, a, t, feet=True):
    x0, x1 = DOOR[0] + 8, DOOR[2] - 8
    y = FLOOR_Y - 3
    f = flicker(t, 3.0)
    cv.save()
    cv.translate((x0 + x1) / 2, y + 8)
    cv.scale(1.0, 0.28)
    glow(cv, 0, 0, 330, "#ff9c45", 0.55 * a * f)
    cv.restore()
    cv.drawRect(skia.Rect.MakeLTRB(x0, y - 4, x1, y + 5), fillp("#ffc070", 0.95 * a * f))
    if feet:
        for fx in (2192, 2276):
            cv.drawRect(skia.Rect.MakeLTRB(fx, y - 5, fx + 44, y + 6), fillp("#0a0605", 0.95 * a))
            cv.drawPath(poly([(fx, y + 6), (fx + 44, y + 6), (fx + 70 + (fx - 2240) * 0.6, y + 130), (fx - 26 + (fx - 2240) * 0.6, y + 130)]),
                        fillp("#000000", 0.35 * a, blur=6))


def room_view(cv, t, camv, st, lights, ambient, behind=None, fg=None, emis=None, lamp_lit=1.0, under=0.0, feet=True):
    cv.save()
    cam(cv, *camv)
    cv.drawPicture(ROOM.p_back)
    ROOM.outside(cv, st)
    ROOM.glass(cv, st)
    cv.drawPicture(ROOM.p_stove)
    ROOM.gap(cv, st, t)
    cv.drawPicture(ROOM.p_winframe)
    cv.drawPicture(ROOM.p_mull)
    cv.drawPicture(ROOM.p_props)
    ROOM.clock(cv, st, t)
    ROOM.door(cv, st, t)
    if behind:
        behind(cv)
    cv.drawPicture(ROOM.p_table)
    ROOM.lamp(cv, st, t, lamp_lit)
    if fg:
        fg(cv)
    lighting(cv, lights, ambient)
    if lamp_lit > 0.03:
        world.flame(cv, LAMP[0], LAMP[1] - 98, 1.0 * (0.55 + 0.45 * lamp_lit), t)
    if under > 0:
        under_door_light(cv, under, t, feet)
    if emis:
        emis(cv)
    cv.restore()


def put(cv, x, y, s, fn, lw_px=5.0, **kw):
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    Style.lw = lw_px / s
    fn(cv, **kw)
    cv.restore()


def lamp_light(t, a=1.0, r=1350):
    return (LAMP[0], LAMP[1] - 95, r, "#ffdfa8", a * flicker(t))


MOON = (1430, 800, 520, "#8fa3d0", 0.45)


# ------------------------------------------------------------------ текст на экране
def tuk_texts(cv, t, grp, pos):
    for k in KNOCKS:
        if k["grp"] != grp:
            continue
        dt = t - k["t"]
        if 0 <= dt < 0.95:
            x, y, rot = pos[k["n"]]
            big = k["s"] > 1.5
            sc = 1.0 + (0.6 if big else 0.45) * (1 - ease_out(dt / 0.14))
            a = 1.0 if dt < 0.55 else 1 - (dt - 0.55) / 0.4
            f = font(BLACK, 215 if big else 150)
            cv.save()
            cv.translate(x, y)
            cv.rotate(rot)
            cv.scale(sc, sc)
            text(cv, "ТУК" + ("!" if big else ""), 0, 0, f, "#ff2d24" if big else "#ffffff", a, outline="#000000", ow=18, shadow=12)
            cv.restore()


def hud(cv, t, grp, y=255):
    n = knocks_done(t, grp)
    if n == 0:
        return
    a = clamp((t - knock_time(grp, 1)) / 0.2)
    f = font(BLACK, 30)
    text(cv, "СТУК", 540, y - 46, f, "#ffffff", 0.8 * a, outline="#000000", ow=6)
    for i in range(3):
        x = 540 + (i - 1) * 86
        if i < n:
            dt = t - knock_time(grp, i + 1)
            pop = 1 + 0.45 * math.exp(-max(0, dt) * 9)
            col = "#ff2d24" if i == 2 else "#ffffff"
            if i == 2:
                glow(cv, x, y, 70, "#ff2a1a", 0.5 * a)
            cv.drawCircle(x, y, 25 * pop, fillp("#000000", 0.6 * a))
            cv.drawCircle(x, y, 22 * pop, fillp(col, a))
        else:
            cv.drawCircle(x, y, 22, strokep("#ffffff", 4, 0.55 * a))


SPK_COL = {"N": "#ffffff", "G": "#ffd23f", "F": "#ffd23f", "F2": "#ffd23f", "W": "#d2cbf5", "S": "#cfe8a0"}


def draw_caption(cv, c, t):
    y = CAP_Y.get(c["scene"], 1320)
    k = clamp((t - c["t0"]) / 0.14)
    sc = 1.17 - 0.17 * back_out(k)
    a = clamp((t - c["t0"]) / 0.05) * clamp((c["t1"] - t) / 0.06)
    if a <= 0:
        return
    size = 80
    f = font(BLACK, size, skew=-0.16 if c["spk"] == "W" else 0.0)
    base = SPK_COL[c["spk"]]
    words = [(w["w"].upper(), "#ff3b30" if w["red"] else base) for w in c["words"]]
    sp = f.measureText(" ")
    widths = [f.measureText(w) for w, _ in words]
    total = sum(widths) + sp * (len(words) - 1)
    lines = [list(range(len(words)))]
    if total > 900 and len(words) > 1:
        best, bi = 1e9, 1
        for i in range(1, len(words)):
            l1 = sum(widths[:i]) + sp * (i - 1)
            l2 = sum(widths[i:]) + sp * (len(words) - i - 1)
            if max(l1, l2) < best:
                best, bi = max(l1, l2), i
        lines = [list(range(bi)), list(range(bi, len(words)))]
    lh = size * 1.1
    cv.save()
    cv.translate(540, y)
    cv.scale(sc, sc)
    outline = skia.Paint(AntiAlias=True, Color=C("#000000", a), Style=skia.Paint.kStroke_Style, StrokeWidth=15,
                         StrokeJoin=skia.Paint.kRound_Join)
    shadow = skia.Paint(AntiAlias=True, Color=C("#000000", 0.55 * a), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 10))
    layout = []
    for li, idxs in enumerate(lines):
        lw_ = sum(widths[i] for i in idxs) + sp * (len(idxs) - 1)
        x = -lw_ / 2
        yy = li * lh - (len(lines) - 1) * lh / 2 + size * 0.36
        for i in idxs:
            layout.append((words[i][0], x, yy, words[i][1]))
            x += widths[i] + sp
    for s_, x, yy, _ in layout:
        cv.drawString(s_, x + 3, yy + 7, f, shadow)
    for s_, x, yy, _ in layout:
        cv.drawString(s_, x, yy, f, outline)
    for s_, x, yy, col in layout:
        cv.drawString(s_, x, yy, f, skia.Paint(AntiAlias=True, Color=C(col, a)))
    cv.restore()


def captions(cv, t):
    for c in CAPS:
        if c["t0"] <= t < c["t1"]:
            draw_caption(cv, c, t)


def frame(cv, t):
    cv.clear(C("#000000"))
    s = scene_at(t)
    SCENE_FN[s["name"]](cv, t, s)
    # вспышка на большом стуке
    for k in KNOCKS:
        if k["s"] > 1.5:
            dt = t - k["t"]
            if 0 <= dt < 0.45:
                col = "#ffffff" if dt < 0.05 else "#c4140e"
                cv.drawRect(skia.Rect.MakeWH(W, H), fillp(col, 0.6 * math.exp(-dt * 9)))
    for fn in POST:
        fn(cv, t)
    captions(cv, t)


def render_range(out, f0, f1):
    surf = skia.Surface(W, H)
    cv = surf.getCanvas()
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-vf", "noise=c0s=8:c0f=t+u:c1s=3:c1f=t+u:c2s=3:c2f=t+u,format=yuv420p",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-threads", "1", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for i in range(f0, f1):
        frame(cv, i / FPS)
        p.stdin.write(surf.makeImageSnapshot().toarray().tobytes())
        if (i - f0) % 150 == 0:
            print(f"[{out}] frame {i}/{f1} {time.time() - t0:.1f}s", flush=True)
    p.stdin.close()
    p.wait()


def stills(times, prefix):
    surf = skia.Surface(W, H)
    cv = surf.getCanvas()
    for t in times:
        frame(cv, t)
        surf.makeImageSnapshot().save(f"{prefix}_{t:06.2f}.png", skia.kPNG)


def main(argv):
    if argv[1] == "stills":
        stills([float(x) for x in argv[3].split(",")], argv[2])
    elif argv[1] == "seg":
        i, n = int(argv[2]), int(argv[3])
        nf = int(math.ceil(TOTAL * FPS))
        f0 = nf * i // n
        f1 = nf * (i + 1) // n
        render_range(os.path.join(HERE, "build", EP, f"seg{i}.mp4"), f0, f1)
