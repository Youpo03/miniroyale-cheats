# -*- coding: utf-8 -*-
"""Огород за избой (день / сумерки / ночь), вид из окна, вороны, интерфейс телефона."""
import math
import random

import skia

import chars
from gfx import (OUT, Style, C, BLACK, BOLD, arc_path, circle, ellipse, fill, fillp, font, glow, lin_grad, line_path, poly,
                 rect, rrect, shape, smooth, stroke, strokep, text)

W, H = 1080, 1920
VP = (540, 870)  # точка схода грядок

PAL = {
    "day": dict(sky=["#8f9ba8", "#b7bfc4", "#d6d5cc"], forest="#34423a", field="#7a845e", dirt="#6b5340", furrow="#4e3b2d",
                bush="#58733f", bush_sh="#3f5630", fence="#857360", fence_sh="#6a5a49", grass="#4f6239", banya="#5d4535"),
    "dusk": dict(sky=["#1d2036", "#4a3a55", "#8e5a55"], forest="#17171f", field="#3a3530", dirt="#3a2e28", furrow="#2a211c",
                 bush="#2f3d2a", bush_sh="#232d1f", fence="#4e4338", fence_sh="#3b3229", grass="#262e20", banya="#2e2420"),
    "night": dict(sky=["#0a0f1a", "#131c30", "#1d2a42"], forest="#090c12", field="#1a2028", dirt="#1c1a1c", furrow="#121012",
                  bush="#18211c", bush_sh="#101612", fence="#2c2a2c", fence_sh="#1f1d1f", grass="#141a14", banya="#1a1616"),
}

# позиции пугала по дням: (x, y-земли, масштаб)
SC_POS = {0: (700, 928, 0.40), 1: (452, 1118, 0.92), 2: (560, 1540, 2.05), "mid": (590, 1210, 1.15)}


def crow(cv, x, y, s=1.0, turn=1, t=0.0):
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    Style.lw = 3.5 / s
    shape(cv, ellipse(0, -22, 20, 15), "#121215")
    shape(cv, circle(14 * turn, -40, 10), "#121215")
    fill(cv, poly([(22 * turn, -42), (36 * turn, -38), (22 * turn, -35)]), "#3a3a3a")
    fill(cv, circle(17 * turn, -42, 2.2), "#d8d8d8")
    shape(cv, poly([(-18 * turn, -22), (-38 * turn, -12), (-16 * turn, -12)]), "#121215")
    for k in (-5, 5):
        cv.drawLine(k, -8, k + 2, 2, strokep("#121215", 2.5))
    cv.restore()


