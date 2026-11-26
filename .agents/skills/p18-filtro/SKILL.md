---
name: p18-filtro
description: Aplica el formato de reel de Proyecto 18 (P18) a un clip crudo aprobado. Usala cuando pidan "pasar al filtro P18", "formato P18", "armar el reel" o "ponerle la plantilla" a un .mp4 (por ejemplo, uno de "06 Biblioteca/Clips crudos"). Hace 1080x1920 con fondo verde, logo, recuadro lima que se adapta al video, subtítulos Manrope lima sobre tinta (traducidos si el audio es en inglés), título en mayúsculas y "MENTALIDAD EMPRENDEDORA". Guarda en "04 Instagram/Reels listos para subir/" y deja capturas para revisar. Nunca publica.
---

# p18-filtro — formato de reel P18

Un solo comando:

```bash
p18 clip.mp4 "TÍTULO CON *PALABRAS CLAVE*" --fuente "Nombre de la fuente"
```

- `p18` está enlazado en `/opt/homebrew/bin/p18`. Si no existe (por ejemplo, en Cowork), usá
  `bash <esta carpeta>/scripts/p18 ...` — la primera vez corre `scripts/setup.sh` e instala todo.
- Las palabras entre `*asteriscos*` van en lima. El título se pasa a MAYÚSCULAS solo.
- El resultado va a `04 Instagram/Reels listos para subir/<fecha> <nombre>.mp4`. **Nunca pisa** un
  archivo existente (agrega ` v2`, ` v3`…).
- Archivos de trabajo (capa, subtítulos, capturas) en `05 Filtro de reels/Trabajos/<fecha> <nombre>/`.

## Diseño aprobado (no cambiar sin pedirlo)

1080x1920 · fondo `#14251D` con cuadrícula suave, "18" gigante en contorno lima y franjas lima (plantilla v=3) ·
arriba logo lima + chip "proyecto18.com" · recuadro de 1000 px de ancho centrado, borde lima, esquinas
redondeadas, **se adapta a la forma del video (opción A)**: alto = 1000 × alto/ancho, entre 520 y 960 px;
si el video es más vertical se recorta (`--encuadre arriba|centro|abajo`) · subtítulos Manrope ExtraBold 46,
texto lima sobre caja tinta, sin animaciones, dentro del recuadro abajo · título debajo del recuadro ·
"MENTALIDAD EMPRENDEDORA" abajo y, si se pasa `--fuente`, el crédito a la derecha · sin intro ni cierre.

La plantilla es `assets/plantilla.html` (copia de `05 Filtro de reels/Plantilla/plantilla.html` v=3 con
el recuadro parametrizado). La original no se toca.

## Flujo que tiene que seguir el agente

1. **Revisar el clip**: sacá un fotograma (`ffmpeg -ss 5 -i clip.mp4 -frames:v 1 f.png`) y miralo.
   - Si trae subtítulos, logos o zócalos quemados de otra cuenta, recortalos con `--recorte W:H:X:Y`
     (píxeles del original, como el crop de ffmpeg). Ej.: `--recorte 1080:700:0:140`.
   - Si trae subtítulos quemados que no se pueden recortar, usá `--sin-subs`.
2. **Título**: si viene del .txt de `p18-clipear`, usá ese; si no, proponé uno corto (máx. ~12 palabras),
   claro, sin promesas de plata o éxito, con 1–3 palabras clave en `*lima*`.
3. **Correr `p18`**. Transcribe con faster-whisper `medium` (≈ 0,5× tiempo real en CPU).
4. **Si el audio no es castellano** el comando frena con código 3 y deja `subs.json` con `"es": null` en
   cada frase. Traducí **frase por frase, manteniendo los tiempos** (castellano rioplatense simple, sin
   jerga, que se lea rápido; ≤ ~34 caracteres por frase; podés repartir palabras entre frases vecinas).
   `"es": ""` oculta esa frase. Después volvé a correr **el mismo comando**.
5. **Revisar los subtítulos en castellano** también: abrí `subs.json`, corregí nombres propios o errores
   de Whisper (el campo es `"texto"`) y volvé a correr; reutiliza el json sin transcribir de nuevo
   (`--retranscribir` para forzar).
6. **Capturas**: abrí `Trabajos/<fecha> <nombre>/capturas.jpg` (4 momentos) y mostráselas a la persona.
   Chequeá: recuadro sin bordes negros, subtítulos legibles y sin tapar caras, título sin cortes.
7. **Aprobación humana siempre.** Decí dónde quedó el reel y esperá el OK. No publiques nada.

## Opciones

| Opción | Para qué |
|---|---|
| `--fuente "X"` | Crédito a la fuente (siempre que se sepa). |
| `--nombre "X"` | Nombre del archivo final (sin fecha). Por defecto, el del clip. |
| `--recorte W:H:X:Y` | Sacar zócalos/logos/subtítulos quemados del original. |
| `--encuadre arriba\|centro\|abajo` | Qué parte se conserva al recortar para entrar al recuadro. |
| `--sin-subs` | Sin subtítulos. |
| `--salud-mental` | Clips de salud mental: agrega al final "Si te pasa algo parecido, hablalo con alguien de confianza o con un profesional." |
| `--idioma es\|en` | Forzar idioma si la detección falla. |
| `--solo-capa` | Prueba rápida de 4 s (no guarda en Reels listos). |
| `--retranscribir` | Ignora `subs.json` y transcribe de nuevo. |

## Parámetros P18 (revisar antes de dar el reel por listo)

- Para principiantes; claro, cercano y sin jerga.
- Sin promesas de dinero o éxito (se puede hablar de plata, pero no puede ser el foco).
- Sin posicionamiento político.
- Salud: nada de pesos, calorías ni cuerpos ideales; nunca decir qué tomar ni diagnosticar. Salud mental →
  `--salud-mental`.
- Sin daño, sin desinformación, siempre con crédito a la fuente.
- Deporte: conceptos para la vida, no enseñar a entrenar.
- Si algo del clip choca con esto, avisá en vez de renderizar.

## Requisitos

`scripts/setup.sh` instala (si falta): `ffmpeg-full` (ffmpeg con libass, necesario para los subtítulos),
`yt-dlp`, `deno`, Python 3.12 y un entorno en `~/.local/share/p18/venv` con faster-whisper, Playwright
(Chromium) y Pillow. Variables opcionales: `P18_RAIZ` (carpeta del proyecto), `P18_FFMPEG`,
`P18_WHISPER_DEVICE=mps` (GPU de Apple, más rápida pero experimental).
