# Conectar Instagram de P18 para publicar desde la skill 5 (p18-subir)

Son dos cosas, una sola vez: **(1) el token de Meta** para publicar y **(2) un lugar público para las imágenes**.
Tiempo: unos 30 minutos. Todo es gratis.

> El token es como una contraseña: no lo pegues en el chat ni en la carpeta del proyecto. Va solo en el archivo del
> paso 1.7, que está en tu usuario.

---

## 1. Token de Meta (Instagram)

**1.1 Cuenta profesional.** En la app de Instagram, en la cuenta de P18: *Configuración → Tipo de cuenta y
herramientas → Cambiar a cuenta profesional* (Creador o Empresa). Si ya lo es, seguí.

**1.2 Cuenta de desarrollador.** Entrá a https://developers.facebook.com con tu Facebook → *Comenzar* → aceptá y
verificá tu cuenta (te pide mail o teléfono).

**1.3 Crear la app.** *Mis apps → Crear app*:
- Caso de uso: **Otro** → tipo **Empresa**.
- Nombre: `P18 Publicador` y tu mail de contacto → *Crear app*.

**1.4 Agregar Instagram.** En el panel de la app → *Agregar producto* → **Instagram** → *Configurar* → elegí
**API de Instagram con inicio de sesión de Instagram** (*API setup with Instagram login*).

**1.5 Conectar la cuenta y generar el token.** En esa pantalla:
- *Generar tokens de acceso* → **Agregar cuenta** → iniciá sesión con la cuenta de Instagram de P18 → aceptá los
  permisos (tienen que figurar `instagram_business_basic` e `instagram_business_content_publish`).
- Al lado de la cuenta aparece **Generar token**: copialo. Ese token ya es de **larga duración (60 días)**.
- Copiá también el **ID de la cuenta de Instagram** (el número que aparece junto al nombre de la cuenta).

**1.6 Si la app pide estar "en vivo".** Para publicar en tu propia cuenta alcanza con que vos seas administrador de la
app (modo desarrollo). Si aparece un error de permisos, en *Roles de la app → Roles* fijate que tu usuario de
Instagram esté agregado como *Instagram tester* y aceptá la invitación desde Instagram (*Configuración → Apps y
sitios web → Invitaciones de testers*).

**1.7 Guardar el token en la compu.** Abrí la app **Terminal** y pegá esto (una línea por vez):

```bash
mkdir -p ~/.config/p18 && touch ~/.config/p18/meta.env && chmod 600 ~/.config/p18/meta.env
```

```bash
open -e ~/.config/p18/meta.env
```

Se abre un archivo de texto. Pegá esto, con tus datos, y guardá (⌘S):

```
IG_TOKEN=pegá_acá_el_token
IG_USER_ID=pegá_acá_el_id_de_la_cuenta
IG_HOST=graph.instagram.com
IG_VERSION=v23.0
```

**1.8 Avisame.** Escribí en el chat "listo el token" y corro el chequeo, que **no publica nada**: muestra la cuenta y
cuántas publicaciones por día permite Instagram.

**1.9 Permiso de métricas (para el agente estratega).** La app de P18 usa el **inicio de sesión unificado**: los
permisos del token salen de la **configuración** (Casos de uso → Personalizar → API setup with Unified login → 1.
Configurar tu app → Vista previa → **Editar permisos**), no de la lista de "Permisos y funciones". Ahí tiene que estar
**`instagram_manage_insights`** (además de `instagram_basic` e `instagram_content_publish`). Después: *2. Generar
tokens de acceso* → Generar token → reemplazá **sólo** la línea `IG_TOKEN=` del archivo del paso 1.7. La cuenta
`proyecto18.ar` tiene que haber aceptado la invitación de *Evaluador de Instagram* (Roles de la app). Sin este permiso
se publica igual, pero el estratega no ve los números. (Funcionó así el 2026-11-15.)

**Renovación:** el token vence a los 60 días. Se renueva desde el mismo botón *Generar token*, y se pega de nuevo en
el archivo.

---

## 2. Lugar público para las imágenes (GitHub, gratis)

La API de Instagram **no deja adjuntar imágenes desde la compu**: pide un link público y la imagen la baja Instagram.
Los videos sí se suben directo. Las imágenes de la Biblioteca viva tampoco sirven, porque son privadas (piden tu
sesión de Claude) e Instagram no puede abrirlas.

La solución: un repositorio público de GitHub donde la skill sube sola cada imagen antes de publicarla. Vos no tenés
que hacer nada en cada publicación.

**2.1 Cuenta.** Creá una cuenta gratis en https://github.com (o usá la que tengas).

**2.2 Repositorio.** Arriba a la derecha *+ → New repository*:
- Nombre: `p18-media`
- **Public**
- Tildá *Add a README file*
- *Create repository*

