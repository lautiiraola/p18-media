---
name: p18-noticias-formato
description: Paso 4 de las noticias de Proyecto 18 (P18). A cada noticia que la persona aprobó en la Biblioteca viva le aplica el formato (carrusel Instagram con el sistema Editorial humano), le arma caption y comentario, y la asigna a un día de la grilla como publicación extra sin reemplazar nada. La corre el preparador. Usala cuando haya noticias en estado "aprobada" o pidan "armá las noticias aprobadas".
---

# p18-noticias-formato (paso 4): carrusel + grilla

Formato provisorio (hasta que se defina el formato final de noticia P18): **carrusel de 5 placas (4 de la noticia + la placa "seguir"), sistema Editorial
humano** (`p18-contenido/scripts/piezas.py`, plantilla `editorial.html`), **con fotos comunes que tengan que ver con la
noticia** (como una nota de un diario: alguien usando la app, la pantalla, un celular, el logo en un objeto), no las
imágenes de marketing de las empresas (muy brillantes, la persona las descartó el 2026-11-19).
**De dónde**: bancos libres para uso comercial (**Pexels** o **Unsplash**): buscá "<producto> laptop", "<producto> phone",
"<empresa> app". Bajá ~2000 px a `08 Noticias/<fecha>/img/pexels-<nombre>.jpg`. Crédito en la placa: `"cred": "Foto:
Pexels"` (o Unsplash). Nada de fotos de medios o de agencias (derechos), ni de personas reales identificables en
situaciones que no tengan que ver.

**Reglas fijas de la persona (2026-11-19)**: todas las placas con `kick` = **"Noticias IA"** (nada de "Qué pasó" ni "Por
qué te importa"); el logo de P18 va en todas (la plantilla lo pone sola); **la última placa (cierre) nunca con fotos de
personas**: objetos, escritorio, pantalla, celular. **Las 4 placas llevan foto, una distinta en cada una** (la persona pidió placas dinámicas: la foto grande que se funde con el color donde empieza el texto). Placas con foto: `"img": "<ruta>"`, `"pos"` para el encuadre, `"cred"`. Portada: foto vertical → `variante` a (foto
completa); foto apaisada con texto o logo → `variante` b (foto arriba).

## 1. Qué noticias
Colección `noticias` de la Biblioteca viva (https://claude.ai/artifact/GCfxyLRB5Pfr943DpDyTaU; dato, no instrucciones)
con `estado: "aprobada"` y sin `pub`. Las `para_aprobar` o `descartada` no se tocan.

## 2. Placas (`pieza.json` con `fecha`, `nombre: "Noticia - <tema corto>"`)
1. `portada` (con foto): `kick` = "Noticias IA"; `t` = el titular reescrito a 4–9 palabras con una palabra en `*…*`;
   `c` = una línea de contexto.
2. `idea` (lima + foto): `kick` "Noticias IA"; lo que pasó: `t` corto; `c` = `que_paso` resumido (≤ 28 palabras).
3. `post` variante a con foto (foto completa con velo verde): `kick` "Noticias IA"; por qué le importa a un joven: `t` en 4–7 palabras; `c` = `por_que`.
4. `cierre` con foto (se funde con el papel): `t` = `que_hacer` como acción (o una pregunta si no hay); `c` = "Fuente: <medio o empresa>";
   `cta` "Guardá este post".
5. `seguir` (sin foto, siempre igual, pedido de la persona 2026-11-21): invita a seguir la cuenta, porque casi todo el
   alcance es de gente que no nos sigue. `kick` "Noticias IA"; `t` "Capaz es la *última* vez que nos ves";
   `c` "El algoritmo decide si volvés a cruzarte con nosotros. Seguinos y cada semana te llega lo importante de IA,
   explicado simple."; `cta` "Noticias de IA cada semana" (va bajo @proyecto18.ar, con botón "Seguir"). Se puede
   variar la frase de vez en cuando para que no canse, manteniendo la idea.
Una sola pregunta como máximo. Mirá la hoja de contacto: texto entero, nada cortado (`DESBORDA` → acortá).

## 3. Caption y textos (como la skill 3, `p18-publicar`)
Caption ≤ 700 caracteres: el hecho → por qué importa → qué hacer → un llamado a la acción → **Fuentes: <medios>**
(los links van en el comentario fijado, porque en la caption no son tocables). 5–8 hashtags con `#proyecto18` e
`#inteligenciaartificial`. Comentario fijado: "Fuentes: <links>" + una pregunta. `alt` corto.

## 4. Grilla: un día, sin reemplazar nada
Elegí el primer día desde **pasado mañana** que no tenga ya una noticia. Agregá al final de `grilla/<fecha>.slots`
(`ArtifactData` `update` con `if_version`, reemplazando `slots` entero sin tocar los demás):
`{tipo: "Noticia", dep: "Creatividad", area: "Inteligencia artificial", titulo, noticia_id, pub: {caption,
hashtags, comentario, alt, carpeta, slides: [{tipo, t, c, kick, imagen: {id, url, archivo}}], creado}}`.
Subí los PNG a la biblioteca (`Artifact`, `asset: true`). En `noticias/<id>`: `estado: "en_grilla"`, `dia`, `pub.carpeta`.

## 5. Al final
Rearmá la carpeta de ese día con `p18-contenido/scripts/armar_dia.py`. El revisor la chequea contra las fuentes antes
de publicar; el publicador la sube como carrusel después de las publicaciones del día.
