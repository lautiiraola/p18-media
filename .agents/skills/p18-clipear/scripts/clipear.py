#!/usr/bin/env python3
"""p18-clipear: de un link de YouTube (o un .mp4) a clips crudos para revisar.

  p18-clipear preparar URL|video.mp4 [--fuente "Nombre"] [--modelo medium]
      Descarga (yt-dlp), transcribe (faster-whisper, tiempos por palabra) y deja
      transcripcion.txt para que el agente elija los momentos. Imprime la carpeta.

  p18-clipear cortar CARPETA plan.json [--copiar]
      Corta cada momento del plan con ffmpeg, crudo, y deja un .txt al lado.

Carpeta: "06 Biblioteca/Clips crudos/<fecha> - <fuente>/", con el original en "_original/".
"""
import argparse, datetime, json, os, re, shutil, subprocess, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

AREAS = {
    "Crecimiento personal": ["Autoconocimiento", "Hábitos y constancia", "Mentalidad y adaptación", "Liderazgo"],
    "Finanzas y trabajo": ["Finanzas personales", "Trabajo y oportunidades", "Ideas, proyectos y ventas"],
    "Crear y comunicar": ["Arte y diseño", "Vínculos y comunicación", "Redes y contenido", "Inteligencia artificial"],
    "Salud": ["Salud mental", "Vínculos", "Salud física", "Alimentación", "Sueño", "Bienestar"],
    "Deporte y mentalidad": ["Disciplina y proceso", "Presión y dificultad", "Liderazgo y equipo", "Mentalidad aplicada"],
}


def die(msg, code=1):
    print(f"\n✗ {msg}", file=sys.stderr)
    sys.exit(code)


def buscar_ffmpeg():
    for c in [os.environ.get("P18_FFMPEG"), "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg",
              "/usr/local/opt/ffmpeg-full/bin/ffmpeg", shutil.which("ffmpeg")]:
        if c and Path(c).exists():
            return c
    die("No encontré ffmpeg. Corré scripts/setup.sh de p18-filtro.")


def ffprobe_de(ffmpeg):
    p = Path(ffmpeg).with_name("ffprobe")
    return str(p) if p.exists() else (shutil.which("ffprobe") or "ffprobe")


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


# ---------------- preparar ----------------

def preparar(a):
    raiz = buscar_raiz(a.raiz)
    ffmpeg = buscar_ffmpeg()
    hoy = datetime.date.today().isoformat()
    origen = a.origen
    es_url = re.match(r"https?://", origen) is not None
    meta = {}

    if es_url:
        import yt_dlp
        with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as y:
            info = y.extract_info(origen, download=False)
        meta = {"url": info.get("webpage_url") or origen, "titulo": info.get("title"), "canal": info.get("channel")
                or info.get("uploader"), "fecha_publicacion": info.get("upload_date"), "duracion": info.get("duration"),
                "id": info.get("id")}
        fuente = a.fuente or meta["canal"] or meta["titulo"]
    else:
        src = Path(origen).expanduser().resolve()
        if not src.exists():
            die(f"No existe: {src}")
        meta = {"archivo": str(src), "titulo": src.stem}
        fuente = a.fuente or src.stem

    # si este video ya se preparó, reusar la carpeta
    base = raiz / "06 Biblioteca" / "Clips crudos"
    carpeta = None
    if base.is_dir():
        for m in base.glob("*/_original/meta.json"):
            try:
                old = json.loads(m.read_text(encoding="utf-8"))
            except Exception:
                continue
            if (meta.get("id") and old.get("id") == meta.get("id")) or \
               (meta.get("archivo") and old.get("archivo") == meta.get("archivo")):
                carpeta = m.parent.parent
                print(f"• Ya existe una carpeta para este video: {carpeta}")
                break
    if carpeta is None:
        carpeta = base / f"{hoy} - {limpio(fuente)}"
        n = 2
        while carpeta.exists():
            carpeta = base / f"{hoy} - {limpio(fuente)} ({n})"
            n += 1
    orig = carpeta / "_original"
    orig.mkdir(parents=True, exist_ok=True)
    meta["fuente"] = fuente

    video = next(iter(sorted(orig.glob("video.*"))), None)
    if video is None:
        if es_url:
            import yt_dlp
            print("• Descargando con yt-dlp (mejor calidad H.264 hasta 1080p, sin subtítulos incrustados)…")
            opts = {
                # H.264 + AAC: se corta sin reencodear y se ve en cualquier Mac. 1080p alcanza para el recuadro de 1000 px.
                "format": "bv*[vcodec^=avc1][height<=1080]+ba[ext=m4a]/bv*[height<=1080]+ba/b",
                "merge_output_format": "mp4",
                "outtmpl": str(orig / "video.%(ext)s"),
                "writesubtitles": False, "embedsubtitles": False,
                "ffmpeg_location": str(Path(ffmpeg).parent),
                "quiet": False, "no_warnings": True, "noprogress": True,
            }
            with yt_dlp.YoutubeDL(opts) as y:
                y.download([origen])
        else:
            src = Path(meta["archivo"])
            dst = orig / f"video{src.suffix.lower()}"
            print(f"• Copio el video local a {dst}")
            shutil.copy2(src, dst)
        video = next(iter(sorted(orig.glob("video.*"))))
    meta["video"] = video.name
    (orig / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")

    tj = orig / "transcripcion.json"
    if not tj.exists():
        from transcribir import transcribir
        print(f"• Transcribiendo con faster-whisper ({a.modelo}). En videos largos tarda (≈ 0,3–0,5× la duración)…")
        tr = transcribir(str(video), a.modelo, a.idioma, ffmpeg=ffmpeg)
        tj.write_text(json.dumps(tr, ensure_ascii=False, indent=1), encoding="utf-8")
    tr = json.loads(tj.read_text(encoding="utf-8"))

    # transcripción legible para que el agente elija momentos
    lineas = [f"# {meta.get('titulo')} — {fuente}", f"# idioma: {tr['idioma']} · duración: {mmss(tr['duracion'])}",
              "# formato: [inicio – fin] texto   (segundos entre paréntesis para usar en plan.json)", ""]
    for s in tr["segmentos"]:
        lineas.append(f"[{mmss(s['ini'])} – {mmss(s['fin'])}] ({s['ini']:.1f}–{s['fin']:.1f}) {s['texto']}")
    (orig / "transcripcion.txt").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"\n✓ Listo para elegir momentos.\n  Carpeta: {carpeta}\n  Transcripción: {orig / 'transcripcion.txt'}"
          f" ({len(tr['segmentos'])} segmentos, idioma {tr['idioma']})")
    print(f"CARPETA={carpeta}")


