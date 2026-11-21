# -*- coding: utf-8 -*-
"""Эпизод 2 «Пугало»: сцены."""
import math
import os
import random
import sys

import skia

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402

common.load("ep2")
from common import *  # noqa: E402,F401,F403
import chars  # noqa: E402
import garden  # noqa: E402
import world  # noqa: E402
from gfx import (BLACK, BOLD, HAND, RUSLAN, C, Style, back_out, circle, clamp, ease_in_out, ease_out,  # noqa: E402,F401
                 ellipse, fill, fillp, font, glow, kf, lerp, lin_grad, line_path, poly, rrect, shape, smooth, stroke,
                 strokep, text, arc_path)

GARDEN = garden.Garden()

B_HOOK = beat_by_text("Каждое утро")
B_GRAN = beat_by_text("Это ты по ночам")
B_REC = beat_by_text("Ночью я поставил")
B_PLAY = beat_by_text("А утром включил")
B_TURN = beat_by_text("А потом поворачивает")
B_LOOK = beat_by_text("И смотрит")
B_BOOTS = beat_by_text("А на сапогах")

common.CAP_Y.update({"title": 1440, "garden": 1440, "rules": 1350, "days": 1400, "gran": 1350, "phone": 1460,
                     "footage": 1470, "morning": 1400, "boots": 560, "choice": 1470, "end": 1500})

# ночное видение: зелёная монохромная картинка с подъёмом яркости
NV = skia.ColorFilters.Matrix([
    0.16, 0.34, 0.06, 0, 0.01,
    0.5, 1.05, 0.19, 0, 0.04,
    0.12, 0.26, 0.05, 0, 0.02,
    0, 0, 0, 1, 0])


def title_block(cv, t, top, big, big_size=250, pulse=0.0):
    sh = lin_grad((0, 0), (0, H), [("#000000", 0.8), ("#000000", 0.3), ("#000000", 0.15), ("#000000", 0.55)], [0, 0.4, 0.6, 1])
    cv.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=sh))
    text(cv, "ГЛУХОМАНЬ", 540, 222, font(RUSLAN, 78), "#e9e0c9", outline="#000000", ow=8, shadow=8)
    cv.drawLine(400, 250, 680, 250, strokep("#d8322a", 4))
    pill = rrect(540 - 100, 282, 200, 54, 27)
    cv.drawPath(pill, fillp("#000000", 0.55))
    cv.drawPath(pill, strokep("#e3342b", 4))
    text(cv, "ЧАСТЬ 1", 540, 320, font(BLACK, 30), "#ffffff")
    text(cv, top, 540, 520, font(BLACK, 96), "#ffffff", outline="#000000", ow=14, shadow=14)
    cv.save()
    cv.translate(540, 745)
    cv.scale(1 + 0.05 * pulse, 1 + 0.05 * pulse)
    glow(cv, 0, -80, 380, "#ff1a10", 0.2 + 0.2 * pulse, blend=skia.BlendMode.kSrcOver)
    text(cv, big, 0, 0, font(RUSLAN, big_size), "#e3342b", outline="#140707", ow=20, shadow=18)
    cv.restore()


def garden_cam(cv, cx, cy, z, ox=0.0, oy=0.0):
    cam(cv, cx, cy, z, 0, ox, oy)


# ================================================================== СЦЕНЫ
def sc_title(cv, t, s):
    lt = t - s["t0"]
    d = s["t1"] - s["t0"]
    z = 1.0 + 0.1 * ease_in_out(lt / d)
    cv.save()
    garden_cam(cv, 560, 905, z)
    x, y, sc = garden.SC_POS[2]
    GARDEN.draw(cv, t, "dusk", dict(pos=(x, y, sc * 1.05), mode="pole", smile=0.55 + 0.1 * math.sin(t * 2), sway=0.6))
    cv.restore()
    vignette(cv, 0.6)
    title_block(cv, t, "ОНО ПОДХОДИТ", "ПУГАЛО", 240, pulse=max(0.0, 1 - lt / 0.4))


