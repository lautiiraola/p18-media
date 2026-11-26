# Conectar el formulario "Sumate" a Google Sheets

Toma unos 10 minutos. Conviene hacerlo con la cuenta de Google de P18 (por ejemplo, la de hola@proyecto18.co), no con una personal: la planilla y el script quedan a nombre de esa cuenta.

## 1. Crear la planilla
1. En Google Drive, creá una planilla nueva llamada **P18 · Sumate**.
2. No hace falta armar columnas: el script crea la hoja **Respuestas** con sus encabezados la primera vez que llega un envío.

## 2. Pegar el script
1. En la planilla: **Extensiones → Apps Script**.
2. Borrá lo que haya en `Code.gs` y pegá el contenido de [Code.gs](Code.gs).
3. Si querés un aviso por mail con cada respuesta, completá `NOTIFY_EMAIL` (por ejemplo, `'hola@proyecto18.co'`).
4. Guardá (ícono de disquete).

## 3. Publicarlo como aplicación web
1. **Implementar → Nueva implementación**.
2. En el engranaje de "Seleccionar tipo", elegí **Aplicación web**.
3. Configurá:
   - **Ejecutar como:** Yo.
   - **Quién tiene acceso:** Cualquier usuario.
4. **Implementar**. Google pide autorizar el acceso a la planilla (y a Gmail si completaste `NOTIFY_EMAIL`). Aceptá con la cuenta de P18.
5. Copiá la **URL de la aplicación web**. Termina en `/exec`.

## 4. Pegar la URL en la web
Al principio de `p18-web/js/p18.js`, en la sección de configuración, pegá la URL entre las comillas:

```js
var ENDPOINT = 'https://script.google.com/macros/s/…/exec';
```

La usan los dos formularios: "Tu mirada suma" y los avisos de «A mis 18».

## 5. Probar
1. Abrí la web, completá el formulario y enviá.
2. Tiene que aparecer "¡Listo, …! Recibimos lo que nos contaste." y una fila nueva en la hoja **Respuestas**.
3. Probá también "Quiero enterarme" en «A mis 18»: los avisos van a la hoja **Serie A mis 18** (nombre, email y celular).

## Si cambiás el script más adelante
**Implementar → Administrar implementaciones → editar (lápiz) → Versión: Nueva versión.** Así la URL sigue siendo la misma. Si hacés una implementación nueva, la URL cambia y hay que volver a pegarla en `index.html`.

## Qué guarda
Hoja **Respuestas**: fecha, nombre, email, perfil (joven, proyecto, mentor, organización), temas elegidos, el texto de "otro tema" y desde qué página llegó. Hoja **Serie A mis 18**: fecha, nombre, email y celular. El script descarta los envíos de bots (campo trampa oculto), valida nombre y email, recorta textos largos y evita que un texto se ejecute como fórmula en la planilla.
