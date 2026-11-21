# Установка для Windows. Запуск из PowerShell в папке проекта:
#   powershell -ExecutionPolicy Bypass -File setup.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Нужен Python 3.11 или 3.12: https://www.python.org/downloads/ (галочка 'Add python.exe to PATH')"
    exit 1
}
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Host "Ставлю ffmpeg через winget (полная сборка с rubberband)..."
    winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements
    Write-Host "После установки ffmpeg перезапустите PowerShell."
}

# Голоса Piper: рассказчик ruslan и бабушка irina (около 130 МБ)
New-Item -ItemType Directory -Force -Path "models\piper" | Out-Null
$hf = "https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU"
foreach ($v in @("ruslan", "irina")) {
    foreach ($ext in @("onnx", "onnx.json")) {
        $dst = "models\piper\$v.$ext"
        if (-not (Test-Path $dst)) {
            Write-Host "Скачиваю $dst"
            Invoke-WebRequest -Uri "$hf/$v/medium/ru_RU-$v-medium.$ext" -OutFile $dst
        }
    }
}
Write-Host "Готово. Проверка: python build.py ep1 --stills 1.25,44.6"
