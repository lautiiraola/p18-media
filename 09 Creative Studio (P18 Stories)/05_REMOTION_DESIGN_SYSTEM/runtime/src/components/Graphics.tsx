// Gráficos explicativos P18: abstractos, rotulados y sin fotorrealismo. Todo deriva del tiempo t.
import React from 'react';
import {COLOR, FONT, FONTS, SAFE} from '../tokens/tokens';
import {prog, rand, easeInOut} from '../utils/time';
import {Tag, Tone, fg} from './Brand';

const svgBox: React.CSSProperties = {position: 'absolute', left: 0, top: 0};

// ── Aspiradora vertical con bolsa (silueta lineal). mode: bag | cone
export const UprightVacuum: React.FC<{
  t: number;
  t0: number;
  mode: 'bag' | 'cone';
  fill?: number; // 0..1 polvo en la bolsa
  coneP?: number; // 0..1 aparición del cono
  spin?: number; // velocidad de giro del polvo en el cono
  opacity?: number;
  x?: number;
  y?: number;
  scale?: number;
}> = ({t, t0, mode, fill = 0, coneP = 0, spin = 1, opacity = 1, x = 540, y = 250, scale = 1}) => {
  const stroke = 'rgba(251,251,245,0.85)';
  const bagOpacity = mode === 'bag' ? 1 : 1 - coneP;
  const dots = Array.from({length: 90}, (_, i) => i);
  return (
    <svg width={1080} height={1920} style={{...svgBox, opacity}} viewBox="0 0 1080 1920">
      <g transform={`translate(${x} ${y}) scale(${scale})`}>
        {/* mango */}
        <line x1={0} y1={0} x2={0} y2={170} stroke={stroke} strokeWidth={6} strokeLinecap="round" />
        <path d="M -38 0 L 38 0" stroke={stroke} strokeWidth={6} strokeLinecap="round" />
        {/* bolsa */}
        <g opacity={bagOpacity}>
          <path d="M -70 170 Q -92 420 -78 700 L 78 700 Q 92 420 70 170 Z" fill="rgba(251,251,245,0.04)" stroke={stroke} strokeWidth={4} />
          {dots.map((i) => {
            const r = rand(i);
            const level = 700 - fill * 470; // altura del polvo
            const yy = 700 - rand(i + 50) * (700 - level);
            const xx = (r - 0.5) * 130 * (0.75 + (yy - 170) / 1060);
            return fill > 0 && yy >= level ? <circle key={i} cx={xx} cy={yy - 4} r={4 + rand(i + 9) * 4} fill={COLOR.muted} opacity={0.75} /> : null;
          })}
        </g>
        {/* cono de cartón */}
        {mode === 'cone' ? (
          <g opacity={coneP}>
            <path d="M -95 190 L 95 190 L 24 640 L -24 640 Z" fill="rgba(201,121,85,0.22)" stroke={COLOR.clay} strokeWidth={5} strokeDasharray={`${coneP * 1400} 1400`} />
            {[0, 1, 2, 3, 4].map((k) => {
              const yy = 230 + k * 85;
              const w = 88 - k * 14;
              const phase = ((t - t0) * 2.2 * spin + k * 0.37) % 1;
              return (
                <ellipse key={k} cx={0} cy={yy} rx={w} ry={10} fill="none" stroke={COLOR.blue} strokeWidth={3} opacity={0.75}
                  strokeDasharray="40 22" strokeDashoffset={-phase * 62 * 3} />
              );
            })}
            {dots.slice(0, 40).map((i) => {
              const life = ((t - t0) * 0.45 * spin + rand(i)) % 1;
              const yy = 210 + life * 430;
              const w = 85 - life * 60;
              const ang = (t - t0) * 6 * spin + i;
              return <circle key={i} cx={Math.cos(ang) * w} cy={yy} r={3.5} fill={COLOR.muted} opacity={0.8 * coneP} />;
            })}
          </g>
        ) : null}
        {/* base y cabezal */}
        <rect x={-110} y={700} width={220} height={90} rx={14} fill="none" stroke={stroke} strokeWidth={5} />
        <rect x={-150} y={790} width={300} height={34} rx={10} fill="none" stroke={stroke} strokeWidth={5} />
      </g>
    </svg>
  );
};

