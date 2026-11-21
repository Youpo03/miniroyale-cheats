# -*- coding: utf-8 -*-
"""Персонажи: мальчик (спереди/сзади), бабушка, «не-бабушка» в окне, глаза за печкой."""
import math

import skia

from gfx import (OUT, Style, arc_path, circle, ellipse, fill, fillp, glow, line_path, poly, rrect, shape, smooth,
                 stroke, strokep)

# мальчик
SKIN = "#f1c8a3"
SKIN_SH = "#d9a582"
HAIR = "#3b2a21"
SW_A = "#d0a040"
SW_B = "#8a5f2e"
SHORTS = "#4b5160"
PACK = "#4a6340"
# бабушка
G_SCARF = "#2e5b57"
G_SCARF_SH = "#234643"
G_DOT = "#e3b54c"
G_SKIN = "#ebc39f"
G_CARD = "#6b5a52"
G_SKIRT = "#7b3535"
G_APRON = "#d8cfb7"
G_SHOE = "#2a2523"
NOSE = "#e2a98a"


def _arm(cv, pts, col, w):
    p = poly(pts, close=False)
    cv.drawPath(p, strokep(OUT, w + 2 * Style.lw))
    cv.drawPath(p, strokep(col, w))


def _hand(cv, x, y, r=7.0, col=SKIN):
    shape(cv, circle(x, y, r), col)


ARM_POSES = {
    "down": [((-30, -110), (-39, -88), (-38, -66)), ((30, -110), (39, -88), (38, -66))],
    "scared": [((-30, -110), (-42, -92), (-20, -126)), ((30, -110), (42, -92), (20, -126))],
    "reach": [((-30, -110), (-39, -88), (-38, -66)), ((30, -110), (50, -112), (70, -128))],
    "hug": [((-30, -110), (-38, -92), (14, -94)), ((30, -110), (38, -92), (-14, -98))],
    "phone": [((-30, -110), (-39, -88), (-38, -66)), ((30, -110), (44, -96), (26, -120))],
}


# ================================================================== МАЛЬЧИК
def boy_front(cv, look=0.0, eyes="normal", mouth=0.0, blink=0.0, arms="down", t=0.0, sweat=0.0,
              brows="calm", pupil=(0.0, 0.0), tremble=0.0, body=True):
    if body:
        for sx in (-1, 1):
            shape(cv, rrect(sx * 13 - 5, -54, 10, 50, 5), SKIN)
            shape(cv, ellipse(sx * 15, -4, 10, 5.5), SKIN)
        shape(cv, smooth([(-31, -72), (31, -72), (34, -44), (5, -42), (0, -52), (-5, -42), (-34, -44)], t=0.15), SHORTS)
        torso = smooth([(-29, -119), (29, -119), (37, -102), (35, -62), (-35, -62), (-37, -102)], t=0.3)
        cv.drawPath(torso, fillp(SW_A))
        cv.save()
        cv.clipPath(torso, skia.ClipOp.kIntersect, True)
        for y in range(-110, -60, 13):
            cv.drawRect(skia.Rect.MakeXYWH(-45, y, 90, 5.5), fillp(SW_B))
        cv.restore()
        stroke(cv, torso, OUT)
        # горловина
        shape(cv, ellipse(0, -118, 13, 5), SW_B)
        for side in ARM_POSES[arms]:
            _arm(cv, side, SW_A, 15)
            _hand(cv, *side[-1])
    # шея
    shape(cv, rrect(-7, -126, 14, 12, 4), SKIN, lw=Style.lw * 0.8)
    boy_head(cv, look, eyes, mouth, blink, t, sweat, brows, pupil, tremble)


