"""Genera p18-001.props.json para el runtime P18 Stories.

Entradas (todas dentro de esta producción):
  02_script/voiceover-final.txt                    texto canónico
  03_voiceover/P18-001-james-dyson-voiceover-words.json   timings por palabra (whisper)
Salida:
  06_remotion/p18-001-v05.props.json

Uso:  python3 -I 06_remotion/build_props.py   (desde la carpeta de la producción)
"""
import difflib
import json
import math
import re
from pathlib import Path
import sys
STUDIO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(STUDIO / '05_REMOTION_DESIGN_SYSTEM/runtime/scripts'))
from p18_build import chunk_captions, assert_unique_images, clamp_captions_to_scenes  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FPS = 60
VOICE_DURATION = 120.27
TAIL = 1.0  # segundos de cierre después de la última palabra

ref = (ROOT / '02_script/voiceover-final.txt').read_text(encoding='utf-8')
asr = json.loads((ROOT / '03_voiceover/P18-001-james-dyson-voiceover-words.json').read_text(encoding='utf-8'))['words']

NUM = {'5126': 'cinco mil ciento veintiséis', '5127': 'cinco mil ciento veintisiete',
       '1993': 'mil novecientos noventa y tres', '84': 'ochenta y cuatro', '10': 'diez', '70': 'setenta'}


def toks(s):
    s = s.lower().replace('g-force', 'g force').replace('dc-01', 'dc cero uno')
    for k, v in NUM.items():
        s = re.sub(r'(?<![\w-])' + k + r'(?!\w)', v, s)
    return re.findall(r"[a-záéíóúñü]+", s)


# tokens ASR con tiempo
at = []
for w in asr:
    ts = toks(w['text'])
    for i, t in enumerate(ts):
        d = (w['t1'] - w['t0']) / max(len(ts), 1)
        at.append((t, w['t0'] + i * d, w['t0'] + (i + 1) * d))

# palabras canónicas (con puntuación) y sus tokens
sentences = [s.strip() for s in re.split(r'(?<=[.?»])\s+', ref.replace('\n', ' ')) if s.strip()]
words = []  # {unit, text, toks}
for ui, s in enumerate(sentences, start=1):
    for raw in s.split():
        words.append({'unit': ui, 'text': raw, 'toks': toks(raw)})
flat = [(wi, t) for wi, w in enumerate(words) for t in w['toks']]
sm = difflib.SequenceMatcher(a=[t for _, t in flat], b=[x[0] for x in at], autojunk=False)
amap = {}
for blk in sm.get_matching_blocks():
    for k in range(blk.size):
        amap[blk.a + k] = blk.b + k
assert len(amap) == len(flat), f'alineación incompleta {len(amap)}/{len(flat)}'
for wi, w in enumerate(words):
    idx = [amap[i] for i, (owner, _) in enumerate(flat) if owner == wi]
    w['t0'] = round(at[idx[0]][1], 3)
    w['t1'] = round(min(at[idx[-1]][2], VOICE_DURATION), 3)

# formato de visualización en subtítulos
DISPLAY = [
    (['cinco', 'mil', 'ciento', 'veintiséis'], '5.126'),
    (['cinco', 'mil', 'ciento', 'veintisiete,'], '5.127,'),
    (['mil', 'novecientos', 'noventa', 'y', 'tres'], '1993'),
    (['ochenta', 'y', 'cuatro'], '84'),
    (['DC', 'cero', 'uno.'], 'DC01.'),
]
disp = []
i = 0
while i < len(words):
    hit = None
    for seq, rep in DISPLAY:
        if [w['text'] for w in words[i:i + len(seq)]] == seq:
            hit = (len(seq), rep)
            break
    if hit:
        n, rep = hit
        disp.append({'unit': words[i]['unit'], 'text': rep, 't0': words[i]['t0'], 't1': words[i + n - 1]['t1']})
        i += n
    else:
        w = words[i]
        disp.append({'unit': w['unit'], 'text': w['text'].replace('«', '').replace('»', ''), 't0': w['t0'], 't1': w['t1']})
        i += 1

# unidades
units = {}
for w in disp:
    u = units.setdefault(w['unit'], {'n': w['unit'], 'start': w['t0'], 'end': w['t1'], 'words': []})
    u['end'] = w['t1']
    u['words'].append(w)
units[1]['start'] = 0.0

