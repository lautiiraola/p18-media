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
  ig.py metricas [--ultimos 25]                 sólo lectura: números de las últimas publicaciones (permiso instagram_business_manage_insights)
  ig.py reel VIDEO.mp4 --caption-file c.txt [--cover-offset 1500] [--colab @cuenta] [--comentario "..."]
  ig.py post IMAGEN.png --caption-file c.txt [--comentario "..."]
  ig.py carrusel ITEM1 ITEM2 ... --caption-file c.txt [--comentario "..."]   (png = imagen, mp4 = video; 2 a 10)
  ig.py historia ARCHIVO(.png|.mp4) [--etiquetar @cuenta]
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
    """Sube un video a Instagram en calidad original.
    Método por defecto (VIDEO_METODO=github): Instagram lo descarga de una release temporal de GitHub (se borra al
    terminar). La subida directa a rupload falla seguido con ProcessingFailedError, así que queda de respaldo.
    Con VIDEO_METODO=directo en meta.env se usa primero la subida directa."""
    video = campos.pop("_archivo")
    tam = Path(video).stat().st_size
    if PRUEBA:
        print(f"[prueba] subiría {video} ({tam/1e6:.1f} MB) con " + json.dumps({k: v for k, v in campos.items() if k != "caption"}, ensure_ascii=False))
        return "PRUEBA"
    hay_gh = bool(C.get("GH_TOKEN") and C.get("GH_REPO"))
    orden = ["github", "directo"] if hay_gh and C.get("VIDEO_METODO", "github") != "directo" else (["directo", "github"] if hay_gh else ["directo"])
    ultimo = ""
    for metodo in orden:
        try:
            if metodo == "github":
                r = api("POST", f"{C.get('IG_USER_ID', 'ID')}/media", {**campos, "video_url": subir_release(video)})
                cid = r["id"]
            else:
                r = api("POST", f"{C.get('IG_USER_ID', 'ID')}/media", {**campos, "upload_type": "resumable"})
                cid, uri = r["id"], r.get("uri")
                up = uri or f"https://rupload.facebook.com/ig-api-upload/{C['IG_VERSION']}/{cid}"
                req = urllib.request.Request(up, data=Path(video).read_bytes(), method="POST", headers={
                    "Authorization": f"OAuth {C['IG_TOKEN']}", "offset": "0", "file_size": str(tam)})
                with urllib.request.urlopen(req, timeout=900) as x:
                    x.read()
            esperar(cid)
            return cid
        except (urllib.error.HTTPError, urllib.error.URLError, SystemExit, KeyError) as e:
            ultimo = e.read().decode(errors="replace")[:400] if isinstance(e, urllib.error.HTTPError) else str(e)[:400]
            print(f"Aviso: falló la subida por {metodo} ({ultimo[:150]}); pruebo la otra vía", file=sys.stderr)
    sys.exit(f"Error subiendo el video por todas las vías: {ultimo}")


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
            SUBIDAS.append((ruta, json.loads(r.read())["content"]["sha"]))
    except urllib.error.HTTPError as e:
        sys.exit(f"Error subiendo la imagen a GitHub ({e.code}): {e.read().decode(errors='replace')[:400]}")
    url = f"https://raw.githubusercontent.com/{repo}/{rama}/{urllib.parse.quote(ruta)}"
    for _ in range(12):  # espera a que esté online
        try:
            urllib.request.urlopen(url, timeout=20).read(1); return url
        except Exception:
            time.sleep(5)
    return url


RELEASES = []  # releases temporales de GitHub con videos: se borran al terminar


def subir_release(local):
    """Plan B para videos de cualquier peso (hasta 2 GB), sin recomprimir: los sube como archivo de una release
    temporal de GitHub y devuelve el link directo de descarga. La release se borra al terminar."""
    repo = C["GH_REPO"]; h = {"Authorization": f"Bearer {C['GH_TOKEN']}", "Accept": "application/vnd.github+json"}
    tag = f"tmp-{int(time.time())}"
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/releases", method="POST", headers=h,
                                 data=json.dumps({"tag_name": tag, "name": tag, "draft": False}).encode())
    rel = json.loads(urllib.request.urlopen(req, timeout=60).read())
    RELEASES.append((rel["id"], tag))
    nombre = "reel.mp4"
    up = urllib.request.Request(f"https://uploads.github.com/repos/{repo}/releases/{rel['id']}/assets?name={nombre}",
                                data=Path(local).read_bytes(), method="POST",
                                headers={**h, "Content-Type": "video/mp4"})
    urllib.request.urlopen(up, timeout=900).read()
    return f"https://github.com/{repo}/releases/download/{tag}/{nombre}"


SUBIDAS = []  # imágenes subidas a GitHub en esta corrida: se borran al terminar


