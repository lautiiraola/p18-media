#!/usr/bin/env python3
"""p18-clipear: de un link de YouTube (o un .mp4) a clips crudos para revisar.

  p18-clipear preparar URL|video.mp4 [--fuente "Nombre"] [--whisper]
      Modo liviano (por defecto con links): baja SÓLO los subtítulos automáticos de
      YouTube (segundos, sin CPU) y arma transcripcion.txt para elegir momentos.
      Si el video no tiene subtítulos, o es un .mp4 local, o se pasa --whisper:
      descarga el video y lo transcribe entero con faster-whisper (lento).

  p18-clipear cortar CARPETA plan.json
      Por cada momento: baja sólo ese tramo (o lo toma del .mp4 local), lo transcribe con
      Whisper para ajustar el corte a las palabras exactas y lo deja crudo con su .txt.

Carpeta: "06 Biblioteca/Clips crudos/<fecha> - <fuente>/", con los datos en "_original/".
"""
import argparse, datetime, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

AREAS = {
    "Crecimiento personal": ["Autoconocimiento", "Hábitos y constancia", "Mentalidad y adaptación", "Liderazgo"],
    "Finanzas y trabajo": ["Finanzas personales", "Trabajo y oportunidades", "Ideas, proyectos y ventas"],
    "Crear y comunicar": ["Vínculos y comunicación", "Redes y contenido", "Inteligencia artificial"],
    "Creatividad": ["Pensamiento creativo", "Arte y diseño", "Música y audiovisual", "Escritura y relatos"],
    "Salud": ["Salud mental", "Vínculos", "Salud física", "Alimentación", "Sueño", "Bienestar"],
    "Deporte y mentalidad": ["Disciplina y proceso", "Presión y dificultad", "Liderazgo y equipo", "Mentalidad aplicada"],
}
# H.264 + AAC hasta 1080p: se ve en cualquier Mac y alcanza para el recuadro de 1000 px.
# La mejor imagen de YouTube hasta 1440p (VP9/AV1: bastante más nítida que el H.264 1080p de YouTube).
# El recuadro del reel mide 1000 px, así que 1440p alcanza sin pérdida visible; 4K sólo sumaba peso y tiempo.
FORMATO = "bv*[height<=1440]+ba/bv*+ba/b"
MARGEN = 2.5  # segundos extra a cada lado del tramo que se transcribe con Whisper


def die(msg, code=1):
    print(f"\n✗ {msg}", file=sys.stderr)
    sys.exit(code)


def buscar_ffmpeg():
    for c in [os.environ.get("P18_FFMPEG"), "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg",
              "/usr/local/opt/ffmpeg-full/bin/ffmpeg", shutil.which("ffmpeg")]:
        if c and Path(c).exists():
            return c
    die("No encontré ffmpeg. Corré scripts/setup.sh.")


def buscar_raiz(arg):
    if arg:
        return Path(arg).expanduser().resolve()
    if os.environ.get("P18_RAIZ"):
        return Path(os.environ["P18_RAIZ"]).expanduser().resolve()
    for base in [Path.cwd(), *Path.cwd().parents, AQUI, *AQUI.parents]:
        if (base / "06 Biblioteca").is_dir() and (base / "04 Instagram").is_dir():
            return base
    die("No encontré la carpeta de Proyecto 18. Pasá --raiz o definí P18_RAIZ.")


def limpio(s, n=60):
    s = re.sub(r'[\\/:*?"<>|#]+', " ", s or "")
    s = re.sub(r"\s+", " ", s).strip(" .-")
    return s[:n].strip() or "sin nombre"


def mmss(t):
    m, s = divmod(max(0.0, t), 60)
    h, m = divmod(int(m), 60)
    return f"{h}:{m:02d}:{s:04.1f}" if h else f"{m:02d}:{s:04.1f}"