def boy_head(cv, look=0.0, eyes="normal", mouth=0.0, blink=0.0, t=0.0, sweat=0.0, brows="calm",
             pupil=(0.0, 0.0), tremble=0.0):
    hx, hy = 0.0, -154.0
    tx = tremble * math.sin(t * 61.0) * 0.8
    cv.save()
    cv.translate(tx, 0)
    # уши
    for sx in (-1, 1):
        shape(cv, circle(hx + sx * 40 - look * 3, hy + 3, 9.5), SKIN)
        stroke(cv, arc_path(hx + sx * 40 - look * 3, hy + 3, 4.5, 4.5, 200 if sx < 0 else -20, 340 if sx < 0 else 120), SKIN_SH, Style.lw * 0.6)
    shape(cv, ellipse(hx, hy, 41, 38.5), SKIN)
    # волосы
    hair = smooth([(-43, -150), (-45, -170), (-37, -187), (-21, -196), (0, -198), (21, -196), (37, -187), (45, -170),
                   (43, -150), (39, -160), (31, -165), (25, -158), (17, -168), (7, -161), (-3, -170), (-12, -161),
                   (-22, -168), (-30, -159), (-37, -164)], t=0.35)
    cv.save()
    cv.translate(look * 2.5, 0)
    shape(cv, hair, HAIR)
    shape(cv, smooth([(2, -196), (8, -212), (16, -205), (12, -195)], t=0.4), HAIR, lw=Style.lw * 0.8)
    cv.restore()
    fx = look * 11.0
    ey = hy + 4
    # румянец и веснушки
    for sx in (-1, 1):
        fill(cv, ellipse(hx + fx + sx * 25, ey + 14, 7.5, 4.2), "#e98f7a", 0.35)
        for k, (dx, dy) in enumerate(((-4, 0), (2, -3), (3, 3))):
            fill(cv, circle(hx + fx + sx * 25 + dx, ey + 12 + dy, 1.1), "#b77556", 0.8)
    # глаза
    lw0 = Style.lw
    for sx in (-1, 1):
        ex = hx + fx + sx * 15
        if eyes == "scared":
            shape(cv, circle(ex, ey, 11.5), "#ffffff", lw=lw0 * 0.75)
            jx = math.sin(t * 37 + sx) * 0.9 * (0.5 + tremble)
            jy = math.cos(t * 41 + sx) * 0.7 * (0.5 + tremble)
            fill(cv, circle(ex + pupil[0] * 5 + jx, ey + pupil[1] * 5 + jy, 2.7), "#111111")
        else:
            ry = 6.6 * (1.0 - 0.92 * blink)
            fill(cv, ellipse(ex + pupil[0] * 2, ey + pupil[1] * 2, 4.9, max(0.6, ry)), "#15100e")
            if blink < 0.5:
                fill(cv, circle(ex + pupil[0] * 2 + 1.6, ey + pupil[1] * 2 - 2.4, 1.5), "#ffffff")
    # брови
    for sx in (-1, 1):
        ex = hx + fx + sx * 15
        if brows == "calm":
            p = arc_path(ex, ey - 12, 7, 3, 200, 340)
        elif brows == "worried":
            p = line_path(ex - sx * 7, ey - 14, ex + sx * 6, ey - 19)
        else:  # high / scared
            p = line_path(ex - sx * 7, ey - 20, ex + sx * 7, ey - 25)
        stroke(cv, p, HAIR, Style.lw * 0.9)
    # нос
    stroke(cv, arc_path(hx + fx * 1.15, ey + 10, 3.5, 2.5, 20, 160), SKIN_SH, Style.lw * 0.7)
    # рот
    mx, my = hx + fx, ey + 24
    if mouth > 0.08:
        shape(cv, ellipse(mx, my, 4.5 + 2.5 * mouth, 3.0 + 6.5 * mouth), "#4a1b17", lw=Style.lw * 0.75)
    else:
        if eyes == "scared":
            p = smooth([(mx - 7, my + 1.5), (mx, my - 1.5), (mx + 7, my + 1.5)], close=False)
        else:
            p = smooth([(mx - 7, my - 1), (mx, my + 2.5), (mx + 7, my - 1)], close=False)
        stroke(cv, p, "#5a2a20", Style.lw * 0.75)
    # капля пота
    if sweat > 0.01:
        sx_, sy_ = hx + 38, hy - 14 + 12 * sweat
        drop = smooth([(sx_, sy_ - 11), (sx_ + 6, sy_ + 2), (sx_, sy_ + 8), (sx_ - 6, sy_ + 2)], t=0.6)
        shape(cv, drop, "#9fd0ef", lw=Style.lw * 0.7, a=min(1.0, sweat * 3))
    cv.restore()


