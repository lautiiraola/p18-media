// Gráficos P18 (lote 2, P18-002): grilla de personas, navegador de época, gráfico real con revelado,
// votación, años de pérdida, video en tarjeta y foto a pantalla completa. Todo deriva del tiempo t.
import React from 'react';
import {AbsoluteFill, Img, OffthreadVideo, staticFile} from 'remotion';
import {COLOR, FONT, FONTS, SAFE} from '../tokens/tokens';
import {easeInOut, prog} from '../utils/time';
import {SourceCaption, Tag, Tone, fg} from './Brand';
import {LetterCascade} from '../subtitles/Kinetic';
import {useVideoConfig} from 'remotion';

// ── Grilla de N personas: aparecen, después "no" se tiñen de clay con NO y "yes" queda en lima
export const PeopleGrid: React.FC<{
  t: number;
  appearAt: number;
  verdictAt: number;
  n?: number;
  yesIndex?: number;
  top?: number;
  focusYes?: number; // tiempo desde el que se enfoca a la persona que dijo que sí
  tone?: Tone;
}> = ({t, appearAt, verdictAt, n = 20, yesIndex = 13, top = 470, focusYes, tone = 'deep'}) => {
  const cols = 5;
  const cell = 176;
  const left = (1080 - cols * cell) / 2;
  const zoom = focusYes ? prog(t, focusYes, focusYes + 0.9, easeInOut) : 0;
  const yx = left + (yesIndex % cols) * cell + cell / 2;
  const yy = top + Math.floor(yesIndex / cols) * cell + cell / 2;
  return (
    <div style={{position: 'absolute', inset: 0, transform: `scale(${1 + zoom * 0.5})`, transformOrigin: `${yx}px ${yy}px`}}>
      <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
        {Array.from({length: n}, (_, i) => {
          const x = left + (i % cols) * cell + cell / 2;
          const y = top + Math.floor(i / cols) * cell + cell / 2;
          const a = prog(t, appearAt + i * 0.035, appearAt + i * 0.035 + 0.2);
          const v = prog(t, verdictAt + (i === yesIndex ? 0.35 : i * 0.03), verdictAt + (i === yesIndex ? 0.6 : i * 0.03 + 0.18));
          const yes = i === yesIndex;
          const base = fg(tone);
          const col = v > 0 ? (yes ? COLOR.lime : COLOR.clay) : base;
          const dim = !yes && zoom > 0 ? 1 - zoom * 0.6 : 1;
          return (
            <g key={i} opacity={a * dim} transform={`translate(${x} ${y + (1 - a) * 20})`}>
              <circle cx={0} cy={-34} r={22} fill={col} />
              <path d="M -38 40 Q -38 -2 0 -2 Q 38 -2 38 40 Z" fill={col} />
              {!yes && v > 0.5 ? (
                <text x={0} y={78} textAnchor="middle" fontFamily={FONT} fontWeight={800} fontSize={26} fill={COLOR.clay} opacity={v}>NO</text>
              ) : null}
              {yes && v > 0.5 ? (
                <text x={0} y={78} textAnchor="middle" fontFamily={FONT} fontWeight={800} fontSize={26} fill={COLOR.lime} opacity={v}>SÍ</text>
              ) : null}
            </g>
          );
        })}
      </svg>
    </div>
  );
};