def borrar_github():
    """Borra del repo las imágenes subidas (Instagram ya las descargó). El repo queda vacío."""
    for ruta, sha in SUBIDAS:
        body = json.dumps({"message": "P18 borrar", "sha": sha, "branch": C.get("GH_BRANCH", "main")}).encode()
        req = urllib.request.Request(f"https://api.github.com/repos/{C['GH_REPO']}/contents/{urllib.parse.quote(ruta)}",
                                     data=body, method="DELETE", headers={"Authorization": f"Bearer {C['GH_TOKEN']}",
                                                                          "Accept": "application/vnd.github+json"})
        try:
            urllib.request.urlopen(req, timeout=60).read()
        except Exception as e:
            print(f"Aviso: no pude borrar {ruta} de GitHub ({e})", file=sys.stderr)
    SUBIDAS.clear()
    h = {"Authorization": f"Bearer {C.get('GH_TOKEN', '')}", "Accept": "application/vnd.github+json"}
    for rid, tag in RELEASES:
        for u in (f"https://api.github.com/repos/{C['GH_REPO']}/releases/{rid}",
                  f"https://api.github.com/repos/{C['GH_REPO']}/git/refs/tags/{tag}"):
            try:
                urllib.request.urlopen(urllib.request.Request(u, method="DELETE", headers=h), timeout=60).read()
            except Exception as e:
                print(f"Aviso: no pude borrar {u} ({e})", file=sys.stderr)
    RELEASES.clear()


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
    try:
        _main()
    finally:
        if SUBIDAS or RELEASES:
            borrar_github()


def _main():
    global PRUEBA
    ap = argparse.ArgumentParser()
    ap.add_argument("modo", choices=["check", "metricas", "github", "reel", "post", "carrusel", "historia"])
    ap.add_argument("--ultimos", type=int, default=25)
    ap.add_argument("archivos", nargs="*")
    ap.add_argument("--caption-file"); ap.add_argument("--comentario")
    ap.add_argument("--colab", action="append", default=[]); ap.add_argument("--cover-offset", type=int)
    ap.add_argument("--etiquetar", action="append", default=[], help="reel o historia: @cuenta a etiquetar (le llega la notificación; en historias puede compartirla)")
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
        u = api("GET", C.get("IG_USER_ID", "me"), {"fields": "username,media_count" if "facebook" in C.get("IG_HOST", "") else "username,account_type,media_count"})
        lim = api("GET", f"{C.get('IG_USER_ID')}/content_publishing_limit", {"fields": "quota_usage,config"})
        print(json.dumps({"ok": True, "cuenta": u, "cupo_24h": lim, "imagenes": ("GitHub " + C["GH_REPO"]) if C.get("GH_TOKEN") and C.get("GH_REPO") else (C.get("IMG_BASE_URL") or "FALTA (posts y carruseles)")}, ensure_ascii=False))
        return
    if a.modo == "metricas":  # sólo lectura: últimas publicaciones con sus números (necesita instagram_business_manage_insights)
        uid = C.get("IG_USER_ID", "me")
        cuenta = api("GET", uid, {"fields": "username,followers_count,media_count"})
        medias = api("GET", f"{uid}/media", {"fields": "id,caption,media_type,media_product_type,timestamp,permalink,like_count,comments_count", "limit": str(a.ultimos)}).get("data", [])
        for m in medias:
            pedir = ["views", "reach", "saved", "shares", "total_interactions"]
            if m.get("media_product_type") == "REELS":
                pedir += ["ig_reels_avg_watch_time"]
            m["caption"] = (m.get("caption") or "")[:120]
            try:
                ins = api("GET", f"{m['id']}/insights", {"metric": ",".join(pedir)}).get("data", [])
                m["insights"] = {i["name"]: (i.get("values") or [{}])[0].get("value", i.get("total_value", {}).get("value")) for i in ins}
            except SystemExit as e:
                m["insights"] = {"error": str(e)[:200]}
        print(json.dumps({"ok": True, "cuenta": cuenta, "publicaciones": medias}, ensure_ascii=False))
        return
    if a.modo == "github":  # prueba: sube una imagen, chequea que se vea y la borra (no toca Instagram)
        url = subir_github(a.archivos[0])
        ok = urllib.request.urlopen(url, timeout=30).status == 200
        borrar_github()
        print(json.dumps({"ok": ok, "subida_y_borrada": url}, ensure_ascii=False))
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
        if a.etiquetar:  # etiqueta real en el reel (les llega la notificación); si Instagram no puede, publica sin la etiqueta
            f["user_tags"] = json.dumps([{"username": c.lstrip("@")} for c in a.etiquetar])
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
        st = {"media_type": "STORIES"}
        if a.etiquetar:  # user_tags en historias: soportado por la API desde jul. 2025
            st["user_tags"] = json.dumps([{"username": c.lstrip("@")} for c in a.etiquetar])
        publicar(contenedor_item(a.archivos[0], st))


if __name__ == "__main__":
    main()
