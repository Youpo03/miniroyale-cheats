# -*- coding: utf-8 -*-
"""Миры: изба (одна комната, разные ракурсы) и деревня на закате."""
import math
import random

import skia

import chars
from gfx import (OUT, Style, C, arc_path, circle, ellipse, fill, fillp, glow, line_path, poly, rad_grad, rect, rrect,
                 shape, smooth, stroke, strokep, lin_grad, font, text, RUSLAN, BLACK, hash01)

# ------------------------------------------------------------------ геометрия избы
WALL_TOP, FLOOR_Y = 170, 1420
LOG_H = 72
STOVE = (110, 560, 880, 1420)          # x0, y0, x1, y1
GAP = (860, 520, 995, 1420)
WIN = (1260, 640, 1600, 1000)          # проём окна
WIN_MULL_X = 1430
WIN_MULL_Y = 742
TABLE = (1150, 1235, 1720)             # x0, top_y, x1
LAMP = (1430, 1235)
CLOCK = (1820, 565)
DOOR = (2064, 534, 2436, 1420)         # полотно
JAMB = (2030, 500, 2470, 1420)
BOLT_Y = 945
THERMO = (1452, 766)


def _rng(seed):
    return random.Random(seed)


# ================================================================== статичные слои (Picture)
def _record(fn, w=2900, h=2300):
    rec = skia.PictureRecorder()
    c = rec.beginRecording(skia.Rect(-100, -100, w, h))
    fn(c)
    return rec.finishRecordingAsPicture()


def _draw_back(cv):
    Style.lw = 5.0
    r = _rng(1)
    # потолок
    cv.drawRect(skia.Rect.MakeLTRB(-100, -100, 2900, WALL_TOP), fillp("#2a1e17"))
    for x in range(-100, 2900, 140):
        cv.drawRect(skia.Rect.MakeLTRB(x, -100, x + 4, WALL_TOP), fillp("#1c140f"))
    shape(cv, rect(-100, 110, 3000, 60), "#3b2a20")
    # брёвна
    y = WALL_TOP
    k = 0
    while y < FLOOR_Y:
        col = "#5f4432" if k % 2 == 0 else "#5a3f2f"
        cv.drawRect(skia.Rect.MakeLTRB(-100, y, 2900, y + LOG_H), fillp(col))
        cv.drawRect(skia.Rect.MakeLTRB(-100, y + 6, 2900, y + 20), fillp("#71523c", 0.55))
        cv.drawRect(skia.Rect.MakeLTRB(-100, y + LOG_H - 16, 2900, y + LOG_H), fillp("#3e2b20", 0.6))
        # волокна и сучки
        for _ in range(26):
            gx = r.uniform(-100, 2900)
            gy = y + r.uniform(18, LOG_H - 18)
            gl = r.uniform(60, 220)
            p = smooth([(gx, gy), (gx + gl * 0.5, gy + r.uniform(-3, 3)), (gx + gl, gy + r.uniform(-2, 2))], close=False)
            cv.drawPath(p, strokep("#4a3427", r.uniform(1.5, 3.0), 0.7))
        for _ in range(3):
            kx = r.uniform(-100, 2900)
            ky = y + r.uniform(24, LOG_H - 24)
            fill(cv, ellipse(kx, ky, r.uniform(7, 12), r.uniform(4, 6)), "#3f2c21", 0.85)
            cv.drawPath(ellipse(kx, ky, r.uniform(12, 16), r.uniform(7, 9)), strokep("#4a3427", 2, 0.7))
        # пакля между брёвнами
        pak = [(xx, y + 1.5 * math.sin(xx * 0.07) + r.uniform(-1, 1)) for xx in range(-100, 2901, 25)]
        cv.drawPath(poly(pak, close=False), strokep("#9a8263", 6, 0.9))
        cv.drawPath(poly([(x, yy + 4) for x, yy in pak], close=False), strokep("#2b1e16", 2.5, 0.8))
        y += LOG_H
        k += 1
    # пол
    cv.drawRect(skia.Rect.MakeLTRB(-100, FLOOR_Y, 2900, 2300), fillp("#3f2c21"))
    ys = [FLOOR_Y, 1458, 1505, 1562, 1630, 1710, 1802, 1908, 2030, 2170, 2320]
    for i in range(len(ys) - 1):
        col = "#46322580" if i % 2 else "#3a291f"
        cv.drawRect(skia.Rect.MakeLTRB(-100, ys[i], 2900, ys[i + 1]), fillp(col[:7], 0.9))
        cv.drawRect(skia.Rect.MakeLTRB(-100, ys[i], 2900, ys[i] + 4), fillp("#22170f"))
        for _ in range(8):
            gx = r.uniform(-100, 2900)
            cv.drawLine(gx, ys[i] + (ys[i + 1] - ys[i]) * 0.5, gx + r.uniform(80, 260), ys[i] + (ys[i + 1] - ys[i]) * 0.5 + r.uniform(-3, 3),
                        strokep("#2f2118", 2, 0.6))
    cv.drawRect(skia.Rect.MakeLTRB(-100, FLOOR_Y - 14, 2900, FLOOR_Y + 6), fillp("#2b1e16"))
    # половик
    rug = poly([(1010, 1560), (1860, 1560), (1940, 1760), (930, 1760)])
    cv.drawPath(rug, fillp("#8c6f55"))
    cv.save()
    cv.clipPath(rug, skia.ClipOp.kIntersect, True)
    cols = ["#7a3a34", "#3f5566", "#b49a6c", "#6a4b5c", "#7a3a34", "#4f6b52"]
    yy = 1560
    i = 0
    while yy < 1760:
        h = 26 + (i * 7) % 15
        cv.drawRect(skia.Rect.MakeLTRB(900, yy, 1960, yy + h * 0.55), fillp(cols[i % len(cols)], 0.9))
        yy += h
        i += 1
    cv.restore()
    stroke(cv, rug, OUT, 4)


