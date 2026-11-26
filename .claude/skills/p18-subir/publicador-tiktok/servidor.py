#!/usr/bin/env python3
"""P18 Publicador para TikTok: app de escritorio (corre en la compu, se usa desde el navegador en http://localhost:8718).

Cumple las Content Sharing Guidelines de TikTok (Direct Post): muestra la cuenta, la persona elige la privacidad (sin
valor por defecto), activa a mano comentarios/dúo/stitch, declara contenido comercial, acepta el texto legal y toca
Publicar. Recién ahí se manda el video a TikTok. El agente de P18 sólo prepara la cola (video + texto sugerido).

Credenciales en ~/.config/p18/meta.env: TT_CLIENT_KEY, TT_CLIENT_SECRET (los de la app; en sandbox, los del sandbox).
Login Kit for Desktop: redirect http://localhost:8718/callback/ con PKCE S256 (TikTok usa SHA256 en hexadecimal).
Cola: "04 Instagram/TikTok - cola.json" → [{"id", "titulo", "video" (ruta relativa a la carpeta P18), "texto"}].

Uso:  python3 servidor.py            (abre el navegador)
"""
import hashlib, json, os, secrets, sys, threading, time, urllib.error, urllib.parse, urllib.request, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PUERTO = 8718
REDIRECT = f"http://localhost:{PUERTO}/callback/"
SCOPES = "user.info.basic,video.publish"
API = "https://open.tiktokapis.com/v2/"
AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[3]  # publicador-tiktok → p18-subir → skills → .claude → carpeta P18
COLA = RAIZ / "04 Instagram" / "TikTok - cola.json"
CFG = Path.home() / ".config" / "p18"
TOKEN = CFG / "tiktok_token_publicador.json"
ESTADO = {}  # state → code_verifier


def env():
    c = {}
    for l in (CFG / "meta.env").read_text().splitlines():
        if "=" in l and not l.strip().startswith("#"):
            k, v = l.split("=", 1); c[k.strip()] = v.strip()
    return c


def pedir(url, data=None, js=None, token=None, metodo=None, headers=None, crudo=None):
    h = dict(headers or {})
    if token:
        h["Authorization"] = "Bearer " + token
    body = crudo
    if js is not None:
        body = json.dumps(js).encode(); h["Content-Type"] = "application/json; charset=UTF-8"
    elif data is not None:
        body = urllib.parse.urlencode(data).encode(); h["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(url, data=body, headers=h, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=900) as r:
            t = r.read()
            return json.loads(t) if t.strip().startswith(b"{") else {}
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read())
        except Exception:
            return {"error": {"code": f"http_{e.code}", "message": "Error de TikTok"}}


def token():
    if not TOKEN.exists():
        return None
    t = json.loads(TOKEN.read_text())
    if time.time() > t.get("vence", 0):
        c = env()
        n = pedir(API + "oauth/token/", data={"client_key": c["TT_CLIENT_KEY"], "client_secret": c["TT_CLIENT_SECRET"],
                                             "grant_type": "refresh_token", "refresh_token": t["refresh_token"]})
        if "access_token" not in n:
            return None
        n["vence"] = time.time() + n.get("expires_in", 86400) - 120
        guardar(n); t = n
    return t["access_token"]


def guardar(t):
    CFG.mkdir(parents=True, exist_ok=True)
    TOKEN.write_text(json.dumps(t)); os.chmod(TOKEN, 0o600)


def cola():
    return json.loads(COLA.read_text(encoding="utf-8")) if COLA.exists() else []


