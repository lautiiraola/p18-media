"""Utilidades compartidas para los build_props.py de cada producción P18.

Reglas del operador (2026-11-24, tras revisar la v04):
  - "Hay imágenes que se repiten. Eso no puede pasar."  -> assert_unique_images()
  - "Los subtítulos hay veces que se cortan, están raros." -> chunk_captions(): cortes por frase, nunca a mitad
    de una construcción; cada subtítulo queda en pantalla hasta que termina su última palabra.

Uso desde una producción:
    import sys; sys.path.insert(0, str(STUDIO / '05_REMOTION_DESIGN_SYSTEM/runtime/scripts'))
    from p18_build import chunk_captions, assert_unique_images
"""
import re

# Palabras que nunca pueden cerrar un subtítulo (dejarían la frase colgando)
NO_END = {
    'a', 'al', 'ante', 'con', 'de', 'del', 'desde', 'durante', 'el', 'en', 'entre', 'hasta', 'la', 'las', 'le', 'les',
    'lo', 'los', 'mi', 'muy', 'ni', 'no', 'o', 'para', 'pero', 'por', 'que', 'se', 'sin', 'su', 'sus', 'tan', 'un',
    'una', 'unas', 'unos', 'y', 'e', 'u', 'como', 'cuando', 'donde', 'porque', 'si', 'sobre', 'tras', 'cada', 'otra',
    'otro', 'esa', 'ese', 'esta', 'este', 'qué', 'más',
    # auxiliares y adverbios que anuncian el verbo que sigue
    'había', 'habían', 'ha', 'han', 'iba', 'iban', 'va', 'van', 'nunca', 'ya', 'siempre', 'casi',
    'es', 'son', 'era', 'eran', 'está', 'están', 'estaba',
}
# Palabras delante de las cuales un corte es natural (empieza una construcción nueva)
GOOD_BEFORE = {'y', 'que', 'pero', 'para', 'porque', 'cuando', 'hasta', 'como', 'donde', 'mientras', 'aunque'}
OK_BEFORE = {'en', 'con', 'sin', 'desde', 'durante'}

_norm = lambda s: re.sub(r'[^\wáéíóúüñ]', '', s.lower())


def _break_cost(words, i):
    """Costo de cortar DESPUÉS de words[i]."""
    w = words[i]['text']
    nxt = words[i + 1]['text'] if i + 1 < len(words) else ''
    if re.search(r'[.?!:;»]$', w):
        return 0
    if w.endswith(','):
        return 1
    if _norm(w) in NO_END:
        return 1000
    if _norm(nxt) in GOOD_BEFORE:
        return 4
    if _norm(nxt) in OK_BEFORE:
        return 8
    return 12


def _forced(ws, after):
    """Cortes editoriales explícitos: lista de palabras (texto exacto) después de las cuales se corta."""
    cuts, i, last = [], 0, 0
    for target in after:
        while i < len(ws) and ws[i]['text'] != target:
            i += 1
        if i >= len(ws):
            raise SystemExit(f'corte forzado: no encuentro "{target}"')
        cuts.append((last, i + 1)); last = i + 1; i += 1
    if last < len(ws):
        cuts.append((last, len(ws)))
    return cuts


