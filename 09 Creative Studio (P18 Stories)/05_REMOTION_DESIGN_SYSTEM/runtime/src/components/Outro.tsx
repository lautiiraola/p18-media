// P18Outro — cierre fijo de P18 Stories ("El número que se vuelve 18"), 3,0 s sin voz.
// 1) El número clave de la historia (5.127, 19...) gira como un odómetro y cae en 18.
// 2) Aparece la frase institucional: "Los 18 son un punto de quiebre, no un límite."
// 3) Firma: P18 + "Proyecto 18 · talleres gratuitos para jóvenes" + @proyecto18.ar
import React from 'react';
import {AbsoluteFill} from 'remotion';
import {COLOR, FONT, SAFE} from '../tokens/tokens';
import {easeInOut, easeOut, prog} from '../utils/time';
import {Underlined} from './Brand';

const DIGIT_H = 1.0; // em

// Columna de odómetro: pasa por varios dígitos y frena en el final
export const Wheel: React.FC<{from: number; to: number; p: number; spins: number}> = ({from, to, p, spins}) => {
  const total = spins * 10 + ((to - from + 10) % 10);
  const pos = from + total * p;
  const offset = pos % 10;
  return (
    <span style={{display: 'inline-block', height: `${DIGIT_H}em`, overflow: 'hidden', verticalAlign: 'top', position: 'relative', width: '0.62em'}}>
      <span style={{display: 'block', transform: `translateY(${-offset * DIGIT_H}em)`}}>
        {Array.from({length: 11}, (_, k) => (
          <span key={k} style={{display: 'block', height: `${DIGIT_H}em`, lineHeight: `${DIGIT_H}em`, textAlign: 'center'}}>
            {k % 10}
          </span>
        ))}
      </span>
    </span>
  );
};

export const P18Outro: React.FC<{t: number; t0: number; fromNumber: string; fromLabel: string; handle: string; web: string; tagline: string}> = ({
  t,
  t0,
  fromNumber,
  fromLabel,
  handle,
  web,
  tagline,
}) => {
  const enter = prog(t, t0, t0 + 0.25);
  const roll = prog(t, t0 + 0.15, t0 + 0.95, easeInOut);
  const settle = prog(t, t0 + 0.95, t0 + 1.15, easeOut);
  const line = prog(t, t0 + 0.9, t0 + 1.3);
  const under = prog(t, t0 + 1.35, t0 + 1.7);
  const lock = prog(t, t0 + 1.45, t0 + 1.85);

  // El número de origen se alinea a la derecha con "18"; los dígitos sobrantes se van
  const src = fromNumber.replace(/\D/g, '');
  const target = '18';
  const n = Math.max(src.length, target.length);
  const srcP = src.padStart(n, ' ');
  const tgtP = target.padStart(n, ' ');

  return (
    <AbsoluteFill style={{background: COLOR.deep, opacity: enter}}>
      {/* grilla fina de fondo */}
      <AbsoluteFill
        style={{
          opacity: 0.06,
          backgroundImage: `linear-gradient(${COLOR.lime} 1px, transparent 1px), linear-gradient(90deg, ${COLOR.lime} 1px, transparent 1px)`,
          backgroundSize: '90px 90px',
        }}
      />
      {/* etiqueta del número: primero el significado en la historia, después "años" */}
      <div style={{position: 'absolute', left: SAFE.side, top: 300, fontFamily: FONT, fontWeight: 800, fontSize: 30, letterSpacing: '0.16em', textTransform: 'uppercase'}}>
        <span style={{position: 'absolute', whiteSpace: 'nowrap', color: COLOR.clay, opacity: 1 - prog(t, t0 + 0.6, t0 + 0.85)}}>{fromLabel}</span>
        <span style={{position: 'absolute', whiteSpace: 'nowrap', color: COLOR.white, opacity: prog(t, t0 + 0.9, t0 + 1.15)}}>años</span>
      </div>
      {/* odómetro */}
      <div style={{position: 'absolute', left: SAFE.side - 10, top: 350, fontFamily: FONT, fontWeight: 800, fontSize: 330, lineHeight: 1, letterSpacing: '-0.04em', color: COLOR.lime}}>
        {Array.from({length: n}, (_, i) => {
          const a = srcP[i];
          const b = tgtP[i];
          if (b === ' ') {
            // dígito que sobra: sube y desaparece
            return (
              <span key={i} style={{display: 'inline-block', width: (1 - roll) * 0.62 + 'em', overflow: 'hidden', opacity: 1 - roll, transform: `translateY(${-roll * 0.4}em)`}}>
                {a}
              </span>
            );
          }
          const from = a === ' ' ? 0 : Number(a);
          return <Wheel key={i} from={from} to={Number(b)} p={roll} spins={1 + (n - i) % 2} />;
        })}
        <div style={{height: 10, width: `${settle * 100}%`, background: COLOR.lime, marginTop: 18, maxWidth: 420}} />
      </div>

      {/* frase institucional */}
      <div
        style={{
          position: 'absolute',
          left: SAFE.side,
          right: SAFE.side,
          top: 800,
          fontFamily: FONT,
          fontWeight: 700,
          fontSize: 66,
          lineHeight: 1.12,
          letterSpacing: '-0.02em',
          color: COLOR.white,
          opacity: line,
          transform: `translateY(${(1 - line) * 18}px)`,
        }}
      >
        Los 18 son un <Underlined p={under}>punto de quiebre</Underlined>, no un límite.
      </div>

      {/* firma */}
      <div style={{position: 'absolute', left: SAFE.side, right: SAFE.side, top: 1060, opacity: lock, transform: `translateY(${(1 - lock) * 14}px)`}}>
        <div style={{display: 'flex', alignItems: 'baseline', gap: 26}}>
          <span style={{fontFamily: FONT, fontWeight: 800, fontSize: 120, letterSpacing: '-0.03em', color: COLOR.lime, lineHeight: 1}}>P18</span>
          <span style={{fontFamily: FONT, fontWeight: 700, fontSize: 30, letterSpacing: '0.14em', textTransform: 'uppercase', color: COLOR.white, lineHeight: 1.3}}>
            Proyecto 18
            <br />
            <span style={{color: 'rgba(251,251,245,0.75)', fontWeight: 600, letterSpacing: '0.1em'}}>{tagline}</span>
          </span>
        </div>
        {/* sin fondo ni cápsula (regla de firma P18): solo texto con subrayado lima fino */}
        <div style={{marginTop: 44, fontFamily: FONT, lineHeight: 1.25}}>
          <div style={{opacity: prog(t, t0 + 1.7, t0 + 2.0)}}>
            <span style={{fontWeight: 700, fontSize: 26, letterSpacing: '0.14em', textTransform: 'uppercase', color: COLOR.blue, marginRight: 18}}>Seguí las historias</span>
            <span style={{fontWeight: 800, fontSize: 46, color: COLOR.white}}><Underlined p={prog(t, t0 + 1.9, t0 + 2.3)}>{handle}</Underlined></span>
          </div>
          <div style={{marginTop: 18, opacity: prog(t, t0 + 1.9, t0 + 2.2)}}>
            <span style={{fontWeight: 700, fontSize: 26, letterSpacing: '0.14em', textTransform: 'uppercase', color: COLOR.blue, marginRight: 18}}>Conocé los talleres</span>
            <span style={{fontWeight: 800, fontSize: 46, color: COLOR.white}}>{web}</span>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