def ydl(**opts):
    import yt_dlp
    base = {"quiet": True, "no_warnings": True}
    base.update(opts)
    return yt_dlp.YoutubeDL(base)


# ---------------- subtítulos de YouTube ----------------

def elegir_pista(info):
    """Devuelve (clave, lista_de_formatos, tipo) de la mejor pista en el idioma original."""
    auto = info.get("automatic_captions") or {}
    manual = {k: v for k, v in (info.get("subtitles") or {}).items() if k != "live_chat"}
    orig = [k for k in auto if k.endswith("-orig")]
    lang = info.get("language") or (orig[0][:-5] if orig else "es")
    for k in manual:
        if k == lang or k.startswith(lang + "-"):
            return k, manual[k], "manual"
    for k in (f"{lang}-orig", lang):
        if k in auto:
            return k, auto[k], "automáticos"
    return None, None, None


def palabras_json3(data):
    """json3 de YouTube → lista de palabras con tiempos (los automáticos traen tiempo por palabra)."""
    eventos = [e for e in data.get("events", []) if e.get("segs")]
    crudas = []
    for i, e in enumerate(eventos):
        t0 = e.get("tStartMs", 0) / 1000
        dur = (e.get("dDurationMs") or 2000) / 1000
        segs = [s for s in e["segs"] if s.get("utf8", "").strip()]
        if not segs:
            continue
        if len(segs) > 1 or "tOffsetMs" in segs[0]:
            for s in segs:
                for p in s["utf8"].split():
                    crudas.append([t0 + s.get("tOffsetMs", 0) / 1000, p])
        else:  # subtítulo manual: una frase por evento → repartir el tiempo
            ps = segs[0]["utf8"].split()
            for j, p in enumerate(ps):
                crudas.append([t0 + dur * j / len(ps), p])
    crudas.sort(key=lambda x: x[0])
    out = []
    for i, (t, p) in enumerate(crudas):
        sig = crudas[i + 1][0] if i + 1 < len(crudas) else t + 0.5
        out.append({"ini": round(t, 2), "fin": round(min(sig, t + 1.5), 2), "p": p})
    return out


def segmentar(palabras, max_palabras=30, pausa=1.2):
    segs, cur = [], []
    for w in palabras:
        if cur and (w["ini"] - cur[-1]["fin"] > pausa or len(cur) >= max_palabras
                    or (cur[-1]["p"][-1:] in ".?!" and len(cur) >= 8)):
            segs.append(cur); cur = []
        cur.append(w)
    if cur:
        segs.append(cur)
    return [{"ini": s[0]["ini"], "fin": s[-1]["fin"], "texto": " ".join(w["p"] for w in s), "palabras": s} for s in segs]


# ---------------- calidad de los subtítulos ----------------

def entradas_remotas(url, formato=FORMATO):
    """URLs directas (video/audio) de YouTube para que ffmpeg lea sólo el tramo que hace falta."""
    with ydl(format=formato) as y:
        info = y.extract_info(url, download=False)
    out = []
    for f in (info.get("requested_formats") or [info]):
        hdr = "".join(f"{k}: {v}\r\n" for k, v in (f.get("http_headers") or {}).items())
        out.append({"url": f["url"], "hdr": hdr, "tipo": "v" if f.get("vcodec") not in (None, "none") else "a"})
    return out


def _normal(texto):
    import unicodedata
    t = unicodedata.normalize("NFKD", texto.lower())
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    return re.findall(r"[a-z0-9ñ]+", t)