def chunk_captions(units, active, hide=(), breaks=None, max_chars=30, hard_chars=38, min_hold=0.45, gap_close=0.5, line_chars=28):
    """units: {n: {'words': [{'text','t0','t1'}, ...]}} (una unidad = una frase de la voz).
    breaks: {n: [palabra, ...]} cortes editoriales que reemplazan al automático en esa unidad ([] = sin cortes).
    Devuelve subtítulos [{'unit','start','end','words':[{'text','t0','active'}]}]."""
    breaks = breaks or {}
    captions = []
    for n, u in sorted(units.items()):
        if n in hide:
            continue
        ws = u['words']
        L = len(ws)
        if n in breaks:
            for i, j in _forced(ws, breaks[n]):
                seg = ws[i:j]
                captions.append({'unit': n, 'start': seg[0]['t0'], 'end': seg[-1]['t1'],
                                 'words': [{'text': w['text'], 't0': w['t0'], 'active': w['text'] == active.get(n)} for w in seg]})
            continue
        # programación dinámica: mejor partición en trozos de <= hard_chars, prefiriendo <= max_chars y cortes naturales
        best = [0.0] + [float('inf')] * L
        prev = [0] * (L + 1)
        for j in range(1, L + 1):
            for i in range(j - 1, -1, -1):
                seg = ws[i:j]
                chars = sum(len(w['text']) for w in seg) + len(seg) - 1
                if chars > hard_chars and len(seg) > 1:
                    break
                cost = best[i] + (_break_cost(ws, j - 1) if j < L else 0)
                cost += 3  # cada subtítulo extra cuesta
                if chars > max_chars:
                    cost += (chars - max_chars) * 2
                if len(seg) == 1 and L > 1:
                    cost += 6  # palabra huérfana
                dur = seg[-1]['t1'] - seg[0]['t0']
                if dur < 0.6:
                    cost += 5
                if cost < best[j]:
                    best[j], prev[j] = cost, i
        cuts, j = [], L
        while j > 0:
            cuts.append((prev[j], j))
            j = prev[j]
        for i, j in reversed(cuts):
            seg = ws[i:j]
            captions.append({'unit': n, 'start': seg[0]['t0'], 'end': seg[-1]['t1'],
                             'words': [{'text': w['text'], 't0': w['t0'], 'active': w['text'] == active.get(n)} for w in seg]})
    # salto de línea por frase: si un subtítulo no entra en una línea, se elige el mejor punto de corte
    for c in captions:
        ws = c['words']
        txt = ' '.join(w['text'] for w in ws)
        if len(txt) <= line_chars or len(ws) < 3:
            continue
        best, bi = None, None
        for i in range(len(ws) - 1):
            a = len(' '.join(w['text'] for w in ws[:i + 1]))
            b = len(' '.join(w['text'] for w in ws[i + 1:]))
            if max(a, b) > line_chars + 6:
                continue
            cost = _break_cost(ws, i) * 3 + abs(a - b) * 0.5
            if best is None or cost < best:
                best, bi = cost, i
        if bi is not None:
            ws[bi]['br'] = True

    # duración: hasta el próximo subtítulo si el hueco es corto; si no, la última palabra queda min_hold más
    for a, b in zip(captions, captions[1:]):
        hold = a['words'][-1]['t0'] + min_hold
        a['end'] = b['start'] if b['start'] - a['end'] < gap_close else max(a['end'] + 0.3, hold)
        a['end'] = min(max(a['end'], hold), b['start'])
    if captions:
        last = captions[-1]
        last['end'] = max(last['end'] + 0.3, last['words'][-1]['t0'] + min_hold)
    return captions


IMG_RE = re.compile(r'\.(jpe?g|png|webp|gif|svg|mp4|webm|mov)$', re.I)


def assert_unique_images(scenes):
    """Ninguna imagen o video puede aparecer dos veces en un mismo video (src, backdrop, gallery, slide, logo...)."""
    seen = {}

    def walk(o, sid, path):
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v, sid, f'{path}.{k}')
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, sid, f'{path}[{i}]')
        elif isinstance(o, str) and IMG_RE.search(o):
            seen.setdefault(o, []).append(f'{sid}{path}')

    for s in scenes:
        walk(s, s['id'], '')
    dup = {k: v for k, v in seen.items() if len(v) > 1}
    if dup:
        raise SystemExit('IMÁGENES REPETIDAS (regla P18: nunca repetir una imagen): ' +
                         '; '.join(f'{k} en {v}' for k, v in dup.items()))
    return sorted(seen)


def clamp_captions_to_scenes(captions, scenes, min_hold=0.35):
    """Un subtítulo no sigue en pantalla cuando cambia la escena (se veía desenfocándose sobre la escena siguiente)."""
    for c in captions:
        sc = next((s for s in scenes if s['t'][0] <= c['start'] < s['t'][1]), None)
        if sc and c['end'] > sc['t'][1] and sc['t'][1] - c['words'][-1]['t0'] >= min_hold:
            c['end'] = round(sc['t'][1], 3)
    return captions