def sc_garden(cv, t, s):
    th = CUES["hat"]
    k = ease_in_out((t - th + 0.2) / 1.4)
    lt = t - s["t0"]
    cx = lerp(540, 590, k)
    cy = lerp(1000, 905, k)
    z = lerp(1.0 + 0.04 * lt / 3.0, 2.4, k)
    cv.save()
    garden_cam(cv, cx, cy, z)
    GARDEN.draw(cv, t, "day", dict(pos=garden.SC_POS["mid"], mode="pole", smile=0.1, sway=0.4))
    cv.restore()
    vignette(cv, 0.45)


def icon_hand(cv, x, y, col):
    palm = smooth([(x - 22, y + 18), (x - 24, y - 8), (x + 22, y - 8), (x + 22, y + 18), (x, y + 26)], t=0.3)
    cv.drawPath(palm, strokep(col, 5))
    for k, dx in enumerate((-18, -6, 6, 18)):
        cv.drawLine(x + dx, y - 10, x + dx * 1.1, y - 34 + abs(dx) * 0.4, strokep(col, 5))
    cv.drawLine(x - 24, y + 4, x - 38, y - 10, strokep(col, 5))


def icon_hat(cv, x, y, col):
    cv.drawPath(smooth([(x - 30, y + 6), (x - 26, y - 18), (x, y - 28), (x + 26, y - 18), (x + 30, y + 6)], close=False, t=0.4), strokep(col, 5))
    cv.drawPath(rrect(x - 34, y, 68, 16, 6), strokep(col, 5))
    for sx in (-1, 1):
        cv.drawPath(smooth([(x + sx * 30, y + 12), (x + sx * 36, y + 34), (x + sx * 24, y + 36)], close=False), strokep(col, 5))


def icon_eye(cv, x, y, col):
    eye = smooth([(x - 38, y), (x, y - 24), (x + 38, y), (x, y + 24)], t=0.6)
    cv.drawPath(eye, strokep(col, 5))
    cv.drawCircle(x, y, 10, fillp(col))


def cross(cv, x, y, r, col):
    cv.drawLine(x - r, y - r, x + r, y + r, strokep(col, 7))
    cv.drawLine(x - r, y + r, x + r, y - r, strokep(col, 7))


def rules_card(cv, t, rows, t_card):
    if t < t_card - 0.35:
        return
    k = ease_out((t - (t_card - 0.35)) / 0.45)
    cv.save()
    cv.translate(540, 450 - 560 * (1 - k))
    cv.rotate(-2.0)
    pts = [(-430, -230), (-150, -237), (140, -228), (430, -233), (436, -60), (428, 140), (433, 232), (120, 228),
           (-160, 237), (-432, 230), (-438, 40)]
    paper = poly(pts)
    cv.drawPath(paper, fillp("#000000", 0.45, blur=20))
    cv.drawPath(paper, fillp("#eee3c6"))
    cv.save()
    cv.clipPath(paper, skia.ClipOp.kIntersect, True)
    for yy in range(-170, 230, 100):
        cv.drawLine(-440, yy + 60, 440, yy + 60, strokep("#a9b9cf", 2, 0.6))
    cv.drawLine(-350, -240, -350, 240, strokep("#d9837a", 2, 0.6))
    cv.restore()
    cv.drawPath(paper, strokep("#8d7b5c", 3))
    cv.drawCircle(0, -210, 11, fillp("#2a2826"))
    cv.drawCircle(-3, -213, 4, fillp("#8a8680"))
    f = font(HAND, 58)
    for i, (tc, icon, s_, col) in enumerate(rows):
        if t < tc:
            continue
        y = -125 + i * 100
        rev = clamp((t - tc) / 0.7)
        cv.save()
        cv.clipRect(skia.Rect.MakeLTRB(-440, y - 80, -440 + 900 * rev, y + 45), True)
        x = -390
        if icon:
            {"hand": icon_hand, "hat": icon_hat, "eye": icon_eye}[icon](cv, x + 40, y - 18, "#29231e")
            cross(cv, x + 40, y - 18, 30, "#c4231b")
            x += 100
        text(cv, s_, x, y, f, col, align="left")
        if col == "#c4231b":
            w_ = f.measureText(s_)
            cv.drawPath(smooth([(x, y + 14), (x + w_ * 0.5, y + 20), (x + w_, y + 12)], close=False), strokep(col, 5))
        cv.restore()
    cv.restore()


