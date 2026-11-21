# -*- coding: utf-8 -*-
"""Сценарий: ГЛУХОМАНЬ — «Третий стук», часть 1.

Каждый бит — либо реплика (line), либо звуковое событие (sfx), либо пауза.
В тексте реплик *звёздочками* отмечены слова, которые в субтитрах будут красными.
Поле `tts` (необязательное) — текст для озвучки, если он отличается от субтитров.
"""

# Спикеры:
#   N  — рассказчик (мальчик, вспоминает)
#   G  — бабушка
#   F  — голос за дверью (как у бабушки, глухо, через дверь)
#   F2 — голос за дверью, уже «неправильный»
#   W  — шёпот из-за печки

BEATS = [
    # ---------- ХУК / ОБЛОЖКА ----------
    dict(scene="title", kind="sfx", sfx="knock_triple", dur=1.55, cue="title_knocks"),
    dict(scene="title", kind="line", spk="G", text="На третий стук — *не открывай*.", gap=0.25),
    dict(scene="title", kind="line", spk="G", text="Даже если *это я*.", gap=0.55),

    # ---------- ДЕРЕВНЯ ----------
    dict(scene="village", kind="line", spk="N", text="Летом меня отправили к бабушке.", gap=0.15),
    dict(scene="village", kind="line", spk="N", text="В глухую деревню. *Без связи*.", gap=0.45),

    # ---------- ПРАВИЛА ----------
    dict(scene="rules", kind="line", spk="N", text="В первый же вечер она сказала:", gap=0.2),
    dict(scene="rules", kind="line", spk="G", text="Ночью стучат — считай.", gap=0.2, cue="rule0"),
    dict(scene="rules", kind="line", spk="G", text="Два раза — свои. Открывай.", gap=0.2, cue="rule1"),
    dict(scene="rules", kind="line", spk="G", text="*Три* — не подходи.", gap=0.2, cue="rule2"),
    dict(scene="rules", kind="line", spk="G", text="И в окно *не смотри*.", gap=0.5, cue="rule3"),

    # ---------- БАБУШКА УХОДИТ ----------
    dict(scene="leave", kind="line", spk="N", text="Через неделю бабушка ушла к соседке. Та слегла.", gap=0.2),
    dict(scene="leave", kind="line", spk="G", text="Вернусь до полуночи. Постучу *два раза*.", gap=0.15),
    dict(scene="leave", kind="sfx", sfx="door_close", dur=1.1, cue="door_close"),

    # ---------- ЧАСЫ ----------
    dict(scene="clock", kind="line", spk="N", text="Без двух минут полночь.", gap=0.7, pre=0.4),

    # ---------- ДВЕРЬ ----------
    dict(scene="door", kind="sfx", sfx="knock", dur=0.75, cue="knock1"),
    dict(scene="door", kind="sfx", sfx="knock", dur=0.9, cue="knock2"),
    dict(scene="door", kind="line", spk="F", text="Внучек, это я. Открывай.", gap=0.35),
    dict(scene="door", kind="line", spk="N", text="Два раза. Свои.", gap=0.2),
    dict(scene="door", kind="line", spk="N", text="Я отодвинул засов…", gap=0.15, cue="bolt"),
    dict(scene="door", kind="sfx", sfx="bolt", dur=0.9, cue="bolt_sfx"),
    dict(scene="door", kind="sfx", sfx="knock_big", dur=1.25, cue="knock3"),
    dict(scene="door", kind="line", spk="N", text="*Третий*.", gap=0.6),

    # ---------- ЛИЦО МАЛЬЧИКА ----------
    dict(scene="face", kind="line", spk="F2", text="Ну что же ты, внучек? Бабушка замёрзла.", gap=0.35),
    dict(scene="face", kind="line", spk="N", text="А на улице *плюс тридцать*.", gap=0.45),
    dict(scene="face", kind="line", spk="N", text="Засов открыт. Но она не входит.", gap=0.15),
    dict(scene="face", kind="line", spk="N", text="Ждёт, чтобы я открыл *сам*.", gap=0.5),

    # ---------- ОКНО ----------
    dict(scene="window", kind="line", spk="N", text="Я глянул в окно. Хотя было *нельзя*.", gap=0.35),
    dict(scene="window", kind="line", spk="N", text="Она улыбалась. *Слишком широко*.", gap=0.6, cue="smile"),

    # ---------- ПЕЧЬ ----------
    dict(scene="stove", kind="line", spk="N", text="А за печкой кто-то зашептал:", gap=0.35),
    dict(scene="stove", kind="line", spk="W", text="Не открывай. Я дома.", gap=0.25, cue="eyes"),
    dict(scene="stove", kind="line", spk="W", text="Я *никуда не уходила*.", gap=0.6),

    # ---------- РАЗВИЛКА ----------
    dict(scene="split", kind="line", spk="N", text="Одна из них — *не бабушка*.", gap=0.5),
    dict(scene="choice", kind="line", spk="N", text="Кому мне верить?", gap=0.25, cue="choice"),
    dict(scene="choice", kind="pause", dur=1.2),
    dict(scene="choice", kind="line", spk="N", text="Решай быстрее. *Она снова стучит*.", gap=0.2),
    dict(scene="choice", kind="sfx", sfx="knock_triple_end", dur=2.2, cue="end_knocks"),
    dict(scene="end", kind="pause", dur=1.6),
]
