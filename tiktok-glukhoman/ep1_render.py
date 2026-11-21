# -*- coding: utf-8 -*-
"""Эпизод 1 «Третий стук»: сцены."""
import math
import os
import sys

import skia

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402

common.load("ep1")
from common import *  # noqa: E402,F401,F403
import chars  # noqa: E402
import world  # noqa: E402
from gfx import (BLACK, BOLD, HAND, RUSLAN, C, Style, back_out, circle, clamp, ease_in_out, ease_out,  # noqa: E402,F401
                 ellipse, fill, fillp, font, glow, kf, lerp, lin_grad, poly, rrect, shape, smooth, stroke, strokep, text)
from world import BOLT_Y, DOOR, LAMP  # noqa: E402,F401

B_SVYAZ = beat_by_text("В глухую")

B_GLYANUL = beat_by_text("Я глянул")

B_ULYB = beat_by_text("Она улыбалась")

B_PLUS = beat_by_text("А на улице")
B_F2 = beat_by_text("Ну что же")

B_TRETIY = beat_by_text("Третий")

common.CAP_Y.update({"title": 1430, "village": 1215, "rules": 1350, "leave": 1270, "clock": 1520, "door": 1330,
         "face": 1350, "window": 1420, "stove": 1360, "split": 1012, "choice": 1470, "end": 1500})


# ================================================================== СЦЕНЫ
def sc_title(cv, t, s):
    lt = t - s["t0"]
    d = s["t1"] - s["t0"]
    sx, sy = shake(t, ("title",), 12)
    z = 1.3 + 0.08 * ease_in_out(lt / d)
    st = dict(bolt=0.0, door_shake=door_kick(t, ("title",)), bolt_rattle=2 * math.sin(t * 80) * knock_env(t, ("title",), 10))
    lights = [(2250, 1430, 360, "#ffae55", 0.95 * flicker(t, 2)), (1500, 800, 1100, "#7f93c4", 0.25)]
    room_view(cv, t, (2250, 930, z, 0, sx, sy), st, lights, "#141826", lamp_lit=0.0, under=1.0)
    # затемнение под текст
    sh = lin_grad((0, 0), (0, H), [("#000000", 0.78), ("#000000", 0.35), ("#000000", 0.25), ("#000000", 0.7)], [0, 0.42, 0.62, 1])
    cv.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=sh))
    vignette(cv, 0.6)
    # логотип и «часть 1»
    text(cv, "ГЛУХОМАНЬ", 540, 222, font(RUSLAN, 78), "#e9e0c9", outline="#000000", ow=8, shadow=8)
    cv.drawLine(400, 250, 680, 250, strokep("#d8322a", 4))
    pill = rrect(540 - 100, 282, 200, 54, 27)
    cv.drawPath(pill, fillp("#000000", 0.55))
    cv.drawPath(pill, strokep("#e3342b", 4))
    text(cv, "ЧАСТЬ 1", 540, 320, font(BLACK, 30), "#ffffff")
    # заголовок
    pulse = knock_env(t, ("title",), 9.0)
    text(cv, "ТРЕТИЙ", 540, 655, font(BLACK, 132), "#ffffff", outline="#000000", ow=16, shadow=14)
    cv.save()
    cv.translate(540, 920)
    cv.scale(1 + 0.07 * pulse, 1 + 0.07 * pulse)
    cv.rotate(1.5 * math.sin(t * 40) * pulse)
    glow(cv, 0, -100, 420, "#ff1a10", 0.22 + 0.25 * pulse, blend=skia.BlendMode.kSrcOver)
    text(cv, "СТУК", 0, 0, font(RUSLAN, 330), "#e3342b", outline="#140707", ow=20, shadow=18)
    cv.restore()
    # три кружка-стука
    n = knocks_done(t, "title")
    for i in range(3):
        x = 540 + (i - 1) * 100
        y = 1080
        if i < n:
            dt = t - knock_time("title", i + 1)
            pop = 1 + 0.5 * math.exp(-dt * 9)
            col = "#ff2d24" if i == 2 else "#ffffff"
            if i == 2:
                glow(cv, x, y, 80, "#ff2a1a", 0.5)
            cv.drawCircle(x, y, 29 * pop, fillp("#000000", 0.7))
            cv.drawCircle(x, y, 25 * pop, fillp(col))
        else:
            cv.drawCircle(x, y, 25, strokep("#ffffff", 5, 0.6))