def kitchen(cv, t, cx, cy, z, finger, eyes="stern"):
    mG = mouth(t, {"G"})

    def behind(c):
        put(c, 1185, 1470, 2.8, chars.boy_front, look=0.55, blink=blink(t, 0.7), brows="worried", pupil=(0.6, 0.0))
        put(c, 1690, 1500, 3.0, chars.granny, arms="finger" if finger else "down", eyes=eyes, look=-0.45, mouth=mG, t=t,
            blink=blink(t, 1.9, 4.1))

    room_view(cv, t, (cx, cy, z), {}, [lamp_light(t, 1.0), MOON], "#2a2f45", behind=behind, lamp_lit=1.0)
    vignette(cv, 0.55)


def sc_rules(cv, t, s):
    r0 = CUES["rule0"]
    cx = kf(t, [(s["t0"], 1440.0), (r0, 1445.0), (r0 + 1.4, 1490.0), (s["t1"], 1500.0)])
    cy = kf(t, [(s["t0"], 1090.0), (r0, 1080.0), (r0 + 1.4, 1065.0), (s["t1"], 1060.0)])
    z = kf(t, [(s["t0"], 1.0), (r0, 1.03), (r0 + 1.4, 1.09), (s["t1"], 1.12)])
    kitchen(cv, t, cx, cy, z, finger=t >= r0 - 0.4)
    ink, red = "#29231e", "#c4231b"
    rows = [(r0 - 0.4, None, "Про пугало:", ink),
            (r0, "hand", "его не трогай", ink),
            (CUES["rule1"], "hat", "шапку НЕ СНИМАЙ!", red),
            (CUES["rule2"], "eye", "ночью на огород не смотри", ink)]
    rules_card(cv, t, rows, r0 - 0.4)


DAY_INFO = {1: ("ДЕНЬ 1", "ДО ДОМА: 40 ШАГОВ", "#ffffff"), 2: ("ДЕНЬ 2", "ДО ДОМА: 15 ШАГОВ", "#ffd23f"),
            3: ("ДЕНЬ 3", "ДО ДОМА: 3 ШАГА", "#ff3b30"), 4: ("УТРО", "ОНО ОПЯТЬ НА МЕСТЕ", "#ffffff")}


def window_day(cv, t, day, t_day, smile=0.0, face_sway=0.0):
    lt = t - t_day
    pos = {1: garden.SC_POS[0], 2: garden.SC_POS[1], 3: (735, 1545, 2.0), 4: garden.SC_POS[0]}[day]
    z = 1.0 + 0.05 * clamp(lt / 3.0)
    cv.save()
    garden_cam(cv, 540, 900, z)
    GARDEN.draw(cv, t, "day", dict(pos=pos, mode="pole", smile=smile, sway=face_sway))
    cv.restore()
    garden.window_pov(cv, t)
    title, sub, col = DAY_INFO[day]
    k = back_out(clamp(lt / 0.3))
    if k > 0:
        cv.save()
        cv.translate(540, 175)
        cv.scale(k, k)
        text(cv, title, 0, 0, font(BLACK, 84), "#ffffff", outline="#000000", ow=14, shadow=12)
        cv.restore()
        text(cv, sub, 540, 248, font(BLACK, 40), col, clamp(lt / 0.4), outline="#000000", ow=9)
    vignette(cv, 0.45)
    # «склейка» дней: короткое затемнение
    if lt < 0.18:
        cv.drawRect(skia.Rect.MakeWH(W, H), fillp("#000000", 1 - lt / 0.18))


