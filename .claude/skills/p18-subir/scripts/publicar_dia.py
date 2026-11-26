#!/usr/bin/env python3
"""Actuador: publica en Instagram todo lo listo de un día de la grilla, en orden, con caption y primer comentario.

Uso:
  publicar_dia.py GRILLA_DIR CLIPS_DIR FECHA                 → muestra el plan (no publica)
  publicar_dia.py GRILLA_DIR CLIPS_DIR FECHA --si            → publica (sólo después del OK de la persona)
  opciones: --prueba (simula todo sin llamar a la API) · --solo reel,post,carrusel,historia · --desde N (retomar)
            --tanda 1|2 (el día se sube en 2 tandas, ver TANDAS abajo; sin --tanda sube todo)
GRILLA_DIR / CLIPS_DIR: salida de ArtifactData con out_dir (grilla/<fecha>.json y clips/<id>.json).
Lo ya publicado (pub.publicado.instagram) se saltea. Al final imprime una línea JSON
{"fecha", "resultados": [{"slot", "tipo", "id", "permalink"} | {"historia", ...}]} para guardar en la grilla.
Si una publicación falla, frena ahí (no sigue con el resto) y dice desde dónde retomar.
"""
import argparse, json, subprocess, sys, tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent

# TANDAS (pedido de la persona, 2026-11-24): el día no se sube todo junto sino en 2 horarios.
#   tanda 1 (13 h): la primera mitad del feed (reel 1, post 1, reel 2, post 2) con sus reposts.
#   tanda 2 (21 h): el resto (reel 3, post 3, carrusel) con sus reposts, las otras historias y la frase del día al final.
#   Slots extra (Entrevista, Noticia): se reparten alternando, empezando por la tanda 1.
#   Un slot con "tanda": 1 o 2 en la grilla manda sobre esta regla.
EXTRA = ("entrevista", "noticia", "historia de vida")  # historia de vida: P18 Stories (Creative Studio), 1 por día