# palabra activa por unidad (storyboard [activa: X])
ACTIVE = {1: 'grandes.', 2: 'años.', 4: 'hora.', 5: 'ciclón.', 8: 'nunca.', 9: 'sí', 10: 'cartón', 11: 'Parecía',
          12: 'grandes.', 14: 'fino.', 16: 'probar.', 19: 'solo', 23: 'deudas', 25: '5.127,', 28: 'no.', 30: 'rosa',
          32: 'él.', 34: 'apellido.', 36: 'cambiar.', 37: 'nada.'}

# subtítulos: trozos de hasta ~34 caracteres por línea, 2 líneas máx.
HIDE_SUBS = {1, 12, 24, 25, 29, 38}
# subtítulos: cortes por frase (módulo compartido p18_build, regla del operador 2026-11-24)
BREAKS = {9: ["casa,"], 13: [], 28: ["fabricantes"], 32: ["Japón", "garantía,"], 36: ["fallido"], 37: ["grandes"]}  # cortes editoriales
captions = chunk_captions(units, ACTIVE, HIDE_SUBS, BREAKS)

U = lambda n: units[n]
def span(a, b):
    return [round(U(a)['start'], 3), round(U(b)['end'], 3)]

end_total = VOICE_DURATION + TAIL

# escenas (tiempos sobre la voz; ver 05_storyboard/audiovisual-script.csv)
scenes = [
    {'id': 'S01', 't': span(1, 1), 'type': 'quote', 'kicker': 'La frase', 'bg': 'deep',
     'words': [{'text': w['text'], 't0': w['t0']} for w in U(1)['words']], 'underline': ['alguna', 'de', 'las', 'grandes.']},
    {'id': 'S02', 't': span(2, 2), 'type': 'portrait', 'kicker': 'La frase', 'src': 'img/A25c.jpg',
     'label': 'James Dyson', 'credit': 'Foto: Dyson ©', 'miniQuote': 'Si existiera una aspiradora mejor, ya la habría inventado alguna de las grandes.'},
    {'id': 'S03', 't': span(3, 3), 'type': 'year', 'kicker': 'El problema', 'bg': 'paper', 'year': '1978', 'caption': 'Inglaterra · fines de los 70'},
    {'id': 'S04', 't': span(4, 4), 'type': 'document', 'kicker': 'El problema', 'bg': 'paper', 'src': 'img/A02.png', 'from': 1.0, 'to': 1.18,
     'focusX': 0.82, 'focusY': 0.75, 'credit': 'Patente US 4.058.344 (Ballbarrow) · dominio público', 'overlay': 'clog'},
    {'id': 'S05', 't': span(5, 5), 'type': 'photo', 'kicker': 'La pista', 'src': 'img/A14.jpg', 'from': 1.05, 'to': 1.22,
     'focusX': 0.62, 'focusY': 0.28, 'panY': [0.55, 0.2], 'credit': 'Ciclón del aserradero Hill Leigh, Bath · Foto: Dyson ©'},
    {'id': 'S06', 't': [U(6)['start'], U(8)['end']], 'type': 'cyclone', 'kicker': 'La pista', 'bg': 'deep',
     'grow': U(7)['start'], 'hours': U(8)['start'], 'label': 'Representación gráfica'},
    {'id': 'S09', 't': span(9, 9), 'type': 'bag', 'kicker': 'El problema', 'bg': 'deep', 'label': 'Representación gráfica'},
    {'id': 'S10', 't': [U(10)['start'], U(11)['end']], 'type': 'cardboard', 'kicker': 'La idea', 'bg': 'deep',
     'freeze': U(11)['start'], 'label': 'Representación gráfica'},
    {'id': 'S12', 't': span(12, 12), 'type': 'quote', 'kicker': 'El rechazo', 'bg': 'paper', 'attribution': 'Sus socios no quisieron saber nada',
     'words': [{'text': ('Si' if w['text'] == 'si' else w['text']), 't0': w['t0']} for w in U(12)['words']][6:], 'underline': ['una', 'de', 'las', 'grandes.']},
    {'id': 'S13', 't': span(13, 13), 'type': 'photo', 'kicker': 'Por su cuenta', 'src': 'img/A17c.jpg', 'from': 1.0, 'to': 1.1,
     'focusX': 0.52, 'focusY': 0.45, 'mono': True, 'credit': 'El taller de la cochera, con un prototipo · Foto: Dyson ©'},
    {'id': 'S14', 't': span(14, 14), 'type': 'microns', 'kicker': 'El obstáculo', 'bg': 'deep', 'label': 'Según Dyson · Representación gráfica'},
    {'id': 'S15', 't': span(15, 15), 'type': 'formulas', 'kicker': 'El obstáculo', 'bg': 'deep'},
    {'id': 'S16', 't': span(16, 16), 'type': 'document', 'kicker': 'El método', 'bg': 'paper', 'src': 'img/A01-p1.png', 'from': 1.0, 'to': 1.9,
     'focusX': 0.3, 'focusY': 0.12, 'credit': 'Patente US 4.373.228 · solicitada en el Reino Unido en 1979 · dominio público'},
    {'id': 'S17', 't': [U(17)['start'], U(21)['end']], 'type': 'method', 'kicker': 'El método', 'bg': 'deep', 'src': 'img/A01-p3.png',
     'beats': [U(17)['start'], U(18)['start'], U(19)['start'], U(20)['start'], U(21)['start']]},
    {'id': 'S22', 't': span(22, 22), 'type': 'photo', 'kicker': 'El costo', 'src': 'img/A16.jpg', 'from': 1.0, 'to': 1.12,
     'focusX': 0.5, 'focusY': 0.42, 'panX': [0.4, 0.55], 'credit': 'Deirdre Dyson, 1977 · Foto: Dyson ©', 'label': 'Deirdre Dyson'},
    {'id': 'S23', 't': span(23, 23), 'type': 'debt', 'kicker': 'El costo', 'bg': 'deep'},
    {'id': 'S24', 't': [U(24)['start'], U(25)['end']], 'type': 'counter', 'kicker': 'El método', 'bg': 'deep',
     'hit': next(w['t0'] for w in U(25)['words'] if w['text'].startswith('5.127'))},
    {'id': 'S26', 't': span(26, 26), 'type': 'document', 'kicker': 'El rechazo', 'bg': 'paper', 'src': 'img/A01-p2.png', 'from': 1.0, 'to': 1.15,
     'focusX': 0.33, 'focusY': 0.45, 'credit': 'Patente US 4.373.228, fig. 1 · dominio público'},
    {'id': 'S27', 't': span(27, 27), 'type': 'field', 'kicker': 'El rechazo', 'bg': 'paper'},
    {'id': 'S28', 't': span(28, 28), 'type': 'rejections', 'kicker': 'El rechazo', 'bg': 'paper', 'label': 'Representación gráfica'},
    {'id': 'S29', 't': span(29, 29), 'type': 'quote', 'kicker': 'El rechazo', 'bg': 'deep', 'worn': True,
     'words': [{'text': w['text'], 't0': U(29)['start']} for w in U(1)['words']], 'caption': 'Otra vez, la misma frase.', 'captionT': U(29)['start']},
    {'id': 'S30', 't': span(30, 30), 'type': 'japan', 'kicker': 'Japón', 'bg': 'deep', 'src': 'img/A19.jpg',
     'photoAt': next(w['t0'] for w in U(30)['words'] if w['text'] == 'aspiradora'),
     'credit': 'Dyson con la G-Force, 1986 · Foto: Dyson ©'},
    {'id': 'S31', 't': span(31, 31), 'type': 'timeline', 'kicker': 'La decisión', 'bg': 'deep'},
    {'id': 'S32', 't': span(32, 32), 'type': 'guarantee', 'kicker': 'La decisión', 'bg': 'deep', 'src': 'img/A22.jpg',
     'cut': next(w['t0'] for w in U(32)['words'] if w['text'] == 'decidió'),
     'credit': 'Primera línea de producción del DC01, Chippenham, 1993 · Foto: Dyson ©'},
    {'id': 'S33', 't': [U(33)['start'], U(34)['end']], 'type': 'photo', 'kicker': 'El resultado', 'src': 'img/A21.jpg', 'from': 1.0, 'to': 1.08,
     'focusX': 0.45, 'focusY': 0.45, 'label': '1993 · DC01', 'credit': 'James Dyson con el DC01, 1993 · Foto: Dyson ©',
     'zoomAt': U(34)['start'], 'zoomTo': {'scale': 2.2, 'focusX': 0.9, 'focusY': 0.45}},
    {'id': 'S35', 't': span(35, 35), 'type': 'metric', 'kicker': 'El resultado', 'bg': 'deep', 'value': 84, 'unit': 'mercados',
     'countAt': next(w['t0'] for w in U(35)['words'] if w['text'] == '84'), 'note': 'Dato oficial de Dyson, consultado en 2026'},
    {'id': 'S36', 't': span(36, 36), 'type': 'grid', 'kicker': 'La pregunta', 'bg': 'deep'},
    {'id': 'S37', 't': span(37, 37), 'type': 'dissolve', 'kicker': 'La pregunta', 'bg': 'deep',
     'text': 'Si existiera una aspiradora mejor, ya la habría inventado alguna de las grandes.'},
    {'id': 'S38', 't': [U(38)['start'], end_total], 'type': 'question', 'bg': 'paper',
     'words': [{'text': w['text'], 't0': w['t0']} for w in U(38)['words']], 'underline': ['sin', 'probar']},
]
# continuidad: cada escena dura hasta el inicio de la siguiente
for a, b in zip(scenes, scenes[1:]):
    a['t'][1] = b['t'][0]
