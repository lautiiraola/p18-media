#!/usr/bin/env python3
"""Genera la voz en off de un video P18 Stories con la API de ElevenLabs.

Decisión de la persona (2026-11-25): la voz la genera el agente p18-historias, ya no Valentín a mano.
Se mantiene la misma voz y los mismos ajustes que usó Valentín en P18-001..003:
"Brian - Warm, Smooth, Confident", stability 0.50, similarity 0.75.

Uso:
  voz_elevenlabs.py TEXTO.txt SALIDA.wav            genera la voz (texto limpio, cifras en palabras)
  voz_elevenlabs.py --check                         verifica la clave, la voz y el modelo (no gasta caracteres)

Clave: ~/.config/p18/elevenlabs.env con
  ELEVENLABS_API_KEY=...
  ELEVENLABS_VOICE_ID=...      (opcional: si falta, busca "Brian" entre las voces de la cuenta)
  ELEVENLABS_MODEL=...         (opcional: si falta, el modelo más nuevo multilingüe disponible)
La clave nunca se imprime ni se copia a otro lado.
"""
import json, os, subprocess, sys, urllib.request, urllib.error
from pathlib import Path

ENV = Path.home() / ".config/p18/elevenlabs.env"
API = "https://api.elevenlabs.io/v1"
AJUSTES = {"stability": 0.50, "similarity_boost": 0.75, "style": 0.0, "use_speaker_boost": True}


def cfg():
    if not ENV.exists():
        sys.exit(f"Falta {ENV}. La persona tiene que crear ese archivo con ELEVENLABS_API_KEY=... (no pegarla en el chat).")
    c = {}
    for l in ENV.read_text().splitlines():
        if "=" in l and not l.strip().startswith("#"):
            k, v = l.split("=", 1)
            c[k.strip()] = v.strip().strip('"').strip("'")
    if not c.get("ELEVENLABS_API_KEY"):
        sys.exit("ELEVENLABS_API_KEY vacía en " + str(ENV))
    return c


def req(c, path, body=None, raw=False):
    r = urllib.request.Request(API + path, data=json.dumps(body).encode() if body else None,
                               headers={"xi-api-key": c["ELEVENLABS_API_KEY"], "Content-Type": "application/json",
                                        "Accept": "audio/wav" if raw else "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=300) as f:
            return f.read() if raw else json.loads(f.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"ElevenLabs respondió {e.code}: {e.read()[:300].decode(errors='replace')}")


def voz(c):
    if c.get("ELEVENLABS_VOICE_ID"):
        return c["ELEVENLABS_VOICE_ID"], "(ELEVENLABS_VOICE_ID)"
    vs = req(c, "/voices").get("voices", [])
    b = [v for v in vs if v.get("name", "").lower().startswith("brian")]
    b.sort(key=lambda v: ("warm" not in v["name"].lower(), v.get("category") != "professional"))
    if not b:
        sys.exit("No encontré la voz Brian en la cuenta. Agregala desde la Voice Library o poné ELEVENLABS_VOICE_ID.")
    return b[0]["voice_id"], b[0]["name"]


def modelo(c):
    if c.get("ELEVENLABS_MODEL"):
        return c["ELEVENLABS_MODEL"]
    ms = [m["model_id"] for m in req(c, "/models") if m.get("can_do_text_to_speech")]
    for pref in ("eleven_v4", "eleven_v3", "eleven_multilingual_v2"):
        hit = [m for m in ms if m.startswith(pref)]
        if hit:
            return hit[0]
    return ms[0]


def main():
    c = cfg()
    vid, nombre = voz(c)
    mod = modelo(c)
    if sys.argv[1:] == ["--check"]:
        u = req(c, "/user/subscription")
        print(f"OK · voz: {nombre} · modelo: {mod} · caracteres usados este mes: {u.get('character_count')}/{u.get('character_limit')}")
        return
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    texto = Path(sys.argv[1]).read_text().strip()
    out = Path(sys.argv[2])
    out.parent.mkdir(parents=True, exist_ok=True)
    audio = req(c, f"/text-to-speech/{vid}?output_format=pcm_44100", {"text": texto, "model_id": mod, "voice_settings": AJUSTES}, raw=True)
    pcm = out.with_suffix(".pcm")
    pcm.write_bytes(audio)
    ff = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
    ff = ff if Path(ff).exists() else "ffmpeg"
    subprocess.run([ff, "-nostdin", "-y", "-loglevel", "error", "-f", "s16le", "-ar", "44100", "-ac", "1", "-i", str(pcm), str(out)], check=True)
    pcm.unlink()
    print(f"{out} · {len(texto.split())} palabras · voz {nombre} · {mod}")


if __name__ == "__main__":
    main()