def duracion(video):
    import subprocess
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def responder(self, cod, cuerpo, tipo="application/json; charset=utf-8", extra=None):
        b = cuerpo if isinstance(cuerpo, bytes) else (json.dumps(cuerpo, ensure_ascii=False) if not isinstance(cuerpo, str) else cuerpo).encode()
        self.send_response(cod); self.send_header("Content-Type", tipo); self.send_header("Content-Length", str(len(b)))
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path); q = urllib.parse.parse_qs(u.query)
        if u.path == "/":
            return self.responder(200, (AQUI / "index.html").read_bytes(), "text/html; charset=utf-8")
        if u.path == "/demo-tiktok.mp4" and (AQUI / "demo-tiktok.mp4").exists():  # para adjuntarlo en el formulario de revisión
            return self.responder(200, (AQUI / "demo-tiktok.mp4").read_bytes(), "video/mp4",
                                  extra={"Access-Control-Allow-Origin": "https://developers.tiktok.com"})
        if u.path == "/logo.svg":
            return self.responder(200, (AQUI / "logo.svg").read_bytes(), "image/svg+xml")
        if u.path == "/login":
            c = env(); estado = secrets.token_urlsafe(16); verif = secrets.token_urlsafe(64)[:96]
            ESTADO[estado] = verif
            reto = hashlib.sha256(verif.encode()).hexdigest()  # TikTok Desktop: SHA256 en hexadecimal
            url = "https://www.tiktok.com/v2/auth/authorize/?" + urllib.parse.urlencode({
                "client_key": c["TT_CLIENT_KEY"], "scope": SCOPES, "response_type": "code", "redirect_uri": REDIRECT,
                "state": estado, "code_challenge": reto, "code_challenge_method": "S256"})
            return self.responder(302, b"", extra={"Location": url})
        if u.path == "/callback/":
            estado, code = q.get("state", [""])[0], q.get("code", [""])[0]
            verif = ESTADO.pop(estado, None)
            if not code or not verif:
                return self.responder(400, "<p>No se pudo iniciar sesión. Volvé a intentar.</p><a href='/'>Volver</a>", "text/html; charset=utf-8")
            c = env()
            t = pedir(API + "oauth/token/", data={"client_key": c["TT_CLIENT_KEY"], "client_secret": c["TT_CLIENT_SECRET"],
                      "code": code, "grant_type": "authorization_code", "redirect_uri": REDIRECT, "code_verifier": verif})
            if "access_token" not in t:
                return self.responder(400, f"<p>TikTok no devolvió el acceso: {t.get('error_description') or t.get('error')}</p><a href='/'>Volver</a>", "text/html; charset=utf-8")
            t["vence"] = time.time() + t.get("expires_in", 86400) - 120
            guardar(t)
            return self.responder(302, b"", extra={"Location": "/"})
        if u.path == "/logout":
            TOKEN.unlink(missing_ok=True)
            return self.responder(302, b"", extra={"Location": "/"})
        if u.path == "/api/creador":
            tok = token()
            if not tok:
                return self.responder(200, {"conectado": False})
            r = pedir(API + "post/publish/creator_info/query/", js={}, token=tok, metodo="POST")
            return self.responder(200, {"conectado": True, **r})
        if u.path == "/api/cola":
            out = []
            for it in [x for x in cola() if not x.get("enviado")]:
                v = RAIZ / it["video"]
                out.append({**it, "existe": v.exists(), "dur": round(duracion(v), 1) if v.exists() else 0})
            return self.responder(200, out)
        if u.path.startswith("/video/"):
            it = next((x for x in cola() if x["id"] == u.path.split("/")[-1]), None)
            if not it or not (RAIZ / it["video"]).exists():
                return self.responder(404, {"error": "no existe"})
            return self.enviar_video(RAIZ / it["video"])
        if u.path == "/api/estado":
            r = pedir(API + "post/publish/status/fetch/", js={"publish_id": q.get("id", [""])[0]}, token=token(), metodo="POST")
            return self.responder(200, r)
        self.responder(404, {"error": "no existe"})

    def enviar_video(self, v):
        tam = v.stat().st_size; rango = self.headers.get("Range")
        ini, fin = 0, tam - 1
        if rango and rango.startswith("bytes="):
            a, _, b = rango[6:].partition("-"); ini = int(a or 0); fin = int(b) if b else min(tam - 1, ini + 4 * 1024 * 1024)
        self.send_response(206 if rango else 200)
        self.send_header("Content-Type", "video/mp4"); self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(fin - ini + 1))
        if rango:
            self.send_header("Content-Range", f"bytes {ini}-{fin}/{tam}")
        self.end_headers()
        with open(v, "rb") as f:
            f.seek(ini); self.wfile.write(f.read(fin - ini + 1))

    def do_POST(self):
        if self.path != "/api/publicar":
            return self.responder(404, {"error": "no existe"})
        p = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        tok = token()
        if not tok:
            return self.responder(401, {"error": "Iniciá sesión con TikTok."})
        it = next((x for x in cola() if x["id"] == p.get("id")), None)
        if not it:
            return self.responder(404, {"error": "Ese video ya no está en la cola."})
        v = RAIZ / it["video"]
        info = pedir(API + "post/publish/creator_info/query/", js={}, token=tok, metodo="POST")
        err = (info.get("error") or {}).get("code")
        if err not in (None, "ok"):
            return self.responder(400, {"error": "Esta cuenta no puede publicar en este momento. Probá más tarde.", "detalle": err})
        d = info.get("data", {})
        if p.get("privacy_level") not in (d.get("privacy_level_options") or []):
            return self.responder(400, {"error": "Elegí quién puede ver el video."})
        if d.get("max_video_post_duration_sec") and duracion(v) > d["max_video_post_duration_sec"]:
            return self.responder(400, {"error": f"El video dura más de lo que esta cuenta permite ({d['max_video_post_duration_sec']} s)."})
        tam = v.stat().st_size
        trozo = tam if tam <= 64 * 1024 * 1024 else 10 * 1024 * 1024
        n = max(1, tam // trozo)
        r = pedir(API + "post/publish/video/init/", token=tok, js={
            "post_info": {"title": p.get("title", "")[:2200], "privacy_level": p["privacy_level"],
                          "disable_comment": not p.get("comment"), "disable_duet": not p.get("duet"),
                          "disable_stitch": not p.get("stitch"),
                          "brand_content_toggle": bool(p.get("brand_content")), "brand_organic_toggle": bool(p.get("brand_organic"))},
            "source_info": {"source": "FILE_UPLOAD", "video_size": tam, "chunk_size": trozo, "total_chunk_count": n}})
        err = (r.get("error") or {}).get("code")
        if err not in (None, "ok"):
            return self.responder(400, {"error": "TikTok no aceptó la publicación.", "detalle": err})
        up = r["data"]["upload_url"]
        with open(v, "rb") as f:
            for i in range(n):
                ini = i * trozo; fin = tam - 1 if i == n - 1 else ini + trozo - 1
                f.seek(ini); parte = f.read(fin - ini + 1)
                pedir(up, metodo="PUT", crudo=parte, headers={"Content-Type": "video/mp4", "Content-Length": str(len(parte)),
                                                             "Content-Range": f"bytes {ini}-{fin}/{tam}"})
        todo = cola()  # queda registrado en la cola; la próxima vez ya no aparece
        for x in todo:
            if x["id"] == it["id"]:
                x["enviado"] = {"publish_id": r["data"]["publish_id"], "privacidad": p["privacy_level"], "cuando": int(time.time())}
        COLA.write_text(json.dumps(todo, ensure_ascii=False, indent=1), encoding="utf-8")
        self.responder(200, {"publish_id": r["data"]["publish_id"]})


if __name__ == "__main__":
    s = ThreadingHTTPServer(("127.0.0.1", PUERTO), H)
    print(f"P18 Publicador para TikTok → http://localhost:{PUERTO}  (Ctrl+C para cerrar)")
    if "--sin-abrir" not in sys.argv:
        threading.Timer(0.8, lambda: webbrowser.open(f"http://localhost:{PUERTO}")).start()
    s.serve_forever()