def calidad_subtitulos(url, ws, duracion, idioma, ffmpeg, modelo="medium"):
    """Compara 2 muestras de 45 s de los subtítulos contra Whisper. Devuelve (puntaje 0-1, detalle)."""
    import difflib
    if duracion <= 0 or not ws:
        return 0.0, "sin subtítulos"
    wpm = len(ws) / (duracion / 60)
    musica = sum(1 for w in ws if re.match(r"^\[.*\]$", w["p"])) / len(ws)
    if wpm < 40 or musica > 0.2:
        return 0.0, f"muy pocas palabras ({wpm:.0f}/min) o casi todo [Música]"
    from transcribir import transcribir
    audio = [e for e in entradas_remotas(url, "ba[ext=m4a]/ba/b") if e["tipo"] == "a"] or entradas_remotas(url, "ba/b")
    e = audio[0]
    puntajes = []
    for frac in (0.3, 0.65):
        t0 = max(0.0, duracion * frac)
        t1 = t0 + 45
        ref = [w["p"] for w in ws if t0 + 2 <= w["ini"] <= t1 - 2]
        if len(ref) < 30:
            continue
        with tempfile.TemporaryDirectory() as tmp:
            wav = os.path.join(tmp, "m.wav")
            subprocess.run([ffmpeg, "-v", "error", "-y", "-ss", f"{t0:.2f}"] + (["-headers", e["hdr"]] if e["hdr"] else [])
                           + ["-i", e["url"], "-t", "45", "-ac", "1", "-ar", "16000", wav], check=True)
            tr = transcribir(wav, modelo, idioma, ffmpeg=ffmpeg, log=False)
        hyp = [w["p"] for sg in tr["segmentos"] for w in sg["palabras"] if 2 <= w["ini"] <= 43]
        puntajes.append(difflib.SequenceMatcher(None, _normal(" ".join(ref)), _normal(" ".join(hyp))).ratio())
    if not puntajes:
        return 0.5, f"no pude comparar ({wpm:.0f} palabras/min)"
    p = sum(puntajes) / len(puntajes)
    return p, f"coinciden {p:.0%} con Whisper en {len(puntajes)} muestras de 45 s ({wpm:.0f} palabras/min)"


UMBRAL_SUBS = 0.6


# ---------------- preparar ----------------

def carpeta_para(raiz, meta, fuente, hoy):
    base = raiz / "06 Biblioteca" / "Clips crudos"
    if base.is_dir():
        for m in base.glob("*/_original/meta.json"):
            try:
                old = json.loads(m.read_text(encoding="utf-8"))
            except Exception:
                continue
            if (meta.get("id") and old.get("id") == meta.get("id")) or \
               (meta.get("archivo") and old.get("archivo") == meta.get("archivo")):
                print(f"• Ya existe una carpeta para este video: {m.parent.parent}")
                return m.parent.parent
    carpeta = base / f"{hoy} - {limpio(fuente)}"
    n = 2
    while carpeta.exists():
        carpeta = base / f"{hoy} - {limpio(fuente)} ({n})"
        n += 1
    return carpeta