def sc_village(cv, t, s):
    lt = t - s["t0"]
    d = s["t1"] - s["t0"]
    z = 1.0 + 0.07 * ease_in_out(lt / d)
    cv.save()
    cam(cv, 540, 1150, z)
    VIL.draw(cv, t, {"walk": lt / d})
    cv.restore()
    vignette(cv, 0.55)
    tp = wt(B_SVYAZ, 3) - 0.05
    if t >= tp:
        k = clamp((t - tp) / 0.3)
        sc = 0.55 + 0.45 * back_out(k)
        cv.save()
        cv.translate(540, 585)
        cv.rotate(-3 + 2 * math.sin((t - tp) * 30) * math.exp(-(t - tp) * 6))
        cv.scale(sc, sc)
        card = rrect(-220, -112, 440, 224, 36)
        cv.drawPath(card, fillp("#000000", 0.5, blur=18))
        cv.drawPath(card, fillp("#0f1318", 0.94))
        cv.drawPath(card, strokep("#3a414a", 4))
        # значок сети с крестом
        for i in range(4):
            h_ = 14 + i * 14
            cv.drawRect(skia.Rect.MakeXYWH(-180 + i * 22, 28 - h_, 15, h_), fillp("#5b636e"))
        cv.drawLine(-186, -36, -100, 34, strokep("#ff3b30", 9))
        cv.drawLine(-186, 34, -100, -36, strokep("#ff3b30", 9))
        text(cv, "НЕТ СЕТИ", 50, 16, font(BLACK, 58), "#ffffff", align="center")
        text(cv, "только экстренные вызовы", 50, 62, font(BOLD, 24), "#9aa3ad", align="center")
        cv.restore()


def rules_card(cv, t):
    r0 = CUES["rule0"]
    if t < r0 - 0.35:
        return
    k = ease_out((t - (r0 - 0.35)) / 0.45)
    cv.save()
    cv.translate(540, 470 - 560 * (1 - k))
    cv.rotate(-2.2)
    pts = [(-430, -255), (-150, -262), (140, -252), (430, -258), (436, -60), (428, 160), (433, 258), (120, 252),
           (-160, 262), (-432, 255), (-438, 40)]
    paper = poly(pts)
    cv.drawPath(paper, fillp("#000000", 0.45, blur=20))
    cv.drawPath(paper, fillp("#eee3c6"))
    cv.save()
    cv.clipPath(paper, skia.ClipOp.kIntersect, True)
    for yy in range(-190, 250, 74):
        cv.drawLine(-440, yy + 48, 440, yy + 48, strokep("#a9b9cf", 2, 0.6))
    cv.drawLine(-350, -260, -350, 260, strokep("#d9837a", 2, 0.6))
    cv.restore()
    cv.drawPath(paper, strokep("#8d7b5c", 3))
    cv.drawCircle(0, -232, 11, fillp("#2a2826"))
    cv.drawCircle(-3, -235, 4, fillp("#8a8680"))
    ink, red = "#29231e", "#c4231b"
    f = font(HAND, 60)
    rows = [
        (CUES["rule0"], None, "Ночью стучат — считай!", ink),
        (CUES["rule1"], 2, "— свои, открывай", ink),
        (CUES["rule2"], 3, "— НЕ ПОДХОДИ!", red),
        (CUES["rule3"], "eye", "— в окно не смотри", ink),
    ]
    for i, (tc, icon, s_, col) in enumerate(rows):
        if t < tc:
            continue
        y = -150 + i * 112
        rev = clamp((t - tc) / 0.7)
        cv.save()
        cv.clipRect(skia.Rect.MakeLTRB(-440, y - 80, -440 + 900 * rev, y + 40), True)
        x = -390
        if icon in (2, 3):
            for j in range(icon):
                cx = x + 26 + j * 52
                cv.drawCircle(cx, y - 20, 17, fillp(col))
                for a_ in range(0, 360, 60):
                    ar = math.radians(a_ + 30)
                    cv.drawLine(cx + 23 * math.cos(ar), y - 20 + 23 * math.sin(ar), cx + 31 * math.cos(ar), y - 20 + 31 * math.sin(ar), strokep(col, 4))
            x += icon * 52 + 18
        elif icon == "eye":
            cx = x + 50
            eye = smooth([(cx - 42, y - 20), (cx, y - 46), (cx + 42, y - 20), (cx, y + 6)], t=0.6)
            cv.drawPath(eye, strokep(ink, 5))
            cv.drawCircle(cx, y - 20, 11, fillp(ink))
            cv.drawLine(cx - 40, y - 52, cx + 40, y + 12, strokep(red, 7))
            cv.drawLine(cx - 40, y + 12, cx + 40, y - 52, strokep(red, 7))
            x += 118
        text(cv, s_, x, y, f, col, align="left")
        if col == red:
            w_ = f.measureText(s_)
            cv.drawPath(smooth([(x, y + 14), (x + w_ * 0.5, y + 20), (x + w_, y + 12)], close=False), strokep(red, 5))
        cv.restore()
    cv.restore()


