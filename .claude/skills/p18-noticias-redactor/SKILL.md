---
name: p18-noticias-redactor
description: Paso 3 de las noticias de Proyecto 18 (P18). Escribe cada noticia elegida en la voz de P18 (titular, qué pasó, por qué te importa, qué podés hacer, fuentes) y la carga en la sección Noticias de la Biblioteca viva para que la persona la apruebe. No diseña ni publica. Usala después de p18-noticias-curador o cuando pidan "redactá las noticias".
---

# p18-noticias-redactor (paso 3): escribir

Entrada: `08 Noticias/<fecha>/elegidas.json`. Formato provisorio hasta que se defina el formato final de noticia P18.

## Voz
Castellano rioplatense con voseo, claro, cercano y preciso, como un buen medio que le habla a alguien de 17-19. Sin
jerga ni siglas sin explicar, sin alarmismo, sin exagerar, sin opinar como si fuera un dato. Cada dato tiene que estar
en las fuentes. Nada de emojis. **No llenes de advertencias** ("ojo", "tené cuidado", "es sólo para Pro", "letra chica"):
si una limitación importa, mencionala una vez y con naturalidad; el tono es de entusiasmo informado, no de alerta.

## Por noticia
- `titulo`: ≤ 12 palabras, el hecho, sin clickbait.
- `que_paso`: 2–3 frases con el dato central y quién lo hizo.
- `por_que`: 1–2 frases: qué le cambia a un joven.
- `que_hacer`: una acción concreta y segura (probar algo, mirar algo, cuidar algo). Si no hay, vacío.
- `fuentes`: `[{titulo, url}]` (la primaria primero).
- `tema`, `quien`, `fecha_hecho`.

## Dónde se deja
1. Biblioteca viva (https://claude.ai/artifact/GCfxyLRB5Pfr943DpDyTaU), colección `noticias`, un documento por noticia
   (`ArtifactData` `batch`, `set` sin `if_version` porque son nuevos; id `<AAAA-MM-DD>-<n>`):
   `{semana: "<AAAA-MM-DD>", titulo, que_paso, por_que, que_hacer, fuentes, tema, quien, fecha_hecho, puntaje (1-10), puntaje_max: 10,
   estado: "para_aprobar", creado: <ms>}`. La persona aprueba o descarta desde la pestaña Noticias.
2. Respaldo: `08 Noticias/<fecha> - Noticias IA.md` con todas las noticias y un resumen de la semana de 3 líneas.

Después de aprobar, el formato y el día de la grilla los pone `p18-noticias-formato` (lo corre el preparador).