def boy_back(cv, arms="down", pack=False, t=0.0, look=0.0):
    for sx in (-1, 1):
        shape(cv, rrect(sx * 13 - 5, -54, 10, 50, 5), SKIN)
        shape(cv, ellipse(sx * 15, -4, 10, 5.5), SKIN)
    shape(cv, smooth([(-31, -72), (31, -72), (34, -44), (5, -42), (0, -48), (-5, -42), (-34, -44)], t=0.15), SHORTS)
    torso = smooth([(-29, -119), (29, -119), (37, -102), (35, -62), (-35, -62), (-37, -102)], t=0.3)
    cv.drawPath(torso, fillp(SW_A))
    cv.save()
    cv.clipPath(torso, skia.ClipOp.kIntersect, True)
    for y in range(-110, -60, 13):
        cv.drawRect(skia.Rect.MakeXYWH(-45, y, 90, 5.5), fillp(SW_B))
    cv.restore()
    stroke(cv, torso, OUT)
    poses = ARM_POSES["down"] if arms != "reach" else [((-30, -110), (-39, -88), (-38, -66)), ((30, -110), (48, -126), (58, -150))]
    for side in poses:
        _arm(cv, side, SW_A, 15)
        _hand(cv, *side[-1])
    if pack:
        shape(cv, rrect(-26, -116, 52, 58, 12), PACK)
        shape(cv, rrect(-26, -116, 52, 24, 10), "#5b774f")
        shape(cv, rrect(-10, -84, 20, 14, 4), "#3c5234", lw=Style.lw * 0.7)
    shape(cv, rrect(-7, -126, 14, 12, 4), SKIN, lw=Style.lw * 0.8)
    hx, hy = look * 3, -154.0
    for sx in (-1, 1):
        shape(cv, circle(hx + sx * 40, hy + 3, 9.5), SKIN)
    shape(cv, ellipse(hx, hy, 41, 38.5), HAIR)
    shape(cv, smooth([(hx - 4, -190), (hx + 4, -206), (hx + 12, -198), (hx + 8, -188)], t=0.4), HAIR, lw=Style.lw * 0.8)
    for k in range(5):
        a = -150 + k * 25
        x0 = hx + 34 * math.cos(math.radians(a))
        y0 = hy + 32 * math.sin(math.radians(a))
        stroke(cv, line_path(x0, y0, x0 * 0.85 + hx * 0.15, y0 * 0.85 + hy * 0.15), "#2a1d17", Style.lw * 0.5)


# ================================================================== БАБУШКА
def _scarf_dots(cv, path, col=G_DOT, a=1.0, step=13.0, r=2.1, x0=-70, x1=70, y0=-215, y1=-110):
    cv.save()
    cv.clipPath(path, skia.ClipOp.kIntersect, True)
    p = fillp(col, a)
    y = y0
    row = 0
    while y < y1:
        x = x0 + (step / 2 if row % 2 else 0)
        while x < x1:
            cv.drawCircle(x, y, r, p)
            x += step
        y += step * 0.86
        row += 1
    cv.restore()


GRAN_ARMS = {
    "down": [((-36, -124), (-44, -102), (-14, -90)), ((36, -124), (44, -102), (14, -92))],
    "finger": [((-36, -124), (-44, -102), (-14, -90)), ((36, -124), (56, -122), (60, -152))],
    "lantern": [((-36, -124), (-44, -102), (-14, -90)), ((36, -124), (50, -102), (54, -84))],
    "wave": [((-36, -124), (-56, -134), (-62, -162)), ((36, -124), (44, -102), (14, -92))],
}


def granny(cv, arms="down", mouth=0.0, eyes="kind", look=0.0, t=0.0, blink=0.0, wave_t=0.0, lit_lantern=False):
    # обувь, юбка, фартук
    for sx in (-1, 1):
        shape(cv, ellipse(sx * 13, -5, 13, 6.5), G_SHOE)
    skirt = smooth([(-40, -94), (40, -94), (47, -40), (50, -7), (25, -4), (0, -7), (-25, -4), (-50, -7), (-47, -40)], t=0.25)
    shape(cv, skirt, G_SKIRT)
    apron = smooth([(-25, -92), (25, -92), (29, -40), (30, -16), (0, -14), (-30, -16), (-29, -40)], t=0.2)
    shape(cv, apron, G_APRON)
    shape(cv, rrect(-11, -62, 22, 15, 4), "#c9bea2", lw=Style.lw * 0.7)
    # кофта
    torso = smooth([(-37, -132), (37, -132), (45, -110), (42, -88), (-42, -88), (-45, -110)], t=0.3)
    shape(cv, torso, G_CARD)
    for y in (-122, -110, -98):
        fill(cv, circle(0, y, 2.3), "#cdbfae")
    # руки
    poses = GRAN_ARMS[arms]
    for i, side in enumerate(poses):
        pts = list(side)
        if arms == "wave" and i == 0:
            a = math.sin(wave_t * 9.0) * 10
            pts[-1] = (pts[-1][0] + a, pts[-1][1] + abs(a) * 0.2)
        _arm(cv, pts, G_CARD, 15)
        hx, hy = pts[-1]
        _hand(cv, hx, hy, 7.5, G_SKIN)
        if arms == "finger" and i == 1:
            shape(cv, rrect(hx - 2.6, hy - 22, 5.2, 18, 2.6), G_SKIN, lw=Style.lw * 0.75)
        if arms == "lantern" and i == 1:
            lantern(cv, hx, hy + 6, 1.0, lit_lantern, t)
    granny_head(cv, mouth, eyes, look, t, blink)


