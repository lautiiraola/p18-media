#!/usr/bin/env python3
"""Publica en Instagram de P18 con la API oficial de Meta (Instagram Graph API). Sin dependencias externas.

Credenciales (nunca en el proyecto ni en el chat): archivo ~/.config/p18/meta.env (permisos 600) con
    IG_TOKEN=...            token de acceso de larga duración (Instagram Login o página de Facebook)
    IG_USER_ID=...          id de la cuenta de Instagram profesional
    IG_HOST=graph.instagram.com   (o graph.facebook.com si el token es de Facebook Login)
    IG_VERSION=v23.0
    IMG_BASE_URL=https://.../ig/   URL pública donde quedan las imágenes (la API no acepta subir imágenes locales)
    IMG_DIR=/ruta/local/que/se/publica/en/esa/URL   (opcional: si está, el script copia ahí las imágenes)

Uso:
  ig.py check                                   verifica token, cuenta y cupo de publicaciones (no publica nada)
  ig.py reel VIDEO.mp4 --caption-file c.txt [--cover-offset 1500] [--colab @cuenta] [--comentario "..."]
  ig.py post IMAGEN.png --caption-file c.txt [--comentario "..."]
  ig.py carrusel ITEM1 ITEM2 ... --caption-file c.txt [--comentario "..."]   (png = imagen, mp4 = video; 2 a 10)
  ig.py historia ARCHIVO(.png|.mp4)
  Todos aceptan --prueba: muestra lo que haría sin llamar a la API.
Imprime al final una línea JSON: {"ok": true, "id": "...", "permalink": "..."}.
Los videos se suben directo desde la compu (subida reanudable); las imágenes necesitan IMG_BASE_URL.
"""
import argparse, json, os, shutil, sys, time, urllib.parse, urllib.request
from pathlib import Path

CFG = Path.home() / ".config" / "p18" / "meta.env"


def cargar():
    c = {"IG_HOST": "graph.instagram.com", "IG_VERSION": "v23.0"}
    if CFG.exists():
        for l in CFG.read_text().splitlines():
            l = l.strip()
            if l and not l.startswith("#") and "=" in l:
                k, v = l.split("=", 1)
                c[k.strip()] = v.strip().strip('"')
    for k in ("IG_TOKEN", "IG_USER_ID", "IG_HOST", "IG_VERSION", "IMG_BASE_URL", "IMG_DIR", "GH_TOKEN", "GH_REPO", "GH_BRANCH"):
        if os.environ.get(k):
            c[k] = os.environ[k]
    return c


C = cargar()
PRUEBA = False