def _draw_stove(cv):
    Style.lw = 5.0
    x0, y0, x1, y1 = STOVE
    # ухват у печки
    stroke(cv, line_path(70, 1415, 105, 860), "#2a1d15", 16)
    stroke(cv, line_path(70, 1415, 105, 860), "#8a6a48", 10)
    stroke(cv, arc_path(105, 850, 28, 34, 180, 360), "#2a2826", 9)
    # тело
    body = rrect(x0 + 10, y0 + 40, x1 - x0 - 20, y1 - y0 - 40, 18)
    shape(cv, body, "#dad2c3")
    cv.drawRect(skia.Rect.MakeLTRB(x1 - 80, y0 + 50, x1 - 12, y1 - 4), fillp("#beb4a2", 0.8))
    cv.drawRect(skia.Rect.MakeLTRB(x0 + 14, y0 + 50, x0 + 40, y1 - 4), fillp("#e8e2d6", 0.6))
    # лежанка
    shape(cv, rrect(x0 - 10, y0, x1 - x0 + 20, 56, 10), "#e3dccd")
    # одеяло-лоскутное + подушка
    quilt = smooth([(170, y0 + 4), (180, y0 - 52), (330, y0 - 64), (500, y0 - 50), (520, y0 + 4)], t=0.4)
    shape(cv, quilt, "#9a5b4f")
    cv.save()
    cv.clipPath(quilt, skia.ClipOp.kIntersect, True)
    pc = ["#6e7f5a", "#c9a45a", "#5a6f8a", "#b06a55", "#8a6a8a"]
    for i in range(8):
        for j in range(3):
            cv.drawRect(skia.Rect.MakeXYWH(170 + i * 45, y0 - 70 + j * 26, 45, 26), fillp(pc[(i * 2 + j) % 5], 0.85))
    cv.restore()
    stroke(cv, quilt, OUT)
    shape(cv, smooth([(560, y0 + 4), (565, y0 - 34), (640, y0 - 44), (705, y0 - 30), (700, y0 + 4)], t=0.4), "#ece7dc")
    # печурки
    for (nx, ny) in ((250, 760), (700, 760), (250, 1318), (700, 1318)):
        p = smooth([(nx - 34, ny + 28), (nx - 34, ny - 6), (nx, ny - 30), (nx + 34, ny - 6), (nx + 34, ny + 28)], t=0.35)
        shape(cv, p, "#2c2521", lw=4)
    # копоть и чело
    cv.drawOval(skia.Rect.MakeLTRB(330, 900, 670, 1120), fillp("#4a423c", 0.5, blur=30))
    chelo = smooth([(360, 1240), (360, 1080), (420, 1025), (500, 1012), (580, 1025), (640, 1080), (640, 1240)], t=0.3)
    shape(cv, chelo, "#130f0d")
    glow(cv, 500, 1220, 120, "#a0401c", 0.25, blend=skia.BlendMode.kSrcOver)
    # шесток
    shape(cv, rrect(320, 1236, 360, 38, 6), "#d0c7b5")
    # заслонка
    zas = smooth([(565, 1236), (575, 1085), (640, 1070), (705, 1090), (712, 1236)], t=0.25)
    shape(cv, zas, "#3b3c40")
    shape(cv, rrect(625, 1140, 34, 14, 6), "#56575c", lw=4)
    # трещинки
    for (a, b) in (((160, 700), (210, 760)), ((760, 1000), (800, 1080)), ((300, 1380), (360, 1340))):
        stroke(cv, poly([a, ((a[0] + b[0]) / 2 + 8, (a[1] + b[1]) / 2), b], close=False), "#a89e8c", 2.5)
    shape(cv, rect(x0, y1 - 22, x1 - x0, 24), "#a99f8d", lw=4)


def _draw_gap_back(cv):
    gx0, gy0, gx1, gy1 = GAP
    cv.drawRect(skia.Rect.MakeLTRB(gx0, gy0, gx1, gy1), fillp("#0a0706"))
    sh = lin_grad((gx0, 0), (gx1, 0), [("#000000", 0.0), ("#000000", 0.5)])
    cv.drawRect(skia.Rect.MakeLTRB(gx0, gy0, gx1, gy1), skia.Paint(Shader=sh))


