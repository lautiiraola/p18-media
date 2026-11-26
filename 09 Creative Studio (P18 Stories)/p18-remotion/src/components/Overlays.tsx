// Gráficos que se integran sobre el video a pantalla completa
import React from 'react';
import {AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {COLOR, FONT, SAFE} from '../brand/tokens';
import {BrandBackground, CategoryChip, DiagonalStripes, KeywordText, Logo, Outline18, UrlPill} from './Brand';

const ease = Easing.bezier(0.22, 1, 0.36, 1);

// Degradés para legibilidad (arriba: logo / abajo: subtítulos). Suaves, sin "caja".
export const Scrims: React.FC<{top?: number; bottom?: number}> = ({top = 0.55, bottom = 0.6}) => (
  <AbsoluteFill style={{pointerEvents: 'none'}}>
    <div
      style={{
        position: 'absolute', left: 0, right: 0, top: 0, height: 420,
        background: `linear-gradient(180deg, rgba(10,20,15,${top}) 0%, rgba(10,20,15,0) 100%)`,
      }}
    />
    <div
      style={{
        position: 'absolute', left: 0, right: 0, bottom: 0, height: 900,
        background: `linear-gradient(0deg, rgba(10,20,15,${bottom}) 0%, rgba(10,20,15,${bottom * 0.55}) 45%, rgba(10,20,15,0) 100%)`,
      }}
    />
  </AbsoluteFill>
);

// Cabecera permanente: logo P18 + pastilla proyecto18.com (misma ubicación que en los reels)
export const Header: React.FC<{delay?: number}> = ({delay = 0}) => {
  const f = useCurrentFrame();
  const o = interpolate(f - delay, [0, 12], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});
  return (
    <div
      style={{
        position: 'absolute', top: SAFE.top - 30, left: SAFE.side, right: SAFE.side,
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        opacity: o, transform: `translateY(${(1 - o) * -16}px)`,
      }}
    >
      <Logo size={62} />
      <UrlPill />
    </div>
  );
};

// Bloque de titular: chip de categoría + titular en mayúsculas con palabras clave lima + barra lateral lima
export const HeadlineBlock: React.FC<{
  title: string;
  category?: string;
  source?: string;
  start?: number;
  size?: number;
  exitAt?: number;
}> = ({title, category, source, start = 0, size = 76, exitAt}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const lines = title.split('\n');
  const bar = interpolate(f - start, [0, 14], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});
  const out = exitAt === undefined ? 0 : interpolate(f, [exitAt, exitAt + 10], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.cubic)});
  return (
    <div style={{opacity: 1 - out, transform: `translateY(${out * 30}px)`}}>
      {category ? (
        <div
          style={{
            marginBottom: 22,
            opacity: interpolate(f - start, [2, 12], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}),
            transform: `translateX(${interpolate(f - start, [2, 14], [-20, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease})}px)`,
          }}
        >
          <CategoryChip label={category} scale={1.15} />
        </div>
      ) : null}
      <div style={{display: 'flex', gap: 26}}>
        <div style={{width: 8, background: COLOR.lime, borderRadius: 2, transform: `scaleY(${bar})`, transformOrigin: 'top'}} />
        <div>
          {lines.map((line, i) => {
            const p = spring({frame: f - start - 4 - i * 4, fps, config: {damping: 200, mass: 0.6}});
            return (
              <div key={i} style={{overflow: 'hidden', paddingBottom: 4}}>
                <div
                  style={{
                    fontFamily: FONT.text, fontWeight: 800, fontSize: size, lineHeight: 1.04,
                    letterSpacing: '-0.025em', color: COLOR.white, textTransform: 'uppercase',
                    transform: `translateY(${(1 - p) * 110}%)`,
                    textShadow: '0 4px 24px rgba(0,0,0,0.35)',
                  }}
                >
                  <KeywordText text={line} />
                </div>
              </div>
            );
          })}
        </div>
      </div>
      {source ? (
        <div
          style={{
            marginTop: 22, marginLeft: 34, fontFamily: FONT.text, fontWeight: 700, fontSize: 22,
            letterSpacing: '0.08em', textTransform: 'uppercase', color: 'rgba(255,255,255,0.75)',
            opacity: interpolate(f - start, [16, 26], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}),
          }}
        >
          <KeywordText text={source} />
        </div>
      ) : null}
    </div>
  );
};

// Zócalo de nombre (entrevistada / entrevistador)
export const LowerThird: React.FC<{name: string; role: string; dur: number}> = ({name, role, dur}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const inP = spring({frame: f, fps, config: {damping: 200, mass: 0.7}});
  const outP = interpolate(f, [dur - 10, dur], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.cubic)});
  const p = inP * (1 - outP);
  return (
    <div style={{position: 'absolute', left: SAFE.side, top: 1170, display: 'flex', alignItems: 'stretch', gap: 18}}>
      <div style={{width: 7, background: COLOR.lime, borderRadius: 2, transform: `scaleY(${p})`, transformOrigin: 'bottom'}} />
      <div style={{overflow: 'hidden'}}>
        <div style={{transform: `translateX(${(1 - p) * -105}%)`}}>
          <div style={{fontFamily: FONT.text, fontWeight: 800, fontSize: 54, color: COLOR.white, letterSpacing: '-0.02em', lineHeight: 1.05, textShadow: '0 3px 18px rgba(0,0,0,0.45)'}}>
            {name}
          </div>
          <div style={{fontFamily: FONT.text, fontWeight: 700, fontSize: 25, color: COLOR.lime, letterSpacing: '0.08em', textTransform: 'uppercase', marginTop: 6}}>
            {role}
          </div>
        </div>
      </div>
    </div>
  );
};