def granny_head(cv, mouth=0.0, eyes="kind", look=0.0, t=0.0, blink=0.0, x=0.0, y=0.0):
    cv.save()
    cv.translate(x, y)
    # платок (задняя часть + концы на плечи)
    scarf = smooth([(0, -201), (27, -196), (41, -178), (45, -152), (44, -132), (52, -120), (30, -116),
                    (8, -126), (-8, -126), (-30, -116), (-52, -120), (-44, -132), (-45, -152), (-41, -178), (-27, -196)], t=0.4)
    shape(cv, scarf, G_SCARF)
    _scarf_dots(cv, scarf)
    fx = look * 6
    # лицо
    face = ellipse(fx * 0.5, -154, 26, 28)
    shape(cv, face, G_SKIN)
    # кромка платка вокруг лица
    rim = arc_path(fx * 0.5, -154, 31, 33, 195, 345)
    stroke(cv, rim, OUT, Style.lw * 3.6)
    stroke(cv, rim, G_SCARF, Style.lw * 1.8)
    # узел под подбородком
    shape(cv, ellipse(fx * 0.3, -124, 9, 6.5), G_SCARF_SH)
    shape(cv, smooth([(fx * 0.3 + 4, -122), (fx * 0.3 + 14, -110), (fx * 0.3 + 8, -106), (fx * 0.3 + 1, -118)], t=0.3), G_SCARF_SH, lw=Style.lw * 0.8)
    shape(cv, smooth([(fx * 0.3 - 4, -122), (fx * 0.3 - 12, -108), (fx * 0.3 - 6, -105), (fx * 0.3 - 1, -118)], t=0.3), G_SCARF_SH, lw=Style.lw * 0.8)
    # морщины
    for dy in (-170, -166):
        stroke(cv, arc_path(fx * 0.5, dy + 22, 12, 4, 200, 340), "#c79c7a", Style.lw * 0.45)
    for sx in (-1, 1):
        stroke(cv, arc_path(fx + sx * 9, -141, 5, 7, 90 - sx * 60, 90 + sx * 10 if sx > 0 else 160), "#c79c7a", Style.lw * 0.45)
        fill(cv, ellipse(fx + sx * 16, -146, 6, 3.5), "#e48f78", 0.35)
    # глаза
    ey = -158
    for sx in (-1, 1):
        ex = fx + sx * 10
        if eyes == "kind":
            stroke(cv, arc_path(ex, ey + 2, 4.6, 4.0, 200, 340), "#2a1c16", Style.lw * 0.8)
        elif eyes == "stern":
            ry = 3.4 * (1 - 0.9 * blink)
            fill(cv, ellipse(ex, ey, 3.0, max(0.5, ry)), "#1a1311")
            stroke(cv, line_path(ex - sx * 6, ey - 10, ex + sx * 5, ey - 7), "#8f8880", Style.lw * 1.2)
        elif eyes == "worried":
            ry = 3.6 * (1 - 0.9 * blink)
            fill(cv, ellipse(ex, ey, 3.0, max(0.5, ry)), "#1a1311")
            stroke(cv, line_path(ex - sx * 6, ey - 7, ex + sx * 5, ey - 11), "#8f8880", Style.lw * 1.1)
        # гусиные лапки
        stroke(cv, line_path(ex + sx * 7, ey + 1, ex + sx * 11, ey - 1), "#c79c7a", Style.lw * 0.4)
        stroke(cv, line_path(ex + sx * 7, ey + 3, ex + sx * 11, ey + 4), "#c79c7a", Style.lw * 0.4)
    if eyes == "kind":
        for sx in (-1, 1):
            stroke(cv, arc_path(fx + sx * 10, ey - 8, 5, 2, 200, 340), "#8f8880", Style.lw * 1.0)
    # нос
    shape(cv, ellipse(fx * 1.15, -147, 6.2, 5.2), NOSE, lw=Style.lw * 0.75)
    # родинка
    fill(cv, circle(fx + 14, -137, 1.6), "#5a3a2a")
    # рот
    mx, my = fx * 1.05, -135
    if mouth > 0.08:
        shape(cv, ellipse(mx, my, 5.5 + 2.0 * mouth, 1.5 + 5.5 * mouth), "#4a1b17", lw=Style.lw * 0.7)
    else:
        stroke(cv, smooth([(mx - 7, my + 1), (mx, my - 0.5), (mx + 7, my + 1)], close=False), "#6a3426", Style.lw * 0.75)
    cv.restore()


