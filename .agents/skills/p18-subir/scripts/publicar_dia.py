#!/usr/bin/env python3
"""Actuador: publica en Instagram todo lo listo de un día de la grilla, en orden, con caption y primer comentario.

Uso:
  publicar_dia.py GRILLA_DIR CLIPS_DIR FECHA                 → muestra el plan (no publica)
  publicar_dia.py GRILLA_DIR CLIPS_DIR FECHA --si            → publica (sólo después del OK de la persona)
  opciones: --prueba (simula todo sin llamar a la API) · --solo reel,post,carrusel,historia · --desde N (retomar)
GRILLA_DIR / CLIPS_DIR: salida de ArtifactData con out_dir (grilla/<fecha>.json y clips/<id>.json).
Lo ya publicado (pub.publicado.instagram) se saltea. Al final imprime una línea JSON
{"fecha", "resultados": [{"slot", "tipo", "id", "permalink"} | {"historia", ...}]} para guardar en la grilla.
Si una publicación falla, frena ahí (no sigue con el resto) y dice desde dónde retomar.
"""
import argparse, json, subprocess, sys, tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent


def raiz():
    for b in [Path.cwd(), *Path.cwd().parents, *AQUI.parents]:
        if (b / "04 Instagram").is_dir() and (b / "06 Biblioteca").is_dir():
            return b
    sys.exit("No encontré la carpeta de P18.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("grilla"); ap.add_argument("clips"); ap.add_argument("fecha")
    ap.add_argument("--si", action="store_true"); ap.add_argument("--prueba", action="store_true")
    ap.add_argument("--solo", default="reel,post,carrusel,historia"); ap.add_argument("--desde", type=int, default=1)
    a = ap.parse_args()
    R = raiz()
    g = Path(a.grilla); g = g / "grilla" if (g / "grilla").is_dir() else g
    c = Path(a.clips); c = c / "clips" if (c / "clips").is_dir() else c
    d = json.loads((g / f"{a.fecha}.json").read_text()); d = d.get("data", d)
    clips = {p.stem: json.loads(p.read_text()) for p in c.glob("*.json")}
    solo = set(a.solo.split(","))

    plan, hist = [], []
    for i, s in enumerate(d.get("slots", [])):
        pub = s.get("pub")
        tipo = s.get("tipo", "Reel").split(":")[0].lower()
        if not pub:
            plan.append({"slot": i, "tipo": tipo, "salta": "sin material"}); continue
        if (pub.get("publicado") or {}).get("instagram"):
            plan.append({"slot": i, "tipo": tipo, "salta": "ya publicado"}); continue
        cap = (pub.get("caption", "") + ("\n\n" + pub["hashtags"] if pub.get("hashtags") else "")).strip()
        it = {"slot": i, "tipo": tipo, "caption": cap, "comentario": pub.get("comentario"), "colab": pub.get("colaborador")}
        if tipo == "reel":
            it["modo"], it["archivos"] = "reel", [clips[s["clip_id"]]["reel"]["archivo"]]
            hist += [h for h in pub.get("historias", []) if not h.get("publicado")]
        elif tipo == "post":
            it["modo"], it["archivos"] = "post", [pub["slides"][0]["imagen"]["archivo"]]
        else:
            it["modo"] = "carrusel"
            it["archivos"] = [x["imagen"]["archivo"] if x.get("imagen") else x["archivo"] for x in pub["slides"]]
        plan.append(it)
    if d.get("frase"):
        hist.append(d["frase"])
    hist.sort(key=lambda h: h.get("tipo") == "Frase")
    for k, h in enumerate(hist):
        src = h.get("video") or (h.get("imagen") or {}).get("archivo")
        plan.append({"historia": k, "tipo": "historia", "modo": "historia", "archivos": [src],
                     "nota": "agregar a mano el sticker de link al reel" if h.get("tipo") == "Repost" else ""})

    todo = [p for p in plan if "modo" in p and p["modo"] in solo]
    print(f"Plan {a.fecha}: {len(todo)} publicaciones")
    for n, p in enumerate(todo, 1):
        extra = (" · comentario: " + p["comentario"][:60]) if p.get("comentario") else ""
        print(f"{n:2d}. {p['tipo'].upper():9s} {Path(p['archivos'][0]).name}" + (f" (+{len(p['archivos'])-1})" if len(p['archivos']) > 1 else "")
              + (f"\n    caption: {p['caption'][:90].replace(chr(10), ' ')}…" if p.get("caption") else "") + extra
              + (f"\n    {p['nota']}" if p.get("nota") else ""))
    for p in plan:
        if "salta" in p:
            print(f"   (salta {p['tipo']} del slot {p['slot']}: {p['salta']})")
    if not (a.si or a.prueba):
        print("\nNo se publicó nada. Para publicar: el mismo comando con --si (después del OK de la persona).")
        return

    res = []
    for n, p in enumerate(todo, 1):
        if n < a.desde:
            continue
        cmd = [sys.executable, str(AQUI / "ig.py"), p["modo"], *[str(R / f) for f in p["archivos"]]]
        if p.get("caption"):
            tf = tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt", encoding="utf-8"); tf.write(p["caption"]); tf.close()
            cmd += ["--caption-file", tf.name]
        if p.get("comentario"):
            cmd += ["--comentario", p["comentario"]]
        if p.get("colab"):
            cmd += ["--colab", p["colab"]]
        if a.prueba:
            cmd.append("--prueba")
        r = subprocess.run(cmd, capture_output=True, text=True)
        ult = (r.stdout.strip().splitlines() or [""])[-1]
        if r.returncode != 0 or not ult.startswith("{"):
            print(f"\nFALLÓ la publicación {n} ({p['tipo']}): {(r.stderr or r.stdout).strip()[-600:]}")
            print(f"Para retomar: --si --desde {n}")
            break
        o = json.loads(ult)
        res.append({k: p[k] for k in ("slot", "historia", "tipo") if k in p} | {"id": o["id"], "permalink": o.get("permalink")})
        print(f"OK {n}. {p['tipo']} → {o.get('permalink')}")
    print(json.dumps({"fecha": a.fecha, "resultados": res}, ensure_ascii=False))


if __name__ == "__main__":
    main()