scenes[0]['t'][0] = 0.0

def at_word(n, text):
    return next(w['t0'] for w in U(n)['words'] if w['text'].startswith(text))

sfx = [
    {'file': 'audio/whoosh_suave.wav', 'at': U(5)['start'], 'vol': 0.16},
    {'file': 'audio/whoosh_corto.wav', 'at': U(16)['start'], 'vol': 0.16},
    {'file': 'audio/tick.wav', 'at': U(17)['start'], 'vol': 0.25},
    {'file': 'audio/tick.wav', 'at': U(18)['start'], 'vol': 0.25},
    {'file': 'audio/tick.wav', 'at': U(19)['start'], 'vol': 0.25},
    *[{'file': 'audio/tick.wav', 'at': round(U(24)['start'] + d, 3), 'vol': 0.16} for d in (0.0, 0.7, 1.25, 1.65, 1.95, 2.15)],
    {'file': 'audio/riser.wav', 'at': round(at_word(25, '5.127') - 2.8, 3), 'vol': 0.2},
    {'file': 'audio/pop.wav', 'at': at_word(25, '5.127'), 'vol': 0.22},
    {'file': 'audio/whoosh_corto.wav', 'at': U(28)['start'], 'vol': 0.14},
    {'file': 'audio/whoosh_suave.wav', 'at': U(30)['start'], 'vol': 0.16},
    {'file': 'audio/riser.wav', 'at': round(at_word(32, 'decidió') - 2.8, 3), 'vol': 0.2},
    {'file': 'audio/impacto_suave.wav', 'at': at_word(32, 'él'), 'vol': 0.25},
    {'file': 'audio/pop.wav', 'at': at_word(33, '1993'), 'vol': 0.2},
    {'file': 'audio/pop.wav', 'at': at_word(35, '84'), 'vol': 0.2},
    {'file': 'audio/whoosh_suave.wav', 'at': U(37)['start'], 'vol': 0.1},
]
hit5127 = at_word(25, '5.127')
music = {
    'file': 'audio/cama.wav',
    # (segundo, volumen lineal)
    'points': [[0, 0.0], [0.6, 0.1], [U(11)['start'], 0.1], [U(11)['start'] + 0.3, 0.07], [U(12)['start'], 0.1],
               [U(24)['start'], 0.1], [hit5127 - 0.2, 0.15], [hit5127, 0.0], [hit5127 + 1.0, 0.0], [hit5127 + 1.6, 0.1],
               [U(35)['start'], 0.1], [U(36)['start'], 0.07], [U(38)['start'] - 2.0, 0.06], [U(38)['start'], 0.0]],
}