def tandas(slots):
    base = [i for i, s in enumerate(slots) if s.get("tipo", "Reel").split(":")[0].lower() not in EXTRA]
    extra = [i for i in range(len(slots)) if i not in base]
    mitad = (len(base) + 1) // 2
    t = {i: (1 if k < mitad else 2) for k, i in enumerate(base)}
    t |= {i: (1 if k % 2 == 0 else 2) for k, i in enumerate(extra)}
    for i, s in enumerate(slots):
        if s.get("tanda") in (1, 2, "1", "2"):
            t[i] = int(s["tanda"])
    return t


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
    ap.add_argument("--sin-youtube", action="store_true", help="No subir los reels como Shorts.")
    ap.add_argument("--sin-tiktok", action="store_true", help="No subir los reels a TikTok.")
    ap.add_argument("--tanda", type=int, choices=[1, 2], help="Sube sólo esa tanda del día (1 = 13 h, 2 = 21 h).")
    ap.add_argument("--saltear-slots", default="", help="Slots bloqueados por el revisor (ej. 2,4): no se publican, ni sus reposts.")
    a = ap.parse_args()
    R = raiz()
    g = Path(a.grilla); g = g / "grilla" if (g / "grilla").is_dir() else g
    c = Path(a.clips); c = c / "clips" if (c / "clips").is_dir() else c
    d = json.loads((g / f"{a.fecha}.json").read_text()); d = d.get("data", d)
    clips = {p.stem: json.loads(p.read_text()) for p in c.glob("*.json")}
    solo = set(a.solo.split(","))

    plan, hist = [], []
    tanda_de = tandas(d.get("slots", []))
    for i, s in enumerate(d.get("slots", [])):
        if a.tanda and tanda_de[i] != a.tanda:
            continue
        pub = s.get("pub")
        tipo = s.get("tipo", "Reel").split(":")[0].lower()
        if not pub:
            plan.append({"slot": i, "tipo": tipo, "salta": "sin material"}); continue
        if str(i) in {x.strip() for x in a.saltear_slots.split(",") if x.strip()}:
            plan.append({"slot": i, "tipo": tipo, "salta": "bloqueado por el revisor"}); continue
        if (pub.get("publicado") or {}).get("instagram"):
            plan.append({"slot": i, "tipo": tipo, "salta": "ya publicado"}); continue
        cap = (pub.get("caption", "") + ("\n\n" + pub["hashtags"] if pub.get("hashtags") else "")).strip()
        it = {"slot": i, "tipo": tipo, "caption": cap, "comentario": pub.get("comentario"), "colab": pub.get("colaborador"), "tiktok": pub.get("tiktok"),
              "youtube": pub.get("youtube", True), "etiquetar": pub.get("etiquetar", [])}  # pub.youtube = false: no va a YouTube (p. ej. entrevistas completas)
        if tipo in ("entrevista", "historia de vida"):  # reel extra del día: una parte de una entrevista P18 (pub.video)
            it["modo"], it["archivos"] = "reel", [pub["video"]]
            reps = [h for h in pub.get("historias", []) if h.get("tipo") == "Repost" and not h.get("publicado") and h.get("video")]
        elif tipo == "reel":
            it["modo"], it["archivos"] = "reel", [clips[s["clip_id"]]["reel"]["archivo"]]
            if a.tanda != 1:  # las historias sueltas salen con la frase, en la última tanda
                hist += [h for h in pub.get("historias", []) if not h.get("publicado") and h.get("tipo") != "Repost"]
            reps = [h for h in pub.get("historias", []) if h.get("tipo") == "Repost" and not h.get("publicado") and h.get("video")]
        elif tipo == "post":
            it["modo"], it["archivos"] = "post", [pub["slides"][0]["imagen"]["archivo"]]
        else:
            it["modo"] = "carrusel"
            it["archivos"] = [x["imagen"]["archivo"] if x.get("imagen") else x["archivo"] for x in pub["slides"]]
        plan.append(it)
        if tipo in ("reel", "entrevista", "historia de vida"):  # el repost (reel dentro del recuadro) sale justo después de su reel
            for h in reps:
                plan.append({"slot": i, "historia": f"repost-{i}", "tipo": "historia", "modo": "historia",
                             "archivos": [h["video"]], "nota": "repost: " + h.get("texto", "").replace("*", ""),
                             "etiquetar": h.get("etiquetar", [])})
    if d.get("frase") and a.tanda != 1 and not d["frase"].get("publicado"):
        hist.append(d["frase"])
    hist.sort(key=lambda h: h.get("tipo") == "Frase")
    for k, h in enumerate(hist):
        src = h.get("video") or (h.get("imagen") or {}).get("archivo")
        plan.append({"historia": k, "tipo": "historia", "modo": "historia", "archivos": [src],
                     "nota": ""})

    todo = [p for p in plan if "modo" in p and p["modo"] in solo]
    print(f"Plan {a.fecha}" + (f" · tanda {a.tanda}" if a.tanda else "") + f": {len(todo)} publicaciones")
    if not a.sin_youtube and (Path.home() / ".config/p18/youtube_token.json").exists():
        print("Además, cada reel se sube como Short de YouTube (mientras la app no esté aprobada por Google, queda privado).")
    if not a.sin_tiktok and (Path.home() / ".config/p18/tiktok_token.json").exists():
        print("Además, cada reel se sube a TikTok con su texto corto (mientras TikTok no apruebe la app, queda privado).")
    for n, p in enumerate(todo, 1):
        extra = (" · comentario: " + p["comentario"][:60]) if p.get("comentario") else ""
        colab = [p["colab"]] if isinstance(p.get("colab"), str) else p.get("colab") or []
        extra += (" · colaborador: " + " ".join(c for c in colab if c)) if any(colab) else ""
        extra += (" · etiqueta a: " + " ".join(p["etiquetar"])) if p.get("etiquetar") else ""
        extra += " · sin YouTube" if p.get("modo") == "reel" and not p.get("youtube", True) else ""
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
        for c in ([p["colab"]] if isinstance(p.get("colab"), str) else p.get("colab") or []):
            if c:
                cmd += ["--colab", c]
        for c in p.get("etiquetar") or []:
            cmd += ["--etiquetar", c]
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
        # el mismo reel, como Short de YouTube (si YouTube está conectado). Si falla, avisa y sigue con Instagram.
        if p["modo"] == "reel" and p.get("youtube", True) and not a.sin_youtube and (Path.home() / ".config/p18/youtube_token.json").exists():
            tit = (p.get("caption") or "").strip().splitlines()[0][:90] if p.get("caption") else Path(p["archivos"][0]).stem
            tf = tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt", encoding="utf-8"); tf.write(p.get("caption", "")); tf.close()
            yc = [sys.executable, str(AQUI / "yt.py"), "short", str(R / p["archivos"][0]), "--titulo", tit, "--descripcion-file", tf.name]
            if a.prueba:
                yc.append("--prueba")
            y = subprocess.run(yc, capture_output=True, text=True)
            yu = (y.stdout.strip().splitlines() or [""])[-1]
            if y.returncode == 0 and yu.startswith("{"):
                yo = json.loads(yu)
                res.append({"slot": p["slot"], "tipo": "youtube", "id": yo["id"], "permalink": yo.get("url"), "privacidad": yo.get("privacidad")})
                print(f"   + YouTube Short → {yo.get('url')} ({yo.get('privacidad')})")
            else:
                print(f"   ! YouTube falló (Instagram sí se publicó): {(y.stderr or y.stdout).strip()[-300:]}")
        # el mismo reel en TikTok, con pub.tiktok (texto corto). Si falla, avisa y sigue.
        # Con POSTIZ_API_KEY en meta.env, TikTok sale por Postiz (app auditada → público). Si no, por tiktok.py (privado).
        postiz = "POSTIZ_API_KEY=" in ((Path.home() / ".config/p18/meta.env").read_text() if (Path.home() / ".config/p18/meta.env").exists() else "")
        # Sin Postiz: el video queda en la cola del "P18 Publisher for TikTok" (app de escritorio que cumple las reglas
        # de TikTok); la persona lo publica ahí eligiendo la privacidad. Ver publicador-tiktok/servidor.py.
        if p["modo"] == "reel" and not a.sin_tiktok and not postiz and not a.prueba:
            cola_f = R / "04 Instagram" / "TikTok - cola.json"
            cola = json.loads(cola_f.read_text(encoding="utf-8")) if cola_f.exists() else []
            vid = f"{a.fecha}-{p['slot']}"
            if not any(x["id"] == vid for x in cola):
                cola.append({"id": vid, "titulo": (p.get("caption") or "").splitlines()[0][:60] or Path(p["archivos"][0]).stem,
                             "video": p["archivos"][0], "texto": p.get("tiktok") or p.get("caption", ""), "fecha": a.fecha})
                cola_f.write_text(json.dumps(cola, ensure_ascii=False, indent=1), encoding="utf-8")
            print("   + TikTok → en la cola del P18 Publisher (publicalo ahí)")
        elif p["modo"] == "reel" and not a.sin_tiktok and postiz:
            tf2 = tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt", encoding="utf-8"); tf2.write(p.get("tiktok") or p.get("caption", "")); tf2.close()
            tc = ([sys.executable, str(AQUI / "postiz.py"), "tiktok", str(R / p["archivos"][0]), "--texto-file", tf2.name] if postiz else
                  [sys.executable, str(AQUI / "tiktok.py"), "video", str(R / p["archivos"][0]), "--texto-file", tf2.name])
            if a.prueba:
                tc.append("--prueba")
            t = subprocess.run(tc, capture_output=True, text=True)
            tu = (t.stdout.strip().splitlines() or [""])[-1]
            if t.returncode == 0 and tu.startswith("{"):
                to = json.loads(tu)
                res.append({"slot": p["slot"], "tipo": "tiktok", "id": to.get("post_id") or to.get("publish_id"), "estado": to.get("estado"), "url": to.get("url"), "privacidad": to.get("privacidad")})
                print(f"   + TikTok → {to.get('estado')} ({to.get('privacidad')})")
            else:
                print(f"   ! TikTok falló (Instagram sí se publicó): {(t.stderr or t.stdout).strip()[-300:]}")
    print(json.dumps({"fecha": a.fecha, "resultados": res}, ensure_ascii=False))


if __name__ == "__main__":
    main()