// ── Ciclón: cono con aire que gira y polvo que cae
export const Cyclone: React.FC<{t: number; t0: number; growAt?: number; hoursAt?: number; label?: string}> = ({t, t0, growAt, hoursAt, label}) => {
  const grow = growAt ? prog(t, growAt, growAt + 0.5) : 0;
  const s = 0.86 + grow * 0.14;
  const draw = prog(t, t0, t0 + 0.8);
  const rings = 7;
  const particles = Array.from({length: 70}, (_, i) => i);
  const pile = Math.min(1, (t - t0) / 6);
  const hours = hoursAt ? Math.max(0, Math.floor((t - hoursAt) * 3.2)) : 0;
  return (
    <>
      <svg width={1080} height={1920} style={svgBox} viewBox="0 0 1080 1920">
        {/* centro visual en y=760; el cono mide 820 de alto + 120 de salida arriba */}
        <g transform={`translate(540 760) scale(${s}) translate(0 -380)`}>
          <path d="M -260 0 L 260 0 L 60 820 L -60 820 Z" fill="rgba(142,195,230,0.05)" stroke={COLOR.white} strokeWidth={4}
            strokeDasharray={`${draw * 2400} 2400`} />
          <rect x={-60} y={-120} width={120} height={120} fill="none" stroke={COLOR.white} strokeWidth={4} opacity={draw} />
          {Array.from({length: rings}, (_, k) => {
            const yy = 60 + k * 105;
            const w = 245 - k * 27;
            const phase = ((t - t0) * 1.6 + k * 0.21) % 1;
            return (
              <ellipse key={k} cx={0} cy={yy} rx={w} ry={22} fill="none" stroke={COLOR.blue} strokeWidth={4}
                strokeDasharray="70 40" strokeDashoffset={-phase * 330} opacity={0.85 * draw} />
            );
          })}
          {/* aire limpio sale por arriba */}
          {[0, 1, 2].map((k) => {
            const ph = ((t - t0) * 0.9 + k / 3) % 1;
            return <line key={k} x1={0} y1={-130 - ph * 120} x2={0} y2={-160 - ph * 120} stroke={COLOR.blue} strokeWidth={5} strokeLinecap="round" opacity={(1 - ph) * draw} />;
          })}
          {particles.map((i) => {
            const life = ((t - t0) * 0.32 + rand(i)) % 1;
            const yy = 40 + life * 760;
            const w = 240 - life * 190;
            const ang = (t - t0) * 5 + i * 1.7;
            return <circle key={i} cx={Math.cos(ang) * w} cy={yy} r={4 + rand(i + 3) * 3} fill={COLOR.muted} opacity={0.85 * draw} />;
          })}
          {/* polvo acumulado abajo, fuera del flujo */}
          <rect x={-90} y={830} width={180} height={pile * 60} fill={COLOR.muted} opacity={0.6} />
        </g>
      </svg>
      {hoursAt && t >= hoursAt ? (
        <div style={{position: 'absolute', right: SAFE.side, top: 1240, fontFamily: FONT, fontWeight: 800, fontSize: 46, color: COLOR.blue, letterSpacing: '0.02em'}}>
          {hours} h<span style={{fontSize: 22, fontWeight: 700, letterSpacing: '0.16em', marginLeft: 14}}>SIN TAPARSE</span>
        </div>
      ) : null}
      {label ? <Tag text={label} tone="deep" style={{position: 'absolute', left: SAFE.side, top: 1300}} /> : null}
    </>
  );
};

