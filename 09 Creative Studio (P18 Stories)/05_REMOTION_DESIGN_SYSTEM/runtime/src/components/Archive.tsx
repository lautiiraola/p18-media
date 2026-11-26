// Archivo real: fotografía y documento. El movimiento deriva del tiempo; nunca se altera la imagen.
import React from 'react';
import {AbsoluteFill, Img, interpolate, staticFile} from 'remotion';
import {COLOR, SAFE} from '../tokens/tokens';
import {prog, easeInOut} from '../utils/time';
import {SourceCaption, Tag, Tone} from './Brand';
import {Enter, ImageEnter} from './Motion';

type Framing = {scale: number; fx: number; fy: number};

const Framed: React.FC<{src: string; f: Framing; mono?: boolean; fit?: 'cover' | 'contain'; style?: React.CSSProperties}> = ({
  src,
  f,
  mono,
  fit = 'cover',
  style,
}) => (
  <Img
    src={staticFile(src)}
    style={{
      width: '100%',
      height: '100%',
      objectFit: fit,
      objectPosition: `${f.fx * 100}% ${f.fy * 100}%`,
      transform: `scale(${f.scale})`,
      transformOrigin: `${f.fx * 100}% ${f.fy * 100}%`,
      filter: mono ? 'grayscale(1) contrast(1.05)' : undefined,
      ...style,
    }}
  />
);

export const lerpFraming = (a: Framing, b: Framing, p: number): Framing => ({
  scale: a.scale + (b.scale - a.scale) * p,
  fx: a.fx + (b.fx - a.fx) * p,
  fy: a.fy + (b.fy - a.fy) * p,
});

// Foto de archivo en tarjeta sobre su propia versión desenfocada (para material horizontal o de baja resolución)
export const ArchivePhoto: React.FC<{
  src: string;
  t: number;
  t0: number;
  t1: number;
  from: Framing;
  to: Framing;
  credit?: string;
  label?: string;
  mono?: boolean;
  cardTop?: number;
  cardHeight?: number;
  tone?: Tone;
  enter?: Enter;
}> = ({src, t, t0, t1, from, to, credit, label, mono, cardTop = 360, cardHeight = 700, tone = 'deep', enter}) => {
  const p = prog(t, t0, t1, easeInOut);
  const f = lerpFraming(from, to, p);
  const enterStyle = enter;
  const enterP = prog(t, t0, t0 + 0.35);
  const width = 1080 - SAFE.side * 2 + 40;
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{opacity: 0.38}}>
        <Framed src={src} f={{scale: 1.15, fx: from.fx, fy: from.fy}} mono={mono} style={{filter: `blur(46px) saturate(0.7)${mono ? ' grayscale(1)' : ''}`}} />
      </AbsoluteFill>
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(15,29,22,0.55) 0%, rgba(15,29,22,0.15) 40%, rgba(15,29,22,0.75) 100%)'}} />
      {enterStyle ? (
        <ImageEnter t={t} t0={t0} enter={enterStyle} style={{left: (1080 - width) / 2, top: cardTop, width, height: cardHeight}}>
          <div style={{width: '100%', height: '100%', overflow: 'hidden', boxShadow: '0 30px 80px rgba(0,0,0,0.45)'}}>
            <Framed src={src} f={f} mono={mono} />
          </div>
        </ImageEnter>
      ) : (
        <div
          style={{
            position: 'absolute',
            left: (1080 - width) / 2,
            top: cardTop,
            width,
            height: cardHeight,
            overflow: 'hidden',
            boxShadow: '0 30px 80px rgba(0,0,0,0.45)',
            opacity: enterP,
            transform: `translateY(${(1 - enterP) * 24}px)`,
          }}
        >
          <Framed src={src} f={f} mono={mono} />
        </div>
      )}
      {label ? (
        <Tag text={label} tone={tone} style={{position: 'absolute', left: SAFE.side - 20, top: cardTop - 46, color: COLOR.lime, opacity: enterP}} />
      ) : null}
      {credit ? (
        <SourceCaption text={credit} tone={tone} style={{position: 'absolute', left: SAFE.side - 20, right: SAFE.side, top: cardTop + cardHeight + 18, opacity: enterP}} />
      ) : null}
    </AbsoluteFill>
  );
};

// Documento (patente, ficha) sobre papel, con zoom documental
export const DocumentCard: React.FC<{
  src: string;
  t: number;
  t0: number;
  t1: number;
  from: Framing;
  to: Framing;
  credit?: string;
  cardTop?: number;
  cardHeight?: number;
}> = ({src, t, t0, t1, from, to, credit, cardTop = 300, cardHeight = 900}) => {
  const p = prog(t, t0 + 0.15, t1, easeInOut);
  const f = lerpFraming(from, to, p);
  const enter = prog(t, t0, t0 + 0.4);
  const width = 1080 - SAFE.side * 2;
  return (
    <AbsoluteFill>
      <div
        style={{
          position: 'absolute',
          left: SAFE.side,
          top: cardTop,
          width,
          height: cardHeight,
          overflow: 'hidden',
          background: '#FFFFFF',
          boxShadow: '0 18px 50px rgba(23,32,25,0.16)',
          opacity: enter,
          transform: `translateY(${interpolate(enter, [0, 1], [40, 0])}px)`,
        }}
      >
        <Framed src={src} f={f} fit="contain" />
      </div>
      {credit ? (
        <SourceCaption text={credit} tone="paper" style={{position: 'absolute', left: SAFE.side, right: SAFE.side, top: cardTop + cardHeight + 18, opacity: enter}} />
      ) : null}
    </AbsoluteFill>
  );
};