def sc_rules(cv, t, s):
    r0 = CUES["rule0"]
    cx = kf(t, [(s["t0"], 1440.0), (r0, 1445.0), (r0 + 1.4, 1490.0), (s["t1"], 1500.0)])
    cy = kf(t, [(s["t0"], 1090.0), (r0, 1080.0), (r0 + 1.4, 1065.0), (s["t1"], 1060.0)])
    z = kf(t, [(s["t0"], 1.0), (r0, 1.03), (r0 + 1.4, 1.09), (s["t1"], 1.12)])
    mG = mouth(t, {"G"})
    after = t >= r0 - 0.4

    def behind(c):
        put(c, 1185, 1470, 2.8, chars.boy_front, look=0.55, blink=blink(t, 0.7),
            brows="worried" if t >= CUES["rule2"] else "calm", pupil=(0.6, 0.0))
        put(c, 1690, 1500, 3.0, chars.granny, arms="finger" if after else "down", eyes="stern" if after else "kind",
            look=-0.45, mouth=mG, t=t, blink=blink(t, 1.9, 4.1))

    lights = [lamp_light(t, 1.0), MOON]
    room_view(cv, t, (cx, cy, z), {}, lights, "#2a2f45", behind=behind, lamp_lit=1.0)
    vignette(cv, 0.55)
    rules_card(cv, t)


def sc_leave(cv, t, s):
    lt = t - s["t0"]
    d = s["t1"] - s["t0"]
    tc = CUES["door_close"]
    open_k = ease_out(lt / 0.9)
    if t >= tc:
        open_k = min(open_k, 1 - ease_in_out((t - tc - 0.05) / 0.5))
    away = clamp((t - tc) / 0.45)
    lant = (2170 + 54 * 3.0, 1425 - 56 * 3.0)

    def doorway(c):
        if away >= 1:
            return
        c.saveLayerAlpha(None, int(255 * (1 - away)))
        put(c, 2170 + 30 * away, 1425 - 25 * away, 3.0 * (1 - 0.18 * away), chars.granny, arms="lantern",
            eyes="kind", look=-0.35, mouth=mouth(t, {"G"}), t=t, blink=blink(t, 0.4), lit_lantern=True)
        c.restore()

    def fg(c):
        put(c, 1870, 2140, 4.6, chars.boy_back, t=t, look=0.4)

    def emis(c):
        if away < 1 and open_k > 0.05:
            glow(c, lant[0], lant[1], 150, "#ffb860", 0.55 * (1 - away) * flicker(t, 5))

    st = dict(door_open=open_k, doorway=doorway)
    lights = [lamp_light(t, 0.75), (lant[0], lant[1], 900, "#ffc070", 0.9 * (1 - away) * open_k * flicker(t, 5)),
              (2250, 950, 520, "#7086bb", 0.35 * open_k), MOON]
    sx, sy = shake(t, ("none",), 0)
    if t >= tc + 0.5:
        dt = t - tc - 0.55
        if 0 <= dt < 0.6:
            sx = 14 * math.exp(-dt * 9) * math.sin(dt * 90)
    z = 1.05 + 0.05 * ease_in_out(lt / d)
    room_view(cv, t, (2200, 1000, z, 0, sx, sy), st, lights, "#22283a", fg=fg, emis=emis, lamp_lit=0.75)
    vignette(cv, 0.6)


