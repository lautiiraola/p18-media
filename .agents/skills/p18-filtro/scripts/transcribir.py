#!/usr/bin/env python3
"""Transcribe un audio/video con faster-whisper y tiempos por palabra.

Uso: transcribir.py VIDEO SALIDA.json [--modelo medium] [--idioma es] [--desde S --hasta S]

Salida JSON:
{"idioma": "es", "duracion": 123.4, "segmentos": [
   {"ini": 0.0, "fin": 3.2, "texto": "...", "palabras": [{"ini":0.0,"fin":0.3,"p":"Hola"}, ...]}]}
"""
import argparse, json, os, subprocess, sys, tempfile, time


def extraer_audio(video, wav, desde=None, hasta=None, ffmpeg="ffmpeg"):
    cmd = [ffmpeg, "-v", "error", "-y"]
    if desde is not None:
        cmd += ["-ss", str(desde)]
    if hasta is not None:
        cmd += ["-to", str(hasta)]
    cmd += ["-i", video, "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", wav]
    subprocess.run(cmd, check=True)


def leer_wav(path):
    import wave
    import numpy as np
    with wave.open(path, "rb") as w:
        data = w.readframes(w.getnframes())
    return np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0


def cargar_modelo(WhisperModel, modelo, log=True):
    # CPU int8 por defecto (estable). P18_WHISPER_DEVICE=mps prueba la GPU de Apple
    # (más rápida pero experimental en ctranslate2: a veces se cae a mitad).
    dev = os.environ.get("P18_WHISPER_DEVICE", "cpu")
    intentos = [(dev, "int8" if dev == "cpu" else "float16")] + ([("cpu", "int8")] if dev != "cpu" else [])
    for dev, ct in intentos:
        try:
            m = WhisperModel(modelo, device=dev, compute_type=ct, cpu_threads=os.cpu_count() or 4)
            if log:
                print(f"  Whisper {modelo} en {dev} ({ct})", file=sys.stderr)
            return m
        except Exception as e:  # noqa
            if log:
                print(f"  ({dev} no disponible: {str(e)[:80]})", file=sys.stderr)
    raise RuntimeError("No pude cargar faster-whisper")


def transcribir(video, modelo="medium", idioma=None, desde=None, hasta=None, ffmpeg="ffmpeg", log=True):
    from faster_whisper import WhisperModel

    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "audio.wav")
        extraer_audio(video, wav, desde, hasta, ffmpeg)
        audio = leer_wav(wav)
        t0 = time.time()
        m = cargar_modelo(WhisperModel, modelo, log)
        largo = len(audio) / 16000
        kw = dict(language=idioma, word_timestamps=True, vad_filter=True, beam_size=5,
                  condition_on_previous_text=False)
        if largo > 600:
            # videos largos: inferencia en lotes (bastante más rápida en CPU)
            from faster_whisper import BatchedInferencePipeline
            kw.pop("condition_on_previous_text")
            segs, info = BatchedInferencePipeline(model=m).transcribe(audio, batch_size=8, **kw)
        else:
            segs, info = m.transcribe(audio, **kw)
        out = {"idioma": info.language, "duracion": round(info.duration, 2), "modelo": modelo, "segmentos": []}
        for s in segs:
            out["segmentos"].append({
                "ini": round(s.start, 2), "fin": round(s.end, 2), "texto": s.text.strip(),
                "palabras": [{"ini": round(w.start, 2), "fin": round(w.end, 2), "p": w.word.strip()}
                             for w in (s.words or []) if w.word.strip()],
            })
            if log:
                print(f"  [{s.start:7.1f}s / {info.duration:.0f}s] {s.text.strip()[:70]}", file=sys.stderr, flush=True)
        if log:
            print(f"  Transcripción lista en {time.time()-t0:.0f}s (idioma: {info.language})", file=sys.stderr)
        return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("salida")
    ap.add_argument("--modelo", default="medium"); ap.add_argument("--idioma")
    ap.add_argument("--desde", type=float); ap.add_argument("--hasta", type=float)
    ap.add_argument("--ffmpeg", default=os.environ.get("P18_FFMPEG", "ffmpeg"))
    a = ap.parse_args()
    out = transcribir(a.video, a.modelo, a.idioma, a.desde, a.hasta, a.ffmpeg)
    with open(a.salida, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(a.salida)


if __name__ == "__main__":
    main()
