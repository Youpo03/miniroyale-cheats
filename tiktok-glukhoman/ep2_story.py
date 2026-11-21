# -*- coding: utf-8 -*-
"""Сценарий: ГЛУХОМАНЬ — «Пугало», часть 1.

Формат битов тот же, что в ep1_story.py. Спикеры: N — рассказчик, G — бабушка.
"""

# ударения, которые espeak ставит неверно
PRON_FIX = [
    (r"\b[Пп]угало", "[[pˈuɡʌɭʌ]]"),
    (r"\bдо смерти", "[[də]] смерти"),
    (r"\bдо самого", "[[də]] самого"),
    (r"\bпотом", "[[pʌtˈom]]"),
]

BEATS = [
    # ---------- ХУК / ОБЛОЖКА ----------
    dict(scene="title", kind="sfx", sfx="crow", dur=0.9, cue="title_crow"),
    dict(scene="title", kind="line", spk="N", text="Каждое утро пугало стояло *на шаг ближе* к дому.", gap=0.55),

    # ---------- ОГОРОД ----------
    dict(scene="garden", kind="line", spk="N", text="Его поставил дед. За неделю до смерти.", gap=0.25),
    dict(scene="garden", kind="line", spk="N", text="В дедовой фуфайке. И в *дедовой шапке*.", gap=0.5, cue="hat"),

    # ---------- ПРАВИЛА ----------
    dict(scene="rules", kind="line", spk="N", text="Бабушка сразу предупредила:", gap=0.2),
    dict(scene="rules", kind="line", spk="G", text="Его не трогай.", gap=0.2, cue="rule0"),
    dict(scene="rules", kind="line", spk="G", text="И шапку с него *не снимай*.", gap=0.2, cue="rule1"),
    dict(scene="rules", kind="line", spk="G", text="А ночью на огород *не смотри*.", gap=0.5, cue="rule2"),

    # ---------- ДНИ: вид из окна ----------
    dict(scene="days", kind="sfx", sfx="hit", dur=0.5, cue="day1"),
    dict(scene="days", kind="line", spk="N", text="В первый день оно стояло в конце огорода.", gap=0.3),
    dict(scene="days", kind="sfx", sfx="hit", dur=0.45, cue="day2"),
    dict(scene="days", kind="line", spk="N", text="На второй — у бани.", gap=0.3),
    dict(scene="days", kind="sfx", sfx="hit_big", dur=0.5, cue="day3"),
    dict(scene="days", kind="line", spk="N", text="На третий — у забора. *Лицом к окну*.", gap=0.45),
    dict(scene="gran", kind="line", spk="G", text="Это ты по ночам ходишь. Сам его и таскаешь.", gap=0.45),

    # ---------- ТЕЛЕФОН ----------
    dict(scene="phone", kind="line", spk="N", text="Ночью я поставил телефон *на запись*.", gap=0.25, cue="rec"),
    dict(scene="phone", kind="line", spk="N", text="А утром включил видео.", gap=0.35, cue="play"),

    # ---------- ЗАПИСЬ (ночное видение) ----------
    dict(scene="footage", kind="line", spk="N", text="Три часа ночи. Я сплю.", gap=0.25, cue="f_start"),
    dict(scene="footage", kind="sfx", sfx="door_creak", dur=1.1, cue="door_open"),
    dict(scene="footage", kind="line", spk="N", text="Дверь открывается.", gap=0.25),
    dict(scene="footage", kind="line", spk="N", text="Оно заходит в дом.", gap=0.15, cue="enter"),
    dict(scene="footage", kind="line", spk="N", text="И встаёт *у моей кровати*.", gap=0.35, cue="stand"),
    dict(scene="footage", kind="line", spk="N", text="Стоит до самого утра.", gap=0.25, cue="timelapse"),
    dict(scene="footage", kind="line", spk="N", text="А потом поворачивает голову.", gap=0.15, cue="turn"),
    dict(scene="footage", kind="line", spk="N", text="И смотрит *в камеру*.", gap=0.75, cue="turn2"),

    # ---------- УТРО ----------
    dict(scene="morning", kind="line", spk="N", text="Утром пугало стояло на своём месте.", gap=0.3),
    dict(scene="boots", kind="line", spk="N", text="А на сапогах у меня была *солома*.", gap=0.6, cue="boots"),

    # ---------- ВЫБОР ----------
    dict(scene="choice", kind="line", spk="N", text="Что мне делать?", gap=0.25, cue="choice"),
    dict(scene="choice", kind="pause", dur=1.3),
    dict(scene="choice", kind="line", spk="N", text="Решай быстрее. Ночью оно *придёт снова*.", gap=0.7),
    dict(scene="end", kind="pause", dur=1.8),
]