def lantern(cv, x, y, s=1.0, lit=True, t=0.0):
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    stroke(cv, arc_path(0, 0, 9, 10, 180, 360), "#3d3a36", Style.lw * 0.9)
    shape(cv, rrect(-11, 2, 22, 6, 2), "#4a4640", lw=Style.lw * 0.7)
    glass = smooth([(-9, 8), (9, 8), (12, 22), (9, 36), (-9, 36), (-12, 22)], t=0.4)
    shape(cv, glass, "#f6d27a" if lit else "#6d6a60", lw=Style.lw * 0.7)
    if lit:
        flick = 1 + 0.15 * math.sin(t * 23) * math.sin(t * 7.3)
        fill(cv, ellipse(0, 24, 3.2, 6 * flick), "#fff4c8")
    for xx in (-6, 0, 6):
        stroke(cv, line_path(xx, 8, xx * 1.2, 36), "#3d3a36", Style.lw * 0.45)
    shape(cv, rrect(-12, 36, 24, 7, 2), "#4a4640", lw=Style.lw * 0.7)
    cv.restore()


# ================================================================== «НЕ-БАБУШКА» в окне
F_SKIN = "#b9c2b3"
F_SKIN_SH = "#8e9a8c"


def fake_face(cv, smile=0.0, t=0.0, eye_glint=1.0, tilt=0.0):
    """Локальные координаты: центр лица (0,0), лицо ~ 70x104."""
    cv.save()
    cv.rotate(tilt)
    scarf = smooth([(0, -86), (40, -78), (58, -46), (62, -4), (60, 40), (70, 72), (40, 70), (24, 56),
                    (-24, 56), (-40, 70), (-70, 72), (-60, 40), (-62, -4), (-58, -46), (-40, -78)], t=0.4)
    shape(cv, scarf, "#24413e")
    _scarf_dots(cv, scarf, col="#9c8a52", a=0.85, step=15, r=2.3, x0=-80, x1=80, y0=-95, y1=80)
    face = ellipse(0, 0, 37, 54)
    cv.drawPath(face, fillp(F_SKIN))
    sh = skia.GradientShader.MakeRadial(skia.Point(-8, -10), 60, [0x00000000, 0x55303a30], [0.55, 1.0])
    cv.drawPath(face, skia.Paint(AntiAlias=True, Shader=sh))
    stroke(cv, face, OUT)
    stroke(cv, arc_path(0, -2, 44, 58, 198, 342), OUT, Style.lw * 3.4)
    stroke(cv, arc_path(0, -2, 44, 58, 198, 342), "#24413e", Style.lw * 1.6)
    # глаза — пустые, чёрные
    for sx in (-1, 1):
        fill(cv, ellipse(sx * 15, -16, 14, 16), "#57615a", 0.55)
        shape(cv, ellipse(sx * 15, -14, 9.5, 12), "#07070a", lw=Style.lw * 0.6)
        if eye_glint > 0:
            fill(cv, circle(sx * 15 + 1.5, -15, 1.7), "#ffffff", eye_glint)
    # нос
    for sx in (-1, 1):
        stroke(cv, line_path(sx * 3.5, 8, sx * 5.5, 12), "#5e6a5c", Style.lw * 0.6)
    # улыбка: шире лица при smile→1
    w = 16 + 46 * smile
    h = 6 + 20 * smile
    my = 24
    upper = [(-w, my - 3 * smile), (0, my + 2), (w, my - 3 * smile)]
    lower = [(w, my - 3 * smile), (w * 0.55, my + h * 0.9), (0, my + h), (-w * 0.55, my + h * 0.9), (-w, my - 3 * smile)]
    mouth = smooth(upper + lower[1:-1], t=0.45)
    shape(cv, mouth, "#1a0d0d", lw=Style.lw * 0.8)
    cv.save()
    cv.clipPath(mouth, skia.ClipOp.kIntersect, True)
    n = int(8 + 14 * smile)
    for k in range(n):
        x0 = -w + (2 * w) * k / n
        x1 = -w + (2 * w) * (k + 1) / n
        yy = my - 3 * smile + 2 + (1 - ((x0 + x1) / 2 / max(w, 1)) ** 2) * 3
        shape(cv, poly([(x0, yy - 4), (x1, yy - 4), ((x0 + x1) / 2, yy + 6 + 3 * smile)]), "#e9e3c7", lw=Style.lw * 0.35)
        yb = my + h * (1 - ((x0 + x1) / 2 / max(w, 1)) ** 2) - 1
        shape(cv, poly([(x0, yb + 4), (x1, yb + 4), ((x0 + x1) / 2, yb - 5 - 3 * smile)]), "#d8d1b2", lw=Style.lw * 0.35)
    cv.restore()
    # складки от улыбки
    if smile > 0.3:
        for sx in (-1, 1):
            stroke(cv, arc_path(sx * (w + 2), my - 6, 6, 10, 90 if sx > 0 else -90, 200 if sx > 0 else 20), "#5e6a5c", Style.lw * 0.6, a=smile)
    cv.restore()