def _draw_window_frame(cv):
    Style.lw = 5.0
    x0, y0, x1, y1 = WIN
    blue = "#c9d4de"
    # наличник: кокошник
    kok = smooth([(x0 - 60, y0 - 50), (x0 - 40, y0 - 120), ((x0 + x1) / 2, y0 - 175), (x1 + 40, y0 - 120), (x1 + 60, y0 - 50)], t=0.35)
    shape(cv, kok, blue)
    for i in range(7):
        a = math.radians(200 + i * 20)
        cx = (x0 + x1) / 2 + 150 * math.cos(a)
        cy = y0 - 40 + 95 * math.sin(a)
        shape(cv, circle(cx, cy, 11), "#3a2a20", lw=3)
    shape(cv, circle((x0 + x1) / 2, y0 - 105, 22), "#7a8fa3", lw=4)
    # рама
    frame = skia.Path()
    frame.addRect(skia.Rect.MakeLTRB(x0 - 45, y0 - 45, x1 + 45, y1 + 45))
    frame.addRect(skia.Rect.MakeLTRB(x0, y0, x1, y1))
    frame.setFillType(skia.PathFillType.kEvenOdd)
    shape(cv, frame, blue)
    stroke(cv, rect(x0 - 12, y0 - 12, x1 - x0 + 24, y1 - y0 + 24), "#8fa0b0", 4)
    # нижняя доска с фестонами
    pts = [(x0 - 60, y1 + 40)]
    for i in range(9):
        xx = x0 - 60 + (x1 - x0 + 120) * (i + 0.5) / 9
        pts += [(xx - 12, y1 + 70), (xx, y1 + 92), (xx + 12, y1 + 70)]
    pts.append((x1 + 60, y1 + 40))
    shape(cv, poly(pts), blue)
    # подоконник
    shape(cv, rect(x0 - 30, y1, x1 - x0 + 60, 26), "#d9e1e8")
    # горшок с геранью
    gx = x1 - 50
    shape(cv, poly([(gx - 26, y1 - 46), (gx + 26, y1 - 46), (gx + 18, y1), (gx - 18, y1)]), "#a5583a")
    for (lx, ly, rr) in ((-24, -70, 18), (14, -78, 20), (-4, -96, 17), (24, -60, 14)):
        shape(cv, circle(gx + lx, y1 + ly, rr), "#3f6b3a", lw=4)
    for (fx, fy) in ((-10, -112), (12, -106), (0, -120), (-20, -98)):
        shape(cv, circle(gx + fx, y1 + fy, 8), "#c8403a", lw=3)
    # кружевная занавеска-ламбрекен
    lace = [(x0, y0), (x1, y0), (x1, y0 + 48)]
    n = 12
    for i in range(n, -1, -1):
        xx = x0 + (x1 - x0) * i / n
        lace += [(xx, y0 + 48 + (14 if i % 2 else 0))]
    cv.drawPath(poly(lace), fillp("#efeae0", 0.88))
    for i in range(n):
        cv.drawCircle(x0 + (x1 - x0) * (i + 0.5) / n, y0 + 26, 5, fillp("#b9b2a5", 0.8))
    stroke(cv, poly(lace), "#9c958a", 2.5)


def _draw_mullions(cv):
    x0, y0, x1, y1 = WIN
    blue = "#c9d4de"
    shape(cv, rect(WIN_MULL_X - 9, y0, 18, y1 - y0), blue, lw=4)
    shape(cv, rect(x0, WIN_MULL_Y - 8, x1 - x0, 16), blue, lw=4)


def _draw_wall_props(cv):
    Style.lw = 5.0
    # полка с банками
    sx0, sy = 1665, 1045
    shape(cv, rect(sx0, sy, 300, 18), "#6e4d34")
    for bx in (sx0 + 30, sx0 + 260):
        shape(cv, poly([(bx, sy + 18), (bx + 14, sy + 18), (bx + 14, sy + 70)]), "#5b3f2b", lw=4)
    jar = rrect(sx0 + 24, sy - 92, 64, 92, 14)
    shape(cv, jar, "#9fb7a2")
    for (cx, cy) in ((sx0 + 44, sy - 60), (sx0 + 62, sy - 40), (sx0 + 50, sy - 22), (sx0 + 70, sy - 70)):
        shape(cv, ellipse(cx, cy, 8, 16), "#5b7a3c", lw=3)
    shape(cv, rrect(sx0 + 20, sy - 104, 72, 16, 5), "#c9b26a", lw=4)
    shape(cv, smooth([(sx0 + 120, sy), (sx0 + 112, sy - 50), (sx0 + 132, sy - 78), (sx0 + 176, sy - 78), (sx0 + 196, sy - 50), (sx0 + 188, sy)], t=0.35), "#9a5a3a")
    shape(cv, rrect(sx0 + 216, sy - 56, 54, 56, 8), "#d8cfba")
    stroke(cv, line_path(sx0 + 216, sy - 40, sx0 + 270, sy - 40), "#3d5a8a", 4)
    # ватник на гвозде и валенки
    shape(cv, circle(2560, 600, 7), "#2b2b2b", lw=3)
    coat = smooth([(2560, 600), (2620, 640), (2650, 760), (2655, 1020), (2470 + 30, 1030), (2500, 760), (2515, 640)], t=0.3)
    shape(cv, coat, "#3d4440")
    cv.save()
    cv.clipPath(coat, skia.ClipOp.kIntersect, True)
    for xx in range(2480, 2680, 26):
        cv.drawLine(xx, 600, xx, 1040, strokep("#2c312e", 3, 0.9))
    cv.restore()
    shape(cv, smooth([(2575, 640), (2585, 760), (2580, 1020)], close=False), None)
    stroke(cv, poly([(2577, 650), (2583, 1020)], close=False), "#262a28", 4)
    for vx in (2515, 2585):
        shape(cv, smooth([(vx, 1290), (vx + 50, 1290), (vx + 52, 1390), (vx + 75, 1400), (vx + 74, 1422), (vx - 2, 1422)], t=0.2), "#5a5450")
    # косяки двери
    jx0, jy0, jx1, jy1 = JAMB
    shape(cv, rect(jx0, jy0, 36, jy1 - jy0), "#4a3426")
    shape(cv, rect(jx1 - 36, jy0, 36, jy1 - jy0), "#4a3426")
    shape(cv, rect(jx0 - 20, jy0 - 10, jx1 - jx0 + 40, 44), "#4f382a")
    # ответная скоба засова на косяке
    shape(cv, rect(jx0 - 6, BOLT_Y - 16, 58, 14), "#2e2e30", lw=3.5)
    shape(cv, rect(jx0 - 6, BOLT_Y + 36, 58, 14), "#2e2e30", lw=3.5)