def sc_days(cv, t, s):
    if t >= CUES["day3"]:
        lt = t - CUES["day3"]
        window_day(cv, t, 3, CUES["day3"], smile=0.25 + 0.25 * clamp(lt / 2.0), face_sway=0.2)
    elif t >= CUES["day2"]:
        window_day(cv, t, 2, CUES["day2"])
    else:
        window_day(cv, t, 1, CUES["day1"])


def sc_gran(cv, t, s):
    lt = t - s["t0"]
    kitchen(cv, t, 1600, 1050, 1.35 + 0.08 * ease_in_out(lt / (s["t1"] - s["t0"])), finger=False, eyes="kind")


# ---------------------------------------------------------------- телефон и запись
def sleeping_boy(c, t):
    Style.lw = 5.0
    c.save()
    c.translate(632, 506)
    c.rotate(-84)
    c.scale(1.35, 1.35)
    c.translate(0, 154)
    Style.lw = 5.0 / 1.35
    chars.boy_head(c, look=0.0, blink=1.0, t=t)
    c.restore()
    Style.lw = 5.0
    breath = 3 * math.sin(t * 1.6)
    blanket = smooth([(300, 566), (318, 492 - breath), (420, 470 - breath), (540, 486 - breath), (598, 532), (600, 566)], t=0.35)
    shape(c, blanket, "#7c6a8c")
    c.save()
    c.clipPath(blanket, skia.ClipOp.kIntersect, True)
    for i in range(10):
        c.drawLine(300 + i * 34, 460, 280 + i * 34, 570, strokep("#655577", 8, 0.7))
    c.restore()


def footage_world(c, t, st_extra=None, sc_state=None):
    """Изба ночью в ИК-подсветке. Рисуется в мировых координатах (камера уже выставлена)."""
    st = dict(door_open=st_extra.get("door_open", 0.0) if st_extra else 0.0)

    def doorway(cc):
        if sc_state and sc_state.get("in_doorway"):
            sc_state["draw"](cc)

    st["doorway"] = doorway

    def fg(cc):
        sleeping_boy(cc, t)
        if sc_state and not sc_state.get("in_doorway"):
            sc_state["draw"](cc)

    c.drawPicture(ROOM.p_back)
    ROOM.outside(c, {})
    ROOM.glass(c, {})
    c.drawPicture(ROOM.p_stove)
    ROOM.gap(c, {}, t)
    c.drawPicture(ROOM.p_winframe)
    c.drawPicture(ROOM.p_mull)
    c.drawPicture(ROOM.p_props)
    ROOM.clock(c, {"time": (3, 0)}, t)
    ROOM.door(c, st, t)
    c.drawPicture(ROOM.p_table)
    ROOM.lamp(c, {}, t, 0.0)
    fg(c)
    lighting(c, [(1250, 1000, 1350, "#ffffff", 0.62), (1430, 800, 500, "#ffffff", 0.2)], "#262626")


def scarecrow_state(t, x, face="back", smile=0.3, walk=0.0, squash=1.0, in_doorway=False, s=2.05, y=1560):
    def draw(c):
        c.save()
        c.translate(x, y)
        c.scale(s, s)
        Style.lw = 4.2 / s
        chars.scarecrow(c, mode="stand", face=face, smile=smile, t=t, walk=walk, squash=squash)
        c.restore()
    return dict(draw=draw, in_doorway=in_doorway)


def footage_time(t):
    """Время на записи (сек от 00:00)."""
    t0 = CUES["f_start"]
    tl0 = CUES["timelapse"]
    tl1 = CUES["turn"]
    base = 3 * 3600 + 0
    if t < tl0:
        return base + (t - t0)
    k = clamp((t - tl0) / (tl1 - tl0))
    fast = base + (tl0 - t0) + ease_in_out(k) * (2 * 3600 + 55 * 60)
    return fast + max(0.0, t - tl1)