def fake_hand(cv, t=0.0, slide=0.0):
    """Длинные пальцы, прижатые к стеклу (локально: запястье в (0,0), пальцы вверх)."""
    for k, (dx, ln) in enumerate(((-27, 92), (-9, 112), (9, 108), (27, 86))):
        x = dx * 1.1
        y0 = 0 - slide * (8 + k * 3)
        finger = rrect(x - 6.5, y0 - ln, 13, ln + 20, 6.5)
        shape(cv, finger, "#aeb8a8", lw=Style.lw * 0.8)
        fill(cv, ellipse(x, y0 - ln + 9, 7.5, 9), "#d3dbcc", 0.9)
        nail = poly([(x - 4.5, y0 - ln + 6), (x + 4.5, y0 - ln + 6), (x, y0 - ln - 9)])
        shape(cv, nail, "#3a3f3a", lw=Style.lw * 0.5)
        for j in (0.35, 0.62):
            stroke(cv, line_path(x - 4, y0 - ln * j, x + 4, y0 - ln * j), "#7d8878", Style.lw * 0.4)
    shape(cv, rrect(-38, -10, 76, 60, 18), "#aeb8a8", lw=Style.lw * 0.8)


# ================================================================== ГЛАЗА ЗА ПЕЧКОЙ
def stove_eyes(cv, open_k=1.0, t=0.0, look=0.0, finger=0.0):
    """Локально: центр между глазами (0,0)."""
    # едва различимый платок и лицо в темноте
    fill(cv, ellipse(0, 18, 38, 50), "#1a1716", 0.9)
    scarf = smooth([(0, -52), (34, -42), (44, -10), (42, 30), (24, 44), (-24, 44), (-42, 30), (-44, -10), (-34, -42)], t=0.4)
    cv.save()
    cv.clipPath(scarf, skia.ClipOp.kIntersect, True)
    for i in range(-3, 4):
        for j in range(-3, 1):
            cv.drawCircle(i * 13 + (6 if j % 2 else 0), -14 + j * 11, 2.1, fillp(G_DOT, 0.22))
    cv.restore()
    for sx in (-1, 1):
        ex = sx * 13
        glow(cv, ex, 0, 22, "#cfc79a", 0.10 * open_k)
        ry = 5.5 * open_k
        if ry > 0.4:
            fill(cv, ellipse(ex, 0, 7.5, ry), "#d9d1a4")
            fill(cv, ellipse(ex + look * 3, 0, 2.6, min(ry, 4.2)), "#0b0908")
            fill(cv, circle(ex + look * 3 + 1.4, -1.5, 0.9), "#ffffff", 0.9)
    if finger > 0:
        y0 = 70 - 40 * finger
        shape(cv, rrect(-4.5, y0 - 30, 9, 44, 4.5), "#8c7a6a", lw=Style.lw * 0.6, a=min(1, finger * 2))
        fill(cv, ellipse(0, y0 - 24, 3, 4), "#6f6156", min(1, finger * 2))


# ================================================================== ПУГАЛО
SC_SACK = "#b99b69"
SC_SACK_SH = "#9a7d52"
SC_COAT = "#3d4851"
SC_COAT_LINE = "#56636e"
SC_STRAW = "#dcbd5e"
SC_HAT = "#4a3a2d"
SC_FUR = "#6e5846"
SC_PANTS = "#3a3a42"
SC_POLE = "#7a5a3a"


def straw(cv, x, y, ang, length, n=7, seed=0, spread=46):
    import random as _r
    r = _r.Random(seed)
    w = 3.4
    for i in range(n):
        a = math.radians(ang + r.uniform(-spread / 2, spread / 2))
        ln = length * r.uniform(0.55, 1.0)
        x1, y1 = x + math.cos(a) * ln, y + math.sin(a) * ln
        cv.drawLine(x, y, x1, y1, strokep(OUT, w + Style.lw * 1.2))
    for i in range(n):
        r2 = _r.Random(seed)
        pass
    r = _r.Random(seed)
    for i in range(n):
        a = math.radians(ang + r.uniform(-spread / 2, spread / 2))
        ln = length * r.uniform(0.55, 1.0)
        x1, y1 = x + math.cos(a) * ln, y + math.sin(a) * ln
        cv.drawLine(x, y, x1, y1, strokep(SC_STRAW if i % 3 else "#c9a646", w))


