#!/usr/bin/env python3
"""Corta una entrevista editada en reels por pregunta.
Uso: cortar.py plan.json
plan.json: {"video": ".../X.mp4", "salida": "carpeta", "fin": [ini, fin],   # placa final P18
            "partes": [{"n":1, "nombre":"...", "tramos": [[ini, fin], ...]}]}
Cada parte = sus tramos concatenados + la placa final. Re-encode a 1080x1920 30 fps, H.264 + AAC.
"""
import json, subprocess, sys
from pathlib import Path

p = json.loads(Path(sys.argv[1]).read_text())
src, out = p["video"], Path(p["salida"]); out.mkdir(parents=True, exist_ok=True)
F = 0.25  # fundido corto de audio en cada empalme para que no haga "click"
for parte in p["partes"]:
    tramos = parte["tramos"] + ([p["fin"]] if p.get("fin") else [])
    fc, ins = [], []
    for k, (a, b) in enumerate(tramos):
        d = b - a
        es_fin = p.get("fin") and k == len(tramos) - 1  # la placa final de P18 no se toca (es la marca)
        sat = f",eq=saturation={p['saturacion']}" if p.get("saturacion") and not es_fin else ""  # 0.85 = -15%, 0.7 = -30%
        fc.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,fps=30{sat},format=yuv420p[v{k}]")
        fc.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d={F},afade=t=out:st={max(0,d-F)}:d={F}[a{k}]")
        ins.append(f"[v{k}][a{k}]")
    fc.append("".join(ins) + f"concat=n={len(tramos)}:v=1:a=1[v][a]")
    dest = out / f"{parte['n']:02d} - {parte['nombre']}.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", str(dest)], check=True)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(dest)],
                               capture_output=True, text=True).stdout)
    print(f"{dest.name}: {dur:.1f} s" + ("   PASA DE 60" if dur > 60.05 else ""))