def hms(sec):
    sec = int(sec)
    return "%02d:%02d:%02d" % (sec // 3600, (sec // 60) % 60, sec % 60)


def glitch_slices(cv, t, draw_fn, box, strength):
    """Несколько горизонтальных полос кадра со сдвигом (эффект «битой» записи)."""
    r = random.Random(int(t * 30))
    x0, y0, x1, y1 = box
    for _ in range(int(3 + 5 * strength)):
        yy = r.uniform(y0, y1)
        hh = r.uniform(8, 60)
        dx = r.uniform(-90, 90) * strength
        cv.save()
        cv.clipRect(skia.Rect.MakeLTRB(x0, yy, x1, yy + hh), True)
        cv.translate(dx, 0)
        draw_fn(cv)
        cv.restore()


def sc_phone(cv, t, s):
    if t < CUES["play"]:
        # телефон на столе пишет ночь
        lt = t - s["t0"]
        z = 2.3 + 0.2 * ease_in_out(lt / 2.6)

        def fg(c):
            c.save()
            c.translate(1318, 1236)
            c.rotate(-7)
            Style.lw = 4.0
            shape(c, rrect(-40, -150, 80, 150, 14), "#141519")
            c.drawRect(skia.Rect.MakeLTRB(-32, -140, 32, -10), fillp("#12301c"))
            c.restore()

        def emis(c):
            c.save()
            c.translate(1318, 1236)
            c.rotate(-7)
            glow(c, 0, -75, 130, "#7fd38f", 0.25)
            c.drawRect(skia.Rect.MakeLTRB(-32, -140, 32, -10), fillp("#2c6a3c", 0.9))
            on = (int(t * 2) % 2) == 0
            if on:
                c.drawCircle(-18, -126, 6, fillp("#ff2b20"))
            text(c, "REC", 6, -120, font(BLACK, 13), "#ffffff", align="center")
            c.restore()

        room_view(cv, t, (1340, 1150, z), {}, [lamp_light(t, 0.0), MOON, (1318, 1160, 420, "#7fd38f", 0.45)], "#151826",
                  fg=fg, emis=emis, lamp_lit=0.0)
        vignette(cv, 0.6)
    else:
        # утро: галерея на телефоне
        lt = t - CUES["play"]
        cv.drawColor(C("#1b1e26"))
        sx0, sy0, sx1, sy1 = garden.phone(cv, 540, 900, 640, 1180, r=60)
        cv.drawRect(skia.Rect.MakeLTRB(sx0, sy0, sx1, sy1), fillp("#f2f2f4"))
        text(cv, "Видео", sx0 + 34, sy0 + 92, font(BLACK, 46), "#111111", align="left")
        bx0, by0, bx1, by1 = sx0 + 30, sy0 + 150, sx1 - 30, sy0 + 150 + (sx1 - sx0 - 60) * 9 / 16
        cv.save()
        cv.clipPath(rrect(bx0, by0, bx1 - bx0, by1 - by0, 18), skia.ClipOp.kIntersect, True)
        cv.saveLayer(None, skia.Paint(ColorFilter=NV))
        cv.save()
        cam(cv, 1200, 1085, (bx1 - bx0) / 2400, 0, 0, 0, (bx0 + bx1) / 2, (by0 + by1) / 2)
        footage_world(cv, t)
        cv.restore()
        cv.restore()
        cv.restore()
        pk = 1 + 0.08 * math.sin(lt * 8)
        tap = CUES["play"] + 1.5
        if t >= tap:
            pk = 0.85
        cv.drawCircle((bx0 + bx1) / 2, (by0 + by1) / 2, 46 * pk, fillp("#000000", 0.5))
        cv.drawPath(poly([((bx0 + bx1) / 2 - 14, (by0 + by1) / 2 - 22), ((bx0 + bx1) / 2 + 24, (by0 + by1) / 2),
                          ((bx0 + bx1) / 2 - 14, (by0 + by1) / 2 + 22)]), fillp("#ffffff"))
        text(cv, "03:00 — 06:02", bx0, by1 + 60, font(BOLD, 36), "#333333", align="left")
        text(cv, "длительность 3:02:15", bx0, by1 + 108, font(BOLD, 30), "#888888", align="left")
        if t >= tap:
            k = clamp((t - tap) / 0.4)
            cv.drawCircle((bx0 + bx1) / 2, (by0 + by1) / 2, 40 + 120 * k, strokep("#ffffff", 6, 1 - k))


def sc_footage(cv, t, s):
    lt = t - s["t0"]
    t_open = CUES["door_open"]
    t_enter = CUES["enter"]
    t_stand = CUES["stand"]
    t_turn = CUES["turn"]
    door_k = ease_in_out((t - t_open - 0.05) / 1.0) * 0.9
    # пугало: входит в дверь, идёт к печи, стоит
    walk_k = clamp((t - t_enter) / (t_stand + 0.6 - t_enter))
    x = lerp(2250, 1010, ease_in_out(walk_k))
    walking = 0 < walk_k < 1
    in_door = t < t_enter + 0.35
    # поворот головы
    tg = wt(B_TURN, 3)
    kt = clamp((t - tg) / 0.55)
    squash = abs(math.cos(math.pi * kt))
    face = "front" if kt >= 0.5 else "back"
    tl = wt(B_LOOK, 2)
    smile = 0.3 + 0.7 * ease_out((t - tl) / 0.35)
    sc_st = None
    if t >= t_enter - 0.1:
        sc_st = scarecrow_state(t, x, face=face, smile=smile, walk=(t * 1.6) % 1.0 if walking else 0.0,
                                squash=max(0.06, squash), in_doorway=in_door)
    # раскладка: окно плеера → на весь экран при повороте
    zk = ease_in_out((t - t_turn) / 1.2)
    box0 = (0, 640, W, 640 + 607)
    box = tuple(lerp(a, b, zk) for a, b in zip(box0, (0, 0, W, H)))
    bw, bh = box[2] - box[0], box[3] - box[1]
    z_world = lerp(W / 2360, 2.1, zk)
    ccx = lerp(1200, 1010, zk)
    ccy = lerp(1085, 1560 - 262 * 2.05, zk)

    def draw_view(c):
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(*box), True)
        c.saveLayer(None, skia.Paint(ColorFilter=NV))
        c.save()
        cam(c, ccx, ccy, z_world, 0, 0, 0, (box[0] + box[2]) / 2, (box[1] + box[3]) / 2)
        footage_world(c, t, {"door_open": door_k}, sc_st)
        c.restore()
        c.restore()
        # ИК-отблеск глаза-пуговицы
        if face == "front" and sc_st is not None:
            c.save()
            cam(c, ccx, ccy, z_world, 0, 0, 0, (box[0] + box[2]) / 2, (box[1] + box[3]) / 2)
            c.translate(x, 1560)
            c.scale(2.05, 2.05)
            chars.scarecrow_eyes_glow(c, clamp((t - tl) / 0.2))
            c.restore()
        c.restore()

    cv.drawColor(C("#050506"))
    if zk < 0.99:
        text(cv, "НОЧЬ_03-00.mp4", 540, 600, font(BOLD, 34), "#8a8f99", 1 - zk)
    draw_view(cv)
    # глитч на повороте и на взгляде в камеру
    g = 0.0
    for tg_ in (tg + 0.2, tl):
        if 0 <= t - tg_ < 0.3:
            g = max(g, 1 - (t - tg_) / 0.3)
    if g > 0:
        glitch_slices(cv, t, draw_view, box, g)
    # интерфейс записи поверх
    cv.save()
    cv.clipRect(skia.Rect.MakeLTRB(*box), True)
    for yy in range(int(box[1]), int(box[3]), 5):
        cv.drawLine(box[0], yy, box[2], yy, strokep("#000000", 1.6, 0.16))
    vg = rad_grad(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2), max(bw, bh) * 0.75,
                  [("#000000", 0.0), ("#000000", 0.0), ("#000000", 0.65)], [0, 0.55, 1])
    cv.drawRect(skia.Rect.MakeLTRB(*box), skia.Paint(Shader=vg))
    sc_ui = lerp(1.0, 1.6, zk)
    pad = 34 * sc_ui
    if (int(t * 2) % 2) == 0:
        cv.drawCircle(box[0] + pad + 12, box[1] + pad + 14, 12 * sc_ui, fillp("#ff2b20"))
    text(cv, "REC", box[0] + pad + 34 * sc_ui, box[1] + pad + 26 * sc_ui, font(BLACK, int(32 * sc_ui)), "#ffffff", align="left")
    text(cv, hms(footage_time(t)), box[2] - pad, box[3] - pad, font(BLACK, int(40 * sc_ui)), "#ffffff", align="right")
    if CUES["timelapse"] <= t < t_turn:
        fy = box[3] - pad - 62 * sc_ui
        fx = box[2] - pad - 150 * sc_ui
        for k in range(2):
            x_ = fx + k * 22 * sc_ui
            cv.drawPath(poly([(x_, fy - 12 * sc_ui), (x_ + 20 * sc_ui, fy), (x_, fy + 12 * sc_ui)]), fillp("#ffffff"))
        text(cv, "x5000", box[2] - pad, fy + 11 * sc_ui, font(BLACK, int(30 * sc_ui)), "#ffffff", align="right")
    cv.drawPath(rrect(box[2] - pad - 64 * sc_ui, box[1] + pad, 56 * sc_ui, 26 * sc_ui, 5), strokep("#ffffff", 3))
    cv.drawRect(skia.Rect.MakeXYWH(box[2] - pad - 60 * sc_ui, box[1] + pad + 4 * sc_ui, 18 * sc_ui, 18 * sc_ui), fillp("#ff3b30"))
    cv.restore()
    if zk < 0.99:
        a = 1 - zk
        prog = clamp((footage_time(t) - 3 * 3600) / (3 * 3600 + 2 * 60 - 3 * 3600 + 3600 * 0 + 1) * 0.0 + (t - s["t0"]) / (s["t1"] - s["t0"]))
        cv.drawLine(60, 1300, 1020, 1300, strokep("#555a66", 6, a))
        cv.drawLine(60, 1300, 60 + 960 * prog, 1300, strokep("#ff3b30", 6, a))
        cv.drawCircle(60 + 960 * prog, 1300, 12, fillp("#ffffff", a))
    if 0 <= t - tl < 0.12:
        cv.drawRect(skia.Rect.MakeWH(W, H), fillp("#d8ffd8", 0.5 * (1 - (t - tl) / 0.12)))


