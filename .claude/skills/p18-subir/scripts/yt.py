#!/usr/bin/env python3
"""YouTube Shorts de P18 con la API oficial (YouTube Data API v3). Sin dependencias externas.

Credenciales (nunca en el proyecto ni en el chat):
  ~/.config/p18/youtube_client.json   el "ID de cliente OAuth" (tipo App de escritorio) que bajás de Google Cloud
  ~/.config/p18/youtube_token.json    lo crea `yt.py conectar` (permisos 600)

Uso:
  yt.py conectar                     abre Google en el navegador, entrás con la cuenta del canal y aceptás (una vez)
  yt.py check                        muestra el canal conectado (no sube nada)
  yt.py short VIDEO.mp4 --titulo "…" --descripcion-file d.txt [--privacidad private|unlisted|public] [--prueba]
Imprime al final una línea JSON: {"ok": true, "id": "...", "url": "https://youtube.com/shorts/..."}.

Ojo: mientras Google no apruebe la app (auditoría de la API), YouTube deja todo lo que se sube por la API en PRIVADO,
aunque se pida "public". Se pasa a público a mano en YouTube Studio hasta que llegue la aprobación.
"""
import argparse, http.server, json, os, secrets, sys, time, urllib.parse, urllib.request, webbrowser
from pathlib import Path

CFG = Path.home() / ".config" / "p18"
CLIENT, TOKEN = CFG / "youtube_client.json", CFG / "youtube_token.json"
SCOPES = "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly"


def cliente():
    if not CLIENT.exists():
        sys.exit(f"Falta {CLIENT}. Seguí 'Conectar YouTube' en LEEME - Conectar Instagram (paso a paso).md.")
    c = json.loads(CLIENT.read_text())
    return c.get("installed") or c.get("web") or c


def post(url, data):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode())
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"Error de Google ({e.code}): {e.read().decode(errors='replace')[:500]}")


def guardar_token(t):
    CFG.mkdir(parents=True, exist_ok=True)
    TOKEN.write_text(json.dumps(t)); os.chmod(TOKEN, 0o600)


def conectar():
    c = cliente()
    estado, codigo = secrets.token_urlsafe(16), {}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            codigo.update({k: v[0] for k, v in q.items()})
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers()
            self.wfile.write("<h2>Listo. Ya podés cerrar esta pestaña y volver a Claude.</h2>".encode())

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(("127.0.0.1", 0), H)
    redirect = f"http://127.0.0.1:{srv.server_port}/"
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": c["client_id"], "redirect_uri": redirect, "response_type": "code", "scope": SCOPES,
        "access_type": "offline", "prompt": "consent", "state": estado})
    print("Se abre Google: entrá con la cuenta del canal de P18 y aceptá los permisos.")
    webbrowser.open(url)
    while "code" not in codigo and "error" not in codigo:
        srv.handle_request()
    if codigo.get("error") or codigo.get("state") != estado:
        sys.exit(f"No se pudo conectar: {codigo.get('error', 'respuesta inválida')}")
    t = post("https://oauth2.googleapis.com/token", {"code": codigo["code"], "client_id": c["client_id"],
             "client_secret": c["client_secret"], "redirect_uri": redirect, "grant_type": "authorization_code"})
    t["vence"] = time.time() + t.get("expires_in", 3600) - 60
    guardar_token(t)
    print("✓ YouTube conectado. Probá: yt.py check")


def acceso():
    if not TOKEN.exists():
        sys.exit("YouTube no está conectado: corré `yt.py conectar` (lo hace la persona).")
    t = json.loads(TOKEN.read_text())
    if time.time() > t.get("vence", 0):
        c = cliente()
        n = post("https://oauth2.googleapis.com/token", {"refresh_token": t["refresh_token"], "client_id": c["client_id"],
                 "client_secret": c["client_secret"], "grant_type": "refresh_token"})
        t.update(access_token=n["access_token"], vence=time.time() + n.get("expires_in", 3600) - 60)
        guardar_token(t)
    return t["access_token"]


def api(url, metodo="GET", body=None, headers=None):
    h = {"Authorization": "Bearer " + acceso(), **(headers or {})}
    req = urllib.request.Request(url, data=body, method=metodo, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=900) as r:
            return r.headers, (json.loads(r.read() or b"{}"))
    except urllib.error.HTTPError as e:
        sys.exit(f"Error de YouTube ({e.code}): {e.read().decode(errors='replace')[:600]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("modo", choices=["conectar", "check", "short"])
    ap.add_argument("video", nargs="?")
    ap.add_argument("--titulo"); ap.add_argument("--descripcion-file")
    ap.add_argument("--privacidad", default="public", choices=["private", "unlisted", "public"])
    ap.add_argument("--prueba", action="store_true")
    a = ap.parse_args()
    if a.modo == "conectar":
        return conectar()
    if a.modo == "check":
        _, r = api("https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&mine=true")
        ch = (r.get("items") or [{}])[0]
        print(json.dumps({"ok": bool(ch), "canal": ch.get("snippet", {}).get("title"), "id": ch.get("id"),
                          "suscriptores": ch.get("statistics", {}).get("subscriberCount")}, ensure_ascii=False))
        return
    if not a.video or not Path(a.video).exists():
        sys.exit("Falta el video (.mp4).")
    titulo = (a.titulo or "").strip()
    if "#shorts" not in titulo.lower() and len(titulo) <= 91:
        titulo += " #Shorts"
    if not 1 <= len(titulo) <= 100:
        sys.exit(f"El título tiene {len(titulo)} caracteres (YouTube: 1 a 100).")
    desc = Path(a.descripcion_file).read_text(encoding="utf-8").strip() if a.descripcion_file else ""
    meta = {"snippet": {"title": titulo, "description": desc[:5000], "categoryId": "27"},  # 27 = Educación
            "status": {"privacyStatus": a.privacidad, "selfDeclaredMadeForKids": False}}
    if a.prueba:
        print("[prueba] subiría", Path(a.video).name, json.dumps(meta, ensure_ascii=False)[:400])
        print(json.dumps({"ok": True, "id": "PRUEBA", "url": "PRUEBA"})); return
    tam = Path(a.video).stat().st_size
    h, _ = api("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status", "POST",
               json.dumps(meta).encode(), {"Content-Type": "application/json; charset=UTF-8",
                                           "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(tam)})
    _, r = api(h["Location"], "PUT", Path(a.video).read_bytes(), {"Content-Type": "video/mp4"})
    vid = r.get("id")
    estado = r.get("status", {}).get("privacyStatus")
    print(json.dumps({"ok": bool(vid), "id": vid, "url": f"https://youtube.com/shorts/{vid}", "privacidad": estado},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