def _draw_table(cv):
    Style.lw = 5.0
    x0, ty, x1 = TABLE
    for lx in (x0 + 30, x1 - 65):
        shape(cv, rect(lx, ty + 60, 36, 300), "#6a4a30")
    shape(cv, rect(x0 + 60, ty + 250, x1 - x0 - 120, 22), "#5b3f29")
    shape(cv, rect(x0 - 10, ty, x1 - x0 + 20, 26), "#7a5636")
    cloth = poly([(x0 - 14, ty - 4), (x1 + 14, ty - 4), (x1 + 22, ty + 96), (x0 - 22, ty + 96)])
    shape(cv, cloth, "#e9e4d6")
    for yy, col in ((ty + 66, "#b2342c"), (ty + 80, "#b2342c")):
        cv.drawLine(x0 - 18, yy, x1 + 18, yy, strokep(col, 4))
    for i in range(int((x1 - x0 + 40) / 22)):
        cx = x0 - 16 + i * 22 + 11
        cv.drawPath(poly([(cx - 6, ty + 73), (cx, ty + 67), (cx + 6, ty + 73), (cx, ty + 79)]), fillp("#b2342c"))
    # бахрома
    for i in range(int((x1 - x0 + 44) / 12)):
        cx = x0 - 20 + i * 12
        cv.drawLine(cx, ty + 96, cx + 1, ty + 112, strokep("#d8d2c2", 3))


