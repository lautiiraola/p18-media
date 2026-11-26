"""Genera p18-003-v01.props.json para el runtime P18 Stories (05_REMOTION_DESIGN_SYSTEM/runtime).
Uso (desde la carpeta de la producción):  python3 -I 06_remotion/build_props.py
Reglas aplicadas: 9:16, 30–50 s, cierre outro3d, música rotativa (no cama_p18), tipografía y texto cinético,
imágenes rotativas sin repetir (assert_unique_images) y subtítulos por frase (chunk_captions).
"""
import difflib
import json
import math
import re
import sys
from pathlib import Path

STUDIO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(STUDIO / '05_REMOTION_DESIGN_SYSTEM/runtime/scripts'))
from p18_build import chunk_captions, assert_unique_images, clamp_captions_to_scenes  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FPS = 60
VOICE_DURATION = 38.84
TAIL = 1.0

ref = (ROOT / '02_script/voiceover-final.txt').read_text(encoding='utf-8')
asr = json.loads((ROOT / '03_voiceover/P18-003-steve-jobs-voiceover-words.json').read_text(encoding='utf-8'))['words']
NUM = {'30': 'treinta', '11': 'once'}


def toks(s):
    s = s.lower()
    for k, v in NUM.items():
        s = re.sub(r'(?<![\w-])' + k + r'(?!\w)', v, s)
    return [t.replace('haces', 'hacés') for t in re.findall(r"[a-záéíóúñü]+", s)]


at = []
for w in asr:
    ts = toks(w['text'])
    for i, t in enumerate(ts):
        d = (w['t1'] - w['t0']) / max(len(ts), 1)
        at.append((t, w['t0'] + i * d, w['t0'] + (i + 1) * d))

sentences = [s.strip() for s in re.split(r'(?<=[.?»])\s+', ref.replace('\n', ' ')) if s.strip()]
words = []
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
    idx = [amap[i] for i, (o, _) in enumerate(flat) if o == wi]
    w['t0'] = round(at[idx[0]][1], 3)
    w['t1'] = round(min(at[idx[-1]][2], VOICE_DURATION), 3)

DISPLAY = {'treinta.': '30.', 'Once': '11'}
units = {}
for w in words:
    text = DISPLAY.get(w['text'], w['text']).replace('«', '').replace('»', '')
    u = units.setdefault(w['unit'], {'start': w['t0'], 'end': w['t1'], 'words': []})
    u['end'] = w['t1']
    u['words'].append({'unit': w['unit'], 'text': text, 't0': w['t0'], 't1': w['t1']})
units[1]['start'] = 0.0
U = lambda n: units[n]
assert len(units) == 10, len(units)


def at_word(n, prefix):
    return next(w['t0'] for w in U(n)['words'] if w['text'].startswith(prefix))


# palabra activa por unidad; unidades 1, 9 y 10 se leen como texto de escena (sin subtítulo)
ACTIVE = {2: '30.', 3: 'garaje.', 4: 'afuera.', 5: 'Pixar.', 6: 'pérdidas.', 7: 'buscar', 8: 'plata.'}
HIDE_SUBS = {1, 9, 10}
BREAKS = {4: ['directorio', 'traído,'], 6: [], 7: ['echado', 'salvarse:']}  # cortes editoriales
captions = chunk_captions(units, ACTIVE, HIDE_SUBS, BREAKS)

end_total = VOICE_DURATION + TAIL


def quote_words(n, skip=0):
    ws = [{'text': w['text'], 't0': w['t0']} for w in U(n)['words']][skip:]
    if ws:
        ws[0]['text'] = ws[0]['text'][:1].upper() + ws[0]['text'][1:]
    return ws


def S(n):
    return round(U(n)['start'], 3)