**2.3 Token de GitHub (solo para ese repo).** *Foto de perfil → Settings → Developer settings → Personal access
tokens → Fine-grained tokens → Generate new token*:
- Nombre: `P18 imágenes`. Vencimiento: 1 año.
- *Repository access*: **Only select repositories** → `p18-media`.
- *Permissions → Repository permissions → Contents*: **Read and write**.
- *Generate token* y copialo.

**2.4 Guardarlo.** Abrí el mismo archivo del paso 1.7 (`open -e ~/.config/p18/meta.env`) y agregá abajo:

```
GH_TOKEN=pegá_acá_el_token_de_github
GH_REPO=tu_usuario_de_github/p18-media
```

Guardá y avisame "listo GitHub".

Las imágenes que se suban ahí quedan públicas, igual que en Instagram. No subas nada privado a ese repositorio.

---

## 3. Conectar YouTube (Shorts)

Una sola vez, unos 15 minutos, gratis. Hace falta la cuenta de Google que maneja el canal de YouTube de P18.

**3.1 Proyecto.** Entrá a https://console.cloud.google.com con esa cuenta → arriba, selector de proyecto → **Proyecto
nuevo** → nombre `P18 Publicador` → *Crear*. Fijate que quede seleccionado.

**3.2 Activar la API.** Menú ☰ → *APIs y servicios → Biblioteca* → buscá **YouTube Data API v3** → **Habilitar**.

**3.3 Pantalla de consentimiento.** *APIs y servicios → Pantalla de consentimiento de OAuth* (o *Google Auth Platform*):
- Tipo de usuario: **Externo** → nombre de la app `P18 Publicador`, tu mail de soporte y de contacto → Guardar.
- En **Público / Usuarios de prueba**: **Agregar usuarios** → el mail de la cuenta del canal. (Mientras la app esté
  "en prueba", sólo esa cuenta puede conectarse, y alcanza.)

**3.4 Credencial.** *APIs y servicios → Credenciales* → **Crear credenciales → ID de cliente de OAuth** → tipo
**App de escritorio** → nombre `P18 compu` → *Crear* → **Descargar JSON**.

**3.5 Guardarla.** En la Terminal (cambiá la ruta si se descargó con otro nombre):
```bash
mv ~/Downloads/client_secret_*.json ~/.config/p18/youtube_client.json && chmod 600 ~/.config/p18/youtube_client.json
```

**3.6 Conectar.** En la Terminal:
```bash
python3 "$HOME/Documents/06 Proyecto 18/.claude/skills/p18-subir/scripts/yt.py" conectar
```
Se abre Google: elegí la cuenta del canal. Va a decir *"Google no verificó esta app"* → **Continuar** (es tu propia
app) → aceptá los permisos. Cuando diga "Listo", avisá "listo YouTube" en el chat.

**3.7 Público vs. privado.** Hasta que Google apruebe la app, todo lo que se sube por la API queda **privado**. Para
publicar en público sin tocar nada, hay que pedir la auditoría: https://support.google.com/youtube/contact/yt_api_form
(se completa una vez; tarda unas semanas). Mientras tanto, los Shorts se pasan a públicos con un toque en YouTube Studio.

---

## 4. TikTok (cuando exista la cuenta)

**4.1 Cuenta.** Crear la cuenta de TikTok de P18 en el celular y pasarla a **cuenta de empresa o creador**
(Configuración → Cuenta → Cambiar a cuenta de empresa).

**4.2 Desarrollador.** Entrá a https://developers.tiktok.com con esa cuenta → *Manage apps* → **Connect an app** →
nombre `P18 Publicador`.

**4.3 Lo que pide la app** (TikTok lo revisa):
- Ícono, descripción corta y categoría.
- **Web oficial, Términos y Política de privacidad**: web `https://proyecto18.com`, términos
  `https://proyecto18-748.netlify.app/terminos/` y privacidad `https://proyecto18-748.netlify.app/privacidad/`
  (cuando Valen las suba a proyecto18.com, se cambian por `https://proyecto18.com/terminos/` y `/privacidad/`).
- Productos: **Login Kit** y **Content Posting API** (con *Direct Post* activado).
- Permisos: `user.info.basic` y `video.publish`. Web y URL de redireccionamiento: `https://proyecto18-748.netlify.app/`
  (verificada en *URL properties* con el archivo `tiktok….txt` que está en la raíz de la web de Netlify).

**4.4 Revisión.** Se manda con un video corto de demostración (Claude puede armarlo con una prueba en modo sandbox).
TikTok tarda unos días. **Hasta que la aprueben, lo que se sube por la API queda privado** (sólo lo ve la cuenta).

Cuando la cuenta exista, avisá en el chat y seguimos con 4.2.
