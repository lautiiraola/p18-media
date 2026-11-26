// Subtítulo narrativo CINÉTICO con rotación tipográfica P18 (reglas del operador, 2026-11-24).
// Cada palabra entra cuando se dice. Cuatro comportamientos que rotan frase a frase, nunca dos iguales seguidos:
//   editorial · Manrope 700; cada palabra sube desde una máscara; la palabra clave recibe un barrido lima detrás
//   serif     · Instrument Serif itálica; las palabras entran desenfocadas y con tracking abierto; la clave salta en Manrope 800 lima
//   caps      · Manrope 800 en mayúsculas; cada palabra golpea (escala y rotación con rebote); la clave en lima
//   stack     · escalera: la frase chica arriba y la palabra clave sola, gigante, en Unbounded, con pop
// Toda frase sale animada (sube, se desenfoca) y deriva apenas mientras está en pantalla.
import React, {useMemo} from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {COLOR, FONTS, SAFE, SUBTITLE_Y} from '../tokens/tokens';
import {Caption, Scene} from '../types';
import {KWord, Marker, exitStyle, springAt} from './Kinetic';

type Style = 'editorial' | 'serif' | 'caps' | 'stack';
const ROTATION: Style[] = ['editorial', 'serif', 'caps', 'stack', 'serif', 'editorial', 'caps', 'stack'];

const textLen = (c: Caption) => c.words.map((w) => w.text).join(' ').length;
const hasActive = (c: Caption) => c.words.some((w) => w.active);

export const assignStyles = (captions: Caption[]): Style[] => {
  const out: Style[] = [];
  let k = 0;
  captions.forEach((c, i) => {
    const explicit = (c as Caption & {style?: Style}).style;
    if (explicit) {
      out.push(explicit);
      return;
    }
    if (i > 0 && captions[i - 1].unit === c.unit) {
      out.push(out[i - 1] === 'stack' ? 'editorial' : out[i - 1]);
      return;
    }
    let s = ROTATION[k % ROTATION.length];
    k++;
    if (s === 'stack' && (!hasActive(c) || textLen(c) > 40)) s = 'caps';
    if (i > 0 && s === out[i - 1]) {
      s = ROTATION[k % ROTATION.length];
      k++;
      if (s === 'stack' && (!hasActive(c) || textLen(c) > 40)) s = 'editorial';
    }
    out.push(s);
  });
  return out;
};