def preparar(a):
    raiz = buscar_raiz(a.raiz)
    ffmpeg = buscar_ffmpeg()
    hoy = datetime.date.today().isoformat()
    es_url = re.match(r"https?://", a.origen) is not None
    info = None

    if es_url:
        with ydl() as y:
            info = y.extract_info(a.origen, download=False)
        meta = {"url": info.get("webpage_url") or a.origen, "titulo": info.get("title"),
                "canal": info.get("channel") or info.get("uploader"), "fecha_publicacion": info.get("upload_date"),
                "duracion": info.get("duration"), "id": info.get("id")}
        fuente = a.fuente or meta["canal"] or meta["titulo"]
    else:
        src = Path(a.origen).expanduser().resolve()
        if not src.exists():
            die(f"No existe: {src}")
        meta = {"archivo": str(src), "titulo": src.stem}
        fuente = a.fuente or src.stem

    carpeta = carpeta_para(raiz, meta, fuente, hoy)
    orig = carpeta / "_original"
    orig.mkdir(parents=True, exist_ok=True)
    mj = orig / "meta.json"
    if mj.exists():  # conservar datos previos (p. ej. video ya descargado)
        meta = {**json.loads(mj.read_text(encoding="utf-8")), **meta}
    meta["fuente"] = fuente
    tj = orig / "transcripcion.json"

    # --- modo liviano: subtítulos de YouTube ---
    if es_url and not a.whisper and not tj.exists():
        clave, formatos, tipo = elegir_pista(info)
        f3 = next((f for f in (formatos or []) if f.get("ext") == "json3"), None)
        if f3:
            print(f"• Bajando subtítulos {tipo} de YouTube ({clave}) — sin descargar el video…")
            with ydl() as y:
                data = json.loads(y.urlopen(f3["url"]).read().decode("utf-8"))
            ws = palabras_json3(data)
            dur = float(info.get("duration") or (ws[-1]["fin"] if ws else 0))
            if a.sin_chequeo:
                cal, det = 1.0, "chequeo salteado"
            else:
                print("• Chequeando que los subtítulos se entiendan (2 muestras contra Whisper, ~1 min)…")
                cal, det = calidad_subtitulos(meta["url"], ws, dur, clave.split("-")[0], ffmpeg, a.modelo)
            meta["calidad_subtitulos"] = {"puntaje": round(cal, 2), "detalle": det}
            print(f"  {det}")
            if cal < UMBRAL_SUBS:
                print(f"  ✗ No son confiables (umbral {UMBRAL_SUBS:.0%}): transcribo con Whisper.")
                ws = []
            if len(ws) > 50:
                tr = {"idioma": clave.split("-")[0], "duracion": float(info.get("duration") or ws[-1]["fin"]),
                      "origen": f"subtítulos {tipo} de YouTube", "segmentos": segmentar(ws)}
                tj.write_text(json.dumps(tr, ensure_ascii=False, indent=1), encoding="utf-8")
                meta["modo"] = "subtitulos"
            elif cal >= UMBRAL_SUBS:
                print("  (los subtítulos vienen vacíos; paso a Whisper)")
        else:
            print("• Este video no tiene subtítulos en YouTube; paso a Whisper (más lento).")

    # --- modo completo: video + Whisper (fallback) ---
    if not tj.exists():
        video = next(iter(sorted(orig.glob("video.m*"))), None) or next(iter(sorted(orig.glob("audio.*"))), None)
        if video is None:
            if es_url:
                # sólo el audio (~10× más liviano); los clips después bajan sólo sus tramos de video
                print("• Descargando sólo el audio con yt-dlp para transcribir…")
                with ydl(format="ba[ext=m4a]/ba", outtmpl=str(orig / "audio.%(ext)s"),
                         ffmpeg_location=str(Path(ffmpeg).parent), quiet=False, noprogress=True) as y:
                    y.download([a.origen])
            else:
                dst = orig / f"video{Path(meta['archivo']).suffix.lower()}"
                print(f"• Copio el video local a {dst}")
                shutil.copy2(meta["archivo"], dst)
            video = next(iter(sorted(orig.glob("video.m*"))), None) or next(iter(sorted(orig.glob("audio.*"))))
        if video.name.startswith("video"):
            meta["video"] = video.name
        else:
            meta["audio"] = video.name
        from transcribir import transcribir
        print(f"• Transcribiendo el video entero con faster-whisper ({a.modelo}): ≈ 0,6× la duración…")
        tr = transcribir(str(video), a.modelo, a.idioma, ffmpeg=ffmpeg)
        tr["origen"] = f"faster-whisper {a.modelo}"
        tj.write_text(json.dumps(tr, ensure_ascii=False, indent=1), encoding="utf-8")
        meta["modo"] = "whisper"
    mj.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")

    tr = json.loads(tj.read_text(encoding="utf-8"))
    lineas = [f"# {meta.get('titulo')} — {fuente}",
              f"# idioma: {tr['idioma']} · duración: {mmss(tr['duracion'])} · texto: {tr.get('origen', '')}",
              "# formato: [inicio – fin] (segundos para plan.json) texto", ""]
    for s in tr["segmentos"]:
        lineas.append(f"[{mmss(s['ini'])} – {mmss(s['fin'])}] ({s['ini']:.1f}–{s['fin']:.1f}) {s['texto']}")
    (orig / "transcripcion.txt").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"\n✓ Listo para elegir momentos.\n  Carpeta: {carpeta}\n  Transcripción: {orig / 'transcripcion.txt'}"
          f" ({len(tr['segmentos'])} bloques, {tr.get('origen', '')})")
    print(f"CARPETA={carpeta}")