def sc_clock(cv, t, s):
    lt = t - s["t0"]
    d = s["t1"] - s["t0"]
    z = 2.55 + 0.4 * ease_in_out(lt / d)
    lights = [lamp_light(t, 0.6, 1500), MOON]
    room_view(cv, t, (1872, 790, z), {"time": (23, 58)}, lights, "#1d2233", lamp_lit=0.55)
    vignette(cv, 0.65)


def bolt_amount(t):
    tb = CUES["bolt_sfx"]
    return ease_in_out((t - tb - 0.05) / 0.55) if t >= tb else 0.0


def door_state(t, frost=0.0):
    return dict(bolt=bolt_amount(t), door_shake=door_kick(t, ("door",)),
                bolt_rattle=3 * math.sin(t * 85) * knock_env(t, ("door",), 10), door_frost=frost)


TUK_POS = {1: (310, 600, -9), 2: (770, 760, 8), 3: (540, 560, -4)}


def reach_arm(c, hx, hy):
    """Рука в полосатом рукаве, тянущаяся к засову (мировые координаты)."""
    Style.lw = 5.0
    sx0, sy0 = hx - 360, hy + 470
    ex, ey = hx - 30, hy + 34
    dx, dy = ex - sx0, ey - sy0
    ln = math.hypot(dx, dy)
    ux, uy = dx / ln, dy / ln
    nx, ny = -uy, ux
    w = 34
    sleeve = poly([(sx0 + nx * w, sy0 + ny * w), (ex + nx * w * 0.9, ey + ny * w * 0.9),
                   (ex - nx * w * 0.9, ey - ny * w * 0.9), (sx0 - nx * w, sy0 - ny * w)])
    c.drawPath(sleeve, fillp(chars.SW_A))
    c.save()
    c.clipPath(sleeve, skia.ClipOp.kIntersect, True)
    for k in range(1, 12):
        px, py = sx0 + ux * ln * k / 11, sy0 + uy * ln * k / 11
        c.drawLine(px + nx * 60, py + ny * 60, px - nx * 60, py - ny * 60, strokep(chars.SW_B, 13, cap="butt"))
    c.restore()
    stroke(c, sleeve, "#1c1512", 5)
    # манжета
    cuff = poly([(ex + nx * w, ey + ny * w), (ex - ux * 26 + nx * w, ey - uy * 26 + ny * w),
                 (ex - ux * 26 - nx * w, ey - uy * 26 - ny * w), (ex - nx * w, ey - ny * w)])
    shape(c, cuff, chars.SW_B)
    # ладонь и пальцы, обхватившие брус
    shape(c, ellipse(hx - 8, hy + 18, 30, 26), chars.SKIN)
    for k in range(4):
        fx = hx - 26 + k * 15
        shape(c, rrect(fx, hy - 22, 13, 34, 6.5), chars.SKIN, lw=4)
    shape(c, rrect(hx - 44, hy + 6, 26, 14, 7), chars.SKIN, lw=4)


