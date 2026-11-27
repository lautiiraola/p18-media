#!/usr/bin/env python3
"""Filtro carrusel P18: pasa un clip al slide de video del carrusel (1080x1350, video en recuadro 1:1).

Uso:  carrusel.py clip.mp4 "TÍTULO CON *CLAVE*" --salida "<carpeta del carrusel>/NN - video.mp4"
          [--fondo oscuro|lima|papel] [--area "Hábitos y disciplina"] [--fuente "Manu Ginóbili"]
          [--subs "<Trabajos/.../subs.json del reel>"] [--encuadre izquierda|centro|derecha] [--recorte W:H:X:Y]
          [--sin-subs] [--salud-mental] [--solo-capa]

- El slide mide lo mismo que el resto del carrusel (4:5): Instagram recorta todos los elementos de un carrusel a la
  forma del primero, así que un video 1:1 suelto quedaría cortado. El video va 1:1 adentro, con el fondo del carrusel.
- Subtítulos: reutiliza el subs.json del reel (mismos tiempos y traducción). Si no hay, transcribe como p18.
- Máximo 59,5 s (límite de video de carrusel); termina ~0,5 s después de la última palabra con el audio bajando.
- Deja capturas en "05 Filtro de reels/Trabajos/<fecha> <nombre> (carrusel)/capturas.jpg".
"""
import argparse, datetime, json, re, shutil, subprocess, sys, urllib.parse
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import p18  # noqa: E402  (reutiliza probe, subtítulos, máscara, ffmpeg)

W, H = 1080, 1350
LADO, TOP = 880, 130
MAX_DUR = 59.5


def ass(path, frases, idioma, box_x, box_bottom, salud, dur):
    m_lr, mv = box_x + 46, H - box_bottom + 30
    l = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0",
         "ScaledBorderAndShadow: yes", "", "[V4+ Styles]",
         "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
         "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
         "MarginR, MarginV, Encoding",
         f"Style: P18,Manrope ExtraBold,42,{p18.LIMA_ASS},{p18.LIMA_ASS},{p18.TINTA_ASS},{p18.TINTA_ASS},0,0,0,0,100,100,0,0,3,13,0,2,{m_lr},{m_lr},{mv},1",
         f"Style: Cierre,Manrope ExtraBold,32,{p18.PAPEL_ASS},{p18.PAPEL_ASS},{p18.TINTA_ASS},{p18.TINTA_ASS},0,0,0,0,100,100,0,0,3,14,0,5,{m_lr},{m_lr},0,1",
         "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for f in frases:
        t = f.get("es") if idioma != "es" else f.get("texto")
        if t and t.strip() and f["ini"] < dur:
            l.append(f"Dialogue: 0,{p18.ts(f['ini'])},{p18.ts(min(f['fin'], dur))},P18,,0,0,0,,{p18.ass_txt(t)}")
    if salud:
        l.append(f"Dialogue: 1,{p18.ts(max(0, dur - 4.5))},{p18.ts(dur)},Cierre,,0,0,0,,{p18.ass_txt(p18.CIERRE_SALUD)}")
    Path(path).write_text("\n".join(l) + "\n", encoding="utf-8")


def capa(out, params):
    from playwright.sync_api import sync_playwright
    url = (p18.ASSETS / "carrusel.html").as_uri() + "?" + urllib.parse.urlencode(params)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.goto(url); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
        info = pg.evaluate("window.P18")
        pg.screenshot(path=str(out))
        b.close()
    return info