# ---------------- cortar ----------------

class Fuente:
    """De dónde se saca cada tramo: el .mp4 local o, si no hay, directo de YouTube (sólo ese tramo)."""

    def __init__(self, ffmpeg, orig, meta):
        self.ffmpeg = ffmpeg
        local = orig / meta["video"] if meta.get("video") else None
        if not (local and local.exists()) and meta.get("archivo") and Path(meta["archivo"]).exists():
            local = Path(meta["archivo"])  # .mp4 local original (la copia ya se borró)
        self.local = local if local and local.exists() else None
        self.entradas = None
        if self.local is None:
            if not meta.get("url"):
                die("No hay video local ni link para bajar los tramos.")
            self.entradas = entradas_remotas(meta["url"])

    def _inputs(self, ini, solo_audio=False):
        if self.local:
            return ["-ss", f"{ini:.3f}", "-i", str(self.local)], "0:v:0", "0:a:0"
        args, mv, ma = [], None, None
        ents = [e for e in self.entradas if not (solo_audio and e["tipo"] == "v" and len(self.entradas) > 1)]
        for i, e in enumerate(ents):
            args += ["-ss", f"{ini:.3f}"] + (["-headers", e["hdr"]] if e["hdr"] else []) + ["-i", e["url"]]
            if e["tipo"] == "v" and mv is None:
                mv = f"{i}:v:0"
            if ma is None and (e["tipo"] == "a" or len(ents) == 1):
                ma = f"{i}:a:0"
        return args, mv, ma

    def audio(self, ini, fin, wav):
        args, _, ma = self._inputs(ini, solo_audio=True)
        subprocess.run([self.ffmpeg, "-v", "error", "-y", *args, "-t", f"{fin - ini:.3f}", "-map", ma,
                        "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", wav], check=True)

    def clip(self, ini, fin, out):
        args, mv, ma = self._inputs(ini)
        subprocess.run([self.ffmpeg, "-v", "error", "-y", *args, "-t", f"{fin - ini:.3f}", "-map", mv, "-map", ma,
                        # crudo en calidad casi sin pérdida (H.264 para que se vea en cualquier Mac)
                        "-vf", "format=yuv420p", "-c:v", "libx264", "-preset", "slow", "-crf", "14",
                        "-profile:v", "high", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                        "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", str(out)], check=True)


def hacer_vista(ffmpeg, src, dst, escala):
    """Copia liviana (≈2-5 MB) para ver el video dentro de la Biblioteca viva."""
    subprocess.run([ffmpeg, "-v", "error", "-y", "-i", str(src), "-vf", escala, "-c:v", "libx264", "-preset", "veryfast",
                    "-crf", "28", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(dst)],
                   check=True)


def ajustar_a_palabras(ws, ini, fin):
    """Empieza justo antes de la primera palabra y termina un poco después de la última."""
    dentro = [w for w in ws if w["fin"] > ini + 0.05 and w["ini"] < fin - 0.05]
    if not dentro:
        return ini, fin, []
    a = max(0.0, dentro[0]["ini"] - 0.12)
    b = dentro[-1]["fin"] + 0.35
    idx = ws.index(dentro[-1])
    if idx + 1 < len(ws) and ws[idx + 1]["ini"] < b:
        b = max(dentro[-1]["fin"] + 0.05, ws[idx + 1]["ini"] - 0.02)
    return round(a, 2), round(b, 2), dentro