def sc_door(cv, t, s):
    lt = t - s["t0"]
    d = s["t1"] - s["t0"]
    under = clamp((t - (knock_time("door", 1) - 0.6)) / 0.3)
    st = door_state(t)
    lights = [lamp_light(t, 0.45, 1600), MOON, (2250, 1440, 330, "#ffae55", 0.9 * under * flicker(t, 3))]
    if CUES["bolt"] <= t < CUES["knock3"]:
        z = 2.45 + 0.1 * clamp((t - CUES["bolt"]) / 2.0)
        bx = 2004 + 112 * st["bolt"]

        def hand(c):
            reach_arm(c, bx + 2, BOLT_Y + 16)

        room_view(cv, t, (2160, 975, z), st, lights, "#1b1f2f", fg=hand, lamp_lit=0.45, under=under)
    else:
        punch = 0.12 * knock_env(t, ("door",), 6.0, big_only=True) / 1.9
        z = 1.1 + 0.1 * ease_in_out(lt / d) + punch
        sx, sy = shake(t, ("door",), 18)
        trem = clamp((t - CUES["knock3"]) / 0.3) if t >= CUES["knock3"] else 0.0

        def fg(c):
            put(c, 1900 + 4 * trem * math.sin(t * 50), 2160, 4.8, chars.boy_back, t=t)

        room_view(cv, t, (2240, 1000, z, 0, sx, sy), st, lights, "#1b1f2f", fg=fg, lamp_lit=0.45, under=under)
    vignette(cv, 0.62)
    tuk_texts(cv, t, "door", TUK_POS)
    hud(cv, t, "door")


def sc_face(cv, t, s):
    b = beat_at(t)
    if b["i"] <= B_F2["i"]:
        # крупный план мальчика
        lt = t - s["t0"]
        cv.saveLayer(None, skia.Paint(ImageFilter=skia.ImageFilters.Blur(16, 16)))
        lights = [lamp_light(t, 0.4, 1600), MOON, (2250, 1440, 330, "#ffae55", 0.9)]
        room_view(cv, t, (2240, 980, 1.15), door_state(t), lights, "#1b1f2f", lamp_lit=0.4, under=1.0)
        cv.restore()
        cv.drawRect(skia.Rect.MakeWH(W, H), fillp("#000000", 0.35))
        S = 9.0 + 0.8 * ease_in_out(lt / 4.5)
        sweat = clamp(lt / 2.5)
        cv.save()
        cv.translate(560 + 4 * math.sin(t * 1.3), 830 + 154 * S)
        cv.scale(S, S)
        Style.lw = 6.5 / S
        chars.boy_front(cv, eyes="scared", brows="high", mouth=0.25 + 0.1 * math.sin(t * 9), arms="hug", t=t,
                        sweat=sweat, pupil=(0.45, 0.05), tremble=1.0)
        cv.restore()
        # холодный свет справа, тёплый снизу
        cv.saveLayer(None, skia.Paint(BlendMode=skia.BlendMode.kMultiply))
        sh = lin_grad((0, 0), (W, 0), ["#39405e", "#8a95c4", "#d9e0ff"], [0, 0.55, 1])
        cv.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=sh))
        cv.restore()
        glow(cv, 760, 1900, 700, "#ff9a40", 0.18)
    elif b["i"] == B_PLUS["i"]:
        lt = t - B_PLUS["t0"]
        fr = 0.1 + 0.35 * ease_in_out(lt / 1.8)
        z = 3.0 + 0.4 * ease_in_out(lt / 2.0)
        lights = [lamp_light(t, 0.3, 1500), (1470, 860, 700, "#b3c2e6", 1.0)]
        room_view(cv, t, (1478, 905, z), {"frost": fr, "thermo": 30}, lights, "#1b1f2f", lamp_lit=0.3)
    else:
        t24 = beat_at(t)
        b24 = BEATS[B_PLUS["i"] + 1]
        lt = t - b24["t0"]
        fr = 0.05 + 0.45 * ease_in_out(lt / 4.5)
        z = 1.3 + 0.35 * ease_in_out(lt / 5.0)
        lights = [lamp_light(t, 0.4, 1600), MOON, (2250, 1440, 330, "#ffae55", 0.9 * flicker(t, 3))]
        room_view(cv, t, (2250, 1010, z), door_state(t, fr), lights, "#1a1e2e", lamp_lit=0.4, under=1.0)
    vignette(cv, 0.62)
    hud(cv, t, "door")


