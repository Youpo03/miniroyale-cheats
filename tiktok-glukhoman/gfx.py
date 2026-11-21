# -*- coding: utf-8 -*-
"""Графические помощники поверх skia-python."""
import math
import os

import skia

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")
W, H = 1080, 1920

OUT = "#1c1512"


class Style:
    lw = 5.0  # толщина контура в локальных единицах (меняется вызывающим кодом)


# ------------------------------------------------------------------ цвет
def C(hexstr, a=1.0):
    h = hexstr.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return skia.ColorSetARGB(int(max(0, min(1, a)) * 255), r, g, b)


def mixhex(h1, h2, k):
    a = [int(h1.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(h2.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join("%02x" % int(round(a[i] + (b[i] - a[i]) * k)) for i in range(3))


def fillp(col, a=1.0, blend=None, shader=None, blur=0.0):
    p = skia.Paint(AntiAlias=True, Color=C(col, a))
    if shader is not None:
        p.setShader(shader)
        p.setAlphaf(a)
    if blend is not None:
        p.setBlendMode(blend)
    if blur > 0:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


def strokep(col, w, a=1.0, cap="round", blur=0.0, effect=None):
    p = skia.Paint(AntiAlias=True, Color=C(col, a), Style=skia.Paint.kStroke_Style, StrokeWidth=w,
                   StrokeJoin=skia.Paint.kRound_Join,
                   StrokeCap=skia.Paint.kRound_Cap if cap == "round" else skia.Paint.kButt_Cap)
    if blur > 0:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if effect is not None:
        p.setPathEffect(effect)
    return p


# ------------------------------------------------------------------ пути
def ellipse(cx, cy, rx, ry):
    p = skia.Path()
    p.addOval(skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry))
    return p


def circle(cx, cy, r):
    return ellipse(cx, cy, r, r)


def rect(x, y, w, h):
    p = skia.Path()
    p.addRect(skia.Rect.MakeXYWH(x, y, w, h))
    return p


def rrect(x, y, w, h, r):
    p = skia.Path()
    p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r))
    return p


def poly(pts, close=True):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if close:
        p.close()
    return p


def smooth(pts, close=True, t=0.5):
    """Сплайн Катмулла–Рома через точки → кубические безье."""
    n = len(pts)
    p = skia.Path()
    if n < 2:
        return p
    p.moveTo(*pts[0])
    rng = range(n) if close else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (close or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (close or i + 2 < n) else pts[(i + 1) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) * t / 3, p1[1] + (p2[1] - p0[1]) * t / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * t / 3, p2[1] - (p3[1] - p1[1]) * t / 3)
        p.cubicTo(c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])
    if close:
        p.close()
    return p


def arc_path(cx, cy, rx, ry, a0, a1, steps=24):
    pts = []
    for i in range(steps + 1):
        a = math.radians(a0 + (a1 - a0) * i / steps)
        pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    return poly(pts, close=False)


def line_path(x0, y0, x1, y1):
    p = skia.Path()
    p.moveTo(x0, y0)
    p.lineTo(x1, y1)
    return p


# ------------------------------------------------------------------ рисование
def shape(cv, path, fill, outline=OUT, lw=None, a=1.0):
    if fill is not None:
        cv.drawPath(path, fillp(fill, a))
    if outline is not None:
        cv.drawPath(path, strokep(outline, Style.lw if lw is None else lw, a))


def fill(cv, path, col, a=1.0, blend=None, blur=0.0):
    cv.drawPath(path, fillp(col, a, blend=blend, blur=blur))


def stroke(cv, path, col, w=None, a=1.0, blur=0.0, cap="round"):
    cv.drawPath(path, strokep(col, Style.lw if w is None else w, a, cap=cap, blur=blur))


def lin_grad(p0, p1, cols, pos=None):
    return skia.GradientShader.MakeLinear([skia.Point(*p0), skia.Point(*p1)], [C(*c) if isinstance(c, tuple) else C(c) for c in cols], pos)


