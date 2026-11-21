#!/usr/bin/env bash
# Установка зависимостей, голосов и шрифтов для генератора «ГЛУХОМАНЬ».
set -euo pipefail
cd "$(dirname "$0")"

python3 -m pip install --quiet skia-python numpy scipy piper-tts onnx onnxruntime faster-whisper

# skia-python на Linux требует libEGL/libGL
if command -v apt-get >/dev/null 2>&1 && ! ldconfig -p 2>/dev/null | grep -q "libEGL.so.1"; then
  apt-get install -y -qq libegl1 libgl1 || echo "Установите libegl1 и libgl1 вручную"
fi
command -v ffmpeg >/dev/null 2>&1 || echo "ВНИМАНИЕ: нужен ffmpeg (с фильтром rubberband)"

# Голоса Piper (рассказчик — ruslan, бабушка — irina)
mkdir -p models/piper fonts
HF=https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU
for v in ruslan irina; do
  for ext in onnx onnx.json; do
    [ -s "models/piper/$v.$ext" ] || curl -fsSL -o "models/piper/$v.$ext" "$HF/$v/medium/ru_RU-$v-medium.$ext"
  done
done

# Шрифты (лицензия OFL)
M=https://raw.githubusercontent.com/JulietaUla/Montserrat/master/fonts/ttf
G=https://raw.githubusercontent.com/google/fonts/main/ofl
for w in Black ExtraBold Bold; do
  [ -s "fonts/Montserrat-$w.ttf" ] || curl -fsSL -o "fonts/Montserrat-$w.ttf" "$M/Montserrat-$w.ttf"
done
[ -s fonts/RuslanDisplay-Regular.ttf ] || curl -fsSL -o fonts/RuslanDisplay-Regular.ttf "$G/ruslandisplay/RuslanDisplay-Regular.ttf"
[ -s fonts/Pangolin-Regular.ttf ] || curl -fsSL -o fonts/Pangolin-Regular.ttf "$G/pangolin/Pangolin-Regular.ttf"

echo "Готово. Собрать серию: python3 build.py ep1  →  out/ep1.mp4"