def creature_fn(t, rise, smile, glint, slide=0.0, x=1430, y=845, s=2.3):
    def fn(c):
        c.save()
        c.translate(x, y + 330 * (1 - rise))
        c.scale(s, s)
        Style.lw = 4.5 / s
        chars.fake_face(c, smile=smile, t=t, eye_glint=glint, tilt=2.0 * math.sin(t * 0.7))
        c.restore()
        if rise > 0.85:
            for hx in (1320, 1545):
                c.save()
                c.translate(hx, 1010 + 60 * (1 - (rise - 0.85) / 0.15) + 30 * slide)
                c.scale(1.45, 1.45)
                Style.lw = 4.0 / 1.45
                chars.fake_hand(c, t=t, slide=slide)
                c.restore()
    return fn


def sc_window(cv, t, s):
    b26, b27 = B_GLYANUL, B_ULYB
    t_rise = wt(b26, 4) - 0.25
    rise = ease_in_out((t - t_rise) / 1.3)
    s0, s1 = wt(b27, 2), wt(b27, 3, end=True)
    smile = 0.08 + 0.92 * ease_in_out((t - s0) / max(0.3, s1 - s0))
    slide = ease_in_out((t - s1) / 0.8)
    if t < b27["t0"]:
        z = 1.95 + 0.25 * ease_in_out((t - b26["t0"]) / (b27["t0"] - b26["t0"]))
    else:
        z = 2.2 + 0.2 * ease_in_out((t - b27["t0"]) / max(0.1, s0 - b27["t0"])) + 0.55 * ease_out((t - wt(b27, 3)) / 0.35)
    fog = 0.5 + 0.5 * math.sin(t * 1.6)
    st = {"creature": creature_fn(t, rise, smile, rise, slide), "frost": 0.65, "fog": fog * rise}
    stg = wt(b27, 3)
    gx = 0.0
    if 0 <= t - stg < 0.3:
        gx = 18 * math.sin((t - stg) * 120) * (1 - (t - stg) / 0.3)
    lights = [lamp_light(t, 0.3, 1500), (1430, 790, 640, "#a9badf", 0.95)]
    cyw = 870 + 35 * clamp((t - b27["t0"]) / 1.0) if t >= b27["t0"] else 870
    room_view(cv, t, (1430, cyw, z, 0, gx, 0), st, lights, "#191d2c", lamp_lit=0.3)
    vignette(cv, 0.65)
    if 0 <= t - stg < 0.25:
        cv.drawRect(skia.Rect.MakeWH(W, H), fillp("#ffffff", 0.35 * (1 - (t - stg) / 0.25)))
    hud(cv, t, "door")


def eyes_fn(t, open_k, x=928, y=1010, s=2.1):
    def fn(c):
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(world.GAP[0], world.GAP[1], world.GAP[2], world.GAP[3]), True)
        c.translate(x, y)
        c.scale(s, s)
        Style.lw = 3.0 / s
        chars.stove_eyes(c, open_k=open_k, t=t, look=0.3 * math.sin(t * 0.8), finger=0.0)
        c.restore()
    return fn


def stove_open(t):
    te = CUES["eyes"]
    k = ease_out((t - te + 0.05) / 0.35)
    bl = blink(t, -te - 1.4 + 3.4, 3.4) if t > te + 1.0 else 0.0
    return k * (1 - 0.95 * bl)


