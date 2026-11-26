#!/usr/bin/env python3
"""Arma una publicación de feed P18 (carrusel o post) como imágenes 1080x1350 con la estética P18. Todo local, sin costo.

Uso: piezas.py pieza.json [--raiz CARPETA_P18]

pieza.json:
{
  "fecha": "2026-11-25",
  "nombre": "Estrategia",                       # va en el nombre de la carpeta
  "area": "Mentalidad aplicada",                 # etiqueta lima de arriba (opcional, se usa en portada/post)
  "fuente": "Cracks Podcast #373 · Carlos García",  # crédito por defecto para slides "dato"
  "slides": [
    {"tipo": "portada", "t": "Tener un *plan B* no es rendirse"},
    {"tipo": "idea", "n": "01", "t": "…", "c": "…"},
    {"tipo": "video", "crudo": "06 Biblioteca/Clips crudos/<carpeta>/01 - x.mp4", "t": "No fue *suerte*",
     "subs": "05 Filtro de reels/Trabajos/<fecha> <nombre>/subs.json"},   # filtro carrusel (p18-filtro/carrusel.py)
    {"tipo": "dato", "t": "…frase del clip…"},
    {"tipo": "cierre", "t": "…", "cta": "Guardalo para esta semana"}
  ]
}
- "fondo": oscuro | lima | papel (en la pieza o en cada slide); "adorno": flecha | numero | nada; "etq": texto abajo a la derecha.
- tipos: portada | idea | dato | cierre | seguir (última placa: invita a seguir, "handle" opcional, "cta" = línea bajo el usuario) | post (una sola imagen) | video (filtro carrusel de p18-filtro: video 1:1 en slide 1080x1350; pasá "crudo", "t" y "subs").
- "foto": {"video": "<clip crudo .mp4>", "seg": 12} pone un cuadro del clip arriba; "quien": "Carlos García" va sobre la foto.
- *palabras* entre asteriscos van en lima; "\\n" corta línea.
Salida: "04 Instagram/Publicaciones listas para subir/<fecha> - <nombre>/NN - <tipo>.png|.mp4" (nunca pisa: agrega " v2").
Imprime cada archivo, y "DESBORDA" al lado si el texto no entró ni achicado (hay que acortarlo).
"""
import argparse, json, os, re, subprocess, sys, tempfile, urllib.parse
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ASSETS = AQUI.parent / "assets"
FONDO = "0x14251D"
FILTRO_CARRUSEL = AQUI.parents[1] / "p18-filtro" / "scripts" / "carrusel.py"
VENV_PY = Path.home() / ".local/share/p18/venv/bin/python"


def buscar_raiz(arg):
    if arg:
        return Path(arg).expanduser().resolve()
    if os.environ.get("P18_RAIZ"):
        return Path(os.environ["P18_RAIZ"]).expanduser().resolve()
    for base in [Path.cwd(), *Path.cwd().parents, AQUI, *AQUI.parents]:
        if (base / "04 Instagram").is_dir() and (base / "06 Biblioteca").is_dir():
            return base
    sys.exit("No encontré la carpeta de Proyecto 18. Pasá --raiz.")


def carpeta_libre(base):
    d, v = base, 2
    while d.exists():
        d = base.with_name(f"{base.name} v{v}")
        v += 1
    d.mkdir(parents=True)
    return d


