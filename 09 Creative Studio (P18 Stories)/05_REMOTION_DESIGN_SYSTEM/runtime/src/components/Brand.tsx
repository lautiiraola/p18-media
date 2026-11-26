// Identidad P18 Stories: fondos, firma sin fondo, etiqueta superior, créditos y rótulos.
import React from 'react';
import {AbsoluteFill} from 'remotion';
import {COLOR, FONT, FONTS, SAFE} from '../tokens/tokens';
import {LetterCascade} from '../subtitles/Kinetic';

export type Tone = 'deep' | 'paper';
export const fg = (tone: Tone) => (tone === 'paper' ? COLOR.ink : COLOR.white);

export const Background: React.FC<{tone: Tone}> = ({tone}) => (
  <AbsoluteFill
    style={{
      background:
        tone === 'paper'
          ? COLOR.paper
          : `radial-gradient(120% 80% at 50% 35%, #1B3127 0%, ${COLOR.deep} 55%, #0F1D16 100%)`,
    }}
  />
);

// Firma P18: tipográfica, sin cápsula ni fondo. Lima sobre oscuro, verde/tinta sobre claro.
export const P18BrandSignature: React.FC<{tone: Tone; tagline?: string; size?: number; style?: React.CSSProperties}> = ({
  tone,
  tagline,
  size = 30,
  style,
}) => (
  <div style={{display: 'flex', alignItems: 'baseline', gap: size * 0.55, ...style}}>
    <span
      style={{
        fontFamily: FONT,
        fontWeight: 800,
        fontSize: size,
        letterSpacing: '-0.02em',
        color: tone === 'paper' ? COLOR.deep : COLOR.lime,
      }}
    >
      P18
    </span>
    {tagline ? (
      <span
        style={{
          fontFamily: FONT,
          fontWeight: 700,
          fontSize: size * 0.62,
          letterSpacing: '0.16em',
          textTransform: 'uppercase',
          color: tone === 'paper' ? 'rgba(23,32,25,0.72)' : 'rgba(251,251,245,0.72)',
        }}
      >
        {tagline}
      </span>
    ) : null}
  </div>
);

// Etiqueta superior: línea lateral lima + texto con tracking amplio
export const Kicker: React.FC<{text: string; tone: Tone; opacity?: number; t?: number; t0?: number; fps?: number}> = ({text, tone, opacity = 1, t, t0, fps}) => (
  <div
    style={{
      position: 'absolute',
      left: SAFE.side,
      top: SAFE.top + 40,
      display: 'flex',
      alignItems: 'center',
      gap: 16,
      opacity,
    }}
  >
    <div style={{width: 5, height: 34, background: tone === 'paper' ? COLOR.deep : COLOR.lime}} />
    <div
      style={{
        fontFamily: FONT,
        fontWeight: 800,
        fontSize: 25,
        letterSpacing: '0.18em',
        textTransform: 'uppercase',
        color: tone === 'paper' ? COLOR.deep : COLOR.lime,
      }}
    >
      {t !== undefined && t0 !== undefined && fps ? <LetterCascade text={text} t={t} t0={t0} fps={fps} stagger={0.02} /> : text}
    </div>
  </div>
);

// Fuente o crédito visible
export const SourceCaption: React.FC<{text: string; tone: Tone; style?: React.CSSProperties}> = ({text, tone, style}) => (
  <div
    style={{
      fontFamily: FONTS.mono,
      fontWeight: 500,
      fontSize: 19,
      lineHeight: 1.4,
      color: tone === 'paper' ? '#3F6E8C' : COLOR.blue,
      ...style,
    }}
  >
    {text}
  </div>
);

// Rótulo de representación gráfica o atribución
export const Tag: React.FC<{text: string; tone: Tone; style?: React.CSSProperties}> = ({text, tone, style}) => (
  <div
    style={{
      fontFamily: FONTS.mono,
      fontWeight: 600,
      fontSize: 19,
      letterSpacing: '0.08em',
      textTransform: 'uppercase',
      color: tone === 'paper' ? '#3F6E8C' : COLOR.blue,
      ...style,
    }}
  >
    {text}
  </div>
);

// Palabra con subrayado lima fino que se dibuja según progreso
export const Underlined: React.FC<{children: React.ReactNode; p: number; color?: string; thickness?: number}> = ({
  children,
  p,
  color = COLOR.lime,
  thickness = 0.085,
}) => (
  <span style={{position: 'relative', display: 'inline-block'}}>
    {children}
    <span
      style={{
        position: 'absolute',
        left: 0,
        bottom: '-0.06em',
        height: `${thickness}em`,
        width: `${p * 100}%`,
        background: color,
      }}
    />
  </span>
);