def _sack_head(cv, front=True, smile=0.0, t=0.0, squash=1.0):
    cv.save()
    cv.translate(0, -262)
    cv.scale(squash, 1.0)
    pts = []
    for k in range(14):
        a = math.radians(k * 360 / 14)
        rr = 44 + 3.5 * math.sin(k * 2.7) + (4 if 3 <= k <= 5 else 0)
        pts.append((rr * math.cos(a), rr * math.sin(a) * 1.04))
    head = smooth(pts, t=0.45)
    cv.drawPath(head, fillp(SC_SACK))
    cv.save()
    cv.clipPath(head, skia.ClipOp.kIntersect, True)
    for i in range(-60, 61, 7):
        cv.drawLine(i, -60, i + 10, 60, strokep(SC_SACK_SH, 1.4, 0.45))
        cv.drawLine(-60, i, 60, i - 6, strokep(SC_SACK_SH, 1.4, 0.35))
    cv.drawOval(skia.Rect.MakeLTRB(8, -40, 60, 50), fillp("#6d5636", 0.25, blur=10))
    cv.restore()
    stroke(cv, head, OUT)
    if front:
        # левый глаз — пуговица, правый — зашит крестом
        shape(cv, circle(-16, -6, 10), "#18151a", lw=Style.lw * 0.8)
        for (hx, hy) in ((-19, -9), (-13, -9), (-19, -3), (-13, -3)):
            fill(cv, circle(hx, hy, 1.6), "#6a6670")
        stroke(cv, line_path(-21, -11, -11, -1), "#d8d0b8", 1.6)
        stroke(cv, line_path(-11, -11, -21, -1), "#d8d0b8", 1.6)
        stroke(cv, line_path(10, -14, 25, 1), "#1a1410", Style.lw * 1.0)
        stroke(cv, line_path(25, -14, 10, 1), "#1a1410", Style.lw * 1.0)
        # зашитая улыбка
        hw = 20 + 13 * smile
        dep = 5 + 7 * smile
        p = smooth([(-hw, 14 - 3 * smile), (-hw * 0.5, 14 + dep), (0, 15 + dep * 1.1), (hw * 0.5, 14 + dep), (hw, 14 - 3 * smile)], close=False)
        stroke(cv, p, "#1a1410", Style.lw * 0.9)
        n = int(6 + 5 * smile)
        for k in range(n + 1):
            u = k / n
            xx = -hw + 2 * hw * u
            yy = 14 - 3 * smile + (dep + 1) * math.sin(math.pi * u) * 1.05
            stroke(cv, line_path(xx, yy - 5, xx, yy + 5), "#1a1410", Style.lw * 0.7)
    else:
        stroke(cv, line_path(2, -40, -2, 36), SC_SACK_SH, 2.0)
    cv.restore()


def _ushanka(cv, front=True):
    crown = smooth([(-47, -282), (-44, -306), (-24, -322), (0, -326), (24, -322), (44, -306), (47, -282)], close=False, t=0.4)
    crown.close()
    shape(cv, crown, SC_HAT)
    # уши шапки вниз
    for sx in (-1, 1):
        flap = smooth([(sx * 40, -290), (sx * 52, -286), (sx * 54, -258), (sx * 48, -244), (sx * 40, -250)], t=0.4)
        shape(cv, flap, SC_FUR)
        for k in range(3):
            stroke(cv, arc_path(sx * 47, -278 + k * 10, 4, 3, 0, 180), "#4f3f31", Style.lw * 0.5)
    band = smooth([(-52, -296), (-30, -301), (0, -303), (30, -301), (52, -296), (52, -280), (0, -276), (-52, -280)], t=0.3)
    shape(cv, band, SC_FUR)
    for k in range(9):
        x = -44 + k * 11
        stroke(cv, arc_path(x, -289, 5, 4, 200, 340), "#53412f", Style.lw * 0.55)
    if front:
        shape(cv, ellipse(0, -312, 7, 5), "#3a2d22", lw=Style.lw * 0.6)