def video_4x5(src, out):
    # Instagram acepta hasta 60 s por video de carrusel: se corta en 59,5 s.
    # Entra el reel entero (9:16) en 1080x1350, centrado sobre el verde P18: no se corta título ni subtítulos.
    vf = f"scale=-2:1350,pad=1080:1350:(ow-iw)/2:0:color={FONDO},setsar=1"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-t", "59.5", "-vf", vf, "-c:v", "libx264",
                    "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", str(out)], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json"); ap.add_argument("--raiz")
    a = ap.parse_args()
    p = json.loads(Path(a.json).read_text(encoding="utf-8"))
    raiz = buscar_raiz(a.raiz)
    nombre = re.sub(r'[\\/:*?"<>|]', "", p.get("nombre", "Publicacion")).strip() or "Publicacion"
    dest = carpeta_libre(raiz / "04 Instagram" / "Publicaciones listas para subir" / f"{p['fecha']} - {nombre}")
    slides = p["slides"]
    # Sistema "Editorial humano" (manual de Valentín, nov 2026) es el predeterminado; "estilo": "v1" usa la plantilla vieja.
    PLANTILLA = "pieza.html" if p.get("estilo") == "v1" else "editorial.html"
    total = len(slides)
    salidas = []
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for i, s in enumerate(slides, 1):
            tipo = s.get("tipo", "post").lower()
            if tipo == "video":
                out = dest / f"{i:02d} - video.mp4"
                if s.get("crudo"):  # filtro carrusel (skill 2): video 1:1 en slide 1080x1350, fondo oscuro
                    src = Path(s["crudo"]); src = src if src.is_absolute() else raiz / src
                    if not src.exists():
                        sys.exit(f"No existe el clip crudo: {src}")
                    cmd = [str(VENV_PY), str(FILTRO_CARRUSEL), str(src), s.get("t", ""), "--salida", str(out),
                           "--fondo", "oscuro", "--area", s.get("area", p.get("area", "")),
                           "--fuente", s.get("src", p.get("fuente", "")), "--raiz", str(raiz)]
                    if s.get("subs"):
                        sb = Path(s["subs"]); cmd += ["--subs", str(sb if sb.is_absolute() else raiz / sb)]
                    for k in ("recorte", "encuadre", "nombre"):
                        if s.get(k):
                            cmd += [f"--{k}", s[k]]
                    if s.get("salud_mental"):
                        cmd.append("--salud-mental")
                    r = subprocess.run(cmd, capture_output=True, text=True)
                    if r.returncode:
                        sys.exit(f"Falló el filtro carrusel ({r.returncode}):\n{r.stdout[-800:]}\n{r.stderr[-800:]}")
                else:  # viejo: reel 9:16 achicado. Sólo si no hay clip crudo.
                    src = Path(s["archivo"]); src = src if src.is_absolute() else raiz / src
                    if not src.exists():
                        sys.exit(f"No existe el video: {src}")
                    print(f"⚠ Slide {i}: sin 'crudo', uso el reel achicado (no es el filtro carrusel).")
                    video_4x5(src, out)
                salidas.append(str(out))
                continue
            img = ""
            if s.get("foto"):  # {"video": "<clip crudo .mp4>", "seg": 12}: un cuadro del clip original arriba
                fv = Path(s["foto"]["video"])
                fv = fv if fv.is_absolute() else raiz / fv
                if not fv.exists():
                    sys.exit(f"No existe el video para la foto: {fv}")
                fpng = Path(tempfile.gettempdir()) / f"p18-foto-{os.getpid()}-{i}.png"
                rc = s["foto"].get("recorte")  # "W:H:X:Y" en píxeles del video, para sacar logos o zócalos de otra cuenta
                vf = ["-vf", f"crop={rc}"] if rc else []
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(s["foto"].get("seg", 3)), "-i",
                                str(fv), "-frames:v", "1", *vf, str(fpng)], check=True)
                img = fpng.as_uri()
            if s.get("img"):  # imagen externa (p. ej. imagen oficial de prensa de una empresa), con "cred"
                fi = Path(s["img"]); fi = fi if fi.is_absolute() else raiz / fi
                img = fi.as_uri()
            params = {"tipo": tipo, "t": s.get("t", ""), "c": s.get("c", ""), "n": s.get("n", ""),
                      "cred": s.get("cred", ""),
                      "pos": s.get("pos", "center"), "variante": s.get("variante", ""),
                      "cta": s.get("cta", ""), "handle": s.get("handle", ""), "img": img, "quien": s.get("quien", ""),
                      "fondo": s.get("fondo", p.get("fondo", "oscuro")), "adorno": s.get("adorno", ""), "etq": s.get("etq", ""), "kick": s.get("kick", ""),
                      "area": s.get("area", p.get("area", "") if tipo in ("portada", "post") else ""),
                      "src": s.get("src", p.get("fuente", "") if tipo in ("dato", "post") else ""),
                      "pag": ""}
            pg.goto((ASSETS / PLANTILLA).as_uri() + "?" + urllib.parse.urlencode(params))
            pg.evaluate("document.fonts.ready")
            pg.wait_for_function("window.LISTO === true")
            pg.wait_for_timeout(200)
            out = dest / f"{i:02d} - {tipo}.png"
            pg.screenshot(path=str(out))
            salidas.append(str(out) + ("   DESBORDA" if pg.evaluate("window.DESBORDA") else ""))
        b.close()
    print(dest)
    for s in salidas:
        print(s)


if __name__ == "__main__":
    main()
