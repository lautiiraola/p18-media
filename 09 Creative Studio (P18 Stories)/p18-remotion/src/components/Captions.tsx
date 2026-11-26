// Subtítulos P18: texto lima sobre caja oscura translúcida (estilo de los reels), con revelado palabra por palabra.
import React from 'react';
import {interpolate, useCurrentFrame, useVideoConfig, Easing} from 'remotion';
import {COLOR, FONT} from '../brand/tokens';

export type Word = {t0: number; t1: number; text: string; key?: boolean};
export type Chunk = {start: number; end: number; words: Word[]};

export const Captions: React.FC<{chunks: Chunk[]; bottom?: number; fontSize?: number; offset?: number}> = ({
  chunks,
  bottom = 560,
  fontSize = 58,
  offset = 0,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps + offset;
  const chunk = chunks.find((c) => t >= c.start && t < c.end);
  if (!chunk) return null;
  const local = (t - chunk.start) * fps;
  const appear = interpolate(local, [0, 4], [0, 1], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  return (
    <div
      style={{
        position: 'absolute',
        left: 80,
        right: 80,
        bottom,
        display: 'flex',
        justifyContent: 'center',
        pointerEvents: 'none',
      }}
    >
      <div
        style={{
          fontFamily: FONT.text,
          fontWeight: 800,
          fontSize,
          lineHeight: 1.42,
          letterSpacing: '-0.015em',
          textAlign: 'center',
          color: COLOR.lime,
          maxWidth: 900,
          textWrap: 'balance',
          opacity: appear,
          transform: `translateY(${(1 - appear) * 10}px) scale(${0.97 + appear * 0.03})`,
        }}
      >
        {/* la caja oscura abraza cada línea (box-decoration-break: clone) */}
        <span
          style={{
            background: 'rgba(14,25,19,0.82)',
            borderRadius: 12,
            padding: '5px 20px 7px',
            boxDecorationBreak: 'clone',
            WebkitBoxDecorationBreak: 'clone',
          }}
        >
          {chunk.words.map((w, i) => {
            const spoken = t >= w.t0 - 0.02;
            const o = spoken ? 1 : 0.38;
            return (
              <span key={i} style={{opacity: o, color: w.key ? COLOR.white : undefined}}>
                {w.text}
                {i < chunk.words.length - 1 ? ' ' : ''}
              </span>
            );
          })}
        </span>
      </div>
    </div>
  );
};
