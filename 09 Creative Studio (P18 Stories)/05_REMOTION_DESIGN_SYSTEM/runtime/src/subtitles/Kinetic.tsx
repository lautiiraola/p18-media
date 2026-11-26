// Motor de tipografía cinética P18 (regla del operador, 2026-11-24: "los textos tienen que tener movimiento,
// aparecer dinámicamente"). Basado en las referencias: la frase se construye palabra por palabra al ritmo de la voz,
// la palabra clave cambia de jerarquía y cada frase modifica el estado visual. Todo deriva del frame (spring/interpolate).
import React from 'react';
import {interpolate, spring} from 'remotion';
import {COLOR} from '../tokens/tokens';

export type Motion = 'rise' | 'focus' | 'slam' | 'pop' | 'type';

const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};

// Progreso con resorte desde el instante t0 (segundos)
export const springAt = (t: number, t0: number, fps: number, config: {damping?: number; mass?: number; stiffness?: number} = {}) =>
  t < t0 ? 0 : spring({frame: (t - t0) * fps, fps, config: {damping: 14, mass: 0.6, stiffness: 170, ...config}});

// Una palabra que entra con un movimiento según el tipo
export const KWord: React.FC<{
  text: string;
  t: number;
  t0: number;
  fps: number;
  motion: Motion;
  style?: React.CSSProperties;
  index?: number;
}> = ({text, t, t0, fps, motion, style, index = 0}) => {
  // v05 (operador: "los subtítulos a veces se cortan, están raros"): ninguna palabra se recorta con máscaras,
  // ninguna cambia el ancho de la línea mientras entra (sin letterSpacing animado) y todas quedan legibles en ≤ 0,15 s.
  const p = springAt(t, t0, fps, motion === 'slam' ? {damping: 15, stiffness: 260} : motion === 'pop' ? {damping: 11, stiffness: 230} : {damping: 20, stiffness: 220});
  const lin = interpolate(t, [t0, t0 + 0.12], [0, 1], clamp);
  if (motion === 'rise') {
    return (
      <span style={{display: 'inline-block', opacity: lin, filter: `blur(${(1 - lin) * 4}px)`, transform: `translateY(${(1 - p) * 0.38}em)`, ...style}}>
        {text}
      </span>
    );
  }
  if (motion === 'focus') {
    return (
      <span style={{display: 'inline-block', opacity: lin, filter: `blur(${(1 - lin) * 10}px)`, transform: `translateY(${(1 - p) * 0.22}em) scale(${1.06 - p * 0.06})`, transformOrigin: '50% 80%', ...style}}>
        {text}
      </span>
    );
  }
  if (motion === 'slam') {
    return (
      <span
        style={{
          display: 'inline-block',
          opacity: lin,
          transform: `scale(${1 + (1 - p) * 0.32}) rotate(${(1 - p) * (index % 2 ? 3 : -3)}deg)`,
          transformOrigin: '50% 80%',
          ...style,
        }}
      >
        {text}
      </span>
    );
  }
  if (motion === 'pop') {
    return (
      <span style={{display: 'inline-block', opacity: lin, transform: `scale(${0.6 + p * 0.4}) translateY(${(1 - p) * 0.2}em)`, transformOrigin: '50% 80%', ...style}}>
        {text}
      </span>
    );
  }
  // type: aparición letra por letra (mono / documental)
  const n = Math.round(interpolate(t, [t0, t0 + Math.max(0.12, text.length * 0.03)], [0, text.length], clamp));
  return (
    <span style={{display: 'inline-block', ...style}}>
      {text.slice(0, n)}
      <span style={{opacity: 0}}>{text.slice(n)}</span>
    </span>
  );
};

// Resaltador lima que barre detrás de TODA la palabra (la palabra pasa a tinta sobre lima: legible en fondo oscuro y papel)
export const Marker: React.FC<{p: number; children: React.ReactNode; color?: string}> = ({p, children, color = COLOR.lime}) => (
  <span style={{position: 'relative', display: 'inline-block'}}>
    <span
      style={{
        position: 'absolute',
        left: '-0.12em',
        right: '-0.12em',
        top: '0.06em',
        bottom: '0.02em',
        background: color,
        borderRadius: '0.08em',
        transform: `scaleX(${p}) skewX(-6deg)`,
        transformOrigin: 'left center',
        zIndex: 0,
      }}
    />
    <span style={{position: 'relative', zIndex: 1}}>{children}</span>
  </span>
);

// Salida del bloque: solo cuando después hay silencio. Si el siguiente subtítulo entra enseguida, el cambio es
// directo (una salida animada se comía la última palabra).
export const exitStyle = (t: number, end: number, nextStart?: number): React.CSSProperties => {
  if (nextStart !== undefined && nextStart - end < 0.12) return {};
  const e = interpolate(t, [end - 0.14, end], [0, 1], clamp);
  return {opacity: 1 - e, transform: `translateY(${-e * 18}px)`, filter: `blur(${e * 5}px)`};
};

// Texto que entra letra por letra (titulares y cifras)
export const LetterCascade: React.FC<{text: string; t: number; t0: number; fps: number; stagger?: number; style?: React.CSSProperties}> = ({
  text,
  t,
  t0,
  fps,
  stagger = 0.025,
  style,
}) => (
  <span style={style}>
    {text.split('').map((ch, i) => {
      const p = springAt(t, t0 + i * stagger, fps, {damping: 13, stiffness: 190});
      return (
        <span key={i} style={{display: 'inline-block', whiteSpace: 'pre', opacity: Math.min(1, p * 2), transform: `translateY(${(1 - p) * 60}%) scale(${0.85 + p * 0.15})`}}>
          {ch}
        </span>
      );
    })}
  </span>
);