// ── Filtro que se satura (panel bajo la patente)
export const FilterClog: React.FC<{t: number; t0: number; t1: number; top?: number}> = ({t, t0, t1, top = 950}) => {
  const p = prog(t, t0 + 0.5, t1, easeInOut);
  const cells = Array.from({length: 120}, (_, i) => i);
  return (
    <div style={{position: 'absolute', left: SAFE.side, right: SAFE.side, top}}>
      <Tag text="Filtro de tela" tone="paper" style={{marginBottom: 14}} />
      <svg width={916} height={200} viewBox="0 0 916 200">
        <rect x={1} y={1} width={914} height={198} fill="#FFFFFF" stroke={COLOR.ink} strokeWidth={2} />
        {Array.from({length: 23}, (_, k) => <line key={`v${k}`} x1={k * 40 + 18} y1={0} x2={k * 40 + 18} y2={200} stroke="rgba(23,32,25,0.12)" />)}
        {Array.from({length: 5}, (_, k) => <line key={`h${k}`} x1={0} y1={k * 40 + 20} x2={916} y2={k * 40 + 20} stroke="rgba(23,32,25,0.12)" />)}
        {cells.map((i) => (rand(i) < p ? <circle key={i} cx={10 + rand(i + 1) * 896} cy={10 + rand(i + 2) * 180} r={6 + rand(i + 3) * 9} fill={COLOR.clay} opacity={0.55} /> : null))}
      </svg>
    </div>
  );
};

// ── Escala de micrones
export const Microns: React.FC<{t: number; t0: number; label?: string}> = ({t, t0, label}) => {
  const a = prog(t, t0, t0 + 0.6);
  const b = prog(t, t0 + 1.6, t0 + 2.4);
  return (
    <>
      <svg width={1080} height={1920} style={svgBox} viewBox="0 0 1080 1920">
        <circle cx={400} cy={760} r={250 * a} fill="rgba(142,195,230,0.06)" stroke={COLOR.blue} strokeWidth={5} />
        {Array.from({length: 40}, (_, i) => {
          const x = 140 + ((t - t0) * 160 + rand(i) * 800) % 820;
          const y = 520 + rand(i + 7) * 480;
          return <circle key={i} cx={x} cy={y} r={3.2} fill={COLOR.white} opacity={b} />;
        })}
      </svg>
      <div style={{position: 'absolute', left: 300, top: 1060, opacity: a, fontFamily: FONT}}>
        <div style={{fontFamily: FONTS.mono, fontWeight: 700, fontSize: 60, color: COLOR.blue}}>20 µm</div>
        <div style={{fontWeight: 600, fontSize: 26, color: COLOR.white, opacity: 0.8}}>lo que atrapaba un ciclón</div>
      </div>
      <div style={{position: 'absolute', right: SAFE.side, top: 470, opacity: b, fontFamily: FONT, textAlign: 'right'}}>
        <div style={{fontFamily: FONTS.mono, fontWeight: 700, fontSize: 60, color: COLOR.white}}>{'< 1 µm'}</div>
        <div style={{fontWeight: 600, fontSize: 26, color: COLOR.white, opacity: 0.8}}>polvo de una casa</div>
      </div>
      {label ? <Tag text={label} tone="deep" style={{position: 'absolute', left: SAFE.side, top: 1300}} /> : null}
    </>
  );
};

// ── Cinco fórmulas, cinco resultados
export const Formulas: React.FC<{t: number; t0: number}> = ({t, t0}) => {
  const p = prog(t, t0 + 0.1, t0 + 1.4, easeInOut);
  const ends = [-330, -150, 20, 180, 360];
  return (
    <>
      <svg width={1080} height={1920} style={svgBox} viewBox="0 0 1080 1920">
        {ends.map((dy, k) => (
          <g key={k}>
            <path d={`M 150 760 C 420 760, 520 ${760 + dy * 0.6}, 860 ${760 + dy}`} fill="none" stroke={COLOR.blue} strokeWidth={4}
              strokeDasharray={`${p * 900} 900`} opacity={0.9} />
            <circle cx={860} cy={760 + dy} r={14} fill={COLOR.white} opacity={p > 0.95 ? 1 : 0} />
          </g>
        ))}
        <circle cx={150} cy={760} r={16} fill={COLOR.lime} />
      </svg>
      <div style={{position: 'absolute', left: SAFE.side, top: 1180, fontFamily: FONT, fontWeight: 800, fontSize: 34, color: COLOR.white, letterSpacing: '0.04em', opacity: prog(t, t0 + 0.8, t0 + 1.3)}}>
        5 FÓRMULAS · 5 RESULTADOS
      </div>
    </>
  );
};

