#!/usr/bin/env python3
"""Pide un token de Instagram con los permisos exactos (incluido el de métricas) y lo guarda en ~/.config/p18/meta.env.

Se corre en la Terminal de la persona (nunca por el chat):  python3 token_ig.py
Necesita en meta.env:  IG_APP_ID=...  e  IG_APP_SECRET=...  (Identificador y Clave secreta de la app de Instagram,
en developers.facebook.com → Casos de uso → API de Instagram → Configurar API con inicio de sesión de Instagram).
La URL de redireccionamiento (REDIRECT) tiene que estar registrada igual en esa pantalla.
El token nunca se muestra: se escribe directo en el archivo (permisos 600).
"""
import json, os, sys, urllib.parse, urllib.request, webbrowser
from pathlib import Path

CFG = Path.home() / ".config" / "p18" / "meta.env"
REDIRECT = "https://proyecto18.com/"
SCOPES = "instagram_business_basic,instagram_business_content_publish,instagram_business_manage_insights"


def leer():
    c = {}
    for l in CFG.read_text().splitlines():
        if "=" in l and not l.strip().startswith("#"):
            k, v = l.split("=", 1)
            c[k.strip()] = v.strip().strip('"')
    return c


def guardar(clave, valor):
    lineas, hecho = CFG.read_text().splitlines(), False
    for i, l in enumerate(lineas):
        if l.split("=", 1)[0].strip() == clave:
            lineas[i] = f"{clave}={valor}"; hecho = True
    if not hecho:
        lineas.append(f"{clave}={valor}")
    CFG.write_text("\n".join(lineas) + "\n"); os.chmod(CFG, 0o600)


def pedir(url, data=None):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode() if data else None)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"Error de Instagram ({e.code}): {e.read().decode(errors='replace')[:400]}")


c = leer()
if not c.get("IG_APP_ID") or not c.get("IG_APP_SECRET"):
    sys.exit(f"Faltan IG_APP_ID e IG_APP_SECRET en {CFG}. Agregalos y volvé a correr.")

auth = "https://www.instagram.com/oauth/authorize?" + urllib.parse.urlencode({
    "client_id": c["IG_APP_ID"], "redirect_uri": REDIRECT, "response_type": "code",
    "scope": SCOPES, "force_reauth": "true"})
print("\n1) Se abre Instagram en el navegador. Entrá con la cuenta de P18 y aceptá los permisos (tienen que ser 3,")
print("   incluido el de estadísticas).")
print("2) Te va a llevar a la web de P18. Copiá la dirección COMPLETA de la barra (empieza con", REDIRECT + "?code=)")
print("   y pegala acá abajo.\n")
webbrowser.open(auth)
pegado = input("Dirección: ").strip()
code = urllib.parse.parse_qs(urllib.parse.urlparse(pegado).query).get("code", [pegado])[0].split("#")[0]
if not code:
    sys.exit("No encontré el código en esa dirección.")

corto = pedir("https://api.instagram.com/oauth/access_token", {
    "client_id": c["IG_APP_ID"], "client_secret": c["IG_APP_SECRET"], "grant_type": "authorization_code",
    "redirect_uri": REDIRECT, "code": code})
corto = corto.get("data", [corto])[0] if isinstance(corto.get("data"), list) else corto
largo = pedir("https://graph.instagram.com/access_token?" + urllib.parse.urlencode({
    "grant_type": "ig_exchange_token", "client_secret": c["IG_APP_SECRET"], "access_token": corto["access_token"]}))

guardar("IG_TOKEN", largo["access_token"])
print(f"\n✓ Token guardado en {CFG} (vence en {int(largo.get('expires_in', 0)) // 86400} días).")
print("  Permisos:", corto.get("permissions", "(no informados)"))
print("  Volvé al chat y escribí: listo el token")