def sc_stove(cv, t, s):
    lt = t - s["t0"]
    pan = ease_in_out(lt / 0.55)
    te = CUES["eyes"]
    cx = lerp(1430, 930, pan)
    cy = lerp(835, 1000, pan)
    z = lerp(2.0, 1.75, pan) + 0.75 * ease_in_out((t - te) / 4.0)
    sway = 0.5 + 0.5 * clamp((t - te) / 1.0)
    st = {"sway": sway, "frost": 0.65}
    lights = [lamp_light(t, 0.33, 1450), MOON]
    room_view(cv, t, (cx, cy, z), st, lights, "#141725", lamp_lit=0.3, emis=eyes_fn(t, stove_open(t)))
    vignette(cv, 0.7)
    hud(cv, t, "door")


def sc_split(cv, t, s):
    lt = t - s["t0"]
    k = ease_out(lt / 0.3)
    st1 = {"creature": creature_fn(t, 1.0, 1.0, 1.0, 1.0), "frost": 0.65, "fog": 0.4}
    cv.save()
    cv.clipRect(skia.Rect.MakeLTRB(0, 0, W, 952), True)
    room_view(cv, t, (1430, 860, 2.45, 0, -W * (1 - k), 0, W / 2, 476), st1, [lamp_light(t, 0.3, 1500), (1430, 790, 640, "#a9badf", 0.95)],
              "#191d2c", lamp_lit=0.3)
    cv.restore()
    cv.save()
    cv.clipRect(skia.Rect.MakeLTRB(0, 968, W, H), True)
    room_view(cv, t, (928, 1000, 2.55, 0, W * (1 - k), 0, W / 2, 1444), {"sway": 0.6}, [lamp_light(t, 0.33, 1450), MOON],
              "#141725", lamp_lit=0.3, emis=eyes_fn(t, 1.0))
    cv.restore()
    jag = [(0, 960)]
    for i in range(1, 25):
        jag.append((i * 45, 960 + (10 if i % 2 else -10)))
    cv.drawPath(poly(jag, close=False), strokep("#000000", 16))
    cv.drawPath(poly(jag, close=False), strokep("#e9e2d0", 6))
    vignette(cv, 0.55)


def thumb(cv, t, which, box):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    cv.save()
    cv.clipPath(rrect(x0, y0, x1 - x0, y1 - y0, 26), skia.ClipOp.kIntersect, True)
    if which == 1:
        st = {"creature": creature_fn(t, 1.0, 1.0, 1.0, 1.0), "frost": 0.65, "fog": 0.3}
        room_view(cv, t, (1430, 880, 1.25, 0, 0, 0, cx, cy), st, [lamp_light(t, 0.3, 1500), (1430, 790, 640, "#a9badf", 0.95)],
                  "#191d2c", lamp_lit=0.3)
    else:
        room_view(cv, t, (930, 1000, 1.45, 0, 0, 0, cx, cy), {"sway": 0.6}, [lamp_light(t, 0.33, 1450), MOON],
                  "#141725", lamp_lit=0.3, emis=eyes_fn(t, stove_open(t + 5)))
    cv.restore()
    cv.drawPath(rrect(x0, y0, x1 - x0, y1 - y0, 26), strokep("#e9e2d0", 5))