// ── Grilla de prototipos (72 columnas). n celdas grises; highlight = índice 1-based en lima
const COLS = 72;
const CELL = 12.7;
export const PrototypeGrid: React.FC<{n: number; highlight?: number; top?: number; scale?: number; opacity?: number}> = ({
  n,
  highlight,
  top = 430,
  scale = 1,
  opacity = 1,
}) => {
  const fullRows = Math.floor(n / COLS);
  const rest = n % COLS;
  const size = COLS * CELL;
  const pattern = `repeating-linear-gradient(90deg, ${COLOR.muted} 0 ${CELL - 3}px, transparent ${CELL - 3}px ${CELL}px)`;
  const hx = highlight ? ((highlight - 1) % COLS) * CELL : 0;
  const hy = highlight ? Math.floor((highlight - 1) / COLS) * CELL : 0;
  return (
    <div style={{position: 'absolute', left: (1080 - size) / 2, top, width: size, height: size, transform: `scale(${scale})`, transformOrigin: '50% 50%', opacity}}>
      <div style={{position: 'absolute', inset: 0, opacity: 0.08, backgroundImage: pattern, WebkitMaskImage: `repeating-linear-gradient(180deg, #000 0 ${CELL - 3}px, transparent ${CELL - 3}px ${CELL}px)`}} />
      <div style={{position: 'absolute', left: 0, top: 0, width: size, height: fullRows * CELL, opacity: 0.55, backgroundImage: pattern, WebkitMaskImage: `repeating-linear-gradient(180deg, #000 0 ${CELL - 3}px, transparent ${CELL - 3}px ${CELL}px)`}} />
      <div style={{position: 'absolute', left: 0, top: fullRows * CELL, width: rest * CELL, height: CELL - 3, opacity: 0.55, backgroundImage: pattern}} />
      {highlight ? <div style={{position: 'absolute', left: hx - 3, top: hy - 3, width: CELL + 3, height: CELL + 3, background: COLOR.lime, boxShadow: `0 0 24px ${COLOR.lime}`}} /> : null}
    </div>
  );
};

// ── Contador 0001 → 5.126 y luego 5.127 en lima
export const Counter: React.FC<{t: number; t0: number; hit: number}> = ({t, t0, hit}) => {
  const p = prog(t, t0 + 0.2, hit - 0.35, (x) => x * x * (3 - 2 * x));
  const n = Math.max(1, Math.round(1 + p * 5125));
  const after = t >= hit;
  const shown = after ? 5127 : n;
  const pop = after ? prog(t, hit, hit + 0.25) : 0;
  return (
    <>
      <PrototypeGrid n={after ? 5126 : n} highlight={after ? 5127 : undefined} top={560} opacity={after ? 0.9 : 1} />
      <div style={{position: 'absolute', left: SAFE.side, top: 250, fontFamily: FONT}}>
        <div style={{fontFamily: FONTS.display, fontWeight: 800, fontSize: 132, lineHeight: 1, letterSpacing: '-0.04em', color: after ? COLOR.lime : COLOR.white, transform: `scale(${1 + pop * 0.04 - pop * pop * 0.04})`, transformOrigin: 'left center'}}>
          {shown.toLocaleString('es-AR')}
        </div>
        <div style={{fontWeight: 700, fontSize: 38, color: COLOR.white, marginTop: 14}}>
          {after ? 'El 5.127, sí.' : 'prototipos que no funcionaron'}
        </div>
        <Tag text="Según James Dyson" tone="deep" style={{marginTop: 16}} />
      </div>
    </>
  );
};