CBY2 = 'CC BY 2.0'
scenes = [
    {'id': 'S01', 't': [0.0, S(2)], 'type': 'quote', 'kicker': 'La pregunta', 'bg': 'deep',
     'attribution': 'Steve Jobs, Stanford, 2005', 'words': quote_words(1), 'underline': ['echar', 'fundaste?']},
    {'id': 'S02', 't': [S(2), S(3)], 'type': 'portrait', 'kicker': '1985', 'src': 'img/A02.jpg',
     'label': 'Steve Jobs, enero de 1984', 'credit': 'Foto: Bernard Gotfryd · dominio público (Library of Congress)'},
    {'id': 'S03', 't': [S(3), S(4)], 'type': 'photo', 'kicker': 'El origen', 'src': 'img/A03.jpg',
     'from': 1.0, 'to': 1.1, 'focusX': 0.5, 'focusY': 0.5, 'label': 'Apple I · 1976',
     'credit': 'Apple I, Smithsonian · Blakespot, CC0'},
    {'id': 'S04', 't': [S(4), S(5)], 'type': 'photo', 'kicker': 'El directorio', 'src': 'img/A05.jpg',
     'from': 1.0, 'to': 1.06, 'focusX': 0.5, 'focusY': 0.06, 'label': 'John Sculley · el CEO que Jobs había traído',
     'credit': 'Sculley en Pepsi, 1979 · B. Gotfryd, dominio público'},
    {'id': 'S05', 't': [S(5), S(6)], 'type': 'photo', 'kicker': 'Afuera', 'src': 'img/A07.jpg',
     'from': 1.0, 'to': 1.1, 'focusX': 0.5, 'focusY': 0.5, 'label': 'NeXT · 1988–1993',
     'credit': 'Computadoras NeXT · stiefkind, CC0'},
    {'id': 'S06', 't': [S(6), S(7)], 'type': 'metric', 'kicker': 'Mientras tanto', 'value': 816,
     'unit': 'millones de dólares', 'note': 'Pérdida de Apple · año fiscal 1996', 'countAt': S(6) + 1.2},
    {'id': 'S07', 't': [S(7), at_word(7, 'compró')], 'type': 'year', 'kicker': 'El giro', 'bg': 'paper', 'year': '1996',
     'caption': 'Once años después'},
    {'id': 'S07b', 't': [at_word(7, 'compró'), S(8)], 'type': 'photo', 'kicker': 'El giro', 'src': 'img/A12.jpg',
     'from': 1.0, 'to': 1.1, 'focusX': 0.5, 'focusY': 0.5, 'label': 'Apple compra NeXT · US$ 429 millones',
     'credit': 'NeXTcube, 1990 · M. Hicks, CC BY 2.0'},
    {'id': 'S08', 't': [S(8), S(9)], 'type': 'fullbleed', 'kicker': 'Ganancia · 1998', 'src': 'img/A09.jpg',
     'focusX': 0.5, 'focusY': 0.5, 'zoom': 1.12, 'credit': 'iMac G3 (1998) · Tokumeigakarinoaoshima, CC0',
     'headline': '+309 millones', 'headlineAt': at_word(8, 'ganar'), 'headlineTop': 300, 'headlineSize': 104},
    {'id': 'S09', 't': [S(9), S(10)], 'type': 'quote', 'kicker': 'Su lectura', 'bg': 'paper',
     'attribution': 'Steve Jobs, Stanford, 2005', 'words': quote_words(9, 2), 'underline': ['lo', 'mejor']},
    {'id': 'S10', 't': [S(10), end_total], 'type': 'question', 'bg': 'paper',
     'words': quote_words(10), 'underline': ['dejan', 'afuera?']},
]

sfx = [
    {'file': 'audio/tick.wav', 'at': 0.05, 'vol': 0.16},
    {'file': 'audio/impacto_suave.wav', 'at': at_word(1, 'echar'), 'vol': 0.16},
    {'file': 'audio/whoosh_corto.wav', 'at': S(2), 'vol': 0.12},
    {'file': 'audio/whoosh_suave.wav', 'at': S(3), 'vol': 0.12},
    {'file': 'audio/golpe_grave.wav', 'at': at_word(4, 'afuera'), 'vol': 0.6},
    {'file': 'audio/pop.wav', 'at': at_word(5, 'NeXT'), 'vol': 0.16},
    {'file': 'audio/pop.wav', 'at': at_word(5, 'Pixar'), 'vol': 0.14},
    {'file': 'audio/tick.wav', 'at': S(6) + 1.2, 'vol': 0.14},
    {'file': 'audio/swell.wav', 'at': round(at_word(7, 'buscar') - 1.45, 3), 'vol': 0.5},
    {'file': 'audio/impacto_suave.wav', 'at': at_word(7, 'buscar'), 'vol': 0.2},
    {'file': 'audio/whoosh_suave.wav', 'at': S(8), 'vol': 0.14},
    {'file': 'audio/pop.wav', 'at': at_word(8, 'ganar'), 'vol': 0.18},
    {'file': 'audio/whoosh_corto.wav', 'at': S(9), 'vol': 0.1},
]
# cama rotativa (regla 2026-11-24): «On the Passing of Time», Kevin MacLeod, CC BY 3.0 (no cama_p18)
music = {'file': 'audio/cama.wav', 'points': [[0, 0.0], [0.6, 0.11], [S(4), 0.11], [at_word(4, 'afuera'), 0.05],
                                              [S(6), 0.06], [S(7), 0.1], [at_word(7, 'buscar'), 0.14], [S(8), 0.13],
                                              [S(9), 0.08], [S(10), 0.05], [end_total, 0.0]]}

