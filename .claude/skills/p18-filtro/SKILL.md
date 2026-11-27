---
name: p18-filtro
description: Aplica el formato de reel de Proyecto 18 (P18) a un clip crudo aprobado, y el "filtro carrusel" (video 1:1 en slide 1080x1350, fondo oscuro) al video de los carruseles. Usala cuando pidan "pasar al filtro P18", "formato P18", "armar el reel" o "ponerle la plantilla" a un .mp4 (por ejemplo, uno de "06 Biblioteca/Clips crudos"). Hace 1080x1920 con fondo verde, logo, recuadro lima que se adapta al video, subtítulos Manrope lima sobre tinta (traducidos si el audio es en inglés), título en mayúsculas y "MENTALIDAD EMPRENDEDORA". Guarda en "04 Instagram/Reels listos para subir/" y deja capturas para revisar. Nunca publica.
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
  archivo existente (agrega ` v2`, ` v3`…). En esa carpeta van **sólo los videos finales** (un .mp4 por reel, sin
  textos, capturas ni versiones de prueba): de ahí los toma el agente que los sube a Instagram y TikTok. Las pruebas
  (`--solo-capa`) y todo lo demás quedan en la carpeta de trabajo.
- Archivos de trabajo (capa, subtítulos, capturas) en `05 Filtro de reels/Trabajos/<fecha> <nombre>/`.

## Diseño aprobado (no cambiar sin pedirlo)

1080x1920 · fondo `#14251D` con cuadrícula suave, "18" gigante en contorno lima y franjas lima (plantilla v=3) ·
arriba logo lima + chip "proyecto18.com" · recuadro de 1000 px de ancho centrado, borde lima, esquinas
redondeadas, **se adapta a la forma del video (opción A)**: alto = 1000 × alto/ancho, entre 520 y 960 px ·
**videos verticales (`--forma auto`, por defecto)**: el recuadro crece hacia abajo hasta donde deje el título y,
si aun así no entra, se angosta (mín. 760 px, centrado) para mostrar el video **entero** sin recortarlo ·
`--forma clasica`: siempre 1000 de ancho y máx. 960 de alto (recorta arriba/abajo con `--encuadre`) · subtítulos Manrope ExtraBold 46,
texto lima sobre caja tinta, sin animaciones, dentro del recuadro abajo · título debajo del recuadro ·
"MENTALIDAD EMPRENDEDORA" abajo y, si se pasa `--fuente`, el crédito a la derecha · sin intro ni cierre.

La plantilla es `assets/plantilla.html` (copia de `05 Filtro de reels/Plantilla/plantilla.html` v=3 con
el recuadro parametrizado). La original no se toca.

## Flujo que tiene que seguir el agente

1. **Revisar el clip**: sacá un fotograma (`ffmpeg -ss 5 -i clip.mp4 -frames:v 1 f.png`) y miralo.
   - Si trae subtítulos, logos o zócalos quemados de otra cuenta, recortalos con `--recorte W:H:X:Y`
     (píxeles del original, como el crop de ffmpeg). Ej.: `--recorte 1080:700:0:140`.
   - Si trae subtítulos quemados que no se pueden recortar, usá `--sin-subs`.
2. **Forma del recuadro** (sólo importa en videos verticales): por defecto `auto` muestra el video entero y
   más grande. **No es obligatorio**: usala sólo si queda mejor. Si al mostrar todo aparecen logos, zócalos o
   textos de otra cuenta, o la persona queda chica, probá `--forma clasica` (o `--recorte`) y quedate con la
   que se vea mejor en las capturas (podés comparar rápido con `--solo-capa`).
3. **Título**: si viene del .txt de `p18-clipear`, usá ese; si no, proponé uno corto (máx. ~12 palabras),
   claro, sin promesas de plata o éxito, con 1–3 palabras clave en `*lima*`.
4. **Correr `p18`**. Transcribe con faster-whisper `medium` (≈ 0,5× tiempo real en CPU).
5. **Si el audio no es castellano** el comando frena con código 3 y deja `subs.json` con `"es": null` en
   cada frase. Traducí **frase por frase, manteniendo los tiempos** (castellano rioplatense simple, sin
   jerga, que se lea rápido; ≤ ~34 caracteres por frase; podés repartir palabras entre frases vecinas).
   `"es": ""` oculta esa frase. Después volvé a correr **el mismo comando**.
6. **Revisar los subtítulos en castellano** también: abrí `subs.json`, corregí nombres propios o errores
   de Whisper (el campo es `"texto"`) y volvé a correr; reutiliza el json sin transcribir de nuevo
   (`--retranscribir` para forzar).
7. **Capturas**: abrí `Trabajos/<fecha> <nombre>/capturas.jpg` (4 momentos) y mostráselas a la persona.
   Chequeá: recuadro sin bordes negros, subtítulos legibles y sin tapar caras, título sin cortes.