// ── Navegador de fines de los 90 con un logo
export const BrowserMock: React.FC<{t: number; t0: number; logo: string; url: string; caption?: string}> = ({t, t0, logo, url, caption}) => {
  const a = prog(t, t0, t0 + 0.4);
  const type = Math.floor(prog(t, t0 + 0.2, t0 + 1.4) * url.length);
  return (
    <div style={{position: 'absolute', left: SAFE.side - 10, right: SAFE.side - 10, top: 430, opacity: a, transform: `translateY(${(1 - a) * 30}px)`}}>
      <div style={{background: '#C9CCC4', border: '3px solid #8E928A', boxShadow: '0 24px 60px rgba(0,0,0,0.45)'}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 12, padding: '12px 16px', background: '#9AA0A6'}}>
          {[0, 1, 2].map((k) => (
            <div key={k} style={{width: 18, height: 18, background: '#DADCD7', border: '2px solid #6E726C'}} />
          ))}
          <div style={{flex: 1, marginLeft: 12, background: '#FFFFFF', border: '2px solid #6E726C', padding: '6px 14px', fontFamily: 'Courier New, monospace', fontSize: 26, color: '#111'}}>
            http://{url.slice(0, type)}
            <span style={{opacity: Math.floor(t * 2.5) % 2 ? 1 : 0}}>|</span>
          </div>
        </div>
        <div style={{background: '#FFFFFF', height: 520, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
          <Img src={staticFile(logo)} style={{width: 720, opacity: prog(t, t0 + 1.3, t0 + 1.8)}} />
        </div>
      </div>
      {caption ? <Tag text={caption} tone="deep" style={{marginTop: 18}} /> : null}
    </div>
  );
};

// ── Gráfico real con revelado de izquierda a derecha y marcas de año
export const ChartReveal: React.FC<{
  t: number;
  t0: number;
  t1: number;
  src: string;
  marks: {x: number; label: string; at: number; color?: string; bottom?: boolean}[];
  credit?: string;
}> = ({t, t0, t1, src, marks, credit}) => {
  const p = prog(t, t0 + 0.1, t1 - 0.2, easeInOut);
  const w = 1080 - SAFE.side * 2 + 40;
  const h = (w * 1120) / 2000;
  const top = 560;
  return (
    <>
      <div style={{position: 'absolute', left: (1080 - w) / 2, top, width: w, height: h, background: '#FFFFFF', overflow: 'hidden', boxShadow: '0 18px 50px rgba(23,32,25,0.16)'}}>
        <div style={{position: 'absolute', inset: 0, clipPath: `inset(0 ${(1 - p) * 100}% 0 0)`}}>
          <Img src={staticFile(src)} style={{width: '100%', height: '100%'}} />
        </div>
        {marks.map((m, i) => {
          const a = prog(t, m.at, m.at + 0.25);
          return (
            <div key={i} style={{position: 'absolute', left: `${m.x * 100}%`, top: 0, bottom: 0, width: 4, background: m.color ?? COLOR.clay, opacity: a}}>
              <div style={{position: 'absolute', ...(m.bottom ? {bottom: 70, right: 12} : {top: 16, left: 12}), whiteSpace: 'nowrap', fontFamily: FONT, fontWeight: 800, fontSize: 30, color: m.color ?? COLOR.clay, background: '#FFFFFF', padding: '2px 8px'}}>
                {m.label}
              </div>
            </div>
          );
        })}
      </div>
      {credit ? <SourceCaption text={credit} tone="paper" style={{position: 'absolute', left: SAFE.side - 20, right: SAFE.side, top: top + h + 16}} /> : null}
    </>
  );
};

// ── Votación para cerrar la empresa (representación gráfica): la barra avanza y se frena en "casi"
export const VoteBar: React.FC<{t: number; t0: number; stopAt: number; label?: string}> = ({t, t0, stopAt, label}) => {
  const fill = Math.min(prog(t, t0 + 0.2, stopAt, easeInOut) * 0.9, 0.9);
  const stopped = t >= stopAt;
  const shake = stopped ? Math.sin((t - stopAt) * 40) * Math.max(0, 1 - (t - stopAt) * 3) * 6 : 0;
  return (
    <>
      <div style={{position: 'absolute', left: SAFE.side, right: SAFE.side, top: 560, fontFamily: FONT}}>
        <div style={{fontWeight: 800, fontSize: 28, letterSpacing: '0.16em', color: COLOR.blue}}>VOTACIÓN DE ACCIONISTAS</div>
        <div style={{fontFamily: FONTS.serif, fontStyle: 'italic', fontWeight: 400, fontSize: 112, letterSpacing: '-0.01em', lineHeight: 1, color: COLOR.white, marginTop: 18}}>¿Cerrar la empresa?</div>
        <div style={{marginTop: 50, height: 46, background: 'rgba(251,251,245,0.12)', position: 'relative', transform: `translateX(${shake}px)`}}>
          <div style={{width: `${fill * 100}%`, height: '100%', background: COLOR.clay}} />
          <div style={{position: 'absolute', left: '100%', top: -14, width: 4, height: 74, background: COLOR.white, transform: 'translateX(-2px)'}} />
        </div>
        <div style={{marginTop: 20, display: 'flex', justifyContent: 'space-between', fontWeight: 800, fontSize: 30, color: COLOR.white}}>
          <span style={{color: COLOR.clay}}>CERRAR</span>
          <span style={{opacity: stopped ? 1 : 0, color: COLOR.lime}}>CASI</span>
        </div>
      </div>
      {label ? <Tag text={label} tone="deep" style={{position: 'absolute', left: SAFE.side, top: 1300}} /> : null}
    </>
  );
};

// ── Años de pérdida: barras bajo cero de 1999 a 2006 que llegan al equilibrio
export const LossYears: React.FC<{t: number; t0: number; t1: number; years: number[]}> = ({t, t0, t1, years}) => {
  const n = years.length;
  const zeroY = 900;
  const w = 1080 - SAFE.side * 2;
  const bw = w / n - 18;
  return (
    <>
      <div style={{position: 'absolute', left: SAFE.side, top: 330, fontFamily: FONTS.display, fontWeight: 800, fontSize: 130, letterSpacing: '-0.04em', color: COLOR.clay, opacity: prog(t, t0, t0 + 0.3)}}>
        7 años
      </div>
      <div style={{position: 'absolute', left: SAFE.side, right: SAFE.side, top: zeroY, height: 3, background: 'rgba(251,251,245,0.6)'}} />
      <Tag text="Equilibrio" tone="deep" style={{position: 'absolute', right: SAFE.side, top: zeroY - 36}} />
      <Tag text="Representación gráfica · sin escala" tone="deep" style={{position: 'absolute', left: SAFE.side, top: 1300}} />
      {years.map((y, i) => {
        const a = prog(t, t0 + 0.15 + i * 0.22, t0 + 0.35 + i * 0.22);
        const last = i === n - 1;
        const hgt = last ? 6 : 150 * a; // altura pareja: no hay datos de magnitud por año
        return (
          <div key={y} style={{position: 'absolute', left: SAFE.side + i * (bw + 18), top: zeroY + 6, width: bw}}>
            <div style={{height: hgt, background: last ? COLOR.lime : COLOR.clay, opacity: a}} />
            <div style={{marginTop: 12, fontFamily: FONT, fontWeight: 700, fontSize: 24, color: COLOR.white, opacity: a, textAlign: 'center'}}>{y}</div>
          </div>
        );
      })}
    </>
  );
};

// ── Video de archivo en tarjeta (mudo), con crédito
export const VideoCard: React.FC<{src: string; t: number; t0: number; top?: number; height?: number; credit?: string; label?: string; startFrom?: number}> = ({
  src,
  t,
  t0,
  top = 300,
  height = 560,
  credit,
  label,
  startFrom = 0,
}) => {
  const a = prog(t, t0, t0 + 0.3);
  const w = 1080 - SAFE.side * 2 + 40;
  return (
    <>
      <div style={{position: 'absolute', left: (1080 - w) / 2, top, width: w, height, overflow: 'hidden', opacity: a, boxShadow: '0 30px 80px rgba(0,0,0,0.45)'}}>
        <OffthreadVideo src={staticFile(src)} muted startFrom={startFrom} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
      </div>
      {label ? <Tag text={label} tone="deep" style={{position: 'absolute', left: SAFE.side - 20, top: top - 44, color: COLOR.lime, opacity: a}} /> : null}
      {credit ? <SourceCaption text={credit} tone="deep" style={{position: 'absolute', left: SAFE.side - 20, right: SAFE.side, top: top + height + 14, opacity: a}} /> : null}
    </>
  );
};

// ── Foto a pantalla completa (material vertical de buena resolución)
export const FullBleedPhoto: React.FC<{src: string; t: number; t0: number; t1: number; fx?: number; fy?: number; credit?: string; zoom?: number}> = ({
  src,
  t,
  t0,
  t1,
  fx = 0.5,
  fy = 0.5,
  credit,
  zoom = 1.04,
}) => {
  const p = prog(t, t0, t1, easeInOut);
  return (
    <AbsoluteFill>
      <Img src={staticFile(src)} style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: `${fx * 100}% ${fy * 100}%`, transform: `scale(${zoom + p * 0.06})`, transformOrigin: `${fx * 100}% ${fy * 100}%`}} />
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(15,29,22,0.65) 0%, rgba(15,29,22,0.1) 30%, rgba(15,29,22,0.3) 52%, rgba(15,29,22,0.8) 68%, rgba(15,29,22,0.92) 100%)'}} />
      {/* P18-003: la franja de subtítulos (y ≈ 1390–1560) queda siempre oscura, aunque la foto sea clara */}
      {credit ? <SourceCaption text={credit} tone="deep" style={{position: 'absolute', left: SAFE.side, right: SAFE.side, top: 1320}} /> : null}
    </AbsoluteFill>
  );
};

export const BigLine: React.FC<{t: number; at: number; text: string; top?: number; size?: number; color?: string}> = ({t, at, text, top = 300, size = 96, color = COLOR.white}) => {
  const a = prog(t, at, at + 0.3);
  const {fps} = useVideoConfig();
  return (
    <div style={{position: 'absolute', left: SAFE.side, right: SAFE.side, top, fontFamily: FONTS.display, fontWeight: 700, fontSize: size * 0.86, lineHeight: 1.06, letterSpacing: '-0.035em', color, opacity: a, transform: `translateY(${(1 - a) * 16}px)`, textShadow: '0 4px 30px rgba(0,0,0,0.35)'}}>
      <LetterCascade text={text} t={t} t0={at} fps={fps} stagger={0.018} />
    </div>
  );
};