# ---------------- cortar ----------------

def keyframes(ffmpeg, video):
    r = subprocess.run([ffprobe_de(ffmpeg), "-v", "error", "-select_streams", "v:0", "-skip_frame", "nokey",
                        "-show_entries", "frame=pts_time", "-of", "csv=p=0", str(video)],
                       capture_output=True, text=True)
    return sorted(float(x) for x in r.stdout.split() if x.strip() and x.strip() != "N/A")


def palabras_en(tr, ini, fin):
    return [w for s in tr["segmentos"] for w in s["palabras"] if w["ini"] >= ini - 0.05 and w["fin"] <= fin + 0.05]


def ajustar_a_palabras(tr, ini, fin):
    """Empieza justo antes de la primera palabra y termina un poco después de la última."""
    ws = [w for s in tr["segmentos"] for w in s["palabras"]]
    dentro = [w for w in ws if w["fin"] > ini and w["ini"] < fin]
    if not dentro:
        return ini, fin
    a = max(0.0, dentro[0]["ini"] - 0.12)
    b = dentro[-1]["fin"] + 0.35
    sig = next((w for w in ws if w["ini"] >= dentro[-1]["fin"] and w is not dentro[-1]), None)
    if sig and sig["ini"] < b:
        b = max(dentro[-1]["fin"] + 0.05, sig["ini"] - 0.02)
    return round(a, 2), round(b, 2)


