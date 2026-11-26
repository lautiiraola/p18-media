// Clip P18 para Reels: se recorta del VIDEO PRINCIPAL YA EDITADO (mismo color, subtítulos y mezcla)
// y se le suma el titular persistente del formato P18 (titular con *palabras clave* en lima + categoría + fuente).
import React from 'react';
import {AbsoluteFill, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig, Easing} from 'remotion';
import {COLOR, FONT, SAFE} from '../brand/tokens';
import {KeywordText} from '../components/Brand';

export type ClipRange = {ini: number; fin: number}; // segundos del video principal
export type ClipData = {
  n: number;
  source: string; // archivo en public/
  ranges: ClipRange[];
  titulo: string; // con *palabras clave*
  departamento: string;
  area: string;
  fuente: string;
};

export const clipDuration = (c: ClipData, fps: number) =>
  c.ranges.reduce((acc, r) => acc + Math.round((r.fin - r.ini) * fps), 0);

const Piece: React.FC<{src: string; r: ClipRange; dur: number; fadeIn: boolean; fadeOut: boolean}> = ({src, r, dur, fadeIn, fadeOut}) => {
  const {fps} = useVideoConfig();
  return (
    <OffthreadVideo
      src={staticFile(src)}
      startFrom={Math.round(r.ini * fps)}
      style={{width: '100%', height: '100%'}}
      volume={(f) => {
        const a = fadeIn ? interpolate(f, [0, 2], [0, 1], {extrapolateRight: 'clamp'}) : interpolate(f, [0, 1], [0.6, 1], {extrapolateRight: 'clamp'});
        const b = fadeOut ? interpolate(f, [dur - 3, dur], [1, 0], {extrapolateLeft: 'clamp'}) : interpolate(f, [dur - 1, dur], [1, 0.6], {extrapolateLeft: 'clamp'});
        return Math.min(a, b);
      }}
    />
  );
};

// Titular persistente del clip (debajo de la cabecera P18 que ya trae el video principal)
const ClipTitle: React.FC<{c: ClipData}> = ({c}) => {
  const f = useCurrentFrame();
  const bar = interpolate(f, [0, 10], [0.4, 1], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const len = c.titulo.replace(/\*/g, '').length;
  const size = len > 58 ? 56 : len > 42 ? 62 : 68;
  return (
    <div style={{position: 'absolute', left: SAFE.side, right: SAFE.right - 40, top: 232}}>
      <div style={{display: 'flex', gap: 22}}>
        <div style={{width: 8, background: COLOR.lime, borderRadius: 2, transform: `scaleY(${bar})`, transformOrigin: 'top'}} />
        <div
          style={{
            fontFamily: FONT.text, fontWeight: 800, fontSize: size, lineHeight: 1.05, letterSpacing: '-0.025em',
            color: COLOR.white, textTransform: 'uppercase', textShadow: '0 3px 22px rgba(0,0,0,0.55)', textWrap: 'balance',
          }}
        >
          <KeywordText text={c.titulo} />
        </div>
      </div>
      {/* como en los reels: categoría (área en lima) y debajo la fuente, cada una en su renglón */}
      <div
        style={{
          marginTop: 18, marginLeft: 30, fontFamily: FONT.text, fontWeight: 800, fontSize: 23,
          letterSpacing: '0.08em', textTransform: 'uppercase', color: COLOR.lime, textShadow: '0 2px 12px rgba(0,0,0,0.6)',
          whiteSpace: 'nowrap',
        }}
      >
        {c.area}
      </div>
      <div
        style={{
          marginTop: 6, marginLeft: 30, fontFamily: FONT.text, fontWeight: 700, fontSize: 19,
          letterSpacing: '0.08em', textTransform: 'uppercase', color: 'rgba(255,255,255,0.72)', textShadow: '0 2px 12px rgba(0,0,0,0.6)',
          whiteSpace: 'nowrap',
        }}
      >
        Fuente: {c.fuente}
      </div>
    </div>
  );
};

export const Clip: React.FC<{clip: ClipData}> = ({clip}) => {
  const {fps} = useVideoConfig();
  let from = 0;
  return (
    <AbsoluteFill style={{background: '#000'}}>
      {clip.ranges.map((r, i) => {
        const dur = Math.round((r.fin - r.ini) * fps);
        const el = (
          <Sequence key={i} from={from} durationInFrames={dur}>
            <Piece src={clip.source} r={r} dur={dur} fadeIn={i === 0} fadeOut={i === clip.ranges.length - 1} />
          </Sequence>
        );
        from += dur;
        return el;
      })}
      {/* refuerzo del degradé superior para que el titular se lea sobre cualquier fondo */}
      <div
        style={{
          position: 'absolute', left: 0, right: 0, top: 0, height: 760,
          background: 'linear-gradient(180deg, rgba(10,20,15,0.55) 0%, rgba(10,20,15,0.38) 45%, rgba(10,20,15,0) 100%)',
        }}
      />
      <ClipTitle c={clip} />
    </AbsoluteFill>
  );
};
