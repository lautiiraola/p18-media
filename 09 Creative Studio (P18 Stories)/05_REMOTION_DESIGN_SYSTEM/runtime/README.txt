RUNTIME COMPARTIDO — P18 STORIES
Creado durante la primera producción real (P18-001, 2026-11-24), como prevé 05_REMOTION_DESIGN_SYSTEM/arquitectura.txt.

QUÉ ES
Un proyecto Remotion con una sola composición genérica, P18Story: 1080 × 1920, 60 fps. No contiene datos de ningún protagonista.
Cada video aporta:
- sus datos, con --props: 09_.../<video>/06_remotion/<id>.props.json, generado por el build_props.py de esa producción;
- sus assets, con --public-dir: 09_.../<video>/06_remotion/public (imágenes, voz, cama, SFX, fuentes).

VERSIONES (fijas)
remotion 4.0.545 · @remotion/cli 4.0.545 · react 19.3.1 · typescript 7.0.2 · node 26.0.0

ESTRUCTURA
src/tokens        tokens visuales (tokens.txt)
src/types.ts      contrato de props (StoryData, Scene, Caption)
src/components    Brand (fondo, firma P18 sin fondo, kicker, crédito, subrayado), Archive (foto y documento),
                  Typography (cita sincronizada, cita que se desarma, pregunta final),
                  Graphics (ciclón, silueta de aspiradora, grilla y contador de prototipos, timeline, métrica, etc.)
src/subtitles     NarrativeSubtitle (1–2 líneas, una palabra activa con subrayado lima)
src/scenes        SceneView: traduce cada escena según su campo "type"
src/compositions  P18Story: escenas, subtítulos, firma y audio (voz, cama automatizada, SFX)
src/utils         carga local de Manrope; easing; pseudo-aleatorio determinista

COMANDOS (desde esta carpeta)
Typecheck:
  ./node_modules/.bin/tsc --noEmit -p .
Fotograma de control:
  npx remotion still P18Story out.png --frame=<n> --props=<props.json> --public-dir=<public>
Render de revisión:
  npx remotion render P18Story <out.mp4> --props=<props.json> --public-dir=<public> --codec=h264 --crf=18 --audio-codec=aac --audio-bitrate=320k

REGLAS
- Toda animación deriva del frame; no hay timers.
- No se cargan URLs remotas.
- Los componentes de Graphics.tsx que son específicos de una historia (ciclón, silueta de aspiradora) quedan como candidatos.
  Se generalizan o se mueven a la producción cuando aparezca un segundo uso.

LOTE 2 (P18-002, 2026-11-24) — src/components/Graphics2.tsx
PeopleGrid (grilla de N personas con veredicto NO/SÍ y zoom), BrowserMock (navegador de época que escribe la URL y muestra un logo),
ChartReveal (gráfico real revelado con marcas de año arriba o abajo), VoteBar (votación que se frena en "CASI"), LossYears (barras parejas hasta el equilibrio),
VideoCard (OffthreadVideo mudo en tarjeta con crédito), FullBleedPhoto (foto vertical a pantalla completa con zoom), BigLine (titular grande).
Tipos de escena nuevos en SceneView: people, photoThenBrowser, videoQuote, chart, vote, losses, photoThenSlide, fullbleed.

CIERRE FIJO 3D (aprobado el 2026-11-24) — src/components/Outro3D.tsx, escena "outro3d"
Dependencias agregadas (versiones fijas): @remotion/three 4.0.545, three 0.170.0, @react-three/fiber 9.1.2, @types/three 0.170.0.
remotion.config.ts usa Config.setChromiumOpenGlRenderer('angle') para el WebGL.
Logo 3D: contornos de Manrope 800 en src/assets/p18-glyphs.json, generados con scripts/extract_glyphs.py (requiere fontTools).
Campos por video: fromNumber, fromLabel. Fijos: line "Mentalidad emprendedora para los jóvenes.", lineAccent "los jóvenes", handle @proyecto18.ar.

TIPOGRAFÍA ROTATIVA (2026-11-24)
tokens.FONTS = {sans: Manrope, display: Unbounded, serif: Instrument Serif, mono: JetBrains Mono}. utils/fonts.ts carga las 5 caras desde public/fonts.
NarrativeSubtitle.assignStyles rota editorial, serif, caps y punch por frase, sin repetir estilo seguido (se puede forzar con caption.style).
Citas (SyncedQuote, DissolvingQuote) en serif itálica. Cifras (Counter, Metric, YearCard, BigLine, LossYears) en display. Créditos y Tag en mono.
Cada producción tiene que tener en public/fonts: Manrope-Variable.ttf, Unbounded-Variable.ttf, InstrumentSerif-Regular.ttf, InstrumentSerif-Italic.ttf, JetBrainsMono-Variable.ttf.

TIPOGRAFÍA CINÉTICA (2026-11-24) — src/subtitles/Kinetic.tsx
KWord (movimientos rise, focus, slam, pop y type), Marker (barrido lima), exitStyle (salida), LetterCascade (letra por letra), springAt.
NarrativeSubtitle: rota editorial, serif, caps y stack; cada palabra entra en su t0 de voz. SyncedQuote usa focus, QuestionClose usa rise, BigLine y Kicker usan LetterCascade.

IMÁGENES ROTATIVAS (2026-11-24) — src/components/Motion.tsx
ImageEnter (entradas iris, wipe, blinds, drop, zoom, slide, flip y rise, con salida), GalleryCard y Gallery (tarjetas polaroid, film o sin marco, con Ken Burns, crédito y rotación).
Cualquier escena acepta "gallery" [{src, at, until?, x, y, w, h, rot?, enter?, frame?, credit?, fx?, fy?, mono?}]. Las escenas de foto aceptan "enter".

LOTE v05 (2026-11-24): imágenes sin repetir y subtítulos limpios
- scripts/p18_build.py (nuevo): chunk_captions() hace los cortes de subtítulos por frase y acepta BREAKS editoriales; assert_unique_images() corta el build si una imagen se repite.
  Los build_props.py lo importan con sys.path (STUDIO/05_REMOTION_DESIGN_SYSTEM/runtime/scripts).
- subtitles/Kinetic.tsx:
  - rise sin máscara;
  - focus sin letterSpacing;
  - slam más corto (escala 1,32 y 3°), para que no encime palabras;
  - Marker como resaltador completo;
  - exitStyle(t, end, nextStart): sin salida si el próximo subtítulo entra enseguida.
- subtitles/NarrativeSubtitle.tsx: las palabras entran 0,08 s antes de la voz; stack en orden de lectura; palabra clave editorial en tinta sobre lima.