// ── Método: prototipo → medición → un cambio → mejora / empeora
export const Method: React.FC<{t: number; beats: number[]; src: string; Img: React.FC<{src: string}>}> = ({t, beats, Img}) => {
  const [b1, b2, b3, b4, b5] = beats;
  const idx = t >= b5 ? 5 : t >= b4 ? 4 : t >= b3 ? 3 : t >= b2 ? 2 : 1;
  const proto = idx >= 3 ? '0002' : '0001';
  const bar = idx === 1 ? 0 : idx === 2 ? prog(t, b2, b2 + 0.4) * 0.5 : idx === 3 ? 0.5 : idx === 4 ? 0.5 + prog(t, b4, b4 + 0.4) * 0.3 : 0.8 - prog(t, b5, b5 + 0.4) * 0.45;
  const barColor = idx === 4 ? COLOR.lime : idx === 5 ? COLOR.clay : COLOR.blue;
  const enter = prog(t, b1, b1 + 0.25);
  return (
    <>
      <div style={{position: 'absolute', left: SAFE.side, top: 280, width: 916, height: 680, background: '#FFFFFF', overflow: 'hidden', opacity: enter}}>
        <Img src="img/A01-p3.png" />
        {idx >= 3 ? (
          <div style={{position: 'absolute', left: 330, top: 120, width: 250, height: 250, border: `6px solid ${COLOR.lime}`, borderRadius: 125, opacity: prog(t, b3, b3 + 0.25)}} />
        ) : null}
      </div>
      <div style={{position: 'absolute', left: SAFE.side, top: 990, fontFamily: FONT, fontWeight: 800, fontSize: 30, letterSpacing: '0.12em', color: COLOR.white}}>
        PROTOTIPO {proto}
        <span style={{color: COLOR.lime, marginLeft: 24, opacity: idx >= 3 ? 1 : 0}}>· 1 CAMBIO</span>
      </div>
      <div style={{position: 'absolute', left: SAFE.side, top: 1050, width: 916, height: 26, background: 'rgba(251,251,245,0.12)'}}>
        <div style={{width: `${bar * 100}%`, height: '100%', background: barColor}} />
      </div>
      <div style={{position: 'absolute', left: SAFE.side, top: 1090, fontFamily: FONT, fontWeight: 700, fontSize: 22, letterSpacing: '0.16em', color: COLOR.blue, opacity: idx >= 2 ? 1 : 0}}>
        MEDICIÓN · POLVO RETENIDO
      </div>
    </>
  );
};

// ── Línea de deuda (sin cifras)
export const DebtLine: React.FC<{t: number; t0: number; t1: number}> = ({t, t0, t1}) => {
  const p = prog(t, t0, t1);
  const pts = Array.from({length: 30}, (_, i) => {
    const x = 120 + i * 29;
    const y = 1100 - Math.pow(i / 29, 1.6) * 520 - rand(i) * 30;
    return `${x},${y}`;
  }).join(' ');
  return (
    <>
      <svg width={1080} height={1920} style={svgBox} viewBox="0 0 1080 1920">
        <line x1={120} y1={1110} x2={960} y2={1110} stroke="rgba(251,251,245,0.3)" strokeWidth={2} />
        <polyline points={pts} fill="none" stroke={COLOR.clay} strokeWidth={7} strokeLinejoin="round" strokeDasharray={`${p * 1400} 1400`} />
      </svg>
      <Tag text="Deuda · sin escala" tone="deep" style={{position: 'absolute', left: 120, top: 1130}} />
    </>
  );
};

