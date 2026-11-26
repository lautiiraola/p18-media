// Bloques tipográficos: cita sincronizada con la voz, pregunta final y cita que se desarma.
import React from 'react';
import {useVideoConfig} from 'remotion';
import {COLOR, FONT, FONTS, SAFE} from '../tokens/tokens';
import {KWord, springAt} from '../subtitles/Kinetic';
import {prog, rand} from '../utils/time';
import {Tag, Tone, Underlined, fg} from './Brand';

type W = {text: string; t0: number};

// Palabras que aparecen al ritmo de la voz; subrayado lima en un tramo
export const SyncedQuote: React.FC<{
  words: W[];
  t: number;
  tone: Tone;
  underline?: string[];
  size?: number;
  top?: number;
  attribution?: string;
  quoteMarks?: boolean;
  opacity?: number;
}> = ({words, t, tone, underline = [], size = 78, top = 560, attribution, quoteMarks = true, opacity = 1}) => {
  // tramo subrayado: últimas N palabras que coinciden en orden
  const n = underline.length;
  let uStart = -1;
  for (let i = words.length - n; i >= 0; i--) {
    if (underline.every((u, k) => words[i + k]?.text.replace(/[«»]/g, '') === u)) {
      uStart = i;
      break;
    }
  }
  const lastU = uStart >= 0 ? words[uStart + n - 1] : undefined;
  const pU = lastU ? prog(t, lastU.t0, lastU.t0 + 0.45) : 0;
  const {fps} = useVideoConfig();
  const qm = springAt(t, (words[0]?.t0 ?? 0) - 0.25, fps, {damping: 12});
  return (
    <div style={{position: 'absolute', left: SAFE.side, right: SAFE.side, top, opacity}}>
      {attribution ? (
        <Tag text={attribution} tone={tone} style={{marginBottom: 26, opacity: prog(t, words[0]?.t0 - 0.3, words[0]?.t0)}} />
      ) : null}
      <div
        style={{
          fontFamily: FONTS.serif,
          fontStyle: 'italic',
          fontWeight: 400,
          fontSize: size * 1.22,
          lineHeight: 1.0,
          letterSpacing: '-0.01em',
          color: fg(tone),
          textWrap: 'pretty',
        }}
      >
        {quoteMarks ? (
          <span style={{display: 'inline-block', color: COLOR.lime, opacity: Math.min(1, qm * 2), transform: `scale(${0.4 + qm * 0.6}) rotate(${(1 - qm) * -20}deg)`, transformOrigin: '50% 70%'}}>«</span>
        ) : null}
        {words.map((w, i) => {
          const txt = w.text.replace(/[«»]/g, '');
          const isEnd = i === words.length - 1;
          // cada palabra entra con foco (desenfoque + tracking que se cierra) cuando la voz la dice
          const content = <KWord text={txt + (isEnd && quoteMarks ? '»' : '')} t={t} t0={w.t0 - 0.05} fps={fps} motion="focus" />;
          const inU = uStart >= 0 && i >= uStart && i < uStart + n;
          return (
            <React.Fragment key={i}>
              {inU ? <Underlined p={pU}>{content}</Underlined> : content}
              {!isEnd ? ' ' : ''}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};

// La frase se desarma: cada letra gira hacia un punto (el ciclón) y se apaga
export const DissolvingQuote: React.FC<{text: string; t: number; t0: number; t1: number}> = ({text, t, t0, t1}) => {
  const p = prog(t, t0 + 0.6, t1 - 0.2);
  const chars = text.split('');
  return (
    <div style={{position: 'absolute', left: SAFE.side, right: SAFE.side, top: 520}}>
      <div style={{fontFamily: FONTS.serif, fontStyle: 'italic', fontWeight: 400, fontSize: 76, lineHeight: 1.04, letterSpacing: '-0.01em', color: COLOR.white}}>
        {chars.map((c, i) => {
          const r = rand(i + 3);
          const delay = r * 0.5;
          const q = Math.max(0, Math.min(1, (p - delay) / 0.5));
          const ang = r * 720 + q * 540;
          const rad = (1 - q) * 0 + q * (120 + r * 260);
          const dx = Math.cos((ang * Math.PI) / 180) * rad + q * (460 - (i % 28) * 16);
          const dy = Math.sin((ang * Math.PI) / 180) * rad * 0.4 + q * 520;
          return (
            <span
              key={i}
              style={{
                display: 'inline-block',
                whiteSpace: 'pre',
                opacity: 1 - q,
                transform: `translate(${dx}px, ${dy}px) rotate(${q * (r - 0.5) * 360}deg) scale(${1 - q * 0.7})`,
                color: q > 0.05 ? COLOR.muted : COLOR.white,
              }}
            >
              {c}
            </span>
          );
        })}
      </div>
    </div>
  );
};

// Pregunta final sobre papel
export const QuestionClose: React.FC<{words: W[]; t: number; underline: string[]}> = ({words, t, underline}) => {
  const {fps: qfps} = useVideoConfig();
  const idx = words.findIndex((w, i) => underline.every((u, k) => words[i + k]?.text.replace(/[,.]/g, '') === u));
  const last = idx >= 0 ? words[idx + underline.length - 1] : undefined;
  const pU = last ? prog(t, last.t0, last.t0 + 0.45) : 0;
  return (
    <div style={{position: 'absolute', left: SAFE.side, right: SAFE.side, top: 520}}>
      <div style={{fontFamily: FONT, fontWeight: 800, fontSize: 82, lineHeight: 1.06, letterSpacing: '-0.035em', color: COLOR.ink, textWrap: 'pretty'}}>
        {words.map((w, i) => {
          const content = <KWord text={w.text} t={t} t0={w.t0 - 0.05} fps={qfps} motion="rise" />;
          const inU = idx >= 0 && i >= idx && i < idx + underline.length;
          return (
            <React.Fragment key={i}>
              {inU ? <Underlined p={pU} color={COLOR.lime}>{content}</Underlined> : content}
              {i < words.length - 1 ? ' ' : ''}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};
