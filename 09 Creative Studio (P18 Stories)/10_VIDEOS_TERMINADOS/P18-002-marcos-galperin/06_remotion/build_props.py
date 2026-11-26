"""Genera p18-002.props.json para el runtime P18 Stories (05_REMOTION_DESIGN_SYSTEM/runtime).
Uso (desde la carpeta de la producción):  python3 -I 06_remotion/build_props.py
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
VOICE_DURATION = 46.76
TAIL = 1.0

ref = (ROOT / '02_script/voiceover-final.txt').read_text(encoding='utf-8')
asr = json.loads((ROOT / '03_voiceover/P18-002-marcos-galperin-voiceover-words.json').read_text(encoding='utf-8'))['words']
NUM = {'2007': 'dos mil siete', '99': 'noventa y nueve', '20': 'veinte', '19': 'diecinueve', '7': 'siete'}


def toks(s):
    s = s.lower()
    for k, v in sorted(NUM.items(), key=lambda x: -len(x[0])):
        s = re.sub(r'(?<![\w-])' + k + r'(?!\w)', v, s)
    return [t.replace('aca', 'acá') for t in re.findall(r"[a-záéíóúñü]+", s)]


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

DISPLAY = [(['noventa', 'y', 'nueve,'], '99,'), (['dos', 'mil', 'siete'], '2007'), (['Diecinueve'], '19'), (['veinte'], '20'), (['siete'], '7')]
disp, i = [], 0
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

units = {}
for w in disp:
    u = units.setdefault(w['unit'], {'start': w['t0'], 'end': w['t1'], 'words': []})
    u['end'] = w['t1']
    u['words'].append(w)
units[1]['start'] = 0.0
U = lambda n: units[n]


def at_word(n, prefix):
    return next(w['t0'] for w in U(n)['words'] if w['text'].startswith(prefix))


ACTIVE = {3: 'Stanford', 6: 'cocheras', 7: 'burbuja', 8: 'cerrarla.', 9: 'Casi', 10: '7', 11: 'Nasdaq:'}
HIDE_SUBS = {1, 2, 4, 5, 12, 13}
# subtítulos: cortes por frase (módulo compartido p18_build, regla del operador 2026-11-24)
BREAKS = {3: ["Galperin", "Stanford"]}  # cortes editoriales
captions = chunk_captions(units, ACTIVE, HIDE_SUBS, BREAKS)

end_total = VOICE_DURATION + TAIL
def quote_words(n, skip=0):
    ws = [{'text': w['text'], 't0': w['t0']} for w in U(n)['words']][skip:]
    if ws:
        ws[0]['text'] = ws[0]['text'][:1].upper() + ws[0]['text'][1:]
    return ws

scenes = [
    {'id': 'S01', 't': [0.0, U(3)['start']], 'type': 'people', 'kicker': '1999', 'bg': 'deep',
     'appearAt': 0.05, 'verdictAt': at_word(2, '19'), 'gridTop': 640,
     'headline0': '20 personas', 'headline': '19 de 20 dijeron NO', 'headlineAt': at_word(2, '19'), 'headlineTop': 330, 'headlineSize': 92},
    {'id': 'S03', 't': [U(3)['start'], U(4)['start']], 'type': 'photoThenBrowser', 'kicker': 'La idea',
     'src': 'img/A03.jpg', 'label': 'Stanford, California', 'credit': 'Stanford (foto de 2009) · Steve Jurvetson, CC BY 2.0',
     'switchAt': at_word(3, 'quería'), 'logo': 'img/A13.png', 'url': 'www.mercadolibre.com',
     'browserCaption': 'Un mercado online para América Latina'},
    {'id': 'S04', 't': [U(4)['start'], U(5)['start']], 'type': 'quote', 'kicker': 'El rechazo', 'bg': 'paper',
     'attribution': 'Lo que le decían', 'words': quote_words(4, 2), 'underline': ['vio', 'ni', 'tocó.']},
    {'id': 'S05', 't': [U(5)['start'], U(6)['start']], 'type': 'videoQuote', 'kicker': 'Su respuesta',
     'video': 'video/V02-wef-galperin.mp4', 'label': 'Marcos Galperin',
     'credit': 'World Economic Forum on Latin America, 2017 · CC BY 3.0',
     'words': quote_words(5, 4), 'underline': ['la', 'oportunidad.']},
    {'id': 'S06', 't': [U(6)['start'], U(7)['start']], 'type': 'photo', 'kicker': 'El arranque',
     'src': 'img/A04.jpg', 'from': 1.0, 'to': 1.12, 'focusX': 0.45, 'focusY': 0.5, 'label': 'Buenos Aires · 1999',
     'credit': 'Puerto Madero, mayo de 1999 · dominio público'},
    {'id': 'S07', 't': [U(7)['start'], U(8)['start']], 'type': 'chart', 'kicker': 'La crisis', 'bg': 'paper', 'src': 'img/A05.png',
     'marks': [{'x': 0.50, 'label': '1999 · nace', 'at': U(7)['start'] + 0.2, 'color': '#2F6B3F', 'bottom': True},
               {'x': 0.595, 'label': '2000 · explota', 'at': at_word(7, 'explotó'), 'color': '#C97955'}],
     'credit': 'Índice Nasdaq Composite 1994–2005 · dominio público', 'subY': 1250},
    {'id': 'S08', 't': [U(8)['start'], U(10)['start']], 'type': 'vote', 'kicker': 'La crisis',
     'stopAt': U(9)['start'], 'label': 'Representación gráfica'},
    {'id': 'S10', 't': [U(10)['start'], U(11)['start']], 'type': 'losses', 'kicker': 'El costo',
     'years': [1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006]},
    {'id': 'S11', 't': [U(11)['start'], U(12)['start']], 'type': 'photoThenSlide', 'kicker': 'El resultado',
     'src': 'img/A07.jpg', 'label': 'Nasdaq · 2007', 'credit': 'Nasdaq, Times Square, septiembre de 2007 · Roman Suzuki, CC BY 3.0',
     'switchAt': at_word(11, 'la'), 'slide': 'img/V01-slide-historia.png', 'zoomX': 0.5, 'zoomY': 0.86,
     'slideLabel': 'La historia, contada por Mercado Libre', 'slideCredit': 'Presentación de Galperin en LACNIC, 2012 · CC BY 3.0'},
    {'id': 'S12', 't': [U(12)['start'], U(13)['start']], 'type': 'fullbleed', 'kicker': 'Hoy',
     'src': 'img/A11.jpg', 'focusX': 0.56, 'focusY': 0.62, 'zoom': 1.15, 'credit': 'Camioneta de Mercado Libre, Xalapa (México), 2023 · Koffermejia, CC0',
     'headline': '19 de 20 dijeron que no.', 'headlineAt': U(12)['start'], 'headlineTop': 1040, 'headlineSize': 92},
    {'id': 'S13', 't': [U(13)['start'], end_total], 'type': 'question', 'bg': 'paper',
     'words': quote_words(13), 'underline': ['haciendo', 'caso?']},
]

sfx = [
    {'file': 'audio/tick.wav', 'at': 0.05, 'vol': 0.18},
    {'file': 'audio/impacto_suave.wav', 'at': at_word(2, '19'), 'vol': 0.22},
    {'file': 'audio/whoosh_suave.wav', 'at': U(3)['start'], 'vol': 0.14},
    {'file': 'audio/pop.wav', 'at': at_word(3, 'quería') + 1.3, 'vol': 0.18},
    {'file': 'audio/whoosh_corto.wav', 'at': U(5)['start'], 'vol': 0.12},
    {'file': 'audio/whoosh_suave.wav', 'at': U(7)['start'], 'vol': 0.14},
    {'file': 'audio/riser.wav', 'at': round(U(9)['start'] - 2.8, 3), 'vol': 0.18},
    {'file': 'audio/tick.wav', 'at': U(9)['start'], 'vol': 0.22},
    {'file': 'audio/whoosh_suave.wav', 'at': U(11)['start'], 'vol': 0.16},
    {'file': 'audio/pop.wav', 'at': at_word(11, 'Nasdaq'), 'vol': 0.2},
]
music = {'file': 'audio/cama.wav', 'points': [[0, 0.0], [0.5, 0.1], [U(9)['start'], 0.1], [U(9)['start'] + 0.2, 0.05],
                                              [U(10)['start'], 0.08], [U(11)['start'], 0.12], [U(12)['start'], 0.1],
                                              [U(13)['start'], 0.04], [end_total, 0.0]]}

# ── CIERRE FIJO P18 (outro3d, 3,0 s) — aprobado el 2026-11-24, agregado en la v02
OUTRO_START, OUTRO_DUR = 46.85, 3.0
scenes[-1]['t'][1] = OUTRO_START
scenes.append({'id': 'OUTRO', 't': [OUTRO_START, OUTRO_START + OUTRO_DUR], 'type': 'outro3d',
               'fromNumber': '19', 'fromLabel': 'dijeron que no',
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

_s3 = _scene('S03'); _rel_sw = _s3['switchAt'] - _s3['t'][0] - 0.1
G('S03', [dict(src='img/A01.jpg', rel=1.0, relUntil=_rel_sw, x=600, y=900, w=360, h=430, rot=5, enter='drop', credit='Galperin, 2009 · Edans, CC BY 2.0')])
G('S04', [dict(src='img/V01-slide-comercio.png', rel=1.2, x=100, y=930, w=540, h=394, rot=-4, enter='flip', credit='Comercio electrónico · LACNIC 2012, CC BY 3.0')])
E('S06', 'iris')
G('S08', [dict(src='img/A08.jpg', rel=0.8, x=540, y=990, w=440, h=300, rot=4, enter='zoom', credit='Nasdaq, 2006 · L. Villa del Campo, CC BY 2.0')])
G('S10', [dict(src='img/V01-podio.png', rel=0.5, x=640, y=520, w=340, h=250, rot=-4, enter='blinds', credit='Galperin, LACNIC 2012 · CC BY 3.0')])

assert_unique_images(scenes)
clamp_captions_to_scenes(captions, scenes)

props = {'data': {'videoId': 'P18-002', 'fps': FPS, 'durationInFrames': math.ceil(end_total * FPS), 'voice': 'audio/voz.wav',
                  'music': music, 'sfx': sfx, 'captions': captions, 'scenes': scenes, 'footer': 'Historias para actuar'}}
out = ROOT / '06_remotion/p18-002-v05.props.json'
out.write_text(json.dumps(props, ensure_ascii=False, indent=1), encoding='utf-8')
print('ok', out.name, 'frames', props['data']['durationInFrames'], 'escenas', len(scenes), 'subtítulos', len(captions))