def sc_morning(cv, t, s):
    window_day(cv, t, 4, s["t0"])


def sc_boots(cv, t, s):
    lt = t - s["t0"]
    z = 2.3 + 0.25 * ease_in_out(lt / (s["t1"] - s["t0"]))

    def fg(c):
        r = random.Random(5)
        for k in range(26):
            px = r.uniform(1900, 2500)
            py = r.uniform(1440, 1640)
            chars.straw(c, px, py, r.uniform(0, 360), r.uniform(14, 30), n=3, seed=200 + k, spread=40)
        put(c, 2180, 1560, 1.25, chars.boots, lw_px=4.0, t=t, straw_k=1.0)

    room_view(cv, t, (2240, 1400, z), {"bolt": 1.0}, [(1430, 820, 1800, "#fff3dc", 1.0), (2200, 1200, 900, "#ffe9c8", 0.6)],
              "#8c8478", fg=fg, lamp_lit=0.0)
    vignette(cv, 0.5)
    tb = wt(B_BOOTS, 6)
    if 0 <= t - tb < 0.2:
        cv.drawRect(skia.Rect.MakeWH(W, H), fillp("#ffffff", 0.25 * (1 - (t - tb) / 0.2)))


def thumb(cv, t, which, box):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    cv.save()
    cv.clipPath(rrect(x0, y0, x1 - x0, y1 - y0, 26), skia.ClipOp.kIntersect, True)
    if which == 1:
        cv.save()
        cam(cv, 590, 1060, 0.62, 0, 0, 0, cx, cy)
        GARDEN.draw(cv, t, "dusk", dict(pos=garden.SC_POS["mid"], mode="pole", smile=0.3), crows=False)
        cv.restore()
        # огонь у основания пугала
        for k in range(5):
            fx = cx - 60 + k * 30
            fy = y1 - 60 - (k % 2) * 16
            h_ = 60 + 30 * math.sin(t * 9 + k)
            glow(cv, fx, fy - 20, 70, "#ff7a1a", 0.35)
            cv.drawPath(smooth([(fx, fy - h_), (fx + 16, fy - 10), (fx + 10, fy + 8), (fx - 10, fy + 8), (fx - 16, fy - 10)], t=0.5),
                        fillp("#ffb02e"))
            cv.drawPath(smooth([(fx, fy - h_ * 0.6), (fx + 8, fy - 6), (fx, fy + 6), (fx - 8, fy - 6)], t=0.5), fillp("#fff1a8"))
    else:
        cv.drawColor(C("#141620"))
        cv.save()
        cam(cv, 0, -270, 2.1, 0, 0, 0, cx, cy + 30)
        Style.lw = 2.0
        chars.scarecrow(cv, mode="stand", face="front", smile=0.8, t=t)
        cv.restore()
        sh = rad_grad((cx, cy), 300, [("#000000", 0.0), ("#000000", 0.6)])
        cv.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), skia.Paint(Shader=sh))
    cv.restore()
    cv.drawPath(rrect(x0, y0, x1 - x0, y1 - y0, 26), strokep("#e9e2d0", 5))


