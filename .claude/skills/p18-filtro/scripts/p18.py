#!/usr/bin/env python3
"""p18: pasa un clip crudo al formato de reel P18 (1080x1920).

Uso:  p18 clip.mp4 "TÍTULO CON *PALABRAS CLAVE*" [opciones]

Las palabras entre *asteriscos* (o <b>…</b>) van en lima.
Pasos: transcribe (o reutiliza subs.json) → arma la capa con la plantilla →
compone con ffmpeg + subtítulos .ass → guarda en "04 Instagram/Reels listos para subir/"
→ hace capturas para revisar.

Si el audio NO está en castellano, frena después de transcribir y deja subs.json
con un campo "es" vacío por frase: hay que completarlo (traducción frase por frase,
mismos tiempos) y volver a correr el mismo comando.
"""
import argparse, datetime, json, os, re, shutil, subprocess, sys, urllib.parse
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ASSETS = AQUI.parent / "assets"
sys.path.insert(0, str(AQUI))

W, H = 1080, 1920
BOX_X, BOX_W, BOX_MAX_H, BOX_MIN_H, BOX_TOP = 40, 1000, 960, 520, 250
BOX_MIN_W, PIE_LIMITE = 760, 1700  # forma "auto": ancho mínimo del recuadro y hasta dónde puede bajar el pie
LIMA_ASS, TINTA_ASS, PAPEL_ASS = "&H0042F5C2", "&H10192017", "&H00EBF5F5"
CIERRE_SALUD = "Si te pasa algo parecido, hablalo con alguien de confianza o con un profesional."


def die(msg, code=1):
    print(f"\n✗ {msg}", file=sys.stderr)
    sys.exit(code)


def buscar_ffmpeg():
    cands = [os.environ.get("P18_FFMPEG"), "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg",
             "/usr/local/opt/ffmpeg-full/bin/ffmpeg", shutil.which("ffmpeg")]
    for c in cands:
        if c and Path(c).exists():
            r = subprocess.run([c, "-hide_banner", "-filters"], capture_output=True, text=True)
            if re.search(r"\s(subtitles|ass)\s+V->V", r.stdout):
                return c
    die("No encontré un ffmpeg con libass (filtro 'subtitles'). En Mac: brew install ffmpeg-full")


def buscar_raiz(arg):
    if arg:
        return Path(arg).expanduser().resolve()
    if os.environ.get("P18_RAIZ"):
        return Path(os.environ["P18_RAIZ"]).expanduser().resolve()
    for base in [Path.cwd(), *Path.cwd().parents, AQUI, *AQUI.parents]:
        if (base / "04 Instagram").is_dir() and (base / "05 Filtro de reels").is_dir():
            return base
    die("No encontré la carpeta de Proyecto 18. Pasá --raiz o definí P18_RAIZ.")


def probe(ffmpeg, video):
    ffprobe = str(Path(ffmpeg).with_name("ffprobe"))
    if not Path(ffprobe).exists():
        ffprobe = shutil.which("ffprobe") or "ffprobe"
    r = subprocess.run([ffprobe, "-v", "error", "-show_entries",
                        "stream=codec_type,width,height,r_frame_rate:stream_side_data=rotation:format=duration",
                        "-of", "json", video], capture_output=True, text=True, check=True)
    d = json.loads(r.stdout)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    w, h = v["width"], v["height"]
    rot = 0
    for sd in v.get("side_data_list", []) or []:
        rot = int(sd.get("rotation", 0) or 0)
    if abs(rot) in (90, 270):
        w, h = h, w
    num, den = (v.get("r_frame_rate") or "30/1").split("/")
    fps = float(num) / float(den or 1)
    if not 10 <= fps <= 61:
        fps = 30.0
    tiene_audio = any(s["codec_type"] == "audio" for s in d["streams"])
    return w, h, fps, float(d["format"]["duration"]), tiene_audio