# ── CIERRE FIJO P18 (outro3d, 3,0 s)
OUTRO_START, OUTRO_DUR = round(VOICE_DURATION + TAIL, 3), 3.0
scenes[-1]['t'][1] = OUTRO_START
scenes.append({'id': 'OUTRO', 't': [OUTRO_START, OUTRO_START + OUTRO_DUR], 'type': 'outro3d',
               'fromNumber': '11', 'fromLabel': 'años afuera',
               'line': 'Mentalidad emprendedora para los jóvenes.', 'lineAccent': 'los jóvenes', 'handle': '@proyecto18.ar'})
end_total = OUTRO_START + OUTRO_DUR
sfx += [{'file': 'audio/whoosh_suave.wav', 'at': OUTRO_START, 'vol': 0.12}] + \
       [{'file': 'audio/tick.wav', 'at': round(OUTRO_START + 0.12 + k * 0.11, 3), 'vol': 0.11} for k in range(6)] + \
       [{'file': 'audio/pop.wav', 'at': OUTRO_START + 0.78, 'vol': 0.2}]
music['points'] = [p for p in music['points'] if p[0] < OUTRO_START - 0.6] + [[OUTRO_START - 0.5, 0.05], [OUTRO_START + 0.25, 0.12], [OUTRO_START + 2.6, 0.09], [end_total, 0.0]]


# ── IMÁGENES ROTATIVAS: galerías por escena, entradas creativas, sin repetir ninguna imagen
def _scene(sid):
    return next(s for s in scenes if s['id'] == sid)


def G(sid, items):
    sc = _scene(sid)
    t0 = sc['t'][0]
    for it in items:
        it['at'] = round(t0 + it.pop('rel'), 3)
        if 'relUntil' in it:
            it['until'] = round(t0 + it.pop('relUntil'), 3)
    sc.setdefault('gallery', []).extend(items)


def E(sid, enter):
    _scene(sid)['enter'] = enter


G('S01', [dict(src='img/A01.jpg', rel=0.9, x=560, y=930, w=400, h=540, rot=4, enter='drop', fy=0.3, credit='Jobs, 2005 · mylerdude, CC BY 2.0')])
G('S02', [dict(src='img/A14.jpg', rel=0.6, x=640, y=560, w=320, h=420, rot=5, enter='flip', fy=0.35, mono=True, credit='Jobs, anuario 1972 · dominio público')])
E('S03', 'iris')
G('S03', [dict(src='img/A04.jpg', rel=0.7, x=520, y=1000, w=460, h=300, rot=-4, enter='slide', fy=0.2, credit='Aviso del Apple I, 1976 · dominio público')])
E('S04', 'wipe')
G('S04', [dict(src='img/A13.jpg', rel=2.4, x=640, y=1010, w=340, h=330, rot=-5, enter='drop', fy=0.45, credit='Macintosh 128K (1984) · B. Prieur, CC0')])
E('S05', 'flip')
G('S05', [dict(src='img/A08.jpg', rel=at_word(5, 'Pixar') - S(5) - 0.15, x=560, y=1010, w=420, h=300, rot=4, enter='blinds', credit='Pixar, Emeryville (2016) · S. Hahn Darlin, ' + CBY2)])
G('S06', [dict(src='img/A15.jpg', rel=0.4, x=580, y=1000, w=400, h=340, rot=5, enter='zoom', credit='Apple Newton, 1993 · M. Hicks, CC BY 2.0')])
G('S07', [dict(src='img/A16.jpg', rel=0.9, x=500, y=880, w=480, h=360, rot=4, enter='drop', fx=0.3, credit='Jobs, 2007 · JD Lasica, ' + CBY2)])
G('S07b', [dict(src='img/A10.jpg', rel=at_word(7, 'volvió') - at_word(7, 'compró') - 0.05, x=540, y=1000, w=440, h=320, rot=4, enter='iris', fx=0.4, credit='Jobs, 2008 · Tom Coates, ' + CBY2)])
G('S09', [dict(src='img/A11.jpg', rel=0.5, x=620, y=980, w=340, h=360, rot=4, enter='slide', fy=0.2, credit='Jobs, 2010 · Gobierno de Chile, ' + CBY2)])

assert_unique_images(scenes)
clamp_captions_to_scenes(captions, scenes)

props = {'data': {'videoId': 'P18-003', 'fps': FPS, 'durationInFrames': math.ceil(end_total * FPS), 'voice': 'audio/voz.wav',
                  'music': music, 'sfx': sfx, 'captions': captions, 'scenes': scenes, 'footer': 'Historias para actuar'}}
out = ROOT / '06_remotion/p18-003-v01.props.json'
out.write_text(json.dumps(props, ensure_ascii=False, indent=1), encoding='utf-8')
print('ok', out.name, 'frames', props['data']['durationInFrames'], 'escenas', len(scenes), 'subtítulos', len(captions))
for c in captions:
    print(f"  {c['start']:6.2f}-{c['end']:6.2f} " + ''.join((('*' + w['text'] + '*') if w['active'] else w['text']) + (' / ' if w.get('br') else ' ') for w in c['words']))
