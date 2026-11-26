---
name: p18-clipear
description: Recorta un video de YouTube (link) o un .mp4 local en 3 a 5 clips crudos de 30–60 s con potencial viral para Proyecto 18 (P18). Usala cuando peguen un link de YouTube y pidan "clipear", "sacar clips", "recortar momentos" o "buscar reels" de un video. Descarga con yt-dlp, transcribe con faster-whisper (tiempos por palabra), elige los momentos según los parámetros y áreas de P18, los corta con ffmpeg sin filtro ni subtítulos en "06 Biblioteca/Clips crudos/<fecha> - <fuente>/" con un .txt por clip, y muestra la lista para aprobar o descartar. Nunca publica.
---

# p18-clipear — de un link a clips crudos

Paso 1 de 2. El paso 2 (formato P18) es la skill `p18-filtro` (comando `p18`), y sólo con clips aprobados.

`p18-clipear` está enlazado en `/opt/homebrew/bin/`. Si no existe (por ejemplo, en Cowork), usá
`bash <esta carpeta>/scripts/p18-clipear ...` — la primera vez corre `scripts/setup.sh`.

## Flujo

### 1. Preparar (descarga + transcripción)

```bash
p18-clipear preparar "https://youtu.be/XXXX" --fuente "Programa - Invitado"
```

- `--fuente`: cómo se acredita (programa + invitado). Si no se pasa, usa el nombre del canal.
- Descarga H.264 + AAC hasta 1080p (se corta sin problemas y alcanza para el recuadro de 1000 px), sin
  subtítulos incrustados. Si el video original ya trae subtítulos **quemados**, avisá: conviene buscar otra
  subida o recortarlos después con `p18 --recorte`.
- Transcribe con faster-whisper `medium`. **Tarda**: ~0,3–0,5× la duración del video en CPU (un podcast de
  2 h ≈ 40–60 min). Corrélo en segundo plano y avisale a la persona.
- Si el mismo video ya se preparó, reutiliza la carpeta y la transcripción.
- Al final imprime `CARPETA=...`. Ahí quedan `_original/video.mp4`, `meta.json`, `transcripcion.json`
  (con palabras) y `transcripcion.txt` (legible, con segundos).

### 2. Elegir 3 a 5 momentos (lo hace el agente)

Leé `_original/transcripcion.txt` completa (si es larga, por partes). Buscá momentos de **30 a 60 s** que:

1. **Gancho en los primeros 3 s**: arranca con una frase que frena el scroll (pregunta, dato que sorprende,
   contradicción, "el error que…", una historia en primera persona). No arrancar con "y entonces", "como
   te decía", muletillas o respuestas a algo que no se ve.
2. **Idea completa que se entiende sola**, sin contexto previo: no depende de "eso que dijimos antes", de
   nombres sin presentar ni de la pregunta del entrevistador. Termina en un cierre natural (fin de frase).
3. **Lenguaje simple**, para un chico de 17–19 que recién empieza.
4. **Encaja en un departamento y un área** de P18 (lista abajo).

Y que respeten los **parámetros P18** (si una parte los rompe, se descarta o se corta antes):

- Para principiantes; claro, cercano y sin jerga (o con jerga que se explica en el mismo clip).
- **Sin promesas de dinero o éxito.** Se puede hablar de plata, pero no puede ser el foco: nada de
  "cómo me hice millonario", cifras de facturación como gancho o "vas a ganar X".
- **Sin política**: descartar cualquier parte donde alguien opine de política, gobiernos o partidos.
- **Salud**: nada de pesos, calorías ni cuerpos ideales; nunca decir qué tomar ni diagnosticar. Si es de
  salud mental, el .txt lo marca y en `p18` se usa `--salud-mental` (invita a hablarlo con alguien de
  confianza o un profesional).
- Sin daño, sin desinformación (si dice un dato dudoso, no lo uses), siempre con crédito a la fuente.
- **Deporte**: sacar conceptos para la vida (disciplina, presión, equipo), no enseñar a entrenar.

Preferí variedad (no 5 clips del mismo tema) y calidad sobre cantidad: si sólo hay 3 buenos, son 3.

Escribí el plan en `<CARPETA>/plan.json`:

```json
{"clips": [
  {"ini": 754.2, "fin": 801.0,
   "titulo": "NADIE TE ENSEÑA A PERDERLE EL MIEDO AL *NO*",
   "departamento": "Finanzas y trabajo", "area": "Ideas, proyectos y ventas",
   "tema": "Miedo al rechazo al vender", "slug": "miedo al no",
   "gancho": "Las primeras palabras del clip",
   "porque": "Por qué funciona: gancho, idea completa, para quién es, qué se lleva el que lo ve.",
   "notas": "Opcional: riesgos o dudas para quien revisa (p. ej. menciona una cifra)."}
]}
```

- `ini`/`fin` en segundos (de la transcripción). El script los ajusta solo al inicio de la primera palabra
  y al final de la última.
- `titulo`: en MAYÚSCULAS, corto (≤ ~12 palabras), sin clickbait de plata, con 1–3 palabras clave entre
  `*asteriscos*` (van en lima en el reel).

### 3. Cortar

```bash
p18-clipear cortar "<CARPETA>" "<CARPETA>/plan.json"
```

- Corta sin reencodear sólo si hay un keyframe justo en el inicio; si no, reencodea en alta calidad
  (CRF 16) para que el clip arranque exacto en la primera palabra (en YouTube casi siempre pasa esto).
  `--copiar` fuerza el corte sin reencodear (puede arrancar unos segundos antes).
- Valida que departamento y área existan. Avisa si un clip no dura 30–60 s.
- Deja `NN - <tema>.mp4` (crudo, sin filtro ni subtítulos) + `NN - <tema>.txt` (inicio y fin, transcripción,
  título, departamento, área, tema, por qué, fuente con link al minuto, y el comando `p18` listo) +
  `LISTA PARA APROBAR.md`. Nunca pisa archivos existentes.

### 4. Mostrar y esperar

Mostrale a la persona una tabla: nº, minuto, duración, título, departamento › área, y en una línea por qué.
Pedí que **apruebe o descarte** cada uno. **Nunca publiques nada.** No borres los descartados sin preguntar.
Con los aprobados, seguí con la skill `p18-filtro`.

## Departamentos y áreas (usar exactamente estos nombres)

- **Crecimiento personal**: Autoconocimiento · Hábitos y constancia · Mentalidad y adaptación · Liderazgo
- **Finanzas y trabajo**: Finanzas personales · Trabajo y oportunidades · Ideas, proyectos y ventas
- **Crear y comunicar**: Arte y diseño · Vínculos y comunicación · Redes y contenido · Inteligencia artificial
- **Salud**: Salud mental · Vínculos · Salud física · Alimentación · Sueño · Bienestar
- **Deporte y mentalidad**: Disciplina y proceso · Presión y dificultad · Liderazgo y equipo · Mentalidad aplicada

## Requisitos

Los mismos que `p18-filtro` (`scripts/setup.sh`): ffmpeg (`ffmpeg-full`), yt-dlp + deno, Python 3.12 y el
entorno `~/.local/share/p18/venv` con faster-whisper. Variable opcional `P18_RAIZ` (carpeta del proyecto).
