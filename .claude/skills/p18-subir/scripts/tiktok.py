#!/usr/bin/env python3
"""TikTok de P18 con la API oficial (Content Posting API, Direct Post). Sin dependencias externas.

Credenciales (nunca en el proyecto ni en el chat), en ~/.config/p18/meta.env:
  TT_CLIENT_KEY=...      Client key de la app en developers.tiktok.com
  TT_CLIENT_SECRET=...   Client secret de esa app
El token lo crea `tiktok.py conectar` en ~/.config/p18/tiktok_token.json (permisos 600).

Uso:
  tiktok.py conectar                 (la persona, en la Terminal) abre TikTok, aceptás y pegás la dirección de vuelta
  tiktok.py check                    muestra la cuenta y qué privacidad permite (no sube nada)
  tiktok.py borrador VIDEO.mp4      manda el video a la bandeja de TikTok (la persona lo publica desde la app)
  tiktok.py video VIDEO.mp4 --texto-file t.txt [--privacidad auto|SELF_ONLY|PUBLIC_TO_EVERYONE] [--prueba]
Imprime al final una línea JSON: {"ok": true, "publish_id": "...", "estado": "...", "privacidad": "..."}.

Mientras TikTok no apruebe la app (auditoría), sólo deja publicar en privado (SELF_ONLY): `auto` elige público si
TikTok lo permite y, si no, privado.
"""
import argparse, json, math, os, secrets, sys, time, urllib.parse, urllib.request, webbrowser
from pathlib import Path

CFG = Path.home() / ".config" / "p18"
ENV, TOKEN = CFG / "meta.env", CFG / "tiktok_token.json"
REDIRECT = "https://proyecto18-748.netlify.app/"
SCOPES = "user.info.basic,video.publish,video.upload"
API = "https://open.tiktokapis.com/v2/"


def env():
    c = {}
    if ENV.exists():
        for l in ENV.read_text().splitlines():
            if "=" in l and not l.strip().startswith("#"):
                k, v = l.split("=", 1); c[k.strip()] = v.strip().strip('"')
    if not c.get("TT_CLIENT_KEY") or not c.get("TT_CLIENT_SECRET"):
        sys.exit(f"Faltan TT_CLIENT_KEY y TT_CLIENT_SECRET en {ENV}.")
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
        sys.exit(f"Error de TikTok ({e.code}): {e.read().decode(errors='replace')[:600]}")


def guardar(t):
    CFG.mkdir(parents=True, exist_ok=True)
    TOKEN.write_text(json.dumps(t)); os.chmod(TOKEN, 0o600)


def conectar():
    c = env()
    estado = secrets.token_urlsafe(12)
    url = "https://www.tiktok.com/v2/auth/authorize/?" + urllib.parse.urlencode({
        "client_key": c["TT_CLIENT_KEY"], "scope": SCOPES, "response_type": "code", "redirect_uri": REDIRECT, "state": estado})
    print("\n1) Se abre TikTok: entrá con la cuenta de P18 y aceptá.")
    print(f"2) Te lleva a {REDIRECT} (puede verse vacía). Copiá la dirección COMPLETA de la barra y pegala acá.")
    print("   Si en la compu TikTok te pide un código por mail que no llega, abrí este link en el celular")
    print("   (donde la app de TikTok ya tiene la sesión abierta), aceptá y mandate a la compu la dirección final:\n")
    print("   " + url + "\n")
    webbrowser.open(url)
    q = urllib.parse.parse_qs(urllib.parse.urlparse(input("Dirección: ").strip()).query)
    if q.get("state", [""])[0] != estado or not q.get("code"):
        sys.exit("Esa dirección no trae el código de TikTok (o es de otro intento). Volvé a correr `conectar`.")
    t = pedir(API + "oauth/token/", data={"client_key": c["TT_CLIENT_KEY"], "client_secret": c["TT_CLIENT_SECRET"],
              "code": q["code"][0], "grant_type": "authorization_code", "redirect_uri": REDIRECT})
    if "access_token" not in t:
        sys.exit(f"TikTok no devolvió el token: {t}")
    t["vence"] = time.time() + t.get("expires_in", 86400) - 120
    guardar(t)
    print("✓ TikTok conectado. Permisos:", t.get("scope"), "· Probá: tiktok.py check")