def api(metodo, ruta, params=None, data=None, headers=None, url=None):
    if PRUEBA:
        print(f"[prueba] {metodo} {ruta} {json.dumps({k: v for k, v in (params or {}).items() if k != 'access_token'}, ensure_ascii=False)[:300]}")
        return {"id": "PRUEBA", "uri": "PRUEBA", "status_code": "FINISHED", "permalink": "PRUEBA"}
    if not C.get("IG_TOKEN") or not C.get("IG_USER_ID"):
        sys.exit(f"Faltan IG_TOKEN / IG_USER_ID en {CFG}. Ver SKILL.md, 'Preparar el acceso'.")
    p = dict(params or {})
    p["access_token"] = C["IG_TOKEN"]
    u = url or f"https://{C['IG_HOST']}/{C['IG_VERSION']}/{ruta}"
    if metodo == "GET":
        req = urllib.request.Request(u + "?" + urllib.parse.urlencode(p))
    else:
        req = urllib.request.Request(u, data=urllib.parse.urlencode(p).encode(), method="POST", headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        msg = e.read().decode(errors="replace")
        sys.exit(f"Error de la API ({e.code}): {msg[:800]}")


def esperar(cid, max_seg=900):
    t0 = time.time()
    while True:
        r = api("GET", cid, {"fields": "status_code,status"})
        s = r.get("status_code")
        if s in ("FINISHED", "PUBLISHED"):
            return
        if s in ("ERROR", "EXPIRED"):
            sys.exit(f"El contenedor {cid} falló: {r.get('status')}")
        if time.time() - t0 > max_seg:
            sys.exit(f"El contenedor {cid} no terminó de procesarse en {max_seg}s")
        time.sleep(8)


def subir_video(campos):
    """Crea el contenedor con subida reanudable y manda el archivo local."""
    video = campos.pop("_archivo")
    r = api("POST", f"{C.get('IG_USER_ID', 'ID')}/media", {**campos, "upload_type": "resumable"})
    cid, uri = r["id"], r.get("uri")
    tam = Path(video).stat().st_size
    if PRUEBA:
        print(f"[prueba] subiría {video} ({tam/1e6:.1f} MB)")
    else:
        up = uri or f"https://rupload.facebook.com/ig-api-upload/{C['IG_VERSION']}/{cid}"
        req = urllib.request.Request(up, data=Path(video).read_bytes(), method="POST", headers={
            "Authorization": f"OAuth {C['IG_TOKEN']}", "offset": "0", "file_size": str(tam)})
        try:
            with urllib.request.urlopen(req, timeout=900) as x:
                x.read()
        except urllib.error.HTTPError as e:
            sys.exit(f"Error subiendo el video ({e.code}): {e.read().decode(errors='replace')[:600]}")
    esperar(cid)
    return cid


def subir_github(local):
    """Sube la imagen a un repo público de GitHub (gratis) y devuelve su URL pública."""
    import base64
    repo, rama = C["GH_REPO"], C.get("GH_BRANCH", "main")
    ruta = f"ig/{time.strftime('%Y-%m')}/{int(time.time())}-{Path(local).name}".replace(" ", "-")
    if PRUEBA:
        return f"https://raw.githubusercontent.com/{repo}/{rama}/{urllib.parse.quote(ruta)}"
    body = json.dumps({"message": f"P18 {Path(local).name}", "branch": rama,
                       "content": base64.b64encode(Path(local).read_bytes()).decode()}).encode()
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/contents/{urllib.parse.quote(ruta)}", data=body,
                                 method="PUT", headers={"Authorization": f"Bearer {C['GH_TOKEN']}",
                                                         "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"Error subiendo la imagen a GitHub ({e.code}): {e.read().decode(errors='replace')[:400]}")
    url = f"https://raw.githubusercontent.com/{repo}/{rama}/{urllib.parse.quote(ruta)}"
    for _ in range(12):  # espera a que esté online
        try:
            urllib.request.urlopen(url, timeout=20).read(1); return url
        except Exception:
            time.sleep(5)
    return url


def url_imagen(local):
    if C.get("GH_TOKEN") and C.get("GH_REPO"):
        return subir_github(local)
    base = C.get("IMG_BASE_URL")
    if not base:
        if PRUEBA:
            return "https://EJEMPLO/" + urllib.parse.quote(Path(local).name)
        sys.exit("Las imágenes necesitan una URL pública: configurá IMG_BASE_URL (y opcional IMG_DIR) en " + str(CFG))
    nombre = f"{int(time.time())}-{Path(local).name}".replace(" ", "-")
    if C.get("IMG_DIR") and not PRUEBA:
        shutil.copy(local, Path(C["IMG_DIR"]) / nombre)
        print(f"Copiada a {C['IMG_DIR']}/{nombre}: esperá a que esté online antes de seguir si tu hosting tarda.")
    return base.rstrip("/") + "/" + urllib.parse.quote(nombre)


def contenedor_item(archivo, extra):
    if archivo.lower().endswith(".mp4"):
        return subir_video({"_archivo": archivo, "media_type": extra.pop("media_type", "VIDEO"), **extra})
    r = api("POST", f"{C.get('IG_USER_ID', 'ID')}/media", {"image_url": url_imagen(archivo), **extra})
    esperar(r["id"])
    return r["id"]


def publicar(cid, comentario=None):
    r = api("POST", f"{C.get('IG_USER_ID', 'ID')}/media_publish", {"creation_id": cid})
    mid = r["id"]
    link = api("GET", mid, {"fields": "permalink"}).get("permalink")
    if comentario:
        api("POST", f"{mid}/comments", {"message": comentario})
    print(json.dumps({"ok": True, "id": mid, "permalink": link}, ensure_ascii=False))


def main():
    global PRUEBA
    ap = argparse.ArgumentParser()
    ap.add_argument("modo", choices=["check", "reel", "post", "carrusel", "historia"])
    ap.add_argument("archivos", nargs="*")
    ap.add_argument("--caption-file"); ap.add_argument("--comentario")
    ap.add_argument("--colab", action="append", default=[]); ap.add_argument("--cover-offset", type=int)
    ap.add_argument("--prueba", action="store_true")
    a = ap.parse_args()
    PRUEBA = a.prueba
    cap = Path(a.caption_file).read_text(encoding="utf-8").strip() if a.caption_file else ""
    if len(cap) > 2200:
        sys.exit(f"La caption tiene {len(cap)} caracteres (máximo 2200).")
    for f in a.archivos:
        if not Path(f).exists():
            sys.exit(f"No existe: {f}")

    if a.modo == "check":
        u = api("GET", C.get("IG_USER_ID", "me"), {"fields": "username,account_type,media_count"})
        lim = api("GET", f"{C.get('IG_USER_ID')}/content_publishing_limit", {"fields": "quota_usage,config"})
        print(json.dumps({"ok": True, "cuenta": u, "cupo_24h": lim, "imagenes_url": C.get("IMG_BASE_URL") or "FALTA"}, ensure_ascii=False))
        return
    if not a.archivos:
        sys.exit("Falta el archivo a publicar.")
    extra = {}
    if a.colab:
        extra["collaborators"] = json.dumps([c.lstrip("@") for c in a.colab])

    if a.modo == "reel":
        f = {"_archivo": a.archivos[0], "media_type": "REELS", "caption": cap, "share_to_feed": "true", **extra}
        if a.cover_offset is not None:
            f["thumb_offset"] = str(a.cover_offset)
        publicar(subir_video(f), a.comentario)
    elif a.modo == "post":
        r = api("POST", f"{C.get('IG_USER_ID', 'ID')}/media", {"image_url": url_imagen(a.archivos[0]), "caption": cap, **extra})
        esperar(r["id"]); publicar(r["id"], a.comentario)
    elif a.modo == "carrusel":
        if not 2 <= len(a.archivos) <= 10:
            sys.exit("Un carrusel lleva de 2 a 10 elementos.")
        hijos = [contenedor_item(x, {"is_carousel_item": "true"}) for x in a.archivos]
        r = api("POST", f"{C.get('IG_USER_ID', 'ID')}/media", {"media_type": "CAROUSEL", "children": ",".join(hijos), "caption": cap, **extra})
        esperar(r["id"]); publicar(r["id"], a.comentario)
    elif a.modo == "historia":
        publicar(contenedor_item(a.archivos[0], {"media_type": "STORIES"}))


if __name__ == "__main__":
    main()