# ── CIERRE FIJO P18 (outro3d, 3,0 s) — aprobado el 2026-11-24, agregado en la v02
OUTRO_START, OUTRO_DUR = 120.4, 3.0
scenes[-1]['t'][1] = OUTRO_START
scenes.append({'id': 'OUTRO', 't': [OUTRO_START, OUTRO_START + OUTRO_DUR], 'type': 'outro3d',
               'fromNumber': '5127', 'fromLabel': 'prototipos',
               'line': 'Mentalidad emprendedora para los jóvenes.', 'lineAccent': 'los jóvenes', 'handle': '@proyecto18.ar'})
end_total = OUTRO_START + OUTRO_DUR
sfx += [{'file': 'audio/whoosh_suave.wav', 'at': OUTRO_START, 'vol': 0.12}] + \
       [{'file': 'audio/tick.wav', 'at': round(OUTRO_START + 0.12 + k * 0.11, 3), 'vol': 0.11} for k in range(6)] + \
       [{'file': 'audio/pop.wav', 'at': OUTRO_START + 0.78, 'vol': 0.2}]
music['points'] = [p for p in music['points'] if p[0] < OUTRO_START - 0.6] + [[OUTRO_START - 0.5, 0.04], [OUTRO_START + 0.25, 0.12], [OUTRO_START + 2.6, 0.09], [end_total, 0.0]]