class Garden:
    def __init__(self):
        self.pics = {tod: self._record(tod) for tod in PAL}
        r = random.Random(4)
        self.clouds = [(r.uniform(-100, 1180), r.uniform(80, 600), r.uniform(120, 260), r.uniform(30, 60)) for _ in range(9)]

    def _record(self, tod):
        rec = skia.PictureRecorder()
        c = rec.beginRecording(skia.Rect(-200, -200, W + 200, H + 200))
        self._static(c, tod)
        return rec.finishRecordingAsPicture()

    def _static(self, cv, tod):
        p = PAL[tod]
        Style.lw = 4.0
        sh = lin_grad((0, -200), (0, 900), p["sky"], [0, 0.6, 1])
        cv.drawRect(skia.Rect.MakeLTRB(-200, -200, W + 200, 920), skia.Paint(Shader=sh))
        if tod != "day":
            r = random.Random(2)
            for _ in range(60):
                cv.drawCircle(r.uniform(-100, 1180), r.uniform(-150, 650), r.uniform(0.8, 2.2), fillp("#e8e6ff", 0.6))
            glow(cv, 820, 330, 220, "#c9b9d8", 0.25, blend=skia.BlendMode.kSrcOver)
            fill(cv, circle(820, 330, 58), "#efe6cf" if tod == "dusk" else "#dcdfe8")
        # лес
        r = random.Random(3)
        pts = [(-200, 900)]
        x = -200
        while x < W + 200:
            hgt = r.uniform(70, 170)
            pts += [(x + 18, 880 - hgt * 0.4), (x + 30, 880 - hgt), (x + 42, 880 - hgt * 0.4)]
            x += r.uniform(30, 55)
        pts += [(W + 200, 900), (W + 200, 960), (-200, 960)]
        fill(cv, poly(pts), p["forest"])
        cv.drawRect(skia.Rect.MakeLTRB(-200, 880, W + 200, 935), fillp(p["field"]))
        if tod == "day":
            cv.drawRect(skia.Rect.MakeLTRB(-200, 850, W + 200, 930), fillp("#dfe2e0", 0.25, blur=20))
        # земля огорода
        cv.drawRect(skia.Rect.MakeLTRB(-200, 925, W + 200, H + 200), fillp(p["dirt"]))
        for bx in range(-1400, 2600, 210):
            cv.drawLine(VP[0], VP[1], bx, H + 200, strokep(p["furrow"], 9))
        # кусты картошки вдоль грядок
        r = random.Random(7)
        for bx in range(-1295, 2600, 210):
            u = 0.07
            while u < 1.05:
                x = VP[0] + (bx - VP[0]) * u
                y = VP[1] + (H + 200 - VP[1]) * u
                if y > 930 and -60 < x < W + 60:
                    s = 0.15 + 1.25 * u
                    for (dx, dy, rr) in ((-14, 0, 15), (12, -2, 14), (0, -12, 16)):
                        cv.drawCircle(x + dx * s, y - 10 * s + dy * s, rr * s, fillp(p["bush"]))
                    cv.drawCircle(x + 6 * s, y - 6 * s, 9 * s, fillp(p["bush_sh"]))
                    cv.drawPath(ellipse(x, y - 8 * s, 30 * s, 22 * s), strokep(OUT, max(0.8, 2.2 * s), 0.5))
                u += 0.05 + 0.13 * u
        # баня
        b = p["banya"]
        shape(cv, rect(120, 1000, 230, 120), b)
        for yy in range(1012, 1120, 18):
            cv.drawLine(120, yy, 350, yy, strokep(OUT, 2, 0.6))
        shape(cv, poly([(100, 1006), (235, 930), (370, 1006)]), "#2f2620" if tod == "day" else "#1a1512")
        shape(cv, rect(280, 900, 24, 60), "#3a302a")
        shape(cv, rect(160, 1040, 40, 30), "#1b1a1d" if tod == "day" else "#120f10")
        shape(cv, rect(240, 1030, 50, 90), "#3a2c22")

    def fence(self, cv, tod, y0=1440, y1=1625):
        p = PAL[tod]
        Style.lw = 4.0
        for k in range(-1, 21):
            px = -10 + k * 56
            col = p["fence"] if k % 3 else p["fence_sh"]
            shape(cv, poly([(px, y1), (px, y0 + 12), (px + 15, y0 - 6), (px + 30, y0 + 12), (px + 30, y1)]), col)
        cv.drawRect(skia.Rect.MakeLTRB(-60, y0 + 50, W + 60, y0 + 68), fillp(p["fence_sh"]))
        cv.drawRect(skia.Rect.MakeLTRB(-60, y1 - 60, W + 60, y1 - 42), fillp(p["fence_sh"]))
        cv.drawRect(skia.Rect.MakeLTRB(-60, y1, W + 60, H + 200), fillp(p["grass"]))
        r = random.Random(11)
        for _ in range(140):
            gx = r.uniform(-40, W + 40)
            gy = r.uniform(y1 + 10, H + 100)
            cv.drawLine(gx, gy, gx + r.uniform(-9, 9), gy - r.uniform(18, 46), strokep("#2c3a24" if tod == "day" else "#11160f", 3, 0.9))

    def draw(self, cv, t, tod="day", sc=None, crows=True, fence=True):
        """sc: dict(pos=(x,y,s), mode, face, smile, sway) или None."""
        cv.drawPicture(self.pics[tod])
        if tod == "day":
            for (x, y, w, h) in self.clouds:
                xx = (x + t * 6) % (W + 400) - 200
                cv.drawOval(skia.Rect.MakeLTRB(xx - w, y - h, xx + w, y + h), fillp("#e7eaec", 0.35, blur=25))
        if sc is not None:
            x, y, s = sc["pos"]
            cv.save()
            cv.translate(x, y)
            cv.scale(s, s)
            Style.lw = 4.2 / s
            chars.scarecrow(cv, mode=sc.get("mode", "pole"), face=sc.get("face", "front"), smile=sc.get("smile", 0.0),
                            t=t, sway=sc.get("sway", 0.0) * math.sin(t * 1.3))
            cv.restore()
        if fence:
            self.fence(cv, tod)
        if crows:
            turn = 1 if (t % 3.2) > 1.7 else -1
            crow(cv, 158, 1438, 1.25, turn, t)
            crow(cv, 886, 1438, 1.2, -1, t)


