# Entrevistas P18 (Café IA de emprendedores y las que vengan)

## Flujo
1. **Crudo**: el video largo va a `Crudos/` y se carga en la Biblioteca viva → pestaña **Entrevistas → Material crudo**
   (nombre, emprendimiento, archivo o link). Queda en estado "Esperando edición".
2. **Edición** (skill `p18-entrevistas`, pendiente: se arma con el primer video editado por Valen y sus instrucciones):
   recorta, ordena y aplica el formato "P18 entrevistas" igual que Valen, entendiendo por qué hace cada corte.
   El resultado (~4 min) va a `Editadas/` y aparece en **Entrevistas → Editadas**.
3. **Partes**: cada entrevista editada se divide en partes (criterio a definir) → `Partes/`.
4. **Grilla**: cada parte se suma a un día como **slot extra** `tipo: "Entrevista"` (no reemplaza reels, posts ni
   carrusel de ese día), con `pub.video` = la parte y su caption/historia hecha con la skill 3 (`p18-publicar`).
   El publicador ya lo sube como reel en Instagram y en YouTube/TikTok (sólo reels).

## Datos en la Biblioteca viva (colección `entrevistas`)
`{nombre, emprendimiento, fecha_grabacion, crudo: {archivo | link}, nota, estado: crudo|editando|editada|error,
detalle, editado: {id, url, archivo, dur}, resumen, partes: [{n, titulo, dur, archivo, url, dia, publicado}], creado}`

## Slot de grilla
`{tipo: "Entrevista", dep, area, titulo, entrevista_id, parte, pub: {video, caption, hashtags, comentario, tiktok,
historias, publicado}}`, agregado al final de `slots` del día.

## Falta
- Primer video editado por Valen + sus instrucciones/formato → crear `p18-entrevistas`.
- Definir cómo se divide cada entrevista y cada cuántos días va una parte.