export const NarrativeSubtitles: React.FC<{captions: Caption[]; scenes: Scene[]}> = ({captions, scenes}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const styles = useMemo(() => assignStyles(captions), [captions]);
  const t = frame / fps;
  const idx = captions.findIndex((c) => t >= c.start - 0.05 && t < c.end);
  if (idx < 0) return null;
  const cap = captions[idx];
  const style = styles[idx];
  const scene = scenes.find((s) => t >= s.t[0] && t < s.t[1]);
  const paper = scene?.bg === 'paper';
  const y = typeof scene?.subY === 'number' ? (scene.subY as number) : SUBTITLE_Y;
  const ink = paper ? COLOR.ink : COLOR.white;
  const accent = paper ? '#2F6B3F' : COLOR.lime;
  const shadow = paper ? 'none' : '0 2px 18px rgba(0,0,0,0.55)';
  const drift = (t - cap.start) * -6; // micro-movimiento continuo
  const wrap: React.CSSProperties = {
    position: 'absolute',
    left: SAFE.side,
    right: SAFE.side,
    top: style === 'stack' ? y - 10 : y,
    display: 'flex',
    justifyContent: style === 'stack' ? 'center' : 'flex-start',
    ...exitStyle(t, cap.end, captions[idx + 1]?.start),
  };
  const words = cap.words;
  // cada palabra entra cuando la voz la dice (con 0,08 s de anticipación para que se lea a tiempo)
  const startOf = (i: number) => words[i].t0 - 0.08;

  if (style === 'stack') {
    // escalera en orden de lectura: lo dicho antes (chico) · la palabra clave (gigante) · lo dicho después (chico)
    const ai = words.findIndex((w) => w.active);
    const key = words[ai];
    const keyText = key.text.replace(/[.,:;]$/, '');
    const keySize = keyText.length <= 6 ? 150 : keyText.length <= 9 ? 118 : 90;
    const smallLine = (from: number, to: number) => (
      <div style={{fontFamily: FONTS.sans, fontWeight: 700, fontSize: 40, lineHeight: 1.2, color: ink}}>
        {words.slice(from, to).map((w, k) => (
          <React.Fragment key={k}>
            <KWord text={w.text} t={t} t0={startOf(from + k)} fps={fps} motion="rise" />
            {from + k < to - 1 ? ' ' : ''}
          </React.Fragment>
        ))}
      </div>
    );
    return (
      <div style={wrap}>
        <div style={{textAlign: 'center', transform: `translateY(${drift}px)`, textShadow: shadow, maxWidth: 916}}>
          {ai > 0 ? smallLine(0, ai) : null}
          <div style={{fontFamily: FONTS.display, fontWeight: 800, fontSize: keySize, lineHeight: 1.04, letterSpacing: '-0.03em', color: accent, margin: '4px 0'}}>
            <KWord text={keyText} t={t} t0={startOf(ai)} fps={fps} motion="pop" />
          </div>
          {ai < words.length - 1 ? smallLine(ai + 1, words.length) : null}
        </div>
      </div>
    );
  }

  const typo: Record<Exclude<Style, 'stack'>, React.CSSProperties> = {
    editorial: {fontFamily: FONTS.sans, fontWeight: 700, fontSize: 56, lineHeight: 1.22, letterSpacing: '-0.015em'},
    serif: {fontFamily: FONTS.serif, fontStyle: 'italic', fontWeight: 400, fontSize: 76, lineHeight: 1.02, letterSpacing: '-0.01em'},
    caps: {fontFamily: FONTS.sans, fontWeight: 800, fontSize: 46, lineHeight: 1.2, letterSpacing: '0.005em', textTransform: 'uppercase'},
  };
  const motion = style === 'editorial' ? 'rise' : style === 'serif' ? 'focus' : 'slam';

  return (
    <div style={wrap}>
      <div style={{...typo[style], color: ink, textShadow: shadow, maxWidth: 916, textWrap: 'balance', transform: `translateY(${drift}px)`}}>
        {words.map((w, i) => {
          // salto de línea elegido por frase en el build (br); si no, espacio normal
          const sep = i < words.length - 1 ? ((w as {br?: boolean}).br ? <br /> : ' ') : '';
          const t0 = startOf(i);
          if (!w.active) {
            return (
              <React.Fragment key={i}>
                <KWord text={w.text} t={t} t0={t0} fps={fps} motion={motion} index={i} />
                {sep}
              </React.Fragment>
            );
          }
          if (style === 'editorial') {
            // resaltador lima detrás de toda la palabra; la palabra pasa a tinta cuando el lima ya la cubre
            const m = springAt(t, t0 + 0.06, fps, {damping: 22, stiffness: 240});
            return (
              <React.Fragment key={i}>
                <span style={{display: 'inline-block', margin: '0 0.14em'}}>
                  <Marker p={m} color={COLOR.lime}>
                    <KWord text={w.text} t={t} t0={t0} fps={fps} motion="rise" style={{color: m > 0.97 ? COLOR.ink : ink, textShadow: m > 0.97 ? 'none' : shadow}} />
                  </Marker>
                </span>
                {sep}
              </React.Fragment>
            );
          }
          if (style === 'serif') {
            return (
              <React.Fragment key={i}>
                <KWord text={w.text} t={t} t0={t0} fps={fps} motion="pop" style={{fontFamily: FONTS.sans, fontStyle: 'normal', fontWeight: 800, fontSize: '0.82em', letterSpacing: '-0.02em', color: accent, margin: '0 0.1em'}} />
                {sep}
              </React.Fragment>
            );
          }
          return (
            <React.Fragment key={i}>
              <KWord text={w.text} t={t} t0={t0} fps={fps} motion="slam" index={i} style={{color: accent, fontSize: '1.12em'}} />
              {sep}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};
