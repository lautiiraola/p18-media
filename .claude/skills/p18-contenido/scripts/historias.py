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
   {"tipo": "entrevista", "etq": "Pregunta 01", "t": "¿Qué hacés *mañana*?", "quien": "@persona", "s": "Mirá la respuesta en el perfil",
    "video": "06 Biblioteca/Entrevistas/Partes/<nombre>/01 - ….mp4", "foto": {"video": "<misma parte>", "seg": 20}},
   {"tipo": "texto", "t": "…"}]}

Sistema "Editorial humano" (predeterminado para fondo, repost, frase, texto y dato; "estilo": "v1" = el viejo):
  "foto": {"video": "<clip CRUDO .mp4>", "seg": 12, "recorte": "W:H:X:Y"} → cuadro real del clip de fondo (o "img": archivo),
  "pos": "50% 30%" encuadre. Una sola palabra en *…* (si hay más, sólo la primera se subraya en lima).

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


def video_en_marco(fondo, video, hueco, desde, seg, out, encima=None):
    x, y, w, h = hueco["x"], hueco["y"], hueco["w"], hueco["h"]
    w -= w % 2; h -= h % 2
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                               capture_output=True, text=True).stdout.strip() or seg)
    seg = min(seg, max(1.0, dur - desde), 60)  # nunca más largo que el reel (ni que 60 s, el máximo de una historia)
    with tempfile.TemporaryDirectory() as td:
        mk = Path(td) / "m.png"
        mascara(w, h, 28, mk)
        # colores: el video viene en BT.709; se convierte a RGB y de vuelta con la MISMA norma (si no, cambia el color)
        fc = (f"[1:v]scale={w}:{h}:force_original_aspect_ratio=increase:in_color_matrix=bt709:in_range=tv,crop={w}:{h},setsar=1,fps=30,format=rgba[v];"
              f"[2:v]format=gray,scale={w}:{h}[m];[v][m]alphamerge[vm];"
              f"[0:v][vm]overlay={x}:{y}:shortest=1" + ("[b];[3:v]format=rgba[s];[b][s]overlay=0:0:shortest=1" if encima else "")
              + ",scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv[o]")
        extra = ["-loop", "1", "-i", str(encima)] if encima else []  # capa de arriba (sticker con el nombre)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", "30", "-i", str(fondo),
                        "-ss", str(desde), "-t", str(seg), "-i", str(video), "-loop", "1", "-i", str(mk), *extra,
                        "-filter_complex", fc, "-map", "[o]", "-map", "1:a?", "-t", str(seg),
                        "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-colorspace", "bt709", "-color_primaries", "bt709",
                        "-color_trc", "bt709", "-color_range", "tv", "-c:a", "aac", "-b:a", "160k",
                        "-movflags", "+faststart", str(out)], check=True)


EDITORIAL = ("fondo", "repost", "entrevista", "frase", "texto", "dato")


def foto_de(hst, raiz, i):
    """Foto real para la historia: "foto": {"video": <clip crudo>, "seg": 12, "recorte": "W:H:X:Y"} o "img": <archivo>.
    Devuelve (uri, suave): suave=True si la fuente es de baja resolución (se suaviza para que no se vea pixelada)."""
    if hst.get("img"):
        fi = Path(hst["img"]); fi = fi if fi.is_absolute() else raiz / fi
        return fi.as_uri(), False
    f = hst.get("foto")
    if not f:
        return None
    fv = Path(f["video"]); fv = fv if fv.is_absolute() else raiz / fv
    if not fv.exists():
        sys.exit(f"No existe el video para la foto: {fv}")
    out = Path(tempfile.gettempdir()) / f"p18-hfoto-{os.getpid()}-{i}.png"
    vf = ["-vf", f"crop={f['recorte']}"] if f.get("recorte") else []
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(f.get("seg", 3)), "-i", str(fv), "-frames:v", "1",
                    *vf, str(out)], check=True)
    from PIL import Image
    alto = Image.open(out).size[1]
    return out.as_uri(), alto < 720


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
            params = {k: hst[k] for k in ("t", "s", "area", "src", "n", "etq", "ancho", "pos", "quien", "quien2") if hst.get(k)}
            params["tipo"] = tipo
            if hst.get("items"):
                params["items"] = "|".join(hst["items"])
            # Sistema "Editorial humano" (predeterminado desde el 2026-11-20) para fondo, repost, frase, texto y dato;
            # "estilo": "v1" vuelve a la plantilla vieja. Encuesta, pregunta, quiz y canal siguen en historia.html.
            editorial = tipo in EDITORIAL and hst.get("estilo") != "v1"
            if editorial:
                foto = foto_de(hst, raiz, i)
                if foto:
                    params["img"], suave = foto
                    if suave:
                        params["suave"] = "1"
            plantilla = "historia-editorial.html" if editorial else "historia.html"
            pg.goto((ASSETS / plantilla).as_uri() + "?" + urllib.parse.urlencode(params))
            pg.evaluate("document.fonts.ready")
            pg.wait_for_function("window.LISTO === true")
            pg.wait_for_timeout(200)
            png = libre(dest / f"{i:02d} - {tipo}.png")
            encima = None
            if tipo == "entrevista":  # fondo sin el sticker + el sticker solo, en transparente, para ponerlo sobre el video
                pg.goto((ASSETS / plantilla).as_uri() + "?" + urllib.parse.urlencode({**params, "capa": "sticker"}))
                pg.evaluate("document.fonts.ready"); pg.wait_for_function("window.LISTO === true"); pg.wait_for_timeout(200)
                encima = Path(tempfile.gettempdir()) / f"p18-sticker-{os.getpid()}-{i}.png"
                pg.screenshot(path=str(encima), omit_background=True)
                pg.goto((ASSETS / plantilla).as_uri() + "?" + urllib.parse.urlencode({**params, "capa": "fondo"}))
                pg.evaluate("document.fonts.ready"); pg.wait_for_function("window.LISTO === true"); pg.wait_for_timeout(200)
            pg.screenshot(path=str(png))
            nota = "   DESBORDA" if pg.evaluate("window.DESBORDA") else ""
            if tipo in ("repost", "fondo", "entrevista") and hst.get("video"):
                src = Path(hst["video"])
                if not src.is_absolute():
                    src = raiz / src
                if not src.exists():
                    salidas.append(f"{png}{nota}   (no encontré el video {src}: quedó sólo la imagen)")
                    continue
                mp4 = libre(dest / f"{i:02d} - {tipo}.mp4")
                video_en_marco(png, src, pg.evaluate("window.HUECO"), hst.get("desde", 0), a.seg, mp4, encima)
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