def canjear(direccion):
    """Termina la conexión con la dirección final de TikTok (la de la web de P18 con ?code=...), sin pasar por input()."""
    c = env()
    q = urllib.parse.parse_qs(urllib.parse.urlparse(direccion.strip()).query)
    if not q.get("code"):
        sys.exit("Esa dirección no trae el código de TikTok.")
    t = pedir(API + "oauth/token/", data={"client_key": c["TT_CLIENT_KEY"], "client_secret": c["TT_CLIENT_SECRET"],
              "code": q["code"][0], "grant_type": "authorization_code", "redirect_uri": REDIRECT})
    if "access_token" not in t:
        sys.exit(f"TikTok no devolvió el token: {t.get('error') or t}")
    t["vence"] = time.time() + t.get("expires_in", 86400) - 120
    guardar(t)
    print("✓ TikTok conectado. Permisos:", t.get("scope"))


def subir_partes(up, video):
    tam = Path(video).stat().st_size
    trozo = tam if tam <= 64 * 1024 * 1024 else 10 * 1024 * 1024
    n = max(1, tam // trozo)
    with open(video, "rb") as f:
        for i in range(n):
            ini = i * trozo
            fin = tam - 1 if i == n - 1 else ini + trozo - 1
            f.seek(ini); parte = f.read(fin - ini + 1)
            pedir(up, metodo="PUT", crudo=parte, headers={"Content-Type": "video/mp4",
                  "Content-Length": str(len(parte)), "Content-Range": f"bytes {ini}-{fin}/{tam}"})


def borrador(tok, a):
    """Upload to TikTok: manda el video a la bandeja de la cuenta (notificación en la app). La persona abre la
    notificación, pega el texto y publica. Sirve sin auditoría. Máx. 5 borradores pendientes por día."""
    tam = Path(a.video).stat().st_size
    trozo = tam if tam <= 64 * 1024 * 1024 else 10 * 1024 * 1024
    n = max(1, tam // trozo)
    if a.prueba:
        print(json.dumps({"ok": True, "publish_id": "PRUEBA", "estado": "PRUEBA", "modo": "borrador"})); return
    r = pedir(API + "post/publish/inbox/video/init/", token=tok, js={
        "source_info": {"source": "FILE_UPLOAD", "video_size": tam, "chunk_size": trozo, "total_chunk_count": n}})
    if (r.get("error") or {}).get("code") not in (None, "ok"):
        sys.exit(f"TikTok: {r['error']}")
    subir_partes(r["data"]["upload_url"], a.video)
    pid, estado = r["data"]["publish_id"], "PROCESANDO"
    for _ in range(40):
        time.sleep(6)
        st = pedir(API + "post/publish/status/fetch/", token=tok, js={"publish_id": pid}).get("data", {})
        estado = st.get("status", estado)
        if estado in ("SEND_TO_USER_INBOX", "PUBLISH_COMPLETE", "FAILED"):
            if estado == "FAILED":
                sys.exit(f"TikTok rechazó el video: {st.get('fail_reason')}")
            break
    print(json.dumps({"ok": True, "publish_id": pid, "estado": estado, "modo": "borrador"}, ensure_ascii=False))


def acceso():
    if not TOKEN.exists():
        sys.exit("TikTok no está conectado: corré `tiktok.py conectar` (lo hace la persona).")
    t = json.loads(TOKEN.read_text())
    if time.time() > t.get("vence", 0):
        c = env()
        n = pedir(API + "oauth/token/", data={"client_key": c["TT_CLIENT_KEY"], "client_secret": c["TT_CLIENT_SECRET"],
                  "grant_type": "refresh_token", "refresh_token": t["refresh_token"]})
        if "access_token" not in n:
            sys.exit(f"No se pudo renovar el token de TikTok (hay que volver a `conectar`): {n}")
        t.update(n); t["vence"] = time.time() + n.get("expires_in", 86400) - 120
        guardar(t)
    return t["access_token"]


def creador(tok):
    r = pedir(API + "post/publish/creator_info/query/", js={}, token=tok)
    if (r.get("error") or {}).get("code") not in (None, "ok"):
        sys.exit(f"TikTok: {r['error']}")
    return r.get("data", {})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("modo", choices=["conectar", "canjear", "check", "video", "borrador"])
    ap.add_argument("video", nargs="?")
    ap.add_argument("--texto-file")
    ap.add_argument("--privacidad", default="auto")
    ap.add_argument("--prueba", action="store_true")
    a = ap.parse_args()
    if a.modo == "conectar":
        return conectar()
    if a.modo == "canjear":  # tiktok.py canjear "<dirección final con code=>"
        return canjear(a.video or "")
    tok = acceso()
    info = creador(tok)
    if a.modo == "check":
        print(json.dumps({"ok": True, "cuenta": info.get("creator_username"), "nombre": info.get("creator_nickname"),
                          "privacidades": info.get("privacy_level_options"),
                          "max_seg": info.get("max_video_post_duration_sec")}, ensure_ascii=False))
        return
    if not a.video or not Path(a.video).exists():
        sys.exit("Falta el video (.mp4).")
    if a.modo == "borrador":
        return borrador(tok, a)
    opciones = info.get("privacy_level_options") or ["SELF_ONLY"]
    priv = ("PUBLIC_TO_EVERYONE" if "PUBLIC_TO_EVERYONE" in opciones else "SELF_ONLY") if a.privacidad == "auto" else a.privacidad
    if priv not in opciones:
        sys.exit(f"TikTok no permite '{priv}' para esta cuenta; permite {opciones}.")
    texto = Path(a.texto_file).read_text(encoding="utf-8").strip()[:2200] if a.texto_file else ""
    tam = Path(a.video).stat().st_size
    trozo = tam if tam <= 64 * 1024 * 1024 else 10 * 1024 * 1024  # un solo envío hasta 64 MB; si no, de a 10 MB
    n = max(1, tam // trozo)
    if a.prueba:
        print(f"[prueba] subiría {Path(a.video).name} ({tam // 1048576} MB, {n} partes) como {priv}: {texto[:80]}…")
        print(json.dumps({"ok": True, "publish_id": "PRUEBA", "estado": "PRUEBA", "privacidad": priv})); return
    def iniciar(pv):
        try:
            return _iniciar(pv)
        except SystemExit as e:  # TikTok responde 403 si la app sin auditar intenta publicar en público
            if "unaudited" in str(e):
                return {"error": {"code": "unaudited_client_can_only_post_to_private_accounts"}}
            raise

    def _iniciar(pv):
        return pedir(API + "post/publish/video/init/", token=tok, js={
            "post_info": {"title": texto, "privacy_level": pv, "disable_comment": False, "disable_duet": False,
                          "disable_stitch": False, "brand_content_toggle": False, "brand_organic_toggle": False},
            "source_info": {"source": "FILE_UPLOAD", "video_size": tam, "chunk_size": trozo, "total_chunk_count": n}})
    r = iniciar(priv)
    # app sin auditar: TikTok rechaza lo público aunque lo liste como opción → con "auto", se sube en privado
    if a.privacidad == "auto" and priv != "SELF_ONLY" and "unaudited" in str((r.get("error") or {}).get("code", "")):
        priv = "SELF_ONLY"; r = iniciar(priv)
    if (r.get("error") or {}).get("code") not in (None, "ok"):
        sys.exit(f"TikTok: {r['error']}")
    up, pid = r["data"]["upload_url"], r["data"]["publish_id"]
    with open(a.video, "rb") as f:
        for i in range(n):
            ini = i * trozo
            fin = tam - 1 if i == n - 1 else ini + trozo - 1  # la última parte se lleva el resto
            f.seek(ini); parte = f.read(fin - ini + 1)
            pedir(up, metodo="PUT", crudo=parte, headers={"Content-Type": "video/mp4",
                  "Content-Length": str(len(parte)), "Content-Range": f"bytes {ini}-{fin}/{tam}"})
    estado = "PROCESANDO"
    for _ in range(40):  # hasta ~5 minutos
        time.sleep(8)
        s = pedir(API + "post/publish/status/fetch/", token=tok, js={"publish_id": pid}).get("data", {})
        estado = s.get("status", estado)
        if estado in ("PUBLISH_COMPLETE", "FAILED"):
            if estado == "FAILED":
                sys.exit(f"TikTok rechazó el video: {s.get('fail_reason')}")
            break
    print(json.dumps({"ok": True, "publish_id": pid, "estado": estado, "privacidad": priv,
                      "ids": s.get("publicaly_available_post_id")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