// ── Ficha con casillero vacío
export const EmptyField: React.FC<{t: number; t0: number}> = ({t, t0}) => {
  const a = prog(t, t0, t0 + 0.4);
  const blink = Math.floor((t - t0) * 2.4) % 2 === 0;
  const row = (k: string, v: React.ReactNode, d: number) => (
    <div style={{display: 'flex', gap: 30, alignItems: 'baseline', borderBottom: `2px solid ${COLOR.ink}`, padding: '26px 0', opacity: prog(t, t0 + d, t0 + d + 0.3)}}>
      <div style={{width: 340, fontWeight: 800, fontSize: 28, letterSpacing: '0.14em', color: '#3F6E8C'}}>{k}</div>
      <div style={{fontWeight: 700, fontSize: 46, color: COLOR.ink}}>{v}</div>
    </div>
  );
  return (
    <div style={{position: 'absolute', left: SAFE.side, right: SAFE.side, top: 520, fontFamily: FONT, opacity: a}}>
      {row('MÁQUINA', 'Funciona', 0)}
      {row('PATENTE', 'Registrada', 0.15)}
      {row('FABRICANTE', <span style={{display: 'inline-block', width: 26, height: 52, background: blink ? COLOR.ink : 'transparent', verticalAlign: 'middle'}} />, 0.3)}
    </div>
  );
};

// ── Tarjetas de rechazo (representación gráfica, sin marcas)
export const Rejections: React.FC<{t: number; t0: number; label?: string}> = ({t, t0, label}) => (
  <>
    {[0, 1, 2].map((k) => {
      const p = prog(t, t0 + k * 0.45, t0 + k * 0.45 + 0.35);
      const rot = (k - 1) * 4;
      return (
        <div key={k} style={{position: 'absolute', left: 180 + k * 30, top: 480 + k * 60, width: 660, height: 440, background: '#FFFFFF', border: `3px solid ${COLOR.ink}`,
          transform: `translateY(${(1 - p) * -140}px) rotate(${rot}deg)`, opacity: p, boxShadow: '0 14px 40px rgba(23,32,25,0.15)', fontFamily: FONT, padding: 40, boxSizing: 'border-box'}}>
          <div style={{fontWeight: 800, fontSize: 26, letterSpacing: '0.16em', color: '#3F6E8C'}}>PROPUESTA DE LICENCIA</div>
          <div style={{height: 10, width: 420, background: 'rgba(23,32,25,0.12)', marginTop: 34}} />
          <div style={{height: 10, width: 360, background: 'rgba(23,32,25,0.12)', marginTop: 18}} />
          <div style={{height: 10, width: 400, background: 'rgba(23,32,25,0.12)', marginTop: 18}} />
          <div style={{position: 'absolute', right: 44, bottom: 30, fontWeight: 800, fontSize: 120, color: COLOR.clay, letterSpacing: '-0.03em'}}>NO</div>
        </div>
      );
    })}
    {label ? <Tag text={label} tone="paper" style={{position: 'absolute', left: SAFE.side, top: 1240}} /> : null}
  </>
);

// ── Recorrido Reino Unido → Japón (abstracto)
export const RouteJapan: React.FC<{t: number; t0: number}> = ({t, t0}) => {
  const p = prog(t, t0 + 0.2, t0 + 1.6, easeInOut);
  return (
    <>
      <svg width={1080} height={1920} style={svgBox} viewBox="0 0 1080 1920">
        <path d="M 200 380 C 420 240, 760 260, 880 470" fill="none" stroke={COLOR.lime} strokeWidth={5} strokeDasharray="14 14" strokeDashoffset={0}
          style={{clipPath: `inset(0 ${(1 - p) * 100}% 0 0)`}} />
        <circle cx={200} cy={380} r={14} fill={COLOR.white} />
        <circle cx={880} cy={470} r={14 * p} fill={COLOR.lime} />
      </svg>
      <div style={{position: 'absolute', left: 130, top: 420, fontFamily: FONT, fontWeight: 800, fontSize: 26, letterSpacing: '0.14em', color: COLOR.white}}>REINO UNIDO</div>
      <div style={{position: 'absolute', right: 110, top: 510, fontFamily: FONT, fontWeight: 800, fontSize: 26, letterSpacing: '0.14em', color: COLOR.lime, opacity: p}}>JAPÓN · 1986</div>
    </>
  );
};