def cortar(a):
    ffmpeg = buscar_ffmpeg()
    carpeta = Path(a.carpeta).expanduser().resolve()
    orig = carpeta / "_original"
    meta = json.loads((orig / "meta.json").read_text(encoding="utf-8"))
    tr = json.loads((orig / "transcripcion.json").read_text(encoding="utf-8"))
    video = orig / meta["video"]
    plan = json.loads(Path(a.plan).read_text(encoding="utf-8"))
    clips = plan["clips"] if isinstance(plan, dict) else plan

    # validar contra los departamentos y áreas de P18
    for i, c in enumerate(clips, 1):
        for k in ("ini", "fin", "titulo", "departamento", "area", "tema", "porque"):
            if k not in c:
                die(f"Clip {i}: falta '{k}' en el plan.")
        if c["departamento"] not in AREAS:
            die(f"Clip {i}: departamento '{c['departamento']}' no existe. Opciones: {', '.join(AREAS)}")
        if c["area"] not in AREAS[c["departamento"]]:
            die(f"Clip {i}: área '{c['area']}' no es de {c['departamento']}. Opciones: {', '.join(AREAS[c['departamento']])}")

    kfs = keyframes(ffmpeg, video)
    resumen = []
    for i, c in enumerate(clips, 1):
        ini, fin = ajustar_a_palabras(tr, float(c["ini"]), float(c["fin"]))
        dur = fin - ini
        aviso = "" if 30 <= dur <= 60.5 else f"  ⚠ dura {dur:.1f}s (buscado: 30–60s)"
        slug = limpio(c.get("slug") or c["tema"], 40)
        nombre = f"{i:02d} - {slug}"
        out = carpeta / f"{nombre}.mp4"
        n = 2
        while out.exists() or (carpeta / f"{nombre}.txt").exists():  # no pisar
            nombre = f"{i:02d} - {slug} ({n})"
            out = carpeta / f"{nombre}.mp4"
            n += 1

        # ¿se puede cortar sin reencodear? sólo si hay un keyframe pegado al inicio
        kf = max((k for k in kfs if k <= ini + 0.02), default=None)
        copiar = a.copiar or (kf is not None and ini - kf <= 0.12)
        if copiar:
            st = kf if kf is not None else ini
            cmd = [ffmpeg, "-v", "error", "-y", "-ss", f"{st:.3f}", "-i", str(video), "-t", f"{fin - st:.3f}",
                   "-map", "0:v:0", "-map", "0:a:0?", "-c", "copy", "-avoid_negative_ts", "make_zero",
                   "-movflags", "+faststart", str(out)]
            modo = f"sin reencodear (desde keyframe {st:.2f}s)"
        else:
            cmd = [ffmpeg, "-v", "error", "-y", "-ss", f"{ini:.3f}", "-i", str(video), "-t", f"{dur:.3f}",
                   "-map", "0:v:0", "-map", "0:a:0?", "-c:v", "libx264", "-preset", "medium", "-crf", "16",
                   "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)]
            modo = "reencodeado en alta calidad (CRF 16) para que arranque justo en la primera palabra"
        subprocess.run(cmd, check=True)

        texto = " ".join(w["p"] for w in palabras_en(tr, ini, fin))
        fuente_txt = meta.get("fuente", "")
        if meta.get("titulo"):
            fuente_txt += f" — \"{meta['titulo']}\""
        if meta.get("url"):
            fuente_txt += f"\n            {meta['url']}&t={int(ini)}s" if "?" in meta["url"] else f"\n            {meta['url']}?t={int(ini)}s"
        txt = f"""CLIP {i:02d} — {c['titulo'].upper()}

Inicio:     {mmss(ini)}  ({ini:.2f} s)
Fin:        {mmss(fin)}  ({fin:.2f} s)
Duración:   {dur:.1f} s{aviso}
Corte:      {modo}

Título sugerido:  {c['titulo'].upper()}
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
        resumen.append((nombre, ini, fin, dur, c, aviso))
        print(f"• {nombre}.mp4  [{mmss(ini)}–{mmss(fin)}] {dur:.1f}s  {c['departamento']} › {c['area']}{aviso}")

    # índice para aprobar / descartar
    idx = [f"# Clips crudos — {meta.get('fuente')}", "", f"Original: {meta.get('titulo', '')} {meta.get('url', '')}", "",
           "Marcá [x] aprobado o escribí DESCARTADO. Nada se publica sin aprobación humana.", ""]
    for nombre, ini, fin, dur, c, aviso in resumen:
        idx.append(f"- [ ] **{nombre}** · {mmss(ini)}–{mmss(fin)} ({dur:.0f}s) · {c['departamento']} › {c['area']}"
                   f"\n      {c['titulo'].upper()}")
    lista = carpeta / "LISTA PARA APROBAR.md"
    if lista.exists():
        lista = carpeta / f"LISTA PARA APROBAR {datetime.datetime.now():%H%M}.md"
    lista.write_text("\n".join(idx) + "\n", encoding="utf-8")
    print(f"\n✓ {len(resumen)} clips en {carpeta}\n  Lista: {lista}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("preparar")
    p.add_argument("origen"); p.add_argument("--fuente"); p.add_argument("--modelo", default="medium")
    p.add_argument("--idioma"); p.add_argument("--raiz")
    c = sub.add_parser("cortar")
    c.add_argument("carpeta"); c.add_argument("plan")
    c.add_argument("--copiar", action="store_true", help="Forzar corte sin reencodear (puede arrancar unos segundos antes).")
    a = ap.parse_args()
    preparar(a) if a.cmd == "preparar" else cortar(a)


if __name__ == "__main__":
    main()