def rad_grad(c, r, cols, pos=None):
    return skia.GradientShader.MakeRadial(skia.Point(*c), max(r, 0.1), [C(*cc) if isinstance(cc, tuple) else C(cc) for cc in cols], pos)


def glow(cv, x, y, r, col, a=1.0, blend=skia.BlendMode.kPlus):
    sh = rad_grad((x, y), r, [(col, a), (col, a * 0.35), (col, 0.0)], [0.0, 0.35, 1.0])
    p = skia.Paint(AntiAlias=True, Shader=sh, BlendMode=blend)
    cv.drawCircle(x, y, r, p)


# ------------------------------------------------------------------ шрифты
_TF = {}


def typeface(name):
    if name not in _TF:
        _TF[name] = skia.Typeface.MakeFromFile(os.path.join(FONT_DIR, name))
    return _TF[name]


def font(name, size, skew=0.0):
    f = skia.Font(typeface(name), size)
    f.setSubpixel(True)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    if skew:
        f.setSkewX(skew)
    return f


BLACK = "Montserrat-Black.ttf"
XBOLD = "Montserrat-ExtraBold.ttf"
BOLD = "Montserrat-Bold.ttf"
RUSLAN = "RuslanDisplay-Regular.ttf"
HAND = "Pangolin-Regular.ttf"


def text(cv, s, x, y, f, col, a=1.0, align="center", outline=None, ow=0.0, shadow=0.0, shadow_a=0.6):
    w = f.measureText(s)
    if align == "center":
        x0 = x - w / 2
    elif align == "right":
        x0 = x - w
    else:
        x0 = x
    if shadow > 0:
        sp = skia.Paint(AntiAlias=True, Color=C("#000000", shadow_a * a),
                        MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, shadow))
        cv.drawString(s, x0 + shadow * 0.3, y + shadow * 0.6, f, sp)
    if outline is not None and ow > 0:
        op = skia.Paint(AntiAlias=True, Color=C(outline, a), Style=skia.Paint.kStroke_Style, StrokeWidth=ow,
                        StrokeJoin=skia.Paint.kRound_Join)
        cv.drawString(s, x0, y, f, op)
    cv.drawString(s, x0, y, f, skia.Paint(AntiAlias=True, Color=C(col, a)))
    return w


# ------------------------------------------------------------------ анимация
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def lerp(a, b, k):
    return a + (b - a) * k


def smoothstep(e0, e1, x):
    if e1 == e0:
        return 1.0 if x >= e1 else 0.0
    k = clamp((x - e0) / (e1 - e0))
    return k * k * (3 - 2 * k)


def ease_out(k):
    k = clamp(k)
    return 1 - (1 - k) ** 3


def ease_in_out(k):
    k = clamp(k)
    return 4 * k ** 3 if k < 0.5 else 1 - (-2 * k + 2) ** 3 / 2


def back_out(k, s=1.70158):
    k = clamp(k) - 1
    return k * k * ((s + 1) * k + s) + 1


def kf(t, keys, ease=ease_in_out):
    """Ключевые кадры [(t, v), ...] с интерполяцией (v — число или кортеж)."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            k = ease((t - t0) / (t1 - t0)) if t1 > t0 else 1.0
            if isinstance(v0, tuple):
                return tuple(a + (b - a) * k for a, b in zip(v0, v1))
            return v0 + (v1 - v0) * k
    return keys[-1][1]


def wobble(t, seed=0.0, freqs=(0.31, 0.53, 0.97)):
    return sum(math.sin(2 * math.pi * f * t + seed * (i + 1) * 1.7) / (i + 1) for i, f in enumerate(freqs)) / 1.8


def hash01(*args):
    x = 0
    for a in args:
        x = (x * 1103515245 + int(a * 1000) + 12345) & 0x7FFFFFFF
    x ^= x >> 13
    x = (x * 1274126177) & 0x7FFFFFFF
    return (x % 100000) / 100000.0
