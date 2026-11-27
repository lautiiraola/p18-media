# Central P18

La página online de P18: **https://claude.ai/artifact/GCfxyLRB5Pfr943DpDyTaU**
Tres secciones: **Biblioteca** (material, clips, grilla, noticias, entrevistas, historias), **Red P18** (nuestra red + oportunidades) y **Equipo** (áreas, agentes y personas).

## Qué hay acá
- `central.html` — el código de la página (diseño y funciones). **Esta es la versión oficial**: se edita acá.

## Qué NO hay acá
Los datos (contactos de la red, grilla, clips, equipo, avisos de los agentes) viven en la base de datos de la Central,
no en este archivo. Se editan desde la página misma o los cambian los agentes.

## Cómo cambiar la Central
1. Editá `central.html` (o pedíselo a Claude: "en la Central, cambiá …").
2. Guardá el cambio en GitHub (commit + push).
3. Publicá: abrí Claude Code en esta carpeta y pedile **"publicá la Central"**. Claude publica `01 Web/Central P18/central.html`
   en el link de arriba (mismo link, se actualiza para todos).

Para publicar hace falta permiso de edición en la Central: Lauti lo da desde el menú **Compartir** de la página.
Antes de editar, hacé `git pull` para tener la última versión y no pisar cambios de otro.

## Colecciones de la base (para quien arme algo que lea los datos)
`videos`, `clips`, `grilla`, `noticias`, `entrevistas`, `historias_vida`, `red`, `oportunidades`,
`equipo_areas` (áreas), `equipo` (un doc por puesto: nombre, rol, area, tipo, estado, tarea…), `equipo_feed` (avisos de los agentes).
