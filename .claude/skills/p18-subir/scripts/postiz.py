#!/usr/bin/env python3
"""TikTok de P18 a través de Postiz (app de TikTok ya auditada: publica en PÚBLICO). Sin dependencias externas.

Credencial (nunca en el proyecto ni en el chat), en ~/.config/p18/meta.env:
  POSTIZ_API_KEY=...     Postiz → Settings → Public API
  POSTIZ_URL=...         opcional; por defecto https://api.postiz.com/public/v1 (Postiz Cloud)

Uso:
  postiz.py check                                   muestra los canales conectados (no publica)
  postiz.py tiktok VIDEO.mp4 --texto-file t.txt [--titulo "..."] [--privacidad PUBLIC_TO_EVERYONE] [--prueba]
Imprime al final una línea JSON: {"ok": true, "post_id": "...", "estado": "...", "url": "..."}.
"""
import argparse, json, mimetypes, sys, time, uuid, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ENV = Path.home() / ".config" / "p18" / "meta.env"


def env():
    c = {}
    if ENV.exists():
        for l in ENV.read_text().splitlines():
            if "=" in l and not l.strip().startswith("#"):
                k, v = l.split("=", 1); c[k.strip()] = v.strip()
    if not c.get("POSTIZ_API_KEY"):
        sys.exit(f"Falta POSTIZ_API_KEY en {ENV} (Postiz → Settings → Public API).")
    return c


C = None


def api(metodo, ruta, js=None, datos=None, tipo=None, query=None):
    base = C.get("POSTIZ_URL", "https://api.postiz.com/public/v1").rstrip("/")
    url = base + ruta + ("?" + urllib.parse.urlencode(query) if query else "")
    h = {"Authorization": C["POSTIZ_API_KEY"], "Accept": "application/json"}
    body = None
    if js is not None:
        body = json.dumps(js).encode(); h["Content-Type"] = "application/json"
    elif datos is not None:
        body = datos; h["Content-Type"] = tipo
    req = urllib.request.Request(url, data=body, headers=h, method=metodo)
    for intento in range(4):
        try:
            with urllib.request.urlopen(req, timeout=900) as r:
                t = r.read()
                return json.loads(t) if t.strip()[:1] in (b"{", b"[") else {}
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:600]
            if e.code >= 500 and intento < 3:
                time.sleep(5 * 2 ** intento); continue
            sys.exit(f"Error de Postiz ({e.code}) en {ruta}: {msg}")


def canal_tiktok():
    canales = api("GET", "/integrations")
    canales = canales if isinstance(canales, list) else canales.get("integrations", canales.get("data", []))
    tt = [c for c in canales if "tiktok" in str(c.get("identifier", "")).lower() and not c.get("disabled")]
    if not tt:
        sys.exit("No hay un canal de TikTok conectado en Postiz. Conectalo en Postiz → Add channel → TikTok.")
    return tt[0]


def subir(video):
    limite = "----p18" + uuid.uuid4().hex
    nombre = Path(video).name.encode("ascii", "ignore").decode() or "video.mp4"
    tipo = mimetypes.guess_type(video)[0] or "video/mp4"
    cuerpo = (f"--{limite}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{nombre}\"\r\n"
              f"Content-Type: {tipo}\r\n\r\n").encode() + Path(video).read_bytes() + f"\r\n--{limite}--\r\n".encode()
    m = api("POST", "/upload", datos=cuerpo, tipo=f"multipart/form-data; boundary={limite}")
    for _ in range(60):  # espera a que Postiz termine de procesar el video
        if m.get("status", "ready") == "ready" or not m.get("id"):
            break
        time.sleep(5)
        m.update(api("GET", f"/media/{m['id']}/status"))
        if m.get("status") == "failed":
            sys.exit(f"Postiz no pudo procesar el video: {m.get('error')}")
    return {"id": m["id"], "path": m["path"]}


def buscar(post_id, desde):
    hasta = datetime.now(timezone.utc) + timedelta(minutes=5)
    r = api("GET", "/posts", query={"startDate": desde.isoformat().replace("+00:00", "Z"),
                                     "endDate": hasta.isoformat().replace("+00:00", "Z")})
    lista = r if isinstance(r, list) else r.get("posts", r.get("data", []))
    return next((p for p in lista if p.get("id") == post_id), None)


def main():
    global C
    ap = argparse.ArgumentParser()
    ap.add_argument("modo", choices=["check", "tiktok"]); ap.add_argument("video", nargs="?")
    ap.add_argument("--texto-file"); ap.add_argument("--titulo", default="")
    ap.add_argument("--privacidad", default="PUBLIC_TO_EVERYONE"); ap.add_argument("--prueba", action="store_true")
    a = ap.parse_args()
    C = env()
    if a.modo == "check":
        t = canal_tiktok()
        print(json.dumps({"ok": True, "tiktok": {"id": t.get("id"), "nombre": t.get("name"), "cuenta": t.get("profile")}},
                         ensure_ascii=False)); return
    if not a.video or not Path(a.video).exists():
        sys.exit("Falta el video (.mp4).")
    texto = Path(a.texto_file).read_text(encoding="utf-8").strip()[:2200] if a.texto_file else ""
    canal = canal_tiktok()
    if a.prueba:
        print(f"[prueba] subiría {Path(a.video).name} a TikTok ({canal.get('profile')}) como {a.privacidad}: {texto[:80]}…")
        print(json.dumps({"ok": True, "post_id": "PRUEBA", "estado": "PRUEBA"})); return
    media = subir(a.video)
    ahora = datetime.now(timezone.utc)
    r = api("POST", "/posts", js={
        "type": "now", "date": ahora.strftime("%Y-%m-%dT%H:%M:%S.000Z"), "shortLink": False, "tags": [],
        "posts": [{"integration": {"id": canal["id"]},
                   "value": [{"content": texto, "image": [media]}],
                   "settings": {"__type": "tiktok", "title": (a.titulo or texto.splitlines()[0] if texto else "")[:90],
                                "privacy_level": a.privacidad, "duet": True, "stitch": True, "comment": True,
                                "autoAddMusic": "no", "brand_content_toggle": False, "brand_organic_toggle": False,
                                "video_made_with_ai": False, "content_posting_method": "DIRECT_POST"}}]})
    pid = (r[0] if isinstance(r, list) and r else r).get("postId")
    estado, url, error = "QUEUE", None, None
    for _ in range(40):  # hasta ~6 minutos
        time.sleep(9)
        p = buscar(pid, ahora - timedelta(minutes=5)) if pid else None
        if p:
            estado, url, error = p.get("state", estado), p.get("releaseURL"), p.get("error")
            if estado in ("PUBLISHED", "ERROR"):
                break
    if estado == "ERROR":
        sys.exit(f"TikTok (vía Postiz) rechazó el video: {error}")
    print(json.dumps({"ok": True, "post_id": pid, "estado": estado, "url": url, "privacidad": a.privacidad},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