def titulo_html(t):
    t = re.sub(r"\*(.+?)\*", r"<b>\1</b>", t.strip())
    return t.upper().replace("<B>", "<b>").replace("</B>", "</b>")


# ---------- subtítulos ----------

def armar_frases(trans, max_chars=34, max_dur=3.4, pausa=0.55):
    palabras = [w for s in trans["segmentos"] for w in s["palabras"]]
    frases, cur = [], []

    def cerrar():
        if cur:
            frases.append({"ini": cur[0]["ini"], "fin": cur[-1]["fin"], "texto": " ".join(w["p"] for w in cur)})
            cur.clear()

    for w in palabras:
        if cur:
            largo = len(" ".join(x["p"] for x in cur))
            prev = cur[-1]["p"]
            if (largo + 1 + len(w["p"]) > max_chars
                    or w["ini"] - cur[-1]["fin"] > pausa
                    or w["fin"] - cur[0]["ini"] > max_dur
                    or prev[-1:] in ".?!"
                    or (prev[-1:] in ",;:" and largo >= 22)):
                cerrar()
        cur.append(w)
    cerrar()
    # tiempos: estirar hasta la siguiente frase si el hueco es chico; duración mínima
    for i, f in enumerate(frases):
        sig = frases[i + 1]["ini"] if i + 1 < len(frases) else None
        if sig is not None and sig - f["fin"] < 0.35:
            f["fin"] = sig
        if f["fin"] - f["ini"] < 0.7:
            f["fin"] = min(f["ini"] + 0.7, sig if sig is not None else f["ini"] + 0.7)
        f["ini"], f["fin"] = round(f["ini"], 2), round(f["fin"], 2)
    return frases


def ts(t):
    t = max(0.0, t)
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def ass_txt(s):
    return s.replace("\\", "").replace("{", "(").replace("}", ")").replace("\n", "\\N").strip()


def escribir_ass(path, frases, idioma, box_bottom, foot_bottom, dur, salud_mental, box_x=BOX_X):
    margin_v = H - box_bottom + 34
    m_lr = box_x + 60  # subtítulos dentro del recuadro, sea del ancho que sea
    lineas = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0",
        "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
        "MarginR, MarginV, Encoding",
        f"Style: P18,Manrope ExtraBold,46,{LIMA_ASS},{LIMA_ASS},{TINTA_ASS},{TINTA_ASS},0,0,0,0,100,100,0,0,3,14,0,2,{m_lr},{m_lr},{margin_v},1",
        f"Style: Cierre,Manrope ExtraBold,34,{PAPEL_ASS},{PAPEL_ASS},{TINTA_ASS},{TINTA_ASS},0,0,0,0,100,100,0,0,3,16,0,2,110,110,{max(60, H - foot_bottom - 110)},1",
        "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    for f in frases:
        txt = f.get("es") if idioma != "es" else f.get("texto")
        if txt and txt.strip():
            lineas.append(f"Dialogue: 0,{ts(f['ini'])},{ts(f['fin'])},P18,,0,0,0,,{ass_txt(txt)}")
    if salud_mental:
        lineas.append(f"Dialogue: 1,{ts(max(0, dur - 4.5))},{ts(dur)},Cierre,,0,0,0,,{ass_txt(CIERRE_SALUD)}")
    Path(path).write_text("\n".join(lineas) + "\n", encoding="utf-8")


# ---------- capa y máscara ----------

def geometria(vw, vh, forma, titulo_h, pie_h):
    """Recuadro (x, y, ancho, alto). Horizontal/cuadrado: 1000 de ancho, alto según el video (como Kavak).
    Vertical con forma "auto": el recuadro crece hacia abajo lo que deje el título y, si aun así no entra,
    se angosta (mín. 760) para mostrar el video entero en vez de recortarlo."""
    natural = BOX_W * vh / vw
    if forma == "clasica" or natural <= BOX_MAX_H:
        h = max(BOX_MIN_H, min(BOX_MAX_H, round(natural))) // 2 * 2
        return BOX_X, BOX_TOP + (BOX_MAX_H - h) // 4, BOX_W, h
    max_h = max(BOX_MAX_H, PIE_LIMITE - BOX_TOP - 50 - titulo_h - 42 - pie_h)
    if natural <= max_h:
        w, h = BOX_W, round(natural)
    else:
        h = max_h
        w = max(BOX_MIN_W, round(max_h * vw / vh))
    w, h = w // 2 * 2, h // 2 * 2
    return (W - w) // 2, BOX_TOP, w, h