def sc_choice(cv, t, s):
    lt = t - s["t0"]
    cv.drawColor(C("#0c0e15"))
    cv.saveLayer(None, skia.Paint(ImageFilter=skia.ImageFilters.Blur(20, 20)))
    room_view(cv, t, (2240, 1000, 1.0), door_state(t), [lamp_light(t, 0.35, 1600), MOON], "#161a28", lamp_lit=0.35, under=1.0)
    cv.restore()
    cv.drawRect(skia.Rect.MakeWH(W, H), fillp("#06070b", 0.62))
    sx, sy = shake(t, ("end",), 14)
    cv.save()
    cv.translate(sx, sy)
    k0 = ease_out(lt / 0.35)
    text(cv, "КОМУ ВЕРИТЬ?", 540, 330 - 40 * (1 - k0), font(BLACK, 92), "#ffffff", k0, outline="#000000", ow=12, shadow=12)
    boxes = [(70, 400, 515, 900), (565, 400, 1010, 900)]
    labels = [("ТОЙ, ЧТО", "ЗА ДВЕРЬЮ"), ("ТОЙ, ЧТО", "ЗА ПЕЧКОЙ")]
    for i, box in enumerate(boxes):
        ki = back_out(clamp((lt - 0.1 - i * 0.12) / 0.35))
        if ki <= 0:
            continue
        cxb = (box[0] + box[2]) / 2
        cv.save()
        cv.translate(cxb, 650)
        cv.scale(ki, ki)
        cv.translate(-cxb, -650)
        cv.drawPath(rrect(box[0] - 8, box[1] - 8, box[2] - box[0] + 16, box[3] - box[1] + 150, 34), fillp("#000000", 0.55, blur=14))
        cv.drawPath(rrect(box[0] - 8, box[1] - 8, box[2] - box[0] + 16, box[3] - box[1] + 150, 34), fillp("#151923"))
        thumb(cv, t, i + 1, box)
        bc = "#ffd23f" if i == 0 else "#d2cbf5"
        cv.drawCircle(box[0] + 52, box[1] + 52, 40, fillp("#000000", 0.7))
        cv.drawCircle(box[0] + 52, box[1] + 52, 34, fillp(bc))
        text(cv, str(i + 1), box[0] + 52, box[1] + 70, font(BLACK, 48), "#111111")
        text(cv, labels[i][0], cxb, box[3] + 62, font(BLACK, 40), "#ffffff")
        text(cv, labels[i][1], cxb, box[3] + 110, font(BLACK, 46), bc)
        cv.restore()
    kb = back_out(clamp((lt - 0.5) / 0.35))
    if kb > 0:
        cv.save()
        cv.translate(540, 1150)
        cv.scale(kb * (1 + 0.04 * math.sin(t * 6)), kb * (1 + 0.04 * math.sin(t * 6)))
        cv.drawPath(rrect(-420, -52, 840, 104, 52), fillp("#000000", 0.5, blur=12))
        cv.drawPath(rrect(-420, -52, 840, 104, 52), fillp("#e3342b"))
        text(cv, "ПИШИ 1 ИЛИ 2 В КОММЕНТАХ", 0, 15, font(BLACK, 42), "#ffffff")
        cv.restore()
        text(cv, "часть 2 — по вашему выбору", 540, 1262, font(BOLD, 36), "#b9b2c9", kb)
    cv.restore()
    tuk_texts(cv, t, "end", {1: (250, 560, -10), 2: (820, 690, 9), 3: (540, 800, -3)})
    vignette(cv, 0.5)


def sc_end(cv, t, s):
    lt = t - s["t0"]
    cv.drawColor(C("#050506"))
    on = 1.0 if lt > 0.35 else (1.0 if int(lt * 30) % 3 else 0.2)
    glow(cv, 540, 900, 520, "#7a1a14", 0.35 * on, blend=skia.BlendMode.kSrcOver)
    text(cv, "ГЛУХОМАНЬ", 540, 930, font(RUSLAN, 128), "#ece3cc", on, outline="#000000", ow=8, shadow=14)
    cv.drawLine(330, 975, 750, 975, strokep("#d8322a", 6, on))
    text(cv, "ПОДПИШИСЬ — ЧАСТЬ 2 СКОРО", 540, 1070, font(BLACK, 42), "#ffffff", on * clamp((lt - 0.3) / 0.3))
    if lt < 0.25:
        cv.drawRect(skia.Rect.MakeWH(W, H), fillp("#ffffff", 0.5 * (1 - lt / 0.25)))


common.SCENE_FN.update({"title": sc_title, "village": sc_village, "rules": sc_rules, "leave": sc_leave, "clock": sc_clock,
            "door": sc_door, "face": sc_face, "window": sc_window, "stove": sc_stove, "split": sc_split,
            "choice": sc_choice, "end": sc_end})




if __name__ == "__main__":
    common.main(sys.argv)