class Room:
    def __init__(self):
        self.p_back = _record(_draw_back)
        self.p_stove = _record(_draw_stove)
        self.p_gapback = _record(_draw_gap_back)
        self.p_winframe = _record(_draw_window_frame)
        self.p_mull = _record(_draw_mullions)
        self.p_props = _record(_draw_wall_props)
        self.p_table = _record(_draw_table)
        r = _rng(5)
        # морозные узоры: заранее «выращенные» ветки
        self.frost = []
        for k in range(140):
            side = r.choice(["l", "r", "t", "b", "l", "r"])
            u = r.random()
            ang = {"l": 0, "r": 180, "t": 90, "b": -90}[side] + r.uniform(-50, 50)
            L = r.uniform(18, 70)
            segs = []
            x, y = 0.0, 0.0
            a = math.radians(ang)
            steps = r.randint(4, 7)
            for s in range(steps):
                nx = x + math.cos(a) * L / steps
                ny = y + math.sin(a) * L / steps
                segs.append((x, y, nx, ny, s))
                bl = L / steps * (1.4 - s / steps)
                for sgn in (-1, 1):
                    b = a + math.radians(sgn * 58)
                    segs.append((nx, ny, nx + math.cos(b) * bl, ny + math.sin(b) * bl, s + 0.5))
                x, y = nx, ny
                a += math.radians(r.uniform(-12, 12))
            self.frost.append((side, u, r.random(), segs))
        self.stars = [(r.uniform(0, 1), r.uniform(0, 1), r.uniform(0.8, 2.2)) for _ in range(40)]

    # -------------------------------------------------------------- динамика
    def outside(self, cv, st):
        x0, y0, x1, y1 = WIN
        cv.save()
        cv.clipRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), True)
        sh = lin_grad((0, y0), (0, y1), ["#0e1424", "#1d2a44", "#2b3b5a"], [0, 0.6, 1])
        cv.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), skia.Paint(Shader=sh))
        for (u, v, rr) in self.stars:
            cv.drawCircle(x0 + u * (x1 - x0), y0 + v * (y1 - y0) * 0.6, rr, fillp("#cfd8ff", 0.6))
        # луна
        glow(cv, x1 - 70, y0 + 80, 120, "#9fb2e0", 0.35, blend=skia.BlendMode.kSrcOver)
        fill(cv, circle(x1 - 70, y0 + 80, 30), "#e6e3d2")
        fill(cv, circle(x1 - 60, y0 + 74, 26), "#1d2a44", 0.0)
        # лес и забор
        tree = [(x0, y1 - 70)]
        for i in range(14):
            xx = x0 + (x1 - x0) * i / 13
            tree += [(xx - 12, y1 - 80 - (i % 3) * 18), (xx, y1 - 125 - (i * 7) % 40), (xx + 12, y1 - 80 - (i % 2) * 14)]
        tree += [(x1, y1 - 70), (x1, y1), (x0, y1)]
        fill(cv, poly(tree), "#0b1018")
        for i in range(10):
            px = x0 + 10 + i * 36
            fill(cv, poly([(px, y1), (px, y1 - 70), (px + 10, y1 - 84), (px + 20, y1 - 70), (px + 20, y1)]), "#121a28")
        cv.drawRect(skia.Rect.MakeLTRB(x0, y1 - 52, x1, y1 - 42), fillp("#121a28"))
        # термометр за окном (крупный, с делениями)
        tx, ty = THERMO
        shape(cv, rrect(tx, ty, 50, 226, 10), "#e4e7ea", lw=3.5)
        fnt = font(BLACK, 13)
        for k, val in enumerate((40, 30, 20, 10, 0, -10, -20)):
            yy = ty + 26 + k * 27
            cv.drawLine(tx + 30, yy, tx + 42, yy, strokep("#3a3a3a", 2))
            text(cv, ("+" if val > 0 else "") + str(val), tx + 33, yy - 3, fnt, "#2a2a2a", align="right")
        temp = st.get("thermo", 30)
        top = ty + 26 + (40 - temp) / 10 * 27
        shape(cv, rrect(tx + 34, top, 8, ty + 205 - top, 4), "#d8281e", lw=2)
        shape(cv, circle(tx + 38, ty + 206, 10), "#d8281e", lw=2.5)
        if st.get("creature") is not None:
            st["creature"](cv)
        cv.restore()

    def glass(self, cv, st):
        x0, y0, x1, y1 = WIN
        cv.save()
        cv.clipRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), True)
        # блики на стекле
        for i, (ox, w) in enumerate(((40, 26), (90, 10), (210, 18))):
            p = poly([(x0 + ox, y1), (x0 + ox + w, y1), (x0 + ox + w + 180, y0), (x0 + ox + 180, y0)])
            cv.drawPath(p, fillp("#cfd8ea", 0.07))
        fog = st.get("fog", 0.0)
        if fog > 0:
            cv.drawOval(skia.Rect.MakeLTRB(x0 + 90, y0 + 210, x1 - 90, y1 - 20), fillp("#dfe6f0", 0.18 * fog, blur=30))
        fr = st.get("frost", 0.0)
        if fr > 0:
            self.draw_frost(cv, (x0, y0, x1, y1), fr, seed_off=0)
        cv.restore()

    def draw_frost(self, cv, box, amount, seed_off=0):
        x0, y0, x1, y1 = box
        m = min(x1 - x0, y1 - y0) * (0.12 + 0.22 * amount)
        a = 0.38 * amount
        for (p0, p1, rr) in (((x0, 0), (x0 + m, 0), (x0, y0, x0 + m, y1)), ((x1, 0), (x1 - m, 0), (x1 - m, y0, x1, y1)),
                             ((0, y0), (0, y0 + m), (x0, y0, x1, y0 + m)), ((0, y1), (0, y1 - m), (x0, y1 - m, x1, y1))):
            sh = lin_grad(p0, p1, [("#e6f0ff", a), ("#e6f0ff", 0.0)])
            cv.drawRect(skia.Rect.MakeLTRB(*rr), skia.Paint(Shader=sh))
        p = strokep("#f2f8ff", 2.2, 0.7)
        p2 = strokep("#ffffff", 6.0, 0.1)
        k = 0.8 + 0.9 * amount
        for i, (side, u, thr, segs) in enumerate(self.frost):
            if thr > amount * 1.25:
                continue
            if side == "l":
                bx, by = x0, y0 + u * (y1 - y0)
            elif side == "r":
                bx, by = x1, y0 + u * (y1 - y0)
            elif side == "t":
                bx, by = x0 + u * (x1 - x0), y0
            else:
                bx, by = x0 + u * (x1 - x0), y1
            for (ax, ay, bx2, by2, s) in segs:
                cv.drawLine(bx + ax * k, by + ay * k, bx + bx2 * k, by + by2 * k, p)
                cv.drawLine(bx + ax * k, by + ay * k, bx + bx2 * k, by + by2 * k, p2)

    def gap(self, cv, st, t):
        gx0, gy0, gx1, gy1 = GAP
        cv.drawPicture(self.p_gapback)
        if st.get("eyes") is not None:
            cv.save()
            cv.clipRect(skia.Rect.MakeLTRB(gx0, gy0, gx1, gy1), True)
            st["eyes"](cv)
            cv.restore()
        # занавеска (покачивается)
        sway = st.get("sway", 0.0)
        hem_y = 905
        pts = [(gx0 - 10, 545), (gx1 + 12, 545)]
        n = 7
        for i in range(n, -1, -1):
            xx = gx0 - 10 + (gx1 - gx0 + 22) * i / n
            dx = sway * 14 * math.sin(t * 2.3 + i * 0.8) * (1 if i > 0 else 0.3)
            pts.append((xx + dx, hem_y + (16 if i % 2 else 0) + sway * 6 * math.sin(t * 3 + i)))
        cur = smooth(pts, t=0.25)
        shape(cv, cur, "#8a3c36", lw=4.5)
        cv.save()
        cv.clipPath(cur, skia.ClipOp.kIntersect, True)
        for i in range(8):
            xx = gx0 - 5 + i * 20
            cv.drawLine(xx, 545, xx + sway * 8 * math.sin(t * 2.3 + i), hem_y + 10, strokep("#6e2c28", 6, 0.6))
        for i in range(6):
            for j in range(16):
                cv.drawCircle(gx0 + i * 26 + (13 if j % 2 else 0), 565 + j * 22, 3, fillp("#e8dccb", 0.8))
        cv.restore()
        stroke(cv, line_path(gx0 - 20, 545, gx1 + 22, 545), "#2a2018", 7)

    def clock(self, cv, st, t):
        cx, cy = CLOCK
        Style.lw = 4.5
        body = poly([(cx - 66, cy + 45), (cx, cy - 10), (cx + 66, cy + 45), (cx + 62, cy + 180), (cx - 62, cy + 180)])
        shape(cv, body, "#7a5a3c")
        shape(cv, rect(cx - 52, cy + 50, 104, 120), "#5c4129", lw=3.5)
        # кот
        shape(cv, poly([(cx - 24, cy + 52), (cx - 30, cy + 24), (cx - 10, cy + 40)]), "#26262a", lw=3.5)
        shape(cv, poly([(cx + 24, cy + 52), (cx + 30, cy + 24), (cx + 10, cy + 40)]), "#26262a", lw=3.5)
        shape(cv, ellipse(cx, cy + 62, 30, 24), "#26262a", lw=3.5)
        ph = math.sin(2 * math.pi * t / 1.0)
        for sx in (-1, 1):
            fill(cv, ellipse(cx + sx * 11, cy + 60, 7.5, 6), "#f2e7a0")
            fill(cv, ellipse(cx + sx * 11 + ph * 3.5, cy + 60, 2.6, 5), "#111111")
        fill(cv, poly([(cx - 3, cy + 70), (cx + 3, cy + 70), (cx, cy + 74)]), "#d77a8a")
        # циферблат
        dial_y = cy + 128
        shape(cv, circle(cx, dial_y, 36), "#efe9da", lw=4)
        for k in range(12):
            a = math.radians(k * 30)
            cv.drawLine(cx + 28 * math.sin(a), dial_y - 28 * math.cos(a), cx + 33 * math.sin(a), dial_y - 33 * math.cos(a), strokep("#333333", 2.5))
        hh, mm = st.get("time", (23, 58))
        am = math.radians(mm * 6)
        ah = math.radians((hh % 12) * 30 + mm * 0.5)
        cv.drawLine(cx, dial_y, cx + 17 * math.sin(ah), dial_y - 17 * math.cos(ah), strokep("#1a1a1a", 4.5))
        cv.drawLine(cx, dial_y, cx + 27 * math.sin(am), dial_y - 27 * math.cos(am), strokep("#1a1a1a", 3))
        fill(cv, circle(cx, dial_y, 3.5), "#1a1a1a")
        # маятник
        ang = 0.0 if st.get("pendulum_stop") else 11 * math.sin(2 * math.pi * t / 1.0)
        cv.save()
        cv.rotate(ang, cx, cy + 182)
        stroke(cv, line_path(cx, cy + 182, cx, cy + 300), "#2a2a2a", 4)
        shape(cv, circle(cx, cy + 305, 15), "#c9a24a", lw=3.5)
        cv.restore()
        # гири на цепочках
        for sx, ln in ((-1, 290), (1, 330)):
            xx = cx + sx * 26
            for yy in range(int(cy + 182), int(cy + ln), 9):
                cv.drawOval(skia.Rect.MakeLTRB(xx - 2.5, yy, xx + 2.5, yy + 8), strokep("#5a5a5a", 1.8))
            cone = smooth([(xx, cy + ln - 4), (xx + 11, cy + ln + 18), (xx + 9, cy + ln + 50), (xx, cy + ln + 58), (xx - 9, cy + ln + 50), (xx - 11, cy + ln + 18)], t=0.4)
            shape(cv, cone, "#4a4440", lw=3.5)

    def door(self, cv, st, t):
        dx0, dy0, dx1, dy1 = DOOR
        shake = st.get("door_shake", 0.0)
        open_a = st.get("door_open", 0.0)  # 0 закрыто, 1 открыто (~75°)
        cv.save()
        # проём (видно, когда дверь открыта)
        if open_a > 0.001:
            sh = lin_grad((0, dy0), (0, dy1), ["#0b1220", "#18233a"])
            cv.drawRect(skia.Rect.MakeLTRB(dx0, dy0, dx1, dy1), skia.Paint(Shader=sh))
            cv.drawRect(skia.Rect.MakeLTRB(dx0, dy1 - 140, dx1, dy1), fillp("#1b2130"))
            for (fx, fy) in ((2150, 900), (2320, 1050), (2230, 760), (2390, 820)):
                a = 0.5 + 0.5 * math.sin(t * 3 + fx)
                glow(cv, fx, fy, 14, "#e8f08a", 0.7 * a)
            if st.get("doorway") is not None:
                st["doorway"](cv)
        # полотно
        ang = open_a * 78
        sx = math.cos(math.radians(ang))
        cv.translate(shake, 0)
        cv.save()
        # петли справа: сжимаем полотно к правому краю и «выдвигаем» к камере
        cv.translate(dx1, 0)
        cv.scale(-1 if sx < 0 else 1, 1)
        cv.scale(max(abs(sx), 0.001), 1)
        cv.translate(-dx1, 0)
        Style.lw = 5.0 / max(abs(sx), 0.35)
        leaf = rect(dx0, dy0, dx1 - dx0, dy1 - dy0)
        shape(cv, leaf, "#684833")
        cv.save()
        cv.clipPath(leaf, skia.ClipOp.kIntersect, True)
        pw = (dx1 - dx0) / 6
        for i in range(6):
            col = "#6c4b35" if i % 2 else "#624431"
            cv.drawRect(skia.Rect.MakeLTRB(dx0 + i * pw, dy0, dx0 + (i + 1) * pw, dy1), fillp(col))
            cv.drawLine(dx0 + i * pw, dy0, dx0 + i * pw, dy1, strokep("#2c1e15", 4))
            r = _rng(100 + i)
            for _ in range(6):
                gy = r.uniform(dy0, dy1)
                cv.drawLine(dx0 + i * pw + r.uniform(8, 20), gy, dx0 + i * pw + r.uniform(8, 20) + r.uniform(-4, 4), gy + r.uniform(60, 160), strokep("#4e3424", 2.2, 0.7))
        cv.restore()
        for (by0, by1) in ((618, 664), (1288, 1334)):
            shape(cv, rect(dx0, by0, dx1 - dx0, by1 - by0), "#55392a")
        shape(cv, poly([(dx0 + 30, 1288), (dx0 + 72, 1288), (dx1 - 30, 664), (dx1 - 72, 664)]), "#5a3c2b")
        for hy in (640, 1310):
            shape(cv, poly([(dx1, hy - 13), (dx1 - 190, hy - 7), (dx1 - 215, hy), (dx1 - 190, hy + 7), (dx1, hy + 13)]), "#2f2f31", lw=Style.lw * 0.7)
            for k in range(3):
                fill(cv, circle(dx1 - 40 - k * 55, hy, 4), "#5d5d60")
        # кольцо-ручка
        stroke(cv, circle(dx0 + 45, 1010, 22), "#2a2a2c", 9)
        fill(cv, circle(dx0 + 45, 988, 6), "#2a2a2c")
        # скобы засова на двери
        for bx in (2150, 2290):
            shape(cv, rect(bx, BOLT_Y - 16, 46, 14), "#2e2e30", lw=Style.lw * 0.7)
            shape(cv, rect(bx, BOLT_Y + 36, 46, 14), "#2e2e30", lw=Style.lw * 0.7)
        cv.restore()
        # засов (рисуем поверх, сдвигается вправо при открытии)
        if open_a < 0.01:
            bolt = st.get("bolt", 0.0)  # 0 — заперто, 1 — отодвинут
            bx = 2004 + 112 * bolt
            rattle = st.get("bolt_rattle", 0.0)
            Style.lw = 5.0
            shape(cv, rrect(bx, BOLT_Y - 2 + rattle, 330, 38, 6), "#8a6440")
            cv.drawLine(bx + 10, BOLT_Y + 8 + rattle, bx + 320, BOLT_Y + 8 + rattle, strokep("#a07a52", 3, 0.8))
            for bxx in (2150, 2290):
                shape(cv, rect(bxx, BOLT_Y - 16, 46, 14), "#2e2e30", lw=3.5)
            # иней по краям двери
            fr = st.get("door_frost", 0.0)
            if fr > 0:
                self.draw_frost(cv, (dx0, dy0, dx1, dy1), fr, seed_off=1)
        cv.restore()

    def lamp(self, cv, st, t, lit=1.0):
        x, y = LAMP
        Style.lw = 4.5
        shape(cv, ellipse(x, y - 22, 48, 26), "#9fb3a8")
        fill(cv, ellipse(x, y - 30, 30, 12), "#c4d4cb", 0.6)
        shape(cv, rrect(x - 22, y - 62, 44, 18, 4), "#b8923e")
        chim = smooth([(x - 14, y - 62), (x - 26, y - 100), (x - 12, y - 150), (x + 12, y - 150), (x + 26, y - 100), (x + 14, y - 62)], t=0.4)
        cv.drawPath(chim, fillp("#f4ead0", 0.35 + 0.35 * lit))
        stroke(cv, chim, OUT, 3.5)

    def candle(self, cv, x, y, t):
        Style.lw = 4
        shape(cv, ellipse(x, y, 34, 9), "#6a6560")
        shape(cv, rect(x - 10, y - 70, 20, 70), "#efe6cf")