def generar_capa(out_png, titulo, top, h, fuente, left=BOX_X, w=BOX_W):
    from playwright.sync_api import sync_playwright
    url = (ASSETS / "plantilla.html").as_uri() + "?" + urllib.parse.urlencode(
        {"t": titulo, "top": top, "h": h, "l": left, "w": w, "src": fuente or ""})
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.goto(url)
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(300)
        info = pg.evaluate("window.P18")
        if out_png:
            pg.screenshot(path=str(out_png))
        b.close()
    return info


def generar_outro(out_png, w, h, r=28):
    """Tarjeta del outro: el recuadro en verde profundo con el logo lima y proyecto18.com, chiquitos y centrados."""
    from PIL import Image, ImageDraw, ImageFont
    k = 2
    im = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, w * k - 1, h * k - 1], radius=r * k, fill=(20, 37, 29, 255))
    logo = Image.open(ASSETS / "logo-lima.png").convert("RGBA")
    lh = 70 * k
    logo = logo.resize((round(logo.width * lh / logo.height), lh), Image.LANCZOS)
    font = ImageFont.truetype(str(ASSETS / "Manrope-700.ttf"), 30 * k)
    txt = "proyecto18.com"
    tw = ImageDraw.Draw(im).textlength(txt, font=font)
    total = lh + 28 * k + 30 * k
    y0 = (h * k - total) // 2
    im.alpha_composite(logo, ((w * k - logo.width) // 2, y0))
    ImageDraw.Draw(im).text(((w * k - tw) / 2, y0 + lh + 28 * k), txt, font=font, fill=(245, 245, 235, 200))
    im.resize((w, h), Image.LANCZOS).save(out_png)


def generar_mascara(out_png, w, h, r=28):
    from PIL import Image, ImageDraw
    k = 4  # supersampling para bordes suaves
    im = Image.new("L", (w * k, h * k), 0)
    ImageDraw.Draw(im).rounded_rectangle([0, 0, w * k - 1, h * k - 1], radius=r * k, fill=255)
    im.resize((w, h), Image.LANCZOS).save(out_png)


# ---------- principal ----------

def main():
    ap = argparse.ArgumentParser(description="Formato P18 para un clip crudo.")
    ap.add_argument("video")
    ap.add_argument("titulo", help='Título. Palabras clave entre *asteriscos*.')
    ap.add_argument("--nombre", help="Nombre del archivo final (sin fecha). Por defecto, el del clip.")
    ap.add_argument("--fuente", help='Crédito que aparece abajo, p. ej. "Cracks Podcast".')
    ap.add_argument("--idioma", help="Forzar idioma del audio (es, en…). Por defecto lo detecta.")
    ap.add_argument("--modelo", default="medium", help="Modelo de faster-whisper (medium por defecto).")
    ap.add_argument("--sin-subs", action="store_true", help="No agregar subtítulos (si el video ya los trae).")
    ap.add_argument("--salud-mental", action="store_true",
                    help="Agrega al final la invitación a hablarlo con alguien de confianza o un profesional.")
    ap.add_argument("--final", default="corte", choices=["corte", "outro", "ninguno"],
                    help="corte: termina ~0,5 s después de la última palabra con el audio bajando (default). "
                         "outro: igual + 1,5 s con el recuadro fundiéndose al logo y proyecto18.com. ninguno: como viene.")
    ap.add_argument("--forma", default="auto", choices=["auto", "clasica"],
                    help="auto: en videos verticales el recuadro crece/se angosta para mostrar el video entero. "
                         "clasica: siempre 1000 de ancho y máx. 960 de alto (recorta los verticales).")
    ap.add_argument("--encuadre", default="centro", choices=["arriba", "centro", "abajo"],
                    help="Qué parte del video se conserva si hay que recortarlo para entrar en el recuadro.")
    ap.add_argument("--recorte", metavar="W:H:X:Y",
                    help="Recortar el video fuente antes de ponerlo en el recuadro (p. ej. para sacar subtítulos "
                         "o logos quemados). En píxeles del video original, como el crop de ffmpeg.")
    ap.add_argument("--retranscribir", action="store_true", help="Ignorar subs.json existente.")
    ap.add_argument("--solo-capa", action="store_true", help="Sólo generar capa y capturas de prueba (rápido).")
    ap.add_argument("--raiz", help="Carpeta de Proyecto 18.")
    a = ap.parse_args()

    video = Path(a.video).expanduser().resolve()
    if not video.exists():
        die(f"No existe el video: {video}")
    raiz = buscar_raiz(a.raiz)
    ffmpeg = buscar_ffmpeg()
    vw, vh, fps, dur, tiene_audio = probe(ffmpeg, str(video))

    hoy = datetime.date.today().isoformat()
    nombre = a.nombre or re.sub(r"^\d{4}-\d{2}-\d{2}\s*-?\s*", "", video.stem)
    base = f"{hoy} {nombre}"
    trabajo = raiz / "05 Filtro de reels" / "Trabajos" / base
    trabajo.mkdir(parents=True, exist_ok=True)
    if not a.solo_capa:  # para poder rehacer el reel igual (p18-corregir)
        (trabajo / "args.json").write_text(json.dumps({"video": str(video), **{k: v for k, v in vars(a).items() if k != "video"}},
                                                      ensure_ascii=False, indent=1), encoding="utf-8")
    destino_dir = raiz / "04 Instagram" / "Reels listos para subir"
    destino_dir.mkdir(parents=True, exist_ok=True)
    destino = destino_dir / f"{base}.mp4"
    n = 2
    while destino.exists():  # nunca pisar un reel existente
        destino = destino_dir / f"{base} v{n}.mp4"
        n += 1

    pre = ""
    if a.recorte:
        try:
            cw, ch, cx, cy = (int(x) for x in a.recorte.split(":"))
        except ValueError:
            die("--recorte tiene que ser W:H:X:Y, p. ej. 1080:700:0:140")
        if cx + cw > vw or cy + ch > vh:
            die(f"El recorte {a.recorte} se sale del video ({vw}x{vh}).")
        pre = f"crop={cw}:{ch}:{cx}:{cy},"
        vw, vh = cw, ch

    print(f"• Video {vw}x{vh} @ {fps:.2f} fps, {dur:.1f}s")

    # --- subtítulos ---
    subs_json = trabajo / "subs.json"
    frases, idioma = [], "es"
    if not a.sin_subs and tiene_audio and not a.solo_capa:
        if subs_json.exists() and not a.retranscribir:
            d = json.loads(subs_json.read_text(encoding="utf-8"))
            frases, idioma = d["frases"], d["idioma"]
            print(f"• Uso subtítulos existentes: {subs_json}")
        else:
            from transcribir import transcribir
            print(f"• Transcribiendo con faster-whisper ({a.modelo})…")
            tr = transcribir(str(video), a.modelo, a.idioma, ffmpeg=ffmpeg)
            (trabajo / "transcripcion.json").write_text(json.dumps(tr, ensure_ascii=False, indent=1), encoding="utf-8")
            idioma = tr["idioma"]
            frases = armar_frases(tr)
            if idioma != "es":
                for f in frases:
                    f["es"] = None  # null = falta traducir; "" = no mostrar esta frase
            subs_json.write_text(json.dumps({"idioma": idioma, "frases": frases}, ensure_ascii=False, indent=1),
                                 encoding="utf-8")
            print(f"• Subtítulos ({len(frases)} frases) en {subs_json} — se pueden corregir y volver a correr.")
        if idioma != "es" and any(f.get("es") is None for f in frases):
            print(f"\n⚠ El audio está en '{idioma}'. Falta traducir.\n"
                  f"  Completá el campo \"es\" (hoy null) de cada frase en:\n  {subs_json}\n"
                  f"  (castellano rioplatense simple, mismos tiempos) y volvé a correr el mismo comando.")
            sys.exit(3)

    # --- capa ---
    titulo = titulo_html(a.titulo)
    # recuadro: se adapta a la forma del video (opción A); en verticales puede crecer si queda mejor
    medida = generar_capa(None, titulo, BOX_TOP, BOX_MAX_H, a.fuente)
    box_x, box_top, box_w, box_h = geometria(vw, vh, a.forma, medida["titleH"], medida["footH"])
    print(f"• Recuadro {box_w}x{box_h} en x={box_x}, y={box_top} (forma {a.forma})")
    capa = trabajo / "capa.png"
    info = generar_capa(capa, titulo, box_top, box_h, a.fuente, box_x, box_w)
    mascara = trabajo / "mascara.png"
    generar_mascara(mascara, box_w, box_h)
    print(f"• Capa lista: {capa} (título {info['fontSize']}px)")

    ass = trabajo / "subs.ass"
    escribir_ass(ass, frases, idioma, box_top + box_h, info["footBottom"], dur, a.salud_mental, box_x)
    fonts = trabajo / "fuentes"
    fonts.mkdir(exist_ok=True)
    for ttf in ASSETS.glob("Manrope-*.ttf"):
        if not (fonts / ttf.name).exists():
            shutil.copy(ttf, fonts / ttf.name)

    # --- composición ---
    # Final: "corte" = termina ~0,5 s después de la última palabra con el audio bajando;
    # "outro" = igual, y después 1,5 s donde el recuadro se funde a verde con el logo y proyecto18.com;
    # "ninguno" = como viene el clip.
    fin_habla = dur
    tj = trabajo / "transcripcion.json"
    if tj.exists():
        ws = [w for sg in json.loads(tj.read_text(encoding="utf-8"))["segmentos"] for w in sg["palabras"]]
        if ws:
            fin_habla = min(dur, ws[-1]["fin"] + 0.5)
    elif frases:
        fin_habla = min(dur, max(f["fin"] for f in frases) + 0.3)
    base_dur = min(4.0, dur) if a.solo_capa else (fin_habla if a.final != "ninguno" else dur)
    extra = 1.5 if (a.final == "outro" and not a.solo_capa) else 0.0
    dur_total = base_dur + extra
    if extra:
        generar_outro(trabajo / "outro.png", box_w, box_h)

    y_frac = {"arriba": 0.0, "centro": 0.5, "abajo": 1.0}[a.encuadre]
    salida = trabajo / "render.mp4" if not a.solo_capa else trabajo / "prueba.mp4"
    congelar = f"tpad=stop_mode=clone:stop_duration={extra + 1:.2f}," if extra else ""
    filtros = (
        f"[1:v]{pre}{congelar}scale={box_w}:{box_h}:force_original_aspect_ratio=increase:flags=lanczos,"
        f"crop={box_w}:{box_h}:(iw-{box_w})/2:(ih-{box_h})*{y_frac},setsar=1,format=rgba[v];"
        f"[2:v]format=gray[m];[v][m]alphamerge[vm];"
        f"[0:v][vm]overlay={box_x}:{box_top}:shortest=1:format=auto,"
        f"subtitles=subs.ass:fontsdir=fuentes"
    )
    if extra:  # la tarjeta del outro aparece con un fundido suave sobre el recuadro
        filtros += (f"[pre];[3:v]format=rgba,fade=t=in:st={base_dur - 0.1:.2f}:d=0.6:alpha=1[o];"
                    f"[pre][o]overlay={box_x}:{box_top}:format=auto")
    # RGB → YUV con matriz BT.709 (la de Instagram/TikTok); el default de ffmpeg (BT.601) corre los colores
    filtros += ",scale=out_color_matrix=bt709:out_range=tv:flags=lanczos,format=yuv420p[out]"
    cmd = [ffmpeg, "-hide_banner", "-v", "error", "-stats", "-y",
           "-loop", "1", "-framerate", f"{fps:.5f}", "-i", "capa.png",
           "-i", str(video),
           "-loop", "1", "-framerate", f"{fps:.5f}", "-i", "mascara.png"]
    if extra:
        cmd += ["-loop", "1", "-framerate", f"{fps:.5f}", "-i", "outro.png"]
    # las imágenes van en loop: la duración la marca el video (más el outro, si hay)
    cmd += ["-t", f"{dur_total:.3f}"]
    cmd += ["-filter_complex", filtros + (";" + (
        f"[1:a:0]afade=t=out:st={max(0.0, base_dur - 0.45):.2f}:d=0.45,apad[a]" if a.final != "ninguno" and not a.solo_capa
        else "[1:a:0]anull[a]")) if tiene_audio else filtros, "-map", "[out]"]
    if tiene_audio:
        cmd += ["-map", "[a]", "-c:a", "aac", "-b:a", "320k", "-ar", "48000"]
    # Calidad máxima para subir a IG/TikTok: H.264 High 4.2, CRF 14 (casi sin pérdida), GOP de 1 s,
    # color BT.709 etiquetado. Las redes recomprimen igual: cuanto mejor el archivo, mejor lo que queda.
    calidad = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "23"] if a.solo_capa else \
        ["-c:v", "libx264", "-preset", "slow", "-crf", "14", "-tune", "film",
         "-profile:v", "high", "-level:v", "4.2", "-g", str(round(fps)), "-bf", "2"]
    cmd += ["-r", f"{fps:.5f}", *calidad, "-pix_fmt", "yuv420p",
            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
            "-bsf:v", "h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1:video_full_range_flag=0", "-movflags", "+faststart", str(salida)]  # bsf: escribe BT.709 en el video (si no, el iPhone lo ve lavado)
    print("• Componiendo el reel…")
    subprocess.run(cmd, check=True, cwd=trabajo)

    # --- capturas ---
    dur_out = dur_total
    capturas = trabajo / "capturas.jpg"
    tiempos = [dur_out * x for x in (0.08, 0.35, 0.65, 0.92)]
    ins = []
    for t in tiempos:
        ins += ["-ss", f"{t:.2f}", "-i", str(salida)]
    graf = "".join(f"[{i}:v]trim=end_frame=1,scale=432:768[c{i}];" for i in range(4))
    graf += "".join(f"[c{i}]" for i in range(4)) + "hstack=4[out]"
    subprocess.run([ffmpeg, "-v", "error", "-y", *ins, "-filter_complex", graf, "-map", "[out]",
                    "-frames:v", "1", "-q:v", "3", str(capturas)], check=True)

    if a.solo_capa:
        print(f"\n✓ Prueba lista (sin guardar en Reels listos). Capturas: {capturas}")
        return
    shutil.move(str(salida), destino)
    vista = trabajo / "vista.mp4"  # copia liviana para la Biblioteca viva
    subprocess.run([ffmpeg, "-v", "error", "-y", "-i", str(destino), "-vf", "scale=540:960", "-c:v", "libx264",
                    "-preset", "veryfast", "-crf", "28", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k",
                    "-movflags", "+faststart", str(vista)], check=True)
    print(f"\n✓ Reel listo: {destino}\n  Vista previa (para la Biblioteca viva): {vista}\n  Capturas para revisar: {capturas}\n  Archivos de trabajo: {trabajo}")
    print("  Antes de subir: revisar capturas y subtítulos. Una persona da el OK final.")


if __name__ == "__main__":
    main()
