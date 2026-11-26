#!/usr/bin/env python3
"""Arma las historias de un día como imágenes 1080x1920 con la estética P18.

Uso: historias.py FECHA historias.json [--fuente "Cracks Podcast #373 · Carlos García"] [--raiz CARPETA_P18]

historias.json: [{"tipo": "Encuesta", "texto": "¿Te da *miedo* equivocarte…?", "opciones": [...]},
                 {"tipo": "Dato", "texto": "…"}, {"tipo": "Repost del reel", "texto": "…"}]
- *palabras* entre asteriscos van en lima.
- "Repost del reel" no lleva imagen (se comparte el reel desde la app): se saltea.
- Encuesta deja el espacio para el sticker; Dato lleva el crédito de la fuente.
Salida: "04 Instagram/Historias listas para subir/<FECHA>/NN - <tipo>.png" (nunca pisa: agrega " v2").
"""
import argparse, json, os, sys, urllib.parse
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fecha"); ap.add_argument("json")
    ap.add_argument("--fuente", default=""); ap.add_argument("--raiz")
    a = ap.parse_args()
    hist = json.loads(Path(a.json).read_text(encoding="utf-8"))
    dest = buscar_raiz(a.raiz) / "04 Instagram" / "Historias listas para subir" / a.fecha
    dest.mkdir(parents=True, exist_ok=True)
    from playwright.sync_api import sync_playwright
    salidas = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        for n, h in enumerate(hist, 1):
            tipo = h.get("tipo", "Texto")
            if tipo.lower().startswith("repost"):
                salidas.append(None)
                continue
            params = {"tipo": tipo, "t": h.get("texto", ""),
                      "hueco": "1" if tipo.lower().startswith("encuesta") else "0",
                      "src": a.fuente if tipo.lower().startswith("dato") else ""}
            pg.goto((ASSETS / "historia.html").as_uri() + "?" + urllib.parse.urlencode(params))
            pg.evaluate("document.fonts.ready")
            pg.wait_for_function("window.LISTO === true")
            pg.wait_for_timeout(200)
            out = dest / f"{n:02d} - {tipo}.png"
            v = 2
            while out.exists():
                out = dest / f"{n:02d} - {tipo} v{v}.png"
                v += 1
            pg.screenshot(path=str(out))
            salidas.append(str(out))
        b.close()
    for s in salidas:
        print(s or "(repost: se comparte el reel desde la app, sin imagen)")


if __name__ == "__main__":
    main()