// Tarjeta de pregunta: estructura la entrevista en capítulos. Se apoya sobre el video oscurecido.
export const QuestionCard: React.FC<{n: number; total: number; text: string; dur: number}> = ({n, total, text, dur}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const dim = interpolate(f, [0, 8, dur - 8, dur], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const p = spring({frame: f - 2, fps, config: {damping: 200, mass: 0.7}});
  const out = interpolate(f, [dur - 9, dur], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.cubic)});
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <AbsoluteFill style={{background: `rgba(12,22,17,${0.55 * dim})`, backdropFilter: `blur(${10 * dim}px)`}} />
      <div style={{position: 'absolute', left: SAFE.side, right: SAFE.right - 30, top: 600, opacity: 1 - out, transform: `translateY(${out * -24}px)`}}>
        <div
          style={{
            fontFamily: FONT.text, fontWeight: 800, fontSize: 26, letterSpacing: '0.14em', color: COLOR.lime,
            marginBottom: 26, opacity: p,
          }}
        >
          PREGUNTA {String(n).padStart(2, '0')} <span style={{color: 'rgba(255,255,255,0.5)'}}>/ {String(total).padStart(2, '0')}</span>
        </div>
        <div style={{display: 'flex', gap: 26}}>
          <div style={{width: 8, background: COLOR.lime, borderRadius: 2, transform: `scaleY(${p})`, transformOrigin: 'top'}} />
          <div
            style={{
              fontFamily: FONT.text, fontWeight: 800, fontSize: text.length > 80 ? 62 : 72, lineHeight: 1.06, letterSpacing: '-0.025em',
              color: COLOR.white, textTransform: 'uppercase', clipPath: `inset(0 ${(1 - p) * 100}% 0 0)`,
              textShadow: '0 4px 24px rgba(0,0,0,0.35)',
            }}
          >
            <KeywordText text={text} />
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Barrido de marca: franjas diagonales lima cruzan la pantalla (transición entre capítulos)
export const BrandWipe: React.FC<{dur?: number}> = ({dur = 16}) => {
  const f = useCurrentFrame();
  const p = interpolate(f, [0, dur], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.65, 0, 0.35, 1)});
  const x = interpolate(p, [0, 1], [-2600, 2600]);
  return (
    <AbsoluteFill style={{pointerEvents: 'none', overflow: 'hidden'}}>
      <div style={{position: 'absolute', left: x, top: -600, width: 1500, height: 3200, transform: 'rotate(-18deg)', display: 'flex', gap: 46}}>
        <div style={{width: 1100, background: COLOR.lime}} />
        <div style={{width: 120, background: COLOR.limeDeep}} />
        <div style={{width: 40, background: COLOR.lime, opacity: 0.8}} />
      </div>
    </AbsoluteFill>
  );
};

// Cierre: placa de marca con el "18" en contorno, franjas y llamada a seguir explorando
export const EndCard: React.FC<{dur: number; line1?: string; line2?: string}> = ({
  dur,
  line1 = 'Hay todo un *mundo*.',
  line2 = 'Exploralo con P18.',
}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const inP = spring({frame: f, fps, config: {damping: 200}});
  const stripes = interpolate(f, [6, 26], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});
  const t1 = spring({frame: f - 8, fps, config: {damping: 200}});
  const t2 = spring({frame: f - 14, fps, config: {damping: 200}});
  const t3 = spring({frame: f - 22, fps, config: {damping: 200}});
  const fadeOut = interpolate(f, [dur - 12, dur], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{opacity: inP * fadeOut}}>
      <BrandBackground />
      <Outline18 size={1250} opacity={0.2} style={{right: -120, top: 560, transform: `translateY(${(1 - inP) * 60}px)`}} />
      <DiagonalStripes progress={stripes} style={{left: 0, bottom: 0}} />
      <div style={{position: 'absolute', left: SAFE.side, top: 640}}>
        <div style={{opacity: t1, transform: `translateY(${(1 - t1) * 30}px)`}}>
          <Logo size={170} />
        </div>
        <div
          style={{
            marginTop: 70, fontFamily: FONT.text, fontWeight: 800, fontSize: 84, lineHeight: 1.04,
            letterSpacing: '-0.03em', color: COLOR.white, opacity: t2, transform: `translateY(${(1 - t2) * 30}px)`,
          }}
        >
          <KeywordText text={line1} underline />
          <br />
          {line2}
        </div>
        <div style={{marginTop: 60, display: 'flex', gap: 18, alignItems: 'center', opacity: t3, transform: `translateY(${(1 - t3) * 20}px)`}}>
          <div style={{fontFamily: FONT.text, fontWeight: 800, fontSize: 36, color: COLOR.lime}}>@proyecto18.ar</div>
          <UrlPill scale={1.1} />
        </div>
      </div>
    </AbsoluteFill>
  );
};