def sc_choice(cv, t, s):
    lt = t - s["t0"]
    cv.drawColor(C("#0c0e15"))
    cv.saveLayer(None, skia.Paint(ImageFilter=skia.ImageFilters.Blur(20, 20)))
    cv.save()
    cam(cv, 560, 1060, 1.0)
    GARDEN.draw(cv, t, "night", dict(pos=garden.SC_POS[2], mode="pole", smile=0.6), crows=False)
    cv.restore()
    cv.restore()
    cv.drawRect(skia.Rect.MakeWH(W, H), fillp("#06070b", 0.6))
    k0 = ease_out(lt / 0.35)
    text(cv, "ЧТО ДЕЛАТЬ?", 540, 330 - 40 * (1 - k0), font(BLACK, 92), "#ffffff", k0, outline="#000000", ow=12, shadow=12)
    boxes = [(70, 400, 515, 900), (565, 400, 1010, 900)]
    labels = [("СЖЕЧЬ", "ПУГАЛО"), ("СНЯТЬ", "ДЕДОВУ ШАПКУ")]
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
        bc = "#ffb02e" if i == 0 else "#ffd23f"
        cv.drawCircle(box[0] + 52, box[1] + 52, 40, fillp("#000000", 0.7))
        cv.drawCircle(box[0] + 52, box[1] + 52, 34, fillp(bc))
        text(cv, str(i + 1), box[0] + 52, box[1] + 70, font(BLACK, 48), "#111111")
        text(cv, labels[i][0], cxb, box[3] + 62, font(BLACK, 44), "#ffffff")
        text(cv, labels[i][1], cxb, box[3] + 112, font(BLACK, 40 if i else 46), bc)
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


common.SCENE_FN.update({"title": sc_title, "garden": sc_garden, "rules": sc_rules, "days": sc_days, "gran": sc_gran,
                        "phone": sc_phone, "footage": sc_footage, "morning": sc_morning, "boots": sc_boots,
                        "choice": sc_choice, "end": sc_end})

if __name__ == "__main__":
    common.main(sys.argv)