def main():
    ap = argparse.ArgumentParser(description="Filtro carrusel P18 (slide de video 1080x1350 con recuadro 1:1).")
    ap.add_argument("video"); ap.add_argument("titulo")
    ap.add_argument("--salida", help="Archivo final (.mp4). Por defecto, en la carpeta de trabajo.")
    ap.add_argument("--fondo", default="oscuro", choices=["oscuro", "lima", "papel"], help="Aprobado: oscuro (siempre).")
    ap.add_argument("--area", default=""); ap.add_argument("--fuente", default="")
    ap.add_argument("--nombre"); ap.add_argument("--subs", help="subs.json del reel (reutiliza tiempos y traducción).")
    ap.add_argument("--encuadre", default="centro", choices=["izquierda", "centro", "derecha"])
    ap.add_argument("--recorte", metavar="W:H:X:Y")
    ap.add_argument("--idioma"); ap.add_argument("--modelo", default="medium")
    ap.add_argument("--sin-subs", action="store_true"); ap.add_argument("--salud-mental", action="store_true")
    ap.add_argument("--solo-capa", action="store_true", help="Prueba de 4 s, rápida.")
    ap.add_argument("--silenciar", default="", metavar="INI-FIN,…",
                    help="Tramos de audio a silenciar en segundos (malas palabras), ej. 29.8-30.6,31.4-31.8")
    ap.add_argument("--raiz")
    a = ap.parse_args()

    video = Path(a.video).expanduser().resolve()
    if not video.exists():
        p18.die(f"No existe el video: {video}")
    raiz = p18.buscar_raiz(a.raiz)
    ffmpeg = p18.buscar_ffmpeg()
    vw, vh, fps, dur, audio = p18.probe(ffmpeg, str(video))
    pre = ""
    if a.recorte:
        cw, ch, cx, cy = (int(x) for x in a.recorte.split(":"))
        pre, vw, vh = f"crop={cw}:{ch}:{cx}:{cy},", cw, ch

    nombre = a.nombre or re.sub(r"^\d{4}-\d{2}-\d{2}\s*-?\s*", "", video.stem)
    trabajo = raiz / "05 Filtro de reels" / "Trabajos" / f"{datetime.date.today().isoformat()} {nombre} (carrusel)"
    trabajo.mkdir(parents=True, exist_ok=True)

    # subtítulos
    frases, idioma = [], "es"
    if not a.sin_subs and audio:
        sj = Path(a.subs) if a.subs else trabajo / "subs.json"
        if sj.exists():
            d = json.loads(sj.read_text(encoding="utf-8")); frases, idioma = d["frases"], d["idioma"]
            print(f"• Uso subtítulos: {sj}")
        elif not a.solo_capa:
            from transcribir import transcribir
            tr = transcribir(str(video), a.modelo, a.idioma, ffmpeg=ffmpeg)
            idioma, frases = tr["idioma"], p18.armar_frases(tr)
            if idioma != "es":
                for f in frases:
                    f["es"] = None
            sj.write_text(json.dumps({"idioma": idioma, "frases": frases}, ensure_ascii=False, indent=1), encoding="utf-8")
        if idioma != "es" and any(f.get("es") is None for f in frases):
            print(f"⚠ Audio en '{idioma}': completá \"es\" en {sj} y volvé a correr."); sys.exit(3)

    fin = min(dur, MAX_DUR)
    if frases:
        fin = min(fin, max(f["fin"] for f in frases) + 0.5)
    if a.solo_capa:
        fin = min(4.0, dur)

    info = capa(trabajo / "capa.png", {"fondo": a.fondo, "area": a.area, "t": a.titulo, "src": a.fuente,
                                        "top": TOP, "s": LADO})
    if info.get("desborda"):
        print("DESBORDA: el título no entra en 2 renglones; acortalo.")
    bx, by, s = int(info["left"]), int(info["top"]), int(info["s"])
    p18.generar_mascara(trabajo / "mascara.png", s, s)
    ass(trabajo / "subs.ass", frases, idioma, bx, by + s, a.salud_mental, fin)
    (trabajo / "fuentes").mkdir(exist_ok=True)
    for ttf in p18.ASSETS.glob("Manrope-*.ttf"):
        shutil.copy(ttf, trabajo / "fuentes" / ttf.name)

    xf = {"izquierda": 0.0, "centro": 0.5, "derecha": 1.0}[a.encuadre]
    filtros = (f"[1:v]{pre}scale={s}:{s}:force_original_aspect_ratio=increase:flags=lanczos,"
               f"crop={s}:{s}:(iw-{s})*{xf}:(ih-{s})/2,setsar=1,format=rgba[v];[2:v]format=gray[m];[v][m]alphamerge[vm];"
               f"[0:v][vm]overlay={bx}:{by}:shortest=1:format=auto,subtitles=subs.ass:fontsdir=fuentes,"
               f"scale=out_color_matrix=bt709:out_range=tv:flags=lanczos,format=yuv420p[out]")
    salida = trabajo / ("prueba.mp4" if a.solo_capa else "render.mp4")
    cmd = [ffmpeg, "-hide_banner", "-v", "error", "-stats", "-y", "-loop", "1", "-framerate", f"{fps:.5f}", "-i", "capa.png",
           "-i", str(video), "-loop", "1", "-framerate", f"{fps:.5f}", "-i", "mascara.png", "-t", f"{fin:.3f}"]
    if audio:
        mudo = "".join(f"volume=enable='between(t,{float(x.split('-')[0]):.2f},{float(x.split('-')[1]):.2f})':volume=0,"
                       for x in a.silenciar.split(",") if "-" in x)
        filtros += f";[1:a:0]{mudo}afade=t=out:st={max(0.0, fin - 0.45):.2f}:d=0.45[a]"
    cmd += ["-filter_complex", filtros, "-map", "[out]"]
    if audio:
        cmd += ["-map", "[a]", "-c:a", "aac", "-b:a", "320k", "-ar", "48000"]
    cmd += ["-r", f"{fps:.5f}"] + (["-c:v", "libx264", "-preset", "veryfast", "-crf", "23"] if a.solo_capa else
            ["-c:v", "libx264", "-preset", "slow", "-crf", "14", "-tune", "film", "-profile:v", "high", "-level:v", "4.2",
             "-g", str(round(fps)), "-bf", "2"])
    cmd += ["-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
            "-color_range", "tv", "-bsf:v", "h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1:video_full_range_flag=0", "-movflags", "+faststart", str(salida)]
    print(f"• Componiendo slide de carrusel ({fin:.1f} s, recuadro {s}x{s}, fondo {a.fondo})…")
    subprocess.run(cmd, check=True, cwd=trabajo)

    caps = trabajo / "capturas.jpg"
    ins = []
    for x in (0.1, 0.4, 0.7, 0.95):
        ins += ["-ss", f"{fin * x:.2f}", "-i", str(salida)]
    g = "".join(f"[{i}:v]trim=end_frame=1,scale=432:540[c{i}];" for i in range(4)) + "".join(f"[c{i}]" for i in range(4)) + "hstack=4[out]"
    subprocess.run([ffmpeg, "-v", "error", "-y", *ins, "-filter_complex", g, "-map", "[out]", "-frames:v", "1", "-q:v", "3", str(caps)], check=True)

    if a.salida and not a.solo_capa:
        dest = Path(a.salida).expanduser()
        dest = dest if dest.is_absolute() else raiz / dest
        dest.parent.mkdir(parents=True, exist_ok=True)
        n = 2
        base = dest
        while dest.exists():
            dest = base.with_name(f"{base.stem} v{n}{base.suffix}"); n += 1
        shutil.move(str(salida), dest)
        salida = dest
    print(f"\n✓ Slide de carrusel: {salida}\n  Capturas: {caps}")


if __name__ == "__main__":
    main()