// ── Línea de tiempo 1978 → diez años
export const TimelineTen: React.FC<{t: number; t0: number}> = ({t, t0}) => {
  const p = prog(t, t0 + 0.2, t0 + 2.2, easeInOut);
  const x0 = 140;
  const x1 = 940;
  return (
    <>
      <svg width={1080} height={1920} style={svgBox} viewBox="0 0 1080 1920">
        <line x1={x0} y1={800} x2={x0 + (x1 - x0) * p} y2={800} stroke={COLOR.lime} strokeWidth={6} />
        {Array.from({length: 11}, (_, k) => (
          <line key={k} x1={x0 + k * 80} y1={780} x2={x0 + k * 80} y2={820} stroke={COLOR.white} strokeWidth={3} opacity={k / 10 <= p ? 0.8 : 0.15} />
        ))}
      </svg>
      <div style={{position: 'absolute', left: x0 - 20, top: 850, fontFamily: FONT, fontWeight: 800, fontSize: 40, color: COLOR.white}}>1978</div>
      <div style={{position: 'absolute', left: x0 - 20, top: 900, fontFamily: FONT, fontWeight: 600, fontSize: 24, color: COLOR.blue}}>el ciclón de cartón</div>
      <div style={{position: 'absolute', right: SAFE.side, top: 640, fontFamily: FONTS.display, fontWeight: 800, fontSize: 84, color: COLOR.lime, opacity: prog(t, t0 + 1.6, t0 + 2.2), letterSpacing: '-0.03em'}}>
        10 años
      </div>
    </>
  );
};

// ── Casa como garantía
export const HouseGuarantee: React.FC<{t: number; t0: number}> = ({t, t0}) => {
  const a = prog(t, t0, t0 + 0.8, easeInOut);
  const s = prog(t, t0 + 1.4, t0 + 1.8);
  return (
    <>
      <svg width={1080} height={1920} style={svgBox} viewBox="0 0 1080 1920">
        <path d="M 340 980 L 340 700 L 540 540 L 740 700 L 740 980 Z M 490 980 L 490 840 L 590 840 L 590 980" fill="none" stroke={COLOR.white} strokeWidth={6}
          strokeLinejoin="round" strokeDasharray={`${a * 2200} 2200`} />
      </svg>
      <div style={{position: 'absolute', left: 300, top: 1030, width: 480, textAlign: 'center', fontFamily: FONT, fontWeight: 800, fontSize: 40, letterSpacing: '0.22em', color: COLOR.lime,
        border: `3px solid ${COLOR.lime}`, padding: '14px 0', opacity: s, transform: `scale(${1.25 - s * 0.25}) rotate(-4deg)`}}>
        GARANTÍA
      </div>
    </>
  );
};

// ── Métrica con contexto
export const Metric: React.FC<{t: number; at: number; value: number; unit: string; note?: string; tone?: Tone}> = ({t, at, value, unit, note, tone = 'deep'}) => {
  const p = prog(t, at - 0.5, at + 0.2);
  return (
    <div style={{position: 'absolute', left: SAFE.side, top: 470, fontFamily: FONT}}>
      <div style={{fontFamily: FONTS.display, fontWeight: 800, fontSize: 260, lineHeight: 0.95, letterSpacing: '-0.05em', color: COLOR.lime}}>{Math.round(p * value)}</div>
      <div style={{fontWeight: 700, fontSize: 64, color: fg(tone), marginTop: 10}}>{unit}</div>
      {note ? <Tag text={note} tone={tone} style={{marginTop: 26}} /> : null}
    </div>
  );
};

// ── Año grande sobre papel
export const YearCard: React.FC<{t: number; t0: number; year: string; caption?: string}> = ({t, t0, year, caption}) => {
  const p = prog(t, t0, t0 + 0.45);
  return (
    <div style={{position: 'absolute', left: SAFE.side, top: 560, fontFamily: FONT, opacity: p, transform: `translateY(${(1 - p) * 20}px)`}}>
      <div style={{fontFamily: FONTS.display, fontWeight: 800, fontSize: 230, lineHeight: 0.95, letterSpacing: '-0.05em', color: COLOR.ink}}>{year}</div>
      {caption ? <Tag text={caption} tone="paper" style={{marginTop: 20, fontSize: 26}} /> : null}
    </div>
  );
};