def scarecrow(cv, mode="pole", face="front", smile=0.0, t=0.0, walk=0.0, sway=0.0, squash=1.0):
    """Пугало: origin — земля, высота ~326. mode: pole (на шесте, руки в стороны) | stand (стоит, руки висят)."""
    if mode == "pole":
        fill(cv, ellipse(0, 0, 34, 7), "#2e241c", 0.6)
        shape(cv, rrect(-7, -126, 14, 128, 3), SC_POLE)
        for k, x in enumerate((-40, -20, 0, 20, 40)):
            straw(cv, x * 1.2, -102, 95 + x * 0.5, 30, n=5, seed=k)
    else:
        sw = math.sin(walk * 2 * math.pi)
        for sx in (-1, 1):
            fx = sx * 18 + sx * sw * 9
            leg = poly([(sx * 6, -108), (sx * 30, -108), (fx + sx * 13, -12), (fx - sx * 11, -12)])
            shape(cv, leg, SC_PANTS)
            straw(cv, fx, -12, 90 + sx * 18, 26, n=6, seed=10 + sx)
    cv.save()
    cv.rotate(sway * 3)
    # руки
    if mode == "pole":
        for sx in (-1, 1):
            arm = rrect(min(sx * 46, sx * 152), -222, 106, 32, 14)
            shape(cv, arm, SC_COAT)
            for k in range(4):
                xx = sx * (62 + k * 22)
                stroke(cv, line_path(xx, -219, xx, -193), SC_COAT_LINE, 1.6)
            straw(cv, sx * 150, -206, 0 if sx > 0 else 180, 34, n=8, seed=20 + sx)
    else:
        for sx in (-1, 1):
            arm = poly([(sx * 40, -214), (sx * 64, -206), (sx * 74, -118), (sx * 50, -118)])
            shape(cv, arm, SC_COAT)
            straw(cv, sx * 62, -118, 90 + sx * 8, 40, n=8, seed=30 + sx)
    # фуфайка
    coat = smooth([(-50, -218), (50, -218), (60, -190), (66, -104), (30, -98), (0, -100), (-30, -98), (-66, -104), (-60, -190)], t=0.25)
    shape(cv, coat, SC_COAT)
    cv.save()
    cv.clipPath(coat, skia.ClipOp.kIntersect, True)
    for y in range(-206, -100, 15):
        cv.drawLine(-70, y, 70, y + 2, strokep(SC_COAT_LINE, 1.8, 0.9))
    cv.drawRect(skia.Rect.MakeXYWH(16, -170, 28, 26), fillp("#5b6650"))
    stroke(cv, rect_path(16, -170, 28, 26), "#2b3226", 1.4)
    cv.restore()
    stroke(cv, line_path(0, -214, 0, -100), "#262d33", Style.lw * 0.8)
    for y in (-196, -170, -144, -118):
        fill(cv, circle(-6, y, 3.2), "#8a8478")
    # солома из ворота, верёвка
    for k, x in enumerate((-26, -12, 6, 22)):
        straw(cv, x, -222, -90 + x, 22, n=4, seed=40 + k)
    shape(cv, rrect(-26, -230, 52, 11, 5), "#8a6a40", lw=Style.lw * 0.7)
    if face == "back":
        straw(cv, 0, -226, 100, 24, n=5, seed=55)
    # голова и шапка
    _sack_head(cv, front=(face == "front"), smile=smile, t=t, squash=squash)
    cv.save()
    cv.translate(0, -262)
    cv.scale(squash, 1.0)
    cv.translate(0, 262)
    _ushanka(cv, front=(face == "front"))
    cv.restore()
    cv.restore()


def scarecrow_eyes_glow(cv, a=1.0):
    """Отблеск пуговицы-глаза (для ночной съёмки), в тех же координатах, что scarecrow(face=front)."""
    glow(cv, -16, -268, 22, "#ffffff", 0.7 * a)
    fill(cv, circle(-16, -268, 4), "#ffffff", a)


def rect_path(x, y, w, h):
    p = skia.Path()
    p.addRect(skia.Rect.MakeXYWH(x, y, w, h))
    return p


def boots(cv, t=0.0, straw_k=1.0):
    """Резиновые сапоги в соломе (origin — пол между сапогами)."""
    for k, (bx, tilt) in enumerate(((-58, -4), (52, 6))):
        cv.save()
        cv.translate(bx, 0)
        cv.rotate(tilt)
        boot = smooth([(-26, -150), (24, -150), (26, -40), (58, -26), (60, -2), (-30, -2), (-30, -40)], t=0.2)
        shape(cv, boot, "#3c5a3e")
        shape(cv, rrect(-30, -160, 58, 18, 7), "#2f4a31")
        cv.drawRect(skia.Rect.MakeLTRB(-28, -12, 58, -2), fillp("#2a221c", 0.8))
        fill(cv, ellipse(14, -20, 30, 6), "#5a4430", 0.7)
        if straw_k > 0:
            for j in range(4):
                straw(cv, -20 + j * 13, -150, -90 + (j - 1.5) * 18, 34 * straw_k, n=4, seed=70 + k * 10 + j)
            straw(cv, 40, -6, -20, 30 * straw_k, n=5, seed=90 + k)
        cv.restore()
    for j in range(6):
        straw(cv, -110 + j * 45, 2, 180 + (j % 2) * 160 - 10, 26, n=3, seed=100 + j, spread=30)
