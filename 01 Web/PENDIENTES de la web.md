# P18 web · pendientes

## Recursos que faltan
- ~~Logo~~ listo: logo final "Modular sin corte" (Escritorio/P18 - Logo Modular) en `01 Web/Sitio web/assets/logo.svg` (tinta), `logo-papel.svg` y `logo-lima.svg`, con PNG transparentes. Favicons, `apple-touch-icon.png`, íconos 192/512 y `site.webmanifest` en la raíz de la web.
- ~~Foto del hero~~ lista en `01 Web/Sitio web/assets/hero.jpg` (imagen generada; se muestra con la aclaración "Imagen ilustrativa generada").

## Integraciones
- ~~WhatsApp~~ cargado: +54 9 11 2157-0660 (`var WHATSAPP` en `01 Web/Sitio web/js/p18.js`). Cada botón abre el chat con su propio mensaje (atributo `data-wa-text` en `index.html`).
- **Formularios → Google Sheets**: el código ya está listo en `01 Web/Formularios a Google Sheets/` y guarda dos hojas (Respuestas y Serie A mis 18). Falta implementarlo con la cuenta de Google de P18 y pegar la URL `/exec` en `var ENDPOINT` al principio de `01 Web/Sitio web/js/p18.js` (pasos en `01 Web/Formularios a Google Sheets/LEEME.md`). Hasta entonces, los formularios avisan que no están conectados y no simulan el envío.
- **Privacidad**: el formulario junta datos de menores de edad. Antes de publicar hace falta una política de privacidad (Ley 25.326) y el link correspondiente al lado del botón.

## Contenido a confirmar con P18
- **Temas de los chips**: "Arte y diseño" y "Vínculos y comunicación" salen de la guía; el resto sale de los temas de la charla de la web anterior. Confirmar la lista final y si cada tema va a tener su propia página (hoy cada chip lleva al formulario con el tema ya marcado).
- **"A mis 18"**: se presenta solo como serie en desarrollo, sin fecha ni episodios.
- **Datos de la sección Qué es P18**: talleres gratuitos, virtuales o presenciales (confirmado por el equipo). Falta confirmar si sigue siendo para el último año del secundario.
- **Dominio y mail**: proyecto18.co redirige a .com, pero el mail es hola@proyecto18.co. Definir uno solo.
- **Aliados**: no se muestran porque la guía pide no inventar alianzas. Si Enjinia, Alpanel y Degalpones van, falta definir dónde.

## Propuestas nuevas (no están en la referencia)
- Opción "Soy de un colegio" en el formulario, para pedir un taller.
- Preguntas frecuentes en acordeón dentro de "Qué es P18".
- Chip "Otro tema", que lleva al campo "Contanos ese tema que no encontraste".

## Netlify
- Sitio: https://proyecto18-748.netlify.app (proyecto `proyecto18-748`, ID `71c05b3f-3b13-4671-9dc0-a0d48dff7d17`, cuenta de Lautaro). Protección de acceso desactivada para que se pueda compartir.
- Para volver a publicar después de un cambio, desde esta carpeta:
  `npx netlify-cli deploy --prod --dir "01 Web/Sitio web" --site 71c05b3f-3b13-4671-9dc0-a0d48dff7d17`
- Cuando Mati conecte el dominio: Netlify → proyecto18-748 → Domain management → Add a domain.
- **Cartel "Powered by Netlify"**: no aparece porque `01 Web/Sitio web/_headers` solo permite scripts de la carpeta `/js/` de los dominios de P18 (proyecto18-748.netlify.app, proyecto18.co y proyecto18.com, con y sin www). **Si la web pasa a otro dominio, hay que agregarlo en esa línea con `/js/` al final**; si no, los scripts de la web (scroll, formulario, cinta, WhatsApp) dejan de funcionar en ese dominio.