def window_pov(cv, t, frost=0.0, label=None, label_a=1.0):
    """Изнутри избы: стена, окно на огород, рама с переплётом (рисуется поверх огорода)."""
    x0, y0, x1, y1 = 110, 300, 970, 1470
    wall = skia.Path()
    wall.addRect(skia.Rect.MakeLTRB(-200, -200, W + 200, H + 200))
    wall.addRect(skia.Rect.MakeLTRB(x0, y0, x1, y1))
    wall.setFillType(skia.PathFillType.kEvenOdd)
    cv.drawPath(wall, fillp("#3d2b20"))
    cv.save()
    cv.clipPath(wall, skia.ClipOp.kIntersect, True)
    y = -200
    k = 0
    while y < H + 200:
        cv.drawRect(skia.Rect.MakeLTRB(-200, y, W + 200, y + 90), fillp("#4a3426" if k % 2 else "#45301f"))
        cv.drawLine(-200, y, W + 200, y, strokep("#8a7458", 6, 0.8))
        cv.drawLine(-200, y + 4, W + 200, y + 4, strokep("#21160f", 3, 0.8))
        y += 90
        k += 1
    cv.restore()
    Style.lw = 5.0
    blue = "#c9d4de"
    frame = skia.Path()
    frame.addRect(skia.Rect.MakeLTRB(x0 - 46, y0 - 46, x1 + 46, y1 + 46))
    frame.addRect(skia.Rect.MakeLTRB(x0, y0, x1, y1))
    frame.setFillType(skia.PathFillType.kEvenOdd)
    shape(cv, frame, blue)
    # блики на стекле
    for (ox, w) in ((60, 40), (140, 14), (330, 26)):
        cv.drawPath(poly([(x0 + ox, y1), (x0 + ox + w, y1), (x0 + ox + w + 380, y0), (x0 + ox + 380, y0)]), fillp("#ffffff", 0.05))
    shape(cv, rect((x0 + x1) / 2 - 12, y0, 24, y1 - y0), blue, lw=4)
    shape(cv, rect(x0, 760, x1 - x0, 22), blue, lw=4)
    # кружевной ламбрекен
    lace = [(x0, y0), (x1, y0), (x1, y0 + 70)]
    n = 16
    for i in range(n, -1, -1):
        lace.append((x0 + (x1 - x0) * i / n, y0 + 70 + (20 if i % 2 else 0)))
    cv.drawPath(poly(lace), fillp("#efeae0", 0.9))
    for i in range(n):
        cv.drawCircle(x0 + (x1 - x0) * (i + 0.5) / n, y0 + 36, 7, fillp("#b9b2a5", 0.8))
    stroke(cv, poly(lace), "#9c958a", 3)
    shape(cv, rect(x0 - 60, y1 + 30, x1 - x0 + 120, 40), "#d9e1e8")
    if label:
        f = font(BLACK, 76)
        text(cv, label, W / 2, 210, f, "#ffffff", label_a, outline="#000000", ow=14, shadow=12)


def phone(cv, cx, cy, w, h, r=46, body="#141519"):
    """Корпус телефона (вертикальный или горизонтальный), возвращает прямоугольник экрана."""
    Style.lw = 5.0
    cv.drawPath(rrect(cx - w / 2 + 8, cy - h / 2 + 16, w, h, r), fillp("#000000", 0.5, blur=18))
    shape(cv, rrect(cx - w / 2, cy - h / 2, w, h, r), body)
    m = 18
    return (cx - w / 2 + m, cy - h / 2 + m, cx + w / 2 - m, cy + h / 2 - m)
