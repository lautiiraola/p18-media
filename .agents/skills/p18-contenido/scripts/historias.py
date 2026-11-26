#!/usr/bin/env python3
"""Arma las 6 historias de un día con la plantilla P18 (1080x1920). Todo local, sin costo.

Uso: historias.py historias.json [--raiz CARPETA_P18] [--seg 15]

historias.json:
{"fecha": "2026-11-14",
 "historias": [
   {"tipo": "repost", "t": "Que no estén de acuerdo *no es un ataque*", "s": "Mirá el reel completo",
    "area": "Vínculos", "n": "1/3", "video": "04 Instagram/Reels listos para subir/….mp4", "desde": 0},
   {"tipo": "encuesta", "t": "¿Cómo te tomás un *no estoy de acuerdo*?", "opciones": ["Me lo tomo personal", "Lo escucho"]},
   {"tipo": "pregunta", "t": "¿Qué *idea* probarías esta semana?"},
   {"tipo": "quiz", "t": "…", "opciones": ["…", "…", "…"], "correcta": 1},
   {"tipo": "canal", "t": "Enterate primero de los *próximos talleres*", "s": "…", "items": ["…", "…", "…"]},
   {"tipo": "dato", "t": "…", "src": "Cracks Podcast · Carlos García"},
   {"tipo": "texto", "t": "…"}]}

- repost: sale un .mp4 con el reel (desde `desde`, `--seg` segundos) adentro del marco P18, y un .png de portada.
- encuesta / pregunta / quiz / canal: .png con el hueco marcado donde va el sticker (encuesta, pregunta, quiz o link).
- *palabras* entre asteriscos van en lima.
Salida: "04 Instagram/Historias listas para subir/<fecha>/NN - <tipo>.png|.mp4" (nunca pisa: agrega " v2").
Imprime cada archivo (y "DESBORDA" si el texto no entró: acortalo).
"""
import argparse, json, os, subprocess, sys, tempfile, urllib.parse
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ASSETS = AQUI.parent / "assets"


def buscar_raiz(arg):
    if arg:
        return Path(arg).expanduser().resolve()
    if os.environ.get("P18_RAIZ"):
        return Path(os.environ["P18_RAIZ"]).expanduser().resolve()
    for base in [Path.cwd(), *Path.cwd().parents, AQUI, *AQUI.parents]:
        if (base / "04 Instagram").is_dir() and (base / "06 Biblioteca").is_dir():
            return base
    sys.exit("No encontré la carpeta de Proyecto 18. Pasá --raiz.")


def libre(p):
    v = 2
    out = p
    while out.exists():
        out = p.with_name(f"{p.stem} v{v}{p.suffix}")
        v += 1
    return out


def mascara(w, h, r, path):
    from PIL import Image, ImageDraw
    im = Image.new("L", (w, h), 0)
    ImageDraw.Draw(im).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255)
    im.save(path)


def video_en_marco(fondo, video, hueco, desde, seg, out):
    x, y, w, h = hueco["x"], hueco["y"], hueco["w"], hueco["h"]
    w -= w % 2; h -= h % 2
    with tempfile.TemporaryDirectory() as td:
        mk = Path(td) / "m.png"
        mascara(w, h, 28, mk)
        fc = (f"[1:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,fps=30,format=rgba[v];"
              f"[2:v]format=gray,scale={w}:{h}[m];[v][m]alphamerge[vm];"
              f"[0:v][vm]overlay={x}:{y}:shortest=1,format=yuv420p[o]")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", "30", "-i", str(fondo),
                        "-ss", str(desde), "-t", str(seg), "-i", str(video), "-loop", "1", "-i", str(mk),
                        "-filter_complex", fc, "-map", "[o]", "-map", "1:a?", "-t", str(seg),
                        "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-c:a", "aac", "-b:a", "160k",
                        "-movflags", "+faststart", str(out)], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json"); ap.add_argument("--raiz"); ap.add_argument("--seg", type=float, default=15)
    a = ap.parse_args()
    data = json.loads(Path(a.json).read_text(encoding="utf-8"))
    raiz = buscar_raiz(a.raiz)
    dest = raiz / "04 Instagram" / "Historias listas para subir" / data["fecha"]
    dest.mkdir(parents=True, exist_ok=True)
    salidas = []
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        for i, hst in enumerate(data["historias"], 1):
            tipo = hst.get("tipo", "texto").lower()
            params = {k: hst[k] for k in ("t", "s", "area", "src", "n", "etq") if hst.get(k)}
            params["tipo"] = tipo
            if hst.get("items"):
                params["items"] = "|".join(hst["items"])
            pg.goto((ASSETS / "historia.html").as_uri() + "?" + urllib.parse.urlencode(params))
            pg.evaluate("document.fonts.ready")
            pg.wait_for_function("window.LISTO === true")
            pg.wait_for_timeout(200)
            png = libre(dest / f"{i:02d} - {tipo}.png")
            pg.screenshot(path=str(png))
            nota = "   DESBORDA" if pg.evaluate("window.DESBORDA") else ""
            if tipo == "repost" and hst.get("video"):
                src = Path(hst["video"])
                if not src.is_absolute():
                    src = raiz / src
                if not src.exists():
                    salidas.append(f"{png}{nota}   (no encontré el video {src}: quedó sólo la imagen)")
                    continue
                mp4 = libre(dest / f"{i:02d} - {tipo}.mp4")
                video_en_marco(png, src, pg.evaluate("window.HUECO"), hst.get("desde", 0), a.seg, mp4)
                # portada con un cuadro del reel adentro (para revisar y para la biblioteca)
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "2", "-i", str(mp4), "-frames:v", "1",
                                str(png)], check=True)
                salidas.append(f"{mp4}{nota}")
                salidas.append(f"{png}   (portada)")
            else:
                salidas.append(f"{png}{nota}")
        b.close()
    for s in salidas:
        print(s)


if __name__ == "__main__":
    main()