8. **Aprobación humana siempre.** Decí dónde quedó el reel y esperá el OK. No publiques nada.

## Filtro carrusel (slide de video de los carruseles)

Diseño aprobado el 2026-11-15 (no cambiar sin pedirlo): 1080x1350 (4:5, igual que el resto del carrusel, porque
Instagram recorta todo el carrusel a la forma del primer elemento) · fondo **oscuro** P18 con puntos, aro y "18" en
contorno · etiqueta de área arriba a la izquierda · video en recuadro **1:1** de 880 px, borde lima · subtítulos
Manrope lima sobre tinta adentro del recuadro · título del clip debajo (2 renglones máx., *clave* en papel) · "P18"
abajo a la izquierda y "Fuente: …" a la derecha · sin "Mirá el clip" · máx. 59,5 s, corta ~0,5 s después de la última palabra.

```bash
~/.local/share/p18/venv/bin/python "<esta carpeta>/scripts/carrusel.py" "<clip crudo>.mp4" "No fue *suerte*: fue *esfuerzo*" \
  --salida "<carpeta del carrusel>/NN - video.mp4" --area "Hábitos y disciplina" --fuente "Manu Ginóbili" \
  --subs "05 Filtro de reels/Trabajos/<fecha> <nombre del reel>/subs.json" [--encuadre izquierda|centro|derecha] [--recorte W:H:X:Y]
```
Malas palabras: `--silenciar 29.8-30.6,31.4-31.8` (segundos del clip, de `transcripcion.json` del reel) silencia el audio en esos tramos; además cambiá el subtítulo por una palabra limpia en una copia del `subs.json` (ej. `subs_limpio.json`).
Plantilla: `assets/carrusel.html`. Lo llama solo `p18-contenido` (piezas.py) cuando arma un carrusel con video; no
hace falta correrlo a mano. Deja `capturas.jpg` en `05 Filtro de reels/Trabajos/<fecha> <nombre> (carrusel)/`.

## Biblioteca viva P18 (de dónde salen los clips y adónde van los reels)

Artifact https://claude.ai/artifact/GCfxyLRB5Pfr943DpDyTaU, colección `clips` (ver la skill `p18-clipear` para
todos los campos). La persona aprueba clips en el apartado **Clips crudos**; esta skill los pasa al formato P18 y
aparecen en **Videos listos**.

1. Candidatos: `clips` con `estado == "aprobado"` y sin `reel.url` (y `reel_estado` distinto de `error`).
2. Por cada uno: `reel_estado = "en_proceso"`, revisá un fotograma del crudo (zócalos/logos quemados →
   `--recorte`), y corré `p18 "<raíz>/<archivo>" "<titulo_p18>" --fuente "<fuente del video>" --nombre "<Video> - <tema corto>"`
   (más `--salud-mental` si el área es Salud mental). Mirá `capturas.jpg`.
3. Subí `05 Filtro de reels/Trabajos/<fecha> <nombre>/vista.mp4` con `Artifact` (`asset: true`, `url` de la biblioteca).
4. Actualizá el clip: `reel = {id, url, archivo: "04 Instagram/Reels listos para subir/<archivo>.mp4"}`, `reel_estado = "listo"`.
   Si falla: `reel_estado = "error"` y un `reel_detalle` corto.
5. Nunca publiques en redes: el reel queda para que una persona lo revise y lo suba.

## Calidad de exportación

El reel final sale listo para Instagram y TikTok sin pérdida visible: 1080x1920, H.264 High 4.2, CRF 14
(preset slow), un keyframe por segundo, color BT.709 etiquetado (el lima no se corre), audio AAC 320 kbps 48 kHz.
Los clips crudos llegan de la mejor versión de YouTube (VP9/AV1 hasta 4K) en CRF 14.

## Opciones

| Opción | Para qué |
|---|---|
| `--fuente "X"` | Crédito a la fuente (siempre que se sepa). |
| `--nombre "X"` | Nombre del archivo final (sin fecha). Por defecto, el del clip. |
| `--recorte W:H:X:Y` | Sacar zócalos/logos/subtítulos quemados del original. |
| `--forma auto\|clasica` | Verticales: `auto` agranda el recuadro para mostrar el video entero; `clasica`, el de siempre. |
| `--encuadre arriba\|centro\|abajo` | Qué parte se conserva al recortar para entrar al recuadro. |
| `--sin-subs` | Sin subtítulos. |
| `--salud-mental` | Clips de salud mental: agrega al final "Si te pasa algo parecido, hablalo con alguien de confianza o con un profesional." |
| `--idioma es\|en` | Forzar idioma si la detección falla. |
| `--solo-capa` | Prueba rápida de 4 s (no guarda en Reels listos). |

Además de el reel, deja `vista.mp4` (540x960, liviana) en la carpeta de trabajo para subir a la Biblioteca viva.
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
