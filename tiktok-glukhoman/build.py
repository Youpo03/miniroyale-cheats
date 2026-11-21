# -*- coding: utf-8 -*-
"""Сборка серии целиком: озвучка → таймлайн → звук → кадры → MP4.

    python3 build.py ep1            # всё
    python3 build.py ep1 --stills 0,12.5,44.6   # только кадры-превью (после озвучки/таймлайна)
    python3 build.py ep1 --from audio           # начать с шага (tts|timeline|audio|video|mux)
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = ["tts", "timeline", "audio", "video", "mux"]


def run(cmd, **kw):
    print("$", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, cwd=HERE, **kw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ep")
    ap.add_argument("--from", dest="start", default="tts", choices=STEPS)
    ap.add_argument("--stills", default=None)
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 4)
    a = ap.parse_args()
    ep = a.ep
    bdir = os.path.join(HERE, "build", ep)
    os.makedirs(bdir, exist_ok=True)
    py = sys.executable
    todo = STEPS[STEPS.index(a.start):]
    if a.stills:
        todo = [s for s in todo if s in ("tts", "timeline")]
    t0 = time.time()
    if "tts" in todo:
        run([py, "tts.py", ep])
    if "timeline" in todo:
        run([py, "timeline.py", ep])
    if a.stills:
        os.makedirs(os.path.join(bdir, "stills"), exist_ok=True)
        run([py, f"{ep}_render.py", "stills", os.path.join(bdir, "stills", "s"), a.stills])
        return
    if "audio" in todo:
        run([py, f"{ep}_audio.py"])
    if "video" in todo:
        n = max(1, a.jobs)
        procs = [subprocess.Popen([py, f"{ep}_render.py", "seg", str(i), str(n)], cwd=HERE) for i in range(n)]
        for p in procs:
            if p.wait() != 0:
                raise SystemExit("render failed")
        with open(os.path.join(bdir, "segs.txt"), "w") as f:
            for i in range(n):
                f.write(f"file 'seg{i}.mp4'\n")
        run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(bdir, "segs.txt"),
             "-c", "copy", os.path.join(bdir, "video_raw.mp4")])
    if "mux" in todo:
        mix = os.path.join(bdir, "mix.wav")
        r = subprocess.run(["ffmpeg", "-hide_banner", "-i", mix, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
                            "-f", "null", "-"], capture_output=True, text=True)
        js = r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1]
        d = json.loads(js)
        ln = ("loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:"
              "measured_thresh={input_thresh}:offset={target_offset}:linear=true").format(**d)
        os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
        out = os.path.join(HERE, "out", f"{ep}.mp4")
        run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(bdir, "video_raw.mp4"), "-i", mix, "-map", "0:v:0", "-map", "1:a:0",
             "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.2",
             "-af", ln + ",aresample=44100", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-movflags", "+faststart",
             "-shortest", out])
        print("готово:", out, "%.1f МБ" % (os.path.getsize(out) / 1e6), "за %.0f с" % (time.time() - t0))


if __name__ == "__main__":
    if not shutil.which("ffmpeg"):
        raise SystemExit("нужен ffmpeg")
    main()
