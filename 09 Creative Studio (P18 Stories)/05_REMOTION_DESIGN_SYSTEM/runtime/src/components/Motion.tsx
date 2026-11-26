// Motor de imágenes rotativas P18 (regla del operador, 2026-11-24): más imágenes por escena, entradas y salidas
// creativas que no se repiten, y tarjetas de archivo que ocupan los espacios vacíos. Todo deriva del tiempo t.
import React from 'react';
import {Img, interpolate, staticFile, useVideoConfig} from 'remotion';
import {COLOR, FONTS} from '../tokens/tokens';
import {springAt} from '../subtitles/Kinetic';

export type Enter = 'iris' | 'wipe' | 'blinds' | 'drop' | 'zoom' | 'slide' | 'flip' | 'rise';
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};

// Contenedor de entrada/salida: recibe la imagen ya armada como hijo (salvo blinds, que necesita src)
export const ImageEnter: React.FC<{
  t: number;
  t0: number;
  t1?: number;
  enter: Enter;
  rot?: number;
  children: React.ReactNode;
  style?: React.CSSProperties;
}> = ({t, t0, t1, enter, rot = 0, children, style}) => {
  const {fps} = useVideoConfig();
  const p = springAt(t, t0, fps, enter === 'drop' ? {damping: 12, stiffness: 140} : {damping: 20, stiffness: 150});
  const lin = interpolate(t, [t0, t0 + 0.45], [0, 1], clamp);
  const out = t1 !== undefined ? interpolate(t, [t1 - 0.22, t1], [0, 1], clamp) : 0;
  let s: React.CSSProperties = {};
  switch (enter) {
    case 'iris':
      s = {clipPath: `circle(${lin * 85}% at 50% 50%)`};
      break;
    case 'wipe':
      s = {clipPath: `polygon(0 0, ${lin * 160}% 0, ${lin * 160 - 40}% 100%, 0 100%)`};
      break;
    case 'drop':
      s = {transform: `translateY(${(1 - p) * -140}%) rotate(${rot + (1 - p) * -18}deg)`, opacity: Math.min(1, lin * 3)};
      break;
    case 'zoom':
      s = {transform: `scale(${1.5 - p * 0.5}) rotate(${rot}deg)`, filter: `blur(${(1 - lin) * 18}px)`, opacity: lin};
      break;
    case 'slide':
      s = {transform: `translateX(${(1 - p) * 120}%) rotate(${rot}deg)`};
      break;
    case 'flip':
      s = {transform: `perspective(1400px) rotateY(${(1 - p) * 88}deg) rotate(${rot}deg)`, opacity: Math.min(1, lin * 2)};
      break;
    case 'rise':
    default:
      s = {transform: `translateY(${(1 - p) * 60}px) rotate(${rot}deg)`, opacity: lin};
  }
  if (out > 0) {
    s = {...s, opacity: (typeof s.opacity === 'number' ? s.opacity : 1) * (1 - out), transform: `${s.transform ?? ''} scale(${1 - out * 0.06})`};
  }
  return <div style={{position: 'absolute', ...style, ...s}}>{children}</div>;
};

// Imagen con Ken Burns lento dentro de su marco
const KenBurns: React.FC<{src: string; t: number; t0: number; dur: number; fx?: number; fy?: number; mono?: boolean}> = ({src, t, t0, dur, fx = 0.5, fy = 0.5, mono}) => {
  const k = interpolate(t, [t0, t0 + Math.max(dur, 1)], [1.04, 1.14], clamp);
  return (
    <Img
      src={staticFile(src)}
      style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: `${fx * 100}% ${fy * 100}%`, transform: `scale(${k})`, transformOrigin: `${fx * 100}% ${fy * 100}%`, filter: mono ? 'grayscale(1) contrast(1.05)' : undefined}}
    />
  );
};

export type GalleryItem = {
  src: string;
  at: number; // entra
  until?: number; // sale (por defecto, fin de escena)
  x: number; // posición del marco (px, lienzo 1080x1920)
  y: number;
  w: number;
  h: number;
  rot?: number;
  enter?: Enter;
  frame?: 'polaroid' | 'bare' | 'film';
  credit?: string;
  fx?: number;
  fy?: number;
  mono?: boolean;
  z?: number;
};

// Persiana: la imagen entra en tiras verticales escalonadas
const Blinds: React.FC<{it: GalleryItem; t: number; strips?: number}> = ({it, t, strips = 5}) => {
  const {fps} = useVideoConfig();
  return (
    <>
      {Array.from({length: strips}, (_, i) => {
        const p = springAt(t, it.at + i * 0.06, fps, {damping: 18, stiffness: 170});
        const l = (i / strips) * 100;
        const r = 100 - ((i + 1) / strips) * 100;
        return (
          <div key={i} style={{position: 'absolute', inset: 0, clipPath: `inset(0 ${r}% 0 ${l}%)`, transform: `translateY(${(1 - p) * (i % 2 ? 100 : -100)}%)`}}>
            <KenBurns src={it.src} t={t} t0={it.at} dur={(it.until ?? it.at + 4) - it.at} fx={it.fx} fy={it.fy} mono={it.mono} />
          </div>
        );
      })}
    </>
  );
};

export const GalleryCard: React.FC<{it: GalleryItem; t: number; sceneEnd: number}> = ({it, t, sceneEnd}) => {
  const until = it.until ?? sceneEnd;
  if (t < it.at - 0.02 || t > until) return null;
  const frame = it.frame ?? 'polaroid';
  const pad = frame === 'polaroid' ? 14 : 0;
  const bottomPad = frame === 'polaroid' ? (it.credit ? 46 : 14) : 0;
  const enter = it.enter ?? 'drop';
  const inner =
    enter === 'blinds' ? (
      <Blinds it={it} t={t} />
    ) : (
      <KenBurns src={it.src} t={t} t0={it.at} dur={until - it.at} fx={it.fx} fy={it.fy} mono={it.mono} />
    );
  return (
    <ImageEnter t={t} t0={it.at} t1={until} enter={enter === 'blinds' ? 'rise' : enter} rot={it.rot ?? 0} style={{left: it.x, top: it.y, width: it.w, height: it.h, zIndex: it.z ?? 1}}>
      <div
        style={{
          width: '100%',
          height: '100%',
          background: frame === 'polaroid' ? '#F5F5EB' : 'transparent',
          padding: `${pad}px ${pad}px ${bottomPad}px ${pad}px`,
          boxSizing: 'border-box',
          boxShadow: '0 26px 60px rgba(0,0,0,0.5)',
          border: frame === 'film' ? `3px solid ${COLOR.lime}` : undefined,
          position: 'relative',
        }}
      >
        <div style={{position: 'relative', width: '100%', height: '100%', overflow: 'hidden'}}>{inner}</div>
        {frame === 'polaroid' && it.credit ? (
          <div style={{position: 'absolute', left: pad, right: pad, bottom: 10, fontFamily: FONTS.mono, fontSize: 15, color: '#3F6E8C', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}}>{it.credit}</div>
        ) : null}
      </div>
    </ImageEnter>
  );
};

export const Gallery: React.FC<{items: GalleryItem[]; t: number; sceneEnd: number}> = ({items, t, sceneEnd}) => (
  <>
    {items.map((it, i) => (
      <GalleryCard key={i} it={it} t={t} sceneEnd={sceneEnd} />
    ))}
  </>
);
