---
name: p18-noticias-curador
description: Paso 2 de las noticias de Proyecto 18 (P18). Toma las candidatas del radar, las puntúa con criterio P18, verifica cada dato en su fuente y elige las 3 a 5 que más le sirven a un joven de 17-19. Usala después de p18-noticias-radar o cuando pidan "elegí las noticias de la semana".
---

# p18-noticias-curador (paso 2): elegir y verificar

Entrada: `08 Noticias/<fecha>/candidatas.json`.

## Puntaje (1 a 10; se queda con las de 7 o más)
| Criterio | Máximo | Lo máximo es |
|---|---|---|
| **Impacto joven** | 3 | cambia cómo estudia, trabaja, crea o decide alguien de 17-19 |
| **Confirmada** | 3 | fuente primaria o dos medios serios dicen lo mismo |
| **Novedad** | 2 | pasó esta semana y no es una repetición |
| **Claridad** | 2 | se explica en dos frases sin jerga |

**Fuera siempre**: rumores o `sin_confirmar`; **una sola fuente** que no sea la oficial (sin comunicado de la empresa
y sin un segundo medio serio, no entra, aunque el puntaje dé); cosas disponibles sólo en otro país o sólo pagas, salvo
que el impacto sea muy alto; peleas entre empresas sin impacto real; promesas de plata fácil;
política partidaria; alarmismo ("la IA te va a reemplazar"); contenido para adultos o violento.
Variedad: no más de 2 noticias de la misma empresa.

## Verificación
Abrí la fuente primaria de cada elegida y confirmá el dato central (qué, quién, cuándo, cifras). Si no coincide,
corregilo o descartá la noticia. Anotá el link exacto que lo confirma.

## Salida
`08 Noticias/<fecha>/elegidas.json`: 3 a 5 noticias con `{hecho, quien, fecha, dato_central, fuentes:[{titulo,url}],
puntaje, por_que_entra}`. Una línea por descartada importante con el motivo.