# ================================================================== эмиссия (после света)
def flame(cv, x, y, s, t, seed=0.0):
    f = 1 + 0.12 * math.sin(t * 19 + seed) * math.sin(t * 7.1 + seed * 2)
    glow(cv, x, y, 90 * s, "#ffb052", 0.55)
    p = smooth([(x, y - 30 * s * f), (x + 9 * s, y - 6 * s), (x + 6 * s, y + 6 * s), (x - 6 * s, y + 6 * s), (x - 9 * s, y - 6 * s)], t=0.5)
    cv.drawPath(p, fillp("#ffcf6a"))
    cv.drawPath(ellipse(x, y - 2 * s, 3.5 * s, 9 * s * f), fillp("#fff6d8"))


# ================================================================== ДЕРЕВНЯ
class Village:
    def __init__(self):
        r = _rng(9)
        self.stars = [(r.uniform(0, 1080), r.uniform(0, 700), r.uniform(0.8, 2.3)) for _ in range(70)]
        self.flies = [(r.uniform(0, 1080), r.uniform(1150, 1650), r.uniform(0, 6)) for _ in range(18)]
        self.p_static = _record(self._static, 1300, 2100)

    def _static(self, cv):
        Style.lw = 4.5
        sh = lin_grad((0, 0), (0, 1150), ["#151a2e", "#2c2b48", "#5a3f55", "#9a6158"], [0, 0.45, 0.8, 1])
        cv.drawRect(skia.Rect.MakeLTRB(-100, -100, 1200, 1200), skia.Paint(Shader=sh))
        for (x, y, rr) in self.stars:
            cv.drawCircle(x, y, rr, fillp("#e8e6ff", 0.75 * (1 - y / 800)))
        # луна
        glow(cv, 790, 360, 260, "#c9b9d8", 0.28, blend=skia.BlendMode.kSrcOver)
        fill(cv, circle(790, 360, 74), "#efe6cf")
        for (cx, cy, rr) in ((770, 340, 12), (815, 380, 9), (790, 395, 6)):
            fill(cv, circle(cx, cy, rr), "#d8cdb2")
        # дальний лес
        pts = [(-100, 1080)]
        r = _rng(3)
        x = -100
        while x < 1200:
            hgt = r.uniform(60, 150)
            pts += [(x + 18, 1060 - hgt * 0.4), (x + 30, 1060 - hgt), (x + 42, 1060 - hgt * 0.4)]
            x += r.uniform(30, 55)
        pts += [(1200, 1080), (1200, 1200), (-100, 1200)]
        fill(cv, poly(pts), "#1b1a28")
        cv.drawRect(skia.Rect.MakeLTRB(-100, 1040, 1200, 1120), fillp("#c8b9c8", 0.10, blur=18))
        # земля
        sh2 = lin_grad((0, 1080), (0, 2000), ["#2a2a30", "#1d1c20"])
        cv.drawRect(skia.Rect.MakeLTRB(-100, 1080, 1200, 2100), skia.Paint(Shader=sh2))
        # дорога
        road = poly([(500, 1085), (580, 1085), (900, 2100), (180, 2100)])
        fill(cv, road, "#4a3d33")
        for (a, b) in (((520, 1100), (330, 2100)), ((565, 1100), (760, 2100))):
            cv.drawLine(*a, *b, strokep("#3a2f27", 10, 0.8))
        fill(cv, ellipse(610, 1700, 90, 18), "#5a6280", 0.75)
        fill(cv, ellipse(420, 1450, 50, 10), "#5a6280", 0.6)
        # заброшенный дом справа
        shape(cv, poly([(690, 1180), (690, 930), (1110, 930), (1110, 1180)]), "#2a2422")
        shape(cv, poly([(660, 940), (890, 800), (1130, 950)]), "#211c1c")
        for (wx, wy) in ((760, 1010), (960, 1010)):
            shape(cv, rect(wx, wy, 90, 100), "#0e0d10")
            cv.drawLine(wx - 6, wy + 10, wx + 96, wy + 90, strokep("#3d3330", 12))
            cv.drawLine(wx - 6, wy + 90, wx + 96, wy + 10, strokep("#3d3330", 12))
        # бабушкин дом слева
        shape(cv, poly([(20, 1240), (20, 930), (470, 930), (470, 1240)]), "#5a3f30")
        for yy in range(945, 1240, 34):
            cv.drawLine(20, yy, 470, yy, strokep("#3e2b20", 3))
        shape(cv, poly([(-10, 945), (245, 760), (500, 945)]), "#3b2d2a")
        for k in range(8):
            cv.drawLine(-10 + k * 32, 945 - k * 23.3, 245 + k * 32, 760 + k * 23.3, strokep("#2c2220", 3, 0.6))
        shape(cv, rect(330, 760, 46, 120), "#4a3a34")
        # окно (тёплый свет)
        shape(cv, rect(170, 1010, 150, 140), "#ffcf7a")
        cv.drawLine(245, 1010, 245, 1150, strokep(OUT, 9))
        cv.drawLine(170, 1068, 320, 1068, strokep(OUT, 9))
        shape(cv, poly([(150, 1000), (245, 950), (340, 1000)]), "#c9d4de")
        shape(cv, rect(150, 1150, 190, 18), "#c9d4de")
        # забор
        for k in range(13):
            px = -20 + k * 46
            shape(cv, poly([(px, 1340), (px, 1215), (px + 14, 1198), (px + 28, 1215), (px + 28, 1340)]), "#6b5a4a" if k % 3 else "#5d4e40", lw=4)
        cv.drawRect(skia.Rect.MakeLTRB(-30, 1240, 590, 1256), fillp("#4d4035"))
        cv.drawRect(skia.Rect.MakeLTRB(-30, 1300, 590, 1316), fillp("#4d4035"))
        # табличка «ГЛУХОВО»
        shape(cv, rect(905, 1200, 16, 260), "#6b6b6b", lw=4)
        shape(cv, rect(760, 1120, 300, 110), "#efefe8", lw=5)
        stroke(cv, rect(772, 1132, 276, 86), "#1a1a1a", 5)
        text(cv, "ГЛУХОВО", 910, 1196, font(BLACK, 50), "#1a1a1a")
        for (rx, ry) in ((780, 1215), (1040, 1140), (1000, 1210)):
            fill(cv, circle(rx, ry, 6), "#8a5a3a", 0.7)
        # трава
        r = _rng(12)
        for _ in range(160):
            gx = r.uniform(-50, 1130)
            gy = r.uniform(1260, 2000)
            if 180 + (gy - 1085) * -0.3 < gx < 900 + (gy - 2100) * 0.3 and gy > 1100:
                continue
            hh = r.uniform(14, 40) * (gy / 1500)
            cv.drawLine(gx, gy, gx + r.uniform(-8, 8), gy - hh, strokep("#2f3a2a", 3, 0.9))

    def draw(self, cv, t, st):
        cv.drawPicture(self.p_static)
        # дым из трубы
        for k in range(5):
            ph = (t * 0.25 + k / 5) % 1.0
            sx = 353 + math.sin(ph * 6 + k) * 20 + ph * 60
            sy = 750 - ph * 380
            fill(cv, circle(sx, sy, 18 + ph * 40), "#b8b0c0", 0.2 * (1 - ph), blur=10 + ph * 14)
        # вороны на заборе
        for i, (vx, vy) in enumerate(((60, 1198), (474, 1198))):
            turn = 1 if (i == 1 and (t % 3.0) > 1.6) else -1
            Style.lw = 3.5
            shape(cv, ellipse(vx, vy - 22, 20, 15), "#121215")
            shape(cv, circle(vx + 14 * turn, vy - 40, 10), "#121215")
            fill(cv, poly([(vx + 22 * turn, vy - 42), (vx + 36 * turn, vy - 38), (vx + 22 * turn, vy - 35)]), "#3a3a3a")
            fill(cv, circle(vx + 17 * turn, vy - 42, 2.2), "#d8d8d8")
            shape(cv, poly([(vx - 18 * turn, vy - 22), (vx - 38 * turn, vy - 12), (vx - 16 * turn, vy - 12)]), "#121215")
        # светлячки
        for (fx, fy, ph) in self.flies:
            a = 0.5 + 0.5 * math.sin(t * 2.2 + ph)
            glow(cv, fx + 20 * math.sin(t * 0.5 + ph), fy + 10 * math.cos(t * 0.7 + ph), 16, "#e8f08a", 0.8 * a)
        # бабушка у калитки (машет)
        cv.save()
        cv.translate(330, 1330)
        cv.scale(1.25, 1.25)
        Style.lw = 4.0 / 1.25
        chars.granny(cv, arms="wave", eyes="kind", t=t, wave_t=t)
        cv.restore()
        # мальчик идёт по дороге (спиной, с рюкзаком)
        walk = st.get("walk", 0.0)
        bob = abs(math.sin(t * 6.0)) * 6
        bx = 560 - walk * 60
        by = 1880 - walk * 120 - bob
        s = 2.9 - walk * 0.4
        cv.save()
        cv.translate(bx, by)
        cv.scale(s, s)
        Style.lw = 4.5 / s
        chars.boy_back(cv, pack=True, t=t)
        cv.restore()
