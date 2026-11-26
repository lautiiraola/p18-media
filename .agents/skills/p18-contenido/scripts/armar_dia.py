#!/usr/bin/env python3
"""Arma (o rearma) la carpeta del día con TODO lo que se sube, en orden, lista para pasar al celular.

Uso: armar_dia.py GRILLA_DIR CLIPS_DIR [FECHA ...] [--raiz CARPETA_P18]
  GRILLA_DIR: carpeta con grilla/<fecha>.json (ArtifactData get/list con out_dir)
  CLIPS_DIR:  carpeta con clips/<id>.json
  FECHA: AAAA-MM-DD (si no se pasa, todas las de GRILLA_DIR)

Salida: "07 Para subir (por día)/<fecha> - <día>/"
  00 - Captions y orden.txt   (captions, comentario a fijar y TikTok de cada publicación, en orden)
  01 - Reel - ….mp4 · 02 - Post - <título>.png · … · 07 - Carrusel - <área>/01.png …
  Historias/01 - Repost.mp4 … 04 - Frase.png
La carpeta del día se borra y se vuelve a armar entera (los originales quedan en sus carpetas de siempre).
"""
import argparse, json, os, re, shutil, sys
from pathlib import Path

DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


def limpio(s):
    return re.sub(r'[\\/:*?"<>|]', ",", s.replace("*", "")).strip().rstrip(".")


def raiz_p18(arg):
    if arg:
        return Path(arg)
    for b in [Path.cwd(), *Path.cwd().parents, Path(__file__).resolve().parent, *Path(__file__).resolve().parents]:
        if (b / "04 Instagram").is_dir() and (b / "06 Biblioteca").is_dir():
            return b
    sys.exit("No encontré la carpeta de P18 (--raiz).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("grilla"); ap.add_argument("clips"); ap.add_argument("fechas", nargs="*"); ap.add_argument("--raiz")
    a = ap.parse_args()
    R = raiz_p18(a.raiz)
    gdir = Path(a.grilla) / "grilla" if (Path(a.grilla) / "grilla").is_dir() else Path(a.grilla)
    cdir = Path(a.clips) / "clips" if (Path(a.clips) / "clips").is_dir() else Path(a.clips)
    clips = {p.stem: json.loads(p.read_text()) for p in cdir.glob("*.json")}
    fechas = a.fechas or sorted(p.stem for p in gdir.glob("*.json"))
    import datetime
    for f in fechas:
        d = json.loads((gdir / f"{f}.json").read_text())
        d = d.get("data", d)
        dn = DIAS[datetime.date.fromisoformat(f).weekday()]
        out = R / "07 Para subir (por día)" / f"{f} - {dn}"
        shutil.rmtree(out, ignore_errors=True)
        (out / "Historias").mkdir(parents=True)
        txt = [f"P18 · {dn} {f[8:]}/{f[5:7]} · todo lo que se sube, en orden\n"]
        n, hist, faltan = 0, [], []
        for s in d.get("slots", []):
            pub, tipo = s.get("pub"), s.get("tipo", "Reel").split(":")[0]
            if not pub:
                faltan.append(f"{tipo} ({s.get('area')})")
                continue
            n += 1
            try:
                if tipo == "Reel":
                    src = clips[s["clip_id"]]["reel"]["archivo"]
                    nom = f"{n:02d} - Reel - {Path(src).stem[11:] or Path(src).stem}.mp4"
                    shutil.copy(R / src, out / nom)
                    hist += pub.get("historias", [])
                elif tipo == "Post":
                    sl = pub["slides"][0]
                    nom = f"{n:02d} - Post - {limpio(sl.get('t', s.get('area', '')))}.png"
                    shutil.copy(R / sl["imagen"]["archivo"], out / nom)
                else:
                    nom = f"{n:02d} - Carrusel - {limpio(s.get('area', ''))}"
                    (out / nom).mkdir()
                    for k, x in enumerate(pub["slides"], 1):
                        src = x["imagen"]["archivo"] if x.get("imagen") else x["archivo"]
                        shutil.copy(R / src, out / nom / f"{k:02d}{Path(src).suffix}")
            except (KeyError, FileNotFoundError) as e:
                faltan.append(f"{tipo} ({s.get('area')}): falta el archivo {e}")
                n -= 1
                continue
            cap = pub.get("caption", "") + ("\n\n" + pub["hashtags"] if pub.get("hashtags") else "")
            txt.append(f"\n{'=' * 50}\n{nom}\n{'=' * 50}\nCAPTION (copiar):\n{cap}\n\nCOMENTARIO (fijar):\n{pub.get('comentario', '')}\n"
                       + (f"\nTIKTOK:\n{pub['tiktok']}\n" if pub.get("tiktok") else ""))
        if d.get("frase"):
            hist.append(d["frase"])
        hist.sort(key=lambda x: x.get("tipo") == "Frase")
        txt.append(f"\n{'=' * 50}\nHISTORIAS (en orden)\n{'=' * 50}\n")
        for k, x in enumerate(hist, 1):
            src = x.get("video") or (x.get("imagen") or {}).get("archivo")
            if not src or not (R / src).exists():
                continue
            es_rep = x.get("tipo") == "Repost"
            nom = f"{k:02d} - {'Repost' if es_rep else 'Frase'}{Path(src).suffix}"
            shutil.copy(R / src, out / "Historias" / nom)
            txt.append(f"{nom}: " + (f"subir y agregar sticker de link al reel. Texto: {x.get('texto', '').replace('*', '')}"
                                     if es_rep else "subir tal cual.") + "\n")
        if faltan:
            txt.append("\nFALTA (no hay material todavía):\n" + "\n".join("- " + x for x in faltan) + "\n")
        (out / "00 - Captions y orden.txt").write_text("".join(txt), encoding="utf-8")
        print(out)


if __name__ == "__main__":
    main()