# ── IMÁGENES ROTATIVAS (regla del operador, 2026-11-24, v04): más archivo por escena, entradas creativas, sin espacios vacíos
def _scene(sid):
    return next(s for s in scenes if s['id'] == sid)
def G(sid, items):
    sc = _scene(sid); t0 = sc['t'][0]
    for it in items:
        it['at'] = round(t0 + it.pop('rel'), 3)
        if 'relUntil' in it:
            it['until'] = round(t0 + it.pop('relUntil'), 3)
    sc.setdefault('gallery', []).extend(items)
def E(sid, enter):
    _scene(sid)['enter'] = enter

DC = 'Foto: Dyson ©'
G('S01', [dict(src='img/A26.jpg', rel=1.4, x=80, y=880, w=520, h=292, rot=-5, enter='drop', fx=0.82, credit='Aspiradora con bolsa · ' + DC)])
G('S03', [dict(src='img/A30.jpg', rel=0.3, x=470, y=960, w=520, h=370, rot=4, enter='slide', credit='Los Ballbarrow, años 70 · ' + DC)])
E('S05', 'iris')
G('S05', [dict(src='img/A15.jpg', rel=2.0, x=560, y=1010, w=440, h=248, rot=5, enter='drop', credit='Hill Leigh, Bath · ' + DC)])
# S12 sin tarjeta: A26 ya aparece en S01 (regla: nunca repetir una imagen)
E('S13', 'wipe')
G('S13', [dict(src='img/A17b.jpg', rel=0.9, x=560, y=1000, w=430, h=242, rot=-4, enter='slide', credit='La Coach House · ' + DC)])
G('S17', [dict(src='img/A23.jpg', rel=4.0, x=600, y=1140, w=400, h=225, rot=3, enter='blinds', credit='Boceto del ciclón · ' + DC)])
E('S22', 'flip')
_j = _scene('S30'); _rel_photo = _j['photoAt'] - _j['t'][0] - 0.15
G('S30', [dict(src='img/A18.jpg', rel=0.4, relUntil=_rel_photo, x=90, y=620, w=430, h=242, rot=-5, enter='drop', credit='Japón, 1985 · ' + DC),
          dict(src='img/A17.jpg', rel=1.1, relUntil=_rel_photo, x=560, y=900, w=430, h=242, rot=4, enter='zoom', credit='Japón, 1985 · ' + DC)])
_z = _scene('S33'); _rel_zoom = _z['zoomAt'] - _z['t'][0]
G('S33', [dict(src='img/A27.jpg', rel=1.4, relUntil=_rel_zoom, x=560, y=1170, w=400, h=200, rot=4, enter='slide', credit='DC01 · Ilustración: Dyson ©')])
G('S35', [dict(src='img/A25r.jpg', rel=0.5, x=620, y=470, w=360, h=372, rot=3, enter='iris', credit='Hoy · ' + DC)])

assert_unique_images(scenes)
clamp_captions_to_scenes(captions, scenes)

props = {
    'data': {
        'videoId': 'P18-001', 'fps': FPS, 'durationInFrames': math.ceil(end_total * FPS),
        'voice': 'audio/voz.wav', 'music': music, 'sfx': sfx,
        'captions': captions, 'scenes': scenes,
        'footer': 'Historias para actuar',
    }
}
out = ROOT / '06_remotion/p18-001-v05.props.json'
out.write_text(json.dumps(props, ensure_ascii=False, indent=1), encoding='utf-8')
print('ok', out, 'frames', props['data']['durationInFrames'], 'escenas', len(scenes), 'subtítulos', len(captions))