def cortar(a):
    ffmpeg = buscar_ffmpeg()
    carpeta = Path(a.carpeta).expanduser().resolve()
    orig = carpeta / "_original"
    meta = json.loads((orig / "meta.json").read_text(encoding="utf-8"))
    tr = json.loads((orig / "transcripcion.json").read_text(encoding="utf-8"))
    plan = json.loads(Path(a.plan).read_text(encoding="utf-8"))
    clips = plan["clips"] if isinstance(plan, dict) else plan

    for i, c in enumerate(clips, 1):  # validar contra los departamentos y áreas de P18
        for k in ("ini", "fin", "titulo", "departamento", "area", "tema", "porque"):
            if k not in c:
                die(f"Clip {i}: falta '{k}' en el plan.")
        if c["departamento"] not in AREAS:
            die(f"Clip {i}: departamento '{c['departamento']}' no existe. Opciones: {', '.join(AREAS)}")
        if c["area"] not in AREAS[c["departamento"]]:
            die(f"Clip {i}: área '{c['area']}' no es de {c['departamento']}. Opciones: {', '.join(AREAS[c['departamento']])}")

    fuente = Fuente(ffmpeg, orig, meta)
    print("• Video: " + ("archivo local" if fuente.local else "bajando sólo los tramos elegidos de YouTube"))
    from transcribir import transcribir
    resumen = []
    for i, c in enumerate(clips, 1):
        t0 = max(0.0, float(c["ini"]) - MARGEN)
        t1 = float(c["fin"]) + MARGEN
        with tempfile.TemporaryDirectory() as tmp:  # Whisper sólo sobre este tramo (≈1 min, no 2 h)
            wav = os.path.join(tmp, "tramo.wav")
            fuente.audio(t0, t1, wav)
            trc = transcribir(wav, a.modelo, tr.get("idioma"), ffmpeg=ffmpeg, log=False)
        ws = [{"ini": round(w["ini"] + t0, 2), "fin": round(w["fin"] + t0, 2), "p": w["p"]}
              for s in trc["segmentos"] for w in s["palabras"]]
        ini, fin, dentro = ajustar_a_palabras(ws, float(c["ini"]), float(c["fin"]))
        dur = fin - ini
        aviso = "" if 30 <= dur <= 60.5 else f"  ⚠ dura {dur:.1f}s (buscado: 30–60s)"
        slug = limpio(c.get("slug") or c["tema"], 40)
        num = int(c.get("n", i))  # "n" en el plan permite rehacer un clip puntual con su número
        nombre = f"{num:02d} - {slug}"
        out = carpeta / f"{nombre}.mp4"
        n = 2
        while out.exists() or (carpeta / f"{nombre}.txt").exists():  # no pisar
            nombre = f"{num:02d} - {slug} ({n})"
            out = carpeta / f"{nombre}.mp4"
            n += 1
        fuente.clip(ini, fin, out)
        vistas = orig / "vistas"
        vistas.mkdir(exist_ok=True)
        hacer_vista(ffmpeg, out, vistas / f"{nombre}.mp4", "scale=-2:360")

        texto = " ".join(w["p"] for w in dentro)
        fuente_txt = meta.get("fuente", "")
        if meta.get("titulo"):
            fuente_txt += f" — \"{meta['titulo']}\""
        if meta.get("url"):
            sep = "&" if "?" in meta["url"] else "?"
            fuente_txt += f"\n                  {meta['url']}{sep}t={int(ini)}s"
        titulo_txt = c["titulo"].replace("*", "").upper()
        txt = f"""CLIP {num:02d} — {titulo_txt}

Inicio:     {mmss(ini)}  ({ini:.2f} s)
Fin:        {mmss(fin)}  ({fin:.2f} s)
Duración:   {dur:.1f} s{aviso}
Corte:      ajustado a las palabras con Whisper; reencodeado una vez en alta calidad (CRF 16)

Título sugerido:  {titulo_txt}   (en el reel, en lima: {', '.join(re.findall(r"\*(.+?)\*", c['titulo'])) or '—'})
Departamento:     {c['departamento']}
Área:             {c['area']}
Tema:             {c['tema']}
Fuente:           {fuente_txt}

Por qué lo elegí:
{c['porque']}
"""
        if c.get("gancho"):
            txt += f"\nGancho (primeros 3 s): {c['gancho']}\n"
        if c.get("notas"):
            txt += f"\nNotas para la revisión: {c['notas']}\n"
        txt += f"""
Transcripción del clip:
{texto}

Para pasarlo al formato P18 (una vez aprobado):
p18 "{out}" "{c.get('titulo_p18', c['titulo'])}" --fuente "{meta.get('fuente', '')}"{' --salud-mental' if c['area'] == 'Salud mental' else ''}
"""
        (carpeta / f"{nombre}.txt").write_text(txt, encoding="utf-8")
        resumen.append((nombre, ini, fin, dur, c))
        print(f"• {nombre}.mp4  [{mmss(ini)}–{mmss(fin)}] {dur:.1f}s  {c['departamento']} › {c['area']}{aviso}")

    idx = [f"# Clips crudos — {meta.get('fuente')}", "", f"Original: {meta.get('titulo', '')} {meta.get('url', '')}", "",
           "Marcá [x] aprobado o escribí DESCARTADO. Nada se publica sin aprobación humana.", ""]
    for nombre, ini, fin, dur, c in resumen:
        idx.append(f"- [ ] **{nombre}** · {mmss(ini)}–{mmss(fin)} ({dur:.0f}s) · {c['departamento']} › {c['area']}"
                   f"\n      {c['titulo'].replace('*', '').upper()}")
    # borrar el video/audio completo: ya no hace falta (los clips están cortados)
    if not a.conservar:
        borrados = []
        for k in ("video", "audio"):
            f = orig / meta[k] if meta.get(k) else None
            if f and f.exists():  # siempre es una descarga o una copia nuestra
                tam = f.stat().st_size / 1e6
                f.unlink()
                borrados.append(f"{f.name} ({tam:.0f} MB)")
                meta.pop(k)
        if borrados:
            meta["original_borrado"] = f"{datetime.date.today().isoformat()}: {', '.join(borrados)}"
            (orig / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"• Borré el original completo para liberar espacio: {', '.join(borrados)}")

    lista = carpeta / "LISTA PARA APROBAR.md"
    if lista.exists():
        lista = carpeta / f"LISTA PARA APROBAR {datetime.datetime.now():%H%M}.md"
    lista.write_text("\n".join(idx) + "\n", encoding="utf-8")
    print(f"\n✓ {len(resumen)} clips en {carpeta}\n  Lista: {lista}")


def analizar(a):
    """Skill 0: todo lo necesario para decidir si un video sirve para P18, rápido y sin descargar el video.
    Imprime JSON: datos del video, descripción, capítulos y muestras del texto repartidas por todo el video."""
    ffmpeg = buscar_ffmpeg()
    with ydl() as y:
        i = y.extract_info(a.url, download=False)
    dur = float(i.get("duration") or 0)
    out = {"url": i.get("webpage_url") or a.url, "titulo": i.get("title"), "canal": i.get("channel") or i.get("uploader"),
           "duracion_min": round(dur / 60, 1), "publicado": i.get("upload_date"), "idioma": i.get("language"),
           "vistas": i.get("view_count"), "descripcion": (i.get("description") or "")[:1500],
           "capitulos": [f"{mmss(c.get('start_time', 0))} {c.get('title', '')}" for c in (i.get("chapters") or [])][:40],
           "tags": (i.get("tags") or [])[:20], "muestras": [], "texto_de": None}
    clave, formatos, tipo = elegir_pista(i)
    f3 = next((f for f in (formatos or []) if f.get("ext") == "json3"), None)
    ws = []
    if f3:
        with ydl() as y:
            ws = palabras_json3(json.loads(y.urlopen(f3["url"]).read().decode("utf-8")))
    n = max(4, min(10, int(dur // 600) + 4))  # 4 a 10 muestras según la duración
    if len(ws) > 50:
        out["texto_de"] = f"subtítulos {tipo} de YouTube ({clave})"
        out["idioma"] = out["idioma"] or clave.split("-")[0]
        for k in range(n):
            t0 = dur * (k + 0.5) / n - 40
            frag = [w["p"] for w in ws if t0 <= w["ini"] <= t0 + 80]
            if frag:
                out["muestras"].append({"min": mmss(max(0, t0)), "texto": " ".join(frag)})
    else:  # sin subtítulos: Whisper sobre 3 muestras cortas (≈1-2 min)
        from transcribir import transcribir
        aud = [e for e in entradas_remotas(out["url"], "ba[ext=m4a]/ba/b") if e["tipo"] == "a"]
        out["texto_de"] = "Whisper (3 muestras de 45 s; el video no tiene subtítulos)"
        for frac in (0.2, 0.5, 0.8):
            t0 = max(0.0, dur * frac)
            with tempfile.TemporaryDirectory() as tmp:
                wav = os.path.join(tmp, "m.wav")
                subprocess.run([ffmpeg, "-v", "error", "-y", "-ss", f"{t0:.1f}"] + (["-headers", aud[0]["hdr"]] if aud and aud[0]["hdr"] else [])
                               + ["-i", aud[0]["url"] if aud else out["url"], "-t", "45", "-ac", "1", "-ar", "16000", wav], check=True)
                # idioma que informa YouTube (es-US → es): en muestras cortas Whisper a veces lo confunde
                tr = transcribir(wav, a.modelo, (i.get("language") or "").split("-")[0] or None, ffmpeg=ffmpeg, log=False)
            out["idioma"] = out["idioma"] or tr["idioma"]
            out["muestras"].append({"min": mmss(t0), "texto": " ".join(sg["texto"] for sg in tr["segmentos"])})
    print(json.dumps(out, ensure_ascii=False, indent=1))


def info(a):
    """Duración y subtítulos de un link, sin descargar nada (para repartir el cupo por corrida)."""
    with ydl() as y:
        i = y.extract_info(a.url, download=False)
    clave, _, tipo = elegir_pista(i)
    print(json.dumps({"titulo": i.get("title"), "canal": i.get("channel"), "duracion_min": round((i.get("duration") or 0) / 60, 1),
                      "subtitulos": tipo or "no tiene", "pista": clave}, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("preparar")
    p.add_argument("origen"); p.add_argument("--fuente"); p.add_argument("--modelo", default="medium")
    p.add_argument("--idioma"); p.add_argument("--raiz")
    p.add_argument("--whisper", action="store_true", help="Ignorar subtítulos de YouTube y transcribir todo (lento).")
    p.add_argument("--sin-chequeo", action="store_true", help="No comparar los subtítulos con Whisper.")
    c = sub.add_parser("cortar")
    c.add_argument("carpeta"); c.add_argument("plan"); c.add_argument("--modelo", default="medium")
    c.add_argument("--conservar", action="store_true",
                   help="No borrar el video/audio completo después de cortar (sólo se borra si vino de un link).")
    z = sub.add_parser("analizar", help="Skill 0: datos y muestras de texto de un link para decidir si sirve.")
    z.add_argument("url"); z.add_argument("--modelo", default="medium")
    n = sub.add_parser("info", help="Duración y subtítulos de un link, sin descargar.")
    n.add_argument("url")
    a = ap.parse_args()
    {"preparar": preparar, "cortar": cortar, "info": info, "analizar": analizar}[a.cmd](a)


if __name__ == "__main__":
    main()
